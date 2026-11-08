
from datetime import datetime
import platform
import socket
import subprocess
import re
import time
import csv
import os
import ipaddress
import shutil

# ---------------------------------
# NETWORK MONITORING CONFIGURATION
# ---------------------------------

NUMBER_OF_TESTS = 10
DATA_FILE = "network_data.csv"

FIELDNAMES = [
    "timestamp",
    "computer_name",
    "destination",
    "status",
    "response_time_ms",
    "packet_loss_percent"
]

# ---------------------------------
# AUTOMATIC GATEWAY DISCOVERY
# ---------------------------------

def find_default_gateway():

    try:
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            encoding="mbcs",
            errors="replace",
            timeout=10
        )

        lines = result.stdout.splitlines()

        for index, line in enumerate(lines):

            if "Default Gateway" in line:

                match = re.search(
                    r"(\d{1,3}(?:\.\d{1,3}){3})",
                    line
                )

                if not match and index + 1 < len(lines):
                    match = re.search(
                        r"(\d{1,3}(?:\.\d{1,3}){3})",
                        lines[index + 1]
                    )

                if match:

                    address = match.group(1)

                    if address != "0.0.0.0":
                        return str(
                            ipaddress.IPv4Address(address)
                        )

    except Exception as error:
        print(f"Gateway discovery error: {error}")

    return None


# ---------------------------------
# MONITORING DESTINATIONS
# ---------------------------------

TARGETS = {
    "Google DNS": "8.8.8.8",
    "Cloudflare DNS": "1.1.1.1",
}

gateway = find_default_gateway()

if gateway:
    TARGETS["Local Network Gateway"] = gateway
else:
    print("Warning: No IPv4 default gateway was discovered.")


# ---------------------------------
# PRESERVE AND UPDATE EXISTING CSV
# ---------------------------------

def prepare_csv():

    if not os.path.exists(DATA_FILE):
        return

    if os.path.getsize(DATA_FILE) == 0:
        return

    with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        old_fieldnames = reader.fieldnames or []

        if "packet_loss_percent" in old_fieldnames:
            return

        records = list(reader)

    backup_file = "network_data_backup.csv"

    if not os.path.exists(backup_file):
        shutil.copy2(DATA_FILE, backup_file)

    for record in records:
        record["packet_loss_percent"] = ""

    temporary_file = DATA_FILE + ".tmp"

    with open(
        temporary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writeheader()
        writer.writerows(records)

    os.replace(temporary_file, DATA_FILE)

    print("Existing CSV updated successfully.")
    print("Historical records preserved.")


# ---------------------------------
# PREPARE CSV FILE
# ---------------------------------

prepare_csv()

file_exists = (
    os.path.exists(DATA_FILE)
    and os.path.getsize(DATA_FILE) > 0
)


# ---------------------------------
# SYSTEM INFORMATION
# ---------------------------------

print("=" * 55)
print("       INTELLIGENT NETWORK MONITORING SYSTEM")
print("=" * 55)

print(f"Computer: {socket.gethostname()}")
print(f"Operating system: {platform.system()}")
print(f"Monitoring destinations: {len(TARGETS)}")
print(f"Start time: {datetime.now()}")


# ---------------------------------
# NETWORK MONITORING
# ---------------------------------

with open(
    DATA_FILE,
    mode="a",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=FIELDNAMES
    )

    if not file_exists:
        writer.writeheader()

    # ---------------------------------
    # MONITOR EACH DESTINATION
    # ---------------------------------

    for device_name, target in TARGETS.items():

        print("\n" + "=" * 55)
        print(f"MONITORING: {device_name}")
        print(f"IP ADDRESS: {target}")
        print("=" * 55)

        successful_tests = 0
        failed_tests = 0
        response_times = []

        destination_records = []

        for test_number in range(
            1,
            NUMBER_OF_TESTS + 1
        ):

            print(f"\nTest {test_number} of {NUMBER_OF_TESTS}")

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            status = "NO_RESPONSE"
            latency = None

            try:

                result = subprocess.run(
                    [
                        "ping",
                        "-n",
                        "1",
                        "-w",
                        "2000",
                        target
                    ],
                    capture_output=True,
                    text=True,
                    encoding="mbcs",
                    errors="replace",
                    timeout=4
                )

                output = result.stdout + result.stderr

                match = re.search(
                    r"time[=<]\s*(\d+)\s*ms",
                    output,
                    re.IGNORECASE
                )

                if result.returncode == 0:

                    status = "ONLINE"
                    successful_tests += 1

                    if match:
                        latency = float(match.group(1))
                        response_times.append(latency)

                        print("Status: ONLINE")
                        print(f"Response time: {latency} ms")

                    else:
                        print("Status: ONLINE")
                        print("Response time: Not available")

                else:

                    failed_tests += 1
                    print("Status: NO PING RESPONSE")

            except subprocess.TimeoutExpired:

                status = "TIMEOUT"
                failed_tests += 1

                print("Status: TIMEOUT")

            except Exception as error:

                status = "ERROR"
                failed_tests += 1

                print(f"Error: {error}")

            # Calculate cumulative packet loss

            packet_loss = (
                failed_tests / test_number
            ) * 100

            # Store measurement

            record = {
                "timestamp": timestamp,
                "computer_name": socket.gethostname(),
                "destination": target,
                "status": status,
                "response_time_ms": latency,
                "packet_loss_percent": round(
                    packet_loss, 2
                )
            }

            destination_records.append(record)

            time.sleep(1)

        # ---------------------------------
        # SAVE DESTINATION RECORDS
        # ---------------------------------

        writer.writerows(destination_records)
        file.flush()

        # ---------------------------------
        # DESTINATION SUMMARY
        # ---------------------------------

        final_packet_loss = (
            failed_tests / NUMBER_OF_TESTS
        ) * 100

        print("\nDESTINATION SUMMARY")
        print(f"Successful tests: {successful_tests}")
        print(f"Failed tests: {failed_tests}")

        print(
            f"Packet loss: {final_packet_loss:.2f}%"
        )

        if response_times:

            average = (
                sum(response_times)
                / len(response_times)
            )

            print(f"Average latency: {average:.2f} ms")

        else:

            print("Average latency: Not available")


# ---------------------------------
# MONITORING COMPLETED
# ---------------------------------

print("\n" + "=" * 55)
print("MULTI-DESTINATION MONITORING COMPLETED")
print(f"Data saved to: {DATA_FILE}")
print("=" * 55)
