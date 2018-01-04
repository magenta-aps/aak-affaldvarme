#!/bin/bash
# This script is useful for keeping track of progress when doing a full
# import from KMD EE. Basically, it spares you the work of starting psql
# and executing the SQL statements yourself.

while true
do
    echo -ne $(psql mox -U mox -c "select (select count(*) from bruger)+(select count(*) from organisation) as kunder")
    echo -ne " "
    echo -ne $(psql mox -U mox -c "select count(*) as kundeforhold from interessefaellesskab")
    echo -ne "\r"
    sleep 1
done
