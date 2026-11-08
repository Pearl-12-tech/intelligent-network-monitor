import pandas as pd
from pathlib import Path

# ---------------------------------
# NETWORK DATA ANALYSIS
# ---------------------------------

DATA_FILE = Path("network_data.csv")

print("=" * 55)
print("          NETWORK DATA ANALYSIS")
print("=" * 55)

# Check whether our dataset exists

if not DATA_FILE.exists():
    print("Error: network_data.csv was not found.")
    raise SystemExit

# Load the collected data

data = pd.read_csv(DATA_FILE)

if data.empty:
    print("The dataset is empty. Run monitor.py first.")
    raise SystemExit

# Convert response times into numeric values

data["response_time_ms"] = pd.to_numeric(
    data["response_time_ms"],
    errors="coerce"
)

# ---------------------------------
# CALCULATE NETWORK STATISTICS
# ---------------------------------

total_tests = len(data)

successful_tests = (data["status"] == "ONLINE").sum()

unsuccessful_tests = total_tests - successful_tests

success_rate = (successful_tests / total_tests) * 100

response_times = data["response_time_ms"].dropna()

# ---------------------------------
# DISPLAY RESULTS
# ---------------------------------

print(f"\nTotal network tests: {total_tests}")
print(f"Successful responses: {successful_tests}")
print(f"Unsuccessful responses: {unsuccessful_tests}")

print(f"\nICMP response success rate: {success_rate:.2f}%")

if not response_times.empty:

    average_latency = response_times.mean()
    highest_latency = response_times.max()
    lowest_latency = response_times.min()

    print(f"\nAverage response time: {average_latency:.2f} ms")
    print(f"Highest response time: {highest_latency:.2f} ms")
    print(f"Lowest response time: {lowest_latency:.2f} ms")

else:

    print("\nNo successful response-time measurements available.")

# ---------------------------------
# DISPLAY STATUS DISTRIBUTION
# ---------------------------------

print("\nSTATUS DISTRIBUTION")
print("-" * 30)

for status, count in data["status"].value_counts().items():
    print(f"{status}: {count}")

print("\nAnalysis completed successfully.")
print("=" * 55)