from sandbox.sp_agent.sp_adapter_base import SPAdapterBase


class CVRAdapter(SPAdapterBase):

    def __init__(self, uuids, cert_filename, prod_mode=False):

        binding_name = '{http://rep.oio.dk/eogs/xml.wsdl/}CvrBinding'

        if prod_mode:
            wsdl_url     = 'https://prod.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
            endpoint_url = 'https://prod.serviceplatformen.dk/service/CVROnline/CVROnline/1'
        else:
            wsdl_url     = 'https://exttestwww.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
            endpoint_url = 'https://exttest.serviceplatformen.dk/service/CVROnline/CVROnline/1'

        super(CVRAdapter, self).__init__(uuids, wsdl_url, endpoint_url,
                                         binding_name, cert_filename)


        self.client.set_ns_prefix('ns_oio_auth_code', 'http://rep.oio.dk/cpr.dk/xml/schemas/core/2005/03/18/')
        self.client.set_ns_prefix('ns_oio_street_and_zip', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2005/03/15/')
        self.client.set_ns_prefix('ns_oio_build_ident', 'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/')

        self.level_obj = self.client.get_type('ns0:LevelType')(10) #TODO what does this do??


    def searchProdUnits(self, mun_code, max_no_results=500000):
        search_address_obj = self.getSearchMunicipalityObj(mun_code)

        max_no_results_obj = self.client.get_type('ns0:MaximumNumberOfResultsType')(max_no_results)

        response = self.service.searchProductionUnit(InvocationContext=self.inv_context,
                                                     SearchAddress=search_address_obj,
                                                     maximumNumberOfResultsType=max_no_results_obj)

        prod_unit_ids =  response['ProductionUnitIdentifierCollection']['ProductionUnitIdentifier']
        response_complete = not response['moreResultsExistIndicator']

        return prod_unit_ids, response_complete

    def searchLegalUnits(self, mun_code, max_no_results=500000):
        search_address_obj = self.getSearchMunicipalityObj(mun_code)
        max_no_results_obj = self.client.get_type('ns0:MaximumNumberOfResultsType')(max_no_results)

        response = self.service.searchLegalUnit(InvocationContext=self.inv_context,
                                                SearchAddress=search_address_obj,
                                                maximumNumberOfResultsType=max_no_results_obj)

        legal_unit_ids =  response['LegalUnitIdentifierCollection']['LegalUnitIdentifier']
        response_complete = not response['moreResultsExistIndicator']

        return legal_unit_ids, response_complete

    def getProdUnit(self, prod_unit_id):
        ProdUnitIDType = self.client.get_type('ns2:ProductionUnitIdentifierType')
        prod_unit_id_obj = ProdUnitIDType(prod_unit_id)
        response = self.service.getProductionUnit(InvocationContext=self.inv_context,
                                                  ProductionUnitIdentifier=prod_unit_id_obj,
                                                  level=self.level_obj)
        return response

    def getLegalUnit(self, legal_unit_id):
        LegalUnitIDType = self.client.get_type('ns2:LegalUnitIdentifierType')
        legal_unit_id_obj = LegalUnitIDType(legal_unit_id)
        response = self.service.getLegalUnit(InvocationContext=self.inv_context,
                                             LegalUnitIdentifier=legal_unit_id_obj,
                                             level=self.level_obj)
        return response


    def getSearchMunicipalityObj(self, mun_code):
        SearchAddressType = self.client.get_type('ns0:SearchAddressType')
        AuthorityCodeType = self.client.get_type('ns_oio_auth_code:AuthorityCodeType')
        mun_code_obj = AuthorityCodeType(mun_code)
        return SearchAddressType(MunicipalityCode=mun_code_obj)
