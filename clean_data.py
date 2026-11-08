
import csv
import os
import shutil

DATA_FILE = "network_data.csv"
BACKUP_FILE = "network_data_before_cleanup.csv"

if not os.path.exists(DATA_FILE):
    print("Error: network_data.csv was not found.")
    raise SystemExit

if os.path.exists(BACKUP_FILE):
    print("Backup already exists. Rename it before running cleanup.")
    raise SystemExit

# Preserve the complete original dataset
shutil.copy2(DATA_FILE, BACKUP_FILE)

# Read existing records
with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    records = list(reader)

# Remove only controlled-test and malformed records
clean_records = [
    record for record in records
    if "192.0.2.1" not in str(record.get("destination", ""))
    and "Controlled Test Destination" not in str(record.get("destination", ""))
]

removed = len(records) - len(clean_records)

# Save the cleaned dataset
with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(clean_records)

print("DATA CLEANUP COMPLETED")
print(f"Original records: {len(records)}")
print(f"Removed test records: {removed}")
print(f"Remaining records: {len(clean_records)}")
print(f"Original data preserved in: {BACKUP_FILE}")
