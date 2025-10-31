from src.account import Account

def test_history_records_order():
    a = Account("A", "B", "05240811968", "PROM_123")
    a.deposit(100)
    a.withdraw(30)
    a.send_transfer(20)
    a.receive_transfer(50)
    assert a.history == [50.0, 100.0, -30.0, -20.0, 50.0]

def test_history_empty_initially():
    a = Account("A", "B", "05240811968", "")
    assert a.history == []

