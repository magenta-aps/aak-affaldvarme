
The Mox KMD EE integration is built in Python and is intended to be run
each time there's known to be updates in the database belonging to KMD's
Easy Energy product - normally once every day.

The application is split in a number of modules, each with their own
responsibility. The easiest way to understand these responsibilities is
to note that the integration was designed by first

* mapping the CRM system's object model to LoRa as described in the
  document `Modellering af AVAs objektmodeller i LoRa <https://alfresco.magenta-aps.dk/share/page/site/rammearkitektur/document-details?nodeRef=workspace://SpacesStore/56024c0f-3d79-4a7e-9f40-354c46385fb2>`_.
* analyzing the KMD EE object model and mapping it to the CRM system's
  model, as described in :doc:`mapning_fra_kmd_ee_til_crm`. 
* mapping the KMD EE object model to LoRa as implied by the two previous
  steps.

These design principles leads us to identify the following roles for the
modules involved in the integration:

* The :doc:`mox_kmd_ee` contains the main program and the overall import
  functions that interpret the KMD EE data and converts it to the CRM
  system's language and concepts.

* The :doc:`crm_utils` allows data manipulation (generally, CRUD) in terms
  of the CRM system's object model - it's possible to create customers,
  customer roles, customer relations, agreements, etc. The functions in
  this module map these concepts to the underlying implementation in
  LoRa - i.e., to Bruger, Organisation, Interessefaellesskab, and
  Indsats.

* The :doc:`ee_oio` contains functions that create OIO objects as well as
  auxiliary functions that allow the system to talk directly with LoRa.
  The object creation methods do not constitute a generalized LoRa API,
  on the contrary the signature of functions such as
  ``create_indsats`` etc. are completely bound to the needs and inherent
  interpretations of the EE-to-CRM integration.

* The :doc:`ee_data` handles all reading and writing of data between
  database and disk. It contains functions to *read* customer and
  installation data from the database, *store* them on disk, and
  *retrieve* them from disk as needed.

* The :doc:`ee_utils` contains a number of utility functions needed by
  the KMD EE integration - for connecting to the database, for
  formatting different type of customer numbers (which are stored as
  floats in the KMD EE database and must be converted to strings), and
  for looking up addresses.

* The :doc:`ee_sql` contains all of the SQL used for communicating with
  the database.

* The :doc:`service_clients` contains clients of third party services.
  These include DAR, Serviceplatformen (CVR) and error reporting/AMQP.

As has already been said, the MOX KMD EE program is intended to run once
daily, or at the frequency desired by the customer.

It should be used as described when invoking it with the ``-h`` flag: ::

    usage: mox_kmd_ee.py [-h] [--verbose] [--initial-import]

    Mox KMD EE main program.

    optional arguments:
      -h, --help        show this help message and exit
        --verbose         print helpful comments during execution
        --initial-import  only perform inital import

As may be guessed, the first time it is run, it *must* be run with the
``--initial-import`` flag. When using for notifications about changes,
this should *not* be specified.
