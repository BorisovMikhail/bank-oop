from dataclasses import dataclass


@dataclass
class Account:
    id: int
    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[int, Account] = {}

    def open_account(self, account_id: int, owner: str, initial_balance: float = 0.0) -> Account:
        if account_id in self._accounts:
            raise ValueError(f"Account {account_id} already exists")
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")

        account = Account(id=account_id, owner=owner, balance=initial_balance)
        self._accounts[account_id] = account
        return account

    def get_account(self, account_id: int) -> Account:
        try:
            return self._accounts[account_id]
        except KeyError as exc:
            raise KeyError(f"Account {account_id} not found") from exc

