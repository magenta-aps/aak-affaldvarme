# -*- coding: utf-8 -*-

import json
import logging
import requests

import cache_adapter as adapter

# Local settings
from settings import OIO_REST_URL
from settings import DO_VERIFY_SSL_SIGNATURE
from settings import ORGANISATION_UUID


# Init logging
log = logging.getLogger(__name__)


# Switch statement workaround
# TODO: Please replace with sane code
resources = {
    "bruger": {
        "resource": "organisation/bruger",
        "adapter": adapter.ava_bruger
    },
    "organisation": {
        "resource": "organisation/organisation",
        "adapter": adapter.ava_organisation
    },
    "organisationfunktion": {
        "resource": "organisation/organisationfunktion",
        "adapter": adapter.ava_kunderolle
    },
    "interessefaellesskab": {
        "resource": "organisation/interessefaellesskab",
        "adapter": adapter.ava_account
    },
    "indsats": {
        "resource": "indsats/indsats",
        "adapter": adapter.ava_aftale
    },
    "klasse": {
        "resource": "klassifikation/klasse",
        "adapter": adapter.ava_installation
    }
}


def batch_generator(resource, list_of_uuids):
    """Generate and return batches of objects"""

    # Use switch to determine resource path
    switch = resources.get(resource)

    resource = switch.get("resource")
    adapter = switch.get("adapter")

    # Amount of chuncks a batch contains
    chunck = 50

    # Generate batches until done
    while len(list_of_uuids) > 0:
        uuid_batch = list_of_uuids[:chunck]
        list_of_uuids = list_of_uuids[chunck:]

        params = {
            'uuid': uuid_batch
        }

        # Call GET request function
        results = get_request(resource, params)

        # Return iterator
        for result in results:
            yield adapter(result)


def get_all(resource):

    # Use switch to determine resource path
    switch = resources.get(resource)

    resource = switch.get("resource")

    # Belongs to parent organisation
    params = {
        "tilhoerer": ORGANISATION_UUID
    }

    # Generate list of contacts (uuid)
    log.info(
        "Attempting to import: {0}".format(resource)
    )

    list_of_uuids = get_request(resource, params)

    # Debug:
    total = len(list_of_uuids)

    log.debug(
        "{0} {1} uuid(s) returned".format(total, resource)
    )

    # TODO: Log error when nothing is returned
    if not list_of_uuids:
        log.error("No uuids returned")
        return None

    return list_of_uuids


def fetch_relation(identifier):
    """
    Helper function
    Returns fetch_entity() with paramters
    """

    resource = resources.get("organisationfunktion")

    # Check if the option corresponds with any switch key
    if not resource:
        return False

    params = {
        "tilknyttedebrugere": identifier
    }

    # Call GET request function
    query = get_request(resource, params)

    # Check if a result was returned
    if not query:
        return False

    # Reference uuid
    reference = query[0]

    return query


def fetch_relation_indsats(identifier):
    """
    Helper function
    Returns fetch_entity() with paramters
    """

    resource = resources.get("indsats")

    # Check if the option corresponds with any switch key
    if not resource:
        return False

    params = {
        "indsatsmodtager": identifier
    }

    # Call GET request function
    query = get_request(resource, params)

    # Check if a result was returned
    if not query:
        return False

    # Reference uuid
    reference = query[0]

    # Check for entities with more than one result
    if len(query) > 1:
        print("AFTALE: {}".format(query))

    return fetch_entity("indsats", reference)


def fetch_entity(option, identifier):
    """
    Higher function for performing a GET request
    Returns object or list of objects
        :option: Resource key for using the resources switch
        :identifier: Usually object uuid
    TODO: Resource switch and options is a convoluted mechanic
    MUST: Be replaced rather sooner than later!
    """

    resource = resources.get(option)

    # Check if the option corresponds with any switch key
    if not resource:
        return False

    params = {
        "uuid": identifier
    }

    # Call GET request function
    query = get_request(resource, params)

    # Check if a result was returned
    if not query:
        return False

    # If the list contains only 1 object
    # Return the object instead of a list
    if len(query) is 1:
        return query[0]

    # Return list of objects
    return query


def get_request(resource, params={}):
    """
    Perform the underlying GET request, 
    Returns object (or false if no objects are retrieved) 
        :resource: Service path, e.g. /service/path
        :params: e.g. dict({ "answer": 42 })
    """

    # REST endpoint / resource
    # (https://oio.rest.dk/resource)
    service_url = "{0}/{1}".format(OIO_REST_URL, resource)

    # TODO: Verify SSL signature must dynamically be set
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
