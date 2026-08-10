#!/bin/bash
# Render public Daily Digest content, retain its version history, then deploy jsbuildslowly.com.
set -euo pipefail

REPO_DIR="/Users/joeyshee/Documents/daily-digest"
GH_BIN="/Users/joeyshee/.local/bin/gh"
SITE_REPO="JoeyShee/jsbuildslowly-site"
MESSAGE_PREFIX="digest"
RUN_RENDER=true
FORCE_DEPLOY=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-render) RUN_RENDER=false ;;
    --force-deploy) FORCE_DEPLOY=true ;;
    --message-prefix=*) MESSAGE_PREFIX="${1#*=}" ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ! -x "$GH_BIN" ]; then
  echo "Personal-site publish failed: GitHub CLI is unavailable." >&2
  exit 1
fi

cd "$REPO_DIR"

if [ "$RUN_RENDER" = true ]; then
  python3 render.py --today
fi

git add -A
HAS_CHANGES=false
if ! git diff --cached --quiet; then
  TODAY="$(date +%Y-%m-%d)"
  git commit -m "${MESSAGE_PREFIX}: ${TODAY}"
  git push origin main
  HAS_CHANGES=true
fi

if [ "$HAS_CHANGES" = false ] && [ "$FORCE_DEPLOY" = false ]; then
  echo "[SILENT]"
  exit 0
fi

RUN_URL="$($GH_BIN workflow run deploy.yml --repo "$SITE_REPO" --ref main)"
RUN_ID="${RUN_URL##*/}"

if ! [[ "$RUN_ID" =~ ^[0-9]+$ ]]; then
  echo "Personal-site deploy was requested but no run ID was returned: $RUN_URL" >&2
  exit 1
fi

$GH_BIN run watch "$RUN_ID" --repo "$SITE_REPO" --exit-status

echo "✅ Daily Digest 已发布到个人站：https://jsbuildslowly.com/digest/"
echo "部署记录：$RUN_URL"
