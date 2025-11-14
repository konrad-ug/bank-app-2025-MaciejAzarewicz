import pytest
from src.account import Account

def test_loan_approved_by_three_recent_deposits():
    a = Account("A", "B", "05240811968", "")
    # three deposits as last three transactions
    a.deposit(1)
    a.deposit(1)
    a.deposit(1)
    # despite small deposits, condition A says last 3 are deposits -> loan granted
    assert a.submit_for_loan(1000) is True
    assert a.balance == 1003.0
    assert a.history[-1] == 1000.0

def test_loan_approved_by_five_transactions_sum():
    a = Account("A", "B", "05240811968", "")
    # build at least 5 transactions: mix of deposits and withdrawals
    a.deposit(50)    # +50
    a.withdraw(10)   # -10
    a.deposit(40)    # +40
    a.send_transfer(20)  # -20 (but will raise InsufficientFunds if balance isn't enough -> avoid)
    # Adjust sequence so sends don't fail:
    # Reset: rebuild safely
    a = Account("A", "B", "05240811968", "")
    a.deposit(50)
    a.deposit(10)
    a.deposit(40)
    a.withdraw(5)
    a.receive_transfer(30)
    # last 5 sum = 50+10+40-5+30 = 125
    assert len(a.history) >= 5
    assert a.submit_for_loan(100) is True
    assert a.balance == 125.0 + 100.0  # previous balance + loan
    assert a.history[-1] == 100.0

def test_loan_rejected_if_not_personal():
    b = Account(company_name="Firma", nip="1234567890")
    b.deposit(100)
    b.deposit(100)
    b.deposit(100)
    assert b.submit_for_loan(50) is False

def test_loan_rejected_when_conditions_not_met():
    a = Account("A", "B", "05240811968", "")
    # not enough history and not 3 last deposits
    a.deposit(50)
    a.withdraw(10)
    a.deposit(5)
    assert a.submit_for_loan(10) is False
    # balance unchanged
    assert a.balance == 45.0

def test_submit_for_loan_invalid_amount_raises():
    a = Account("A", "B", "05240811968", "")
    with pytest.raises(ValueError):
        a.submit_for_loan(0)
    with pytest.raises(ValueError):
        a.submit_for_loan(-10)
