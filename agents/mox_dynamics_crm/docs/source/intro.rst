The Mox Dynamics CRM integration is a transport agent with the purpose of shipping data sets from OIO Rest (Lora)
to a Microsoft Dynamics CRM application (Azure cloud).

The application hosts an import and export function:

:Import:
    As the CRM application does not follow the OIO specification,
    data sets are converted to JSON formatted documents and stored in a local cache layer.

:Export:
    The pre-formatted documents are passed to the CRM application via Microsoft's Dynamics 365 Web Api,
    which is an OData (Open Data) protocol RESTful web interface.

    For more information on Microsoft's Web Api,
    please see https://msdn.microsoft.com/en-us/library/mt593051.aspx

    For more information on the OData protocol,
    please see http://www.odata.org



Installation
------------
Requirements:

* Python 3.5.4+
* Virtual environment


Install:

1) Navigate to application directory: ::

    # cd /opt/magenta/aak-affaldvarme/agents/mox_dynamics_crm


2) Create virtual environment: ::

    # python3 -m venv python-env
    # source python-env/bin/activate


3) Install (PyPi) dependencies: ::

    # pip install -r requirements



Configuration
-------------
The application entry point is a python (click) command line client: ``manage.py``

Running the client without any arguments will print the help file: ::

    (python-env) # python manage.py
    Usage: manage.py [OPTIONS] COMMAND [ARGS]...

      Mox Dynamics CRM manager cli. See 'help' for available options

    Options:
      --help  Show this message and exit.

    Commands:
      configure  Auto configure agent (Create config file) If...
      export     Build relations and export all objects to CRM...
      find       Retrieve contact by CPR id from cache.
      import     Import all OIO entities to the cache layer.
      token      Display current OAUTH token, use --generate...


:Note:
    Running `manage.py COMMAND --help` will provide additional information on the command.


The application requires a configuration (config.ini) file in order to run.
In order to bootstrap the configuration, issue the command: ::

    (python-env) # python manage.py configure

This will auto-generate a configuration file with randomly generated values.

:Note:
    In a production environment, the system values will have already been pre-configured.
    As such the generated config values should be replaced with the actual values.

The configuration must contain the following three sections: ::

    [DEFAULT]

    # UUID of the data set owner (organisation):
    parent_organisation = 1981c978-8c97-46f1-9e04-2e0a847ff322

    # OIO rest endpoint:
    oio_rest_endpoint = https://example.org



    [rethinkdb]

    # Database hostname
    db_host = localhost

    # Database port
    db_port = 28015

    # Database username
    db_user = cache_user

    # Database instance name
    db_name = cache_layer

    # Database password
    db_pass = ItbJIP8XiOXnaLuKgtFKzZsq

    # Database administrator password
    db_admin_pass = SDUhmZ4johFivVxxfAQgRVgM



    [ms_dynamics_crm]

    # The values for the CRM section must be generated
    # by the administrator of the Azure account for the CRM application

    # Authentication endpoint
    crm_oauth_endpoint = https://login.windows.net

    # Web Api base path
    crm_rest_api_path = /api/v8.2/

    # Application resource (by default the endpoint of the CRM application)
    crm_resource = https://example.crm4.dynamics.com

    # Application client identifier
    # This identifier is linked to an Azure user account
    crm_client_id = 34a7f8ac-2344-4741-86e0-a0bab46d218d

    # Generated password hash for the specified CRM application
    crm_client_secret = QXV0byBnZW5lcmF0aW5nIHNlY3JldCBmb3IgdGVzdGluZyBwdXJwb3Nlcw==

    # Azure tenant identifier
    crm_tenant = 34a7f8ac-2344-4741-86e0-a0bab46d218d


Additionally the cache layer can be configured automatically for development purposes.

Running the following command will setup the cache layer (e.g. setup user, create database/tables etc.): ::

    (python-env) # python manage.py configure --setup

:Note:
    Running configure will print minimal information to the terminal.
    However a log file (install.log) is dumped in the application directory for debugging purposes.



Usage
-----
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
