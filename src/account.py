def getpeseldate(pesel):
    rok = int(pesel[0:2])
    miesiac = int(pesel[2:4])
    dzien = int(pesel[4:6])
    if (miesiac > 20):
        miesiac = miesiac - 20
        rok = 2000 + rok
    else:
        rok = 1900 + rok
    return [dzien,miesiac,rok]
class Account:
    def __init__(self, first_name, last_name, pesel, kod):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0
        if (len(str(pesel)) != 11):
            self.pesel = "Invalid"
        else:
            self.pesel = pesel
        kod = kod.split("_")
        if(kod[0]=="PROM" and len(kod[1])==3 and getpeseldate(str(pesel))[2]>1960):
            self.balance += 50
