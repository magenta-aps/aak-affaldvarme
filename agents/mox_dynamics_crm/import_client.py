# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import logging
import requests

# Local modules
import crm_interface as crm
# import crm_mock as crm
import oio_interface as oio
import ava_adapter as adapter
import dawa_interface as dawa

# Logging module
from logger import start_logging

# Local settings
from settings import ORGANISATION_UUID
from settings import LOG_FILE
from settings import DO_RUN_IN_TEST_MODE
from settings import DO_DISABLE_SSL_WARNINGS


# If the SSL signature is not valid requests will print errors
# To circumvent this, warnings can be disabled for testing purposes
if DO_DISABLE_SSL_WARNINGS:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# In test mode log is written to a local logfile
# This is to prevent the test log from being collected for analysis
if DO_RUN_IN_TEST_MODE:
    LOG_FILE = "debug.log"

# Switch statement workaround
# TODO: Please replace with sane code
resources = {
    "bruger": "organisation/bruger",
    "organisation": "organisation/organisation",
    "organisationfunktion": "organisation/organisationfunktion",
    "interessefaellesskab": "organisation/interessefaellesskab",
    "indsats": "indsats/indsats",
    "klasse": "klassifikation/klasse"
}


def batch_generator(resource, list_of_things):
    """Generate and return batches of objects"""

    # Amount of chuncks a batch contains
    chunck = 50

    # Generate batches until done
    while len(list_of_things) > 0:
        uuid_batch = list_of_things[:chunck]
        list_of_things = list_of_things[chunck:]

        params = {
            'uuid': uuid_batch
        }

        # Call GET request function
        results = oio.get_request(resource, params)

        # Return iterator
        for result in results:
            yield result


def run_import(uuid):
    """
    Import function for a single entity
    Perhaps we do not need a method for this
    NOTE: The import all function may render this redundant
    """

    entity = oio.fetch_entity("bruger", uuid)
    contact = adapter.ava_bruger(entity)

    return process_entity(contact)


def run_import_all():
    """
    Import all wrapper function
    All contacts that belongs to parent organisation (See settings)
    """

    # Init logger
    log = logging.getLogger()

    # Use switch to determine resource path
    bruger = resources["bruger"]

    # Belgons to parent organisation
    params = {
        "tilhoerer": ORGANISATION_UUID
    }

    # Generate list of contacts (uuid)
    log.info("Attempting to import all contacts of parent organisation")
    list_of_contacts = oio.get_request(bruger, params)

    # Debug:
    total = len(list_of_contacts)
    log.debug("{0} contacts found".format(total))

    # TODO: Log error when nothing is returned
    if not list_of_contacts:
        log.error("No contacts found")
        return None

    # Batch generate fetches n amount of entities
    # Returns iterator
    for entity in batch_generator(bruger, list_of_contacts):
        # Format adapter
        exported = adapter.ava_bruger(entity)

        # Process the entity
        process_entity(exported)


def process_entity(entity):
    """
    Process customer, requires a contact and address entity
    TODO: Consolidate logic for process contact/organisation
    TODO: Absolutely must be broken down to smaller pieces
    """

    # Set logging
    log = logging.getLogger()

    # Contact required
    if not entity:
        log.error("No contact object provided")
        return False

    # Gather information
    entity_uuid = entity.get("ava_lora_uuid")
    address_uuid = entity.get("ava_adresse")
    ava_masterid = entity.get("ava_masterid")

    # Log entry
    log.info("Processing: {0}".format(entity_uuid))

    # Check if address
    if not address_uuid:
        log.info("Contact: {0} has no address - Exiting".format(entity_uuid))
        return False

    # Attempt to get related kunderolle
    # Set empty object
    kunderolle = None

    # Attempt to fetch the reference (uuid) for kundeforhold
    reference_kundeforhold = None

    try:
        kunderolle_entity = oio.fetch_relation(entity_uuid)
        log.info("Kunderolle found")

        kunderolle = adapter.ava_kunderolle(kunderolle_entity)

        # This must be replaced with a CRM reference
        # Just in case something fails when inserting contact
        # At least we have a reference to the contact
        kunderolle["ava_aktoer"] = entity_uuid

        # This must be replaced with a CRM reference
        # kunderolle["ava_kundeforhold"] = ?

        reference_kundeforhold = kunderolle["ava_kundeforhold"]
        log.info("Setting reference_kundeforhold")

    except:
        log.error("Kunderolle not found: ")
        log.error("Kunderolle: {0}".format(entity_uuid))

    # Attempt to fetch the kundeforhold entity
    kundeforhold = None

    if reference_kundeforhold:
        kundeforhold_entity = oio.fetch_entity(
            "interessefaellesskab",
            reference_kundeforhold
        )

        kundeforhold = adapter.ava_account(kundeforhold_entity)
        log.info("Setting kundeforhold")

    # Attempt to fetch the kundeforhold entity
    aftale = None

    if reference_kundeforhold:
        aftale_entity = oio.fetch_relation_indsats(reference_kundeforhold)
        aftale = adapter.ava_aftale(aftale_entity)
        log.info("Setting aftale")

    try:
        ava_faktureringsgrad = aftale["ava_faktureringsgrad"]
        log.info("Setting ava_faktureringsgrad")
    except:
        log.error('Aftale not found')

    finally:
        # TODO:
        # search_crm_address(ava_faktureringsgrad)
        pass

    # Attempt to get the product
    # This depends on aftale
    produkt = None
    produkt_reference = None

    if aftale:
        produkt_reference = aftale.get("ava_produkter")

    try:
        produkt_entity = oio.fetch_entity("klasse", produkt_reference)
        produkt = adapter.ava_installation(produkt_entity)

        # All following references
        # MUST be replaced with their CRM counterparts
        produkt["ava_adresse"] = aftale["ava_faktureringsgrad"]
        produkt["ava_aftale"] = aftale["ava_faktureringsgrad"]
        produkt["ava_kundenummer"] = kundeforhold["ava_kundenummer"]

    except:
        if aftale:
            log.error("Product not found")
            log.error("Customer: {0}".format(entity_uuid))
            log.error("Aftale: {0}".format(aftale))

    # Last log entry before adding things to CRM
    log.info("Export: {0} to CRM".format(entity_uuid))

    #################################
    # CRM INSERT/UPDATE BEGINS HERE #
    #################################

    # Adresse
    # Depends on: None

    # Prepare lookup reference fallback
    lookup_crm_address = None

    # Check and return reference (GUID) if address exists in CRM
    crm_address_guid = crm.get_ava_address(address_uuid)

    # Create address in CRM if it does not exist
    if not crm_address_guid:
        log.info("Address does not exist in CRM")

        # GET ADDRESS ENTITY HERE
        address_entity = dawa.get_address(address_uuid)

        # Store in CRM
        crm_address_guid = crm.store_address(address_entity)

    # Update lookup reference
    lookup_crm_address = "/ava_adresses({0})".format(crm_address_guid)
    log.info("Lookup created: {0}".format(lookup_crm_address))

    # Contact
    # Depends on: Address

    # Prepare lookup reference fallback
    lookup_crm_contact = None

    # Resolve dependencies for Contact
    log.info("Resolve dependencies for: {0}".format(entity_uuid))
    entity["ava_adresse@odata.bind"] = lookup_crm_address

    # Remove temporary address key
    entity.pop("ava_adresse", None)

    # Check and return contact reference (GUID) if contact exists
    crm_contact_guid = crm.get_contact(entity_uuid)

    # Create contact in CRM if it does not exist
    if not crm_contact_guid:
        log.info("Contact does not exist in CRM")
        crm_contact_guid = crm.store_contact(entity)

    # Update lookup reference
    lookup_crm_contact = "/contacts({0})".format(crm_contact_guid)
    log.info("Lookup for contact created: {0}".format(lookup_crm_contact))

    # Kundeforhold (Account)
    # NOTE: Will depend on "Ejendom" in the future
    # Depends on: None

    # Prepare lookup reference fallback
    lookup_crm_account = None

    if kundeforhold:
        ava_kundenummer = kundeforhold["ava_kundenummer"]
        crm_account_guid = crm.get_account(ava_kundenummer)

        if not crm_account_guid:
            log.info("Account does not exist in CRM")
            crm_account_guid = crm.store_account(kundeforhold)

        # Update lookup reference
        lookup_crm_account = "/accounts({0})".format(crm_account_guid)
        log.info("Lookup for account created: {0}".format(lookup_crm_account))

    # Kunderolle
    # Depends on: Contact, Account

    # Prepare lookup reference fallback
    lookup_crm_kunderolle = None

    if kunderolle:
        # Resolve dependencies for Kunderolle
        kunderolle["ava_aktoer@odata.bind"] = lookup_crm_contact
        kunderolle["ava_kundeforhold@odata.bind"] = lookup_crm_account

        # Remove temporary address key
        kunderolle.pop("ava_aktoer", None)
        kunderolle.pop("ava_kundeforhold", None)

        # Missing identifier
        crm_kunderolle_guid = crm.get_kunderolle(lookup_crm_contact)

        if not crm_kunderolle_guid:
            log.info("Kunderolle does not exist in CRM")
            crm_kunderolle_guid = crm.store_kunderolle(kunderolle)

        # Update lookup reference
        lookup_crm_kunderolle = "/ava_kunde({0})".format(crm_kunderolle_guid)
        log.info("Lookup for kunderolle created: {0}".format(
            lookup_crm_kunderolle))

    # Aftale
    # Depends on: Account, Address (Fakturering)

    # Prepare lookup reference fallback
    lookup_crm_aftale = None

    if aftale:
        # Lookup aftale by account identifier (Missing)
        crm_aftale_guid = crm.get_aftale(lookup_crm_account)

        if not crm_aftale_guid:
            log.info("Aftale does not exist in CRM")

            # Resolve dependencies for Aftale
            aftale["ava_kundeforhold@odata.bind"] = lookup_crm_account
            aftale["ava_faktureringsgrad@odata.bind"] = lookup_crm_address

            # Remove temporary address key
            aftale.pop("ava_kundeforhold", None)
            aftale.pop("ava_faktureringsgrad", None)

            crm_aftale_guid = crm.store_aftale(aftale)

        # Update lookup reference
        lookup_crm_aftale = "/ava_aftale({0})".format(crm_aftale_guid)
        log.info("Lookup for aftale created: {0}".format(lookup_crm_aftale))

    # Product
    # Depends on: Aftale, Address

    # Prepare lookup reference fallback
    lookup_crm_produkt = None

    if produkt:
        # Lookup produkt by "ava_maalernummer"
        produkt_identifier = produkt["ava_maalernummer"]
        crm_produkt_guid = crm.get_produkt(produkt_identifier)

        if not crm_produkt_guid:
            log.info("Produkt does not exist in CRM")

            log.info("Resolving dependencies for produkt")
            # Insert dependencies
            produkt["ava_aftaled@odata.bind"] = lookup_crm_aftale
            produkt["ava_adresses@odata.bind"] = lookup_crm_address

            # Remove temporary address key
            produkt.pop("ava_aftale", None)
            produkt.pop("ava_adresse", None)

            # Call function to insert object into CRM
            crm_produkt_guid = crm.store_produkt(produkt)

        # No need to create a lookup reference
        # lookup_crm_produkt = crm_produkt_guid ?

    log.info("Finished processing entity: {0}".format(entity_uuid))


#####################
# OUTSTANDING TASKS #
#####################

# def import_all_organisation():

#     # Switch
#     organisation = resources["organisation"]

#     # Get all brugere
#     list_of_contacts = list_all(organisation)

#     # TODO: Log error when nothing is returned
#     if not list_of_contacts:
#         return None

#     for entity in batch_generator(organisation, list_of_contacts):
#         exported = adapter.ava_organisation(entity)

#         # Mock
#         to_json = json.dumps(exported)
#         print(to_json)


# RUN THE CLIENT
if __name__ == "__main__":

    # Log to file
    start_logging(20, LOG_FILE)

    # Begin import
    run_import_all()

    # Done
    print("Import procedure completed - Exiting")
