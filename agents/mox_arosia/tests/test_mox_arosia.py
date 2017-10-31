from unittest.mock import MagicMock, patch

import mox_arosia


@patch('mox_arosia.extract_cpr_and_update_lora')
def test_handle_cpr_extracts_parameters_as_expected(mock_extract: MagicMock):
    # Arrange
    cpr = 'CPR'
    contact_id = 'Contact'

    row = {
        'ava_CPRnummer': cpr,
        'ContactId': contact_id,
    }
    phone = 'Phone'
    email = 'Email'
    sms_notif = 'SMSNotif'

    # Act
    mox_arosia.handle_cpr(row, phone, email, sms_notif)

    # Assert
    mock_extract.assert_called_once_with(cpr,
                                         phone=phone,
                                         email=email,
                                         arosia_id=contact_id,
                                         sms_notif=sms_notif)


@patch('mox_arosia.extract_cpr_and_update_lora')
def test_handle_cpr_returns_lora_uuid_if_response(mock_extract: MagicMock):
    # Arrange
    row = {
        'ava_CPRnummer': "",
        'ContactId': "",
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_extract.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_cpr(row, "", "", "")

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.extract_cpr_and_update_lora')
def test_handle_cpr_returns_none_if_no_response(mock_extract: MagicMock):
    # Arrange
    row = {
        'ava_CPRnummer': "",
        'ContactId': "",
    }

    mock_extract.return_value = None

    # Act
    actual_result = mox_arosia.handle_cpr(row, "", "", "")

    # Assert
    assert actual_result is None


@patch('mox_arosia.extract_cvr_and_update_lora')
def test_handle_cvr_extracts_parameters_as_expected(mock_extract: MagicMock):
    # Arrange
    cvr = 'CVR'
    contact_id = 'Contact'

    row = {
        'ava_CVRnummer': cvr,
        'ContactId': contact_id,
    }
    phone = 'Phone'
    email = 'Email'
    sms_notif = 'SMSNotif'

    # Act
    mox_arosia.handle_cvr(row, phone, email, sms_notif)

    # Assert
    mock_extract.assert_called_once_with(cvr,
                                         phone=phone,
                                         email=email,
                                         arosia_id=contact_id,
                                         sms_notif=sms_notif)


@patch('mox_arosia.extract_cvr_and_update_lora')
def test_handle_cvr_returns_lora_uuid_if_response(mock_extract: MagicMock):
    # Arrange
    row = {
        'ava_CVRnummer': "",
        'ContactId': "",
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_extract.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_cvr(row, "", "", "")

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.extract_cvr_and_update_lora')
def test_handle_cvr_returns_none_if_no_response(mock_extract: MagicMock):
    # Arrange
    row = {
        'ava_CVRnummer': "",
        'ContactId': "",
    }

    mock_extract.return_value = None

    # Act
    actual_result = mox_arosia.handle_cvr(row, "", "", "")

    # Assert
    assert actual_result is None


@patch('mox_arosia.handle_cpr')
@patch('mox_arosia.handle_cvr')
def test_handle_contact_calls_handle_cpr_if_cpr(mock_cvr: MagicMock,
                                                mock_cpr: MagicMock):
    # Arrange
    smsnotif = 'smsnotif'
    phone = '12345'
    email = 'EMail'
    row = {
        'ava_CPRnummer': 'CPR',
        'ava_CVRnummer': '',
        'EMailAddress1': email,
        'ava_sms_notifikation': smsnotif,
        'MobilePhone': phone,
        'Telephone1': phone,
        'ContactId': '1337',
    }

    expected_result = mock_cpr.return_value

    # Act
    actual_result = mox_arosia.handle_contact(row)

    # Assert
    assert expected_result is actual_result
    mock_cpr.assert_called_with(row, phone, email, smsnotif)
    mock_cvr.assert_not_called()


@patch('mox_arosia.handle_cpr')
@patch('mox_arosia.handle_cvr')
def test_handle_contact_calls_handle_cvr_if_cvr(mock_cvr: MagicMock,
                                                mock_cpr: MagicMock):
    # Arrange
    smsnotif = 'smsnotif'
    phone = '12345'
    email = 'EMail'
    row = {
        'ava_CPRnummer': '',
        'ava_CVRnummer': 'CVR',
        'EMailAddress1': email,
        'ava_sms_notifikation': smsnotif,
        'MobilePhone': phone,
        'Telephone1': phone,
        'ContactId': '1337',
    }

    expected_result = mock_cvr.return_value

    # Act
    actual_result = mox_arosia.handle_contact(row)

    # Assert
    assert expected_result is actual_result
    mock_cvr.assert_called_with(row, phone, email, smsnotif)
    mock_cpr.assert_not_called()


@patch('mox_arosia.handle_cpr')
@patch('mox_arosia.handle_cvr')
def test_handle_contact_returns_none_if_no_cpr_or_cvr(mock_cvr: MagicMock,
                                                      mock_cpr: MagicMock):
    # Arrange
    smsnotif = 'smsnotif'
    phone = '12345'
    email = 'EMail'
    row = {
        'ava_CPRnummer': '',
        'ava_CVRnummer': '',
        'EMailAddress1': email,
        'ava_sms_notifikation': smsnotif,
        'MobilePhone': phone,
        'Telephone1': phone,
        'ContactId': '1337',
    }

    # Act
    result = mox_arosia.handle_contact(row)

    # Assert
    assert result is None
    mock_cvr.assert_not_called()
    mock_cpr.assert_not_called()


@patch('mox_arosia.handle_cpr')
@patch('mox_arosia.handle_cvr')
def test_handle_contact_uses_mobile_phone_if_available(mock_cvr: MagicMock,
                                                       mock_cpr: MagicMock):
    # Arrange
    smsnotif = 'smsnotif'
    phone = '12345'
    email = 'EMail'
    row = {
        'ava_CPRnummer': 'CPR',
        'ava_CVRnummer': '',
        'EMailAddress1': email,
        'ava_sms_notifikation': smsnotif,
        'MobilePhone': phone,
        'Telephone1': '',
        'ContactId': '1337',
    }

    # Act
    mox_arosia.handle_contact(row)

    # Assert
    mock_cpr.assert_called_with(row, phone, email, smsnotif)
    mock_cvr.assert_not_called()


@patch('mox_arosia.handle_cpr')
@patch('mox_arosia.handle_cvr')
def test_handle_contact_uses_telephone_if_available(mock_cvr: MagicMock,
                                                    mock_cpr: MagicMock):
    # Arrange
    smsnotif = 'smsnotif'
    phone = '12345'
    email = 'EMail'
    row = {
        'ava_CPRnummer': 'CPR',
        'ava_CVRnummer': '',
        'EMailAddress1': email,
        'ava_sms_notifikation': smsnotif,
        'MobilePhone': '',
        'Telephone1': phone,
        'ContactId': '1337',
    }

    # Act
    mox_arosia.handle_contact(row)

    # Assert
    mock_cpr.assert_called_with(row, phone, email, smsnotif)
    mock_cvr.assert_not_called()


@patch('mox_arosia.create_or_update_interessefaellesskab')
def test_handle_account_extracts_parameters_as_expected(mock_create: MagicMock):
    # Arrange
    account_number = 'AccountNumber'
    name = 'Name'
    account_id = 'AccountId'

    customer_type = 'Affald'

    row = {
        'AccountNumber': account_number,
        'Name': name,
        'AccountId': account_id,
    }

    # Act
    mox_arosia.handle_account(row)

    # Assert
    mock_create.assert_called_once_with(customer_number=account_number,
                                        customer_relation_name=name,
                                        customer_type=customer_type,
                                        arosia_id=account_id)


@patch('mox_arosia.create_or_update_interessefaellesskab')
def test_handle_account_returns_lora_uuid_if_response(mock_create: MagicMock):
    # Arrange
    row = {
        'AccountNumber': "",
        'Name': "",
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_create.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_account(row)

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.create_or_update_interessefaellesskab')
def test_handle_account_returns_none_if_no_response(mock_create: MagicMock):
    # Arrange
    row = {
        'AccountNumber': "",
        'Name': "",
    }

    mock_create.return_value = None

    # Act
    actual_result = mox_arosia.handle_account(row)

    # Assert
    assert actual_result is None


@patch('mox_arosia.create_or_update_organisationfunktion')
def test_handle_kontaktrolle_extracts_parameters_as_expected(
        mock_create: MagicMock):
    # Arrange
    name = 'Name'
    role = 'Role'

    row = {
        'ava_KontaktName': name,
        'ava_Rolle': role,
    }

    contact = "5335d80e-5726-4beb-8c48-f7758d2ee876"
    account = "b4a47942-b5c3-48d7-8733-6d51fe2b1b91"

    # Act
    mox_arosia.handle_kontaktrolle(row, contact, account)

    # Assert
    mock_create.assert_called_once_with(customer_number=name,
                                        customer_uuid=contact,
                                        customer_relation_uuid=account,
                                        role=role)


@patch('mox_arosia.create_or_update_organisationfunktion')
def test_handle_kontaktrolle_returns_lora_uuid_if_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_KontaktName': '',
        'ava_Rolle': '',
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_create.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_kontaktrolle(row, "", "")

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.create_or_update_organisationfunktion')
def test_handle_kontaktrolle_returns_none_if_no_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_KontaktName': '',
        'ava_Rolle': '',
    }

    mock_create.return_value = None

    # Act
    actual_result = mox_arosia.handle_kontaktrolle(row, "", "")

    # Assert
    assert actual_result is None


@patch('mox_arosia.create_or_update_klasse')
def test_handle_placeretmateriel_extracts_parameters_as_expected(
        mock_create: MagicMock):
    # Arrange
    name = 'Name'
    stregkode = 'Stregkode'
    affaldstype = 'Affaldstype'
    placeretmateriel_id = 'ID'
    aftale_id = 'AftaleId'

    row = {
        'ava_navn': name,
        'ava_stregkode': stregkode,
        'ava_affaldstypeName': affaldstype,
        'ava_placeretmaterielId': placeretmateriel_id,
        'ava_Kundeaftale': aftale_id
    }

    installation_type = 'Affald'

    # Act
    mox_arosia.handle_placeretmateriel(row)

    # Assert
    mock_create.assert_called_once_with(name=name,
                                        identification=stregkode,
                                        installation_type=installation_type,
                                        arosia_id=placeretmateriel_id,
                                        afhentningstype=affaldstype,
                                        aftale_id=aftale_id)


@patch('mox_arosia.create_or_update_klasse')
def test_handle_placeretmateriel_returns_lora_uuid_if_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_navn': '',
        'ava_stregkode': '',
        'ava_affaldstypeName': '',
        'ava_placeretmaterielId': ''
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_create.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_placeretmateriel(row)

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.create_or_update_klasse')
def test_handle_placeretmateriel_returns_none_if_no_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_KontaktName': '',
        'ava_Rolle': '',
    }

    mock_create.return_value = None

    # Act
    actual_result = mox_arosia.handle_placeretmateriel(row)

    # Assert
    assert actual_result is None


@patch('mox_arosia.create_or_update_indsats')
def test_handle_kundeaftale_extracts_parameters_as_expected(
        mock_create: MagicMock):
    # Arrange
    name = "Name"
    start_date = "Startdate"
    end_date = "Enddate"

    row = {
        'ava_navn': name,
        'ava_Startdato': start_date,
        'ava_Slutdato': end_date,
    }

    agreement_type = "Affald"
    cr_uuid = "3ca80a43-6a91-40b1-8cca-48f853c2c768"
    products = ['product1', 'product2']

    # Act
    mox_arosia.handle_kundeaftale(row, cr_uuid, products)

    # Assert
    mock_create.assert_called_once_with(name=name,
                                        agreement_type=agreement_type,
                                        no_of_products=len(products),
                                        start_date=start_date,
                                        end_date=end_date,
                                        customer_relation_uuid=cr_uuid,
                                        product_uuids=products)


@patch('mox_arosia.create_or_update_indsats')
def test_handle_kundeaftale_returns_lora_uuid_if_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_navn': '',
        'ava_Startdato': '',
        'ava_Slutdato': '',
    }

    uuid = '904ca40e-85b2-4140-b186-0556efc84cad'

    mock_response = mock_create.return_value
    mock_response.json.return_value = {'uuid': uuid}

    # Act
    actual_result = mox_arosia.handle_kundeaftale(row, '', [])

    # Assert
    assert uuid == actual_result


@patch('mox_arosia.create_or_update_indsats')
def test_handle_kundeaftale_returns_none_if_no_response(
        mock_create: MagicMock):
    # Arrange
    row = {
        'ava_navn': '',
        'ava_Startdato': '',
        'ava_Slutdato': '',
    }

    mock_create.return_value = None

    # Act
    actual_result = mox_arosia.handle_kundeaftale(row, '', [])

    # Assert
    assert actual_result is None
