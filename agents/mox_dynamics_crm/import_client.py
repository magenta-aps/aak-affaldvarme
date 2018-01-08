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
import cache_interface as cache
import crm_interface as crm
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
from settings import AREA_CODE


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
log = logging.getLogger(__name__)


### CACHE ###
def import_all_addresses():
    """ 
    Missing docstring
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
            "No addresses found in area code:  {0}".format(AREA_CODE)
        )
        return False

    # Store addresses
    try:
        cache.store_address(addresses)
    except Exception as error:
        log.error(error)

    # Finished procedure
    log.info("Finished processing all addresses")


def import_to_cache(resource):

    # Get all uuids
    list_of_uuids = oio.get_all(resource)

    # Prepare cache payload
    cache_payload = []

    # Workaround for consolidating bruger/organisation
    cache_resource = resource

    if resource == "bruger" or resource == "organisation":
        cache_resource = "contact"

    # Batch generate fetches n amount of entities
    # Returns iterator
    for entity in oio.batch_generator(resource, list_of_uuids):
        # # Append to the payload
        # cache_payload.append(entity)
        store = cache.update_or_insert(cache_resource, entity)
        print(store)


def import_sanity_check():

    # Loop and do stuff
    for address in cache.find_all("addresses"):
        identifier = address.get("_id")
        external = address.get("_external")

        payload = {
            "ava_dawa_uuid": identifier
        }

        print("ava_adresses({0})".format(external))
        print(json.dumps(payload))


# RUN THE CLIENT
if __name__ == "__main__":

    # Log to file
    start_logging(20, LOG_FILE)

    # Import all addresses
    # import_all_addresses()

    # Import to cache
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
