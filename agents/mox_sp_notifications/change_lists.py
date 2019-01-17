import interfaces.oio_interface as oio
import requests
import datetime
import cpr_udtraek
from helper import get_config


cpr_config = get_config("cpr_udtraek")
oio_config = get_config("oio")


def get_changed_cprs():
    cprnos = []
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    citizen_changes_by_date = cpr_udtraek.delta(
        yesterday.strftime("%y%m%d"), settings=cpr_config
    )
    [
        cprnos.extend(x.keys()) 
        for x in citizen_changes_by_date.values()
    ]
    return list(set(cprnos))


def get_bruger_uuids_from_cprno(cprno):
    return requests.get(
        url="{oio_rest_url}/organisation/bruger".format(**oio_config),
        params={"tilknyttedepersoner":"urn:{pnr}".format(pnr=cprno)},
        verify=False
    ).json()["results"][0]


def get_changed_bruger_uuids():
    changed_uuids = []
    #return oio.get_all("bruger")  # current functionality
    cprnos = get_changed_cprs()   # new functionality
    for i in cprnos :
        changed_uuids.extend(get_bruger_uuids_from_cprno(i))
    return changed_uuids


def get_changed_uuids(resource):
    if resource == "bruger":
        return get_changed_bruger_uuids()
    else:
        return oio.get_all(resource)


if __name__ == '__main__':
    cprs = get_changed_cprs()
