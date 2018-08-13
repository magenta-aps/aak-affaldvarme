"""This contains the functions that read KMD EE data from disk or database.

This module follows a simple naming convention:

The functions starting with "read" read data from the MS SQL database.

Functions starting with "store" write to files on disk, and files starting with
"retrieve" retrieves them from disk.
"""

import pickle
import os
import re
import json
import datetime

from ee_sql import CUSTOMER_SQL, RELEVANT_TREF_INSTALLATIONS_SQL
from ee_utils import int_str


LASTRUN_FILE = 'var/lastrun.json'
CUSTOMER_RELATIONS_FILE = 'var/customer_relations'
INSTALLATIONS_FILE = 'var/installations'
CRM_FAILED_CUSTOMER_NUMBERS_FILE = "var/kundenumre.txt"
CRM_FAILED_INSTALLATION_NUMBERS_FILE = "var/installationsnumre.txt"


""" LASTRUN """


def read_lastrun_dict():
    lastrun_dict = {"last_run": datetime.datetime.today(
    ).strftime("%Y-%m-%d")}
    # update default from file if it exists
    if os.path.exists(LASTRUN_FILE):
        with open(LASTRUN_FILE) as f:
            lastrun_dict.update(json.load(f))
    lastrun_dict.update({
            "last_run": datetime.datetime.strptime(
                lastrun_dict["last_run"],
                "%Y-%m-%d"
            )
    })
    return lastrun_dict


def write_lastrun_dict(lastrun_dict):
    lastrun_dict.update({"last_run": datetime.datetime.today(
    ).strftime("%Y-%m-%d")})
    with open(LASTRUN_FILE, "w") as f:
        f.write(json.dumps(lastrun_dict))


""" CUSTOMER RECORDS """


def has_customer_records():
    """Decide if the initial import of customer records has run."""
    return os.path.isfile(CUSTOMER_RELATIONS_FILE)


def read_customer_records(cursor, lastrun_dict):
    """Read customer relations from database.

    Read all data regarding customers, customer roles and customer
    relationships and map them for easy lookup in case something
    changes. Basically, by creating a dictionary with customer
    number as key.
    """
    cursor.execute(CUSTOMER_SQL.format(
        last_year=lastrun_dict["last_run"].year,
        last_month=lastrun_dict["last_run"].month,
        last_day=lastrun_dict["last_run"].day
    ))
    rows = cursor.fetchall()
    customer_dict = {int_str(row['Kundenr']): row for row in rows}

    return customer_dict


def store_customer_records(customer_relations):
    """Store customer records on disk.

    This is a simple, no-frills cache using the pickle module.
    """
    with open(CUSTOMER_RELATIONS_FILE, 'wb') as f:
        pickle.dump(customer_relations, f, protocol=4)


def retrieve_customer_records():
    """Retrieve customer records from disk."""
    try:
        with open(CUSTOMER_RELATIONS_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def get_crm_failed_customer_numbers():
    if os.path.exists(CRM_FAILED_CUSTOMER_NUMBERS_FILE):
        with open(CRM_FAILED_CUSTOMER_NUMBERS_FILE) as f:
            return set(re.findall("[0-9]+", f.read()))
    else:
        return set()


""" INSTALLATION RECORDS """


def read_installation_records(cursor, lastrun_dict):
    """Read relevant Tref installation records from database.

    Reads all relevant data about installations and meters.
    """
    cursor.execute(RELEVANT_TREF_INSTALLATIONS_SQL.format(
        last_year=lastrun_dict["last_run"].year,
        last_month=lastrun_dict["last_run"].month,
        last_day=lastrun_dict["last_run"].day
    ))
    rows = cursor.fetchall()
    data_dict = {int_str(row['InstalNummer']): row for row in rows}

    return data_dict


def store_installation_records(installations):
    """Store installation information in file for later use."""
    with open(INSTALLATIONS_FILE, 'wb') as f:
        pickle.dump(installations, f, protocol=4)


def retrieve_installation_records():
    """Read installation information from disk."""
    try:
        with open(INSTALLATIONS_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def get_crm_failed_installation_numbers():
    if os.path.exists(CRM_FAILED_INSTALLATION_NUMBERS_FILE):
        with open(CRM_FAILED_INSTALLATION_NUMBERS_FILE) as f:
            return set(re.findall("[0-9]+", f.read()))
    else:
        return set()
