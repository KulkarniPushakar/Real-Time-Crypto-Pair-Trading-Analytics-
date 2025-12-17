import time
from analytics.align_pairs import get_aligned_pair
from analytics.hedge_ratio import compute_static_hedge, compute_dynamic_hedge
from analytics.spread import compute_spread
from analytics.zscore import compute_zscore
from analytics.ADF_test import compute_adf
from analytics.rolling_corr import compute_rolling_corr
from analytics.state import analytics_state
from db.writer import insert_snapshot

def analytics_loop(symbol1="BTCUSDT", symbol2="ETHUSDT", timeframe="1s",
                   rolling_window=30, run_adf=True, regression_type="OLS",
                   dynamic_hedge=False, interval=5):

    while True:
        try:
            df = get_aligned_pair(symbol1, symbol2, timeframe)
            if df.empty or len(df) < rolling_window:
                time.sleep(interval)
                continue

            if dynamic_hedge:
                beta_series = compute_dynamic_hedge(df, symbol1, symbol2)
                hedge_ratio = beta_series[-1] if beta_series is not None else None
            else:
                hedge_ratio = compute_static_hedge(df, symbol1, symbol2, regression_type)

            spread = compute_spread(df, hedge_ratio, symbol1, symbol2)
            if spread is None:
                time.sleep(interval)
                continue

            zscore = compute_zscore(spread, rolling_window)
            corr = compute_rolling_corr(df, symbol1, symbol2, rolling_window)
            adf_p = compute_adf(spread) if run_adf else None

            analytics_state.update({
                "hedge_ratio": hedge_ratio,
                "spread": spread,
                "zscore": zscore,
                "adf_pvalue": adf_p,
                "rolling_corr": corr,
                "low_liquidity": False,
                "alert": False,
                "pnl": None
            })

            insert_snapshot(symbol1, symbol2, timeframe,
                            hedge_ratio, spread.iloc[-1] if spread is not None else None,
                            zscore.iloc[-1] if zscore is not None else None,
                            adf_p,
                            corr.iloc[-1] if corr is not None else None)
        except Exception as e:
            print("Analytics error:", e)
        time.sleep(interval)
