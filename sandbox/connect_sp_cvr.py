import logging
import zeep
from requests import Session
from zeep.transports import Transport


def main(service_agreement_uuid, user_system_uuid, user_uuid, service_uuid):

    handler = logging.StreamHandler()
    logging.getLogger("zeep.wsdl.bindings.soap").addHandler(handler)

    wsdl_url = 'https://exttestwww.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
    endpoint_url ='https://exttest.serviceplatformen.dk/service/CVROnline/CVROnline/1'

    session = Session()
    session.cert = './magenta_ava_test_2017-03.crt'
    transport = Transport(session=session)
    client = zeep.Client(wsdl=wsdl_url, transport=transport)
    service = client.create_service('{http://rep.oio.dk/eogs/xml.wsdl/}CvrBinding', endpoint_url)

    service_agreement_uuid_obj = client.get_type('ns1:ServiceAgreenentUUIDtype')(service_agreement_uuid)
    user_system_uuid_obj = client.get_type('ns1:UserSystemUUIDtype')(user_system_uuid)
    user_uuid_obj = client.get_type('ns1:UserUUIDtype')(user_uuid)
    service_uuid_obj = client.get_type('ns1:ServiceUUIDtype')(service_uuid)

    InvContextType = client.get_type('ns1:InvocationContextType')
    inv_context = InvContextType(ServiceAgreementUUID=service_agreement_uuid_obj,
                                 UserSystemUUID=user_system_uuid_obj,
                                 UserUUID=user_uuid_obj,
                                 ServiceUUID=service_uuid_obj)

    client.set_ns_prefix('ns_oio_auth_code', 'http://rep.oio.dk/cpr.dk/xml/schemas/core/2005/03/18/')
    client.set_ns_prefix('ns_oio_street_and_zip', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2005/03/15/')
    client.set_ns_prefix('ns_oio_build_ident', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/')

    search_address_obj = getSearchAddressObj(client, '0751', 'Frydenlunds Alle')

    max_no_results_obj = client.get_type('ns0:MaximumNumberOfResultsType')(50)

    response = service.searchProductionUnit(InvocationContext=inv_context, SearchAddress=search_address_obj, maximumNumberOfResultsType=max_no_results_obj)

    prod_unit_ids =  response['ProductionUnitIdentifierCollection']['ProductionUnitIdentifier']
    print "Found " + str(len(prod_unit_ids)) + " prod unit ids"

    level_obj = client.get_type('ns0:LevelType')(10)
    ProdUnitIDType = client.get_type('ns2:ProductionUnitIdentifierType')
    for prod_unit_id in prod_unit_ids:
        prod_unit_id_obj = ProdUnitIDType(prod_unit_id)
        response = service.getProductionUnit(InvocationContext=inv_context,
                                             ProductionUnitIdentifier=prod_unit_id_obj,
                                             level= level_obj)
        print response['ProductionUnitName']['name']


def getSearchAddressObj(client, mun_code, street_name):
    SearchAddressType = client.get_type('ns0:SearchAddressType')
    AuthorityCodeType = client.get_type('ns_oio_auth_code:AuthorityCodeType')
    mun_code_obj = AuthorityCodeType(mun_code)
    StreetNameType = client.get_type('ns_oio_street_and_zip:StreetNameType')
    street_name_obj = StreetNameType(street_name)
    return SearchAddressType(StreetName=street_name_obj,
                             MunicipalityCode=mun_code_obj)


if __name__ == "__main__":
    service_agreement_uuid = ''
    user_system_uuid = ''
    user_uuid = ''
    service_uuid = ''

    main(service_agreement_uuid, user_system_uuid, user_uuid, service_uuid)