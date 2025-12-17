import numpy as np
import pandas as pd
from analytics.resample import resample_symbol

def get_aligned_pair(symbol1, symbol2, timeframe="1s"):
    """
    Aligns two symbols' price data by timestamp.
    Returns DataFrame with columns: symbol1, symbol2, log_symbol1, log_symbol2
    """
    s1 = resample_symbol(symbol1, timeframe)
    s2 = resample_symbol(symbol2, timeframe)

    if s1.empty or s2.empty:
        return pd.DataFrame()

    df = s1.join(s2, how="inner")
    df[f"log_{symbol1}"] = np.log(df[symbol1])
    df[f"log_{symbol2}"] = np.log(df[symbol2])

    return df
