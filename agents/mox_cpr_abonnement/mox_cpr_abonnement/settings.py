import os
import pathlib
import configparser

inipaths = [p for p in [
        pathlib.Path(os.environ.get("MOX_CPR_ABONNEMENT_CONFIG", "")),
        pathlib.Path("") / "settings.ini",
        pathlib.Path(__file__).absolute() / "settings.ini",
    ] if p.is_file()
]

if not len(inipaths):
    inifile = ""
else:
    inifile = inipaths[0]

config = configparser.ConfigParser(defaults={
    "MOX_LOG_LEVEL": "10",
    "MOX_LOG_FILE": "",  # "" sends log to console
    "ADD_PNR_SUBSCRIPTION": "AddPNRSubscription",
    "REMOVE_PNR_SUBSCRIPTION": "RemovePNRSubscription",
    "GET_PNR_SUBSCRIPTIONS": "GetAllFilters",
    "SP_ABO_SERVICE_ENDPOINT": "N/A",
    "SP_ABO_CERTIFICATE": "N/A",
    "SP_ABO_SOAP_REQUEST_ENVELOPE": "N/A",
    "SP_ABO_SYSTEM": "N/A",
    "SP_ABO_USER": "N/A",
    "SP_ABO_SERVICE_AGREEMENT": "N/A",
    "SP_ABO_SERVICE": "N/A",
    "LORA_HTTP_BASE": "N/A",
    "LORA_ORG_UUID": "N/A",
    "LORA_CA_BUNDLE": "",
})
config["settings"] = {}

if inifile:
    config.read(str(inifile))

settings = config["settings"]


MOX_LOG_LEVEL = int(settings["MOX_LOG_LEVEL"])
MOX_LOG_FILE = settings["MOX_LOG_FILE"]
SP_ABO_SERVICE_ENDPOINT = settings["SP_ABO_SERVICE_ENDPOINT"]
SP_ABO_CERTIFICATE = settings["SP_ABO_CERTIFICATE"]
SP_ABO_SOAP_REQUEST_ENVELOPE = settings["SP_ABO_SOAP_REQUEST_ENVELOPE"]
SP_ABO_SYSTEM = settings["SP_ABO_SYSTEM"]
SP_ABO_USER = settings["SP_ABO_USER"]
SP_ABO_SERVICE_AGREEMENT = settings["SP_ABO_SERVICE_AGREEMENT"]
SP_ABO_SERVICE = settings["SP_ABO_SERVICE"]
ADD_PNR_SUBSCRIPTION = settings["ADD_PNR_SUBSCRIPTION"]
REMOVE_PNR_SUBSCRIPTION = settings["REMOVE_PNR_SUBSCRIPTION"]
GET_PNR_SUBSCRIPTIONS = settings["GET_PNR_SUBSCRIPTIONS"]
LORA_HTTP_BASE = settings["LORA_HTTP_BASE"]
LORA_ORG_UUID = settings["LORA_ORG_UUID"]
LORA_CA_BUNDLE = settings["LORA_CA_BUNDLE"]

if LORA_CA_BUNDLE:
    if LORA_CA_BUNDLE.lower() in ["1", "true", "yes", "on"]:
        LORA_CA_BUNDLE = True
    elif LORA_CA_BUNDLE.lower() in ["0", "false", "no", "off"]:
        LORA_CA_BUNDLE = False
