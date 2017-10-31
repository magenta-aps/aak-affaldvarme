from arosia_sql import (ACCOUNT_SQL, CONTACT_SQL, KONTAKTROLLE_SQL,
                        KUNDEAFTALE_SQL, PLACERETMATERIEL_SQL)
from mox_arosia import (handle_account, handle_contact, handle_kontaktrolle,
                        handle_kundeaftale, handle_placeretmateriel)
from services import connect, report_error

# Contains a map of Arosia Contact UUIDs to LoRa bruger and organisation UUIDs
CONTACT_MAP = {}
# Contains a map of Arosia Account UUIDs to LoRa interessefællesskab UUIDs
ACCOUNT_MAP = {}
# Contains a map of Arosia Kundeaftale UUIDs to a list of their associated
# products as LoRa Klasse UUIDs
AFTALE_PRODUCT_MAP = {}

"""
Contains functions for performing an initial import of all relevant data in
AROSia and inserting in LoRa

We use internal caches of UUIDs of inserted items, to save ourselves from 
having to repeatedly perform lookups in LoRa when relating data.
"""


def import_contact(connection):
    """
    Fetches all 'contact' objects from AROSia and inserts in LoRa, while
    updating the internal cache
    """
    cursor = connection.cursor(as_dict=True)
    cursor.execute(CONTACT_SQL)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_contact(row)
        contact_id = row['ContactId']
        if lora_id and contact_id:
            CONTACT_MAP[contact_id] = lora_id
        else:
            report_error('Unable to import contact', error_object=row)
            continue


def import_account(connection):
    """
    Fetches all 'account' objects from AROSia and inserts in LoRa, while
    updating the internal cache
    """
    cursor = connection.cursor(as_dict=True)
    cursor.execute(ACCOUNT_SQL)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_account(row)
        account_id = row['AccountId']
        if lora_id and account_id:
            ACCOUNT_MAP[account_id] = lora_id
        else:
            report_error('Unable to import account', error_object=row)
            continue


def import_kontaktrolle(connection):
    """
    Fetches all 'kontaktrolle' objects from AROSia and inserts in LoRa, using
    the cache where relevant
    """
    cursor = connection.cursor(as_dict=True)
    cursor.execute(KONTAKTROLLE_SQL)
    rows = cursor.fetchall()

    for row in rows:
        contact_id = row['ava_Kontakt']
        account_id = row['ava_Kundeforhold']

        contact = CONTACT_MAP.get(contact_id)
        account = ACCOUNT_MAP.get(account_id)
        if not account or not contact:
            report_error('Unknown contact_id ({0}) or account_id ({1})'.format(
                contact_id, account_id))
            continue

        lora_id = handle_kontaktrolle(row, contact, account)
        if not lora_id:
            report_error('Unable to import kontaktrolle', error_object=row)
            continue


def import_placeretmateriel(connection):
    """
    Fetches all 'placeretmateriel' objects from AROSia and inserts in LoRa,
    using and updating the cache where relevant
    """
    cursor = connection.cursor(as_dict=True)
    cursor.execute(PLACERETMATERIEL_SQL)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_placeretmateriel(row)
        aftale_id = row.get('ava_Kundeaftale')

        if lora_id and aftale_id:
            product_list = AFTALE_PRODUCT_MAP.setdefault(aftale_id, [])
            product_list.append(lora_id)
        else:
            report_error('Unable to import placeretmateriel', error_object=row)
            continue


def import_kundeaftale(connection):
    """
    Fetches all 'kundeaftale' objects from AROSia and inserts in LoRa,
    using the cache where relevant
    """
    cursor = connection.cursor(as_dict=True)
    cursor.execute(KUNDEAFTALE_SQL)
    rows = cursor.fetchall()

    for row in rows:
        account_id = row.get('ava_kundeforhold')
        account = ACCOUNT_MAP.get(account_id)

        aftale_id = row.get('ava_kundeaftaleId')
        products = AFTALE_PRODUCT_MAP.setdefault(aftale_id, [])

        lora_id = handle_kundeaftale(row, account, products)

        if not lora_id:
            report_error('Unable to import kundeaftale', error_object=row)
            continue


def import_all(connection):
    """
    Given a database connection, performs insertions of all relevant AROSia
    data into LoRa
    """
    import_contact(connection)
    import_account(connection)
    import_kontaktrolle(connection)
    import_placeretmateriel(connection)
    import_kundeaftale(connection)


if __name__ == '__main__':
    from mssql_config import username, password, server, database

    connection = connect(server, database, username, password)
    import_all(connection)
