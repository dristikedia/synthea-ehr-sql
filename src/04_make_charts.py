"""Draw charts from the result tables made by 03_run_queries.py.

Run from the project folder:
    python src/04_make_charts.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # DRAW TO FILES, NO WINDOW NEEDED
import matplotlib.pyplot as plt
import pandas as pd

# SETTINGS
PROJECT_DIR = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_DIR / "results" / "tables"
CHARTS_DIR = PROJECT_DIR / "results" / "charts"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREY = "#8a8985"
CLASS_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#8a8985"]
NEEDED_TABLES = [
    "05_encounters_per_year",
    "07_encounter_types_by_age_group",
    "09_diabetes_comorbidities",
    "11_oral_conditions_by_diabetes",
]


def style_axes(ax):
    """Light, quiet axes so the data stands out."""
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GREY)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(colors="#52514e")
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)


def top_classes_with_other(df, keep):
    """Keep the listed encounter classes and add everything else together as 'other'."""
    df = df.copy()
    df["class_group"] = df["encounter_class"].where(df["encounter_class"].isin(keep), "other")
    table = df.pivot_table(
        index="age_group", columns="class_group", values="pct_within_age_group",
        aggfunc="sum", fill_value=0,
    )
    columns = [c for c in keep if c in table.columns]
    if "other" in table.columns:
        columns.append("other")
    return table[columns]


def chart_encounters_per_year(df, path):
    """Bars of encounters per year; the partial last year is lighter."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    complete = df[df["is_partial_year"] == 0]
    partial = df[df["is_partial_year"] == 1]
    ax.bar(complete["year"].astype(str), complete["encounters"], color=BLUE, width=0.7)
    ax.bar(partial["year"].astype(str), partial["encounters"], color="#a9c8ee", width=0.7,
           label="Partial year (data ends mid-year)")
    style_axes(ax)
    ax.set_title("Encounters per year", loc="left", fontsize=13)
    ax.set_ylabel("Encounters")
    if not partial.empty:
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def chart_encounter_mix_by_age(df, path):
    """100% stacked bars: the mix of encounter classes inside each age group."""
    keep = ["ambulatory", "wellness", "outpatient", "emergency", "urgentcare"]
    table = top_classes_with_other(df, keep)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = pd.Series(0.0, index=table.index)
    for color, column in zip(CLASS_COLORS, table.columns):
        ax.bar(table.index, table[column], bottom=bottom, color=color, label=column,
               edgecolor="white", linewidth=1.5, width=0.6)
        bottom = bottom + table[column]
    style_axes(ax)
    ax.set_ylim(0, 100)
    ax.set_title("Encounter types by age group (percent of each group's encounters)", loc="left", fontsize=13)
    ax.set_xlabel("Age at encounter")
    ax.set_ylabel("Percent of encounters")
    # REVERSE THE LEGEND SO ITS ORDER MATCHES THE STACK (TOP SEGMENT LISTED FIRST)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def chart_comorbidities(df, group_sizes, path):
    """Paired horizontal bars: percent of diabetic vs other patients with each disorder."""
    df = df.iloc[::-1]  # LARGEST AT THE TOP
    positions = range(len(df))
    height = 0.38
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh([p + height / 2 for p in positions], df["pct_of_diabetic"], height=height,
            color=BLUE, label=f"Diabetic patients (n = {group_sizes['Diabetic']})")
    ax.barh([p - height / 2 for p in positions], df["pct_of_not_diabetic"], height=height,
            color=ORANGE, label=f"Other patients (n = {group_sizes['Not diabetic']})")
    labels = df["disorder"].str.replace(" (disorder)", "", regex=False)
    ax.set_yticks(list(positions))
    ax.set_yticklabels(labels)
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#e6e5e0", linewidth=0.8)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percent of patients in the group")
    ax.set_title("Most common disorders in diabetic patients vs other patients", loc="left", fontsize=13)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def chart_oral_conditions(df, path):
    """Grouped bars: gum disease, caries, and tooth loss by diabetes status."""
    conditions = [("gum_disease_pct", "Gum disease"), ("caries_pct", "Dental caries"),
                  ("tooth_loss_pct", "Tooth loss")]
    df = df.set_index("patient_group")
    positions = range(len(conditions))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for offset, group, color in [(-width / 2, "Diabetic", BLUE), (width / 2, "Not diabetic", ORANGE)]:
        if group not in df.index:
            continue
        values = [df.at[group, column] for column, _ in conditions]
        n = df.at[group, "patients"]
        bars = ax.bar([p + offset for p in positions], values, width=width, color=color,
                      label=f"{group} (n = {n})")
        ax.bar_label(bars, fmt="%.0f%%", padding=2, color="#52514e", fontsize=9)
    ax.set_xticks(list(positions))
    ax.set_xticklabels([label for _, label in conditions])
    style_axes(ax)
    ax.set_ylim(0, 110)
    ax.set_ylabel("Percent of patients")
    ax.set_title("Oral conditions recorded, by diabetes status", loc="left", fontsize=13)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    # CHECK THE TABLES EXIST
    missing = [name for name in NEEDED_TABLES if not (TABLES_DIR / f"{name}.csv").exists()]
    if missing:
        print(f"ERROR: missing result tables: {', '.join(missing)}")
        print("Fix: run  python src/03_run_queries.py  first.")
        sys.exit(1)

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    tables = {name: pd.read_csv(TABLES_DIR / f"{name}.csv") for name in NEEDED_TABLES}

    # DRAW EACH CHART
    chart_encounters_per_year(tables["05_encounters_per_year"], CHARTS_DIR / "01_encounters_per_year.png")
    chart_encounter_mix_by_age(tables["07_encounter_types_by_age_group"], CHARTS_DIR / "02_encounter_types_by_age.png")
    sizes = tables["11_oral_conditions_by_diabetes"].set_index("patient_group")["patients"].to_dict()
    chart_comorbidities(tables["09_diabetes_comorbidities"], sizes, CHARTS_DIR / "03_diabetes_comorbidities.png")
    chart_oral_conditions(tables["11_oral_conditions_by_diabetes"], CHARTS_DIR / "04_oral_conditions_by_diabetes.png")

    for path in sorted(CHARTS_DIR.glob("*.png")):
        print(f"Saved {path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
