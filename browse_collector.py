#!/usr/bin/env python3
"""
Browse 频道数据收集器
从多个数据源收集内容并统一输出到 items.json
"""

import json
import re
from pathlib import Path
from datetime import datetime

def load_json(path):
    """安全加载 JSON"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def collect_rss_items():
    """收集 RSS 条目"""
    items = []
    feeds_dir = Path("~/.hermes/data/browse/feeds").expanduser()

    if not feeds_dir.exists():
        return items

    for feed_file in feeds_dir.glob("*.json"):
        feed_entries = load_json(feed_file)
        for entry in feed_entries:
            items.append({
                "original_title": entry.get("title", ""),
                "hook_title": "",
                "source": entry.get("source", ""),
                "date": entry.get("date", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")
            })

    return items

def collect_graveyard_items():
    """收集想法墓地条目"""
    items = []
    stones_file = Path("~/.hermes/idea-graveyard/stones.json").expanduser()
    stones = load_json(stones_file)

    for stone in stones:
        category = stone.get("category", "")

        # 只取包含 "Idea" 或 "选题" 的条目
        if "Idea" not in category and "选题" not in category:
            continue

        content = stone.get("content", "")
        if not content or content.startswith("【早期笔记"):
            continue

        # title = content 前 50 字符
        title = content[:50]

        # 日期：优先用 updated_at，其次 time
        date_field = stone.get("updated_at") or stone.get("time", "")
        date_str = date_field[:10] if date_field else ""

        items.append({
            "original_title": title,
            "hook_title": "",
            "source": "想法墓地",
            "date": date_str,
            "link": "",
            "summary": content
        })

    return items

def collect_community_items():
    """收集社区精华条目"""
    items = []
    community_dir = Path("~/.hermes/cron/output/3c77a5155a6d").expanduser()

    if not community_dir.exists():
        return items

    for brief_file in community_dir.glob("brief-*.md"):
        # 从文件名提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', brief_file.name)
        if not date_match:
            continue
        date_str = date_match.group(1)

        content = brief_file.read_text(encoding='utf-8', errors='replace')

        # 提取 "### 精华解读" 下的条目
        精华_section = re.search(r'### 精华解读\s*\n(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
        if not 精华_section:
            continue

        精华_content = 精华_section.group(1)

        # 提取每条精华（格式：- **标题**（作者）：描述）
        pattern = r'- \*\*([^*]+)\*\*[^:]*:([^-]+)(?=\n-|$)'
        matches = re.findall(pattern, 精华_content, re.DOTALL)

        for title, desc in matches:
            title = title.strip()
            desc = desc.strip()

            # 清理描述
            desc = re.sub(r'\s+', ' ', desc)
            desc = desc[:500]  # 截断到500字符

            items.append({
                "original_title": title,
                "hook_title": "",
                "source": "社区精华",
                "date": date_str,
                "link": "",
                "summary": desc
            })

    return items

def collect_entropy_case_items():
    """收集熵减经典案例条目"""
    items = []
    entropy_dir = Path("~/.hermes/cron/output/a9cf36ac90bb").expanduser()

    if not entropy_dir.exists():
        return items

    for entropy_file in entropy_dir.glob("*.md"):
        # 从文件名提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', entropy_file.name)
        if not date_match:
            continue
        date_str = date_match.group(1)

        content = entropy_file.read_text(encoding='utf-8', errors='replace')

        # 提取 "经典案例" 相关的区块
        # 寻找 🏆 经典案例 标题
        case_blocks = re.split(r'━* 🏆 经典案例', content)

        for i, block in enumerate(case_blocks[1:], 1):  # 跳过第一个（标题前的内容）
            if not block.strip():
                continue

            # 提取第一个加粗标题
            title_match = re.search(r'\*\*([^*]+)\*\*', block)
            if not title_match:
                continue

            title = title_match.group(1).strip()

            # 获取案例内容（去掉标题行和分隔符）
            case_content = block[title_match.end():].strip()
            # 清理内容
            case_content = re.sub(r'^━*\s*', '', case_content)
            case_content = re.sub(r'\n━*\s*', '\n', case_content)

            # 截断到500字符
            case_content = case_content[:500]

            items.append({
                "original_title": title,
                "hook_title": "",
                "source": "经典案例",
                "date": date_str,
                "link": "",
                "summary": case_content
            })

    return items

def map_source_tags(source):
    """映射 source 标签到带 emoji 的版本"""
    tag_map = {
        "想法墓地": "💡 想法",
        "社区精华": "🌐 社区",
        "经典案例": "🏆 案例"
    }
    return tag_map.get(source, source)

def main():
    """主函数"""
    all_items = []

    print("收集数据:")

    # 1. RSS
    rss_items = collect_rss_items()
    print(f"  RSS: {len(rss_items)} 条")
    all_items.extend(rss_items)

    # 2. 想法墓地
    graveyard_items = collect_graveyard_items()
    print(f"  想法墓地: {len(graveyard_items)} 条")
    all_items.extend(graveyard_items)

    # 3. 社区精华
    community_items = collect_community_items()
    print(f"  社区精华: {len(community_items)} 条")
    all_items.extend(community_items)

    # 4. 熵减案例
    entropy_items = collect_entropy_case_items()
    print(f"  经典案例: {len(entropy_items)} 条")
    all_items.extend(entropy_items)

    # 按 date 倒序排列
    all_items.sort(key=lambda x: x.get("date", ""), reverse=True)

    # 按 original_title 去重，保留最新的（date 最大的）
    seen_titles = {}
    deduped_items = []
    for item in all_items:
        title = item.get("original_title", "")
        if title in seen_titles:
            # 保留 date 更新的
            existing_date = seen_titles[title].get("date", "")
            if item.get("date", "") > existing_date:
                seen_titles[title] = item
        else:
            seen_titles[title] = item
    all_items = list(seen_titles.values())

    # 映射 source 标签
    for item in all_items:
        item["source"] = map_source_tags(item["source"])

    # 输出到 items.json
    output_dir = Path("~/.hermes/data/browse").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "items.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据收集完成，共 {len(all_items)} 条")
    print(f"   输出到: {output_file}")

if __name__ == "__main__":
    main()