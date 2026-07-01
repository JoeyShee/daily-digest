#!/usr/bin/env python3
"""
RSS 抓取器
从 3 个 RSS 源抓取内容并保存为 JSON
"""

import feedparser
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import time

FEEDS = [
    {"url": "https://blog.fsck.com/feed/rss.xml", "name": "Jesse Vincent"},
    {"url": "https://www.startupsfortherestofus.com/feed", "name": "Rob Walling"},
    {"url": "https://patwalls.com/feed", "name": "Pat Walls"},
]

def strip_html(html):
    """去除 HTML 标签，返回纯文本"""
    if not html:
        return ""
    # 简单的 HTML 标签去除
    text = re.sub(r'<[^>]+>', '', html)
    # 解码 HTML 实体
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#?\w+;', '', text)
    return text.strip()

def truncate_text(text, max_length=500):
    """截断文本到指定长度"""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_length:
        return text
    # 在单词边界截断
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # 如果最后一个空格在合理位置
        truncated = truncated[:last_space]
    return truncated + "..."

def parse_date(date_str):
    """解析各种日期格式到 YYYY-MM-DD"""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    try:
        # feedparser 的 parsed_date
        if hasattr(date_str, 'strftime'):
            return date_str.strftime("%Y-%m-%d")

        # 尝试解析字符串
        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d']:
            try:
                dt = datetime.strptime(date_str[:25], fmt)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                continue
    except:
        pass

    return datetime.now().strftime("%Y-%m-%d")

def fetch_feed(feed_url, feed_name):
    """抓取单个 RSS feed"""
    print(f"正在抓取: {feed_name} ({feed_url})")

    try:
        feed = feedparser.parse(feed_url)
        entries = []

        for entry in feed.entries:
            # 解析日期
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except:
                    pub_date = None
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                try:
                    pub_date = datetime(*entry.updated_parsed[:6])
                except:
                    pub_date = None

            date_str = parse_date(pub_date)

            # 提取内容
            title = entry.get('title', '')
            summary = ''

            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            elif hasattr(entry, 'content'):
                content = entry.content[0] if isinstance(entry.content, list) else entry.content
                summary = content.get('value', '') if isinstance(content, dict) else str(content)

            # 清洗摘要
            summary = strip_html(summary)
            summary = truncate_text(summary, 1500)

            link = entry.get('link', '')

            entries.append({
                "title": title,
                "summary": summary,
                "link": link,
                "date": date_str,
                "source": feed_name
            })

        # 按发布日期倒序排序，只取最新 20 条
        entries.sort(key=lambda x: x.get("date", ""), reverse=True)
        entries = entries[:20]

        print(f"  → 抓取到 {len(entries)} 条")
        return entries

    except Exception as e:
        print(f"  ✗ 抓取失败: {e}")
        return []

def main():
    """主函数"""
    output_dir = Path("~/.hermes/data/browse/feeds").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    all_entries = {}

    for feed in FEEDS:
        entries = fetch_feed(feed["url"], feed["name"])

        # 保存到单独的 JSON 文件
        feed_file = output_dir / f"{feed['name'].replace(' ', '_')}.json"
        with open(feed_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)

        all_entries[feed["name"]] = len(entries)

        # 避免频繁请求
        time.sleep(2)

    print("\nRSS 抓取完成:")
    for name, count in all_entries.items():
        print(f"  {name}: {count} 条")

if __name__ == "__main__":
    main()