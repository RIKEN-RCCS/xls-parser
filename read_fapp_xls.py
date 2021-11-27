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
PROCESSED_CELLS = set()
WORKSHEET_STACK = []
INFIX_OP_MAP = {"=": "=="}

DEBUG = True
# DEBUG = False


def dbg_print(msg: str) -> None:
    if DEBUG:
        print(msg)


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
    dbg_print(f"BEGIN GET_CELL({cell_id})")
    if "!" not in cell_id:
        cell_id = WORKSHEET_STACK[-1] + "!" + cell_id
    ws, cell = cell_id.split("!")
    cell = WORKBOOK[ws][cell]
    if isinstance(cell, MergedCell):
        print("WARNING: MergedCell!")
    dbg_print(f"END GET_CELL -> cell")
    return cell


def get_raw(cell_id: str) -> Optional[str]:
    dbg_print(f"BEGIN GET_RAW({cell_id})")
    if "!" not in cell_id:
        cell_id = WORKSHEET_STACK[-1] + "!" + cell_id
    ws, cell = cell_id.split("!")
    if ws == "label":
        value = WORKBOOK[ws][cell].value
        return f"'{cell_id_to_var(value)}'"
    if ws == "data":
        if cell == "G4":
            return "data['measured time']"
        if cell == "G5":
            return "data[what_is_G5]"
        if cell == "G10":
            return "data[what_is_G10]"
        if cell == "G11":
            return "data[what_is_G11]"
        if cell == "G12":
            return "data[what_is_G12]"
        if cell == "C10":
            return "data[what_is_C10]"
    return None


def unknown_type(token: Token) -> None:
    msg = f"ERROR: Unknown type {token.type}"
    raise Exception(msg)


def unknown_subtype(token: Token) -> None:
    msg = f"ERROR: Unknown subtype {token.subtype} (of token type {token.type})"
    raise Exception(msg)


def unknown_func(token: Token) -> None:
    msg = f"ERROR: Unknown FUNC {token.value}"
    raise Exception(msg)


def assert_sep_comma(token: Token) -> None:
    assert token.type == Token.SEP and token.value == ","


def assert_func_close(token: Token) -> None:
    assert token.type == Token.FUNC and token.subtype == Token.CLOSE


def parse_tokens(tokens: list[Token], cur: int) -> (str, int):
    dbg_print(f"BEGIN PARSE_TOKENS({tokens}, {cur}")
    result = ""
    while cur < len(tokens):
        token = tokens[cur]
        if token.type == Token.OPERAND:
            if token.subtype == Token.RANGE:
                raw = get_raw(token.value)
                if raw:
                    result += raw
                else:
                    cell_to_inst(token.value)
                    result += cell_id_to_var(token.value)
            elif token.subtype == Token.TEXT:
                result += token.value
            else:
                unknown_subtype(token)
        elif token.type == Token.FUNC:
            if token.subtype == Token.OPEN:
                if token.value == "IF(":
                    cond, cur = parse_tokens(tokens, cur + 1)
                    assert_sep_comma(tokens[cur])
                    true_val, cur = parse_tokens(tokens, cur + 1)
                    assert_sep_comma(tokens[cur])
                    false_val, cur = parse_tokens(tokens, cur + 1)
                    assert_func_close(tokens[cur])
                    result += f"({true_val}) if ({cond}) else ({false_val})"
                elif token.value == "OR(":
                    print(f"####### RESULT: {result}")
                    cells, cur = parse_tokens(tokens, cur + 1)
                    result += f"any(cells)"
                elif token.value == "COUNT(":
                    print(f"####### RESULT: {result}")
                    cells, cur = parse_tokens(tokens, cur + 1)
                    result += f"sum(1 for e in {cells} if e)"

                else:
                    unknown_func(token)
            elif token.subtype == Token.CLOSE:
                break
            else:
                unknown_subtype(token)
        elif token.type == Token.OP_IN:
            op_name = token.value
            if token.value in INFIX_OP_MAP:
                op_name = INFIX_OP_MAP[token.value]
            result += op_name
        elif token.type == Token.SEP:
            break
        else:
            unknown_type(token)
        # print("tokens[cur]:", token)
        # print(token.value, token.type, token.subtype)
        cur += 1
    dbg_print(f"END PARSE_TOKENS - > {result}, {cur}")
    return result, cur


def parse_cell(cell: Cell) -> str:
    dbg_print(f"BEGIN PARSE_CELL({cell})")
    WORKSHEET_STACK.append(cell.parent.title)
    tokens = Tokenizer(cell.value).items
    value, _ = parse_tokens(tokens, 0)
    WORKSHEET_STACK.pop()
    dbg_print(f"END PARSE_CELL -> {value}")
    return value


def cell_to_inst(cell_id: str) -> None:
    dbg_print(f"BEGIN CELL_TO_INST({cell_id})")
    cell = get_cell(cell_id)
    cell_var = cell_id_to_var(cell_id)
    if cell_var in PROCESSED_CELLS:
        return
    cell_val = parse_cell(cell)
    line = f"{cell_var} = {cell_val}"
    dbg_print(f"END CELL_TO_INST: LINES.append({line})")
    PROCESSED_CELLS.add(cell_var)
    LINES.append(line)


# main prelude
if "WORKBOOK" not in locals():
    filename = Path(
        "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
    ).expanduser()
    WORKBOOK = openpyxl.load_workbook(filename)


def main():
    # header_cells = ["A3", "A4", "H3", "H4", "H5", "O3"]  # , "O4"]
    header_cells = ["A3", "C3"]
    header_cells = ["A4", "C4"]
    header_cells = ["H3", "J3"]
    header_cells = ["H4", "J4"]
    header_cells = ["H5", "J5"]
    header_cells = ["O3", "Q3"]
    # header_cells = ["O4", "Q4"]

    for cell_loc in header_cells:
        cell_id = "report!" + cell_loc
        # print(f"\n--- START: {cell_id} ---")
        cell_to_inst(cell_id)
        # print("\n".join(LINES))

    print("\n".join(LINES))
    assert WORKSHEET_STACK == []


main()
