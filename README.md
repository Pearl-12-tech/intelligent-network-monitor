# Intelligent Network Monitoring and Fault Detection System

A Python-based network monitoring prototype that measures network reachability, response time and packet loss across selected destinations. It stores monitoring results, analyses network performance and presents the findings through an interactive Streamlit dashboard.

## Project Overview

This project was developed as part of a Computer Engineering internship project. It demonstrates how network measurements can be collected and analysed to help identify unusual network conditions.

The system monitors:
- Google Public DNS (`8.8.8.8`)
- Cloudflare DNS (`1.1.1.1`)
- The computer's automatically discovered local IPv4 default gateway

Each destination is tested repeatedly using ICMP ping requests. The results are stored in a CSV dataset and displayed in a dashboard.

## Features

- Automated multi-destination network monitoring
- Automatic local default gateway discovery
- Response-time measurement
- Packet-loss calculation
- Timestamped monitoring records
- CSV-based data storage
- Network performance statistics
- Interactive Streamlit dashboard
- Response-time and status visualisations
- Destination-level performance comparisons
- Anomaly detection using the Isolation Forest algorithm
- Rule-based alerts for connection failure, high packet loss and high latency

## Technologies Used

- Python
- pandas
- Streamlit
- scikit-learn
- Windows command-line networking utilities
- Git and GitHub

## Project Structure

```text
intelligent-network-monitor/
│
├── monitor.py
├── dashboard.py
├── analyze_data.py
├── anomaly_detection.py
├── clean_data.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── screenshots/
```

## Installation

1. Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

2. Move into the project directory:

```bash
cd intelligent-network-monitor
```

3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

5. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Monitoring Script

Run:

```bash
python monitor.py
```

The script performs ten ping tests per configured destination and saves the measurements to `network_data.csv`.

## Launching the Dashboard

Run:

```bash
python -m streamlit run dashboard.py
```

Streamlit will open the dashboard in your browser, normally at:

```text
http://localhost:8501
```

Run the monitoring script first so that the dashboard has data to display.

## Machine Learning

The project uses the Isolation Forest algorithm from scikit-learn to identify unusual combinations of response time and packet-loss measurements.

The model is used for anomaly detection. It does not predict future network failures or independently confirm the cause of an unusual measurement.

## Alert Conditions

The dashboard uses configurable rules to highlight:

- Connection failures when the latest recorded status is not ONLINE
- High packet loss at or above 20%
- High latency at or above 150 milliseconds

These alerts indicate conditions that may require investigation.

## Testing and Limitations

The prototype was tested from a Windows computer using selected public DNS destinations and its local default gateway. Controlled tests were also used to verify the alert functionality.

The system relies on ICMP responses. Some hosts or networks may block ping requests even when other network services are available. The prototype does not directly monitor every device on a university network.

Monitoring of institutional devices should only be performed with appropriate authorisation.

## Author

**Pearl Owusua Amoah**  
BSc Computer Engineering  
University of Ghana

## Project Type

Computer Engineering Internship Project — 1 Credit Hour