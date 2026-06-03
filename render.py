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
ZERO2IDEA_DIR = BASE_DIR / "zero2idea"

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
    # 去掉开头的经典案例编号行（如 "🏆 经典案例 #9｜商业洞察"）
    block = re.sub(r'^🏆\s*经典案例\s*#\d+[｜|].*?\n', '', block).strip()
    # 去掉残留的分隔符
    block = re.sub(r'^━+\s*', '', block).strip()
    # 找第一个加粗标题
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "经典案例"
    # body 去掉标题行
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
    # 取第一行非空内容做标题，跳过通用标题行
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    title = lines[0] if lines else ct
    title = re.sub(r'^[🧠📌🏆📋💊📦🎯💡🛠⚡🔍⚠️📎｜|━]+\s*', '', title)
    # 如果标题是通用词（熵减卡片），用下一行
    if title.strip() in ('熵减卡片', '场景案例') and len(lines) > 1:
        title = re.sub(r'^[🧠📌🏆📋💊📦🎯💡🛠⚡🔍⚠️📎｜|]+\s*', '', lines[1])
    return card(bar, ct, title, md_to_html(block))

def render_entropy_health(block):
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "健康提醒"
    return card("health", "💊 健康提醒", title, md_to_html(block))

def render_entropy_opportunity(block):
    """Zero2Idea 机会雷达卡片"""
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "机会雷达"
    return card("zero2idea", "🔭 Zero2Idea 机会雷达", title, md_to_html(block))

def render_entropy_graveyard_review(block):
    """昨日想法回顾卡片"""
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "昨日想法回顾"
    return card("graveyard", "🪦 昨日想法回顾", title, md_to_html(block))

def parse_entropy_output(raw):
    content = raw
    if "---" in content:
        content = content.split("---", 1)[1]
    content = content.strip()
    if not content or "[SILENT]" in content:
        return [], []
    
    # 去掉首行标题 "📋 **熵减计划**（日期）"
    content = re.sub(r'^📋\s*\*?熵减计划.*?\n*', '', content).strip()
    
    # 用 ━━━ + emoji 分割成区块
    raw_blocks = re.split(r'━━━\s*[🏆🧠💊📡🔭🪦🎯]', content)
    # raw_blocks: [头部, "标题残留1", "内容1", "标题残留2", "内容2", ...]
    # 合并标题残留到下一个 block
    sections = []
    pending_header = ""
    for b in raw_blocks[1:]:  # 跳过 blocks[0]（头部）
        b = b.strip()
        b = re.sub(r'━+\s*$', '', b).strip()
        if not b:
            continue
        # 如果 block 很短（<20字符）且只包含标题关键词，它是残留标题
        is_header_remnant = (
            len(b) < 20 
            and any(kw in b for kw in ['经典案例', '熵减卡片', '思维模型', '场景案例', '健康提醒', '机会雷达', '昨日想法回顾'])
        )
        if is_header_remnant:
            pending_header = b
            continue
        if pending_header:
            b = pending_header + "\n" + b
            pending_header = ""
        sections.append(b)
    
    entropy_cards = []
    zero2idea_cards = []
    for sec in sections:
        if '经典案例' in sec[:40]:
            sec = re.sub(r'^.*?经典案例\s*[#│|].*?\n', '', sec, count=1).strip()
            entropy_cards.append(render_entropy_case(sec))
        elif '思维模型' in sec[:40]:
            entropy_cards.append(render_entropy_card(sec))
        elif '熵减卡片' in sec[:40]:
            entropy_cards.append(render_entropy_card(sec))
        elif '健康提醒' in sec[:40]:
            sec = re.sub(r'^.*?健康提醒\s*[#│|].*?\n', '', sec, count=1).strip()
            entropy_cards.append(render_entropy_health(sec))
        elif '机会雷达' in sec[:40]:
            sec = re.sub(r'^.*?机会雷达\s*[#│|].*?\n', '', sec, count=1).strip()
            zero2idea_cards.append(render_entropy_opportunity(sec))
        elif '昨日想法回顾' in sec[:40] or '想法回顾' in sec[:40]:
            sec = re.sub(r'^.*?昨日想法回顾\s*[#│|].*?\n', '', sec, count=1).strip()
            entropy_cards.append(render_entropy_graveyard_review(sec))
        else:
            entropy_cards.append(card("entropy", "熵减推送", "熵减推送", md_to_html(sec)))

    if not entropy_cards and not zero2idea_cards and content:
        entropy_cards.append(card("entropy", "熵减计划", "熵减推送", md_to_html(content)))
    return entropy_cards, zero2idea_cards

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
        return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{DATE}} · {{SECTION_TITLE}}</title><link rel="stylesheet" href="{{CSS_PATH}}"></head><body><nav class="top-nav"><a href="{{INDEX_PATH}}" class="brand">📋 每日精选</a>{{TAB_NAV}}</nav><div class="container"><div class="day-nav"><a href="{{PREV_DAY}}">← 前一天</a><div class="day-title">{{DATE}}</div><a href="{{NEXT_DAY}}">后一天 →</a></div>{{CARDS}}<footer class="site-footer"><p>Daily Digest</p></footer></div><script>
var cards=document.querySelectorAll(".card");cards.forEach(function(c,i){if(i>0)c.classList.add("collapsed")});
document.addEventListener("click",function(e){var h=e.target.closest(".card-header");if(h)h.closest(".card").classList.toggle("collapsed")});
</script></body></html>'''
    return ""

def _find_prev_next(date_str, available_dates):
    """在 available_dates 中找到当前日期的前一个和后一个有数据的日期。
    返回 (prev, next)，如果不存在则为 None。
    """
    sorted_dates = sorted(available_dates)
    prev_d = None
    next_d = None
    for d in sorted_dates:
        if d < date_str:
            prev_d = d
        elif d > date_str and next_d is None:
            next_d = d
    return prev_d, next_d

def _tab_nav_html(section, base_path=".."):
    """生成 3 频道 tab 导航 HTML"""
    tabs = [
        ("entropy", f"{base_path}/entropy/", "🧠 熵减计划"),
        ("graveyard", f"{base_path}/index.html", "🪦 想法墓地"),
        ("zero2idea", f"{base_path}/zero2idea/", "🔭 Zero2Idea"),
    ]
    items = []
    for key, href, label in tabs:
        active = " active" if key == section else ""
        items.append(f'<a href="{href}" class="tab-item{active}">{label}</a>')
    return '<div class="tab-nav">\n' + '\n'.join(items) + '\n</div>'

def render_day_page(date_str, cards_html, section, section_title, available_dates=None):
    """渲染单日页面"""
    if available_dates is None:
        available_dates = set()

    if section == "entropy":
        out_dir = ENTROPY_DIR
    elif section == "zero2idea":
        out_dir = ZERO2IDEA_DIR
    else:
        out_dir = GRAVEYARD_DIR

    css_path = "../style.css"
    index_path = "../index.html"

    tab_nav = _tab_nav_html(section, "..")

    prev_d, next_d = _find_prev_next(date_str, available_dates)
    prev_link = f"{prev_d}.html" if prev_d else index_path
    next_link = f"{next_d}.html" if next_d else index_path

    template = load_template("day.html")
    html = template
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{SECTION_TITLE}}", section_title)
    html = html.replace("{{CSS_PATH}}", css_path)
    html = html.replace("{{INDEX_PATH}}", index_path)
    html = html.replace("{{TAB_NAV}}", tab_nav)
    html = html.replace("{{PREV_DAY}}", prev_link)
    html = html.replace("{{NEXT_DAY}}", next_link)
    html = html.replace("{{CARDS}}", cards_html)
    html = html.replace(".html.html", ".html")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{date_str}.html").write_text(html)

def render_index(dates_entropy, dates_graveyard, dates_zero2idea):
    """渲染首页 + 频道首页"""
    # 首页 = 想法墓地最新日内容
    if dates_graveyard:
        latest_g = max(dates_graveyard)
        g_cards = collect_graveyard_cards(latest_g)
        if g_cards.strip():
            tab_nav = _tab_nav_html("graveyard", ".")
            prev_d, next_d = _find_prev_next(latest_g, dates_graveyard)
            prev_link = f"graveyard/{prev_d}.html" if prev_d else "index.html"
            next_link = f"graveyard/{next_d}.html" if next_d else "index.html"

            template = load_template("day.html")
            html = template
            html = html.replace("{{DATE}}", latest_g)
            html = html.replace("{{SECTION_TITLE}}", "想法墓地")
            html = html.replace("{{CSS_PATH}}", "style.css")
            html = html.replace("{{INDEX_PATH}}", "index.html")
            html = html.replace("{{TAB_NAV}}", tab_nav)
            html = html.replace("{{PREV_DAY}}", prev_link)
            html = html.replace("{{NEXT_DAY}}", next_link)
            html = html.replace("{{CARDS}}", g_cards)
            html = html.replace(".html.html", ".html")
            (BASE_DIR / "index.html").write_text(html)

    # 熵减频道 index
    ENTROPY_DIR.mkdir(parents=True, exist_ok=True)
    if dates_entropy:
        latest = max(dates_entropy)
        latest_file = ENTROPY_DIR / f"{latest}.html"
        if latest_file.exists():
            (ENTROPY_DIR / "index.html").write_text(latest_file.read_text())

    # 墓地频道 index
    GRAVEYARD_DIR.mkdir(parents=True, exist_ok=True)
    if dates_graveyard:
        latest = max(dates_graveyard)
        latest_file = GRAVEYARD_DIR / f"{latest}.html"
        if latest_file.exists():
            (GRAVEYARD_DIR / "index.html").write_text(latest_file.read_text())

    # Zero2Idea 频道 index
    ZERO2IDEA_DIR.mkdir(parents=True, exist_ok=True)
    if dates_zero2idea:
        latest = max(dates_zero2idea)
        latest_file = ZERO2IDEA_DIR / f"{latest}.html"
        if latest_file.exists():
            (ZERO2IDEA_DIR / "index.html").write_text(latest_file.read_text())

# ============================================================
# 收集卡片
# ============================================================

def collect_entropy_cards(date_str):
    """收集熵减计划卡片"""
    entropy_outputs = get_entropy_outputs()
    if date_str not in entropy_outputs:
        return ""
    entropy_cards, _ = parse_entropy_output(entropy_outputs[date_str])
    return "\n".join(entropy_cards)

def collect_zero2idea_cards(date_str):
    """收集 Zero2Idea 机会雷达卡片"""
    entropy_outputs = get_entropy_outputs()
    if date_str not in entropy_outputs:
        return ""
    _, zero2idea_cards = parse_entropy_output(entropy_outputs[date_str])
    return "\n".join(zero2idea_cards)

def get_zero2idea_dates():
    """收集所有有 zero2idea 数据的日期"""
    dates = set()
    for date_str, raw in get_entropy_outputs().items():
        if '机会雷达' in raw:
            dates.add(date_str)
    return dates

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

def render_date(date_str, e_dates=None, g_dates=None, z_dates=None):
    """渲染某一天的熵减+墓地+Zero2Idea页面"""
    if e_dates is None: e_dates = set()
    if g_dates is None: g_dates = set()
    if z_dates is None: z_dates = set()

    e = collect_entropy_cards(date_str)
    if e.strip():
        render_day_page(date_str, e, "entropy", "熵减计划", e_dates)

    g = collect_graveyard_cards(date_str)
    if g.strip():
        render_day_page(date_str, g, "graveyard", "想法墓地", g_dates)

    z = collect_zero2idea_cards(date_str)
    if z.strip():
        render_day_page(date_str, z, "zero2idea", "Zero2Idea", z_dates)

def main():
    args = sys.argv[1:]
    if not args:
        print("用法: render.py --today | --date YYYY-MM-DD | --all")
        sys.exit(1)

    if "--today" in args:
        d = datetime.now().strftime("%Y-%m-%d")
        e_dates, g_dates = get_available_dates()
        z_dates = get_zero2idea_dates()
        render_date(d, e_dates, g_dates, z_dates)
        render_index(e_dates, g_dates, z_dates)
        print(f"✅ 渲染完成: {d}")

    elif "--date" in args:
        idx = args.index("--date")
        d = args[idx + 1]
        e_dates, g_dates = get_available_dates()
        z_dates = get_zero2idea_dates()
        render_date(d, e_dates, g_dates, z_dates)
        render_index(e_dates, g_dates, z_dates)
        print(f"✅ 渲染完成: {d}")

    elif "--all" in args:
        e_dates, g_dates = get_available_dates()
        z_dates = get_zero2idea_dates()
        all_dates = e_dates | g_dates | z_dates
        for d in sorted(all_dates):
            render_date(d, e_dates, g_dates, z_dates)
        render_index(e_dates, g_dates, z_dates)
        print(f"✅ 渲染完成: 熵减 {len(e_dates)} 天, 墓地 {len(g_dates)} 天, Zero2Idea {len(z_dates)} 天")

if __name__ == "__main__":
    main()
