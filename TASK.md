# Task: Daily Digest 3 频道改造

## 项目路径: ~/Documents/daily-digest/

## 当前结构
- index.html — 频道入口选择页（2个大卡片，点进去才看内容）
- entropy/ — 熵减计划按天页面
- graveyard/ — 想法墓地按天页面
- style.css — 样式
- render.py — 渲染脚本（数据→HTML）
- templates/ — HTML 模板

## 要改成

### 1. 三个频道 tab（固定顶部导航栏）
- 🧠 熵减计划
- 🪦 想法墓地  
- 🔭 Zero2Idea（从熵减计划的「机会雷达」区块拆出来）

### 2. 所有页面顶部固定 3 tab 栏
- 粘性定位（sticky），永远可见
- 当前频道高亮 active 状态
- 点击切换到对应频道的最新日页面

### 3. 默认落地页 = 想法墓地最新日
- 访问 index.html 直接展示想法墓地最新天的卡片内容
- 不再需要「选择频道」入口页

### 4. 每个频道按天展示，可前后翻日
- 保持现有 day-nav（前一天/后一天）
- tab 栏始终可用，在任何天的页面都能切换频道

## 具体改动

### render.py 改动

1. **新增 ZERO2IDEA_DIR = BASE_DIR / 'zero2idea'**

2. **parse_entropy_output() 改为返回两个列表**：
   - 遇到 '机会雷达' 区块时，不再放入 entropy cards，而是单独收集到 zero2idea_cards 列表
   - 函数签名改为返回 (entropy_cards_html_list, zero2idea_cards_html_list)
   - 机会雷达区块用 render_entropy_opportunity() 渲染

3. **新增 collect_zero2idea_cards(date_str)**：从 parse_entropy_output 的返回中取 zero2idea 部分

4. **新增 get_zero2idea_dates()**：收集所有有 zero2idea 数据的日期

5. **render_day_page() 增加 section='zero2idea'**：输出到 ZERO2IDEA_DIR

6. **render_index() 重写**：首页 = 想法墓地最新日内容；新增 zero2idea/index.html

7. **页面模板中加入 3 tab 栏**：
   所有页面的 top-nav 中加入：
   ```html
   <nav class="top-nav">
     <a href="../index.html" class="brand">每日精选</a>
     <div class="tab-nav">
       <a href="../entropy/" class="tab-item">🧠 熵减计划</a>
       <a href="../index.html" class="tab-item active">🪦 想法墓地</a>
       <a href="../zero2idea/" class="tab-item">🔭 Zero2Idea</a>
     </div>
   </nav>
   ```
   （active 根据当前频道切换）

8. **render_date() 和 main() 改动**：处理 zero2idea 频道

### style.css 改动

1. **.top-nav 改为 sticky**：position: sticky; top: 0;

2. **tab 样式**：
   ```css
   .top-nav { flex-wrap: wrap; }
   .tab-nav { width: 100%; display: flex; gap: 0; padding: 8px 0 0; border-top: 1px solid var(--border); margin-top: 4px; }
   .tab-nav .tab-item { font-size: 0.88rem; font-weight: 500; padding: 8px 16px; color: var(--text-muted); border-radius: 9999px; transition: all 0.15s; }
   .tab-nav .tab-item:hover { color: var(--text); background: var(--surface-warm); text-decoration: none; }
   .tab-nav .tab-item.active { color: var(--text); background: var(--surface-warm); font-weight: 600; }
   ```

## 重要约束

- 保持现有 Notion 风格设计不变（颜色、字体、间距、卡片样式）
- render.py 的数据加载逻辑不变
- md_to_html, esc, card() 等工具函数不变
- 卡片渲染函数不变
- 只改页面结构、导航、频道拆分逻辑

## 验证

改完后运行 `python3 render.py --all` 确认无报错
