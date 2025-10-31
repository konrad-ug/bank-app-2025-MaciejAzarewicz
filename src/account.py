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

