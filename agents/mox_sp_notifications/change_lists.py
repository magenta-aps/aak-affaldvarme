import interfaces.oio_interface as oio
import requests
import datetime
import time
import cpr_udtraek
from helper import get_config
import logging
from paramiko.ssh_exception import SSHException


logger = logging.getLogger("change-lists")
cpr_config = get_config("cpr_udtraek")
oio_config = get_config("oio")


def get_changed_cprs():
    "Get the updated CPR numbers from serviceplatformen"
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
    "Translate a cpr number to a list of one or more uuids"
    return requests.get(
        url="{oio_rest_url}/organisation/bruger".format(**oio_config),
        params={"tilknyttedepersoner": "urn:{pnr}".format(pnr=cprno)},
        verify=False
    ).json()["results"][0]


def get_changed_bruger_uuids():
    "Get changed cprnumbers from SP and translate them to uuids in lora"
    changed_uuids, cprnos = [], None
    # retry a couple of times in case of trouble
    for i in range(3):
        try:
            cprnos = get_changed_cprs()
            break
        except (SSHException, EOFError) as e:
            logger.exception(e)
        time.sleep(2)
    if cprnos is None:
        raise RuntimeError(
            "SFTP to serviceplatformen had an error"
            " which should be visible above"
        )
    logger.info("changed cprs: %d", len(cprnos))
    for i in cprnos:
        logger.info("getting uuid for cpr %s", i)
        changed_uuids.extend(get_bruger_uuids_from_cprno(i))
    return changed_uuids


def get_changed_uuids(resource):
    "Get changed uuids for resource"
    if resource == "bruger":
        return get_changed_bruger_uuids()
    else:
        # 'all' for organisations
        return oio.get_all(resource)


if __name__ == '__main__':
    cprs = get_changed_cprs()
    print(len(cprs))
