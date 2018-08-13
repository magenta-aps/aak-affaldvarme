# -*- coding: utf-8 -*-


# skip module level code when 
# generating top level documentation
import sys
if not sys.base_prefix.endswith("/docs/python-env"):

    import crm_interface as crm
    import cache_interface as cache
    import dawa_interface as dawa

    from helper import get_config
    from logging import getLogger
    import copy


    # Init logging
    log = getLogger(__name__)

    # Get config
    config = get_config()


def export_everything():
    """
    Export everything (in sequence) from the cache layer to CRM.
    During this process all the relations between the entities are created.
    Relations are stored in the cache layer as references.

    TODO:   This function should be rewritten to base relations
            on 'contacts' rather than 'kunderolles'.
    """

    all_kunderolle = cache.all("ava_kunderolles")

    for kunderolle in all_kunderolle:
        process(kunderolle)


def process(kunderolle):
    """
    Process sequence of related documents (by 'ava_kunderolles')
    TODO: Process should be merged with all of the updates modules.

    (For further information, see update functions below)

    :param kunderolle:  Kunderolle document retrieved from the cache layer.

    :return:
    """

    # calls to store an entity in crm may fail and thus cause the value False
    # to be inserted as external_ref. It should maybe have been Null, but the
    # False value is nice - it can be used to check in the cache layer which
    # entities failed when inserting into crm. The False value will cause
    # a retry next time the program is run
    #

    # Prepare lookup reference fallback
    lookup_contact = None
    lookup_account = None
    lookup_aftale = None
    lookup_address = None
    lookup_billing_address = None

    # skip-if-no-changes references
    # DO NOT USE for other purpose than indicators of change
    kunderolle_ref = kunderolle["id"]
    SINC = config.getboolean("skip-if-no-changes", fallback=True)
    if SINC:
        kunderolle_cached = copy.deepcopy(kunderolle)
    else:
        kunderolle_cached = {}

    contact_cached = {}
    aftale_cached = {}
    billing_address_cached = {}
    utility_address_cached = {}
    contact_address_cached = {}
    kundeforhold_cached = {}
    produkt_cached = {}

    # progress - which was transferred
    progress_log = {}

    # May not be needed:
    lookup_utility_address = None
    # lookup_kunderolle = None

    # Hotfix:
    # To create a link between contact and aftale,
    # We need the CRM GUID references
    contact_external_ref = None
    aftale_external_ref = None

    # References
    contact_ref = kunderolle["contact_ref"]
    interessefaellesskab_ref = kunderolle["interessefaellesskab_ref"]

    # Kundeforhold - moved here for logging purposes
    kundeforhold = cache.get(
        table="accounts",
        uuid=interessefaellesskab_ref
    )
    if kundeforhold:
        ava_kundenummer = kundeforhold["data"]["ava_kundenummer"]
    else:
        log.error("Kundeforhold not found: {}".format(
            interessefaellesskab_ref)
        )
        log.error(kunderolle)
        return

    # Customer/Contact
    if contact_ref:
        contact = cache.get(table="contacts", uuid=contact_ref)
    else:
        contact = None

    if not contact:
        log.error("Contact not found: {}".format(contact_ref))
        log.error(kunderolle)
        log.error(
            "ee-ref kundenummer {0} "
            "contact ikke fundet på reference {1} i kunderolle {2}" .format(
                ava_kundenummer,
                contact_ref,
                kunderolle_ref
            )
        )
        return False

    # skip-if-no-changes reference
    contact_cached = copy.deepcopy(contact)

    # Set KMDEE email address as primary if primary is null
    secondary_email = contact["data"]["ava_emailkmdee"]

    # Set primary email
    contact["data"]["emailaddress1"] = secondary_email

    # Address
    address_ref = contact["dawa_ref"]

    if not address_ref:
        log.info("No address reference found, skipping")
        log.debug("Kunderolle: {0}".format(kunderolle.get("_id")))
        log.debug("Contact: {0}".format(contact.get("_id")))
        log.error(
            "ee-ref kundenummer {0} "
            "har ingen adresse på contact {1}".format(
                ava_kundenummer,
                contact_ref
            )
        )
        return False

    address = cache.get(table="ava_adresses", uuid=address_ref)

    if not address:

        dawa_address = dawa.get_address(address_ref)
        if dawa_address:
            # Store address in the cache layer
            cache.store(resource="dawa", payload=dawa_address)
            # Get from cache once more
            address = cache.get(table="ava_adresses", uuid=address_ref)

    if not address:
        log.warn(
            "address {address_ref} not cached, "
            "skipping contact {contact_ref}".format(**locals())
        )
        log.error(
            "ee-ref kundenummer {0} "
            "adresse ikke fundet på reference {1} i contact {2}".format(
                ava_kundenummer,
                address_ref,
                contact_ref
            )
        )
        return False

    # this doesn't do that much but look like the others
    # skip-if-no-changes reference
    if SINC:
        contact_address_cached = copy.deepcopy(address)

    # Export address
    # Depends on: None
    if not address["external_ref"]:
        address["external_ref"] = crm.store_address(address["data"])
        address["import_changed"] = False
    elif address != contact_address_cached or address.get("import_changed"):
        if crm.update_address(
            identifier=address["external_ref"],
            payload=address["data"]
        ):
            address["import_changed"] = False

    else:
        log.debug("skipping NOP address update for {id}".format(**address))
        log.debug("{a} == {b}".format(
            a=address,
            b=contact_address_cached)
        )

    if address != contact_address_cached:
        update_cache = cache.update(
            table="ava_adresses",
            document=address
        )
        log.info("Updating cache for contact address")
        log.info(update_cache)

    lookup_address = "/ava_adresses({external_ref})".format(
        external_ref=address["external_ref"]
    )
    contact["data"]["ava_adresse@odata.bind"] = lookup_address

    # Export contact
    # Depends on: address
    if not contact["external_ref"]:
        contact["external_ref"] = crm.store_contact(contact["data"])
        contact["import_changed"] = False
    elif contact != contact_cached or contact.get("import_changed"):
        if crm.update_contact(
            identifier=contact["external_ref"],
            payload=contact["data"]
        ):
            contact["import_changed"] = False

    else:
        log.debug("skipping NOP contact update for {id}".format(**contact))
        log.debug("{a} == {b}".format(a=contact, b=contact_cached))

    if contact != contact_cached:
        update_cache = cache.update(
            table="contacts",
            document=contact
        )
        log.info("Updating cache for contact")
        log.info(update_cache)

    # Update contact lookup
    lookup_contact = "/contacts({external_ref})".format(
        external_ref=contact["external_ref"]
    )

    progress_log.update({
        "type": "cvr" if contact["data"].get("ava_cvr_nummer") else "cpr",
        "lora_ref": contact["id"],
        "contact_ref": contact["external_ref"],
        "firstname": contact["data"].get("firstname", ""),
        "lastname": contact["data"].get("lastname", ""),
        "mobil": contact["data"]["ava_mobilkmdee"],
        "email": contact["data"]["ava_emailkmdee"],
        "adresse": address["data"]["ava_name"]
    })

    # Utility address
    utility_address_ref = kundeforhold.get("dawa_ref")

    # Fallback
    utility_address = None
    utility_address_table = None

    if utility_address_ref: #  try both places before giving up and fetching

        utility_address = cache.get(
            table="ava_adresses",
            uuid=utility_address_ref
        )
        utility_address_table = "ava_adresses"

        if not utility_address:
            utility_address = cache.get(
                table="access",
                uuid=utility_address_ref
            )
            utility_address_table = "access"

        if not utility_address:
            utility_address = dawa.get_address(utility_address_ref)
            if utility_address:
                log.info("storing new utility_address from dawa")
                # Store address in cache layer
                cache.store(resource="dawa", payload=utility_address)
                # Get newly stored address
                utility_address = cache.get(
                    table="ava_adresses",
                    uuid=utility_address_ref
                )
            if utility_address:
                utility_address_table = "ava_adresses"

        if not utility_address:
            if not utility_address:
                utility_address = dawa.get_access_address(utility_address_ref)
                if utility_address:
                    log.info("storing new utility_address from dawa_access")
                    # Store address in cache layer
                    cache.store(
                        resource="dawa_access",
                        payload=utility_address
                    )
                    # Get newly stored address
                    utility_address = cache.get(
                        table="access",
                        uuid=utility_address_ref
                    )
                if utility_address:
                    utility_address_table = "access"

    if not utility_address:
        log.error(
            "ee-ref kundenummer {0} "
            "adgangsadresse kunne ikke slås op "
            "på reference {1} i account {2}".format(
                ava_kundenummer,
                utility_address_ref,
                interessefaellesskab_ref
            )
        )

    if utility_address:

        if SINC:
            utility_address_cached = copy.deepcopy(utility_address)

        if not utility_address["external_ref"]:
            utility_address["external_ref"] = crm.store_address(
                utility_address["data"]
            )
            utility_address["import_changed"] = False
        elif (
                utility_address != utility_address_cached
                or utility_address.get("import_changed")
               ):
            if crm.update_address(
                identifier=utility_address["external_ref"],
                payload=utility_address["data"]
            ):
                utility_address["import_changed"] = False
        else:
            log.debug("skipping NOP utility_address update for {id}".format(
                **utility_address)
            )
            log.debug("{a} == {b}".format(
                a=utility_address,
                b=utility_address_cached)
            )

        if utility_address != utility_address_cached:
            update_cache = cache.update(
                table=utility_address_table,
                document=utility_address
            )
            log.info("Updating cache for utility_address")
            log.info(update_cache)

        lookup_utility_address = "/ava_adresses({external_ref})".format(
            external_ref=utility_address["external_ref"]
        )

    kundeforhold_data = kundeforhold["data"]

    # skip-if-no-changes reference
    if SINC:
        kundeforhold_cached = copy.deepcopy(kundeforhold)

    if lookup_utility_address:
        kundeforhold_data[
            "ava_adresse@odata.bind"
        ] = lookup_utility_address

    if not kundeforhold["external_ref"]:
        kundeforhold["external_ref"] = crm.store_account(kundeforhold_data)
        kundeforhold["import_changed"] = False
    elif (
            kundeforhold != kundeforhold_cached
            or kundeforhold.get("import_changed")
            ):
        if crm.update_account(
            identifier=kundeforhold["external_ref"],
            payload=kundeforhold["data"]
        ):
            kundeforhold["import_changed"] = False

    else:
        log.debug("skipping NOP kundeforhold update for {id}".format(
            **kundeforhold)
        )
        log.debug("{a} == {b}".format(
            a=kundeforhold,
            b=kundeforhold_cached)
        )

    if kundeforhold != kundeforhold_cached:
        update_cache = cache.update(
            table="accounts",
            document=kundeforhold
        )
        log.info("Updating cache for kundeforhold")
        log.info(update_cache)

    # Update account lookup
    lookup_account = "/accounts({external_ref})".format(
        external_ref=kundeforhold["external_ref"]
    )

    # Kunderolle
    # Depends on: Contact, Account

    # Resolve dependencies for Kunderolle
    kunderolle_data = kunderolle["data"]

    if lookup_contact:
        kunderolle_data["ava_aktoer@odata.bind"] = lookup_contact

    if lookup_account:
        kunderolle_data["ava_kundeforhold@odata.bind"] = lookup_account

    if not kunderolle["external_ref"]:
        log.info("Kunderolle does not exist in CRM")
        kunderolle["external_ref"] = crm.store_kunderolle(
            kunderolle_data
        )
        kunderolle["import_changed"] = False
    elif kunderolle != kunderolle_cached or kunderolle.get("import_changed"):
        if crm.update_kunderolle(
            identifier=kunderolle["external_ref"],
            payload=kunderolle["data"]
        ):
            kunderolle["import_changed"] = False
    else:
        log.debug("skipping NOP kunderolle update for {id}".format(
            **kunderolle)
        )
        log.debug("{a} == {b}".format(
            a=kunderolle["data"],
            b=kunderolle_cached)
        )

    if kunderolle != kunderolle_cached:
        update_cache = cache.update(
            table="ava_kunderolles",
            document=kunderolle
        )
        log.info("Updating cache for organisationfunktion")
        log.info(update_cache)

    # why update account-lookup, when reference is to a kunderolle?
    # old error?
    # Update account lookup
    # if "external_ref" in kunderolle:
    #     lookup_account = "/accounts({external_ref})".format(
    #         external_ref=kunderolle["external_ref"]
    #     )

    # Aftale
    aftale = cache.find_indsats(interessefaellesskab_ref)

    if not aftale:
        log.warning("Aftale does not exist")
        log.error(
            "ee-ref kundenummer {0} "
            "aftale ikke fundet på reference {1} i kunderolle {2}".format(
                ava_kundenummer,
                interessefaellesskab_ref,
                kunderolle_ref
            )
        )
        return

    # skip-if-no-changes reference
    if SINC:
        aftale_cached = copy.deepcopy(aftale)

    # Billing address
    billing_address_ref = aftale.get("dawa_ref")

    # Fallback
    billing_address = None

    if billing_address_ref:
        billing_address = cache.get(
            table="ava_adresses",
            uuid=billing_address_ref
        )

        if not billing_address:
            log.info("Address does not exist in the cache layer, importing")
            dawa_address = dawa.get_address(billing_address_ref)
            if dawa_address:
                # Store address in cache layer
                cache.store(resource="dawa", payload=dawa_address)

                # Get newly stored address
                billing_address = cache.get(
                    table="ava_adresses",
                    uuid=billing_address_ref
                )
        if not billing_address:
            log.error(
                "ee-ref kundenummer {0} "
                "faktureringsadresse kunne ikke slås op "
                "på reference {1} i aftale {2}".format(
                    ava_kundenummer,
                    billing_address_ref,
                    interessefaellesskab_ref
                )
            )

    if billing_address:

        # this doesn't do that much but look like the others
        # skip-if-no-changes reference
        if SINC:
            billing_address_cached = copy.deepcopy(billing_address)

        if not billing_address["external_ref"]:
            billing_address["external_ref"] = crm.store_address(
                billing_address["data"]
            )
            billing_address["import_changed"] = False
        elif (
                billing_address != billing_address_cached
                or billing_address.get("import_changed")
                ):
            if crm.update_address(
                identifier=billing_address["external_ref"],
                payload=billing_address["data"]
            ):
                billing_address["import_changed"] = False
        else:
            log.debug("skipping NOP billing_address update for {id}".format(
                **billing_address)
            )
            log.debug("{a} == {b}".format(
                a=billing_address,
                b=billing_address_cached)
            )

        if billing_address != billing_address_cached:
            update_cache = cache.update(
                table="ava_adresses",
                document=billing_address
            )
            log.info("Updating cache for billing_address")
            log.info(update_cache)

        lookup_billing_address = "/ava_adresses({external_ref})".format(
            external_ref=billing_address["external_ref"]
        )

    aftale_data = aftale["data"]

    if lookup_account:
        kundeforhold_bind = "ava_kundeforhold@odata.bind"
        aftale_data[kundeforhold_bind] = lookup_account

    if lookup_billing_address:
        billing_bind = "ava_faktureringsadresse@odata.bind"
        aftale_data[billing_bind] = lookup_billing_address

    log.debug("AFTALE DATA CHECK:")
    log.debug(aftale_data)

    if not aftale.get("external_ref"):
        aftale["external_ref"] = crm.store_aftale(aftale_data)
        aftale["import_changed"] = False
    elif aftale != aftale_cached or aftale.get("import_changed"):
        if crm.update_aftale(
            identifier=aftale["external_ref"],
            payload=aftale["data"]
        ):
            aftale["import_changed"] = False
    else:
        log.debug("skipping NOP aftale update for {id}".format(**aftale))
        log.debug("{a} == {b}".format(a=aftale, b=aftale_cached))

    # Create / replace link between aftale and contact
    # This one should probably copy the procedure which we
    # have below with the customer_number -
    # only have the latest updated
    if crm.mend_contact_and_aftale_link(contact, aftale, SINC):

        # only progress log if successfull
        if False:
            log.info(
                "Overført {type}: {firstname} {lastname},"
                " {adresse}, mobil:{mobil}, email:{email}"
                " crm:{contact_ref}, lora:{lora_ref}".format(
                    **progress_log
                )
            )
        else:
            log.info(
                "Overført {type}: xxxx,"
                " {adresse}, mobil:xxxx, email:xxxx"
                " crm:{contact_ref}, lora:{lora_ref}".format(
                    **progress_log
                )
            )

    if aftale != aftale_cached:
        update_cache = cache.update(
            table="ava_aftales",
            document=aftale
        )
        log.info("Updating cache for indsats")
        log.info(update_cache)

    # Update aftale lookup
    aftale_external_ref = aftale["external_ref"]

    lookup_aftale = "/ava_aftales({external_ref})".format(
        external_ref=aftale["external_ref"]
    )

    # Installation
    klasse_ref = aftale["klasse_ref"]

    if not klasse_ref:
        log.warning(
            "No reference for product found: {internal}".format(
                internal=aftale.get("id"),
            )
        )
        log.error(
            "ee-ref kundenummer {0} "
            "klasse-ref mangler på aftale {1}".format(
                ava_kundenummer,
                aftale["id"],
            )
        )
        return

    produkt = cache.get(table="ava_installations", uuid=klasse_ref)

    if not produkt:
        log.warning("Produkt does not exist")
        log.error(
            "ee-ref kundenummer {0} "
            "Produkt for aftale {1} kunne ikke findes på reference {2}".format(
                ava_kundenummer,
                aftale["id"],
                klasse_ref
            )
        )
        return

    # skip-if-no-changes reference
    if SINC:
        produkt_cached = copy.deepcopy(produkt)

    # TODO: utility address must be added here
    # Utility address fallback

    #utility_address = None

    if produkt["dawa_ref"]:

        utility_ref = produkt["dawa_ref"]

        # Debug
        log.debug("Found utility address reference: {reference}".format(
                reference=utility_ref
            )
        )

        # Get address external ref
        utility_address = cache.get(
            table="access",
            uuid=utility_ref
        )

        # If address does not exist in the cache layer
        # Get from DAR and store in cache

        if not utility_address:
            # Info
            log.info(
                "Utility address not found, importing from DAWA"
            )
            utility_address = dawa.get_access_address(utility_ref)

            # Debug
            log.debug("Utility address: {0}".format(utility_address))

        if not utility_address:

            log.error(
                "ee-ref installationsnummer {0} "
                "utility-addresse kunne ikke slås op "
                "på reference {1} for produkt {2}".format(
                    produkt["data"]["ava_maalernummer"],
                    utility_ref,
                    klasse_ref,
                )
            )

    if utility_address:

        # this doesn't do that much but look like the others
        # skip-if-no-changes reference
        if SINC:
            utility_address_cached = copy.deepcopy(utility_address)

        if not utility_address["external_ref"]:
            utility_address["external_ref"] = crm.store_address(
                utility_address["data"]
            )
            utility_address["import_changed"] = False
        elif (
                utility_address != utility_address_cached
                or utility_address.get("import_changed")
                ):
            if crm.update_address(
                identifier=utility_address["external_ref"],
                payload=utility_address["data"]
            ):
                utility_address["import_changed"] = False

        else:
            log.debug("skipping NOP utility address update for {id}".format(
                **utility_address)
            )
            log.debug("{a} == {b}".format(
                a=utility_address,
                b=utility_address_cached)
            )

        if utility_address != utility_address_cached:
            # Store in cache
            cache.store(
                resource="dawa_access",
                payload=utility_address
            )

        # Update utility address lookup
        lookup_utility_address = "/ava_adresses({reference})".format(
            reference=utility_address["external_ref"]
        )



    # Workaround: Just inserting billing address
    # This workaround is nowhere to be found, maybe time for it.

    # But here is something else
    # This is a controversial fix. We know that customer_numbers are going up 
    # alongside the agreement periods, so we only update the customer_number on the produkt
    # only if the current is greater than the previous. That should work.
    # So after one complete run the produkts should all have the correct kundenummer
    # but what about ava_aftale_odata_bind?
    # well - the agreement should match che account, where only the latest concerning the 
    # product gets to have something to say 
    # so we only update the bind-fields on the latest agreement
     
    if (
        not produkt["data"].get("ava_kundenummer")
        or int(produkt["data"]["ava_kundenummer"]) <= int(ava_kundenummer)
    ):
        produkt["data"]["ava_kundenummer"] = ava_kundenummer
        produkt["data"]["ava_aftale@odata.bind"] = lookup_aftale
        # this utility address can be a fall through from kundeforhold
        produkt["data"]["ava_adresse@odata.bind"] = lookup_utility_address
        produkt["indsats_ref"] = aftale["id"]

    # end of controversial change

    if not produkt["external_ref"]:
        produkt["external_ref"] = crm.store_produkt(produkt["data"])
        produkt["import_changed"] = False
    elif produkt != produkt_cached or produkt.get("import_changed"):
        if crm.update_produkt(
            identifier=produkt["external_ref"],
            payload=produkt["data"]
        ):
            produkt["import_changed"] = False
    else:
        log.debug("skipping NOP produkt update for {id}".format(**produkt))
        log.debug("{a} == {b}".format(a=produkt, b=produkt_cached))

    if produkt != produkt_cached:
        update_cache = cache.update(
            table="ava_installations",
            document=produkt
        )
        log.info("Updating cache for produkt")
        log.info(update_cache)


def update_all_installations():
    """
    Alternative addresses for installations (Produkt)
    The Lora entity is "klasse"
    """

    all_installations = []

    for installation in cache.all("ava_installations"):

        if not installation["dawa_ref"]:
            continue

        # Append all objects that contain an alternative address
        all_installations.append(installation)

    for installation in all_installations:
        update_alternative_address(installation)


def update_alternative_address(installation):

    # Identifier
    identifier = installation["_id"]

    # DEBUG
    log.debug(
        "Processing installation: {id}".format(id=identifier)
    )
    log.debug(installation)

    resource = "access"

    if not installation["external_ref"]:
        log.info("No external reference found")
        return False

    address_ref = installation["dawa_ref"]

    access_address = cache.get(resource, address_ref)

    if not access_address:
        log.info("Access address does not yet exist, creating")

        try:
            # Return adapted access address
            log.info("Attempting to retrieve access address from DAWA")
            access_address = dawa.get_access_address(address_ref)
            log.debug(access_address)

            # Store address externally (CRM)
            log.info("Attempting to store access address")
            access_address["external_ref"] = crm.store_address(
                access_address["data"]
            )

            # Update cache
            log.info("Attempting to update cache for access address")
            cache.store("access", access_address)

        except Exception as error:
            log.error("Failed to create access address:")
            log.error(error)
            return False

    if not access_address["external_ref"]:
        log.warning(
            "No external ref found for access address: {reference}".format(
                reference=access_address["_id"]
            )
        )

    # Hotfix:
    # Create fallback
    if "lookup_access_address" not in installation:
        log.debug("Creating access address lookup key")
        installation["lookup_access_address"] = None

    if not installation["lookup_access_address"]:
        log.info("Creating lookup for access address")
        lookup_utility_address = "/ava_adresses({external_ref})".format(
            external_ref=access_address["external_ref"]
        )

        try:
            log.info("Updating installation with access address")

            payload = {
                "ava_adresse@odata.bind": lookup_utility_address
            }

            update_response = crm.update_produkt(
                identifier=installation["external_ref"],
                payload=payload
            )

            if not update_response:
                log.debug("Update failed: ")
                log.debug(update_response.text)

            installation["lookup_access_address"] = lookup_utility_address

            # Update cache
            log.info("Attempting to update cache for installation")
            update_cache = cache.update(
                table="ava_installations",
                document=installation
            )

            if not update_cache:
                log.debug(update_cache)

        except Exception as error:
            log.error(
                "Error updating access address for: {reference}".format(
                    reference=installation["_id"]
                )
            )
            log.error(error)

    return True
