# -- coding: utf-8 --
from jinja2 import Template

__author__ = "Heini Leander Ovason"


def construct_envelope_SF1520(template, service_uuids, cprnr):
    """The function returnes a envelope for the service
    'SF1520 - Udvidet person stamdata (lokal)'."""

    with open(template, "r") as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids['service_agreement'],
        user_system=service_uuids['user_system'],
        user=service_uuids['user'],
        service=service_uuids['service']
    )

    # service platform requirement.
    latin_1_encoded_soap_envelope = populated_template.encode('latin-1')

    return latin_1_encoded_soap_envelope


def construct_envelope_SF6002(template, service_uuids, cprnr, operation):
    """The function returnes a envelope for the service
    'SF6002 - CPR Abonnement'."""

    with open(template, "r") as filestream:
        template_string = filestream.read()

    xml_template = Template(template_string)

    populated_template = xml_template.render(
        cprnr=cprnr,
        service_agreement=service_uuids['service_agreement'],
        user_system=service_uuids['user_system'],
        user=service_uuids['user'],
        service=service_uuids['service'],
        operation=operation
    )

    # service platform requirement.
    latin_1_encoded_soap_envelope = populated_template.encode('latin-1')

    return latin_1_encoded_soap_envelope
