# TASK: Zero2Idea 机会雷达页面优化

## 背景
Daily Digest 的 Zero2Idea 频道页面有严重体验问题：
1. 所有机会挤在一个卡片里（因为数据源输出一整块文本）
2. 手机端没适配（无 mobile breakpoint）
3. 决策标签没有颜色区分

## 需要修改的 3 个文件

### 文件 1: `/Users/joeyshee/.hermes/skills/openclaw-imports/entropy-card/scripts/entropy_plan.py`

修改 `_build_opportunity_radar()` 函数（第 44-122 行）。

**当前行为**: 把所有机会拼成一块文本，用 `\n` join 到一起。

**改为**: 每条机会之间用 `\n---OPP---\n` 分隔，每条前面加 META 行。

输出格式示例：
```
今日新增 4 条机会（Top 5）：
---OPP---
META: score=84 | tag=观察 → 冷冻 | source=榜单
**Tabula. AI-powered data tool for startups...**
产品横跨数据集成+BI+报告自动化...
证据缺口: 真实关键词搜索量和CPC数据...
---OPP---
META: score=71 | tag=观察 → 缩小验证 | source=榜单
**Julep AI...**
这个机会基于单一 Toolify...
```

具体改法 — 把第 83-122 行的 analyzed_opportunities 分支改为：

```python
    # 有 analyzed_opportunities，按 score 排序取 Top 5
    analyzed.sort(key=lambda x: x.get("score", 0), reverse=True)
    top = analyzed[:5]

    opp_blocks = []
    for opp in top:
        title = opp.get("title", "").strip()
        if len(title) > 80:
            title = title[:77] + "..."
        score = opp.get("score", 0)
        source_ch = opp.get("source_channel", "")
        decision = opp.get("decision", "")
        rec = opp.get("recommendation", "")
        reason = opp.get("decision_reason", "")
        gap = opp.get("evidence_gap", [])

        # 决策标签
        tag = ""
        if decision:
            tag = decision
        if rec:
            tag = f"{tag} → {rec}" if tag else rec

        # 理由截断
        reason_short = reason[:120] + "..." if len(reason) > 120 else reason
        gap_str = "；".join(gap[:2]) if gap else ""

        block = f"META: score={score} | tag={tag} | source={source_ch}\n"
        block += f"**{title}**\n"
        block += f"{reason_short}"
        if gap_str:
            block += f"\n证据缺口: {gap_str}"
        opp_blocks.append(block)

    summary = data.get("summary", {})
    new_count = summary.get("new_opportunities", len(analyzed))
    header = f"今日新增 {new_count} 条机会（Top {len(top)}）："
    return header + "\n---OPP---\n" + "\n---OPP---\n".join(opp_blocks)
```

同样修改 fallback 分支（第 66-81 行），每条机会之间也用 `---OPP---` 分隔，加 META 行。

### 文件 2: `/Users/joeyshee/Documents/daily-digest/render.py`

#### 2a. 新增解析函数（在 `render_entropy_opportunity` 后面，约第 147 行后）

```python
def _parse_opp_meta(line):
    """解析 META: score=84 | tag=观察 → 冷冻 | source=榜单"""
    m = re.match(r'META:\s*score=(\d+)\s*\|\s*tag=(.+?)\s*\|\s*source=(.+)', line.strip())
    if m:
        return {'score': int(m.group(1)), 'tag': m.group(2).strip(), 'source': m.group(3).strip()}
    return None

def _decision_tag_class(tag):
    """决策标签 → CSS class"""
    tag_lower = tag.lower()
    if '冷冻' in tag_lower or '观察' in tag_lower:
        return 'freeze'
    elif '缩小验证' in tag_lower or '验证' in tag_lower:
        return 'validate'
    elif '立项' in tag_lower or '执行' in tag_lower:
        return 'launch'
    return 'validate'

def render_single_opportunity_card(block_text):
    """渲染单条机会卡片"""
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
                # title 行之后的内容
                rest = line[title_m.end():].strip()
                if rest:
                    body_lines.append(rest)
                continue
        body_lines.append(line)

    if not title:
        title = "机会"

    # 构建 body HTML
    body_html = f'<div class="opp-meta-row">'
    if tag:
        tag_cls = _decision_tag_class(tag)
        body_html += f'<span class="decision-tag {tag_cls}">{esc(tag)}</span>'
    body_html += f' <span style="color:var(--text-muted);font-size:0.88rem;">来源: {esc(source)}</span>'
    body_html += '</div>'

    # body 内容
    body_text = '\n'.join(body_lines)
    body_html += md_to_html(body_text)

    # 在 header title 后面拼 score badge
    title_with_score = f'{title} <span class="opp-score">{score}</span>'

    return card("zero2idea", "🔭 ZERO2IDEA", title_with_score, body_html)
```

#### 2b. 修改 `parse_entropy_output` 中 zero2idea 分支（第 213-215 行）

将：
```python
        elif '机会雷达' in sec[:40]:
            sec = re.sub(r'^.*?机会雷达\s*[#│|].*?\n', '', sec, count=1).strip()
            zero2idea_cards.append(render_entropy_opportunity(sec))
```

改为：
```python
        elif '机会雷达' in sec[:40]:
            sec = re.sub(r'^.*?机会雷达\s*[#│|].*?\n', '', sec, count=1).strip()
            # 按分隔符拆分为多条机会
            if '---OPP---' in sec:
                opp_blocks = re.split(r'---OPP---', sec)
                for ob in opp_blocks:
                    ob = ob.strip()
                    if not ob:
                        continue
                    zero2idea_cards.append(render_single_opportunity_card(ob))
            else:
                # 兼容旧格式（没有分隔符的情况）
                zero2idea_cards.append(render_entropy_opportunity(sec))
```

### 文件 3: `/Users/joeyshee/Documents/daily-digest/style.css`

在第 536 行 `@media (min-width: 768px)` 之前，插入以下 CSS：

```css
/* ---------- 机会卡片专属样式 ---------- */
.opp-score {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
  background: rgba(37, 99, 235, 0.08);
  color: var(--color-zero2idea);
  vertical-align: middle;
  margin-left: 8px;
  letter-spacing: 0;
}

.opp-meta-row {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.decision-tag {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 3px 12px;
  border-radius: 9999px;
  line-height: 1.4;
}
.decision-tag.freeze   { background: rgba(142, 142, 147, 0.1);  color: #6b6b70; }
.decision-tag.validate { background: rgba(223, 171, 1, 0.1);   color: #b08d00; }
.decision-tag.launch   { background: rgba(22, 163, 74, 0.1);   color: #16a34a; }

.opp-evidence-gap {
  font-size: 0.88rem;
  color: var(--text-muted);
  padding: 10px 14px;
  background: var(--surface-warm);
  border-radius: var(--radius-sm);
  margin-top: 12px;
  line-height: 1.7;
}

/* ---------- Mobile first ---------- */
@media (max-width: 640px) {
  html { font-size: 16px; }
  .container { padding: 0 14px; }
  .top-nav { padding: 0 14px; }
  .tab-nav .tab-item { font-size: 0.78rem; padding: 6px 10px; }
  .day-nav { padding: 14px 0; }
  .day-nav a { font-size: 0.82rem; padding: 6px 10px; }
  .day-nav .day-title { font-size: 1rem; }
  .card { margin-bottom: 20px; border-radius: 10px; }
  .card-header { padding: 14px 16px 12px; gap: 8px; }
  .card-header h2 { font-size: 1.05rem; }
  .card-header .card-type { font-size: 0.75rem; }
  .card-body { padding: 0 16px 20px; }
  .card-body p { line-height: 1.7; margin-bottom: 10px; font-size: 0.92rem; }
  .opp-score { font-size: 0.68rem; padding: 2px 6px; }
  .channel-card { padding: 16px 18px; }
  .channel-card .channel-icon { font-size: 1.5rem; margin-right: 12px; }
}
```

## 验收

改完后运行：
```bash
cd ~/Documents/daily-digest && python3 render.py --today
```

然后用浏览器打开 `zero2idea/2026-06-04.html` 检查：
1. 4 条机会各自独立卡片
2. 卡片 header 显示标题 + 评分 badge
3. 决策标签有颜色区分（冷冻灰、缩小验证黄、立项绿）
4. 手机 viewport（375px）下排版正常
5. 熵减计划和想法墓地页面不受影响（也重新渲染一下确认）

最后也跑一下历史数据确保不 break：
```bash
cd ~/Documents/daily-digest && python3 render.py --all
```
