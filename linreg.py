#!/usr/bin/env python


# TODO(vatai) print colum scores!!!

import argparse

import pandas as pd
from sklearn.linear_model import LinearRegression


def normalise(data, colnames, normalizer=""):
    for col in colnames:
        pass


def get_numpy(derived_path: str, diffs_path: str) -> pd.DataFrame:
    selected_diffs_cols = [0, 2, 3, 4]
    last_removed_col = 8
    y_key = "Difference"

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
    X = cleaned.drop(columns=[y_key])
    y = cleaned[y_key]
    normalise(X, [])
    return X, y


def print_results(coefs, n=5):
    print("Top:")
    for i in range(n):
        p = coefs[i]
        print(f"{p[1]:0.10f} : {p[0]}")

    print()
    print("Bottom:")
    for i in range(n):
        idx = len(coefs) - n + i
        p = coefs[idx]
        print(f"{p[1]:0.10f} : {p[0]}")
    # print(f"Top: {coefs[:5]}")
    # print(f"Bottom: {coefs[-5:]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--derived_path",
        help="TSV from xml/xls flatten script",
        default="~/Sync/all.tsv",
    )
    parser.add_argument(
        "--diffs_path",
        help="TSV from google sheets",
        default="~/Sync/polybench.tsv",
    )
    args = parser.parse_args()

    X, y = get_numpy(args.derived_path, args.diffs_path)
    reg = LinearRegression().fit(X, y)
    print(f"Score: {reg.score(X, y)}")
    coefs = sorted(zip(X.columns, reg.coef_), key=lambda t: t[1], reverse=True)
    print_results(coefs)
    print(reg.intercept_)
    # for c in merged.columns:
    #     print(merged[c].dtype, c)


main()
