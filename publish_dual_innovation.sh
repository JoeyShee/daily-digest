#!/bin/bash
# 将 10x 投机系统当天的一页交付发布到个人站“双创研究”栏目。
set -euo pipefail

SITE_REPO="/Users/joeyshee/Documents/daily-digest"
DELIVERY_DIR="/Users/joeyshee/Documents/10x投机/deliveries"
TODAY="$(date +%Y-%m-%d)"

if ! find "$DELIVERY_DIR" -maxdepth 1 -type f -name "$TODAY-*.md" -print -quit | grep -q .; then
    echo "发布停止：未找到 $TODAY 的 10x 每日交付。"
    exit 1
fi

exec "$SITE_REPO/publish_to_personal_site.sh" --message-prefix=dual-innovation
