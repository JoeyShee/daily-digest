# Task: Daily Digest 页面体验修复（3项）

## 修改文件清单

1. `~/.hermes/skills/openclaw-imports/entropy-card/scripts/daily_case_push.py`
2. `~/.hermes/skills/openclaw-imports/entropy-card/scripts/entropy_plan.py`
3. `~/Documents/daily-digest/render.py`

## 任务 A: daily_case_push.py — 空字段过滤 + 推3个案例

### A1. 推3个案例

当前 `main()` 函数（约 line 240-252）只调一次 `pick_next_case()`。改为循环调3次，每个案例之间用空行 + 分隔符分开：

```python
def main():
    results = []
    for _ in range(3):
        case, idx = pick_next_case()
        if case is None:
            break
        results.append((case, idx))
    
    for i, (case, idx) in enumerate(results):
        if i > 0:
            print()  # 案例间空行
        rendered = render_case(case, idx)
        print(f"__TYPE__:classic-case")
        print(f"__INDEX__:{idx}")
        print()
        print(rendered)
```

注意：`pick_next_case()` 每次调用会更新 push log，所以连续调3次是安全的，会依次取3个不同的案例。

### A2. 空字段过滤

**render_product_case()** （约 line 150-268）的精简版模板（else 分支，约 line 225 开始）当前不检查空值：

```python
# 当前（有问题的代码）
parts.append(f"💎 **核心洞察**\n{core_insight}\n")
parts.append(f"📈 **关键数据**\n{key_numbers}\n")
```

改为每个字段都检查非空：

```python
if core_insight:
    parts.append(f"💎 **核心洞察**\n{core_insight}\n")
if key_numbers:
    parts.append(f"📈 **关键数据**\n{key_numbers}\n")
```

对精简版模板中所有字段都做同样处理：`core_insight`, `key_numbers`, `biz_position`, `takeaway`, `red_flag`。

**render_person_path_case()** （约 line 68-140）已经有部分空值检查，但需要确认所有字段都有检查。重点检查：
- `key_numbers` → 已有 `if key_numbers:`
- `first_money` → 已有 `if first_money:`
- `revenue_model` → 已有 `if revenue_model:`
- `path_from_zero` → 已有 `if path_from_zero:`
- `ai_core_role` → 已有 `if ai_core_role:`
- `replicable_path` → 已有 `if replicable_path:`
- `key_insight` → 已有 `if key_insight:`
- `red_flag` → 已有 `if red_flag:`
- `biz_position` → 已有但检查一下是否完整

如果这些都已经有了，person_path_case 不需要改。如果发现漏掉的，补上。

## 任务 D: entropy_plan.py — 清洗机会雷达内部指标

在 `_build_opportunity_radar()` 函数（line 44-126）中，有 `analyzed_opportunities` 的分支（约 line 89-126）。

当前 line 112-113：
```python
reason_short = reason[:120] + "..." if len(reason) > 120 else reason
```

在截断之前，先清洗内部指标：

```python
import re  # 文件顶部可能已有，没有就加

# 清洗内部指标 — 移除括号内的评估分数
reason_clean = re.sub(r'\([^)]*(?:personal_fit_score|pay_evidence|evidence_grade|market_size_score|competition_score|tech_fit_score|personal_fit|tech_complexity|time_to_mvp|mvp_feasibility)[^)]*\)', '', reason)
# 清理残留空括号和多余标点
reason_clean = re.sub(r'\(\)', '', reason_clean)
reason_clean = re.sub(r'[；;]\s*[；;]', '；', reason_clean)
reason_clean = re.sub(r'^\s*[；;]\s*', '', reason_clean)
reason_clean = re.sub(r'\s*[；;]\s*$', '', reason_clean)
reason_clean = reason_clean.strip()
if not reason_clean:
    reason_clean = "详见完整分析"
reason_short = reason_clean[:120] + "..." if len(reason_clean) > 120 else reason_clean
```

这段加在 line 112 之前（替换原来的 line 112-113）。

同理，对 fallback 分支（line 62-87）中的 `evidence` 字段也做类似处理——如果有内部指标就清洗。

## 任务 B（前端兜底）: render.py — 经典案例空卡片跳过

在 `render_entropy_case()` 函数（line 108-120）中，加一个空 body 检查：

```python
def render_entropy_case(block):
    # 去掉开头的经典案例编号行
    block = re.sub(r'^🏆\s*经典案例\s*#\d+[｜|].*?\n', '', block).strip()
    block = re.sub(r'^━+\s*', '', block).strip()
    # 找第一个加粗标题
    title_m = re.search(r'\*\*(.+?)\*\*', block)
    title = title_m.group(1) if title_m else "经典案例"
    # body 去掉标题行
    body = block
    if title_m and block.startswith(title_m.group(0)):
        body = block[title_m.end():].strip()
    
    # 新增：如果 body 为空或只有空白，跳过该卡片
    if not body or not body.strip():
        return ""
    
    return card("case", "🏆 经典案例", title, md_to_html(body))
```

然后在 `parse_entropy_output()` 中（约 line 270-276），过滤掉空字符串：

```python
for sub in sub_cases:
    sub = sub.strip()
    if not sub:
        continue
    sub = re.sub(r'^.*?经典案例\s*[#│|].*?\n', '', sub, count=1).strip()
    if sub:
        rendered = render_entropy_case(sub)
        if rendered:  # 新增：过滤空卡片
            entropy_cards.append(rendered)
```

## 验证步骤（CC 执行完后不要跑，留给傲天验证）

不需要 CC 跑验证，只做代码修改即可。
