'KMD EE import and update agent main program.'
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from ee_sql import CUSTOMER_SQL, TREFINSTALLATION_SQL
from ee_sql import ALTERNATIVSTED_ADRESSE_SQL
from ee_oio import KUNDE, LIGESTILLINGSKUNDE

from ee_utils import cpr_cvr, connect, int_str
from crm_utils import lookup_customer, create_customer, create_customer_role
from crm_utils import create_customer_relation, create_agreement
from crm_utils import lookup_customer_relation, create_product

from service_clients import get_address_uuid, fuzzy_address_uuid
from service_clients import report_error, access_address_uuid

# FIXME:
# The following lines allow us to import this file even where the certificates
# for ServicePlatformen aren't properly installed.
try:
    from serviceplatformen_cpr import get_cpr_data
except TypeError:
    def get_cpr_data(s):
        pass
    print("TODO: Fix this!")


# Definition of strings used for Klassifikation URNs

VARME = "Varme"


def get_products_for_location(forbrugssted):
    "Get locations for this customer ID from the Forbrugssted table"
    from mssql_config import username, password, server, database
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    cursor.execute(TREFINSTALLATION_SQL.format(forbrugssted))
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_forbrugssted_address_uuid(row):
    "Get UUID of the address for this Forbrugssted"

    vejnavn = row['ForbrStVejnavn']
    vejkode = row['Vejkode']
    postnr = row['Postnr']
    postdistrikt = row['ForbrStPostdistrikt']
    husnummer = str(row['Husnr'])
    if row['Bogstav']:
        husnummer += row['Bogstav']
    etage = row['Etage']
    doer = row['Sidedørnr']

    address_string1 = "{0} {1} {2}{3}".format(
        vejnavn, husnummer, etage, doer
    )
    address_string2 = "{0} {1}".format(postnr, postdistrikt)

    address_string = "{0}, {1}".format(address_string1.strip(),
                                       address_string2)

    address = {
        "vejkode": vejkode,
        "postnr": postnr
    }
    if etage:
        address["etage"] = etage
    if doer:
        address["dør"] = doer.strip('-')
    if husnummer:
        address["husnr"] = husnummer

    try:
        address_uuid = get_address_uuid(address)
    except Exception:
        try:
            address_uuid = fuzzy_address_uuid(address_string)
        except Exception as e:
            id_number = row['PersonnrSEnr']
            err_str = "Forbrugsadresse fejler for kunde {0}: {1}".format(
                id_number, address_string
            )
            report_error(err_str, error_stack=None, error_object=address)
            address_uuid = None
    return (address_string, address_uuid)


def get_alternativsted_address_uuid(alternativsted_id):
    "Get UUID of the address for this AlternativSted"
    if not alternativsted_id:
        return None
    from mssql_config import username, password, server, database
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    cursor.execute(ALTERNATIVSTED_ADRESSE_SQL.format(alternativsted_id))
    rows = cursor.fetchall()
    connection.close()

    if len(rows) != 1:
        # Send error to log:
        report_error(
            "Alternativt sted for {0} returnerer: {1}".format(
                alternativsted_id, str(rows)
            )
        )

        return None

    altsted_addr = rows[0]
    # Lookup addres
    vejnavn = altsted_addr['ForbrStVejnavn']
    vejkode = altsted_addr['VejkodeAltern']
    postnr = altsted_addr['Postnr']
    husnummer = str(altsted_addr['HusnrAltern'])
    bogstav = altsted_addr.get('Bogstav', None)
    etage = altsted_addr['EtageAltAdr']
    doer = altsted_addr['SidedørnrAltern']

    address = {
        "vejkode": vejkode,
        "postnr": postnr,
        "vejnavn": vejnavn
    }
    if etage:
        address["etage"] = etage
    if doer:
        address["dør"] = doer
    if husnummer:
        address["husnr"] = husnummer
    if bogstav:
        address["bogstav"] = bogstav

    try:
        address_uuid = access_address_uuid(address)
    except Exception as e:
        report_error(
            "Alternativ adresse fejler for alt. sted {0}: {1}".format(
                alternativsted_id, str(address)
            ), error_stack=None, error_object=address
        )
        address_uuid = None

    return address_uuid


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

        id_number = cpr_cvr(int_str(row['PersonnrSEnr']))
        ligest_personnr = cpr_cvr(int_str(row['LigestPersonnr']))
        customer_number = int_str(row['Kundenr'])
        master_id = int_str(row['KundeSagsnr'])

        customer_uuid = lookup_customer(id_number)

        if not customer_uuid:
            new_customer_uuid = create_customer(
                id_number=id_number,
                key=customer_number,
                name=row['KundeNavn'],
                master_id=master_id,
                phone=row['Telefonnr'],
                email=row['EmailKunde'],
                mobile=row['MobilTlf'],
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

        # If customer relation already exists, please skip.

        if lookup_customer_relation(customer_number):
            print("This customer relation already exists:", customer_number)
            continue

        # Get Forbrugsstedadresse
        (forbrugssted_address,
         forbrugssted_address_uuid) = get_forbrugssted_address_uuid(row)

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
                    name=row['KundeNavn'],
                    master_id=master_id
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
        invoice_address = (row['VejNavn'].replace(',-', ' ') +
                           ', ' + row['Postdistrikt'])
        try:
            invoice_address_uuid = fuzzy_address_uuid(invoice_address)
        except Exception as e:
            invoice_address_uuid = None
            report_error(
                "Customer {1}: Unable to lookup invoicing address: {0}".format(
                    str(e), id_number
                )
            )
        start_date = row['Tilflytningsdato']
        end_date = row['Fraflytningsdato']

        # There is always one agreement for each location (Forbrugssted)
        # AND only one location for each customer record.

        forbrugssted = row['ForbrugsstedID']

        products = get_products_for_location(forbrugssted)

        no_of_products = len(products)

        product_uuids = []

        for p in products:
            identification = p['InstalNummer']
            installation_type = VARME
            meter_number = p['Målernr']
            meter_type = p['MaalerTypeBetegnel']
            name = "{0}, {1} {2}".format(meter_number, p['Målertypefabrikat'],
                                         meter_type)
            start_date = p['DatoFra']
            end_date = p['DatoTil']
            product_address = None
            # Check alternative address
            alternativsted_id = p['AlternativStedID']
            if alternativsted_id:
                alternativ_adresse_uuid = get_alternativsted_address_uuid(
                    alternativsted_id
                )
                if alternativ_adresse_uuid:
                    product_address = alternativ_adresse_uuid

            product_uuid = create_product(
                name, identification, installation_type, meter_number,
                meter_type, start_date, end_date, product_address
            )
            if product_uuid:
                product_uuids.append(product_uuid)

        agreement_name = "Varme, " + name
        agreement_uuid = create_agreement(
            agreement_name, agreement_type, no_of_products,
            invoice_address_uuid, start_date, end_date, forbrugssted,
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
