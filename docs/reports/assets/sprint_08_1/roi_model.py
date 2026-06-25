from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ALERT_RATE = 3704 / 8788
DISCOUNT_RATE = 0.10
HOURS_PER_FTE_YEAR = 1920
OUTPUT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Scenario:
    name: str
    applications_per_month: int
    baseline_minutes_per_app: float
    screen_minutes_per_app: float
    extra_review_minutes_for_alerted_cases: float
    loaded_hourly_cost: float
    realization_rate: float
    implementation_cost: float
    annual_operating_cost: float


SCENARIOS = [
    Scenario(
        name="Worst",
        applications_per_month=8000,
        baseline_minutes_per_app=9.5,
        screen_minutes_per_app=4.5,
        extra_review_minutes_for_alerted_cases=8.5,
        loaded_hourly_cost=30,
        realization_rate=0.60,
        implementation_cost=60000,
        annual_operating_cost=45000,
    ),
    Scenario(
        name="Expected",
        applications_per_month=10000,
        baseline_minutes_per_app=10.0,
        screen_minutes_per_app=4.0,
        extra_review_minutes_for_alerted_cases=8.0,
        loaded_hourly_cost=35,
        realization_rate=0.75,
        implementation_cost=49270,
        annual_operating_cost=38400,
    ),
    Scenario(
        name="Best",
        applications_per_month=12000,
        baseline_minutes_per_app=11.0,
        screen_minutes_per_app=3.5,
        extra_review_minutes_for_alerted_cases=7.5,
        loaded_hourly_cost=40,
        realization_rate=0.90,
        implementation_cost=42000,
        annual_operating_cost=34000,
    ),
]


def compute_metrics(scenario: Scenario) -> dict[str, float | str]:
    ai_minutes_per_app = (
        scenario.screen_minutes_per_app
        + ALERT_RATE * scenario.extra_review_minutes_for_alerted_cases
    )
    time_saved_per_app = scenario.baseline_minutes_per_app - ai_minutes_per_app

    baseline_hours_per_month = (
        scenario.applications_per_month * scenario.baseline_minutes_per_app / 60
    )
    ai_hours_per_month = scenario.applications_per_month * ai_minutes_per_app / 60
    hours_saved_per_month = baseline_hours_per_month - ai_hours_per_month
    hours_saved_per_year = hours_saved_per_month * 12
    monetized_hours_saved_per_year = hours_saved_per_year * scenario.realization_rate

    baseline_annual_labor_cost = (
        baseline_hours_per_month * scenario.loaded_hourly_cost * 12
    )
    ai_annual_labor_cost = ai_hours_per_month * scenario.loaded_hourly_cost * 12
    theoretical_annual_labor_savings = baseline_annual_labor_cost - ai_annual_labor_cost
    gross_annual_benefit = (
        monetized_hours_saved_per_year * scenario.loaded_hourly_cost
    )

    year1_total_cost = (
        scenario.implementation_cost + scenario.annual_operating_cost
    )
    recurring_annual_net_benefit = gross_annual_benefit - scenario.annual_operating_cost
    year1_net_benefit = gross_annual_benefit - year1_total_cost
    year1_roi_pct = (year1_net_benefit / year1_total_cost) * 100

    if recurring_annual_net_benefit <= 0:
        payback_months = float("inf")
    else:
        payback_months = scenario.implementation_cost / (
            recurring_annual_net_benefit / 12
        )

    npv_3yr = -scenario.implementation_cost
    for year in range(1, 4):
        npv_3yr += recurring_annual_net_benefit / ((1 + DISCOUNT_RATE) ** year)

    return {
        "scenario": scenario.name,
        "applications_per_month": scenario.applications_per_month,
        "alert_rate": ALERT_RATE,
        "baseline_manual_reviews_per_month": scenario.applications_per_month,
        "ai_deep_reviews_per_month": scenario.applications_per_month * ALERT_RATE,
        "ai_fast_track_reviews_per_month": scenario.applications_per_month
        * (1 - ALERT_RATE),
        "baseline_minutes_per_app": scenario.baseline_minutes_per_app,
        "ai_minutes_per_app": ai_minutes_per_app,
        "time_saved_per_app": time_saved_per_app,
        "baseline_hours_per_month": baseline_hours_per_month,
        "ai_hours_per_month": ai_hours_per_month,
        "hours_saved_per_month": hours_saved_per_month,
        "hours_saved_per_year": hours_saved_per_year,
        "monetized_hours_saved_per_year": monetized_hours_saved_per_year,
        "fte_capacity_freed_theoretical": hours_saved_per_year / HOURS_PER_FTE_YEAR,
        "fte_capacity_freed_monetized": monetized_hours_saved_per_year
        / HOURS_PER_FTE_YEAR,
        "loaded_hourly_cost": scenario.loaded_hourly_cost,
        "realization_rate": scenario.realization_rate,
        "baseline_annual_labor_cost": baseline_annual_labor_cost,
        "ai_annual_labor_cost": ai_annual_labor_cost,
        "theoretical_annual_labor_savings": theoretical_annual_labor_savings,
        "gross_annual_benefit": gross_annual_benefit,
        "implementation_cost": scenario.implementation_cost,
        "annual_operating_cost": scenario.annual_operating_cost,
        "year1_total_cost": year1_total_cost,
        "year1_net_benefit": year1_net_benefit,
        "year1_roi_pct": year1_roi_pct,
        "recurring_annual_net_benefit": recurring_annual_net_benefit,
        "payback_months": payback_months,
        "npv_3yr": npv_3yr,
    }


def write_summary_csv(rows: list[dict[str, float | str]]) -> None:
    output_path = OUTPUT_DIR / "roi_scenario_summary.csv"
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_workload_chart(expected: dict[str, float | str]) -> None:
    labels = ["Baseline", "With AutoGuard AI", "Saved"]
    values = [
        float(expected["baseline_hours_per_month"]),
        float(expected["ai_hours_per_month"]),
        float(expected["hours_saved_per_month"]),
    ]
    colors = ["#8f5e3b", "#2a6f97", "#4c956c"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Expected Case Monthly Underwriting Hours")
    ax.set_ylabel("Hours per month")
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 15,
            f"{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "expected_case_workload_hours.png", dpi=200)
    plt.close(fig)


def plot_roi_chart(rows: list[dict[str, float | str]]) -> None:
    labels = [str(row["scenario"]) for row in rows]
    roi_values = [float(row["year1_roi_pct"]) for row in rows]
    colors = ["#b56576" if value < 0 else "#6d597a" for value in roi_values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, roi_values, color=colors)
    ax.axhline(0, color="#333333", linewidth=1)
    ax.set_title("First-Year ROI Sensitivity")
    ax.set_ylabel("ROI (%)")
    ax.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, roi_values):
        offset = 8 if value >= 0 else -14
        va = "bottom" if value >= 0 else "top"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            f"{value:.1f}%",
            ha="center",
            va=va,
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "roi_sensitivity.png", dpi=200)
    plt.close(fig)


def main() -> None:
    rows = [compute_metrics(scenario) for scenario in SCENARIOS]
    write_summary_csv(rows)
    expected_row = next(row for row in rows if row["scenario"] == "Expected")
    plot_workload_chart(expected_row)
    plot_roi_chart(rows)


if __name__ == "__main__":
    main()
