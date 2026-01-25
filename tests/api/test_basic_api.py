import pytest
import requests
import uuid
import random
import time

def generate_unique_pesel():
    timestamp = str(int(time.time() * 1000000))[-4:]
    random_part = str(random.randint(10000, 99999))
    uuid_part = str(uuid.uuid4().int)[:2]
    return f"{timestamp}{random_part}{uuid_part}"

def generate_unique_company_data():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "company_name": f"TEST_COMPANY_{unique_id}",
        "nip": f"{random.randint(1000000000, 9999999999)}"
    }

def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass

class TestAccountCreationAPI:
    def test_create_personal_account(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        payload = {
            "name": "Jan",
            "surname": "Kowalski",
            "pesel": unique_pesel
        }
        response = requests.post(
            f"{base_url}/api/accounts",
            json=payload,
            timeout=2
        )
        assert response.status_code == 201
        assert "Konto utworzone" in response.json().get("message", "")
        delete_account_safely(base_url, unique_pesel)

    def test_create_company_account(self, base_url):
        company_data = generate_unique_company_data()
        payload = {
            "company_name": company_data["company_name"],
            "nip": company_data["nip"]
        }
        response = requests.post(
            f"{base_url}/api/accounts",
            json=payload,
            timeout=2
        )
        assert response.status_code == 201
        assert "Konto utworzone" in response.json().get("message", "")

    def test_create_account_invalid_data(self, base_url):
        payload = {
            "name": "Jan",
        }
        response = requests.post(
            f"{base_url}/api/accounts",
            json=payload,
            timeout=2
        )
        assert response.status_code in [400, 409]

class TestAccountRetrievalAPI:
    def test_get_account_by_pesel(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        response = requests.get(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data["pesel"] == unique_pesel
        assert data["name"] == "Test"
        assert data["surname"] == "User"
        delete_account_safely(base_url, unique_pesel)

    def test_get_all_accounts(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        response = requests.get(f"{base_url}/api/accounts", timeout=2)
        assert response.status_code == 200
        accounts = response.json()
        assert isinstance(accounts, list)
        pesels = [acc.get("pesel") for acc in accounts]
        assert unique_pesel in pesels
        delete_account_safely(base_url, unique_pesel)

    def test_get_account_count(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        response = requests.get(f"{base_url}/api/accounts/count", timeout=2)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 1
        delete_account_safely(base_url, unique_pesel)

class TestTransferAPI:
    def test_incoming_transfer(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        response = requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "incoming", "amount": 100},
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == 100
        delete_account_safely(base_url, unique_pesel)

    def test_outgoing_transfer(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "incoming", "amount": 100},
            timeout=2
        )
        response = requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "outgoing", "amount": 50},
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == 50
        delete_account_safely(base_url, unique_pesel)

    def test_express_transfer(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "incoming", "amount": 100},
            timeout=2
        )
        response = requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "express", "amount": 30},
            timeout=2
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == 69
        delete_account_safely(base_url, unique_pesel)

class TestAccountDeletionAPI:
    def test_delete_account(self, base_url):
        unique_pesel = generate_unique_pesel()
        delete_account_safely(base_url, unique_pesel)
        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "Test", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201
        response = requests.delete(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )
        assert response.status_code == 200
        assert "konto usunięte" in response.json().get("message", "").lower()

    def test_delete_nonexistent_account(self, base_url):
        unique_id = str(uuid.uuid4())[:12]
        response = requests.delete(
            f"{base_url}/api/accounts/{unique_id}",
            timeout=2
        )
        assert response.status_code == 404