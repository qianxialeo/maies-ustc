#!/usr/bin/env python3
"""一次性配置 GitHub 仓库的团队协作设置（需要具有 repo 权限的 PAT）。

用法：
    # 1) 先在本地导出 token（不要写进仓库、不要发给别人）
    #    Windows PowerShell:  $env:GITHUB_TOKEN = "ghp_xxx"
    #    Git Bash:            export GITHUB_TOKEN=ghp_xxx
    python scripts/setup_github.py --dry-run          # 只预览要改什么
    python scripts/setup_github.py                    # 真正执行
    python scripts/setup_github.py --protect          # 另外配置 main 分支保护
    python scripts/setup_github.py --invite alice,bob # 邀请协作者（写权限）

做的事（全部幂等，可重复运行）：
  1. 仓库基础设置：描述、首页、Squash-only 合并、合并后删分支、关闭 Wiki、开启 Issues/Projects/Discussions
  2. Topics 标签
  3. Issue 标签（bug / enhancement / art / map / npc / docs / good first issue …）
  4. 里程碑（v3.1 NPC 入场 / v4 镜渊景观）
  5. 可选：main 分支保护（需 CI 已跑过一次，直接读取真实 check 名称）
  6. 可选：开启 GitHub Pages（Source = GitHub Actions）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"

DESCRIPTION = "中国科学技术大学三校区 2.5D 像素开放世界地图 · 现实/镜渊双版本"
HOMEPAGE = "https://qianxialeo.github.io/maies-ustc/"
TOPICS = ["pixel-art", "map", "ustc", "openstreetmap", "canvas", "visual-novel", "game"]

LABELS = [
    ("bug", "d73a4a", "地图、渲染或交互出错了"),
    ("enhancement", "a2eeef", "新功能或改进"),
    ("art", "f9d0c4", "像素美术调整"),
    ("map", "0e8a16", "地图几何、建筑、道路、水系"),
    ("npc", "5319e7", "角色、对话、剧情"),
    ("docs", "0075ca", "文档"),
    ("ci", "bfd4f2", "CI / 构建 / 发布"),
    ("good first issue", "7057ff", "适合新人的小任务"),
    ("help wanted", "008672", "需要协助"),
    ("blocked", "b60205", "被其它改动阻塞"),
]

MILESTONES = [
    ("v3.1 NPC 入场", "小茉、小橘作为可对话 NPC 进入地图，带基础对话框"),
    ("v4 镜渊景观", "空中岛屿、月面广场等镜渊专属可探索场景"),
]


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


def detect_repo() -> tuple[str, str]:
    url = sh("git", "remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]+(?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit(f"无法从 origin 解析 owner/repo：{url!r}")
    return m.group("owner"), m.group("repo")


class Client:
    def __init__(self, token: str, dry: bool) -> None:
        self.token = token
        self.dry = dry
        self.calls = 0

    def __call__(self, method: str, path: str, body: dict | None = None, ok=(200, 201, 204)):
        if self.dry:
            print(f"  [dry] {method} {path}" + (f"  {json.dumps(body, ensure_ascii=False)}" if body else ""))
            return {}
        req = urllib.request.Request(
            API + path,
            method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "maies-setup",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                self.calls += 1
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code in ok:
                return {}
            raise SystemExit(f"API 失败 {method} {path} -> {e.code}\n{detail}") from e


def step(title: str) -> None:
    print(f"\n== {title}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印将要执行的请求")
    ap.add_argument("--protect", action="store_true", help="配置 main 分支保护（要求 CI 通过 + 1 人 review）")
    ap.add_argument("--pages", action="store_true", help="开启 GitHub Pages（Source = GitHub Actions）")
    ap.add_argument("--invite", default="", help="逗号分隔的 GitHub 用户名，邀请为 write 权限协作者")
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token and not args.dry_run:
        raise SystemExit("缺少 token：请先设置环境变量 GITHUB_TOKEN（dry-run 不需要）")

    owner, repo = detect_repo()
    print(f"仓库：{owner}/{repo}" + ("（dry-run）" if args.dry_run else ""))
    gh = Client(token or "", args.dry_run)

    step("1. 仓库基础设置")
    gh("PATCH", f"/repos/{owner}/{repo}", {
        "description": DESCRIPTION,
        "homepage": HOMEPAGE,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False,
        "has_discussions": True,
        "allow_squash_merge": True,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
        "delete_branch_on_merge": True,
        "squash_merge_commit_title": "PR_TITLE",
        "squash_merge_commit_message": "PR_BODY",
    })

    step("2. Topics")
    gh("PUT", f"/repos/{owner}/{repo}/topics", {"names": TOPICS})

    step("3. Issue 标签")
    existing = {l["name"] for l in ([] if args.dry_run else gh("GET", f"/repos/{owner}/{repo}/labels?per_page=100"))}
    for name, color, desc in LABELS:
        if name in existing:
            print(f"  已存在：{name}")
            continue
        print(f"  新建：{name}")
        gh("POST", f"/repos/{owner}/{repo}/labels", {"name": name, "color": color, "description": desc})

    step("4. 里程碑")
    ms = {m["title"] for m in ([] if args.dry_run else gh("GET", f"/repos/{owner}/{repo}/milestones?state=all"))}
    for title, desc in MILESTONES:
        if title in ms:
            print(f"  已存在：{title}")
            continue
        print(f"  新建：{title}")
        gh("POST", f"/repos/{owner}/{repo}/milestones", {"title": title, "description": desc})

    if args.protect:
        step("5. main 分支保护")
        sha = sh("git", "rev-parse", "HEAD")
        contexts: list[str] = []
        if not args.dry_run:
            runs = gh("GET", f"/repos/{owner}/{repo}/commits/{sha}/check-runs") or {}
            contexts = [c["name"] for c in runs.get("check_runs", [])]
        if not contexts:
            print("  还没读到 CI 的检查名（先让 ci.yml 在 main 上跑过一次）。")
            print("  技巧：下面的请求用空 contexts 提交会失败，所以本次跳过分支保护。")
        else:
            print(f"  使用检查名：{contexts}")
            gh("PUT", f"/repos/{owner}/{repo}/branches/main/protection", {
                "required_status_checks": {"strict": False, "contexts": contexts},
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True,
                },
                "restrictions": None,
                "allow_force_pushes": False,
                "allow_deletions": False,
                "required_conversation_resolution": True,
            })

    if args.pages:
        step("6. GitHub Pages")
        gh("POST", f"/repos/{owner}/{repo}/pages", {"build_type": "workflow"}, ok=(201, 204, 409))
        print("  已提交（409 表示本来就开着）。请在 Actions 里等 pages 工作流跑完。")

    if args.invite:
        step("7. 邀请协作者")
        for user in [u.strip() for u in args.invite.split(",") if u.strip()]:
            print(f"  邀请：{user}")
            gh("PUT", f"/repos/{owner}/{repo}/collaborators/{user}", {"permission": "write"}, ok=(201, 204))

    print(f"\n完成，实际请求 {gh.calls} 次。")
    if not args.dry_run:
        print(f"打开看看：https://github.com/{owner}/{repo}/settings")


if __name__ == "__main__":
    main()
