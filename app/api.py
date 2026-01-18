from flask import Flask, request, jsonify
from src.registry import AccountsRegistry
from src.account import Account, InsufficientFunds
import os

app = Flask(__name__)
registry = AccountsRegistry()


def skip_mf_validation():
    return os.environ.get('SKIP_MF_VALIDATION', '').lower() in ('true', '1', 'yes')


@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    try:
        account_data = {
            "first_name": data.get("name"),
            "last_name": data.get("surname"), 
            "pesel": data.get("pesel"),
            "company_name": data.get("company_name"),
            "nip": data.get("nip"),
            "skip_mf_validation": skip_mf_validation()
        }
        account_data = {k: v for k, v in account_data.items() if v is not None and v is not False}
        account = Account(**account_data)
        registry.add_account(account)
        return jsonify({"message": "Account created"}), 201
    except ValueError as e:
        if "already exists" in str(e):
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400

@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.get_all_accounts()
    accounts_data = [{"name": acc.first_name, "surname": acc.last_name, "pesel": acc.pesel, "balance": acc.balance} for acc in accounts]
    return jsonify(accounts_data), 200

@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Get account count request received")
    count = registry.count_accounts()
    return jsonify({"count": count}), 200

@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    print(f"Get account by pesel request: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    account_data = {"name": account.first_name, "surname": account.last_name, "pesel": account.pesel, "balance": account.balance}
    return jsonify(account_data), 200

@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    print(f"Update account request: {pesel}")
    data = request.get_json()
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    first_name = data.get("name")
    last_name = data.get("surname")
    registry.update_account(pesel, first_name, last_name)
    return jsonify({"message": "Account updated"}), 200

@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    print(f"Delete account request: {pesel}")
    success = registry.delete_account(pesel)
    if not success:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"message": "Account deleted"}), 200

@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer_money(pesel):
    print(f"Transfer money request: {pesel}")
    data = request.get_json()
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    transfer_type = data.get("type")
    if transfer_type not in ["incoming", "outgoing", "express"]:
        return jsonify({"error": "Invalid transfer type. Must be: incoming, outgoing, or express"}), 400
    try:
        amount = float(data.get("amount"))
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400
    try:
        if transfer_type == "incoming":
            account.receive_transfer(amount)
        elif transfer_type == "outgoing":
            account.send_transfer(amount)
        elif transfer_type == "express":
            account.send_express_transfer(amount)
        return jsonify({
            "message": "Transfer completed successfully",
            "balance": account.balance
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except InsufficientFunds as e:
        return jsonify({"error": "InsufficientFunds"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 422
