# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import oio_interface as oio
import dawa_interface as dawa
import cache_interface as cache

from helper import get_config
from logger import start_logging

# Settings (For compatibility)
config = get_config()

# Parent organisation
# Reference to which organisation an object belongs to
# NOTE: Only some entities support this reference
ORGANISATION_UUID = config["parent_organisation"] or None

# Optionally the signature of the SSL certificate can be verified
# This should be disabled when no commercial certificate is installed
# (E.g. should be disabled or set to 'no' when using a self signed signature)
# By default this is set to 'Yes'
DO_VERIFY_SSL_SIGNATURE = config.getboolean("do_verify_ssl_signature", "yes")

# General
DO_DISABLE_SSL_WARNINGS = True
DO_RUN_IN_TEST_MODE = True

# Logging
LOG_FILE = "/var/log/mox/mox_dynamics_crm.log"

# DAR/DAWA settings
AREA_CODE = "0751"

# If the SSL signature is not valid requests will print errors
# To circumvent this, warnings can be disabled for testing purposes
if DO_DISABLE_SSL_WARNINGS:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# In test mode log is written to a local logfile
# This is to prevent the test log from being collected for analysis
if DO_RUN_IN_TEST_MODE:
    LOG_FILE = "debug.log"


# Set logging
log = start_logging(20, LOG_FILE)


def import_all_addresses():
    """
    Import all addresses from DAR (DAWA service)
    and store them as documents in the cache layer

    :return:    All operations are written to logs
    """

    # Begin
    log.info("Begin address import")
    log.info(
        "Import all addresses from area code: {0}".format(AREA_CODE)
    )

    # Get list of all address within "AREA_CODE"
    # See settings to get the area code
    addresses = dawa.get_all(AREA_CODE)

    if not addresses:
        log.warning(
            "No addresses found in area code: {0}".format(AREA_CODE)
        )
        return False

    # Batch operation
    size = 200

    while len(addresses) > 0:
        batch_of_addresses = addresses[:size]
        addresses = addresses[size:]

        try:
            cache.store_address(batch_of_addresses)

        except Exception as error:
            log.error(batch_of_addresses)
            log.error(error)

    # Finished procedure
    log.info("Finished processing all addresses")


def import_to_cache(resource):
    """
    Import all database objects (by entity)

    :param resource:    Name of the entity to import
    :return:            Prints cache status object to terminal
    """

    # Get all uuids
    list_of_uuids = oio.get_all(resource)

    # Workaround for consolidating bruger/organisation
    cache_resource = resource

    if resource == "bruger" or resource == "organisation":
        cache_resource = "contact"

    # Batch generate fetches n amount of entities
    # Returns iterator
    for entity in oio.batch_generator(resource, list_of_uuids):
        # # Append to the payload
        # cache_payload.append(entity)
        store = cache.store(cache_resource, entity)
        print(store)


def import_sanity_check():
    """
    Simple sanity check for addresses.
    It iterates over all addresses stored in the cache layer,
    and confirms that the address exists in the DAR database.

    TODO: Create check
    """

    # Retrieve all address from cache
    addresses = cache.all("ava_adresses")

    for address in addresses:
        identifier = address.get("id")

        # Missing DAR check to confirm whether the address exists
        # check_if_address_exists(identifier)
        print(identifier)


def run_import():
    """
    Run all import tasks
    """

    # Import addresses
    import_all_addresses()

    # Import Lora objects
    import_to_cache("bruger")
    import_to_cache("organisation")
    import_to_cache("organisationfunktion")
    import_to_cache("indsats")
    import_to_cache("interessefaellesskab")
    import_to_cache("klasse")

    # Run sanity check
    # import_sanity_check()

    # Done
    print("Import procedure completed - Exiting")


if __name__ == "__main__":
    run_import()
