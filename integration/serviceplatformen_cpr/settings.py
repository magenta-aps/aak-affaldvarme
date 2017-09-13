# imports
import os
from dotenv import load_dotenv
from os.path import join, dirname

# Get .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SP_CERTIFICATE_PATH = os.environ.get('SP_CERTIFICATE_PATH')

# Generic invocation context UUIDS for production environment
SP_USER_SYSTEM_UUID_PROD = os.environ.get('SP_USER_SYSTEM_UUID_PROD')
SP_USER_UUID_PROD = os.environ.get('SP_USER_UUID_PROD')

# Specific invocation context UUIDS
# Service SF6001 - ADRSOG1 CPR Opslag (lokal)
SP_SERVICE_ENDPOINT_CPRLOOKUP_2 = os.environ.get(
    'SP_SERVICE_ENDPOINT_CPRLOOKUP_2'
)
SP_SERVICE_AGREEMENT_UUID_SF6001_PROD = os.environ.get(
    'SP_SERVICE_AGREEMENT_UUID_SF6001_PROD'
)
SP_SF6001_SOAP_ENVELOPE_TEMPLATE = os.environ.get(
    'SP_SF6001_SOAP_ENVELOPE_TEMPLATE'
)
SP_SERVICE_SF6001_PROD = os.environ.get('SP_SERVICE_SF6001_PROD')
