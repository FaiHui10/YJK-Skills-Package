# -*- coding: utf-8 -*-
r"""读 YJK 导出的 xlsx（`施工图/全楼*钢筋用量*.xlsx`）。

坑：YJK 写出的 `styles.xml` 里有**非 aRGB 的 rgb 值**（如 `rgb="auto"` 或 6 位色值），
openpyxl 直接抛 `Colors must be aRGB hex values`，整本读不了。

办法：把 xlsx 当 zip 读出来，**修好 styles.xml 的 rgb 属性**，再交给 openpyxl。
只在内存里改，不动原文件。
"""
import io
import os
import re
import zipfile

import openpyxl


def _fix_styles(data: bytes) -> bytes:
    """把 rgb="..." 里非 8 位十六进制的值换成合法值。"""
    def rep(m):
        v = m.group(1)
        if re.fullmatch(r"[0-9A-Fa-f]{8}", v or ""):
            return m.group(0)
        if re.fullmatch(r"[0-9A-Fa-f]{6}", v or ""):
            return 'rgb="FF%s"' % v
        return 'rgb="FF000000"'

    txt = data.decode("utf-8", errors="replace")
    txt = re.sub(r'rgb="([^"]*)"', rep, txt)
    # theme/indexed 属性也可能越界，一并去掉，避免 again 抛错
    txt = re.sub(r'\s(?:theme|indexed)="[^"]*"', "", txt)
    return txt.encode("utf-8")


def load(path):
    """返回 openpyxl Workbook（已修 styles）。"""
    with zipfile.ZipFile(path) as z:
        items = {n: z.read(n) for n in z.namelist()}
    if "xl/styles.xml" in items:
        items["xl/styles.xml"] = _fix_styles(items["xl/styles.xml"])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in items.items():
            z.writestr(n, b)
    buf.seek(0)
    return openpyxl.load_workbook(buf, data_only=True)


def dump(path, maxrow=40):
    wb = load(path)
    print("=" * 74)
    print(os.path.basename(path), " 工作表:", wb.sheetnames)
    for ws in wb.worksheets:
        print("  --- [%s]  %d 行 × %d 列 ---" % (ws.title, ws.max_row,
                                                 ws.max_column))
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= maxrow:
                print("   ...（还有 %d 行）" % (ws.max_row - maxrow))
                break
            cells = ["" if c is None else c for c in row]
            while cells and cells[-1] == "":
                cells.pop()
            print("   ", cells)


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        dump(p)
