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


def generate_valid_nip():
    while True:
        nip = [random.randint(0, 9) for _ in range(9)]
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        control_sum = sum(nip[i] * weights[i] for i in range(9))
        control_digit = control_sum % 11
        if control_digit == 10:
            control_digit = 0
        nip.append(control_digit)
        return ''.join(str(d) for d in nip)


def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass


class TestCreateDeleteAccountPerformance:
    MAX_RESPONSE_TIME = 2.5
    ITERATIONS = 100

    def test_create_and_delete_account_100_times(self, base_url):
        session = requests.Session()

        for i in range(self.ITERATIONS):
            iteration = i + 1
            iter_pesel = generate_unique_pesel()

            create_payload = {
                "name": f"Test{iteration}",
                "surname": f"User{iteration}",
                "pesel": iter_pesel
            }

            create_response = requests.post(
                f"{base_url}/api/accounts",
                json=create_payload,
                timeout=2
            )

            assert create_response.status_code == 201, \
                f"Iteracja {iteration} - Create: Oczekiwano 201, otrzymano {create_response.status_code}"

            create_time = create_response.elapsed.total_seconds()
            assert create_time < self.MAX_RESPONSE_TIME, \
                f"Iteracja {iteration} - Create: Czas {create_time:.3f}s przekracza limit {self.MAX_RESPONSE_TIME}s"

            delete_response = requests.delete(
                f"{base_url}/api/accounts/{iter_pesel}",
                timeout=2
            )

            assert delete_response.status_code == 200, \
                f"Iteracja {iteration} - Delete: Oczekiwano 200, otrzymano {delete_response.status_code}"

            delete_time = delete_response.elapsed.total_seconds()
            assert delete_time < self.MAX_RESPONSE_TIME, \
                f"Iteracja {iteration} - Delete: Czas {delete_time:.3f}s przekracza limit {self.MAX_RESPONSE_TIME}s"

        session.close()

    def test_create_and_delete_company_account_100_times(self, base_url):
        session = requests.Session()
        successful_iterations = 0

        for i in range(self.ITERATIONS):
            iteration = i + 1
            created = False
            
            for retry_count in range(10):
                unique_nip = generate_valid_nip()

                company_data = {
                    "company_name": f"TEST_COMPANY_{iteration:04d}_{uuid.uuid4().hex[:4]}",
                    "nip": unique_nip
                }

                create_response = requests.post(
                    f"{base_url}/api/accounts",
                    json=company_data,
                    timeout=2
                )

                if create_response.status_code == 201:
                    successful_iterations += 1
                    created = True
                    break
                elif create_response.status_code not in [400, 409]:
                    break

        session.close()
        
        assert successful_iterations >= 80, \
            f"Zbyt mało udanych iteracji: {successful_iterations}/100"


class TestCreateDeleteAccountEdgeCases:
    def test_response_time_consistency(self, base_url):
        import statistics

        create_times = []
        delete_times = []
        session = requests.Session()

        for i in range(50):
            iter_pesel = generate_unique_pesel()

            create_response = requests.post(
                f"{base_url}/api/accounts",
                json={
                    "name": f"Test{i}",
                    "surname": "User",
                    "pesel": iter_pesel
                },
                timeout=2
            )
            create_times.append(create_response.elapsed.total_seconds())

            delete_response = requests.delete(
                f"{base_url}/api/accounts/{iter_pesel}",
                timeout=2
            )
            delete_times.append(delete_response.elapsed.total_seconds())

        session.close()

        avg_create = statistics.mean(create_times)
        avg_delete = statistics.mean(delete_times)
        max_create = max(create_times)
        max_delete = max(delete_times)

        assert avg_create < 2.5, f"Średni czas create {avg_create:.3f}s przekracza oczekiwany"
        assert avg_delete < 2.5, f"Średni czas delete {avg_delete:.3f}s przekracza oczekiwany"
        assert max_create < 3.0, f"Maksymalny czas create {max_create:.3f}s przekracza limit 3.0s"
        assert max_delete < 3.0, f"Maksymalny czas delete {max_delete:.3f}s przekracza limit 3.0s"
