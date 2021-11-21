#!/usr/bin/env python

from pathlib import Path

import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


def get_label(workbook: Workbook, cell_loc: str) -> str:
    wb, loc = "report", cell_loc
    cell = workbook[wb][loc]
    while cell.data_type == "f":
        cell = cell.value
        assert cell[0] == "="
        assert "!" in cell[1:]
        wb, loc = cell[1:].split("!")
        cell = workbook[wb][loc]
    return cell.value


def get_coords_on_right(workbook: Workbook, cell_loc: str):
    worksheet = workbook["report"]
    print(type(worksheet))
    cell = worksheet[cell_loc]
    row, col = cell.row, cell.col_idx

    while not isinstance(worksheet.cell(row, col), MergedCell):
        col += 1
    col += 1
    return worksheet.cell(row, col).coordinate


def get_label_and_value_on_the_right(workbook: Workbook, cell_loc: str) -> dict:

    coord = get_coords_on_right(workbook, cell_loc)
    print(coord)
    return {"label": get_label(workbook, cell_loc)}


# def main():
# filename = Path(
#     "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
# ).expanduser()
# workbook = openpyxl.load_workbook(filename)
rv = get_label_and_value_on_the_right(workbook, "A3")
print(rv)
