import logging
import zeep
from requests import Session

# Adopted from initial state of the project
# TODO: Needs refactoring for more clarity


class SPAdapterBase(object):

    def __init__(
            self, uuids, wsdl_url, endpoint_url, binding_name, cert_filename):
        self._init_zeep_logging()
        self._init_client(cert_filename, wsdl_url)
        self._init_inv_context(uuids)

        self.service = self.client.create_service(binding_name, endpoint_url)

    def _init_zeep_logging(self):
        logger = logging.getLogger("zeep.wsdl.bindings.soap")
        if len(logger.handlers) == 0:
            handler = logging.StreamHandler()
            logger.addHandler(handler)

    def _init_client(self, cert_filename, wsdl_url):
        session = Session()
        session.cert = cert_filename
        transport = zeep.Transport(session=session)
        self.client = zeep.Client(wsdl=wsdl_url, transport=transport)

    def _init_inv_context(self, uuids):
        service_agreement_uuid_obj = self.client.get_type(
            'ns1:ServiceAgreenentUUIDtype')(uuids['service_agreement'])
        user_system_uuid_obj = self.client.get_type(
            'ns1:UserSystemUUIDtype')(uuids['user_system'])
        user_uuid_obj = self.client.get_type(
            'ns1:UserUUIDtype')(uuids['user'])
        service_uuid_obj = self.client.get_type(
            'ns1:ServiceUUIDtype')(uuids['service'])

        InvContextType = self.client.get_type('ns1:InvocationContextType')
        self.inv_context = InvContextType(
            ServiceAgreementUUID=service_agreement_uuid_obj,
            UserSystemUUID=user_system_uuid_obj,
            UserUUID=user_uuid_obj,
            ServiceUUID=service_uuid_obj)


# Adopted from initial state of the project
# TODO: Needs refactoring for more clarity
class CVRAdapter(SPAdapterBase):

    def __init__(self, uuids, cert_filename, prod_mode=False):

        binding_name = '{http://rep.oio.dk/eogs/xml.wsdl/}CvrBinding'

        if prod_mode:
            wsdl_url = 'https://prod.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
            endpoint_url = 'https://prod.serviceplatformen.dk/service/CVROnline/CVROnline/1'
        else:
            wsdl_url = 'https://exttestwww.serviceplatformen.dk/administration/wsdl/CvrService.wsdl'
            endpoint_url = 'https://exttest.serviceplatformen.dk/service/CVROnline/CVROnline/1'

        super(CVRAdapter, self).__init__(uuids, wsdl_url, endpoint_url,
                                         binding_name, cert_filename)

        self.client.set_ns_prefix(
            'ns_oio_auth_code', 'http://rep.oio.dk/cpr.dk/xml/schemas/core/2005/03/18/')
        self.client.set_ns_prefix('ns_oio_street_and_zip',
                                  'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2005/03/15/')
        self.client.set_ns_prefix('ns_oio_build_ident',
                                  'http://rep.oio.dk/ebxml/xml/schemas/dkcc/2003/02/13/')

        self.level_obj = self.client.get_type('ns0:LevelType')(10)  # TODO what does this do??

    def searchProdUnits(self, mun_code, max_no_results=500000):
        search_address_obj = self.getSearchMunicipalityObj(mun_code)

        max_no_results_obj = self.client.get_type(
            'ns0:MaximumNumberOfResultsType')(max_no_results)

        response = self.service.searchProductionUnit(InvocationContext=self.inv_context,
                                                     SearchAddress=search_address_obj,
                                                     maximumNumberOfResultsType=max_no_results_obj)

        prod_unit_ids = response['ProductionUnitIdentifierCollection'][
            'ProductionUnitIdentifier']
        response_complete = not response['moreResultsExistIndicator']

        return prod_unit_ids, response_complete

    def searchLegalUnits(self, mun_code, max_no_results=500000):
        search_address_obj = self.getSearchMunicipalityObj(mun_code)
        max_no_results_obj = self.client.get_type(
            'ns0:MaximumNumberOfResultsType')(max_no_results)

        response = self.service.searchLegalUnit(InvocationContext=self.inv_context,
                                                SearchAddress=search_address_obj,
                                                maximumNumberOfResultsType=max_no_results_obj)

        legal_unit_ids = response[
            'LegalUnitIdentifierCollection']['LegalUnitIdentifier']
        response_complete = not response['moreResultsExistIndicator']

        return legal_unit_ids, response_complete

    def getProdUnit(self, prod_unit_id):
        ProdUnitIDType = self.client.get_type(
            'ns2:ProductionUnitIdentifierType')
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
        AuthorityCodeType = self.client.get_type(
            'ns_oio_auth_code:AuthorityCodeType')
        mun_code_obj = AuthorityCodeType(mun_code)
        return SearchAddressType(MunicipalityCode=mun_code_obj)
