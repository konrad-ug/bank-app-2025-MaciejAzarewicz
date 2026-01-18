import pytest
import requests
import uuid
import random


BASE_URL = "http://localhost:5000"


def is_valid_pesel(pesel):
    return pesel and isinstance(pesel, str) and pesel.isdigit() and len(pesel) == 11


def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def api_session():
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def unique_pesel():
    random_suffix = f"{random.randint(10000, 99999)}"
    pesel = f"{random_suffix}123456"
    return pesel


@pytest.fixture
def unique_company_data():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "company_name": f"TEST_COMPANY_{unique_id}",
        "nip": f"{random.randint(1000000000, 9999999999)}"
    }


@pytest.fixture
def created_account(base_url, unique_pesel):
    delete_account_safely(base_url, unique_pesel)

    payload = {
        "name": "Test",
        "surname": "User",
        "pesel": unique_pesel
    }

    response = requests.post(
        f"{base_url}/api/accounts",
        json=payload,
        timeout=2
    )

    if response.status_code != 201:
        pytest.skip(f"Nie udało się utworzyć konta testowego: {response.status_code}")

    yield unique_pesel

    delete_account_safely(base_url, unique_pesel)


@pytest.fixture
def created_company_account(base_url, unique_company_data):
    delete_account_safely(base_url, unique_company_data['company_name'])

    payload = {
        "company_name": unique_company_data["company_name"],
        "nip": unique_company_data["nip"]
    }

    response = requests.post(
        f"{base_url}/api/accounts",
        json=payload,
        timeout=2
    )

    if response.status_code != 201:
        pytest.skip(f"Nie udało się utworzyć konta firmowego: {response.status_code}")

    yield unique_company_data

    delete_account_safely(base_url, unique_company_data['company_name'])


@pytest.fixture
def account_with_balance(base_url, unique_pesel):
    delete_account_safely(base_url, unique_pesel)

    create_response = requests.post(
        f"{base_url}/api/accounts",
        json={
            "name": "Test",
            "surname": "User",
            "pesel": unique_pesel
        },
        timeout=2
    )

    if create_response.status_code != 201:
        pytest.skip(f"Nie udało się utworzyć konta: {create_response.status_code}")

    transfer_response = requests.post(
        f"{base_url}/api/accounts/{unique_pesel}/transfer",
        json={"type": "incoming", "amount": 1000},
        timeout=2
    )

    if transfer_response.status_code != 200:
        pytest.skip(f"Nie udało się wpłacić środków: {transfer_response.status_code}")

    yield unique_pesel

    delete_account_safely(base_url, unique_pesel)
