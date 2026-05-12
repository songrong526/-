# -*- coding: utf-8 -*-
"""
生成活跃信息_yn格式_控制流修正版.py

功能：
1. 从当前脚本所在目录读取：优化四元式.txt
2. 输出：活跃信息_yn格式_控制流修正版.txt

修正点：
1. 不再把 if 分支和 else 分支当成普通顺序语句。
2. if 分支里的赋值不会被 else 分支里的赋值错误覆盖。
3. while 按循环控制流处理。
4. 只有 t 后面接数字的才是临时变量，例如 t1、t2、t10。
5. 普通变量在程序出口默认活跃，临时变量在程序出口默认不活跃。
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "优化四元式.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "活跃信息_yn格式_控制流修正版.txt")

STRUCT_OPS = {"program", "end", "if", "el", "ie", "wh", "do", "we"}


def is_number(x):
    x = str(x).strip()
    if x == "":
        return False
    try:
        float(x)
        return True
    except ValueError:
        return False


def is_temp_var(x):
    """
    只有 t 后面直接接数字，才算临时变量。
    """
    return re.fullmatch(r"t\d+", str(x).strip()) is not None


def is_identifier(x):
    """
    判断是否是普通变量或临时变量。
    """
    x = str(x).strip()
    if x == "":
        return False
    if is_number(x):
        return False
    if x in STRUCT_OPS:
        return False
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", x) is not None


def split_quad(line):
    """
    读取形如：
    1 (+, a, b, t1)
    """
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
            q = split_quad(line)
            if q is not None:
                quads.append(q)
    return quads


def find_pairs(quads):
    """
    寻找 if-el-ie、wh-do-we 的配对位置。
    下标使用 0 开始。
    """
    if_stack = []
    wh_stack = []

    if_to_el = {}
    if_to_ie = {}
    el_to_ie = {}

    wh_to_do = {}
    wh_to_we = {}
    do_to_we = {}
    we_to_wh = {}

    for i, q in enumerate(quads):
        op = q["op"]

        if op == "if":
            if_stack.append({"if": i, "el": None})

        elif op == "el":
            if if_stack:
                if_stack[-1]["el"] = i

        elif op == "ie":
            if if_stack:
                item = if_stack.pop()
                if_pos = item["if"]
                el_pos = item["el"]
                if_to_ie[if_pos] = i
                if el_pos is not None:
                    if_to_el[if_pos] = el_pos
                    el_to_ie[el_pos] = i

        elif op == "wh":
            wh_stack.append({"wh": i, "do": None})

        elif op == "do":
            if wh_stack:
                wh_stack[-1]["do"] = i

        elif op == "we":
            if wh_stack:
                item = wh_stack.pop()
                wh_pos = item["wh"]
                do_pos = item["do"]
                wh_to_we[wh_pos] = i
                we_to_wh[i] = wh_pos
                if do_pos is not None:
                    wh_to_do[wh_pos] = do_pos
                    do_to_we[do_pos] = i

    return {
        "if_to_el": if_to_el,
        "if_to_ie": if_to_ie,
        "el_to_ie": el_to_ie,
        "wh_to_do": wh_to_do,
        "wh_to_we": wh_to_we,
        "do_to_we": do_to_we,
        "we_to_wh": we_to_wh
    }


def build_successors(quads, pairs):
    """
    建立简单控制流后继关系。
    """
    n = len(quads)
    succ = {i: [] for i in range(n)}

    for i, q in enumerate(quads):
        op = q["op"]

        def add(j):
            if 0 <= j < n and j not in succ[i]:
                succ[i].append(j)

        if op == "if":
            # 真分支：下一条
            add(i + 1)

            # 假分支：有 else 到 else 后第一条；无 else 到 ie 后第一条
            if i in pairs["if_to_el"]:
                add(pairs["if_to_el"][i] + 1)
            elif i in pairs["if_to_ie"]:
                add(pairs["if_to_ie"][i] + 1)
            else:
                add(i + 1)

        elif op == "el":
            # if 真分支结束后，跳到 ie 后面
            if i in pairs["el_to_ie"]:
                add(pairs["el_to_ie"][i] + 1)
            else:
                add(i + 1)

        elif op == "we":
            # 循环结束，回到 wh
            if i in pairs["we_to_wh"]:
                add(pairs["we_to_wh"][i])
            add(i + 1)

        elif op == "do":
            # 条件真：进入循环体
            add(i + 1)
            # 条件假：跳出循环
            if i in pairs["do_to_we"]:
                add(pairs["do_to_we"][i] + 1)

        else:
            add(i + 1)

    return succ


def use_def(q):
    """
    计算当前四元式的 use 和 def。
    """
    op = q["op"]
    arg1 = q["arg1"]
    arg2 = q["arg2"]
    result = q["result"]

    use = set()
    define = set()

    if op in {"program", "end", "el", "ie", "wh", "we"}:
        return use, define

    if op in {"if", "do"}:
        if is_identifier(arg1):
            use.add(arg1)
        return use, define

    if is_identifier(arg1):
        use.add(arg1)
    if is_identifier(arg2):
        use.add(arg2)
    if is_identifier(result):
        define.add(result)

    return use, define


def collect_all_names(quads):
    names = set()
    for q in quads:
        for key in ["arg1", "arg2", "result"]:
            x = q[key]
            if is_identifier(x):
                names.add(x)
    return names


def analyze_liveness(quads):
    """
    使用控制流迭代算法计算 live_in / live_out。
    """
    n = len(quads)
    pairs = find_pairs(quads)
    succ = build_successors(quads, pairs)

    use_list = []
    def_list = []

    for q in quads:
        u, d = use_def(q)
        use_list.append(u)
        def_list.append(d)

    all_names = collect_all_names(quads)

    # 程序出口：
    # 普通变量默认活跃，临时变量默认不活跃。
    final_live = {name for name in all_names if not is_temp_var(name)}

    live_in = [set() for _ in range(n)]
    live_out = [set() for _ in range(n)]

    changed = True
    while changed:
        changed = False

        for i in range(n - 1, -1, -1):
            old_in = set(live_in[i])
            old_out = set(live_out[i])

            out_set = set()
            if len(succ[i]) == 0:
                out_set |= final_live
            else:
                for j in succ[i]:
                    out_set |= live_in[j]

            # 如果是最后一条，也并入程序出口活跃变量
            if i == n - 1:
                out_set |= final_live

            in_set = use_list[i] | (out_set - def_list[i])

            live_out[i] = out_set
            live_in[i] = in_set

            if old_in != live_in[i] or old_out != live_out[i]:
                changed = True

    return live_in, live_out


def mark_name(name, active_set):
    if not is_identifier(name):
        return name
    return f"{name}({'y' if name in active_set else 'n'})"


def format_quad(q, live_out_set):
    op = q["op"]
    arg1 = q["arg1"]
    arg2 = q["arg2"]
    result = q["result"]

    # 结构符号不标注 program/main/end 等内容
    if op in {"program", "end", "el", "ie", "wh", "we"}:
        return f"{q['index']} ({op}, {arg1}, {arg2}, {result})"

    # if / do 只可能标条件变量
    if op in {"if", "do"}:
        return f"{q['index']} ({op}, {mark_name(arg1, live_out_set)}, {arg2}, {result})"

    return f"{q['index']} ({op}, {mark_name(arg1, live_out_set)}, {mark_name(arg2, live_out_set)}, {mark_name(result, live_out_set)})"


def main():
    if not os.path.exists(INPUT_FILE):
        print("未找到 优化四元式.txt")
        return

    quads = read_quads()
    if not quads:
        print("未读取到有效四元式")
        return

    live_in, live_out = analyze_liveness(quads)

    lines = []
    for i, q in enumerate(quads):
        lines.append(format_quad(q, live_out[i]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("活跃信息生成完成")


if __name__ == "__main__":
    main()
