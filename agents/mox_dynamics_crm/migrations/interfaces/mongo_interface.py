# -*- coding: utf-8 -*-

from pymongo import MongoClient
from helper import get_config


# Configuration
config = get_config()
mongo = config["mongodb"]

# Create mongo client connection pool
client = MongoClient(
    host=mongo["db_host"],
    port=int(mongo["db_port"]),
    authSource=mongo["db_name"],
    username=mongo["db_user"],
    password=mongo["db_pass"]
)

# Database connection object
db = client[mongo["db_name"]]


def find_all(resource, **params):

    # Open connection pool socket
    collection = db[resource]

    return collection.find(params)


if __name__ == "__main__":
    find_all()
