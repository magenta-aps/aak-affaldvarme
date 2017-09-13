# -- coding: utf-8 --

import re

__author__ = "Heini Leander Ovason"

# TODO:
# facade function
# validate cprnr
# build SOAP envelope template.
# call SP web service
# parse SOAP xml response to dict


def get_citizen_data(cprnr):
    """The function returnes a citizen dict from the
    'SF1520 - Udvidet person stamdata (lokal)' service.
    It serves as a facade to simplify input validation and the SOAP interaction
    with the service,and parsing the response to a dict.
    return dict"""

    if is_cprnr_valid(cprnr):

        return {'name': 'Jens Lyn'}
    else:
        raise ValueError('{} is not a valid Danish cprnr.'.format(cprnr))


def is_cprnr_valid(cprnr):
    return re.match(r'^\d{10}$', cprnr)
