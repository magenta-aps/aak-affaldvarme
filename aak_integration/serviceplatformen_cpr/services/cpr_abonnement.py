# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests
import settings
import xmltodict

from helpers.soap import construct_envelope_SF6002
from helpers.validation import validate_cprnr
from helpers.http_requester import http_post


def cprnr_subscription_service(service_uuids, certificate, cprnr, operation):
    """The function serves as a facade to ease the interaction with
    Serviceplatformen's 'SF6002 - CPR Abonnement' service.
    The type of operation you want to perform depends on the type of operation
    that is assigned to the operation parameter key when calling the function.
    :param service_uuids: Serviceplatform invocation context uuids
    :param certificate: Path to Serviceplatform certificate
    :param cprnr: String of 10 digits -> r'^\d{10}$'
    :param operation: 'add' or 'remove'
    :type service_uuids: dict
    :type certificate: str
    :type cprnr: str
    :type operation: str
    :return: Response from the respective Serviceplatform web service operation
    invoked.
    :rtype: str"""

    is_cprnr_valid = validate_cprnr(cprnr)

    if is_cprnr_valid:

        result = None

        if operation == 'add':

            result = invoke_operation(
                service_uuids=service_uuids,
                certificate=certificate,
                cprnr=cprnr,
                operation='AddPNRSubscription'
            )

        elif operation == 'remove':

            result = invoke_operation(
                service_uuids=service_uuids,
                certificate=certificate,
                cprnr=cprnr,
                operation='RemovePNRSubscription'
            )

        else:

            result = 'Invalid operation.'

        return result


def invoke_operation(service_uuids, certificate, cprnr, operation):
    """The function is used to respectively invoke one of the two web service
    operations, 'AddPNRSubscription' or 'RemovePNRSubscription', from
    serviceplatformen's 'SF6002 - CPR Abonnement' service. It does this by
    constructing a SOAP envelope based on the type of operation assigned to
    the operation parameter key when calling the function.
    :param service_uuids: Serviceplatform invocation context uuids
    :param certificate: Path to Serviceplatform certificate
    :param cprnr: String of 10 digits -> r'^\d{10}$'
    :param operation: 'add' or 'remove'
    :type service_uuids: dict
    :type certificate: str
    :type cprnr: str
    :type operation: str
    :return: Response from the respective Serviceplatform web service operation
    invoked.
    :rtype: str"""

    soap_envelope_template = settings.SP_SF6002_SOAP_ENVELOPE_TEMPLATE

    # NOTE: This is the name of the paramter for AddPNRSubscription
    parameter_type = 'PNR'

    soap_envelope = construct_envelope_SF6002(
        template=soap_envelope_template,
        service_uuids=service_uuids,
        cprnr=cprnr,
        operation=operation,
        parameter_type=parameter_type
    )

    service_url = settings.SP_SERVICE_ENDPOINT_CPR_SUBSCRIPTION_1

    response = http_post(
        endpoint=service_url,
        soap_envelope=soap_envelope,
        certificate=certificate
    )

    if response.status_code == 200:

        xml_to_dict = xmltodict.parse(response.text)

        operation = 'ns2:{}Response'.format(operation)

        result = xml_to_dict['soap:Envelope']['soap:Body'][
            operation]['ns2:Result']

        return result

    else:

        return str(response.status_code)
