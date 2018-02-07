# -*- coding: utf-8 -*-

import re
import requests
from logging import getLogger

# DAR Service settings
BASE_URL = "https://dawa.aws.dk"

# Init logging
log = getLogger(__name__)


def get_request(resource, **params):
    """
    Parent GET request primarily used by wrapper functions

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


def fuzzy_address_uuid(addr_str):
    "Get DAWA UUID from string using the 'datavask' API."

    DAWA_DATAVASK_URL = "https://dawa.aws.dk/datavask/adresser"

    params = {'betegnelse': addr_str}

    result = requests.get(url=DAWA_DATAVASK_URL, params=params)

    if result:
        addrs = result.json()['resultater']
        if len(addrs) == 1:
            return addrs[0]['adresse']['id']
        elif len(addrs) > 1:
            # print("Adresses found:")
            # print(addrs)
            raise RuntimeError(
                'Non-unique (datavask) address: {0}'.format(addr_str)
            )
        else:
            # len(addrs) == 0
            raise RuntimeError(
                '(datavask) address not found: {0}'.format(addr_str)
            )
    else:
        return None