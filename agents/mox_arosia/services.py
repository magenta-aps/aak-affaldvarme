import json
import pymssql
import time

import pika
import requests
from serviceplatformen_cpr import get_cpr_data
from serviceplatformen_cvr import get_cvr_data as _get_cvr_data

from settings import (CPR_CERTIFICATE_FILE, CPR_SP_UUIDS, CVR_CERTIFICATE_FILE,
                      CVR_SP_UUIDS, ERROR_MQ_HOST, ERROR_MQ_QUEUE)


def report_error(error_message, error_stack=None, error_object=None):
    source = "MOX AROSIA"
    error_msg = {
        "source": source,
        "error_mesage": error_message,
        "error_stack": error_stack,
        "error_object": error_object
    }

    # TODO: Remove this
    # if not (error_message.startswith('CVR number not found') or
    #        error_message in ['Unable to import contact',]):
    #    raise RuntimeError(error_msg)
    print(error_msg)
    return

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ERROR_MQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=ERROR_MQ_QUEUE, durable=True)

    channel.basic_publish(
        exchange='', routing_key=ERROR_MQ_QUEUE, body=json.dumps(error_msg)
    )
    connection.close()



def get_cvr_data(id_number):
    # TODO: Remove this
    # return {
    #     "vejkode": "5520",
    #     "virksomhedsform": 80,
    #     "etage": "3",
    #     "organisationsnavn": "MAGENTA ApS",
    #     "kommunekode": "0101",
    #     "doer": "",
    #     "branchekode": "620200",
    #     "vejnavn": "Pilestr\u00e6de",
    #     "dawa_uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
    #     "husnummer": "43",
    #     "postnummer": "1112",
    #     "postboks": "",
    #     "branchebeskrivelse": "Konsulentbistand vedr\u00f8rende informationsteknologi"
    # }

    try:
        company_dir = _get_cvr_data(id_number, CVR_SP_UUIDS,
                                    CVR_CERTIFICATE_FILE)
    except (TypeError, IndexError, KeyError) as e:
        report_error(
            "CVR number not found: {0}: {1}".format(id_number, str(e))
        )
        return None
    except Exception as e:
        # Retry *once* after sleeping
        time.sleep(40)
        try:
            company_dir = _get_cvr_data(id_number, CVR_SP_UUIDS,
                                        CVR_CERTIFICATE_FILE)
        except Exception as e:
            report_error(
            "CVR number not found: {0}: {1}".format(id_number, str(e))
            )
            return None
    return company_dir


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
        elif len(addrs) > 1:
            report_error('Non-unique (datavask) address: {0}'.format(addr_str))
        else:
            # len(addrs) == 0
            report_error('(datavask) address not found: {0}'.format(addr_str))
    else:
        return None


def connect(server, database, username, password):
    driver1 = '{SQL Server}'
    driver2 = '{ODBC Driver 13 for SQL Server}'
    connection = None
    try:
        connection = pymssql.connect(server=server, user=username,
                                     password=password, database=database)
    except Exception as e:
        report_error(str(e))
        raise
    return connection
