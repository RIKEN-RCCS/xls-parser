#!/usr/bin/env python


import argparse

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.linear_model import LinearRegression

NORM_COLS = [
    "CNTVCT",
    "PMCCNTR",
    "0x80c0",
    "0x80c1",
    "0x0017",
    "0x0018",
    "0x0325",
    "0x0326",
    "0x0121",
    "0x8000",
    "0x0190",
    "0x0191",
    "0x0184",
    "0x0186",
    "0x0189",
    "0x018c",
    "0x018d",
    "0x018e",
    "0x0240",
    "0x0241",
    "0x0330",
    "0x0274",
    "0x01a4",
    "0x01b4",
    "0x01a5",
    "0x01b5",
    "0x0003",
    "0x0049",
    "0x0300",
    "0x80ad",
    "0x80ae",
    "0x8010",
    "0x8028",
    "0x8034",
    "0x0070",
    "0x0071",
    "0x8085",
    "0x8086",
    "0x8087",
    "0x0185",
    "0x0182",
    "0x0183",
    "0x0180",
    "0x0181",
    "0x0187",
    "0x0188",
    "0x018a",
    "0x0192",
    "0x0193",
    "0x0194",
    "0x018b",
    "0x80c6",
    "0x80c4",
    "0x80c7",
    "0x80c5",
    "0x01a6",
    "0x01e0",
    "0x03e0",
    "0x03e8",
    "0x01a0",
    "0x01a1",
    "0x01a2",
    "0x01a3",
    "0x0202",
    "0x0059",
    "0x0302",
    "0x0005",
    "0x002d",
    "0x0001",
    "0x8091",
    "0x8092",
    "0x80bc",
    "0x80af",
    "0x809f",
    "0x009f",
    "0x8043",
    "0x0012",
    "0x80a5",
    "0x80a6",
    "0x8038",
    "0x0105",
    "0x0113",
    "0x0108",
    "0x0112",
    "0x011a",
    "0x8008",
    "0x0198",
    "0x0199",
    "0x0139",
    "0x0010",
    "0x8095",
    "0x8096",
    "0x807c",
    "0x800e",
    "0x0109",
    "0x010a",
    "0x0077",
    "0x0230",
    "0x0231",
    "0x0232",
    "0x0233",
    "0x0234",
    "0x0235",
    "0x0236",
    "0x02b2",
    "0x02b1",
    "0x02b0",
    "0x02b8",
    "0x02b9",
    "0x0260",
    "0x0261",
    "0x0309",
    "0x0396",
    "0x0370",
    "0x0318",
    "0x0319",
    "0x031a",
    "0x031b",
    "0x0316",
    "0x0314",
    "0x0315",
    "0x031e",
    "0x031c",
    "0x031d",
    "0x0391",
    "0x03ae",
]


def get_numpy(derived_path: str, diffs_path: str) -> pd.DataFrame:
    last_removed_col = 8
    y_key = "Difference"
    denom_key = "Statistics::Execution time (s)"

    derived = pd.read_csv(derived_path, sep="\t")
    diffs = pd.read_csv(diffs_path, sep="\t")
    merged = pd.merge(derived, diffs, on="Benchmark")
    removed_cols = merged.iloc[:, :last_removed_col].columns
    print(f"Removed cols: {[c for c in removed_cols]}")

    print(
        merged[["Benchmark", "Statistics::Execution time (s)", "A64fx time"]].assign(
            quotient=merged["Statistics::Execution time (s)"] / merged["A64fx time"]
        )
    )
    cleaned = merged.iloc[:, last_removed_col:]
    print(f"Remaining cols: {len(cleaned.columns)}")

    all_numeric = all([is_numeric_dtype(cleaned[c]) for c in cleaned.columns])
    print("All remaining columns are numeric", all_numeric)

    for col in NORM_COLS:  # normalisation
        cleaned[col] /= cleaned[denom_key]
        cleaned = cleaned.rename(columns={col: f"{col} (norm)"})
    return cleaned.drop(columns=[y_key]), cleaned[y_key]


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


main()
