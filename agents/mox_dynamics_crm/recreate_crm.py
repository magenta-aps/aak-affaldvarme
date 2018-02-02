# -*- coding: utf-8 -*-

from helper import get_config
from crm_interface import get_request
from crm_interface import delete_request


###################################
#                                 #
# IMPORTANT NOTE:                 #
#                                 #
# THIS IS A UTILITY TOOL          #
# FOR DEVELOPMENT PURPOSES ONLY   #
#                                 #
# PLEASE DO NOT USE IN PRODUCTION #
#                                 #
###################################


# Get config
config = get_config("ms_dynamics_crm")

# Configuration
CRM_OWNER_ID = config["crm_owner_id"]


def retrieve_all_object_guids(identifier, resource):
    """
    Retrieve all CRM object identifiers.

    :param identifier:  Name of the identifier,
                        Examples:
                            Identifier for contacts is contactid
                            Identifier for ava_adresses is ava_adresseid

    :param resource:    Name of the API resource, e.g. contacts
                        {REST_API}/<resource>

    :return:            Returns list of CRM GUID's or None
    """

    # Query parameters
    params = {
        "$select": identifier,
        "$filter": "_ownerid_value eq {0}".format(CRM_OWNER_ID)
    }

    # Call underlying GET request
    query = get_request(resource, **params)

    # Results
    list_of_contacts = query.json()["value"]

    if not list_of_contacts:
        print("Contact does not exist in CRM")
        return False

    # If object exists return identifier
    return list_of_contacts


def delete_all(identifier, resource):
    """
    Utility function to remove all CRM objects
    created by the LORA integration user.

    FOR DEVELOPMENT PURPOSES ONLY!

    :param identifier:  Name of the identifier,
                        Examples:
                            Identifier for contacts is contactid
                            Identifier for ava_adresses is ava_adresseid

    :param resource:    Name of the API resource, e.g. contacts
                        {REST_API}/<resource>

    :return:            Nothing is returned,
                        Activity is printed in the terminal.
    """

    entities = retrieve_all_object_guids(
        identifier=identifier,
        resource=resource
    )

    if not entities:
        print("No {0} returned".format(resource))
        return

    for entity in entities:
        guid = entity[identifier]

        response = delete_request(resource, guid)

        if not response.status_code == 204:
            print("NOT 204")
            print(response.text)

        print(
            "Deleting: {entity}: {id} ({status})".format(
                entity=resource,
                id=guid,
                status=response.status_code
            )
        )


if __name__ == "__main__":

    # Delete all entities
    delete_all("contactid", "contacts")
    delete_all("ava_adresseid", "ava_adresses")
    delete_all("ava_aftaleid", "ava_aftales")
    delete_all("ava_kunderolleid", "ava_kunderolles")
    delete_all("accountid", "accounts")
    delete_all("ava_installationid", "ava_installations")
