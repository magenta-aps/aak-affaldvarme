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
from dateutil import parser

from settings import SYSTEM_USER, AVA_ORGANISATION, BASE_URL

session = requests.Session()
session.verify = '/etc/ssl/certs/ca-certificates.crt'


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


def request(func):
    def call_and_raise(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            result.raise_for_status()
        return result
    return call_and_raise


@request
def create_organisation(cvr_number, key, name, phone="", email="",
                        mobile="", fax="", address_uuid="", company_type="",
                        industry_code="", note=""):
    # Sanity check
    uuid = lookup_organisation(cvr_number)
    if uuid:
        print("{0} already exists with UUID {1}".format(cvr_number, uuid))

    virkning = create_virkning()
    organisation_dict = {
        "note": note,
        "attributter": {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": key,
                    "organisationsnavn": name,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning
                },
            ],
            "virksomhed": [
                {
                    "urn": "urn:{0}".format(cvr_number),
                    "virkning": virkning
                }
            ],
            "adresser": [

            ]
        }
    }

    if company_type:
        organisation_dict['relationer']['virksomhedstype'] = [{
            "urn": "urn:{0}".format(company_type),
            "virkning": virkning
        }]

    if industry_code:
        organisation_dict['relationer']['branche'] = [{
            "urn": "urn:{0}".format(industry_code),
            "virkning": virkning
        }]

    if phone:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:tel:{0}".format(phone),
                "virkning": virkning
            }
        )
    if email:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:email:{0}".format(email),
                "virkning": virkning
            }
        )
    if address_uuid:
        organisation_dict['relationer']['adresser'].append(
            {
                "uuid": address_uuid,
                "virkning": virkning
            }
        )
    url = "{0}/organisation/organisation".format(BASE_URL)
    response = session.post(url, json=organisation_dict)

    return response


def lookup_organisation(id_number):
    request_string = (
        "{0}/organisation/organisation?virksomhed=urn:{1}".format(
            BASE_URL, id_number
        )
    )

    result = session.get(request_string)

    if result:
        search_results = result.json()['results'][0]

    if len(search_results) > 0:
        # There should only be one
        assert(len(search_results) == 1)
        return search_results[0]


@request
def create_bruger(cpr_number, key, name, phone="", email="",
                  mobile="", fax="", first_name="", middle_name="",
                  last_name="", address_uuid="", gender="", marital_status="",
                  address_protection="", note=""):

    # Sanity check
    uuid = lookup_bruger(cpr_number)
    if uuid:
        print("{0} already exists with UUID {1}".format(cpr_number, uuid))

    virkning = create_virkning()
    bruger_dict = {
        "note": note,
        "attributter": {
            "brugeregenskaber": [
                {
                    "brugervendtnoegle": key,
                    "brugernavn": name,
                    "ava_fornavn": first_name,
                    "ava_mellemnavn": middle_name,
                    "ava_efternavn": last_name,
                    "ava_civilstand": marital_status,
                    "ava_koen": gender,
                    "ava_adressebeskyttelse": address_protection,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "brugergyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
            "tilknyttedepersoner": [
                {
                    "urn": "urn:{0}".format(cpr_number),
                    "virkning": virkning
                }
            ],
            "adresser": [

            ]
        }
    }

    if phone:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:tel:{0}".format(phone),
                "virkning": virkning
            }
        )
    if email:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:email:{0}".format(email),
                "virkning": virkning
            }
        )
    if address_uuid:
        bruger_dict['relationer']['adresser'].append(
            {
                "uuid": address_uuid,
                "virkning": virkning
            }
        )
    if mobile:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:mobile:{0}".format(mobile),
                "virkning": virkning
            }
        )

    url = "{0}/organisation/bruger".format(BASE_URL)
    response = session.post(url, json=bruger_dict)

    return response


def lookup_bruger(id_number):
    request_string = (
        "{0}/organisation/bruger?tilknyttedepersoner=urn:{1}".format(
            BASE_URL, id_number
        )
    )

    result = session.get(request_string)

    if result:
        search_results = result.json()['results'][0]
    else:
        # TODO: What to do? Network error. Ignore and assume it will work next
        # time.
        return None

    if len(search_results) > 0:
        # There should only be one
        if len(search_results) > 1:
            print("Denne bruger findes {0} gange: {1}".format(
                len(search_results), id_number)
            )
        return search_results[0]


def create_interessefaellesskab(customer_number, customer_relation_name,
                                customer_type, note=""):
    virkning = create_virkning()
    interessefaellesskab_dict = {
        "note": note,
        "attributter": {
            "interessefaellesskabegenskaber": [
                {
                    "brugervendtnoegle": customer_number,
                    "interessefaellesskabsnavn": customer_relation_name,
                    "interessefaellesskabstype": customer_type,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "interessefaellesskabgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
        }
    }

    url = "{0}/organisation/interessefaellesskab".format(BASE_URL)
    response = session.post(url, json=interessefaellesskab_dict)

    return response


def create_organisationfunktion(customer_number,
                                customer_uuid,
                                customer_relation_uuid,
                                role, note=""):
    virkning = create_virkning()
    organisationfunktion_dict = {
        "note": note,
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "brugervendtnoegle": " ".join([role, customer_number]),
                    "funktionsnavn": role,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationfunktiongyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "urn": "urn:{0}".format(role),
                    "virkning": virkning
                }
            ],
            "tilknyttedeinteressefaellesskaber": [
                {
                    "uuid": customer_relation_uuid,
                    "virkning": virkning
                },
            ],
            "tilknyttedebrugere": [
                {
                    "uuid": customer_uuid,
                    "virkning": virkning
                },
            ]
        }
    }

    url = "{0}/organisation/organisationfunktion".format(BASE_URL)
    response = session.post(url, json=organisationfunktion_dict)

    return response


@request
def create_indsats(name, agreement_type, no_of_products, invoice_address,
                   address, start_date, end_date, location,
                   customer_relation_uuid, product_uuids, note=""):
    virkning = create_virkning()
    tz = pytz.timezone('Europe/Copenhagen')
    starttidspunkt = tz.localize(start_date)
    try:
        sluttidspunkt = timezone.localize(end_date)
    except:  # noqa
        # This is only for Max date - which is 9999-12-31 =~ infinity
        sluttidspunkt = pytz.utc.localize(end_date)
    indsats_dict = {
        "note": note,
        "attributter": {
            "indsatsegenskaber": [
                {
                    "brugervendtnoegle": name,
                    "beskrivelse": no_of_products,
                    "starttidspunkt": str(starttidspunkt),
                    "sluttidspunkt": str(sluttidspunkt),
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "indsatsfremdrift": [{
                "fremdrift": "Disponeret",
                "virkning": virkning
            }],
            "indsatspubliceret": [{
                "publiceret": "IkkePubliceret",
                "virkning": virkning
            }]
        },
        "relationer": {
            "indsatstype": [
                {
                    "urn": "urn:{0}".format(agreement_type),
                    "virkning": virkning
                }
            ],
            "indsatsmodtager": [
                {
                    "uuid": customer_relation_uuid,
                    "virkning": virkning
                }
            ],
            "indsatskvalitet": [
                {
                    "uuid": p,
                    "virkning": virkning
                }
                for p in product_uuids
            ]
        }
    }

    if invoice_address:
        indsats_dict['relationer']['indsatsdokument'] = [
            {
                "uuid": invoice_address,
                "virkning": virkning
            }
        ]
    """
    if address:
        indsats_dict['relationer']['indsatssag'] = [
            {
                "uuid": address,
                "virkning": virkning
            }
        ]
    """
    url = "{0}/indsats/indsats".format(BASE_URL)
    response = session.post(url, json=indsats_dict)

    return response


@request
def create_klasse(name, identification, installation_type,
                  meter_number, meter_type, start_date, end_date, note=""):
    virkning = create_virkning(start_date, end_date)
    klasse_dict = {
        "note": note,
        "attributter": {
            "klasseegenskaber": [
                {
                    "brugervendtnoegle": identification,
                    "titel": name,
                    "eksempel": meter_number,
                    "beskrivelse": meter_type,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "klassepubliceret": [{
                "publiceret": "Publiceret",
                "virkning": virkning
            }]
        },
        "relationer": {
            "ejer": [{
                "uuid": AVA_ORGANISATION,
                "virkning": virkning,
                "objekttype": "Organisation",
            }],
            "overordnetklasse": [{
                "urn": "urn:{0}".format(installation_type),
                "virkning": virkning
            }]
        }
    }

    url = "{0}/klassifikation/klasse".format(BASE_URL)
    response = session.post(url, json=klasse_dict)
    return response
