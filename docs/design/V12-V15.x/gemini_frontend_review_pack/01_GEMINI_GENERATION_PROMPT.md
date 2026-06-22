# Gemini Prompt For HarnessOS V12 Frontend Prototype Generation

请只阅读当前文件夹中的文件，并基于它们为 HarnessOS 生成一个新的、可独立审查的前端网页原型。

你必须先阅读：

1. `00_README.md`
2. `02_PRODUCT_AND_BOUNDARIES.md`
3. `03_FROZEN_UX_DECISIONS.md`
4. `04_USER_SCENARIOS_AND_ACCEPTANCE.md`
5. `05_STARTER_PROTOTYPE_LIGHT_STUDIO.html`
6. `06_REFERENCE_RENDER.png`
7. `07_REVIEW_CHECKLIST.json`
8. `08_MANIFEST.json`

## 你的角色

- 资深产品设计负责人
- 前端架构师
- 低代码工作流工作台 UX 设计师

## 你的任务

请生成一个新的 HarnessOS V12 Light Studio 浏览器原型，用于前端设计审查和下一阶段实现准备。输出优先级如下：

1. 最优：`index.html` + `styles.css` + `app.js`
2. 可接受：单文件 `index.html`，内联 CSS / JS

同时输出：

- `README.md`：说明设计结构、组件逻辑、已知限制
- `audit-notes.md`：自审结果、剩余问题、禁止过度声明

## 硬边界

你的输出必须满足以下限制：

- 当前阶段是 `design_only`
- 不是 browser implementation evidence
- 不是 BFF evidence
- 不是 runtime evidence
- 不是 DTO evidence
- 不是 Xpert parity proof
- 不是 complete Workflow Studio proof

禁止正向声明：

- `Xpert parity complete`
- `Xpert-level UX complete`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `production ready`
- `Agent executor ready`
- `已完全追平 Xpert`
- `产品级前端已完成`
- `完整工作流工作台已完成`
- `生产可用`
- `Agent 执行器已完成`

禁止把参考图、HTML 原型、设计文档包装成：

- HarnessOS runtime evidence
- 浏览器已实现证据
- BFF 已实现证据

## 必须出现的页面结构

### 1. 顶部全局状态栏

必须展示：

- HarnessOS V12 / Light Studio
- 工作空间
- 项目
- 环境
- 模型
- 供应商
- API 状态
- 运行状态
- 证据状态
- 等待确认状态

必须支持这些状态样式：

- `api_online`
- `api_offline`
- `api_rate_limited`
- `api_unconfigured`
- `run_idle`
- `run_in_progress`
- `run_blocked`
- `run_failed`
- `awaiting_confirmation`
- `evidence_ready`
- `evidence_missing`
- `design_only_evidence`

### 2. 左侧一级 Rail

一级导航是产品域，不是资源列表。至少包含：

- 工作台
- 智能体
- 工作流
- 技能
- MCP
- 证据
- 运行记录
- 模板中心
- 设置

图标要求：

- 风格统一
- 简洁现代
- 接近 lucide / shadcn 的线性图标风格
- 不使用 emoji 或粗糙占位图标

### 3. 左侧二级导航

当用户处于“工作台 / 工作流”域时，二级导航需要展示：

- 分镜生成工作流
- 罗马广场讨论工作流
- 代码审查工作流
- 文档总结工作流

并展示“上下文资源”区：

- 智能体
- 技能
- MCP
- 证据
- 运行记录

必须有：

- 计数
- hover 态
- active 态
- 可折叠层次

### 4. 中央画布

必须是低代码工作流画布，而不是卡片平铺。

必须包含：

- 网格背景
- 节点
- 输入输出端口
- 曲线连线
- hover 态
- selected 态
- blocked 态
- waiting 态
- minimap 或局部视图提示

必须至少有 6 个节点：

- Trigger
- Planner Agent
- Discussion Agent A
- Discussion Agent B
- Summary Agent
- Quality Agent

节点卡必须展示：

- 节点编号
- 节点名称
- Agent 角色
- 输入端口
- 输出端口
- 状态 badge
- output ref / evidence ref

必须能表达多输入、多输出。

### 5. 右侧 Inspector

点击节点后，右侧 Inspector 必须同步变化。

Inspector 至少展示：

- Agent 名称
- 角色
- 目标
- 记忆摘要
- Tools
- Skills
- MCP refs
- 输入 refs
- 输出 refs
- 质量门槛
- 证据 refs
- 最新输出摘要

长文本必须可读，不得严重截断。

### 6. 底部工作台

底部区域不能退化成普通聊天框。必须是工作台。

至少包含这些 tabs：

- 对话
- 提案时间线
- Trace
- 质量
- 证据

对话区必须体现：

- 这是 workspace chat
- 用户目标
- 当前系统状态
- 下一步建议
- 不会自动发布 / 不会自动运行
- slash commands，例如 `/help /stations /evidence /diff`

### 7. 交互

请用 JS 做最小可感知交互：

- 点击一级导航，切换二级导航内容
- 点击节点，节点高亮并刷新 Inspector
- hover 节点，显示轻微阴影与端口强调
- 切换底部 tab
- 状态 chip 或状态 badge 支持 tooltip / popover

## 必须覆盖的工作流场景

页面中必须能看出这些场景能力：

1. 多 Agent 讨论
2. 视频分镜创作
3. 文档总结
4. 代码提案
5. 证据审计

## 输出质量要求

- 用简体中文写 UI 文案
- 风格统一，信息密度接近现代 SaaS / AI 工作台
- 布局清楚，不能出现大面积重叠、断线、严重截断
- 不复制 Xpert 的品牌、素材或专有资源
- 可以参考其交互质感，但必须是 HarnessOS 自有表达

## 你必须在最终回答中给出以下结构化结论

```text
overall_result=PASS | CONDITIONAL_GO | NO_GO

supports_v12_0p_high_fidelity_review=true/false
supports_figma_replacement_review=true/false
supports_v12_browser_implementation_readiness_audit=true/false
supports_direct_browser_implementation_now=false

claim_xpert_parity_complete_allowed=false
claim_complete_workflow_studio_ready_allowed=false
claim_production_ready_allowed=false
claim_agent_executor_ready_allowed=false

p0_blockers=[]
p1_fixes=[]
p2_suggestions=[]
```
