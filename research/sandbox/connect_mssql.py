#encoding: utf-8
# import pyodbc

import pymssql

def connect(server, database, username, password):
    driver1= '{SQL Server}'
    driver2= '{ODBC Driver 13 for SQL Server}'
    print "Attempting connect..."
    #PORT=1433
    cnxn = None
    try:
        #cnxn = pyodbc.connect('DRIVER=' + driver1 + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        #cnxn = pyodbc.connect('DRIVER='+driver1+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
        #cnxn = pyodbc.connect(driver=driver1, server=server, database=database, username=username, password=password)
        cnxn = pymssql.connect(server=server, user=username, password=password, database=database)
    except Exception as e:
        print e
        return
    print "Connected"
    cursor = cnxn.cursor()
    # cursor.execute("select @@VERSION")
    cursor.execute("""select count(*) from Forbrug""")
    row = cursor.fetchone()
    while row:
        # print str(row[0]) + " " + str(row[1]) + " " + str(row[2])
        print " ".join(map(str, row))
        row = cursor.fetchone()


if __name__ == '__main__':
    server = u''
    database = u''
    username = u''
    password = u''
    connect(server, database, username, password)
