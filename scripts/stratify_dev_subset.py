#!/usr/bin/env python
"""
stratify_dev_subset.py

Build a smaller, stratified development subset from a full FairFace/UTKFace
predictions CSV, preserving the relative proportions of each demographic
stratum (by default: race x gender x age) so the subset stays representative
of the full dataset rather than favoring whichever rows happen to sort first.

Usage:
    python scripts/stratify_dev_subset.py INPUT_CSV OUTPUT_CSV [options]

Examples:
    # 5,000-row dev subset, stratified by race, gender, and age
    python scripts/stratify_dev_subset.py \\
        data/processed/fairface_predictions_val.csv \\
        data/processed/fairface_predictions_dev_5000.csv \\
        --n 5000

    # Stratify by race and gender only, guarantee at least 30 rows per
    # stratum where the full dataset supports it (matches the NFR-003
    # subgroup-eligibility threshold used by the fairness engine)
    python scripts/stratify_dev_subset.py \\
        data/processed/fairface_predictions_val.csv \\
        data/processed/fairface_predictions_dev_5000.csv \\
        --n 5000 --stratify-cols race,gender --min-per-group 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a stratified dev subset from a full predictions CSV, "
            "preserving demographic proportions from the source data."
        )
    )
    parser.add_argument("input_csv", type=Path, help="Path to the full predictions CSV.")
    parser.add_argument("output_csv", type=Path, help="Path to write the subset CSV to.")
    parser.add_argument(
        "--n",
        type=int,
        default=5000,
        help="Target number of rows in the output subset (default: 5000).",
    )
    parser.add_argument(
        "--stratify-cols",
        type=str,
        default="race,gender,age",
        help=(
            "Comma-separated column names to stratify by (default: "
            "'race,gender,age'). Rows are sampled proportionally within "
            "each unique combination of these columns."
        ),
    )
    parser.add_argument(
        "--min-per-group",
        type=int,
        default=0,
        help=(
            "Minimum rows to keep per stratum when the full dataset has at "
            "least that many available, even if proportional allocation "
            "would round down to fewer (default: 0, i.e. no floor)."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling (default: 42).",
    )
    return parser.parse_args(argv)


def stratified_sample(
    df: pd.DataFrame,
    stratify_cols: list[str],
    n: int,
    min_per_group: int,
    seed: int,
) -> pd.DataFrame:
    """
    Sample n rows from df, allocated proportionally across the unique
    combinations of stratify_cols. Each stratum's allocation is at least
    min_per_group (capped at that stratum's actual size), and the overall
    result is truncated or topped up to land as close to n as possible.
    """
    total = len(df)
    if total == 0:
        raise ValueError("input dataset is empty; nothing to sample")

    groups = df.groupby(stratify_cols, dropna=False, sort=False)
    group_sizes = groups.size()

    # Proportional allocation, floored, then apply the minimum floor.
    raw_allocation = (group_sizes / total * n).round().astype(int)
    allocation = raw_allocation.clip(lower=min_per_group)
    # Never ask for more rows than a stratum actually has.
    allocation = allocation.clip(upper=group_sizes)

    sampled_frames = []
    rng_seed = seed
    for key, group_df in groups:
        k = int(allocation.loc[key]) if isinstance(allocation.index, pd.MultiIndex) else int(
            allocation.loc[key]
        )
        if k <= 0:
            continue
        sampled_frames.append(group_df.sample(n=k, random_state=rng_seed))
        rng_seed += 1  # vary the seed per group to avoid correlated draws

    if not sampled_frames:
        raise ValueError(
            "stratified allocation produced zero rows; check --stratify-cols "
            "match actual column names in the input CSV"
        )

    result = pd.concat(sampled_frames, ignore_index=True)

    # If proportional rounding overshot the target, trim the surplus
    # uniformly at random rather than always cutting from the same strata.
    if len(result) > n:
        result = result.sample(n=n, random_state=seed).reset_index(drop=True)

    return result.sample(frac=1, random_state=seed).reset_index(drop=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input_csv.exists():
        print(f"error: input file not found: {args.input_csv}", file=sys.stderr)
        return 1

    stratify_cols = [c.strip() for c in args.stratify_cols.split(",") if c.strip()]

    df = pd.read_csv(args.input_csv)

    missing = [c for c in stratify_cols if c not in df.columns]
    if missing:
        print(
            f"error: stratify column(s) not found in input CSV: {missing}\n"
            f"available columns: {list(df.columns)}",
            file=sys.stderr,
        )
        return 1

    if args.n >= len(df):
        print(
            f"note: requested n={args.n} >= input rows ({len(df)}); "
            "writing the full dataset unchanged."
        )
        subset = df
    else:
        subset = stratified_sample(
            df,
            stratify_cols=stratify_cols,
            n=args.n,
            min_per_group=args.min_per_group,
            seed=args.seed,
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    subset.to_csv(args.output_csv, index=False)

    print(f"wrote {len(subset)} rows to {args.output_csv}")
    print("stratum sizes in output:")
    print(subset.groupby(stratify_cols, dropna=False).size().to_string())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())