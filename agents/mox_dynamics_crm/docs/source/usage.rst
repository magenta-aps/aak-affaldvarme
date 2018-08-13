Usage
=====

To begin importing data from OIO REST (Lora) to the cache layer,
issue the command: ::

    (python-env) # python manage.py import

To follow the process, you may watch the "debug.log" file which is dumped into the application directory on import.
By default log level is set to "INFO".

If the need for deeper logging information arises,
the level can be set to 10 (DEBUG) in the ``manage.py`` file: ::

    Line 35-36:

    # Set logging
    log = start_logging(20, LOG_FILE)


:Note:
    Options for specifying the log level through a config parameter will be added in the near future.

Similarly for exporting the cached documents to the CRM application can be invoked by issuing the command: ::

    (python-env) # python manage.py export


For debugging purposes it may be necessary to manually query the Microsoft Web Api,
for this a valid access token is needed.

To get a valid token, issue the command(s): ::

    # View the current access token:

    (python-env) # python manage.py token


    # If the token is expired,
    # you may generate a new token:

    (python-env) # python manage.py token --generate


Lastly, a helper function to quickly fetch a "contact" (OIO bruger) is provided.
Fetch a contact by "CPR ID" as follows: ::

    (python-env) # python manage.py find --cpr 1122334455

This will fetch a matching contact document from the cache layer.
The document contains meta data such as:

 * META: The OIO identifier
 * META: The CRM identifier
 * The CRM formatted document

For debugging purposes a web interface is available to visually access the documents in the cache layer.
However in a production environment this feature will be disabled by default as a security meassure.

To enable the web interface temporarily, please contact the server administrator / security officer.

:TODO:
    The author of this document has failed to add a detailed description on how to use the web interface.
    For more information contact the author and/or see the official documentation,

    RethinkDB website: https://rethinkdb.com


Support
-------
For any issues related to this agent,
please do not hesitate to contact the author:

:Author:
    Steffen Park
    <steffen@magenta.dk>
