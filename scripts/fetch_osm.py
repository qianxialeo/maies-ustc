"""可选：重新抓取三校区 OSM 数据到 data/campus3.osm。

默认走 OSM 主 API（小范围 bbox 很稳）；若失败可换 Overpass 镜像。
只在需要更新底图数据时运行，日常开发不必执行。
"""
from __future__ import annotations

import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "campus3.osm"
# lat_min, lon_min, lat_max, lon_max —— 覆盖西区、中区、东区及两条连接街道
BBOX = "31.8335,117.2450,31.8445,117.2690"
UA = {"User-Agent": "maies-ustc-pixel-map/3.0 (offline game art; contact: repo owner)"}


def from_osm_api() -> bytes:
    url = f"https://api.openstreetmap.org/api/0.6/map?bbox={BBOX}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
        return r.read()


def from_overpass() -> bytes:
    query = f"""[out:xml][timeout:240];
(
  way["building"]({BBOX});
  way["highway"]({BBOX});
  way["natural"="water"]({BBOX});
  way["waterway"]({BBOX});
  way["leisure"]({BBOX});
  way["amenity"="college"]({BBOX});
);
out body;
>;
out skel qt;
"""
    data = urllib.parse.urlencode({"data": query}).encode()
    for host in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        try:
            req = urllib.request.Request(host, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r:
                body = r.read()
            if b"<osm" in body[:200]:
                return body
        except Exception as exc:  # noqa: BLE001 - 依次尝试镜像
            print(f"[fetch] {host} 失败：{exc}", file=sys.stderr)
    raise SystemExit("两个数据源都失败了，稍后再试或手动下载后放到 data/campus3.osm")


def main() -> None:
    for name, fn in (("OSM API", from_osm_api), ("Overpass", from_overpass)):
        try:
            raw = fn()
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"[fetch] {name} 失败：{exc}", file=sys.stderr)
            continue
        OUT.write_bytes(raw)
        print(f"[fetch] 已写入 {OUT.relative_to(ROOT)}  {len(raw)/1048576:.2f} MB")
        return
    raise SystemExit("抓取失败，请稍后重试")


if __name__ == "__main__":
    main()
