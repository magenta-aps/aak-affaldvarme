from unittest.mock import ANY, MagicMock, patch

import arosia_import
from arosia_cache import ArosiaCache


def setup():
    arosia_import.CACHE = ArosiaCache()
    pass


@patch('arosia_import.handle_contact')
def test_import_contact_calls_handle_contact(mock_handle: MagicMock):
    # Arrange
    row = {
        'ContactId': '161cba2c-694e-4151-9b1f-5c3ed86da8e8',
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_contact(connection)

    # Assert
    mock_handle.assert_called_once_with(row)


@patch('arosia_import.handle_contact')
def test_import_contact_caches_lora_id(mock_handle: MagicMock):
    # Arrange
    contact_id = '161cba2c-694e-4151-9b1f-5c3ed86da8e8'
    row = {
        'ContactId': contact_id,
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    lora_id = 'LORA ID'

    mock_handle.return_value = lora_id

    # Act
    arosia_import.import_contact(connection)

    # Assert
    assert arosia_import.CACHE.get_contact(contact_id) is lora_id


@patch('arosia_import.handle_contact')
def test_import_contact_handles_multiple_rows(mock_handle: MagicMock):
    # Arrange
    row = {
        'ContactId': '161cba2c-694e-4151-9b1f-5c3ed86da8e8',
    }
    rows = [row, row, row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_contact(connection)

    # Assert
    assert mock_handle.call_count is 3


@patch('arosia_import.report_error')
@patch('arosia_import.handle_contact')
def test_import_contact_reports_error_on_missing_contact_id(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    row = {
        'ContactId': '',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_contact(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.report_error')
@patch('arosia_import.handle_contact')
def test_import_contact_reports_error_on_no_lora_id(mock_handle: MagicMock,
                                                    mock_report: MagicMock):
    # Arrange
    row = {
        'ContactId': '161cba2c-694e-4151-9b1f-5c3ed86da8e8',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows
    mock_handle.return_value = None

    # Act
    arosia_import.import_contact(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.handle_account')
def test_import_account_calls_handle_account(mock_handle: MagicMock):
    # Arrange
    row = {
        'AccountId': 'e9244f36-92e8-4b60-8cd6-00d163cdb067',
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_account(connection)

    # Assert
    mock_handle.assert_called_once_with(row)


@patch('arosia_import.handle_account')
def test_import_account_caches_lora_id(mock_handle: MagicMock):
    # Arrange
    account_id = 'e9244f36-92e8-4b60-8cd6-00d163cdb067'
    row = {
        'AccountId': account_id,
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    lora_id = 'LORA ID'

    mock_handle.return_value = lora_id

    # Act
    arosia_import.import_account(connection)

    # Assert
    assert arosia_import.CACHE.get_account(account_id) is lora_id


@patch('arosia_import.handle_account')
def test_import_account_handles_multiple_rows(mock_handle: MagicMock):
    # Arrange
    row = {
        'AccountId': 'e9244f36-92e8-4b60-8cd6-00d163cdb067',
    }
    rows = [row, row, row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_account(connection)

    # Assert
    assert mock_handle.call_count is 3


@patch('arosia_import.report_error')
@patch('arosia_import.handle_account')
def test_import_account_reports_error_on_missing_account_id(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    row = {
        'AccountId': '',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_account(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.report_error')
@patch('arosia_import.handle_account')
def test_import_account_reports_error_on_no_lora_id(mock_handle: MagicMock,
                                                    mock_report: MagicMock):
    # Arrange
    row = {
        'AccountId': 'e9244f36-92e8-4b60-8cd6-00d163cdb067',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows
    mock_handle.return_value = None

    # Act
    arosia_import.import_account(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.handle_kontaktrolle')
def test_import_kontaktrolle_calls_handle_kontaktrolle_correctly(
        mock_handle: MagicMock):
    # Arrange
    kontakt = '282b8bb8-cef8-4dd3-8382-233b5a07b870'
    kundeforhold = '2f110fd8-976c-417b-811d-30a92fef9636'
    row = {
        'ava_Kontakt': kontakt,
        'ava_Kundeforhold': kundeforhold,
    }
    rows = [row]

    # Populate the cache
    kontakt_lora = '1d04e1f0-fe59-4613-b59e-27432dd621b4'
    kundeforhold_lora = '5ad648ec-7662-4b6a-8e78-90265f973f6b'
    arosia_import.CACHE.add_contact(kontakt, kontakt_lora)
    arosia_import.CACHE.add_account(kundeforhold, kundeforhold_lora)

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_kontaktrolle(connection)

    # Assert
    mock_handle.assert_called_once_with(row, kontakt_lora, kundeforhold_lora)


@patch('arosia_import.handle_kontaktrolle')
def test_import_kontaktrolle_handles_multiple_rows(mock_handle: MagicMock):
    # Arrange
    kontakt = '282b8bb8-cef8-4dd3-8382-233b5a07b870'
    kundeforhold = '2f110fd8-976c-417b-811d-30a92fef9636'
    row = {
        'ava_Kontakt': kontakt,
        'ava_Kundeforhold': kundeforhold,
    }
    rows = [row, row, row]

    # Populate the cache
    kontakt_lora = '1d04e1f0-fe59-4613-b59e-27432dd621b4'
    kundeforhold_lora = '5ad648ec-7662-4b6a-8e78-90265f973f6b'
    arosia_import.CACHE.add_contact(kontakt, kontakt_lora)
    arosia_import.CACHE.add_account(kundeforhold, kundeforhold_lora)

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_kontaktrolle(connection)

    # Assert
    assert mock_handle.call_count is 3


@patch('arosia_import.report_error')
@patch('arosia_import.handle_kontaktrolle')
def test_import_kontaktrolle_reports_error_on_missing_contact_cache(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    kontakt = '282b8bb8-cef8-4dd3-8382-233b5a07b870'
    kundeforhold = '2f110fd8-976c-417b-811d-30a92fef9636'
    row = {
        'ava_Kontakt': kontakt,
        'ava_Kundeforhold': kundeforhold,
    }
    rows = [row]

    # Populate the cache
    kundeforhold_lora = '5ad648ec-7662-4b6a-8e78-90265f973f6b'
    arosia_import.CACHE.add_account(kundeforhold, kundeforhold_lora)

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_kontaktrolle(connection)

    # Assert
    mock_report.assert_called_once_with(ANY)


@patch('arosia_import.report_error')
@patch('arosia_import.handle_kontaktrolle')
def test_import_kontaktrolle_reports_error_on_missing_account_cache(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    kontakt = '282b8bb8-cef8-4dd3-8382-233b5a07b870'
    kundeforhold = '2f110fd8-976c-417b-811d-30a92fef9636'
    row = {
        'ava_Kontakt': kontakt,
        'ava_Kundeforhold': kundeforhold,
    }
    rows = [row]

    # Populate the cache
    kontakt_lora = '1d04e1f0-fe59-4613-b59e-27432dd621b4'
    arosia_import.CACHE.add_contact(kontakt, kontakt_lora)

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_kontaktrolle(connection)

    # Assert
    mock_report.assert_called_once_with(ANY)


@patch('arosia_import.report_error')
@patch('arosia_import.handle_kontaktrolle')
def test_import_kontaktrolle_reports_error_on_no_lora_id(mock_handle: MagicMock,
                                                         mock_report: MagicMock):
    # Arrange
    kontakt = '282b8bb8-cef8-4dd3-8382-233b5a07b870'
    kundeforhold = '2f110fd8-976c-417b-811d-30a92fef9636'
    row = {
        'ava_Kontakt': kontakt,
        'ava_Kundeforhold': kundeforhold,
    }
    rows = [row]

    # Populate the cache
    kontakt_lora = '1d04e1f0-fe59-4613-b59e-27432dd621b4'
    kundeforhold_lora = '5ad648ec-7662-4b6a-8e78-90265f973f6b'
    arosia_import.CACHE.add_contact(kontakt, kontakt_lora)
    arosia_import.CACHE.add_account(kundeforhold, kundeforhold_lora)

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows
    mock_handle.return_value = None

    # Act
    arosia_import.import_kontaktrolle(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.handle_placeretmateriel')
def test_import_placeretmateriel_calls_handle_placeretmateriel(
        mock_handle: MagicMock):
    # Arrange
    row = {
        'ava_Kundeaftale': '364726df-efff-4e09-bbdf-284c7866cef2',
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_placeretmateriel(connection)

    # Assert
    mock_handle.assert_called_once_with(row)


@patch('arosia_import.handle_placeretmateriel')
def test_import_placeretmateriel_caches_lora_id(mock_handle: MagicMock):
    # Arrange
    kundeaftale_id = 'e9244f36-92e8-4b60-8cd6-00d163cdb067'
    row = {
        'ava_Kundeaftale': kundeaftale_id,
    }
    rows = [row]
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    lora_id = 'LORA ID'

    mock_handle.return_value = lora_id

    # Act
    arosia_import.import_placeretmateriel(connection)

    # Assert
    assert len(arosia_import.CACHE.get_products(kundeaftale_id)) is 1
    assert lora_id in arosia_import.CACHE.get_products(kundeaftale_id)


@patch('arosia_import.handle_placeretmateriel')
def test_import_placeretmateriel_handles_multiple_rows(mock_handle: MagicMock):
    # Arrange
    row = {
        'ava_Kundeaftale': '364726df-efff-4e09-bbdf-284c7866cef2',
    }
    rows = [row, row, row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_placeretmateriel(connection)

    # Assert
    assert mock_handle.call_count is 3


@patch('arosia_import.report_error')
@patch('arosia_import.handle_placeretmateriel')
def test_import_placeretmateriel_reports_error_on_missing_kundeaftale_id(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    row = {
        'ava_Kundeaftale': '',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows

    # Act
    arosia_import.import_placeretmateriel(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)


@patch('arosia_import.report_error')
@patch('arosia_import.handle_placeretmateriel')
def test_import_placeretmateriel_reports_error_on_no_lora_id(
        mock_handle: MagicMock,
        mock_report: MagicMock):
    # Arrange
    row = {
        'ava_Kundeaftale': '364726df-efff-4e09-bbdf-284c7866cef2',
    }
    rows = [row]

    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = rows
    mock_handle.return_value = None

    # Act
    arosia_import.import_placeretmateriel(connection)

    # Assert
    mock_report.assert_called_once_with(ANY, error_object=row)
