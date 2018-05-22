# -*- coding: utf-8 -*-

from logging import getLogger


log = getLogger(__name__)

CRM_FIRSTNAME_LIMIT = 150  # issue 22298 lifted to 150
CRM_LASTNAME_LIMIT = 100  # issue 22298 lifted to 100
CRM_MIDDLENAME_LIMIT = 80  # issue 22298 lifted to 80
CRM_FULLNAME_LIMIT = 260  # issue 22298 N/A


def ava_bruger(entity, old_adapted):
    """
    Adapter to convert (LORA) bruger object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Bruger
    CRM:    Aktoer (contact)

    The original identifiers are stored 1:1.

    Example:
        Original LORA identifier:   8768568D-90B8-4552-B37D-E7B5B50C5495
        Cache layer identifier:     8768568D-90B8-4552-B37D-E7B5B50C5495

    When exporting the content to CRM the external reference (CRM reference)
    is stored in the 'externel_ref' field for maintenance purposes.

    The actual (converted) content which is inserted in CRM
    is stored in the 'data' field of the document.

    :param entity:  OIO Rest object (dictionary)

    :return:        Cache document containing meta data and CRM data object.
                    Example:
                    {
                        "id": <LORA reference (uuid)>,
                        "external_ref": <CRM reference (guid)>,
                        "<entity>_ref": <relational reference>,
                        "data": <CRM data object>
                    }
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["brugeregenskaber"][0]

    # Properties
    firstname = egenskaber.get("ava_fornavn")
    middlename = egenskaber.get("ava_mellemnavn")
    lastname = egenskaber.get("ava_efternavn")
    ava_eradressebeskyttet = egenskaber.get("ava_adressebeskyttelse")
    ava_modtag_sms_notifikation = egenskaber.get("ava_sms_notifikation")
    ava_kmdeemasterid = egenskaber.get("ava_masterid")

    # KMD EE related data
    kmd_ee = {}

    # Address (DAR) reference
    dawa_address = None

    try:
        # Filter "living" address
        addresses = relationer.get("adresser", {})
        residence = (addr for addr in addresses if "uuid" in addr)

        # Filter other address items
        other = (addr for addr in addresses if "urn" in addr)

        for item in residence:
            dawa_address = item["uuid"]

        # Set email and phone number
        for item in other:
            if "urn:tel" in item["urn"]:
                kmd_ee["landline"] = item["urn"].split(":")[-1]

            if "urn:mobile" in item["urn"]:
                kmd_ee["mobile"] = item["urn"].split(":")[-1]

            if "urn:email" in item["urn"]:
                kmd_ee["email"] = item["urn"].split(":")[-1]

    except Exception as error:
        # TODO: Must be sent to error queue for manual processing
        log.error("Error getting address from: {0}".format(origin_id))
        log.error("Relationer: {0}".format(relationer))

        # Debug
        log.debug(error)

    # Convert gender to CRM values
    gender = egenskaber.get("ava_koen")
    gender_options = {
        "M": 1,
        "K": 2
    }

    gendercode = gender_options.get(gender)

    # Pending: family status code may not be needed
    # "familystatuscode": ava_family.get(civilstand),

    # Convert family status code to CRM values
    # civilstand = egenskaber.get("ava_civilstand")

    # Pending: family status code may not be needed
    # # Missing
    # # L = længstlevende partner
    # # D = død

    # ava_family = {
    #     "P": 0,  # P = registreret partnerskab
    #     "F": 1,  # F = fraskilt
    #     "G": 2,  # G = gift
    #     "O": 3,  # O = ophævelse af registreret partnerskab
    #     "E": 4,  # E = enke/enkemand
    #     # "O": 5,
    #     "U": 6,  # U = ugift
    # }

    # Fetch CPR ID from field value
    cpr_id = relationer["tilknyttedepersoner"][0]["urn"].split(":")
    ava_cpr_id = cpr_id[-1]

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "dawa_ref": dawa_address,
        "data": dict(old_adapted.get("data",{}))
    }

    document["data"].update({
        "firstname": (
            firstname[:CRM_FIRSTNAME_LIMIT]
            if firstname else None
        ),
        "middlename": (
            middlename[:CRM_MIDDLENAME_LIMIT]
            if middlename else None
        ),
        "lastname": (
            lastname[:CRM_LASTNAME_LIMIT]
            if lastname else None
        ),
        "ava_eradressebeskyttet": ava_eradressebeskyttet,
        "ava_modtag_sms_notifikation": ava_modtag_sms_notifikation,
        "ava_cpr_nummer": ava_cpr_id,
        "gendercode":  gendercode,

        # KMD EE
        "ava_kmdeemasterid": ava_kmdeemasterid,
        "ava_mobilkmdee": kmd_ee.get("mobile"),
        "ava_fastnetkmdee": kmd_ee.get("landline"),
        "ava_emailkmdee": kmd_ee.get("email"),

        # Arosia fields (Not supported by CRM)
        # "telephone1": None,
        # "emailaddress1": None
        # "arosia_telephone": None,
        # "ava_arosiaid": None
    })

    return document


def ava_organisation(entity, old_adapted):
    """
    Adapter to convert (LORA) object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Organisation
    CRM:    Aktoer (contact)

    For further details, please see the documentation above.
    (ava_bruger :py:func:~`ava_adapter.ava_bruger`)

    :param entity:  OIO Rest object (dictionary)
    :return:        Cache document containing meta data and CRM data object.
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["organisationegenskaber"][0]

    # Properties
    organisationsnavn = egenskaber.get("organisationsnavn")
    ava_eradressebeskyttet = egenskaber.get("ava_adressebeskyttelse")
    ava_modtag_sms_notifikation = egenskaber.get("ava_sms_notifikation")
    ava_kmdeemasterid = egenskaber.get("ava_masterid")

    # KMD EE
    kmd_ee = {}

    # Filter "living" address
    residence = (addr for addr in relationer.get("adresser", []) if
                 "uuid" in addr)

    # Filter other address items
    other = (addr for addr in relationer.get("adresser", []) if "urn" in addr)

    # Fetch address uuid
    dawa_address = None

    for item in residence:
        dawa_address = item["uuid"]

    # Fetch contact mobile and email
    for item in other:
        if "urn:tel" in item["urn"]:
            kmd_ee["landline"] = item["urn"].split(":")[-1]

        if "urn:mobile" in item["urn"]:
            kmd_ee["mobile"] = item["urn"].split(":")[-1]

        if "urn:email" in item["urn"]:
            kmd_ee["email"] = item["urn"].split(":")[-1]

    # Fetch CVR ID from field
    cvr_id = relationer.get("virksomhed")[0]["urn"].split(":")
    ava_cvr_id = cvr_id[-1]

    # Fetch type value from field
    virksomhedsform = relationer["virksomhedstype"][0]["urn"].split(":")
    ava_virksomhedsform = virksomhedsform[-1]

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "dawa_ref": dawa_address,
        "data": dict(old_adapted.get("data",{}))
    }

    document["data"].update({
        "firstname": organisationsnavn[:CRM_FIRSTNAME_LIMIT],
        "ava_eradressebeskyttet": ava_eradressebeskyttet,
        "ava_modtag_sms_notifikation": ava_modtag_sms_notifikation,
        "ava_cvr_nummer": ava_cvr_id,
        "ava_virksomhedsform": ava_virksomhedsform,

        # KMD EE
        "ava_kmdeemasterid": ava_kmdeemasterid,
        "ava_mobilkmdee": kmd_ee.get("mobile"),
        "ava_fastnetkmdee": kmd_ee.get("landline"),
        "ava_emailkmdee": kmd_ee.get("email"),

        # Arosia
        # "telephone1": None,
        # "emailaddress1": None
        # "arosia_telephone": None,
        # "ava_arosiaid": None,
    })

    return document


def ava_kunderolle(entity, old_adapted):
    """
    Adapter to convert (LORA) object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Organisationsfunktion
    CRM:    Kunderolle (ava_kunderolle)

    For further details, please see the documentation above.
    (ava_bruger :py:func:~`ava_adapter.ava_bruger`)

    :param entity:  OIO Rest object (dictionary)
    :return:        Cache document containing meta data and CRM data object.
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]
    relationer = data["relationer"]
    egenskaber = attributter["organisationfunktionegenskaber"][0]

    # Fetch references
    tilknyttedebrugere = relationer.get("tilknyttedebrugere")[0]
    customer_ref = tilknyttedebrugere.get("uuid")

    rolle_ref = egenskaber.get("funktionsnavn")

    # NOTE: KMDEE customers are classified as follows:
    # Kunde or Ligestillingskunde

    # All valid types are:
    customer_types = {
        "Kunde": 915240004,
        "Ligestillingskunde": 915240006,
        "Hovedejer": 915240000,
        "Ligestillingsejer": 915240001,
        "Administrator": 915240002,
        "Vicevært": 915240003,
        "Medejer": 915240005
    }

    # Get type value
    ava_rolle = customer_types.get(rolle_ref)

    # Related reference
    kundeforhold = relationer.get("tilknyttedeinteressefaellesskaber")[0]
    ava_kundeforhold = kundeforhold.get("uuid")
    if not ava_kundeforhold:
        log.error(
            "Kundeforhold not found on role: {0}".format(entity)
        )

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "contact_ref": customer_ref,
        "interessefaellesskab_ref": ava_kundeforhold,
        "data": dict(old_adapted.get("data",{}))
    }

    document["data"].update({
        "ava_rolle": ava_rolle
    })

    return document


def ava_account(entity, old_adapted):
    """
    Adapter to convert (LORA) object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Interessefaellesskab
    CRM:    Kundeforhold (account)

    For further details, please see the documentation above.
    (ava_bruger :py:func:~`ava_adapter.ava_bruger`)

    :param entity:  OIO Rest object (dictionary)
    :return:        Cache document containing meta data and CRM data object.
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    registeringer = entity["registreringer"][0]
    attributter = registeringer["attributter"]
    relationer = registeringer["relationer"]
    egenskaber = attributter["interessefaellesskabegenskaber"][0]

    # Fetch references
    account_name = egenskaber.get("interessefaellesskabsnavn")
    ava_kundenummer = egenskaber.get("brugervendtnoegle")

    # AVA Utility address
    ava_adresse = None

    # Fetch utility address
    addresses = relationer.get("adresser")

    if addresses:
        ava_adresse = addresses[0]["uuid"]

    # Convert "kundetype" to literal
    type_ref = egenskaber.get("interessefaellesskabstype")

    customer_types = {
        "Varme": 915240001,
        "Affald": 915240000
    }

    # Get type
    ava_kundetype = customer_types.get(type_ref)

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "dawa_ref": ava_adresse,
        "data": dict(old_adapted.get("data",{}))
    }

    document["data"].update({
        "name": account_name,
        "ava_kundenummer": ava_kundenummer,
        "ava_kundetype": ava_kundetype
    })

    return document


def ava_aftale(entity, old_adapted):
    """
    Adapter to convert (LORA) object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Indsats
    CRM:    Aftale (ava_aftale)

    For further details, please see the documentation above.
    (ava_bruger :py:func:~`ava_adapter.ava_bruger`)

    :param entity:  OIO Rest object (dictionary)
    :return:        Cache document containing meta data and CRM data object.
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    data = entity["registreringer"][0]
    attributter = data["attributter"]

    # relationer = data["relationer"]
    relationer = data.get("relationer")
    # Bail out on no relations, avoiding program crash
    if not relationer:
        log.error(
            "Error no relationer for: {0}".format(origin_id)
        )
        return False  # make oio_interface skip

    egenskaber = attributter["indsatsegenskaber"][0]

    # Fetch references
    ava_name = egenskaber.get("brugervendtnoegle")
    kundeforhold = relationer.get("indsatsmodtager")[0]
    ava_kundeforhold = kundeforhold.get("uuid")

    aftaletype = relationer.get("indsatstype")[0]
    type_ref = aftaletype.get("urn")[4:]

    # Convert string value to int
    ava_antal_produkter = int(egenskaber.get("beskrivelse"))

    # Convert type to literal
    available_types = {
        "Varme": 915240001,
        "Affald": 915240000
    }

    # Get type
    ava_aftaletype = available_types.get(type_ref)

    # Not necessarily present
    produkter = relationer.get("indsatskvalitet")
    ava_produkter = None

    if produkter:
        ava_produkter = produkter[0].get("uuid")

    # CRM does not support timestamps, we are passing the date ONLY
    ava_startdato = egenskaber.get("starttidspunkt").split(" ")[0]
    ava_slutdato = egenskaber.get("sluttidspunkt").split(" ")[0]

    # Billing
    ava_billing_address = None

    try:
        indsatsdokument = relationer.get("indsatsdokument")[0]
        ava_billing_address = indsatsdokument.get("uuid")
    except Exception as error:
        log.error(
            "Error getting address for: {0}".format(origin_id)
        )

        log.debug(error)

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "interessefaellesskab_ref": ava_kundeforhold,
        "contact_refs": old_adapted.get("contact_refs", []),
        "dawa_ref": ava_billing_address,
        "klasse_ref": ava_produkter,
        "data": dict(old_adapted.get("data",{}))
    }

    document["data"].update({
        "ava_name": ava_name,
        "ava_aftaletype": ava_aftaletype,
        "ava_antal_produkter": ava_antal_produkter,
        "ava_startdato": ava_startdato,
        "ava_slutdato": ava_slutdato
    })

    return document


def ava_installation(entity, old_adapted):
    """
    Adapter to convert (LORA) object to cache layer document.
    The document contains both transport meta data and the original content.

    Lora:   Klasse
    CRM:    Produkt (ava_installation)

    For further details, please see the documentation above.
    (ava_bruger :py:func:~`ava_adapter.ava_bruger`)

    :param entity:  OIO Rest object (dictionary)
    :return:        Cache document containing meta data and CRM data object.
    """

    # CRM meta field references Lora entity
    origin_id = entity["id"]

    # Map data object
    registeringer = entity["registreringer"][0]
    attributter = registeringer["attributter"]
    relationer = registeringer.get("relationer", {})
    egenskaber = attributter["klasseegenskaber"][0]

    # Fetch references
    ava_name = egenskaber.get("titel")
    ava_identifikation = egenskaber.get("brugervendtnoegle")
    ava_maalertype = egenskaber.get("beskrivelse")
    if relationer:
        installationstype = relationer.get("overordnetklasse")[0]
    else:
        # TODO: Change this when we add Arosia integration
        installationstype = {"urn": "urn:Varme"}

    # Convert type to literal
    type_ref = installationstype.get("urn").split(":")[-1]
    installation_types = {
        "Affald": 915240000,
        "Varme": 915240001
    }

    # Get type
    ava_installationstype = installation_types[type_ref]

    ava_maalernummer = egenskaber.get("eksempel")

    # AVA alternative address
    ava_adresse = None

    # Fetch alternative address
    alternative_address = relationer.get("ava_opstillingsadresse")

    if alternative_address:
        ava_adresse = alternative_address[0].get('uuid')

    # Referenced by other entities

    # Entity: Lora (Aftale/Indsats)
    # ava_aftale used to be nulled - below we take it from old_adapted
    # ava_aftale = None

    # Entity: Lora (Account/Interessefaellesskab)
    ava_kundenummer = old_adapted.get("data",{}).get("ava_kundenummer")

    # Arosia not yet implemented
    # ava_arosiaid = None

    # Cache layer compliant document
    document = {
        "id": origin_id,
        "external_ref": old_adapted.get("external_ref"),
        "indsats_ref": old_adapted.get("indsats_ref"),
        "dawa_ref": ava_adresse,
        "data": dict(old_adapted.get("data",{}))
    }
    
    document["data"].update({
        "ava_name": ava_name,
        "ava_identifikation": ava_identifikation,
        "ava_installationstype": ava_installationstype,
        "ava_maalernummer": ava_maalernummer,
        "ava_maalertype": ava_maalertype,
        "ava_kundenummer": ava_kundenummer
    })



    return document
