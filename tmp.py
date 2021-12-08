from pprint import pprint


def path_add(path, item, d):
    cur_dict = d
    for p in path[:-1]:
        if p not in cur_dict:
            cur_dict[p] = {}
        cur_dict = cur_dict[p]
    cur_dict[path[-1]] = item


def main1():
    DICT = {}
    path_add(["foo"], 1, DICT)
    path_add(["bar", "buz1"], 2, DICT)
    path_add(["bar", "buz2"], 3, DICT)
    pprint(DICT)


def _col2num(col: str, base: int = 26) -> int:
    ords = list(map(lambda t: ord(t) - ord("A"), col))
    result = ords[0]
    if len(col) == 2:
        result = (ords[0] + 1) * base + ords[1]
    return result


def _num2col(num: int, base: int = 26) -> str:
    q, r = divmod(num, base)
    result = chr(r + ord("A"))
    if q:
        result = chr(q - 1 + ord("A")) + result
    return result


def col_range(begin: str, end: str):
    assert len(begin) <= 2
    assert len(end) <= 2

    b = _col2num(begin)
    e = _col2num(end)
    return [_num2col(num) for num in range(b, e + 1)]


def main():
    r = col_range("Y", "AC")
    print(r)


main()
