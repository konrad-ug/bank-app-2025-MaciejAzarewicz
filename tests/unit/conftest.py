import pytest
from src.account import Account

@pytest.fixture
def personal_account():
    """Proste konto osobiste z prawidłowym PESEL-em."""
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
    # 5 transakcji przykładowych (uwzględniają opłaty ekspresowe jako transakcje jeśli chcesz)
    a.deposit(50)     # +50
    a.deposit(10)     # +10
    a.deposit(40)     # +40
    a.withdraw(5)     # -5
    a.receive_transfer(30)  # +30
    return a

@pytest.fixture
def business_account():
    """Proste konto firmowe z prawidłowym NIP-em."""
    return Account(company_name="TestCompany", nip="1234567890")

@pytest.fixture
def business_account_with_zus_transfer():
    """Konto firmowe z przelewem do ZUS i odpowiednim saldem."""
    acc = Account(company_name="CompanyZUS", nip="9876543210")
    acc.deposit(10000)  # Wysokie saldo
    acc.send_transfer(1775)  # Przelew do ZUS
    return acc

@pytest.fixture
def business_account_high_balance_no_zus():
    """Konto firmowe z wysokim saldem ale bez przelewu do ZUS."""
    acc = Account(company_name="CompanyNoZUS", nip="1111111111")
    acc.deposit(10000)
    return acc

@pytest.fixture
def accounts_registry():
    """Pusty rejestr kont dla testów."""
    from src.registry import AccountsRegistry
    return AccountsRegistry()

