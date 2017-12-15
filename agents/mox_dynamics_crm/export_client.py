# -*- coding: utf-8 -*-

import logging
import crm_interface as crm
import cache_interface as cache
import dawa_interface as dawa


# Init logger
log = logging.getLogger(__name__)


def export_everything():
    all_kunderolle = []

    for kunderolle in cache.find_all("organisationfunktion"):
        all_kunderolle.append(kunderolle)

    for kunderolle in all_kunderolle:
        process(kunderolle)


def process(kunderolle):

    # Prepare lookup reference fallback
    lookup_contact = None
    lookup_account = None
    lookup_aftale = None
    lookup_address = None
    lookup_billing_address = None
    lookup_utility_address = None
    lookup_kunderolle = None

    # References
    contact_ref = kunderolle["contact_ref"]
    interessefaellesskab_ref = kunderolle["interessefaellesskab_ref"]

    # Customer/Contact
    contact = cache.find("contact", contact_ref)

    # Address
    address_ref = contact["dawa_ref"]
    address = cache.find("dawa", address_ref)

    if not address:
        dawa_address = dawa.get_address(address_ref)
        store = cache.store_address(dawa_address)
        address = cache.find("dawa", address_ref)

    # Export address
    # Depends on: None
    if not address["external_ref"]:
        address_data = address["data"]
        address["external_ref"] = crm.store_address(address_data)

        update_cache = cache.update_or_insert(
            resource="dawa",
            payload=address
        )

        log.info("Updating cache for klasse")
        log.info(update_cache)

    # Update address lookup
    lookup_address = "/ava_adresses({external_ref})".format(
        external_ref=address["external_ref"]
    )

    # Export contact
    # Depends on: address
    if not contact["external_ref"]:
        contact_data = contact["data"]
        contact_data["ava_adresse@odata.bind"] = lookup_address
        contact["external_ref"] = crm.store_contact(contact_data)

        update_cache = cache.update_or_insert(
            resource="contact",
            payload=contact
        )

        log.info("Updating cache for contact")
        log.info(update_cache)

    # Update contact lookup
    lookup_contact = "/contacts({external_ref})".format(
        external_ref=contact["external_ref"]
    )

    # Kundeforhold
    kundeforhold = cache.find(
        "interessefaellesskab",
        interessefaellesskab_ref
    )

    # Billing address
    billing_address_ref = kundeforhold["dawa_ref"]

    if billing_address_ref:
        billing_address = cache.find("dawa", billing_address_ref)

        if not billing_address:
            dawa_address = dawa.get_address(billing_address_ref)
            if dawa_address:
                store = cache.store_address(dawa_address)
                billing_address = cache.find("dawa", billing_address_ref)

        if billing_address:

            if not billing_address["external_ref"]:
                billing_address["external_ref"] = crm.store_address(
                    billing_address["data"]
                )

                update_cache = cache.update_or_insert(
                    resource="dawa",
                    payload=billing_address
                )

                log.info("Updating cache for billing_address")
                log.info(update_cache)

            # Update address lookup
            lookup_billing_address = "/ava_adresses({external_ref})".format(
                external_ref=billing_address["external_ref"]
            )

    if not kundeforhold["external_ref"]:
        kundeforhold_data = kundeforhold["data"]
        kundeforhold_data["ava_adresse@odata.bind"] = lookup_billing_address
        kundeforhold["external_ref"] = crm.store_account(kundeforhold_data)

        update_cache = cache.update_or_insert(
            resource="interessefaellesskab",
            payload=kundeforhold
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
    kunderolle_data["ava_aktoer@odata.bind"] = lookup_contact
    kunderolle_data["ava_kundeforhold@odata.bind"] = lookup_account

    if not kunderolle["external_ref"]:
        log.info("Kunderolle does not exist in CRM")
        kunderolle["external_ref"] = crm.store_kunderolle(
            kunderolle_data
        )

        update_cache = cache.update_or_insert(
            resource="organisationfunktion",
            payload=kunderolle
        )

        log.info("Updating cache for organisationfunktion")
        log.info(update_cache)

    # Aftale
    aftale = cache.find_indsats(interessefaellesskab_ref)

    if not aftale:
        log.warning("Aftale does not exist")
        return

    if not aftale["external_ref"]:
        aftale_data = kundeforhold["data"]

        # Dependencies
        kundeforhold_bind = "ava_kundeforhold@odata.bind"
        billing_bind = "ava_faktureringsadresse@odata.bind"

        aftale_data[kundeforhold_bind] = lookup_account
        aftale_data[billing_bind] = lookup_billing_address

        aftale["external_ref"] = crm.store_aftale(aftale_data)

        update_cache = cache.update_or_insert(
            resource="indsats",
            payload=aftale
        )

        log.info("Updating cache for indsats")
        log.info(update_cache)

    # Update aftale lookup
    lookup_account = "/ava_aftales({external_ref})".format(
        external_ref=aftale["external_ref"]
    )

    # Installation
    klasse_ref = aftale["klasse_ref"]
    produkt = cache.find("klasse", klasse_ref)

    if not produkt:
        log.warning("Produkt does not exist")
        return

    if not produkt["external_ref"]:
        produkt_data = produkt["data"]

        # TODO: utility address must be added here
        # Workaround: Just inserting billing address
        ava_kundenummer = kundeforhold["data"]["ava_kundenummer"]
        produkt_data["ava_kundenummer"] = ava_kundenummer
        produkt_data["ava_adresse@odata.bind"] = lookup_billing_address
        produkt["external_ref"] = crm.store_produkt(produkt_data)

        update_cache = cache.update_or_insert(
            resource="klasse",
            payload=produkt
        )

        log.info("Updating cache for produkt")
        log.info(update_cache)


if __name__ == "__main__":
    print("Begin exporting to crm")

    # Run
    export_everything()

    # Done
    print("All done")
