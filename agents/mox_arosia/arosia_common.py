import logging

from arosia_oio import (create_or_update_indsats,
                        create_or_update_interessefaellesskab,
                        create_or_update_klasse,
                        create_or_update_organisationfunktion,
                        extract_cpr_and_update_lora,
                        extract_cvr_and_update_lora,
                        lookup_bruger,
                        lookup_klasse,
                        lookup_organisation,
                        lookup_organisationfunktion,
                        lookup_interessefaellesskab)
from services import fuzzy_address_uuid

"""
This file contains general functions for handling rows from the various tables
of AROSia
"""

logger = logging.getLogger('arosia_common')


def handle_cpr(row, phone, email, sms_notif):
    cpr = row.get('ava_CPRnummer')
    arosia_id = row.get('ContactId')
    response = extract_cpr_and_update_lora(cpr,
                                           phone=phone,
                                           email=email,
                                           arosia_id=arosia_id,
                                           sms_notif=sms_notif)
    if response:
        try:
            lora_id = response.json()['uuid']
        except AttributeError:
            lora_id = response
        return lora_id


def handle_cvr(row, phone, email, sms_notif):
    cvr = row.get('ava_CVRnummer')
    arosia_id = row.get('ContactId')
    response = extract_cvr_and_update_lora(cvr,
                                           phone=phone,
                                           email=email,
                                           arosia_id=arosia_id,
                                           sms_notif=sms_notif)
    if response:
        lora_id = response.json()['uuid']
        return lora_id


def handle_contact(row):
    logger.info('Handling contact')
    cpr = row['ava_CPRnummer']
    cvr = row['ava_CVRnummer']
    email = row['EMailAddress1']
    sms_notif = row['ava_sms_notifikation']

    mobile_phone = row['MobilePhone']
    telephone = row['Telephone1']

    phone = mobile_phone or telephone

    if cpr:
        lora_id = lookup_bruger(cpr)
        if not lora_id:
            lora_id = handle_cpr(row, phone, email, sms_notif)
    elif cvr:
        lora_id = lookup_organisation(cvr)
        if not lora_id:
            lora_id = handle_cvr(row, phone, email, sms_notif)
    else:
        # Empty row
        lora_id = None
    return lora_id


def handle_kundeaftale(row, account, products):
    logger.info('Handling kundeaftale')
    name = row.get('ava_navn')
    agreement_type = "Affald"
    no_of_products = len(products)
    start_date = row.get('ava_Startdato')
    end_date = row.get('ava_Slutdato')
    customer_relation_uuid = account

    invoice_address = row.get('ava_Kundeforholdname')
    invoice_address_uuid = fuzzy_address_uuid(invoice_address)

    response = create_or_update_indsats(
        name=name,
        invoice_address=invoice_address_uuid,
        agreement_type=agreement_type,
        no_of_products=no_of_products,
        start_date=start_date,
        end_date=end_date,
        customer_relation_uuid=customer_relation_uuid,
        product_uuids=products)
    if response:
        lora_id = response.json()['uuid']
        return lora_id


def handle_placeretmateriel(row):
    logger.info('Handling placeretmateriel')
    name = row.get('ava_navn')
    identification = row.get('ava_stregkode')
    installation_type = "Affald"
    afhentningstype = row.get('ava_affaldstypeName')
    arosia_id = row.get('ava_placeretmaterielId')
    aftale_id = row.get('ava_Kundeaftale')

    uuid = lookup_klasse(identification)
    if uuid:
        return uuid
    response = create_or_update_klasse(name=name,
                                       identification=identification,
                                       installation_type=installation_type,
                                       arosia_id=arosia_id,
                                       afhentningstype=afhentningstype,
                                       aftale_id=aftale_id)
    if response:
        lora_id = response.json()['uuid']
        return lora_id


def handle_account(row):
    logger.info('Handling account')
    customer_number = row.get('AccountNumber')
    customer_relation_name = row.get('Name')
    arosia_id = row.get('AccountId')
    customer_type = "Affald"

    response = create_or_update_interessefaellesskab(
        customer_number=customer_number,
        customer_relation_name=customer_relation_name,
        customer_type=customer_type,
        arosia_id=arosia_id)
    if response:
        try:
            lora_id = response.json()['uuid']
        except AttributeError:
            lora_id = response
        return lora_id


def handle_kontaktrolle(row, contact, account):
    logger.info('Handling kontaktrolle')
    role = str(row.get('ava_Rolle'))
    uuid = lookup_organisationfunktion(contact, account)
    if uuid:
        return uuid
    response = create_or_update_organisationfunktion(
        customer_uuid=contact,
        customer_relation_uuid=account,
        numeric_role=role)
    if response:
        lora_id = response.json()['uuid']
        return lora_id
