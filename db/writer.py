from db.sqlite import get_connection

def insert_snapshot(
    symbol1,
    symbol2,
    timeframe,
    hedge_ratio,
    spread,
    zscore,
    adf_pvalue,
    rolling_corr
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analytics_snapshot
        (symbol1, symbol2, timeframe, hedge_ratio, spread, zscore, adf_pvalue, rolling_corr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (symbol1, symbol2, timeframe, hedge_ratio, spread, zscore, adf_pvalue, rolling_corr))
    conn.commit()
    conn.close()
