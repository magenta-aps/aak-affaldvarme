import pymssql

from service_clients import report_error
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
        report_error(str(e))
        raise
    return cnxn
