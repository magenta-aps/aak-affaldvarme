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
import ava_adapter as adapter


class test_ava_adapter(TestCase):

    def setUp(self):

        # OIO bruger
        self.bruger_data = get_test_data(
            file="oio_bruger.json"
        )

        # OIO Organisation
        self.org_data = get_test_data(
            file="oio_organisation.json"
        )

        # OIO Organisationsfunktion
        self.kunderolle_data = get_test_data(
            file= "oio_organisationfunktion.json"
        )

        # OIO Interessefaellesskab
        self.account_data = get_test_data(
            file="oio_interessefaellesskab.json"
        )

        # OIO Indsats
        self.aftale_data = get_test_data(
            file="oio_indsats.json"
        )

        # OIO Klasse
        self.produkt_data = get_test_data(
            file="oio_klasse.json"
        )

    def test_ava_bruger(self):
        adapter_output = adapter.ava_bruger(self.bruger_data)

        expected_output =  {
            "id": "43214E3A-EF6D-4478-9466-B7B3B722817D",
            "external_ref": None,
            "dawa_ref": "09DF29D5-ED30-4710-BA7C-25A38DFD636B",
            "data": {
                "ava_cpr_nummer": "0102034567",
                "ava_emailkmdee": "email@example.com",
                "ava_eradressebeskyttet": "false",
                "ava_fastnetkmdee": "11223344",
                "ava_kmdeemasterid": "112233",
                "ava_mobilkmdee": "11223344",
                "ava_modtag_sms_notifikation": None,
                "firstname": "First",
                "gendercode": 2,
                "lastname": "Last",
                "middlename": "Middle"
            }
        }

        self.assertEqual(expected_output, adapter_output)


    def test_ava_organisation(self):
        adapter_output = adapter.ava_organisation(self.org_data)

        expected_output = {
            "id": "9EC08DC9-8028-4030-9861-CDB2973A4372",
            "external_ref": None,
            "dawa_ref": "A83604B4-C363-4B9A-9F02-CCC16F93639D",
            "data": {
                "ava_eradressebeskyttet": None,
                "ava_kmdeemasterid": "1122",
                "ava_emailkmdee": "email@example.com",
                "ava_virksomhedsform": "110",
                "firstname": "DeathStar - It's NOT a moon",
                "ava_mobilkmdee": "11223344",
                "ava_fastnetkmdee": "11223344",
                "ava_cvr_nummer": "11223344",
                "ava_modtag_sms_notifikation": None
            }
        }

        self.assertEqual(expected_output, adapter_output)


    def test_ava_kunderolle(self):
        adapter_output = adapter.ava_kunderolle(self.kunderolle_data)

        expected_output = {
            "id": "8a7de9dc-8bb4-4d83-b4bd-c8d5aa3c88de",
            "external_ref": None,
            "contact_ref": "13b8c51d-29dc-4205-982c-5082396b6660",
            "interessefaellesskab_ref": "9c8f3feb-bbd6-4e83-a7d3-a79517258993",
            "data": {
                "ava_rolle": 915240004
            }
        }

        self.assertEqual(expected_output, adapter_output)


    def test_ava_account(self):
        adapter_output = adapter.ava_account(self.account_data)

        expected_output = {
            "id": "4a2d223a-e4dd-471f-ba5c-a29c96753059",
            "external_ref": None,
            "dawa_ref": "befdd8a8-2fc6-45f4-86be-10d75fca204b",
            "data": {
                "ava_kundenummer": "123456",
                "name": "Varme, Testgade 99, 9999 Testby",
                "ava_kundetype": 915240001
            }
        }

        self.assertEqual(expected_output, adapter_output)


    def test_ava_aftale(self):
        adapter_output = adapter.ava_aftale(self.aftale_data)

        expected_output = {
            "id": "61f4eff4-80ab-41c3-9eb4-8e7506256b08",
            "dawa_ref": "a619e796-3f77-4e5b-8138-9f9b8f40e527",
            "klasse_ref": "7eea142b-97cf-4b5d-b4ac-54875e7a7083",
            "interessefaellesskab_ref": "57f01ad2-0160-44f7-af9a-2be943dacc79",
            "external_ref": None,
            "data": {
                "ava_slutdato": "9999-12-31",
                "ava_antal_produkter": 1,
                "ava_startdato": "2014-10-09",
                "ava_aftaletype": 915240001,
                "ava_name": "Varme, 11223344, Testfacility 111-identifier qp 9,9"
            }
        }

        self.assertEqual(expected_output, adapter_output)


    def test_ava_installation(self):
        adapter_output = adapter.ava_installation(self.produkt_data)

        expected_output = {
            "id": "fd20055c-cfcd-405e-911d-62b1fdef4efe",
            "external_ref": None,
            "dawa_ref": None,
            "indsats_ref": None,
            "data": {
                "ava_name": "11223344, Testfacility 999-Identifier qp 9",
                "ava_maalernummer": "11223344",
                "ava_identifikation": "112233",
                "ava_installationstype": 915240001,
                "ava_maalertype": "999-Identifier qp 9",
                "ava_kundenummer": None
            }
        }

        self.assertEqual(expected_output, adapter_output)