# Daily Digest

辉哥的商业感知入口。`商业感知`是产品总品牌；公开导航只保留两个入口：

1. **今日判断**（`perception/`）：用 Repricing 分析把散乱信号压缩成少量判断——**什么正在被重新定价，以及它对 Build / 10x 意味着什么。**
2. **10x研究**（`dual-innovation/`）：10x 投机研究系统的成熟投资交付，沿用原有 URL，旧链接不受影响。

首页没有 Repricing 报告时，安静地显示“暂无值得占用注意力的新判断”，不回退展示后台内容。

默认信息层级：

1. 一个今日主判断；
2. 最多少量候选判断；
3. 按需展开的证据层。

Repricing 正式报告路径：`~/.hermes/data/repricing/reports/YYYY-MM-DD.md`。

## 10x研究

“10x研究”是 10x 投机研究系统的公开阅读层（原名“双创研究”，URL 保持 `/dual-innovation/` 不变）。
首页分为“当前行动 / 本周变化 / 公司库”，普通研究在后台持续积累，只有改变行动的证据才即时提醒。
每天的成熟判断仍保留为日期归档页，内容来自 `~/Documents/10x投机/deliveries/YYYY-MM-DD-*.md`，
而不是把原始信号、研究台账或未验证猜测直接公开。

固定阅读结构是：当前状态、今天改变了什么、可能的错价、最强反证和当前行动。没有足够证据时，允许明确发布“今日无重要变化”，不为保持日更而制造机会。

自动发布入口：`./publish_dual_innovation.sh`。所有公开栏目统一通过
`./publish_to_personal_site.sh` 触发个人站部署；GitHub 仓库仅保留公开产物的版本记录。

## 已停更频道（历史保留）

熵减计划（`entropy/`）、想法墓地（`graveyard/`）、Zero2Idea（`zero2idea/`）、
旧 10x 投机（`10x/`）、信号库（`browse/`）已停止生成与更新：`render.py` 不再渲染这些频道，
导航也不再指向它们。历史目录与 HTML 原样保留，旧链接仍可直达，只是不再更新、不再曝光。
“生意案例”和“Build 下注”是下一阶段目标；在通过证据门的首批内容之前不创建栏目。

🔗 [jsbuildslowly.com/digest](https://jsbuildslowly.com/digest/)

旧 GitHub Pages 地址只保留兼容跳转，不再作为正式发布出口。
