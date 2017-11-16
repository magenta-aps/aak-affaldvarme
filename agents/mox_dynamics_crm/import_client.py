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
# import crm_interface as crm
import crm_cache_interface as crm
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

# Set logging
log = logging.getLogger(__name__)


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


def run_import_all_org():
    """
    Import all org wrapper function
    All organisations that belong to parent organisation (See settings)
    """

    # Use switch to determine resource path
    org = resources["organisation"]

    # Belgons to parent organisation
    params = {
        "tilhoerer": ORGANISATION_UUID
    }

    # Generate list of contacts (uuid)
    log.info("Attempting to import all organisations")
    list_of_contacts = oio.get_request(org, params)

    # Debug:
    total = len(list_of_contacts)
    log.debug("{0} contacts found".format(total))

    # TODO: Log error when nothing is returned
    if not list_of_contacts:
        log.error("No contacts found")
        return None

    # Batch generate fetches n amount of entities
    # Returns iterator
    for entity in batch_generator(org, list_of_contacts):
        # Format adapter
        exported = adapter.ava_organisation(entity)

        # Process the entity
        process_entity(exported)


def process_entity(entity):
    """
    Process customer, requires a contact and address entity
    TODO: Consolidate logic for process contact/organisation
    TODO: Absolutely must be broken down to smaller pieces
    """

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

    # CRM INSERT ADDRESS
    # Adresse
    # Depends on: None

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

    # CRM INSERT CONTACT
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

    # ABSTRACTED KUNDEROLLE

    # List of related "kunderoller" (belongs to contact)
    kunderolle_uuids = oio.fetch_relation(entity_uuid)

    if not kunderolle_uuids:
        log.error("Kunderolle not found: ")
        log.error("No kunderoller found for: {0}".format(entity_uuid))

    for kunderolle_uuid in kunderolle_uuids:
        log.info("Kunderolle found: {0}".format(kunderolle_uuid))

        kunderolle_entity = oio.fetch_entity(
            "organisationfunktion",
            kunderolle_uuid
        )

        kunderolle = adapter.ava_kunderolle(kunderolle_entity)

        # Append "kundeforhold" reference to the list
        reference_kundeforhold = kunderolle["ava_kundeforhold"]

        kundeforhold_entity = oio.fetch_entity(
            "interessefaellesskab",
            reference_kundeforhold
        )

        kundeforhold = adapter.ava_account(kundeforhold_entity)
        log.info("Setting kundeforhold")

        if not kundeforhold:
            log.info("Kundeforhold not found for {0}".format(entity_uuid))
            return False

        # Kundeforhold (Account)
        # Depends on: Address
        # NOTE: Will depend on "Ejendom" in the future

        ava_kundenummer = kundeforhold["ava_kundenummer"]
        crm_account_guid = crm.get_account(ava_kundenummer)

        # Resolve dependencies
        kundeforhold["ava_adresse@odata.bind"] = lookup_crm_address
        kundeforhold.pop("ava_adresse", None)

        if not crm_account_guid:
            log.info("Account does not exist in CRM")
            crm_account_guid = crm.store_account(kundeforhold)

        # Update lookup reference
        lookup_crm_account = "/accounts({0})".format(crm_account_guid)
        log.info("Lookup for account created: {0}".format(
            lookup_crm_account))

        # Kunderolle
        # Depends on: Contact, Account

        # Prepare lookup reference fallback
        lookup_crm_kunderolle = None

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

        # AFTALE
        # Attempt to fetch the kundeforhold entity
        aftale_entity = oio.fetch_relation_indsats(reference_kundeforhold)
        aftale = adapter.ava_aftale(aftale_entity)
        log.info("Setting aftale")

        if not aftale:
            log.error('Aftale not found')
            return False

        ava_faktureringsgrad = aftale["ava_faktureringsgrad"]
        produkt_reference = aftale.get("ava_produkter")

        log.info("Setting ava_faktureringsgrad")

        # TODO:
        # We are currently not sure how to pass the product address

        # PRODUCT ADDRESSS
        # Check and return reference (GUID) if address exists in CRM
        crm_product_address_guid = crm.get_ava_address(ava_faktureringsgrad)

        # Create address in CRM if it does not exist
        if not crm_product_address_guid:
            log.info("Product address does not exist in CRM")

            # GET ADDRESS ENTITY HERE
            product_address = dawa.get_address(ava_faktureringsgrad)

            # Store in CRM
            crm_product_address_guid = crm.store_address(product_address)

        # Update lookup reference
        lookup_crm_product_address = "/ava_adresses({0})".format(
            crm_product_address_guid
        )
        log.info("Product address created")

        # END PRODUCT ADDRESS

        # INSERT AFTALE INTO CRM
        # Aftale
        # Depends on: Account, Address (Fakturering)

        # Lookup aftale by account identifier (Missing)
        crm_aftale_guid = crm.get_aftale(lookup_crm_account)

        if not crm_aftale_guid:
            log.info("Aftale does not exist in CRM")

            # Resolve dependencies for Aftale
            aftale["ava_kundeforhold@odata.bind"] = lookup_crm_account
            aftale["ava_faktureringsadresse@odata.bind"] = lookup_crm_address

            # Remove temporary address key
            aftale.pop("ava_kundeforhold", None)
            aftale.pop("ava_faktureringsgrad", None)
            aftale.pop("ava_produkter", None)

            crm_aftale_guid = crm.store_aftale(aftale)

        # Update lookup reference
        lookup_crm_aftale = "/ava_aftales({0})".format(crm_aftale_guid)
        log.info("Lookup for aftale created: {0}".format(lookup_crm_aftale))

        # Hotfix:
        # NOTES: This will be replaced by the cache functionality
        # Create link between Contact and Aftale
        crm.contact_and_aftale_link(
            aftale_guid=crm_aftale_guid,
            contact_guid=crm_contact_guid
        )

        # Attempt to get the product
        # This depends on aftale

        if not produkt_reference:
            log.error(
                "No product reference found for: {0}".format(
                    entity_uuid
                )
            )
            return False

        produkt_entity = oio.fetch_entity("klasse", produkt_reference)
        produkt = adapter.ava_installation(produkt_entity)

        if not produkt:
            log.error("Product not found")
            log.error("Customer: {0}".format(entity_uuid))
            log.error("Aftale: {0}".format(aftale))
            return False

        # All following references
        # MUST be replaced with their CRM counterparts
        produkt["ava_adresse"] = ava_faktureringsgrad
        produkt["ava_aftale"] = ava_faktureringsgrad
        produkt["ava_kundenummer"] = kundeforhold["ava_kundenummer"]

        # INSERT PRODUKT INTO CRM
        # Product
        # Depends on: Aftale, Address

        # Lookup produkt by "ava_maalernummer"
        produkt_identifier = produkt["ava_maalernummer"]
        crm_produkt_guid = crm.get_produkt(produkt_identifier)

        if not crm_produkt_guid:
            log.info("Produkt does not exist in CRM")

            # Resolve dependencies
            log.info("Resolving dependencies for produkt")
            produkt["ava_aftale@odata.bind"] = lookup_crm_aftale
            produkt["ava_adresse@odata.bind"] = lookup_crm_product_address

            # Remove temporary address key
            produkt.pop("ava_aftale", None)
            produkt.pop("ava_adresse", None)

            # Call function to insert object into CRM
            crm_produkt_guid = crm.store_produkt(produkt)

        # Finished inserting product

    # Finished processing entity
    log.info("Finished processing entity: {0}".format(entity_uuid))


# RUN THE CLIENT
if __name__ == "__main__":

    # Log to file
    start_logging(20, LOG_FILE)

    # Begin import
    run_import_all()
    run_import_all_org()

    # Done
    print("Import procedure completed - Exiting")
