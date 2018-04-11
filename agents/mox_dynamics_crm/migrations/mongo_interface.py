# -*- coding: utf-8 -*-

from pymongo import MongoClient
from helper import get_config


# Configuration
config = get_config("mongodb")

# Create mongo client connection pool
client = MongoClient(
    host=config["db_host"] or None,
    port=int(config["db_port"]) or None,
    authSource=config["db_name"] or None,
    username=config["db_user"] or None,
    password=config["db_pass"] or None
)

# Database connection object
db_name = config["db_name"]
db = client[db_name]


def find_all(resource, **params):

    # Open connection pool socket
    collection = db[resource]

    return collection.find(params)
