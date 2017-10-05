#!/bin/sh

cd $(dirname $0)

exec ./python-env/bin/python ./mox_kmd_ee.py "$@"
