from abc import ABC, abstractmethod
from typing import List


class AccountsRepository(ABC):

    @abstractmethod
    def save_all(self, accounts: list) -> bool:
        pass

    @abstractmethod
    def load_all(self) -> list:
        pass
