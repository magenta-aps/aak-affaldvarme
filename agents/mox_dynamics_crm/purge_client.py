# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import oio_interface as oio
import cache_interface as cache
import crm_interface as crm

from logging import getLogger

DO_WRITE = True

# Init logging
log = getLogger(__name__)


def purge_objects(oio_resource, crm_table):
    """
        for every aftale that was not updated in the latest transfer:
            if it was deleted in lora:
                try to delete it in crm
                if succesful, delete it in cache,
                otherwise leave it, as it may be undeleteabl
                in crm due to internal links there

    """
    list_of_lora_ids = [
        x["id"]
        for x in cache.all_obsolete(crm_table)
    ]

    set_of_lora_ids = set(list_of_lora_ids)
    list_of_crm_ids = []

    for i in range(0, len(list_of_lora_ids), 90):
        objects = oio.get_request(
            resource=oio_resource,
            uuid=list_of_lora_ids[i:i+90])

        for o in objects:
            registrering = o.get("registreringer", [{}])[-1]
            if registrering.get(
                "livscykluskode",
                "NotApplicable"
            ) == "Slettet":

                cached_object = cache.get(
                    table=crm_table,
                    uuid=o["id"]
                )

                if not cached_object.get("external_ref"):
                    set_of_lora_ids -= {o["id"]}
                    continue

                if not DO_WRITE:
                    log.debug(
                        "to be deleted from crm.{table_name}"
                        " lora-id:{lora_id}, "
                        "crm-id:{crm_id}".format(
                            table_name=crm_table,
                            lora_id=o["id"],
                            crm_id=cached_object["external_ref"]
                        )
                    )
                    continue
                else:
                    response = crm.get_request(
                        resource="{table_name}({crm_id})".format(
                            table_name=crm_table,
                            crm_id=cached_object["external_ref"]
                        )
                    )

                    if response.status_code in [404]:
                        log.info(
                            "not found in crm.{table_name} lora-id:{lora_id}, "
                            "crm-id:{crm_id}".format(
                                table_name=crm_table,
                                lora_id=o["id"],
                                crm_id=cached_object["external_ref"]
                            )
                        )

                        # this has not been deleted this time
                        set_of_lora_ids -= {o["id"]}

                    log.info(
                        "deleting from crm.{table_name} lora-id:{lora_id}, "
                        "crm-id:{crm_id}".format(
                            table_name=crm_table,
                            lora_id=o["id"],
                            crm_id=cached_object["external_ref"]
                        )
                    )

                    response = crm.delete_request(
                        resource=crm_table,
                        identifier=cached_object["external_ref"]
                    )
                    if response.status_code in [200, 204]:
                        list_of_crm_ids.append(cached_object["external_ref"])
                    elif response.status_code in [404]:
                        set_of_lora_ids -= {o["id"]}

                    # either way we check via get_request
                    response = crm.get_request(
                        resource="{table_name}({crm_id})".format(
                            table_name=crm_table,
                            crm_id=cached_object["external_ref"]
                        )
                    )

                    # delete in cache if not found in crm
                    if response.status_code in [404]:
                        log.info(
                            "deleting from cache.{table_name} "
                            "lora-id:{lora_id}, "
                            "crm-id:{crm_id}".format(
                                table_name=crm_table,
                                lora_id=o["id"],
                                crm_id=cached_object["external_ref"]
                            )
                        )
                        cache.delete(crm_table, o["id"])

    return set_of_lora_ids, set(list_of_crm_ids)


def purge_ava_aftales():
    purged_lora_ids, purged_crm_ids = purge_objects(
        oio_resource=oio.resources["indsats"]["resource"],
        crm_table="ava_aftales"
    )

    # it seems like the link from aftale to kunde is cascade-deleted
    return purged_lora_ids, purged_crm_ids


def purge_ava_kundeforhold():
    return purge_objects(
        oio_resource=oio.resources["interessefaellesskab"]["resource"],
        crm_table="accounts"
    )


def run_purge():
    purge_ava_kundeforhold()
    purge_ava_aftales()
