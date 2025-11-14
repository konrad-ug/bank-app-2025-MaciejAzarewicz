import pytest
from src.account import Account, InsufficientFunds

def test_deposit_and_withdraw_sequence():
    a = Account("A", "B", "05240811968", "")
    a.deposit(100)
    a.withdraw(40)
    assert a.balance == 60
    assert a.history == [100.0, -40.0]

def test_withdraw_invalid_values():
    a = Account("A", "B", "05240811968", "")
    with pytest.raises(ValueError):
        a.withdraw(0)
    with pytest.raises(ValueError):
        a.withdraw(-5)

def test_deposit_invalid_values():
    a = Account("A", "B", "05240811968", "")
    with pytest.raises(ValueError):
        a.deposit(0)
    with pytest.raises(ValueError):
        a.deposit(-1)

def test_withdraw_insufficient_funds():
    a = Account("A", "B", "05240811968", "")
    a.deposit(10)
    with pytest.raises(InsufficientFunds):
        a.withdraw(11)

