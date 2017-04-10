import logging

import zeep
from requests import Session
from zeep import Transport


def init_service(endpoint_url,
                 service_agreement_uuid,
                 user_system_uuid,
                 user_uuid,
                 service_uuid,
                 cert_filename,
                 wsdl_url,
                 binding_name):

    handler = logging.StreamHandler()
    logging.getLogger("zeep.wsdl.bindings.soap").addHandler(handler)

    session = Session()
    session.cert = cert_filename
    transport = Transport(session=session)
    client = zeep.Client(wsdl=wsdl_url, transport=transport)
    service = client.create_service(binding_name, endpoint_url)

    service_agreement_uuid_obj = client.get_type('ns1:ServiceAgreenentUUIDtype')(service_agreement_uuid)
    user_system_uuid_obj = client.get_type('ns1:UserSystemUUIDtype')(user_system_uuid)
    user_uuid_obj = client.get_type('ns1:UserUUIDtype')(user_uuid)
    service_uuid_obj = client.get_type('ns1:ServiceUUIDtype')(service_uuid)

    InvContextType = client.get_type('ns1:InvocationContextType')
    inv_context = InvContextType(ServiceAgreementUUID=service_agreement_uuid_obj,
                                 UserSystemUUID=user_system_uuid_obj,
                                 UserUUID=user_uuid_obj,
                                 ServiceUUID=service_uuid_obj)

    return client, service, inv_context