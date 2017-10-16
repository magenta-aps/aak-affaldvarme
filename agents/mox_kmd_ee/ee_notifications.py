
if __name__ == '__main__':

    import csv
    import datetime

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
