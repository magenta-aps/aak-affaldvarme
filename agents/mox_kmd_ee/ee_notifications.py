
if __name__ == '__main__':

    import csv
    import os
    import glob
    import datetime
    import difflib

    from io import StringIO

    from mssql_config import username, password, server, database
    from ee_utils import connect
    from ee_sql import CUSTOMER_AND_FORBRUGSSTED_SQL, CUSTOMER_SQL
    from ee_sql import TREFINSTALLATION_ALL_SQL

    def write_csv(csv_file, cursor):
        with open(csv_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(cursor)

    # Obtain CSV files for "now"
    """
    connection = connect(server, database, username, password)
    cursor = connection.cursor()
    cursor.execute(CUSTOMER_AND_FORBRUGSSTED_SQL)
    # rows = cursor.fetchall()

    today = str(datetime.date.today())
    csv_filename = 'tmp/kunde_forbrugssted_{0}.csv'.format(today)
    write_csv(csv_filename, cursor)

    cursor.execute(TREFINSTALLATION_ALL_SQL)

    csv_filename = 'tmp/trefinstallation_{0}.csv'.format(today)
    write_csv(csv_filename, cursor)
    """

    customer_files = glob.glob('tmp/kunde_forbrugssted_*')
    latest_customer_file = max(customer_files)

    stored_customers = open(latest_customer_file, "r").read().split('\n')

    # Connect and get rows
    connection = connect(server, database, username, password)
    cursor = connection.cursor()
    cursor.execute(CUSTOMER_AND_FORBRUGSSTED_SQL)
    strio = StringIO()
    writer = csv.writer(strio)
    writer.writerow([i[0] for i in cursor.description])
    writer.writerows(cursor)

    customer_rows = strio.getvalue().split('\n')

    print(stored_customers[0])
    print(stored_customers[1])
    print(customer_rows[0])
    print(customer_rows[1])

    # Calculate diff
    print('Calculating diff ...')
    delta = difflib.ndiff(stored_customers, customer_rows)
    print(len(stored_customers))
    print(len(customer_rows))
    delta = [r for r in delta if not r.startswith('  ')]
    print('done!')

    print(len(delta))
