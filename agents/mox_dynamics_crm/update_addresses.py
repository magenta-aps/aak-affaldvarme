# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from logging import getLogger
import cache_interface as cache
import dawa_interface as dawa


# Init log
log = getLogger(__name__)


def check_for_updates():
    """
    Entry point for the update client.

    Fetch all addresses stored in the cache layer,
    then fetch the equivilant address from DAR and compare them.

    If the value sets are not equal,
    the address is updated accordingly in the cache layer.
    """

    addresses = cache.all("ava_adresses")

    if not addresses:
        raise RuntimeWarning(
            "No addresses found"
        )

    for address in addresses:
        updated_address = compare(address)

        if not updated_address:
            continue

        run_update(updated_address)


def compare(address):
    """
    Fetch the address (by identifier) from DAR,
    and compare the value sets.

    The address fetched from DAR is first converted
    using the dawa_interface adapter.

    :param address:     Address object (Type: dict)
                        Example:

                        {
                            "id": < DAR uuid >
                            "external_ref": < External / CRM uuid >,
                            "data": {
                                "ava_bogstav":  "G" ,
                                "ava_breddegrad":  "567317.16" ,
                                "ava_by":  "Brabrand" ,
                                "ava_dawaadgangsadresseid":  "81ee8714-2893-4b0d-939c-b161b397c3c6" ,
                                "ava_doer": null ,
                                "ava_etage": null ,
                                "ava_gadenavn":  "Silkeborgvej" ,
                                "ava_husnummer":  "710" ,
                                "ava_kommunenummer":  "0751" ,
                                "ava_koordinat_nord":  "56.15320025" ,
                                "ava_koordinat_oest":  "10.08367247" ,
                                "ava_kvhx":  "07517166710G_______" ,
                                "ava_laengdegrad":  "6223659.32" ,
                                "ava_land":  "Danmark" ,
                                "ava_name":  "Silkeborgvej 710G, 8220 Brabrand" ,
                                "ava_postnummer":  "8220" ,
                                "ava_vejkode":  "7166"
                                }
                        }

    :return:            Returns the converted DAR address object.
                        (The format is identical than the above example)
    """

    if not address:
        return None

    identifier = address.get("id")
    address_data = address.get("data")

    # Info
    log.info(
        "Checking for updates: {id}".format(
            id=identifier
        )
    )

    try:
        dawa_address = dawa.get_address(identifier)

    except(ValueError) as error:
        # Log error
        log.error(error)
        return

    if not dawa_address:
        log.error(
            "Nothing returned from DAR"
        )
        return

    # Address data set
    dawa_address_data = dawa_address.get("data")

    # Compare DAR address data against cached data
    if address_data == dawa_address_data:
        return False

    # Info
    log.info(
        "Update found for address id: {id}".format(
            id=identifier
        )
    )
    return dawa_address


def run_update(address):
    """
    Wrapper function to call the cache.update function.

    :param address:     Address object (Type: dict)

    :return:            Nothing is returned.
    """

    # Get ID
    cache_id = address.get("id")

    # Info
    log.info(
        "Updating cached address: {id}".format(
            id=cache_id
        )
    )

    update = cache.update(
        table="ava_adresses",
        document=address
    )

    # Infor
    log.info(update)


if __name__ == '__main__':
    from logger import start_logging

    # Init log
    start_logging()

    # Run
    check_for_updates()