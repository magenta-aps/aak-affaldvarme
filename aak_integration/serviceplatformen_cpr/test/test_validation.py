#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from helpers.validation import validate_cprnr
from helpers.http_requester import http_post

__author__ = 'Heini Leander Ovason'


class TestValidation(unittest.TestCase):

    # ##### BEGIN TEST CASES - validate_cprnr() #####

    def test_validate_cprnr_10_returns_false(self):
        self.assertTrue(validate_cprnr('0123456789'))

    def test_validate_cprnr_none_returns_false(self):
        self.assertFalse(validate_cprnr(None))

    def test_validate_cprnr_9_digits_returns_false(self):
        self.assertFalse(validate_cprnr('012345678'))

    def test_validate_cprnr_11_digits_returns_false(self):
        self.assertFalse(validate_cprnr('01234567890'))

    # ##### END TEST CASES - validate_cprnr() #####

    # ##### BEGIN TEST CASES - http_post() #####

    @unittest.expectedFailure
    def test_http_post_parameters_are_not_None_return_response_object(self):
        pass

    def test_http_post_if_param_1_is_none_then_return_none(self):

        endpoint = None
        soap_envelope = 'magic soap envelope'
        certificate = 'some/certificate.crt'

        expected = None

        response = http_post(
            endpoint=endpoint,
            soap_envelope=soap_envelope,
            certificate=certificate
        )

        self.assertEqual(expected, response)

    def test_http_post_if_param_2_is_none_then_return_none(self):

        endpoint = 'some web service'
        soap_envelope = None
        certificate = 'some/certificate.crt'

        expected = None

        response = http_post(
            endpoint=endpoint,
            soap_envelope=soap_envelope,
            certificate=certificate
        )

        self.assertEqual(expected, response)

    def test_http_post_if_param_3_is_none_then_return_none(self):

        endpoint = 'some web service'
        soap_envelope = 'magic soap envelope'
        certificate = None

        expected = None

        response = http_post(
            endpoint=endpoint,
            soap_envelope=soap_envelope,
            certificate=certificate
        )

        self.assertEqual(expected, response)

    # ##### END TEST CASES - http_post() #####


if __name__ == '__main__':
    unittest.main()
