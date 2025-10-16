from src.account import Account
class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe","05240811968","PROM_123")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 50.0
        assert account.pesel == "05240811968"
        account2 = Account("","","123","PRO_123")
        assert account2.balance == 0.0
        assert account2.pesel == "Invalid"
        account3 = Account("","","1234567891011","PROM123")
        assert account3.pesel == "Invalid"
        assert account3.balance == 0.0
        account4 = Account("","","45042502666","PROM_123")
        assert account4.balance == 0.0
        account5 = Account("","",None,"")
        assert account5.pesel == "Invalid"
