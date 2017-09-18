# -- coding: utf-8 --
import requests
import settings

from helpers.soap import construct_envelope_SF6002
from helpers.validation import validate_cprnr
from helpers.http_requester import http_post


def add_cprnr_to_subscription(service_uuids, certificate, cprnr):

    is_cprnr_valid = validate_cprnr(cprnr)

    if is_cprnr_valid:

        soap_envelope_template = settings.SP_SF6002_SOAP_ENVELOPE_TEMPLATE

        # NOTE: This the name of the remote operation we want to invoke.
        operation = 'AddPNRSubscription'

        soap_envelope = construct_envelope_SF6002(
            template=soap_envelope_template,
            service_uuids=service_uuids,
            cprnr=cprnr,
            operation=operation
        )

        service_url = settings.SP_SERVICE_ENDPOINT_CPR_SUBSCRIPTION_1

        response = http_post(
            endpoint=service_url,
            soap_envelope=soap_envelope,
            certificate=certificate)

        if response.status_code == 200:
            return response.text
        else:
            return {'Error': 'Something went wrong'}
