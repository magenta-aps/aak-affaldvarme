# -*- coding: utf-8 -*-

import logging
import rethinkdb as r
from helper import get_config

# Get config
config = get_config("rethinkdb") 

def connect():
    return r.connect(
        host=config["db_host"],
        port=config["db_port"],
        db=config["db_name"],
        user=config["db_user"],
        password=config["db_pass"]
    )


def insert(resource, payload):

    # Init logger
    log = logging.getLogger(__name__)

    # Debug
    log.debug(payload)

    with connect() as connection:
        query = r.table(resource).insert(payload, conflict="error")
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=resource,
                query=run
            )
        )

        if run["errors"]:
            log.error(
                "Error inserting into {table}: {stack}".format(
                    table=resource,
                    stack=run
                )
            )

        return run


def set_admin_password(password):

    if not config:
        return False

    # Credentials
    params = {
        "password": password
    }

    with r.connect(
        host=config["db_host"],
        port=config["db_port"],
        db="rethinkdb"
    ) as connection:

        table = r.table("users")
        query = table.get("admin").update(params)
        update = query.run(connection)

        return update


def create_database(database_name):
    """
    Create application database
    The database name is "cache_layer" by default
    """

    if not config:
        return False

    with r.connect(
        host=config["db_host"],
        port=config["db_port"],
        password=config["db_admin_pass"],
    ) as connection:

        # list current databases
        query = r.db_list().run(connection)

        if database_name in query:
            print("Database already exists")
            return

        create = r.db_create(database_name).run(connection)
        return create

    print("Database created")


def create_user(username, password):
    """
    Create application user with limited access
    Access to cache database only
    """

    if not config:
        return False

    if not username or not password:
        print("Username/Password not provided")
        return False

    with r.connect(
        host=config["db_host"],
        port=config["db_port"],
        password=config["db_admin_pass"],
        db="rethinkdb"
    ) as connection:

        # Mapping
        table = "users"

        user = {
            "id": username,
            "password": password
        }

        existing_user = r.table(table).get(username).run(connection)

        if not existing_user:
            r.table(table).insert(user).run(connection)
            print("User has been created")
        else:
            print("User already exists")

        permissions = {
            "connect": True,
            "config": True,
            "read": True,
            "write": True
        }

        print("Granting permissions")
        grant = r.grant(username, permissions).run(connection)
        return grant


def create_tables(tables):

    with connect() as connection:

        # list current tables
        query = r.table_list().run(connection)

        for table in tables:
            if table not in query:
                # Create table
                r.table_create(table).run(connection)

                # Inform user
                print(
                    "Table created: {0}".format(table)
                )

            else:
                # Inform user
                print(
                    "{0} already exists".format(table)
                )

        print("All application tables created")
