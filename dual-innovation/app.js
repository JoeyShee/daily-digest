const companies = {
  "301308": {
    code:"301308", name:"江波龙", date:"2026-08-12", status:"观察，不行动", statusNote:"等待三季度现金、库存和企业级收入验证",
    tags:["R · 供需／价格型", "AI存储"],
    intro:{doing:"设计、封测并销售存储产品和企业级存储方案",payer:"手机、汽车、服务器、运营商及互联网客户",profit:"存储产品售价、产品结构、库存成本与企业级业务",position:"存储模组与企业级存储解决方案环节"},
    judgment:"利润兑现是真的，但系统现在买的不是“利润很多”，而是“市场低估了利润能持续多久”。库存、借款和负现金流尚未证明这一点。",
    flow:["存储价格与企业需求上升","售价／销量／产品结构变化","毛利与净利润增加","现金转化决定利润质量"],
    positive:["上半年收入240.88亿元，归母净利润105.77亿元","Q2综合毛利率倒算约61.26%，高于Q1","企业级存储收入21.40亿元，同比增长208.80%"],
    risks:["上半年经营现金流-31.51亿元","存货257.77亿元，占总资产60.12%","长期借款104.93亿元，较年末增长139.7%"],
    method:[
      ["基本面动量","检查盈利是否持续改善，而不是只看股价上涨。Q2利润和毛利率继续环比提升，正向事实成立。"],
      ["利润桥分析","把周期涨价、低成本库存和企业级产品升级分开。当前披露无法量化三者贡献，因此不能把全部利润归因于AI。"],
      ["营运资本分析","核对利润是否转成现金。存货增加约造成142.27亿元现金占用，是当前最重要的反证。"],
      ["反向估值","行情接口显示的约8.35倍是上半年利润机械年化，不是真正TTM；直接称低估会低估周期回落风险。"],
      ["催化剂时钟","下一有效验证是三季报：毛利率、库存周转、经营现金流、融资依赖和企业级收入占比。"],
    ],
    glm:"GLM初稿确认利润、毛利率和企业级收入增长，倾向认为低PE提供明显安全边际。",
    codex:"接受增长事实；驳回“低PE即安全边际”。纠正PE口径，并把库存、借款与负现金流设为升级前置条件。",
    sources:[
      ["江波龙2026年半年度报告","https://static.cninfo.com.cn/finalpage/2026-08-11/1225467150.PDF"],
      ["江波龙2026年第一季度报告","https://static.cninfo.com.cn/finalpage/2026-04-28/1225214140.PDF"]
    ]
  },
  "300274": {
    code:"300274", name:"阳光电源", date:"2026-08-12", status:"机会核查", statusNote:"等待半年报分业务利润和现金转化",
    tags:["R · 公司经营拐点", "储能／逆变器"],
    intro:{doing:"销售光伏逆变器、储能系统并开发新能源电站",payer:"电力企业、项目开发商、工商业客户及海外渠道",profit:"储能和逆变器销售、产品毛利及项目开发收益",position:"新能源发电与储能系统核心设备环节"},
    judgment:"价格要求不算极端，但一季度收入、利润和现金流同步下滑。系统必须先证明这是交付与汇率扰动，而不是结构性降速。",
    flow:["全球储能与光伏需求","设备销量和产品结构","毛利与质保／汇率影响","现金回款与资本占用"],
    positive:["2025年储能业务收入同比增长约49%","逆变器毛利率提升约3.76个百分点","海外收入同比增长约49%"],
    risks:["2026Q1收入同比下降18.26%","归母净利润同比下降40.12%","产品×地区交叉利润没有披露，不能证明海外储能是利润主因"],
    method:[["分部利润分析","拆开储能、逆变器和项目开发，避免用合并增长掩盖业务差异。"],["反向估值","当前价格对应的未来增长要求不极端，但估值便宜不能解释经营下滑。"],["反证优先","下一步优先解释Q1利润降幅远大于收入，而不是继续收集行业利好。"]],
    glm:"GLM初稿识别储能与海外增长，并将两者组合解释为主要利润驱动。",
    codex:"否定产品和地区两张独立表可以直接交叉归因；保留增长事实，但要求半年报补足分业务利润和现金证据。",
    sources:[["阳光电源2025年年度报告","https://www.cninfo.com.cn/"],["阳光电源2026年第一季度报告","https://www.cninfo.com.cn/"]]
  },
  "300308": {
    code:"300308", name:"中际旭创", date:"2026-08-11", status:"等待价格", statusNote:"基本面成立，赔率尚未达到行动门槛",
    tags:["R · 高预期", "AI光互连"],
    intro:{doing:"生产面向AI数据中心的高速光模块",payer:"全球云计算和网络设备客户",profit:"800G、1.6T等高端产品销量、ASP与规模效应",position:"AI算力集群内部高速光互连关键节点"},
    judgment:"公司兑现很强，但优秀基本面已经成为共识。当前真正问题不是增长是否存在，而是增长能否超过股价已经要求的高门槛。",
    flow:["AI资本开支增长","高速光模块需求","高端产品收入与利润","当前估值隐含更高增长"],
    positive:["AI资本开支已传导到高速光模块需求","公司收入和利润兑现强","技术与客户位置仍然领先"],
    risks:["当前市值隐含未来利润持续高速复合增长","客户集中和资本开支周期风险","应收、库存和预付款需要转化为现金"],
    method:[["反向估值","先问当前价格要求公司未来赚多少，而不是只给目标价。"],["预期差分析","基本面强不等于错价；只有真实增长超过市场隐含增长才是机会。"],["赔率门","单日下跌不是买点，价格必须给出足够下行保护。"]],
    glm:"GLM确认行业需求与公司兑现强，倾向维持积极判断。",
    codex:"认可基本面，否定直接升级行动；价格隐含要求过高，当前更应等待安全边际。",
    sources:[["中际旭创公司主记录","#"],["历史判断快照","#"]]
  },
  "300124": {
    code:"300124", name:"汇川技术", date:"2026-08-11", status:"长期候选研究", statusNote:"尚未形成正式价值锚",
    tags:["C · 长期复利候选", "工业自动化"],
    intro:{doing:"提供工业自动化控制产品和新能源汽车电驱系统",payer:"制造企业、设备厂商和新能源汽车客户",profit:"自动化高毛利产品、规模制造和跨行业产品平台",position:"工业控制与电气自动化核心部件平台"},
    judgment:"它可能具备从成长公司升级为长期复利公司的部分条件，但还要证明多业务扩张能持续产生高质量现金和增量资本回报。",
    flow:["制造业自动化与电动化","产品平台和客户扩张","收入与利润复利","现金回报与再投资能力"],
    positive:["2025年收入451.05亿元，同比增长21.77%","扣非净利润同比增长22.66%","工业自动化具备产品平台和客户粘性"],
    risks:["新能源汽车业务规模与盈利质量需要分开","研发和扩张投入持续增加","尚未完成三年正常利润与合理价值测算"],
    method:[["竞争优势持续期","判断客户、产品平台和研发是否能把超额回报保持多年。"],["增量资本回报","检查新增投入带来的利润和现金，而不是只看收入规模。"],["唐朝式价值锚","只有利润为真、可持续且不依赖大量新增资本后，才估算三年合理价值。"]],
    glm:"GLM完成业务和财务基线，认为增长稳定且产品平台优势明显。",
    codex:"保留为长期候选，但不在未验证现金回报和分业务质量前给出买入区。",
    sources:[["汇川技术2025年年度报告","https://www.cninfo.com.cn/"]]
  },
  "688012": {
    code:"688012", name:"中微公司", date:"2026-08-11", status:"长期候选研究", statusNote:"等待平台化和资本回报验证",
    tags:["C · 长期复利候选", "半导体设备"],
    intro:{doing:"生产半导体刻蚀设备，并向薄膜沉积等设备扩展",payer:"晶圆制造厂和芯片生产企业",profit:"设备销售、客户验证、产品扩张与后续服务",position:"半导体制造设备上游关键环节"},
    judgment:"公司正在展示设备平台化和现金改善，但半导体周期、研发投入与投资收益仍需拆开，暂时不能直接套用成熟价值企业估值。",
    flow:["国产设备验证","客户采购和产品扩张","收入毛利与服务收入","现金回报和平台持续性"],
    positive:["2025年收入增长36.62%","归母净利润增长30.69%","经营现金流增长57.39%"],
    risks:["扣非利润增速低于归母利润","设备业务仍受客户资本开支影响","平台化优势需要更长时间验证"],
    method:[["平台型公司分析","检查从单品到多品类扩张是否共享客户、技术和服务体系。"],["利润质量拆分","区分主业扣非利润、投资收益和现金流。"],["长期升级门","只有竞争优势、现金回报和再投资空间持续验证后才进入价值锚。"]],
    glm:"GLM识别收入、利润和现金流增长，倾向认为平台化已经成立。",
    codex:"认可积极迹象，但把“平台化已经成立”降为待验证推断，并要求继续拆分扣非利润与资本回报。",
    sources:[["中微公司2025年度披露","https://star.sse.com.cn/"]]
  }
};

const views = document.querySelectorAll('.view');
const navItems = document.querySelectorAll('.nav-item');
function showView(name){
  views.forEach(v=>v.classList.toggle('active',v.id===`view-${name}`));
  navItems.forEach(n=>n.classList.toggle('active',n.dataset.view===name));
  window.scrollTo({top:0,behavior:'smooth'});
}
document.addEventListener('click',e=>{
  const viewButton=e.target.closest('[data-view]');
  if(viewButton) showView(viewButton.dataset.view);
  const companyButton=e.target.closest('[data-company]');
  if(companyButton){renderCompany(companies[companyButton.dataset.company]);showView('company');}
});

function renderCompany(c){
  const detail=document.getElementById('company-detail');
  const logic=c.flow.map((x,i)=>`<div class="logic-step"><b>0${i+1}</b>${x}</div>`).join('');
  const methods=c.method.map(m=>`<div class="method-row"><b>${m[0]}</b><span>${m[1]}</span></div>`).join('');
  const sources=c.sources.map(s=>`<li><a href="${s[1]}" target="_blank" rel="noreferrer">${s[0]}</a></li>`).join('');
  detail.innerHTML=`
    <div class="company-hero">
      <div><div class="eyebrow">公司研究 · ${c.date} 更新</div><div class="company-title-row"><h1>${c.name}</h1><span class="company-code">${c.code}</span></div><div class="strategy-pills">${c.tags.map((t,i)=>`<span class="tag ${i===0&&t.startsWith('C')?'compounder':'repricing'}">${t}</span>`).join('')}</div></div>
      <aside class="decision-box"><span>当前动作</span><strong>${c.status}</strong><p>${c.statusNote}</p></aside>
    </div>
    <article class="intro-card"><span class="section-kicker">30秒认识公司</span><h2>${c.intro.doing}</h2><div class="intro-grid"><div><span>谁付钱</span><strong>${c.intro.payer}</strong></div><div><span>利润来自哪里</span><strong>${c.intro.profit}</strong></div><div><span>产业链位置</span><strong>${c.intro.position}</strong></div><div><span>当前策略身份</span><strong>${c.tags[0]}</strong></div></div></article>
    <article class="thesis-card"><header class="thesis-head"><div><span class="section-kicker">投资判断</span><h2>系统现在怎么看</h2></div><span class="status ${c.status.includes('核查')?'verify':c.status.includes('价格')?'price':c.status.includes('长期')?'research':'wait'}">${c.status}</span></header><div class="thesis-body"><p class="judgment">${c.judgment}</p><span class="section-kicker">利润传导</span><div class="logic-flow">${logic}</div><div class="evidence-grid"><div class="evidence-box positive"><h4>支持判断的证据</h4><ul>${c.positive.map(x=>`<li>${x}</li>`).join('')}</ul></div><div class="evidence-box risk"><h4>最强反证</h4><ul>${c.risks.map(x=>`<li>${x}</li>`).join('')}</ul></div></div></div></article>
    <details class="whitebox" open><summary>展开白盒分析：用了什么方法，怎么得到结论</summary><div class="whitebox-content">${methods}<div class="audit-box"><span class="section-kicker">CC × Codex 交叉验证</span><div class="audit-grid"><div><span>CC（Kimi／GLM）初步研究</span>${c.glm}</div><div><span>Codex最终裁决</span>${c.codex}</div></div></div></div></details>
    <details class="whitebox"><summary>原始证据与来源</summary><div class="whitebox-content"><ul class="source-list">${sources}</ul><p class="source-list">关键数字必须回到公司或交易所一手披露；行情保存时间戳。模型意见不是证据。</p></div></details>`;
}

document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{
  document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));btn.classList.add('active');
  const f=btn.dataset.filter;document.querySelectorAll('.company-card').forEach(card=>card.classList.toggle('hidden',f!=='all'&&card.dataset.kind!==f));
}));
document.getElementById('company-search').addEventListener('input',e=>{
  const q=e.target.value.trim().toLowerCase();document.querySelectorAll('.company-card').forEach(card=>card.classList.toggle('hidden',q&&!card.textContent.toLowerCase().includes(q)));
});
