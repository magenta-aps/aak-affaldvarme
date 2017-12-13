import pymssql

from service_clients import report_error
# CPR/CVR helper function


def int_str(s):
    "Normalize numbers, e.g. customer or CPR numbers that are Float in MS SQL"
    return str(int(float(s)))


def cpr_cvr(val):
    assert(type(val) == str)
    val = str(int(val))
    if not (8 <= len(val) <= 10):
        raise RuntimeError("Not a CPR or CVR number")
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


def lookup_customer(id_number):
    if is_cpr(id_number):
        return lookup_bruger(id_number)
    elif is_cvr(id_number):
        return lookup_organisation(id_number)
