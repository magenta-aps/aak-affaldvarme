# -*- coding: utf-8 -*-

import os
import time
import json
import adal
import requests

from logging import getLogger
from helper import get_config

# If this is set to True, the agent will not write anything to CRM.
DO_WRITE = False

# Configuration section
# A configuration block must be added to config.ini
# Example:
#
# [ms_dynamics_crm]
# crm_resource = https://myapplication.crm.dynamics.com
# crm_tenant = 551DCF91-FB70-4E88-A5AD-701A75B31BF3
# crm_oauth_endpoint = https://login.windows.net
# crm_client_id = 551DCF91-FB70-4E88-A5AD-701A75B31BF3
# crm_client_secret = <HASH>
# crm_rest_api_path = "api/data/v8.2"
# crm_owner_id = 551DCF91-FB70-4E88-A5AD-701A75B31BF3
#

# Configuration section
section = "ms_dynamics_crm"

# Get config
config = get_config(section)

# Local settings
CRM_RESOURCE = config["crm_resource"]
CRM_TENANT = config["crm_tenant"]
CRM_ENDPOINT = config["crm_oauth_endpoint"]
CRM_CLIENT_ID = config["crm_client_id"]
CRM_CLIENT_SECRET = config["crm_client_secret"]
CRM_REST_API_PATH = config["crm_rest_api_path"]

# Init logger
log = getLogger(__name__)

# Request timeout workaround
# Setting retry attempts to 15
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=15)
session.mount('http://', adapter)
session.mount('https://', adapter)
requests = session

# REST API endpoint (base)
base_endpoint = "{resource}/{path}".format(
    resource=CRM_RESOURCE,
    path=CRM_REST_API_PATH
)

# Temporary file containing token
# It may be better to store the token in a global variable
filename = "access_token.tmp"


# Request header information
# These are the default values
# An authorization header must be added on each request
headers = {
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0",
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Prefer": "return=representation"
}


class DummyRequest:
    """Simulate a real return value from requests."""

    def __init__(self, status_code, json_field=None):
        self.status_code = status_code
        self.json_field = json_field
        self.text = "Hej!"

    def json(self):
        from uuid import uuid4
        return {self.json_field: str(uuid4())}


def get_token():
    """
    Get generated token from file.

    The token is stored in a temporary file
    which can be accessed globally.

    This is a temporary solution
    to reduce the amount of requests for tokens.

    :return:    Returns access token
    """

    # If the file does not exist, generate it
    if not os.path.isfile(filename):
        request_token()

    # Read the file and return the token
    with open(filename, "r") as token:
        return token.read()


def request_token():
    """
    If no valid token exists,
    A new token can be requested from the OAUTH REST Service.

    The service provider must add the correct privileges
    in order to to grant read/write access.

    E.g.
    In previous scenarios a token was granted, however with no privileges,
    we were unable to retrieve any information from the REST API.

    :return:    Returns newly generated token or False
    """

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


def get_request(resource, **params):
    """
    Generic GET request.

    (Primiarily used by child/wrapper functions)

    If the token header is invalid or the token is expired,
    a new token is requested and the original request is performed once more.

    :param resource:    Resource (resource path),
                        e.g. 'contacts', 'ava_adresses' etc.

    :param params:      Query parameters

    :return:            Returns full response object
    """

    headers["Authorization"] = get_token()

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
        log.warning("HTTP Response: {0}".format(response.status_code))

        # Generate a new token
        log.info("Generating a new token")
        request_token()

        # Sleep 10 seconds
        time.sleep(10)

        # Set generated token into the auth header
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
    Generic POST request

    (Primiarily used by child/wrapper functions)

    If the token header is invalid or the token is expired,
    a new token is requested and the original request is performed once more.

    :param resource:    Resource (resource path),
                        e.g. 'contacts', 'ava_adresses' etc

    :param payload:     Payload (dictionary)

    :return:            Returns full response object
    """

    headers["Authorization"] = get_token()

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
        log.warning("HTTP Response: {0}".format(response.status_code))

        # Generate a new token
        log.info("Generating a new token")
        request_token()

        # Sleep 10 seconds
        time.sleep(10)

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


def patch_request(resource, payload):
    """
    Generic PATCH request.

    A patch request can be used to update existing objects,
    or alternatively import new objects (with a predefined identifier).

    (Primiarily used by child/wrapper functions)

    Please note that the identifier
     should be passed in as part of the resource.

    E.g. {base_url}/contacts(<uuid>)

    :param resource:    Resource (resource path) containing the identifier,
                        (See example above)

    :param payload:     Payload (dictionary)

    :return:            Returns full response object
    """

    # Set token into authorization header
    headers["Authorization"] = get_token()

    service_url = "{base}/{resource}".format(
        base=base_endpoint,
        resource=resource
    )

    response = requests.patch(
        url=service_url,
        headers=headers,
        json=payload
    )

    if response.status_code == 401:
        log.warning("HTTP Response: {0}".format(response.status_code))

        # Generate a new token
        log.info("Generating a new token")
        request_token()

        # Sleep 10 seconds
        time.sleep(10)

        # Set new token into the auth header
        headers["Authorization"] = get_token()

        # Perform the request again
        response = requests.patch(
            url=service_url,
            headers=headers,
            json=payload
        )

    log.debug("PATCH Request: ")
    log.debug(response.text)
    return response


def delete_request(resource, identifier):
    """
    Generic DELETE request

    !! This should never be used in production. !!

    In order to 'remove' an object,
    the object is set to inactive,
    rather than actually being deleted.

    The reason for this is how relations between objects work in CRM.

    Delete is development purposes only (e.g. to 'reset' the database)

    (Primiarily used by child/wrapper functions)

    :param resource:    Resource (resource path)

    :param identifier:  MS Dynamics CRM object GUID
                        e.g. 551DCF91-FB70-4E88-A5AD-701A75B31BF3

    :return:            Returns full response object
                        (Status code 204 on deletion)
    """

    # Set token into authorization header
    headers["Authorization"] = get_token()

    service_url = "{base}/{resource}({identifier})".format(
        base=base_endpoint,
        resource=resource,
        identifier=identifier
    )

    response = requests.delete(
        url=service_url,
        headers=headers
    )

    if response.status_code == 401:
        log.debug('Requesting token and retrying DELETE request')

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

    log.debug("Delete Request: ")
    log.debug(response.text)
    return response


def store_address(payload):
    """
    Wrapper function
    to insert new address objects into CRM via a POST request.

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # Check if payload exists
    if not payload:
        return None

    # REST resource
    resource = "ava_adresses"

    log.info("Creating address in CRM")
    log.debug(payload)
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "ava_adresseid")

    crm_guid = response.json()["ava_adresseid"]

    if not crm_guid:
        log.error("No address GUID returned from CRM")
        log.error("Status code: {0}".format(response.status_code))
        log.error(response.text)
        return False

    return crm_guid


def update_address(identifier, payload):
    """
    Wrapper function to update CRM address via a PATCH request.

    CRM:    Adresse (ava_adresses)

    :param identifier:  DAR/DAWA identifier (Type: uuid)
    :param payload:     Payload (dictionary)

    :return:            Returns updated CRM object
    """

    # REST resource
    resource = "ava_adresses({identifier})".format(
        identifier=identifier
    )

    log.info("Updating address in CRM")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating address in CRM for"
            " resource: {resource}".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("Address updated")
    return response


def store_contact(payload):
    """
    Wrapper function
    to insert new contact objects into CRM via a POST request.

    OIO:    Bruger/Organisation
    CRM:    Contact (contacts)

    Missing: additional logging

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # REST resource
    resource = "contacts"

    # Check if payload exists
    if not payload:
        return None

    # Attempt to store
    log.info("Creating contact in CRM")
    log.debug(payload)
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "contactid")

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


def update_contact(identifier, payload):
    """
    Wrapper function
    to update existing contact objects via a PATCH request.

    OIO:    Bruger/Organisation
    CRM:    Contact (contacts)

    :param identifier:  Object identifier (guid)
    :param payload:     Payload (dictionary)

    :return:            Returns the updated object
    """

    # REST resource
    resource = "contacts({identifier})".format(
        identifier=identifier
    )

    log.info("UPDATING contact in CRM")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating contact in CRM"
            " for resource: {resource}".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("Contact updated")
    return response


def store_kunderolle(payload):
    """
    Wrapper function
    to insert new kunderolle objects into CRM via a POST request.

    OIO:    Interessefaellesskab
    CRM:    Kunderolle (ava_kunderolles)

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # REST resource
    resource = "ava_kunderolles"

    # Check if payload exists
    if not payload:
        return None

    # Attempt to store
    log.info("Creating kunderolle in CRM")
    log.debug(payload)
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "ava_kunderolleid")

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating kunderolle in CRM")
        log.error(response.text)
        return False

    if response.status_code == 400:
        log.error("Payload: ")
        log.error(json.dumps(payload))

    crm_guid = response.json()["ava_kunderolleid"]

    if not crm_guid:
        log.error("No kunderolle GUID returned from CRM")
        return False

    return crm_guid


def update_kunderolle(identifier, payload):
    """
    Wrapper function to update CRM account via a PATCH request.

    OIO:    Organisationfunktion
    CRM:    Kunderolle (ava_kunderolles)

    :param identifier:  CRM object identifier (Type: uuid)
    :param payload:     Payload (dictionary)

    :return:            Returns updated CRM object
    """

    # REST resource
    resource = "ava_kunderolles({identifier})".format(
        identifier=identifier
    )

    log.info("Updating CRM kunderolle")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating CRM kunderolle for"
            " resource: {resource}".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("CRM kunderolle updated")
    return response


def store_account(payload):
    """
    Wrapper function
    to insert new account objects into CRM via a POST request.

    OIO:    Organisationfunktion
    CRM:    Account (accounts)

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # REST resource
    resource = "accounts"

    # Check if payload exists
    if not payload:
        log.error("No payload supplied")
        return None

    log.info("Creating account in CRM")
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "accountid")

    # Return False if not created
    if response.status_code != 201:
        log.error("Error creating account in CRM")
        log.error(response.json())
        log.error(payload)
        return False

    crm_guid = response.json()["accountid"]

    if not crm_guid:
        log.error("No account GUID returned from CRM")
        return False

    return crm_guid


def update_account(identifier, payload):
    """
    Wrapper function to update CRM account via a PATCH request.

    OIO:    Interessefaellesskab
    CRM:    Kundeforhold (accounts)

    :param identifier:  CRM object identifier (Type: uuid)
    :param payload:     Payload (dictionary)

    :return:            Returns updated CRM object
    """

    # REST resource
    resource = "accounts({identifier})".format(
        identifier=identifier
    )

    log.info("Updating CRM account")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating CRM account for"
            " resource: {resource}".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("Account updated")
    return response


def store_aftale(payload):
    """
    Wrapper function
    to insert new aftale objects into CRM via a POST request.

    OIO:    Indsats
    CRM:    Aftale (ava_aftales)

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # REST resource
    resource = "ava_aftales"

    # Check if payload exists
    if not payload:
        return None

    log.info("Creating aftale in CRM")
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "ava_aftaleid")

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


def update_aftale(identifier, payload):
    """
    Wrapper function to update CRM aftale via a PATCH request.

    OIO:    Indsats
    CRM:    Aftale (ava_aftales)

    :param identifier:  CRM object identifier (Type: uuid)
    :param payload:     Payload (dictionary)

    :return:            Returns updated CRM object
    """

    # REST resource
    resource = "ava_aftales({identifier})".format(
        identifier=identifier
    )

    log.info("Updating CRM aftale")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating CRM aftale for"
            " resource: {resource} ".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("CRM aftale updated")
    return response


def store_produkt(payload):
    """
    Wrapper function
    to insert new produkt objects into CRM via a POST request.

    OIO:    Klasse
    CRM:    Produkt (ava_installations)

    :param payload:     Payload (dictionary)

    :return:            Returns CRM guid if inserted
                        or False if the request has failed
    """

    # REST resource
    resource = "ava_installations"

    # Check if payload exists
    if not payload:
        return None

    log.info("Creating produkt in CRM")
    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(201, "ava_installationid")

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


def update_produkt(identifier, payload):
    """
    Wrapper function to update produkt via a PATCH request.

    OIO:    Klasse
    CRM:    Produkt (ava_installations)

    :param identifier:  Object GUID (ava_installationid)
    :param payload:     Payload (dictionary)

    :return:            Returns CRM GUID or False
    """

    # REST resource
    resource = "ava_installations({identifier})".format(
        identifier=identifier
    )

    log.info("UPDATING produkt in CRM")
    if DO_WRITE:
        response = patch_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error updating CRM produkt for"
            " resource: {resource} ".format(**locals())
        )
        log.error(response.text)
        return False

    log.info("Produkt updated")
    return response


def DEPRECATED_contact_and_aftale_link(aftale_guid, contact_guid):
    """
    Temporary solution to create a link between contact and aftale
    NOTES: This should be replaced by the cache functionality

    :param aftale_guid:     CRM identifier (GUID) for entity: ava_aftale
    :param contact_guid:    CRM identifier (GUID) for entity: contact

    :return:                Nothing is returned from CRM,
                            returning True when request is successfull
    """

    resource = "ava_aftales({guid})/ava_aktoerens_aftaler/$ref".format(
        guid=aftale_guid
    )

    odata_id = "{base}/contacts({guid})".format(
        base=base_endpoint,
        guid=contact_guid
    )

    payload = {
        "@odata.id": odata_id
    }

    if DO_WRITE:
        response = post_request(resource, payload)
    else:
        response = DummyRequest(200)

    # Return False if not created
    if response.status_code != 200:
        log.error(
            "Error creating link between contact and aftale"
            " for resource: {resource} with"
            " payload: {payload}".format(**locals())
        )
        log.error(response.text)
        return False

    return True


def mend_contact_and_aftale_link(contact, aftale):
    """ link from aftale to contact - aftale has it cached
        if new link is in aftale and it is unchanged:
            leave it
        if it is different (or non existing):
            try to update
        if it does not update:
            insert
    """

    resource = "ava_aftales({guid})/ava_aktoerens_aftaler/$ref".format(
        guid=aftale["external_ref"]
    )

    # the new link is absolute (server-specific)
    contact_ref_link = "{base}/contacts({guid})".format(
        base=base_endpoint,
        guid=contact["external_ref"]
    )

    if contact_ref_link == aftale.get("contact_ref_link"):
        # this one is unchanged - leave it
        requestors = []
    else:
        # be safe - try to update, if that does not work, insert
        requestors = [patch_request, post_request]
        aftale["contact_ref_link"] = contact_ref_link

    payload = {
        "@odata.id": contact_ref_link
    }

    if DO_WRITE and len(requestors):
        for req in requestors:
            response = req(resource, payload)
            if response.status_code == 200:
                log.info(
                    "Success updating/inserting link ({req})"
                    " from aftale to contact"
                    " for resource: {resource} with"
                    " payload: {payload}".format(**locals())
                )
                break
            else:
                log.error(
                    "Error updating/inserting link ({req})"
                    " from aftale to contact"
                    " for resource: {resource} with"
                    " payload: {payload}".format(**locals())
                )
    elif len(requestors):
        log.info(
            "Pretended updating link with"
            " {requestors} from aftale to contact"
            " for resource: {resource} with payload:"
            " {payload}".format(**locals())
        )

    # return whether or not something was done
    return len(requestors) > 0
