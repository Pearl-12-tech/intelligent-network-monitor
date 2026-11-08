import pandas as pd
from sklearn.ensemble import IsolationForest

# ---------------------------------
# LOAD NETWORK DATA
# ---------------------------------

df = pd.read_csv("network_data.csv")

df["response_time_ms"] = pd.to_numeric(
    df["response_time_ms"],
    errors="coerce"
)

# Keep successful records with valid response times
data = df[
    (df["status"].str.lower() == "online") &
    (df["response_time_ms"].notna())
].copy()

# ---------------------------------
# ANALYSE EACH DESTINATION
# ---------------------------------

print("\nNETWORK ANOMALY DETECTION")
print("=" * 50)

for destination in data["destination"].unique():

    destination_data = data[
        data["destination"] == destination
    ].copy()

    print(f"\nDESTINATION: {destination}")
    print("-" * 50)

    if len(destination_data) < 10:

        print("Not enough records for anomaly detection.")
        continue

    # Train a separate model for this destination
    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    model.fit(
        destination_data[["response_time_ms"]]
    )

    # Detect unusual response times
    destination_data["prediction"] = model.predict(
        destination_data[["response_time_ms"]]
    )

    destination_data["anomaly_status"] = (
        destination_data["prediction"].map({
            1: "Normal",
            -1: "Anomaly"
        })
    )

    # Display results
    print(
        destination_data[[
            "timestamp",
            "response_time_ms",
            "anomaly_status"
        ]].tail(15).to_string(index=False)
    )

    print("\nSUMMARY:")

    print(
        destination_data["anomaly_status"].value_counts()
    )