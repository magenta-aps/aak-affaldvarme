#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import pytz
import requests
import functools
import collections

from settings import SYSTEM_USER, AVA_ORGANISATION, BASE_URL

KUNDE = 'Kunde'
LIGESTILLINGSKUNDE = 'Ligestillingskunde'

ROLE_MAP = {KUNDE: '915240004', LIGESTILLINGSKUNDE: '915240006'}


# session = requests.Session()
# session.verify = '/etc/ssl/certs/ca-certificates.crt'


def request(func):
    def call_and_raise(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            result.raise_for_status()
        return result
    return call_and_raise


class DummyResult:
    "Return a request result when not actually calling LoRa."
    def __init__(self, uuid):
        self.__uuid = uuid

    def json(self):
        return {'uuid': self.__uuid}


def lookup_objects(service, oio_class, **conditions):
    'Lookup objects of class cls in service with the specified conditions.'
    search_results = []
    if conditions:
        condition_string = '&'.join(
            ['{0}={1}'.format(k, v) for k, v in conditions.items()]
        )
        request_string = ('{0}/{1}/{2}?{3}'.format(
            BASE_URL, service, oio_class, condition_string
        ))

        result = requests.get(request_string)

        if result:
            search_results = result.json()['results'][0]

    return search_results


def lookup_one(service, oio_class, **conditions):
    'Lookup supposedly unique object - assert/fail if more than one is found.'
    search_results = lookup_objects(service, oio_class, **conditions)

    if len(search_results) > 0:
        # There should only be one
        assert(len(search_results) == 1)
        return search_results[0]
    else:
        return None


@request
def read_object(uuid, service, oio_class):
    '''Read object from LoRa, return JSON. Fail (throw 404) if not found.

    This function does not include more than one registration period and will
    thus return the current registration only. Within this registration period,
    all date dependent values will have the current Virkning period only.
    '''
    request_string = '{0}/{1}/{2}/{3}'.format(
        BASE_URL, service, oio_class, uuid
    )
    response = requests.get(request_string)
    object_dict = response.json()
    # Only the current registration.
    return object_dict[uuid][0]['registreringer'][0]


@request
def delete_object(uuid, service, oio_class):
    'Delete object in sevice with the given UUID'
    ALREADY_DELETED = 'Invalid [livscyklus] transition to [Slettet]'
    request_string = '{0}/{1}/{2}/{3}'.format(
        BASE_URL, service, oio_class, uuid
    )
    response = requests.delete(request_string)
    if response.status_code == 400 and ALREADY_DELETED in response.text:
        # Already deleted, this is OK
        print('Deleting object {} again'.format(uuid))
        response = True
    return response


# Lookup one
lookup_organisation = functools.partial(
    lookup_one, service='organisation', oio_class='organisation'
)
lookup_bruger = functools.partial(
    lookup_one, service='organisation', oio_class='bruger'
)
lookup_interessefaellesskab = functools.partial(
    lookup_one, service='organisation', oio_class='interessefaellesskab'
)

# Lookup many
lookup_organisationfunktioner = functools.partial(
    lookup_objects, service='organisation', oio_class='organisationfunktion'
)
lookup_indsatser = functools.partial(
    lookup_objects, service='indsats', oio_class='indsats'
)


def create_virkning(frm=datetime.datetime.now(),
                    to="infinity",
                    user=SYSTEM_USER,
                    note=""):
    virkning = {
        "from": str(frm),
        "to": str(to),
        "aktoerref": user,
        "aktoertypekode": "Bruger",
        "notetekst": note
    }

    return virkning


Relation = collections.namedtuple('Relation', 'mode value')

org_default_state = {"gyldighed": "Aktiv"}


def create_object_dict(class_name, properties, relations, note,
                       states=org_default_state, virkning=None):
    '''Create a dictionary for updating or creating an OIO object.

    Note, "properties" should really be "attributes", but we'll not handle this
    level of nesting here.

    The parameter relations should be a dictionary mapping relation names to
    Relation values as specified above.
    '''

    if not virkning:
        virkning = create_virkning()
    object_dict = {
        "note": note,
        "attributter": {
            "{}egenskaber".format(class_name): [
                {
                    **properties,
                    **{"virkning": virkning}
                }
            ]
        },
        "tilstande": {
            "{}{}".format(class_name, state_name): [
                {
                    state_name: state_value,
                    "virkning": virkning
                }
            ] for state_name, state_value in states.items()
        },
        "relationer": {
            name: [
                {
                    relation.mode: relation.value,
                    "virkning": virkning
                } for relation in rels
            ] for name, rels in relations.items()
        }
    }
    return object_dict


@request
def create_organisation(cvr_number, key, name, master_id, phone="", email="",
                        mobile="", fax="", address_uuid="", company_type="",
                        industry_code="", note=""):
    # Sanity check
    urn = 'urn:{}'.format(cvr_number)
    uuid = lookup_organisation(virksomhed=urn)

    if uuid:
        print("{0} already exists with UUID {1}".format(cvr_number, uuid))
        return DummyResult(uuid)
    properties = dict(brugervendtnoegle=key, organisationsnavn=name,
                      ava_master_id=master_id)
    # In order to calculate relations, calculate address list.
    adresser = []
    if phone:
        adresser.append(Relation("urn", "urn:tel:{0}".format(phone)))
    if mobile:
        adresser.append(Relation("urn", "urn:mobile:{0}".format(phone)))
    if email:
        adresser.append(Relation("urn", "urn:email:{0}".format(email)))
    if address_uuid:
        adresser.append(Relation("uuid", address_uuid))

    relations = dict(
        tilhoerer=[Relation("uuid", AVA_ORGANISATION)],
        virksomhed=[Relation("urn", "urn:{0}".format(cvr_number))],
        adresser=adresser
    )

    organisation_dict = create_object_dict("organisation", properties,
                                           relations, note)

    if company_type:
        organisation_dict['relationer']['virksomhedstype'] = [{
            "urn": "urn:{0}".format(company_type),
            "virkning": create_virkning()
        }]

    if industry_code:
        organisation_dict['relationer']['branche'] = [{
            "urn": "urn:{0}".format(industry_code),
            "virkning": create_virkning()
        }]

    url = "{0}/organisation/organisation".format(BASE_URL)
    response = requests.post(url, json=organisation_dict)

    return response


@request
def create_bruger(cpr_number, key, name, master_id, phone="", email="",
                  mobile="", fax="", first_name="", middle_name="",
                  last_name="", address_uuid="", gender="", marital_status="",
                  address_protection="", note=""):

    # Sanity check
    urn = 'urn:{}'.format(cpr_number)
    uuid = lookup_bruger(tilknyttedepersoner=urn)
    if uuid:
        print("{0} already exists with UUID {1}".format(cpr_number, uuid))
        return DummyResult(uuid)

    properties = dict(
        brugervendtnoegle=key, brugernavn=name, ava_fornavn=first_name,
        ava_mellemnavn=middle_name, ava_efternavn=last_name,
        ava_civilstand=marital_status, ava_koen=gender,
        ava_adressebeskyttelse=address_protection, ava_masterid=master_id
    )
    # In order to calculate relations, calculate address list.
    adresser = []
    if phone:
        adresser.append(Relation("urn", "urn:tel:{0}".format(phone)))
    if mobile:
        adresser.append(Relation("urn", "urn:mobile:{0}".format(phone)))
    if email:
        adresser.append(Relation("urn", "urn:email:{0}".format(email)))
    if address_uuid:
        adresser.append(Relation("uuid", address_uuid))

    relations = dict(
        tilhoerer=[Relation("uuid", AVA_ORGANISATION)],
        tilknyttedepersoner=[Relation("urn", "urn:{0}".format(cpr_number))],
        adresser=adresser
    )

    bruger_dict = create_object_dict("bruger", properties, relations, note)

    url = "{0}/organisation/bruger".format(BASE_URL)
    response = requests.post(url, json=bruger_dict)

    return response


def create_interessefaellesskab(customer_number, customer_relation_name,
                                customer_type, address_uuid, note=""):
    properties = dict(brugervendtnoegle=customer_number,
                      interessefaellesskabsnavn=customer_relation_name,
                      interessefaellesskabstype=customer_type)
    adresser = []
    if address_uuid:
        adresser.append(Relation("uuid", address_uuid))
    relations = dict(tilhoerer=[Relation("uuid", AVA_ORGANISATION)],
                     adresser=adresser)
    interessefaellesskab_dict = create_object_dict("interessefaellesskab",
                                                   properties, relations, note)

    url = "{0}/organisation/interessefaellesskab".format(BASE_URL)
    response = requests.post(url, json=interessefaellesskab_dict)

    return response


def create_organisationfunktion(customer_uuid,
                                customer_relation_uuid,
                                role, note=""):
    numeric_role = ROLE_MAP[role]

    properties = dict(brugervendtnoegle=numeric_role, funktionsnavn=role)
    relations = dict(
        organisatoriskfunktionstype=[Relation("urn",
                                              "urn:{0}".format(numeric_role))],
        tilknyttedeinteressefaellesskaber=[Relation("uuid",
                                                    customer_relation_uuid)],
        tilknyttedebrugere=[Relation("uuid", customer_uuid)]
    )

    organisationfunktion_dict = create_object_dict("organisationfunktion",
                                                   properties, relations, note)

    url = "{0}/organisation/organisationfunktion".format(BASE_URL)
    response = requests.post(url, json=organisationfunktion_dict)

    return response


@request
def create_indsats(name, agreement_type, no_of_products, invoice_address,
                   start_date, end_date, location,
                   customer_relation_uuid, product_uuids, note=""):
    tz = pytz.timezone('Europe/Copenhagen')
    starttidspunkt = tz.localize(start_date)
    try:
        sluttidspunkt = tz.localize(end_date)
    except:  # noqa
        # This is only for Max date - which is 9999-12-31 =~ infinity
        sluttidspunkt = pytz.utc.localize(end_date)
    properties = dict(brugervendtnoegle=name, beskrivelse=no_of_products,
                      starttidspunkt=str(starttidspunkt),
                      sluttidspunkt=str(sluttidspunkt))
    states = dict(fremdrift="Disponeret", publiceret="IkkePubliceret")
    relations = dict(
        indsatstype=[Relation("urn", "urn:{0}".format(agreement_type))],
        indsatsmodtager=[Relation("uuid", customer_relation_uuid)],
        indsatskvalitet=[Relation("uuid", p) for p in product_uuids]
    )

    indsats_dict = create_object_dict("indsats", properties, relations, note,
                                      states=states)
    if invoice_address:
        indsats_dict['relationer']['indsatsdokument'] = [
            {
                "uuid": invoice_address,
                "virkning": create_virkning()
            }
        ]

    url = "{0}/indsats/indsats".format(BASE_URL)
    response = requests.post(url, json=indsats_dict)

    return response


@request
def create_klasse(name, identification, installation_type,
                  meter_number, meter_type, start_date, end_date,
                  product_address, note=""):
    virkning = create_virkning(start_date, end_date)
    properties = dict(brugervendtnoegle=identification, titel=name,
                      eksempel=meter_number, beskrivelse=meter_type)
    states = dict(publiceret="Publiceret")
    relations = dict(
        ejer=[Relation("uuid", AVA_ORGANISATION)],
        overordnetklasse=[Relation("urn", "urn:{0}".format(installation_type))]
    )

    klasse_dict = create_object_dict("klasse", properties, relations, note,
                                     states=states, virkning=virkning)
    if product_address:
        klasse_dict['relationer']['ava_opstillingsadresse'] = [
            {
                "uuid": product_address,
                "virkning": virkning
            }
        ]
    url = "{0}/klassifikation/klasse".format(BASE_URL)
    response = requests.post(url, json=klasse_dict)
    return response
