"""Create charts and summary metrics for the Korean IT/SI time-series analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROCESSED = Path("data/processed")
IMAGES = Path("images")
MAIN_INDUSTRY = "computer_programming_system_integration"

INDUSTRY_LABELS = {
    "information_communication": "Information & communication",
    "software_development_supply": "Software development & supply",
    "computer_programming_system_integration": "Programming, SI & management",
    "information_service": "Information services",
}

plt.style.use("ggplot")
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11


def savefig(name: str) -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(IMAGES / name, dpi=160)
    plt.close()
    print(f"[OK] images/{name}")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = [
        PROCESSED / "service_production_long.csv",
        PROCESSED / "job_demand_long.csv",
        PROCESSED / "merged_monthly.csv",
    ]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"먼저 `python3 src/preprocess.py`를 실행하세요. 누락: {missing}")
    service = pd.read_csv(paths[0], parse_dates=["date"])
    jobs = pd.read_csv(paths[1], parse_dates=["date"])
    merged = pd.read_csv(paths[2], parse_dates=["date"])
    return service, jobs, merged


def plot_service_trend(service: pd.DataFrame) -> None:
    df = service[service["index_type"] == "constant_index"].copy()
    df["label"] = df["industry"].map(INDUSTRY_LABELS)
    df["ma12"] = df.groupby("industry")["value"].transform(lambda x: x.rolling(12, min_periods=6).mean())
    plt.figure(figsize=(13, 7))
    for industry, group in df.groupby("industry"):
        label = INDUSTRY_LABELS[industry]
        line = plt.plot(group["date"], group["value"], alpha=0.25, linewidth=1)[0]
        plt.plot(group["date"], group["ma12"], label=label, linewidth=2.2, color=line.get_color())
    plt.axvspan(pd.Timestamp("2020-02-01"), pd.Timestamp("2021-12-01"), color="gray", alpha=0.12)
    plt.title("Service Production Index Trend (constant index + 12M moving average)")
    plt.xlabel("Date")
    plt.ylabel("Index, 2020=100")
    plt.legend(title="Industry", loc="upper left")
    savefig("01_service_trend_constant_index.png")


def plot_seasonality(service: pd.DataFrame) -> None:
    df = service[service["index_type"] == "constant_index"].copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["annual_avg"] = df.groupby(["industry", "year"])["value"].transform("mean")
    df["seasonal_ratio"] = df["value"] / df["annual_avg"] * 100
    df["label"] = df["industry"].map(INDUSTRY_LABELS)
    monthly = df.groupby(["industry", "month"], as_index=False)["seasonal_ratio"].mean()
    plt.figure(figsize=(13, 7))
    for industry, group in monthly.groupby("industry"):
        plt.plot(group["month"], group["seasonal_ratio"], marker="o", linewidth=2, label=INDUSTRY_LABELS[industry])
    plt.axhline(100, color="black", linestyle="--", linewidth=1)
    plt.xticks(range(1, 13))
    plt.title("Average Monthly Seasonality (monthly value / annual average * 100)")
    plt.xlabel("Month")
    plt.ylabel("Seasonal ratio")
    plt.legend(title="Industry")
    savefig("02_monthly_seasonality_by_industry.png")


def plot_current_vs_constant(service: pd.DataFrame) -> None:
    df = service[
        (service["industry"] == MAIN_INDUSTRY)
        & (service["index_type"].isin(["current_index", "constant_index"]))
    ].copy()
    df["label"] = df["index_type"].map({"current_index": "Current index", "constant_index": "Constant index"})
    plt.figure(figsize=(13, 6))
    for label, group in df.groupby("label"):
        plt.plot(group["date"], group["value"], linewidth=2, label=label)
    plt.title("Current vs Constant Index: Programming, SI & Management")
    plt.xlabel("Date")
    plt.ylabel("Index, 2020=100")
    plt.legend(title="Index type")
    savefig("03_current_vs_constant_index.png")


def plot_job_vs_service(merged: pd.DataFrame) -> None:
    cols = {
        "service_computer_programming_system_integration": "Service index: SI-related industry",
        "job_openings_it_broad": "Job openings: broad IT",
        "job_openings_software_developer": "Job openings: software developers",
    }
    df = merged[["date", *cols.keys()]].copy()
    for col in cols:
        df[col] = df[col] / df[col].dropna().iloc[0] * 100
    long = df.melt("date", var_name="series", value_name="indexed_value")
    long["series"] = long["series"].map(cols)
    plt.figure(figsize=(13, 7))
    for label, group in long.groupby("series"):
        plt.plot(group["date"], group["indexed_value"], linewidth=2, label=label)
    plt.axhline(100, color="black", linestyle="--", linewidth=1)
    plt.title("Service Activity vs IT Labor Demand (first month = 100)")
    plt.xlabel("Date")
    plt.ylabel("Indexed value")
    plt.legend(title="Series")
    savefig("04_service_vs_job_demand_indexed.png")


def compute_lag_correlations(merged: pd.DataFrame, max_lag: int = 6) -> pd.DataFrame:
    """Compute lag correlations.

    lag_months > 0: job demand is compared with later months, so service activity leads job demand.
    lag_months < 0: job demand is compared with earlier months, so job demand leads service activity.
    """
    service_col = "service_computer_programming_system_integration"
    job_cols = {
        "job_openings_it_broad": "broad_it",
        "job_openings_software_developer": "software_developer",
    }
    rows = []
    base = merged.sort_values("date").copy()
    for lag in range(-max_lag, max_lag + 1):
        for col, label in job_cols.items():
            tmp = pd.DataFrame({
                "service": base[service_col],
                "job": base[col].shift(-lag),
            }).dropna()
            rows.append({
                "lag_months": lag,
                "job_indicator": label,
                "correlation": tmp["service"].corr(tmp["job"]),
                "n": len(tmp),
            })
    return pd.DataFrame(rows)


def plot_lag_correlation(lag_corr: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))
    labels = {
        "broad_it": "Broad IT openings",
        "software_developer": "Software developer openings",
    }
    for indicator, group in lag_corr.groupby("job_indicator"):
        plt.plot(group["lag_months"], group["correlation"], marker="o", linewidth=2, label=labels[indicator])
    plt.axhline(0, color="black", linewidth=1, linestyle="--")
    plt.axvline(0, color="black", linewidth=1, linestyle=":")
    plt.xticks(range(lag_corr["lag_months"].min(), lag_corr["lag_months"].max() + 1))
    plt.title("Lag Correlation: SI-related Service Index vs IT Job Openings")
    plt.xlabel("Lag months (negative = job demand leads, positive = service activity leads)")
    plt.ylabel("Correlation")
    plt.legend(title="Job indicator")
    savefig("06_lag_correlation_service_vs_jobs.png")


def plot_forecast_error(merged: pd.DataFrame) -> pd.DataFrame:
    df = merged[["date", "service_computer_programming_system_integration"]].copy()
    df = df.rename(columns={"service_computer_programming_system_integration": "actual"})
    df["forecast"] = df["actual"].shift(12)
    df["error"] = df["actual"] - df["forecast"]
    df["abs_pct_error"] = df["error"].abs() / df["actual"] * 100
    eval_df = df.dropna().copy()
    recent = eval_df.tail(12)
    long = recent.melt("date", ["actual", "forecast"], "series", "value")
    long["series"] = long["series"].map({"actual": "Actual", "forecast": "Seasonal naive forecast"})
    fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=False)
    for label, group in long.groupby("series"):
        axes[0].plot(group["date"], group["value"], marker="o", linewidth=2, label=label)
    axes[0].set_title("Seasonal Naive Forecast: Last 12 Months")
    axes[0].set_ylabel("Index, 2020=100")
    axes[0].legend()
    axes[1].bar(recent["date"].dt.strftime("%Y-%m"), recent["abs_pct_error"], color="#d95f02")
    axes[1].set_title("Absolute Percentage Error by Month")
    axes[1].set_ylabel("APE (%)")
    axes[1].tick_params(axis="x", rotation=45)
    savefig("05_seasonal_naive_forecast_error.png")
    return eval_df


def write_metrics(
    service: pd.DataFrame,
    jobs: pd.DataFrame,
    merged: pd.DataFrame,
    forecast: pd.DataFrame,
    lag_corr: pd.DataFrame,
) -> None:
    const = service[service["index_type"] == "constant_index"].copy()
    main = const[const["industry"] == MAIN_INDUSTRY].sort_values("date").copy()
    main["year"] = main["date"].dt.year
    main["month"] = main["date"].dt.month
    main["annual_avg"] = main.groupby("year")["value"].transform("mean")
    main["seasonal_ratio"] = main["value"] / main["annual_avg"] * 100
    march_avg = main[main["month"] == 3]["seasonal_ratio"].mean()
    non_march_avg = main[main["month"] != 3]["seasonal_ratio"].mean()
    start, end = main.iloc[0], main.iloc[-1]
    change_pct = (end["value"] / start["value"] - 1) * 100
    covid = main[(main["date"] >= "2020-02-01") & (main["date"] <= "2021-12-01")]
    covid_min = covid.loc[covid["value"].idxmin()]

    seas = const.copy()
    seas["year"] = seas["date"].dt.year
    seas["seasonal_ratio"] = seas["value"] / seas.groupby(["industry", "year"])["value"].transform("mean") * 100
    variation = seas.groupby("industry")["seasonal_ratio"].std().sort_values(ascending=False)

    corr = merged[[
        "service_computer_programming_system_integration",
        "job_openings_it_broad",
        "job_openings_software_developer",
    ]].corr()
    worst = forecast.sort_values("abs_pct_error", ascending=False).head(5)
    recent_worst = forecast.tail(12).sort_values("abs_pct_error", ascending=False).head(3)

    lines = [
        "# Analysis Metrics", "",
        "## Data coverage",
        f"- Service production index: {service['date'].min().date()} ~ {service['date'].max().date()}, rows={len(service)}",
        f"- Job demand: {jobs['date'].min().date()} ~ {jobs['date'].max().date()}, rows={len(jobs)}",
        f"- Merged monthly table: {merged['date'].min().date()} ~ {merged['date'].max().date()}, rows={len(merged)}", "",
        "## Q1. March concentration, SI-related industry",
        f"- March average seasonal ratio: {march_avg:.2f}",
        f"- Non-March average seasonal ratio: {non_march_avg:.2f}", "",
        "## Q2. Long-term trend and COVID reference period",
        f"- First value ({start['date'].date()}): {start['value']:.1f}",
        f"- Last value ({end['date'].date()}): {end['value']:.1f}",
        f"- Change from first to last: {change_pct:.1f}%",
        f"- Lowest value in 2020-02~2021-12: {covid_min['value']:.1f} at {covid_min['date'].date()}", "",
        "## Q3. Seasonality difference by industry",
    ]
    for industry, value in variation.items():
        lines.append(f"- {INDUSTRY_LABELS[industry]}: seasonal-ratio std={value:.2f}")
    lines += ["", "## Q4. Correlation, service index vs job openings"]
    lines.append(f"- Same-month corr(service, broad IT openings): {corr.iloc[0, 1]:.3f}")
    lines.append(f"- Same-month corr(service, software developer openings): {corr.iloc[0, 2]:.3f}")
    lines.append("- Lag correlation convention: negative lag = job demand leads, positive lag = service activity leads")
    for indicator in ["broad_it", "software_developer"]:
        best = lag_corr[lag_corr["job_indicator"] == indicator].sort_values("correlation", ascending=False).iloc[0]
        worst_lag = lag_corr[lag_corr["job_indicator"] == indicator].sort_values("correlation", ascending=True).iloc[0]
        lines.append(
            f"- Best positive correlation for {indicator}: lag={int(best['lag_months'])}, corr={best['correlation']:.3f}, n={int(best['n'])}"
        )
        lines.append(
            f"- Strongest negative correlation for {indicator}: lag={int(worst_lag['lag_months'])}, corr={worst_lag['correlation']:.3f}, n={int(worst_lag['n'])}"
        )
    lines += ["", "## Q5. Seasonal naive forecast errors", "- Worst 5 months across evaluable period:"]
    for _, row in worst.iterrows():
        lines.append(f"  - {row['date'].date()}: actual={row['actual']:.1f}, forecast={row['forecast']:.1f}, APE={row['abs_pct_error']:.1f}%")
    lines.append("- Worst 3 months in the last 12 months:")
    for _, row in recent_worst.iterrows():
        lines.append(f"  - {row['date'].date()}: actual={row['actual']:.1f}, forecast={row['forecast']:.1f}, APE={row['abs_pct_error']:.1f}%")
    path = PROCESSED / "analysis_metrics.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] {path}")


def main() -> None:
    service, jobs, merged = load_data()
    plot_service_trend(service)
    plot_seasonality(service)
    plot_current_vs_constant(service)
    plot_job_vs_service(merged)
    lag_corr = compute_lag_correlations(merged)
    plot_lag_correlation(lag_corr)
    lag_corr.to_csv(PROCESSED / "lag_correlations.csv", index=False, encoding="utf-8-sig")
    forecast = plot_forecast_error(merged)
    write_metrics(service, jobs, merged, forecast, lag_corr)


if __name__ == "__main__":
    main()
