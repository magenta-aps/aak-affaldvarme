#/usr/bin/env bash

if [ ! -e python-env ]
then
    virtualenv -p $(which python3) python-env
fi

source python-env/bin/activate

pip install -r requirements.txt
