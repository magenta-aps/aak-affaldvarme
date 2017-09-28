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


def callback(ch, method, properties, body):
    """This method is the message handler"""

    # Do something with the error
    error = json.loads(body)
    print(error)


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
    consume()
