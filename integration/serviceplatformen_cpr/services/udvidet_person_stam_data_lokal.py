# -- coding: utf-8 --
import requests
import settings
import xmltodict

from helpers.soap import build_soap_envelope
from helpers.validation import validate_cprnr


__author__ = "Heini Leander Ovason"


def get_citizen(service_uuids, certificate, cprnr):
    """The function returnes a citizen dict from the
    'SF1520 - Udvidet person stamdata (lokal)' service.
    It serves as a facade to simplify input validation, and interaction
    with the SOAP service, parsing and filtering the response.
    :param cprnr: Danish cprnr
    :type cpr: String of 10 digits / r'^\d{10}$'
    :return: Dictionary representation of a citizen.
    :rtype: dict"""

    is_cprnr_valid = validate_cprnr(cprnr)

    if is_cprnr_valid:

        soap_envelope_template = settings.SP_SF1520_SOAP_ENVELOPE_TEMPLATE

        soap_envelope = build_soap_envelope(
            soap_envelope_template=soap_envelope_template,
            service_uuids=service_uuids,
            cprnr=cprnr
        )

        response = call_cpr_person_lookup_request(
            soap_envelope=soap_envelope,
            certificate=certificate
        )

        if response.status_code is 200:

            citizen_dict = parse_and_filter_cpr_person_lookup_response(
                soap_response_xml=response.text
            )

            return citizen_dict


def call_cpr_person_lookup_request(soap_envelope, certificate):
    """Description pending.
    return string"""

    service_url = settings.SP_SERVICE_ENDPOINT_CPR_INFORMATION_1

    response = requests.post(
        url=service_url,
        data=soap_envelope,
        cert=certificate
    )

    return response


def parse_and_filter_cpr_person_lookup_response(soap_response_xml):

    xml_to_dict = xmltodict.parse(soap_response_xml)

    return xml_to_dict
