# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import logging
import requests

from .sp_adapter import CVRAdapter

# Settings
RUN_IN_PROD_MODE = False
DAWA_SERVICE_URL = 'https://dawa.aws.dk/adresser'


def get_cvr_data(cvr_id, service_uuids, service_certificate):
    """
    Run client
    TODO: Description missing
    """

    # Retrieve UUIDS from settings and run CVRAdapter
    cvr_adapter = CVRAdapter(
        service_uuids,
        service_certificate,
        prod_mode=RUN_IN_PROD_MODE
    )

    zeep_data = cvr_adapter.getLegalUnit(cvr_id)
    extracted = _extract_zeep_data(zeep_data)

    address = {}
    address["vejnavn"] = extracted["vejnavn"]
    address["husnr"] = extracted["husnummer"]
    address["etage"] = extracted["etage"]
    address["dør"] = extracted["doer"]
    address['postnr'] = extracted["postnummer"]

    extracted["dawa_uuid"] = _get_address_uuid(address)

    return extracted


def _extract_zeep_data(data):
    """Extract values from zeep object and returns formatted dictionary"""

    # Categories
    organisation = data["LegalUnitName"]
    lifecycle = data["Lifecycle"]
    address = data["AddressOfficial"]
    activity = data["ActivityInformation"]["MainActivity"]
    businessformat = data["BusinessFormat"]

    # Country code not included
    # There may be a need for an identifier for countries outside Denmark
    formatted = {
        "organisationsnavn": organisation["name"],
        "vejnavn":
            address["AddressPostalExtended"]["StreetName"],
        "vejkode":
            address["AddressAccess"]["StreetCode"],
        "husnummer":
            address["AddressPostalExtended"]["StreetBuildingIdentifier"],
        "etage":
            address["AddressPostalExtended"]["FloorIdentifier"],
        "doer":
            address["AddressPostalExtended"]["SuiteIdentifier"],
        "postnummer":
            address["AddressPostalExtended"]["PostCodeIdentifier"],
        "kommunekode":
            address["AddressAccess"]["MunicipalityCode"],
        "postboks":
            address["AddressPostalExtended"]["PostOfficeBoxIdentifier"],
        "branchekode":
            activity["ActivityCode"],
        "branchebeskrivelse":
            activity["ActivityDescription"],
        "virksomhedsform":
            businessformat["BusinessFormatCode"]
    }

    # Some parameter values are None and must be replaced with an empty string
    for key, value in formatted.items():
        if value is None:
            formatted[key] = ""

    # Return the data
    return formatted


def _get_address_uuid(address):

    params = address
    params['struktur'] = "mini"

    response = requests.get(
        url=DAWA_SERVICE_URL,
        params=params
    )

    address_uuid = response.json()[0]['id']
    return address_uuid
