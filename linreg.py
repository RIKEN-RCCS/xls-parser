#!/usr/bin/env python
import pandas as pd

derived = pd.read_csv("all.tsv", sep="\t")
print(derived.shape)

diffs = pd.read_csv("polybench.tsv", sep="\t")
diffs = diffs.iloc[:, [0, 2, 3, 4]]
print(diffs.shape)

merged = pd.merge(derived, diffs, on="Benchmark")
print(merged.shape)
print(merged.head())

print(set(derived["Benchmark"]) - set(diffs["Benchmark"]))
print(set(diffs["Benchmark"]) - set(derived["Benchmark"]))
