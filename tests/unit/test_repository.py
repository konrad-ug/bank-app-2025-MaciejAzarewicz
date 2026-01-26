import pytest
from unittest.mock import Mock, MagicMock
from src.mongo_repository import MongoAccountsRepository
from src.account import Account


class TestMongoAccountsRepository:

    @pytest.fixture
    def mock_accounts(self):
        account1 = Mock(spec=Account)
        account1.first_name = "Jan"
        account1.last_name = "Kowalski"
        account1.pesel = "90050512345"
        account1.balance = 100.0
        account1.history = [100.0]
        account1.company_name = None
        account1.nip = "Invalid"

        account2 = Mock(spec=Account)
        account2.first_name = "Anna"
        account2.last_name = "Nowak"
        account2.pesel = "85050567890"
        account2.balance = 200.0
        account2.history = [200.0]
        account2.company_name = None
        account2.nip = "Invalid"

        return [account1, account2]

    @pytest.fixture
    def repository_with_mock_collection(self, mocker):
        mock_collection = mocker.Mock()
        mock_mongo_client = mocker.Mock()
        mock_db = mocker.Mock()
        mock_db.__getitem__ = mocker.Mock(return_value=mock_collection)
        mock_mongo_client.__getitem__ = mocker.Mock(return_value=mock_db)

        mocker.patch('src.mongo_repository.MongoClient', return_value=mock_mongo_client)

        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        repo._db = mock_db
        return repo, mock_collection

    def test_save_all_clears_collection_first(self, repository_with_mock_collection, mock_accounts):
        repo, mock_collection = repository_with_mock_collection

        result = repo.save_all(mock_accounts)

        mock_collection.delete_many.assert_called_once()
        assert result is True

    def test_save_all_inserts_all_accounts(self, repository_with_mock_collection, mock_accounts):
        repo, mock_collection = repository_with_mock_collection

        repo.save_all(mock_accounts)

        assert mock_collection.update_one.call_count == 2

    def test_save_all_handles_empty_list(self, repository_with_mock_collection):
        repo, mock_collection = repository_with_mock_collection

        result = repo.save_all([])

        mock_collection.delete_many.assert_called_once()
        assert result is True

    def test_save_all_returns_true_on_success(self, repository_with_mock_collection, mock_accounts):
        repo, mock_collection = repository_with_mock_collection

        result = repo.save_all(mock_accounts)

        assert result is True

    def test_save_all_returns_false_on_error(self, mocker, mock_accounts):
        mock_collection = mocker.Mock()
        mock_collection.delete_many.side_effect = Exception("Database error")

        mock_mongo_client = mocker.Mock()
        mock_db = mocker.Mock()
        mock_db.__getitem__ = mocker.Mock(return_value=mock_collection)
        mock_mongo_client.__getitem__ = mocker.Mock(return_value=mock_db)

        mocker.patch('src.mongo_repository.MongoClient', return_value=mock_mongo_client)

        repo = MongoAccountsRepository()
        repo._collection = mock_collection

        result = repo.save_all(mock_accounts)

        assert result is False

    def test_load_all_returns_list_of_accounts(self, repository_with_mock_collection, mock_accounts):
        repo, mock_collection = repository_with_mock_collection

        mock_cursor = [
            {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "pesel": "90050512345",
                "balance": 100.0,
                "history": [100.0],
                "company_name": None,
                "nip": "Invalid",
                "_id": "mock_id_1"
            },
            {
                "first_name": "Anna",
                "last_name": "Nowak",
                "pesel": "85050567890",
                "balance": 200.0,
                "history": [200.0],
                "company_name": None,
                "nip": "Invalid",
                "_id": "mock_id_2"
            }
        ]
        mock_collection.find.return_value = mock_cursor

        result = repo.load_all()

        assert len(result) == 2
        assert result[0]["pesel"] == "90050512345"
        assert result[1]["pesel"] == "85050567890"
        assert "_id" not in result[0]

    def test_load_all_returns_empty_list_on_error(self, mocker):
        mock_collection = mocker.Mock()
        mock_collection.find.side_effect = Exception("Database error")

        mock_mongo_client = mocker.Mock()
        mock_db = mocker.Mock()
        mock_db.__getitem__ = mocker.Mock(return_value=mock_collection)
        mock_mongo_client.__getitem__ = mocker.Mock(return_value=mock_db)

        mocker.patch('src.mongo_repository.MongoClient', return_value=mock_mongo_client)

        repo = MongoAccountsRepository()
        repo._collection = mock_collection

        result = repo.load_all()

        assert result == []

    def test_load_all_handles_empty_collection(self, repository_with_mock_collection):
        repo, mock_collection = repository_with_mock_collection

        mock_collection.find.return_value = []

        result = repo.load_all()

        assert result == []
