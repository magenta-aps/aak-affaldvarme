# -*- coding: utf-8 -*-

import re
import requests
from logging import getLogger
import cache_interface as cache

# DAR Service settings
BASE_URL = "https://dawa.aws.dk"

# Init logging
log = getLogger(__name__)


def get_request(resource, **params):
    """
    Parent GET request primarily used by wrapper functions

    :param resource:    REST API resource path (e.g. /adresser/<uuid>)
    :param uuid:        Address object identifier (Type: uuid)
    :param params:      Query parameters, by default 'flad'
                        which provides a flattened object structure

    :return:            Returns address object
    """

    # Generate url
    url = "{base_url}/{resource_path}".format(
        base_url=BASE_URL,
        resource_path=resource
    )

    # INFO
    log.info(
        "GET request: {url} (Params: {params})".format(
            url=url,
            params=params
        )
    )

    response = requests.get(
        url=url,
        params=params
    )

    if not response.status_code == 200:
        # Log error
        log.error(response.text)

        return False

    return response.json()


def get_access_address(uuid):
    """
    Helper function for retrieving access addresses.
    Buildings with multiple sections/appartments
    usually have limited entry points.

    Access address points towards such an entry point.
    For more information, see service documentation (http://dawa.aws.dk)

    :param uuid:    Address object identifier

    :return:        Returns access_adapter (document)
    """

    resource = "adgangsadresser/{identifier}".format(
        identifier=uuid
    )

    data = get_request(
        resource=resource,
        struktur="flad"
    )

    if not data:
        return False

    return access_adapter(data)


def access_adapter(data):
    # no old_adapted here, as these do not seem to be imported
    # thus an already cached external_ref is not overwritten
    """
    Adapter to convert an access address object to cache layer document.
    The document contains both transport meta data and the original content.

    :param data:    Accepts DAR address (REST) object

    :return:        Cache document containing meta data and CRM data object.
                    Example:
                    {
                        "id": <DAR reference (uuid)>,
                        "external_ref": <CRM reference (guid)>,
                        "data": <CRM data object>
                    }
    """

    adresseid = data["id"]
    vejkode = data["vejkode"]
    vejnavn = data["vejnavn"]
    husnr = data["husnr"]
    postnr = data["postnr"]
    postnrnavn = data["postnrnavn"]
    kommunekode = data["kommunekode"]

    koordinat_nord = data["wgs84koordinat_bredde"]
    koordinat_oest = data["wgs84koordinat_længde"]

    laengdegrad = data["etrs89koordinat_nord"]
    breddegrad = data["etrs89koordinat_øst"]

    land = "Danmark"

    husnr_nr = re.findall("\d+", husnr)[0]
    husnr_bogstav = re.findall("\D+", husnr)

    if husnr_bogstav:
        husnr_bogstav = husnr_bogstav[0]
    else:
        husnr_bogstav = None

    # Create address search string by combining all relevant values
    search = "{} {}".format(vejnavn, husnr)

    search += ", {} {}".format(postnr, postnrnavn)

    # Add "adgangsadresser" to the search string"
    # To distinguish between actual addresses and access addresses
    search += ", adgangsadresse"

    # Cache layer compliant document
    document = {
        "id": adresseid,
        "external_ref": None,
        "data": {
            "ava_name": search,
            "ava_gadenavn": vejnavn,
            "ava_husnummer": husnr_nr,
            "ava_bogstav": husnr_bogstav,
            "ava_postnummer": postnr,
            "ava_vejkode": vejkode,
            "ava_kommunenummer": kommunekode,
            "ava_by": postnrnavn,
            "ava_land": land,
            "ava_koordinat_nord": str(koordinat_nord),
            "ava_koordinat_oest": str(koordinat_oest),
            "ava_laengdegrad": str(laengdegrad),
            "ava_breddegrad": str(breddegrad)
        }
    }
    return document


def get_address(uuid):
    """
    Helper function for retrieving addresses.

    :param uuid:    Address object identifier

    :return:        Returns adapter (document)
    """

    resource = "adresser/{identifier}".format(
        identifier=uuid
    )

    data = get_request(
        resource=resource,
        struktur="flad"
    )

    if not data:
        return False

    return adapter(data)


def adapter(data, old_adapted={}):
    # old_adapted is defaulted because the call can also stem from
    # export_client, but this happens only when address is not cached
    # and in that case the document would be empty anyway
    """
    Adapter to convert an address object to cache layer document.
    The document contains both transport meta data and the original content.

    :param data:    Accepts DAR address (REST) object

    :return:        Cache document containing meta data and CRM data object.
                    Example:
                    {
                        "id": <DAR reference (uuid)>,
                        "external_ref": <CRM reference (guid)>,
                        "data": <CRM data object>
                    }
    """

    adresseid = data["id"]
    vejkode = data["vejkode"]
    vejnavn = data["vejnavn"]
    husnr = data["husnr"]
    etage = data["etage"]
    doer = data["dør"]
    postnr = data["postnr"]
    postnrnavn = data["postnrnavn"]
    kommunekode = data["kommunekode"]
    adgangsadresseid = data["adgangsadresseid"]
    kvhx = data["kvhx"]

    # Coordinates
    koordinat_nord = data["wgs84koordinat_bredde"]
    koordinat_oest = data["wgs84koordinat_længde"]

    laengdegrad = data["etrs89koordinat_nord"]
    breddegrad = data["etrs89koordinat_øst"]

    # Todo:
    # Country is currently hardcoded
    # This may have to be dynamically set
    land = "Danmark"

    # Split building id (numbers and letters)
    husnr_nr = re.findall("\d+", husnr)[0]
    husnr_bogstav = re.findall("\D+", husnr)

    if husnr_bogstav:
        husnr_bogstav = husnr_bogstav[0]
    else:
        husnr_bogstav = None

    # Create address search string by combining all relevant values
    search = "{} {}".format(vejnavn, husnr)

    if etage:
        search += ", {}.".format(etage)

    if doer:
        search += " {}".format(doer)

    search += ", {} {}".format(postnr, postnrnavn)

    # Cache layer compliant document
    document = {
        "id": adresseid,
        "external_ref": old_adapted.get("external_ref"),
        "data": {
            "ava_dawaadgangsadresseid": adgangsadresseid,
            "ava_name": search,
            "ava_gadenavn": vejnavn,
            "ava_husnummer": husnr_nr,
            "ava_bogstav": husnr_bogstav,
            "ava_etage": etage,
            "ava_doer": doer,
            "ava_postnummer": postnr,
            "ava_kommunenummer": kommunekode,
            "ava_by": postnrnavn,
            "ava_land": land,
            "ava_kvhx": kvhx,
            "ava_vejkode": vejkode,
            "ava_koordinat_nord": str(koordinat_nord),
            "ava_koordinat_oest": str(koordinat_oest),
            "ava_laengdegrad": str(laengdegrad),
            "ava_breddegrad": str(breddegrad)
        }
    }
    return document


def get_all(area_code):
    """
    Helper function for retrieving all addresses within an area code.

    :param area_code:   4 digit area code identifier

    :return:            Returns list of converted documents
    """

    resource = "adresser"
    table = cache.mapping.get("dawa")

    addresses = get_request(
        resource=resource,
        kommunekode=area_code,
        struktur="flad"
    )

    if not addresses:
        return

    # cache all previous addresses in memory dict
    existing_adapted = {
        d["id"]: d
        for d in cache.r.table(
            table
            ).get_all(*[a["id"] for a in addresses]).run(cache.connect())
    }

    # Create empty payload:
    list_of_documents = []

    batch_timestamp = cache.r.now()

    # Iterate and append converted documents to the list
    for address in addresses:
        converted = adapter(address, existing_adapted.get(address["id"], {}))
        old_data = existing_adapted.get(address["id"], {}).get("data")
        if converted["data"] != old_data:
            # change this back after export
            converted["import_changed"] = True

        # set update time
        converted["updated"] = batch_timestamp

        list_of_documents.append(converted)

    return list_of_documents
