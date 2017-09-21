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

    @unittest.expectedFailure
    def test_http_post_parameters_are_none_returns_none(self):
        pass

    # ##### END TEST CASES - http_post() #####


if __name__ == '__main__':
    unittest.main()
