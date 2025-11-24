import pytest
from src.account import Account


class TestBusinessLoan:
    def test_take_loan_approved_with_both_conditions(self, business_account_with_zus_transfer):
        acc = business_account_with_zus_transfer
        initial_balance = acc.balance
        loan_amount = 1000
        result = acc.take_loan(loan_amount)
        assert result is True
        assert acc.balance == initial_balance + loan_amount

    def test_take_loan_rejected_no_zus_transfer(self, business_account_high_balance_no_zus):
        acc = business_account_high_balance_no_zus
        initial_balance = acc.balance
        loan_amount = 1000
        result = acc.take_loan(loan_amount)
        assert result is False
        assert acc.balance == initial_balance

    def test_take_loan_rejected_insufficient_balance(self):
        acc = Account(company_name="LowBalance", nip="2222222222")
        acc.deposit(3000)
        acc.send_transfer(1775)
        loan_amount = 1000
        initial_balance = acc.balance
        result = acc.take_loan(loan_amount)
        assert result is False
        assert acc.balance == initial_balance

    def test_take_loan_rejected_both_conditions_not_met(self, business_account):
        acc = business_account
        acc.deposit(500)
        loan_amount = 1000
        initial_balance = acc.balance
        result = acc.take_loan(loan_amount)
        assert result is False
        assert acc.balance == initial_balance

    @pytest.mark.parametrize("amount", [0, -100, -1])
    def test_take_loan_invalid_amount(self, business_account_with_zus_transfer, amount):
        acc = business_account_with_zus_transfer
        with pytest.raises(ValueError):
            acc.take_loan(amount)

    def test_take_loan_not_available_for_personal_accounts(self, personal_account):
        acc = personal_account
        acc.deposit(10000)
        acc.send_transfer(1775)
        loan_amount = 1000
        initial_balance = acc.balance
        result = acc.take_loan(loan_amount)
        assert result is False
        assert acc.balance == initial_balance

    def test_take_loan_edge_case_exact_double_balance(self):
        acc = Account(company_name="EdgeCase", nip="3333333333")
        acc.deposit(4000)
        acc.send_transfer(1775)
        loan_amount = 1112.5
        result = acc.take_loan(loan_amount)
        assert result is True
        assert acc.balance == 2225 + 1112.5

    def test_take_loan_multiple_zus_transfers(self):
        acc = Account(company_name="MultiZUS", nip="4444444444")
        acc.deposit(20000)
        acc.send_transfer(1775)
        acc.send_transfer(1775)
        acc.send_transfer(1775)
        loan_amount = 5000
        result = acc.take_loan(loan_amount)
        assert result is True
        assert acc.balance == 14675 + 5000
