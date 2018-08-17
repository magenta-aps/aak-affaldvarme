# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# skip module level code when 
# generating top level documentation
import os
if not os.environ.get("SPHINXBUILDING"):
    import oio_interface as oio
    import dawa_interface as dawa
    import cache_interface as cache

    from logging import getLogger


    # Init logging
    log = getLogger(__name__)


def import_all_addresses():
    """
    Import all addresses from DAR (DAWA service)
    and store them as documents in the cache layer

    :return:    All operations are written to logs
    """

    # DAR/DAWA settings
    AREA_CODE = "0751"

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
            cache.store(
                resource="dawa",
                payload=batch_of_addresses
            )

        except Exception as error:
            log.error(batch_of_addresses)
            log.error(error)

    # Finished procedure
    log.info("Finished processing all addresses")


def import_to_cache(resource):
    """
    Retrieve all database objects (by entity)
    and store converted (ava_adapter) document into the cache layer.

    Data objects are just stored,
    no relations between documents at this point.

    :param resource:    Name of the entity to import

    """

    # Get all uuids
    list_of_uuids = oio.get_all(resource)

    # Batch generate fetches n amount of entities
    # Returns iterator
    for batch in oio.batch_generator(resource, list_of_uuids):

        # Info
        log.info(
            "Attempting to import batch of {resource}".format(
                resource=resource
            )
        )

        # Store in the cache layer
        store = cache.store(
            resource=resource,
            payload=batch
        )

        # Log database status object
        log.info(store)


def import_sanity_check():
    """
    Simple sanity check for addresses.
    It iterates over all addresses stored in the cache layer,
    and confirms that the address exists in the DAR database.

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
    Wrapper to run full import.

    records start and finish in a table 'imports'
    """

    import_start = cache.r.now().run(cache.connect())
    new_import = {
        "id": import_start.strftime("%Y%m%dT%H%M%S"),
        "started": import_start,
        "ended": None
    }

    # Begin
    log.info("Begin import (all) procedure")

    # Import addresses
    import_all_addresses()

    # Import Lora objects
    import_to_cache("bruger")
    import_to_cache("organisation")
    import_to_cache("organisationfunktion")
    import_to_cache("indsats")
    import_to_cache("interessefaellesskab")
    import_to_cache("klasse")

    # Done
    log.info("Import procedure completed - Exiting")

    new_import["ended"] = cache.r.now().run(cache.connect())
    query = cache.r.table("imports").insert(new_import, conflict="update")
    query.run(cache.connect())
