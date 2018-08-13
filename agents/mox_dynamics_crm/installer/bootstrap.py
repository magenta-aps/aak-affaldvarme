# -*- coding: utf-8 -*-

import os
import logging
from configparser import ConfigParser
from uuid import uuid4
from base64 import b64encode
from socket import gethostname
from helper import generate_password

from .rethinkdb_interface import set_admin_password
from .rethinkdb_interface import create_database
from .rethinkdb_interface import create_user
from .rethinkdb_interface import create_tables


def setup_logger():
    # Configure install log
    loglevel = os.environ.get("LOG_LEVEL") or 10
    logfile = os.environ.get("LOG_FILE") or "install.log"

    # Create logger
    logger = logging.getLogger()

    # Set logger handler
    handler = logging.FileHandler(logfile)
    logger.addHandler(handler)

    # Set logger formatter
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    # Pass format to the handler
    handler.setFormatter(formatter)

    # Set loglevel
    logger.setLevel(loglevel)
    handler.setLevel(loglevel)

    return logger


def get_config(config_file="config.ini"):
    """
    Helper function to get a configuration section from config.ini
    This file is required

    :param section: Name of the configuration section
                    (If empty, revert to default)
    :return:        Dictionary containing the config parameters
    """

    config = ConfigParser()

    # Read "config.ini"
    config.read(config_file)

    return config


def auto_configure(config_file="configtest.ini"):

    # Init log
    log = setup_logger()

    # Get config
    config = get_config()

    if not config["DEFAULT"]:
        config["DEFAULT"] = generate_section_default()

    if "rethinkdb" not in config:
        config["rethinkdb"] = generate_section_rethinkdb()

    if "ms_dynamics_crm" not in config:
        config["ms_dynamics_crm"] = generate_section_ms_dynamics_crm()

    # Superseed default config filename
    # If passed in as an environment variable
    config_env = os.environ.get("AVA_MOX_CONFIG")

    if config_env:
        config_file = config_env

    with open(config_file, 'w') as file:
            config.write(file)

    log.info(
        "Configuration created"
    )


def generate_section_default():
    """
    oio_rest_endpoint
    :return:
    """

    # Init log
    log = setup_logger()

    # Info
    log.info(
        "Generating default config section"
    )

    oio_rest_endpoint = "https://{hostname}".format(
        hostname=gethostname()
    )

    log.info(
        "Set OIO Rest endpoint: {endpoint}".format(
            endpoint=oio_rest_endpoint
        )
    )

    return {
        "oio_rest_endpoint": oio_rest_endpoint,
        "parent_organisation": uuid4()
    }


def generate_section_rethinkdb():
    """

    :return:
    """

    # Init log
    log = setup_logger()

    # Info
    log.info(
        "Generating config section for cache layer"
    )

    return {
        "db_host": "localhost",
        "db_port": "28015",
        "db_name": "cache_layer",
        "db_user": "cache_user",
        "db_pass":  generate_password(24),
        "db_admin_pass": generate_password(24)
    }


def generate_section_ms_dynamics_crm():
    """

    :return:
    """

    # Init log
    log = setup_logger()

    # Info
    log.info(
        "Generating config section for MS Dynamics CRM"
    )

    secret = b64encode(
        b"Auto generating secret for testing purposes"
    )

    return {
        "crm_resource": "localhost",
        "crm_tenant": "28015",
        "crm_oauth_endpoint": "cache_layer",
        "crm_client_id": uuid4(),
        "crm_client_secret": secret.decode(),
        "crm_rest_api_path": "api/data/v8.2"
    }


def auto_setup_cache():
    """

    :return:
    """

    # Init log
    log = setup_logger()

    # Info
    log.info(
        "Running cache layer auto-setup"
    )

    # Get config
    import_config = get_config()
    config = import_config["rethinkdb"]

    # Set admin password
    try:
        log.info("Attempting to set administrator password")

        set_admin_password(
            password=config["db_admin_pass"]
        )

    except Exception as error:
        log.error("Unable to set admin password")
        log.error(error)

    # Create database
    try:
        log.info("Attempting to create database")

        create_database(config["db_name"])

    except Exception as error:
        log.error("Unable to create database")
        log.error(error)

    # Create application user
    try:
        log.info("Attempting to create application user")

        create_user(
            username=config["db_user"],
            password=config["db_pass"]
        )

    except Exception as error:
        log.error("Unable to create application user")
        log.error(error)

    # Tables that must be created
    tables = [
        "contacts",
        "ava_adresses",
        "access",
        "accounts",
        "ava_aftales",
        "ava_installations",
        "ava_kunderolles",
        "imports"
    ]

    try:
        log.info(
            "Attempting to create tables: {list}".format(
                list=tables
            )
        )

        create_tables(tables)

    except Exception as error:
        log.error("Unable to create tables")
        log.error(error)

    return True
