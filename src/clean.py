"""
Phase 1: clean the raw College Scorecard file.

Run from the project folder:
    .venv/bin/python src/clean.py

Output: data/clean_colleges.csv (one row per college).
"""

import pandas as pd

import config


def load_raw(path=config.RAW_CSV):
    """Read only the columns we need, turning 'NULL', 'PS', etc. into NaN."""
    df = pd.read_csv(
        path,
        usecols=list(config.COLUMN_RENAMES.keys()),
        na_values=config.NULL_MARKERS,
        low_memory=False,
    )
    return df.rename(columns=config.COLUMN_RENAMES)


def filter_schools(df, keep_for_profit=False):
    """Keep open, mostly-bachelor's colleges. Drop for-profits unless asked."""
    df = df[df["pred_degree"] == 3]
    df = df[df["currently_operating"] == 1]
    if not keep_for_profit:
        df = df[df["control"].isin([1, 2])]
    return df


def add_net_price(df):
    """Public and private schools report net price in different columns.
    Each school fills only one, so we combine them into a single column."""
    df = df.copy()
    df["net_price"] = df["net_price_public"].fillna(df["net_price_private"])
    return df.drop(columns=["net_price_public", "net_price_private"])


def add_extra_columns(df):
    """Small helper columns that later phases use."""
    df = df.copy()
    df["control_label"] = df["control"].map(config.CONTROL_LABELS)
    # Many schools are test-optional and don't report SAT. We keep a flag
    # so the model can tell "missing" apart from "low".
    df["sat_missing"] = df["sat_avg"].isna().astype(int)
    # Positive = Pell students graduate at a HIGHER rate than everyone else
    df["pell_gap"] = df["pell_grad_rate"] - df["grad_rate"]
    return df.drop(columns=["pred_degree", "currently_operating"])


def drop_missing_outcomes(df):
    """Drop schools that are missing any required outcome."""
    return df.dropna(subset=config.REQUIRED_OUTCOMES)


def drop_small_cohorts(df):
    """Drop schools whose grad rate comes from too few students to trust."""
    return df[df["grad_cohort_size"] >= config.MIN_GRAD_COHORT]


def print_summary(df, start_rows):
    """Print row counts, a missing-value table, and Boston University's row."""
    print(f"Raw rows:   {start_rows:,}")
    print(f"Clean rows: {len(df):,}")
    print("\nBy type:")
    print(df["control_label"].value_counts().to_string())

    print("\nMissing values (% of clean rows):")
    missing = (df.isna().mean() * 100).round(1)
    print(missing[missing > 0].sort_values(ascending=False).to_string())

    print("\nBoston University:")
    bu = df[df["unitid"] == config.BU_UNITID]
    print(bu.T.to_string(header=False) if len(bu) else "  (not found!)")


def main():
    raw = load_raw()
    df = filter_schools(raw)
    df = add_net_price(df)
    df = add_extra_columns(df)
    df = drop_missing_outcomes(df)
    df = drop_small_cohorts(df)

    config.DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(config.CLEAN_CSV, index=False)

    print_summary(df, start_rows=len(raw))
    print(f"\nSaved {config.CLEAN_CSV.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
