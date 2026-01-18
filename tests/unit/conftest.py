import pytest
from src.account import Account

@pytest.fixture
def personal_account():
    return Account("A", "B", "05240811968", "")

@pytest.fixture
def account_with_three_deposits(personal_account):
    a = personal_account
    a.deposit(1)
    a.deposit(1)
    a.deposit(1)
    return a

@pytest.fixture
def account_with_5_history(personal_account):
    a = personal_account
    a.deposit(50)
    a.deposit(10)
    a.deposit(40)
    a.withdraw(5)
    a.receive_transfer(30)
    return a

@pytest.fixture
def business_account():
    return Account(company_name="KONRAD SOŁTYS", nip="8461627563")

@pytest.fixture
def business_account_with_zus_transfer():
    acc = Account(company_name="FIRMA Z ZUS", nip="8461627563")
    acc.deposit(10000)
    acc.receive_transfer(1775)
    return acc

@pytest.fixture
def business_account_high_balance_no_zus():
    acc = Account(company_name="FIRMA BEZ ZUS", nip="8461627563")
    acc.deposit(50000)
    return acc

@pytest.fixture
def accounts_registry():
    from src.registry import AccountsRegistry
    return AccountsRegistry()

@pytest.fixture
def business_account_valid_nip():
    return Account(company_name="TEST COMPANY", nip="8461627563")

@pytest.fixture
def business_account_invalid_nip():
    return None

@pytest.fixture
def personal_account_with_history():
    account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
    account.deposit(100)
    account.withdraw(1)
    account.deposit(500)
    return account

@pytest.fixture
def company_account_with_history(mocker):
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
    account.send_transfer(1000)
    account.receive_transfer(500)
    return account

@pytest.fixture
def mock_smtp_client(mocker):
    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.send.return_value = True
    
    mocker.patch('src.account.SMTPClient', return_value=mock_client)
    return mock_client
