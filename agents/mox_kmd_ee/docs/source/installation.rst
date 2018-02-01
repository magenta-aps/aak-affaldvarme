Installation
============

.. note:: All paths are given relative to the `AAK Affald/Varme <https://github.com/magenta-aps/aak-affaldvarme>`_ Github repository which you need to check out first.

Run the installer
-----------------

Navigate to the folder where the program is located
(``agents/mox_kmd_ee``) and enter the
following command:

    python3 install.py

When prompted, enter the credentials (server, database, username and
password) for the database you're going to talk to.

Edit the configuration
----------------------

Edit the ``settings.py`` file and enter the correct valus for
``SYSTEM_USER`` and ``AVA_ORGANISATION``. Note, ``SYSTEM_USER`` is only
given here as long as the integration runs without authentication.
Authentication is currently not supported in the KMD EE integration.

Also enter the ``BASE_URL`` for the OIO REST interface as well as the
variables ``CERTIFICATE_FILE`` and ``SP_UUIDS`` which contain our
credentials for accessing ServicePlatformen's CVR service.

Configure the CPR integration
-----------------------------

If this is the initial install of the ``aak-affaldvarme`` repository,
you need to configure the CPR client for ServicePlatformen (which gives
you access to data from the official Danish civil registry).

To configure:

* Navigate to the directory ``aak_integration/serviceplatformen_cpr`` 

* Copy the file ``.env.example`` to ``.env``

* Edit ``.env`` and provide the path to your ServicePlatformen
  certificate as well as the endpoints and UUIDs according to your
  service agreement with ServicePlatformen.

Run
---

Once everything is configured correctly, you may start the initial
import by navigating to the program directory as given above and enter
the command ::

    python-env/bin/python3 --verbose --initial-import

.. warning:: This will call up to a number of external services and is likely to take a long time.
