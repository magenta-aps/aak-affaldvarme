# -*- coding: utf-8 -*-

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

    # Read "config.ini"
    read_config = config.read("config.ini")

    # If file does not exist or cannot be read
    # Return False
    if not read_config:
        return False

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


def generate_config(section, **params):
    """
    Create configuration file
    """

    config[section] = params

    # Write config to file
    with open('config.ini', 'w') as file:
        config.write(file)

    print("Creating config.ini")
