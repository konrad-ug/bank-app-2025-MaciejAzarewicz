from src.account import getpeseldate

def test_getpeseldate_1900s_branch():
    assert getpeseldate("99010100000") == [1, 1, 1999]
