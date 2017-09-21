import unittest

from helpers.validation import validate_cprnr

__author__ = 'Heini Leander Ovason'


class TestValidation(unittest.TestCase):

    # ##### BEGIN TEST - validate_cprnr() #####

    def test_validate_cprnr_10_returns_false(self):
        self.assertTrue(validate_cprnr('0123456789'))

    def test_validate_cprnr_none_returns_false(self):
        self.assertFalse(validate_cprnr(None))

    def test_validate_cprnr_9_digits_returns_false(self):
        self.assertFalse(validate_cprnr('012345678'))

    def test_validate_cprnr_11_digits_returns_false(self):
        self.assertFalse(validate_cprnr('01234567890'))


if __name__ == '__main__':
    unittest.main()
