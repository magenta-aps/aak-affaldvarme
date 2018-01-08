# -*- coding: utf-8 -*-

import logging
from logger import start_logging
import crm_interface as crm
import cache_interface as cache

# Local settings
from settings import LOG_FILE


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
            identifier = contact["_id"]

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


if __name__ == "__main__":
    # Start logging
    start_logging(20, LOG_FILE)

    # Run
    set_primary_email_for_contact()
