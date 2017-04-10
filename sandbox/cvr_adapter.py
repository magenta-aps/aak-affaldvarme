from sandbox.sp_init import init_service


class CVRAdapter(object):


    def __init__(self, uuids, cert_filename, prod_mode=False):
        self.uuids = uuids
        self.binding_name = '{http://rep.oio.dk/eogs/xml.wsdl/}CvrBinding'

        if prod_mode:
            self.endpoint_url = 'https://prod.serviceplatformen.dk/service/CVROnline/CVROnline/1'
            self.wsdl_url = 'https://prod.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
        else:
            self.endpoint_url = 'https://exttest.serviceplatformen.dk/service/CVROnline/CVROnline/1'
            self.wsdl_url = 'https://exttestwww.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'


        self.client, self.service, self.inv_context = init_service(self.endpoint_url,
                                                    uuids['service_agreement'],
                                                    uuids['user_system'],
                                                    uuids['user'],
                                                    uuids['service'],
                                                    cert_filename,
                                                    self.wsdl_url,
                                                    self.binding_name)

        self.client.set_ns_prefix('ns_oio_auth_code', 'http://rep.oio.dk/cpr.dk/xml/schemas/core/2005/03/18/')
        self.client.set_ns_prefix('ns_oio_street_and_zip', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2005/03/15/')
        self.client.set_ns_prefix('ns_oio_build_ident', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/')

        self.level_obj = self.client.get_type('ns0:LevelType')(10) #TODO what does this do??

    def searchProdUnitsDemo(self):
        search_address_obj = self.getSearchAddressObj('0751', 'Frydenlunds Alle')

        max_no_results_obj = self.client.get_type('ns0:MaximumNumberOfResultsType')(50)

        response = self.service.searchProductionUnit(InvocationContext=self.inv_context,
                                                     SearchAddress=search_address_obj,
                                                     maximumNumberOfResultsType=max_no_results_obj)

        prod_unit_ids =  response['ProductionUnitIdentifierCollection']['ProductionUnitIdentifier']
        print "Found " + str(len(prod_unit_ids)) + " prod unit ids"


        ProdUnitIDType = self.client.get_type('ns2:ProductionUnitIdentifierType')
        for prod_unit_id in prod_unit_ids:
            prod_unit_id_obj = ProdUnitIDType(prod_unit_id)
            response = self.service.getProductionUnit(InvocationContext=self.inv_context,
                                                 ProductionUnitIdentifier=prod_unit_id_obj,
                                                 level= level_obj)
            print response['ProductionUnitName']['name']

    def searchProdUnits(self, mun_code):
        search_address_obj = self.getSearchMunicipalityObj('0751')

        max_no_results_obj = self.client.get_type('ns0:MaximumNumberOfResultsType')(100000)

        response = self.service.searchProductionUnit(InvocationContext=self.inv_context,
                                                     SearchAddress=search_address_obj,
                                                     maximumNumberOfResultsType=max_no_results_obj)

        prod_unit_ids =  response['ProductionUnitIdentifierCollection']['ProductionUnitIdentifier']
        more_results = response['moreResultsExistIndicator']
        response_complete = not more_results

        return prod_unit_ids, response_complete

    def lookupProdUnit(self, prod_unit_id):
        ProdUnitIDType = self.client.get_type('ns2:ProductionUnitIdentifierType')
        prod_unit_id_obj = ProdUnitIDType(prod_unit_id)
        response = self.service.getProductionUnit(InvocationContext=self.inv_context,
                                                  ProductionUnitIdentifier=prod_unit_id_obj,
                                                  level=self.level_obj)
        return response


    def getSearchMunicipalityObj(self, mun_code):
        SearchAddressType = self.client.get_type('ns0:SearchAddressType')
        AuthorityCodeType = self.client.get_type('ns_oio_auth_code:AuthorityCodeType')
        mun_code_obj = AuthorityCodeType(mun_code)
        return SearchAddressType(MunicipalityCode=mun_code_obj)


    def getSearchAddressObj(self, mun_code, street_name=None):
        SearchAddressType = self.client.get_type('ns0:SearchAddressType')
        AuthorityCodeType = self.client.get_type('ns_oio_auth_code:AuthorityCodeType')
        mun_code_obj = AuthorityCodeType(mun_code)
        StreetNameType = self.client.get_type('ns_oio_street_and_zip:StreetNameType')
        street_name_obj = StreetNameType(street_name)
        return SearchAddressType(StreetName=street_name_obj,
                                 MunicipalityCode=mun_code_obj)




