import logging
import zeep
from requests import Session


class SPAdapterBase(object):

    def __init__(self, uuids, wsdl_url, endpoint_url, binding_name, cert_filename):
        self._init_logging()
        self._init_client(cert_filename, wsdl_url)
        self._init_inv_context(uuids)

        self.service = self.client.create_service(binding_name, endpoint_url)

    def _init_logging(self):
        handler = logging.StreamHandler()
        logging.getLogger("zeep.wsdl.bindings.soap").addHandler(handler)

    def _init_client(self, cert_filename, wsdl_url):
        session = Session()
        session.cert = cert_filename
        transport = zeep.Transport(session=session)
        self.client = zeep.Client(wsdl=wsdl_url, transport=transport)

    def _init_inv_context(self, uuids):
        service_agreement_uuid_obj = self.client.get_type('ns1:ServiceAgreenentUUIDtype')(uuids['service_agreement'])
        user_system_uuid_obj = self.client.get_type('ns1:UserSystemUUIDtype')(uuids['user_system'])
        user_uuid_obj = self.client.get_type('ns1:UserUUIDtype')(uuids['user'])
        service_uuid_obj = self.client.get_type('ns1:ServiceUUIDtype')(uuids['service'])

        InvContextType = self.client.get_type('ns1:InvocationContextType')
        self.inv_context = InvContextType(
            ServiceAgreementUUID=service_agreement_uuid_obj,
            UserSystemUUID=user_system_uuid_obj,
            UserUUID=user_uuid_obj,
            ServiceUUID=service_uuid_obj)
