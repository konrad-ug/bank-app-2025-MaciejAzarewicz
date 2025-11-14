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

