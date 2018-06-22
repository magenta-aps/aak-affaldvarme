Configuration
=============

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
    crm_rest_api_path = api/data/v8.2

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

    # On a newly created server/instance
    # A sample config file (containing dummy values) can be auto generated
    (python-env) # python manage.py configure

    # To setup the cache database
    # The following command will setup the database with the current configuration values
    # Note that the setup script assumes that the admin user has a blank password
    (python-env) # python manage.py configure --setup

:NOTE:
    The auto generation of the "config.ini" file is for development purposes only.
    In a production environment the responsability of creating e.g. credentials should
    lie with the admin/team in charge of the environment.

    Running configure will print minimal information to the terminal.
    However a log file (install.log) is dumped in the application directory for debugging purposes.
