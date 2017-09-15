# -- coding: utf-8 --
import re
import requests
import settings
import xmltodict

from jinja2 import Template


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

        payload = build_soap_envelope(service_uuids, cprnr)

        response = call_cpr_person_lookup_request(
            soap_envelope=payload,
            certificate=certificate
        )

        if response.status_code is 200:

            citizen_dict = parse_and_filter_cpr_person_lookup_response(
                soap_response_xml=response.text
            )

            return citizen_dict


def validate_cprnr(cprnr):
    # TODO: This function can be more generic and moved into a utilities module

    if cprnr is not None:

        check = re.match(r'^\d{10}$', cprnr)

        if check:

            return True

        else:

            raise ValueError('"{}" is not a valid Danish cprnr.'.format(cprnr))
    else:

        raise TypeError('"{}" is not a valid type.'.format(cprnr))


def build_soap_envelope(service_uuids, cprnr):
    # TODO: This function can be more generic and moved into a utilities module

    envelope_template = settings.SP_SF1520_SOAP_ENVELOPE_TEMPLATE

    with open(envelope_template, "r") as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids['service_agreement'],
        user_system=service_uuids['user_system'],
        user=service_uuids['user'],
        service=service_uuids['service']
    )

    # requests response will throw UnicodeEncodeError otherwise.
    latin_1_encoded_soap_envelope = populated_template.encode('latin-1')

    return latin_1_encoded_soap_envelope


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
