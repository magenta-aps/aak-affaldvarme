
import os
import datetime
import pickle
import warnings

import settings

from mssql_config import username, password, server, database
from ee_utils import connect, int_str, cpr_cvr
from ee_sql import CUSTOMER_SQL, RELEVANT_TREF_INSTALLATIONS_SQL
from ee_oio import lookup_interessefaellesskab, lookup_bruger
from ee_oio import KUNDE, LIGESTILLINGSKUNDE
from mox_kmd_ee import lookup_customer, create_customer
from mox_kmd_ee import get_forbrugssted_address_uuid, VARME
from mox_kmd_ee import create_customer_relation, create_customer_role
from mox_kmd_ee import get_products_for_location, create_product
from mox_kmd_ee import create_agreement, get_alternativsted_address_uuid
from service_clients import report_error, fuzzy_address_uuid


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
    try:
        with open(CUSTOMER_RELATIONS_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


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

    # Lookup customer in LoRa - insert if it doesn't exist already.
    id_number = cpr_cvr(int_str(fields['PersonnrSEnr']))
    ligest_personnr = cpr_cvr(int_str(fields['LigestPersonnr']))
    customer_number = int_str(fields['Kundenr'])
    master_id = int_str(fields['KundeSagsnr'])

    # If customer relation already exists, please skip.
    if lookup_interessefaellesskab(customer_number):
        # print("This customer relation already exists:", customer_number)
        return

    # Now start handling customers etc.
    customer_uuid = lookup_customer(id_number)

    if not customer_uuid:
        new_customer_uuid = create_customer(
            id_number=id_number,
            key=customer_number,
            name=fields['KundeNavn'],
            master_id=master_id,
            phone=fields['Telefonnr'],
            email=fields['EmailKunde'],
            mobile=fields['MobilTlf'],
        )

        if new_customer_uuid:
            # New customer created
            customer_uuid = new_customer_uuid
        else:
            # No customer created or found.
            report_error("No customer created: %s %s" % (
                         fields['KundeNavn'],
                         fields['PersonnrSEnr']))
            return

    # Create customer relation
    # NOTE: In KMD EE, there's always one customer relation for each row in
    # the Kunde table.

    # Get Forbrugsstedadresse
    (forbrugssted_address,
     forbrugssted_address_uuid) = get_forbrugssted_address_uuid(fields)

    name_address = forbrugssted_address
    if not forbrugssted_address_uuid:
        report_error(forbrugssted_address)
    cr_name = "{0}, {1}".format(VARME, name_address)
    cr_type = VARME  # Always for KMD EE
    cr_address_uuid = forbrugssted_address_uuid
    cr_uuid = create_customer_relation(
        customer_number, cr_name, cr_type, cr_address_uuid
    )

    assert(cr_uuid)

    # This done, create customer roles & link customer and relation
    role_uuid = create_customer_role(customer_uuid, cr_uuid, KUNDE)
    assert(role_uuid)

    # Now handle partner/roommate, ignore empty CPR numbers
    if len(ligest_personnr) > 1:

        ligest_uuid = lookup_customer(ligest_personnr)

        if not ligest_uuid:
            new_ligest_uuid = create_customer(
                id_number=ligest_personnr,
                key=customer_number,
                name=fields['KundeNavn'],
                master_id=master_id
            )
            if new_ligest_uuid:
                ligest_uuid = new_ligest_uuid

        if ligest_uuid:
            create_customer_role(
                ligest_uuid, cr_uuid, LIGESTILLINGSKUNDE
            )

    # Create agreement
    name = 'Fjernvarmeaftale'
    agreement_type = VARME
    invoice_address = (fields['VejNavn'].replace(',-', ' ') +
                       ', ' + fields['Postdistrikt'])
    try:
        invoice_address_uuid = fuzzy_address_uuid(invoice_address)
    except Exception as e:
        invoice_address_uuid = None
        report_error(
            "Customer {1}: Unable to lookup invoicing address: {0}".format(
                str(e), id_number
            )
        )
    agreement_start_date = fields['Tilflytningsdato']
    agreement_end_date = fields['Fraflytningsdato']

    # There is always one agreement for each location (Forbrugssted)
    # AND only one location for each customer record.

    forbrugssted = fields['ForbrugsstedID']

    products = get_products_for_location(forbrugssted)

    no_of_products = len(products)

    product_uuids = []

    for p in products:
        meter_number = p['Målernr']
        meter_type = p['MaalerTypeBetegnel']
        product_uuid = create_product(
            name="{0}, {1} {2}".format(
                meter_number, p['Målertypefabrikat'], meter_type
            ),
            identification=p['InstalNummer'],
            installation_type=VARME,
            meter_number=meter_number,
            meter_type=meter_type,
            start_date=p['DatoFra'],
            end_date=p['DatoTil'],
            product_address=get_alternativsted_address_uuid(
                p['AlternativStedID']
            )
        )
        if product_uuid:
            product_uuids.append(product_uuid)

    agreement_name = "Varme, " + name
    agreement_uuid = create_agreement(
        agreement_name, agreement_type, no_of_products, invoice_address_uuid,
        agreement_start_date, agreement_end_date, forbrugssted, cr_uuid,
        product_uuids
    )
    assert(agreement_uuid)


def update_customer_record(fields, changed_values):
    "Update relevant LoRa objects with the specific changes."


if __name__ == '__main__':

    # Connect and get rows
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    new_values = read_customer_records(cursor)
    connection.close()

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

    # New customer relations - import along with agreements & products
    # Below, the unthreaded version
    """
    for k in new_keys:
        # New customer relations - import along with agreements & products
        # import_customer_record(new_values[k])
        import_customer_record(new_values[k])
    """
    # Threaded import
    from multiprocessing.dummy import Pool

    p = Pool(50)
    p.map(import_customer_record, [new_values[k] for k in new_keys])
    p.close()
    p.join()

    for k, changed_fields in changed_records.items():
        # Handle update of the specific changed fields.
        update_customer_record(old_values[k], changed_fields)

    # All's well that ends well
    store_customer_records(new_values)
