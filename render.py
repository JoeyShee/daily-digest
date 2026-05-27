#!/usr/bin/env python3
"""
Daily Digest 渲染脚本
将想法墓地日报 + 熵减卡片渲染为 HTML，部署到 GitHub Pages

用法：
  python3 render.py --today          只渲染今天
  python3 render.py --date 2026-05-27  渲染指定日期
  python3 render.py --all            渲染所有有数据的日子
"""
import json
import os
import re
import sys
import glob
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("~/Documents/daily-digest").expanduser()
HERMES_DIR = Path("~/.hermes").expanduser()
DATA_DIR = HERMES_DIR / "data" / "openclaw-cognitive-core"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR
DAY_DIR = OUTPUT_DIR / "day"

# ============================================================
# 数据加载
# ============================================================

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def get_classic_cases():
    return load_json(DATA_DIR / "classic-cases.json") or []

def get_scenarios():
    return load_json(DATA_DIR / "scenario-extract-v4" / "usable-scenarios.json") or []

def get_models():
    return load_json(DATA_DIR / "scenario-extract-v4" / "usable-models.json") or []

def get_concepts():
    concepts = []
    cdir = DATA_DIR / "wiki-exploration" / "concepts"
    if cdir.exists():
        for f in sorted(cdir.glob("*.md")):
            concepts.append({"name": f.stem, "content": f.read_text(errors="replace")})
    return concepts

def get_health_tips():
    return load_json(DATA_DIR / "health-tips.json") or []

def get_stones():
    return load_json(HERMES_DIR / "idea-graveyard" / "stones.json") or []

def get_push_log():
    return load_json(DATA_DIR / "push-log.json") or {"pushed": {}, "last_push": ""}

def get_case_push_log():
    return load_json(DATA_DIR / "case-push-log.json") or {"pushed": [], "last_push": ""}

def get_health_push_log():
    return load_json(DATA_DIR / "health-push-log.json") or {"pushed_indices": [], "last_push": ""}

def get_graveyard_outputs():
    """获取想法墓地 cron output"""
    outdir = HERMES_DIR / "cron" / "output" / "159fea63d27e"
    results = {}
    if outdir.exists():
        for f in sorted(outdir.glob("*.md")):
            # 从文件名提取日期
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
            if date_match:
                date_str = date_match.group(1)
                results[date_str] = f.read_text(errors="replace")
    return results

def get_entropy_outputs():
    """获取熵减计划 cron output"""
    outdir = HERMES_DIR / "cron" / "output" / "a9cf36ac90bb"
    results = {}
    if outdir.exists():
        for f in sorted(outdir.glob("*.md")):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
            if date_match:
                date_str = date_match.group(1)
                results[date_str] = f.read_text(errors="replace")
    return results

# ============================================================
# HTML 转义
# ============================================================

def esc(text):
    if not text:
        return ""
    return (str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

# ============================================================
# 卡片渲染器（每种类型一个函数）
# ============================================================

def render_classic_liangchen(case):
    """良辰美经典案例 — 产品拆解风格"""
    biz = case.get("biz_position", {})
    ideas = case.get("ideas", [])
    
    body = ""
    if case.get("product_what"):
        body += f'<h3>📦 产品是什么</h3><p>{esc(case["product_what"])}</p>'
    if case.get("need_what"):
        body += f'<h3>🎯 解决什么需求</h3><p>{esc(case["need_what"])}</p>'
    if case.get("why_pay"):
        body += f'<h3>💰 为什么付钱</h3><p>{esc(case["why_pay"])}</p>'
    if case.get("who_pays"):
        body += f'<h3>👤 谁在付钱</h3><p>{esc(case["who_pays"])}</p>'
    if case.get("growth_path"):
        body += f'<h3>📈 增长路径</h3><p>{esc(case["growth_path"])}</p>'
    if case.get("turning_point"):
        body += f'<h3>⚡ 关键转折点</h3><p>{esc(case["turning_point"])}</p>'
    if case.get("key_numbers"):
        body += f'<div class="highlight-box"><p><strong>关键数据：</strong>{esc(case["key_numbers"])}</p></div>'
    if ideas:
        body += '<h3>💡 辉哥可以做的方向</h3><ol>'
        for idea in ideas:
            body += f'<li>{esc(idea)}</li>'
        body += '</ol>'
    if biz and biz.get("revenue_source"):
        body += f'<h3>🔍 卡位分析</h3>'
        body += f'<p><strong>赚钱：</strong>{esc(biz.get("revenue_source",""))}</p>'
        body += f'<p><strong>卡位：</strong>{esc(biz.get("chokepoint",""))}</p>'
        body += f'<p><strong>启发：</strong>{esc(biz.get("insight",""))}</p>'
        if biz.get("min_action"):
            body += f'<div class="highlight-box"><p>👉 {esc(biz["min_action"])}</p></div>'
    if case.get("takeaway"):
        body += f'<div class="highlight-box"><p><strong>一句话带走：</strong>{esc(case["takeaway"])}</p></div>'
    if case.get("red_flag"):
        body += f'<div class="red-flag"><p>⚠️ {esc(case["red_flag"])}</p></div>'
    
    return f'''<div class="card">
  <div class="card-bar classic-liangchen"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">经典案例 · 良辰美</div><h2>{esc(case.get('title',''))}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

def render_classic_shengcai(case):
    """生财宝典经典案例 — 人物故事风格"""
    body = ""
    if case.get("background"):
        body += f'<p>{esc(case["background"])}</p>'
    if case.get("income"):
        body += f'<div class="highlight-box"><p><strong>💰 赚到什么：</strong>{esc(case["income"])}</p></div>'
    if case.get("path"):
        body += f'<h3>🛤️ 从0到1路径</h3><p>{esc(case["path"])}</p>'
    if case.get("ai_role"):
        body += f'<h3>🤖 AI解决的核心问题</h3><p>{esc(case["ai_role"])}</p>'
    if case.get("revenue_model"):
        body += f'<h3>💵 赚钱模式</h3><p>{esc(case["revenue_model"])}</p>'
    if case.get("replicable_path"):
        body += f'<h3>🎯 辉哥可以复制的路径</h3><p>{esc(case["replicable_path"])}</p>'
    if case.get("takeaway"):
        body += f'<div class="highlight-box"><p>🧠 {esc(case["takeaway"])}</p></div>'
    quotes = case.get("powerful_quotes", [])
    if quotes:
        body += '<h3>💬 原话</h3>'
        for q in quotes:
            body += f'<blockquote>{esc(q)}</blockquote>'
    if case.get("risk"):
        body += f'<div class="red-flag"><p>⚠️ {esc(case["risk"])}</p></div>'
    
    person = case.get("person_name", case.get("title", ""))
    return f'''<div class="card">
  <div class="card-bar classic-shengcai"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">经典案例 · 生财宝典</div><h2>{esc(person)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

def render_manual(case):
    """操作手册 — 步骤指南风格"""
    body = ""
    if case.get("person_name"):
        body += f'<p>{esc(case["person_name"])}的实战经验</p>'
    tools = case.get("tools", [])
    if tools:
        body += '<h3>🛠 工具</h3><ul>'
        for t in tools:
            body += f'<li>{esc(t)}</li>'
        body += '</ul>'
    if case.get("scenario"):
        body += f'<h3>🎯 适用场景</h3><p>{esc(case["scenario"])}</p>'
    steps = case.get("steps", [])
    if steps:
        body += '<h3>📋 步骤</h3><ol class="step-list">'
        for s in steps:
            body += f'<li>{esc(s)}</li>'
        body += '</ol>'
    if case.get("pro_tips"):
        body += f'<div class="highlight-box"><p><strong>💡 贴士：</strong>{esc(case["pro_tips"])}</p></div>'
    if case.get("expected_result"):
        body += f'<h3>📊 预期效果</h3><p>{esc(case["expected_result"])}</p>'
    meta = []
    if case.get("time_investment"):
        meta.append(f'⏱ 上手时间：{esc(case["time_investment"])}')
    if case.get("difficulty"):
        meta.append(f'难度：{esc(case["difficulty"])}')
    if meta:
        body += f'<p>{" | ".join(meta)}</p>'
    
    return f'''<div class="card">
  <div class="card-bar handbook"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">操作手册</div><h2>{esc(case.get('title',''))}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

def render_scenario(item):
    """场景案例 — 情境决策风格"""
    body = ""
    if item.get("domain"):
        body += f'<p><span class="badge scenario">{esc(item["domain"])}</span></p>'
    if item.get("situation"):
        body += f'<h3>📌 情境</h3><p>{esc(item["situation"])}</p>'
    if item.get("decision_point"):
        body += f'<h3>🔀 决策点</h3><p>{esc(item["decision_point"])}</p>'
    if item.get("action_taken"):
        body += f'<h3>✅ 行动</h3><p>{esc(item["action_taken"])}</p>'
    if item.get("outcome"):
        body += f'<h3>📊 结果</h3><p>{esc(item["outcome"])}</p>'
    
    return f'''<div class="card">
  <div class="card-bar scenario"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">场景案例</div><h2>{esc(item.get('title',''))}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

def render_model(item):
    """思维模型 — 知识卡片风格"""
    body = ""
    if item.get("one_liner"):
        body += f'<div class="model-one-liner">{esc(item["one_liner"])}</div>'
    if item.get("when_to_use"):
        body += f'<h3>⏰ 何时使用</h3><p>{esc(item["when_to_use"])}</p>'
    if item.get("explanation"):
        body += f'<h3>💡 核心逻辑</h3><p>{esc(item["explanation"])}</p>'
    if item.get("how_to_use"):
        body += f'<h3>🛠 使用方法</h3><p>{esc(item["how_to_use"])}</p>'
    if item.get("pitfalls"):
        body += f'<div class="red-flag"><p>⚠️ {esc(item["pitfalls"])}</p></div>'
    
    return f'''<div class="card">
  <div class="card-bar mental-model"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">思维模型</div><h2>{esc(item.get('name',''))}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

def render_concept(item):
    """概念词条 — 词典风格"""
    content = item.get("content", "")
    # 去掉 [[...]] 双括号
    content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
    
    return f'''<div class="card">
  <div class="card-bar concept"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">概念词条</div><h2>{esc(item.get('name',''))}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body"><p>{esc(content)}</p></div>
</div>'''

def render_health(tip):
    """健康提醒 — 简洁提醒风格"""
    content = ""
    if isinstance(tip, dict):
        content = tip.get("content", tip.get("title", str(tip)))
    else:
        content = str(tip)
    
    return f'''<div class="card">
  <div class="card-bar health"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">健康提醒</div><h2>{esc(content[:80])}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body"><p>{esc(content)}</p></div>
</div>'''

def render_graveyard_report(md_text):
    """想法墓地日报 — 从 cron output md 解析"""
    # 提取 Response 部分
    if "## Response" in md_text:
        md_text = md_text.split("## Response")[1]
    
    # 如果包含 [SILENT]，跳过
    if "[SILENT]" in md_text:
        return ""
    
    # 简单 markdown → HTML 转换
    html = esc(md_text)
    # 还原一些 markdown 格式
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    html = re.sub(r'^→ (.+)$', r'<p>→ \1</p>', html, flags=re.MULTILINE)
    html = re.sub(r'^👉 (.+)$', r'<div class="highlight-box"><p>👉 \1</p></div>', html, flags=re.MULTILINE)
    html = re.sub(r'^⚠️ (.+)$', r'<div class="red-flag"><p>⚠️ \1</p></div>', html, flags=re.MULTILINE)
    # 换行
    html = re.sub(r'\n\n+', '</p><p>', html)
    
    return f'''<div class="card">
  <div class="card-bar graveyard"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">🪦 想法墓地日报</div><h2>想法墓地日报</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body"><p>{html}</p></div>
</div>'''

def render_stone(stone):
    """想法墓地单条 stone"""
    cat = stone.get("category", "📦存档")
    # 确定色条类型
    bar_class = "graveyard"
    cat_map = {
        "💡困惑": "classic-liangchen",
        "🚀Idea": "classic-shengcai",
        "📝选题": "handbook",
        "🔧任务": "scenario",
        "🪞反思": "mental-model",
        "📦存档": "graveyard",
    }
    bar_class = cat_map.get(cat, "graveyard")
    
    body = ""
    if stone.get("answer"):
        body += f'<div class="highlight-box"><p><strong>解答：</strong>{esc(stone["answer"])}</p>'
        if stone.get("actionable_tip"):
            body += f'<p>👉 {esc(stone["actionable_tip"])}</p>'
        body += '</div>'
    if stone.get("research_thesis"):
        body += f'<h3>🔍 命题</h3><p>{esc(stone["research_thesis"])}</p>'
    if stone.get("new_perspective"):
        body += f'<h3>🔍 新视角</h3><p>{esc(stone["new_perspective"])}</p>'
    if stone.get("progress_point"):
        body += f'<div class="highlight-box"><p>✅ {esc(stone["progress_point"])}</p></div>'
    if stone.get("task_note"):
        body += f'<h3>📋 任务说明</h3><p>{esc(stone["task_note"])}</p>'
    if stone.get("content_matrix_flag"):
        body += f'<p><span class="badge handbook">已进选题池</span></p>'
    
    status = stone.get("status", "")
    if status and status != "processed":
        body += f'<p><span class="badge {bar_class}">{esc(status)}</span></p>'
    
    return f'''<div class="card">
  <div class="card-bar {bar_class}"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">{esc(cat)}</div><h2>{esc(stone.get("content","")[:100])}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

# ============================================================
# 页面渲染
# ============================================================

def load_template(name):
    path = TEMPLATES_DIR / name
    if path.exists():
        return path.read_text()
    # fallback 内嵌模板
    if name == "index.html":
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>每日精选</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav class="top-nav"><span class="brand">📋 每日精选</span></nav>
<div class="container">
<div class="page-header"><h1>每日精选</h1><p>想法墓地 · 熵减卡片</p></div>
<ul class="date-list">{{DATE_LIST}}</ul>
</div>
</body>
</html>'''
    elif name == "day.html":
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{DATE}} — 每日精选</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<nav class="top-nav"><a href="../index.html" class="brand">📋 每日精选</a></nav>
<div class="container">
<div class="day-nav">
<a href="{{PREV_DAY}}">← 前一天</a>
<div class="day-title">{{DATE}}</div>
<a href="{{NEXT_DAY}}">后一天 →</a>
</div>
{{CARDS}}
</div>
<script>
function toggleCard(header){
  header.parentElement.classList.toggle('collapsed');
}
</script>
</body>
</html>'''
    return ""

def render_day_page(date_str, cards_html):
    """渲染单日页面"""
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    template = load_template("day.html")
    html = (template
        .replace("{{DATE}}", date_str)
        .replace("{{PREV_DAY}}", f"{prev_date}.html")
        .replace("{{NEXT_DAY}}", f"{next_date}.html")
        .replace("{{CARDS}}", cards_html))
    
    # 修复可能的双重 .html.html
    html = html.replace(".html.html", ".html")
    
    DAY_DIR.mkdir(parents=True, exist_ok=True)
    (DAY_DIR / f"{date_str}.html").write_text(html)
    return html

def render_index(dates):
    """渲染首页"""
    items = ""
    for d in sorted(dates, reverse=True):
        items += f'<li><a href="day/{d}.html"><span>{d}</span><span class="arrow">→</span></a></li>\n'
    
    template = load_template("index.html")
    html = template.replace("{{DATE_LIST}}", items)
    (OUTPUT_DIR / "index.html").write_text(html)
    return html

# ============================================================
# 收集某日的卡片数据
# ============================================================

def collect_day_cards(date_str):
    """收集某一天的所有卡片数据，返回 HTML"""
    cards = []
    
    # 1. 熵减计划 cron output → 拆成独立卡片
    entropy_outputs = get_entropy_outputs()
    if date_str in entropy_outputs:
        entropy_cards = parse_entropy_output(entropy_outputs[date_str])
        cards.extend(entropy_cards)
    
    # 2. 想法墓地日报
    graveyard_outputs = get_graveyard_outputs()
    if date_str in graveyard_outputs:
        card = render_graveyard_report(graveyard_outputs[date_str])
        if card:
            cards.append(card)
    
    # 3. 想法墓地当天更新的 stones
    stones = get_stones()
    day_stones = [s for s in stones
                  if s.get("updated_at", "").startswith(date_str)
                  or s.get("time", "").startswith(date_str)]
    day_stones_with_content = [s for s in day_stones if s.get("content")]
    for s in day_stones_with_content[:10]:
        cards.append(render_stone(s))
    
    return "\n".join(cards)


def parse_entropy_output(raw):
    """解析熵减计划 cron output，拆成独立卡片"""
    # 去掉 cron 头部
    content = raw
    if "---" in content:
        content = content.split("---", 1)[1]
    content = content.strip()
    if not content or "[SILENT]" in content:
        return []
    
    cards = []
    # 按 ━━━ 分隔符拆成区块
    sections = re.split(r'━━━.*?━━━', content)
    # 第一段通常是标题行，跳过
    # 也试试按标题匹配
    blocks = re.split(r'(?=━━━)', content)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        if '经典案例' in block[:50]:
            cards.append(render_entropy_case(block))
        elif '熵减卡片' in block[:50] or '思维模型' in block[:30] or '场景案例' in block[:30]:
            cards.append(render_entropy_card(block))
        elif '健康提醒' in block[:50] or block.strip().startswith('💊'):
            cards.append(render_entropy_health(block))
    
    # 如果没拆出来（旧格式），整体渲染
    if not cards and content:
        cards.append(render_entropy_fallback(content))
    
    return cards


def md_to_html(text):
    """简易 markdown → HTML"""
    html = esc(text)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'^#{1,3}\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    # 段落
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h3>') or p.startswith('<hr'):
            result.append(p)
        else:
            # 保留换行
            p = p.replace('\n', '<br>')
            result.append(f'<p>{p}</p>')
    return '\n'.join(result)


def render_entropy_case(block):
    """渲染熵减计划中的经典案例"""
    # 提取标题
    title_match = re.search(r'\*\*(.+?)\*\*', block)
    title = title_match.group(1) if title_match else "经典案例"
    
    body = md_to_html(block)
    
    return f'''<div class="card">
  <div class="card-bar classic-liangchen"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">🏆 经典案例</div><h2>{esc(title)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''


def render_entropy_card(block):
    """渲染熵减卡片（思维模型/场景案例）"""
    # 提取类型
    if '思维模型' in block[:50]:
        card_type = "🧠 思维模型"
        bar = "mental-model"
    elif '场景案例' in block[:50]:
        card_type = "📌 场景案例"
        bar = "scenario"
    else:
        card_type = "🧠 熵减卡片"
        bar = "mental-model"
    
    # 提取标题（第一个非空行去掉 ━━━）
    lines = [l for l in block.split('\n') if l.strip() and '━' not in l]
    title = lines[0].strip() if lines else card_type
    # 去掉 emoji 前缀
    title = re.sub(r'^[🧠📌🏆📋💊📦🎯💡🛠⚡🔍⚠️📎]+\s*', '', title)
    
    body = md_to_html(block)
    
    return f'''<div class="card">
  <div class="card-bar {bar}"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">{esc(card_type)}</div><h2>{esc(title)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''


def render_entropy_health(block):
    """渲染健康提醒"""
    title_match = re.search(r'\*\*(.+?)\*\*', block)
    title = title_match.group(1) if title_match else "健康提醒"
    
    body = md_to_html(block)
    
    return f'''<div class="card">
  <div class="card-bar health"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">💊 健康提醒</div><h2>{esc(title)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''


def render_entropy_fallback(content):
    """兜底渲染：整块输出"""
    body = md_to_html(content)
    return f'''<div class="card">
  <div class="card-bar classic-liangchen"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">熵减计划</div><h2>熵减推送</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body}</div>
</div>'''

# ============================================================
# 主逻辑
# ============================================================

def get_available_dates():
    """获取所有有数据的日期"""
    dates = set()
    
    # 想法墓地 output
    graveyard_outputs = get_graveyard_outputs()
    dates.update(graveyard_outputs.keys())
    
    # 熵减计划 output
    entropy_outputs = get_entropy_outputs()
    dates.update(entropy_outputs.keys())
    
    # stones 有更新日期的
    stones = get_stones()
    for s in stones:
        for key in ("updated_at", "time"):
            val = s.get(key, "")
            if val:
                dates.add(val[:10])
    
    return sorted(dates)

def main():
    args = sys.argv[1:]
    
    if not args:
        print("用法: render.py --today | --date YYYY-MM-DD | --all")
        sys.exit(1)
    
    if "--today" in args:
        date_str = datetime.now().strftime("%Y-%m-%d")
        cards = collect_day_cards(date_str)
        if cards.strip():
            render_day_page(date_str, cards)
            print(f"✅ 渲染完成: day/{date_str}.html")
        else:
            print(f"📭 {date_str} 无数据")
    
    elif "--date" in args:
        idx = args.index("--date")
        date_str = args[idx + 1]
        cards = collect_day_cards(date_str)
        if cards.strip():
            render_day_page(date_str, cards)
            print(f"✅ 渲染完成: day/{date_str}.html")
        else:
            print(f"📭 {date_str} 无数据")
    
    elif "--all" in args:
        dates = get_available_dates()
        for d in dates:
            cards = collect_day_cards(d)
            if cards.strip():
                render_day_page(d, cards)
        render_index(dates)
        print(f"✅ 渲染完成: {len(dates)} 天, index.html")

if __name__ == "__main__":
    main()
