The MOX SP notifications is originally envisioned as a daemon which provides update notifications
to various listeners within the MOX/Lora ecosystem.

Currently the application compares data values of existing OIO objects against data sets from "Serviceplatformen".

:Note:
    For further information on this service,
    please see: https://www.serviceplatformen.dk

Changes found during the check will be compiled into updates which will be sent to the OIO Rest interface (Lora).

The application entry point is ``mox_sp_notifier.py`` which contains the task runner.
The task runner accepts two parameters, resource name and handler.

Next the task runner will perform a set of OIO rest queries in order to compile a list
of data objects for the given "resource" and passed into the given "handler".

Finally the handler will, provided that changes were retrieve from the SP services,
generate an update object which will be sent back to OIO rest to apply the changes.

Please note that we are using a specialised handler for each data set from the SP service.

.. code-block:: python

    # List of available tasks
    available_tasks = [
        ("bruger", cpr_handler),
        ("organisation", cvr_handler)
    ]

    # Run all tasks from the list
    for resource, handler in available_tasks:
        run_task(resource, handler)


:Note:
    For additional information on the inner workings of the handlers,
    please see the documentation found within the related code files for each handler.


Installation
------------
Requirements:
    Python 3.5.4+
    Virtual environment


1) Navigate to application directory: ::

    # cd /opt/magenta/aak-affaldvarme/agents/mox_sp_notifications


2) Create virtual environment: ::

    # python3 -m venv python-env
    # source python-env/bin/activate


3) Install (PyPi) dependencies: ::

    # pip install -r requirements


4) Install AAK integration packages: ::

    # cd /opt/magenta/aak-affaldvarme/aak-integration
    # pip install serviceplatformen_lib


5) Bootstrap configuration: ::

    # cd /opt/magenta/aak-affaldvarme/agents/mox_sp_notifications
    # python bootstrap.py



Configuration
-------------
Once step 5 has been completed, a "config.ini" sample file has been created.
Edit the config file and replace the auto-generated values with the actual vaules.

Example: ::

    [oio]
    # OIO rest endpoint:
    oio_rest_url = https://example.org

    # UUID of the data set owner (organisation):
    parent_organisation = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB

    # Verify SSL signature should be set to yes if a valid SSL certificate is in use,
    # otherwise it should be set to no to avoid warnings regarding the signature.
    do_verify_ssl_signature = no


    [sp_cpr]
    # Service access must be ordered from Kombit A/S,
    # For more information, please see https://serviceplatformen.dk)

    # Service UUID's:
    user_system = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    user = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    service_agreement = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    service = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB

    # Path to the service certificate
    certificate = /path/to/service/certificate.crt


    [sp_cvr]
    user_system = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    user = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    service_agreement = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    service = 8137B87B-8CAB-4A2A-A976-48E26D4C44AB
    certificate = /path/to/service/certificate.crt



Usage
-----
To begin the process, start the task runner: ::

    Virtual environment:
    # source python-env/bin/activate

    # Run application:
    (python-env) # python mox_sp_notifier.py


In the current stage of the application, logging cannot be configured.

The application will write to a local "debug.log" file.



Support
-------
For any issues related to this agent,
please do not hesitate to contact the author:

:Author:
    Steffen Park
    <steffen@magenta.dk>
