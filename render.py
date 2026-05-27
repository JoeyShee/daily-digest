#!/usr/bin/env python3
"""
Daily Digest 渲染脚本 v2
熵减计划和想法墓地拆为独立频道，各有独立页面目录

用法：
  python3 render.py --today
  python3 render.py --date 2026-05-27
  python3 render.py --all
"""
import json, re, sys, os
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("~/Documents/daily-digest").expanduser()
HERMES_DIR = Path("~/.hermes").expanduser()
DATA_DIR = HERMES_DIR / "data" / "openclaw-cognitive-core"
TEMPLATES_DIR = BASE_DIR / "templates"

ENTROPY_DIR = BASE_DIR / "entropy"
GRAVEYARD_DIR = BASE_DIR / "graveyard"

# ============================================================
# 数据加载
# ============================================================

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except: return None

STONES_CACHE = None
def get_stones():
    global STONES_CACHE
    if STONES_CACHE is None:
        STONES_CACHE = load_json(HERMES_DIR / "idea-graveyard" / "stones.json") or []
    return STONES_CACHE

ENTROPY_CACHE = None
def get_entropy_outputs():
    global ENTROPY_CACHE
    if ENTROPY_CACHE is None:
        outdir = HERMES_DIR / "cron" / "output" / "a9cf36ac90bb"
        ENTROPY_CACHE = {}
        if outdir.exists():
            for f in sorted(outdir.glob("*.md")):
                m = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
                if m: ENTROPY_CACHE[m.group(1)] = f.read_text(errors="replace")
    return ENTROPY_CACHE

GRAVEYARD_CACHE = None
def get_graveyard_outputs():
    global GRAVEYARD_CACHE
    if GRAVEYARD_CACHE is None:
        outdir = HERMES_DIR / "cron" / "output" / "159fea63d27e"
        GRAVEYARD_CACHE = {}
        if outdir.exists():
            for f in sorted(outdir.glob("*.md")):
                m = re.search(r'(\d{4}-\d{2}-\d{2})', f.name)
                if m: GRAVEYARD_CACHE[m.group(1)] = f.read_text(errors="replace")
    return GRAVEYARD_CACHE

# ============================================================
# HTML 工具
# ============================================================

def esc(text):
    if not text: return ""
    return str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def md_to_html(text):
    """简易 markdown → HTML"""
    html = esc(text)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'^#{1,3}\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        if p.startswith('<h3>') or p.startswith('<hr'):
            result.append(p)
        else:
            p = p.replace('\n', '<br>')
            result.append(f'<p>{p}</p>')
    return '\n'.join(result)

# ============================================================
# 卡片渲染
# ============================================================

def card(bar_class, card_type, title, body_html, collapsed=False):
    cls = ' class="card collapsed"' if collapsed else ' class="card"'
    return f'''<div{cls}>
  <div class="card-bar {bar_class}"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">{esc(card_type)}</div><h2>{esc(title)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body_html}</div>
</div>'''

# --- 熵减卡片 ---

def render_entropy_case(block):
    # block 已经去掉了 ━━━ 标题行，找第一个加粗标题
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "经典案例"
    # body 去掉第一行如果就是标题
    body = block
    if title_m and block.startswith(title_m.group(0)):
        body = block[title_m.end():].strip()
    return card("case", "🏆 经典案例", title, md_to_html(body))

def render_entropy_card(block):
    if '思维模型' in block[:80]:
        ct, bar = "🧠 思维模型", "model"
    elif '场景案例' in block[:80]:
        ct, bar = "📌 场景案例", "idea"
    else:
        ct, bar = "🧠 熵减卡片", "model"
    # 取第一行非空内容做标题
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    title = lines[0] if lines else ct
    title = re.sub(r'^[🧠📌🏆📋💊📦🎯💡🛠⚡🔍⚠️📎｜|]+\s*', '', title)
    return card(bar, ct, title, md_to_html(block))

def render_entropy_health(block):
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "健康提醒"
    return card("health", "💊 健康提醒", title, md_to_html(block))

def parse_entropy_output(raw):
    content = raw
    if "---" in content:
        content = content.split("---", 1)[1]
    content = content.strip()
    if not content or "[SILENT]" in content:
        return []
    
    # 去掉首行标题 "📋 **熵减计划**（日期）"
    content = re.sub(r'^📋\s*\*?熵减计划.*?\n*', '', content).strip()
    
    # 用 ━━━ 分割成区块
    blocks = re.split(r'━━━\s*[🏆🧠💊]', content)
    # blocks[0] 是空或头部，blocks[1:] 是实际内容
    sections = []
    for b in blocks[1:]:
        b = b.strip()
        # 去掉尾部 ━━━
        b = re.sub(r'━+\s*$', '', b).strip()
        if b:
            sections.append(b)
    
    cards = []
    for sec in sections:
        # 判断类型
        if sec.startswith('🏆') or '经典案例' in sec[:20]:
            sec = re.sub(r'^🏆\s*经典案例.*?\n', '', sec).strip()
            cards.append(render_entropy_case(sec))
        elif sec.startswith('🧠') or '熵减卡片' in sec[:30] or '思维模型' in sec[:30]:
            sec = re.sub(r'^🧠\s*(熵减卡片|思维模型).*?\n', '', sec).strip()
            cards.append(render_entropy_card(sec))
        elif sec.startswith('💊') or '健康提醒' in sec[:20]:
            sec = re.sub(r'^💊\s*健康提醒.*?\n', '', sec).strip()
            cards.append(render_entropy_health(sec))
        else:
            # 未知类型，尝试通用渲染
            cards.append(card("entropy", "熵减推送", "熵减推送", md_to_html(sec)))
    
    if not cards and content:
        cards.append(card("entropy", "熵减计划", "熵减推送", md_to_html(content)))
    return cards

# --- 想法墓地 ---

CAT_MAP = {
    "💡困惑": ("entropy", "💡 困惑解答"),
    "🚀Idea": ("idea", "🚀 Idea"),
    "📝选题": ("reflection", "📝 选题"),
    "🔧任务": ("task", "🔧 任务"),
    "🪞反思": ("model", "🪞 反思"),
    "📦存档": ("archive", "📦 存档"),
}

def render_graveyard_report(md_text):
    if "## Response" in md_text:
        md_text = md_text.split("## Response")[1]
    if "[SILENT]" in md_text: return ""
    return card("graveyard", "🪦 想法墓地日报", "想法墓地日报", md_to_html(md_text))

def render_stone(stone):
    cat = stone.get("category", "📦存档")
    bar, label = CAT_MAP.get(cat, ("graveyard", cat))
    
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
    
    return card(bar, label, stone.get("content","")[:120], body)

# ============================================================
# 页面渲染
# ============================================================

def load_template(name):
    path = TEMPLATES_DIR / name
    if path.exists(): return path.read_text()
    if name == "day.html":
        return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{DATE}} · {{SECTION_TITLE}}</title><link rel="stylesheet" href="{{CSS_PATH}}"></head><body><nav class="top-nav"><a href="{{INDEX_PATH}}" class="brand">📋 每日精选</a></nav><div class="container"><div class="day-nav"><a href="{{PREV_DAY}}">← 前一天</a><div class="day-title">{{DATE}}</div><a href="{{NEXT_DAY}}">后一天 →</a></div>{{CARDS}}<footer class="site-footer"><p>Daily Digest</p></footer></div><script>
var cards=document.querySelectorAll(".card");cards.forEach(function(c,i){if(i>0)c.classList.add("collapsed")});
document.addEventListener("click",function(e){var h=e.target.closest(".card-header");if(h)h.closest(".card").classList.toggle("collapsed")});
</script></body></html>'''
    return ""

def render_day_page(date_str, cards_html, section, section_title):
    """渲染单日页面"""
    if section == "entropy":
        out_dir = ENTROPY_DIR
        css_path = "../style.css"
        index_path = "../index.html"
    else:
        out_dir = GRAVEYARD_DIR
        css_path = "../style.css"
        index_path = "../index.html"
    
    prev_d = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_d = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    template = load_template("day.html")
    html = template
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{SECTION_TITLE}}", section_title)
    html = html.replace("{{CSS_PATH}}", css_path)
    html = html.replace("{{INDEX_PATH}}", index_path)
    html = html.replace("{{PREV_DAY}}", f"{prev_d}.html")
    html = html.replace("{{NEXT_DAY}}", f"{next_d}.html")
    html = html.replace("{{CARDS}}", cards_html)
    html = html.replace(".html.html", ".html")
    
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{date_str}.html").write_text(html)

def render_index(dates_entropy, dates_graveyard):
    """渲染首页 + 两个频道首页"""
    template = load_template("index.html")
    (BASE_DIR / "index.html").write_text(template)
    
    # 熵减频道首页
    entropy_list = ""
    for d in sorted(dates_entropy, reverse=True):
        entropy_list += f'<li><a href="{d}.html"><span>{d}</span><span class="arrow">→</span></a></li>\n'
    
    entropy_index = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>熵减计划</title><link rel="stylesheet" href="../style.css"></head><body><nav class="top-nav"><a href="../index.html" class="brand">📋 每日精选</a></nav><div class="container"><div class="page-header"><h1>🧠 熵减计划</h1><p>经典案例 · 思维模型 · 健康提醒</p></div><ul class="date-list">{entropy_list}</ul></div></body></html>'''
    ENTROPY_DIR.mkdir(parents=True, exist_ok=True)
    (ENTROPY_DIR / "index.html").write_text(entropy_index)
    
    # 墓地频道首页
    graveyard_list = ""
    for d in sorted(dates_graveyard, reverse=True):
        graveyard_list += f'<li><a href="{d}.html"><span>{d}</span><span class="arrow">→</span></a></li>\n'
    
    graveyard_index = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>想法墓地</title><link rel="stylesheet" href="../style.css"></head><body><nav class="top-nav"><a href="../index.html" class="brand">📋 每日精选</a></nav><div class="container"><div class="page-header"><h1>🪦 想法墓地</h1><p>困惑 · Idea · 选题 · 反思</p></div><ul class="date-list">{graveyard_list}</ul></div></body></html>'''
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)
    (GRAVEYARD_DIR / "index.html").write_text(graveyard_index)

# ============================================================
# 收集卡片
# ============================================================

def collect_entropy_cards(date_str):
    """收集熵减计划卡片"""
    entropy_outputs = get_entropy_outputs()
    if date_str not in entropy_outputs:
        return ""
    cards = parse_entropy_output(entropy_outputs[date_str])
    return "\n".join(cards)

def collect_graveyard_cards(date_str):
    """收集想法墓地卡片"""
    cards_html = []
    
    # 日报
    graveyard_outputs = get_graveyard_outputs()
    if date_str in graveyard_outputs:
        c = render_graveyard_report(graveyard_outputs[date_str])
        if c: cards_html.append(c)
    
    # 当天更新的 stones
    stones = get_stones()
    day_stones = [s for s in stones
                  if s.get("content")
                  and (s.get("updated_at","").startswith(date_str)
                       or s.get("time","").startswith(date_str))]
    for s in day_stones[:15]:
        cards_html.append(render_stone(s))
    
    return "\n".join(cards_html)

def get_available_dates():
    """获取所有有数据的日期"""
    entropy_dates = set(get_entropy_outputs().keys())
    graveyard_dates = set(get_graveyard_outputs().keys())
    # stones 里的日期也加进去
    for s in get_stones():
        for k in ("updated_at", "time"):
            v = s.get(k, "")
            if v: graveyard_dates.add(v[:10])
    return entropy_dates, graveyard_dates

# ============================================================
# 主逻辑
# ============================================================

def render_date(date_str):
    """渲染某一天的熵减+墓地页面"""
    e = collect_entropy_cards(date_str)
    if e.strip():
        render_day_page(date_str, e, "entropy", "熵减计划")
    
    g = collect_graveyard_cards(date_str)
    if g.strip():
        render_day_page(date_str, g, "graveyard", "想法墓地")

def main():
    args = sys.argv[1:]
    if not args:
        print("用法: render.py --today | --date YYYY-MM-DD | --all")
        sys.exit(1)
    
    if "--today" in args:
        d = datetime.now().strftime("%Y-%m-%d")
        render_date(d)
        e_dates, g_dates = get_available_dates()
        render_index(e_dates, g_dates)
        print(f"✅ 渲染完成: {d}")
    
    elif "--date" in args:
        idx = args.index("--date")
        d = args[idx + 1]
        render_date(d)
        e_dates, g_dates = get_available_dates()
        render_index(e_dates, g_dates)
        print(f"✅ 渲染完成: {d}")
    
    elif "--all" in args:
        e_dates, g_dates = get_available_dates()
        all_dates = e_dates | g_dates
        for d in sorted(all_dates):
            render_date(d)
        render_index(e_dates, g_dates)
        print(f"✅ 渲染完成: 熵减 {len(e_dates)} 天, 墓地 {len(g_dates)} 天")

if __name__ == "__main__":
    main()
