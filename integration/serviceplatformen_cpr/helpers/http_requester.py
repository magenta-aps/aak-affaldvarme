# -- coding: utf-8 --
import requests

__author__ = "Heini Leander Ovason"


def http_post(endpoint, soap_envelope, certificate):

    try:

        response = requests.post(
            url=endpoint,
            data=soap_envelope,
            cert=certificate
        )

        return response

    except requests.exceptions.RequestException as e:

        print(e)
