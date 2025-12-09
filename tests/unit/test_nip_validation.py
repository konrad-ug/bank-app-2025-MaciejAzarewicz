import pytest
import requests
from src.account import Account, InsufficientFunds


class TestNIPValidation:
    """Testy dla walidacji NIPu z Ministry of Finance API"""
    
    def test_nip_validation_active_company(self, mocker):
        """Test walidacji aktywnego NIPu - powinien przejść"""
        # Mock odpowiedzi API dla aktywnego NIPu
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY SP. Z O.O.",
                    "nip": "8461627563",
                    "statusVat": "Czynny"
                }
            }
        }
        
        # Mock requests.get
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        # Tworzenie konta z prawidłowym NIPem
        account = Account(company_name="TEST COMPANY SP. Z O.O.", nip="8461627563")
        
        # Konto powinno zostać utworzone pomyślnie
        assert account.company_name == "TEST COMPANY SP. Z O.O."
        assert account.nip == "8461627563"
        
        # Sprawdzenie czy API zostało wywołane
        mock_get.assert_called_once()
        
    def test_nip_validation_inactive_company(self, mocker):
        """Test walidacji nieaktywnego NIPu - powinien rzucić błąd"""
        # Mock odpowiedzi API dla nieaktywnego NIPu
        mock_response = {
            "result": {
                "subject": None
            }
        }
        
        # Mock requests.get
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        # Próba utworzenia konta z nieprawidłowym NIPem
        with pytest.raises(ValueError, match="Company not registered!!"):
            Account(company_name="TEST COMPANY", nip="1234567890")
            
        # Sprawdzenie czy API zostało wywołane
        mock_get.assert_called_once()
        
    def test_nip_validation_inactive_vat_status(self, mocker):
        """Test walidacji NIPu z nieaktywnym statusem VAT"""
        # Mock odpowiedzi API dla NIPu z nieaktywnym VAT
        mock_response = {
            "result": {
                "subject": {
                    "name": "TEST COMPANY",
                    "nip": "1234567890",
                    "statusVat": "Wykreślony"
                }
            }
        }
        
        # Mock requests.get
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status.return_value = None
        
        # Tworzenie konta z NIPem o nieaktywnym VAT
        account = Account(company_name="TEST COMPANY", nip="1234567890")
        
        # Konto powinno zostać utworzone (VAT nieaktywny ale NIP istnieje)
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "1234567890"
        
    def test_nip_validation_network_error(self, mocker):
        """Test walidacji przy błędzie sieci - konto powinno zostać utworzone"""
        # Mock błędu sieci
        mock_get = mocker.patch('requests.get')
        mock_get.side_effect = requests.ConnectionError("Network error")
        
        # Tworzenie konta przy błędzie sieci
        account = Account(company_name="TEST COMPANY", nip="1234567890")
        
        # Konto powinno zostać utworzone pomimo błędu sieci
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "1234567890"
        
    def test_nip_validation_invalid_length(self, mocker):
        """Test NIPu o nieprawidłowej długości - nie powinien wywoływać API"""
        # Mock requests.get żeby sprawdzić czy nie zostanie wywołany
        mock_get = mocker.patch('requests.get')
        
        # Tworzenie konta z nieprawidłowym NIPem (9 cyfr zamiast 10)
        account = Account(company_name="TEST COMPANY", nip="123456789")
        
        # Konto powinno zostać utworzone, ale API nie powinno być wywołane
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"  # Nieprawidłowy NIP nie jest zapisywany
        mock_get.assert_not_called()
        
    def test_nip_validation_nondigit_nip(self, mocker):
        """Test NIPu zawierającego litery"""
        # Mock requests.get żeby sprawdzić czy nie zostanie wywołany
        mock_get = mocker.patch('requests.get')
        
        # Tworzenie konta z NIPem zawierającym litery
        account = Account(company_name="TEST COMPANY", nip="123456789A")
        
        # Konto powinno zostać utworzone, ale API nie powinno być wywołane
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"  # Nieprawidłowy NIP nie jest zapisywany
        mock_get.assert_not_called()
        
    def test_personal_account_no_nip_validation(self, mocker):
        """Test konta osobowego - nie powinno wywoływać walidacji NIPu"""
        # Mock requests.get żeby sprawdzić czy nie zostanie wywołany
        mock_get = mocker.patch('requests.get')
        
        # Tworzenie konta osobowego
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        
        # Konto osobowe nie powinno wywoływać API
        assert account.first_name == "Jan"
        assert account.last_name == "Kowalski"
        assert account.company_name is None
        mock_get.assert_not_called()
        
    def test_company_account_without_nip(self, mocker):
        """Test konta firmowego bez NIPu"""
        # Mock requests.get żeby sprawdzić czy nie zostanie wywołany
        mock_get = mocker.patch('requests.get')
        
        # Tworzenie konta firmowego bez NIPu
        account = Account(company_name="TEST COMPANY")
        
        # Konto powinno zostać utworzone bez walidacji
        assert account.company_name == "TEST COMPANY"
        assert account.nip == "Invalid"
        mock_get.assert_not_called()
        
    def test_api_url_from_environment(self, mocker):
        """Test czy używana jest zmienna środowiskowa dla URL"""
        import os
        from unittest.mock import patch
        
        # Ustawienie custom URL
        test_url = "https://custom-api.mf.gov.pl/"
        
        with patch.dict(os.environ, {'BANK_APP_MF_URL': test_url}):
            # Mock odpowiedzi API
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
            
            # Tworzenie konta
            account = Account(company_name="TEST COMPANY", nip="8461627563")
            
            # Sprawdzenie czy użyto custom URL
            expected_url = f"{test_url}api/search/nip/8461627563?date="
            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            assert called_url.startswith(expected_url)


class TestAccountOperationsWithNIP:
    """Testy operacji na kontach z walidacją NIPu"""
    
    def test_business_account_deposit_with_valid_nip(self, mocker):
        """Test wpłaty na konto firmowe z prawidłowym NIPem"""
        # Mock walidacji NIPu
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
        
        # Tworzenie konta i wpłata
        account = Account(company_name="TEST COMPANY", nip="8461627563")
        account.deposit(1000)
        
        assert account.balance == 1000.0
        assert account.history == [1000.0]
        
    def test_business_account_loan_requirements(self, mocker):
        """Test wymagań dla pożyczek firmowych"""
        # Mock walidacji NIPu
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
        
        # Tworzenie konta
        account = Account(company_name="TEST COMPANY", nip="8461627563")
        account.deposit(5000)
        
        # Firma nie może składać o pożyczkę osobistą
        assert account.submit_for_loan(1000) is False
        
        # Firma może wziąć pożyczkę biznesową (inna logika)
        # (ta funkcjonalność może być w innej metodzie)


# Test fixtures z conftest.py
@pytest.fixture
def personal_account():
    return Account("A", "B", "05240811968", "")

@pytest.fixture  
def business_account_valid_nip(mocker):
    """Fixture dla konta firmowego z prawidłowym NIPem"""
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
    """Fixture dla konta firmowego z nieprawidłowym NIPem"""
    mock_response = {
        "result": {
            "subject": None
        }
    }
    
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status.return_value = None
    
    # Ten fixture będzie używany tylko do testowania catching ValueError
    return None
