# 📈 Real-Time Crypto Pair Trading Analytics Platform

A real-time **statistical arbitrage & pair trading analytics platform** built using **Binance WebSockets**, **Python**, and **Streamlit**.  
The system continuously ingests live trade data, computes hedge ratios (static & dynamic), spread, Z-score, correlation, and statistical tests, and visualizes everything through an interactive dashboard.

---
## Requirements
- Python 3.10
 
##   Key Features

###   Real-Time Market Data
- Live trade data from **Binance WebSocket API**
- Supports multiple crypto pairs (e.g. BTCUSDT–ETHUSDT)
- Tick-level data storage with rolling window control

###   Pair Trading Analytics
- **Hedge Ratio Estimation**
  - OLS Regression
  - Huber Regression
  - Theil–Sen Regression
  - **Kalman Filter (Dynamic Hedge Ratio)**

- **Spread Calculation**
- **Rolling Z-Score**
- **Rolling Correlation**
- **ADF Test (Stationarity Check)**

###   Visualization Dashboard (Streamlit)
- Live price charts for both assets
- Spread & Z-score chart with entry/exit thresholds
- Dynamic hedge ratio plot (Kalman)
- Rolling correlation plot
- Rule-based trading alerts (LONG / SHORT / EXIT)
- Latest statistical metrics

###   Data Management
- In-memory tick store with automatic trimming
- SQLite database for analytics snapshots
- CSV export of analytics data

###   Built-in Knowledge Chatbot
- Finance & crypto-related Q&A
- Covers concepts like Z-score, hedge ratio, arbitrage, regression methods

---

### Deployment

This project is Streamlit Community Cloud compatible.
Deployment requirements:
app.py as entry file
requirements.txt
WebSocket auto-reconnect logic included
No local state dependencies. Must use python 3.10

### Trading Logic 

Stream live trades via Binance WebSocket
Align prices by timestamp
Compute hedge ratio (static or Kalman)
Calculate spread & Z-score
Generate alerts based on thresholds
Visualize & export analytics
