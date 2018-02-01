# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import requests

__author__ = "Heini Leander Ovason"


def http_post(endpoint, soap_envelope, certificate):

    if endpoint and soap_envelope and certificate:

        response = requests.post(
            url=endpoint,
            data=soap_envelope,
            cert=certificate
        )

        return response

    else:

        return None
