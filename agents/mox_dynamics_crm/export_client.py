# -*- coding: utf-8 -*-

import logging
import requests

import crm_interface as crm
import cache_interface as cache
import dawa_interface as dawa

# Log handler
from logger import start_logging

# Local settings
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


# Init logger
log = logging.getLogger(__name__)


def export_everything():
    all_kunderolle = []

    for kunderolle in cache.find_all("organisationfunktion"):
        all_kunderolle.append(kunderolle)

    for kunderolle in all_kunderolle:
        process(kunderolle)


def process(kunderolle):

    # Prepare lookup reference fallback
    lookup_contact = None
    lookup_account = None
    lookup_aftale = None
    lookup_address = None
    lookup_billing_address = None
    lookup_utility_address = None
    lookup_kunderolle = None

    # Hotfix:
    # To create a link between contact and aftale,
    # We need the CRM GUID references
    contact_external_ref = None
    aftale_external_ref = None

    # References
    contact_ref = kunderolle["contact_ref"]
    interessefaellesskab_ref = kunderolle["interessefaellesskab_ref"]

    # Customer/Contact
    contact = cache.find("contact", contact_ref)

    # Address
    address_ref = contact["dawa_ref"]

    if not address_ref:
        log.info("No address reference found, skipping")
        log.debug("Kunderolle: {0}".format(kunderolle["_id"]))
        log.debug("Contact: {0}".format(contact["_id"]))
        return False

    address = cache.find("dawa", address_ref)

    if not address:
        dawa_address = dawa.get_address(address_ref)
        store = cache.store_address(dawa_address)
        address = cache.find("dawa", address_ref)

    if not address:
        return False

    # Export address
    # Depends on: None
    if not address["external_ref"]:
        address_data = address["data"]
        address["external_ref"] = crm.store_address(address_data)

        update_cache = cache.update_or_insert(
            resource="dawa",
            payload=address
        )

        log.info("Updating cache for klasse")
        log.info(update_cache)

    # Update address lookup
    if address["external_ref"]:
        lookup_address = "/ava_adresses({external_ref})".format(
            external_ref=address["external_ref"]
        )

    # Export contact
    # Depends on: address
    if not contact["external_ref"]:
        contact_data = contact["data"]
        contact_data["ava_adresse@odata.bind"] = lookup_address
        contact["external_ref"] = crm.store_contact(contact_data)

        update_cache = cache.update_or_insert(
            resource="contact",
            payload=contact
        )

        log.info("Updating cache for contact")
        log.info(update_cache)

    # Update contact lookup
    if contact["external_ref"]:
        # Hotfix:
        contact_external_ref = contact["external_ref"]

        # Create lookup
        lookup_contact = "/contacts({external_ref})".format(
            external_ref=contact["external_ref"]
        )

    # Kundeforhold
    kundeforhold = cache.find(
        "interessefaellesskab",
        interessefaellesskab_ref
    )

    # Billing address
    billing_address_ref = kundeforhold["dawa_ref"]

    # Fallback
    billing_address = None

    if billing_address_ref:
        try:
            billing_address = cache.find("dawa", billing_address_ref)
        except:
            log.info("Address does not exist in the cache layer, importing")
            dawa_address = dawa.get_address(billing_address_ref)
            if dawa_address:
                store = cache.store_address(dawa_address)
                billing_address = cache.find("dawa", billing_address_ref)

    if billing_address:

        if not billing_address["external_ref"]:
            billing_address["external_ref"] = crm.store_address(
                billing_address["data"]
            )

            update_cache = cache.update_or_insert(
                resource="dawa",
                payload=billing_address
            )

            log.info("Updating cache for billing_address")
            log.info(update_cache)

        # Update address lookup
        if billing_address["external_ref"]:
            lookup_billing_address = "/ava_adresses({external_ref})".format(
                external_ref=billing_address["external_ref"]
            )

    if not kundeforhold["external_ref"]:
        kundeforhold_data = kundeforhold["data"]

        if lookup_billing_address:
            kundeforhold_data[
                "ava_adresse@odata.bind"] = lookup_billing_address

        kundeforhold["external_ref"] = crm.store_account(kundeforhold_data)

        update_cache = cache.update_or_insert(
            resource="interessefaellesskab",
            payload=kundeforhold
        )

        log.info("Updating cache for kundeforhold")
        log.info(update_cache)

    # Update account lookup
    if kundeforhold["external_ref"]:
        lookup_account = "/accounts({external_ref})".format(
            external_ref=kundeforhold["external_ref"]
        )

    # Kunderolle
    # Depends on: Contact, Account

    # Resolve dependencies for Kunderolle
    kunderolle_data = kunderolle["data"]

    if lookup_contact:
        kunderolle_data["ava_aktoer@odata.bind"] = lookup_contact

    if lookup_account:
        kunderolle_data["ava_kundeforhold@odata.bind"] = lookup_account

    if not kunderolle["external_ref"]:
        log.info("Kunderolle does not exist in CRM")
        kunderolle["external_ref"] = crm.store_kunderolle(
            kunderolle_data
        )

        update_cache = cache.update_or_insert(
            resource="organisationfunktion",
            payload=kunderolle
        )

        log.info("Updating cache for organisationfunktion")
        log.info(update_cache)

    # Aftale
    aftale = cache.find_indsats(interessefaellesskab_ref)

    if not aftale:
        log.warning("Aftale does not exist")
        return

    if not aftale["external_ref"]:
        aftale_data = aftale["data"]

        if lookup_account:
            kundeforhold_bind = "ava_kundeforhold@odata.bind"
            aftale_data[kundeforhold_bind] = lookup_account

        if lookup_billing_address:
            billing_bind = "ava_faktureringsadresse@odata.bind"
            aftale_data[billing_bind] = lookup_billing_address

        log.debug("AFTALE DATA CHECK:")
        log.debug(aftale_data)

        aftale["external_ref"] = crm.store_aftale(aftale_data)

        update_cache = cache.update_or_insert(
            resource="indsats",
            payload=aftale
        )

        log.info("Updating cache for indsats")
        log.info(update_cache)

    # Update aftale lookup
    if aftale["external_ref"]:
        # Hotfix:
        aftale_external_ref = aftale["external_ref"]

        lookup_aftale = "/ava_aftales({external_ref})".format(
            external_ref=aftale["external_ref"]
        )

        # Create link between aftale and contact
        create_link = crm.contact_and_aftale_link(
            contact_guid=contact_external_ref,
            aftale_guid=aftale_external_ref
        )

    # Installation
    klasse_ref = aftale["klasse_ref"]
    produkt = cache.find("klasse", klasse_ref)

    if not produkt:
        log.warning("Produkt does not exist")
        return

    # Workaround
    if aftale_external_ref:
        produkt["indsats_ref"] = aftale_external_ref

    if not produkt["external_ref"]:
        produkt_data = produkt["data"]

        # TODO: utility address must be added here
        # Workaround: Just inserting billing address
        ava_kundenummer = kundeforhold["data"]["ava_kundenummer"]
        produkt_data["ava_kundenummer"] = ava_kundenummer

        if lookup_aftale:
            produkt_data["ava_aftale@odata.bind"] = lookup_aftale

        if lookup_billing_address:
            produkt_data["ava_adresse@odata.bind"] = lookup_billing_address

        produkt["external_ref"] = crm.store_produkt(produkt_data)

    if produkt["external_ref"]:
        produkt_update = {
            "ava_aftale@odata.bind": lookup_aftale
        }

        # Update CRM
        crm.update_produkt(
            identifier=produkt["external_ref"],
            payload=produkt_update
        )

    # Update cache
    update_cache = cache.update_or_insert(
        resource="klasse",
        payload=produkt
    )

    log.info("Updating cache for produkt")
    log.info(update_cache)


def update_all_installations():
    """
    Alternative addresses for installations (Produkt)
    The Lora entity is "klasse"
    """

    all_installations = []

    for installation in cache.find_all("klasse"):

        if not installation["dawa_ref"]:
            continue

        # Append all objects that contain an alternative address
        all_installations.append(installation)

    for installation in all_installations:
        update_alternative_address(installation)


def update_alternative_address(installation):

    resource = "dawa_access"

    if not installation["external_ref"]:
        return False

    address_ref = installation["dawa_ref"]

    access_address = cache.find(resource, address_ref)

    if not access_address:
        log.info("Access address does not yet exist, creating")

        try:
            # Return adapted access address
            log.info("Attempting to retrieve access address from DAWA")
            access_address = dawa.get_access_address(address_ref)
            log.debug(access_address)

            # Store address externally (CRM)
            log.info("Attempting to store access address")
            access_address["external_ref"] = crm.store_address(
                access_address["data"]
            )

            # Update cache
            log.info("Attempting to update cache for access address")
            cache.update_or_insert("dawa_access", access_address)

        except Exception as error:
            log.error("Failed to create access address:")
            log.error(error)
            return False

    if not access_address["external_ref"]:
        log.warning(
            "No external ref found for access address: {reference}".format(
                reference=access_address["_id"]
            )
        )

    # Hotfix:
    # Create fallback
    if not "lookup_access_address" in installation:
        log.debug("Creating access address lookup key")
        installation["lookup_access_address"] = None

    if not installation["lookup_access_address"]:
        log.info("Creating lookup for access address")
        lookup_utility_address = "/ava_adresses({external_ref})".format(
            external_ref=access_address["external_ref"]
        )

        try:
            log.info("Updating installation with access address")
            crm.update_produkt({
                "ava_adresse@odata.bind": lookup_utility_address
            })
            installation["lookup_access_address"] = lookup_utility_address

            # Update cache
            log.info("Attempting to update cache for installation")
            cache.update_or_insert("klasse", installation)

        except Exception as error:
            log.error(
                "Error updating access address for: {reference}".format(
                    reference=installation["_id"]
                )
            )

    return True


if __name__ == "__main__":

    # Begin
    print("Begin export from cache to CRM")

    # Log to file
    start_logging(20, LOG_FILE)

    # Run
    # export_everything()
    update_all_installations()

    # Done
    print("All done")
