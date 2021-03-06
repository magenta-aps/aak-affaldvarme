MOX ServicePlatform CPR
***********************
Module that integrates with third party web services from Serviceplatformen.

:Author:
    Heini Leander Ovason <heini@magenta.dk>

API (with examples)
===================

*In order for this module to interact with Serviceplatformen you need valid 'Invocation context' UUIDs and a certificate.*

get_citizen()
-------------
*The function serves as a facade to ease interaction with Serviceplatformen's 'SF1520 - Udvidet person stamdata (lokal)' service.*

.. code-block:: python

    # -- coding: utf-8 --
    import json

    from services.udvidet_person_stam_data_lokal import get_citizen

    uuids = {
        'service_agreement': '42571b5d-6371-4edb-8729-1343a3f4c9b9',
        'user_system': '99478e20-68e6-41ff-b822-681fb69b8ff2',
        'user': 'e3108916-8ed9-4482-8045-7b46c83904b0',
        'service': '9883c483-d42f-424a-9a2a-94d1d200d294'
    }

    certificate = '/path/to/certificate.crt'

    cprnr = '0123456789'

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr
    )

    print(json.dumps(result))

`Example Output <https://pastebin.com/MSmk3YaB>`_


cprnr_subscription_service()
----------------------------
*The function serves as a facade to ease the interaction with Serviceplatformen's 'SF6002 - CPR Abonnement' service.
The type of operation you want to perform depends on the type of operation that is assigned to the operation parameter key when calling the function.*

.. code-block:: python

    # -- coding: utf-8 --
    import json

    from services.cpr_abonnement import cprnr_subscription_service

    uuids = {
        'service_agreement': '42571b5d-6371-4edb-8729-1343a3f4c9b9',
        'user_system': '99478e20-68e6-41ff-b822-681fb69b8ff2',
        'user': 'e3108916-8ed9-4482-8045-7b46c83904b0',
        'service': '9883c483-d42f-424a-9a2a-94d1d200d294'
    }

    certificate = '/path/to/certificate.crt'

    cprnr = '0123456789'

    # NOTE: Available operations are 'add' and 'remove'
    operations = ['add', 'remove']

    # NOTE: Add cprnr to subscription
    result = cprnr_subscription_service(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr,
        operation=operations[0]
    )

    print(json.dumps(result))

Example output: "ADDED"
