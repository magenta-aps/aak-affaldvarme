import datetime
import json
import os
from unittest.mock import ANY, MagicMock, patch

from freezegun import freeze_time

import arosia_oio


def get_test_file_path(filename):
    script_dir = os.path.dirname(__file__)
    rel_path = 'oio_output/{}'.format(filename)
    return os.path.join(script_dir, rel_path)


@freeze_time('2017-01-01')
def test_create_virkning_with_default_params():
    # Arrange
    # Act
    result = arosia_oio.create_virkning()
    # Assert
    assert result.get('from') == str(datetime.datetime.now())
    assert result.get('to') == 'infinity'


def test_create_virkning_uses_supplied_params():
    # Arrange
    frm = '2010-01-01'
    to = '2017-01-01'
    # Act
    actual_result = arosia_oio.create_virkning(frm=frm, to=to)
    # Assert
    assert actual_result.get('from') == str(frm)
    assert actual_result.get('to') == str(to)


@freeze_time('2017-01-01')
@patch('arosia_oio.AVA_ORGANISATION', new='AVA_ORGANISATION')
class TestGenerate():
    def test_generate_organisation_dict_all_args(self):
        # Arrange
        file_path = get_test_file_path('organisation.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_organisation_dict(
                'CVR', 'KEY', 'NAME', 'AROSIA_PHONE', 'AROSIA_EMAIL',
                'KMDEE_PHONE', 'KMDEE_EMAIL', 'ADDRESS_UUID', 'COMPANY_TYPE',
                'INDUSTRY_CODE', 'NOTE', 'AROSIA_ID', 'SMS_NOTIF')

            # Assert
            assert expected_result == actual_result

    def test_generate_organisation_dict_minimal_args(self):
        # Arrange
        file_path = get_test_file_path('organisation_minimal.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_organisation_dict(
                'CVR', 'KEY', 'NAME')

            # Assert
            assert expected_result == actual_result

    def test_generate_bruger_dict_all_args(self):
        # Arrange
        file_path = get_test_file_path('bruger.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            actual_result = arosia_oio.generate_bruger_dict(
                'CPR', 'KEY', 'NAME', 'AROSIA_PHONE', 'AROSIA_EMAIL',
                'KMDEE_PHONE', 'KMDEE_EMAIL', 'FIRST_NAME', 'MIDDLE_NAME',
                'LAST_NAME', 'ADDRESS_UUID', 'GENDER', 'MARITAL_STATUS',
                'ADDRESS_PROTECTION', 'NOTE', 'AROSIA_ID', 'SMS_NOTIF')

            # Assert
            assert expected_result == actual_result

    def test_generate_bruger_dict_minimal_args(self):
        # Arrange
        file_path = get_test_file_path('bruger_minimal.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_bruger_dict(
                'CPR', 'KEY', 'NAME')

            # Assert
            assert expected_result == actual_result

    def test_generate_interessefaellesskab_dict(self):
        # Arrange
        file_path = get_test_file_path('interessefaellesskab.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_interessefaellesskab_dict(
                'CUSTOMER_NUMBER', 'CUSTOMER_RELATION_NAME', 'CUSTOMER_TYPE',
                'AROSIA_ID', 'NOTE')

            # Assert
            assert expected_result == actual_result

    def test_generate_organisationfunktion_dict(self):
        # Arrange
        file_path = get_test_file_path('organisationfunktion.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_organisationfunktion_dict(
                'CUSTOMER_NUMBER', 'CUSTOMER_UUID', 'CUSTOMER_RELATION_UUID',
                'ROLE', 'NOTE')

            # Assert
            assert expected_result == actual_result

    def test_generate_indsats_dict(self):
        # Arrange
        file_path = get_test_file_path('indsats.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            start_date = datetime.datetime(2010, 1, 1)
            end_date = datetime.datetime(2017, 1, 1)

            # Act
            actual_result = arosia_oio.generate_indsats_dict(
                'NAME', 'AGREEMENT_TYPE', 'NO_OF_PRODUCTS', 'INVOICE_ADDRESS',
                start_date, end_date, 'CUSTOMER_RELATION_UUID',
                ['PRODUCT1', 'PRODUCT2'], 'NOTE')

            # Assert
            assert expected_result == actual_result

    def test_generate_klasse_dict(self):
        # Arrange
        file_path = get_test_file_path('klasse.json')
        with open(file_path, 'r') as file:
            expected_result = json.load(file)

            # Act
            actual_result = arosia_oio.generate_klasse_dict(
                'AFHENTNINGSTYPE', 'AROSIA_ID', 'IDENTIFICATION',
                'INSTALLATION_TYPE', 'METER_NUMBER', 'NAME', 'NOTE',
                'AFTALE_ID')

            # Assert
            assert expected_result == actual_result


@patch('arosia_oio.create_or_update_organisation')
@patch('arosia_oio.get_cvr_data')
def test_extract_cvr_calls_get_cvr_data(mock_get_cvr: MagicMock,
                                        mock_create: MagicMock):
    # Arrange
    id_number = 'ID_NUMBER'

    # Act
    arosia_oio.extract_cvr_and_update_lora(id_number)

    # Assert
    mock_get_cvr.assert_called_once_with(id_number)


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_organisation')
def test_create_or_update_organisation_handles_create(mock_lookup: MagicMock,
                                                      mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_organisation('CVR', 'KEY', 'NAME')

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_organisation')
def test_create_or_update_organisation_handles_update(mock_lookup: MagicMock,
                                                      mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_organisation('CVR', 'KEY', 'NAME')

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_bruger')
def test_create_or_update_bruger_handles_create(mock_lookup: MagicMock,
                                                mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_bruger('CVR', 'KEY', 'NAME')

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_bruger')
def test_create_or_update_bruger_handles_update(mock_lookup: MagicMock,
                                                mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_bruger('CPR', 'KEY', 'NAME')

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_interessefaellesskab')
def test_create_or_update_interessefaellesskab_handles_create(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_interessefaellesskab('123', '456', '789')

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_interessefaellesskab')
def test_create_or_update_interessefaellesskab_handles_update(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_interessefaellesskab('123', '456', '789')

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_organisationfunktion')
def test_create_or_update_organisationfunktion_handles_create(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_organisationfunktion('12', '34', '56', '78')

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_organisationfunktion')
def test_create_or_update_organisationfunktion_handles_update(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_organisationfunktion('12', '34', '56', '78')

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_indsats')
def test_create_or_update_indsats_handles_create(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_indsats('12', '34', '56', '78',
                                        datetime.datetime.now(),
                                        datetime.datetime.now(), '90',
                                        ['12', '34'])

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_indsats')
def test_create_or_update_indsats_handles_update(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_indsats('12', '34', '56', '78',
                                        datetime.datetime.now(),
                                        datetime.datetime.now(), '90',
                                        ['12', '34'])

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_klasse')
def test_create_or_update_klasse_handles_create(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = '6e9908df-2b6b-472b-a2de-d58d79e59c33'

    # Act
    arosia_oio.create_or_update_klasse('12', '34', '56')

    # Assert
    mock_session.put.assert_called_once_with(ANY, json=ANY)
    mock_session.post.assert_not_called()


@patch('arosia_oio.session')
@patch('arosia_oio.lookup_klasse')
def test_create_or_update_klasse_handles_update(
        mock_lookup: MagicMock,
        mock_session: MagicMock):
    # Arrange
    mock_lookup.return_value = None

    # Act
    arosia_oio.create_or_update_klasse('12', '34', '56')

    # Assert
    mock_session.post.assert_called_once_with(ANY, json=ANY)
    mock_session.put.assert_not_called()
