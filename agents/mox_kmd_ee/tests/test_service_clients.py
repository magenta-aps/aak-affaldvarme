import common

import os
import smtpd
import pika
import subprocess
import time
import threading
import asyncore
import service_clients


class MailServer(smtpd.SMTPServer):
    messages = []

    def process_message(self, *args, **kwargs):
        self.messages.append((args, kwargs))


class TestServiceClients(common.Test):

    def empty_queue(self):
        received = []
        while True:
            method_frame, header_frame, body = self.channel.basic_get(
                queue=service_clients.ERROR_MQ_QUEUE)
            if not method_frame or method_frame.NAME == 'Basic.GetEmpty':
                break
            else:
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                received.append((method_frame, header_frame, body))
        return received

    def setUp(self):
        super().setUp()
        if os.path.exists("var/bulkfile.txt"):
            os.unlink("var/bulkfile.txt")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=service_clients.ERROR_MQ_HOST)
        )

        # Initiate channel
        self.channel = self.connection.channel()
        self.empty_queue()

    def test_report_error_amqp_integration(self):
        "send via amqp and subsequently via mail sent by the queue callback"

        # start the mailserver and it's loop in a thread
        m = MailServer(("localhost", 1025), remoteaddr=None, decode_data=True)
        thread = threading.Thread(target=asyncore.loop, kwargs={"timeout": 2})
        thread.start()

        # run the mox_error_handler until stopped
        p = subprocess.Popen(
            ["python", "../mox_error_handler/run_agent.py"],
            cwd="../mox_error_handler"
            )

        # send an error to file via queue
        service_clients.report_error_amqp("this is a test-line", headers={
            "x-ava-bulk-report": os.path.abspath("./var/bulkfile.txt")
        })

        # make queue send the file by supplying an smtp server
        service_clients.report_error_amqp("This is the mail subject", headers={
            "x-ava-bulk-report": os.path.abspath("./var/bulkfile.txt"),
            "x-ava-bulk-to": "to@example.org",
            "x-ava-bulk-from": "from@example.org",
            "x-ava-bulk-smtp": "localhost:1025"
        })

        # wait a long time
        time.sleep(2)

        # stop mox_error_handler
        p.terminate()

        # stop mail server
        m.close()

        # wait for asyncore loop to timeout after stopped mail server
        thread.join()

        # print (m.messages)
        # there should be a mail waiting for delivery
        self.assertEqual(len(m.messages), 1)
