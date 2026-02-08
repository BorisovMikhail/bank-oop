import pytest

from src.bank import Account, Bank, Transaction


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


def test_bank_transfer_moves_money_and_stores_transaction() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.0)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.0)

    transaction = bank.transfer(from_id=1, to_id=2, amount=30.0)

    assert isinstance(transaction, Transaction)
    assert transaction.from_id == 1
    assert transaction.to_id == 2
    assert transaction.amount == 30.0
    assert bank.get_account(1).balance == 70.0
    assert bank.get_account(2).balance == 50.0
    assert bank.get_transactions() == [transaction]


def test_bank_transfer_non_positive_amount_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.0)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.0)

    with pytest.raises(ValueError, match="positive"):
        bank.transfer(from_id=1, to_id=2, amount=0)


def test_bank_transfer_insufficient_funds_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=10.0)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.0)

    with pytest.raises(ValueError, match="Insufficient funds"):
        bank.transfer(from_id=1, to_id=2, amount=30.0)

    assert bank.get_account(1).balance == 10.0
    assert bank.get_account(2).balance == 20.0
    assert bank.get_transactions() == []


def test_bank_transfer_unknown_sender_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.0)

    with pytest.raises(KeyError, match="not found"):
        bank.transfer(from_id=1, to_id=2, amount=5.0)


def test_bank_transfer_unknown_receiver_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.0)

    with pytest.raises(KeyError, match="not found"):
        bank.transfer(from_id=1, to_id=2, amount=5.0)

    assert bank.get_account(1).balance == 100.0
    assert bank.get_transactions() == []


def test_bank_transfer_to_same_account_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.0)

    with pytest.raises(ValueError, match="same account"):
        bank.transfer(from_id=1, to_id=1, amount=10.0)
