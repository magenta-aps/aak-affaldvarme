# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re

__author__ = "Heini Leander Ovason"


def validate_cprnr(cprnr):

    if cprnr:

        check = re.match(r'^\d{10}$', cprnr)

        if check:

            return True

        else:

            # Log e.g. 'Not a valid cprnr'
            return False

    else:

        # Log e.g. 'Type error occured: input'
        return False
