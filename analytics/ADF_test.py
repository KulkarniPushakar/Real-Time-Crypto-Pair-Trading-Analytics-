from statsmodels.tsa.stattools import adfuller

def compute_adf(spread):
    if spread is None or len(spread) < 30:
        return None
    return adfuller(spread.dropna())[1]
