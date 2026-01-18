import pytest
from app.api import app, registry
from src.account import InsufficientFunds

class TestAccountTransfer:
    
    def test_transfer_incoming_success(self, api_client):
        # Create account
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        # Perform incoming transfer
        transfer_data = {
            "type": "incoming",
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Transfer completed successfully"
        assert response.json["balance"] == 100.0
        
        # Verify account balance
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 100.0
    
    def test_transfer_outgoing_success(self, api_client):
        # Create account and deposit money
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(500.0)
        
        # Perform outgoing transfer
        transfer_data = {
            "type": "outgoing", 
            "amount": 200.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Transfer completed successfully"
        assert response.json["balance"] == 300.0
        
        # Verify account balance
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 300.0
    
    def test_transfer_express_success(self, api_client):
        # Create account and deposit money (more for fee)
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(100.0)
        
        # Perform express transfer (amount + 1.0 fee)
        transfer_data = {
            "type": "express",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 200
        assert response.json["message"] == "Transfer completed successfully"
        assert response.json["balance"] == 49.0  # 100 - 50 - 1.0 fee
        
        # Verify account balance
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
        assert "Account not found" in response.json["error"]
    
    @pytest.mark.parametrize("invalid_type", ["invalid", "wrong", "transfer", ""])
    def test_transfer_invalid_type_returns_400(self, api_client, invalid_type):
        # Create account
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        transfer_data = {
            "type": invalid_type,
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
        assert "Invalid transfer type" in response.json["error"]
    
    @pytest.mark.parametrize("invalid_amount", [0, -100, -1, "invalid", "abc"])
    def test_transfer_invalid_amount_returns_400(self, api_client, invalid_amount):
        # Create account
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
        # Create account with small balance
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(50.0)
        
        # Try to transfer more than available
        transfer_data = {
            "type": "outgoing",
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 422
        assert "error" in response.json
        assert "InsufficientFunds" in response.json["error"]
    
    def test_transfer_express_insufficient_funds_returns_422(self, api_client):
        # Create account with very low balance
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(10.0)
        
        # Try express transfer that would result in balance < -fee
        # balance=10, amount=10.5, fee=1 -> final=-1.5 < -1 (fee), should fail
        transfer_data = {
            "type": "express",
            "amount": 10.5
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 422
        assert "error" in response.json
        assert "InsufficientFunds" in response.json["error"]
    
    def test_multiple_transfers_accumulate_balance(self, api_client):
        # Create account
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        # Multiple incoming transfers
        for i in range(3):
            transfer_data = {
                "type": "incoming",
                "amount": 100.0
            }
            response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
            assert response.status_code == 200
        
        # Check final balance
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 300.0
        
        # Mix incoming and outgoing
        transfer_data = {
            "type": "outgoing",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        assert response.status_code == 200
        
        account = registry.find_account_by_pesel("05240811968")
        assert account.balance == 250.0
    
    def test_transfer_express_company_account_higher_fee(self, api_client):
        # Create company account
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
        
        # Express transfer should charge 5.0 fee for company
        transfer_data = {
            "type": "express",
            "amount": 50.0
        }
        response = api_client.post('/api/accounts/12345678901/transfer', json=transfer_data)
        
        assert response.status_code == 200
        account = registry.find_account_by_pesel("12345678901")
        assert account.balance == 45.0  # 100 - 50 - 5.0 fee
        assert account.company_name == "TechCorp Sp. z o.o."
    
    def test_transfer_missing_amount_field_returns_400(self, api_client):
        # Create account
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        # Missing amount field
        transfer_data = {
            "type": "incoming"
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
    
    def test_transfer_missing_type_field_returns_400(self, api_client):
        # Create account
        account_data = {"name": "Jan", "surname": "Kowalski", "pesel": "05240811968"}
        api_client.post('/api/accounts', json=account_data)
        
        # Missing type field
        transfer_data = {
            "amount": 100.0
        }
        response = api_client.post('/api/accounts/05240811968/transfer', json=transfer_data)
        
        assert response.status_code == 400
        assert "error" in response.json
