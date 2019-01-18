# -- coding: utf-8 --
#
# Copyright (c) 2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import logging
from .settings import LORA_HTTP_BASE, LORA_CA_BUNDLE, LORA_ORG_UUID

logger = logging.getLogger("mox_cpr_delta_mo")


def lora_url(url):
    """format url like
    {BASE}/o/{ORG}/e
    params like
    {'limit':0, 'query':''}
    """
    url = url.format(BASE=LORA_HTTP_BASE, ORG=LORA_ORG_UUID)
    logger.debug(url)
    return url


def lora_get(url, **params):
    url = lora_url(url)
    try:
        return requests.get(url, params=params, verify=LORA_CA_BUNDLE)
    except Exception as e:
        logger.exception(url)


def lora_get_all_cpr_numbers(start=0, end=-1):
    alluuids = lora_get(
        "{BASE}/organisation/bruger/?bvn=%"
    ).json()["results"][0] 
    allcprs = []
    if end == -1:
        end = len(alluuids)
    for i in range(start, end, 90):
        somebrugere=lora_get("{BASE}/organisation/bruger",
                             uuid=alluuids[i:i+90])
        for b in somebrugere.json()["results"][0]:
            urn = b["registreringer"][0]["relationer"][
                    "tilknyttedepersoner"][0]["urn"]
            idnum = urn.split("urn:")[-1]
            if len(idnum) > 8:
                allcprs.append(idnum)
    return allcprs[start:end]
