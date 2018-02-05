"""Utility functions etc. based on the CRM data model and mapped to LoRa."""
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools
import pytz

from collections import defaultdict

try:
    from serviceplatformen_cpr import get_cpr_data
except (TypeError, ImportError):
    """The SP CPR API wasn't configured - this can happen when testing etc."""
    def get_cpr_data(id):
        """Dummy implementation for dry runs."""
        pass

from ee_oio import lookup_bruger, lookup_organisation, lookup_klasse
from ee_oio import lookup_interessefaellesskab, lookup_organisationfunktioner
from ee_oio import lookup_organisationfunktion, lookup_indsats
from ee_oio import lookup_indsatser, delete_object, read_object, create_klasse
from ee_oio import create_organisation, create_bruger, create_indsats
from ee_oio import create_interessefaellesskab, create_organisationfunktion
from ee_oio import Relation, KUNDE, LIGESTILLINGSKUNDE
from ee_oio import write_object, write_object_dict
from ee_utils import is_cvr, is_cpr, int_str, cpr_cvr, say
from ee_utils import get_forbrugssted_address_uuid
from service_clients import report_error, get_cvr_data, get_address_uuid
from service_clients import fuzzy_address_uuid

VARME = "Varme"

# Delete functions
delete_customer_relation = functools.partial(
    delete_object, service='organisation', oio_class='interessefaellesskab'
)
delete_customer_role = functools.partial(
    delete_object, service='organisation', oio_class='organisationfunktion'
)
delete_agreement = functools.partial(
    delete_object, service='indsats', oio_class='indsats'
)
delete_product = functools.partial(
    delete_object, service='klassifikation', oio_class='klasse'
)


# Read functions
read_agreement = functools.partial(
    read_object, service='indsats', oio_class='indsats'
)


# Lookup of one object
def lookup_customer_from_cvr(id_number):
    """Look up customer from the CVR number of its Virksomhed."""
    urn = 'urn:{}'.format(id_number)
    return lookup_organisation(virksomhed=urn)


def lookup_customer_from_cpr(id_number):
    """Look up customer (user) from CPR number."""
    urn = 'urn:{}'.format(id_number)
    return lookup_bruger(tilknyttedepersoner=urn)


def lookup_customer(id_number):
    """Look up customer by ID number."""
    if is_cpr(id_number):
        return lookup_customer_from_cpr(id_number)
    elif is_cvr(id_number):
        return lookup_customer_from_cvr(id_number)


def lookup_customer_relation(customer_number):
    """Look up customer relations belonging to customer number."""
    return lookup_interessefaellesskab(brugervendtnoegle=customer_number)


def lookup_customer_role(customer_relation, role):
    """Look up customer role from customer and role specification."""
    return lookup_organisationfunktion(
        tilknyttedeinteressefaellesskaber=customer_relation,
        funktionsnavn=role
    )


def lookup_product(productid):
    """Look up product (installation and meter) from ID."""
    return lookup_klasse(brugervendtnoegle=productid)


def lookup_agreement_from_product(product_uuid):
    """Lookup agreement from the UUID of a product."""
    return lookup_indsats(indsatskvalitet=product_uuid)


# Lookup of more than one object
def lookup_customer_roles(customer_relation):
    """Find all customer roles for a given customer relation."""
    return lookup_organisationfunktioner(
        tilknyttedeinteressefaellesskaber=customer_relation
    )


def lookup_agreements(customer_relation):
    """Lookup agreement(s) for customer relation, by UUID."""
    return lookup_indsatser(indsatsmodtager=customer_relation)


def lookup_products(agreement_uuid):
    """Get products for this agreement."""
    # FIXME: This is bothersome, because we actually have to load the agreement
    # to find the products. The correct way would be to do as we do in Arosia
    # and have an AVA specific relation from Klasse to Indsats.
    agreement = read_agreement(agreement_uuid)
    indsatskvalitet = agreement['relationer'].get('indsatskvalitet', [])
    product_uuids = [r['uuid'] for r in indsatskvalitet]

    return product_uuids


# Write functions

write_agreement_dict = functools.partial(write_object_dict, service='indsats',
                                         oio_class='indsats')


def add_product_to_agreement(product_uuid, agreement_uuid):
    """Add product to agreement."""
    relations = {'indsatskvalitet': [Relation('uuid', product_uuid)]}
    write_object(agreement_uuid, {}, relations, 'indsats', 'indsats')


# Address lookup
def lookup_address_from_sp_data(sp_dict, id_number):
    """Lookup DAWA address from data returned by SP."""
    address = {}

    if "vejkode" in sp_dict:
        address["vejkode"] = sp_dict["vejkode"]
    if "postnummer" in sp_dict:
        address["postnr"] = sp_dict["postnummer"]

    if "etage" in sp_dict:
        address["etage"] = sp_dict["etage"].lstrip('0')
    if "sidedoer" in sp_dict:
        address["dør"] = sp_dict["sidedoer"].lstrip('0')
    if "husnummer" in sp_dict:
        address["husnr"] = sp_dict["husnummer"]

    try:
        address_uuid = get_address_uuid(address)
    except Exception as e:
        # First, determine customer type and include street name, if any.
        if is_cvr(id_number):
            customer_type = "CVR"
        else:
            customer_type = "CPR"
        if "vejnavn" in sp_dict:
            address["vejnavn"] = sp_dict["vejnavn"]

        report_error(
            "Unable to lookup address for {} from SP data ({}): {}".format(
                id_number, customer_type, str(address)
            ), error_stack=None
        )
        address_uuid = None

    return address_uuid


# Create functions
def create_customer(id_number, key, name, master_id, phone="", email="",
                    mobile="", fax="", note=""):
    """Create customer from data extracted from KMD EE."""
    if is_cvr(id_number):
        # Collect info from SP and include in call creating user.
        try:
            company_dir = get_cvr_data(id_number)
        except Exception as e:
            # Retry *once*
            try:
                company_dir = get_cvr_data(id_number)
            except Exception as e:
                say("CVR number {0} not found: {1}".format(id_number, str(e)))
                return None

        name = company_dir['organisationsnavn']
        address_uuid = company_dir['dawa_uuid']
        if not address_uuid:
            address_uuid = lookup_address_from_sp_data(company_dir, id_number)
        company_type = company_dir['virksomhedsform']
        industry_code = company_dir['branchekode']

        result = create_organisation(
            id_number, key, name, master_id, phone, email, mobile, fax,
            address_uuid, company_type, industry_code, note
        )
    elif is_cpr(id_number):
        # Collect info from SP and include in call creating user.
        try:
            person_dir = get_cpr_data(id_number)
        except Exception as e:
            # Retry *once*
            try:
                person_dir = get_cpr_data(id_number)
            except Exception as e:
                say("CPR lookup failed after retrying:", id_number, name)
                return None

        first_name = person_dir['fornavn']
        middle_name = person_dir.get('mellemnavn', '')
        last_name = person_dir['efternavn']

        address_uuid = lookup_address_from_sp_data(person_dir, id_number)

        gender = person_dir['koen']
        marital_status = person_dir['civilstand']
        address_protection = person_dir['adressebeskyttelse']

        result = create_bruger(
            id_number, key, name, master_id, phone, email, mobile, fax,
            first_name, middle_name, last_name, address_uuid, gender,
            marital_status, address_protection, note
        )
    else:
        say("Forkert CPR/SE-nr for {0}: {1}".format(name, id_number))
        # Invalid customer
        return None

    if result:

        return result.json()['uuid']


def create_customer_role(customer_uuid, customer_relation_uuid, role):
    """Create an OrgFunktion from this info and return UUID."""
    result = create_organisationfunktion(
        customer_uuid,
        customer_relation_uuid,
        role
    )

    if result:
        return result.json()['uuid']


def create_customer_relation(customer_number, customer_relation_name,
                             customer_type, address_uuid):
    """Create an Interessefællesskab from this info and return UUID."""
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
                     customer_relation_uuid, product_uuids):
    """Create an Indsats from this info and return UUID."""
    result = create_indsats(name, agreement_type, no_of_products,
                            invoice_address, start_date, end_date,
                            location, customer_relation_uuid, product_uuids)
    if result:
        return result.json()['uuid']


def create_product(name, identification, installation_type, meter_number,
                   meter_type, start_date, end_date, product_address):
    """Create a Klasse from this info and return UUID."""
    result = create_klasse(name, identification, installation_type,
                           meter_number, meter_type, start_date, end_date,
                           product_address)
    if result:
        return result.json()['uuid']


def update_product(uuid, fields, new_values):
    """Update product with new information."""
    name_fields = {'Målernr', 'Målertypefabrikat', 'MaalerTypeBetegnel'}
    alt_place = 'AlternativStedID'

    properties = {}
    relations = defaultdict(list)
    all_fields = {**fields, **new_values}

    if name_fields & new_values.keys:
        properties['eksempel'] = all_fields['Målernr']
        properties['beskrivelse'] = all_fields['MaalerTypeBetegnel']
        properties['name'] = '{0}, {1} {2}'.format(
            all_fields['Målernr'], all_fields['Målertypefabrikat'],
            all_fields['MaalerTypeBetegnel']
        )

    if alt_place in new_values:
        new_id = new_values[alt_place] if new_values[alt_place] != '0' else ''
        relations['ava_opstillingsadresse'].append(Relation('uuid', new_id))

    write_object(uuid, properties, relations, "klassifikation", "klasse")


def update_customer(fields, new_values):
    """Update customer with new information."""
    properties = {}
    relations = defaultdict(list)
    # TODO: Replace this explicit mapping with an automation iterating through
    # property_fields and relation_fields. E.g., defining
    #   property_fields =  ['KundeSagsnr']
    #   relation_fields = ['Telefon', 'MobilTlf']
    if 'KundeSagsnr' in new_values:
        properties['ava_masterid'] = new_values['KundeSagsnr']

    id_number = cpr_cvr(int_str(
        new_values.get('PersonnrSEnr', None) or fields.get('PersonnrSEnr')
    ))

    customer_uuid = lookup_customer(id_number)
    if not customer_uuid:
        print("Customer {} not found when updating: ERROR".format(id_number))
        return

    if is_cpr(id_number):
        customer_class = "bruger"
    else:
        customer_class = "organisation"
    if 'MobilTlf' in new_values or 'Telefon' in new_values:
        # Handle the addresses - read the addresses
        # and replace mobile and telephone with the new ones
        # as appropriate.
        customer = read_object(customer_uuid, "organisation", customer_class)
        adresser = customer['relationer'].get('adresser', {})
        telephone_needed = 'Telefon' in new_values
        mobile_needed = 'MobilTlf' in new_values
        for addr in adresser:
            if "uuid" in addr:
                relations['adresser'].append(Relation("uuid", addr["uuid"],
                                                      addr["virkning"]))
            elif "urn" in addr:
                if telephone_needed and addr["urn"].startswith("urn:tel"):
                    pass
                elif mobile_needed and addr["urn"].startswith("urn:mobile"):
                    pass
                else:
                    relations['adresser'].append(Relation("urn", addr["urn"],
                                                          addr["virkning"]))
        if telephone_needed:
            relations['adresser'].append(
                Relation("urn", "urn:tel:{}".format(new_values['Telefon']))
            )
        if mobile_needed:
            relations['adresser'].append(
                Relation("urn", "urn:mobile:{}".format(new_values['MobilTlf']))
            )

    write_object(customer_uuid, properties, relations, "organisation",
                 customer_class)


def update_customer_relation(fields, new_values):
    """Update customer relation with the changed values."""
    address_fields = ['ForbrStVejnavn', 'Vejkode', 'Postnr',
                      'ForbrStPostdistrikt', 'Husnr', 'Bogstav',
                      'Etage', 'Sidedørnr']
    customer_role_fields = ['PersonnrSEnr', 'LigestPersonnr']
    customer_roles = [KUNDE, LIGESTILLINGSKUNDE]
    customer_number = int_str(fields['Kundenr'])
    cr_uuid = lookup_customer_relation(customer_number)
    customer_relation = read_object(cr_uuid, "organisation",
                                    "interessefaellesskab")
    # Dictionary of updated values - no need to exclusively check new_values.
    new_fields = {**fields, **new_values}

    if set(new_values) & set(address_fields):
        # If there's any change at all in address fields we need to recalculate
        # address to see if it's still correct.
        # NOTE: Normally this will be a spelling correction and should yield
        # the same address, but DAR addresses may actually change once in a
        # while.

        properties = {}
        relations = {}
        old_addresses = customer_relation['relationer'].get('adresser', [])
        assert(len(old_addresses) <= 1)
        old_address_uuid = old_addresses[0] if old_addresses else None
        # Recalculate address & set correct address link.
        (new_address,
         new_address_uuid) = get_forbrugssted_address_uuid(new_fields)
        if not new_address_uuid:
            report_error(
                "Unable to look up new address for Forbrugssted: {}".format(
                    new_address)
            )

        if new_address_uuid and new_address_uuid != old_address_uuid:
            relations['adresser'] = [Relation("uuid", new_address_uuid)]

        # Recalculate customer relation name and set if it has changed.
        # Note: We exploit that these properties always have virkning to
        # infinity and that the current period is always the last.
        try:
            current_egenskaber = max(
                customer_relation["attributter"][
                    "interessefaellesskabegenskaber"
                ], key=lambda elem: elem['virkning']['to']
            )
        except KeyError:
            print(
                customer_relation["attributter"][
                    "interessefaellesskabegenskaber"])
            # This should *not* happen
            raise
        old_name = current_egenskaber["interessefaellesskabsnavn"]
        new_name = "{0}, {1}".format(VARME, new_address)
        if old_name != new_name:
            properties["interessefaellesskabsnavn"] = old_name

        write_object(cr_uuid, properties, relations, "organisation",
                     "interessefaellesskab")

    for field, role in zip(customer_role_fields, customer_roles):
        # Handle customer role changes.
        if field in new_values:
            old_customer_role = lookup_customer_role(cr_uuid, role)
            if old_customer_role:
                delete_customer_role(old_customer_role)
            id_number = cpr_cvr(int_str(new_values[field]))
            customer_uuid = lookup_customer(id_number)
            if not customer_uuid:
                # No such customer - we need to create one
                master_id = int_str(new_fields['KundeSagsnr'])
                customer_number = int_str(new_fields['Kundenr'])

                customer_uuid = create_customer(
                    id_number=id_number,
                    key=customer_number,
                    name=new_fields['KundeNavn'],
                    master_id=master_id,
                    phone=new_fields['Telefonnr'],
                    email=new_fields['EmailKunde'],
                    mobile=new_fields['MobilTlf'],
                )
            if not customer_uuid:
                report_error("Unable to lookup or create customer {}".format(
                    field
                ))
                return
            create_customer_role(customer_uuid, cr_uuid, KUNDE)


def update_agreement(fields, new_values):
    """Update agreement based on the changed fields."""
    address_fields = ['Vejnavn', 'Postdistrikt']
    date_fields = ['Tilflytningsdato', 'Fraflytningsdato']
    date_properties = ['startdato', 'slutdato']
    new_fields = {**fields, **new_values}

    # Look up agreement, we know we're going to need this.
    customer_number = int_str(fields['Kundenr'])
    cr_uuid = lookup_customer_relation(customer_number)
    if not cr_uuid:
        print("Customer not found when updating agreement:", customer_number)
        return
    # The should be one and only one agreement for each CR.
    agreements = lookup_agreements(cr_uuid)
    if len(agreements) > 0:
        agreement_uuid = agreements[0]
    else:
        print("Agreement not found for customer:", customer_number)
        return

    properties = {}
    relations = defaultdict(list)

    if set(new_values) & set(address_fields):
        # Handle possible new invoicing address
        invoice_address = (new_fields['VejNavn'].replace(',-', ' ') +
                           ', ' + new_fields['Postdistrikt'])
        try:
            invoice_address_uuid = fuzzy_address_uuid(invoice_address)
        except Exception as e:
            invoice_address_uuid = None
            report_error(
                "Customer {1}: Unable to lookup invoicing address: {0}".format(
                    str(e), customer_number
                )
            )
        if invoice_address_uuid:
            relations['indsatsdokument'].append(
                Relation("uuid", invoice_address_uuid)
            )

    # Now handle the date change(s).
    tz = pytz.timezone('Europe/Copenhagen')
    for field, property in zip(date_fields, date_properties):
        if field in new_values:
            date_str = new_fields[field]
            try:
                date = tz.localize(date_str)
            except:  # noqa
                # This is only for Max date - which is 9999-12-31 =~ infinity
                date = pytz.utc.localize(date_str)
            properties[property] = str(date)

    # Update agreement if we arrived at any changes.
    if relations or properties:
        write_object(
            agreement_uuid, properties, relations, "indsats", "indsats"
        )
