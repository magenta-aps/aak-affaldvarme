# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests

from .sp_adapter import CVRAdapter

# Settings
RUN_IN_PROD_MODE = True
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

    if not zeep_data:
        # No CVR data found
        raise RuntimeError("CVR number {} not found".format(cvr_id))

    extracted = _extract_zeep_data(zeep_data)

    address = {}
    # address["vejnavn"] = extracted["vejnavn"]
    address["vejkode"] = extracted.get("vejkode")
    address["husnr"] = extracted.get("husnummer")
    address["etage"] = extracted.get("etage")
    address["dør"] = extracted.get("doer")
    address['postnr'] = extracted.get("postnummer")

    # get result - there should only be one
    extracted["dawa_uuid"] = _get_address_uuid(address)

    return extracted


def _extract_zeep_data(data):
    """Extract values from zeep object and returns formatted dictionary"""

    # Categories
    organisation_name = (
        data["LegalUnitName"]["name"] if "LegalUnitName" in data else ''
    )
    address = data["AddressOfficial"]
    activity = data["ActivityInformation"]["MainActivity"]
    businessformat = data["BusinessFormat"]
    # Country code not included
    # There may be a need for an identifier for countries outside Denmark
    formatted = {
        "organisationsnavn": organisation_name,
        "branchekode":
            activity["ActivityCode"],
        "branchebeskrivelse":
            activity["ActivityDescription"],
        "virksomhedsform":
            businessformat["BusinessFormatCode"]
    }

    extended = {
        "vejnavn":
            address["AddressPostalExtended"]["StreetName"],
        "husnummer":
            address["AddressPostalExtended"]["StreetBuildingIdentifier"],
        "etage":
            address["AddressPostalExtended"]["FloorIdentifier"],
        "doer":
            address["AddressPostalExtended"]["SuiteIdentifier"],
        "postnummer":
            address["AddressPostalExtended"]["PostCodeIdentifier"],
        "postboks":
            address["AddressPostalExtended"]["PostOfficeBoxIdentifier"]
    } if address["AddressPostalExtended"] else {}

    access = {
        "vejkode":
            address["AddressAccess"]["StreetCode"],
        "kommunekode":
            address["AddressAccess"]["MunicipalityCode"]
    } if address["AddressAccess"] else {}

    formatted = {**formatted, **extended, **access}
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
    address_uuid = None
    if response:
        try:
            address_uuid = response.json()[0]['id']
        except (IndexError, KeyError):
            pass

    return address_uuid
