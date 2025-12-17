CREATE TABLE IF NOT EXISTS analytics_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    symbol1 TEXT,
    symbol2 TEXT,
    timeframe TEXT,
    hedge_ratio REAL,
    spread REAL,
    zscore REAL,
    adf_pvalue REAL,
    rolling_corr REAL
);
