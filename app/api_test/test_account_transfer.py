import pytest
from app.api import app, registry
from src.account import InsufficientFunds

class TestAccountTransfer:
    
    def test_transfer_incoming_success(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "type": "incoming",
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Przelew wykonany pomyślnie"
        assert response.json["balance"] == 100.0
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 100.0
    
    def test_transfer_outgoing_success(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(500.0)
        
        transfer_data = {
            "type": "outgoing", 
            "amount": 200.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Przelew wykonany pomyślnie"
        assert response.json["balance"] == 300.0
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 300.0
    
    def test_transfer_express_success(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(100.0)
        
        transfer_data = {
            "type": "express",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Przelew wykonany pomyślnie"
        assert response.json["balance"] == 49.0
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 49.0
    
    def test_transfer_account_not_found_returns_404(self, api_client):
        transfer_data = {
            "type": "incoming",
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/99999999999/transfer', json=transfer_data)
        
        assert response.status_code == 404
        assert "error" in response.json
        assert "Konto nie znalezione" in response.json["error"]
    
    @pytest.mark.parametrize("invalid_type", ["invalid", "wrong", "transfer", ""])
    def test_transfer_invalid_type_returns_400(self, api_client, invalid_type):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "type": invalid_type,
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
        assert "Niepoprawny typ przelewu" in response.json["error"]
    
    @pytest.mark.parametrize("invalid_amount", [0, -100, -1, "invalid", "abc"])
    def test_transfer_invalid_amount_returns_400(self, api_client, invalid_amount):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "type": "incoming",
            "amount": invalid_amount
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_transfer_outgoing_insufficient_funds_returns_422(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(50.0)
        
        transfer_data = {
            "type": "outgoing",
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 422
        assert "error" in response.json
        assert "Niewystarczające środki" in response.json["error"]
    
    def test_transfer_express_insufficient_funds_returns_422(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(10.0)
        
        transfer_data = {
            "type": "express",
            "amount": 10.5
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 422
        assert "error" in response.json
        assert "Niewystarczające środki" in response.json["error"]
    
    def test_multiple_transfers_accumulate_balance(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        for i in range(3):
            transfer_data = {
                "type": "incoming",
                "amount": 100.0
            }
            response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
            assert response.status_code == 200
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 300.0
        
        transfer_data = {
            "type": "outgoing",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        assert response.status_code == 200
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 250.0
    
    def test_transfer_express_company_account_higher_fee(self, api_client):
        company_data = {
            "name": "TechCorp", 
            "surname": "", 
            "pesel": "12345678901",
            "company_name": "TechCorp Sp. z o.o.",
            "nip": "1234567890"
        }
        api_client.post('/api/accounts', json=company_data)
        account = registry.find_account_by_pesel("12345678901")
        account.deposit(100.0)
        
        transfer_data = {
            "type": "express",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/12345678901/transfer', json=transfer_data)
        
        assert response.status_code == 200
        account = registry.find_account_by_pesel("12345678901")
        assert account.balance == 45.0
        assert account.company_name == "TechCorp Sp. z o.o."
    
    def test_transfer_missing_amount_field_returns_400(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "type": "incoming"
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_transfer_missing_type_field_returns_400(self, api_client):
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
