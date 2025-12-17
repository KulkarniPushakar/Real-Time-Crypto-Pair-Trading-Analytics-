import pandas as pd

class MeanReversionBacktest:
    def __init__(self, spread, zscore, entry_z=2, exit_z=0):
        self.spread = spread
        self.zscore = zscore
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.trades = []

    def run(self):
        position = 0
        entry_price = 0
        for ts, z, s in zip(self.spread.index, self.zscore, self.spread):
            if position == 0:
                if abs(z) > self.entry_z:
                    position = -1 if z > 0 else 1
                    entry_price = s
                    self.trades.append({
                        "entry_time": ts,
                        "entry_price": entry_price,
                        "position": position,
                        "exit_time": None,
                        "exit_price": None,
                        "pnl": None
                    })
            else:
                if (position == 1 and z < self.exit_z) or (position == -1 and z > -self.exit_z):
                    exit_price = s
                    trade = self.trades[-1]
                    trade["exit_time"] = ts
                    trade["exit_price"] = exit_price
                    trade["pnl"] = (exit_price - trade["entry_price"]) * trade["position"]
                    position = 0
        return pd.DataFrame(self.trades)

    def summary(self):
        df = pd.DataFrame(self.trades).dropna(subset=["pnl"])
        total_trades = len(df)
        win_rate = (df["pnl"] > 0).mean() if total_trades > 0 else 0
        cum_pnl = df["pnl"].sum() if total_trades > 0 else 0
        return {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "cumulative_pnl": cum_pnl
        }
