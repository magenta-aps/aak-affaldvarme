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


client = MongoClient(
    host=CACHE_HOST,
    port=CACHE_PORT,
    authSource=CACHE_DATABASE,
    username=CACHE_USERNAME,
    password=CACHE_PASSWORD
)

db = client[CACHE_DATABASE]


def insert(resource, payload):

    # do stuff
    collection = db[resource]

    query = collection.insert(
        doc_or_docs=payload,
        check_keys=False
    )

    return query


def update_or_insert(resource, payload):

    # Get id
    identifier = payload.get("_id")

    # do stuff
    collection = db[resource]

    query = collection.update(
        spec={"_id": identifier},
        document=payload,
        upsert=True,
        check_keys=False
    )

    return query


def find(resource, uuid):

    # do stuff
    collection = db[resource]

    params = {
        "_id": uuid
    }

    return collection.find_one(params)


def find_all(resource, params=None):

    # do stuff
    collection = db[resource]

    return collection.find(params)


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
    resource = "dawa"

    return insert(resource, payload)


def find_indsats(uuid):

    # Set resource
    resource = "indsats"

    # do stuff
    collection = db[resource]

    params = {
        "interessefaellesskab_ref": uuid
    }

    return collection.find_one(params)


def disconnect():
    return client.close()

if __name__ == "__main__":
    # address = find_address("0a3f50c2-6335-32b8-e044-0003ba298018s")
    # print(address)
    addresses = []
    for address in find_all("addresses"):
        addresses.append(address)

    print(len(addresses))
