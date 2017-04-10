from sandbox.sp_init import init_service


def main(endpoint_url, service_agreement_uuid, user_system_uuid, user_uuid, service_uuid, cert_filename):
    wsdl_url = 'CprSubsc/CprSubscriptionService.wsdl'
    binding_name = '{http://serviceplatformen.dk/xml/wsdl/soap11/CprSubscriptionService/1/}CprSubscriptionWebServiceBinding'
    client, service, inv_context = init_service(endpoint_url,
                                        service_agreement_uuid,
                                        user_system_uuid,
                                        user_uuid,
                                        service_uuid,
                                        cert_filename,
                                        wsdl_url,
                                        binding_name)


    response = service.AddMunicipalityCodeSubscription(InvocationContext=inv_context, MunicipalityCode='0751')

    #response = service.RemoveMunicipalityCodeSubscription(InvocationContext=inv_context, MunicipalityCode='0751')

    print response

