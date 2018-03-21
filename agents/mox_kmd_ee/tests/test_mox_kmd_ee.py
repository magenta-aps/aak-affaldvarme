import common

# steer clear of production data
import ee_data
CUSTRELATIONS = ee_data.CUSTOMER_RELATIONS_FILE = 'var/test_customer_relations'
INSTALLATIONS = ee_data.INSTALLATIONS_FILE = 'var/test_installations'
BULKFILE = "tests/data/test_bulkfile.txt"



import io
import os, sys
import smtpd

class MailServer(smtpd.SMTPServer):
    messages=[]
    def process_message(self,*args,**kwargs):
        self.messages.append((args,kwargs))


class Connected:
    # stub out the database connection, cursor, execute and fetchall

    def close(self):
        return None

    #def fetchall(self,*args,**kwargs):
    #    return []

    #def execute(self,*args,**kwargs):
    #    return self

    def cursor(self,*args,**kwargs):
        return self


class TestMoxKmdEe(common.Test):

    def _connect(self,*args,**kwargs):
        return Connected()

    def _read_installation_records(self,cursor):
        return self.testdata["read_installation_records.json"]

    def _read_customer_records(self,cursor):
        return self.testdata["read_customer_records.json"]

    def _cpr_cvr(self,id_number):
        return self.testdata["cpr_cvr.json"][id_number]

    def setUp(self):
        super().setUp()
        import mox_kmd_ee
        mut = self.mut = mox_kmd_ee
        mut.connect = self._connect 
        mut.read_customer_records = self._read_customer_records
        mut.read_installation_records = self._read_installation_records
        mut.cpr_cvr = self._cpr_cvr

    #@common.debug(TypeError,KeyError)
    def test_initial_imports_has_bulk_errors(self):
        # todo - empty the mox-queue
        if os.path.exists(CUSTRELATIONS):
            os.unlink(CUSTRELATIONS)            
        if os.path.exists(INSTALLATIONS):
            os.unlink(INSTALLATIONS)            
        sys.argv=["--verbose"]
        with self.assertRaises(SystemExit) as cm:
            self.mut.main()
        # look at filename in headers 
        # there should be queued messages for that

