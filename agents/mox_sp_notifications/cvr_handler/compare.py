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


def extract_address_uuid_from_oio(org_data):
    """
    Extract address uuid (DAR/DAWA) from OIO data object.

    Object structure:
    {
        "relationer": {
            "adresser": [
                {
                    <address object1>
                },
                {
                    <address object2>
                }
            ]
        }
    }

    Address objects can contain either:
     - phone number
     - email address
     - residence address

    ONLY residence (location) address is defined in an "uuid" field.

    As such we must filter the address objects
    which do not contain a "uuid" value.

    :param org_data:    OIO data object

    :return:            Returns address identifier (Type: uuid)

                        Example:
                        04448F85-4FEA-430F-A386-C65DE21F8F2F
    """

    # Map
    map = create_object_map(org_data)
    relationer = map.get("relationer")
    adresser = relationer.get("adresser")
    if not adresser:
        return None

    # Filter
    dawa_addresses = [x for x in adresser if
                      "uuid" in x]

    # We expect there only to be one dawa address active
    if len(dawa_addresses) != 1:
        log.error(
            "Only 1 active (DAR/DAWA) address expected"
        )

        # Include list
        log.error(dawa_addresses)
        return

    # Extract address uuid
    address = dawa_addresses[0]
    address_uuid = address["uuid"]

    return address_uuid


def extract_address_uuid_from_sp(sp_data):
    """
    Extract address (DAR/DAWA) identifier from the SP data object.

    Luckily, the object returned by the SP_CVR module is flat,
    it is as easy as returning the key "dawa_uuid".

    :param sp_data:     SP data object

    :return:            Returns address identifier (Type: uuid)

                        Example:
                        04448F85-4FEA-430F-A386-C65DE21F8F2F
    """

    # Fetch reference
    address_reference = sp_data.get("dawa_uuid")

    if not address_reference:
        log.warning(
            "Unable to extract address from SP object")

        # Include
        log.error(sp_data)
        return False

    return str(address_reference)


def update_address_uuid(update_value):
    """
    Generate an update object
    with the updated address reference.

    Example:

    {
        "section": "relationer",
        "key": "adresser",
        "update": {
            "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F",
            "virkning: {
                "from": "2018-02-12 00:00:00+01",
                "to": "infinity"
            }
        }
    }

    :param update_value:    Updated address reference (SP/DAR)
                            the actual updated set
                            from the example above is:

                            {
                                "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F",
                                "virkning: {
                                    "from": "2018-02-12 00:00:00+01",
                                    "to": "infinity"
                                }
                            }

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    # Build update
    update = {
        "uuid": update_value,
        "virkning": create_virkning()
    }

    return {
        "section": "relationer",
        "key": "adresser",
        "update": update
    }


def extract_org_name_from_oio(org_data):
    """
    Extract name of an organisation from an OIO data object.

    Object structure:
    {
        "attributter": {
            "organisationegenskaber": [
                {
                    ...
                    "organisationsnavn": <string value>
                }
        }
    }

    :param org_data:    OIO data object

    :return:            Returns name of an organisation (Type: string)

                        Example:
                        "Magenta Aps - Open Source Software"

    """

    # Map
    map = create_object_map(org_data)
    attributter = map["attributter"]
    org_details_list = attributter["organisationegenskaber"]

    # Filter
    org_details = [x for x in org_details_list if "organisationsnavn" in x]

    # We expect there only to be one active organisationsnavn
    if len(org_details) != 1:
        log.error(
            "We expect one active organisationsnavn per object")

        # Include
        log.error(org_details)
        return

    details = org_details[0]
    org_name = details["organisationsnavn"]

    return org_name


def extract_org_name_from_sp(sp_data):
    """
    Extract name of an organisation from a SP data object.

    As previously described,
    the object returned by the SP_CVR module is flat.

    :param sp_data:     SP data object

    :return:            Returns name of an organisation (Type: string)

                        Example:
                        "Magenta Aps - Open Source Software"
    """

    # Extract name from SP object
    org_name = sp_data.get("organisationsnavn")

    return str(org_name)


def update_org_name(update_value):
    """
    Generate an update object
    with the updated organisation name.

    Example:

    {
        "section": "attributter",
        "key": "organisationegenskaber",
        "update": {
            "organisationsnavn": "Magenta Aps - Open Source Software",
            "virkning: {
                "from": "2018-02-12 00:00:00+01",
                "to": "infinity"
            }
        }
    }

    :param update_value:    Name of an organisation as a string value,
                            example:
                            "Magenta Aps - Open Source Software"

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    # Build update
    update = {
        "organisationsnavn": update_value,
        "virkning": create_virkning()
    }

    return {
        "section": "attributter",
        "key": "organisationegenskaber",
        "update": update
    }


def extract_business_code_from_oio(org_data):
    """
    Extract business code from an OIO data object.

    Object structure:
    {
        "relationer": {
            "branche": [
                {
                    "urn": "urn:<branch id>"
                }
        }
    }

    :param org_data:    OIO data object

    :return:            Returns 6-digit business code (Type: string)
                        Example: "112233"
    """

    # Map
    map = create_object_map(org_data)
    relationer = map["relationer"]
    businesses_list = relationer["branche"]

    # We expect there only to be one active branche
    if not businesses_list or len(businesses_list) != 1:
        log.error(
            "We expect one active businesses type object"
        )

        # Include
        log.error(businesses_list)

    # Extract org type id (branchekode)
    branche = businesses_list[0]
    split_urn = branche['urn'].split(':')
    org_type_id = split_urn[-1]

    return org_type_id


def extract_business_code_from_sp(sp_data):
    """
    Extract business code from a SP data object.

    As previously described,
    the object returned by the SP_CVR module is flat.

    :param sp_data:     SP data object

    :return:            Returns 6-digit business code (Type: string)
                        Example: "112233"
    """

    business_code = sp_data["branchekode"]
    return str(business_code)


def update_business_code(update_value):
    """
    Generate an update object
    with the updated business code.

    Example:

    {
        "section": "relationer",
        "key": "branche",
        "update": {
            "branchekode": "112233",
            "virkning: {
                "from": "2018-02-12 00:00:00+01",
                "to": "infinity"
            }
        }
    }

    :param update_value:    6-digit business code (Type: string),
                            example: "112233"

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    # Build update
    update = {
        "urn": "urn:{business_code}".format(
            business_code=update_value
        ),
        "virkning": create_virkning()
    }

    return {
        "section": "relationer",
        "key": "branche",
        "update": update
    }


def extract_business_type_from_oio(org_data):
    """
    Extract business type from an OIO data object.

    Object structure:
    {
        "relationer": {
            "virksomhedstype": [
                {
                    "urn": "urn:<business type code>"
                }
        }
    }

    :param org_data:    OIO data object

    :return:            Returns 3-digit business type value (Type: string)
                        Example: "110"
    """

    # Map
    map = create_object_map(org_data)
    relationer = map["relationer"]
    virksomhedstype_list = relationer.get('virksomhedstype')

    # We expect there only to be one active branche
    if not virksomhedstype_list or len(virksomhedstype_list) != 1:
        log.error(
            "We expect one active virksomhedstype"
        )

        # Include
        log.error(virksomhedstype_list)
        return

    # Grab first item
    virksomhedstype = virksomhedstype_list[0]

    # Split the string
    split_urn_value = virksomhedstype['urn'].split(':')

    # Get the value
    business_type_code = split_urn_value[-1]

    return business_type_code


def extract_business_type_from_sp(cvr_data):
    """
    Extract business type code from a SP data object.

    As previously described,
    the object returned by the SP_CVR module is flat.

    :param sp_data:     SP data object

    :return:            Returns 3-digit business type code (Type: string)
                        Example: "110"
    """

    business_type_code = cvr_data.get('virksomhedsform')
    return str(business_type_code)


def update_business_type(update_value):
    """
    Generate an update object
    with the updated business type value.

    Example:

    {
        "section": "relationer",
        "key": "virksomhedstype",
        "update": {
            "virksomhedsform": "urn:110",
            "virkning: {
                "from": "2018-02-12 00:00:00+01",
                "to": "infinity"
            }
        }
    }

    :param update_value:    3-digit business type value (Type: string)
                            Example: "110"

    :return:                Returns update object
                            (Object as shown in the top example)
    """

    # Build update
    update = {
        "urn": "urn:{type}".format(type=update_value),
        "virkning": create_virkning()
    }

    return {
        "section": "relationer",
        "key": "virksomhedstype",
        "update": update
    }
