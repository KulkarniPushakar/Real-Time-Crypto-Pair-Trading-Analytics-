import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import threading
import random
from streamlit_autorefresh import st_autorefresh
from ws.binance_ws import start_ws

from analytics.align_pairs import get_aligned_pair
from analytics.spread import compute_spread
from analytics.zscore import compute_zscore
from analytics.rolling_corr import compute_rolling_corr
from analytics.ADF_test import compute_adf
from analytics.hedge_ratio import compute_static_hedge, compute_dynamic_hedge

# =============================
# Streamlit Page Setup
# =============================
st.set_page_config(page_title="Real-Time Pair Trading Analytics", layout="wide")

# -----------------------------
# CSS for dark theme + background
# -----------------------------
st.markdown("""
<style>
    /* Background image */
    .main {
        background-image: url("https://images.unsplash.com/photo-1601597116410-3be850f7e5b6?auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: #f0f0f0;
    }

    /* Overlay for readability */
    .css-1outpf7 {  /* Streamlit main container */
        background-color: rgba(30,30,30,0.85);  /* dark overlay */
        padding: 1rem;
        border-radius: 10px;
    }

    /* Headers */
    .stSubheader {color:#1f77b4; font-weight:bold;}
    
    /* Metrics */
    .metric-label {font-weight:bold; font-size:16px; color:#f0f0f0;}
    
    /* Alert box */
    .alert-box {padding:10px; border-radius:5px; font-weight:bold; color:white;}
    
    /* News cards */
    .news-card {border:1px solid #444; padding:10px; border-radius:5px; margin-bottom:5px; background-color: rgba(43,43,43,0.8); color:#f0f0f0;}
    
    /* Chatbot cards */
    .chat-card {border:1px solid #444; padding:10px; border-radius:5px; background-color: rgba(43,43,43,0.8); color:#f0f0f0;}
    
    /* Sidebar dark */
    .css-1d391kg {background-color: rgba(43,43,43,0.95);}
    .css-1v3fvcr {color:#f0f0f0;}
</style>
""", unsafe_allow_html=True)

st.title("Real-Time Pair Trading Analytics")

# =============================
# News & Chatbot Side by Side
# =============================
st.markdown("---")
news_col, chat_col = st.columns([2, 1])

# ----- News Section -----
with news_col:
    st.subheader("📰 Market News")
    news_items = [
        {"title": "Bitcoin volatility rises amid macro uncertainty", "source": "CoinDesk", "url": "https://www.coindesk.com/markets/"},
        {"title": "Ethereum price reacts to ETF-related developments", "source": "CoinTelegraph", "url": "https://cointelegraph.com/"},
        {"title": "Crypto markets await US Fed policy signals", "source": "Reuters", "url": "https://www.reuters.com/markets/"}
    ]
    for news in news_items:
        st.markdown(f"<div class='news-card'>- **[{news['title']}]({news['url']})**  <br>  _Source: {news['source']}_</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # space after news

# ----- Chatbot Section -----
with chat_col:
    st.subheader("💬 Crypto/Finance Chatbot")
    chat_container = st.container()
    chat_qa = {
        "What is Z-Score?": "The Z-Score indicates how many standard deviations the spread is from its mean. Entry/exit signals are based on thresholds.",
        "How to trade BTC?": "You can trade BTC based on pair trading signals like spread, hedge ratio, and Z-Score crossings.",
        "Explain Hedge Ratio": "Hedge Ratio shows the proportion of one asset to hedge the other in a pair trade, minimizing market risk.",
        "What is Pair Trading?": "Pair trading is a market-neutral strategy where you take opposite positions in two correlated assets based on spread deviations.",
        "What is a Spread in trading?": "Spread is the difference between the prices of two assets in a pair trade.",
        "How to use moving averages?": "Moving averages help identify trends and smooth out price action for better signals.",
        "What is Arbitrage?": "Arbitrage is the practice of profiting from price differences of the same asset across different markets.",
        "Explain Kalman Filter?": "Kalman Filter is used to dynamically estimate hedge ratios and track time-varying relationships between assets.",
        "What is OLS Regression?": "OLS regression finds the best-fit line that minimizes the squared errors between variables.",
        "Difference between short and long positions?": "Long means buying an asset expecting it to rise, short means selling it expecting it to fall.",
        "What is Market Neutral Strategy?": "A strategy designed to eliminate market risk by taking offsetting long and short positions.",
        "Explain Theil-Sen Regression?": "Theil-Sen is a robust regression technique that is less sensitive to outliers compared to OLS.",
        "What is Huber Regression?": "Huber Regression is a robust method combining OLS and absolute error to handle outliers.",
        "How to interpret correlation?": "Correlation measures the strength of a linear relationship between two assets, ranging from -1 to 1.",
        "What is a Trading Signal?": "A trading signal indicates when to enter or exit a trade based on technical or statistical analysis."
    }
    questions_list = list(chat_qa.keys())
    random.shuffle(questions_list)
    selected_question = st.selectbox("Choose a question:", [""] + questions_list)
    user_input = st.text_input("Or type your question:")
    final_question = selected_question if selected_question else user_input
    if final_question:
        response = chat_qa.get(final_question.strip(), "Sorry, I can only answer crypto and finance related questions.")
        chat_container.markdown(f"<div class='chat-card'>**Bot:** {response}</div>", unsafe_allow_html=True)

# =============================
# Sidebar Controls
# =============================
st.sidebar.header("Controls")
symbol1 = st.sidebar.selectbox("Symbol 1", ["BTCUSDT", "ETHUSDT"], index=0)
symbol2 = st.sidebar.selectbox("Symbol 2", ["BTCUSDT", "ETHUSDT"], index=1)
timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1min", "5min"])
rolling_window = st.sidebar.slider("Rolling Window", 10, 100, 30)
regression_type = st.sidebar.selectbox("Regression Type", ["OLS", "Huber", "Theil-Sen", "Kalman"], index=0)
run_adf = st.sidebar.checkbox("Run ADF Test", value=True)
zscore_entry = st.sidebar.number_input("Z-Score Entry Threshold", value=2.0, step=0.1)
zscore_exit = st.sidebar.number_input("Z-Score Exit Threshold", value=0.0, step=0.1)

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="analytics_refresh")

# =============================
# Start WebSocket
# =============================
ws_thread = threading.Thread(target=start_ws, daemon=True)
ws_thread.start()
st.sidebar.success("WebSocket started in background...")

# =============================
# Fetch aligned data
# =============================
df = get_aligned_pair(symbol1, symbol2, timeframe)
if df.empty or len(df) < rolling_window:
    st.warning("Waiting for enough data to compute analytics...")
    st.stop()

# =============================
# Compute Hedge Ratio
# =============================
if regression_type == "Kalman":
    beta_series = compute_dynamic_hedge(df, symbol1, symbol2)
    hedge_ratio = beta_series[-1] if beta_series is not None else None
else:
    hedge_ratio = compute_static_hedge(df, symbol1, symbol2, regression_type)
    beta_series = None

# =============================
# Spread, Z-Score & Rolling Correlation
# =============================
spread = compute_spread(df, hedge_ratio, symbol1, symbol2)
zscore = compute_zscore(spread, rolling_window)
rolling_corr = compute_rolling_corr(df, symbol1, symbol2, rolling_window)
adf_p = compute_adf(spread) if run_adf else None

# =============================
# Price Chart
# =============================
st.subheader("Price Chart")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df.index, y=df[symbol1], name=symbol1, line=dict(color="cyan", width=2)))
fig_price.add_trace(go.Scatter(x=df.index, y=df[symbol2], name=symbol2, line=dict(color="orange", width=2)))
fig_price.update_layout(
    height=400,
    xaxis_title="Time",
    yaxis_title="Price",
    hovermode="x unified",
    plot_bgcolor="rgba(30,30,30,0.9)",
    paper_bgcolor="rgba(30,30,30,0.9)",
    font=dict(color="white")
)
st.plotly_chart(fig_price, use_container_width=True)

# =============================
# Spread & Z-Score Chart
# =============================
st.subheader("Spread & Z-Score")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=spread, name="Spread", yaxis="y1", line=dict(color="green", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=zscore, name="Z-Score", yaxis="y2", line=dict(color="red", width=2)))
fig.add_hline(y=zscore_entry, line_dash="dash", line_color="yellow", annotation_text="Entry Threshold")
fig.add_hline(y=-zscore_entry, line_dash="dash", line_color="yellow")
fig.add_hline(y=zscore_exit, line_dash="dot", line_color="orange", annotation_text="Exit Threshold")
fig.add_hline(y=-zscore_exit, line_dash="dot", line_color="orange")
fig.update_layout(
    xaxis=dict(title="Time", gridcolor="#333"),
    yaxis=dict(title="Spread", showgrid=True, zeroline=True),
    yaxis2=dict(title="Z-Score", overlaying="y", side="right", showgrid=False, zeroline=True),
    height=400,
    hovermode="x unified",
    plot_bgcolor="rgba(30,30,30,0.9)",
    paper_bgcolor="rgba(30,30,30,0.9)",
    font=dict(color="white")
)
st.plotly_chart(fig, use_container_width=True)

# =============================
# Dynamic Hedge Ratio (Kalman)
# =============================
if beta_series is not None:
    st.subheader("Dynamic Hedge Ratio (Kalman)")
    st.line_chart(pd.Series(beta_series, index=df.index), use_container_width=True)

# =============================
# Rolling Correlation
# =============================
st.subheader("Rolling Correlation")
if rolling_corr is not None:
    st.line_chart(pd.Series(rolling_corr, index=df.index), use_container_width=True)

# =============================
# Rule-Based Alerts
# =============================
st.subheader("Rule-Based Alerts")
latest_z = zscore.iloc[-1]
alert_msg = ""
alert_color = "green"

if latest_z > zscore_entry:
    alert_msg = f"🚨 SHORT {symbol1} / LONG {symbol2} — Z-Score: {latest_z:.2f}"
    alert_color = "#d9534f"
elif latest_z < -zscore_entry:
    alert_msg = f"🚨 LONG {symbol1} / SHORT {symbol2} — Z-Score: {latest_z:.2f}"
    alert_color = "#d9534f"
elif abs(latest_z) < zscore_exit:
    alert_msg = f"✅ Close Position — Z-Score: {latest_z:.2f}"
    alert_color = "#5bc0de"
else:
    alert_msg = f"No action — Z-Score: {latest_z:.2f}"
    alert_color = "#5cb85c"

st.markdown(f"<div class='alert-box' style='background-color:{alert_color}'>{alert_msg}</div>", unsafe_allow_html=True)

# =============================
# Latest Statistics
# =============================
st.subheader("Latest Statistics")
latest = {
    "Hedge Ratio": hedge_ratio,
    "Spread": spread.iloc[-1],
    "Z-Score": latest_z,
    "ADF p-value": adf_p if run_adf else "Disabled"
}
cols = st.columns(len(latest))
for col, (name, value) in zip(cols, latest.items()):
    if isinstance(value, float):
        col.metric(name, f"{value:.4f}")
    else:
        col.metric(name, str(value))

# =============================
# Raw Data & CSV Export
# =============================
with st.expander("Show raw data"):
    st.dataframe(df.tail(50))

st.subheader("Export Data")
export_df = df[[symbol1, symbol2]].copy()
export_df["Spread"] = spread
export_df["Z-Score"] = zscore
export_df.index.name = "Timestamp"
export_df_reset = export_df.reset_index()
export_df_reset['Timestamp'] = export_df_reset['Timestamp'].astype(str)

st.download_button(
    label="Download CSV",
    data=export_df_reset.to_csv(index=False),
    file_name=f"{symbol1}_{symbol2}_analytics.csv",
    mime="text/csv"
)
