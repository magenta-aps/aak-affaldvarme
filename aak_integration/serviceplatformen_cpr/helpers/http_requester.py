# -- coding: utf-8 --
import requests

__author__ = "Heini Leander Ovason"


def http_post(endpoint, soap_envelope, certificate):

    if endpoint and soap_envelope and certificate:

        response = requests.post(
            url=endpoint,
            data=soap_envelope,
            cert=certificate
        )

        return response

    else:

        return None
