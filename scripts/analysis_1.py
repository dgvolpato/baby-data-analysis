# /// script
# dependencies = ["pandas", "matplotlib", "scipy"]
# ///
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats

df_feedings = pd.read_csv("data/2026-05-16/milo_tracker - Feedings.csv")
df_diapers = pd.read_csv("data/2026-05-16/milo_tracker - Diapers.csv")
df_weights = pd.read_csv("data/2026-05-16/milo_tracker - Weight Log.csv")

# --- Area chart: Formula vs Breastmilk over time ---
df_feedings["Date"] = pd.to_datetime(df_feedings["Date"])

daily = (
    df_feedings[df_feedings["Type"].isin(["Formula", "Breast Milk (bottle)"])]
    .groupby(["Date", "Type"])["Amount (oz)"]
    .sum()
    .unstack(fill_value=0)
    .rename(columns={"Breast Milk (bottle)": "Breastmilk"})
)

daily["Total_MA"] = (daily["Breastmilk"] + daily["Formula"]).rolling(window=7, min_periods=1).mean()
daily["Breastmilk_MA"] = daily["Breastmilk"].rolling(window=3, min_periods=1).mean()
daily["Formula_MA"] = daily["Formula"].rolling(window=3, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(12, 5))
daily[["Breastmilk", "Formula"]].plot.area(ax=ax, alpha=0.7)
daily["Total_MA"].plot(ax=ax, color="black", linewidth=2, linestyle="--", label="7-day total avg")
daily["Breastmilk_MA"].plot(ax=ax, color="steelblue", linewidth=2, linestyle="-", label="3-day breastmilk avg")
daily["Formula_MA"].plot(ax=ax, color="darkorange", linewidth=2, linestyle="-", label="3-day formula avg")
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_minor_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", labelrotation=45)
ax.legend()
ax.set_xlabel("Date")
ax.set_ylabel("Amount (oz)")
ax.set_title("Daily Feedings: Formula vs Breastmilk")
plt.tight_layout()
plt.savefig("output/feedings_formula_vs_breastmilk.png", dpi=150)
plt.close()

# --- Feeding vs Weight over time ---
df_weights["Date"] = pd.to_datetime(df_weights["Date"])
df_weights = df_weights.set_index("Date").sort_index()

# Interpolate weight to daily frequency within the measured range
daily_index = pd.date_range(df_weights.index.min(), df_weights.index.max(), freq="D")
weight_daily = df_weights["Weight (lbs)"].reindex(daily_index).interpolate(method="linear")

daily_total = (daily["Breastmilk"] + daily["Formula"]).rename("Total")
weight_gain = weight_daily.diff().rename("Weight Gain (lbs/day)")

merged = pd.concat([daily_total, weight_daily, weight_gain], axis=1).dropna()

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()

ax1.bar(merged.index, merged["Total"], color="steelblue", alpha=0.5, label="Total feeding (oz)")
ax2.plot(weight_daily.index, weight_daily.values, color="darkorange", linewidth=2, label="Weight (lbs)")

ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax1.xaxis.set_minor_locator(mdates.DayLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax1.tick_params(axis="x", labelrotation=45)
ax1.set_xlabel("Date")
ax1.set_ylabel("Total Feeding (oz)")
ax2.set_ylabel("Weight (lbs)")
ax1.set_title("Daily Feeding vs Weight Over Time")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2)

plt.tight_layout()
plt.savefig("output/feedings_vs_weight.png", dpi=150)
plt.close()

# Correlation: daily feeding vs next-day weight gain
r, p = stats.pearsonr(merged["Total"], merged["Weight Gain (lbs/day)"])
print("Correlation: daily feeding vs next-day weight gain:")
print(f"\tPearson r = {r:.3f}, p-value = {p:.3f} (n={len(merged)})\n")

# Scatter plots: rolling avg feeding vs weight gain over the same window (3–7 days)
fig, axes = plt.subplots(1, 5, figsize=(18, 4), sharey=True)

for ax, window in zip(axes, range(3, 8)):
    feeding_avg = daily_total.rolling(window).mean()
    weight_gain_window = weight_daily - weight_daily.shift(window)
    df_window = pd.concat([feeding_avg, weight_gain_window], axis=1).dropna()
    df_window.columns = ["feeding_avg", "weight_gain"]

    r_w, p_w = stats.pearsonr(df_window["feeding_avg"], df_window["weight_gain"])

    ax.scatter(df_window["feeding_avg"], df_window["weight_gain"], alpha=0.6)

    slope, intercept, *_ = stats.linregress(df_window["feeding_avg"], df_window["weight_gain"])
    x_line = pd.Series([df_window["feeding_avg"].min(), df_window["feeding_avg"].max()])
    ax.plot(x_line, slope * x_line + intercept, color="red", linewidth=1.5)

    ax.set_title(f"{window}-day window\nr={r_w:.2f}, p={p_w:.3f}")
    ax.set_xlabel("Avg feeding (oz)")

axes[0].set_ylabel("Weight gain (lbs)")
fig.suptitle("Avg Daily Feeding vs Weight Gain by Window Size", y=1.02)
plt.tight_layout()
plt.savefig("output/feeding_vs_weight_gain_windows.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Feeding vs Diaper changes over time ---
df_diapers["Date"] = pd.to_datetime(df_diapers["Date"])

daily_diapers = pd.DataFrame(index=pd.DatetimeIndex(sorted(df_diapers["Date"].unique())))
daily_diapers["Wet"] = df_diapers[df_diapers["Type"].isin(["Wet", "Wet + Poop"])].groupby("Date").size()
daily_diapers["Poop"] = df_diapers[df_diapers["Type"].isin(["Poop", "Wet + Poop"])].groupby("Date").size()
daily_diapers = daily_diapers.fillna(0).sort_index()
daily_diapers["Total"] = daily_diapers["Wet"] + daily_diapers["Poop"]

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()

ax1.bar(daily_diapers.index, daily_diapers["Wet"], label="Wet", alpha=0.6, color="steelblue")
ax1.bar(daily_diapers.index, daily_diapers["Poop"], bottom=daily_diapers["Wet"], label="Poop", alpha=0.6, color="sienna")
ax2.plot(daily_total.index, daily_total.values, color="black", linewidth=2, label="Total feeding (oz)")

ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax1.xaxis.set_minor_locator(mdates.DayLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax1.tick_params(axis="x", labelrotation=45)
ax1.set_xlabel("Date")
ax1.set_ylabel("Diaper count")
ax2.set_ylabel("Total feeding (oz)")
ax1.set_title("Daily Diaper Changes vs Feeding")

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2)

plt.tight_layout()
plt.savefig("output/diapers_vs_feeding.png", dpi=150)
plt.close()

# Correlations
for col, label in [("Wet", "Wet diapers"), ("Poop", "Poop diapers"), ("Total", "Total diapers")]:
    df_corr = pd.concat([daily_diapers[col], daily_total], axis=1).dropna()
    df_corr.columns = [col, "feeding"]
    r_d, p_d = stats.pearsonr(df_corr[col], df_corr["feeding"])
    print(f"{label:15s} vs feeding — r={r_d:.3f}, p={p_d:.3f} (n={len(df_corr)})")

# --- Lagged correlation: feeding vs diapers (same day and next day) ---
diaper_cols = [("Wet", "Wet"), ("Poop", "Poop"), ("Total", "Total")]
lags = [0, 1]
bar_width = 0.3
x = range(len(diaper_cols))

fig, ax = plt.subplots(figsize=(8, 5))

for i, lag in enumerate(lags):
    r_values, p_values = [], []
    for col, _ in diaper_cols:
        df_lag = pd.concat([daily_total, daily_diapers[col].shift(-lag)], axis=1).dropna()
        df_lag.columns = ["feeding", col]
        r_l, p_l = stats.pearsonr(df_lag["feeding"], df_lag[col])
        r_values.append(r_l)
        p_values.append(p_l)

    offset = (i - len(lags) / 2 + 0.5) * bar_width
    bars = ax.bar([xi + offset for xi in x], r_values, width=bar_width,
                  label=f"Lag {lag} ({'same day' if lag == 0 else 'next day'})", alpha=0.7)

    for bar, p_val in zip(bars, p_values):
        marker = "**" if p_val < 0.01 else ("*" if p_val < 0.05 else "")
        if marker:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    marker, ha="center", va="bottom", fontsize=11)

ax.set_xticks(list(x))
ax.set_xticklabels([label for _, label in diaper_cols])
ax.set_ylabel("Pearson r")
ax.set_title("Feeding vs Diaper Correlation by Lag\n(* p<0.05, ** p<0.01)")
ax.axhline(0, color="black", linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.savefig("output/diaper_feeding_lag_correlation.png", dpi=150)
plt.close()

# --- Rebound effect: heavy feeding day → fewer diapers / less feeding next day ---
df_rebound = pd.concat([
    daily_total.rename("feeding_today"),
    daily_diapers["Total"].shift(-1).rename("diapers_tomorrow"),
    daily_total.shift(-1).rename("feeding_tomorrow"),
], axis=1).dropna()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, y_col, y_label, title in [
    (axes[0], "diapers_tomorrow", "Total diapers (next day)", "Feeding today vs Diapers tomorrow"),
    (axes[1], "feeding_tomorrow", "Total feeding tomorrow (oz)", "Feeding today vs Feeding tomorrow"),
]:
    r_r, p_r = stats.pearsonr(df_rebound["feeding_today"], df_rebound[y_col])
    slope, intercept, *_ = stats.linregress(df_rebound["feeding_today"], df_rebound[y_col])
    x_line = pd.Series([df_rebound["feeding_today"].min(), df_rebound["feeding_today"].max()])

    ax.scatter(df_rebound["feeding_today"], df_rebound[y_col], alpha=0.6)
    ax.plot(x_line, slope * x_line + intercept, color="red", linewidth=1.5)
    ax.set_xlabel("Total feeding today (oz)")
    ax.set_ylabel(y_label)
    ax.set_title(f"{title}\nr={r_r:.3f}, p={p_r:.3f} (n={len(df_rebound)})")

plt.tight_layout()
plt.savefig("output/rebound_effect.png", dpi=150)
plt.close()