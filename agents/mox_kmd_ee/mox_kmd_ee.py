# encoding: utf-8
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import time

import pymssql

from serviceplatformen_cpr import get_cpr_data

from ee_sql import CUSTOMER_SQL, TREFINSTALLATION_SQL, FORBRUGSSTED_ADRESSE_SQL
from ee_oio import create_organisation, create_bruger, create_indsats
from ee_oio import create_interessefaellesskab, create_organisationfunktion
from ee_oio import create_klasse, lookup_bruger, lookup_organisation
from ee_oio import KUNDE, LIGESTILLINGSKUNDE

from ee_utils import cpr_cvr, is_cpr, is_cvr, connect

from service_clients import get_address_uuid, fuzzy_address_uuid, get_cvr_data
from service_clients import report_error

# Definition of strings used for Klassifikation URNs

VARME = "Varme"

# This is used to cache customer's addresses from SP for use when creating
# names for customer roles.


def create_customer(id_number, key, name, master_id, phone="", email="",
                    mobile="", fax="", note=""):

    if is_cvr(id_number):

        # Collect info from SP and include in call creating user.
        # Avoid getting throttled by SP
        try:
            company_dir = get_cvr_data(id_number)
        except Exception as e:
            # Retry *once* after sleeping
            time.sleep(40)
            try:
                company_dir = get_cvr_data(id_number)
            except Exception as e:
                report_error(
                    "CVR number not found: {0}".format(id_number)
                )
                return None

        name = company_dir['organisationsnavn']
        address_uuid = company_dir['dawa_uuid']
        company_type = company_dir['virksomhedsform']
        industry_code = company_dir['branchekode']
        address_string = "{0} {1}, {2}".format(
            company_dir['vejnavn'], company_dir['husnummer'],
            company_dir['postnummer']
        )

        result = create_organisation(
            id_number, key, name, master_id, phone, email, mobile, fax,
            address_uuid, company_type, industry_code, note
        )
    elif is_cpr(id_number):
        # This is a CPR number

        # Collect info from SP and include in call creating user.
        # Avoid getting throttled by SP
        try:
            person_dir = get_cpr_data(id_number)
        except Exception as e:
            report_error(traceback.format_exc())

            # Retry *once* after sleeping
            time.sleep(40)
            try:
                person_dir = get_cpr_data(id_number)
            except Exception as e:
                report_error(
                    "CPR number not found: {0}".format(id_number)
                )
                return None

        first_name = person_dir['fornavn']
        middle_name = person_dir.get('mellemnavn', '')
        last_name = person_dir['efternavn']

        # Address related stuff
        address = {
            "vejnavn": person_dir["vejnavn"],
            "postnr": person_dir["postnummer"]
        }
        if "etage" in person_dir:
            address["etage"] = person_dir["etage"].lstrip('0')
        if "sidedoer" in person_dir:
            address["dør"] = person_dir["sidedoer"].lstrip('0')
        if "husnummer" in person_dir:
            address["husnr"] = person_dir["husnummer"]

        try:
            address_uuid = get_address_uuid(address)
        except Exception as e:
            report_error(
                "Unable to lookup address for customer: {0}".format(
                    id_number
                ), error_stack=None, error_object=address
            )
            address_uuid = None

        # Cache address for customer relation
        address_string = "{0}, {1}".format(
            person_dir['standardadresse'], person_dir['postnummer']
        )
        gender = person_dir['koen']
        marital_status = person_dir['civilstand']
        address_protection = person_dir['adressebeskyttelse']

        result = create_bruger(
            id_number, key, name, master_id, phone, email, mobile, fax,
            first_name, middle_name, last_name, address_uuid, gender,
            marital_status, address_protection, note
        )
    else:
        report_error("Forkert CPR/SE-nr for {0}: {1}".format(
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


def create_customer_role(customer_uuid, customer_relation_uuid, role):
    "Create an OrgFunktion from this info and return UUID"
    result = create_organisationfunktion(
        customer_uuid,
        customer_relation_uuid,
        role
    )

    if result:
        return result.json()['uuid']


def create_customer_relation(customer_number, customer_relation_name,
                             customer_type, address_uuid):
    "Create an Interessefællesskab from this info and return UUID"
    result = create_interessefaellesskab(
        customer_number,
        customer_relation_name,
        customer_type,
        address_uuid
    )
    if result:
        return result.json()['uuid']


def create_agreement(name, agreement_type, no_of_products, invoice_address,
                     start_date, end_date, location,
                     customer_role_uuid, product_uuids):
    "Create an Indsats from this info and return UUID"
    result = create_indsats(name, agreement_type, no_of_products,
                            invoice_address, start_date, end_date,
                            location, customer_role_uuid, product_uuids)
    if result:
        return result.json()['uuid']


def get_products_for_location(connection, forbrugssted):
    "Get locations for this customer ID from the Forbrugssted table"
    cursor = connection.cursor(as_dict=True)
    cursor.execute(TREFINSTALLATION_SQL.format(forbrugssted))
    rows = cursor.fetchall()
    return rows


def get_forbrugssted_address_uuid(connection, forbrugssted, id_number):
    "Get UUID of the address for this Forbrugssted"
    cursor = connection.cursor(as_dict=True)
    cursor.execute(FORBRUGSSTED_ADRESSE_SQL.format(forbrugssted))
    rows = cursor.fetchall()

    # Hotfix:
    # Some lookups will return 0
    # Removing the assert as it breaks the import flow
    # TODO:
    # We must investigate the circumstances which cause this issue
    # In theory forbrugssted should not be returned as 0

    # assert(len(rows) == 1)

    # Hotfix:
    # Log if
    if len(rows) != 1:
        # Send error to log:
        report_error(
            "Forbrugssted for {0} returnerer: {1}".format(
                id_number, forbrugssted
            )
        )

        return None

    frbrst_addr = rows[0]
    # Lookup addres
    vejnavn = frbrst_addr['ForbrStVejnavn']
    vejkode = frbrst_addr['Vejkode']
    postnr = frbrst_addr['Postnr']
    postdistrikt = frbrst_addr['Postdistrikt']
    husnummer = str(frbrst_addr['Husnr'])
    if frbrst_addr['Bogstav']:
        husnummer += frbrst_addr['Bogstav']
    etage = frbrst_addr['Etage']
    doer = frbrst_addr['Sidedørnr']

    address_string = "{0} {1} {2} {3}, {4}".format(
        vejnavn, husnummer, etage, doer, postdistrikt
    )

    address = {
        "vejkode": vejkode,
        "postnr": postnr
    }
    if etage:
        address["etage"] = etage
    if doer:
        address["dør"] = doer
    if husnummer:
        address["husnr"] = husnummer

    try:
        address_uuid = get_address_uuid(address)
    except Exception as e:
        report_error(
            "Forbrugsadresse fejler for kunde {0}: {1}".format(
                id_number, address_string
            ), error_stack=None, error_object=address
        )
        address_uuid = None

    return (address_string, address_uuid)


def create_product(name, identification, installation_type, meter_number,
                   meter_type, start_date, end_date, product_address):
    "Create a Klasse from this info and return UUID"
    result = create_klasse(name, identification, installation_type,
                           meter_number, meter_type, start_date, end_date,
                           product_address)
    if result:
        return result.json()['uuid']


def import_all(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(CUSTOMER_SQL)
    rows = cursor.fetchall()
    # import csv
    # reader = csv.DictReader(open('Kunde.csv', 'r'))
    # rows = [r for r in reader]
    n = 0
    ligest_persons = 0
    print("Importing {} rows...".format(len(rows)))
    for row in rows:
        # Lookup customer in LoRa - insert if it doesn't exist already.

        id_number = cpr_cvr(float(row['PersonnrSEnr']))
        ligest_personnr = cpr_cvr(float(row['LigestPersonnr']))
        customer_number = str(int(float(row['Kundenr'])))
        master_id = row['KundeSagsnr']

        customer_uuid = lookup_customer(id_number)

        if not customer_uuid:
            new_customer_uuid = create_customer(
                id_number,
                customer_number,
                row['KundeNavn'],
                row['Telefonnr'],
                row['EmailKunde'],
                row['MobilTlf'],
                master_id
            )

            if new_customer_uuid:
                # New customer created
                customer_uuid = new_customer_uuid
                n += 1
            else:
                # No customer created or found.
                report_error("No customer created: %s %s" % (
                             row['KundeNavn'],
                             row['PersonnrSEnr']))
                continue

        # Create customer relation
        # NOTE: In KMD EE, there's always one customer relation for each row in
        # the Kunde table.

        # Get Forbrugsstedadresse
        forbrugssted = row['ForbrugsstedID']

        (forbrugssted_address,
         forbrugssted_address_uuid) = get_forbrugssted_address_uuid(
            connection,
            forbrugssted,
            id_number
        )

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
                    ligest_personnr, customer_number, row['KundeNavn']
                )
                if new_ligest_uuid:
                    ligest_uuid = new_ligest_uuid
                    ligest_persons += 1

            if ligest_uuid:
                create_customer_role(
                    ligest_uuid, cr_uuid, LIGESTILLINGSKUNDE
                )

        # Create agreement
        name = 'Fjernvarmeaftale'
        agreement_type = VARME
        invoice_address = row['VejNavn'] + ', ' + row['Postdistrikt']
        try:
            invoice_address_uuid = fuzzy_address_uuid(invoice_address)
        except Exception as e:
            report_error(
                "Customer {1}: Unable to lookup invoicing address: {0}".format(
                    str(e), id_number
                )
            )
        start_date = row['Tilflytningsdato']
        end_date = row['Fraflytningsdato']

        # There is always one agreement for each location (Forbrugssted)
        # AND only one location for each customer record.

        customer_id = row['KundeID']

        products = get_products_for_location(connection, forbrugssted)

        no_of_products = len(products)

        product_uuids = []

        for p in products:
            name = p['Målertypefabrikat'] + ' ' + p['MaalerTypeBetegnel']
            identification = p['InstalNummer']
            installation_type = VARME
            meter_number = p['Målernr']
            meter_type = p['MaalerTypeBetegnel']
            start_date = p['DatoFra']
            end_date = p['DatoTil']
            product_address = forbrugssted_address
            # TODO: Check alternative address!
            product_uuid = create_product(
                name, identification, installation_type, meter_number,
                meter_type, start_date, end_date, product_address
            )
            if product_uuid:
                product_uuids.append(product_uuid)

        agreement_uuid = create_agreement(
            name, agreement_type, no_of_products, invoice_address_uuid,
            start_date, end_date, forbrugssted,
            cr_uuid, product_uuids
        )
        assert(agreement_uuid)
    print("Fandt {0} primære kunder og {1} ligestillingskunder.".format(
        n, ligest_persons)
    )


if __name__ == '__main__':
    from mssql_config import username, password, server, database

    connection = connect(server, database, username, password)
    import_all(connection)
