# -*- coding: utf-8 -*-
r"""编码守卫：静态检查本包（以及本包生成/维护的脚本）有没有会引发编码问题的写法。

为什么需要它
------------
编码问题在本包反复以不同面目出现，而且**大多不报错**，只是静默给错结果：

* 控制台默认 GBK，`print` 里出现非 cp936 字符（✅ ❌ ⚠ ² ³ − ✓）会抛
  `UnicodeEncodeError` 并以退出码 1 中断 —— 文件其实已经写好，调用方却判成失败；
  被别的脚本 `import` 当库用时更隐蔽：兜底若只写在 `if __name__ == "__main__"` 里就不生效。
* `open()` 不给 `encoding=` 时按系统 locale 打开（中文 Windows 上是 cp936）：
  读 UTF-8 文件抛 `UnicodeDecodeError`，写中文则落成 GBK，别人按 UTF-8 读成乱码。
* YJK 的结果文件（`wdisp.out` / `wmass.out` / `wpj*.out`）是 **GBK** 写的；
  用 UTF-8 读会整段乱码，而乱码**通常不报错**，只是解析出 0 条记录 —— 典型的静默失败。
* 子进程抓输出不指定编码 → 中文变乱码，错误信息失去价值。
* 带 BOM 的文件会让"按字节读首字段"的解析失败（例如收件箱 ready 文件的首字段本该是 PID）。

用法
----
    python encoding_check.py                  # 检查整包
    python encoding_check.py --root <包根>
    python encoding_check.py --only R2,R8     # 只查指定规则
退出码：0 = 全部通过；1 = 有违规（逐条列出文件:行号）。
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys

TEXT_EXT = (".py", ".md", ".json", ".txt", ".bat", ".cmd", ".ps1", ".ini", ".cfg")

# 非 cp936（GBK）可编码的常见字符 —— 出现在 print 里就必须有控制台兜底
SYMBOLS = "✅❌⚠✓✔✘²³−⇒★☆→①②③④⑤"

# 供应商官方参考代码：原样保留（不是本包运行的代码，改了反而不好对照上游）
IGNORE_PREFIX = ("yjk-dev-refs/", "yjk-dev-refs\\")


def ignored(rel: str) -> bool:
    return rel.startswith(IGNORE_PREFIX)


def non_gbk(ch: str) -> bool:
    try:
        ch.encode("cp936")
        return False
    except UnicodeEncodeError:
        return True


def read_utf8(p: str):
    """按 UTF-8（容忍 BOM）读文本；读不出来返回 None（说明这个文件不是 UTF-8）。"""
    raw = open(p, "rb").read()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def it_files(root, exts=None):
    for dp, dn, fn in os.walk(root):
        if "__pycache__" in dp:
            continue
        for f in sorted(fn):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if ignored(rel):
                continue
            if exts and not f.endswith(exts):
                continue
            yield p, rel


def it_py(root):
    return it_files(root, (".py",))


# ---------------------------------------------------------------- 规则实现
def r1_no_bom(root):
    """源码与文本产物必须是**无 BOM 的 UTF-8**。

    * BOM 会被当成正文：按字节读首字段的解析会失败（收件箱 ready 文件首字段本该是 PID）。
    * 不是 UTF-8（例如被某个编辑器存成 GBK）会让别人按 UTF-8 读成乱码或直接报错。
    """
    out = []
    for p, rel in it_files(root, TEXT_EXT):
        raw = open(p, "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"):
            out.append((rel, 0, "文件带 UTF-8 BOM（应为无 BOM 的 UTF-8）"))
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as e:
            out.append((rel, 0, "不是 UTF-8 编码（第 %d 字节处解码失败）—— 本包文本一律 UTF-8"
                        % e.start))
    return out


def r9_coding_declaration(root):
    """`.py` 首两行应声明 `# -*- coding: utf-8 -*-`。

    Python 3 默认就是 UTF-8，所以这条是**回归守卫**：防止某个编辑器/工具把文件
    另存成别的编码后，文件里又没有声明，问题要等到运行时才暴露。
    """
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        head = src.splitlines()[:2]
        if not any("coding" in h and "utf-8" in h.lower() for h in head):
            out.append((rel, 0, "首两行缺少 `# -*- coding: utf-8 -*-` 声明"))
    return out


def r2_open_encoding(root):
    """所有文本 `open()` 必须显式 `encoding=`。"""
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            out.append((rel, 0, "文件不是 UTF-8 编码（本包源码与产物一律 UTF-8）"))
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            out.append((rel, e.lineno or 0, "语法错误：%s" % e.msg))
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name != "open":
                continue
            kws = {k.arg for k in node.keywords if k.arg}
            mode = None
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
            for k in node.keywords:
                if k.arg == "mode" and isinstance(k.value, ast.Constant):
                    mode = k.value.value
            if isinstance(mode, str) and "b" in mode:
                continue                      # 二进制模式不需要 encoding
            if "encoding" not in kws:
                out.append((rel, node.lineno,
                            "open() 未显式 encoding=（mode=%r）" % (mode,)))
    return out


def _guard_called_in_main(src: str) -> bool:
    """控制台兜底是否在 `main()` 里被调用（这样 import 当库用也覆盖）。"""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    n = getattr(sub.func, "id", None) or getattr(sub.func, "attr", None)
                    if n == "_utf8_console":
                        return True
                    # sys.stdout.reconfigure(...)
                    if n == "reconfigure":
                        return True
    return False


def r3_print_guard(root):
    """print 里出现非 GBK 字符的文件，必须带控制台兜底。"""
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        guarded = ("_utf8_console" in src) or ("reconfigure(" in src)
        for i, l in enumerate(src.splitlines(), 1):
            s = l.strip()
            if s.startswith("#"):
                continue
            if not (re.match(r"print\s*\(", s) or "sys.stdout.write(" in s
                    or "sys.stderr.write(" in s):
                continue
            if any(non_gbk(c) for c in l) and not guarded:
                out.append((rel, i, "print 含非 GBK 字符且本文件无控制台兜底：%s"
                            % s[:56]))
    return out


def r4_yjk_out_gbk(root):
    """读 YJK 结果文件必须用 GBK：不得用 utf-8 **读取** `.out`。

    ★ 只查"读"：`json.dump(..., open(a.out, "w", encoding="utf-8"))` 里的 `a.out`
      是**输出**路径（argparse 的 --out），不是 YJK 的 .out，写成 UTF-8 是对的。
    """
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name != "open":
                continue
            mode = "r"
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                mode = node.args[1].value
            for k in node.keywords:
                if k.arg == "mode" and isinstance(k.value, ast.Constant):
                    mode = k.value.value
            if "r" not in str(mode):
                continue                       # 写模式：不关 YJK 输出的事
            seg = ast.get_source_segment(src, node) or ""
            if ".out" not in seg:
                continue
            enc = None
            for k in node.keywords:
                if k.arg == "encoding" and isinstance(k.value, ast.Constant):
                    enc = k.value.value
            if isinstance(enc, str) and enc.lower().startswith("utf"):
                out.append((rel, node.lineno,
                            "读 .out 却用 UTF-8 解码（YJK 结果文件是 GBK）：%s"
                            % seg.splitlines()[0][:56]))
        # 同一行里既提到 YJK 结果文件名、又在读文件，却全文没有 gbk 字样 → 请人工确认口径。
        # （按"同一行"是为了避开只把 wpj 当**正则字面量**用的文件，如 portability_check.py 的白名单）
        if "gbk" not in src.lower():
            for i, l in enumerate(src.splitlines(), 1):
                if not re.search(r"wdisp|wmass|wpj\d*", l):
                    continue
                if not re.search(r"open\(|read_text\(|\.read\(\)|\.readlines\(\)", l):
                    continue
                out.append((rel, i, "同一行里读 YJK 结果文件但未见 gbk：%s" % l.strip()[:56]))
    return out


def r5_cli_guard(root):
    """CLI 入口含非 GBK 字符时必须能兜底（定义或调用 _utf8_console / reconfigure）。"""
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None or "__main__" not in src:
            continue
        if any(non_gbk(c) for c in src) and "_utf8_console" not in src \
                and "reconfigure(" not in src:
            out.append((rel, 0, "CLI 入口含非 GBK 字符但没有控制台兜底"))
    return out


def r6_subprocess_encoding(root):
    """subprocess 抓文本输出必须显式 encoding（否则按 locale 解码）。"""
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            n = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if n not in ("run", "check_output", "Popen"):
                continue
            kws = {k.arg for k in node.keywords if k.arg}
            capturing = ("capture_output" in kws) or ("stdout" in kws)
            if capturing and "text" in kws and "encoding" not in kws:
                out.append((rel, node.lineno, "subprocess 抓文本但未指定 encoding="))
    return out


def r7_json_ensure_ascii(root):
    """写 JSON 应 `ensure_ascii=False`（否则中文写成 \\uXXXX，人不可读）。"""
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "dump":
                kws = {k.arg for k in node.keywords if k.arg}
                if "ensure_ascii" not in kws:
                    out.append((rel, node.lineno,
                                "json.dump 未给 ensure_ascii=（中文会写成 \\uXXXX）"))
    return out


def _guard_called_in_public_entry(src: str) -> bool:
    """在没有 `main()` 的库里，兜底是否在**公开入口函数**里调用。

    ★ 为什么要有这一档：`ydb_serialize.py` 这种**以库形式被调用**的模块没有 `main()`，
      它把 `_utf8_console()` 放在对外入口 `serialize()` 里 —— 这也是对的
      （调用方 import 它之后走的就是那个入口）。只认 `main()` 会把它误报成违规。
      判据：存在**不以 `_` 开头**的函数，其函数体里调用了 `_utf8_console()`/`reconfigure`。
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                n = getattr(sub.func, "id", None) or getattr(sub.func, "attr", None)
                if n in ("_utf8_console", "reconfigure"):
                    return True
    return False


def r8_guard_in_main(root):
    """兜底必须在 `main()`（或库模块的公开入口）里调用。

    只在 `if __name__ == "__main__"` 里调用时，**被 import 当库用**仍会在 GBK 控制台崩。
    """
    out = []
    for p, rel in it_py(root):
        src = read_utf8(p)
        if src is None:
            continue
        prints_non_gbk = any(
            any(non_gbk(c) for c in l) and re.match(r"\s*print\s*\(", l)
            for l in src.splitlines())
        if not prints_non_gbk:
            continue
        if _guard_called_in_main(src) or _guard_called_in_public_entry(src):
            continue
        out.append((rel, 0, "文件里有非 GBK 的 print，但 `_utf8_console()` 既没在 main() 里、"
                            "也没在公开入口函数里调用（被 import 当库用时 GBK 控制台会崩）"))
    return out


RULES = [
    ("R1", "文本文件为无 BOM 的 UTF-8", r1_no_bom),
    ("R2", "open() 显式 encoding=", r2_open_encoding),
    ("R3", "print 非 GBK 字符有兜底", r3_print_guard),
    ("R4", "YJK 结果文件按 GBK 读", r4_yjk_out_gbk),
    ("R5", "CLI 入口有控制台兜底", r5_cli_guard),
    ("R6", "subprocess 抓文本指定 encoding", r6_subprocess_encoding),
    ("R7", "json.dump 用 ensure_ascii=False", r7_json_ensure_ascii),
    ("R8", "兜底在 main() 里调用（库调用也安全）", r8_guard_in_main),
    ("R9", ".py 声明 coding: utf-8", r9_coding_declaration),
]


def pkg_root(explicit=None):
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get("YJK_SKILLS_DIR")
    if env and os.path.isdir(env):
        return os.path.abspath(env)
    # 本文件位于 <包根>/<技能>/scripts/ 下
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv=None):
    ap = argparse.ArgumentParser(description="编码守卫（静态检查）")
    ap.add_argument("--root", default=None, help="包根；默认按本文件位置推断")
    ap.add_argument("--only", default=None, help="只查指定规则，如 R2,R8")
    ap.add_argument("--max", type=int, default=30, help="每条规则最多列几行")
    a = ap.parse_args(argv)
    root = pkg_root(a.root)
    want = set((a.only or "").split(",")) - {""}

    print("=" * 78)
    print("编码守卫：%s" % root)
    print("（忽略目录：%s —— 供应商官方参考代码，原样保留）"
          % ", ".join(sorted({x.rstrip("/\\") for x in IGNORE_PREFIX})))
    print("=" * 78)
    total = 0
    for rid, desc, fn in RULES:
        if want and rid not in want:
            continue
        probs = fn(root)
        total += len(probs)
        print("[%s] %-38s %s" % (rid, desc, "通过" if not probs else "%d 处" % len(probs)))
        for rel, ln, msg in probs[:a.max]:
            print("     %s:%s  %s" % (rel, ln, msg))
        if len(probs) > a.max:
            print("     …… 其余 %d 处省略" % (len(probs) - a.max))
    print("=" * 78)
    if total:
        print("结论：不通过 —— 共 %d 处。修法见各条说明；本包要求：源码与产物 UTF-8（无 BOM）、"
              "open() 显式 encoding、YJK 结果文件按 GBK 读、非 GBK 输出有控制台兜底"
              "（且在 main() 里调用）、subprocess 抓文本指定 encoding、json 用 ensure_ascii=False。"
              % total)
        return 1
    print("结论：通过 —— 编码约定全部满足")
    return 0


def _utf8_console():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


if __name__ == "__main__":
    _utf8_console()
    sys.exit(main())
