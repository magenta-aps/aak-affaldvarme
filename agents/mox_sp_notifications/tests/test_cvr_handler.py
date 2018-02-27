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
from cvr_handler.cvr_handler import extract_cvr_from_org
from cvr_handler.compare import create_object_map
from cvr_handler.compare import extract_address_uuid_from_oio
from cvr_handler.compare import extract_address_uuid_from_sp
from cvr_handler.compare import update_address_uuid
from cvr_handler.compare import extract_org_name_from_oio
from cvr_handler.compare import extract_org_name_from_sp
from cvr_handler.compare import update_org_name
from cvr_handler.compare import extract_business_code_from_oio
from cvr_handler.compare import extract_business_code_from_sp
from cvr_handler.compare import update_business_code
from cvr_handler.compare import extract_business_type_from_oio
from cvr_handler.compare import extract_business_type_from_sp
from cvr_handler.compare import update_business_type

class test_cvr_handler(TestCase):

    def setUp(self):
        self.oio_data = get_test_data("get_oio_organisation.json")
        self.sp_data = get_test_data("get_sp_organisation.json")

    def test_create_object_map(self):
        map = create_object_map(self.oio_data)
        map_length = map.__len__()

        expected_length = 3

        self.assertEqual(expected_length, map_length)


    def test_create_object_map_keys(self):
        extracted = create_object_map(self.oio_data)
        extracted_keys = set(extracted.keys())

        expected_keys = [
            "attributter",
            "relationer",
            "tilstande"
        ]

        expected_keys = set(expected_keys)

        self.assertEqual(expected_keys, extracted_keys)


    def test_extract_cvr_from_org(self):
        extracted_cvr = extract_cvr_from_org(self.oio_data)

        expected_cvr = "11223344"

        self.assertEqual(expected_cvr, extracted_cvr)


    def test_extract_address_uuid_from_oio(self):
        extracted_address = extract_address_uuid_from_oio(self.oio_data)

        expected_address = "A83604B4-C363-4B9A-9F02-CCC16F93639D"

        self.assertEqual(expected_address, extracted_address)


    def test_extract_address_uuid_from_sp(self):
        extracted_address = extract_address_uuid_from_sp(self.sp_data)

        expected_address = "A83604B4-C363-4B9A-9F02-CCC16F93639D"

        self.assertEqual(expected_address, extracted_address)


    def test_update_address_uuid(self):

        test_address = "A83604B4-C363-4B9A-9F02-CCC16F93639D"

        create = update_address_uuid(test_address)
        test_update = create["update"]

        expected_update = {
            "uuid": test_address,
            "virkning": create_virkning()
        }

        self.assertEqual(expected_update, test_update)


    def test_extract_org_name_from_oio(self):
        extracted_org_name = extract_org_name_from_oio(self.oio_data)

        expected_org_name = "DeathStar - It's NOT a moon"

        self.assertEqual(expected_org_name, extracted_org_name)


    def test_extract_org_name_from_sp(self):
        extracted_org_name = extract_org_name_from_sp(self.sp_data)

        expected_org_name = "DeathStar - It's NOT a moon"

        self.assertEqual(expected_org_name, extracted_org_name)


    def test_update_org_name(self):

        org_name = "DeathStar - It's NOT a moon"

        create = update_org_name(org_name)
        test_update = create["update"]

        expected_update = {
            "organisationsnavn": org_name,
            "virkning": create_virkning()
        }

        self.assertEqual(expected_update, test_update)


    def test_extract_business_code_from_oio(self):
        extracted_code = extract_business_code_from_oio(self.oio_data)
        expected_code = "682010"

        self.assertEqual(extracted_code, expected_code)


    def test_extract_business_code_from_sp(self):
        extracted_code = extract_business_code_from_sp(self.sp_data)
        expected_code = "682010"

        self.assertEqual(extracted_code, expected_code)


    def test_update_business_code(self):
        test_code = "682010"

        create = update_business_code(test_code)
        test_update = create["update"]

        formatted_code = "urn:{code}".format(code=test_code)

        expected_update = {
            "urn": formatted_code,
            "virkning": create_virkning()
        }

        self.assertEqual(expected_update, test_update)


    def test_extract_business_type_from_oio(self):
        extracted_type = extract_business_type_from_oio(self.oio_data)
        expected_type = "110"

        self.assertEqual(expected_type, extracted_type)


    def test_extract_business_type_from_sp(self):
        extracted_type = extract_business_type_from_sp(self.sp_data)
        expected_type = "110"

        self.assertEqual(expected_type, extracted_type)


    def test_update_business_type(self):
        test_type = "682010"

        create = update_business_type(test_type)
        test_update = create["update"]

        formatted_type = "urn:{type}".format(type=test_type)

        expected_update = {
            "urn": formatted_type,
            "virkning": create_virkning()
        }

        self.assertEqual(expected_update, test_update)
