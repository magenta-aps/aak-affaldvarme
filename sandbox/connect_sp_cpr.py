import logging
import zeep
from requests import Session
from zeep.transports import Transport


def init_service(endpoint_url, service_agreement_uuid, user_system_uuid, user_uuid, service_uuid, cert_filename):
    handler = logging.StreamHandler()
    logging.getLogger("zeep.wsdl.bindings.soap").addHandler(handler)
    wsdl_url = 'CprSubsc/CprSubscriptionService.wsdl'

    session = Session()
    session.cert = cert_filename
    transport = Transport(session=session)
    client = zeep.Client(wsdl=wsdl_url, transport=transport)
    service = client.create_service(
        '{http://serviceplatformen.dk/xml/wsdl/soap11/CprSubscriptionService/1/}CprSubscriptionWebServiceBinding',
         endpoint_url)

    service_agreement_uuid_obj = client.get_type('ns1:ServiceAgreenentUUIDtype')(service_agreement_uuid)
    user_system_uuid_obj = client.get_type('ns1:UserSystemUUIDtype')(user_system_uuid)
    user_uuid_obj = client.get_type('ns1:UserUUIDtype')(user_uuid)
    service_uuid_obj = client.get_type('ns1:ServiceUUIDtype')(service_uuid)

    InvContextType = client.get_type('ns1:InvocationContextType')
    inv_context = InvContextType(ServiceAgreementUUID=service_agreement_uuid_obj,
                                 UserSystemUUID=user_system_uuid_obj,
                                 UserUUID=user_uuid_obj,
                                 ServiceUUID=service_uuid_obj)

    return service, inv_context


def main(endpoint_url, service_agreement_uuid, user_system_uuid, user_uuid, service_uuid, cert_filename):

    service, inv_context = init_service(endpoint_url, service_agreement_uuid, user_system_uuid, user_uuid, service_uuid, cert_filename)


    response = service.AddMunicipalityCodeSubscription(InvocationContext=inv_context, MunicipalityCode='0751')

    #response = service.RemoveMunicipalityCodeSubscription(InvocationContext=inv_context, MunicipalityCode='0751')

    print response



if __name__ == "__main__":
    endpoint_url = 'https://exttest.serviceplatformen.dk/service/CPRSubscription/CPRSubscription/1/'
    service_agreement_uuid = ''
    user_system_uuid = ''
    user_uuid = ''
    service_uuid = ''

    main(service_agreement_uuid, user_system_uuid, user_uuid, service_uuid)