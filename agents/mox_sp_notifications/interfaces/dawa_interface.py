# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests
from logging import getLogger

# DAR Service settings
BASE_URL = "https://dawa.aws.dk"

# Init logging
log = getLogger(__name__)


def get_request(resource, **params):
    """
    Generic function to build a HTTP GET request.

    A HTTP 200 response is expected,
    other responses are treated as an error and written to logs.

    :param resource:    REST API resource path (e.g. /adresser/<uuid>)

    :param uuid:        Address object identifier (Type: uuid)

    :param params:      Query parameters, by default 'flad'
                        which provides a flattened object structure

    :return:            Returns address object
    """

    # Generate url
    url = "{base_url}/{resource_path}".format(
        base_url=BASE_URL,
        resource_path=resource
    )

    # INFO
    log.info(
        "GET request: {url} (Params: {params})".format(
            url=url,
            params=params
        )
    )

    response = requests.get(
        url=url,
        params=params
    )

    if not response.status_code == 200:
        # Log error
        log.error(response.text)

        return False

    return response.json()


def fuzzy_address_uuid(address_string):
    """
    If a conventional search does not yield any results,
    this function is called to perform a fuzzy address search.

    For more information on the "datavask" resource,
    please see: http://dawa.aws.dk/dok/adresser#adressevask

    :param address_string:  String describing the full address,

                            e.g.
                                "pilestræde 43, 3.sal, 1112 kbh"

    :return:                Returns address object
                            if found by the given string.
    """

    # Resource (Datavask)
    datavask = "datavask/adresser"

    response = get_request(
        resource=datavask,
        betegnelse=address_string
    )

    if not response:
        log.error("Nothing returned from DAR")
        return False

    # Extract results list
    addresses = response["resultater"]

    # If no addresses are returned
    if not addresses:
        log.error(
            "No addresses are matching the search string: {search}".format(
                search=address_string
            )
        )
        return False

    # If more than 1 address is returned,
    # we cannot determine the correct address
    if len(addresses) > 1:
        # Error log
        log.error("Several addresses returned for: {search}".format(
            search=address_string
            )
        )

        # Include addresses
        log.error(addresses)
        return False

    # Extract identifier (DAWA UUID) from address object
    identifier = addresses[0]['adresse']['id']

    return identifier
