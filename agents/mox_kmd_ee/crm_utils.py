'Utility functions etc. based on the CRM data model and mapped to LoRa.'
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

from ee_oio import lookup_organisation, lookup_bruger, lookup_organisation
from ee_oio import lookup_interessefaellesskab, lookup_organisationfunktioner
from ee_oio import lookup_indsats, delete_object, create_klasse
from ee_oio import create_organisation, create_bruger, create_indsats
from ee_oio import create_interessefaellesskab, create_organisationfunktion
from ee_utils import is_cvr, is_cpr


# Delete functions
delete_customer_relation = functools.partial(
    delete_object, service='organisation', oio_class='interessefaellesskab'
)
delete_customer_role = functools.partial(
    delete_object, service='organisation', oio_class='organisationfunktion'
)
delete_agreement = functools.partial(
    delete_object, service='organisation', oio_class='indsats'
)
delete_product = functools.partial(
    delete_object, service='klassifikation', oio_class='klasse'
)


# Lookup of one object
def lookup_customer_from_cvr(id_number):
    'Look up customer (organisation) from the CVR number of its Virksomhed.'
    urn = 'urn:{}'.format(id_number)
    return lookup_organisation(virksomhed=urn)


def lookup_customer_from_cpr(id_number):
    'Look up customer (user) from CPR number.'
    urn = 'urn:{}'.format(id_number)
    return lookup_bruger(tilknyttedepersoner=urn)


def lookup_customer(id_number):
    if is_cpr(id_number):
        return lookup_customer_from_cpr(id_number)
    elif is_cvr(id_number):
        return lookup_customer_from_cvr(id_number)


def lookup_customer_relation(customer_number):
    'Look up customer relations belonging to customer number.'
    return lookup_interessefaellesskab(brugervendtnoegle=customer_number)


# Lookup of more than one object
def lookup_customer_roles(customer_relation):
    return lookup_organisationfunktioner(
        tilknyttedeinteressefaellesskaber=customer_relation
    )


def lookup_agreements(customer_relation):
    'Lookup agreement(s) for customer relation.'
    return lookup_indsatser(indsatsmodtager=customer_relation)


def lookup_products(agreement):
    'Get products for this agreement.'
    # FIXME: This is bothersome, because we actually have to load the agreement
    # to find the products. The correct way would be to do as we do in Arosia
    # and have an AVA specific relation from Klasse to Indsats.


# Create functions
def create_customer(id_number, key, name, master_id, phone="", email="",
                    mobile="", fax="", note=""):

    if is_cvr(id_number):

        # Collect info from SP and include in call creating user.
        # Avoid getting throttled by SP
        try:
            company_dir = get_cvr_data(id_number)
        except Exception as e:
            # Retry *once*
            try:
                company_dir = get_cvr_data(id_number)
            except Exception as e:
                report_error(
                    "CVR number not found: {0}".format(id_number)
                )
                return None

        name = company_dir['organisationsnavn']
        address_uuid = company_dir['dawa_uuid']
        company_type = company_dir['virksomhedsform']
        industry_code = company_dir['branchekode']
        address_string = "{0} {1}, {2}".format(
            company_dir['vejnavn'], company_dir['husnummer'],
            company_dir['postnummer']
        )

        result = create_organisation(
            id_number, key, name, master_id, phone, email, mobile, fax,
            address_uuid, company_type, industry_code, note
        )
    elif is_cpr(id_number):
        # This is a CPR number

        # Collect info from SP and include in call creating user.
        # Avoid getting throttled by SP
        try:
            person_dir = get_cpr_data(id_number)
        except Exception as e:
            # Deprecate:
            # report_error(traceback.format_exc())

            # Print to screen instead
            error_message = "SP CPR Lookup failed for ID: {0}".format(
                id_number
            )

            # Retry *once*
            try:
                person_dir = get_cpr_data(id_number)
            except Exception as e:
                # Hotfix:
                print("CPR lookukup failed after retrying, logging error")
                # Certain CPR ID's are actually P-Numbers
                # These must be manually processed
                report_error(
                    error_message=error_message,
                    error_stack=e,
                    error_object=id_number
                )
                return None

        first_name = person_dir['fornavn']
        middle_name = person_dir.get('mellemnavn', '')
        last_name = person_dir['efternavn']

        # Address related stuff
        address = {
            "vejnavn": person_dir["vejnavn"]
        }

        # Hotfix:
        if "postnummer" in person_dir:
            address["postnr"] = person_dir["postnummer"]

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
                "Unable to lookup address for customer: {0}".format(
                    id_number
                ), error_stack=None, error_object=address
            )
            address_uuid = None

        # Cache address for customer relation
        address_string = "{0}".format(
            person_dir['standardadresse']
        )

        # Hotfix:
        if 'postnummer' in person_dir:
            address_string += ", {0}".format(person_dir['postnummer'])

        gender = person_dir['koen']
        marital_status = person_dir['civilstand']
        address_protection = person_dir['adressebeskyttelse']

        result = create_bruger(
            id_number, key, name, master_id, phone, email, mobile, fax,
            first_name, middle_name, last_name, address_uuid, gender,
            marital_status, address_protection, note
        )
    else:
        report_error("Forkert CPR/SE-nr for {0}: {1}".format(
            name, id_number)
        )
        # Invalid customer
        return None

    if result:

        return result.json()['uuid']


def create_customer_role(customer_uuid, customer_relation_uuid, role):
    "Create an OrgFunktion from this info and return UUID"
    result = create_organisationfunktion(
        customer_uuid,
        customer_relation_uuid,
        role
    )

    if result:
        return result.json()['uuid']


def create_customer_relation(customer_number, customer_relation_name,
                             customer_type, address_uuid):
    "Create an Interessefællesskab from this info and return UUID"
    result = create_interessefaellesskab(
        customer_number,
        customer_relation_name,
        customer_type,
        address_uuid
    )
    if result:
        return result.json()['uuid']


def create_agreement(name, agreement_type, no_of_products, invoice_address,
                     start_date, end_date, location,
                     customer_role_uuid, product_uuids):
    "Create an Indsats from this info and return UUID"
    result = create_indsats(name, agreement_type, no_of_products,
                            invoice_address, start_date, end_date,
                            location, customer_role_uuid, product_uuids)
    if result:
        return result.json()['uuid']


def create_product(name, identification, installation_type, meter_number,
                   meter_type, start_date, end_date, product_address):
    "Create a Klasse from this info and return UUID"
    result = create_klasse(name, identification, installation_type,
                           meter_number, meter_type, start_date, end_date,
                           product_address)
    if result:
        return result.json()['uuid']
