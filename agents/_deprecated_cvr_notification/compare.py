from datetime import datetime

from services import report_error


def generate_virkning():
    """Generates a 'virkning' object spanning from 'today' to 'infinity'"""
    return {
        'from': datetime.now().strftime('%Y-%m-%d'),
        'to': 'infinity'
    }


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


def generate_and_add_dawa_uuid_update(dawa_uuid, update_json):
    relationer = update_json.setdefault('relationer', {})
    adresser_list = relationer.setdefault(
        'adresser',
        [])

    if len(adresser_list) is 0:
        adresser_list.append({})
    adresse = adresser_list[0]

    adresse['uuid'] = dawa_uuid
    adresse.setdefault('virkning', generate_virkning())


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


def generate_and_add_org_navn_update(org_navn, update_json):
    attributter = update_json.setdefault('attributter', {})
    organisationegenskaber_list = attributter.setdefault(
        'organisationegenskaber',
        [])

    if len(organisationegenskaber_list) is 0:
        organisationegenskaber_list.append({})
    egenskaber = organisationegenskaber_list[0]

    egenskaber['organisationsnavn'] = org_navn
    egenskaber.setdefault('virkning', generate_virkning())


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


def generate_and_add_branche_update(branche, update_json):
    relationer = update_json.setdefault('relationer', {})
    branche_list = relationer.setdefault(
        'branche',
        [])

    if len(branche_list) is 0:
        branche_list.append({})
    branche_dict = branche_list[0]

    branche_dict['urn'] = 'urn:{}'.format(branche)
    branche_dict.setdefault('virkning', generate_virkning())


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


def generate_and_add_virksomhedstype_update(virksomhedstype, update_json):
    relationer = update_json.setdefault('relationer', {})
    virksomhedstype_list = relationer.setdefault(
        'virksomhedstype',
        [])

    if len(virksomhedstype_list) is 0:
        virksomhedstype_list.append({})
    virksomhedstype_dict = virksomhedstype_list[0]

    virksomhedstype_dict['urn'] = 'urn:{}'.format(virksomhedstype)
    virksomhedstype_dict.setdefault('virkning', generate_virkning())


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
