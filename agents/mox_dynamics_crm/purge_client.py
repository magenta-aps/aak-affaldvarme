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
import pprint

from logging import getLogger

DO_WRITE = False

# Init logging
log = getLogger(__name__)


def delete_crm_entity(crm_table, lora_ref, external_ref):
    """ deletes object in crm and then if it is subsequently not found there 
        it is deleted in the cache_layer
    """

    if not external_ref:
        log.warn("ref error lora_ref:%s  external_ref:%s in %s delete in cache", 
            lora_ref, external_ref, crm_table
        )
        cache.delete(crm_table, lora_ref)
        return

    response = crm.get_request(
        resource="{table_name}({crm_id})".format(
            table_name=crm_table,
            crm_id=external_ref
        )
    )

    if response.status_code in [404]:
        log.info(
            "not found in crm.{table_name} lora-id:{lora_id}, "
            "crm-id:{crm_id}".format(
                table_name=crm_table,
                lora_id=lora_ref,
                crm_id=external_ref
            )
        )

    if DO_WRITE == True:
        log.info("deleting lora_ref:%s  external_ref:%s in %s", 
            lora_ref, external_ref, crm_table
        )
        response = crm.delete_request(
            resource=crm_table,
            identifier=external_ref
        )
    else:
        log.info("NOT deleting lora_ref:%s  external_ref:%s in %s", 
            lora_ref, external_ref, crm_table
        )

    response = crm.get_request(
        resource="{table_name}({crm_id})".format(
            table_name=crm_table,
            crm_id=external_ref
        )
    )

    # delete in cache if not found in crm
    if response.status_code in [404]:
        if DO_WRITE == True:
            log.info(
                "deleting from cache.{table_name} "
                "lora-id:{lora_id}, "
                "crm-id:{crm_id}".format(
                    table_name=crm_table,
                    lora_id=lora_ref,
                    crm_id=external_ref
                )
            )
            cache.delete(crm_table, lora_ref)
        else:
            log.info(
                "NOT deleting from cache.{table_name} "
                "lora-id:{lora_id}, "
                "crm-id:{crm_id}".format(
                    table_name=crm_table,
                    lora_id=lora_ref,
                    crm_id=external_ref
                )
            )

def get_obsolete_objects_dict(crm_table):
    """ returns a dict with lora-id as key and object as value
        for all objects that were not updated in the latest import
    """
    return {o["id"]:o for o in cache.all_obsolete(crm_table)}

def get_semi_safe_to_delete_objects_dict(
    forbidden_refs, 
    forbidden_keys, 
    objects 
):
    """ copies all objects into semi_safe_to_delete
        and then removes any object from semi_safe_to_delete that is directly
        referenced by any incident in dynamics_crm
        for contacts for example, it will disallow deleting if the objects 
        external_ref is referred to by any incident in '_ava_aktoer_value'

        The name semi_safe refers to the fact that this is only looking 
        at direct references. 
        It does not take into account that a contact is mentioned here
        and then a customer_relation refers to that by use of an 'obind'
    """
    semi_safe_to_delete=dict(objects)
    for k in forbidden_keys:
        for loraid, o in objects.items():
            if o["external_ref"] in forbidden_refs[k]:
                log.info("excluding refd by incident lora_ref:%s  external_ref:%s in %s", 
                    loraid, o["external_ref"], crm_table
                ) 
                semi_safe_to_delete.pop(k, None)

    return semi_safe_to_delete 


def find_incident_relations():
    external_refs={
        "_ava_kundeforhold_value":[],
        "_customerid_value":[],
        "_ava_aktoer_value":[],
        "_ava_installation_value":[],

    }

    #response = crm.get_request(
    #    resource="{table_name}".format(
    #    table_name="incidents"
    #    )
    #)

    #if response.status_code != 200:
    #    log.error("incidents not retrieved")
    #    exit()
    #incidents = response.json()["value"]
    #refkeys=list(external_refs.keys())
    #for i in incidents:
    #    for k in refkeys:
    #        kval = i.get(k)
    #        if kval: 
    #            external_refs[k].append(kval)

    return { 
        k: set(v) 
        for k,v in external_refs.items()
    }
        

def get_deleted_objects(objects, oio_resource):
    deleted_objects = {}
    list_of_lora_ids = list(objects.keys())

    for i in range(0, len(list_of_lora_ids), 90):
        oio_objects = oio.get_request(
            resource=oio_resource,
            uuid=list_of_lora_ids[i:i+90])

        for o in oio_objects:
            registrering = o.get("registreringer", [{}])[-1]
            if registrering.get(
                "livscykluskode",
                "NotApplicable"
            ) == "Slettet":
                deleted_objects[
                    o["id"]
                ] = objects[o["id"]]

    return deleted_objects

def purge_objects(purgable_objects, crm_table):
    for loraid, o in purgable_objects.items():
        delete_crm_entity(crm_table, loraid, o["external_ref"]) 

def get_purgable_objects(
    crm_table, 
    forbidden_refs, 
    forbidden_keys,
):
    obsolete_objects = get_obsolete_objects_dict(crm_table)
    purgable_objects = get_semi_safe_to_delete_objects_dict(
        forbidden_refs,
        forbidden_keys,
        obsolete_objects
    )
    # we dont need this now, but we had it earlier - to see if they are really deleted in lora
    # purgable_objects = get_deleted_objects(purgable_objects, oio_resource)
    log.warn("purgable_objects %d of %s",len(purgable_objects),crm_table)
    return purgable_objects


def purge_ava_kundeforhold(forbidden_refs):
    crm_table = "accounts"
    oio_resource=oio.resources["interessefaellesskab"]["resource"]
    forbidden_keys=["_ava_kundeforhold_value", "_customerid_value" ]
    purgable_objects = get_purgable_objects(
        crm_table, 
        forbidden_refs, 
        forbidden_keys
    )
    purge_objects(purgable_objects, crm_table)


def purge_ava_aftales (forbidden_refs):
    crm_table = "ava_aftales"
    oio_resource=oio.resources["indsats"]["resource"]
    forbidden_keys=[]
    purgable_objects = get_purgable_objects(
        crm_table, 
        forbidden_refs, 
        forbidden_keys
    )
    purge_objects(purgable_objects, crm_table)


def purge_ava_installations(forbidden_refs):
    crm_table = "ava_installations"    
    oio_resource=oio.resources["klasse"]["resource"]
    forbidden_keys=["_ava_installation_value"] 
    purgable_objects = get_purgable_objects(
        crm_table, 
        forbidden_refs, 
        forbidden_keys
    )
    purge_objects(purgable_objects, crm_table)

def purge_ava_contacts(forbidden_refs):
    crm_table = "contacts"    
    oio_resource=oio.resources["bruger"]["resource"]
    forbidden_keys=["_ava_aktoer_value"] 
    purgable_objects = get_purgable_objects(
        crm_table, 
        forbidden_refs, 
        forbidden_keys
    )
    purge_objects(purgable_objects, crm_table)

def purge_ava_kunderolles(forbidden_refs):
    crm_table = "ava_kunderolles"    
    oio_resource=oio.resources["organisationfunktion"]["resource"]
    forbidden_keys=[]
    purgable_objects = get_purgable_objects(
        crm_table, 
        forbidden_refs, 
        forbidden_keys
    )
    purge_objects(purgable_objects, crm_table)


def run_purge():
    incident_relations = find_incident_relations()

    purge_ava_kundeforhold(incident_relations)
    purge_ava_aftales(incident_relations)
    purge_ava_installations(incident_relations)
    purge_ava_contacts(incident_relations)
    purge_ava_kunderolles(incident_relations)


