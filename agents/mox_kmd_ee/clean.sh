#!/bin/bash

MOX_DIR=/home/agger/mox
VAR_DIR=/home/agger/aak-affaldvarme/agents/mox_kmd_ee/var

sudo service apache2 stop
$MOX_DIR/db/recreatedb.sh
sudo service apache2 start
rm -f $VAR_DIR/customer_relations
rm -f $VAR_DIR/installations


