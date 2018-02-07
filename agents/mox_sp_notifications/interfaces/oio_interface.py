import logging
import requests
from datetime import datetime

log = logging.getLogger(__name__)

OIO_REST_URL = "https://minilab"
ORGANISATION_UUID = "842092f6-7147-4349-bf8c-626757a28771"
DO_VERIFY_SSL_SIGNATURE = False

switch = {
    "bruger": "organisation/bruger",
    "organisation": "organisation/organisation"
}


def get_all(resource):
    """
    Wrapper function to retrieve all objects uuids,
    which belong to the parent organisation (see settings on top).

    :param resource:    Name of the resource path/entity
    :return:            Returns a list of entity uuids
                        (References only, not the actual database objects)
    """


    # Generate list of contacts (uuid)
    log.info(
        "Attempting to import: {0}".format(resource)
    )

    list_of_uuids = get_request(
        resource=resource,
        tilhoerer=ORGANISATION_UUID
    )

    # Debug
    log.debug(
        "{total_amount} {resource} uuid(s) returned".format(
            total_amount=len(list_of_uuids),
            resource=resource
        )
    )

    if not list_of_uuids:
        log.error("No uuids returned")
        return None

    return list_of_uuids


def get_request(resource, **params):
    """
    Parent function to perform the underlying GET request,
    Returns object (or false if no objects are retrieved)

    :param resource:    Resource path, e.g. /service/path
    :param params:      Query parameters
    :return:
    """

    # Use switch to determine resource path
    resource = switch.get(resource)

    # Generate service url
    service_url = "{base_url}/{resource}".format(
        base_url=OIO_REST_URL,
        resource=resource
    )

    # GET REQUEST
    oio_response = requests.get(
        url=service_url,
        params=params,
        verify=DO_VERIFY_SSL_SIGNATURE
    )

    # TODO: If request fails, Log to error queue
    if oio_response.status_code != 200:
        return False

    results = oio_response.json()["results"]

    # Check if the list is empty
    if len(results) <= 0:
        return False

    # Currently OIO REST returns a list inside a list,
    # As such, we return the first result which is the actual list
    # {
    # "results": [
    #     [ <objects...> ]  <-- This is what we want
    #   ]
    # }
    return results[0]


def put_request(resource, identifier, payload):
    """
    Parent function to perform the underlying GET request,
    Returns object (or false if no objects are retrieved)

    :param resource:    Resource path, e.g. /service/path
    :param params:      Query parameters
    :return:
    """

    # Use switch to determine resource path
    resource = switch.get(resource)

    # Generate service url
    service_url = "{base_url}/{resource}/{uuid}".format(
        base_url=OIO_REST_URL,
        resource=resource,
        uuid=identifier
    )

    # PUT REQUEST
    return requests.put(
        url=service_url,
        json=payload,
        verify=DO_VERIFY_SSL_SIGNATURE
    )


def update_bruger(identifier, payload):

    response = put_request(
        resource="bruger",
        identifier=identifier,
        payload=payload
    )

    if not response.status_code == 200:
        print(response.text)

    return response.json()



