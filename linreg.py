#!/usr/bin/env python
import argparse

import pandas as pd


def get_cleaned(derived_path: str, diffs_path: str) -> pd.DataFrame:
    selected_diffs_cols = [0, 2, 3, 4]
    last_removed_col = 8

    derived = pd.read_csv(derived_path, sep="\t")
    diffs = pd.read_csv(diffs_path, sep="\t")
    diffs = diffs.iloc[:, selected_diffs_cols]
    merged = pd.merge(derived, diffs, on="Benchmark")
    removed_cols = merged.iloc[:, :last_removed_col].columns
    print(f"Removed cols: {[c for c in removed_cols]}")
    cleaned = merged.iloc[:, last_removed_col:]
    return cleaned


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--derived_path",
        help="TSV from xml/xls flatten script",
        default="all.tsv",
    )
    parser.add_argument(
        "--diffs_path",
        help="TSV from google sheets",
        default="polybench.tsv",
    )
    args = parser.parse_args()
    data = get_cleaned(args.derived_path, args.diffs_path)
    print(data.head())
    # for c in merged.columns:
    #     print(merged[c].dtype, c)


main()
