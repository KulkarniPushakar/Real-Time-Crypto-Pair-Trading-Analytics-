import numpy as np
from sklearn.linear_model import HuberRegressor, TheilSenRegressor

def compute_static_hedge(df, symbol1, symbol2, regression_type="OLS"):
    if df.empty:
        return None

    y = df[f"log_{symbol1}"].values.ravel()  # <-- flatten to 1D
    x = df[f"log_{symbol2}"].values.reshape(-1, 1)

    if regression_type == "OLS":
        beta = np.polyfit(x.flatten(), y, 1)[0]
    elif regression_type == "Huber":
        model = HuberRegressor(fit_intercept=False).fit(x, y)
        beta = model.coef_[0]
    elif regression_type == "Theil-Sen":
        model = TheilSenRegressor(fit_intercept=False).fit(x, y)
        beta = model.coef_[0]
    else:
        raise ValueError("Invalid regression_type")
    return beta

def compute_dynamic_hedge(df, symbol1, symbol2, delta=1e-5, vt=1e-3):
    if df.empty:
        return None

    y = df[f"log_{symbol1}"].values
    x = df[f"log_{symbol2}"].values

    n = len(y)
    beta = np.zeros(n)
    P = np.zeros(n)
    beta[0] = 0
    P[0] = 1.0

    for t in range(1, n):
        R = P[t-1] + delta
        K = R / (R + vt)
        beta[t] = beta[t-1] + K * (y[t] - beta[t-1] * x[t])
        P[t] = (1 - K) * R
    return beta
