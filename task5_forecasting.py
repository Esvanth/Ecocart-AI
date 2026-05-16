"""
EcoCart Demand Forecasting Prototype
Task 5 — Linear Regression vs Random Forest on synthetic daily sales.

Run:  python3 task5_forecasting.py
Out:  forecast.png, residuals.png, feature_importance.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
RNG = np.random.default_rng(42)


# ── 1. Synthetic sales data ────────────────────────────────
def generate_sales(days=730):
    t = np.arange(days)
    dates = pd.date_range("2023-01-01", periods=days, freq="D")
    base   = 100 + 0.05 * t
    weekly = 25 * np.sin(2 * np.pi * t / 7)
    yearly = 40 * np.sin(2 * np.pi * t / 365)
    noise  = RNG.normal(0, 8, days)
    promo  = np.zeros(days)
    promo[RNG.choice(days, int(days * 0.06), replace=False)] = RNG.uniform(30, 70, int(days * 0.06))
    sales = np.clip(base + weekly + yearly + noise + promo, 0, None)
    return pd.DataFrame({
        "date": dates, "sales": sales,
        "dow": dates.dayofweek, "month": dates.month,
        "day_of_year": dates.dayofyear,
        "is_promo": (promo > 0).astype(int),
    })

# ── 2. Features ────────────────────────────────────────────
def add_features(df):
    out = df.copy()
    for lag in [1, 7, 14]:
        out[f"lag_{lag}"] = out["sales"].shift(lag)
    out["roll_7"]  = out["sales"].shift(1).rolling(7).mean()
    out["roll_30"] = out["sales"].shift(1).rolling(30).mean()
    return out.dropna().reset_index(drop=True)


FEATURES = ["dow", "month", "day_of_year", "is_promo",
            "lag_1", "lag_7", "lag_14", "roll_7", "roll_30"]


# ── 3. Train & evaluate ───────────────────────────────────
def evaluate(name, y_true, y_pred):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, 1, y_true))) * 100
    print(f"  {name:<22s}  MAE={mae:6.2f}  RMSE={rmse:6.2f}  R²={r2:.3f}  MAPE={mape:.2f}%")
    return {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape}


def main():
    print("="*70)
    print("EcoCart Demand Forecasting — LR vs Random Forest")
    print("="*70)

    df = generate_sales()
    df = add_features(df)
    split = int(len(df) * 0.8)
    train, test = df.iloc[:split], df.iloc[split:]
    X_tr, y_tr = train[FEATURES], train["sales"]
    X_te, y_te = test[FEATURES],  test["sales"]
    print(f"Train: {len(train)} days  Test: {len(test)} days")

    lr = LinearRegression().fit(X_tr, y_tr)
    rf = RandomForestRegressor(n_estimators=200, max_depth=12,
                               min_samples_leaf=3, random_state=42,
                               n_jobs=-1).fit(X_tr, y_tr)
    lr_pred = lr.predict(X_te)
    rf_pred = rf.predict(X_te)

    print("\nTest-set metrics:")
    lr_m = evaluate("Linear Regression", y_te.values, lr_pred)
    rf_m = evaluate("Random Forest",     y_te.values, rf_pred)

    # ── Plots ──
    plt.rcParams.update({"axes.facecolor":"#0d1117","figure.facecolor":"#0d1117",
                         "text.color":"white","axes.labelcolor":"white",
                         "xtick.color":"white","ytick.color":"white"})

    # Forecast
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(test.date, y_te, color="#e2e8f0", lw=1.3, label="Actual")
    ax.plot(test.date, lr_pred, color="#3b82f6", lw=1, alpha=0.8, label="Linear Regression")
    ax.plot(test.date, rf_pred, color="#10b981", lw=1, alpha=0.8, label="Random Forest")
    ax.set_title("Test-set: actual vs predicted daily demand", fontsize=12)
    ax.set_xlabel("Date"); ax.set_ylabel("Units sold")
    ax.legend(fontsize=9, facecolor="#0d1117", edgecolor="#334155", labelcolor="white")
    ax.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig("output/forecast.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Residuals
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, pred, name, color, m in [
        (axes[0], lr_pred, "Linear Regression", "#3b82f6", lr_m),
        (axes[1], rf_pred, "Random Forest",     "#10b981", rf_m),
    ]:
        ax.scatter(pred, y_te.values - pred, s=12, c=color, alpha=0.6)
        ax.axhline(0, color="white", lw=0.8)
        ax.set_title(f"{name} residuals (RMSE={m['rmse']:.2f})", fontsize=11)
        ax.set_xlabel("Predicted"); ax.set_ylabel("Residual")
        ax.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig("output/residuals.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Feature importance
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(imp.index, imp.values, color="#10b981")
    ax.set_title("Random Forest — feature importance", fontsize=12)
    ax.set_xlabel("Importance")
    ax.grid(True, axis="x", alpha=0.1)
    plt.tight_layout()
    plt.savefig("output/feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\nTop features: {', '.join(imp.index[-3:][::-1])}")
    print("Wrote: forecast.png, residuals.png, feature_importance.png")

if __name__ == "__main__":
    main()
