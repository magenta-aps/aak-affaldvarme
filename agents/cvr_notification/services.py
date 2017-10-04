import pika
import requests
from serviceplatformen_cvr import get_cvr_data

from settings import ERROR_MQ_HOST, ERROR_MQ_QUEUE, LORA_URL, \
    LORA_ORG_BATCH_SIZE, UUIDS, SERVICE_CERTIFICATE


def report_error(error_message, error_stack=None, error_object=None):
    source = "CVR notification"
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


def update_organisation_in_lora(update_json, uuid):
    url = '{0}/organisation/organisation/{1}'.format(LORA_URL, uuid)
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=update_json, headers=headers)

    if not response:
        raise RuntimeError(
            'PUT {0}, {1}, {2} responded with {3}'.format(url, update_json,
                                                          headers, response))


def fetch_associated_orgs_from_lora(uuid):
    params = {
        'tilhoerer': uuid
    }
    url = LORA_URL + '/organisation/organisation'
    response = requests.get(url, params=params)

    if not response:
        raise RuntimeError(
            'GET {0}, {1} responded with {2}'.format(url, params, response))

    if 'results' in response.json() and len(response.json()['results']) > 0:
        return response.json()['results'][0]


def fetch_org_data_from_lora(org_uuids):
    url = LORA_URL + '/organisation/organisation'

    remainder = org_uuids
    while len(remainder) > 0:
        batch = remainder[:LORA_ORG_BATCH_SIZE]
        remainder = remainder[LORA_ORG_BATCH_SIZE:]

        params = {'uuid': batch}
        response = requests.get(url, params=params)

        if not response:
            raise RuntimeError(
                'GET {0}, {1} responded with {2}'.format(url, params, response))

        results = response.json()['results'][0]

        for result in results:
            yield result


def get_cvr_data_from_serviceplatform(cvr):
    cvr_data = get_cvr_data(cvr, UUIDS, SERVICE_CERTIFICATE)

    return cvr_data
