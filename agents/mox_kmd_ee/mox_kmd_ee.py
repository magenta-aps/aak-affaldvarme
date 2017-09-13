# encoding: utf-8
# import pyodbc

import pymssql
import datetime
import requests

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).

# TODO: Use authentication & real user UUID.
SYSTEM_USER = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# AVA-Organisation
AVA_ORGANISATION = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# API URL
BASE_URL = "http://agger"


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


def create_organisation(cvr_number, name, phone="", email="",
                        mobile="", fax="", note=""):
    virkning = create_virkning()
    organisation_dict = {
        "note": note,
        "attributter": {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": cvr_number,
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


def create_bruger(cpr_number, name, phone="", email="",
                  mobile="", fax="", note=""):
    virkning = create_virkning()
    bruger_dict = {
        "note": note,
        "attributter": {
            "brugeregenskaber": [
                {
                    "brugervendtnoegle": name,
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


KUNDE_SQL = """
SELECT [PersonnrSEnr]
      ,[KundeCprnr]
      ,[LigestPersonnr]
      ,[Tilflytningsdato]
      ,[Fraflytningsdato]
      ,[EmailKunde]
      ,[MobilTlf]
      ,[KundeID]
      ,[Kundenr]
      ,[Status]
      ,[Telefonnr]
      ,[FasadministratorID]
      ,[BoligadminID]
      ,[KundeNavn]
  FROM [KMD_EE].[dbo].[Kunde]
"""

# CPR/CVR helper function


def cpr_cvr(val):
    if type(val) == float:
        val = str(int(val))
        if not (8 <= len(val) <= 10):
            pass
        if len(val) == 9:
            val = '0' + val
    return val


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
    cursor.execute(KUNDE_SQL)
    rows = cursor.fetchall()
    n = 0
    persons = 0
    companies = 0
    ligest_persons = 0
    print("Importing {} rows...".format(len(rows)))
    for row in rows:
        # print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
        n += 1
        # TODO: Insert customer in Lora if it doesn't exist already.

        id_number = cpr_cvr(row['PersonnrSEnr'])
        ligest_personnr = cpr_cvr(row['LigestPersonnr'])

        if len(id_number) == 8:
            # This is a CVR number
            result = create_organisation(
                id_number,
                row['Kundenr'],
                row['KundeNavn'],
                row['Telefonnr'],
                row['EmailKunde'],
                row['MobilTlf']
            )
            companies += 1
        elif len(id_number) == 10:
            # This is a CPR number
            result = create_bruger(
                id_number,
                row['Kundenr'],
                row['KundeNavn'],
                row['Telefonnr'],
                row['EmailKunde'],
                row['MobilTlf']
            )
            persons += 1
        else:
            print("Forkert CPR/SE-nr for {0}: {1}".format(
                row['KundeNavn'], id_number)
            )

        if len(ligest_personnr) == 8:
            # We expect this not to happen.
            result = create_organisation(ligest_personnr, row['Kundenr'])
            ligest_persons += 1
            print(
                "Found LigestPerson who is company for customer {}".format(
                    row['KundeNavn']
                )
            )
        elif len(ligest_personnr) == 10:
            result = create_bruger(ligest_personnr, row['Kundenr'])
            ligest_persons += 1

    print("Fandt {0} primære kunder og {1} ligestillingskunder.".format(
        n, ligest_persons)
    )
    print("{0} personer og {1} virksomheder".format(persons, companies))


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
