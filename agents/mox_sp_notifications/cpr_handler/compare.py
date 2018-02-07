# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from helper import create_virkning

from interfaces.dawa_interface import get_request, fuzzy_address_uuid

def create_lora_map(data):
    """
    Helper function to create a simple mapped OIO object

    :param data:
    :return:
    """

    # Mapping (Lora data)
    registreringer = data["registreringer"][0]

    return {
        "attributter": registreringer["attributter"],
        "relationer": registreringer["relationer"],
        "tilstande": registreringer["tilstande"]
    }


def extract_details_from_lora(data):
    """

    :param data:
    :return:
    """

    # Create map
    map = create_lora_map(data)

    attributter = map["attributter"]
    egenskaber = attributter["brugeregenskaber"][0]

    return {
        "ava_fornavn": egenskaber.get("ava_fornavn"),
        "ava_mellemnavn": egenskaber.get("ava_mellemnavn"),
        "ava_efternavn": egenskaber.get("ava_efternavn"),
        "ava_koen": egenskaber.get("ava_koen"),
        "ava_civilstand": egenskaber.get("ava_civilstand"),
        "ava_adressebeskyttelse": egenskaber.get("ava_adressebeskyttelse")
    }


def extract_details_from_sp(data):


    if not data:
        raise Exception("NO SP DATA")

    payload = {
        "ava_fornavn": data.get("fornavn"),
        "ava_mellemnavn": data.get("mellemnavn"),
        "ava_efternavn": data.get("efternavn"),
        "ava_koen": data.get("koen"),
        "ava_civilstand": data.get("civilstand"),
        "ava_adressebeskyttelse": data.get("adressebeskyttelse")
    }

    return payload




def update_details(update_value):

    if not update_value:
        return False

    print(update_value)
    return {
        "type": "update",
        "group": "attributter",
        "subgroup": "brugeregenskaber",
        "update": update_value
    }


def extract_dawa_uuid_from_lora(data):

    # Create map
    map = create_lora_map(data)

    # Traverse through the map
    relationer = map["relationer"]

    if not "adresser" in relationer:
        print("Address does not exist")
        return

    adresser = relationer["adresser"]

    for item in adresser:

        if not "uuid" in item:
            continue

        dawa_uuid = item["uuid"]

        # There are objects with no address
        if not dawa_uuid:
            return False

        return dawa_uuid



def extract_dawa_uuid_from_sp(data):

    vejkode = data.get("vejkode")
    postnummer = data.get("postnummer")
    husnummer = data.get("husnummer")
    etage = data.get("etage")
    sidedoer = data.get("sidedoer")
    standardadresse = data.get("standardadresse")
    postdistrikt = data.get("postdistrikt")

    params = {
        "vejkode": vejkode,
        "husnummer": husnummer,
        "postnummer": postnummer,
        "etage": etage,
        "sidedoer": sidedoer,
        "struktur": "mini"
    }

    fields = [
        "husnummer",
        "etage",
        "sidedoer"
    ]

    for value in fields:
        if not value:
            del params[key]
            continue

        if value.startswith("0"):
            params[key] = value.lstrip("0")

    address_uuid = None

    address = get_request("adresser", **params)

    if not address or len(address) > 1:
        fuzzy_string = "{street}, {zip} {city}".format(
            street=standardadresse,
            zip=postnummer,
            city=postdistrikt
        )

        address_uuid = fuzzy_address_uuid(fuzzy_string)

    else:
        address_uuid = address[0]["id"]

    return address_uuid


def update_address(update_value):

    if not update_value:
        return False

    print(update_value)

    return {
        "type": "update",
        "group": "relationer",
        "subgroup": "adresser",
        "update": {
            "uuid": update_value
        }
    }


COMPARISON = [
    (
        extract_dawa_uuid_from_lora,
        extract_dawa_uuid_from_sp,
        update_address
    ),
    (
        extract_details_from_lora,
        extract_details_from_sp,
        update_details
    )
]