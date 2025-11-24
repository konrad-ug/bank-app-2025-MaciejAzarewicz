import pytest
import requests
from app.api import app, registry

class TestAccountCRUD:
    
    def test_create_account(self, api_client, sample_account_data):
        response = api_client.post('/api/accounts', json=sample_account_data)
        assert response.status_code == 201
        assert response.json == {"message": "Account created"}
        assert registry.count_accounts() == 1

    def test_get_all_accounts_empty(self, api_client):
        response = api_client.get('/api/accounts')
        assert response.status_code == 200
        assert response.json == []

    def test_get_all_accounts_with_data(self, api_client, sample_account_data, another_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        api_client.post('/api/accounts', json=another_account_data)
        response = api_client.get('/api/accounts')
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]["pesel"] == "05240811968"
        assert response.json[1]["pesel"] == "92031512345"

    def test_get_account_count_zero(self, api_client):
        response = api_client.get('/api/accounts/count')
        assert response.status_code == 200
        assert response.json == {"count": 0}

    def test_get_account_count_with_accounts(self, api_client, sample_account_data, another_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        api_client.post('/api/accounts', json=another_account_data)
        response = api_client.get('/api/accounts/count')
        assert response.status_code == 200
        assert response.json == {"count": 2}

    def test_get_account_by_pesel_existing(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        response = api_client.get('/api/accounts/05240811968')
        assert response.status_code == 200
        assert response.json["pesel"] == "05240811968"
        assert response.json["name"] == "Jan"
        assert response.json["surname"] == "Kowalski"
        assert "balance" in response.json

    def test_get_account_by_pesel_not_found(self, api_client):
        response = api_client.get('/api/accounts/99999999999')
        assert response.status_code == 404
        assert "error" in response.json

    def test_update_account_name(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        update_data = {"name": "Janusz"}
        response = api_client.patch('/api/accounts/05240811968', json=update_data)
        assert response.status_code == 200
        assert response.json == {"message": "Account updated"}
        get_response = api_client.get('/api/accounts/05240811968')
        assert get_response.json["name"] == "Janusz"
        assert get_response.json["surname"] == "Kowalski"

    def test_update_account_surname(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        update_data = {"surname": "Nowicki"}
        response = api_client.patch('/api/accounts/05240811968', json=update_data)
        assert response.status_code == 200
        get_response = api_client.get('/api/accounts/05240811968')
        assert get_response.json["name"] == "Jan"
        assert get_response.json["surname"] == "Nowicki"

    def test_update_account_both_fields(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        update_data = {"name": "Piotr", "surname": "Wiśniewski"}
        response = api_client.patch('/api/accounts/05240811968', json=update_data)
        assert response.status_code == 200
        get_response = api_client.get('/api/accounts/05240811968')
        assert get_response.json["name"] == "Piotr"
        assert get_response.json["surname"] == "Wiśniewski"

    def test_update_account_not_found(self, api_client):
        update_data = {"name": "Test"}
        response = api_client.patch('/api/accounts/99999999999', json=update_data)
        assert response.status_code == 404

    def test_update_account_balance_not_changed(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        account = registry.find_account_by_pesel("05240811968")
        account.deposit(1000)
        original_balance = account.balance
        update_data = {"name": "Janusz"}
        api_client.patch('/api/accounts/05240811968', json=update_data)
        get_response = api_client.get('/api/accounts/05240811968')
        assert get_response.json["balance"] == original_balance

    def test_delete_account(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        assert registry.count_accounts() == 1
        response = api_client.delete('/api/accounts/05240811968')
        assert response.status_code == 200
        assert response.json == {"message": "Account deleted"}
        assert registry.count_accounts() == 0

    def test_delete_account_not_found(self, api_client):
        response = api_client.delete('/api/accounts/99999999999')
        assert response.status_code == 404

    def test_delete_account_and_verify(self, api_client, sample_account_data):
        api_client.post('/api/accounts', json=sample_account_data)
        api_client.delete('/api/accounts/05240811968')
        get_response = api_client.get('/api/accounts/05240811968')
        assert get_response.status_code == 404

    @pytest.mark.parametrize("pesel,name,surname", [
        ("05240811968", "Jan", "Kowalski"),
        ("92031512345", "Anna", "Nowak"),
        ("85101098765", "Piotr", "Wiśniewski")
    ])
    def test_create_multiple_accounts_parametrized(self, api_client, pesel, name, surname):
        account_data = {"name": name, "surname": surname, "pesel": pesel}
        response = api_client.post('/api/accounts', json=account_data)
        assert response.status_code == 201
        get_response = api_client.get(f'/api/accounts/{pesel}')
        assert get_response.status_code == 200
        assert get_response.json["pesel"] == pesel
