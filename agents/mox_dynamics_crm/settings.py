# -*- coding: utf-8 -*-

import os
from os.path import join, dirname

# Load env variables from .env file
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# General
DO_VERIFY_SSL_SIGNATURE = False
DO_DISABLE_SSL_WARNINGS = True
DO_RUN_IN_TEST_MODE = True

# Logging
LOG_FILE = "/var/log/mox/mox_dynamics_crm.log"

# OIO Rest settings
OIO_REST_URL = os.environ.get('OIO_REST_URL')
ORGANISATION_UUID = os.environ.get('ORGANISATION_UUID')

# DAWA settings
DAWA_SERVICE_URL = "https://dawa.aws.dk/adresser"

# RabbitMQ settings
MQ_HOST = os.environ.get("MQ_HOST")
MQ_PORT = os.environ.get("MQ_PORT")
MQ_EXCHANGE = os.environ.get("MQ_EXCHANGE")

# MS CRM Dynamics 365
CRM_RESOURCE = os.environ.get("RESOURCE")
CRM_TENANT = os.environ.get("TENANT")
CRM_ENDPOINT = os.environ.get("OAUTH_ENDPOINT")
CRM_CLIENT_ID = os.environ.get("CLIENT_ID")
CRM_CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CRM_REST_API_PATH = "api/data/v8.2"
