Installation
============

Application requirements:

    * Python 3.5.4+
    * Virtual environment


System requirements:
    The mox dynamics crm application is using a cache layer,
    based "RethinkDB" (https://rethinkdb.com) for datastorage.

    This document describes a minimal setup of RethinkDB in the configuration section.
    A minimal setup is for development purposes only.

    TODO: Add configuration sample for a production environment



Install:

1) Navigate to application directory: ::

    # cd /opt/magenta/aak-affaldvarme/agents/mox_dynamics_crm


2) Create virtual environment: ::

    # python3 -m venv python-env
    # source python-env/bin/activate


3) Install (PyPi) dependencies: ::

    # pip install -r requirements
