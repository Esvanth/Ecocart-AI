"""
EcoCart Customer Segmentation — Bias Detection & Mitigation
Task 2 — Demonstrates urban-rural bias in K-Means segmentation and
          applies reweighing to fix it.

Run:  python3 task2_segmentation.py
Out:  bias_before_after.png, disparate_impact.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

RNG = np.random.default_rng(42)
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "customers.csv")


def load_customers():
    """Load the 400-customer dataset from data/customers.csv."""
    return pd.read_csv(CSV_PATH)

# 1. Generate biased customer data 
# Urban customers have more data, higher frequency, higher spend — mimicking
# a real scenario where the platform launched in cities first.

def generate_biased_data(n_urban=300, n_rural=100):
    # Urban: higher frequency and spend on average
    urban = pd.DataFrame({
        "freq":     RNG.normal(6.0, 2.0, n_urban).clip(0.5),
        "spend":    RNG.normal(120, 40, n_urban).clip(10),
        "recency":  RNG.exponential(10, n_urban).clip(1, 90),
        "region":   "urban",
    })
    # Rural: lower frequency and spend (platform is newer there)
    rural = pd.DataFrame({
        "freq":     RNG.normal(3.0, 1.5, n_rural).clip(0.5),
        "spend":    RNG.normal(65, 30, n_rural).clip(10),
        "recency":  RNG.exponential(15, n_rural).clip(1, 90),
        "region":   "rural",
    })
    df = pd.concat([urban, rural], ignore_index=True)
    df["freq"] = df["freq"].round(1)
    df["spend"] = df["spend"].round(0)
    df["recency"] = df["recency"].round(0)
    return df


# ── 2. Segment with K-Means ────────────────────────────────
def segment(df, features=["freq", "spend", "recency"]):
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    df = df.copy()
    df["cluster"] = km.fit_predict(X)

    # Label clusters by mean spend (High/Medium/Low)
    means = df.groupby("cluster")["spend"].mean().sort_values(ascending=False)
    label_map = {means.index[0]: "High Value",
                 means.index[1]: "Medium",
                 means.index[2]: "Low Value"}
    df["segment"] = df["cluster"].map(label_map)
    return df

# ── 3. Bias metrics ────────────────────────────────────────
def compute_fairness(df):
    urban = df[df.region == "urban"]
    rural = df[df.region == "rural"]
    u_high = (urban.segment == "High Value").mean()
    r_high = (rural.segment == "High Value").mean()
    di = r_high / u_high if u_high > 0 else 0
    return {
        "urban_high_pct": round(u_high * 100, 1),
        "rural_high_pct": round(r_high * 100, 1),
        "disparate_impact": round(di, 3),
        "fair": di >= 0.8,
    }

# ── 4. Mitigation: reweigh + balanced re-sample ────────────
def mitigate(df):
    """
    Fix 1: Balance the dataset by oversampling rural customers.
    Fix 2: Add a 'distance_adjusted_spend' feature that normalises
           spend by delivery cost (rural customers pay more for delivery,
           so their raw spend understates their purchase intent).
    Fix 3: Post-processing — reassign borderline rural customers using
           a lowered threshold derived from the rural spend distribution.
    """
    df = df.copy()

    # Oversample rural to match urban count
    rural = df[df.region == "rural"]
    urban = df[df.region == "urban"]
    rural_up = rural.sample(n=len(urban), replace=True, random_state=42)
    balanced = pd.concat([urban, rural_up], ignore_index=True)

    # Adjust spend: rural delivery costs ~€12 more on average
    balanced["adj_spend"] = balanced.apply(
        lambda r: r["spend"] + 12 if r["region"] == "rural" else r["spend"],
        axis=1,
    )
    # Adjust frequency: rural customers batch orders
    balanced["adj_freq"] = balanced.apply(
        lambda r: r["freq"] * 1.5 if r["region"] == "rural" else r["freq"],
        axis=1,
    )

    # Re-segment on adjusted features
    scaler = StandardScaler()
    X = scaler.fit_transform(balanced[["adj_freq", "adj_spend", "recency"]])
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    balanced["cluster"] = km.fit_predict(X)
    means = balanced.groupby("cluster")["adj_spend"].mean().sort_values(ascending=False)
    label_map = {means.index[0]: "High Value",
                 means.index[1]: "Medium",
                 means.index[2]: "Low Value"}
    balanced["segment"] = balanced["cluster"].map(label_map)

    # Post-processing: promote top rural "Medium" and "Low Value" customers
    # to "High Value" until disparate impact reaches 0.85 (above 0.8 threshold)
    rural_mask = balanced.region == "rural"
    urban_mask = balanced.region == "urban"
    urban_high_rate = (balanced[urban_mask].segment == "High Value").mean()
    target_rate = urban_high_rate * 0.85
    n_rural = rural_mask.sum()
    target_rural_high = int(target_rate * n_rural)
    current_rural_high = ((balanced[rural_mask].segment == "High Value")).sum()
    need = target_rural_high - current_rural_high
    if need > 0:
        # Promote from Medium first, then Low Value
        candidates = balanced[rural_mask & (balanced.segment != "High Value")]
        if len(candidates) > 0:
            promote = candidates.nlargest(min(need, len(candidates)), "adj_spend").index
            balanced.loc[promote, "segment"] = "High Value"
    return balanced


# ── 5. Plots ────────────────────────────────────────────────
SEG_COLORS = {"High Value": "#10b981", "Medium": "#f59e0b", "Low Value": "#ef4444"}
def plot_before_after(before_df, after_df, before_fair, after_fair):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.patch.set_facecolor("#0d1117")
    for ax, df, fair, title in [
        (axes[0], before_df, before_fair, "BEFORE mitigation (biased)"),
        (axes[1], after_df,  after_fair,  "AFTER mitigation (reweighed + adjusted)"),
    ]:
        ax.set_facecolor("#0d1117")
        for seg in ["High Value", "Medium", "Low Value"]:
            mask = df.segment == seg
            for region, marker in [("urban", "o"), ("rural", "^")]:
                rmask = mask & (df.region == region)
                ax.scatter(df.loc[rmask, "freq"], df.loc[rmask, "spend"],
                           c=SEG_COLORS[seg], marker=marker, s=25, alpha=0.6,
                           label=f"{seg} ({region})" if ax == axes[0] else None)
        di = fair["disparate_impact"]
        color = "#ef4444" if not fair["fair"] else "#10b981"
        ax.set_title(f"{title}\nDI = {di:.3f} {'⚠ BIASED' if not fair['fair'] else '✓ FAIR'}",
                     color="white", fontsize=11)
        ax.set_xlabel("Purchase frequency / month", color="white")
        ax.set_ylabel("Avg spend (€)", color="white")
        ax.tick_params(colors="white")
        ax.grid(True, alpha=0.1, color="white")

    axes[0].legend(fontsize=7, facecolor="#0d1117", edgecolor="#334155",
                   labelcolor="white", loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig("output/bias_before_after.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    plt.close()

def plot_di(before_fair, after_fair):
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    cats = ["Urban → High", "Rural → High", "Disparate Impact"]
    before_vals = [before_fair["urban_high_pct"], before_fair["rural_high_pct"],
                   before_fair["disparate_impact"] * 100]
    after_vals  = [after_fair["urban_high_pct"],  after_fair["rural_high_pct"],
                   after_fair["disparate_impact"] * 100]
    x = range(len(cats))
    w = 0.35
    ax.bar([i - w/2 for i in x], before_vals, w, label="Before", color="#ef4444", alpha=0.85)
    ax.bar([i + w/2 for i in x], after_vals,  w, label="After",  color="#10b981", alpha=0.85)
    ax.axhline(80, color="#fbbf24", linewidth=1.5, linestyle="--", label="DI threshold (80%)")
    ax.set_xticks(x)
    ax.set_xticklabels(cats, color="white")
    ax.set_ylabel("Percentage", color="white")
    ax.set_title("Fairness metrics before vs after mitigation", color="white", fontsize=12)
    ax.tick_params(colors="white")
    ax.legend(fontsize=9, facecolor="#0d1117", edgecolor="#334155", labelcolor="white")
    ax.grid(True, axis="y", alpha=0.15, color="white")
    plt.tight_layout()
    plt.savefig("output/disparate_impact.png", dpi=150,
                bbox_inches="tight", facecolor="#0d1117")
    plt.close()


# ── 6. Main ─────────────────────────────────────────────────
def main():
    print("="*70)
    print("EcoCart Customer Segmentation — Bias Detection & Mitigation")
    print("="*70)

    # Load and segment (biased)
    df = load_customers()
    df = segment(df)
    before = compute_fairness(df)
    print(f"\nBEFORE mitigation:")
    print(f"  Urban -> High Value: {before['urban_high_pct']}%")
    print(f"  Rural -> High Value: {before['rural_high_pct']}%")
    print(f"  Disparate Impact:   {before['disparate_impact']}")
    print(f"  Fair (DI >= 0.8)?   {before['fair']}")

    print(f"\n  Segment counts:")
    ct = df.groupby(["region", "segment"]).size().unstack(fill_value=0)
    print(ct.to_string(index=True))

    # Mitigate
    fixed = mitigate(df)
    after = compute_fairness(fixed)
    print(f"\nAFTER mitigation:")
    print(f"  Urban -> High Value: {after['urban_high_pct']}%")
    print(f"  Rural -> High Value: {after['rural_high_pct']}%")
    print(f"  Disparate Impact:   {after['disparate_impact']}")
    print(f"  Fair (DI >= 0.8)?   {after['fair']}")

    # Plots
    plot_before_after(df, fixed, before, after)
    plot_di(before, after)
    print("\nWrote: bias_before_after.png, disparate_impact.png")

if __name__ == "__main__":
    main()
