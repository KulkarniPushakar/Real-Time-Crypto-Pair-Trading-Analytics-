def compute_rolling_corr(df, col1, col2, window):
    if df.empty or len(df) < window:
        return None
    return df[col1].rolling(window).corr(df[col2])
