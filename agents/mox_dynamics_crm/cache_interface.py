# -*- coding: utf-8 -*-

import rethinkdb as r

from helper import get_config
from logging import getLogger

# Temporary mapping
mapping = {
    "bruger": "contacts",
    "organisation": "contacts",
    "dawa": "ava_adresses",
    "dawa_access": "access",
    "interessefaellesskab": "accounts",
    "indsats": "ava_aftales",
    "organisationfunktion": "ava_kunderolles",
    "klasse": "ava_installations",
}

# Init logger
log = getLogger(__name__)


def connect():
    """
    Create database connection (object).
    This is NOT a connection pool and must be closed after use.

    :return: Connection object
    """

    # Get configuration
    # config = get_config("cache_layer")

    # Changed for compatibility
    config = get_config("rethinkdb")

    if not config:
        raise Exception("Unable to connect")

    return r.connect(
        host=config["db_host"],
        port=config["db_port"],
        db=config["db_name"],
        user=config["db_user"],
        password=config["db_pass"]
    )


def insert(table, payload, conflict="error"):
    """
    Parent function to insert objects into the database
    Primarily used by wrapper functions

    TODO:   The option for 'return_changes' may be needed.
            If set to true:

            A dataset containing the previous value (if any)
            and the new value:

            {
                new_val: <new value>,
                old_val: null
            }

    :param table:       Table name (required)
    :param payload:     Document or list of documents

    :param conflict:    This will return an error if a document has
                        a conflicting 'id'.

                        By setting conflict to 'update'
                        a document is updated if it already exists.

    :return:            Returns status object
                        Example:
                        {
                            'unchanged': 0,
                            'skipped': 0,
                            'deleted': 0,
                            'generated_keys': [<uuid1>, <uuid2>...<n>]
                            'errors': 0,
                            'replaced': 0,
                            'inserted': <amount>
                        }
    """

    # Debug
    log.debug(payload)

    with connect() as connection:
        query = r.table(table).insert(payload, conflict=conflict)
        run = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        if run["errors"]:
            log.error(
                "Error inserting into {table}: {stack}".format(
                    table=table,
                    stack=run
                )
            )

        return run


def update(table, document):
    """
    Parent function to update objects
    May be redundant as the upsert (conflict=update) functionality
    is more flexible.

    Use case: when when documents should not be inserted
    if they do not exist

    :param table:       Table name (required)
    :param document:     JSON (dictionary) payload/document to be updated
    :return:            Returns status object
    """

    # Debug
    log.debug(document)

    identifier = document["id"]

    with connect() as connection:
        query = r.table(table).get(identifier)
        update = query.update(document)
        run = update.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        if run["errors"]:
            log.error(
                "Error updating {table}: {identifier}".format(
                    table=table,
                    identifier=identifier
                )
            )
            log.error(run["first_error"])

        return run


def get(table, uuid):
    """
    Parent function to retrieve a specific document by 'id'.

    :param table:  Table name (required)
    :param uuid:   The object identifier 'id' (Type: uuid)

    :return:       Returns either a document or 'None'
    """

    with connect() as connection:
        query = r.table(table).get(uuid)
        run = query.run(connection)

        # Debug
        log.debug(
            "{table}: {query}".format(
                table=table,
                query=run
            )
        )

        return run


def filter(table, **params):
    """
    Parent function to find a specific document using a filter.

    :param table:   Table name
    :param params:  Filter parameters, e.g.
                    {
                        external_ref:   <value>
                    }

    :return:        Returns a list of documents
                    If no documents are found, an empty list is returned
    """

    if not params:
        return None

    with connect() as connection:
        query = r.table(table).filter(params)
        result = query.run(connection)

        # Info
        log.info(
            "{table}: {query}".format(
                table=table,
                query=result
            )
        )

        return result


def all(table):
    """
    Parent function to retrieve all documents from a specific table.
    The underlying method returns a cursor.

    For compatibility reasons this function returns a full list of documents.

    :param table:   Table name
    :return:        A list of documents (or None), e.g.
                    [<document1>, <document2>, <document3>...]
    """

    with connect() as connection:
        query = r.table(table)
        run = query.run(connection)

        # Info
        log.info(
            "Retrieving all documents from {table}".format(
                table=table
            )
        )

        # Temporary result list
        result = []

        # Temporarily returning a full list for compatibility
        # TODO: Must be reworked
        for item in run:
            result.append(item)

        return result


def find_address(uuid):
    """
    Wrapper function to retrieve an address by 'id'

    :param uuid:    Document identifier (Type: uuid)
    :return:        Returns either document or None
    """

    return get(
        table=mapping.get("dawa"),  # Get table name from temporary map
        uuid=uuid
    )


def find_indsats(uuid):
    """
    Wrapper function to retrieve an 'indsats' document by 'id'.

    See mapping:
        LORA:   indsats
        CRM:    ava_aftales

    :param uuid:    Document identifier (Type: uuid)
    :return:        Returns either empty list or list of documents
    """
    documents = r.table("ava_aftales").get_all(
        uuid, index="interessefaellesskab_ref"
        ).run(connect())

    for d in documents:
        return d


def store(resource, payload):
    """
    Helper function to insert documents by resource name.
    This is a temporary solution to translate the entity names using the map.

    (See mapping dictionary above)

    :param resource:    LORA entity name
    :param payload:     Document or list of documents

    :return:            Returns generic insert function.
                        Conflict is set to update, which means that
                        existing documents are updated rather than duplicated.
    """

    return insert(
        table=mapping.get(resource),
        payload=payload,
        conflict="update"
    )


def find_contact(cpr_id):
    """
    CLI find --cpr:

    Use filter function to find a contact object by CPR ID.

    This is a utility function for development purposes.
    (Retrieve and display the object in the terminal)

    :param cpr_id:  CPR ID value from:

                    "data":
                        {
                            "ava_cpr_nummer": <cpr id>
                        }

    :return:        Returns list object containing
                    the filtered 'JSON' object
    """

    if not cpr_id:
        raise Exception("No CPR ID provided")

    contact = filter(
        table="contacts",
        data={
            "ava_cpr_nummer": cpr_id
        }
    )

    if not contact:
        return {
            "error": "contact not found"
        }

    return list(contact)
