# -- coding: utf-8 --

import re

__author__ = "Heini Leander Ovason"

# TODO:
# facade function
# validate cprnr - OK
# build SOAP envelope template.
# call SP web service
# parse SOAP xml response to dict


def get_citizen(cprnr):
    """The function returnes a citizen dict from the
    'SF1520 - Udvidet person stamdata (lokal)' service.
    It serves as a facade to simplify input validation, and interaction
    with the SOAP service, and parsing the response to a dict.
    :param cprnr: Danish cprnr
    :type cpr: String of 10 digits / r'^\d{10}$'
    :return: Dictionary representation citizen object.
    :rtype: dict"""

    is_cprnr_valid = validate_cprnr(cprnr)

    if is_cprnr_valid:

        return {'name': 'Jens Lyn'}


def validate_cprnr(cprnr):

    if cprnr is not None:

        check = re.match(r'^\d{10}$', cprnr)

        if check:

            return True

        else:

            raise ValueError('"{}" is not a valid Danish cprnr.'.format(cprnr))
    else:

        raise TypeError('"{}" is not a valid type.'.format(cprnr))
