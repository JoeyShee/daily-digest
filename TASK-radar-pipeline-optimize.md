# TASK: 雷达全链路脚本减负优化

## 背景
`~/.hermes/scripts/browse_radar_pipeline.sh` 每天8点跑，5个python步骤+git push，经常超过120s默认超时被kill。

脚本逻辑没问题（7月3日完整跑完了），但有两处明显的重复/冗余：
1. browse频道被渲染了2遍（28页HTML，白做一半）
2. App Store抓4个地区(us/cn/jp/sg)，实际只有us+cn有价值

## 改动清单

### 改动1：去掉render.py里browse频道重复渲染

**文件:** `~/Documents/daily-digest/render.py`

**问题:** `main()` 的 `--today` 模式（L1015）单独调了 `render_browse_index()`，但 `render_index()`（L741）内部也调了 `render_browse_index()`。所以browse频道每次渲染2遍。

**改法:** 删掉 `main()` 里 `--today` / `--date` / `--all` 三个分支中各自单独调用的 `render_browse_index()`，因为 `render_index()` 里已经有了。

具体来说，删除这三行（或注释掉）：
- L1015: `render_browse_index()  # 渲染 browse 频道`（在 `--today` 分支）
- L1026: `render_browse_index()  # 渲染 browse 频道`（在 `--date` 分支）
- L1037: `render_browse_index()  # 渲染 browse 频道`（在 `--all` 分支）

保留 `render_index()` 内部的 L740-741 `render_browse_details()` + `render_browse_index()`。

### 改动2：App Store地区从4个砍到2个

**文件:** `~/.hermes/scripts/appstore_radar.py`

**改法:** 把 `COUNTRIES` 从 `["us", "cn", "jp", "sg"]` 改成 `["us", "cn"]`。

注意 L270 也有硬编码的 `["us", "cn", "jp", "sg"]`，同步改成 `["us", "cn"]`。

`COUNTRY_LABELS` 字典保留 jp/sg 的映射不用删（无害），只改实际遍历用的列表。

### 改动3：pipeline脚本加耗时日志

**文件:** `~/.hermes/scripts/browse_radar_pipeline.sh`

在每个步骤前后加时间戳，方便以后定位哪步慢：

```bash
#!/bin/bash
set -e

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 雷达全链路 START ==="

echo "--- [1/6] RSS $(date '+%H:%M:%S') ---"
python3 ~/Documents/daily-digest/rss_fetcher.py 2>&1 || true

echo "--- [2/6] App Store $(date '+%H:%M:%S') ---"
python3 ~/.hermes/scripts/appstore_radar.py 2>&1 || true

echo "--- [3/6] Reddit $(date '+%H:%M:%S') ---"
python3 ~/.hermes/scripts/reddit_radar.py 2>&1 || true

echo "--- [4/6] 合并 $(date '+%H:%M:%S') ---"
python3 ~/Documents/daily-digest/browse_collector.py 2>&1 || true

echo "--- [5/6] 渲染 $(date '+%H:%M:%S') ---"
cd ~/Documents/daily-digest && python3 render.py --today 2>&1 || true

echo "--- [6/6] 部署 $(date '+%H:%M:%S') ---"
cd ~/Documents/daily-digest
git add -A
git diff --cached --quiet || git commit -m "browse: radar update $(date +%Y-%m-%d)" && git push origin main

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 雷达全链路 DONE ==="
```

## 验收标准
1. `cd ~/Documents/daily-digest && python3 render.py --today` 跑一遍，确认browse频道只渲染1遍（14页不是28页）
2. `python3 ~/.hermes/scripts/appstore_radar.py` 跑一遍，确认只抓us+cn两个地区
3. grep确认render.py三个main()分支里的独立 `render_browse_index()` 调用已删除
4. grep确认appstore_radar.py里没有遗留的 jp/sg 硬编码
