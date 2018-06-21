# -- coding: utf-8 --
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import adrog1_cpr_opslag_lokal
import os
import xmltodict
import settings
from ee_utils import say, cpr_cvr
# from ee_utils import get_forbrugssted_address_uuid
from service_clients import DAWA_ADDRESS_URL
from service_clients import get_address_from_service
from service_clients import report_error, fuzzy_address_uuid

# use the default envelope supplied by the module if none is specified
envelope = settings.ADRSOG1_SP_SOAP_REQUEST_ENVELOPE
if not envelope:
    envelope = os.path.join(
        os.path.dirname(adrog1_cpr_opslag_lokal.__file__),
        'soap_request_envelope.xml'
    )

dependencies = {
    'service_endpoint': settings.ADRSOG1_SP_SERVICE_ENDPOINT,
    'certificate': settings.ADRSOG1_SP_CERTIFICATE,
    'soap_request_envelope': (
        settings.ADRSOG1_SP_SOAP_REQUEST_ENVELOPE or envelope
    ),
    'system': settings.ADRSOG1_SP_SYSTEM,
    'user': settings.ADRSOG1_SP_USER,
    'service_agreement': settings.ADRSOG1_SP_SERVICE_AGREEMENT,
    'service': settings.ADRSOG1_SP_SERVICE
}

CNVN_STATUS_ACTIVE = {
    '01': True,  # "registreret med bopæl i dansk folkeregister"
    '03': True,  # "registreret med høj vejkode (9900 - 9999) DK"
    '05': True,  # "registreret med bopæl i grønlandsk folkeregister"
    '07': True,  # "registreret med høj vejkode (9900 - 9999) GL"
    '20': True,  # "registreret uden bopæl DK/GL - samt administrative"
    '30': False,  # "annulleret personnummer"
    '50': False,  # "slettet personnummer"
    '60': False,  # "ændret personnummer"
    '70': False,  # "forsvundet"
    '80': False,  # "udrejst"
    '90': False,  # "død (død eller død som udrejst eller forsvundet)"
}

STRINTS = [
    "BoligadminID", "FasadministratorID",
    "ForbrugsstedID", "Husnr", "Telefonnr", "Vejkode"
]

STRFLOATS = [
    "KundeSagsnr", "Kundenr",
    "LigestPersonnr", "PersonnrSEnr"
]


def get_results_on_address(**address):
    """ Parses a complex result from the service adrsog1
    and returns a dictionary with one entry per person
    who have lived / lives on address::

        {
            ("Pjotr Petterson", '311299'):{
                "cpr":"3112996789',
                "indflytningsdato": "19841231",
                "udflytningsdato": None,
            },
        }

    """

    person_numbers_from_adress = (
        adrog1_cpr_opslag_lokal.get_person_numbers_from_address(
            dependencies_dict=dependencies,
            address_dict=address
        )
    )

    # extract 'Row' payload from deeply nested SOAP structure
    nested = xmltodict.parse(person_numbers_from_adress)
    try:
        table = nested[
            'soap:Envelope'
        ][
            'soap:Body'
        ][
            'ns2:callGCTPCheckServiceResponse'
        ][
            'ns2:result'
        ][
            'root'
        ][
            'Gctp'
        ][
            'System'
        ][
            'Service'
        ][
            'CprData'
        ][
            'Rolle'
        ][
            'Table'
        ][
            'Row'
        ]

    except KeyError as e:
        say("Keyerror: %s, no address found for %r " % (str(e), address))
        return {}

    resultdict = {}

    # make sure payload is a list
    if not isinstance(table, list):
        table = [table]

    # extract key and value for each person from payload
    for row in table:
        if "Field" not in row:
            continue
        x = [k.get("@r") for k in row["Field"] if "@r" in k]
        if len(x) < len(row["Field"]):
            say("bad field - no @r at %r" % address)
            # not @r in all, irregular
            continue
        rowdict = {k.get("@r"): k for k in row["Field"]}
        if not CNVN_STATUS_ACTIVE.get(rowdict.get("CNVN_STATUS").get("@v")):
            say("code %s at %r" % (rowdict.get("CNVN_STATUS"), address))
            continue

        # convert date to danish cpr-prefix
        cpfx = rowdict["CPRS_FOEDDATO"]["@v"]
        cpfx = cpfx[6:8] + cpfx[4:6] + cpfx[2:4]

        row_result_key = (rowdict["CNVN_ADRNVN"].get("@t"), cpfx)
        if row_result_key in resultdict:
            # 'same' person in address - better bail till later
            report_error("double on birthday/name in %r %s" % (
                address, cpfx)
            )
            return {}

        resultdict[row_result_key] = {
            'cpr': rowdict["PNR"]["@v"],
            'indflytningsdato': rowdict["STARTDATO"]["@v"],
            'udflytningsdato': rowdict.get("SLUTDATO", {}).get("@v")
        }

    return resultdict


def get_cpr_by_name_firstsix_address(
    name,
    firstsix,
    **address
):
    """ find a cpr number from
        address, first six digits in cpr, and name
    """
    resultdict = get_results_on_address(**address)
    return resultdict.get((name, firstsix), {}).get("cpr")


def get_cpr_by_firstsix_address(
    firstsix,
    **address
):
    """ find a cpr number from
        address and first six digits in cpr
    """
    resultdict = get_results_on_address(**address)
    for name, cpfx in resultdict.keys():
        if firstsix == cpfx:
            return resultdict.get((name, firstsix), {}).get("cpr")


def stringalign_fields(fields):
    """ helper to convert all fields in a cust_dict to strings
        using cpr_cvr prefixing where appropriate
    """
    fields = dict(fields)
    for k, v in list(fields.items()):
        if k in STRINTS:
            fields[k] = str(v)
        elif k in STRFLOATS:
            fields[k] = str(int(v))
    fields["PersonnrSEnr"] = cpr_cvr(fields["PersonnrSEnr"])
    fields["LigestPersonnr"] = cpr_cvr(fields["LigestPersonnr"])
    return fields


def get_cpr_by_custdict(custdict, by_name=True):
    """ Returns a cpr if found using the fields in the custdict:

    * Vejkode
    * Husnr
    * Postnr
    * Etage
    * Sidedørnr
    * KundeNavn
    * PersonnrSEnr (first 6 digits)

    If *by_name* is False the lookup disregards KundeNavn

    """
    resultdict = get_results_on_address(
        street_code=custdict["Vejkode"],
        house_no=custdict["Husnr"],
        zip_code=custdict["Postnr"],
        floor=custdict["Etage"],
        door=custdict["Sidedørnr"]
    )

    if by_name:
        name = custdict["KundeNavn"]
        firstsix = custdict["PersonnrSEnr"][:6]
        return resultdict.get((name, firstsix), {}).get("cpr")
    else:
        firstsix = custdict["LigestPersonnr"][:6]
        # see if first six is the same as cpr prefix in key
        for name, cpfx in resultdict.keys():
            if firstsix == cpfx:
                return resultdict.get((name, firstsix), {}).get("cpr")


def complete_cprs_in_custdict(
    _new_fields,
    _old_fields,
):
    """ Potentially modifies:

    * _new_fields["PersonnrSEnr"]
    * _new_fields["LigestPersonnr"]

    Returns True if:

    * customer is a cvr-customer (company)
    * cpr number was found for inhabitant
      and no ligest-customer is registered.
      In this case _new_fields["PersonnrSEnr"] is completed inplace
    * cpr number was found for both inhabitant and ligest-customer.
      In this case _new_fields["PersonnrSEnr"]
      and _new_fields["LigestPersonnr"] are completed inplace

    Returns False otherwise
    """
    # make sure we are only using stringified copies
    # of the new/old dictionaries for the operation
    # thus we will not affect original program logic
    # should the last 4 chars return at some point
    # we can simply take this logic out of the loop again
    new_fields = stringalign_fields(_new_fields)
    old_fields = stringalign_fields(_old_fields) if _old_fields else None

    cpr_ok = (
        len(new_fields["PersonnrSEnr"]) < 10
        or new_fields["PersonnrSEnr"][-4:] != "0000"
    )

    ligest_ok = (
        len(new_fields["LigestPersonnr"]) < 10
        or new_fields["LigestPersonnr"][-4:] != "0000"
    )

    if cpr_ok and ligest_ok:
        return True

    # take shortcut if we have these fields available
    # in an already cached record
    elif old_fields:

        # possibly copy old cpr number
        if (
               old_fields["PersonnrSEnr"][:6] == new_fields["PersonnrSEnr"][:6]
               and old_fields["PersonnrSEnr"][-4:] != "0000"
        ):
            new_fields["PersonnrSEnr"] = old_fields["PersonnrSEnr"]
            _new_fields["PersonnrSEnr"] = float(new_fields["PersonnrSEnr"])
            cpr_ok = True
        if cpr_ok and ligest_ok:
            return True

        # possibly copy old ligest cpr number
        if (
               old_fields["LigestPersonnr"][:6] == (
                   new_fields["LigestPersonnr"][:6]
               ) and old_fields["LigestPersonnr"][-4:] != "0000"
        ):
            new_fields["LigestPersonnr"] = old_fields["LigestPersonnr"]
            _new_fields["LigestPersonnr"] = float(new_fields["LigestPersonnr"])
            ligest_ok = True
        if cpr_ok and ligest_ok:
            return True

    if not cpr_ok:
        # consumption point / utility_address is looked up from the fields
        # present in the custdict
        id_number = get_cpr_by_custdict(new_fields)
        if id_number:
            new_fields["PersonnrSEnr"] = id_number
            _new_fields["PersonnrSEnr"] = float(new_fields["PersonnrSEnr"])
            cpr_ok = True

        if not cpr_ok:
            # get at invoice address by use of fuzzyness
            invoice_address = (
                new_fields['VejNavn'].replace(',-', ' ') +
                ', ' + new_fields['Postdistrikt']
            )
            try:
                fau = fuzzy_address_uuid(invoice_address)
                address = get_address_from_service(
                    DAWA_ADDRESS_URL,
                    True,
                    address={'id': fau}
                )[1][0]

                # invoice address is cached on top
                # of consumtion point for cpr+ligest lookup
                new_fields["Husnr"] = address["husnr"]
                new_fields["Vejkode"] = address["vejkode"]
                new_fields["Postnr"] = address["postnr"]
                new_fields["Etage"] = address["etage"]
                new_fields["Husnr"] = address["husnr"]
                new_fields["Sidedørnr"] = address["dør"]
                id_number = get_cpr_by_custdict(new_fields)
                if id_number:
                    new_fields["PersonnrSEnr"] = id_number
                    # float is the original storage type
                    _new_fields["PersonnrSEnr"] = float(
                        new_fields["PersonnrSEnr"]
                    )
                    cpr_ok = True
            except Exception as e:
                print(e)

        if not cpr_ok:
            report_error("could not look up PersonnrSEnr for %s" % (
                new_fields["Kundenr"]
            ))
            return False

        if not ligest_ok:
            id_number = get_cpr_by_custdict(new_fields, by_name=False)
            if id_number:
                new_fields["LigestPersonnr"] = id_number
                _new_fields["LigestPersonnr"] = float(
                    new_fields["LigestPersonnr"]
                )
                ligest_ok = True

        if not ligest_ok:
            report_error("could not look up LigestPersonnr for %s" % (
                new_fields["Kundenr"]
            ))
            return False

    return True
