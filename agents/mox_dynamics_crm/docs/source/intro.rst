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


