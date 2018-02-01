# -*- coding: utf-8 -*-

import json
import pika

from settings import MQ_HOST
from settings import MQ_QUEUE

# Set connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=MQ_HOST)
)

# Initiate channel
channel = connection.channel()

# Declare queue
channel.queue_declare(queue=MQ_QUEUE)


def create_error(error_object):

    # Convert dict to json
    error_json = json.dumps(error_object)

    channel.basic_publish(exchange="",
                          routing_key=MQ_QUEUE,
                          body=error_json)
    connection.close()


# Mock error stack
error = "TypeError: handler() missing 1 required positional argument: 'data_object'"

# Mock failed data object
data = {
    "type": "fruit",
    "identifier": "banana",
    "required": None,
    "state": "rotten"

}

# Sample error payload
payload = {
    "source": "Worker One",
    "error_message": "I tried something, but it does not work",
    "error_stack": error,
    "error_object": data
}

# Send error
create_error(payload)
