#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import datetime
import functools

import requests
import pika

from serviceplatformen_cvr import get_cvr_data as _get_cvr_data

from settings import SP_UUIDS, CERTIFICATE_FILE, ERROR_MQ_QUEUE, ERROR_MQ_HOST


DAWA_ADDRESS_URL = 'https://dawa.aws.dk/adresser'
DAWA_ACCESS_URL = 'https://dawa.aws.dk/adgangsadresser'


def get_address_from_service(dawa_service, address):
    "Get DAWA UUID from dictionary with correct fields."

    address['struktur'] = 'mini'

    response = requests.get(
        url=dawa_service,
        params=address
    )
    js = response.json()

    if len(js) == 1:
        address_uuid = js[0]['id']
    elif len(js) > 1:
        raise RuntimeError('Non-unique address: {0}'.format(address))
    else:
        # len(js) == 0
        raise RuntimeError('Address not found: {0}'.format(address))
    print(address_uuid, dawa_service)
    return address_uuid


get_address_uuid = functools.partial(get_address_from_service,
                                     DAWA_ADDRESS_URL)
access_address_uuid = functools.partial(get_address_from_service,
                                        DAWA_ACCESS_URL)


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
        print("Error when looking up address:", result)
        raise RuntimeError("Unable to look up address: {0}".format(addr_str))


def get_cvr_data(cvr_number):
    return _get_cvr_data(cvr_number, SP_UUIDS, CERTIFICATE_FILE)


def report_error(error_message, error_stack=None, error_object=None):
    source = "MOX KMD EE"
    error_msg = {
        "source": source,
        "error_mesage": error_message,
        "error_stack": error_stack,
        "error_object": error_object
    }
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ERROR_MQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=ERROR_MQ_QUEUE, durable=True)

    channel.basic_publish(
        exchange='', routing_key=ERROR_MQ_QUEUE, body=json.dumps(error_msg)
    )
    connection.close()

    # Print error to the error file
    todaystr = str(datetime.datetime.today().date())
    with open("mox_kmd_ee_{0}.log".format(todaystr), "a") as f:
        f.write(error_message + '\n\n')


if __name__ == '__main__':

    print(fuzzy_address_uuid('Parkvej 56, 8920 Randers NV'))
