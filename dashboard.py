
import streamlit as st
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="Intelligent Network Monitor",
    page_icon="",
    layout="wide"
)

DATA_FILE = Path("network_data.csv")

# ---------------------------------
# DASHBOARD TITLE
# ---------------------------------

st.title("Intelligent Network Monitoring System")

st.caption("University Network Monitoring and Performance Analysis")

st.divider()

# ---------------------------------
# LOAD NETWORK DATA
# ---------------------------------

if not DATA_FILE.exists():
    st.error("Network data file not found. Run monitor.py first.")
    st.stop()

data = pd.read_csv(DATA_FILE)

if data.empty:
    st.warning("No network measurements available yet.")
    st.stop()

# Prepare data

data["response_time_ms"] = pd.to_numeric(
    data["response_time_ms"],
    errors="coerce"
)

data["packet_loss_percent"] = pd.to_numeric(
    data["packet_loss_percent"],
    errors="coerce"
)

data["timestamp"] = pd.to_datetime(
    data["timestamp"],
    errors="coerce"
)

# ---------------------------------
# REFRESH CONTROL
# ---------------------------------

if st.button("Refresh Dashboard"):
    st.rerun()

# ---------------------------------
# CALCULATE STATISTICS
# ---------------------------------

total_tests = len(data)

online_tests = (data["status"] == "ONLINE").sum()

failed_tests = total_tests - online_tests

success_rate = (online_tests / total_tests) * 100

response_times = data["response_time_ms"].dropna()

if not response_times.empty:
    average_latency = response_times.mean()
    highest_latency = response_times.max()
    lowest_latency = response_times.min()
else:
    average_latency = 0
    highest_latency = 0
    lowest_latency = 0

# ---------------------------------
# NETWORK SUMMARY
# ---------------------------------

st.subheader("Network Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tests", total_tests)
col2.metric("Successful Responses", online_tests)
col3.metric("Failed Responses", failed_tests)
col4.metric("ICMP Success Rate", f"{success_rate:.1f}%")

st.divider()

# ---------------------------------
# PERFORMANCE SUMMARY
# ---------------------------------

st.subheader("Network Performance")

col5, col6, col7 = st.columns(3)

col5.metric("Average Latency", f"{average_latency:.2f} ms")
col6.metric("Highest Latency", f"{highest_latency:.2f} ms")
col7.metric("Lowest Latency", f"{lowest_latency:.2f} ms")

st.divider()

# ---------------------------------
# RESPONSE TIME CHART
# ---------------------------------

st.subheader("Response Time History")

chart_data = data.dropna(subset=["response_time_ms"]).copy()

if not chart_data.empty:

    chart_data = chart_data.reset_index(drop=True)
    chart_data.index = chart_data.index + 1

    st.line_chart(
        chart_data["response_time_ms"],
        x_label="Test Number",
        y_label="Response Time (ms)"
    )

else:

    st.info("No response-time measurements available.")

st.divider()

# ---------------------------------
# NETWORK STATUS DISTRIBUTION
# ---------------------------------

st.subheader("Network Status Distribution")

status_data = data["status"].value_counts()

st.bar_chart(status_data)

st.divider()

# ---------------------------------
# RECENT NETWORK RECORDS
# ---------------------------------

st.subheader("Recent Network Measurements")

recent_data = data.tail(10).iloc[::-1]

st.dataframe(
    recent_data,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------
# SYSTEM INFORMATION
# ---------------------------------

st.divider()

st.subheader("Monitoring Information")

st.write(f"Monitoring destination: {data['destination'].iloc[-1]}")
st.write(f"Computer: {data['computer_name'].iloc[-1]}")

st.caption(
    "Data source: network_data.csv | "
    "Monitoring method: ICMP Ping"
)

st.caption(
    "Note: ICMP response availability does not necessarily "
    "represent overall internet availability."
)

# ---------------------------------
# DESTINATION PERFORMANCE BREAKDOWN
# ---------------------------------

st.header("Destination Performance Breakdown")

performance = data.groupby("destination").agg(
    total_tests=("status", "count"),
    average_latency=("response_time_ms", "mean"),
    highest_latency=("response_time_ms", "max"),
    lowest_latency=("response_time_ms", "min")
).reset_index()

success_counts = (
    data.assign(
        successful=data["status"].str.lower().eq("online")
    )
    .groupby("destination")["successful"]
    .sum()
)

performance["successful_tests"] = (
    performance["destination"].map(success_counts)
)

performance["failed_tests"] = (
    performance["total_tests"]
    - performance["successful_tests"]
)

performance["success_rate (%)"] = (
    performance["successful_tests"]
    / performance["total_tests"]
    * 100
)

st.dataframe(
    performance.round(2),
    use_container_width=True,
    hide_index=True
)

# ---------------------------------
# MACHINE LEARNING ANOMALY DETECTION
# ---------------------------------


# ---------------------------------
# STAGE 17: MULTI-FEATURE ANOMALY DETECTION
# ---------------------------------

st.header("Intelligent Network Anomaly Detection")

ml_data = data.copy()

# Convert measurements to numeric values
ml_data["response_time_ms"] = pd.to_numeric(
    ml_data["response_time_ms"],
    errors="coerce"
)

ml_data["packet_loss_percent"] = pd.to_numeric(
    ml_data["packet_loss_percent"],
    errors="coerce"
)

# Keep successful records with both measurements available
ml_data = ml_data[
    (ml_data["status"].str.upper() == "ONLINE") &
    (ml_data["response_time_ms"].notna()) &
    (ml_data["packet_loss_percent"].notna())
].copy()

anomaly_results = []

# Analyse each destination separately
for destination in ml_data["destination"].unique():

    destination_data = ml_data[
        ml_data["destination"] == destination
    ].copy()

    if len(destination_data) < 10:
        continue

    # Features used by the machine-learning model
    features = destination_data[
        ["response_time_ms", "packet_loss_percent"]
    ]

    # Create Isolation Forest model
    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    # Train and detect anomalies
    model.fit(features)

    destination_data["prediction"] = model.predict(
        features
    )

    destination_data["anomaly_status"] = (
        destination_data["prediction"].map({
            1: "Normal",
            -1: "Anomaly"
        })
    )

    anomaly_results.append(destination_data)

# Display results
if anomaly_results:

    results = pd.concat(anomaly_results)

    total_anomalies = (
        results["anomaly_status"] == "Anomaly"
    ).sum()

    total_analysed = len(results)

    col1, col2 = st.columns(2)

    col1.metric(
        "Detected Network Anomalies",
        total_anomalies
    )

    col2.metric(
        "Measurements Analysed",
        total_analysed
    )

    st.subheader("Multi-Feature Anomaly Detection Results")

    st.dataframe(
        results[[
            "timestamp",
            "destination",
            "response_time_ms",
            "packet_loss_percent",
            "anomaly_status"
        ]].sort_values(
            "timestamp",
            ascending=False
        ).head(30),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Anomaly Distribution")

    anomaly_counts = (
        results.groupby(
            ["destination", "anomaly_status"]
        ).size().reset_index(name="count")
    )

    st.bar_chart(
        anomaly_counts,
        x="destination",
        y="count",
        color="anomaly_status"
    )

else:

    st.warning(
        "Not enough complete network measurements "
        "for multi-feature anomaly detection. "
        "Collect more monitoring data."
    )

# ---------------------------------
# STAGE 15: PACKET LOSS ANALYSIS
# ---------------------------------

st.divider()

st.header("Network Packet Loss Analysis")

packet_data = data.dropna(
    subset=["packet_loss_percent"]
).copy()

if not packet_data.empty:

    packet_summary = packet_data.groupby(
        "destination"
    ).agg(
        average_packet_loss=(
            "packet_loss_percent", "mean"
        ),
        maximum_packet_loss=(
            "packet_loss_percent", "max"
        )
    ).reset_index()

    st.subheader("Packet Loss by Destination")

    st.dataframe(
        packet_summary.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Average Packet Loss")

    st.bar_chart(
        packet_summary,
        x="destination",
        y="average_packet_loss"
    )

else:

    st.info(
        "No packet-loss measurements available yet. "
        "Run monitor.py to collect packet-loss data."
    )


# ---------------------------------
# STAGE 16: NETWORK FAULT ALERT SYSTEM
# ---------------------------------

st.divider()

st.header("Intelligent Network Fault Alerts")

alerts = []

# Check for offline destinations

latest_records = (
    data.sort_values("timestamp")
    .groupby("destination")
    .tail(1)
)

for _, record in latest_records.iterrows():

    destination = record["destination"]

    if str(record["status"]).upper() != "ONLINE":

        alerts.append({
            "destination": destination,
            "alert_type": "Connection Failure",
            "severity": "Critical",
            "details": "Destination is not responding to ping."
        })

# Check for high packet loss

packet_data = data.dropna(
    subset=["packet_loss_percent"]
)

if not packet_data.empty:

    latest_packet_records = (
        packet_data.sort_values("timestamp")
        .groupby("destination")
        .tail(1)
    )

    for _, record in latest_packet_records.iterrows():

        if record["packet_loss_percent"] >= 20:

            alerts.append({
                "destination": record["destination"],
                "alert_type": "High Packet Loss",
                "severity": "Warning",
                "details": (
                    f"Packet loss is "
                    f"{record['packet_loss_percent']:.2f}%."
                )
            })

# Check for high latency

latency_data = data.dropna(
    subset=["response_time_ms"]
)

if not latency_data.empty:

    latest_latency_records = (
        latency_data.sort_values("timestamp")
        .groupby("destination")
        .tail(1)
    )

    for _, record in latest_latency_records.iterrows():

        if record["response_time_ms"] >= 150:

            alerts.append({
                "destination": record["destination"],
                "alert_type": "High Latency",
                "severity": "Warning",
                "details": (
                    f"Response time is "
                    f"{record['response_time_ms']:.2f} ms."
                )
            })

# Display alerts

if alerts:

    alert_table = pd.DataFrame(alerts)

    st.metric("Active Network Alerts", len(alerts))

    st.dataframe(
        alert_table,
        use_container_width=True,
        hide_index=True
    )

    for alert in alerts:

        message = (
            f"{alert['destination']}: "
            f"{alert['alert_type']} - "
            f"{alert['details']}"
        )

        if alert["severity"] == "Critical":
            st.error(message)

        else:
            st.warning(message)

else:

    st.success(
        "No network faults detected. "
        "All monitored destinations are within the configured thresholds."
    )
