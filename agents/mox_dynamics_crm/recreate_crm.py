# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import adal
import logging
import requests

# Local settings
from settings import CRM_RESOURCE
from settings import CRM_TENANT
from settings import CRM_ENDPOINT
from settings import CRM_CLIENT_ID
from settings import CRM_CLIENT_SECRET
from settings import CRM_REST_API_PATH
from settings import CRM_OWNER_ID

# Init logger
log = logging.getLogger(__name__)

# Set vars
base_endpoint = "{resource}/{path}".format(
    resource=CRM_RESOURCE,
    path=CRM_REST_API_PATH
)

# Temporary file containing token
filename = "access_token.tmp"

# Issue/Hotfix:
# We are not able to reliably fetch CRM references before insert
# As a temporary fix, we are storing CRM references in memory
# A more long term solution for this problem is in the works
global_address = {}
global_contact = {}
global_aftale = {}
global_kunderolle = {}
global_produkt = {}
global_account = {}


def get_token():
    """
    Return token (from file)
    There is no promise that the token is valid!
    (This is to avoid requesting a new token for every request)
    """

    # If the file does not exist, generate it
    if not os.path.isfile(filename):
        request_token()

    # Read the file and return the token
    access_token = open(filename, "r")
    return access_token.read()


def request_token():
    """Request a new access token from the MS OAUTH2 service"""

    # Combine OUATH endpoint and tenant id for full endpoint URL
    authority_url = "{url}/{tenant}".format(
        url=CRM_ENDPOINT,
        tenant=CRM_TENANT
    )

    # Connect and authenticate using the ADAL library
    context = adal.AuthenticationContext(
        authority_url,
        validate_authority=CRM_TENANT != "adfs",
        api_version=None
    )

    token = context.acquire_token_with_client_credentials(
        CRM_RESOURCE,
        CRM_CLIENT_ID,
        CRM_CLIENT_SECRET
    )

    if not token:
        return False

    # Write token to temporary file
    with open(filename, "w") as file:
        file.write(token.get("accessToken"))

    return token


def get_request(resource, params):
    """
    Generic GET Request function
    """

    headers = {
        "Authorization": get_token(),
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
    }

    service_url = "{base}/{resource}".format(
        base=base_endpoint,
        resource=resource
    )

    response = requests.get(
        url=service_url,
        headers=headers,
        params=params
    )

    if response.status_code == 401:
        print("Response: {0}".format(response.status_code))

        # Generate a new token
        print("Generate a new token")
        request_token()

        # Sleep 10 seconds
        time.sleep(10)

        # Set new token into the auth header
        headers["Authorization"] = get_token()

        # Perform the request again
        response = requests.get(
            url=service_url,
            headers=headers,
            params=params
        )

    # TODO: implement method to stop the application,
    # if 401 has not been resolved.
    log.debug("GET Request: ")
    log.debug(response.text)
    return response


def delete_request(resource):
    """
    Generic delete request
    """

    headers = {
        "Authorization": get_token(),
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Prefer": "return=representation"
    }

    service_url = "{base}/{resource}".format(
        base=base_endpoint,
        resource=resource
    )

    response = requests.delete(
        url=service_url,
        headers=headers
    )

    if response.status_code == 401:
        print('Requesting token and retrying delete request')

        # Generate a new token
        request_token()

        # Sleep 10 seconds
        time.sleep(10)

        # Set new token into the auth header
        headers["Authorization"] = get_token()

        # Perform the request again
        response = requests.delete(
            url=service_url,
            headers=headers
        )

    return response


def get_all_guids(identifier, resource):

    filter_string = "_ownerid_value eq {0}".format(CRM_OWNER_ID)

    params = {
        "$select": identifier,
        "$filter": filter_string
    }

    query = get_request(resource, params)
    print(query)
    list_of_contacts = query.json()["value"]

    if not list_of_contacts:
        log.info("Contact does not exist in CRM")
        return False

    # If object exists return identifier
    return list_of_contacts


def delete_all(identifier, resource):

    entities = get_all_guids(
        identifier=identifier,
        resource=resource
    )

    if not entities:
        print("No {0} returned".format(resource))
        return

    for entity in entities:
        guid = entity[identifier]
        service = "{0}({1})".format(resource, guid)
        print(service)

        response = delete_request(service)

        if response.status_code != 200:
            print(response.text)

if __name__ == "__main__":
    # Request new token
    request_token()

    # Delete all entities
    delete_all("contactid", "contacts")
    delete_all("ava_adresseid", "ava_adresses")
    delete_all("ava_aftaleid", "ava_aftales")
    delete_all("ava_kunderolleid", "ava_kunderolles")
    delete_all("accountid", "accounts")
    delete_all("ava_installationid", "ava_installations")
