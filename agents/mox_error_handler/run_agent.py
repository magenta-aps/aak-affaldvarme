# -*- coding: utf-8 -*-

import json
import pika
import logging

from logger import start_logging

from settings import MQ_HOST
from settings import MQ_QUEUE
from settings import LOG_FILE
from settings import DO_USE_DEBUG_LOG

# Set connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=MQ_HOST)
)

# Initiate channel
channel = connection.channel()

# Declare queue
channel.queue_declare(queue=MQ_QUEUE)


def callback(ch, method, properties, body):
    """This method is the message handler"""

    # Create logger
    log = logging.getLogger("auto")

    if not body:
        return False

    # Convert to dict
    received = json.loads(body)

    # Required(ish) fields
    # TODO: Check for the following fields
    # requirements = ["source", "error_message", "error_stack", "error_object"]
    source = received.get("source")
    error_message = received.get("error_message")
    error_stack = received.get("error_stack")
    error_object = received.get("error_object")

    # Log error message
    log.error(
        "({source}): {message}".format(
            source=source,
            message=error_message
        )
    )

    # Log error stack
    log.error(
        "({source}): {stack}".format(
            source=source,
            stack=error_stack
        )
    )

    # Data object that failed processing
    log.error(
        "({source}): {object}".format(
            source=source,
            object=error_object
        )
    )


def consume():
    # Configure consume method
    channel.basic_consume(
        callback,
        queue=MQ_QUEUE,
        no_ack=True
    )

    # Notify user that the listener is started
    print("Listening for errors. To exit press CTRL+C")

    try:
        channel.start_consuming()

    except KeyboardInterrupt:
        connection.close()

    finally:
        print("\nConnection closed - Exiting!")


# Run consume for testing
if __name__ == "__main__":

    if DO_USE_DEBUG_LOG:
        LOG_FILE = "debug.log"

    # Start logging
    start_logging(
        name="auto",
        logfile=LOG_FILE,
    )

    # Start consumer
    consume()
