#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests

from serviceplatformen_cvr import get_cvr_data as _get_cvr_data


def get_address_uuid(address):
    "Get DAWA UUID from dictionary with correct fields."
    DAWA_SERVICE_URL = 'https://dawa.aws.dk/adresser'

    address['struktur'] = 'mini'

    response = requests.get(
        url=DAWA_SERVICE_URL,
        params=address
    )
    js = response.json()

    if len(js) == 1:
        return js[0]['id']
    elif len(js) > 1:
        raise RuntimeError('Non-unique address: {0}'.format(address))
    else:
        # len(js) == 0
        raise RuntimeError('Address not found: {0}'.format(address))


def fuzzy_address_uuid(addr_str):
    "Get DAWA UUID from string using the 'datavask' API."

    DAWA_DATAVASK_URL = "https://dawa.aws.dk/datavask/adresser"

    params = {'betegnelse': addr_str}

    result = requests.get(url=DAWA_DATAVASK_URL, params=params)

    if result:
        addrs = result.json()['resultater']
        if len(addrs) == 1:
            return addrs[0]['adresse']['id']
        else:
            # print("Fundne adresser:", len(addrs), ", ", addr_str)
            return None
    else:
        return None


CERTIFICATE_FILE = 'certificates/magenta_ava_test_2017-03.crt'

SP_UUIDS = {
    "service_agreement": "c97434a1-382f-45c1-8d40-a93e3c3942e8",
    "user_system": "09bf6252-4f71-46f1-b793-eb3cb035f6fa",
    "user": "bfc04260-858c-11e2-9e96-0800200c9a66",
    "service": "93a48b42-3945-11e2-9724-d4bed98c63db"
}


def get_cvr_data(cvr_number):
    return _get_cvr_data(cvr_number, SP_UUIDS, CERTIFICATE_FILE)

if __name__ == '__main__':

    print(fuzzy_address_uuid('Parkvej 56, 8920 Randers NV'))
