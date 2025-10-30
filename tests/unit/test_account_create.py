import pytest
from src.account import Account, InsufficientFunds

def test_history_after_deposit_and_express_and_withdraw():
    acc = Account("J", "D", "05240811968", "PROM_123")
    # promo daje 50 (zapisane w konstruktorze)
    assert acc.balance == 50.0
    acc.receive_transfer(500)
    acc.send_express_transfer(300)
    # historia: promo 50, +500, -300, -1
    assert acc.history == [50.0, 500.0, -300.0, -1.0]
    assert acc.balance == 249.0  # 50 + 500 - 300 -1

def test_history_not_changed_on_failed_operations():
    acc = Account("A", "B", "05240811968", "")
    acc.balance = 10.0
    with pytest.raises(InsufficientFunds):
        acc.send_transfer(11)
    assert acc.history == []
    with pytest.raises(ValueError):
        acc.deposit(0)
    assert acc.history == []

