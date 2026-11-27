# 常用命令都从这里走，Windows 与 macOS/Linux 通用
PY ?= python

.PHONY: help install build serve package clean check fetch-data

help:
	@echo "make install    安装依赖（Pillow + Shapely）"
	@echo "make build      由 data/*.osm 生成 art/ 图层与网页"
	@echo "make serve      构建并在 http://127.0.0.1:8000 预览"
	@echo "make package    打包 dist/MAIES-3campus-<日期>.zip"
	@echo "make check      语法检查（compileall）"
	@echo "make clean      删除生成物"
	@echo "make fetch-data 重新抓取三校区 OSM 数据"

install:
	$(PY) -m pip install -r requirements.txt

build:
	$(PY) scripts/build.py

serve:
	$(PY) scripts/build.py --serve

package: build
	$(PY) scripts/package.py

check:
	$(PY) -m compileall -q source scripts

clean:
	$(PY) -c "import shutil,pathlib;[shutil.rmtree(p,ignore_errors=True) for p in ['art','dist']];[pathlib.Path(f).unlink(missing_ok=True) for f in ['中科大像素漫游.html','中科大全图.png','West-Lakeside.png']]"

fetch-data:
	$(PY) scripts/fetch_osm.py
