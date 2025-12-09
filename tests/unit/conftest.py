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
    return Account(company_name="TestCompany", nip="1234567890")

@pytest.fixture
def business_account_with_zus_transfer():
    acc = Account(company_name="CompanyZUS", nip="9876543210")
    acc.deposit(10000)
    acc.send_transfer(1775)
    return acc

@pytest.fixture
def business_account_high_balance_no_zus():
    acc = Account(company_name="CompanyNoZUS", nip="1111111111")
    acc.deposit(10000)
    return acc

@pytest.fixture
def accounts_registry():
    from src.registry import AccountsRegistry
    return AccountsRegistry()
# FIXTURES Z PRAWDZIWYMI NIPAMI ZAMIAST FAKE
@pytest.fixture
def business_account():
    """Konto firmowe z prawdziwym NIPem (KONRAD SOŁTYS)"""
    return Account(company_name="KONRAD SOŁTYS", nip="8461627563")

@pytest.fixture
def business_account_high_balance_no_zus():
    """Konto firmowe z wysokim saldem, bez ZUS"""
    acc = Account(company_name="FIRMA BEZ ZUS", nip="8461627563")
    acc.deposit(50000)  # Wysokie saldo
    return acc

@pytest.fixture
def business_account_with_zus_transfer():
    """Konto firmowe z transferem ZUS"""
    acc = Account(company_name="FIRMA Z ZUS", nip="8461627563")
    acc.deposit(10000)
    acc.receive_transfer(2000)  # Symulacja ZUS
    return acc

@pytest.fixture
def business_account_valid_nip():
    """Fixture dla konta firmowego z prawidłowym NIPem"""
    return Account(company_name="TEST COMPANY", nip="8461627563")

@pytest.fixture
def business_account_invalid_nip():
    """Fixture dla konta firmowego z nieprawidłowym NIPem
    Użyj monkeypatch żeby zmodyfikować API response w testach"""
    return None  # Ten fixture będzie używany tylko do testowania catching ValueError
