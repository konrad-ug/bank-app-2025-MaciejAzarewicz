class AccountsRegistry:
    def __init__(self):
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def find_account_by_pesel(self, pesel):
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return None

    def get_all_accounts(self):
        return self.accounts

    def count_accounts(self):
        return len(self.accounts)

    def update_account(self, pesel, first_name=None, last_name=None):
        account = self.find_account_by_pesel(pesel)
        if account is None:
            return False
        if first_name is not None:
            account.first_name = first_name
        if last_name is not None:
            account.last_name = last_name
        return True

    def delete_account(self, pesel):
        account = self.find_account_by_pesel(pesel)
        if account is None:
            return False
        self.accounts.remove(account)
        return True
