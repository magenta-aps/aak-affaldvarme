import logging

from arosia_oio import (create_or_update_indsats,
                        create_or_update_interessefaellesskab,
                        create_or_update_klasse,
                        create_or_update_organisationfunktion,
                        extract_cpr_and_update_lora,
                        extract_cvr_and_update_lora)

"""
This file contains general functions for handling rows from the various tables
of AROSia
"""

logger = logging.getLogger('mox_arosia')


def handle_cpr(row, phone, email, sms_notif):
    cpr = row.get('ava_CPRnummer')
    arosia_id = row.get('ContactId')
    response = extract_cpr_and_update_lora(cpr,
                                           phone=phone,
                                           email=email,
                                           arosia_id=arosia_id,
                                           sms_notif=sms_notif)
    if response:
        lora_id = response.json()['uuid']
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
        return handle_cpr(row, phone, email, sms_notif)
    elif cvr:
        return handle_cvr(row, phone, email, sms_notif)


def handle_kundeaftale(row, account, products):
    logger.info('Handling kundeaftale')
    name = row.get('ava_navn')
    agreement_type = "Affald"
    no_of_products = len(products)
    start_date = row.get('ava_Startdato')
    end_date = row.get('ava_Slutdato')
    customer_relation_uuid = account

    response = create_or_update_indsats(
        name=name,
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
        lora_id = response.json()['uuid']
        return lora_id


def handle_kontaktrolle(row, contact, account):
    logger.info('Handling kontaktrolle')
    name = row.get('ava_KontaktName')
    role = row.get('ava_Rolle')
    response = create_or_update_organisationfunktion(
        customer_number=name,
        customer_uuid=contact,
        customer_relation_uuid=account,
        role=role)
    if response:
        lora_id = response.json()['uuid']
        return lora_id
