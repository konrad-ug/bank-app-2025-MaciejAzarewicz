import pytest
from src.account import Account, InsufficientFunds

def test_withdraw_raises_valueerror_and_insufficient():
    a = Account("A", "B", "05240811968", "")
    with pytest.raises(ValueError):
        a.withdraw(0)
    a.deposit(5)
    with pytest.raises(InsufficientFunds):
        a.withdraw(10)

