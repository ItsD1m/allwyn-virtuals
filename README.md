<div align="center">
  
  # ⚽ Allwyn Virtual Sports - Delay Analyzer
  
  *A quantitative Python script designed to track, analyze, and log statistical delays in Allwyn virtual football matches.*

  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)
  ![Status](https://img.shields.io/badge/Status-Active-success.svg)
  ![Data](https://img.shields.io/badge/Data-Analysis-orange.svg)

  <br>
  
<img width="2586" height="1271" alt="allwyn and terminal" src="https://github.com/user-attachments/assets/eb04776c-25ab-4fa2-a92d-0373278947af" />

  
</div>

---

## 📌 Overview

In virtual sports and algorithmic betting, a **"delay"** (ή *"καθυστέρηση"*) refers to the number of consecutive matches where a specific outcome has not occurred. 

This script acts as an automated observer, tracking these anomalies in real-time or through historical data to identify potential **statistical edges**.

## ⚙️ Core Features

* **`1-X-2` Delay Tracking:** Dynamically calculates how many matches have passed without a Home Win (1), Draw (X), or Away Win (2).
* **`Totals` (Over/Under 2.5):** Tracks the consecutive absences of Over 2.5 and Under 2.5 goals.
* **Odds Processing:** Maps the corresponding odds to each match and outcome for further Expected Value (EV) calculations.
* **Data Structuring:** Formats the raw match data into structured dictionaries and DataFrames for seamless integration with backtesting engines.

## 🚀 Usage

The main logic is contained within `allwyn.py`. Run the script via your terminal:

```bash
python allwyn.py
