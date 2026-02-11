from datetime import datetime

from src.bank import Bank


def test_bank_save_and_load_retains_data(tmp_path):
    # 1. Подготовка: создаем банк с данными
    json_file = tmp_path / "bank.json"
    bank = Bank()
    
    # Открываем счета
    bank.open_account(1, "Alice", 100.00)
    bank.open_account(2, "Bob", 50.00)
    
    # Делаем перевод (чтобы была транзакция с timestamp)
    bank.transfer(1, 2, 25.00)
    
    # 2. Сохраняем данные в файл
    bank.save_to_file(json_file)
    
    # 3. Создаем НОВЫЙ банк и загружаем данные
    new_bank = Bank()
    new_bank.load_from_file(json_file)
    
    # 4. Проверяем, что все сохранилось
    # Счета
    alice = new_bank.get_account(1)
    bob = new_bank.get_account(2)
    
    assert alice.balance == 7500  # 75.00 * 100
    assert bob.balance == 7500    # 75.00 * 100
    assert alice.owner == "Alice"
    
    # Транзакции
    transactions = new_bank.get_transactions()
    assert len(transactions) == 1
    
    tx = transactions[0]
    assert tx.from_id == 1
    assert tx.to_id == 2
    assert tx.amount == 2500
    
    # Самое важное: проверка, что timestamp вернулся как объект, а не строка
    assert isinstance(tx.timestamp, datetime)
