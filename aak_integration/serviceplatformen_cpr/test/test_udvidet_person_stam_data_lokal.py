#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import settings

from services.udvidet_person_stam_data_lokal import (
    get_citizen,
    call_cpr_person_lookup_request
)

from helpers.validation import validate_cprnr
from helpers.soap import construct_envelope_SF1520

__author__ = 'Heini Leander Ovason'


class TestUdvidetPersonStamDataLokal(unittest.TestCase):

    @unittest.expectedFailure
    def test_get_citizen_returns_dict(self):
        pass

    @unittest.expectedFailure
    def test_get_citizen_returns_none(self):
        pass


if __name__ == '__main__':
    unittest.main()
