import pytest
from src.registry import AccountsRegistry
from src.account import Account


class TestAccountsRegistry:
    """Testy dla Feature 14 - Rejestr kont osobistych."""

    def test_registry_initialization(self, accounts_registry):
        """Test że rejestr inicjalizuje się z pustą listą kont."""
        registry = accounts_registry
        
        assert registry.accounts == []
        assert len(registry.accounts) == 0

    def test_add_account(self, accounts_registry, personal_account):
        """Test dodawania konta do rejestru."""
        registry = accounts_registry
        
        registry.add_account(personal_account)
        
        assert len(registry.accounts) == 1
        assert registry.accounts[0] == personal_account

    def test_add_multiple_accounts(self, accounts_registry):
        """Test dodawania wielu kont do rejestru."""
        registry = accounts_registry
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        acc2 = Account("Anna", "Nowak", "92031512345")
        acc3 = Account("Piotr", "Wiśniewski", "85101098765")
        
        registry.add_account(acc1)
        registry.add_account(acc2)
        registry.add_account(acc3)
        
        assert len(registry.accounts) == 3

    def test_find_account_by_pesel_existing(self, accounts_registry):
        """Test wyszukiwania konta po PESEL-u (konto istnieje)."""
        registry = accounts_registry
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        acc2 = Account("Anna", "Nowak", "92031512345")
        
        registry.add_account(acc1)
        registry.add_account(acc2)
        
        found = registry.find_account_by_pesel("92031512345")
        
        assert found is not None
        assert found.pesel == "92031512345"
        assert found.first_name == "Anna"

    def test_find_account_by_pesel_not_existing(self, accounts_registry):
        """Test wyszukiwania konta po PESEL-u (konto nie istnieje)."""
        registry = accounts_registry
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        registry.add_account(acc1)
        
        found = registry.find_account_by_pesel("99999999999")
        
        assert found is None

    def test_find_account_by_pesel_empty_registry(self, accounts_registry):
        """Test wyszukiwania w pustym rejestrze."""
        registry = accounts_registry
        
        found = registry.find_account_by_pesel("05240811968")
        
        assert found is None

    def test_get_all_accounts(self, accounts_registry):
        """Test zwracania wszystkich kont z rejestru."""
        registry = accounts_registry
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        acc2 = Account("Anna", "Nowak", "92031512345")
        
        registry.add_account(acc1)
        registry.add_account(acc2)
        
        all_accounts = registry.get_all_accounts()
        
        assert len(all_accounts) == 2
        assert acc1 in all_accounts
        assert acc2 in all_accounts

    def test_get_all_accounts_empty_registry(self, accounts_registry):
        """Test zwracania pustej listy gdy rejestr jest pusty."""
        registry = accounts_registry
        
        all_accounts = registry.get_all_accounts()
        
        assert all_accounts == []

    def test_count_accounts(self, accounts_registry):
        """Test zliczania kont w rejestrze."""
        registry = accounts_registry
        
        assert registry.count_accounts() == 0
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        registry.add_account(acc1)
        assert registry.count_accounts() == 1
        
        acc2 = Account("Anna", "Nowak", "92031512345")
        registry.add_account(acc2)
        assert registry.count_accounts() == 2
        
        acc3 = Account("Piotr", "Wiśniewski", "85101098765")
        registry.add_account(acc3)
        assert registry.count_accounts() == 3

    def test_registry_independence(self):
        """Test że różne instancje rejestru są niezależne."""
        registry1 = AccountsRegistry()
        registry2 = AccountsRegistry()
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        registry1.add_account(acc1)
        
        assert registry1.count_accounts() == 1
        assert registry2.count_accounts() == 0

    def test_find_first_matching_pesel_with_duplicates(self, accounts_registry):
        """
        Test że przy duplikatach PESEL zwracane jest pierwsze konto.
        (W prawdziwej aplikacji PESEL powinny być unikalne, ale testujemy edge case)
        """
        registry = accounts_registry
        
        acc1 = Account("Jan", "Kowalski", "05240811968")
        acc2 = Account("Janina", "Kowalska", "05240811968")  # Ten sam PESEL
        
        registry.add_account(acc1)
        registry.add_account(acc2)
        
        found = registry.find_account_by_pesel("05240811968")
        
        assert found.first_name == "Jan"  # Pierwsze dodane konto

    @pytest.mark.parametrize("pesel", [
        "05240811968",
        "92031512345",
        "85101098765",
        "12345678901"
    ])
    def test_find_account_parametrized(self, accounts_registry, pesel):
        """Test parametryzowany wyszukiwania różnych PESEL-i."""
        registry = accounts_registry
        
        # Dodaj konto z danym PESEL-em
        acc = Account("Test", "User", pesel)
        registry.add_account(acc)
        
        # Wyszukaj
        found = registry.find_account_by_pesel(pesel)
        
        assert found is not None
        assert found.pesel == pesel
