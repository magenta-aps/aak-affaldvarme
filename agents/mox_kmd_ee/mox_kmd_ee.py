# encoding: utf-8
# import pyodbc

import pymssql
import datetime
import requests

from ee_sql import CUSTOMER_SQL

# TODO: Use authentication & real user UUID.
SYSTEM_USER = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# AVA-Organisation
AVA_ORGANISATION = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# API URL
BASE_URL = "http://agger"

# Definition of strings used for Klassifikation URNs

VARME = "Varme"
KUNDE = "Kunde"
LIGESTILLINGSKUNDE = "Ligestillingskunde"


def create_virkning(frm=datetime.datetime.now(),
                    to="infinity",
                    user=SYSTEM_USER,
                    note=""):
    virkning = {
        "from": str(frm),
        "to": str(to),
        "aktoerref": user,
        "aktoertypekode": "Bruger",
        "notetekst": note
    }

    return virkning


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


def create_agreement(name, agreement_type, no_of_products, invoice_adress,
                     address, start_date, end_date, property):
    # TODO Create an Indsats from this info and return UUID
    pass


def get_locations(customer_id):
    # TODO Get locations for this customer ID from the Forbrugssted table
    return []


def create_product(name, identification, agreement, address,
                   installation_type, meter_number):
    pass


def create_organisation(cvr_number, key, name, phone="", email="",
                        mobile="", fax="", note=""):
    virkning = create_virkning()
    organisation_dict = {
        "note": note,
        "attributter": {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": key,
                    "organisationsnavn": name,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
            "virksomhed": [
                {
                    "urn": "urn:{0}".format(cvr_number),
                    "virkning": virkning
                }
            ]
        }
    }

    url = "{0}/organisation/organisation".format(BASE_URL)
    response = requests.post(url, json=organisation_dict)

    return response


def create_interessefaellesskab(customer_number, customer_relation_name,
                                customer_type, note=""):
    virkning = create_virkning()
    interessefaellesskab_dict = {
        "note": note,
        "attributter": {
            "interessefaellesskabegenskaber": [
                {
                    "brugervendtnoegle": customer_number,
                    "interessefaellesskabsnavn": customer_relation_name,
                    "interessefaellesskabstype": customer_type,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "interessefaellesskabgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
        }
    }

    url = "{0}/organisation/interessefaellesskab".format(BASE_URL)
    response = requests.post(url, json=interessefaellesskab_dict)

    return response

def create_organisationfunktion(customer_number, 
                                customer_uuid,
                                customer_relation_uuid,
                                role, note=""):
    virkning = create_virkning()
    organisationfunktion_dict = {
        "note": note,
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "brugervendtnoegle": " ".join([role, customer_number]),
                    "funktionsnavn": role,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationfunktiongyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "urn": "urn:{0}".format(role),
                    "virkning": virkning
                }
            ],
            "tilknyttedeinteressefaellesskaber": [
                {
                    "uuid": customer_relation_uuid,
                    "virkning": virkning
                },
            ],
            "tilknyttedebrugere": [
                {
                    "uuid": customer_uuid,
                    "virkning": virkning
                },
            ]
        }
    }
    
    url = "{0}/organisation/organisationfunktion".format(BASE_URL)
    response = requests.post(url, json=organisationfunktion_dict)

    return response
    
    
def create_bruger(cpr_number, key, name, phone="", email="",
                  mobile="", fax="", note=""):
    virkning = create_virkning()
    bruger_dict = {
        "note": note,
        "attributter": {
            "brugeregenskaber": [
                {
                    "brugervendtnoegle": key,
                    "brugernavn": name,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "brugergyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
            "tilknyttedepersoner": [
                {
                    "urn": "urn:{0}".format(cpr_number),
                    "virkning": virkning
                }
            ]
        }
    }

    url = "{0}/organisation/bruger".format(BASE_URL)
    response = requests.post(url, json=bruger_dict)

    return response


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
    cursor = connection.cursor(as_dict=True)
    cursor.execute(CUSTOMER_SQL)
    rows = cursor.fetchall()
    n = 0
    ligest_persons = 0
    print("Importing {} rows...".format(len(rows)))
    for row in rows:
        # TODO: Insert customer in Lora if it doesn't exist already.

        id_number = cpr_cvr(row['PersonnrSEnr'])
        ligest_personnr = cpr_cvr(row['LigestPersonnr'])
        customer_number = str(int(row['Kundenr']))

        customer_uuid = create_customer(
            id_number,
            customer_number,
            row['KundeNavn'],
            row['Telefonnr'],
            row['EmailKunde'],
            row['MobilTlf']
        )

        if customer_uuid:
            # New customer created
            n += 1
        else:
            # No cake, no eating
            continue

        # TODO: create customer relation
        cr_name = "<Varme + adresse fra SP>"
        cr_type = VARME  # Always for KMD EE
        cr_uuid = create_customer_relation(customer_number, cr_name, cr_type)

        # TODO: This done, create customer roles & link customer and relation
        role_uuid = create_customer_role(customer_number, customer_uuid, cr_uuid, "Kunde")
        assert(role_uuid)

        # Now handle partner/roommate, ignore empty CPR numbers
        if len(ligest_personnr) > 1:
            ligest_uuid = create_customer(
                ligest_personnr, customer_number, row['KundeNavn']
            )
            if ligest_uuid:
                ligest_persons += 1
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

        # For now, assume one agreement for each property (Forbrugssted)

        customer_id = row['KundeID']

        for l in get_locations(customer_id):
            products = get_products_for_location(l)
            no_of_products = len(products)

            agreement_uuid = create_agreement(
                name, agreement_type, no_of_products, invoice_adress, address,
                start_date, end_date, l)

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
    from mssql_config import username, password, server, database

    connection = connect(server, database, username, password)
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
