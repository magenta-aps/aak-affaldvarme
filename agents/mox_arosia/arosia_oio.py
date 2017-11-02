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

from services import get_address_uuid, get_cpr_data, get_cvr_data, report_error
from settings import AVA_ORGANISATION, BASE_URL, SYSTEM_USER

"""
Contains all logic of interacting with LoRa
"""

s = requests.Session()


def create_virkning(frm=None,
                    to="infinity",
                    user=SYSTEM_USER,
                    note=""):
    if frm is None:
        frm = datetime.datetime.now()

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


def lookup_unique(request_string):
    """
    Perform lookup in LoRa using given request string and return result, if any
    ensuring that only one result is found.
    """
    result = s.get(request_string)

    if result:
        search_results = result.json()['results'][0]

        if len(search_results) > 0:
            # There should only be one
            if len(search_results) > 1:
                report_error(
                    "More than one result found for request ({0})".format(
                        request_string))
                pass
            return search_results[0]


def extract_cvr_and_update_lora(id_number, key="", phone="", email="", note="",
                                arosia_id="", sms_notif=""):
    """
    Extracts missing CVR data from SP, and updates LoRa
    """
    # Collect info from SP and include in call creating user.
    # Avoid getting throttled by SP
    company_dir = get_cvr_data(id_number)

    name = company_dir['organisationsnavn']
    address_uuid = company_dir['dawa_uuid']
    company_type = company_dir['virksomhedsform']
    industry_code = company_dir['branchekode']

    return create_or_update_organisation(
        cvr_number=id_number,
        key=key,
        name=name,
        arosia_phone=phone,
        arosia_email=email,
        address_uuid=address_uuid,
        company_type=company_type,
        industry_code=industry_code,
        note=note,
        arosia_id=arosia_id,
        sms_notif=sms_notif
    )


def generate_organisation_dict(cvr_number, key, name, arosia_phone="",
                               arosia_email="", kmdee_phone="",
                               kmdee_email="", address_uuid="",
                               company_type="", industry_code="", note="",
                               arosia_id="", sms_notif=""):
    """
    Generates a 'Organisation' dict for inserting into LoRa
    """
    virkning = create_virkning()
    organisation_dict = {
        "note": note,
        "attributter": {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": key,
                    "organisationsnavn": name,
                    "ava_sms_notifikation": sms_notif,
                    "virkning": virkning,
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

    if arosia_phone:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_tel:{0}".format(arosia_phone),
                "virkning": virkning
            }
        )
    if arosia_email:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_email:{0}".format(arosia_email),
                "virkning": virkning
            }
        )
    if kmdee_phone:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:tel:{0}".format(kmdee_phone),
                "virkning": virkning
            }
        )
    if kmdee_email:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:email:{0}".format(kmdee_email),
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
    if arosia_id:
        organisation_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_id:{0}".format(arosia_id),
                "virkning": virkning
            }
        )

    return organisation_dict


def lookup_organisation(id_number):
    """
    Check for the existance of an organisation object in LoRa
    with the given CVR
    :param id_number: A CVR number
    :return: UUID of the found object, else None
    """
    request_string = (
        "{0}/organisation/organisation?virksomhed=urn:{1}".format(
            BASE_URL, id_number
        )
    )

    return lookup_unique(request_string)


@request
def create_or_update_organisation(cvr_number, key, name, arosia_phone="",
                                  arosia_email="", kmdee_phone="",
                                  kmdee_email="", address_uuid="",
                                  company_type="", industry_code="", note="",
                                  arosia_id="", sms_notif=""):
    uuid = lookup_organisation(cvr_number)
    organisation_dict = generate_organisation_dict(cvr_number, key, name,
                                                   arosia_phone,
                                                   arosia_email,
                                                   kmdee_phone, kmdee_email,
                                                   address_uuid,
                                                   company_type, industry_code,
                                                   note,
                                                   arosia_id,
                                                   sms_notif)
    if uuid:
        print("{0} already exists with UUID {1}".format(cvr_number, uuid))
        url = "{0}/organisation/organisation/{1}".format(BASE_URL, uuid)
        return s.put(url, json=organisation_dict)
    else:
        url = "{0}/organisation/organisation".format(BASE_URL)
        return s.post(url, json=organisation_dict)


def extract_cpr_and_update_lora(id_number, key="", name="", phone="", email="",
                                note="", arosia_id="", sms_notif=""):
    # Collect info from SP and include in call creating user.
    person_dir = get_cpr_data(id_number)
    if not person_dir:
        return

    first_name = person_dir['fornavn']
    middle_name = person_dir.get('mellemnavn', '')
    last_name = person_dir['efternavn']

    # Address related stuff
    address = {
        "vejnavn": person_dir["vejnavn"],
        "postnr": person_dir["postnummer"]
    }
    if "etage" in person_dir:
        address["etage"] = person_dir["etage"].lstrip('0')
    if "sidedoer" in person_dir:
        address["dør"] = person_dir["sidedoer"].lstrip('0')
    if "husnummer" in person_dir:
        address["husnr"] = person_dir["husnummer"]

    try:
        address_uuid = get_address_uuid(address)
    except Exception as e:
        report_error(
            "Unable to lookup_unique address for customer: {0}".format(
                id_number
            ), error_stack=None, error_object=address
        )
        address_uuid = None

    gender = person_dir['koen']
    marital_status = person_dir['civilstand']
    address_protection = person_dir['adressebeskyttelse']

    return create_or_update_bruger(
        cpr_number=id_number,
        key=key,
        name=name,
        arosia_phone=phone,
        arosia_email=email,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        address_uuid=address_uuid,
        gender=gender,
        marital_status=marital_status,
        address_protection=address_protection,
        note=note,
        arosia_id=arosia_id,
        sms_notif=sms_notif
    )


def generate_bruger_dict(cpr_number, key, name, arosia_phone="",
                         arosia_email="", kmdee_phone="", kmdee_email="",
                         first_name="", middle_name="", last_name="",
                         address_uuid="", gender="", marital_status="",
                         address_protection="", note="", arosia_id="",
                         sms_notif=""):
    """
    Generates a 'Bruger' dict for inserting into LoRa
    """
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
                    "ava_sms_notifikation": sms_notif,
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

    if arosia_phone:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_tel:{0}".format(arosia_phone),
                "virkning": virkning
            }
        )
    if arosia_email:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_email:{0}".format(arosia_email),
                "virkning": virkning
            }
        )
    if kmdee_phone:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:tel:{0}".format(kmdee_phone),
                "virkning": virkning
            }
        )
    if kmdee_email:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:email:{0}".format(kmdee_email),
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
    if arosia_id:
        bruger_dict['relationer']['adresser'].append(
            {
                "urn": "urn:arosia_id:{0}".format(arosia_id),
                "virkning": virkning
            }
        )

    return bruger_dict


def lookup_bruger(id_number):
    request_string = (
        "{0}/organisation/bruger?tilknyttedepersoner=urn:{1}".format(
            BASE_URL, id_number
        )
    )

    return request(request_string)


@request
def create_or_update_bruger(cpr_number, key, name, arosia_phone="",
                            arosia_email="", kmdee_phone="", kmdee_email="",
                            first_name="", middle_name="", last_name="",
                            address_uuid="", gender="", marital_status="",
                            address_protection="", note="", arosia_id="",
                            sms_notif=""):
    uuid = lookup_bruger(cpr_number)

    bruger_dict = generate_bruger_dict(
        cpr_number=cpr_number,
        key=key,
        name=name,
        arosia_phone=arosia_phone,
        arosia_email=arosia_email,
        kmdee_phone=kmdee_phone,
        kmdee_email=kmdee_email,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        address_uuid=address_uuid,
        gender=gender,
        marital_status=marital_status,
        address_protection=address_protection,
        note=note,
        arosia_id=arosia_id,
        sms_notif=sms_notif
    )

    if uuid:
        print("{0} already exists with UUID {1}".format(cpr_number, uuid))
        url = "{0}/organisation/bruger/{1}".format(BASE_URL, uuid)
        return s.put(url, json=bruger_dict)
    else:
        url = "{0}/organisation/bruger".format(BASE_URL)
        return s.post(url, json=bruger_dict)


def generate_interessefaellesskab_dict(customer_number, customer_relation_name,
                                       customer_type, arosia_id, note):
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

    if arosia_id:
        interessefaellesskab_dict['relationer']['ava_arosia_id'] = [{
            "urn": "urn:arosia_id:{0}".format(arosia_id),
            "virkning": virkning
        }]

    return interessefaellesskab_dict


def lookup_interessefaellesskab(customer_number):
    request_string = (
        "{0}/organisation/interessefaellesskab?bvn={1}".format(
            BASE_URL, customer_number
        )
    )

    return request(request_string)


def create_or_update_interessefaellesskab(customer_number,
                                          customer_relation_name,
                                          customer_type, arosia_id="", note=""):
    uuid = lookup_interessefaellesskab(customer_number)

    interessefaellesskab_dict = generate_interessefaellesskab_dict(
        customer_number, customer_relation_name, customer_type, arosia_id, note)

    if uuid:
        url = "{0}/organisation/interessefaellesskab/{1}".format(BASE_URL, uuid)
        response = s.put(url, json=interessefaellesskab_dict)
    else:
        url = "{0}/organisation/interessefaellesskab".format(BASE_URL)
        response = s.post(url, json=interessefaellesskab_dict)

    return response


def generate_organisationfunktion_dict(customer_number, customer_uuid,
                                       customer_relation_uuid, role, note):
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

    return organisationfunktion_dict


def lookup_organisationfunktion(role, customer_number):
    key = " ".join([role, customer_number])
    request_string = (
        "{0}/organisation/organisationfunktion?bvn={1}".format(
            BASE_URL, key
        )
    )

    return request(request_string)


@request
def create_or_update_organisationfunktion(customer_number,
                                          customer_uuid,
                                          customer_relation_uuid,
                                          role, note=""):
    uuid = lookup_organisationfunktion(customer_number, role)
    organisationfunktion_dict = generate_organisationfunktion_dict(
        customer_number,
        customer_uuid,
        customer_relation_uuid,
        role, note)

    if uuid:
        url = "{0}/organisation/organisationfunktion/{1}".format(BASE_URL, uuid)
        return s.put(url, json=organisationfunktion_dict)
    else:
        url = "{0}/organisation/organisationfunktion".format(BASE_URL)
        return s.post(url, json=organisationfunktion_dict)


def generate_indsats_dict(name, agreement_type, no_of_products,
                          invoice_address,
                          start_date, end_date, customer_relation_uuid,
                          product_uuids,
                          note):
    virkning = create_virkning()
    tz = pytz.timezone('Europe/Copenhagen')

    starttidspunkt = None
    if start_date:
        starttidspunkt = str(tz.localize(start_date))

    sluttidspunkt = None
    if end_date:
        try:
            sluttidspunkt = str(tz.localize(end_date))
        except:
            # This is only for Max date - which is 9999-12-31 =~ infinity
            sluttidspunkt = str(pytz.utc.localize(end_date))

    indsats_dict = {
        "note": note,
        "attributter": {
            "indsatsegenskaber": [
                {
                    "brugervendtnoegle": name,
                    "beskrivelse": no_of_products,
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

    if starttidspunkt:
        indsats_dict['attributter']['indsatsegenskaber'][0][
            'starttidspunkt'] = starttidspunkt

    if sluttidspunkt:
        indsats_dict['attributter']['indsatsegenskaber'][0][
            'sluttidspunkt'] = sluttidspunkt

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

    return indsats_dict


def lookup_indsats(name):
    request_string = (
        "{0}/indsats/indsats?bvn={1}".format(
            BASE_URL, name
        )
    )

    return request(request_string)


@request
def create_or_update_indsats(name, agreement_type, no_of_products,
                             start_date, end_date, customer_relation_uuid,
                             product_uuids,
                             invoice_address="",
                             note=""):
    uuid = lookup_indsats(name)
    indsats_dict = generate_indsats_dict(name, agreement_type, no_of_products,
                                         invoice_address,
                                         start_date, end_date,
                                         customer_relation_uuid,
                                         product_uuids,
                                         note)

    if uuid:
        url = "{0}/indsats/indsats/{1}".format(BASE_URL, uuid)
        return s.put(url, json=indsats_dict)
    else:
        url = "{0}/indsats/indsats".format(BASE_URL)
        return s.post(url, json=indsats_dict)


def generate_klasse_dict(afhentningstype, arosia_id, identification,
                         installation_type, meter_number, name, note,
                         aftale_id):
    virkning = create_virkning()
    klasse_dict = {
        "note": note,
        "attributter": {
            "klasseegenskaber": [
                {
                    "brugervendtnoegle": identification,
                    "titel": name,
                    "eksempel": meter_number,
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
    if arosia_id:
        klasse_dict['relationer']['ava_arosia_id'] = [{
            "urn": "urn:arosia_id:{0}".format(arosia_id),
            "virkning": virkning
        }]
    if afhentningstype:
        klasse_dict['relationer']['ava_afhentningstype'] = [{
            "urn": "urn:arosia_id:{0}".format(afhentningstype),
            "virkning": virkning
        }]
    if aftale_id:
        klasse_dict['relationer']['ava_aftale_id'] = [{
            "urn": "urn:ava_aftale_id:{0}".format(aftale_id),
            "virkning": virkning
        }]

    return klasse_dict


def lookup_klasse(identification):
    request_string = (
        "{0}/klassifikation/klasse?bvn={1}".format(
            BASE_URL, identification
        )
    )

    return request(request_string)


@request
def create_or_update_klasse(name, identification, installation_type,
                            meter_number="", note="", arosia_id="",
                            afhentningstype="", aftale_id=""):
    uuid = lookup_klasse(identification)

    klasse_dict = generate_klasse_dict(afhentningstype, arosia_id,
                                       identification, installation_type,
                                       meter_number, name, note, aftale_id)

    if uuid:
        url = "{0}/klassifikation/klasse/{1}".format(BASE_URL, uuid)
        return s.put(url, json=klasse_dict)
    else:
        url = "{0}/klassifikation/klasse".format(BASE_URL)
        return s.post(url, json=klasse_dict)


def lookup_bruger_by_arosia_id(contact_id):
    request_string = (
        "{0}/organisation/bruger?adresser=urn:arosia_id:{1}".format(
            BASE_URL, contact_id
        )
    )
    return lookup_unique(request_string)


def lookup_organisation_by_arosia_id(contact_id):
    request_string = (
        "{0}/organisation/organisation?adresser=urn:arosia_id:{1}".format(
            BASE_URL, contact_id
        )
    )
    return lookup_unique(request_string)


def lookup_contact_by_arosia_id(contact_id):
    uuid = lookup_bruger_by_arosia_id(contact_id)
    if not uuid:
        uuid = lookup_organisation_by_arosia_id(contact_id)

    return uuid


def lookup_account_arosia_id(account_id):
    request_string = (
        "{0}/organisation/interessefaellesskab?ava_arosia_id=urn:arosia_id:{1}".format(
            BASE_URL, account_id
        )
    )
    return lookup_unique(request_string)


def lookup_products_by_aftale_id(aftale_id):
    request_string = (
        "{0}/klassifikation/klasse?ava_aftale_id=urn:arosia_id:{1}".format(
            BASE_URL, aftale_id
        )
    )
    result = s.get(request_string)
    if result:
        return result.json()['results'][0]
