# 原始地理数据

| 文件 | 内容 | 来源 |
| --- | --- | --- |
| `campus3.osm` | 西区、中区、东区及周边（建筑、道路、水系、球场、校区边界） | OSM 主 API，bbox `31.8335,117.2450,31.8445,117.2690` |
| `west.osm` | 早期西区节选，供旧版等轴测生成器与对照使用 | OSM（Overpass 导出） |

## 授权

© OpenStreetMap contributors，**ODbL 1.0**。https://www.openstreetmap.org/copyright

- 允许复制、分发、修改与商业使用，但必须署名，且派生数据库需以相同方式共享。
- 本仓库的像素地图由该数据派生，因此美术部分采用 CC BY-SA 4.0（见 `LICENSES.md`）。

## 坐标系

```python
x = (lon - 117.255) * 94650    # 米，东向
y = (lat - 31.84)  * 110900    # 米，北向
```

## 重新抓取

```bash
python scripts/fetch_osm.py
```

抓取后重跑 `python scripts/build.py`，并检查三处易坏点：
田径场跑道、肥西路斑马线、金寨路地下通道的连通性。
