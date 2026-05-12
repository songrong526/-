# -*- coding: utf-8 -*-
"""
生成目标代码_单寄存器R显式版.py

功能：
1. 从当前脚本所在目录读取：优化四元式.txt
2. 生成整体汇编伪代码
3. 默认只有一个寄存器 R
4. 目标代码中显式写出寄存器 R
5. 保存数据时使用 ST 指令
6. 每条目标代码带行号
7. 跳转指令直接跳转到具体行号
8. 输出：目标代码_单寄存器R显式版.txt

伪指令含义：
LD R, x      表示 R = x
ST x, R      表示 x = R
ADD R, x     表示 R = R + x
SUB R, x     表示 R = R - x
MUL R, x     表示 R = R * x
DIV R, x     表示 R = R / x
CMP R, x     表示比较 R 和 x
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "优化四元式.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "目标代码_单寄存器R显式版.txt")

REL_JUMP_TRUE = {
    ">": "JG",
    "<": "JL",
    ">=": "JGE",
    "<=": "JLE",
    "==": "JE",
    "!=": "JNE"
}


def parse_quad_line(line):
    line = line.strip()
    m = re.match(r"^\s*(\d+)\s*\((.*)\)\s*$", line)
    if not m:
        return None

    index = int(m.group(1))
    body = m.group(2)
    parts = [p.strip() for p in body.split(",")]

    while len(parts) < 4:
        parts.append("")

    return {
        "index": index,
        "op": parts[0],
        "arg1": parts[1],
        "arg2": parts[2],
        "result": ",".join(parts[3:]).strip()
    }


def read_quads():
    quads = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            q = parse_quad_line(line)
            if q is not None:
                quads.append(q)
    return quads


def emit(code, text):
    code.append({
        "kind": "code",
        "text": text
    })


def label(code, name):
    code.append({
        "kind": "label",
        "name": name
    })


def generate_raw_code(quads):
    code = []

    if_count = 0
    while_count = 0
    rel_count = 0

    if_stack = []
    while_stack = []

    for q in quads:
        op = q["op"]
        a1 = q["arg1"]
        a2 = q["arg2"]
        res = q["result"]

        if op == "program":
            name = a1 if a1 else "main"
            emit(code, f"PROC {name}")

        elif op == "end":
            name = a1 if a1 else "main"
            emit(code, f"ENDP {name}")

        elif op == "=":
            emit(code, f"LD R, {a1}")
            emit(code, f"ST {res}, R")

        elif op == "+":
            emit(code, f"LD R, {a1}")
            emit(code, f"ADD R, {a2}")
            emit(code, f"ST {res}, R")

        elif op == "-":
            emit(code, f"LD R, {a1}")
            emit(code, f"SUB R, {a2}")
            emit(code, f"ST {res}, R")

        elif op == "*":
            emit(code, f"LD R, {a1}")
            emit(code, f"MUL R, {a2}")
            emit(code, f"ST {res}, R")

        elif op == "/":
            emit(code, f"LD R, {a1}")
            emit(code, f"DIV R, {a2}")
            emit(code, f"ST {res}, R")

        elif op in REL_JUMP_TRUE:
            rel_count += 1
            true_label = f"REL_TRUE_{rel_count}"
            end_label = f"REL_END_{rel_count}"

            emit(code, f"LD R, {a1}")
            emit(code, f"CMP R, {a2}")
            emit(code, f"{REL_JUMP_TRUE[op]} {true_label}")
            emit(code, "LD R, 0")
            emit(code, f"ST {res}, R")
            emit(code, f"JMP {end_label}")
            label(code, true_label)
            emit(code, "LD R, 1")
            emit(code, f"ST {res}, R")
            label(code, end_label)

        elif op == "if":
            if_count += 1
            else_label = f"ELSE_{if_count}"
            end_label = f"IF_END_{if_count}"
            if_stack.append((else_label, end_label))

            emit(code, f"LD R, {a1}")
            emit(code, "CMP R, 0")
            emit(code, f"JE {else_label}")

        elif op == "el":
            if if_stack:
                else_label, end_label = if_stack[-1]
                emit(code, f"JMP {end_label}")
                label(code, else_label)

        elif op == "ie":
            if if_stack:
                else_label, end_label = if_stack.pop()
                label(code, end_label)

        elif op == "wh":
            while_count += 1
            begin_label = f"WHILE_BEGIN_{while_count}"
            end_label = f"WHILE_END_{while_count}"
            while_stack.append((begin_label, end_label))

            label(code, begin_label)

            if a1:
                emit(code, f"LD R, {a1}")
                emit(code, "CMP R, 0")
                emit(code, f"JE {end_label}")

        elif op == "do":
            if while_stack:
                begin_label, end_label = while_stack[-1]

                if a1:
                    emit(code, f"LD R, {a1}")
                    emit(code, "CMP R, 0")
                    emit(code, f"JE {end_label}")

        elif op == "we":
            if while_stack:
                begin_label, end_label = while_stack.pop()
                emit(code, f"JMP {begin_label}")
                label(code, end_label)

        else:
            emit(code, f"; 未处理四元式 ({op}, {a1}, {a2}, {res})")

    return code


def assign_line_numbers(raw_code):
    label_to_line = {}
    line_no = 1

    for item in raw_code:
        if item["kind"] == "label":
            label_to_line[item["name"]] = line_no
        else:
            item["line_no"] = line_no
            line_no += 1

    return label_to_line


def replace_labels_with_lines(raw_code, label_to_line):
    result = []

    for item in raw_code:
        if item["kind"] != "code":
            continue

        text = item["text"]

        for name, line_no in label_to_line.items():
            text = re.sub(r"\b" + re.escape(name) + r"\b", str(line_no), text)

        result.append(f"{item['line_no']:03d}: {text}")

    return result


def main():
    if not os.path.exists(INPUT_FILE):
        print("未找到 优化四元式.txt")
        return

    quads = read_quads()
    if not quads:
        print("未读取到有效四元式")
        return

    raw_code = generate_raw_code(quads)
    label_to_line = assign_line_numbers(raw_code)
    final_lines = replace_labels_with_lines(raw_code, label_to_line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))

    print("单寄存器 R 显式版目标代码生成完成：目标代码_单寄存器R显式版.txt")


if __name__ == "__main__":
    main()
