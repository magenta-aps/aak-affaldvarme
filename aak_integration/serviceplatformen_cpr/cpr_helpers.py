# -- coding: utf-8 --
import json
import serviceplatformen_cpr.settings as settings

from serviceplatformen_cpr.services import get_citizen

uuids = {
    'service_agreement': settings.SP_SERVICE_AGREEMENT_UUID_SF1520_PROD,
    'user_system': settings.SP_USER_SYSTEM_UUID_PROD,
    'user': settings.SP_USER_UUID_PROD,
    'service': settings.SP_SERVICE_SF1520_PROD
}

certificate = settings.SP_CERTIFICATE_PATH


def get_cpr_data(cprnr):

    result = get_citizen(
        service_uuids=uuids,
        certificate=certificate,
        cprnr=cprnr
    )
    return result


if __name__ == '__main__':

    cprnr = '2511640019'
    result = get_cpr_data(cprnr)
    print(json.dumps(result))
