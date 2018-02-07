# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from helper import create_virkning


# TODO: Docstrings!!!!

def extract_dawa_uuid_from_org(org_data, uuid):
    registreringer = org_data.get('registreringer')
    relationer = registreringer[0].get('relationer')
    adresser = relationer.get('adresser')

    dawa_addresses = [x for x in adresser if
                      'uuid' in x]

    # We expect there only to be one dawa address active
    if len(dawa_addresses) != 1:
        report_error(
            'One active DAWA address uuid expected for {}'.format(uuid),
            error_object=org_data)
        return

    address = dawa_addresses[0]
    return address['uuid']




def extract_dawa_uuid_from_cvr(cvr_data, uuid):
    return str(cvr_data.get('dawa_uuid'))


def generate_and_add_dawa_uuid_update(dawa_uuid):

    update = {
        "uuid": dawa_uuid,
        "virkning": create_virkning()
    }

    return {
        "type": "update",
        "group": "relationer",
        "subgroup": "adresser",
        "field": "uuid",
        "update": update
    }


def extract_organisationsnavn_from_org(org_data, uuid):
    registreringer = org_data['registreringer']
    attributter = registreringer[0]['attributter']
    organisationegenskaber = attributter['organisationegenskaber']

    navn_egenskaber = [x for x in organisationegenskaber if
                       'organisationsnavn' in x]

    # We expect there only to be one active organisationsnavn
    if len(navn_egenskaber) != 1:
        report_error(
            'We expect one active organisationsnavn for {}'.format(uuid),
            error_object=org_data)
        return

    org_egenskab = organisationegenskaber[0]
    return org_egenskab['organisationsnavn']


def extract_organisationsnavn_from_cvr(cvr_data, uuid):
    return str(cvr_data.get('organisationsnavn'))


def generate_and_add_org_navn_update(org_navn):
    update = {
        "organisationsnavn": org_navn,
        "virkning": create_virkning()
    }

    return {
        "type": "update",
        "group": "attributter",
        "subgroup": "organisationegenskaber",
        "field": "organisationsnavn",
        "update": update
    }


def extract_branche_from_org(org_data, uuid):
    registreringer = org_data.get('registreringer')
    relationer = registreringer[0].get('relationer')
    branche_list = relationer.get('branche')

    # We expect there only to be one active branche
    if not branche_list or len(branche_list) != 1:
        report_error(
            'We expect one active branche for {}'.format(uuid),
            error_object=org_data)

    branche = branche_list[0]

    split_urn = branche['urn'].split(':')
    return split_urn[1]


def extract_branche_from_cvr(cvr_data, uuid):
    return str(cvr_data.get('branchekode'))


def generate_and_add_branche_update(branche):

    update = {
        "urn": "urn:{type}".format(type=branche),
        "virkning": create_virkning()
    }

    return {
        "type": "update",
        "group": "relationer",
        "subgroup": "branche",
        "field": "urn",
        "update": update
    }


def extract_virksomhedstype_from_org(org_data, uuid):
    registreringer = org_data.get('registreringer')
    relationer = registreringer[0].get('relationer')
    virksomhedstype_list = relationer.get('virksomhedstype')

    # We expect there only to be one active branche
    if not virksomhedstype_list or len(virksomhedstype_list) != 1:
        report_error(
            'We expect one active virksomhedstype for {}'.format(uuid),
            error_object=org_data)
        return

    virksomhedstype = virksomhedstype_list[0]

    split_urn = virksomhedstype['urn'].split(':')
    return split_urn[1]


def extract_virksomhedstype_from_cvr(cvr_data, uuid):
    return str(cvr_data.get('virksomhedsform'))


def generate_and_add_virksomhedstype_update(virksomhedstype):

    update = {
        "urn": "urn:{type}".format(type=virksomhedstype),
        "virkning": create_virkning()
    }

    return {
        "type": "update",
        "group": "relationer",
        "subgroup": "virksomhedstype",
        "field": "urn",
        "update": update
    }



"""
Tuples representing the comparisons and updates to be made

First element should be a function extracting a value from a LoRa organisation

Second element should be a function extracting a value from CVR data

Third element should be a function extending an existing 'update' object 
with updated values, in case an update should be performed.
"""
COMPARISONS = [
    (
        extract_dawa_uuid_from_org,
        extract_dawa_uuid_from_cvr,
        generate_and_add_dawa_uuid_update
    ),
    (
        extract_organisationsnavn_from_org,
        extract_organisationsnavn_from_cvr,
        generate_and_add_org_navn_update
    ),
    (
        extract_branche_from_org,
        extract_branche_from_cvr,
        generate_and_add_branche_update
    ),
    (
        extract_virksomhedstype_from_org,
        extract_virksomhedstype_from_cvr,
        generate_and_add_virksomhedstype_update
    ),
]
