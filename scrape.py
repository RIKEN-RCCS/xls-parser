#!/usr/bin/env python

import argparse
from pathlib import Path, PosixPath
from typing import Optional

import pandas as pd


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="~/Sync/tmp/sim-accuracy/log")
    parser.add_argument("--output_path", default="~/Sync/polybench.tsv")
    return parser.parse_args()


def extract_walltime(line: str) -> Optional[float]:
    prefix = "Walltime of the main kernel:"
    if line.startswith(prefix):
        num = line[len(prefix) :].split()[0]
        result = float(num)
    else:
        result = None
    return result


def bestrun(log: PosixPath) -> (str, float):
    results = []
    with open(log) as file:
        for line in file:
            tmp = extract_walltime(line)
            if tmp is not None:
                results.append(tmp)
    avg = sum(results) / len(results)

    benchmark, ext = log.name.split(".")
    assert ext == "log"
    return (benchmark, avg)


def gem5run(log: PosixPath) -> (str, float):
    logfile = log / "conf1.log"
    assert logfile.exists(), f"There should be a {logfile} here"
    with open(logfile) as file:
        for line in file:
            tmp = extract_walltime(line)
            if tmp is not None:
                benchmark = log.name
                return (benchmark, tmp)


def save_to_csv(results: dict, output_path: Path) -> None:
    df = pd.DataFrame(results)
    df["Difference"] = df["A64fx time"] / df["Gem5 time"]
    df.index = df.index.set_names(["Benchmark"])
    df.to_csv(output_path, sep="\t")


def collect_results(input_dir: Path) -> dict:
    runfunc = {
        "bestrun": bestrun,  # log/e35-7101c/bestrun/polybench/3mm_MEDIUM.log
        "gem5run": gem5run,  # log/kiev1/gem5run/polybench/3mm_MEDIUM[/conf1.log]
    }

    conversion = {"bestrun": "A64fx time", "gem5run": "Gem5 time"}
    results = {val: {} for val in conversion.values()}
    for rtype, func in runfunc.items():
        for log in input_dir.glob(f"*/{rtype}/polybench/*"):
            benchmark, result = func(log)
            results[conversion[rtype]][benchmark] = result
    return results


def main():
    args = get_args()
    input_dir = Path(args.input_dir).expanduser()
    results = collect_results(input_dir)
    output_csv = Path(args.output_path).expanduser()
    save_to_csv(results, output_csv)


if __name__ == "__main__":
    main()
