# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from logging import getLogger
import requests
from helper import get_config


# Init logging
log = getLogger(__name__)

# Get config
config = get_config("oio")

# Settings
OIO_REST_URL = config["oio_rest_url"]

ORGANISATION_UUID = config["parent_organisation"]

DO_VERIFY_SSL_SIGNATURE = config.getboolean(
    "do_verify_ssl_signature", "yes"
)

# Resource switch
# To retrieve the correct resource path
switch = {
    "bruger": "organisation/bruger",
    "organisation": "organisation/organisation"
}


def get_all(resource):
    """
    Retrieve a list of all objects uuids,
    which belong to the parent organisation (see settings on top).

    :param resource:    Name of the resource path/entity

    :return:            Returns a list of uuids
                        (References only, not the actual objects)
    """

    # Info
    log.info(
        "Attempting to import: {0}".format(resource)
    )

    # Get a list of all object uuids
    list_of_uuids = get_request(
        resource=resource,
        tilhoerer=ORGANISATION_UUID
    )

    # Debug
    log.debug(
        "{total_amount} {resource} uuid(s) returned".format(
            total_amount=len(list_of_uuids),
            resource=resource
        )
    )

    if not list_of_uuids:
        log.error("No uuids returned")
        return None

    return list_of_uuids


def get_request(resource, **params):
    """
    Generic function to perform a HTTP GET request.

    :param resource:    Resource path, e.g. /service/path,
                        Needed in order to generate the service url

    :param params:      (Optional) Query parameters

    :return:            Returns a list of objects or None.

                        NOTE:
                        Currently OIO REST returns a list inside a list,

                        As such, we return the first result,
                        which is the actual list of objects.

                        {
                            "results": [
                                [ <objects...> ]  <-- This is what we want
                            ]
                        }
    """

    # Use switch to determine resource path
    resource_path = switch.get(resource)

    # Generate service url
    service_url = "{base_url}/{resource}".format(
        base_url=OIO_REST_URL,
        resource=resource_path
    )

    # HTTP GET
    oio_response = requests.get(
        url=service_url,
        params=params,
        verify=DO_VERIFY_SSL_SIGNATURE
    )

    # TODO: If request fails, Log to error queue
    if oio_response.status_code != 200:
        return False

    # Extract a list of data from the response
    results = oio_response.json()["results"]

    # Check if the list is empty
    if len(results) <= 0:
        return False

    return results[0]


def put_request(resource, identifier, payload):
    """
    Generic function to perform a HTTP PUT request.

    In OIO Rest terms we use PUT requests update existing objects.
    Alternatively a PUT request can also be used to import a new object
    thereby preserving a pre-existing 'id' (Type: uuid)

    :param resource_path:   Resource path, e.g. /service/path,
                            Needed in order to generate the service url

    :param params:          (Optional) Query parameters

    :return:                Returns HTTP response object.

                            For more information on the response object,
                            please refer to the official documentation
                            of the underlying requests library.
    """

    # Use switch to determine resource path
    resource_path = switch.get(resource)

    # Generate service url
    service_url = "{base_url}/{path}/{uuid}".format(
        base_url=OIO_REST_URL,
        path=resource_path,
        uuid=identifier
    )

    return requests.put(
        url=service_url,
        json=payload,
        verify=DO_VERIFY_SSL_SIGNATURE
    )
