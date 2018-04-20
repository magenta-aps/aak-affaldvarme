# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import click
import import_client
import export_client
import cache_interface as cache
import crm_interface as crm
import installer
from helper import get_config
from logger import start_logging

# Get config
config = get_config()

# If the SSL signature is not valid requests will print errors
# To circumvent this, warnings can be disabled for testing purposes
if config.getboolean("do_disable_ssl_warnings", "yes"):
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# In test mode log is written to a local logfile
# This is to prevent the test log from being collected for analysis
if config.getboolean("do_run_in_test_mode", "yes"):
    LOG_FILE = "debug.log"

def create_indexes(connection, table, ixlist=[]):
    existing_indexes = cache.r.table(table).index_list().run(connection)
    for ix in ixlist:
        if not ix in existing_indexes:
            cache.r.table(table).index_create(ix)
    # await all indexes to be ready on this table
    cache.r.table(table).index_wait().run(connection)


# Set logging
log = start_logging(config.getint("loglevel", fallback=20), LOG_FILE)

# wait for indexes to be ready
create_indexes(
    cache.connect(), 
    "ava_aftales", 
    ["interessefaellesskab_ref"]
)


@click.group()
def cli():
    """
    Mox Dynamics CRM manager cli.
    See 'help' for available options
    """
    pass


@cli.command(name="configure")
@click.option(
    "--setup/--no-setup",
    default=False,
    help="Automatically setup cache layer"
)
def configure(setup):
    """
    Auto configure agent
    (Create config file)

    If the --setup flag is passed,
    setup will be run, to install the cache layer
    """

    # Message user
    click.echo("Configure client")

    # Auto configure
    installer.auto_configure()

    if setup:
        installer.auto_setup_cache()

    click.echo("Client configured")


@cli.command(name="import")
def import_from_lora():
    """
    Import all OIO entities to the cache layer.
    For further information, please see the 'import_client'.
    """

    # Message user
    click.echo("Begin import from OIO to cache")

    # Run import
    import_client.run_import()


@cli.command(name="export")
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Run without sending data to CRM"
)
def export_to_crm(dry_run):
    """
    Build relations and export all objects to CRM
    For further information, please see the 'export_client'.
    """

    crm.DO_WRITE = not dry_run

    # Message user
    click.echo("Begin export from cache to CRM")

    # Run export
    export_client.export_everything()


@cli.command()
@click.option('--cpr', help='CPR number')
def find(cpr):
    """
    Retrieve contact by CPR id from cache.
    """

    result = cache.find_contact(cpr)

    if len(result) != 1:
        raise Exception("Several contacts found")

    to_json = json.dumps(result[0], indent=2)

    click.echo("Fetching contact from cache:")
    click.echo(to_json)


@cli.command()
@click.option(
    '--generate/--do-not-generate',
    default=False,
    help='Print token'
)
def token(generate):
    """
    Display current OAUTH token, use --generate to create new token.
    """

    if generate:
        crm.request_token()

    token = crm.get_token()
    click.echo("MS Dynamics OAUTH token:\n")
    click.echo("--- begin token ---")
    click.echo(token)
    click.echo("--- end token ---")


if __name__ == "__main__":
    cli()
