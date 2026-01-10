import pytest
from src.account import Account

class TestBusinessLoan:

    def test_business_loan_approved_when_conditions_met(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(5000)
        account.receive_transfer(1775)
        result = account.take_loan(1000)
        assert result is True
        assert account.balance == 7775.0

    def test_business_loan_rejected_insufficient_balance(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(500)
        account.receive_transfer(1775)
        result = account.take_loan(1500)
        assert result is False

    def test_business_loan_rejected_no_zus_transfer(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(10000)
        result = account.take_loan(1000)
        assert result is False

    def test_business_loan_rejected_personal_account(self):
        account = Account(first_name="Jan", last_name="Kowalski", pesel="05240811968")
        account.deposit(10000)
        account.receive_transfer(1775)
        result = account.take_loan(1000)
        assert result is False
        assert account.balance == 11775.0

    def test_business_loan_rejected_boundary_balance(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(2000)
        account.receive_transfer(1775)
        result = account.take_loan(1000)
        assert result is True

    @pytest.mark.parametrize("amount,should_pass", [
        (500, True),
        (1000, True),
        (2499, True),
        (2500, True),
        (2501, True),
        (3387, True),
        (3388, False),
    ])
    def test_business_loan_amount_boundary(self, amount, should_pass):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(5000)
        account.receive_transfer(1775)
        result = account.take_loan(amount)
        if should_pass:
            assert result is True
            assert account.balance == 6775.0 + amount
        else:
            assert result is False
            assert account.balance == 6775.0

    def test_business_loan_multiple_zus_transfers(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(10000)
        account.receive_transfer(1775)
        account.receive_transfer(2000)
        result = account.take_loan(1000)
        assert result is True
        assert account.balance == 14775.0

    def test_business_loan_updates_history_correctly(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(5000)
        account.receive_transfer(1775)
        initial_history_len = len(account.history)
        result = account.take_loan(1000)
        assert result is True
        assert len(account.history) == initial_history_len + 1
        assert account.history[-1] == 1000.0

    def test_business_loan_no_changes_when_rejected(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(500)
        account.receive_transfer(1775)
        initial_balance = account.balance
        initial_history_len = len(account.history)
        result = account.take_loan(1500)
        assert result is False
        assert account.balance == initial_balance
        assert len(account.history) == initial_history_len

    def test_business_loan_with_different_amounts(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(10000)
        account.receive_transfer(1775)
        assert account.take_loan(100) is True
        assert account.balance == 11875.0
        assert account.take_loan(500) is True
        assert account.balance == 12375.0
        assert account.take_loan(1000) is True
        assert account.balance == 13375.0

class TestBusinessLoanEdgeCases:

    def test_business_loan_exact_boundary(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(4001)
        account.receive_transfer(1775)
        assert account.take_loan(2000) is True

    def test_business_loan_one_cent_less(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(2224.99)
        account.receive_transfer(1775)
        assert account.take_loan(2000) is False

    def test_business_loan_zero_zus_transfer(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(10000)
        account.history.append(0)
        assert account.take_loan(1000) is False

    def test_business_loan_negative_amount_rejected(self):
        account = Account(company_name="Firma", nip="8461627563")
        account.deposit(10000)
        account.receive_transfer(1775)
        with pytest.raises(ValueError):
            account.take_loan(-1000)
