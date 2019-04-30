# -- coding: utf-8 --
#
# Copyright (c) 2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import logging
import xmltodict
from mox_cpr_abonnement import settings

# settings must be imported before cpr_abonnement
import cpr_abonnement
from cpr_abonnement.cpr_abonnement import (
    pnr_subscription,
    pnr_all_subscribed,
)


logger = logging.getLogger("mox_cpr_abonnement")


abo_dependencies = {
    "service_endpoint": settings.SP_ABO_SERVICE_ENDPOINT,
    "certificate": settings.SP_ABO_CERTIFICATE,
    "soap_request_envelope": (
        settings.SP_ABO_SOAP_REQUEST_ENVELOPE
        or os.path.join(
            os.path.dirname(cpr_abonnement.cpr_abonnement.__file__),
            "soap_envelope.xml",
        )
    ),
    "system": settings.SP_ABO_SYSTEM,
    "user": settings.SP_ABO_USER,
    "service_agreement": settings.SP_ABO_SERVICE_AGREEMENT,
    "service": settings.SP_ABO_SERVICE,
}


def cpr_add_subscription(pnr):
    logger.debug("add subscription for %s", pnr)
    result = cpr_change_subscription(pnr, settings.ADD_PNR_SUBSCRIPTION)
    return result == "ADDED"


def cpr_remove_subscription(pnr):
    logger.debug("remove subscription for %s", pnr)
    result = cpr_change_subscription(pnr, settings.REMOVE_PNR_SUBSCRIPTION)
    return result == "REMOVED"


def cpr_get_all_subscribed():
    logger.debug("cpr_get_all_subscribed")
    operation = settings.GET_PNR_SUBSCRIPTIONS
    cpr_abonnement_response_envelope = pnr_all_subscribed(
        dependencies_dict=abo_dependencies,
        operation=operation,
    )
    reply = xmltodict.parse(cpr_abonnement_response_envelope)
    operation_response_key = "ns3:{}Response".format(operation)
    x = reply["soap:Envelope"]["soap:Body"][operation_response_key].get(
        "ns2:PNR", [])
    if isinstance(x, list):
        return x
    else:
        return[x]


def cpr_change_subscription(pnr, operation):
    cpr_abonnement_response_envelope = pnr_subscription(
        dependencies_dict=abo_dependencies, pnr=pnr, operation=operation
    )
    reply = xmltodict.parse(cpr_abonnement_response_envelope)
    operation_response_key = "ns3:{}Response".format(operation)
    return reply["soap:Envelope"]["soap:Body"][operation_response_key][
        "ns3:Result"
    ]
