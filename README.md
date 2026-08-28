# ⚽ Allwyn Virtual Sports - Delay Analyzer

A quantitative Python script designed to track, analyze, and log statistical delays in Allwyn virtual football matches. 

## 📌 Overview
In virtual sports and algorithmic betting, a "delay" (ή "καθυστέρηση") refers to the number of consecutive matches where a specific outcome has not occurred. This script acts as an automated observer, tracking these anomalies in real-time or through historical data to identify potential statistical edges.

## ⚙️ Core Features
* **1-X-2 Delay Tracking:** Dynamically calculates how many matches have passed without a Home Win (1), Draw (X), or Away Win (2).
* **Totals (Over/Under 2.5):** Tracks the consecutive absences of Over 2.5 and Under 2.5 goals.
* **Odds Processing:** Maps the corresponding odds to each match and outcome for further Expected Value (EV) calculations.
* **Data Structuring:** Formats the raw match data into structured dictionaries/DataFrames for seamless integration with backtesting engines.

## 🚀 Usage
The main logic is contained within `allwyn.py`. Run the script via your terminal:

```bash
python allwyn.py
