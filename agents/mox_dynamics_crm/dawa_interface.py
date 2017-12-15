# -*- coding: utf-8 -*-

import re
import json
import requests

from settings import DO_VERIFY_SSL_SIGNATURE


# DAR Service settings
BASE_URL = "https://dawa.aws.dk"


def get_request(resource, uuid):
    """GET ADDRESS"""

    # Generate url
    url = "{base}/{resource}/{uuid}".format(
        base=BASE_URL,
        resource=resource,
        uuid=uuid
    )

    # Params
    params = {
        "struktur": "flad"
    }

    # TODO: Verify SSL signature must dynamically be set
    response = requests.get(
        url=url,
        params=params,
        verify=DO_VERIFY_SSL_SIGNATURE
    )

    if response.status_code != 200:
        return False

    return response.json()


def get_access_address(uuid):

    resource = "adgangsadresser"

    data = get_request(
        resource=resource,
        uuid=uuid
    )

    if not data:
        return

    adresseid = data['id']
    vejkode = data['vejkode']
    vejnavn = data['vejnavn']
    husnr = data['husnr']
    postnr = data['postnr']
    postnrnavn = data['postnrnavn']
    kommunekode = data['kommunekode']

    koordinat_nord = data['wgs84koordinat_bredde']
    koordinat_oest = data['wgs84koordinat_længde']

    laengdegrad = data['etrs89koordinat_nord']
    breddegrad = data['etrs89koordinat_øst']

    land = 'Danmark'

    husnr_nr = re.findall('\d+', husnr)[0]
    husnr_bogstav = re.findall('\D+', husnr)

    if husnr_bogstav:
        husnr_bogstav = husnr_bogstav[0]
    else:
        husnr_bogstav = None

    # Create address search string by combining all relevant values
    search = '{} {}'.format(vejnavn, husnr)

    search += ', {} {}'.format(postnr, postnrnavn)

    # Add "adgangsadresser" to the search string"
    # To distinguish between actual addresses and access addresses
    search += ', adgangsadresse'

    # AVA specific payload
    payload = {
        # Hotfix:
        # Adding redundant origin id
        'origin_id': adresseid,

        # Original payload
        'ava_dawa_uuid': adresseid,
        'ava_name': search,
        'ava_gadenavn': vejnavn,
        'ava_husnummer': husnr_nr,
        'ava_bogstav': husnr_bogstav,
        'ava_postnummer': postnr,
        'ava_kommunenummer': kommunekode,
        'ava_by': postnrnavn,
        'ava_land': land,
        'ava_koordinat_nord': str(koordinat_nord),
        'ava_koordinat_oest': str(koordinat_oest),
        'ava_laengdegrad': str(laengdegrad),
        'ava_breddegrad': str(breddegrad)
    }
    return payload


# IMPORT ALL ADDRESSES
# TODO: Implement adapter for every function
def adapter(data):

    if not data:
        return False

    adresseid = data['id']
    vejkode = data['vejkode']
    vejnavn = data['vejnavn']
    husnr = data['husnr']
    etage = data['etage']
    doer = data['dør']
    postnr = data['postnr']
    postnrnavn = data['postnrnavn']
    kommunekode = data['kommunekode']
    adgangsadresseid = data['adgangsadresseid']
    kvhx = data['kvhx']

    # Coordinates
    koordinat_nord = data['wgs84koordinat_bredde']
    koordinat_oest = data['wgs84koordinat_længde']

    laengdegrad = data['etrs89koordinat_nord']
    breddegrad = data['etrs89koordinat_øst']

    # Todo:
    # Country is currently hardcoded
    # This may have to be dynamically set
    land = 'Danmark'

    # Split building id (numbers and letters)
    husnr_nr = re.findall('\d+', husnr)[0]
    husnr_bogstav = re.findall('\D+', husnr)

    if husnr_bogstav:
        husnr_bogstav = husnr_bogstav[0]
    else:
        husnr_bogstav = None

    # Create address search string by combining all relevant values
    search = '{} {}'.format(vejnavn, husnr)

    if etage:
        search += ', {}.'.format(etage)

    if doer:
        search += ' {}'.format(doer)

    search += ', {} {}'.format(postnr, postnrnavn)

    # AVA specific payload
    payload = {
        "_id": adresseid,
        "external_ref": None,
        "data": {
            'ava_dawaadgangsadresseid': adgangsadresseid,
            'ava_name': search,
            'ava_gadenavn': vejnavn,
            'ava_husnummer': husnr_nr,
            'ava_bogstav': husnr_bogstav,
            'ava_etage': etage,
            'ava_doer': doer,
            'ava_postnummer': postnr,
            'ava_kommunenummer': kommunekode,
            'ava_by': postnrnavn,
            'ava_land': land,
            'ava_kvhx': kvhx,
            "ava_vejkode": vejkode,
            'ava_koordinat_nord': str(koordinat_nord),
            'ava_koordinat_oest': str(koordinat_oest),
            'ava_laengdegrad': str(laengdegrad),
            'ava_breddegrad': str(breddegrad)
        }
    }
    return payload


def get_address(uuid):

    resource = "adresser"

    data = get_request(
        resource=resource,
        uuid=uuid
    )

    if not data:
        return False

    return adapter(data)


def get_all(area_code):
    """GET ADDRESS"""

    resource = "adresser"

    # Generate url
    url = "{base}/{resource}".format(
        base=BASE_URL,
        resource=resource
    )

    # Params
    params = {
        "kommunekode": area_code,
        "struktur": "flad"
    }

    # TODO: Verify SSL signature must dynamically be set
    response = requests.get(
        url=url,
        params=params,
        verify=DO_VERIFY_SSL_SIGNATURE
    )

    if response.status_code != 200:
        return False

    # Create empty payload:
    payload = []

    for address in response.json():
        converted = adapter(address)
        payload.append(converted)

    return payload

if __name__ == "__main__":
    address = get_access_address("0a3f5096-68f7-32b8-e044-0003ba298018")
    print(address)
