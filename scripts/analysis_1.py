# /// script
# dependencies = ["pandas", "matplotlib"]
# ///
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

fig, ax = plt.subplots(figsize=(12, 5))
daily[["Breastmilk", "Formula"]].plot.area(ax=ax, alpha=0.7)
daily["Total_MA"].plot(ax=ax, color="black", linewidth=2, linestyle="--", label="7-day moving avg")
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

# TODO
# plot total feedings vs weight over time
# plot total feeding vs diaper changes (per type and aggregate) over time