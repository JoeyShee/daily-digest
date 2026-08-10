#!/bin/bash
# 将 10x 投机系统当天的一页交付发布到个人站“双创研究”栏目。
set -euo pipefail

SITE_REPO="/Users/joeyshee/Documents/daily-digest"
DELIVERY_DIR="/Users/joeyshee/Documents/10x投机/deliveries"
TODAY="$(date +%Y-%m-%d)"

cd "$SITE_REPO"

if [ -n "$(git status --porcelain)" ]; then
    echo "发布停止：个人站存在未提交改动，请先处理，避免自动发布夹带其他内容。"
    exit 1
fi

if ! find "$DELIVERY_DIR" -maxdepth 1 -type f -name "$TODAY-*.md" -print -quit | grep -q .; then
    echo "发布停止：未找到 $TODAY 的 10x 每日交付。"
    exit 1
fi

python3 render.py --today

if [ -z "$(git status --porcelain)" ]; then
    echo "双创研究今日页面没有变化，无需重复发布。"
    exit 0
fi

git add -A
git commit -m "dual-innovation: $TODAY"
git push origin main

echo "双创研究已发布：https://joeyhee.github.io/daily-digest/dual-innovation/"
