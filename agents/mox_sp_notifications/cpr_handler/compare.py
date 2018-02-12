# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from logging import getLogger
from helper import create_virkning
from interfaces.dawa_interface import get_request
from interfaces.dawa_interface import fuzzy_address_uuid


# Init log
log = getLogger(__name__)


def create_object_map(oio_data):
    """
    Helper function to create a simple mapped OIO object.
    The function splits the data object into its primary sections.

    OIO data arrives as a list.
    There should be only 1 "registrering",
    as such we map only the 1st object of the list.

    :param oio_data:    OIO data object (list)

    :return:            Returns mapped oio object
    """

    # Map sections of OIO object
    registrering = oio_data["registreringer"][0]

    return {
        "attributter": registrering["attributter"],
        "relationer": registrering["relationer"],
        "tilstande": registrering["tilstande"]
    }


def extract_details_from_oio(oio_data):
    """
    Helper function to extract a set of details ("brugeregenskaber")
    from the OIO data set.

    The reason we are not returning the entire set is that only
    a fraction of the set can be compared with values from SP.

    :param oio_data:    OIO data object (list)

    :return:            Returns dictionary containing
                        SP verifiable set of values
    """

    # Create map
    map = create_object_map(oio_data)

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


def extract_details_from_sp(spa_data):
    """
    Helper function to extract a set of person details
    containing a set of values which can be compared with
    a selection of OIO data values.

    :param spa_data:    SP data object

    :return:            Returns dictionary containing
                        a selection of values to compare with OIO.
    """

    # Sanity check
    if not spa_data:
        raise RuntimeError("No SP data provided")

    return {
        "ava_fornavn": spa_data.get("fornavn"),
        "ava_mellemnavn": spa_data.get("mellemnavn"),
        "ava_efternavn": spa_data.get("efternavn"),
        "ava_koen": spa_data.get("koen"),
        "ava_civilstand": spa_data.get("civilstand"),
        "ava_adressebeskyttelse": spa_data.get("adressebeskyttelse")
    }


def update_details(update_value):
    """
    Generate an update object with the updated value(s) from SP.

    Example:

    {
        "section": "attributter",
        "key": "brugeregenskaber",
        "update": {
        "ava_efternavn": "LAST NAME",
        "ava_fornavn": "FIRST NAME",
        "ava_koen": "K",
        "virkning": {  <-- Genererated
            "from": "2017-12-04 11:09:10.912111+01",
            "to": "infinity"
        }
    }

    :param update_value:    Updated value set (from SP),
                            the actual updated set
                            from the example above is:

                            {
                                "ava_efternavn": "LAST NAME",
                                "ava_fornavn": "FIRST NAME",
                                "ava_koen": "K"
                            }

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    if not update_value:
        return False

    # Create "virkning"
    virkning = {
        "virkning": create_virkning()
    }

    # Update dictionary with "virkning"
    update_value.update(virkning)

    return {
        "section": "attributter",
        "key": "brugeregenskaber",
        "update": update_value
    }


def extract_address_uuid_from_oio(oio_data):
    """
    Helper function to extract a set of person details
    containing a set of values which can be compared with
    a selection of OIO data values.

    :param spa_data:    SP data object

    :return:            Returns dictionary containing
                            a selection of values to compare with OIO.
    """

    # Map
    map = create_object_map(oio_data)
    relationer = map["relationer"]

    if "adresser" not in relationer:
        # Warning should be enough
        log.warning("Address section does not exists in oio object")
        return

    # List of address objects
    # NOTE: this may also contain phone numbers/email addresses
    adresser = relationer["adresser"]

    # Fallback
    address_uuid = None

    # Iterate over the address list
    # Target object that contains the key "uuid"
    # (Only residence addresses will contain "uuid")
    # Other address objects will contain "urn" key
    for item in adresser:

        if "uuid" not in item:
            continue

        # Set value
        address_uuid = item["uuid"]

    # There are objects
    # which carry no residence address
    if not address_uuid:
        log.warning(
            "No address reference found in OIO object"
        )
        return False

    return address_uuid


def extract_address_uuid_from_sp(sp_data):
    """
    Helper function to extract the address uuid from DAR/DAWA.

    Building a set of query parameters with values such as:
        - street code
        - building id/number
        - floor id
        - door id
        - zip code
        - city

    The provided address data may not contain values for all parameters,
    for example not every address will contain a floor/door id.

    To accomodate for this, empty parameter keys are filtered/deleted.
    Additionally, some identifiers have left padding (zerofilled),
    these are stripped as well.

    If no definitive address is returned,
    a fuzzy search is performed using the entire address as a string.

    (As defined in the "standardadresse" from the SP data set)

    For more information, please see the dawa_interface module.

    :param sp_data:     SP data object

    :return:            Returns address identifier (Type: uuid)

                        Example:
                        04448F85-4FEA-430F-A386-C65DE21F8F2F
    """

    # Map
    vejkode = sp_data.get("vejkode")
    postnummer = sp_data.get("postnummer")
    husnummer = sp_data.get("husnummer")
    etage = sp_data.get("etage")
    sidedoer = sp_data.get("sidedoer")
    standardadresse = sp_data.get("standardadresse")
    postdistrikt = sp_data.get("postdistrikt")

    # Query parameters
    params = {
        "vejkode": vejkode,
        "husnummer": husnummer,
        "postnummer": postnummer,
        "etage": etage,
        "sidedoer": sidedoer,
        "struktur": "mini"
    }

    # Filter
    filtered_params = dict()

    # Remove empty pairs
    for key, value in params.items():
        if not value:
            continue

        if value.startswith("0"):
            value = value.lstrip("0")

        filtered_params.update({key: value})

    # Build HTTP request
    address = get_request("adresser", **filtered_params)

    if not address:
        log.warning(
            "No address returned from DAR/DAWA"
        )
        return False

    # We expect only 1 address returned
    if len(address) == 1:
        # Set value
        address_uuid = address[0]["id"]

    else:
        # Create search string
        fuzzy_string = "{street}, {zip} {city}".format(
            street=standardadresse,
            zip=postnummer,
            city=postdistrikt
        )

        # Info
        log.info(
            "Address not found, performing fuzzy search: {string}".format(
                string=fuzzy_string
            )
        )

        address_uuid = fuzzy_address_uuid(fuzzy_string)

    if not address_uuid:
        log.warning(
            "Unable to retrieve definitive DAR/DAWA reference"
        )
        # Include params
        log.debug(filtered_params)
        return False

    return address_uuid


def update_address(update_value):
    """
    Generate an update object with the updated address reference.

    Example:

    {
        "section": "relationer",
        "key": "adresser",
        "update": {
            "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F"
        }
    }

    :param update_value:    Updated address reference (SP/DAR)
                            the actual updated set
                            from the example above is:

                            {
                                "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F"
                            }

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    if not update_value:
        return False

    update = {
        "uuid": update_value,
        "virkning": create_virkning()
    }

    return {
        "section": "relationer",
        "key": "adresser",
        "update": update
    }
