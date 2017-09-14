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

# *** Service SF1520(Production) - Udvidet person stamdata (lokal) *** #

# Specific invocation context UUIDS
SP_SERVICE_AGREEMENT_UUID_SF1520_PROD = os.environ.get(
    'SP_SERVICE_AGREEMENT_UUID_SF1520_PROD'
)
SP_SERVICE_SF1520_PROD = os.environ.get(
    'SP_SERVICE_SF1520_PROD'
)

# Endpoint for service SF1520
SP_SERVICE_ENDPOINT_CPR_INFORMATION_1 = os.environ.get(
    'SP_SERVICE_ENDPOINT_CPR_INFORMATION_1'
)
# Path to specific soap envelope template
SP_SF1520_SOAP_ENVELOPE_TEMPLATE = os.environ.get(
    'SP_SF1520_SOAP_ENVELOPE_TEMPLATE'
)
