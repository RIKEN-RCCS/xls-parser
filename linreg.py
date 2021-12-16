#!/usr/bin/env python


# TODO(vatai) print colum scores!!!

import argparse

import pandas as pd
from sklearn.linear_model import LinearRegression


def get_numpy(derived_path: str, diffs_path: str) -> pd.DataFrame:
    selected_diffs_cols = [0, 2, 3, 4]
    last_removed_col = 8

    derived = pd.read_csv(derived_path, sep="\t")
    diffs = pd.read_csv(diffs_path, sep="\t")
    diffs = diffs.iloc[:, selected_diffs_cols]
    merged = pd.merge(derived, diffs, on="Benchmark")
    removed_cols = merged.iloc[:, :last_removed_col].columns
    print(f"Removed cols: {[c for c in removed_cols]}")
    cleaned = merged.iloc[:, last_removed_col:]
    print(f"Remaining cols: {len(cleaned.columns)}")
    all_numeric = all(
        [pd.api.types.is_numeric_dtype(cleaned[c]) for c in cleaned.columns]
    )
    print("All remaining columns are numeric", all_numeric)
    X = cleaned.drop(columns=["Difference"]).to_numpy()
    y = cleaned["Difference"].to_numpy()
    return X, y


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
    X, y = get_numpy(args.derived_path, args.diffs_path)
    reg = LinearRegression().fit(X, y)
    print(reg.score(X, y))
    print(reg.coef_)
    print(reg.intercept_)
    # for c in merged.columns:
    #     print(merged[c].dtype, c)


main()
