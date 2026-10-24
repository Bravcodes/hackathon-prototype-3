"""
Phase 2: run the whole analysis.

Run from the project folder (after clean.py):
    .venv/bin/python src/analysis.py

Outputs:
    data/results.csv          one row per school, with predictions and scores
    data/model_scores.csv     R² and MAE for each model
    data/feature_importance.csv
    figures/*.html, *.png     charts
"""

import pandas as pd

import config
import overperformers
import plots
import prestige


def load_clean():
    return pd.read_csv(config.CLEAN_CSV)


def print_model_scores(scores):
    print("\n=== Model scores on held-out schools (20% test set) ===")
    print(scores.round(3).to_string(index=False))


def print_importance(importance):
    print("\n=== Feature importance ===")
    for target, d in importance.groupby("target"):
        print(f"\n{target}:")
        print(d.drop(columns="target").round(3).to_string(index=False))


def print_top(df, col, n=10, ascending=False):
    cols = ["name", "state", col]
    print(df.sort_values(col, ascending=ascending)[cols].head(n).round(3).to_string(index=False))


def print_comparison(df):
    print("\n=== Does prestige line up with outcomes? (Spearman) ===")
    print(prestige.correlations(df).round(2).to_string(index=False))

    over, under = prestige.biggest_gaps(df)
    print("\nOutcomes BETTER than prestige suggests:")
    print(over.round(1).to_string(index=False))
    print("\nOutcomes WORSE than prestige suggests:")
    print(under.round(1).to_string(index=False))


def print_bu(df):
    bu = df[df["unitid"] == config.BU_UNITID]
    if bu.empty:
        return
    cols = ["grad_rate", "predicted_grad_rate", "residual_grad_rate",
            "earnings_10yr", "predicted_earnings_10yr", "residual_earnings_10yr",
            "prestige_score", "outcome_score", "gap"]
    print("\n=== Boston University ===")
    print(bu[cols].T.round(3).to_string(header=False))
    for col in ["residual_grad_rate", "residual_earnings_10yr", "gap"]:
        pct = (df[col] < bu[col].iloc[0]).mean() * 100
        print(f"  {col}: better than {pct:.0f}% of schools")


def run_rankings(df):
    """Only runs if data/rankings.csv exists (needs librarian approval)."""
    ranks = prestige.load_rankings()
    if ranks is None:
        print("\n(No data/rankings.csv -- skipping real-rankings comparison.)")
        return df
    df = prestige.merge_rankings(df, ranks)
    report = prestige.rankings_report(df)
    if report is None:
        print("\nrankings.csv matched fewer than 10 schools -- check the names/IDs.")
        return df
    print("\n=== Agreement with real rankings (Spearman; + means agrees) ===")
    print(report.round(2).to_string(index=False))

    # Can our student/resource inputs predict a school's rank?
    ranked = df.dropna(subset=["rank"])
    scores, fitted, (X_test, y_test) = overperformers.evaluate(ranked, "rank")
    print("\nPredicting rank from inputs:")
    print(pd.DataFrame(scores).round(3).to_string(index=False))
    imp = overperformers.feature_importance(fitted, X_test, y_test, "rank")
    print(imp.drop(columns="target").round(3).to_string(index=False))
    return df


def make_charts(df, importance, test_sets):
    print("\nSaving charts to figures/ ...")
    plots.save(plots.prestige_vs_outcome(df), "prestige_vs_outcome")
    plots.save(plots.gap_bars(df), "biggest_gaps")
    for target in overperformers.TARGETS:
        plots.save(plots.actual_vs_predicted(test_sets[target], target), f"actual_vs_predicted_{target}")
        plots.save(plots.importance_bars(importance, target), f"importance_{target}")
        plots.save(plots.top_residuals(df, target), f"top_overperformers_{target}")


def main():
    df = load_clean()
    print(f"Loaded {len(df):,} schools")

    # 1. Overperformers model
    df, scores, importance, test_sets = overperformers.run(df)
    print_model_scores(scores)
    print_importance(importance)
    print("\n=== Top 10 overperformers: graduation rate ===")
    print_top(df, "residual_grad_rate")
    print("\n=== Top 10 overperformers: earnings ===")
    print_top(df, "residual_earnings_10yr")

    # 2. Prestige vs. outcomes
    df = prestige.add_scores(df)
    print_comparison(df)
    df = run_rankings(df)
    print_bu(df)

    # 3. Save everything
    df.to_csv(config.RESULTS_CSV, index=False)
    scores.to_csv(config.DATA_DIR / "model_scores.csv", index=False)
    importance.to_csv(config.DATA_DIR / "feature_importance.csv", index=False)
    make_charts(df, importance, test_sets)
    print(f"\nSaved {config.RESULTS_CSV.relative_to(config.PROJECT_ROOT)} ({len(df):,} rows)")


if __name__ == "__main__":
    main()
