# encoding: utf-8
# import pyodbc

import pymssql

# This is the SQL to fetch all customers from the KMD EE database.
# Only relevant fields (please).
KUNDE_SQL = """
SELECT TOP(5) [PersonnrSEnr]
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

        print row[u'KundeNavn'] + u':'
        print '+++'
        for k in row:
            v = row[k]
	    if k == u'PersonnrSEnr':
	        print u"{0}:<{1}>".format(k, cpr_cvr(v))
        print '+++'
    print "Fandt {0} kunder.".format(n)


if __name__ == '__main__':
    from mssql_config import username, password, server, database
    connection = connect(server, database, username, password)
    import_all(connection)
