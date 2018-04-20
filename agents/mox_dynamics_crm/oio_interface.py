# -*- coding: utf-8 -*-

import requests
import ava_adapter as adapter

from helper import get_config
from logging import getLogger

import cache_interface as cache


# Settings (For compatibility)
# TODO: Make general use of config (Configparser)
config = get_config()

# OIO Rest Interface endpoint
OIO_REST_URL = config["oio_rest_endpoint"] or "localhost"

# Parent organisation
# Reference to which organisation an object belongs to
# NOTE: Only some entities support this reference
ORGANISATION_UUID = config["parent_organisation"] or None

# Optionally the signature of the SSL certificate can be verified
# This should be disabled when no commercial certificate is installed
# (E.g. should be disabled or set to 'no' when using a self signed signature)
# By default this is set to 'Yes'
DO_VERIFY_SSL_SIGNATURE = config.getboolean("do_verify_ssl_signature", True)

# Init logging
log = getLogger(__name__)


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
    """
    Utility function to generate batches of database objects.
    The size of the batches are determined from the 'chunk' value.

    TODO:   There may be a need to accept a size parameter
            (To dynamically set the batch sizes)

    :param resource:        Resource or name of the database entity
    :param list_of_uuids:   A list of identifiers (Type: uuid)

    :return:                Returns a generator (iterator).
                            Objects returned by the generator
                            are converted by the adapter (See ava_adapter.py).
    """

    # Use switch to determine resource path
    switch = resources.get(resource)
    table = cache.mapping.get(resource)

    resource = switch.get("resource")
    adapter = switch.get("adapter")

    # Amount of chuncks a batch contains
    chunck = 50

    # Generate batches until done
    while len(list_of_uuids) > 0:
        uuid_batch = list_of_uuids[:chunck]
        list_of_uuids = list_of_uuids[chunck:]

        # Call GET request function
        results = get_request(
            resource=resource,
            uuid=uuid_batch
        )

        if not results:
            log.error("No results for batch: ")
            log.error(uuid_batch)
            return False

        existing_adapted = {
            d["id"]: d
            for d in cache.r.table(
                table
                ).get_all(*uuid_batch).run(cache.connect())
        }

        batch = []

        # Batch timestamp
        batch_timestamp = cache.r.now()

        # Return iterator
        for result in results:
            adapted = adapter(result, existing_adapted.get(result["id"], {}))

            if not adapted:
                log.error("One faulty result: ")
                log.error(result)
                break

            # set update time
            adapted["updated"] = batch_timestamp

            batch.append(adapted)

        yield batch


def get_all(resource):
    """
    Wrapper function to retrieve all objects uuids,
    which belong to the parent organisation (see settings on top).

    :param resource:    Name of the resource path/entity
    :return:            Returns a list of entity uuids
                        (References only, not the actual database objects)
    """

    # Use switch to determine resource path
    switch = resources.get(resource)

    resource = switch.get("resource")

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

    # Currently OIO REST returns a list inside a list,
    # As such, we return the first result which is the actual list
    # {
    # "results": [
    #     [ <objects...> ]  <-- This is what we want
    #   ]
    # }

    # First, check if the list is empty
    if len(results[0]) <= 0:
        return False

    return results[0]


# DEPRECATED:
# The following functions are no longer used
# Functionality has been replaced by the cache layer implementation

# def fetch_relation(identifier):
#     """
#     Wrapper function for retriving related 'organisationfunktion' by id.
#     LORA:   organisationfunktion
#     CRM:    kunderolle
#
#     :param identifier:  Entity id (Type: uuid) for owner reference
#                         Owner is a contact (bruger / organisation)
#     :return:            Returns OIO rest object
#     """
#
#     resource = resources.get("organisationfunktion")
#
#     # Check if the option corresponds with any switch key
#     if not resource:
#         return False
#
#     # Call GET request function
#     query = get_request(
#         resource=resource,
#         tilknyttedebrugere=identifier
#     )
#
#     # Check if a result was returned
#     if not query:
#         return False
#
#     return query


# def fetch_relation_indsats(identifier):
#     """
#     Wrapper function for retriving related 'indsats' by id.
#     LORA:   indsats
#     CRM:    aftale
#
#     :param identifier:  Entity id (Type: uuid) for owner reference
#                         Owner is a contact (bruger / organisation)
#     :return:            Returns OIO rest object
#     """
#
#     resource = resources.get("indsats")
#
#     # Check if the option corresponds with any switch key
#     if not resource:
#         return False
#
#     # Call GET request function
#     query = get_request(
#         resource=resource,
#         indsatsmodtager=identifier
#     )
#
#     # Check if a result was returned
#     if not query:
#         return False
#
#     # Reference uuid
#     reference = query[0]
#
#     # Check for entities with more than one result
#     if len(query) > 1:
#         print("AFTALE: {}".format(query))
#
#     return fetch_entity("indsats", reference)
#
#
# def fetch_entity(option, identifier):
#     """
#     Wrapper function for performing a GET request
#
#     :param option:      Resource key for using the resources switch
#     :param identifier:  Object identifier (Type: uuid)
#     :return:
#     """
#
#     resource = resources.get(option)
#
#     # Check if the option corresponds with any switch key
#     if not resource:
#         return False
#
#     # Call GET request function
#     query = get_request(
#         resource=resource,
#         uuid=identifier)
#
#     # Check if a result was returned
#     if not query:
#         return False
#
#     # If the list contains only 1 object
#     # Return the object instead of a list
#     if len(query) is 1:
#         return query[0]
#
#     # Return list of objects
#     return query
