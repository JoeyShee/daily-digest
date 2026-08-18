#!/usr/bin/env python3
"""
Daily Digest 渲染脚本 v3
公开前台只保留两个入口：今日判断（perception/）和 10x研究（dual-innovation/）。
熵减计划、想法墓地、Zero2Idea、旧10x投机、信号库已停止生成与更新，
历史目录和 HTML 保留在原位，旧链接仍可访问，只是不再出现在导航里。

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
TENX_DIR = BASE_DIR / "10x"
DUAL_INNOVATION_DIR = BASE_DIR / "dual-innovation"
BROWSE_DIR = BASE_DIR / "browse"
PERCEPTION_DIR = BASE_DIR / "perception"
BROWSE_DATA_DIR = HERMES_DIR / "data" / "browse" / "items.json"
REPRICING_DATA_DIR = HERMES_DIR / "data" / "repricing" / "reports"
REPRICING_FALLBACK_DIR = Path("~/Documents/10x投机/docs/reports").expanduser()
DUAL_INNOVATION_SOURCE_DIR = Path("~/Documents/10x投机/deliveries").expanduser()

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

TENX_CACHE = None
def get_10x_outputs():
    global TENX_CACHE
    if TENX_CACHE is None:
        tenx_base = Path("~/Documents/10x投机/scripts/output").expanduser()
        TENX_CACHE = {}
        if tenx_base.exists():
            for d in sorted(tenx_base.glob("weekly_*")):
                report = d / "weekly_report.md"
                if report.exists():
                    m = re.match(r'weekly_(\d{4})(\d{2})(\d{2})', d.name)
                    if m:
                        date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                        TENX_CACHE[date_str] = report.read_text(errors="replace")
    return TENX_CACHE

DUAL_INNOVATION_CACHE = None
def get_dual_innovation_outputs():
    """读取10x系统已经成熟的一页交付，不读取内部研究底稿。"""
    global DUAL_INNOVATION_CACHE
    if DUAL_INNOVATION_CACHE is None:
        DUAL_INNOVATION_CACHE = {}
        if DUAL_INNOVATION_SOURCE_DIR.exists():
            for report in sorted(DUAL_INNOVATION_SOURCE_DIR.glob("*.md")):
                m = re.search(r'(\d{4}-\d{2}-\d{2})', report.name)
                if m:
                    DUAL_INNOVATION_CACHE[m.group(1)] = report.read_text(errors="replace")
    return DUAL_INNOVATION_CACHE

REPRICING_CACHE = None
def get_repricing_outputs():
    """读取 Repricing 报告。Hermes 输出优先，项目试跑报告作为回退。"""
    global REPRICING_CACHE
    if REPRICING_CACHE is None:
        REPRICING_CACHE = {}
        source_dirs = [
            (REPRICING_FALLBACK_DIR, "*repricing*.md"),
            (REPRICING_DATA_DIR, "*.md"),
        ]
        for source_dir, pattern in source_dirs:
            if not source_dir.exists():
                continue
            for report in sorted(source_dir.glob(pattern)):
                m = re.search(r'(\d{4}-\d{2}-\d{2})', report.name)
                if m:
                    # 后读取的 Hermes 正式报告覆盖项目试跑报告。
                    REPRICING_CACHE[m.group(1)] = report.read_text(errors="replace")
    return REPRICING_CACHE

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

def card(bar_class, card_type, title, body_html, collapsed=False, raw_type=False):
    cls = ' class="card collapsed"' if collapsed else ' class="card"'
    type_html = card_type if raw_type else esc(card_type)
    return f'''<div{cls}>
  <div class="card-bar {bar_class}"></div>
  <div class="card-header" onclick="toggleCard(this)">
    <div><div class="card-type">{type_html}</div><h2>{esc(title)}</h2></div>
    <div class="toggle-icon">▼</div>
  </div>
  <div class="card-body">{body_html}</div>
</div>'''

def _strip_markdown_title(text):
    return re.sub(r'^\s*#+\s+', '', text or '').strip()

def _repricing_headline(section_title, section_body):
    """优先提取报告中的明确 Repricing 结论作为卡片标题。"""
    for line in section_body.splitlines():
        cleaned = line.strip().lstrip('>').strip()
        cleaned = cleaned.replace('**', '')
        if '正在被重新定价' in cleaned or '被重新定价的' in cleaned:
            return cleaned[:160]
    return _strip_markdown_title(section_title)[:160]

def _without_repeated_headline(section_body, headline):
    """卡片标题已经承担结论时，不在正文开头重复同一句。"""
    kept = []
    removed = False
    for line in section_body.splitlines():
        cleaned = line.strip().lstrip('>').strip().replace('**', '')
        if not removed and cleaned == headline:
            removed = True
            continue
        kept.append(line)
    return '\n'.join(kept).strip()

def render_repricing_report(text):
    """把一份分析报告压缩成主判断、候选判断和证据层。"""
    sections = re.split(r'^##\s+', text, flags=re.MULTILINE)
    cards = []

    for raw_section in sections[1:]:
        lines = raw_section.strip().splitlines()
        if not lines:
            continue
        section_title = lines[0].strip()
        section_body = '\n'.join(lines[1:]).strip()
        if not section_body:
            continue

        title = _repricing_headline(section_title, section_body)
        section_body = _without_repeated_headline(section_body, title)
        title_lower = section_title.lower()

        if '主判断' in section_title or 'primary' in title_lower:
            cards.append(card(
                'perception', '🌍 今日主判断', title,
                md_to_html(section_body), collapsed=False
            ))
        elif '次判断' in section_title or '候选' in section_title or 'watch' in title_lower:
            cards.append(card(
                'watch', '🟡 候选重定价', title,
                md_to_html(section_body), collapsed=True
            ))
        elif '证据' in section_title or 'source' in title_lower:
            cards.append(card(
                'evidence', '📎 证据层', section_title,
                md_to_html(section_body), collapsed=True
            ))

    if cards:
        return cards

    # 兼容没有标准二级标题的报告：仍只显示为一个连贯判断，不拆成散卡片。
    first_heading = re.search(r'^#\s+(.+)$', text, flags=re.MULTILINE)
    title = first_heading.group(1).strip() if first_heading else '今日 Repricing 判断'
    return [card('perception', '🌍 今日主判断', title, md_to_html(text), collapsed=False)]

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

    # 如果 body 为空或只有空白，跳过该卡片
    if not body or not body.strip():
        return ""

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

def _parse_opp_meta(line):
    """解析 META: score=84 | tag=观察 → 冷冻 | source=榜单"""
    m = re.match(r'META:\s*score=(\d+)\s*\|\s*tag=(.+?)\s*\|\s*source=(.+)', line.strip())
    if m:
        return {'score': int(m.group(1)), 'tag': m.group(2).strip(), 'source': m.group(3).strip()}
    return None

def _decision_tag_class(tag):
    """决策标签 → CSS class"""
    tag_lower = tag.lower()
    if '冷冻' in tag_lower:
        return 'freeze'
    elif '立项' in tag_lower or '执行' in tag_lower:
        return 'launch'
    elif '验证' in tag_lower or '缩小' in tag_lower:
        return 'validate'
    elif '观察' in tag_lower:
        return 'freeze'
    return 'validate'

def render_single_opportunity_card(block_text):
    """渲染单条机会卡片 — 结构化展示：结论先行 → 判断依据 → 证据缺口"""
    lines = block_text.strip().split('\n')
    score = 0
    tag = ''
    source = ''
    title = ''
    body_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        meta = _parse_opp_meta(line)
        if meta:
            score = meta['score']
            tag = meta['tag']
            source = meta['source']
            continue
        if line.startswith('**') and not title:
            title_m = re.match(r'\*\*(.+?)\*\*', line)
            if title_m:
                title = title_m.group(1)
                rest = line[title_m.end():].strip()
                if rest:
                    body_lines.append(rest)
                continue
        body_lines.append(line)

    if not title:
        title = "机会"

    # === 构建 body HTML（结构化） ===
    body_text = '\n'.join(body_lines)

    # 清洗内部指标（双重保险：cron层已清洗，render层再清一次）
    body_text = re.sub(r'[(\uff08][^\)\uff09]*(?:personal_fit_score|pay_evidence|evidence_grade|market_size_score|competition_score|tech_fit_score|personal_fit|tech_complexity|time_to_mvp|mvp_feasibility)[^\)\uff09]*[\)\uff09]', '', body_text)
    body_text = re.sub(r'[(\uff08][\)\uff09]', '', body_text)
    body_text = re.sub(r'[,，]?\s*(?:DH|BP|AX|EL|T)-\d+\s*(?:触发|命中|生效)[^,，；;]*', '', body_text)
    body_text = re.sub(r'[；;]\s*[；;]', '；', body_text)
    body_text = re.sub(r'^\s*[；;]\s*', '', body_text)
    body_text = re.sub(r'\s*[；;]\s*$', '', body_text)
    body_text = body_text.strip()

    # 拆分：判断依据 vs 证据缺口
    reason_parts = []
    gap_parts = []

    # 把 body_lines 重新处理（已清洗）
    body_lines_clean = [l for l in body_text.split('\n') if l.strip()]
    for bl in body_lines_clean:
        bl = bl.strip()
        # 证据缺口行
        if bl.startswith('证据缺口:') or bl.startswith('缺口:'):
            gap_content = re.sub(r'^证据缺口[:：]\s*|^缺口[:：]\s*', '', bl)
            if gap_content:
                gap_parts = [g.strip() for g in re.split(r'[；;]', gap_content) if g.strip()]
            continue
        if bl.startswith('证据缺口'):
            gap_content = re.sub(r'^证据缺口[:：]?\s*', '', bl)
            if gap_content:
                gap_parts = [g.strip() for g in re.split(r'[；;]', gap_content) if g.strip()]
            continue
        reason_parts.append(bl)

    # --- 构建 HTML ---
    body_html = ''

    # 第一行：决策标签 + 来源 + 评分
    body_html += '<div class="opp-meta-row">'
    if tag:
        tag_cls = _decision_tag_class(tag)
        body_html += f'<span class="decision-tag {tag_cls}">{esc(tag)}</span>'
    body_html += f'<span class="opp-source-badge">来源: {esc(source)}</span>'
    body_html += f'<span class="opp-score-inline">{score}分</span>'
    body_html += '</div>'

    # 第二部分：判断依据（拆成要点列表）
    if reason_parts:
        body_html += '<div class="opp-reason">'
        # 把分号分隔的长句拆成要点
        all_reasons = []
        for rp in reason_parts:
            # 按分号拆分
            sub_parts = re.split(r'[；;]', rp)
            for sp in sub_parts:
                sp = sp.strip().rstrip('。，').strip()
                if sp and len(sp) > 2:
                    all_reasons.append(sp)
        if all_reasons:
            body_html += '<ul class="opp-reason-list">'
            for r in all_reasons[:5]:  # 最多5个要点
                body_html += f'<li>{md_to_html(r)}</li>'
            body_html += '</ul>'
        body_html += '</div>'

    # 第三部分：证据缺口（独立区块）
    if gap_parts:
        body_html += '<div class="opp-evidence-gap">'
        body_html += '<span class="opp-gap-label">证据缺口</span>'
        body_html += '<ul class="opp-gap-list">'
        for g in gap_parts[:3]:
            body_html += f'<li>{esc(g)}</li>'
        body_html += '</ul>'
        body_html += '</div>'

    # score 放到 card_type 标签里
    card_type_with_score = f"🔭 ZERO2IDEA · <span class=\"opp-score\">{score}</span>"

    return card("zero2idea", card_type_with_score, title, body_html, raw_type=True)

def render_entropy_graveyard_review(block):
    """昨日想法回顾卡片"""
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "昨日想法回顾"
    return card("graveyard", "🪦 昨日想法回顾", title, md_to_html(block))

def _parse_dedao_meta(line):
    """解析 DEDADOMETA: type=AI案例 | course=快刀广播站"""
    m = re.match(r'DEDADOMETA:\s*type=(.+?)\s*\|\s*course=(.+)', line.strip())
    if m:
        return {'type_label': m.group(1).strip(), 'course': m.group(2).strip()}
    return None

def _dedao_type_class(type_label):
    """得到课程类型 → CSS class"""
    tl = type_label.lower()
    if 'ai' in tl:
        return 'ai'
    elif '商业案例' in tl:
        return 'biz'
    elif '趋势' in tl:
        return 'trend'
    elif '模型' in tl:
        return 'model'
    return 'biz'

def render_single_dedao_card(block_text):
    """渲染单条得到课程卡片"""
    lines = block_text.strip().split('\n')
    type_label = ''
    course = ''
    title = ''
    body_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        meta = _parse_dedao_meta(line)
        if meta:
            type_label = meta['type_label']
            course = meta['course']
            continue
        if line.startswith('**') and not title:
            title_m = re.match(r'\*\*(.+?)\*\*', line)
            if title_m:
                title = title_m.group(1)
                rest = line[title_m.end():].strip()
                if rest:
                    body_lines.append(rest)
                continue
        body_lines.append(line)

    if not title:
        title = "课程信号"

    body_html = ''
    # 第一行：类型标签 + 课程来源
    body_html += '<div class="dedao-meta-row">'
    if type_label:
        tag_cls = _dedao_type_class(type_label)
        body_html += f'<span class="dedao-type-tag {tag_cls}">{esc(type_label)}</span>'
    body_html += f'<span class="dedao-course-badge">{esc(course)}</span>'
    body_html += '</div>'

    # 内容
    body_text = '\n'.join(body_lines)
    if body_text.strip():
        body_html += md_to_html(body_text)

    card_type = f"📚 得到课程雷达"
    return card("dedao", card_type, title, body_html)

def parse_entropy_output(raw):
    content = raw
    # 只在文件开头（前200字符内）有 --- 分隔线时才跳过元数据头
    head = content[:200]
    if "\n---\n" in head:
        content = content.split("\n---\n", 1)[1]
    elif content.startswith("---\n"):
        content = content.split("\n", 1)[1]
    content = content.strip()
    if not content or "[SILENT]" in content:
        return [], []
    
    # 去掉首行标题 "📋 **熵减计划**（日期）"
    content = re.sub(r'^📋\s*\*?熵减计划.*?\n*', '', content).strip()
    
    # 用 ━━━ + emoji 分割成区块
    raw_blocks = re.split(r'━━━\s*[🏆🧠💊📡🔭🪦🎯📚]', content)
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
            and any(kw in b for kw in ['经典案例', '熵减卡片', '思维模型', '场景案例', '健康提醒', '机会雷达', '昨日想法回顾', '得到课程'])
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
            # 可能包含多个案例
            # 优先按 🏆 经典案例 #\d+ 分割（旧格式）
            if re.search(r'🏆\s*经典案例\s*#\d+', sec):
                sub_cases = re.split(r'(?=🏆\s*经典案例\s*#\d+)', sec)
            else:
                # 新格式：按 🧑 案例人物｜ 分割
                sub_cases = re.split(r'(?=\n🧑\s*案例人物)', sec)
            for sub in sub_cases:
                sub = sub.strip()
                if not sub:
                    continue
                # 去掉通用标题行和分隔线
                sub = re.sub(r'^.*?经典案例\s*[#│|].*?\n', '', sub, count=1).strip()
                sub = re.sub(r'^━━━\s*🏆\s*经典案例\s*━+\s*\n', '', sub).strip()
                # 如果只剩标题行或极短内容，跳过
                if not sub or len(sub) < 10:
                    continue
                if sub:
                    rendered = render_entropy_case(sub)
                    if rendered:
                        entropy_cards.append(rendered)
        elif '思维模型' in sec[:40]:
            entropy_cards.append(render_entropy_card(sec))
        elif '熵减卡片' in sec[:40]:
            entropy_cards.append(render_entropy_card(sec))
        elif '健康提醒' in sec[:40]:
            sec = re.sub(r'^.*?健康提醒\s*[#│|].*?\n', '', sec, count=1).strip()
            entropy_cards.append(render_entropy_health(sec))
        elif '机会雷达' in sec[:40]:
            sec = re.sub(r'^.*?机会雷达\s*[#│|━].*?\n', '', sec, count=1).strip()
            # 去掉残留的统计行（如"今日新增 N 条机会（Top N）："）
            sec = re.sub(r'^今日新增\s+\d+\s+条机会.*?\n', '', sec).strip()
            # 按分隔符拆分为多条机会
            if '---OPP---' in sec:
                opp_blocks = re.split(r'---OPP---', sec)
                for ob in opp_blocks:
                    ob = ob.strip()
                    if not ob:
                        continue
                    zero2idea_cards.append(render_single_opportunity_card(ob))
            elif 'META:' in sec:
                # 新格式（有META行但只有1条，无分隔符）
                zero2idea_cards.append(render_single_opportunity_card(sec))
            else:
                # 兼容旧格式
                zero2idea_cards.append(render_entropy_opportunity(sec))
        elif '昨日想法回顾' in sec[:40] or '想法回顾' in sec[:40]:
            sec = re.sub(r'^.*?昨日想法回顾\s*[#│|].*?\n', '', sec, count=1).strip()
            entropy_cards.append(render_entropy_graveyard_review(sec))
        elif '得到课程' in sec[:40]:
            sec = re.sub(r'^.*?得到课程雷达\s*[#│|━].*?\n', '', sec, count=1).strip()
            sec = re.sub(r'^今日\s+\d+\s+条课程信号.*?\n', '', sec).strip()
            if '---DEDAO---' in sec:
                dedao_blocks = re.split(r'---DEDAO---', sec)
            else:
                dedao_blocks = [sec]
            for db in dedao_blocks:
                db = db.strip()
                if not db:
                    continue
                # 每个课程分组内可能有多条 item（以 DEDADOMETA 分隔）
                if 'DEDADOMETA:' in db:
                    # 按课程分组标题拆分
                    sub_items = re.split(r'(?=\nDEDADOMETA:)', db)
                    for si in sub_items:
                        si = si.strip()
                        if si:
                            entropy_cards.append(render_single_dedao_card(si))
                else:
                    entropy_cards.append(render_single_dedao_card(db))
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

# --- 10x投机周报卡片 ---

def render_10x_report(md_text):
    """把 10x 周报 markdown 拆成多张卡片"""
    cards = []

    # 只在顶级标题处分割（市场总览/赛道信号评分/深挖报告），忽略内部 ## Step 标题
    sections = re.split(r'^## (?=(?:市场总览|赛道信号评分|深挖报告))', md_text, flags=re.MULTILINE)

    overview_text = ""
    sector_blocks = []
    deep_blocks = []

    for part in sections:
        part = part.strip()
        if not part:
            continue
        if part.startswith("市场总览"):
            overview_text = part[len("市场总览"):].strip()
        elif part.startswith("赛道信号评分"):
            sector_section = part[len("赛道信号评分"):].strip()
            # 按 ### 拆分各赛道
            sub_parts = re.split(r'^### ', sector_section, flags=re.MULTILINE)
            for sp in sub_parts:
                sp = sp.strip()
                if sp:
                    sector_blocks.append(sp)
        elif part.startswith("深挖报告"):
            deep_section = part[len("深挖报告"):].strip()
            # 按 ### 深挖 N: 拆分（用 lookahead 避免切掉 ### 深挖 N: 本身）
            sub_parts = re.split(r'^### (?=深挖 \d+:)', deep_section, flags=re.MULTILINE)
            for sp in sub_parts:
                sp = sp.strip()
                if sp:
                    deep_blocks.append(sp)

    # 市场总览卡片
    if overview_text:
        cards.append(card("model", "📊 市场总览", "10x投机 · 市场总览", md_to_html(overview_text)))

    # 赛道信号卡片
    for block in sector_blocks:
        title_m = re.match(r'(.+?)\n', block)
        title = title_m.group(1).strip() if title_m else "赛道"
        triggered = "触发深挖" in title
        bar_class = "case" if triggered else "model"
        tag = "🔴 触发深挖" if triggered else "🟡 观察"
        cards.append(card(bar_class, tag, title, md_to_html(block)))

    # 深挖报告卡片
    for block in deep_blocks:
        title_m = re.match(r'(.+?)\n', block)
        title = title_m.group(1).strip() if title_m else "深挖报告"
        cards.append(card("zero2idea", "🔍 深挖报告", title, md_to_html(block), collapsed=True))

    return cards

def render_dual_innovation_report(md_text):
    """把 10x 研究每日一页渲染为单张决策卡，避免暴露后台台账。"""
    title_m = re.search(r'^#\s+(.+)$', md_text, flags=re.MULTILINE)
    title = title_m.group(1).strip() if title_m else "10x研究"
    body = re.sub(r'^#\s+.+$', '', md_text, count=1, flags=re.MULTILINE).strip()
    return card(
        "dual-innovation",
        "📈 10x研究 · 今日一页",
        title,
        md_to_html(body),
        collapsed=False,
    )

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
        return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{DATE}} · {{SECTION_TITLE}}</title><link rel="stylesheet" href="{{CSS_PATH}}"></head><body><nav class="top-nav"><a href="{{INDEX_PATH}}" class="brand">商业感知</a>{{TAB_NAV}}</nav><div class="container"><div class="day-nav"><a href="{{PREV_DAY}}">← 前一天</a><div class="day-title">{{DATE}}</div><a href="{{NEXT_DAY}}">后一天 →</a></div>{{CARDS}}<footer class="site-footer"><p>Daily Digest</p></footer></div><script>
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
    """生成频道导航。公开前台只有两个入口；其余历史频道不再曝光，
    目录与旧链接保留但导航不指向它们。"""
    tabs = [
        ("perception", f"{base_path}/perception/", "🌍 今日判断"),
        ("dual-innovation", f"{base_path}/dual-innovation/", "📈 10x研究"),
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
    elif section == "perception":
        out_dir = PERCEPTION_DIR
    elif section == "zero2idea":
        out_dir = ZERO2IDEA_DIR
    elif section == "10x":
        out_dir = TENX_DIR
    elif section == "dual-innovation":
        out_dir = DUAL_INNOVATION_DIR
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

def render_index(dates_perception=None, dates_dual_innovation=None, today=None):
    """渲染首页 + 今日判断频道首页。

    公开前台只维护今日判断（perception/）与 10x研究（dual-innovation/）。
    熵减计划、想法墓地、Zero2Idea、旧10x投机、信号库不再生成或更新，
    历史目录与 HTML 原样保留，旧链接仍可访问。
    """
    if dates_perception is None: dates_perception = set()
    if dates_dual_innovation is None: dates_dual_innovation = set()
    if today is None: today = datetime.now().strftime("%Y-%m-%d")

    # 首页 = 最新今日判断。没有 Repricing 报告时安静地说明，
    # 不回退展示想法墓地或其他后台内容。
    latest_p = max(dates_perception) if dates_perception else today
    p_cards = collect_repricing_cards(latest_p)
    if not p_cards.strip():
        # 最新日无报告，往前找最近有判断的一天
        for d in sorted(dates_perception, reverse=True):
            p_cards = collect_repricing_cards(d)
            if p_cards.strip():
                latest_p = d
                break

    tab_nav = _tab_nav_html("perception", ".")
    prev_d, next_d = _find_prev_next(latest_p, dates_perception)
    prev_link = f"perception/{prev_d}.html" if prev_d else "index.html"
    next_link = f"perception/{next_d}.html" if next_d else "index.html"

    if p_cards.strip():
        cards_html = '<div class="attention-note">今天只需要理解一个变化。原始信号保留在后台，只有形成判断后才进入这里。</div>' + p_cards
    else:
        cards_html = '<div class="attention-note">暂无值得占用注意力的新判断。</div>'

    template = load_template("day.html")
    html = template
    html = html.replace("{{DATE}}", latest_p)
    html = html.replace("{{SECTION_TITLE}}", "今日判断")
    html = html.replace("{{CSS_PATH}}", "style.css")
    html = html.replace("{{INDEX_PATH}}", "index.html")
    html = html.replace("{{TAB_NAV}}", tab_nav)
    html = html.replace("{{PREV_DAY}}", prev_link)
    html = html.replace("{{NEXT_DAY}}", next_link)
    html = html.replace("{{CARDS}}", cards_html)
    html = html.replace(".html.html", ".html")
    (BASE_DIR / "index.html").write_text(html)

    # 今日判断频道 index：用当前模板重渲染最新一期，确保频道首页与导航保持一致
    PERCEPTION_DIR.mkdir(parents=True, exist_ok=True)
    if dates_perception:
        latest = max(dates_perception)
        cards = collect_repricing_cards(latest)
        if cards.strip():
            intro = '<div class="attention-note">先读判断。只有当判断值得追踪时，再展开候选与证据。</div>'
            render_day_page(latest, intro + cards, "perception", "今日判断", dates_perception)
            latest_file = PERCEPTION_DIR / f"{latest}.html"
            if latest_file.exists():
                (PERCEPTION_DIR / "index.html").write_text(latest_file.read_text())

    # 10x研究首页由独立交互页维护（10x投机/scripts/render_personal_research_frontpage.py）。
    # 每日渲染只新增/更新按日期归档页，不用最新日报覆盖首页，
    # 否则会抹掉“当前行动 / 本周变化 / 公司库”。
    DUAL_INNOVATION_DIR.mkdir(parents=True, exist_ok=True)

    # 熵减计划、想法墓地、Zero2Idea、旧10x投机、信号库（browse）频道
    # 已停止生成与更新：历史目录与 index 保留原样，供旧链接直达。

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

def collect_repricing_cards(date_str):
    """收集商业感知报告；默认只展开主判断。"""
    reports = get_repricing_outputs()
    if date_str not in reports:
        return ""
    return "\n".join(render_repricing_report(reports[date_str]))

def get_repricing_dates():
    return set(get_repricing_outputs().keys())

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

def collect_10x_cards(date_str):
    """收集 10x 投机周报卡片"""
    tenx_outputs = get_10x_outputs()
    if date_str not in tenx_outputs:
        return ""
    cards = render_10x_report(tenx_outputs[date_str])
    return "\n".join(cards)

def get_10x_dates():
    """收集所有有 10x 周报数据的日期"""
    return set(get_10x_outputs().keys())

def collect_dual_innovation_cards(date_str):
    """收集双创研究系统的成熟每日一页。"""
    reports = get_dual_innovation_outputs()
    if date_str not in reports:
        return ""
    return render_dual_innovation_report(reports[date_str])

def get_dual_innovation_dates():
    return set(get_dual_innovation_outputs().keys())

def collect_graveyard_cards(date_str):
    """收集想法墓地卡片"""
    cards_html = []
    
    # 日报
    graveyard_outputs = get_graveyard_outputs()
    if date_str in graveyard_outputs:
        c = render_graveyard_report(graveyard_outputs[date_str])
        if c: cards_html.append(c)
    
    # 当天更新的 stones（排除存档类占位条目）
    stones = get_stones()
    day_stones = [s for s in stones
                  if s.get("content")
                  and s.get("category") != "📦存档"
                  and not s.get("content","").startswith("【早期笔记")
                  and (s.get("updated_at","").startswith(date_str)
                       or s.get("time","").startswith(date_str))]
    for s in day_stones[:15]:
        cards_html.append(render_stone(s))
    
    return "\n".join(cards_html)

def get_available_dates():
    """获取所有有数据的日期"""
    entropy_dates = set(get_entropy_outputs().keys())
    graveyard_dates = set(get_graveyard_outputs().keys())
    # stones 里的日期也加进去（排除存档占位条目，它们不应该创造"有数据"的日期）
    for s in get_stones():
        if s.get("category") == "📦存档": continue
        if not s.get("content") or s.get("content","").startswith("【早期笔记"): continue
        for k in ("updated_at", "time"):
            v = s.get(k, "")
            if v: graveyard_dates.add(v[:10])
    return entropy_dates, graveyard_dates

def collect_browse_items():
    """读取 browse items.json，返回列表"""
    items = load_json(BROWSE_DATA_DIR)
    if not items:
        return []
    return items

def render_browse_details():
    """为没有外部链接的条目生成本地详情页"""
    items = collect_browse_items()
    if not items:
        return

    BROWSE_DIR.mkdir(parents=True, exist_ok=True)
    template = load_template("day.html")

    detail_count = 0
    for idx, item in enumerate(items):
        if item.get("link", "").strip():
            continue  # 有外部链接，跳过

        title = item.get("hook_title") or item.get("original_title", "")
        source = item.get("source", "")
        date = item.get("date", "")
        summary = item.get("summary", "")
        detail_id = idx

        # 渲染完整摘要
        full_summary = summary if len(summary) <= 2000 else summary[:2000] + "..."

        html = template
        html = html.replace("{{DATE}}", date)
        html = html.replace("{{SECTION_TITLE}}", source)
        html = html.replace("{{CSS_PATH}}", "../style.css")
        html = html.replace("{{INDEX_PATH}}", "../index.html")
        html = html.replace("{{TAB_NAV}}", _tab_nav_html("browse", ".."))
        html = html.replace("{{PREV_DAY}}", "")
        html = html.replace("{{NEXT_DAY}}", "")

        card_html = f'''<div class="browse-detail">
  <div class="browse-item-header">
    <span class="browse-source-tag">{esc(source)}</span>
    <span class="browse-date">{esc(date)}</span>
  </div>
  <div class="browse-detail-title">{esc(title)}</div>
  <div class="browse-detail-content">{esc(full_summary)}</div>
</div>'''

        html = html.replace("{{CARDS}}", card_html)
        html = html.replace(".html.html", ".html")

        detail_file = BROWSE_DIR / f"detail-{detail_id}.html"
        detail_file.write_text(html)

        # 回写 link 到 items（这样列表页能链接到详情页）
        item["link"] = f"detail-{detail_id}.html"
        detail_count += 1

    # 保存更新后的 items.json
    items_file = Path.home() / ".hermes" / "data" / "browse" / "items.json"
    with open(items_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✅ 渲染 {detail_count} 个详情页")

def render_browse_index(per_page=20):
    """渲染 browse 频道页面"""
    items = collect_browse_items()
    if not items:
        print("⚠️ browse items.json 为空或不存在")
        return

    # 分页
    total = len(items)
    total_pages = (total + per_page - 1) // per_page

    # 生成所有分页
    for page in range(1, total_pages + 1):
        # 获取当前页的条目
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_items = items[start_idx:end_idx]

        # 生成卡片 HTML
        cards_html = []
        for item in page_items:
            title = item.get("hook_title") or item.get("original_title", "")
            source = item.get("source", "")
            date = item.get("date", "")
            link = item.get("link", "")
            summary = item.get("summary", "")

            # 如果有链接，整条可点击
            if link:
                card_start = f'<a href="{link}" class="browse-item">'
                card_end = '</a>'
            else:
                card_start = '<div class="browse-item">'
                card_end = '</div>'

            card_html = f'''{card_start}
  <div class="browse-item-header">
    <span class="browse-source-tag">{esc(source)}</span>
    <span class="browse-date">{esc(date)}</span>
  </div>
  <div class="browse-title">{esc(title)}</div>
  {f'<div class="browse-summary">{esc(summary[:100])}</div>' if summary else ''}
{card_end}'''

            cards_html.append(card_html)

        # 生成分页导航
        pagination_html = '<div class="pagination">'

        if page > 1:
            prev_page = page - 1
            if prev_page == 1:
                prev_link = "index.html"
            else:
                prev_link = f"page-{prev_page}.html"
            pagination_html += f'<a href="{prev_link}" class="pagination-link">← 上一页</a>'

        pagination_html += f'<span class="pagination-info">第 {page} 页 / 共 {total_pages} 页</span>'

        if page < total_pages:
            next_page = page + 1
            pagination_html += f'<a href="page-{next_page}.html" class="pagination-link">下一页 →</a>'

        pagination_html += '</div>'

        # 生成页面 HTML
        all_cards = '\n'.join(cards_html)

        template = load_template("day.html")
        html = template
        html = html.replace("{{DATE}}", f"第 {page} 页")
        html = html.replace("{{SECTION_TITLE}}", "随便逛逛")
        html = html.replace("{{CSS_PATH}}", "../style.css")
        html = html.replace("{{INDEX_PATH}}", "../index.html")
        html = html.replace("{{TAB_NAV}}", _tab_nav_html("browse", ".."))
        html = html.replace("{{PREV_DAY}}", "")  # browse 不用日期导航
        html = html.replace("{{NEXT_DAY}}", "")
        html = html.replace("{{CARDS}}", f'<div class="browse-grid">{all_cards}</div>{pagination_html}')
        html = html.replace(".html.html", ".html")

        # 输出文件
        BROWSE_DIR.mkdir(parents=True, exist_ok=True)
        if page == 1:
            output_file = BROWSE_DIR / "index.html"
        else:
            output_file = BROWSE_DIR / f"page-{page}.html"

        output_file.write_text(html)

        print(f"✅ 渲染 browse: {output_file.name} ({len(page_items)} 条)")

# ============================================================
# 主逻辑
# ============================================================

def render_date(date_str, p_dates=None, d_dates=None):
    """渲染某一天的公开前台页面：今日判断与 10x研究。

    熵减计划、想法墓地、Zero2Idea、旧10x投机、信号库已停止渲染；
    对应历史页面保留在原目录，不再新增或更新。
    """
    if p_dates is None: p_dates = set()
    if d_dates is None: d_dates = set()

    p = collect_repricing_cards(date_str)
    if p.strip():
        intro = '<div class="attention-note">先读判断。只有当判断值得追踪时，再展开候选与证据。</div>'
        render_day_page(date_str, intro + p, "perception", "今日判断", p_dates)

    d = collect_dual_innovation_cards(date_str)
    if d.strip():
        intro = '<div class="attention-note">每天只看一页：当前状态、变化、错价、反证和行动。</div>'
        render_day_page(date_str, intro + d, "dual-innovation", "10x研究", d_dates)

def main():
    args = sys.argv[1:]
    if not args:
        print("用法: render.py --today | --date YYYY-MM-DD | --all")
        sys.exit(1)

    if "--today" in args:
        d = datetime.now().strftime("%Y-%m-%d")
        p_dates = get_repricing_dates()
        d_dates = get_dual_innovation_dates()
        render_date(d, p_dates, d_dates)
        render_index(p_dates, d_dates, today=d)
        print(f"✅ 渲染完成: {d}")

    elif "--date" in args:
        idx = args.index("--date")
        d = args[idx + 1]
        p_dates = get_repricing_dates()
        d_dates = get_dual_innovation_dates()
        render_date(d, p_dates, d_dates)
        render_index(p_dates, d_dates, today=d)
        print(f"✅ 渲染完成: {d}")

    elif "--all" in args:
        p_dates = get_repricing_dates()
        d_dates = get_dual_innovation_dates()
        for d in sorted(p_dates | d_dates):
            render_date(d, p_dates, d_dates)
        render_index(p_dates, d_dates)
        print(f"✅ 渲染完成: 今日判断 {len(p_dates)} 天, 10x研究 {len(d_dates)} 天")

if __name__ == "__main__":
    main()
