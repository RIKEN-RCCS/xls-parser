#!/usr/bin/env python

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


def get_ordered_dict(xml_dir: str) -> OrderedDict:
    script = Path("~/xls_parse.out.py").expanduser()
    cmd = ["python", script, xml_dir.strip()]
    json_out = subprocess.run(cmd, stdout=subprocess.PIPE)
    result = json.loads(json_out.stdout, object_pairs_hook=OrderedDict)
    return result


def get_values(pairs: list):
    values = [pair[1] for pair in pairs]
    results = [s[0] if isinstance(s, list) and len(s) == 1 else s for s in values]
    return results


def main():
    if len(sys.argv) > 1:
        infile = open(sys.argv[1])
    else:
        infile = sys.stdin

    for line in infile.readlines():
        benchmark = Path(line).expanduser().name.split(".")[0]
        json_dict = get_ordered_dict(line)
        pairs = flatten(json_dict)
        values = get_values(pairs)
        print(benchmark, values)

    if infile is not sys.stdin:
        infile.close()


main()
