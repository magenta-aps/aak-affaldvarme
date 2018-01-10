# -*- coding: utf-8 -*-


import logging
import requests
import crm_interface as crm
import cache_interface as cache

from logger import start_logging

# Local settings
from settings import LOG_FILE
from settings import DO_RUN_IN_TEST_MODE
from settings import DO_DISABLE_SSL_WARNINGS


# In test mode log is written to a local logfile
# This is to prevent the test log from being collected for analysis
if DO_RUN_IN_TEST_MODE:
    LOG_FILE = "debug.log"


# If the SSL signature is not valid requests will print errors
# To circumvent this, warnings can be disabled for testing purposes
if DO_DISABLE_SSL_WARNINGS:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# LOG
log = logging.getLogger(__name__)


def set_primary_email_for_contact():
    """
    Support ticket (REDMINE): #21148
    Set KMDEE email address as primary if primary is null
    """

    # Final list of contacts which must be updated
    contacts_to_update = []

    for contact in cache.find_all("contact"):

        if not contact["external_ref"]:
            continue

        if not "emailaddress1" in contact["data"]:
            contacts_to_update.append(contact)

    for contact in contacts_to_update:
        secondary_email = contact["data"]["ava_emailkmdee"]

        if secondary_email:
            # Gather information
            identifier = contact["external_ref"]

            # Set primary email
            contact["data"]["emailaddress1"] = secondary_email

            # Update CRM
            log.info(
                "Attempting to update CRM contact: {0}".format(identifier)
            )

            try:
                crm.update_contact(identifier, contact["data"])
            except:
                log.error("Failed to update CRM contact")

            # Update cache
            log.info("Attempting to update cache for contact")

            try:
                update_cache = cache.update_or_insert("contact", contact)
                log.info(update_cache)
            except Exception as error:
                log.error("Failed to update cache")
                log.error(error)

            # Finished
            log.info(
                "Primary email updated for: {0}".format(identifier)
            )


def remove_duplicate_contacts():
    """
    Support ticket (REDMINE): #21148
    Remove duplicate entries created with Lora UUID
    """

    # Final list of contacts which must be updated
    contacts_to_update = []

    for contact in cache.find_all("contact"):

        # if not contact["external_ref"]:
        #     continue

        if not "emailaddress1" in contact["data"]:
            continue

        primary_email = contact["data"]["emailaddress1"]
        secondary_email = contact["data"]["ava_emailkmdee"]

        if primary_email == secondary_email:
            contacts_to_update.append(contact)

    for contact in contacts_to_update:
        # Get Lora UUID
        lora_identifier = contact["_id"]
        log.info("Handling: {}".format(lora_identifier))

        # Create service url
        resource = "contacts"

        # Remove object from CRM
        delete_contact = crm.delete_request(
            resource=resource,
            identifier=lora_identifier
        )

        if not delete_contact.status_code == 200:
            log.error("Error deleting contact: lora_identifier")
            log.error(delete_contact.text)

            continue

        try:
            # Remove primary email address from cache
            instructions_to_remove = {
                "$unset": {
                    "data.emailaddress1": ""
                }
            }

            update_cache = cache.unset(
                resource="contact",
                identifier=lora_identifier,
                instructions=instructions_to_remove
            )
            log.debug(update_cache)

        except Exception as error:
            log.error("Error updating cache")
            log.error(error)


if __name__ == "__main__":

    # Start logging
    start_logging(20, LOG_FILE)

    # Hotfix:
    remove_duplicate_contacts()

    # Run
    set_primary_email_for_contact()
