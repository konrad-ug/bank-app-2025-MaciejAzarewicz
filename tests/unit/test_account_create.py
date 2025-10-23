import pytest
from src.account import Account, InsufficientFunds

class TestTransfers:
    def test_send_and_receive_personal(self):
        a = Account("John", "Doe", "05240811968", "PROM_123")
        assert a.balance == 50.0
        a.send_transfer(20)
        assert a.balance == 30.0
        a.receive_transfer(10)
        assert a.balance == 40.0

    def test_send_transfer_insufficient(self):
        a = Account("A", "B", "05240811968", "")
        a.balance = 0.0
        with pytest.raises(InsufficientFunds):
            a.send_transfer(1)

    def test_send_transfer_invalid_amount(self):
        a = Account("A", "B", "05240811968", "")
        with pytest.raises(ValueError):
            a.send_transfer(0)

    def test_business_account_no_promo_and_nip(self):
        b = Account(company_name="Firma", nip="1234567890")
        assert b.company_name == "Firma"
        assert b.nip == "1234567890"
        assert b.balance == 0.0
        b2 = Account(company_name="X", nip="123")
        assert b2.nip == "Invalid"

    def test_express_transfer_personal_fee_allows_negative(self):
        a = Account("J", "D", "05240811968", "PROM_123")
        assert a.balance == 50.0
        a.send_express_transfer(50)
        assert a.balance == -1.0

    def test_express_transfer_personal_insufficient_amount(self):
        a = Account("J", "D", "05240811968", "")
        a.balance = 10.0
        with pytest.raises(InsufficientFunds):
            a.send_express_transfer(11)

    def test_express_transfer_business_fee(self):
        b = Account(company_name="Firma", nip="1234567890")
        b.balance = 100.0
        b.send_express_transfer(100)
        assert b.balance == -5.0

    def test_receive_transfer_invalid_amount(self):
        a = Account("J", "D", "05240811968", "")
        with pytest.raises(ValueError):
            a.receive_transfer(0)
