#!/usr/bin/env python

from pathlib import Path

import openpyxl


def main():
    filename = Path(
        "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
    ).expanduser()
    workbook = openpyxl.load_workbook(filename)
    print(workbook.sheetnames)


main()
