# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests
from helper import start_logging
from cpr_handler import cpr_handler
from cvr_handler import cvr_handler
import interfaces.oio_interface as oio


# Ignore warnings caused by self signed SSL certificate
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Init log
log_level = 20
log = start_logging(log_level)


def run_task(resource, handler):
    """
    Main task runner.

    Import all database objects (by entity),
    iterate and run the given handler for each object.

    The handler will return a list of updates
    and these are applied to the original object.

    Finally "send_update" is called to send an update request
    to the OIO REST interface.

    :param resource:    Name of the entity to import

    :return:            Nothing is returned,
                        however events are written to log.
    """

    # Get all uuids
    list_of_uuids = oio.get_all(resource)

    # Debug
    log.debug(list_of_uuids)

    for uuid in list_of_uuids:
        # Retrieve
        results = oio.get_request(
            resource=resource,
            uuid=uuid
        )

        # Additional (paranoia) check
        # List should only contain 1 result
        if len(results) != 1:
            log.error(
                "OIO REST api has returned more than 1 result"
            )

            # Debug
            log.debug(results)

            continue

        # Pick first result
        result = results[0]

        # Send result to the appropriate handler
        list_of_updates = handler(result)

        # Continue if there is nothing to update
        if not list_of_updates:
            log.info(
                "No updates for '{resource}': {identifier}".format(
                    resource=resource,
                    identifier=uuid
                )
            )
            continue

        # Info
        log.info(
            "The following items must be updated: {}".format(list_of_updates)
        )

        # Extract object from the 'regigisteringer's list
        registrering = result['registreringer'][0]

        # Iterate over the sections of the registrering object
        # and apply updates for matched key/value pairs
        for update in list_of_updates:

            # Info
            log.info("Applying update: {0}".format(update))

            # Update registrering
            apply_update(registrering, update)

        # Send OIO update request
        send_update(resource, uuid, registrering)


def apply_update(registrering, update):
    """
    TODO: Needs to be simplified

    Dynamically traverse through the section and key of the object
    in order to find matching key/value pairs which must be updated.

    If a matching key/value pair is found,
    the values of the original keys are replaced with the updated values.

    Example:

    "registrering":
        {
            "attributter": {  <-- "section"
                "brugeregenskaber": [  <-- "key"
                    {
                        "ava_fornavn":  "Existing First Name"
                    }
                ]
            }
        }

    "update":
        {
            "ava_fornavn":  "New First Name"
        }

    In this example the matching key/value pair is "ava_fornavn".
    The value of the "existing" pair will be replaced with the "update" value.

    :param registrering:    The full "registering" (OIO) object
                            See example above.

    :param update:          The update object containing key/value pairs
                            which should be updated.
                            See example above.

    :return:                The function does not return anything,
                            the "registering" object is modified/updated
    """

    # Map update dictionary
    section = update["section"]
    key = update["key"]
    content = update["update"]

    # Iterate over all items in the list
    # Target the items that needs to be updated
    for item in registrering[section][key]:

        # Next we need to target the key/value pairs
        # which need to be updated
        for key in content.keys():

            if key not in item.keys():
                continue

            # Replace the item values with updated values
            item[key] = content[key]


def send_update(resource, uuid, update):
    """
    Construct a HTTP request to update an existing object.

    The expected response is HTTP 200,
    if the expected response is not returned,
    the event is written to the log along with the failed response.

    The failed object is included in the log.
    TODO:   the object contains sensitive data
            and it may not be appropriate to include

    For more detailed information on the request,
    please see the underlying PUT request from the oio_interface module.

    :param resource:    Name of the OIO entity

    :param uuid:        Identifier of the exising object

    :param update:      The modified/updated "registering" object
                        (Full object with updated key/value pairs)

    :return:            Returns boolean,
                        additionally the HTTP response (200) is logged,
                        e.g.
                        Response: 200 (bruger: <identifier/uuid>)
    """

    # Info
    log.info("Sending update request")

    # Update PUT request
    response = oio.put_request(
        resource=resource,
        identifier=uuid,
        payload=update
    )

    # Not updated (Not HTTP 200)
    if not response.status_code == 200:
        log.error(
            "PUT request returned: {status}".format(
                status=response.status_code
            )
        )

        # Log response
        log.error(response.text)

        # Debug
        # Include failed object
        log.error(update)

        return False

    # Info

    log.info(
        "Response: {status} ({resource}: {identifier})".format(
            status=response.status_code,
            resource=resource,
            identifier=uuid
        )
    )

    return True


if __name__ == "__main__":

    # List of available tasks
    available_tasks = [
        ("bruger", cpr_handler),
        ("organisation", cvr_handler)
    ]

    # Run all tasks from the list
    for resource, handler in available_tasks:
        run_task(resource, handler)
