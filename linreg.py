#!/usr/bin/env python


import argparse

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression


def get_args():
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
    return parser.parse_args()


def get_raw_counter_keys(columns):
    results = ["CNTVCT", "PMCCNTR"]
    for col in columns:
        if col.startswith("0x"):
            results.append(col)
    return results


def get_numbers(
    derived_path: str,
    diffs_path: str,
    verbose: bool = False,
) -> pd.DataFrame:
    last_removed_col = 8

    derived = pd.read_csv(derived_path, sep="\t")
    diffs = pd.read_csv(diffs_path, sep="\t")
    merged = pd.merge(derived, diffs, on="Benchmark")

    if verbose:
        removed_cols = merged.iloc[:, :last_removed_col].columns
        print(f"Removed cols: {[c for c in removed_cols]}")
        fapp_time_col = "Statistics::Execution time (s)"
        chip_time_col = "A64fx time"
        selected_cols = merged[["Benchmark", fapp_time_col, chip_time_col]]
        quotient_col = merged[fapp_time_col] / merged[chip_time_col]
        print(selected_cols.assign(quotient=quotient_col))

    numbers = merged.iloc[:, last_removed_col:]
    # print(f"Remaining cols: {len(numbers.columns)}")

    all_numeric = all([is_numeric_dtype(numbers[c]) for c in numbers.columns])
    assert all_numeric, "Some of the remaining columns are not numeric"
    return numbers


def normalise(
    data,
    norm_cols,
    drop_cols=[],
    y_key="Difference",
    denom_key="Statistics::Execution time (s)",
) -> (pd.DataFrame(), pd.Series):
    for col in norm_cols:  # normalisation
        data[col] /= data[denom_key]
        data = data.rename(columns={col: f"{col} (norm)"})

    X, y = data.drop(columns=[y_key] + drop_cols), data[y_key]

    return X, y


def print_results(coefs, n=5):
    fmt_str = "{:0.10} : {}"
    print("Top:")
    for i in range(n):
        p = coefs[i]
        print(fmt_str.format(p[1], p[0]))

    print()
    print("Bottom:")
    for i in range(n):
        idx = len(coefs) - n + i
        p = coefs[idx]
        print(fmt_str.format(p[1], p[0]))


def main():
    args = get_args()
    numbers = get_numbers(args.derived_path, args.diffs_path)
    norm_cols = get_raw_counter_keys(numbers.columns)
    print(norm_cols)
    X, y = normalise(numbers, norm_cols)

    for col in X.columns:
        print(col)

    reg = LinearRegression().fit(X, y)
    print(f"Score: {reg.score(X, y)}")

    coefs = sorted(zip(X.columns, reg.coef_), key=lambda t: t[1], reverse=True)
    print_results(coefs)
    print(reg.intercept_)


if __name__ == "__main__":
    main()
