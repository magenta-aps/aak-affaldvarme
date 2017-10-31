from arosia_oio import (lookup_account_arosia_id, lookup_contact_by_arosia_id,
                        lookup_products_by_aftale_id)
from arosia_sql import (ACCOUNT_SQL_RECENT, CONTACT_SQL_RECENT,
                        KONTAKTROLLE_SQL_RECENT, KUNDEAFTALE_SQL_RECENT,
                        PLACERETMATERIEL_SQL_RECENT)
from mox_arosia import (handle_account, handle_contact, handle_kontaktrolle,
                        handle_kundeaftale, handle_placeretmateriel)
from services import connect, report_error


def update_contact(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(CONTACT_SQL_RECENT)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_contact(row)
        if not lora_id:
            report_error('Unable to import contact', error_object=row)


def update_account(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(ACCOUNT_SQL_RECENT)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_account(row)
        if not lora_id:
            report_error('Unable to import account', error_object=row)


def update_kontaktrolle(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(KONTAKTROLLE_SQL_RECENT)
    rows = cursor.fetchall()

    for row in rows:
        contact_id = row['ava_Kontakt']
        account_id = row['ava_Kundeforhold']

        contact = lookup_contact_by_arosia_id(contact_id)
        account = lookup_account_arosia_id(account_id)
        if not account or not contact:
            report_error('Unknown contact_id ({0}) or account_id ({1})'.format(
                contact_id, account_id))
            continue

        lora_id = handle_kontaktrolle(row, contact, account)
        if not lora_id:
            report_error('Unable to import kontaktrolle', error_object=row)
            continue


def update_placeretmateriel(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(PLACERETMATERIEL_SQL_RECENT)
    rows = cursor.fetchall()

    for row in rows:
        lora_id = handle_placeretmateriel(row)

        if not lora_id:
            report_error('Unable to import placeretmateriel', error_object=row)
            continue


def update_kundeaftale(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(KUNDEAFTALE_SQL_RECENT)
    rows = cursor.fetchall()

    for row in rows:
        account_id = row.get('ava_kundeforhold')
        account = lookup_account_arosia_id(account_id)

        aftale_id = row.get('ava_kundeaftaleId')
        products = lookup_products_by_aftale_id(aftale_id)

        lora_id = handle_kundeaftale(row, account, products)

        if not lora_id:
            report_error('Unable to import kundeaftale', error_object=row)
            continue


def update_all(connection):
    update_contact(connection)
    update_account(connection)
    update_kontaktrolle(connection)
    update_placeretmateriel(connection)
    update_kundeaftale(connection)


if __name__ == '__main__':
    from mssql_config import username, password, server, database

    connection = connect(server, database, username, password)
    update_all(connection)
