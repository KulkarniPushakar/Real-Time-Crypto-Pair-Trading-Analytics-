def compute_spread(df, hedge_ratio, symbol1, symbol2):
    if df.empty or hedge_ratio is None:
        return None
    return df[f"log_{symbol1}"] - hedge_ratio * df[f"log_{symbol2}"]
