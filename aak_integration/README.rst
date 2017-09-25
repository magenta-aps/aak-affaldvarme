This package (rather, collection of packages) contains integrations to
ServicePlatformen and other third party services used in the
Affald/Varme project.

Currently, there is only the ``serviceplatformen_cpr`` package
available. This must be configured as described in its own README-file.

Specifically, to use it you need a customer agreement with
Serviceplatformen and authentication details provided by them.

In order to retrieve the data associated with a single CPR number, use
the function ``get_cpr_data``: ::

    >>> from serviceplatformen_cpr import get_cpr_data
    >>> get_cpr_data('0123456789')


This command will return all CPR data for this number, if it exists.
