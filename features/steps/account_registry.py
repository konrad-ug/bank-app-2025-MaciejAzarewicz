from behave import *
import requests

URL = "http://localhost:5000"


@step('Account registry is empty')
def clear_account_registry(context):
    response = requests.get(URL + "/api/accounts")
    accounts = response.json()
    for account in accounts:
        pesel = account["pesel"]
        requests.delete(URL + f"/api/accounts/{pesel}")


@step('I create an account using name: "{name}", last name: "{last_name}", pesel: "{pesel}"')
def create_account(context, name, last_name, pesel):
    json_body = {
        "name": f"{name}",
        "surname": f"{last_name}",
        "pesel": pesel
    }
    create_resp = requests.post(URL + "/api/accounts", json=json_body)
    assert create_resp.status_code == 201


@step('Number of accounts in registry equals: "{count}"')
def is_account_count_equal_to(context, count):
    response = requests.get(URL + "/api/accounts/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == int(count)


@step('Account with pesel "{pesel}" exists in registry')
def check_account_with_pesel_exists(context, pesel):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200
    data = response.json()
    assert data["pesel"] == pesel


@step('Account with pesel "{pesel}" does not exist in registry')
def check_account_with_pesel_does_not_exist(context, pesel):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 404


@when('I update "{field}" of account with pesel: "{pesel}" to "{value}"')
def update_field(context, field, pesel, value):
    if field not in ["name", "surname"]:
        raise ValueError(f"Invalid field: {field}. Must be 'name' or 'surname'.")
    json_body = {f"{field}": f"{value}"}
    response = requests.patch(URL + f"/api/accounts/{pesel}", json=json_body)
    assert response.status_code == 200


@then('Account with pesel "{pesel}" has "{field}" equal to "{value}"')
def field_equals_to(context, pesel, field, value):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200
    data = response.json()
    assert data[field] == value


@when('I delete account with pesel: "{pesel}"')
def delete_account(context, pesel):
    response = requests.delete(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200


# ========== TRANSFER STEPS ==========

@when('I make incoming transfer of "{amount}" to account with pesel: "{pesel}"')
@given('I make incoming transfer of "{amount}" to account with pesel: "{pesel}"')
def make_incoming_transfer(context, amount, pesel):
    json_body = {"type": "incoming", "amount": float(amount)}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.response = response


@when('I make outgoing transfer of "{amount}" from account with pesel: "{pesel}"')
@given('I make outgoing transfer of "{amount}" from account with pesel: "{pesel}"')
def make_outgoing_transfer(context, amount, pesel):
    json_body = {"type": "outgoing", "amount": float(amount)}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.response = response


@when('I make express transfer of "{amount}" from account with pesel: "{pesel}"')
@given('I make express transfer of "{amount}" from account with pesel: "{pesel}"')
def make_express_transfer(context, amount, pesel):
    json_body = {"type": "express", "amount": float(amount)}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.response = response


@then('Account with pesel "{pesel}" has balance equal to "{expected_balance}"')
def check_balance(context, pesel, expected_balance):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == float(expected_balance)


@then('Response status code should be "{status_code}"')
def check_status_code(context, status_code):
    assert hasattr(context, 'response'), "No response stored in context"
    assert context.response.status_code == int(status_code), \
        f"Expected {status_code}, got {context.response.status_code}. Response: {context.response.text}"