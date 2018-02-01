#!/bin/sh

set -e

fail () {
    echo "\nInstallation failed\n" 1>&2
    exit 1
}

cd "$(dirname $0)"

sudo apt-get -qq update
sudo apt-get -qq install \
     python3 python3-pip python3-six python3-virtualenv python3-jinja2

cp -v db/db_structure.py mox/oio_rest/oio_rest

mox/install.sh || fail

agents/mox_kmd_ee/install.py || fail
