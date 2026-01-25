import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.api import app
from src.account import Account

class TestAccountsSaveLoadAPI:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def setup_accounts(self, client):
        client.post('/api/accounts', json={
            "name": "Jan",
            "surname": "Kowalski",
            "pesel": "90050512345"
        })
        client.post('/api/accounts', json={
            "name": "Anna",
            "surname": "Nowak",
            "pesel": "85050567890"
        })
        yield
        client.delete('/api/accounts/90050512345')
        client.delete('/api/accounts/85050567890')

    def test_save_accounts_returns_success_message(self, client, setup_accounts):
        response = client.post('/api/accounts/save')
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert "2" in data["message"]

    def test_save_accounts_with_empty_registry(self, client):
        response = client.post('/api/accounts/save')
        assert response.status_code == 200
        data = response.get_json()
        assert "0" in data["message"]

    def test_load_accounts_returns_success_message(self, client, setup_accounts, mocker):
        client.post('/api/accounts/save')
        mock_repo_class = mocker.patch('app.api.MongoAccountsRepository')
        mock_repo = mocker.Mock()
        mock_repo.load_all.return_value = []
        mock_repo_class.return_value = mock_repo
        response = client.post('/api/accounts/load')
        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data
        assert "count" in data

    def test_save_endpoint_returns_500_on_error(self, client, setup_accounts, mocker):
        mock_repo_class = mocker.patch('app.api.MongoAccountsRepository')
        mock_repo = mocker.Mock()
        mock_repo.save_all.return_value = False
        mock_repo_class.return_value = mock_repo
        response = client.post('/api/accounts/save')
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    def test_save_and_load_work_together(self, client, mocker):
        client.post('/api/accounts', json={
            "name": "Test",
            "surname": "User",
            "pesel": "90050599999"
        })
        test_account_data = [{
            "first_name": "Test",
            "last_name": "User",
            "pesel": "90050599999",
            "balance": 100.0,
            "history": [100.0],
            "company_name": None,
            "nip": "Invalid"
        }]
        mock_repo_class = mocker.patch('app.api.MongoAccountsRepository')
        mock_repo = mocker.Mock()
        mock_repo.save_all.return_value = True
        mock_repo.load_all.return_value = test_account_data
        mock_repo_class.return_value = mock_repo
        save_response = client.post('/api/accounts/save')
        assert save_response.status_code == 200
        client.delete('/api/accounts/90050599999')
        load_response = client.post('/api/accounts/load')
        assert load_response.status_code == 200
        client.delete('/api/accounts/90050599999')

    def test_load_clears_registry_first(self, client, setup_accounts, mocker):
        client.post('/api/accounts', json={
            "name": "Initial",
            "surname": "User",
            "pesel": "90050511111"
        })
        loaded_accounts = [
            {
                "first_name": "Loaded",
                "last_name": "User",
                "pesel": "90050522222",
                "balance": 500.0,
                "history": [500.0],
                "company_name": None,
                "nip": "Invalid"
            }
        ]
        mock_repo_class = mocker.patch('app.api.MongoAccountsRepository')
        mock_repo = mocker.Mock()
        mock_repo.load_all.return_value = loaded_accounts
        mock_repo_class.return_value = mock_repo
        response = client.post('/api/accounts/load')
        assert response.status_code == 200
        client.delete('/api/accounts/90050522222')