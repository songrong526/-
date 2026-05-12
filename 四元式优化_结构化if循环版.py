# -*- coding: utf-8 -*-
"""
四元式优化_结构化if循环版.py

功能：
1. 从脚本同目录读取：四元式序列.txt
2. 四元式格式：
   1 (=, 2, , a)
   2 (*, 2, 5, t1)
   3 (>, b, a, t2)
   4 (if, t2, , )
   5 (/, b, 2, t3)
   6 (=, t3, , c)
   7 (el, , , )
   8 (=, a, , c)
   9 (ie, , , )
   10 (<, a, b, t4)
   11 (wh, t4, , )
   12 (+, a, 1, t5)
   13 (=, t5, , a)
   14 (we, , , )

3. 输出：
   优化四元式.txt
   基本块划分.txt
   循环优化信息.txt

说明：
- if / el / ie 表示 if-else 结构
- wh / do / we 表示 while 结构，do 可有可无
- 输出文件中只保留四元式或分析结果，不加入输入输出说明
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "四元式序列.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "优化四元式.txt")
BLOCK_FILE = os.path.join(BASE_DIR, "基本块划分.txt")
LOOP_FILE = os.path.join(BASE_DIR, "循环优化信息.txt")

ARITH_OPS = {"+", "-", "*", "/"}
REL_OPS = {">", "<", ">=", "<=", "==", "!="}
LOGIC_OPS = {"&&", "||"}
STRUCT_OPS = {"if", "el", "ie", "wh", "do", "we"}


def is_number(x):
    x = str(x).strip()
    if x == "":
        return False
    try:
        float(x)
        return True
    except ValueError:
        return False


def format_number(x):
    if int(x) == x:
        return str(int(x))
    return str(x)


def calc_binary(op, a, b):
    a = float(a)
    b = float(b)

    if op == "+":
        return format_number(a + b)
    if op == "-":
        return format_number(a - b)
    if op == "*":
        return format_number(a * b)
    if op == "/":
        if b == 0:
            return None
        return format_number(a / b)

    if op == ">":
        return "1" if a > b else "0"
    if op == "<":
        return "1" if a < b else "0"
    if op == ">=":
        return "1" if a >= b else "0"
    if op == "<=":
        return "1" if a <= b else "0"
    if op == "==":
        return "1" if a == b else "0"
    if op == "!=":
        return "1" if a != b else "0"

    return None


def normalize_empty(x):
    x = x.strip()
    if x == "_":
        return ""
    return x


def read_quads():
    quads = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pattern = re.compile(r"^\s*(\d+)\s*\((.*)\)\s*$")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = pattern.match(line)
        if not m:
            continue

        old_index = int(m.group(1))
        body = m.group(2)
        parts = body.split(",")

        while len(parts) < 4:
            parts.append("")

        op = normalize_empty(parts[0])
        arg1 = normalize_empty(parts[1])
        arg2 = normalize_empty(parts[2])
        result = normalize_empty(",".join(parts[3:]))

        quads.append({
            "index": old_index,
            "op": op,
            "arg1": arg1,
            "arg2": arg2,
            "result": result
        })

    return quads


def write_quads(quads, filename):
    lines = []

    for i, q in enumerate(quads, start=1):
        lines.append(
            f"{i} ({q['op']}, {q['arg1']}, {q['arg2']}, {q['result']})"
        )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def replace_value(x, value_map):
    if x in value_map:
        return value_map[x]
    return x


def optimize_quads(quads):
    optimized = []
    value_map = {}

    for q in quads:
        op = q["op"]
        arg1 = replace_value(q["arg1"], value_map)
        arg2 = replace_value(q["arg2"], value_map)
        result = q["result"]

        # 结构控制符不做删除，只替换条件临时变量
        if op in STRUCT_OPS:
            optimized.append({
                "index": q["index"],
                "op": op,
                "arg1": arg1,
                "arg2": arg2,
                "result": result
            })
            continue

        # 赋值传播
        if op == "=":
            if result:
                value_map[result] = arg1
            optimized.append({
                "index": q["index"],
                "op": op,
                "arg1": arg1,
                "arg2": "",
                "result": result
            })
            continue

        # 常量折叠：算术、关系、逻辑
        if op in ARITH_OPS or op in REL_OPS:
            if is_number(arg1) and is_number(arg2):
                folded = calc_binary(op, arg1, arg2)
                if folded is not None and result:
                    value_map[result] = folded
                    optimized.append({
                        "index": q["index"],
                        "op": "=",
                        "arg1": folded,
                        "arg2": "",
                        "result": result
                    })
                    continue

        if op in LOGIC_OPS:
            if is_number(arg1) and is_number(arg2):
                a = int(float(arg1)) != 0
                b = int(float(arg2)) != 0
                if op == "&&":
                    folded = "1" if a and b else "0"
                else:
                    folded = "1" if a or b else "0"
                if result:
                    value_map[result] = folded
                    optimized.append({
                        "index": q["index"],
                        "op": "=",
                        "arg1": folded,
                        "arg2": "",
                        "result": result
                    })
                    continue

        # 若 result 被重新定义，清除它原来的传播值
        if result in value_map:
            del value_map[result]

        optimized.append({
            "index": q["index"],
            "op": op,
            "arg1": arg1,
            "arg2": arg2,
            "result": result
        })

    return optimized


def divide_basic_blocks(quads):
    leaders = set()

    if quads:
        leaders.add(0)

    for i, q in enumerate(quads):
        op = q["op"]

        if op in {"if", "el", "ie", "wh", "do", "we"}:
            leaders.add(i)
            if i + 1 < len(quads):
                leaders.add(i + 1)

    leaders = sorted(leaders)
    blocks = []

    for idx, start in enumerate(leaders):
        end = leaders[idx + 1] - 1 if idx + 1 < len(leaders) else len(quads) - 1
        if start <= end:
            blocks.append((start, end))

    return blocks


def write_basic_blocks(quads, blocks):
    lines = []

    for block_id, (start, end) in enumerate(blocks, start=1):
        lines.append(f"B{block_id}:")
        for i in range(start, end + 1):
            q = quads[i]
            lines.append(f"  {i + 1} ({q['op']}, {q['arg1']}, {q['arg2']}, {q['result']})")
        lines.append("")

    with open(BLOCK_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip())


def find_while_loops(quads):
    loops = []
    stack = []

    for i, q in enumerate(quads):
        op = q["op"]
        if op == "wh":
            stack.append(i)
        elif op == "we" and stack:
            start = stack.pop()
            loops.append((start, i))

    return loops


def collect_assigned_vars(quads, start, end):
    assigned = set()
    for i in range(start, end + 1):
        result = quads[i]["result"]
        op = quads[i]["op"]
        if result and op not in STRUCT_OPS:
            assigned.add(result)
    return assigned


def is_temp_var(x):
    return re.match(r"^t\d+$", x or "") is not None


def loop_invariant_motion(quads):
    loops = find_while_loops(quads)
    info_lines = []

    # 为避免改变结构四元式顺序过多，这里只识别并记录可外提语句；
    # 若确实安全，则把它移动到 wh 前面。
    moved_indices = set()
    insert_before = {}

    for loop_id, (start, end) in enumerate(loops, start=1):
        assigned = collect_assigned_vars(quads, start + 1, end - 1)
        invariants = []

        for i in range(start + 1, end):
            q = quads[i]
            op = q["op"]
            arg1 = q["arg1"]
            arg2 = q["arg2"]
            result = q["result"]

            if op not in ARITH_OPS:
                continue
            if not result or not is_temp_var(result):
                continue

            arg1_ok = is_number(arg1) or arg1 not in assigned
            arg2_ok = is_number(arg2) or arg2 not in assigned

            if arg1_ok and arg2_ok:
                invariants.append(i)

        info_lines.append(f"循环{loop_id}: 第{start + 1}条 到 第{end + 1}条")

        if invariants:
            info_lines.append("  可外提四元式:")
            insert_before.setdefault(start, [])
            for i in invariants:
                q = quads[i]
                info_lines.append(f"    {i + 1} ({q['op']}, {q['arg1']}, {q['arg2']}, {q['result']})")
                insert_before[start].append(q)
                moved_indices.add(i)
        else:
            info_lines.append("  未发现可外提的循环不变式")

        info_lines.append("")

    new_quads = []
    for i, q in enumerate(quads):
        if i in insert_before:
            new_quads.extend(insert_before[i])
        if i not in moved_indices:
            new_quads.append(q)

    if not loops:
        info_lines.append("未发现 while 循环")

    with open(LOOP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(info_lines).rstrip())

    return new_quads


def main():
    if not os.path.exists(INPUT_FILE):
        print("未找到四元式序列.txt")
        return

    quads = read_quads()

    if not quads:
        print("未读取到有效四元式")
        return

    optimized = optimize_quads(quads)
    optimized = loop_invariant_motion(optimized)
    write_quads(optimized, OUTPUT_FILE)

    blocks = divide_basic_blocks(optimized)
    write_basic_blocks(optimized, blocks)

    print("四元式优化完成")


if __name__ == "__main__":
    main()
