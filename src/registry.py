"""
Account Registry Module
Provides a simple in-memory registry for personal accounts (POC).
"""


class AccountsRegistry:
    """
    Simple registry for managing personal accounts in memory.
    This is a proof of concept - in production, this would connect to a database.
    """

    def __init__(self):
        """Initialize empty accounts registry."""
        self.accounts = []

    def add_account(self, account):
        """
        Add an account to the registry.
        
        Args:
            account: Account instance to add
        """
        self.accounts.append(account)

    def find_account_by_pesel(self, pesel):
        """
        Find an account by PESEL number.
        
        Args:
            pesel (str): PESEL number to search for
            
        Returns:
            Account instance if found, None otherwise
        """
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return None

    def get_all_accounts(self):
        """
        Get all accounts from the registry.
        
        Returns:
            List of all Account instances
        """
        return self.accounts

    def count_accounts(self):
        """
        Count the number of accounts in the registry.
        
        Returns:
            int: Number of accounts
        """
        return len(self.accounts)
