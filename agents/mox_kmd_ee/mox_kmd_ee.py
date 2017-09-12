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

  
def create_bruger(cpr_number, name, phone, email, 
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
                    "urn": cpr_number,
                    "virkning": virkning
                }
            ]
        }
    }

    url = "{0}/organisation/bruger".format(BASE_URL)
    response = requests.post(url, json=bruger_dict)

    return response


KUNDE_SQL = """
SELECT TOP(1000) [PersonnrSEnr]
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
        val = unicode(int(val))
        assert(8 <= len(val) <= 10)
        if len(val) == 9:
            val = '0' + val
    return val


def connect(server, database, username, password):
    driver1= '{SQL Server}'
    driver2= '{ODBC Driver 13 for SQL Server}'
    cnxn = None
    try:
        cnxn = pymssql.connect(server=server, user=username,
                               password=password, database=database)
    except Exception as e:
        print e
        raise
    return cnxn


def import_all(connection):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(KUNDE_SQL)
    rows = cursor.fetchall()
    n = 0
    for row in rows:
        # print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
        n += 1
        # TODO: Insert customer in Lora if it doesn't exist already.

        # print row[u'KundeNavn'] + u':'
        """
        print '+++'
        for k in row:
            v = row[k]
	    if k == u'PersonnrSEnr':
	        print u"{0}:<{1}>".format(k, cpr_cvr(v))
        """
        result = create_bruger(
            row['PersonnrSEnr'],
            row['Kundenr'],
            row['KundeNavn'],
            row['Telefonnr'],
            row['EmailKunde'],
            row['MobilTlf'])
        # print result, result.json()

        # print '+++'
    print "Fandt {0} kunder.".format(n)


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
