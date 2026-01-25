import pytest
import requests
from src.account import Account, InsufficientFunds


class TestNIPValidation:

    def test_nip_validation_active_company(self, mocker):
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY SP. Z O.O.",
                    "nip": "8461627563",
                    "statusVat": "Czynny"
                }
            }
        }
        
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        account = Account(company_name="TEST COMPANY SP. Z O.O.", nip="8461627563")
        
        assert account.company_name == "TEST COMPANY SP. Z O.O."
        assert account.nip == "8461627563"
        
        mock_get.assert_called_once()
        
    def test_nip_validation_inactive_company(self, mocker):
        mock_response = {
            "result": {
                "subject": None
            }
        }
        
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        with pytest.raises(ValueError, match="Firma nie zarejestrowana!!"):
            Account(company_name="TEST COMPANY", nip="1234567890")
            
        mock_get.assert_called_once()
        
    def test_nip_validation_inactive_vat_status(self, mocker):
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY",
                    "nip": "1234567890",
                    "statusVat": "Wykreślony"
                }
            }
        }
        
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        account = Account(company_name="TEST COMPANY", nip="1234567890")
        
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "1234567890"
        
    def test_nip_validation_network_error(self, mocker):
        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        account = Account(company_name="TEST COMPANY", nip="1234567890")
        
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "1234567890"
        
    def test_nip_validation_invalid_length(self, mocker):
        mock_get = mocker.patch('requests.get')
        
        account = Account(company_name="TEST COMPANY", nip="123456789")
        
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"
        mock_get.assert_not_called()
        
    def test_nip_validation_nondigit_nip(self, mocker):
        mock_get = mocker.patch('requests.get')
        
        account = Account(company_name="TEST COMPANY", nip="123456789A")
        
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"
        mock_get.assert_not_called()
        
    def test_personal_account_no_nip_validation(self, mocker):
        mock_get = mocker.patch('requests.get')
        
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        
        assert account.first_name == "Jan"
        assert account.last_name == "Kowalski"
        assert account.company_name is None
        mock_get.assert_not_called()
        
    def test_company_account_without_nip(self, mocker):
        mock_get = mocker.patch('requests.get')
        
        account = Account(company_name="TEST COMPANY")
        
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"
        mock_get.assert_not_called()
        
    def test_api_url_from_environment(self, mocker):
        import os
        from unittest.mock import patch
        
        test_url = "https://custom-api.mf.gov.pl/"
        
        with patch.dict(os.environ, {'BANK_APP_MF_URL': test_url}):
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
            
            expected_url = f"{test_url}api/search/nip/8461627563?date="
            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            assert called_url.startswith(expected_url)


class TestAccountOperationsWithNIP:

    def test_business_account_deposit_with_valid_nip(self, mocker):
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
        account.deposit(1000)
        
        assert account.balance == 1000.0
        assert account.history == [1000.0]
        
    def test_business_account_loan_requirements(self, mocker):
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
        
        assert account.submit_for_loan(1000) is False


@pytest.fixture
def personal_account():
    return Account("A", "B", "05240811968", "")

@pytest.fixture  
def business_account_valid_nip(mocker):
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
    
    return Account(company_name="TEST COMPANY", nip="8461627563")

@pytest.fixture
def business_account_invalid_nip(mocker):
    mock_response = {
        "result": {
            "subject": None
        }
    }
    
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status.return_value = None
    
    return None
