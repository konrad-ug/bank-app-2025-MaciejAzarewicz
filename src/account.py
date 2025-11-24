def getpeseldate(pesel):
    try:
        s = str(pesel)
        if len(s) < 6:
            return [None, None, None]
        rok = int(s[0:2])
        miesiac = int(s[2:4])
        dzien = int(s[4:6])
    except Exception:
        return [None, None, None]
    if miesiac > 20:
        miesiac -= 20
        rok = 2000 + rok
    else:
        rok = 1900 + rok
    return [dzien, miesiac, rok]


class InsufficientFunds(Exception):
    pass


class Account:
    def __init__(self, first_name=None, last_name=None, pesel=None, kod=None, company_name=None, nip=None):
        self.first_name = first_name
        self.last_name = last_name
        self.company_name = None
        self.balance = 0.0
        self.pesel = "Invalid"
        self.nip = "Invalid"
        self.history = []

        if company_name:
            self.company_name = company_name
            if isinstance(nip, str) and len(nip) == 10 and nip.isdigit():
                self.nip = nip
        else:
            if isinstance(pesel, str) and len(pesel) == 11:
                self.pesel = pesel
        parts = []
        if isinstance(kod, str) and "_" in kod:
            parts = kod.split("_", 1)
        if parts and parts[0] == "PROM" and len(parts[1]) == 3 and self.pesel != "Invalid":
            year = getpeseldate(self.pesel)[2]
            if isinstance(year, int) and year > 1960:
                self.balance += 50.0
                self.history.append(round(50.0, 2))

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError
        amount_f = float(amount)
        self.balance += amount_f
        self.history.append(round(amount_f, 2))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError
        if amount > self.balance:
            raise InsufficientFunds
        amount_f = float(amount)
        self.balance -= amount_f
        self.history.append(round(-amount_f, 2))

    def send_transfer(self, amount):
        if amount <= 0:
            raise ValueError
        if amount > self.balance:
            raise InsufficientFunds
        amount_f = float(amount)
        self.balance -= amount_f
        self.history.append(round(-amount_f, 2))

    def receive_transfer(self, amount):
        if amount <= 0:
            raise ValueError
        amount_f = float(amount)
        self.balance += amount_f
        self.history.append(round(amount_f, 2))

    def send_express_transfer(self, amount):
        if amount <= 0:
            raise ValueError
        fee = 1.0 if not self.company_name else 5.0
        if amount > self.balance:
            raise InsufficientFunds
        new_balance = self.balance - float(amount) - float(fee)
        if new_balance < -fee:
            raise InsufficientFunds  # pragma: no cover
        self.balance = new_balance
        self.history.append(round(-float(amount), 2))
        self.history.append(round(-float(fee), 2))

    def submit_for_loan(self, amount):
        """
        Try to grant a personal loan of `amount`.
        Rules:
          - Only personal accounts (no company_name) are eligible.
          - Condition A: last 3 transactions are deposits (positive values).
          - Condition B: account has at least 5 transactions and sum(last 5) > amount.
        Behaviour:
          - If approved: increase balance by amount, append amount to history (rounded),
            return True.
          - If not approved: return False.
        Consistent with other methods, raise ValueError for non-positive amounts.
        """
        if amount <= 0:
            raise ValueError

        # business accounts are not eligible
        if self.company_name:
            return False

        # Condition A: last 3 transactions are deposits
        if len(self.history) >= 3 and all(x > 0 for x in self.history[-3:]):
            self.balance += float(amount)
            self.history.append(round(float(amount), 2))
            return True

        # Condition B: at least 5 transactions and sum(last 5) > amount
        if len(self.history) >= 5:
            if sum(self.history[-5:]) > float(amount):
                self.balance += float(amount)
                self.history.append(round(float(amount), 2))
                return True

        return False

    def take_loan(self, amount):
        """
        Try to grant a business loan of `amount`.
        Rules:
          - Only business accounts (company_name present) are eligible.
          - Condition A: balance >= 2 * amount
          - Condition B: at least one ZUS transfer (-1775) in history
        Behaviour:
          - If both conditions approved: increase balance by amount, 
            append amount to history (rounded), return True.
          - If not approved: return False (no changes).
        Raises ValueError for non-positive amounts.
        """
        if amount <= 0:
            raise ValueError

        # Only business accounts are eligible
        if not self.company_name:
            return False

        # Condition A: balance >= 2 * amount
        if self.balance < 2 * float(amount):
            return False

        # Condition B: at least one ZUS transfer (-1775) in history
        if -1775 not in self.history:
            return False

        # Both conditions met - approve loan
        self.balance += float(amount)
        self.history.append(round(float(amount), 2))
        return True
