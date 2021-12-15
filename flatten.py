#!/usr/bin/env python

import argparse
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path


def flatten(data: OrderedDict) -> list:
    results = []
    for key, value in data.items():
        if isinstance(value, OrderedDict):
            results += [
                [f"{key.strip()}::{t[0].strip()}", t[1]] for t in flatten(value)
            ]
        else:
            results.append([key, value])
    return results


def get_ordered_dict(xml_dir: str, parser: str) -> OrderedDict:
    script = Path(parser).expanduser()
    cmd = ["python", script, xml_dir.strip()]
    json_out = subprocess.run(cmd, stdout=subprocess.PIPE)
    result = json.loads(json_out.stdout, object_pairs_hook=OrderedDict)
    return result


def get_values(pairs: list):
    values = [pair[1] for pair in pairs]
    results = [s[0] if isinstance(s, list) and len(s) == 1 else s for s in values]
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="Input file")
    parser.add_argument(
        "--parser",
        help="Parser for the xml files",
        type=str,
        default="xls_parse.out.py",
    )
    args = parser.parse_args()
    if args.infile is None:
        infile = sys.stdin
    else:
        infile = open(args.infile)

    first = True
    for line in infile.readlines():
        benchmark = Path(line).expanduser().name.split(".")[0]
        json_dict = get_ordered_dict(line, args.parser)
        pairs = flatten(json_dict)
        values = get_values(pairs)
        if first:
            first = False
            keys = [pair[0] for pair in pairs]
            print("\t".join(["Benchmark"] + keys))
        print("\t".join([benchmark] + [str(v) for v in values]))

    if infile is not sys.stdin:
        infile.close()


main()
