from flask import Flask, request, jsonify
from src.registry import AccountsRegistry
from src.account import Account, InsufficientFunds
from src.mongo_repository import MongoAccountsRepository
import os

app = Flask(__name__)
registry = AccountsRegistry()
mongo_repository = None


def get_mongo_repository():
    global mongo_repository
    if mongo_repository is None:
        mongo_repository = MongoAccountsRepository()
    return mongo_repository


def skip_mf_validation():
    return os.environ.get('SKIP_MF_VALIDATION', '').lower() in ('true', '1', 'yes')


@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Żądanie utworzenia konta: {data}")
    try:
        # Validate input data
        is_company = "company_name" in data or "nip" in data
        is_personal = "name" in data or "surname" in data or "pesel" in data
        
        if is_company:
            # Company account validation
            if not data.get("company_name") or not data.get("nip"):
                return jsonify({"error": "Company account requires company_name and nip"}), 400
        elif is_personal:
            # Personal account validation
            if not data.get("name") or not data.get("surname") or not data.get("pesel"):
                return jsonify({"error": "Personal account requires name, surname, and pesel"}), 400
        else:
            return jsonify({"error": "Invalid account data"}), 400
        
        account_data = {
            "first_name": data.get("name"),
            "last_name": data.get("surname"),
            "pesel": data.get("pesel"),
            "company_name": data.get("company_name"),
            "nip": data.get("nip"),
            "skip_mf_validation": True  # Always skip MF validation in API
        }
        account_data = {k: v for k, v in account_data.items() if v is not None and v is not False}
        account = Account(**account_data)
        
        # Additional validation: check if account was created with valid pesel/nip
        if not is_company and account.pesel == "Invalid":
            return jsonify({"error": "Invalid pesel format"}), 400
        if is_company and account.nip == "Invalid":
            return jsonify({"error": "Invalid nip format"}), 400
        
        registry.add_account(account)
        return jsonify({"message": "Konto utworzone"}), 201
    except ValueError as e:
        if "already exists" in str(e):
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400


@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Żądanie pobrania wszystkich kont")
    accounts = registry.get_all_accounts()
    accounts_data = [{"name": acc.first_name, "surname": acc.last_name, "pesel": acc.pesel, "balance": acc.balance} for acc in accounts]
    return jsonify(accounts_data), 200


@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Żądanie policzenia kont")
    count = registry.count_accounts()
    return jsonify({"count": count}), 200


@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    print(f"Żądanie pobrania konta o peselu: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Konto nie znalezione"}), 404
    account_data = {"name": account.first_name, "surname": account.last_name, "pesel": account.pesel, "balance": account.balance}
    return jsonify(account_data), 200


@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    print(f"Żądanie aktualizacji konta o peselu: {pesel}")
    data = request.get_json()
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Konto nie znalezione"}), 404
    first_name = data.get("name")
    last_name = data.get("surname")
    registry.update_account(pesel, first_name, last_name)
    return jsonify({"message": "Konto zaktualizowane"}), 200


@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    print(f"Żądanie usunięcia konta o peselu: {pesel}")
    success = registry.delete_account(pesel)
    if not success:
        return jsonify({"error": "Konto nie znalezione"}), 404
    return jsonify({"message": "Konto usunięte"}), 200


@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer_money(pesel):
    print(f"Żądanie przelewu dla peselu: {pesel}")
    data = request.get_json()
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Konto nie znalezione"}), 404
    transfer_type = data.get("type")
    if transfer_type not in ["incoming", "outgoing", "express"]:
        return jsonify({"error": "Niepoprawny typ przelewu. Musi być: incoming, outgoing lub express"}), 400
    try:
        amount = float(data.get("amount"))
        if amount <= 0:
            return jsonify({"error": "Kwota musi być dodatnia"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Niepoprawna kwota"}), 400
    try:
        if transfer_type == "incoming":
            account.receive_transfer(amount)
        elif transfer_type == "outgoing":
            account.send_transfer(amount)
        elif transfer_type == "express":
            account.send_express_transfer(amount)
        return jsonify({
            "message": "Przelew wykonany pomyślnie",
            "balance": account.balance
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except InsufficientFunds as e:
        return jsonify({"error": "Niewystarczające środki"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 422


@app.route("/api/accounts/save", methods=['POST'])
def save_accounts():
    print("Żądanie zapisania kont do bazy")
    try:
        accounts = registry.get_all_accounts()
        success = get_mongo_repository().save_all(accounts)
        if success:
            return jsonify({"message": f"Zapisano {len(accounts)} kont do bazy danych"}), 200
        else:
            return jsonify({"error": "Nie udało się zapisać kont do bazy danych"}), 500
    except Exception as e:
        print(f"Błąd zapisywania kont: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/accounts/load", methods=['POST'])
def load_accounts():
    print("Żądanie ładowania kont z bazy")
    try:
        registry.accounts = []

        account_dicts = get_mongo_repository().load_all()

        for acc_dict in account_dicts:
            account = Account(
                first_name=acc_dict.get("first_name"),
                last_name=acc_dict.get("last_name"),
                pesel=acc_dict.get("pesel"),
                company_name=acc_dict.get("company_name"),
                nip=acc_dict.get("nip"),
                skip_mf_validation=True
            )
            account.balance = acc_dict.get("balance", 0.0)
            account.history = acc_dict.get("history", [])
            registry.add_account(account)

        return jsonify({
            "message": f"Załadowano {len(account_dicts)} kont z bazy danych",
            "count": len(account_dicts)
        }), 200
    except Exception as e:
        print(f"Błąd ładowania kont: {e}")
        return jsonify({"error": str(e)}), 500
