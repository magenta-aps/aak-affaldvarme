# -*- coding: utf-8 -*-

import logging
import rethinkdb as r
# from helper import get_config

# Temporary mapping
mapping = {
    "contact": "contacts",
    "dawa": "ava_adresses",
    "dawa_access": "access",
    "interessefaelleskab": "accounts",
    "indsats": "ava_aftales",
    "organisationsfunktion": "ava_kunderolles",
    "klasse": "ava_installations",
}

# Temporary configuration
# TODO: Provide config dynamically
config = {
    "db_name": "somedb",
    "db_pass": "somepassword",
    "db_user": "someuser",
    "db_host": "localhost",
    "db_port": 28015
}


def connect():

    return r.connect(
        host=config["db_host"],
        port=config["db_port"],
        db=config["db_name"],
        user=config["db_user"],
        password=config["db_pass"]
    )


# Init logger
log = logging.getLogger(__name__)


def insert(table, payload):

    if not table:
        return False

    # Debug
    log.debug(payload)

    with connect() as connection:
        query = r.table(table).insert(payload, conflict="error")
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        if run["errors"]:
            log.error(
                "Error inserting into {table}: {stack}".format(
                    table=table,
                    stack=run
                )
            )

        return run


def update_or_insert(table, payload):

    if not table:
        return False

    # Debug
    log.debug(payload)

    with connect() as connection:
        query = r.table(table).insert(payload, conflict="update")
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        if run["errors"]:
            log.error(
                "Error inserting into {table}: {stack}".format(
                    table=table,
                    stack=run
                )
            )

        return run


def find(table, uuid):

    if not table:
        return None

    with connect() as connection:
        query = r.table(table).get(uuid)
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        return run


def find_all(table):

    with connect() as connection:
        query = r.table(table)
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        result = []

        for item in run:
            result.append(item)

        return result


def find_address(uuid):

    if not uuid:
        return False

    # Set resource
    table = mapping.get("dawa")

    return find(table, uuid)


def store_address(payload):

    if not payload:
        return False

    # Set resource
    table = mapping.get("dawa")

    return insert(table, payload)


def find_indsats(uuid):

    # Set resource
    table = mapping.get("indsats")

    params = {
        "interessefaellesskab_ref": uuid
    }

    return find(table, params)
