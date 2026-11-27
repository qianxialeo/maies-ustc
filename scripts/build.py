"""一步构建：OSM 数据 -> art/ 图层 -> 可在浏览器打开的 HTML。

用法:
    python scripts/build.py           # 生成 art/ 与中科大像素漫游.html 等产物
    python scripts/build.py --serve   # 构建后启动本地预览服务器
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ("渲染地图图层", ROOT / "source" / "make.py"),
    ("打包网页与全图", ROOT / "source" / "bundle.py"),
]
OUTPUTS = ["中科大像素漫游.html", "中科大全图.png", "West-Lakeside.png"]


def run(step: tuple[str, Path]) -> None:
    name, script = step
    print(f"[build] {name}: {script.relative_to(ROOT)}", flush=True)
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"[build] 失败：{script.name} 退出码 {result.returncode}")


def main() -> None:
    for step in STEPS:
        run(step)
    print("[build] 产物：", flush=True)
    for name in OUTPUTS:
        p = ROOT / name
        if p.exists():
            print(f"  {name}  {p.stat().st_size / 1048576:.2f} MB")
    if "--serve" in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "serve.py")], cwd=ROOT)


if __name__ == "__main__":
    main()
