"""Mox KMD EE main program."""
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import sys

from multiprocessing.dummy import Pool

from mssql_config import username, password, server, database
from ee_utils import connect, int_str, cpr_cvr
from ee_oio import KUNDE, LIGESTILLINGSKUNDE
from crm_utils import lookup_customer_relation, lookup_customer_roles, VARME
from crm_utils import lookup_customer, lookup_agreements, lookup_product
from crm_utils import lookup_agreement_from_product, create_customer
from crm_utils import create_customer_relation, create_customer_role
from crm_utils import create_agreement, create_product, lookup_products
from crm_utils import delete_customer_role, delete_customer_relation
from crm_utils import delete_agreement, delete_product
from crm_utils import add_product_to_agreement, update_product
from crm_utils import update_customer, update_agreement, read_agreement
from crm_utils import update_customer_relation, write_agreement_dict

from ee_utils import get_forbrugssted_address_uuid
from ee_utils import get_products_for_location
from ee_utils import get_alternativsted_address_uuid

from ee_data import read_customer_records, store_customer_records
from ee_data import retrieve_customer_records, read_installation_records
from ee_data import store_installation_records, retrieve_installation_records

from service_clients import report_error, fuzzy_address_uuid


VERBOSE = False


def say(*args):
    """Local utility to give output in verbose mode."""
    if __name__ == '__main__' and VERBOSE:
        print(*args)


"""CUSTOMER RELATED FUNCTIONS.

Import customer, import customer relation, update, delete.
"""


def import_customer(id_and_fields):
    """Import a new customer, log if it fails."""
    id_number, fields = id_and_fields
    id_number = cpr_cvr(int_str(id_number))

    customer_uuid = lookup_customer(id_number)
    if not customer_uuid:
        master_id = int_str(fields['KundeSagsnr'])
        customer_number = int_str(fields['Kundenr'])

        new_customer_uuid = create_customer(
            id_number=id_number,
            key=id_number,
            name=fields['KundeNavn'],
            master_id=master_id,
            phone=fields['Telefonnr'],
            email=fields['EmailKunde'],
            mobile=fields['MobilTlf'],
        )

        if new_customer_uuid:
            # New customer created
            customer_uuid = new_customer_uuid
        else:
            # No customer created or found.
            main_customer = cpr_cvr(int_str(fields['PersonnrSEnr']))
            if id_number == main_customer:
                role = 'hovedkunde'
            else:
                role = 'ligestilling'
            report_error(
                "No customer created: {} {} {} ({})".format(
                    fields['KundeNavn'], id_number, customer_number, role
                )
            )
            return


def import_customer_record(fields):
    """Import a new customer record including relation, agreement, products.

    Assume customers themselves have already been imported.
    """
    # Lookup customer in LoRa - insert if it doesn't exist already.
    id_number = cpr_cvr(int_str(fields['PersonnrSEnr']))
    ligest_personnr = cpr_cvr(int_str(fields['LigestPersonnr']))
    customer_number = int_str(fields['Kundenr'])

    # If customer relation already exists, please skip.
    if lookup_customer_relation(customer_number):
        # print("This customer relation already exists:", customer_number)
        return

    # Now start handling customers etc.
    customer_uuid = lookup_customer(id_number)
    # Customer *must* have been created during previous import step
    if not customer_uuid:
        # This must have failed
        print("Customer not found:", id_number, fields['KundeNavn'])

    # Create customer relation
    # NOTE: In KMD EE, there's always one customer relation for each row in
    # the Kunde table.

    # Get Forbrugsstedadresse
    (forbrugssted_address,
     forbrugssted_address_uuid) = get_forbrugssted_address_uuid(fields)

    if not forbrugssted_address_uuid:
        report_error(forbrugssted_address)
    cr_name = "{0}, {1}".format(VARME, forbrugssted_address)
    cr_type = VARME  # Always for KMD EE
    cr_address_uuid = forbrugssted_address_uuid
    cr_uuid = create_customer_relation(
        customer_number, cr_name, cr_type, cr_address_uuid
    )

    if not cr_uuid:
        print("Unable to create customer relation for customer {}".format(
            customer_number)
        )

    # This done, create customer roles & link customer and relation
    role_uuid = create_customer_role(customer_uuid, cr_uuid, KUNDE)
    assert(role_uuid)

    # Now handle partner/roommate, ignore empty CPR numbers
    if len(ligest_personnr) > 1:

        ligest_uuid = lookup_customer(ligest_personnr)
        # Customer was already created before this step
        if not customer_uuid:
            # This must have failed
            print("Ligest Customer not found:", id_number, fields['KundeNavn'])

        create_customer_role(
            ligest_uuid, cr_uuid, LIGESTILLINGSKUNDE
        )

    # Create agreement
    name = 'Fjernvarmeaftale'
    agreement_type = VARME
    invoice_address = (fields['VejNavn'].replace(',-', ' ') +
                       ', ' + fields['Postdistrikt'])
    try:
        invoice_address_uuid = fuzzy_address_uuid(invoice_address)
    except Exception as e:
        invoice_address_uuid = None
        report_error(
            "Customer {1}: Unable to lookup invoicing address: {0}".format(
                str(e), id_number
            )
        )
    agreement_start_date = fields['Tilflytningsdato']
    agreement_end_date = fields['Fraflytningsdato']

    # There is always one agreement for each location (Forbrugssted)
    # AND only one location for each customer record.

    forbrugssted = fields['ForbrugsstedID']

    products = get_products_for_location(forbrugssted)

    no_of_products = len(products)

    product_uuids = []

    for p in products:
        meter_number = p['Målernr']
        meter_type = p['MaalerTypeBetegnel']
        product_uuid = create_product(
            name="{0}, {1} {2}".format(
                meter_number, p['Målertypefabrikat'], meter_type
            ),
            identification=p['InstalNummer'],
            installation_type=VARME,
            meter_number=meter_number,
            meter_type=meter_type,
            start_date=p['DatoFra'],
            end_date=p['DatoTil'],
            product_address=get_alternativsted_address_uuid(
                p['AlternativStedID']
            )
        )
        if product_uuid:
            product_uuids.append(product_uuid)

    agreement_name = "Varme, " + name
    agreement_uuid = create_agreement(
        agreement_name, agreement_type, no_of_products, invoice_address_uuid,
        agreement_start_date, agreement_end_date, forbrugssted, cr_uuid,
        product_uuids
    )
    assert(agreement_uuid)


def update_customer_record(fields, changed_fields):
    """Update relevant LoRa objects with the specific changes."""
    customer_fields = ['Telefon', 'MobilTlf', 'Fax', 'Kundesagsnr']
    customer_relation_fields = ['ForbrStVejnavn', 'Vejkode', 'Postnr',
                                'ForbrStPostdistrikt', 'Husnr', 'Bogstav',
                                'Etage', 'Sidedørnr', 'PersonnrSEnr',
                                'LigestPersonnr']
    agreement_fields = ['Vejnavn', 'Postdistrikt', 'Tilflytningsdato',
                        'Fraflytningsdato']
    update_handlers = [(customer_fields, update_customer),
                       (customer_relation_fields, update_customer_relation),
                       (agreement_fields, update_agreement)]
    changed_keys = set(changed_fields)

    for field_list, handler in update_handlers:
        if changed_keys & set(field_list):
            handler(fields, changed_fields)


def delete_customer_record(customer_number):
        """Purge relation and customer roles, agreements and products."""
        cr_uuid = lookup_customer_relation(customer_number)
        # This should exist provided everything is up to date!
        if not cr_uuid:
            # Trying to delete a customer that doesn't exist is not an error.
            return

        # Look up the customer roles and customers for this customer relation.

        roles = lookup_customer_roles(customer_relation=cr_uuid)

        # Delete the customer roles.

        for role in roles:
            delete_customer_role(role)

        # Delete all agreements and products corresponding to this customer
        # relation.
        # There can be only one agreement per customer as is, but in the future
        # this might change.
        agreements = lookup_agreements(customer_relation=cr_uuid)

        for agreement_uuid in agreements:
            products = lookup_products(agreement_uuid=agreement_uuid)

            for p in products:
                delete_product(p)

            delete_agreement(agreement_uuid)
        # Now go ahead and delete the customer relation
        delete_customer_relation(cr_uuid)


"""Installation related functions.

Import, update, delete.
"""


def import_installation_record(fields):
    """Import product from KMD EE installation record."""
    # check there's an agreement corresponding to this Forbrugssted
    customer_number = int_str(fields['Kundenr'])
    cr_uuid = lookup_customer_relation(customer_number)
    agreement_uuid = lookup_agreements(cr_uuid)[0] if cr_uuid else None
    if agreement_uuid:
        # Agreement found.
        product_uuid = lookup_product(fields['InstalNummer'])
        if product_uuid:
            # If product exists, don't import it.
            return
        # create the product
        meter_number = fields['Målernr']
        meter_type = fields['MaalerTypeBetegnel']
        product_uuid = create_product(
            name="{0}, {1} {2}".format(
                meter_number, fields['Målertypefabrikat'], meter_type
            ),
            identification=fields['InstalNummer'],
            installation_type=VARME,
            meter_number=meter_number,
            meter_type=meter_type,
            start_date=fields['DatoFra'],
            end_date=fields['DatoTil'],
            product_address=get_alternativsted_address_uuid(
                fields['AlternativStedID']
            )
        )
        if product_uuid:
            # add it to the agreement
            add_product_to_agreement(product_uuid, agreement_uuid)
    else:
        print("No agreement found for customer number {}".format(
            customer_number))


def update_installation_record(old_fields, changed_fields):
    """Update relevant LoRa objects with the changes for each installation."""
    relevant_fields = {'Målernr', 'Målertypefabrikat', 'MaalerTypeBetegnel',
                       'AlternativStedID'}
    if relevant_fields & changed_fields.keys():
        product_uuid = lookup_product(old_fields['InstalNummer'])
        if not product_uuid:
            say("Error: Product {} not found".format(
                old_fields['InstalNummer']))
            return
        say("Updating product: {}".format(changed_fields))
        update_product(product_uuid, old_fields, changed_fields)


def delete_installation_record(product_id):
    """Delete product from LoRa when no longer relevant."""
    # get product UUID
    product_uuid = lookup_product(product_id)
    # delete product & find agreement for this product UUID, if any
    if product_uuid:
        delete_product(product_uuid)
        agreement_uuid = lookup_agreement_from_product(product_uuid)
    else:
        return
    if agreement_uuid:
        # remove product from agreement
        agreement_json = read_agreement(agreement_uuid)
        products = agreement_json['relationer']['indsatskvalitet']
        for p in products:
            if p["uuid"] == product_uuid:
                p["uuid"] = ''
        agreement_json['relationer']['indsatskvalitet'] = products

        write_agreement_dict(agreement_uuid, agreement_json)


def main():
    """Main program. Calculate changes since last run and sync with LoRa.

    * Argument parsing.
    * Read all customer records from KMD EE and calculate changes.
    * From these changes, delete expired records; import new ones; update
      existing ones.
    * Repeat for installations/products.

    Note that products are *not* created separately during the inital import,
    since they're imported as part of creating each agreement.

    """
    # argument parsing
    import argparse
    global VERBOSE

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', action='store_true',
                        help='print helpful comments during execution')
    parser.add_argument('--initial-import', action='store_true',
                        help='only perform inital import')
    args = parser.parse_args()
    VERBOSE = args.verbose
    initial_import = args.initial_import

    """CUSTOMERS AND CUSTOMER RELATIONS"""
    connection = connect(server, database, username, password)
    cursor = connection.cursor(as_dict=True)
    new_values = read_customer_records(cursor)
    new_installation_values = read_installation_records(cursor)
    old_installation_values = retrieve_installation_records()
    connection.close()

    old_values = retrieve_customer_records()

    say('Comparison, new_values == old_values:', new_values == old_values)

    new_keys = new_values.keys() - old_values.keys()
    lost_keys = old_values.keys() - new_values.keys()
    common_keys = new_values.keys() & old_values.keys()

    say("new customers:", len(new_keys))
    say("lost customers:", len(lost_keys))
    say("existing customers:", len(common_keys))

    # Now calculate diff between new values and old values.
    # Build a mapping between customer numbers and
    # dictionaries containing only the changed values.

    changed_records = {
        k: {
            f: v for f, v in new_values[k].items() if
            new_values[k][f] != old_values[k][f]
          } for k in common_keys if new_values[k] != old_values[k]
    }

    say("Number of changed customer records:", len(changed_records))
    # Handle notifications for customer part, do the installations afterwards.
    if len(lost_keys) > 0:
        say("... deleting {} customers...".format(len(lost_keys)))
        for k in lost_keys:
            # These records are no longer active and should be deleted in LoRa
            delete_customer_record(k)
        say("... done")
    # New customer relations - import along with agreements & products
    # First explicitly create the new customers

    new_customer_fields = {**{
        new_values[k]['PersonnrSEnr']: new_values[k]
        for k in new_keys}, **{
            new_values[k]['LigestPersonnr']: new_values[k]
            for k in new_keys if len(
                int_str(new_values[k]['LigestPersonnr'])
            ) > 1
        }}
    # Now import all the new customers using threads
    if len(new_customer_fields) > 0:
        say("... importing {} new customers ...".format(
            len(new_customer_fields)
        ))
        p = Pool(15)
        p.map(import_customer, new_customer_fields.items())
        p.close()
        p.join()
        say("... done")

    if len(new_keys) > 0:
        say('... importing {} new customer relations ...'.format(
            len(new_keys)
        ))
        p = Pool(15)
        p.map(import_customer_record, [new_values[k] for k in new_keys])
        p.close()
        p.join()
        say("... done")

    # Now (and finally) handle update of the specific changed fields.
    if len(changed_records) > 0:
        say('... updating {} customer records ...'.format(
            len(changed_records)
        ))
        for k, changed_fields in changed_records.items():
            update_customer_record(old_values[k], changed_fields)
        say("... done")

    if initial_import:
        # In this case, we shouldn't handle changed installations, only
        # record the ones we've seen.
        store_customer_records(new_values)
        store_installation_records(new_installation_values)
        sys.exit()

    """INSTALLATIONS AND PRODUCTS"""

    new_installation_keys = (new_installation_values.keys() -
                             old_installation_values.keys())
    lost_installation_keys = (old_installation_values.keys() -
                              new_installation_values.keys())
    common_installation_keys = (new_installation_values.keys() &
                                old_installation_values.keys())

    say("new installations:", len(new_installation_keys))
    say("lost installations:", len(lost_installation_keys))
    say("existing installations:", len(common_installation_keys))

    changed_installation_records = {
        k: {
            f: v for f, v in new_installation_values[k].items() if
            new_installation_values[k][f] != old_installation_values[k][f]
          } for k in common_installation_keys if
        new_installation_values[k] != old_installation_values[k]
    }

    say("Number of changed installation records:", len(changed_records))
    #  Those that disappear are expired, either by the customer disappearing or
    #  by crossing the expiry date. If the customer disappeared, it should
    #  already be gone.
    say("... deleting {} expired installations ...".format(
        len(lost_installation_keys)
    ))
    for k in lost_installation_keys:
        delete_installation_record(k)
    say("... done")

    # New records may come into being by entering the valid period.
    # if so, they should be attached to the Aftale corresponding to this
    # Forbrugssted. If none such exists, they should not be created.

    say(
        "... importing {} new installations ...".format(
            len(new_installation_keys)
        )
    )
    for k in new_installation_keys:
        import_installation_record(new_installation_values[k])
    say("... done")

    # Now handle updates
    say("... updating {} changed installations ...".format(
        len(changed_installation_records)
    ))
    for k, changed_fields in changed_installation_records.items():
        update_installation_record(old_installation_values[k], changed_fields)
    say("... done")

    # All's well that ends well
    store_customer_records(new_values)
    store_installation_records(new_installation_values)


if __name__ == '__main__':
    main()
