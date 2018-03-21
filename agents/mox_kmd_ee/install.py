#!/usr/bin/python3

import os
import sys

from installutils import Config, VirtualEnv

DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

print('Installing service')

venv = VirtualEnv(os.path.join(DIR, 'python-env'))
venv.run('-m', 'pip', 'install', '-r', 'requirements.txt')

config = Config(os.path.join(DIR, "mssql_config.py"))
config.prompt([
    ('server', 'server'),
    ('database', 'database'),
    ('username', 'username'),
    ('password', 'password'),
])
config.save()

# service = Service('mox_kmd_ee.sh', user='mox_kmd_ee')
# service.install()

settings_path = os.path.join(DIR, 'settings.py')

if not os.path.exists(settings_path):
    with open(settings_path, 'wt') as fp:
        fp.write('''
# TODO: Use authentication & real user UUID.
SYSTEM_USER = ""

# AVA-Organisation
AVA_ORGANISATION = ""

# API URL
BASE_URL = ""

CERTIFICATE_FILE = ''

SP_UUIDS = {
    "service_agreement": "",
    "user_system": "",
    "user": "",
    "service": ""
}

# Hostname of the AMQP server
ERROR_MQ_HOST = "localhost"

# Name of the queue
ERROR_MQ_QUEUE = "ava_mox_errors"

# SMTP-server for sending errors in bulk
# example: localhost 
# example: localhost:1025
ERROR_BULK_MAIL_HOST = ""

# Email-addresses of error-mail-recipients
# example: ["me@example.com","you@example.com"]
ERROR_BULK_MAIL_TO = []

# Email-address of error-mail-sender
# example: "me@example.com"
ERROR_BULK_MAIL_FROM = ""

# where are the bulk-mail-files put
ERROR_BULK_MAIL_DIR = "var"
'''.lstrip())
