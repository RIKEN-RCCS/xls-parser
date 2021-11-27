#!/usr/bin/env python

from pathlib import Path
from typing import Optional

import openpyxl
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token

# from openpyxl.workbook.workbook import Workbook
# from openpyxl.worksheet.worksheet import Worksheet

LINES = []
DEBUG = True
DEBUG = False


def get_label(cell_loc: str) -> str:
    wb, loc = "report", cell_loc
    cell = WORKBOOK[wb][loc]
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
        cell = WORKBOOK[wb][loc]
    print("TYPE", cell.data_type)
    return cell.value


def get_coords_on_right(cell_loc: str):
    worksheet = WORKBOOK["report"]
    cell = worksheet[cell_loc]
    row, col = cell.row, cell.col_idx

    while not isinstance(worksheet.cell(row, col), MergedCell):
        col += 1
    col += 1
    return worksheet.cell(row, col).coordinate


def cell_id_to_var(cell_id: str) -> str:
    return cell_id.replace("!", "_")


def get_cell(cell_id: str) -> Cell:
    ws, cell = cell_id.split("!")
    cell = WORKBOOK[ws][cell]
    if isinstance(cell, MergedCell):
        print("WARNING: MergedCell!")
    return cell


def get_raw(cell_id: str) -> Optional[str]:
    ws, cell = cell_id.split("!")
    if ws == "label":
        value = WORKBOOK[ws][cell].value
        return f"'{cell_id_to_var(value)}'"
    if ws == "data":
        if cell == "G4":
            return "data['measured time']"
    return None


def parse_tokens(tokens: list[Token], cur: int) -> (str, int):
    if DEBUG:
        print(f"BEGIN PARSE_TOKENS({tokens}, {cur}")
    value = ""
    while cur < len(tokens):
        token = tokens[cur]
        if token.type == Token.OPERAND:
            if token.subtype == Token.RANGE:
                raw = get_raw(token.value)
                if raw:
                    value += raw
                else:
                    cell_to_inst(token.value)
                    value += cell_id_to_var(token.value)
            else:
                print("!!!!!!Unknown subtype", token.subtype)
        else:
            print("!!!!!!Unknown type", token.type)
        # print("tokens[cur]:", token)
        # print(token.value, token.type, token.subtype)
        cur += 1
    if DEBUG:
        print(f"END PARSE_TOKENS - > {value}, {cur}")
    return value, cur


def parse_cell(cell: Cell) -> str:
    if DEBUG:
        print(f"BEGIN PARSE_CELL({cell})")
    tokens = Tokenizer(cell.value).items
    value, _ = parse_tokens(tokens, 0)
    if DEBUG:
        print(f"END PARSE_CELL -> {value}")
    return value


def cell_to_inst(cell_id: str):
    if DEBUG:
        print(f"BEGIN CELL_TO_INST({cell_id})")
    cell = get_cell(cell_id)
    cell_var = cell_id_to_var(cell_id)
    cell_val = parse_cell(cell)
    line = f"{cell_var} = {cell_val}"
    if DEBUG:
        print(f"END CELL_TO_INST: LINES.append({line})")
    LINES.append(line)


# main prelude
if "WORKBOOK" not in locals():
    filename = Path(
        "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
    ).expanduser()
    WORKBOOK = openpyxl.load_workbook(filename)


def main():
    # header_cells = ["A3", "A4", "H3", "H4", "H5", "O3"]  # , "O4"]
    header_cells = ["A3", "B3", "O4"]

    result = dict()
    for cell_loc in header_cells:
        # print("CELL", cell_loc)
        # label = get_label(workbook, cell_loc)
        # print("LABEL", label)
        # coord = get_coords_on_right(workbook, cell_loc)
        # print("COORD", coord)
        # value = get_label(workbook, coord)
        # print("VALUE", value)
        # result[label] = value
        # print()
        cell_id = "report!" + cell_loc
        print(f"--- START: {cell_id} ---")
        print("\n".join(LINES))
        cell_to_inst(cell_id)

    print(result)
    print("\n".join(LINES))


main()
