# -*- coding: utf-8 -*-

import json
import pika
import logging

from logger import start_logging

from email.mime.text import MIMEText
import smtplib

from settings import MQ_HOST
from settings import MQ_QUEUE
from settings import LOG_FILE   # noqa: F811
from settings import DO_USE_DEBUG_LOG

# Set connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=MQ_HOST)
)

# Initiate channel
channel = connection.channel()

# Declare queue
try:
    channel.queue_declare(queue=MQ_QUEUE)
except pika.exceptions.ChannelClosed:
    # https://github.com/MassTransit/MassTransit/issues/370
    channel = connection.channel()
    pass


def route_via_mail(source, msg, stack, obj, headers, log):
    """ Handling mail-sending of report
    """
    # get bulk file and possibly smtp server
    bulk_report = headers.get("x-ava-bulk-report", "")
    bulk_smtp = headers.get("x-ava-bulk-smtp", "")

    # send mail now if smtp server specified
    if bulk_smtp:

        # compose mail
        bulk_from = headers.get("x-ava-bulk-from", "")
        bulk_to = headers.get("x-ava-bulk-to", "")
        mail = MIMEText(open(bulk_report).read())
        mail["Subject"] = msg
        mail["To"] = bulk_to
        mail["From"] = bulk_from

        # connect to smtp host/port
        if ":" in bulk_smtp:
            host, port = bulk_smtp.split(":")
            port = int(port)
        else:
            host, port = bulk_smtp, 25
        smtp = smtplib.SMTP()
        # smtp.set_debuglevel(1)
        smtp.connect(host, port)

        # send mail
        smtp.sendmail(
            bulk_from,
            [bulk_to],
            mail.as_string()
        )
        log.info("mail sent :%r", headers)

    # else write message to bulk mail file
    elif msg:
        "add the line to the bulkfile"
        with open(bulk_report, "a") as f:
            f.write(msg + '\n\n')


def route_via_headers(source, msg, stack, obj, headers, log):
    """ Routing error messages as specified in headers
    """
    if headers.get("x-ava-bulk-report", ""):
        route_via_mail(source, msg, stack, obj, headers, log)
    else:
        log.error(
            "({source}): no route for headers: {headers}".format(
                source=source,
                headers=headers
            )
        )


def callback(ch, method, properties, body):
    """This method is the message handler"""

    # Create logger
    log = logging.getLogger("auto")

    if not body:
        return False

    # Convert to dict
    received = json.loads(body.decode("utf-8"))

    # Required(ish) fields
    # TODO: Check for the following fields
    # requirements = ["source", "error_message", "error_stack", "error_object"]
    source = received.get("source")
    error_message = received.get("error_message")
    error_stack = received.get("error_stack")
    error_object = received.get("error_object")
    error_headers = properties.headers

    if error_message:
        # Log error message
        log.error(
            "({source}): {message}".format(
                source=source,
                message=error_message
            )
        )

    if error_stack:
        # Log error stack
        log.error(
            "({source}): {stack}".format(
                source=source,
                stack=error_stack
            )
        )

    if error_object:
        # Data object that failed processing
        log.error(
            "({source}): {object}".format(
                source=source,
                object=error_object
            )
        )

    if error_headers:
        # Handle special cases like bulk sending etc
        try:
            route_via_headers(
                source, error_message, error_stack,
                error_object, error_headers, log=log
                )
        except Exception as e:
            log.error(
                "({source}): failure {e} when "
                "handling headers: {headers}".format(
                    source=source, e=e,
                    headers=error_headers
                )
            )

    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume():
    # Configure consume method
    channel.basic_consume(
        callback,
        queue=MQ_QUEUE
    )

    # Notify user that the listener is started
    print("Listening for errors. To exit press CTRL+C")

    try:
        channel.start_consuming()

    except KeyboardInterrupt:
        channel.stop_consuming()

    finally:
        connection.close()
        print("\nConnection closed - Exiting!")


# Run consume for testing
if __name__ == "__main__":

    if DO_USE_DEBUG_LOG:
        LOG_FILE = "debug.log"  # noqa: F811

    # Start logging
    start_logging(
        name="auto",
        logfile=LOG_FILE,
    )

    # Start consumer
    consume()
