#!/usr/bin/env python

from pathlib import Path
from typing import Optional

import openpyxl
from openpyxl.cell.cell import Cell, MergedCell
from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token


def dbgp(msg):
    # return
    print(msg)


LINES = []
OUTPUT_DICT = {}
PROCESSED_CELLS = set()
WORKSHEET_STACK = []

FAPP_XML_OBJ = "fapp_xml"
SPECIAL_FAPP_XML_CALL = {
    "C4": f"{FAPP_XML_OBJ}.get_counter_timer_freq()",
    "G4": f"{FAPP_XML_OBJ}.get_measured_time()",
    "G5": f"{FAPP_XML_OBJ}.get_node_name()",
    "G10": f"{FAPP_XML_OBJ}.get_process_no()",
    "G11": f"{FAPP_XML_OBJ}.get_cmg_no()",
    "G12": f"{FAPP_XML_OBJ}.get_measured_region()",
    "C10": f"{FAPP_XML_OBJ}.get_vector_length()",
}
DATA_VALUES = {
    "C6",
    "C7",
    "C8",
    "C9",
    "C14",
    "C15",
    "C16",
    "C17",
}

HEADER_ROW = 29
TOP_ROW = 30
BOTOM_ROW = 41
LEFT_COLUMN = 29
RIGHT_COLUMN = 334

INFIX_OP_MAP = {
    "=": "==",
    "^": "**",
}


def is_event_cell(cell_id: str) -> bool:
    cell = cell_id_to_obj(cell_id)
    col = cell.col_idx
    row = cell.row
    result = (
        LEFT_COLUMN <= col
        and col <= RIGHT_COLUMN
        and TOP_ROW <= row
        and row <= BOTOM_ROW
    )
    return result


def full_cell_id(cell_id: str) -> str:
    dbgp(f"> full_cell_id({cell_id})")
    prefix = WORKSHEET_STACK[-1] if WORKSHEET_STACK else "report"
    if "!" not in cell_id:
        return f"{prefix}!{cell_id}"
    dbgp(f"< full_cell_id -> {cell_id}")
    return cell_id


def cell_obj_to_id(cell: Cell) -> str:
    return cell.parent.title + "!" + cell.coordinate


def cell_id_to_varname(cell_id: str) -> str:
    dbgp(f"> cell_id_to_varname({cell_id})")
    if ":" in cell_id:
        cells = cell_id_to_obj(cell_id)
        cell_ids = [cell_obj_to_id(cell[0]) for cell in cells]
        cell_vars = [cell_id_to_varname(cell_id) for cell_id in cell_ids]
        result = f"[{', '.join(cell_vars)}]"
    else:
        cell_id = full_cell_id(cell_id)
        result = cell_id.replace("!", "_").replace("$", "")
    dbgp(f"< cell_id_to_varname -> {result}")
    return result


def cell_id_to_obj(cell_id: str) -> Cell:
    dbgp(f"> cell_id_to_obj({cell_id})")
    cell_id = full_cell_id(cell_id)
    ws, cell = cell_id.split("!")
    cell = WORKBOOK[ws][cell]
    if isinstance(cell, MergedCell):
        print("WARNING: MergedCell!")
    dbgp(f"< cell_id_to_obj -> {cell}")
    return cell


def unknown_type_exception(token: Token) -> None:
    msg = f"ERROR: Unknown type {token.type}"
    raise Exception(msg)


def unknown_subtype_exception(token: Token) -> None:
    msg = f"ERROR: Unknown subtype {token.subtype} "
    msg += f"(of token type {token.type})"
    raise Exception(msg)


def unknown_func_exception(token: Token) -> None:
    msg = f"ERROR: Unknown FUNC {token.value}"
    raise Exception(msg)


def assert_sep_comma(token: Token) -> None:
    assert token.type == Token.SEP and token.value == ","


def assert_func_close(token: Token) -> None:
    assert token.type == Token.FUNC and token.subtype == Token.CLOSE


def python_cmd_to_read_xml(cell_id: str) -> Optional[str]:
    dbgp(f"> python_cmd_to_read_xml({cell_id})")
    result = None
    cell_id = cell_id.replace("$", "")
    if ":" in cell_id:
        cells = cell_id_to_obj(cell_id)
        cell_ids = [cell_obj_to_id(cell[0]) for cell in cells]
        results = [python_cmd_to_read_xml(cell_id) for cell_id in cell_ids]
        if any(results):
            result = f"[{', '.join(results)}]"
    else:
        cell_id = full_cell_id(cell_id)
        ws, cell = cell_id.split("!")
        if ws == "label":
            value = WORKBOOK[ws][cell].value
            result = f"'{value}'"
        elif ws == "data":
            if cell in SPECIAL_FAPP_XML_CALL:
                result = SPECIAL_FAPP_XML_CALL[cell]
            elif cell in DATA_VALUES:
                result = str(WORKBOOK["data"][cell].value)
            elif is_event_cell(cell_id):
                cell_obj = WORKBOOK[ws][cell]
                col = cell_obj.col_idx - 1
                event_name = WORKBOOK[ws][HEADER_ROW][col].value
                thread_id = cell_obj.row - HEADER_ROW - 1
                result = f"{FAPP_XML_OBJ}.get_event('{event_name}', {thread_id})"
    dbgp(f"< python_cmd_to_read_xml -> {result}")
    return result


def parse_operand(token: Token) -> str:
    dbgp(f"> parse_operand({token})")
    if token.subtype == Token.RANGE:
        cell_id = full_cell_id(token.value)
        raw = python_cmd_to_read_xml(cell_id)
        if raw:
            result = raw
        else:
            cell_to_inst(cell_id)
            result = cell_id_to_varname(cell_id)
    elif token.subtype == Token.TEXT:
        result = token.value
    elif token.subtype == Token.NUMBER:
        result = token.value
    else:
        unknown_subtype_exception(token)
    dbgp(f"< parse_operand -> {result}")
    return result


def parse_func(tokens: list[Token], cur: int):
    dbgp(f"> parse_func({tokens} {cur} = {tokens[cur]})")
    if tokens[cur].subtype == Token.OPEN:
        if tokens[cur].value == "IF(":
            cond, cur = parse_tokens(tokens, cur + 1)
            assert_sep_comma(tokens[cur])
            true_val, cur = parse_tokens(tokens, cur + 1)
            assert_sep_comma(tokens[cur])
            false_val, cur = parse_tokens(tokens, cur + 1)
            assert_func_close(tokens[cur])
            result = f"({true_val}) if ({cond}) else ({false_val})"
        elif tokens[cur].value == "OR(":
            ops, cur = parse_tokens(tokens, cur + 1)
            while tokens[cur].type == Token.SEP and tokens[cur].value == ",":
                tmp, cur = parse_tokens(tokens, cur + 1)
                if tmp != "":
                    ops += f", {tmp}"
            assert_func_close(tokens[cur])
            result = f"(any([{ops}]))"
        elif tokens[cur].value == "COUNT(":
            cells, cur = parse_tokens(tokens, cur + 1)
            assert_func_close(tokens[cur])
            result = f"(sum(1 for e in {cells} if e !=''))"
        elif tokens[cur].value == "SUM(":
            terms, cur = parse_tokens(tokens, cur + 1)
            assert_func_close(tokens[cur])
            result = f"(xls_sum({terms}))"
        elif tokens[cur].value == "AVERAGE(":
            terms, cur = parse_tokens(tokens, cur + 1)
            assert_func_close(tokens[cur])
            result = f"(xls_sum({terms}) / len(xls_nonempty({terms})))"
        # elif tokens[cur].value == "GuardLimitUpper(":
        #     print(tokens[cur:])
        #     result = ""
        else:
            unknown_func_exception(tokens[cur])
    elif tokens[cur].subtype == Token.CLOSE:
        result = None
    else:
        unknown_subtype_exception(tokens[cur])
    dbgp(f"< parse_func -> {result, cur}")
    return result, cur


def parse_infix_op(token: Token) -> str:
    dbgp(f"> parse_infix_op({token})")
    op_name = token.value
    if token.value in INFIX_OP_MAP:
        op_name = INFIX_OP_MAP[token.value]
    dbgp(f"< parse_infix_op -> {op_name}")
    return op_name


def parse_tokens(tokens: list[Token], cur: int) -> (str, int):
    dbgp(f"> parse_tokens({tokens}, {cur} = {tokens[cur]})")
    result = ""
    while cur < len(tokens):
        token = tokens[cur]
        if token.type == Token.OPERAND:
            result += parse_operand(token)
        elif token.type == Token.FUNC:
            tmp, cur = parse_func(tokens, cur)
            if tmp:
                result += tmp
            else:
                break
        elif token.type == Token.OP_IN:
            result += parse_infix_op(token)
        elif token.type == Token.PAREN:
            result += token.value
        elif token.type == Token.WSPACE:
            pass
        elif token.type == Token.SEP:
            break
        else:
            unknown_type_exception(token)
        cur += 1
    dbgp(f"< parse_tokens -> {result, cur}")
    return result, cur


def cell_to_inst(cell_id: str) -> None:
    dbgp(f"> cell_to_inst({cell_id})")
    cell_id = full_cell_id(cell_id)
    cell = cell_id_to_obj(cell_id)
    if isinstance(cell, tuple):
        for c in cell:
            cell_to_inst(cell_obj_to_id(c[0]))
    else:
        cell_var = cell_id_to_varname(cell_id)
        if cell_var in PROCESSED_CELLS:
            return
        WORKSHEET_STACK.append(cell.parent.title)
        tokens = Tokenizer(cell.value).items
        cell_val, _ = parse_tokens(tokens, 0)
        WORKSHEET_STACK.pop()
        line = f"{cell_var} = {cell_val}"
        PROCESSED_CELLS.add(cell_var)
        LINES.append(line)
        dbgp(f"< cell_to_inst -> APPEND: {line}")


def get_label(cell_id: str) -> str:
    cell = WORKBOOK_DATA["report"][cell_id]
    return cell.value


def create_program() -> str:
    with open("fapp_top.py.in") as top:
        result = top.readlines()
    result += [line + "\n" for line in LINES]

    line = "result={"
    for key, value in OUTPUT_DICT.items():
        line += f"'{key}': {value}, "
    line += "}\n"
    result.append(line)

    with open("fapp_bottom.py.in") as top:
        result += top.readlines()

    result = "".join(result)
    with open("read_fapp_xls.out.py", "w") as out:
        out.write(result)
    return result


def add_key_single_value_pair(key: str, value: str) -> None:
    cell_to_inst(value)
    OUTPUT_DICT[get_label(key)] = cell_id_to_varname(value)


def add_column_of_12_1(key: str, first: str, num_rows: int = 12):
    first_cell = cell_id_to_obj(first)
    row = first_cell.row
    col = first_cell.col_idx - 1
    cell_varnames = []
    for offset in range(num_rows):
        cell_id = cell_obj_to_id(WORKBOOK["report"][row + offset][col])
        cell_to_inst(cell_id)
        cell_varnames.append(cell_id_to_varname(cell_id))

    total_id = cell_obj_to_id(WORKBOOK["report"][row + num_rows][col])
    cell_to_inst(total_id)
    total_var = cell_id_to_varname(total_id)

    value = f"[e for e in [{', '.join(cell_varnames)}] if e != '']"
    label = get_label(key)
    OUTPUT_DICT[label] = value
    OUTPUT_DICT[f"{label}_total"] = total_var


def main():
    # add_key_single_value_pair("A3", "C3")
    # add_key_single_value_pair("A4", "C4")
    # add_key_single_value_pair("H3", "J3")
    # add_key_single_value_pair("H4", "J4")
    # add_key_single_value_pair("H5", "J5")
    # add_key_single_value_pair("O3", "Q3")
    # add_key_single_value_pair("O4", "Q4")

    # for col in "CDEFHIJKLMN":
    for col in "L":
        add_column_of_12_1(f"{col}8", f"{col}14")
    assert WORKSHEET_STACK == []

    program = create_program()

    # print(LINES)
    # print(program)
    exec(program)


# main prelude
if "WORKBOOK" not in locals() or "WORKBOOK_DATA" not in locals():
    filename = Path(
        "~/Sync/tmp/work/fapp-xmls/gemver_LARGE.fapp.report/cpu_pa_report.xlsm"
    ).expanduser()
    WORKBOOK = openpyxl.load_workbook(filename)
    WORKBOOK_DATA = openpyxl.load_workbook(filename, data_only=True)
main()
