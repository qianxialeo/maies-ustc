# 贡献指南

欢迎加入《镜渊》地图项目。这个仓库是“生成式像素地图”：**源码 + OSM 数据**进，**离线网页**出。
所以规则的核心只有一条——**只提交源头，不提交产物**。

## 0. 先跑起来

```bash
python -m pip install -r requirements-dev.txt
python scripts/build.py --serve     # 构建 + 本地预览
python -m ruff check --select E9,F source scripts   # 与 CI 同款的最小检查
```

构建约 10 秒；产物在 `art/`、`中科大像素漫游.html` 等位置，均已在 `.gitignore` 中。

## 1. 分支与合并

| 分支 | 用途 |
| --- | --- |
| `main` | 始终保持可构建、可玩；受保护，不能直推 |
| `feat/<主题>` | 新功能，例如 `feat/xiaomo-npc` |
| `fix/<主题>` | 修 bug，例如 `fix/tunnel-nav-mask` |
| `art/<主题>` | 纯美术调整，例如 `art/east-dorm-palette` |
| `docs/<主题>` | 文档 |
| `chore/<主题>` | 依赖、CI、脚本 |

流程：`git switch -c feat/xxx` → 小步提交 → 推送 → 开 PR（草稿即可早开）→ 至少 1 人 review → **Squash merge** → 删分支。

## 2. 提交信息

用 Conventional Commits，中文正文可以，类型与范围用英文：

```
feat(game): 加入小茉的对话触发与立绘占位
fix(map): 地下通道 nav 掩码断开，中区无法走到东区
art(building): 东区宿舍改为暖白 + 阳台栏板
docs(arch): 补充 scene.json 字段说明
chore(ci): 缓存 pip 依赖
```

一次提交只做一件事。涉及“大量重新生成的产物”不要提交（见下）。

## 3. 哪些文件能动

| 想改的东西 | 改哪里 |
| --- | --- |
| 建筑外观、屋顶、铺装、水系、田径场 | `source/make.py` |
| 角色、移动、相机、UI、镜渊效果 | `source/game.html` |
| 打包方式、缩略图、湖畔图 | `source/bundle.py` |
| 地标名称与描述 | `source/make.py` 末尾的 marks 列表 |
| 底图数据 | `data/campus3.osm`（用 `python scripts/fetch_osm.py` 更新） |

**不要直接改 `art/`、`中科大像素漫游.html`、`中科大全图.png`**：下次构建会被覆盖。
手工润色地面贴图的需求，请改成在 `make.py` 里加绘制逻辑。

## 4. 常用改动配方

### 加一栋建筑的专属样式

1. 在 `source/make.py` 的 `OVR` 字典里按 OSM way id 加一条：
   ```python
   '259873139': dict(k='lib', wall='#bd8a5e', roof='#a79e8a', mode='grid'),
   ```
2. `k` 选已有风格（`lib/teach/lab/dorm/canteen/hall/old/admin/glass/brick`），其余键覆盖配色与开窗。
3. `python scripts/build.py`，在 `中科大全图.png` 里确认效果。

### 加一个地标

改 `marks` 列表：`(名称, 世界坐标 x, 世界坐标 y, 一句话说明)`。
坐标是本地米制：`x=(lon-117.255)*94650`，`y=(lat-31.84)*110900`。
落点会自动吸附到最近的可行走位置。

### 调整视角

`source/make.py` 顶部：`S`（像素/米）、`VS`（南北压缩）、`HZ`（立面竖向倍数）、`TH`（网格转正角）。
改完务必检查：田径场分道线、地下通道、建筑遮挡顺序是否仍然正常。

### 加 NPC / 对话

现在只有 `person()` 一个行走小人。建议做法：在 `scene.json` 的 objects 里加 NPC 精灵，
在 `game.html` 里加 `nearNpc()` + 对话框，用 `E` 触发。参考 `docs/architecture.md` 的“渲染顺序”一节。

## 5. 美术规范（摘要）

- 像素网格：1 px = 1/3.1 m（东西）；**不要出现半像素**。
- 所有 1px 斜线必须用脚本里的 `poly1/seg1`（PIL 的 `line()` 会在浅角斜线上漏点）。
- 调色板：粉彩、低饱和；建筑按功能分型，单栋允许 ±6% 明度与 4–16% 环境色混入。
- 详细规则见 [docs/art-style.md](docs/art-style.md)。

## 6. 评审清单（Reviewer 用）

- [ ] PR 只改了源头文件，没有提交 `art/`、构建出的 HTML/PNG
- [ ] 本地 `python scripts/build.py` 能跑通，`make check` 无错误
- [ ] 视角、遮挡、通行掩码没有被破坏（尤其田径场与地下通道）
- [ ] OSM 署名与授权说明仍在
- [ ] 提交信息符合规范，改动范围与 PR 描述一致

## 7. 大文件与素材

- 目前仓库里最大的文件是 `data/campus3.osm`（约 2.5 MB），可以正常放行。
- 如果要提交照片、PSD、音频等大文件，请先 `git lfs install` 并取消 `.gitattributes` 里的 LFS 注释。
- 二进制的生成物请走 Release 附件或 CI Artifact，不要进主分支历史。

## 8. 报告问题

用 Issue 模板（Bug / Feature），附上：系统与浏览器版本、复现步骤、截图（`中科大全图.png` 局部或游戏内截图）、
若涉及坐标请给出 `x, y`（可用小地图估算）。
