import common

# steer clear of production data

import os, sys
import smtpd
import pika
import subprocess 
import time
import threading
import asyncore

# mut - module under test
import service_clients

class MailServer(smtpd.SMTPServer):
    messages=[]
    def process_message(self,*args,**kwargs):
        self.messages.append((args,kwargs))


class TestServiceClients(common.Test):
    def empty_queue(self):
        received=[]        
        while True:
            method_frame, header_frame, body = self.channel.basic_get(
                queue = self.mut.ERROR_MQ_QUEUE)
            if not method_frame or method_frame.NAME == 'Basic.GetEmpty':
                break
            else:
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                received.append((method_frame, header_frame, body))
        return received

    def setUp(self):
        super().setUp()
        mut = self.mut = service_clients
        if os.path.exists("var/bulkfile.txt"):
            os.unlink("var/bulkfile.txt")
        #self.empty_queue()


    def test_report_error_bulk_integration(self):
        # start the mailserver
        m = MailServer(("localhost",1025),None)
        thread =  threading.Thread(target=asyncore.loop,kwargs = {'timeout':4} )
        thread.start()
        # run the mox_error_handler for a short while
        p = subprocess.Popen(["python","../mox_error_handler/run_agent.py"], cwd="../mox_error_handler")
        # send the errors
        self.mut.report_error("this is a test-line",headers={
            "x-ava-bulk-report": os.path.abspath("./var/bulkfile.txt")
        })
        self.mut.report_error("This is the mail subject",headers={
            "x-ava-bulk-report": os.path.abspath("./var/bulkfile.txt"),
            "x-ava-bulk-to":"to@example.org",
            "x-ava-bulk-from":"from@example.org",
            "x-ava-bulk-smtp":"localhost:1025"
        })
        time.sleep(4)
        # stop mox_error_handler
        p.terminate()
        # stop mail server
        m.close()
        thread.join()
        #print (m.messages)
        self.assertEqual(len(m.messages),1)

        
        
