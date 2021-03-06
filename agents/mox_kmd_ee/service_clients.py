"""Clients for various Internet services."""
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import time
import datetime
import functools

import requests
import pika

try:
    from serviceplatformen_cvr import get_cvr_data as _get_cvr_data
except ImportError:
    def _get_cvr_data(id):
        pass


from settings import SP_UUIDS, CERTIFICATE_FILE, ERROR_MQ_QUEUE, ERROR_MQ_HOST


DAWA_ADDRESS_URL = 'http://dawa.aws.dk/adresser'
DAWA_ACCESS_URL = 'http://dawa.aws.dk/adgangsadresser'


def get_address_from_service(dawa_service, as_tuple, address):
    """Get DAWA UUID from dictionary with correct fields."""
    address['struktur'] = 'mini'

    # allow looking up by id only
    if 'id' in address or len(address) > 2:
        pass
    else:
        raise RuntimeError("Insufficient data")

    try:
        response = requests.get(
            url=dawa_service,
            params=address
        )
    except MemoryError:
        print("MemoryError with address = ", address)
        print("Bug in requests module?")
        return

    if response.status_code == 429:
        # Sleep and retry
        time.sleep(1)
        response = requests.get(
            url=dawa_service,
            params=address
        )
    try:
        js = response.json()
    except json.decoder.JSONDecodeError:
        print("Problem looking up address:", str(address),
              response.text)
        if response.status_code == 429:
            print("Blocked by DAWA!")
            response.raise_for_status()
        else:
            raise RuntimeError("Internal Server Error from Dawa")

    if len(js) == 1:
        address_uuid = js[0]['id']
    elif len(js) > 1:
        raise RuntimeError('Non-unique address')
    else:
        # len(js) == 0
        raise RuntimeError('Address not found')
    if as_tuple:
        return address_uuid, js
    else:
        return address_uuid


get_address_uuid = functools.partial(get_address_from_service,
                                     DAWA_ADDRESS_URL, False)
access_address_uuid = functools.partial(get_address_from_service,
                                        DAWA_ACCESS_URL, False)


def fuzzy_address_uuid(addr_str):
    """Get DAWA UUID from string using the 'datavask' API."""
    DAWA_DATAVASK_URL = "https://dawa.aws.dk/datavask/adresser"

    params = {'betegnelse': addr_str}

    result = requests.get(url=DAWA_DATAVASK_URL, params=params)

    if result:
        addrs = result.json()['resultater']
        if len(addrs) == 1:
            if addrs[0]['adresse']['status'] in [2, 4]:
                return addrs[0]['adresse']['adgangsadresseid']
            else:
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
        result.raise_for_status()
        # raise RuntimeError("Unable to look up address: {0}".format(addr_str))


def get_cvr_data(cvr_number):
    """Get CVR data from Serviceplatformen."""
    return _get_cvr_data(cvr_number, SP_UUIDS, CERTIFICATE_FILE)


def report_error(error_message, error_stack=None, error_object=None):
    """Report error, logging to file and sending to an AMQP Queue.

    The AMQP queue will decide what to do with the various errors depending on
    their gravity - e.g inform users by email, log to a special log or discard.
    """
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

    try:
        channel.basic_publish(
            exchange='', routing_key=ERROR_MQ_QUEUE, body=json.dumps(error_msg)
        )
    except Exception:
        print("Unable to send", error_msg, "to AMQP service")
    connection.close()

    # Print error to the error file
    todaystr = str(datetime.datetime.today().date())
    with open("var/mox_kmd_ee_{0}.log".format(todaystr), "a") as f:
        f.write(error_message + '\n\n')


if __name__ == '__main__':
    report_error("Hej med dig!")
    uuid = fuzzy_address_uuid('Parkvej 56, 8920 Randers NV')
    assert uuid == get_address_uuid({'id':uuid})
