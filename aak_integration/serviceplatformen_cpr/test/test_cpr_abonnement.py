import unittest
import settings

from services.cpr_abonnement import (
    cprnr_subscription_service
)

__author__ = 'Heini Leander Ovason'


class TestCprAbonnement(unittest.TestCase):
    """In order to run these test cases you need to:
    - Use a valid cprnr that is not already subscribed too. The tests
    are executed chronologically, and depend on this.
    - Have a valid certificate.
    - Have valid uuids.

    20-09-2017:
        Test executed by author.
        No test cases for exception handling have been implemented yet."""

    # NOTE: Be very careful not to commit real cpr, cert, and uuids!!!

    cprnr = '0123456789'

    uuids = {
        'service_agreement': '1aed0292-86af-42d5-bbc2-45fe0b783d86',
        'user_system': '1aed0292-86af-42d5-bbc2-45fe0b783d86',
        'user': '1aed0292-86af-42d5-bbc2-45fe0b783d86',
        'service': '1aed0292-86af-42d5-bbc2-45fe0b783d86'
    }

    certificate = 'path/to/certificate.crt'

    def test_cprnr_subscription_service_return_ADDED(self):

        operation = 'add'

        expected = "ADDED"

        self.assertEqual(
            expected,
            cprnr_subscription_service(
                cprnr=self.cprnr,
                service_uuids=self.uuids,
                operation=operation,
                certificate=self.certificate
            )
        )

    def test_cprnr_subscription_service_return_ALREADY_EXISTED(self):

        operation = 'add'

        expected = "ALREADY_EXISTED"

        self.assertEqual(
            expected,
            cprnr_subscription_service(
                cprnr=self.cprnr,
                service_uuids=self.uuids,
                operation=operation,
                certificate=self.certificate
            )
        )

    def test_cprnr_subscription_service_return_REMOVED(self):

        operation = 'remove'

        expected = "REMOVED"

        self.assertEqual(
            expected,
            cprnr_subscription_service(
                cprnr=self.cprnr,
                service_uuids=self.uuids,
                operation=operation,
                certificate=self.certificate
            )
        )

    def test_cprnr_subscription_servicen_return_NON_EXISTING_PNR(self):

        operation = 'remove'

        expected = "NON_EXISTING_PNR"

        self.assertEqual(
            expected,
            cprnr_subscription_service(
                cprnr=self.cprnr,
                service_uuids=self.uuids,
                operation=operation,
                certificate=self.certificate
            )
        )
