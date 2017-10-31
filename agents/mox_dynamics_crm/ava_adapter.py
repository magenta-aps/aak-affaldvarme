# -*- coding: utf-8 -*-

import logging


def ava_bruger(entity):
    """
    Lora:    Bruger
    CRM:    Aktoer
    """

    log = logging.getLogger()

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["brugeregenskaber"][0]

    # PERFORM A SEARCH TO GET CRM ADDRESS UUID
    # crm_address = get_address(dawa_address)
    kmd_ee = {}

    # Fetch address uuid
    dawa_address = None

    try:
        # Filter "living" address
        residence = (key for key in relationer[
                     "adresser"] if "uuid" in key.keys())

        # Filter other address items
        other = (key for key in relationer["adresser"] if "urn" in key.keys())

        for item in residence:
            dawa_address = item["uuid"]

        # Set email and phone number
        for item in other:
            if "urn:mobile" in item["urn"]:
                kmd_ee["phone"] = item["urn"].split(":")[-1]

            if "urn:email" in item["urn"]:
                kmd_ee["email"] = item["urn"].split(":")[-1]

    except:
        # TODO: Must be sent to error queue for manual processing
        log.error("Error getting address from: {0}".format(ava_lora_uuid))
        log.error("Relationer: {0}".format(relationer))

    # Convert gender to CRM values
    gender = egenskaber.get("ava_koen")
    ava_gender = {
        "M": 1,
        "K": 2
    }

    # Convert family status code to CRM values
    civilstand = egenskaber.get("ava_civilstand")

    # Missing
    # L = længstlevende partner
    # D = død
    ava_family = {
        "P": 0,  # P = registreret partnerskab
        "F": 1,  # F = fraskilt
        "G": 2,  # G = gift
        "O": 3,  # O = ophævelse af registreret partnerskab
        "E": 4,  # E = enke/enkemand
        # "O": 5,
        "U": 6,  # U = ugift
    }

    # Fetch CPR ID from field value
    cpr_id = relationer["tilknyttedepersoner"][0]["urn"].split(":")
    ava_cpr_id = cpr_id[-1]

    # Not set by this agent
    # Lora does not persist this information
    ava_parking_id = None
    aegtefaelle = None

    # CRM formatted payload
    payload = {
        "ava_lora_uuid": ava_lora_uuid,
        "firstname": egenskaber.get("ava_fornavn"),
        "middlename": egenskaber.get("ava_mellemnavn"),
        "lastname": egenskaber.get("ava_efternavn"),
        "ava_adresse": dawa_address,
        "ava_eradressebeskyttet": egenskaber.get("ava_adressebeskyttelse"),
        "ava_modtag_sms_notifikation": egenskaber.get("ava_sms_notifikation"),
        "familystatuscode": ava_family.get(civilstand),
        "ava_aegtefaelle_samlever": aegtefaelle,
        "ava_cpr_nummer": ava_cpr_id,
        "gendercode":  ava_gender.get(gender),
        "ava_p_nummer": ava_parking_id,

        # KMD EE
        # AVA masterid currently appears to be missing from the CRM schema
        # "ava_masterid": egenskaber.get("brugervendtnoegle"),
        "ava_telefonkmdee": kmd_ee.get("phone"),
        "ava_emailkmdee": kmd_ee.get("email"),


        # Currently commented out Arosia fields (Not supported by CRM)
        # "telephone1": None,
        # "arosia_telephone": None,
        # "ava_arosiaid": None
    }

    return payload


def ava_organisation(entity):
    """
    Lora:   Organisation
    CRM:    Aktoer
    """

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["organisationegenskaber"][0]

    # PERFORM A SEARCH TO GET CRM ADDRESS UUID
    # crm_address = get_address(dawa_address)
    kmd_ee = {}

    # Filter "living" address
    residence = (key for key in relationer["adresser"] if "uuid" in key.keys())

    # Filter other address items
    other = (key for key in relationer["adresser"] if "urn" in key.keys())

    # Fetch address uuid
    dawa_address = None

    for item in residence:
        dawa_address = item["uuid"]

    # Fetch contact mobile and email
    for item in other:
        if "urn:mobile" in item["urn"]:
            kmd_ee["phone"] = item["urn"].split(":")[-1]

        if "urn:email" in item["urn"]:
            kmd_ee["email"] = item["urn"].split(":")[-1]

    # Fetch CVR ID from field
    cvr_id = relationer.get("virksomhed")[0]["urn"].split(":")
    ava_cvr_id = cvr_id[-1]

    # Fetch type value from field
    virksomhedsform = relationer["virksomhedstype"][0]["urn"].split(":")
    ava_virksomhedsform = virksomhedsform[-1]

    # Fetch activity value from field
    branche = relationer["branche"][0]["urn"].split(":")
    ava_branche = branche[-1]

    # Not set by this agent
    # Lora does not persist this information
    ava_parking_id = None
    ava_kreditstatus = None

    # Format CRM payload
    payload = {
        "ava_lora_uuid": ava_lora_uuid,
        "firstname": egenskaber.get("organisationsnavn"),
        "ava_adresse": dawa_address,
        "ava_eradressebeskyttet": egenskaber.get("ava_adressebeskyttelse"),
        "ava_modtag_sms_notifikation": egenskaber.get("ava_sms_notification"),
        "ava_cvr_nummer": ava_cvr_id,
        "ava_kreditstatus": ava_kreditstatus,
        "ava_p_nummer": ava_parking_id,
        "ava_virksomhedsform": ava_virksomhedsform,

        # KMD EE
        "ava_masterid": egenskaber.get("brugervendtnoegle"),
        "ava_telefonkmdee": kmd_ee.get("phone"),
        "ava_emailmkdee": kmd_ee.get("email"),

        # Arosia
        "telephone1": None,
        "arosia_telephone": None,
        "ava_arosiaid": None,
    }

    return payload


def ava_kunderolle(entity):
    """
    Lora:   Organisationsfunktion
    CRM:    Kunderolle
    """

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["organisationfunktionegenskaber"][0]

    # Fetch references
    lookup_customer = egenskaber.get("brugervendtnoegle").split()
    ava_aktoer = lookup_customer[-1]

    ava_rolle = egenskaber.get("funktionsnavn")

    # Issue: KMDEE customers are classified as "Ligestillingskunde"
    # Valid types are:
    # Hovedejer = 915240000
    # Ligestillingsejer = 915240001
    # Administrator = 915240002
    # Vicevært = 915240003
    # Medejer = 915240005

    # WORKAROUND: Forcing ava_rolle to be 915240001
    ava_rolle = 915240001

    # This is a temporary value
    # At import this must be replaced with a CRM reference
    kundeforhold = relationer.get("tilknyttedeinteressefaellesskaber")[0]
    ava_kundeforhold = kundeforhold.get("uuid")

    # Format CRM payload
    payload = {
        "ava_aktoer": ava_aktoer,
        "ava_kundeforhold": ava_kundeforhold,
        "ava_rolle": ava_rolle,
    }

    return payload


def ava_account(entity):
    """
    Lora:   Interessefaelleskab
    CRM:    Kundeforhold
    """

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    registeringer = entity["registreringer"][0]
    attributter = registeringer["attributter"]
    relationer = registeringer["relationer"]
    egenskaber = attributter["interessefaellesskabegenskaber"][0]

    # Fetch references
    account_name = egenskaber.get("interessefaellesskabsnavn")
    ava_kundenummer = egenskaber.get("brugervendtnoegle")

    # Convert "kundetype" to literal
    type_ref = egenskaber.get("interessefaellesskabstype")

    ava_kundetype = {
        "Varme": 915240001,
        "Affald": 915240000
    }

    # Not set by this agent
    # Lora does not persist this information
    ava_kundeforholdstype = None
    ava_ejendom = None

    # Format CRM payload
    payload = {
        "name": account_name,
        "ava_kundenummer": ava_kundenummer,
        "ava_kundetype": ava_kundetype.get(type_ref),
        # "ava_kundeforholdstype": ava_kundeforholdstype,  # Currently not in use
        # "ava_ejendom": ava_ejendom,  # Currently not in use
    }

    return payload


def ava_aftale(entity):
    """
    Lora:   Indsats
    CRM:    Aftale
    """

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["indsatsegenskaber"][0]

    # Name is currently not set dynamically
    # TODO: must be set dynamically
    ava_name = "Fjernvarmeaftale"

    # Fetch references
    kundeforhold = relationer.get("indsatsmodtager")[0]
    ava_kundeforhold = kundeforhold.get("uuid")

    aftaletype = relationer.get("indsatstype")[0]
    ava_aftaletype = aftaletype.get("urn")[-1]

    # Not necessarily present
    produkter = relationer.get("indsatskvalitet")
    ava_produkter = None

    if produkter:
        ava_produkter = produkter[0].get("uuid")

    virkning = egenskaber.get("virkning")
    ava_startdato = virkning.get("from")
    ava_slutdato = virkning.get("to")

    indsatsdokument = relationer.get("indsatsdokument")[0]
    ava_faktureringsgrad = indsatsdokument.get("uuid")

    # Not set by this agent
    # Lora does not persist this information
    ava_beskrivelse = None

    # Format CRM payload
    payload = {
        "ava_name": ava_name,
        "ava_kundeforhold": ava_kundeforhold,
        "ava_aftaletype": ava_aftaletype,
        "ava_beskrivelse": ava_beskrivelse,
        "ava_antal_produkt": egenskaber.get("beskrivelse"),
        "ava_faktureringsgrad": ava_faktureringsgrad,
        "ava_startdato": ava_startdato,
        "ava_slutdato": ava_slutdato,
        "ava_produkter": ava_produkter
    }

    return payload


def ava_installation(entity):
    """
    Lora:   Klasse
    CRM:    Produkt
    TODO: References to other entities needs fixing
    """

    # CRM meta field references Lora entity
    ava_lora_uuid = entity["id"]

    # Map data object
    registeringer = entity["registreringer"][0]
    attributter = registeringer["attributter"]
    relationer = registeringer["relationer"]
    egenskaber = attributter["klasseegenskaber"][0]

    # Fetch references
    ava_name = egenskaber.get("titel")
    ava_identifikation = egenskaber.get("brugervendtnoegle")

    installationstype = relationer.get("overordnetklasse")[0]
    ava_installationstype = installationstype.get("urn").split(":")[-1]

    ava_maalernummer = egenskaber.get("eksempel")

    # Referenced by other entities
    # Entity: Lora (Aftale/Indsats)
    ava_aftale = None

    # Entity: DAWA
    ava_adresse = None

    # Entity: Lora (Account/Interessefaellesskab)
    ava_kundenummer = None

    # Arosia not yet implemented
    ava_arosiaid = None

    # Not set by this agent
    # Lora does not persist this information
    ava_afhentningstype = None
    ava_beskrivelse = None

    # Format CRM payload
    payload = {
        "ava_identifikation": ava_identifikation,
        "ava_aftale": ava_aftale,
        "ava_adresse": ava_adresse,
        "ava_installationstype": ava_installationstype,
        "ava_afhentningstype": ava_afhentningstype,
        "ava_maalernummer": ava_maalernummer,
        "ava_beskrivelse": ava_beskrivelse,
        "ava_kundenummer": ava_kundenummer
    }

    return payload
