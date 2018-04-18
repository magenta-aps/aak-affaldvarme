# -*- coding: utf-8 -*-

from datetime import datetime
from logger import start_logging

# Interfaces
import cache_interface as cache
from migrations import mongo_interface as mongo


# Mapping of database collection/tables
mapping = {
    "contacts": {
        "source": "contact",
        "destination": "contacts"
    },
    "ava_adresses": {
        "source": "dawa",
        "destination": "ava_adresses"
    },
    "access": {
        "source": "dawa_access",
        "destination": "access"
    },
    "accounts": {
        "source": "interessefaellesskab",
        "destination": "accounts"
    },
    "ava_aftales": {
        "source": "indsats",
        "destination": "ava_aftales"
    },
    "ava_kunderolles": {
        "source": "organisationfunktion",
        "destination": "ava_kunderolles"
    },
    "ava_installations": {
        "source": "klasse",
        "destination": "ava_installations"
    },
}


def run():
    """
    Run migration from mongodb to rethinkdb
    """

    # Init logging
    start_logging(
        loglevel=10,
        logfile="migration.log"
    )

    # Set starttime
    start_time = datetime.now().replace(microsecond=0)

    print("=== Begin migration ===")

    for key in mapping:

        item = mapping[key]
        source = item["source"]
        destination = item["destination"]

        print(
            "* Migrating from {source} to {destination}".format(
                source=source,
                destination=destination
            )
        )
        process(source, destination)

    # Set endtime
    end_time = datetime.now().replace(microsecond=0)

    # Complex equation to calculate time spent
    time_passed = end_time - start_time

    print("Migration completed, time: {0}".format(time_passed))


def process(source, destination):

    # Store modified/converted items in new list
    converted_items = []

    # Returns cursor
    items = mongo.find_all(source)

    for item in items:

        item["id"] = item["_id"]
        item.pop("_id", None)

        # Add created timestamp
        item["created"] = str(datetime.now())

        # Add updated timestamp
        item["updated"] = str(datetime.now())

        converted_items.append(item)

    # Batch operation
    size = 200

    while len(converted_items) > 0:
        batch = converted_items[:size]
        converted_items = converted_items[size:]

        try:
            cache.insert(
                table=destination,
                payload=batch,
                conflict="update"
            )

        except Exception as error:
            print(batch)
            print(error)
