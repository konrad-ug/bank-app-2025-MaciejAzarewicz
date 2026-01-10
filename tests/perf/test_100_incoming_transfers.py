import pytest
import requests
import time
import uuid
import random


def generate_unique_pesel():
    timestamp = str(int(time.time() * 1000000))[-4:]
    random_part = str(random.randint(10000, 99999))
    uuid_part = str(uuid.uuid4().int)[:2]
    return f"{timestamp}{random_part}{uuid_part}"


def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass


class TestIncomingTransfersPerformance:
    MAX_RESPONSE_TIME = 0.5
    TRANSFER_COUNT = 100
    TRANSFER_AMOUNT = 10

    def test_100_incoming_transfers_performance_and_balance(self, base_url):
        session = requests.Session()
        unique_pesel = generate_unique_pesel()

        delete_account_safely(base_url, unique_pesel)

        create_payload = {
            "name": "PerformanceTest",
            "surname": "User",
            "pesel": unique_pesel
        }

        create_response = requests.post(
            f"{base_url}/api/accounts",
            json=create_payload,
            timeout=2
        )

        assert create_response.status_code == 201, \
            f"Create account: Oczekiwano 201, otrzymano {create_response.status_code}"

        create_time = create_response.elapsed.total_seconds()
        assert create_time < self.MAX_RESPONSE_TIME, \
            f"Create: Czas {create_time:.3f}s przekracza limit {self.MAX_RESPONSE_TIME}s"

        failed_transfers = []
        expected_balance = self.TRANSFER_COUNT * self.TRANSFER_AMOUNT

        for i in range(self.TRANSFER_COUNT):
            iteration = i + 1

            transfer_payload = {
                "type": "incoming",
                "amount": self.TRANSFER_AMOUNT
            }

            transfer_response = requests.post(
                f"{base_url}/api/accounts/{unique_pesel}/transfer",
                json=transfer_payload,
                timeout=2
            )

            if transfer_response.status_code != 200:
                failed_transfers.append({
                    "iteration": iteration,
                    "status_code": transfer_response.status_code,
                    "response": transfer_response.text
                })

            transfer_time = transfer_response.elapsed.total_seconds()
            assert transfer_time < self.MAX_RESPONSE_TIME, \
                f"Transfer {iteration}: Czas {transfer_time:.3f}s przekracza limit {self.MAX_RESPONSE_TIME}s"

        if failed_transfers:
            pytest.fail(
                f"Nieudane transfery ({len(failed_transfers)}/{self.TRANSFER_COUNT}):\n"
                f"{failed_transfers[:5]}"
            )

        balance_response = requests.get(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )

        assert balance_response.status_code == 200, \
            f"Get account: Oczekiwano 200, otrzymano {balance_response.status_code}"

        balance_data = balance_response.json()
        actual_balance = balance_data.get("balance", 0)

        assert actual_balance == expected_balance, \
            f"Niepoprawne saldo: oczekiwano {expected_balance}, otrzymano {actual_balance}"

        delete_response = requests.delete(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )

        assert delete_response.status_code == 200, \
            f"Delete: Oczekiwano 200, otrzymano {delete_response.status_code}"

        session.close()

    def test_100_incoming_transfers_different_amounts(self, base_url):
        session = requests.Session()
        unique_pesel = generate_unique_pesel()

        delete_account_safely(base_url, unique_pesel)

        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={
                "name": "PerformanceTest",
                "surname": "User",
                "pesel": unique_pesel
            },
            timeout=2
        )
        assert create_response.status_code == 201

        transfer_amounts = [1, 5, 10, 25, 50, 100, 1, 5, 10, 25]
        expected_total = sum(transfer_amounts)

        for i, amount in enumerate(transfer_amounts):
            transfer_response = requests.post(
                f"{base_url}/api/accounts/{unique_pesel}/transfer",
                json={"type": "incoming", "amount": amount},
                timeout=2
            )

            assert transfer_response.status_code == 200, \
                f"Transfer {i + 1} (kwota {amount}): Oczekiwano 200, otrzymano {transfer_response.status_code}"

            transfer_time = transfer_response.elapsed.total_seconds()
            assert transfer_time < self.MAX_RESPONSE_TIME, \
                f"Transfer {i + 1}: Czas {transfer_time:.3f}s przekracza limit"

        balance_response = requests.get(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )

        assert balance_response.status_code == 200
        actual_balance = balance_response.json().get("balance", 0)
        assert actual_balance == expected_total, \
            f"Niepoprawne saldo: oczekiwano {expected_total}, otrzymano {actual_balance}"

        delete_account_safely(base_url, unique_pesel)
        session.close()


class TestMixedTransfersPerformance:
    MAX_RESPONSE_TIME = 0.5

    def test_mixed_transfers_performance(self, base_url):
        session = requests.Session()
        unique_pesel = generate_unique_pesel()

        delete_account_safely(base_url, unique_pesel)

        create_response = requests.post(
            f"{base_url}/api/accounts",
            json={"name": "PerformanceTest", "surname": "User", "pesel": unique_pesel},
            timeout=2
        )
        assert create_response.status_code == 201

        initial_response = requests.post(
            f"{base_url}/api/accounts/{unique_pesel}/transfer",
            json={"type": "incoming", "amount": 1000},
            timeout=2
        )
        assert initial_response.status_code == 200

        for i in range(50):
            response = requests.post(
                f"{base_url}/api/accounts/{unique_pesel}/transfer",
                json={"type": "outgoing", "amount": 5},
                timeout=2
            )
            assert response.status_code == 200
            assert response.elapsed.total_seconds() < self.MAX_RESPONSE_TIME

        for i in range(20):
            response = requests.post(
                f"{base_url}/api/accounts/{unique_pesel}/transfer",
                json={"type": "express", "amount": 10},
                timeout=2
            )
            assert response.status_code == 200
            assert response.elapsed.total_seconds() < self.MAX_RESPONSE_TIME

        balance_response = requests.get(
            f"{base_url}/api/accounts/{unique_pesel}",
            timeout=2
        )

        expected_balance = 1000 - (50 * 5) - (20 * 10) - (20 * 1)
        actual_balance = balance_response.json().get("balance", 0)
        assert actual_balance == expected_balance, \
            f"Niepoprawne saldo: oczekiwano {expected_balance}, otrzymano {actual_balance}"

        delete_account_safely(base_url, unique_pesel)
        session.close()
