#!/usr/bin/env python

from pathlib import Path

import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.formula import Tokenizer
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


def get_label(workbook: Workbook, cell_loc: str) -> str:
    wb, loc = "report", cell_loc
    cell = workbook[wb][loc]
    while cell.data_type == "f":
        cell = cell.value
        assert cell[0] == "="
        tokens = Tokenizer(cell).items
        print("TOKENS", tokens)
        if len(tokens) == 1 and tokens[0].type == "OPERAND":
            token = tokens[0]
            print("YYYYY", token.value.replace("!", "_"))
        assert "!" in cell[1:]
        wb, loc = cell[1:].split("!")
        cell = workbook[wb][loc]
    print("TYPE", cell.data_type)
    return cell.value


def get_coords_on_right(workbook: Workbook, cell_loc: str):
    worksheet = workbook["report"]
    cell = worksheet[cell_loc]
    row, col = cell.row, cell.col_idx

    while not isinstance(worksheet.cell(row, col), MergedCell):
        col += 1
    col += 1
    return worksheet.cell(row, col).coordinate


# # main prelude
# filename = Path(
#     "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
# ).expanduser()
# workbook = openpyxl.load_workbook(filename)


def main():
    header_cells = ["A3", "A4", "H3", "H4", "H5"]  # , "O3", "O4"]

    result = dict()
    for cell_loc in header_cells:
        print("CELL", cell_loc)
        label = get_label(workbook, cell_loc)
        print("LABEL", label)
        coord = get_coords_on_right(workbook, cell_loc)
        print("COORD", coord)
        value = get_label(workbook, coord)
        print("VALUE", value)
        result[label] = value
        print()

    print(result)


def cell_id_to_var(cell_id: str) -> str:
    return cell_id.replace("!", "_")


def parse_expr():
    pass


def cell_to_inst():
    cell = get_cell(cell_id, workbook)
    cell_var = cell_id_to_var(cell_id)
    cell_val = parse_cell(cell.tokens)
    line = f"{cell_var} = {cell_val}"
    LINES.append(line)


def experiment():
    cell_loc = "data!OR30"
    cell_name = cell_loc.replace("!", "_")
    wb, loc = cell_loc.split("!")
    cell = workbook[wb][loc]
    tokens = Tokenizer(cell.value).items
    num_tokens = len(tokens)
    current = 0
    # while current < num_tokens:
    for token in tokens:
        print(cell.value)
        print(type(token), token.type, token.subtype, token.value)


# main()
experiment()
