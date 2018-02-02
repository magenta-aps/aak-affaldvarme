# -*- coding: utf-8 -*-

import os
import json
import pika
import requests

# Local settings
from settings import MQ_HOST
from settings import MQ_PORT
from settings import MQ_EXCHANGE
from settings import OIO_REST_URL

# MQ
HOST = str(MQ_HOST)
PORT = int(MQ_PORT)


def exchange_listener(callback):
    """
    Create AMQP connection and consume messages
    Accept callback method to run for each message received
    """

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=HOST,
            port=PORT
        )
    )
    channel = connection.channel()

    result = channel.queue_declare(exclusive=True)

    queue_name = result.method.queue

    channel.queue_bind(exchange=MQ_EXCHANGE, queue=queue_name)

    # Run callback method on each notification
    channel.basic_consume(
        consumer_callback=callback,
        queue=queue_name,
        no_ack=True
    )

    # Start consuming
    try:
        # Print something to the console
        print("Waiting for magic to happen...")

        # Run consumer
        channel.start_consuming()

    except KeyboardInterrupt:
        connection.close()

    finally:
        print("\nExiting!")


def callback(ch, method, properties, body):
    """This function is called for each consumed message"""

    # Body is always empty
    # The good stuff is in the header
    headers = properties.headers
    event = headers["livscykluskode"]
    entity = headers["objekttype"]
    identifier = headers["objektID"]

    # Run handler for specific entity
    if entity == "Bruger":
        bruger_handler(event, entity, identifier)

    if entity == "Organisation":
        bruger_handler(event, entity, identifier)

    if entity == "Interessefaellesskab":
        interessefaellesskab_handler(event, entity, identifier)

    if entity == "Organisationfunktion":
        organisationfunktion_handler(event, entity, identifier)

    if entity == "Indsats":
        indsats_handler(event, entity, identifier)

    if entity == "Klasse":
        klasse_handler(event, entity, identifier)


def bruger_handler(event, entity, identifier):

    resource = "organisation/bruger"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)


def organisation_handler(event, entity, identifier):
    resource = "organisation/organisation"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)


def interessefaellesskab_handler(event, entity, identifier):
    resource = "organisation/interessefaellesskab"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)


def organisationfunktion_handler(event, entity, identifier):
    resource = "organisation/organisationfunktion"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)


def indsats_handler(event, entity, identifier):
    resource = "indsats/indsats"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)


def klasse_handler(event, entity, identifier):
    resource = "klassifikation/klasse"
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # For now print the notification parameters
    notification = json.dumps({
        "event": event,
        "entity": entity,
        "identifier": identifier,
        "service": service_url
    }, indent=2)

    # Return object
    print(notification)

# For testing purposes
if __name__ == "__main__":

    # For testing purposes
    exchange_listener(callback)
