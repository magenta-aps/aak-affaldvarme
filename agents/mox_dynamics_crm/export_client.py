# -*- coding: utf-8 -*-

import crm_interface as crm
import cache_interface as cache
import dawa_interface as dawa

from helper import get_config
from logging import getLogger


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

    all_kunderolle = [k for k in cache.all("ava_kunderolles")]

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

    # Prepare lookup reference fallback
    lookup_contact = None
    lookup_account = None
    lookup_aftale = None
    lookup_address = None
    lookup_billing_address = None

    # May not be needed:
    # lookup_utility_address = None
    # lookup_kunderolle = None

    # Hotfix:
    # To create a link between contact and aftale,
    # We need the CRM GUID references
    contact_external_ref = None
    aftale_external_ref = None

    # References
    contact_ref = kunderolle["contact_ref"]
    interessefaellesskab_ref = kunderolle["interessefaellesskab_ref"]

    # Customer/Contact
    if contact_ref:
        contact = cache.get(table="contacts", uuid=contact_ref)
    else:
        contact = None

    if not contact:
        log.error("Contact not found: {}".format(contact_ref))
        log.error(kunderolle)
        return False

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
        return False

    address = cache.get(table="ava_adresses", uuid=address_ref)

    if not address:
        dawa_address = dawa.get_address(address_ref)

        # Store address in the cache layer
        cache.store(resource="dawa", payload=dawa_address)

        # Get from cache once more
        address = cache.get(table="ava_adresses", uuid=address_ref)

    if not address:
        log.warn(
            "address {address_ref} not cached, "
            "skipping contact {contact_ref}".format(**locals())
        )
        return False

    # Export address
    # Depends on: None
    if not address["external_ref"]:
        address["external_ref"] = crm.store_address(address["data"])
    else:
        crm.update_address(
            identifier=address["external_ref"],
            payload=address["data"]
        )

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
    else:
        crm.update_contact(
            identifier=contact["external_ref"],
            payload=contact["data"]
        )

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

    # Kundeforhold
    kundeforhold = cache.get(
        table="accounts",
        uuid=interessefaellesskab_ref
    )

    # Billing address
    billing_address_ref = kundeforhold.get("dawa_ref")

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

    if billing_address:

        if not billing_address["external_ref"]:
            billing_address["external_ref"] = crm.store_address(
                billing_address["data"]
            )
        else:
            crm.update_address(
                identifier=billing_address["external_ref"],
                payload=billing_address["data"]
            )

        update_cache = cache.update(
            table="ava_adresses",
            document=billing_address
        )
        log.info("Updating cache for billing_address")
        log.info(update_cache)

        lookup_billing_address = "/ava_adresses({external_ref})".format(
            external_ref=billing_address["external_ref"]
        )

    kundeforhold_data = kundeforhold["data"]
    if lookup_billing_address:
        kundeforhold_data[
            "ava_adresse@odata.bind"
        ] = lookup_billing_address

    if not kundeforhold["external_ref"]:
        kundeforhold["external_ref"] = crm.store_account(kundeforhold_data)
    else:
        crm.update_account(
            identifier=kundeforhold["external_ref"],
            payload=kundeforhold["data"]
        )

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
    else:
        crm.update_kunderolle(
            identifier=kunderolle["external_ref"],
            payload=kunderolle["data"]
        )

    update_cache = cache.update(
        table="ava_kunderolles",
        document=kunderolle
    )

    log.info("Updating cache for organisationfunktion")
    log.info(update_cache)

    # Update account lookup
    if "external_ref" in kunderolle:
        lookup_account = "/accounts({external_ref})".format(
            external_ref=kunderolle["external_ref"]
        )

    # Aftale
    aftale = cache.find_indsats(interessefaellesskab_ref)

    if not aftale:
        log.warning("Aftale does not exist")
        return

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
    else:
        crm.update_aftale(
            identifier=aftale["external_ref"],
            payload=aftale["data"]
        )

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

    # Create link between aftale and contact
    crm.contact_and_aftale_link(
        contact_guid=contact_external_ref,
        aftale_guid=aftale_external_ref
    )

    # Installation
    klasse_ref = aftale["klasse_ref"]

    if not klasse_ref:
        log.warning(
            "No reference for product found: {internal}".format(
                internal=aftale.get("id"),
            )
        )
        return

    produkt = cache.get(table="ava_installations", uuid=klasse_ref)

    if not produkt:
        log.warning("Produkt does not exist")
        return

    # TODO: utility address must be added here
    # Utility address fallback

    utility_address = None

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

    if utility_address:

        if not utility_address["external_ref"]:
            utility_address["external_ref"] = crm.store_address(
                utility_address["data"]
            )
        else:
            crm.update_address(
                identifier=utility_address["external_ref"],
                payload=utility_address["data"]
            )

        # Store in cache
        cache.store(
            resource="dawa_access",
            payload=utility_address
        )

        # Update utility address lookup
        lookup_utility_address = "/ava_adresses({reference})".format(
            reference=utility_address["external_ref"]
        )

        produkt["data"]["ava_adresse@odata.bind"] = lookup_utility_address

    # Workaround
    if aftale_external_ref:
        produkt["indsats_ref"] = aftale_external_ref


    # Workaround: Just inserting billing address
    ava_kundenummer = kundeforhold["data"]["ava_kundenummer"]
    produkt["data"]["ava_kundenummer"] = ava_kundenummer

    if lookup_aftale:
        produkt["data"]["ava_aftale@odata.bind"] = lookup_aftale

    if not produkt["external_ref"]:
        produkt["external_ref"] = crm.store_produkt(produkt["data"])
    else:
        crm.update_produkt(
            identifier=produkt["external_ref"],
            payload=produkt["data"]
        )


    # Update cache
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
