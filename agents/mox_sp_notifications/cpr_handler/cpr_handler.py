# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from helper import get_config
from udvidet_person_stamdata import get_citizen
from cpr_handler.compare import COMPARISON

config = get_config("sp_cpr")

uuids = {
    "service_agreement": config["service_agreement"],
    "user_system": config["user_system"],
    "user": config["user"],
    "service": config["service"]
}

certificate = config["certificate"]


def cpr_handler(object):
    """
    CPR Handler

    :param object:
    :return:
    """

    # Lora data
    bruger_data = object[0]
    uuid = bruger_data["id"]
    cpr_id = extract_cpr_id(bruger_data)

    # Info
    print(
        "Processing bruger: {0}".format(uuid)
    )

    # Service platform data
    sp_data = get_cpr_data(cpr_id)


    updates = []

    # This will contain objects to update
    for extract_lora_data, extract_sp_data, create_update in COMPARISON:
        lora_value = extract_lora_data(bruger_data)
        sp_value = extract_sp_data(sp_data)

        if not lora_value == sp_value:
            update = create_update(sp_value)
            updates.append(update)


    if not updates:
        print("Nothing to update")
        return

    return updates


def extract_cpr_id(data):
    """
    Person/CPR specific helper function
    to extract CPR ID value from OIO REST object.

    :param data:    OIO REST data object (Lora)

    :return:        Returns 10-digit CPR ID value or None
    """

    # Mapping
    registreringer = data["registreringer"][0]
    relationer = registreringer["relationer"]
    tilknyttedepersoner = relationer["tilknyttedepersoner"][0]
    cpr_id = tilknyttedepersoner["urn"].split(":")[-1]

    if not cpr_id:
        return False

    return cpr_id


def get_cpr_data(cprnr):

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr
    )

    return result





