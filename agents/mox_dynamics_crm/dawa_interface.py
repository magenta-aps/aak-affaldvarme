# -*- coding: utf-8 -*-

import re
import json
import requests

from settings import DAWA_SERVICE_URL
from settings import DO_VERIFY_SSL_SIGNATURE


def get_request(service_url=DAWA_SERVICE_URL, uuid=None):
    """GET ADDRESS"""

    # Generate url
    url = "{0}/{1}".format(service_url, uuid)

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


def get_address(uuid):

    data = get_request(uuid=uuid)

    if not data:
        return

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
    koordinat_oest = data['etrs89koordinat_øst']
    koordinat_nord = data['etrs89koordinat_nord']

    """
    On 13 Sep 2017, at 11.40, Akelan Vaithilingam <akva@aarhus.dk> wrote:

    Hej Steffen,
     
    Du skal vende koordinaterne om så du mapper  x til y og omvendt.
    Vi Kører UMT32 koordinatsystem på vores giskort.
     
     
    Mener vi har drøftet dette med Carsten tidligere, måske han ved det?
     
    Med venlig hilsen
     
    Akelan Vaithilingam
    """
    # breddegrad = data['wgs84koordinat_bredde']
    # laengdegrad = data['wgs84koordinat_længde']
    breddegrad = data['wgs84koordinat_længde']
    laengdegrad = data['wgs84koordinat_bredde']

    land = 'Danmark'

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
        'ava_dawa_uuid': adresseid,
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
        'ava_koordinat_nord': str(koordinat_nord),
        'ava_koordinat_oest': str(koordinat_oest),
        'ava_laengdegrad': str(laengdegrad),
        'ava_breddegrad': str(breddegrad)
    }
    return payload

if __name__ == "__main__":
    address = get_address("0a3f50a0-23cc-32b8-e044-0003ba298018")
    print(address)