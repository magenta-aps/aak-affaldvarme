import common

import os
import sys
import ee_data
import mox_kmd_ee

# steer clear of prod data
CUSTRELATIONS = 'var/test_customer_relations'
INSTALLATIONS = 'var/test_installations'
BULKFILE = "tests/data/test_bulkfile.txt"
ee_data.CUSTOMER_RELATIONS_FILE = CUSTRELATIONS
ee_data.INSTALLATIONS_FILE = INSTALLATIONS
mox_kmd_ee.CUSTOMER_RELATIONS_FILE = CUSTRELATIONS
mox_kmd_ee.INSTALLATIONS_FILE = INSTALLATIONS


class Connected:
    # stub out the database connection,
    # cursor, execute and fetchall

    def close(self):
        return None

    def cursor(self, *args, **kwargs):
        return self


class TestMoxKmdEe(common.Test):

    def _connect(self, *args, **kwargs):
        return Connected()

    def _read_installation_records(self, cursor):
        return self.testdata["read_installation_records.json"]

    def _read_customer_records(self, cursor):
        return self.testdata["read_customer_records.json"]

    def _cpr_cvr(self, id_number):
        return self.testdata["cpr_cvr.json"][id_number]

    def setUp(self):
        super().setUp()
        # use test data
        mox_kmd_ee.connect = self._connect
        mox_kmd_ee.read_customer_records = self._read_customer_records
        mox_kmd_ee.read_installation_records = self._read_installation_records
        mox_kmd_ee.cpr_cvr = self._cpr_cvr

    # @common.debug(TypeError,KeyError)
    def test_initial_imports_exits_main(self):
        if os.path.exists(CUSTRELATIONS):
            os.unlink(CUSTRELATIONS)
        if os.path.exists(INSTALLATIONS):
            os.unlink(INSTALLATIONS)
        sys.argv = ["--verbose"]
        with self.assertRaises(SystemExit):
            mox_kmd_ee.main()
