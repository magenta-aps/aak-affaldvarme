import logging

from services import report_error, fetch_associated_orgs_from_lora, \
    update_organisation_in_lora, fetch_org_data_from_lora, \
    get_cvr_data_from_serviceplatform
from settings import ORG_UUID

from compare import COMPARISONS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def extract_cvr_from_org(org_data):
    registreringer = org_data['registreringer']
    relationer = registreringer[0]['relationer']
    virksomhed = relationer['virksomhed']

    # We expect there to only be one active cvr registered
    if len(virksomhed) != 1:
        return

    cvr = virksomhed[0]
    # e.g. urn:25052943
    split_urn = cvr['urn'].split(':')
    return split_urn[1]


def compare_cvr_and_lora(cvr_data, org_data):
    update_json = {}

    uuid = org_data.get('id')

    for org_extractor, cvr_extractor, add_update in COMPARISONS:
        org_field = org_extractor(org_data, uuid)
        cvr_field = cvr_extractor(cvr_data, uuid)

        if not org_field or not cvr_field:
            return

        if org_field != cvr_field:
            add_update(cvr_field, update_json)

    # Update if update_json has been populated
    if update_json:
        update_organisation_in_lora(update_json, uuid)
        logger.info("Updating {0} with {1}".format(uuid, update_json))


def fetch_and_compare():
    # Fetch all orgs associated with ORG_UUID from LoRa
    org_virksomheder = fetch_associated_orgs_from_lora(ORG_UUID)
    if not org_virksomheder:
        report_error('No organisationer found for uuid {}'.format(ORG_UUID))
        return

    # For each, fetch info from LoRa and serviceplatform and compare
    for org_data in fetch_org_data_from_lora(org_virksomheder):

        cvrnr = extract_cvr_from_org(org_data)
        if not cvrnr:
            report_error(
                "One CVR relation expected",
                error_object=org_data)
            continue

        cvr_data = get_cvr_data_from_serviceplatform(cvrnr)
        if not cvr_data:
            report_error("No CVR data found for {}".format(cvrnr))
            continue

        compare_cvr_and_lora(cvr_data, org_data)


if __name__ == "__main__":
    fetch_and_compare()
