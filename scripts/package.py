"""把构建产物打成可分发的 zip（dist/MAIES-3campus-<日期>.zip）。

包里保持“解压即玩”的布局：网页、全图、湖畔放大图、art/、data/、source/、说明文档。
"""
from __future__ import annotations

import datetime as dt
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
FILES = [
    "中科大像素漫游.html",
    "中科大全图.png",
    "West-Lakeside.png",
    "使用说明.md",
    "README.md",
    "LICENSE",
    "LICENSES.md",
    "CONTRIBUTING.md",
    "Makefile",
    "requirements.txt",
    "requirements-dev.txt",
]
DIRS = ["art", "source", "data", "docs", "scripts", "tests"]


def main() -> None:
    missing = [f for f in FILES if not (ROOT / f).exists()]
    if missing:
        raise SystemExit("缺少产物，请先运行 python scripts/build.py：" + ", ".join(missing))
    DIST.mkdir(exist_ok=True)
    stamp = dt.date.today().isoformat()
    out = DIST / f"MAIES-3campus-{stamp}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in FILES:
            z.write(ROOT / name, name)
        for d in DIRS:
            for p in sorted((ROOT / d).rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"}:
                    z.write(p, p.relative_to(ROOT).as_posix())
    print(f"[package] {out.relative_to(ROOT)}  {out.stat().st_size / 1048576:.2f} MB")


if __name__ == "__main__":
    main()
