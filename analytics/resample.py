import pandas as pd
from data.ticks import get_ticks

TIMEFRAME_MAP = {
    "1s": "s",
    "1min": "T",
    "5min": "5T"
}

def resample_symbol(symbol, timeframe="1s"):
    df = get_ticks(symbol)
    if df.empty:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    rule = TIMEFRAME_MAP[timeframe]
    resampled = df["price"].resample(rule).last().dropna()
    return resampled.to_frame(name=symbol)
