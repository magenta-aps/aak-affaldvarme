# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from logging import getLogger
from helper import get_config
from service_person_stamdata_udvidet import get_citizen
from cpr_handler import compare


# Init log
log = getLogger(__name__)

# List of comparisons to perform.
COMPARISONS = [
    (
        compare.extract_address_uuid_from_oio,
        compare.extract_address_uuid_from_sp,
        compare.update_address
    ),
    (
        compare.extract_details_from_oio,
        compare.extract_details_from_sp,
        compare.update_details
    )
]


def cpr_handler(bruger_data):
    """
    Handler for comparing CPR and SP data sets.
    The handler extracts the CPR ID value and retrieves
    the matching SP data set.

    The two data sets are compared,
    using the compare functions from the list above.

    COMPARISON:
    Each item contains two adapter type functions
    which will return a specified value/set from both the OIO and SP data set.
    Lastly a function to generate an update if the value/sets are not equal.

    Example on generated update object:

        (section: relationer, key: adresser)

        {
            "uuid": "8B0DA89B-B1DE-436D-9500-D96FCA2A5868"
        }

    For more information on update objects,
    please see the compare module.

    :param bruger_data:     OIO (Bruger) data set

    :return:                Returns a list of updates.
                            One data set can have several sections which
    """

    # Map
    uuid = bruger_data["id"]
    cpr_id = extract_cpr_id(bruger_data)

    # Info
    log.info(
        "Processing bruger: {0}".format(uuid)
    )

    # Service platform data
    sp_data = get_cpr_data(cpr_id)

    # List of updates found
    list_of_updates = []

    # Run all the comparisons from the specified list
    for extract_lora_data, extract_sp_data, create_update in COMPARISONS:
        lora_value = extract_lora_data(bruger_data)
        sp_value = extract_sp_data(sp_data)

        if not lora_value == sp_value:
            update = create_update(sp_value)
            list_of_updates.append(update)

    # Confirm in the log
    # that no updates were found
    if not list_of_updates:
        log.info("Nothing to update")
        return

    return list_of_updates


def extract_cpr_id(data):
    """
    Helper function to extract CPR ID value
    from the OIO data object.

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


def get_cpr_data(cpr_id):
    """
    Helper function to retrieve SP data set
    by CPR ID value.

    :param cpr_id:  The 10-digit CPR ID value,
                    without the "-" seperator.

                    e.g.
                        121212334 (121212-3344)

    :return:        Returns SP data set
    """

    config = get_config("sp_cpr")

    uuids = {
        "service_agreement": config["service_agreement"],
        "user_system": config["user_system"],
        "user": config["user"],
        "service": config["service"]
    }

    certificate = config["certificate"]

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cpr_id
    )

    return result
