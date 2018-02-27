# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import json


# Local settings
BASE_DIR = os.path.dirname(__file__)
CONTENT_DIR = "fixtures"

# Fixtures directory
FIXTURES = os.path.join(BASE_DIR, CONTENT_DIR)


def get_test_data(file):

    # Get full path
    test_file = os.path.join(FIXTURES, file)

    # Read file
    with open(test_file, "r") as file:
        test_data = file.read()

    return json.loads(test_data)


# class SomeMath:
def math(integer):
    return 5 + integer