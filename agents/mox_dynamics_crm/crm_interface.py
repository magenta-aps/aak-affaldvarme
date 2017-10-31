# -*- coding: utf-8 -*-

import json
import os
import sys
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

# Set vars
base_endpoint = "{resource}/{path}".format(
    resource=CRM_RESOURCE,
    path=CRM_REST_API_PATH
)

# Temporary file containing token
filename = "access_token.tmp"


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

    # Init logger
    log = logging.getLogger()

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


def post_request(resource, payload):
    """
    Generic POST request function
    """

    # Init logger
    log = logging.getLogger()

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

    response = requests.post(
        url=service_url,
        headers=headers,
        json=payload
    )

    if response.status_code == 401:
        # Generate a new token
        request_token()

        # Set new token into the auth header
        headers["Authorization"] = get_token()

        # Perform the request again
        response = requests.post(
            url=service_url,
            headers=headers,
            json=payload
        )

    log.debug("POST Request: ")
    log.debug(response.text)
    return response


def delete_request(service_url):

    return requests.delete(
        url=service_url,
        headers=headers
    )


def get_contact(lora_uuid):

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "contact"

    search_string = "ava_lora_uuid eq '{0}'".format(lora_uuid)

    params = {
        "$filter": search_string
    }

    query = get_request(resource, params)
    exist_in_crm = query.json()["value"]

    if not exist_in_crm:
        log.info("Contact does not exist in CRM")
        return False

    # If object exists return identifier
    response = exist_in_crm[0]["contactid"]
    return response


def get_ava_address(dawa_uuid):

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "ava_adresses"

    search_string = "ava_dawa_uuid eq '{0}'".format(dawa_uuid)

    params = {
        "$filter": search_string
    }

    query = get_request(resource, params)

    exist_in_crm = query.json()["value"]

    if not exist_in_crm:
        return False

    # If object exists return identifier
    response = exist_in_crm[0]["ava_adresseid"]
    return response


def store_address(payload):
    """Address retrieved from DAWA"""

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "ava_adresses"

    # Check if payload exists
    if not payload:
        return None

    log.info("Creating address in CRM")
    log.debug(payload)
    response = post_request(resource, payload)

    crm_guid = response.json()["ava_adresseid"]

    if not crm_guid:
        log.error("No address GUID returned from CRM")
        log.error("Status code: {0}".format(response.status_code))
        log.error(response.text)
        return False

    return crm_guid


def get_contact(cpr_id):
    """
    Attempt to retrieve CRM contact
    Returns GUID
    Missing: Logging on events
    """

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "contacts"

    search_string = "ava_cpr_nummer eq '{0}'".format(cpr_id)

    params = {
        "$filter": search_string
    }

    # If object exists return identifier
    query = get_request(resource, params)
    exist_in_crm = query.json()["value"]

    if not exist_in_crm:
        return False

    response = exist_in_crm[0]["contactid"]
    return response


def store_contact(payload):
    """
    Store CRM contact and returns creation GUID
    Missing: Logging on events
    """

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "contacts"

    # Check if payload exists
    if not payload:
        return None

    # Attempt to store
    log.info("Creating contact in CRM")
    log.debug(payload)
    response = post_request(resource, payload)

    # Return False if not created
    if response.status_code != 201:
        log.error("Error when attempting to store contact")
        log.error(response.text)
        return False

    crm_guid = response.json()["contactid"]

    if not crm_guid:
        log.error("No contact GUID returned from CRM")
        return False

    return crm_guid


def get_kunderolle(identifier):
    """
    MISSING: We have no reference for the CRM entity
    TODO: May be resolved by creating CRM meta fields
    """
    return False


def store_kunderolle(payload):
    """Organisationsfunktion"""

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "ava_kunderolles"

    # Check if payload exists
    if not payload:
        return None

    # Attempt to store
    log.info("Creating kunderolle in CRM")
    log.debug(payload)
    response = post_request(resource, payload)

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating kunderolle in CRM")
        log.error(response.text)
        log.error("Payload: ")
        log.error(payload)
        return False

    crm_guid = response.json()["ava_kunderolleid"]

    if not crm_guid:
        log.error("No kunderolle GUID returned from CRM")
        return False

    return crm_guid


def get_account(identifier):
    """
    Account (Kundeforhold)
    MISSING: We have no reference for the CRM entity
    TODO: May be resolved by creating CRM meta fields
    """
    return False


def store_account(payload):
    """
    Store account (Kundeforhold)
    Returns GUID
    Missing: Logging on events
    """

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "accounts"
    service_url = "{api}/{resource}".format(
        api=base_endpoint,
        resource=resource
    )

    # Check if payload exists
    if not payload:
        log.error("No payload supplied")
        return None

    log.info("Creating account in CRM")
    log.debug(payload)
    response = post_request(service_url, payload)

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating account in CRM")
        log.error(response.text)
        return False

    crm_guid = response.json()["accountid"]

    if not crm_guid:
        log.error("No account GUID returned from CRM")
        return False

    return crm_guid


def get_aftale(identifier):
    """
    MISSING: We have no reference for the CRM entity
    TODO: May be resolved by creating CRM meta fields
    """
    return False


def store_aftale(payload):
    """Indsats"""

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "ava_aftales"
    service_url = "{api}/{resource}".format(
        api=base_endpoint,
        resource=resource
    )

    # Check if payload exists
    if not payload:
        return None

    log.info("Creating aftale in CRM")
    log.debug(payload)
    response = post_request(service_url, payload)

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating aftale in CRM")
        log.error(response.text)
        return False

    crm_guid = response.json()["ava_aftaleid"]
    if not crm_guid:
        log.error("No aftale GUID returned from CRM")
        return False

    return crm_guid


def get_produkt(identifier):
    """
    MISSING: We have no reference for the CRM entity
    TODO: May be resolved by creating CRM meta fields
    """
    return False


def store_produkt(payload):
    """Klasse"""

    # Init logger
    log = logging.getLogger()

    # REST resource
    resource = "ava_installations"
    service_url = "{api}/{resource}".format(
        api=base_endpoint,
        resource=resource
    )

    # Check if payload exists
    if not payload:
        return None

    log.info("Creating produkt in CRM")
    log.debug(payload)
    response = post_request(service_url, payload)

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating produkt in CRM")
        log.error(response.text)
        return False

    crm_guid = response.json()["ava_installationid"]
    if not crm_guid:
        log.error("No produkt GUID returned from CRM")
        return False

    return crm_guid


# DO NOT USE THE DELETE FUNCTION
# def delete_contact(uuid):

#     # REST resource
#     resource = "contacts({contact})".format(
#         contact=uuid
#     )

#     service_url = "{api}/{resource}".format(
#         api=base_endpoint,
#         resource=resource
#     )

#     crm_response = delete_request(service_url)
#     return crm_response


if __name__ == "__main__":
    request_token()
    token = get_token()
    print(token)
