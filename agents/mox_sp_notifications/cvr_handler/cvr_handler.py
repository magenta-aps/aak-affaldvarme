# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import logging
from helper import get_config, create_virkning
from serviceplatformen_cvr import get_cvr_data
from cvr_handler.compare import COMPARISONS

logger = logging.getLogger(__name__)

config = get_config("sp_cvr")


uuids = {
    'service_agreement': config["service_agreement"],
    'user_system': config["user_system"],
    'user': config["user"],
    'service': config["service"]
}

certificate = config["certificate"]

# TODO: Docstrings!!!!


def cvr_handler(object):

    # OIO object
    org_data = object[0]
    uuid = org_data["id"]

    cvr_id = extract_cvr_from_org(org_data)

    # Info
    print(
        "Processing org: {0}".format(uuid)
    )

    # Service platform data
    sp_data = get_cvr_data(
        cvr_id=cvr_id,
        service_uuids=uuids,
        service_certificate=certificate
    )

    update_json = []

    # This will contain objects to update
    for org_extractor, cvr_extractor, add_update in COMPARISONS:
        org_field = org_extractor(org_data, uuid)
        cvr_field = cvr_extractor(sp_data, uuid)

        if not org_field or not cvr_field:
            return

        if org_field != cvr_field:
            update = add_update(cvr_field)
            update_json.append(update)
            # print("Data is not equal, updating")
            # print(json.dumps({
            #     "lora": org_field,
            #     "sp": cvr_field
            # }, indent=2))

    # Update if update_json has been populated
    if not update_json:
        return None

    return update_json





def extract_cvr_from_org(org_data):
    """Extracts a CVR number from a AVA LoRa organisation object"""
    registreringer = org_data['registreringer']
    relationer = registreringer[0]['relationer']
    virksomhed = relationer['virksomhed']

    # We expect there to only be one active cvr registered
    if len(virksomhed) != 1:
        return

    cvr = virksomhed[0]
    # e.g. urn:25052943
    split_urn = cvr['urn'].split(':')
    return split_urn[-1]
