import pytest
from src.account import Account, InsufficientFunds

def test_express_transfer_fee_difference():
    p = Account("A", "B", "05240811968", "")
    p.deposit(10)
    p.send_express_transfer(5)
    assert p.history[-2:] == [-5.0, -1.0]
    b = Account(company_name="Firma", nip="8461627563")
    b.deposit(10)
    b.send_express_transfer(5)
    assert b.history[-2:] == [-5.0, -5.0]

def test_negative_amounts_raise():
    a = Account("A", "B", "05240811968", "")
    with pytest.raises(ValueError):
        a.send_transfer(-10)
    with pytest.raises(ValueError):
        a.receive_transfer(-5)
    with pytest.raises(ValueError):
        a.send_express_transfer(-2)
