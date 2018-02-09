# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import logging
from datetime import datetime
from configparser import ConfigParser


def get_config(section="DEFAULT"):
    """
    Helper function to get a configuration section from config.ini
    TODO: We may need to set default location to '/etc/mox/config.ini'

    This file is required.

    :param section: Name of the configuration section
                    (If empty, revert to default)

    :return:        Dictionary containing the config parameters
    """

    # Create instance
    config = ConfigParser()

    # Location of config file
    # With a local 'config.ini' fallback location
    config_file = "config.ini"

    # Read "config.ini"
    read_config = config.read(config_file)

    # Exit if file does not exist
    if not read_config:
        raise RuntimeError(
            "Configuration file does not exist"
        )

    if section not in config:
        error = "Configuration section: {0} is missing".format(section)
        raise RuntimeError(error)

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

    :param loglevel:    Log level value (Type: int)

    :param logfile:     Name and the full path to the log file.

                        Default is a local 'debug.log' file
                        Best practice would be to set the path
                        to the 'global' log location,
                        e.g.
                            /var/log/mox/<name>.log

    :return:            Returns a configured instance of the logging class
    """

    # Set logger name
    logger = logging.getLogger()

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
