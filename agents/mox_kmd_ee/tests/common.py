import unittest
import os
import json
import sys
import pdb
import functools
import traceback

def debug(*exceptions):
    if not exceptions:
        exceptions = (AssertionError, )
    debug_on_error = os.environ.get("TESTPMPDB",False) 
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                if not debug_on_error:
                    raise
                info = sys.exc_info()
                traceback.print_exception(*info) 
                pdb.post_mortem(info[2])
        return wrapper
    return decorator

class Test(unittest.TestCase):

    @debug(UnicodeDecodeError,json.decoder.JSONDecodeError)
    def setUp(self):
        super().setUp()
        f = os.path.join("tests","data")
        t = self.testdata = {}
        for i in os.listdir(f):
            with open(os.path.join(f,i), encoding="utf-8") as jf:
                if i.endswith(".json"):
                    t[i] = json.load(jf)
                else:
                    t[i] = jf.read()
