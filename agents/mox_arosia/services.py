import json
import pymssql
import time

import pika
import requests
from serviceplatformen_cpr.services import get_citizen as _get_cpr_data
from serviceplatformen_cvr import get_cvr_data as _get_cvr_data

from settings import CERTIFICATE_FILE, ERROR_MQ_HOST, ERROR_MQ_QUEUE, SP_UUIDS


def report_error(error_message, error_stack=None, error_object=None):
    source = "MOX AROSIA"
    error_msg = {
        "source": source,
        "error_mesage": error_message,
        "error_stack": error_stack,
        "error_object": error_object
    }

    # TODO: Remove this
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


def get_cpr_data(id_number):
    # TODO: Remove this
    return {
        "statsborgerskab": "5100",
        "efternavn": "Jensen",
        "postdistrikt": "Næstved",
        "foedselsregistreringssted": "Myndighedsnavn for landekode: 5902",
        "boernUnder18": "false",
        "civilstandsdato": "1991-03-21+01:00",
        "adresseringsnavn": "Jens Jensner Jensen",
        "fornavn": "Jens Jensner",
        "tilflytningsdato": "2001-12-01+01:00",
        "markedsfoeringsbeskyttelse": "true",
        "vejkode": "1759",
        "standardadresse": "Sterkelsvej 17 A,2",
        "etage": "02",
        "koen": "M",
        "status": "80",
        "foedselsdato": "1978-04-27+01:00",
        "vejnavn": "Sterkelsvej",
        "statsborgerskabdato": "1991-09-23+02:00",
        "adressebeskyttelse": "false",
        "stilling": "Sygepl ske",
        "gaeldendePersonnummer": "2704785263",
        "vejadresseringsnavn": "Sterkelsvej",
        "civilstand": "G",
        "alder": "59",
        "relationer": [
            {
                "cprnr": "0123456780",
                "relation": "aegtefaelle"
            },
            {
                "cprnr": "1123456789",
                "relation": "barn"
            },
            {
                "cprnr": "2123456789",
                "relation": "barn"
            },
            {
                "cprnr": "3123456789",
                "relation": "barn"
            },
            {
                "cprnr": "0000000000",
                "relation": "mor"
            },
            {
                "cprnr": "0000000000",
                "relation": "far"
            }
        ],
        "postnummer": "4700",
        "husnummer": "017A",
        "vejviserbeskyttelse": "true",
        "kommunekode": "370"
    }

    # Avoid getting throttled by SP
    try:
        person_dir = _get_cpr_data(service_uuids=SP_UUIDS,
                                   certificate=CERTIFICATE_FILE,
                                   cprnr=id_number)
    except Exception as e:
        # Retry *once* after sleeping
        time.sleep(40)
        try:
            person_dir = _get_cpr_data(service_uuids=SP_UUIDS,
                                       certificate=CERTIFICATE_FILE,
                                       cprnr=id_number)
        except Exception as e:
            report_error(
                "CPR number not found: {0}".format(id_number)
            )
            return None
    return person_dir


def get_cvr_data(id_number):
    # TODO: Remove this
    return {
        "vejkode": "5520",
        "virksomhedsform": 80,
        "etage": "3",
        "organisationsnavn": "MAGENTA ApS",
        "kommunekode": "0101",
        "doer": "",
        "branchekode": "620200",
        "vejnavn": "Pilestr\u00e6de",
        "dawa_uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
        "husnummer": "43",
        "postnummer": "1112",
        "postboks": "",
        "branchebeskrivelse": "Konsulentbistand vedr\u00f8rende informationsteknologi"
    }

    try:
        company_dir = _get_cvr_data(id_number, SP_UUIDS, CERTIFICATE_FILE)
    except Exception as e:
        # Retry *once* after sleeping
        time.sleep(40)
        try:
            company_dir = _get_cvr_data(id_number, SP_UUIDS, CERTIFICATE_FILE)
        except Exception as e:
            report_error(
                "CVR number not found: {0}".format(id_number)
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


def connect(server, database, username, password):
    driver1 = '{SQL Server}'
    driver2 = '{ODBC Driver 13 for SQL Server}'
    connection = None
    try:
        connection = pymssql.connect(server=server, user=username,
                                     password=password, database=database)
    except Exception as e:
        print(e)
        report_error(str(e))
        raise
    return connection
