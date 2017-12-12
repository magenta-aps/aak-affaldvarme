# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient

# Local settings
from settings import CACHE_USERNAME
from settings import CACHE_PASSWORD
from settings import CACHE_DATABASE
from settings import CACHE_ROLES


def connect():
    return MongoClient()


# Create user
def create_database_user():
    """
    Connect to a newly created mongodb instance
    Create a database and an associated user with read and write permission
    """

    # Console message
    print(" * Creating user")

    # Client connect
    client = connect()

    # Change/Use database
    db = client[CACHE_DATABASE]

    # Send user creation command
    query = db.command(
        command="createUser",
        createUser=CACHE_USERNAME,
        pwd=CACHE_PASSWORD,
        roles=CACHE_ROLES
    )

    # Close database connection
    client.close()

    # Create status response
    print(" * User created!")
    print(" * Status: {0}".format(query))


if __name__ == "__main__":
    create_database_user()
