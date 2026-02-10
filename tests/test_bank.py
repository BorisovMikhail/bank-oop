from datetime import datetime, timezone

import pytest

from src.bank import Account, Bank, Transaction


def test_account_deposit_increases_balance() -> None:
    account = Account(id=1, owner="Mikhail", balance=10_000)

    new_balance = account.deposit(50.00)

    assert new_balance == 15_000
    assert account.balance == 15_000


def test_account_deposit_non_positive_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=10_000)

    with pytest.raises(ValueError, match="positive"):
        account.deposit(0.00)


def test_account_deposit_from_string_amount() -> None:
    account = Account(id=1, owner="Mikhail", balance=0)

    new_balance = account.deposit("1.50")

    assert new_balance == 150
    assert account.balance == 150


def test_account_withdraw_decreases_balance() -> None:
    account = Account(id=1, owner="Mikhail", balance=10_000)

    new_balance = account.withdraw(40.00)

    assert new_balance == 6_000
    assert account.balance == 6_000


def test_account_withdraw_non_positive_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=10_000)

    with pytest.raises(ValueError, match="positive"):
        account.withdraw(-1.00)


def test_account_withdraw_over_balance_raises() -> None:
    account = Account(id=1, owner="Mikhail", balance=10_000)

    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(200.00)


def test_bank_open_and_get_account() -> None:
    bank = Bank()

    created = bank.open_account(account_id=10, owner="Alice", initial_balance=25.00)
    loaded = bank.get_account(10)

    assert created is loaded
    assert loaded.id == 10
    assert loaded.owner == "Alice"
    assert loaded.balance == 2_500


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
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.00)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.00)

    before_transfer = datetime.now(timezone.utc)
    transaction = bank.transfer(from_id=1, to_id=2, amount=30.00)
    after_transfer = datetime.now(timezone.utc)

    assert isinstance(transaction, Transaction)
    assert transaction.from_id == 1
    assert transaction.to_id == 2
    assert transaction.amount == 3_000
    assert transaction.timestamp.tzinfo is not None
    assert before_transfer <= transaction.timestamp <= after_transfer
    assert bank.get_account(1).balance == 7_000
    assert bank.get_account(2).balance == 5_000
    assert bank.get_transactions() == [transaction]


def test_bank_transfer_non_positive_amount_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.00)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.00)

    with pytest.raises(ValueError, match="positive"):
        bank.transfer(from_id=1, to_id=2, amount=0.00)


def test_bank_transfer_insufficient_funds_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=10.00)
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.00)

    with pytest.raises(ValueError, match="Insufficient funds"):
        bank.transfer(from_id=1, to_id=2, amount=30.00)

    assert bank.get_account(1).balance == 1_000
    assert bank.get_account(2).balance == 2_000
    assert bank.get_transactions() == []


def test_bank_transfer_unknown_sender_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=2, owner="Bob", initial_balance=20.00)

    with pytest.raises(KeyError, match="not found"):
        bank.transfer(from_id=1, to_id=2, amount=5.00)


def test_bank_transfer_unknown_receiver_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.00)

    with pytest.raises(KeyError, match="not found"):
        bank.transfer(from_id=1, to_id=2, amount=5.00)

    assert bank.get_account(1).balance == 10_000
    assert bank.get_transactions() == []


def test_bank_transfer_to_same_account_raises() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.00)

    with pytest.raises(ValueError, match="same account"):
        bank.transfer(from_id=1, to_id=1, amount=10.00)


def test_bank_get_account_history_returns_only_related_transactions() -> None:
    bank = Bank()
    bank.open_account(account_id=1, owner="Alice", initial_balance=100.00)
    bank.open_account(account_id=2, owner="Bob", initial_balance=50.00)
    bank.open_account(account_id=3, owner="Charlie", initial_balance=40.00)

    tx_1 = bank.transfer(from_id=1, to_id=2, amount=10.00)
    tx_2 = bank.transfer(from_id=2, to_id=1, amount=5.00)
    tx_3 = bank.transfer(from_id=2, to_id=3, amount=7.00)

    history_for_1 = bank.get_account_history(1)
    history_for_3 = bank.get_account_history(3)

    assert history_for_1 == [tx_1, tx_2]
    assert history_for_3 == [tx_3]


def test_bank_get_account_history_unknown_account_raises() -> None:
    bank = Bank()

    with pytest.raises(KeyError, match="not found"):
        bank.get_account_history(404)
