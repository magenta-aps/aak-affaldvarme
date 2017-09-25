# -- coding: utf-8 --
import re

__author__ = "Heini Leander Ovason"


def validate_cprnr(cprnr):

    if cprnr:

        check = re.match(r'^\d{10}$', cprnr)

        if check:

            return True

        else:

            # Log e.g. 'Not a valid cprnr'
            return False

    else:

        # Log e.g. 'Type error occured: input'
        return False
