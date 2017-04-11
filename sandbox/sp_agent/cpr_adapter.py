from sandbox.sp_agent import sp_adapter_base


class CPRAdapter(sp_adapter_base.SPAdapterBase):

    def __init__(self, uuids, cert_filename, prod_mode=False):
        binding_name = '{http://serviceplatformen.dk/xml/wsdl/soap11/CprSubscriptionService/1/}' \
                            'CprSubscriptionWebServiceBinding'
        wsdl_url = 'CprSubsc/CprSubscriptionService.wsdl'
        if prod_mode:
            endpoint_url = 'https://prod.serviceplatformen.dk/service/CPRSubscription/CPRSubscription/1/'
        else:
            endpoint_url = 'https://exttest.serviceplatformen.dk/service/CPRSubscription/CPRSubscription/1/'

        super(CPRAdapter, self).__init__(uuids, wsdl_url, endpoint_url, binding_name, cert_filename)

    def addMunicipalitySubscr(self, mun_code):
        response = self.service.AddMunicipalityCodeSubscription(InvocationContext=self.inv_context,
                                                                MunicipalityCode=mun_code)
        return response

    def removeMunicipalitySubscr(self, mun_code):
        response = self.service.RemoveMunicipalityCodeSubscription(InvocationContext=self.inv_context,
                                                                   MunicipalityCode=mun_code)
        return response