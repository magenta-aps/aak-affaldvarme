# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from configparser import ConfigParser


def bootstrap_configuration(config_file="config.ini"):
    """
    Helper function to generate a sample config file

    :param config_file:     Name of the configuration file
                            (Default: config.ini)

    :return:                The filename is returned
                            if the file was created
    """

    # Create instance
    config = ConfigParser()

    # Read specified config file
    read_config = config.read(config_file)

    if read_config:
        raise RuntimeWarning(
            "Configuration already exists."
        )
        return

    # Generate config for oio
    generate_section_oio(config)

    # Generate config for cpr
    generate_section_sp_cpr(config)

    # Generate config for cvr
    generate_section_sp_cvr(config)

    with open(config_file, "w") as file:
        config.write(file)

    return config_file


def generate_section_oio(config):
    """

    :return:
    """

    config["oio"] = {
        "oio_rest_url": "https://example.org",
        "parent_organisation": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "do_verify_ssl_signature": "no"
    }

    return config


def generate_section_sp_cpr(config):
    """

    :return:
    """

    config["sp_cpr"] = {
        "service_agreement": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "user_system": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "user": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "service": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "certificate": "/path/to/service/certificate.crt"
    }

    return config


def generate_section_sp_cvr(config):
    """

    :return:
    """

    config["sp_cvr"] = {
        "service_agreement": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "user_system": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "user": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "service": "8137B87B-8CAB-4A2A-A976-48E26D4C44AB",
        "certificate": "/path/to/service/certificate.crt"
    }

    return config

if __name__ == "__main__":

    # Generate local config
    # For testing purposes only
    config = bootstrap_configuration()

    print(
        " * Configuration file created: {file}".format(
            file=config
        )
    )