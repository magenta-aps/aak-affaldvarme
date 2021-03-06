# -*- coding: utf-8 -*-

import sys
import string
import random
from configparser import ConfigParser

config = ConfigParser()


def get_config(section="DEFAULT"):
    """
    Helper function to get a configuration section from config.ini
    This file is required

    :param section: Name of the configuration section
                    (If empty, revert to default)
    :return:        Dictionary containing the config parameters
    """

    config_file = "config.ini"

    # Read "config.ini"
    read_config = config.read(config_file)

    # Exit if file does not exist
    if not read_config:
        sys.exit(
            "Configuration file {0} does not exist".format(config_file)
        )

    if section not in config:
        sys.exit(
            "Configuration section: {0} is missing".format(section)
        )

    return config[section]


def generate_password(length: int):
    """
    Helper function to generate a random password

    :param length: Password length as (integer)
    """

    if length < 5:
        length = 5

    password = ""

    chars = str.join(
        string.ascii_letters,
        string.digits
    )

    for _ in range(length):
        password += random.choice(chars)

    return password
