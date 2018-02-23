# -*- coding: utf-8 -*-

from helper import get_config
from datetime import datetime
from logger import start_logging
from interfaces import mongo_interface as mongo
from interfaces import rethinkdb_interface as rethink


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
        "source": "interessefaelleskab",
        "destination": "accounts"
    },
    "ava_aftales": {
        "source": "indsats",
        "destination": "ava_aftales"
    },
    "ava_kunderolles": {
        "source": "organisationsfunktion",
        "destination": "ava_kunderolles"
    },
    "ava_installations": {
        "source": "klasse",
        "destination": "ava_installations"
    },
}


def run():
    """

    :return:
    """

    # Init logging
    start_logging(
        loglevel=20,
        logfile="logs/migration.log"
    )

    # Check config
    config = get_config()

    if not config:
        print(
            """
            Configuration is missing
            Please create a config.ini file
            (Alternatively you may run bootstrap.py to autoconfigure)
            """
        )
        return

    if not config["rethinkdb"]:
        print("Configuration for rethinkdb is missing, exiting")
        return

    if not config["mongodb"]:
        print("Configuration for mongodb is missing, exiting")
        return

    # Set starttime
    start_time = datetime.now().replace(microsecond=0)

    print("=== Begin migration ===")

    for key in mapping.keys():

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

        # Add created and updated fields
        item["created"] = str(datetime.now())
        item["updated"] = str(datetime.now())

        converted_items.append(item)

    # Batch operation
    size = 200

    while len(converted_items) > 0:
        batch = converted_items[:size]
        converted_items = converted_items[size:]

        try:
            rethink.insert(destination, batch)
        except Exception as error:
            print(batch)
            print(error)


if __name__ == "__main__":
    run()
