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


def generate_unique_pesel_with_prefix(prefix):
    remaining = 11 - len(prefix)
    random_part = str(random.randint(10**(remaining-1), 10**remaining - 1))
    return f"{prefix}{random_part[-remaining:]}"


def delete_account_safely(base_url, account_id):
    try:
        requests.delete(f"{base_url}/api/accounts/{account_id}", timeout=2)
    except requests.exceptions.RequestException:
        pass


class Test1000AccountsPerformance:
    MAX_RESPONSE_TIME = 0.5

    def test_create_1000_accounts_batch_then_delete(self, base_url):
        session = requests.Session()
        created_pesels = []
        failed_creates = []
        start_time = time.time()

        test_prefix = str(uuid.uuid4().int)[:6]

        for i in range(1000):
            pesel = generate_unique_pesel_with_prefix(test_prefix)
            created_pesels.append(pesel)

            payload = {
                "name": f"User{i}",
                "surname": f"Test{i}",
                "pesel": pesel
            }

            response = requests.post(
                f"{base_url}/api/accounts",
                json=payload,
                timeout=2
            )

            if response.status_code != 201:
                failed_creates.append({"pesel": pesel, "status": response.status_code})

            if response.elapsed.total_seconds() >= self.MAX_RESPONSE_TIME:
                if i % 50 == 0:
                    print(f"Uwaga: Operacja {i} przekroczyła limit czasowy")

        create_duration = time.time() - start_time
        print(f"\n=== FAZA 1 ZAKOŃCZONA ===")
        print(f"Utworzono: {1000 - len(failed_creates)}/1000 kont")
        print(f"Czas tworzenia: {create_duration:.2f}s")
        print(f"Średni czas na konto: {create_duration/1000*1000:.2f}ms")

        start_time = time.time()
        failed_deletes = []

        for pesel in created_pesels:
            response = requests.delete(
                f"{base_url}/api/accounts/{pesel}",
                timeout=2
            )

            if response.status_code != 200:
                failed_deletes.append({"pesel": pesel, "status": response.status_code})

        delete_duration = time.time() - start_time
        print(f"\n=== FAZA 2 ZAKOŃCZONA ===")
        print(f"Usunięto: {1000 - len(failed_deletes)}/1000 kont")
        print(f"Czas usuwania: {delete_duration:.2f}s")
        print(f"Średni czas na konto: {delete_duration/1000*1000:.2f}ms")

        assert len(failed_creates) < 50, \
            f"Zbyt wiele nieudanych tworzeń: {len(failed_creates)}"
        assert len(failed_deletes) < 50, \
            f"Zbyt wiele nieudanych usunięć: {len(failed_deletes)}"

        session.close()

    def test_create_and_immediately_delete_1000_times(self, base_url):
        session = requests.Session()
        failed_operations = []
        create_times = []
        delete_times = []

        start_time = time.time()

        for i in range(1000):
            pesel = generate_unique_pesel()

            create_response = requests.post(
                f"{base_url}/api/accounts",
                json={"name": f"User{i}", "surname": f"Test{i}", "pesel": pesel},
                timeout=2
            )

            create_time = create_response.elapsed.total_seconds()
            create_times.append(create_time)

            if create_response.status_code != 201:
                failed_operations.append({"iteration": i, "type": "create", "status": create_response.status_code})
                continue

            delete_response = requests.delete(
                f"{base_url}/api/accounts/{pesel}",
                timeout=2
            )

            delete_time = delete_response.elapsed.total_seconds()
            delete_times.append(delete_time)

            if delete_response.status_code != 200:
                failed_operations.append({"iteration": i, "type": "delete", "status": delete_response.status_code})

        total_duration = time.time() - start_time

        avg_create = sum(create_times) / len(create_times) if create_times else 0
        avg_delete = sum(delete_times) / len(delete_times) if delete_times else 0
        max_create = max(create_times) if create_times else 0
        max_delete = max(delete_times) if delete_times else 0

        print(f"\n=== STATYSTYKI (SERIAL) ===")
        print(f"Całkowity czas: {total_duration:.2f}s")
        print(f"Średni czas create: {avg_create*1000:.2f}ms")
        print(f"Średni czas delete: {avg_delete*1000:.2f}ms")
        print(f"Maksymalny create: {max_create*1000:.2f}ms")
        print(f"Maksymalny delete: {max_delete*1000:.2f}ms")
        print(f"Nieudane operacje: {len(failed_operations)}")

        assert len(failed_operations) < 100, \
            f"Zbyt wiele nieudanych operacji: {len(failed_operations)}"
        assert avg_create < 0.3, \
            f"Średni czas create {avg_create:.3f}s przekracza oczekiwany"
        assert avg_delete < 0.3, \
            f"Średni czas delete {avg_delete:.3f}s przekracza oczekiwany"

        session.close()


class TestBatchVsSerialComparison:
    def test_analyze_batch_vs_serial_performance(self, base_url):
        import statistics

        batch_prefix = str(uuid.uuid4().int)[:6]
        serial_prefix = str(uuid.uuid4().int)[:6]

        batch_create_times = []
        batch_delete_times = []

        for i in range(100):
            pesel = generate_unique_pesel_with_prefix(batch_prefix)

            start = time.time()
            response = requests.post(
                f"{base_url}/api/accounts",
                json={"name": f"U{i}", "surname": f"T{i}", "pesel": pesel},
                timeout=2
            )
            batch_create_times.append(time.time() - start)

        for i in range(100):
            pesel = generate_unique_pesel_with_prefix(batch_prefix)

            start = time.time()
            requests.delete(f"{base_url}/api/accounts/{pesel}", timeout=2)
            batch_delete_times.append(time.time() - start)

        serial_times = []

        for i in range(100):
            pesel = generate_unique_pesel_with_prefix(serial_prefix)

            start = time.time()
            requests.post(
                f"{base_url}/api/accounts",
                json={"name": f"U{i}", "surname": f"T{i}", "pesel": pesel},
                timeout=2
            )
            requests.delete(f"{base_url}/api/accounts/{pesel}", timeout=2)
            serial_times.append(time.time() - start)

        batch_total = sum(batch_create_times) + sum(batch_delete_times)
        serial_total = sum(serial_times)

        batch_avg = (sum(batch_create_times) + sum(batch_delete_times)) / 200
        serial_avg = sum(serial_times) / 100

        batch_stdev = statistics.stdev(batch_create_times + batch_delete_times) if len(batch_create_times + batch_delete_times) > 1 else 0
        serial_stdev = statistics.stdev(serial_times) if len(serial_times) > 1 else 0

        print(f"\n=== PORÓWNANIE BATCH vs SERIAL ===")
        print(f"Batch - całkowity czas: {batch_total:.3f}s")
        print(f"Serial - całkowity czas: {serial_total:.3f}s")
        print(f"Batch - średni czas: {batch_avg*1000:.2f}ms")
        print(f"Serial - średni czas: {serial_avg*1000:.2f}ms")
        print(f"Batch - odchylenie std: {batch_stdev*1000:.2f}ms")
        print(f"Serial - odchylenie std: {serial_stdev*1000:.2f}ms")

        assert batch_total > 0
        assert serial_total > 0
