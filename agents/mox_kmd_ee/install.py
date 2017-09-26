#!/usr/bin/python3

import argparse
import os
import sys
from installutils import Config, Service, VirtualEnv

DIR = os.path.dirname(os.path.realpath(sys.argv[0]))

print('Installing service')

venv = VirtualEnv(os.path.join(DIR, 'python-env'))
venv.run('-m', 'pip', 'install', '-r', 'requirements.txt')

config = Config(os.path.join(DIR, "mssql_config.py"))
config.prompt([
    ('server', 'server'),
    ('database', 'database'),
    ('username', 'username'),
    ('password', 'password'),
])
config.save()

service = Service('mox_kmd_ee.sh', user='mox_kmd_ee')
service.install()
