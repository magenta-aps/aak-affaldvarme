# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
from helper import get_config
from logging import getLogger
from cvr_handler import compare
#from service_cvr_online import get_cvr_data
from serviceplatformen_cvr import get_cvr_data
import zeep.exceptions 
import requests.exceptions


# Init logging
log = getLogger(__name__)


def cvr_handler(org_data):
    """
    This function 'handles' an incoming ORG data object (from lora).

    The corresponding SP data set is retrieve (by CVR ID),
    and the data sets are compared using the comparision sets,

    COMPARISIONS:
    The list contains functions to extract values/sets to compare
    as well as the function update the values/sets which are not equal

    For more information on the comparison sets,
    please refer to the compare module from the cvr_handler package.

    :param object:  OIO REST object (Lora)
    :return:        Returns list of objects to be updated
    """

    # Identifier
    uuid = org_data["id"]

    # Extract CVR ID value
    cvr_id = extract_cvr_from_org(org_data)

    # Info
    log.info(
        "Processing org: {0}".format(uuid)
    )


    # Service platform data - perform a simple retry on error
    sp_data = None
    for i in range(2):
        try:
            # Fetch the CVR dataset from SP
            sp_data = get_cvr_data_from_sp(cvr_id)
            break
        except zeep.exceptions.Fault:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except RuntimeError:
            # cvr not found
            continue
    if not sp_data:
        log.error("error for uuid, returning empty list of updates for organisation %s",uuid)
        return []


    # Prepare list of items to be update
    TO_BE_UPDATED = list()

    # Iterate over the comparisions list.
    for org_extractor, cvr_extractor, add_update in COMPARISONS:
        org_field = org_extractor(org_data)
        cvr_field = cvr_extractor(sp_data)

        if not org_field or not cvr_field:
            log.error("Not found in lora or cvr: oio: %s, cvr: %s", org_field, cvr_field)
            return

        if org_field != cvr_field:
            # INFO
            log.info("Data is not equal, updating")

            # Debug
            log.info(json.dumps({
                "old_val": org_field,
                "new_val": cvr_field
            }, indent=2))

            # Run supplied update function
            update = add_update(cvr_field)

            # And append updated object to the list#
            TO_BE_UPDATED.append(update)

    return TO_BE_UPDATED


def extract_cvr_from_org(org_data):
    """
    CVR specific helper function
    to extract the CVR ID value from an ORG/OIO rest object.

    :param org_data:    OIO Rest object (lora)

    :return:            Returns the 8-digit CVR ID value
    """

    # Map
    registreringer = org_data['registreringer']
    relationer = registreringer[0]['relationer']
    virksomhed = relationer['virksomhed']

    # We expect there only 1 object
    if len(virksomhed) != 1:
        # ERROR
        log.error(
            "{amount} CVR ID value(s) returned".format(
                amount=len(virksomhed)
            )
        )
        return

    # Get first (and only) object
    urn = virksomhed[0]

    # Split the urn value
    # Example: urn:25052943
    urn_value = urn["urn"].split(':')

    # Final value
    cvr_id = urn_value[-1]

    # Check
    if not cvr_id:
        log.error(
            "No CVR id found! {0}".format(urn_value)
        )

    return cvr_id


def get_cvr_data_from_sp(cvr_id):
    """
    Wrapper for the underlying 'get_cvr_data' function.

    In order to to gain access to the service,
    a set of service uuids must be passed into every set of service requests.

    Additionally the SP services require a valid certificate
    which must also be passed into every set of service requests.

    Configuration is fetched from the 'config.ini' file,
    using the 'get_config' helper function.

    For more information on the 'get_config' function,
    please see the helper module.

    :param cvr_id:  (Company) CVR ID value

    :return:        Returns the SP data object/set
    """

    # Get config
    config = get_config("sp_cvr")

    # Set service uuids
    uuids = {
        'service_agreement': config["service_agreement"],
        'user_system': config["user_system"],
        'user': config["user"],
        'service': config["service"]
    }

    # Location of the service certificate
    certificate = config["certificate"]

    # GET data from SP
    sp_data = get_cvr_data(
        cvr_id=cvr_id,
        service_uuids=uuids,
        service_certificate=certificate
    )

    # Check
    if not sp_data:
        log.error(
            "No data set found for ID: {id}".format(id=cvr_id)
        )
        return False

    return sp_data


# Tuples representing the comparisons and updates to be made

# First element should be a function
# extracting a value from a LoRa organisation

# Second element should be a function
# extracting a value from CVR data

# Third element should be a function
# extending an existing 'update' object
# with updated values, in case an update should be performed.

COMPARISONS = [
    (
        compare.extract_address_uuid_from_oio,
        compare.extract_address_uuid_from_sp,
        compare.update_address_uuid
    ),
    (
        compare.extract_org_name_from_oio,
        compare.extract_org_name_from_sp,
        compare.update_org_name
    ),
    (
        compare.extract_business_code_from_oio,
        compare.extract_business_code_from_sp,
        compare.update_business_code
    ),
    (
        compare.extract_business_type_from_oio,
        compare.extract_business_type_from_sp,
        compare.update_business_type
    ),
]
