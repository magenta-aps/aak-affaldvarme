"""Miscellaneous utility functions specific to the KMD EE agent."""
import pymssql
import threading
import random
import time

from ee_sql import TREFINSTALLATION_SQL
from ee_sql import ALTERNATIVSTED_ADRESSE_SQL
from service_clients import get_address_uuid, fuzzy_address_uuid
from service_clients import report_error, access_address_uuid


VERBOSE = False


def say(*args):
    """Local utility to give output in verbose mode."""
    global VERBOSE

    if VERBOSE:
        print(*args)


# CPR/CVR helper functions

def int_str(s):
    """Normalize numbers, e.g. CPR numbers, that are Float in MS SQL."""
    return str(int(float(s)))


def cpr_cvr(val):
    """Normalize a customer ID (PersonnrSEnr) as either a CPR or CVR number.

    :param val: The customer ID to normalize as CPR or CVR.
    :type val: str
    :returns: str -- the normalized ID number.
    """
    assert(type(val) == str)
    val = str(int(val))
    if not (8 <= len(val) <= 10) and (len(val) > 1):
        raise RuntimeError("Not a CPR or CVR number:".format(val))
    if len(val) == 9:
        val = '0' + val
    return val


def is_cpr(val):
    """Determine if this is a CPR number."""
    return len(val) == 10 and val.isdigit()


def is_cvr(val):
    """Determine if this is a CVR number."""
    return len(val) == 8 and val.isdigit()


def hide_cpr(id_number):
    """Obfuscate CPR number."""
    if is_cpr(id_number):
        return '123456xxxx'
    else:
        return id_number


# connection id is a tuple including connection parms and thread id
connection_pool = {}


def close_mssql():
    for k in list(connection_pool):
        connection_pool.pop(k).close()


def connect(server, database, username, password):
    """pooled Connect to an MS SQL database."""
    conn_id = hash((
        threading.get_ident(), server,
        database, username, password,)
    )
    tries = 0
    while not connection_pool.get(conn_id, False):
        try:
            connection_pool[conn_id] = pymssql.connect(
                server=server, user=username,
                password=password, database=database
            )
        except Exception as e:
            tries = tries + 1
            if tries > 3:
                print(e)
                report_error(str(e))
                raise
            else:
                # try again - maybe too many in parallel
                time.sleep(random.random() * 2)
                continue
    return connection_pool[conn_id]


def get_products_for_location(forbrugssted):
    """Get locations for this customer ID from the Forbrugssted table."""
    from mssql_config import username, password, server, database
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    cursor.execute(TREFINSTALLATION_SQL.format(forbrugssted))
    rows = cursor.fetchall()
    # connection.close()
    return rows


def get_forbrugssted_address_uuid(row):
    """Get UUID of the address for this Forbrugssted."""
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
    address["etage"] = etage or ''
    address["dør"] = doer.strip('-') or ''
    address["husnr"] = husnummer.upper() or ''

    try:
        address_uuid = get_address_uuid(address)
    except Exception:
        try:
            address_uuid = fuzzy_address_uuid(address_string)
        except Exception:
            address_uuid = None
    return (address_string, address_uuid)


def get_alternativsted_address_uuid(alternativsted_id):
    """Get UUID of the address for this AlternativSted."""
    if not alternativsted_id:
        return None
    from mssql_config import username, password, server, database
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    cursor.execute(ALTERNATIVSTED_ADRESSE_SQL.format(alternativsted_id))
    rows = cursor.fetchall()
    # connection.close()

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
    address["etage"] = etage or ''
    address["dør"] = doer or ''
    address["husnr"] = husnummer.upper() or ''
    if bogstav:
        address["husnr"] += bogstav.strip().upper()

    try:
        address_uuid = access_address_uuid(address)
    except Exception:
        report_error(
            "Alternativ adresse fejler for alt. sted {0}: {1}".format(
                alternativsted_id, str(address)
            ), error_stack=None, error_object=address
        )
        address_uuid = None

    return address_uuid
