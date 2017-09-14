import unittest

from services.udvidet_person_stam_data_lokal import (
    get_citizen,
    validate_cprnr,
    call_cpr_person_lookup_request
)

__author__ = 'Heini Leander Ovason'


class TestUdvidetPersonStamDataLokal(unittest.TestCase):

    # ##### BEGIN TEST - get_citizen_data() #####

    # def test_get_citizen_jens_lyn_exactly_10_digits_OK(self):
    #
    #     cprnr = '0123456789'
    #
    #     uuids = {
    #         'service_agree': '11be3cb9-cd5e-45e8-801e-0fe9502c3a2c',
    #         'user_sys': '11be3cb9-cd5e-45e8-801e-0fe9502c3a2c',
    #         'user': '11be3cb9-cd5e-45e8-801e-0fe9502c3a2c',
    #         'service': '11be3cb9-cd5e-45e8-801e-0fe9502c3a2c'
    #     }
    #
    #     expected = ''
    #
    #     self.assertEqual(
    #         'yeeha!',
    #         get_citizen(service_uuids=uuids, cprnr=cprnr)
    #     )

    # ##### END TEST - get_citizen_data() #####

    # ##### BEGIN TEST - validate_cprnr() #####

    def test_validate_cprnr_10_digits_OK(self):
        self.assertTrue(validate_cprnr('0123456789'))

    def test_validate_cprnr_none_raise_exception(self):
        with self.assertRaises(TypeError):
            validate_cprnr(None)

    def test_validate_cprnr_9_digits_raise_exception(self):
        with self.assertRaises(ValueError):
            validate_cprnr('012345678')

    def test_validate_cprnr_10_digits_raise_exception(self):
        with self.assertRaises(ValueError):
            validate_cprnr('01234567890')

    def test_validate_cprnr_containing_non_digits_raise_exception(self):
        with self.assertRaises(ValueError):
            validate_cprnr('012@456K8')

    # ##### END TEST - validate_cprnr() #####

    # ##### BEGIN TEST - __call_cpr_person_lookup_request() #####

    def test_call_cpr_person_lookup_request(self):
        self.assertEqual(
            'test',
            call_cpr_person_lookup_request('0123456789')
        )

    # ##### END TEST - __call_cpr_person_lookup_request() #####


if __name__ == '__main__':
    unittest.main()
