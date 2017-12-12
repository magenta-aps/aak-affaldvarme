
import os
import datetime
import pickle

from mssql_config import username, password, server, database
from ee_utils import connect
from ee_sql import CUSTOMER_SQL, RELEVANT_TREF_INSTALLATIONS_SQL


CUSTOMER_RELATIONS_FILE = 'var/customer_relations'


def read_customer_relations(cursor):
    """Read customer relations from database.

    Read all data regarding customers, customer roles and customer
    relationships and map them for easy lookup in case something
    changes. Basically, by creating a dictionary with customer
    number as key.
    """
    cursor.execute(CUSTOMER_SQL)
    rows = cursor.fetchall()
    customer_dict = {row['Kundenr']: row for row in rows}

    return customer_dict


def store_customer_relations(customer_relations):
    with open(CUSTOMER_RELATIONS_FILE, 'wb') as f:
        pickle.dump(customer_relations, f, protocol=4)


def retrieve_customer_relations():
    with open(CUSTOMER_RELATIONS_FILE, 'rb') as f:
        return pickle.load(f)


if __name__ == '__main__':

    # Connect and get rows
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)

    cr1 = read_customer_relations(cursor)

    # store_customer_relations(cr1)

    cr2 = retrieve_customer_relations()

    print('Comparison, cr1 == cr2:', cr1 == cr2)
    """
    s1 = set(cr1.items())
    s2 = set(cr2.items())

    diff = (s1 - s2) | (s2 - s1)
    """
    new_keys = set(cr2.keys()) - set(cr1.keys())
    lost_keys = set(cr1.keys()) - set(cr2.keys())

    print("new keys", new_keys)
    print("lost keys", lost_keys)
