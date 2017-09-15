# -- coding: utf-8 --
from jinja2 import Template

__author__ = "Heini Leander Ovason"


def build_soap_envelope(soap_envelope_template, service_uuids, cprnr):

    with open(soap_envelope_template, "r") as filestream:
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
