from dataclasses import dataclass


@dataclass
class Account:
    id: int
    owner: str
    balance: int = 0

    def deposit(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance


@dataclass
class Transaction:
    from_id: int
    to_id: int
    amount: int


class Bank:
    def __init__(self) -> None:
        self._accounts: dict[int, Account] = {}
        self._transactions: list[Transaction] = []

    def open_account(self, account_id: int, owner: str, initial_balance: int = 0) -> Account:
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

    def transfer(self, from_id: int, to_id: int, amount: int) -> Transaction:
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same account")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        from_account = self.get_account(from_id)
        to_account = self.get_account(to_id)

        from_account.withdraw(amount)
        to_account.deposit(amount)

        transaction = Transaction(from_id=from_id, to_id=to_id, amount=amount)
        self._transactions.append(transaction)
        return transaction

    def get_transactions(self) -> list[Transaction]:
        return self._transactions.copy()
