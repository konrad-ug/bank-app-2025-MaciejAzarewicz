import pytest
import requests
import time
import uuid
import random


BASE_URL = "http://localhost:5000"


def generate_unique_pesel():
    timestamp = str(int(time.time() * 1000000))[-4:]
    random_part = str(random.randint(10000, 99999))
    uuid_part = str(uuid.uuid4().int)[:2]
    return f"{timestamp}{random_part}{uuid_part}"


def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass


@pytest.fixture(scope="module")
def base_url():
    return BASE_URL


@pytest.fixture(scope="module")
def api_session():
    session = requests.Session()
    yield session
    session.close()
