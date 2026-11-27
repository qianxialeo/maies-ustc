"""本地预览：构建完成后在 127.0.0.1:8000 打开游戏页面。"""
from __future__ import annotations

import functools
import http.server
import socketserver
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "中科大像素漫游.html"
PORT = 8000


def main() -> None:
    if not PAGE.exists():
        raise SystemExit("还没有构建产物，请先运行 python scripts/build.py")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        url = f"http://127.0.0.1:{PORT}/中科大像素漫游.html"
        print(f"[serve] {url}  (Ctrl+C 退出)")
        webbrowser.open(url)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
