import pytest
from src.account import Account

def test_loan_approved_by_three_recent_deposits(account_with_three_deposits):
    a = account_with_three_deposits
    assert a.submit_for_loan(1000) is True
    assert a.balance == 1003.0
    assert a.history[-1] == 1000.0

def test_loan_approved_by_five_transactions_sum(account_with_5_history):
    a = account_with_5_history
    # suma ostatnich 5 = 50 + 10 + 40 -5 +30 = 125
    assert a.submit_for_loan(100) is True
    assert a.balance == 125.0 + 100.0
    assert a.history[-1] == 100.0

def test_loan_rejected_if_not_personal():
    b = Account(company_name="Firma", nip="8461627563")
    b.deposit(100)
    b.deposit(100)
    b.deposit(100)
    assert b.submit_for_loan(50) is False

def test_loan_rejected_when_conditions_not_met(personal_account):
    a = personal_account
    a.deposit(50)
    a.withdraw(10)
    a.deposit(5)
    assert a.submit_for_loan(10) is False
    assert a.balance == 45.0

@pytest.mark.parametrize("bad_amount", [0, -10])
def test_submit_for_loan_invalid_amount_raises(personal_account, bad_amount):
    with pytest.raises(ValueError):
        personal_account.submit_for_loan(bad_amount)
