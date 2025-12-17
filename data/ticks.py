import pandas as pd
from collections import defaultdict

tick_store = defaultdict(lambda: pd.DataFrame(columns=["timestamp", "price", "qty"]))
MAX_ROWS = 10_000

def add_tick(symbol, timestamp, price, qty):
    df = tick_store[symbol]
    df.loc[len(df)] = [timestamp, price, qty]

    # Keep only last MAX_ROWS rows and reset index
    if len(df) > MAX_ROWS:
        df = df.iloc[-MAX_ROWS:].reset_index(drop=True)

    tick_store[symbol] = df

def get_ticks(symbol):
    return tick_store[symbol].copy()
