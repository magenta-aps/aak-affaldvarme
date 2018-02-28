# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase
from .utils import get_test_data

# Testing import
from helper import create_virkning
from cpr_handler import compare
from cpr_handler.cpr_handler import extract_cpr_id


class test_cpr_handler(TestCase):
    """
    Test class for the cpr handler
    """

    def setUp(self):
        self.test_data = get_test_data("oio_bruger.json")
        self.sp_data = get_test_data("get_sp_person.json")


    def test_helper_create_map(self):
        map = compare.create_object_map(self.test_data)
        map_length = map.__len__()

        expected_length = 3

        self.assertEqual(expected_length, map_length)


    def test_helper_create_map_keys(self):
        extracted = compare.create_object_map(self.test_data)
        extracted_keys = set(extracted.keys())

        expected_keys = [
            "attributter",
            "relationer",
            "tilstande"
        ]

        expected_keys = set(expected_keys)

        self.assertEqual(expected_keys, extracted_keys)


    def test_cpr_id_value_extraction(self):
        # Extract value (testing)
        extracted_value = extract_cpr_id(self.test_data)

        # Expected value
        expected_value = "0102034567"

        # Assertion
        self.assertEqual(expected_value, extracted_value)


    def test_extract_details_from_oio(self):
        extracted_details = compare.extract_details_from_oio(self.test_data)

        expected_details = {
            "ava_mellemnavn": None,
            "ava_civilstand": "G",
            "ava_efternavn": "Last",
            "ava_koen": "K",
            "ava_adressebeskyttelse": "false",
            "ava_fornavn": "First"
        }

        self.assertEqual(expected_details, extracted_details)


    def test_extract_details_from_sp(self):
        extracted_details = compare.extract_details_from_sp(self.sp_data)

        expected_details = {
            "ava_mellemnavn": None,
            "ava_civilstand": "G",
            "ava_efternavn": "Last",
            "ava_koen": "K",
            "ava_adressebeskyttelse": "false",
            "ava_fornavn": "First"
        }

        self.assertEqual(expected_details, extracted_details)


    def test_udate_details(self):
        """

        :return:

        """

        # {
        #     "section": "attributter",
        #     "key": "brugeregenskaber",
        #     "update": update_value
        # }

        test_data = {
            "ava_efternavn": "Last",
            "ava_fornavn": "First",
            "ava_koen": "K"
        }

        test_dict = compare.update_details(test_data)
        test_update = test_dict["update"]


        expected_result = {
            "ava_efternavn": "Last",
            "ava_fornavn": "First",
            "ava_koen": "K",
            "virkning": create_virkning()
        }

        self.assertEqual(expected_result, test_update)


    def test_extract_address_uuid_from_oio(self):

        test_data = compare.extract_address_uuid_from_oio(self.test_data)

        expected_address_uuid = "09DF29D5-ED30-4710-BA7C-25A38DFD636B"

        self.assertEqual(expected_address_uuid, test_data)



    def test_update_address(self):
        test_data = {
            "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F"
        }

        test_dict = compare.update_details(test_data)
        test_update = test_dict["update"]

        expected_update = {
            "uuid": "04448F85-4FEA-430F-A386-C65DE21F8F2F",
            "virkning": create_virkning()
        }

        self.assertEqual(expected_update, test_update)



