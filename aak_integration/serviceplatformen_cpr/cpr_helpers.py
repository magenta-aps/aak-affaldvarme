# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import serviceplatformen_cpr.settings as settings

from serviceplatformen_cpr.services import get_citizen

uuids = {
    'service_agreement': settings.SP_SERVICE_AGREEMENT_UUID_SF1520_PROD,
    'user_system': settings.SP_USER_SYSTEM_UUID_PROD,
    'user': settings.SP_USER_UUID_PROD,
    'service': settings.SP_SERVICE_SF1520_PROD
}

certificate = settings.SP_CERTIFICATE_PATH


def get_cpr_data(cprnr):

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr
    )
    return result


if __name__ == '__main__':

    cprnr = '0123456789'
    result = get_cpr_data(cprnr)
    print(json.dumps(result))
