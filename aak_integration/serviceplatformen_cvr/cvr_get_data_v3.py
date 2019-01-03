""" get_cvr_data as used in aak-integration
depending on the https://github.com/magenta-aps/cvronline-get-legal-unit/tree/development

"""
#
# Copyright (c) 2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests
import logging

from cvronline_get_legal_unit import get_legal_unit

logger = logging.getLogger("cvr")

DAWA_SERVICE_URL = 'https://dawa.aws.dk/adresser'
DAWA_DATAVASK_URL = 'https://dawa.aws.dk/datavask/adresser'
logger = logging.getLogger("cvr")


def processor_v2(data):
    import pdb; pdb.set_trace()
    """Extract values from data and returns formatted dictionary"""

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
            address["AddressPostalExtended"].get("StreetName", ''),
        "husnummer":
            address["AddressPostalExtended"].get("StreetBuildingIdentifier", ''),
        "etage":
            address["AddressPostalExtended"].get("FloorIdentifier", ''),
        "doer":
            address["AddressPostalExtended"].get("SuiteIdentifier", ''),
        "postnummer":
            address["AddressPostalExtended"].get("PostCodeIdentifier", ''),
        "postboks":
            address["AddressPostalExtended"].get("PostOfficeBoxIdentifier", '')
    } if address.get("AddressPostalExtended", '') else {}

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

    address = {
        "vejnavn": formatted.get("vejnavn"),
        "vejkode": formatted.get("vejkode"),
        "husnr": formatted.get("husnummer"),
        "etage": formatted.get("etage"),
        "dør": formatted.get("doer"),
        'postnr': formatted.get("postnummer"),
    }
    formatted["dawa_uuid"] = _get_address_uuid(address)
    # Return the data
    return formatted

def _get_address_uuid(address):

    # try normal lookup - will catch most
    params = dict(address)
    params['struktur'] = "mini"
    params.pop("vejnavn")

    response = requests.get(
        url=DAWA_SERVICE_URL,
        params=params
    )
    if response:
        try:
            return response.json()[0]['id']
        except (IndexError, KeyError):
            pass

    # datavask lookup - should catch the rest
    response = requests.get(
        url=DAWA_DATAVASK_URL,
        params={
            "betegnelse":"%(vejnavn)s %(husnr)s %(etage)s %(dør)s, %(postnr)s" % address
        }
    )
    if response:
        try:
            if len(response.json()["resultater"]) != 1:
                return None
            return response.json()["resultater"][0]['adresse']['id']
        except (IndexError, KeyError):
            return None

def processor_v3(certificate, **kwargs):
    pass

_services = {
    "93a48b42-3945-11e2-9724-d4bed98c63db": {
        "processor": processor_v2,
    },
    "c0daecde-e278-43b7-84fd-477bfeeea027": {
        "processor": processor_v3,
    }
}


def get_cvr_data(certificate, **kwargs):
    _service = _services[kwargs["service"]]
    try:
        data = get_legal_unit(certificate, **kwargs)
        processed = _service["processor"](data)
    except Exception as e:
        logger.exception(e)
        return None
    return processed

if __name__ == '__main__':
    import configparser, pprint
    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config["sp_cvr"]
    result = get_cvr_data(**config, cvrnumber="25052943")
    pprint.pprint(result)
