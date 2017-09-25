# imports
import os
from dotenv import load_dotenv
from os.path import join, dirname

# Get .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

install_path = os.path.abspath(dirname(__file__))

SP_CERTIFICATE_PATH = join(
    dirname(__file__), (os.environ.get('SP_CERTIFICATE_PATH'))
)

# Generic invocation context UUIDS for production environment
SP_USER_SYSTEM_UUID_PROD = os.environ.get('SP_USER_SYSTEM_UUID_PROD')
SP_USER_UUID_PROD = os.environ.get('SP_USER_UUID_PROD')

# *** Service SF1520(Production) - Udvidet person stamdata (lokal) *** #

# SF1520 specific invocation context UUIDS
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
# Path to specific soap envelope template for SF1520
SP_SF1520_SOAP_ENVELOPE_TEMPLATE = os.environ.get(
    'SP_SF1520_SOAP_ENVELOPE_TEMPLATE'
)

# *** Service SF6002(Production) - CPR Abonement *** #

# SF6002 specific invocation context UUIDS
SP_SERVICE_AGREEMENT_UUID_SF6002_PROD = os.environ.get(
    'SP_SERVICE_AGREEMENT_UUID_SF6002_PROD'
)
SP_SERVICE_SF6002_PROD = os.environ.get(
    'SP_SERVICE_SF6002_PROD'
)

# Endpoint for service SF6002
SP_SERVICE_ENDPOINT_CPR_SUBSCRIPTION_1 = os.environ.get(
    'SP_SERVICE_ENDPOINT_CPR_SUBSCRIPTION_1'
)
# Path to specific soap envelope template for SF6002

SP_SF6002_SOAP_ENVELOPE_TEMPLATE = os.environ.get('SP_SF6002_SOAP_ENVELOPE_TEMPLATE')
