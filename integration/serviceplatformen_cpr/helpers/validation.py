# -- coding: utf-8 --
import re

__author__ = "Heini Leander Ovason"


def validate_cprnr(cprnr):

    if cprnr is not None:

        check = re.match(r'^\d{10}$', cprnr)

        if check:

            return True

        else:

            raise ValueError('"{}" is not a valid Danish cprnr.'.format(cprnr))
    else:

        raise TypeError('"{}" is not a valid type.'.format(cprnr))
