from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

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
