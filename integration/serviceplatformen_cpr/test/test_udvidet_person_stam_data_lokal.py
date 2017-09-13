import unittest

from services.udvidet_person_stam_data_lokal import get_citizen_data
from services.udvidet_person_stam_data_lokal import is_cprnr_valid

__author__ = 'Heini Leander Ovason'


class TestUdvidetPersonStamDataLokal(unittest.TestCase):

    def test_get_citizen_data_jens_lyn(self):
        self.assertEqual(
            {'name': 'Jens Lyn'},
            get_citizen_data('0123456789')
        )

    def test_get_citizen_data_incorrect_cprnr_ValueError(self):
        # TODO: This implementation does not work!
        self.assertRaises(
            ValueError,
            get_citizen_data('012345678')
        )

    def test_validate_cprnr_exactly_10_digits(self):
        self.assertTrue(is_cprnr_valid('0123456789'))

    def test_validate_cprnr_under_10_digits(self):
        self.assertFalse(is_cprnr_valid('01234567890'))

    def test_validate_cprnr_above_10_digits(self):
        self.assertFalse(is_cprnr_valid('012345678'))

    def test_validate_cprnr_with_non_digits(self):
        self.assertFalse(is_cprnr_valid('012@456K8'))


if __name__ == '__main__':
    unittest.main()
