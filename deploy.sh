#!/bin/bash
# Daily Digest 自动部署脚本
# 渲染 HTML → git commit → git push
set -e

REPO_DIR="$HOME/Documents/daily-digest"
cd "$REPO_DIR"

# 渲染
python3 render.py --today

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "✅ 无新内容需要部署"
    exit 0
fi

# 提交 & 推送
TODAY=$(date +%Y-%m-%d)
git add -A
git commit -m "digest: $TODAY" || true
git push origin main 2>&1

echo "✅ 部署完成: $TODAY"
