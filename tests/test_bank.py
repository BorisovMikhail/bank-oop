import pytest

from src.bank import Account, Bank


def test_account_deposit_increases_balance() -> None:
    account = Account(id=1, owner="Mikhail", balance=100.0)

    new_balance = account.deposit(50.0)

    assert new_balance == 150.0
    assert account.balance == 150.0


def test_account_deposit_non_positive_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=100.0)

    with pytest.raises(ValueError, match="positive"):
        account.deposit(0)


def test_account_withdraw_decreases_balance() -> None:
    account = Account(id=1, owner="Mikhail", balance=100.0)

    new_balance = account.withdraw(40.0)

    assert new_balance == 60.0
    assert account.balance == 60.0


def test_account_withdraw_non_positive_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=100.0)

    with pytest.raises(ValueError, match="positive"):
        account.withdraw(-1)


def test_account_withdraw_over_balance_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=100.0)

    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(200.0)


def test_bank_open_and_get_account() -> None:
    bank = Bank()

    created = bank.open_account(account_id=10, owner="Alice", initial_balance=25.0)
    loaded = bank.get_account(10)

    assert created is loaded
    assert loaded.id == 10
    assert loaded.owner == "Alice"
    assert loaded.balance == 25.0


def test_bank_open_account_duplicate_id_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=10, owner="Alice")

    with pytest.raises(ValueError, match="already exists"):
        bank.open_account(account_id=10, owner="Bob")


def test_bank_get_unknown_account_raises() -> None:
    bank = Bank()

    with pytest.raises(KeyError, match="not found"):
        bank.get_account(999)

