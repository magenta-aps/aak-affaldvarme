# encoding: utf-8
# import pyodbc

import pymssql

from ee_sql import CUSTOMER_SQL
from ee_oio import create_organisation, create_bruger, create_indsats
from ee_oio import create_interessefaellesskab, create_organisationfunktion
from ee_oio import lookup_bruger, lookup_organisation

# Definition of strings used for Klassifikation URNs

VARME = "Varme"
KUNDE = "Kunde"
LIGESTILLINGSKUNDE = "Ligestillingskunde"


def create_customer(id_number, key, name, phone="", email="",
                    mobile="", fax="", note=""):
        if is_cvr(id_number):
            result = create_organisation(
                id_number, key, name, phone, email, mobile, fax, note
            )
        elif is_cpr(id_number):
            # This is a CPR number
            result = create_bruger(
                id_number, key, name, phone, email, mobile, fax, note
            )
        else:
            print("Forkert CPR/SE-nr for {0}: {1}".format(
                name, id_number)
            )
            # Invalid customer
            return None

        if result:
            return result.json()['uuid']


def lookup_customer(id_number):
    if is_cpr(id_number):
        return lookup_bruger(id_number)
    elif is_cvr(id_number):
        return lookup_organisation(id_number)


def create_customer_role(customer_number, customer_uuid,
                         customer_relation_uuid, role):
    "Create an OrgFunktion from this info and return UUID"
    result = create_organisationfunktion(
        customer_number,
        customer_uuid,
        customer_relation_uuid,
        role
    )

    if result:
        return result.json()['uuid']


def create_customer_relation(customer_number, customer_relation_name,
                             customer_type):
    "Create an Interessefællesskab from this info and return UUID"
    result = create_interessefaellesskab(customer_number,
                                         customer_relation_name,
                                         customer_type)
    if result:
        return result.json()['uuid']


def create_agreement(name, agreement_type, no_of_products, invoice_address,
                     address, start_date, end_date, location,
                     customer_role_uuid):
    "Create an Indsats from this info and return UUID"
    result = create_indsats(name, agreement_type, no_of_products,
                            invoice_address, address, start_date, end_date,
                            location, customer_role_uuid)
    if result:
        return result.json()['uuid']


def get_products_for_location(location):
    # TODO Get locations for this customer ID from the Forbrugssted table
    return []


def create_product(name, identification, agreement, address,
                   installation_type, meter_number):
    pass

# CPR/CVR helper function


def cpr_cvr(val):
    if type(val) == float:
        val = str(int(val))
        if not (8 <= len(val) <= 10):
            pass
        if len(val) == 9:
            val = '0' + val
    return val


def is_cpr(val):
    return len(val) == 10 and val.isdigit()


def is_cvr(val):
    return len(val) == 8 and val.isdigit()


def connect(server, database, username, password):
    driver1 = '{SQL Server}'
    driver2 = '{ODBC Driver 13 for SQL Server}'
    cnxn = None
    try:
        cnxn = pymssql.connect(server=server, user=username,
                               password=password, database=database)
    except Exception as e:
        print(e)
        raise
    return cnxn


def import_all(connection):
    # cursor = connection.cursor(as_dict=True)
    # cursor.execute(CUSTOMER_SQL)
    # rows = cursor.fetchall()
    import csv
    reader = csv.DictReader(open('Kunde.csv', 'r'))
    rows = [r for r in reader]
    n = 0
    ligest_persons = 0
    print("Importing {} rows...".format(len(rows)))
    for row in rows:
        # Lookup customer in LoRa - insert if it doesn't exist already.

        id_number = cpr_cvr(float(row['PersonnrSEnr']))
        ligest_personnr = cpr_cvr(float(row['LigestPersonnr']))
        customer_number = str(int(float(row['Kundenr'])))

        customer_uuid = lookup_customer(id_number)

        if not customer_uuid:
            new_customer_uuid = create_customer(
                id_number,
                customer_number,
                row['KundeNavn'],
                row['Telefonnr'],
                row['EmailKunde'],
                row['MobilTlf']
            )

            if new_customer_uuid:
                # New customer created
                customer_uuid = new_customer_uuid
                n += 1
            else:
                # No customer created or found.
                continue

        # Create customer relation
        # NOTE: In KMD EE, there's always one customer relation for each row in
        # the Kunde table.
        cr_name = "<Varme + adresse fra SP>"
        cr_type = VARME  # Always for KMD EE
        cr_uuid = create_customer_relation(customer_number, cr_name, cr_type)

        assert(cr_uuid)

        # This done, create customer roles & link customer and relation
        role_uuid = create_customer_role(customer_number, customer_uuid,
                                         cr_uuid, "Kunde")
        assert(role_uuid)

        # Now handle partner/roommate, ignore empty CPR numbers
        if len(ligest_personnr) > 1:

            ligest_uuid = lookup_customer(ligest_personnr)

            if not ligest_uuid:
                new_ligest_uuid = create_customer(
                    ligest_personnr, customer_number, row['KundeNavn']
                )
                if new_ligest_uuid:
                    ligest_uuid = new_ligest_uuid
                    ligest_persons += 1

            if ligest_uuid:
                create_customer_role(
                    customer_number, ligest_uuid, cr_uuid, "Ligestillingskunde"
                )

        # TODO: Create agreement
        name = 'Fjernvarmeaftale'
        agreement_type = VARME
        invoice_address = "TODO: Lookup in CRM?"
        address = "TODO: Get from forbrugssted"
        start_date = row['Tilflytningsdato']
        end_date = row['Fraflytningsdato']

        # There is always one agreement for each location (Forbrugssted)
        # AND only one location for each customer record.

        customer_id = row['KundeID']

        location = row['ForbrugsstedID']  # TODO: Get BBR ID from Forbrugssted
        products = get_products_for_location(location)

        no_of_products = len(products)

        agreement_uuid = create_agreement(
            name, agreement_type, no_of_products, invoice_address, address,
            start_date, end_date, location, cr_uuid
        )
        assert(agreement_uuid)
        for p in products:
            name = "TODO: Fabrikat + Betegnel"
            identification = "TODO: Instalnummer"
            agreement = agreement_uuid
            address = "TODO: Get from forbrugssted"
            installation_type = VARME
            meter_number = "TODO: Maalernr"

            create_product(name, identification, agreement, address,
                           installation_type, meter_number)

    print("Fandt {0} primære kunder og {1} ligestillingskunder.".format(
        n, ligest_persons)
    )


if __name__ == '__main__':
    # from mssql_config import username, password, server, database

    connection = None  # connect(server, database, username, password)
    import_all(connection)

    # Test creation of virkning
    # print create_virkning()
    # Test creation of user
    # Mock data
    """
    cpr_number = "2511641919"
    name = "Carsten Agger"
    phone = "20865010"
    email = "agger@modspil.dk"
    note = "Test!"
    result = create_bruger(cpr_number, name, phone, email, note=note)
    print result, result.json()
    """
