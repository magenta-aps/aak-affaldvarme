# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import requests
from helper import start_logging
from cpr_handler import cpr_handler
from cvr_handler import cvr_handler
import interfaces.oio_interface as oio


# Ignore warnings caused by self signed SSL certificate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Init log
log = start_logging(10)


# List of available tasks to run
update_tasks = [
    ("bruger", cpr_handler),
    ("organisation", cvr_handler)
]


def all_tasks():
    """
    Wrapper
    :return:
    """

    for resource, handler in update_tasks:
        run_task(resource, handler)


def run_task(resource, handler):
    """
    Import all database objects (by entity)

    :param resource:    Name of the entity to import
    :return:            Prints cache status object to terminal
    """

    # Get all uuids
    list_of_uuids = oio.get_all(resource)

    # Debug
    log.debug(list_of_uuids)

    for uuid in list_of_uuids:
        oio_object = oio.get_request(
            resource=resource,
            uuid=uuid
        )

        result = handler(oio_object)

        if not result:
            log.error(
                "Unable to retrieve {resource}: {identifier}".format(
                    resource=resource,
                    identifier=uuid
                )
            )
            log.error(oio_object)
            continue

        # Info
        log.info("Running updater")

        # Run updater
        update_controller(resource, oio_object[0], result)


def update_controller(resource, org_data, updates):
    """
    Controller

    :param resource:    OIO resource, e.g. organisation

    :param org_data:    OIO REST data object

    :param updates:     This is the dictionary returned by the handler
                        Example:

    :return:
    """

    # Info
    log.info("Updating: {}".format(resource))

    uuid = org_data["id"]
    registreringer = org_data['registreringer'][0]

    for update in updates:
        # Debug
        log.debug("Processing: {0}".format(update))
        update_values(registreringer, update)

    # Info
    log.info("Updating Lora")

    # Update PUT request
    response = oio.put_request(
        resource=resource,
        identifier=uuid,
        payload=registreringer
    )

    # Not updated (Not HTTP 200)
    if not response.status_code == 200:
        log.error(
            "PUT request returned: {status}".format(
                status=response.status_code
            )
        )

        # Debug
        # Include failed object
        log.error(registreringer)

    # Debug
    log.debug(response.text)


def update_values(registreringer, update):
    """
    Dynamically build update objects

    :param registreringer:
    :param update:
    :return:
    """
    group = update["group"]
    subgroup = update["subgroup"]
    content = update["update"]

    # TODO: Must be refactored into something elegant
    # Iterate over all items in the subgroup list
    # Target the items that needs to be updated
    for item in registreringer[group][subgroup]:

        # Content is the SP value (updated) value,
        # which must replace the item value
        for key in content.keys():

            # We are not touch key/value pairs
            # which does not exist in our update/content list
            if not key in item.keys():
                continue

            # Replace item with updated content
            item[key] = content[key]


if __name__ == "__main__":

    # Run all tasks
    # From the available tasks list
    all_tasks()