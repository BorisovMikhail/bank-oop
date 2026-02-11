from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
import json
from pathlib import Path

MoneyInput = int | float | str | Decimal


def _to_cents(amount: MoneyInput, *, field_name: str) -> int:
    if isinstance(amount, bool):
        raise TypeError(f"{field_name} must be a valid number")

    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise TypeError(f"{field_name} must be a valid number") from exc

    if not decimal_amount.is_finite():
        raise ValueError(f"{field_name} must be a finite number")
    if decimal_amount.as_tuple().exponent < -2:
        raise ValueError(f"{field_name} must have at most 2 decimal places")

    return int(decimal_amount * 100)


@dataclass
class Account:
    id: int
    owner: str
    balance: int = 0

    def _deposit_cents(self, amount_cents: int) -> int:
        if amount_cents <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount_cents
        return self.balance

    def deposit(self, amount: MoneyInput) -> int:
        amount_cents = _to_cents(amount, field_name="Deposit amount")
        return self._deposit_cents(amount_cents)

    def _withdraw_cents(self, amount_cents: int) -> int:
        if amount_cents <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount_cents > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount_cents
        return self.balance

    def withdraw(self, amount: MoneyInput) -> int:
        amount_cents = _to_cents(amount, field_name="Withdraw amount")
        return self._withdraw_cents(amount_cents)


@dataclass
class Transaction:
    from_id: int
    to_id: int
    amount: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[int, Account] = {}
        self._transactions: list[Transaction] = []

    def open_account(self, account_id: int, owner: str, initial_balance: MoneyInput = 0) -> Account:
        if account_id in self._accounts:
            raise ValueError(f"Account {account_id} already exists")

        initial_balance_cents = _to_cents(initial_balance, field_name="Initial balance")
        if initial_balance_cents < 0:
            raise ValueError("Initial balance cannot be negative")

        account = Account(id=account_id, owner=owner, balance=initial_balance_cents)
        self._accounts[account_id] = account
        return account

    def get_account(self, account_id: int) -> Account:
        try:
            return self._accounts[account_id]
        except KeyError as exc:
            raise KeyError(f"Account {account_id} not found") from exc

    def transfer(self, from_id: int, to_id: int, amount: MoneyInput) -> Transaction:
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same account")

        amount_cents = _to_cents(amount, field_name="Transfer amount")
        if amount_cents <= 0:
            raise ValueError("Transfer amount must be positive")

        from_account = self.get_account(from_id)
        to_account = self.get_account(to_id)

        from_account._withdraw_cents(amount_cents)
        to_account._deposit_cents(amount_cents)

        transaction = Transaction(from_id=from_id, to_id=to_id, amount=amount_cents)
        self._transactions.append(transaction)
        return transaction

    def get_transactions(self) -> list[Transaction]:
        return self._transactions.copy()

    def get_account_history(self, account_id: int) -> list[Transaction]:
        self.get_account(account_id)
        return [
            transaction
            for transaction in self._transactions
            if transaction.from_id == account_id or transaction.to_id == account_id
        ]

    def save_to_file(self, filename: str | Path) -> None:
        data = {
            "accounts": {
                str(account_id): {
                    "id": account.id,
                    "owner": account.owner,
                    "balance": account.balance,
                }
                for account_id, account in self._accounts.items()
            },
            "transactions": [
                {
                    "from_id": transaction.from_id,
                    "to_id": transaction.to_id,
                    "amount": transaction.amount,
                    "timestamp": transaction.timestamp.isoformat(),
                }
                for transaction in self._transactions
            ],
        }

        file_path = Path(filename)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load_from_file(self, filename: str | Path) -> None:
        file_path = Path(filename)
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            accounts: dict[int, Account] = {}
            for account_key, account_data in data.get("accounts", {}).items():
                account_id = int(account_key)
                accounts[account_id] = Account(
                    id=int(account_data.get("id", account_id)),
                    owner=account_data["owner"],
                    balance=int(account_data["balance"]),
                )

            transactions: list[Transaction] = []
            for transaction_data in data.get("transactions", []):
                transactions.append(
                    Transaction(
                        from_id=int(transaction_data["from_id"]),
                        to_id=int(transaction_data["to_id"]),
                        amount=int(transaction_data["amount"]),
                        timestamp=datetime.fromisoformat(transaction_data["timestamp"]),
                    )
                )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise IOError(f"Error loading data from {file_path}: invalid file format.") from exc

        self._accounts = accounts
        self._transactions = transactions
