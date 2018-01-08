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

# DAR/DAWA settings
AREA_CODE = "0751"

# RabbitMQ settings
MQ_HOST = os.environ.get("MQ_HOST")
MQ_PORT = os.environ.get("MQ_PORT")
MQ_EXCHANGE = os.environ.get("MQ_EXCHANGE")

# Cache settings
CACHE_HOST = os.environ.get("CACHE_HOST", "localhost")
CACHE_PORT = os.environ.get("CACHE_PORT", 27017)
CACHE_USERNAME = os.environ.get("CACHE_USERNAME")
CACHE_PASSWORD = os.environ.get("CACHE_PASSWORD")
CACHE_DATABASE = "loracache"
CACHE_ROLES = ["readWrite"]

# MS CRM Dynamics 365
CRM_RESOURCE = os.environ.get("RESOURCE")
CRM_TENANT = os.environ.get("TENANT")
CRM_ENDPOINT = os.environ.get("OAUTH_ENDPOINT")
CRM_CLIENT_ID = os.environ.get("CLIENT_ID")
CRM_CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CRM_REST_API_PATH = "api/data/v8.2"
CRM_OWNER_ID = os.environ.get("OWNER_ID")
