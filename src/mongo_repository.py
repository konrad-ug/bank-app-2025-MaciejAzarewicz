from pymongo import MongoClient
from typing import List, Optional
from .repository import AccountsRepository


class MongoAccountsRepository(AccountsRepository):

    def __init__(self, connection_string: Optional[str] = None, database_name: str = "bank_app"):
        if connection_string is None:
            connection_string = "mongodb://localhost:27017/"
        self._client = MongoClient(connection_string)
        self._db = self._client[database_name]
        self._collection = self._db["accounts"]

    def save_all(self, accounts: list) -> bool:
        try:
            self._collection.delete_many({})

            for account in accounts:
                account_dict = self._account_to_dict(account)
                self._collection.update_one(
                    {"pesel": account.pesel},
                    {"$set": account_dict},
                    upsert=True
                )
            return True
        except Exception as e:
            print(f"Błąd zapisywania kont do MongoDB: {e}")
            return False

    def load_all(self) -> list:
        try:
            accounts = []
            for doc in self._collection.find({}):
                if "_id" in doc:
                    del doc["_id"]
                accounts.append(doc)
            return accounts
        except Exception as e:
            print(f"Błąd ładowania kont z MongoDB: {e}")
            return []

    def _account_to_dict(self, account) -> dict:
        return {
            "first_name": account.first_name,
            "last_name": account.last_name,
            "pesel": account.pesel,
            "balance": account.balance,
            "history": account.history,
            "company_name": account.company_name,
            "nip": account.nip
        }

    def close(self):
        self._client.close()
