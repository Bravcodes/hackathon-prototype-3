"""
Phase 2b: prestige score vs. outcome score.

Prestige score (0-100): how selective and rich a school is.
    Built from admit rate (lower = more prestigious), SAT, faculty salary,
    and spending per student. This is a stand-in for what rankings reward.

Outcome score (0-100): how well a school does by its students.
    Built from graduation rate, Pell students' graduation rate, earnings,
    low debt, and low net price.

Both scores use PERCENTILE RANKS: a school at 80 beat 80% of schools on
that measure. We average the percentiles, skipping any that are missing.
"""

import pandas as pd

import config

# column -> True if HIGHER is better, False if LOWER is better
PRESTIGE_PARTS = {
    "admit_rate": False,
    "sat_avg": True,
    "fac_salary_monthly": True,
    "spend_per_student": True,
}

OUTCOME_PARTS = {
    "grad_rate": True,
    "pell_grad_rate": True,
    "earnings_10yr": True,
    "median_debt": False,
    "net_price": False,
}


def percentile_score(df, parts):
    """Average percentile (0-100) across the given columns.

    A school missing a column (e.g. no SAT) is scored on the columns it has.
    """
    pcts = pd.DataFrame(index=df.index)
    for col, higher_is_better in parts.items():
        pcts[col] = df[col].rank(pct=True, ascending=higher_is_better) * 100
    return pcts.mean(axis=1, skipna=True)


def add_scores(df):
    """Add prestige_score, outcome_score, and the gap between them."""
    df = df.copy()
    df["prestige_score"] = percentile_score(df, PRESTIGE_PARTS)
    df["outcome_score"] = percentile_score(df, OUTCOME_PARTS)
    # Positive gap = better outcomes than its prestige would suggest
    df["gap"] = df["outcome_score"] - df["prestige_score"]
    return df


def correlations(df):
    """How strongly prestige lines up with each outcome.

    Spearman correlation: +1 = perfect agreement in order, 0 = no relation.
    """
    cols = ["outcome_score", *OUTCOME_PARTS, "residual_grad_rate", "residual_earnings_10yr"]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corrwith(df["prestige_score"], method="spearman")
    return corr.rename_axis("measure").reset_index(name="spearman_vs_prestige")


def biggest_gaps(df, n=15):
    """Schools whose outcomes beat (or trail) their prestige by the most."""
    cols = ["name", "state", "control_label", "prestige_score", "outcome_score", "gap"]
    ranked = df.sort_values("gap", ascending=False)[cols]
    return ranked.head(n), ranked.tail(n).iloc[::-1]


# ---------------------------------------------------------------------------
# Optional: real rankings (only used if data/rankings.csv exists AND a
# librarian confirmed we may use it). Columns: UNITID or name, plus rank.
# ---------------------------------------------------------------------------
def load_rankings(path=config.RANKINGS_CSV):
    """Return a table with unitid/name and rank, or None if there's no file."""
    if not path.exists():
        return None
    ranks = pd.read_csv(path)
    ranks.columns = [c.strip().lower() for c in ranks.columns]
    return ranks


def merge_rankings(df, ranks):
    """Join rankings onto our data by unitid if present, otherwise by name."""
    key = "unitid" if "unitid" in ranks.columns else "name"
    return df.merge(ranks[[key, "rank"]], on=key, how="left")


def rankings_report(df):
    """How much does the real rank agree with our prestige and outcome scores?

    Rank 1 is best, so we flip the sign: a positive number means agreement.
    """
    ranked = df.dropna(subset=["rank"])
    if len(ranked) < 10:
        return None
    rows = []
    for col in ["prestige_score", "outcome_score", "residual_grad_rate", "residual_earnings_10yr"]:
        rho = -ranked["rank"].corr(ranked[col], method="spearman")
        rows.append({"measure": col, "agreement_with_rank": rho, "n_schools": len(ranked)})
    return pd.DataFrame(rows)
