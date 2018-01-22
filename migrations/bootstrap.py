# -*- coding: utf-8 -*-

from helper import get_config
from helper import generate_password
from helper import generate_config

from interfaces.rethinkdb_interface import set_admin_password
from interfaces.rethinkdb_interface import create_database
from interfaces.rethinkdb_interface import create_user
from interfaces.rethinkdb_interface import create_tables

import_config = get_config()


def auto_configure():

    config_section = "rethinkdb"

    if not import_config:

        # Generate config
        print("=== Create configuration ===")

        hostname = input(
            "Database hostname (default=localhost): "
        ) or "localhost"

        port = input(
            "Database port (default=28015): "
        ) or 28015

        database_name = input(
            "Database name (default=cache_layer): "
        ) or "cache_layer"

        username = input(
            "Username (default=cache_user): "
        ) or "cache_user"

        passwd_user = input(
            "Password: (autogenerate): "
        ) or generate_password(20)

        passwd_admin = input(
            "Administrator password: (autogenerate): "
        ) or generate_password(30)

        confirm = input(
            "Generate configuration ? (N/y)"
        ) or "N"

        if not confirm.lower() == "y":
            print("Configuration was not created, exiting")
            return None

        # Generate configuration
        generate_config(
            section=config_section,
            db_host=hostname,
            db_port=port,
            db_name=database_name,
            db_user=username,
            db_pass=passwd_user,
            db_admin_pass=passwd_admin

        )

        print("Configuration created")
        return

    section_exists = import_config[config_section]

    if section_exists:
        print("Configuration already exists, exiting")


def setup_cache():
    config = import_config["rethinkdb"]

    # Set admin password
    print("Attempting to set administrator password")
    try:
        set_admin_password(
            password=config["db_admin_pass"]
        )

    except Exception as error:
        print(error)
        print("Unable to set admin password")

    # Create database
    print("Attempting to create database")
    try:
        create_database(config["db_name"])

    except Exception as error:
        print(error)
        print("Unable to create database")

    # Tables that must be created
    tables = [
        "contacts",
        "ava_adresses",
        "access",
        "accounts",
        "ava_aftales",
        "ava_installations",
        "ava_kunderolles"
    ]

    # Create application user
    print("Attempting to create application user")

    try:
        create_user(
            username=config["db_user"],
            password=config["db_pass"]
        )
    except Exception as error:
        print(error)
        print("Unable to create application user")

    # Create tables
    print("Attempting to create application tables")

    try:
        create_tables(tables)

    except Exception as error:
        print(error)
        print("Unable to create tables")

    return True


def bootstrap():
    # Run autoconfigure
    auto_configure()

    run_setup = input(
        "Run autosetup to provision the database ? (N/y)"
    ) or "n"

    if not run_setup.lower() == "y":
        print("Not running autosetup, exiting")
        return

    # Run auto setup
    setup_cache()


if __name__ == "__main__":
    bootstrap()
