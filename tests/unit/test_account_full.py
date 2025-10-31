import pytest
from src.account import Account

def test_promo_applied_correctly():
    a = Account("J", "D", "05240811968", "PROM_111")
    assert a.balance == 50.0
    assert a.history == [50.0]

def test_no_promo_invalid_kod():
    a = Account("J", "D", "05240811968", "PR_111")
    assert a.balance == 0.0

def test_no_promo_invalid_pesel():
    a = Account("J", "D", "99999", "PROM_123")
    assert a.balance == 0.0

def test_getpeseldate_valid():
    from src.account import getpeseldate
    assert getpeseldate("05240811968") == [8, 4, 2005]

def test_getpeseldate_invalid():
    from src.account import getpeseldate
    assert getpeseldate("12") == [None, None, None]
    assert getpeseldate("abcdef") == [None, None, None]

def test_company_has_no_promo():
    a = Account(company_name="Firma", nip="1234567890", kod="PROM_123")
    assert a.balance == 0.0

def test_send_transfer_and_receive_transfer():
    a = Account("A", "B", "05240811968", "")
    a.deposit(100)
    a.send_transfer(40)
    a.receive_transfer(10)
    assert a.balance == 70

