# 团队协作配置

这份文档把"仓库要配成什么样"写成可执行的步骤。能脚本化的部分在 `scripts/setup_github.py`，
只能网页点的部分列在第二节。

## 一、一次性配置（脚本，约 1 分钟）

### 1. 建一个 token

GitHub → Settings → Developer settings → **Personal access tokens → Tokens (classic)** → Generate new token：

- 勾 **`repo`**（读写仓库、设置、协作者）
- 有效期建议 30 天，用完即删
- 不需要勾 `admin:org`，除非你要配组织

### 2. 本地跑脚本

```bash
# Git Bash
export GITHUB_TOKEN=ghp_xxxxxxxx
python scripts/setup_github.py --dry-run          # 先看要改什么，不写任何东西
python scripts/setup_github.py                    # 执行：描述/Topics/标签/里程碑/合并策略
python scripts/setup_github.py --pages            # 同时开启 GitHub Pages（Source = Actions）
python scripts/setup_github.py --protect          # 同时给 main 加分支保护
```

脚本是**幂等**的：已存在的标签、里程碑会跳过，可以反复执行。
`--protect` 会读取 `main` 最近一次提交上真实的 check 名称，所以**要先让 `ci` 工作流跑过一次**再执行，
否则会提示"还没读到 CI 的检查名"并跳过（这是有意的，避免写死一个不存在的检查名把合并永久卡死）。

### 3. token 用完就删

```bash
unset GITHUB_TOKEN
```

token 不要写进 `.env`、不要提交、不要贴在聊天里。

## 二、只能网页点的几件事

| 事项 | 位置 | 说明 |
| --- | --- | --- |
| 邀请成员 | Settings → Collaborators（或 `--invite alice,bob`） | 个人仓库用 Collaborators；多人长期协作建议升级到 **Organization**，用 Team 管权限 |
| 组织 / Team | github.com/organizations/new | 组织可以把"地图组/代码组/剧情组"分开，配合 CODEOWNERS 自动指派 |
| 仓库可见性 | Settings → General → Danger Zone | 公开前再确认一次授权与校方名称的使用边界（见 `LICENSES.md`） |
| 自定义域名 | Settings → Pages → Custom domain | 想用 `map.example.com` 时配，注意 CNAME |
| Actions 权限 | Settings → Actions → General | 默认即可；Pages 工作流已显式声明 `pages: write` / `id-token: write` |
| 安全 | Settings → Code security | 打开 Dependabot alerts（`dependabot.yml` 已配版本更新） |

## 三、权限模型

| 角色 | 建议权限 | 适合谁 |
| --- | --- | --- |
| 维护者（maintainer） | Admin | 你：合并、发版、改设置 |
| 协作者（member） | Write | 日常提 PR 的核心成员 |
| 外部贡献者 | Read + Fork | 通过 PR 贡献，不需要进仓库 |

规则：**任何人都不直推 main**，包括维护者（分支保护里勾了 Do not allow bypassing）。
紧急修复也走 PR，只是可以自己批准自己的 PR——但要在 PR 里说明原因。

## 四、评审与合并规则（已由脚本落地）

- main 受保护：必须 PR、必须 1 人 approve、必须 CI 绿、必须解决全部评论。
- 只允许 **Squash merge**，合并后自动删分支。
- `CODEOWNERS` 指向 `@qianxialeo`，`source/make.py` 与 `source/game.html` 的改动会自动请求 review。
- PR 模板里带自检清单（构建通过、没提交生成物、视角/掩码没坏、OSM 署名还在）。

## 五、验收清单

配完之后，用一个 5 分钟的小 PR 把链路走一遍：

- [ ] 开一个 `docs/*` 分支，改一行文档并推送
- [ ] 开 PR：模板自动出现、CODEOWNERS 自动请求 review、`ci` 自动开始跑
- [ ] CI 绿之后，`main` 的分支保护是否允许合并（说明 check 名称对上了）
- [ ] Squash merge 后：分支自动删除、`pages` 工作流自动部署
- [ ] 打开 `https://<账号>.github.io/maies-ustc/` 能看到游戏
- [ ] 在 Actions 的产物里下载 zip，解压能直接玩

## 六、日常运维节奏

| 频率 | 事情 |
| --- | --- |
| 每周 | 过一遍新 Issue，贴标签、进里程碑；合并 dependabot 的依赖升级 |
| 每两周 | 一次 `v3.x` 发版：更新 `CHANGELOG.md` → 打 tag → 用 CI 产物建 Release |
| 每月 | 清理过期分支、检查 Pages 是否正常、核对 OSM 数据是否有更新 |
| 每季度 | 重新评估路线图优先级，把 `docs/roadmap.md` 的条目拆成 Issue |
