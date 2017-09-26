#/usr/bin/env bash

if [ ! -e python-env ]
then
    virtualenv -p $(which python3) python-env
fi

source python-env/bin/activate

pip install -r requirements.txt

if [ ! -f mssql_config.py ]
then
    cat << EOF > mssql_config.py
#encoding: utf-8
server = ''
database = ''
username = ''
password = ''
EOF
fi
