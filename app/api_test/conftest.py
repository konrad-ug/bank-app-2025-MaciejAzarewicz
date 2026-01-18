import pytest
import sys
import os
from multiprocessing import Process
import time
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.api import app, registry

@pytest.fixture(scope="function")
def api_client():
    registry.accounts = []
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def base_url():
    return "http://localhost:5000"

@pytest.fixture(scope="function")
def sample_account_data():
    return {
        "name": "Jan",
        "surname": "Kowalski",
        "pesel": "05240811968"
    }

@pytest.fixture(scope="function")
def another_account_data():
    return {
        "name": "Anna",
        "surname": "Nowak",
        "pesel": "92031512345"
    }
