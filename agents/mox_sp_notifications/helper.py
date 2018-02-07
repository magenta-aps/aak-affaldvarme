# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from logging import getLogger
from datetime import datetime
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


def create_virkning():
    """
    Generates the required bi-temporal date fields,
    spanning from 'today' to 'infinity'.

    :return:    Return example:
                {
                    "virkning": {
                        "from": <start date>
                        "to: <end date, e.g. 'infinity'>
                    }
                }
    """

    return {
        'from': datetime.now().strftime('%Y-%m-%d'),
        'to': 'infinity'
    }


def start_logging(loglevel=10, logfile="debug.log"):
    """
    Function to autoconfigure log format and handler.
    This has been set to write to a specified log file,
    or to a local 'debug.log' logfile.

    :param loglevel:
    :param logfile:
    :return:
    """

    # Set logger name
    logger = getLogger()

    # Set logger handler
    handler = logging.FileHandler(logfile)
    logger.addHandler(handler)

    # Set logger formatter
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    handler.setFormatter(formatter)

    # Set loglevel
    logger.setLevel(loglevel)
    handler.setLevel(loglevel)

    # Return logger
    return logger
