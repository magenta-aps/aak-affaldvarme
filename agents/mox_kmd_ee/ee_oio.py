import datetime
import requests

# TODO: Use authentication & real user UUID.
SYSTEM_USER = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# AVA-Organisation
AVA_ORGANISATION = "cb8122fe-96c6-11e7-8725-6bc18b080504"

# API URL
BASE_URL = "http://agger"


def create_virkning(frm=datetime.datetime.now(),
                    to="infinity",
                    user=SYSTEM_USER,
                    note=""):
    virkning = {
        "from": str(frm),
        "to": str(to),
        "aktoerref": user,
        "aktoertypekode": "Bruger",
        "notetekst": note
    }

    return virkning


def create_organisation(cvr_number, key, name, phone="", email="",
                        mobile="", fax="", note=""):
    virkning = create_virkning()
    organisation_dict = {
        "note": note,
        "attributter": {
            "organisationegenskaber": [
                {
                    "brugervendtnoegle": key,
                    "organisationsnavn": name,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
            "virksomhed": [
                {
                    "urn": "urn:{0}".format(cvr_number),
                    "virkning": virkning
                }
            ]
        }
    }

    url = "{0}/organisation/organisation".format(BASE_URL)
    response = requests.post(url, json=organisation_dict)

    return response


def create_interessefaellesskab(customer_number, customer_relation_name,
                                customer_type, note=""):
    virkning = create_virkning()
    interessefaellesskab_dict = {
        "note": note,
        "attributter": {
            "interessefaellesskabegenskaber": [
                {
                    "brugervendtnoegle": customer_number,
                    "interessefaellesskabsnavn": customer_relation_name,
                    "interessefaellesskabstype": customer_type,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "interessefaellesskabgyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
        }
    }

    url = "{0}/organisation/interessefaellesskab".format(BASE_URL)
    response = requests.post(url, json=interessefaellesskab_dict)

    return response


def create_organisationfunktion(customer_number,
                                customer_uuid,
                                customer_relation_uuid,
                                role, note=""):
    virkning = create_virkning()
    organisationfunktion_dict = {
        "note": note,
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "brugervendtnoegle": " ".join([role, customer_number]),
                    "funktionsnavn": role,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "organisationfunktiongyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "organisatoriskfunktionstype": [
                {
                    "urn": "urn:{0}".format(role),
                    "virkning": virkning
                }
            ],
            "tilknyttedeinteressefaellesskaber": [
                {
                    "uuid": customer_relation_uuid,
                    "virkning": virkning
                },
            ],
            "tilknyttedebrugere": [
                {
                    "uuid": customer_uuid,
                    "virkning": virkning
                },
            ]
        }
    }

    url = "{0}/organisation/organisationfunktion".format(BASE_URL)
    response = requests.post(url, json=organisationfunktion_dict)

    return response


def create_bruger(cpr_number, key, name, phone="", email="",
                  mobile="", fax="", note=""):
    virkning = create_virkning()
    bruger_dict = {
        "note": note,
        "attributter": {
            "brugeregenskaber": [
                {
                    "brugervendtnoegle": key,
                    "brugernavn": name,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "brugergyldighed": [{
                "gyldighed": "Aktiv",
                "virkning": virkning
            }]
        },
        "relationer": {
            "tilhoerer": [
                {
                    "uuid": AVA_ORGANISATION,
                    "virkning": virkning

                },
            ],
            "tilknyttedepersoner": [
                {
                    "urn": "urn:{0}".format(cpr_number),
                    "virkning": virkning
                }
            ]
        }
    }

    url = "{0}/organisation/bruger".format(BASE_URL)
    response = requests.post(url, json=bruger_dict)

    return response
