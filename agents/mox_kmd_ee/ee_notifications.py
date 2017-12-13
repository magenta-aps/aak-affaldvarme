
import os
import datetime
import pickle
import warnings

import settings

from mssql_config import username, password, server, database
from ee_utils import connect, int_str, lookup_customer
from ee_sql import CUSTOMER_SQL, RELEVANT_TREF_INSTALLATIONS_SQL
from ee_oio import lookup_interessefaellesskab
from service_clients import report_error


CUSTOMER_RELATIONS_FILE = 'var/customer_relations'


def report(errmsg):
    if settings.DEBUG:
        warnings.warn(errmsg)
    else:
        report_error(errmsg)


def read_customer_records(cursor):
    """Read customer relations from database.

    Read all data regarding customers, customer roles and customer
    relationships and map them for easy lookup in case something
    changes. Basically, by creating a dictionary with customer
    number as key.
    """
    cursor.execute(CUSTOMER_SQL)
    rows = cursor.fetchall()
    customer_dict = {int_str(row['Kundenr']): row for row in rows}

    return customer_dict


def store_customer_records(customer_relations):
    with open(CUSTOMER_RELATIONS_FILE, 'wb') as f:
        pickle.dump(customer_relations, f, protocol=4)


def retrieve_customer_records():
    with open(CUSTOMER_RELATIONS_FILE, 'rb') as f:
        return pickle.load(f)


def delete_customer_record(customer_number):
        "Purge relation along with customer roles, agreements and products."
        cr_uuid = lookup_interessefaellesskab(k)
        # This should exist provided everything is up to date!
        if not cr_uuid:
            report("Customer number {} not found.".format(customer_number))

        # Look up the customer roles and customers for this customer relation.

        # Delete the customer roles.

        # If the customers have no other customer roles, delete them.

        # Delete all agreements and products corresponding to this customer
        # relation.


def import_customer_record(fields):
    "Import a new customer record including relation, agreement, products."
    print("Importing", fields)


def update_customer_record(fields, changed_values):
    "Update relevant LoRa objects with the specific changes."
    print("Updating", fields, "with", changed_values)


if __name__ == '__main__':

    # Connect and get rows
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)

    new_values = read_customer_records(cursor)

    # store_customer_relations(cr1)

    old_values = retrieve_customer_records()

    print('Comparison, new_values == old_values:', new_values == old_values)

    new_keys = set(new_values.keys()) - set(old_values.keys())
    lost_keys = set(old_values.keys()) - set(new_values.keys())
    common_keys = set(new_values.keys()) & set(old_values.keys())

    print("new keys:", len(new_keys))
    print("lost keys:", len(lost_keys))
    print("common keys:", len(common_keys))

    # Now calculate diff between new values and old values.
    # Build a mapping between customer numbers and
    # dictionaries containing only the changed values.

    changed_records = {
        k: {
            f: v for f, v in new_values[k].items() if
            new_values[k][f] != old_values[k][f]
          } for k in common_keys if new_values[k] != old_values[k]
    }

    print("Number of changed records:", len(changed_records))

    # Handle notifications

    for k in lost_keys:
        # These records are no longer active and should be deleted in LoRa
        delete_customer_record(k)

    for k in new_keys:
        # New customer relations - import along with agreements & products
        import_customer_record(new_values[k])

    for k, changed_fields in changed_records.items():
        # Handle update of the specific changed fields.
        update_customer_record(old_values[k], changed_fields)
