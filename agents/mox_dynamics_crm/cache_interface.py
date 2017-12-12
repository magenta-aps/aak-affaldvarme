# -*- coding: utf-8 -*-

import logging
from pymongo import MongoClient

# Local settings
from settings import CACHE_HOST
from settings import CACHE_PORT
from settings import CACHE_USERNAME
from settings import CACHE_PASSWORD
from settings import CACHE_DATABASE

# Init logger
log = logging.getLogger(__name__)


def connect():

    client = MongoClient(
        host=CACHE_HOST,
        port=CACHE_PORT,
        authSource=CACHE_DATABASE,
        username=CACHE_USERNAME,
        password=CACHE_PASSWORD
    )

    return client[CACHE_DATABASE]


def insert(resource, payload):

    if not resource:
        return False

    if not payload:
        return False

    # Connect
    db = connect()

    # do stuff
    collection = db[resource]

    query = collection.insert(
        doc_or_docs=payload,
        check_keys=False
    )

    # Close db connection
    # collection.close()
    return query


def find(resource, uuid):

    if not resource:
        return False

    # Connect
    db = connect()

    # do stuff
    collection = db[resource]

    params = {
        "_id": uuid
    }

    query = collection.find_one(params)

    return query


def find_address(uuid):

    if not uuid:
        return False

    # Set resource
    resource = "addresses"

    return find(resource, uuid)


def store_address(payload):

    if not payload:
        return False

    # Set resource
    resource = "addresses"

    return insert(resource, payload)

if __name__ == "__main__":
    address = find_address("0a3f50c2-6335-32b8-e044-0003ba298018s")
    print(address)
