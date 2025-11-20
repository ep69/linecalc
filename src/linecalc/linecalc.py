#!/usr/bin/env python3

import sys
import re
import os
import readline  # noqa: F401
import importlib.metadata
import requests
from icecream import ic

ic.disable()

# so we can fetch data only once in a session
CONVERT_DATA = None


def _convert_fetch_data():
    global CONVERT_DATA
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
    r = requests.get(url)
    r.raise_for_status()
    CONVERT_DATA = r.json()["usd"]


def convert(base="usd", quote="czk"):
    ic("convert", base, quote)
    if CONVERT_DATA is None:
        _convert_fetch_data()
    # ic(data)
    result = CONVERT_DATA.get(quote)
    result /= CONVERT_DATA.get(base)
    ic(result)
    return result


def is_op(op):
    return op in OP_PRIO.keys()


def op_eval(val, op, other):
    if op == "+":
        return val + other
    elif op == "-":
        return val - other
    elif op == "*":
        return val * other
    elif op == "/":
        return val / other
    elif op == "^":
        return pow(val, other)
    else:
        assert False


def stack_eval_lr(stack, start, end, ops):
    fst = None
    op, opi = None, -1
    snd, sndi = None, -1
    for i in range(start, end):
        if stack[i] is not None:
            if fst is None:
                fst = stack[i]
                fsti = i
            elif op is None:
                op = stack[i]
                opi = i
            elif snd is None:
                snd = stack[i]
                sndi = i
                if op in ops:
                    val = op_eval(fst, op, snd)
                    stack[fsti] = None
                    stack[opi] = None
                    stack[sndi] = val
                    fst, fsti = val, sndi
                    op, snd = None, None
                else:
                    fst, fsti = snd, sndi
                    op, snd = None, None


def stack_eval_rl(stack, start, end, ops):
    fst = None
    op, opi = None, -1
    snd, sndi = None, -1
    for i in range(end - 1, start - 1, -1):
        if stack[i] is not None:
            if snd is None:
                snd = stack[i]
                sndi = i
            elif op is None:
                op = stack[i]
                opi = i
            elif fst is None:
                fst = stack[i]
                fsti = i
                if op in ops:
                    val = op_eval(fst, op, snd)
                    stack[sndi] = None
                    stack[opi] = None
                    stack[fsti] = val
                    snd, sndi = val, fsti
                    op, fst = None, None
                else:
                    snd, sndi = fst, fsti
                    op, snd = None, None


def stack_eval_range(stack, start, end):
    ic("stack_eval_range", stack, start, end)
    for ops in "^":
        stack_eval_rl(stack, start, end, ops)
    for ops in ("*/", "+-"):
        stack_eval_lr(stack, start, end, ops)
    ic("stack_eval_range END", stack)


def f_conv(stack, m):
    ic("f_conv", m.group())
    i = stack_rindex_notnone(stack)
    val = stack[i]
    unit = m.group()
    stack[i] = val * convert(unit)


def f_space(stack, _):
    pass


def f_op(stack, m):
    op = m.group()
    if op == "x":
        op = "*"
    # interpret(stack, op)
    stack.append(op)


def f_num(stack, m):
    stack.append(float(m.group()))


def f_left_par(stack, m):
    stack.append(m.group())


def stack_rindex(stack, item):
    result = None
    for i in range(len(stack) - 1, -1, -1):
        if stack[i] == item:
            result = i
            break
    return result


def stack_rindex_notnone(stack):
    result = None
    for i in range(len(stack) - 1, -1, -1):
        if stack[i] is not None:
            result = i
            break
    return result


def f_right_par(stack, m):
    lefti = stack_rindex(stack, "(")
    stack_eval_range(stack, lefti + 1, len(stack))
    stack[lefti] = None


class FinalUnit:
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return f"FinalUnit({self.val:.2f})"


def f_final_unit(stack, m):
    unit = m.group(1)
    stack.append(FinalUnit(convert(unit)))
    if False:
        stack_eval_range(stack, 0, len(stack))
        i = stack_rindex_notnone(stack)
        val = stack[i]
        stack[i] = val / convert(unit)


RE_TOKENS = [
    # 'x' can be used instead of '*'
    ("re_op", f_op, re.compile(r"[\+\-\*/^]|(x(?![a-zA-Z]))")),
    # whole line can be ended with a unit for final conversion - 'to usd'
    ("re_final_unit", f_final_unit, re.compile(r"to\s+([a-zA-Z]+)\s*")),
    ("re_conv", f_conv, re.compile(r"([a-zA-Z]+)")),
    ("re_space", f_space, re.compile(r" +")),
    ("re_num", f_num, re.compile(r"[0-9]+(\.[0-9]+)?")),
    ("re_left_par", f_left_par, re.compile(r"\(")),
    ("re_right_par", f_right_par, re.compile(r"\)")),
]


OP_PRIO = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "^": 3,
}


def handle_line(line):
    index = 0
    stack = []
    while True:
        m = None
        ic(index, line[index:])
        for name, fun, r in RE_TOKENS:
            m = r.match(line[index:])
            if m:
                ic("token", name, m.group())
                fun(stack, m)
                break
        ic(m)
        if not m:
            break
        index += m.end()
    if len(line[index:]) > 0:
        print(f'Warning: part of line not parsed: "{line[index:]}"')

    ic("stack before final processing:", stack)
    final_unit = 1.0
    last_item = stack[len(stack) - 1]
    if isinstance(last_item, FinalUnit):
        final_unit = last_item.val
        del stack[len(stack) - 1]

    ic(final_unit)
    stack_eval_range(stack, 0, len(stack))
    ic("final stack:", stack)

    vals = list(filter(lambda x: x is not None, stack))
    assert len(vals) == 1
    ic("filtered stack", vals)
    val = vals[0] / final_unit
    ic(val)

    return val


def main():
    if len(sys.argv) >= 2 and (sys.argv[1] == "-v" or sys.argv[1] == "--version"):
        print(f"Version: {importlib.metadata.version('linecalc')}")
        return 0

    if len(sys.argv) >= 2 and sys.argv[1] == "-d":
        ic.enable()
        del sys.argv[1]

    if os.environ.get("DEBUG", False):
        ic.enable()

    a = []
    for i in range(1, len(sys.argv)):
        ic(f"{i}: {sys.argv[i]}")
        a.append(sys.argv[i])
    ic(a)
    line = " ".join(a)
    ic(line)

    if line:  # specified as arguments
        val = handle_line(line)
        # final number - TADAAA
        ic(val)
        print(f"{val:.2f}")
    else:  # read indefinitely from stdin
        while True:
            try:
                line = input().strip()
            except EOFError:
                ic("input: EOFError")
                break
            ic(line)
            if line:
                val = handle_line(line)
                ic(val)
                print(f"{val:.2f}")
            else:
                break


if __name__ == "__main__":
    main()
