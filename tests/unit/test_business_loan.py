import pytest
from src.account import Account


class TestBusinessLoan:
    """Testy dla Feature 13 - Kredyt firmowy (take_loan)."""

    def test_take_loan_approved_with_both_conditions(self, business_account_with_zus_transfer):
        """
        Test aprobacie kredytu gdy spełnione są oba warunki:
        - balance >= 2 * amount
        - przelew do ZUS (-1775) w historii
        """
        acc = business_account_with_zus_transfer
        initial_balance = acc.balance
        loan_amount = 1000
        
        # balance = 10000 - 1775 = 8225, więc 8225 >= 2*1000 (2000) ✓
        # historia zawiera -1775 ✓
        result = acc.take_loan(loan_amount)
        
        assert result is True
        assert acc.balance == initial_balance + loan_amount

    def test_take_loan_rejected_no_zus_transfer(self, business_account_high_balance_no_zus):
        """
        Test odrzucenia kredytu gdy brak przelewu do ZUS,
        mimo że saldo jest wystarczające.
        """
        acc = business_account_high_balance_no_zus
        initial_balance = acc.balance
        loan_amount = 1000
        
        # balance = 10000 >= 2*1000 ✓
        # ale brak -1775 w historii ✗
        result = acc.take_loan(loan_amount)
        
        assert result is False
        assert acc.balance == initial_balance  # Bez zmian

    def test_take_loan_rejected_insufficient_balance(self):
        """
        Test odrzucenia kredytu gdy jest przelew do ZUS,
        ale saldo jest niewystarczające (< 2 * amount).
        """
        acc = Account(company_name="LowBalance", nip="2222222222")
        acc.deposit(3000)
        acc.send_transfer(1775)  # Przelew do ZUS
        # balance = 3000 - 1775 = 1225
        
        loan_amount = 1000
        initial_balance = acc.balance
        
        # balance = 1225 < 2*1000 (2000) ✗
        # historia zawiera -1775 ✓
        result = acc.take_loan(loan_amount)
        
        assert result is False
        assert acc.balance == initial_balance

    def test_take_loan_rejected_both_conditions_not_met(self, business_account):
        """
        Test odrzucenia gdy żaden warunek nie jest spełniony.
        """
        acc = business_account
        acc.deposit(500)  # Małe saldo
        
        loan_amount = 1000
        initial_balance = acc.balance
        
        # balance = 500 < 2*1000 ✗
        # brak -1775 w historii ✗
        result = acc.take_loan(loan_amount)
        
        assert result is False
        assert acc.balance == initial_balance

    @pytest.mark.parametrize("amount", [0, -100, -1])
    def test_take_loan_invalid_amount(self, business_account_with_zus_transfer, amount):
        """
        Test że metoda rzuca ValueError dla nieprawidłowych kwot.
        """
        acc = business_account_with_zus_transfer
        
        with pytest.raises(ValueError):
            acc.take_loan(amount)

    def test_take_loan_not_available_for_personal_accounts(self, personal_account):
        """
        Test że kredyt firmowy nie jest dostępny dla kont osobistych.
        """
        acc = personal_account
        acc.deposit(10000)
        acc.send_transfer(1775)  # Nawet z przelewem
        
        loan_amount = 1000
        initial_balance = acc.balance
        
        result = acc.take_loan(loan_amount)
        
        assert result is False
        assert acc.balance == initial_balance

    def test_take_loan_edge_case_exact_double_balance(self):
        """
        Test przypadku brzegowego: balance = dokładnie 2 * amount.
        """
        acc = Account(company_name="EdgeCase", nip="3333333333")
        acc.deposit(4000)
        acc.send_transfer(1775)  # ZUS
        # balance = 4000 - 1775 = 2225
        
        loan_amount = 1112.5  # 2225 / 2 = 1112.5
        
        result = acc.take_loan(loan_amount)
        
        assert result is True
        assert acc.balance == 2225 + 1112.5

    def test_take_loan_multiple_zus_transfers(self):
        """
        Test że kredyt jest przyznawany nawet gdy jest wiele przelewów do ZUS.
        """
        acc = Account(company_name="MultiZUS", nip="4444444444")
        acc.deposit(20000)
        acc.send_transfer(1775)
        acc.send_transfer(1775)
        acc.send_transfer(1775)
        # balance = 20000 - 3*1775 = 14675
        
        loan_amount = 5000
        
        result = acc.take_loan(loan_amount)
        
        assert result is True
        assert acc.balance == 14675 + 5000
