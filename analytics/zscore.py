def compute_zscore(spread, window):
    if spread is None or len(spread) < window:
        return None
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    return (spread - mean) / std
