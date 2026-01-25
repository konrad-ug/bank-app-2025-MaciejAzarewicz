import pytest
from unittest.mock import Mock, patch, MagicMock
from src.account import Account


class TestSendHistoryViaEmail:
    def test_personal_account_sends_history_successfully(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        account.withdraw(1)
        account.deposit(500)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("jan.kowalski@example.com")
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "Account Transfer History" in call_args[0][0]
        assert "Personal account history: [100.0, -1.0, 500.0]" in call_args[0][1]
        assert call_args[0][2] == "jan.kowalski@example.com"

    def test_company_account_sends_history_successfully(self, mocker):
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY",
                    "nip": "8461627563",
                    "statusVat": "Czynny"
                }
            }
        }
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        account = Account(company_name="TEST COMPANY", nip="8461627563")
        account.deposit(5000)
        account.send_transfer(1000)
        account.receive_transfer(500)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("firma@example.com")
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "Account Transfer History" in call_args[0][0]
        assert "Company account history: [5000.0, -1000.0, 500.0]" in call_args[0][1]
        assert call_args[0][2] == "firma@example.com"

    def test_send_history_returns_false_on_failure(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = False
        result = account.send_history_via_email("test@example.com")
        assert result is False
        mock_send.assert_called_once()

    def test_send_history_uses_correct_date_format(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        account.send_history_via_email("test@example.com")
        call_args = mock_send.call_args
        subject = call_args[0][0]
        import re
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        assert re.search(date_pattern, subject)
        assert subject.startswith("Account Transfer History ")

    def test_send_history_with_empty_history(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("test@example.com")
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "[]" in call_args[0][1]

    def test_send_history_with_negative_balance(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(60)
        account.send_express_transfer(55)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("test@example.com")
        assert result is True
        call_args = mock_send.call_args
        text = call_args[0][1]
        assert "60" in text
        assert "-55" in text
        assert "-1" in text

    def test_send_history_personal_account_format(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        account.send_history_via_email("test@example.com")
        call_args = mock_send.call_args
        text = call_args[0][1]
        assert text.startswith("Personal account history:")

    def test_send_history_company_account_format(self, mocker):
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY",
                    "nip": "8461627563",
                    "statusVat": "Czynny"
                }
            }
        }
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        account = Account(company_name="TEST COMPANY", nip="8461627563")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        account.send_history_via_email("test@example.com")
        call_args = mock_send.call_args
        text = call_args[0][1]
        assert text.startswith("Company account history:")

    def test_send_history_email_address_is_passed_correctly(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        test_emails = [
            "test@example.com",
            "user.name@domain.org",
            "admin@company.co.uk"
        ]
        for email in test_emails:
            result = account.send_history_via_email(email)
            assert result is True
            call_args = mock_send.call_args
            assert call_args[0][2] == email

    def test_send_history_creates_new_smtp_client_each_time(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_smtp_class = mocker.patch('src.account.SMTPClient')
        mock_instance = MagicMock()
        mock_smtp_class.return_value = mock_instance
        mock_instance.send.return_value = True
        account.send_history_via_email("test1@example.com")
        account.send_history_via_email("test2@example.com")
        assert mock_smtp_class.call_count == 2

    def test_send_history_with_express_transfer_fees(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        account.send_express_transfer(50)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("test@example.com")
        assert result is True
        call_args = mock_send.call_args
        assert "100" in call_args[0][1]
        assert "-50" in call_args[0][1]
        assert "-1" in call_args[0][1]

    def test_send_history_loan_included_in_history(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        account.deposit(100)
        account.deposit(100)
        result = account.submit_for_loan(50)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("test@example.com")
        assert result is True
        call_args = mock_send.call_args
        assert "50" in call_args[0][1]


class TestSMTPClientIntegration:
    def test_email_contains_all_required_parameters(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        account.send_history_via_email("recipient@example.com")
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert len(call_args[0]) == 3
        assert isinstance(call_args[0][0], str)
        assert isinstance(call_args[0][1], str)
        assert isinstance(call_args[0][2], str)

    def test_exception_in_smtp_client_returns_false(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(100)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.side_effect = Exception("SMTP connection failed")
        result = account.send_history_via_email("test@example.com")
        assert result is False


class TestSendHistoryEdgeCases:
    def test_send_history_with_special_characters_in_history(self, mocker):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(99.99)
        account.withdraw(25.50)
        account.deposit(1000.00)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("test@example.com")
        assert result is True
        call_args = mock_send.call_args
        text = call_args[0][1]
        assert "99.99" in text
        assert "-25.5" in text or "-25.50" in text
        assert "1000" in text

    def test_send_history_company_without_loan_history(self, mocker):
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY",
                    "nip": "8461627563",
                    "statusVat": "Czynny"
                }
            }
        }
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        account = Account(company_name="TEST COMPANY", nip="8461627563")
        account.deposit(50000)
        account.send_transfer(1775)
        account.receive_transfer(2000)
        mock_send = mocker.patch('src.account.SMTPClient.send')
        mock_send.return_value = True
        result = account.send_history_via_email("accounting@company.com")
        assert result is True
        call_args = mock_send.call_args
        text = call_args[0][1]
        assert "50000" in text
        assert "-1775" in text
        assert "2000" in text