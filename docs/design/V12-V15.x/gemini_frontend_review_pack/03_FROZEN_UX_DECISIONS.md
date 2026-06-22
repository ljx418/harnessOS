# HarnessOS V12 Frozen UX Decisions

本文件是给 Gemini 的冻结设计决策输入。生成新原型时不得偏离这些核心结构。

## 1. Information Architecture

### L1 Product Rail

一级 rail 是产品域：

- 工作台
- 智能体
- 工作流
- 技能
- MCP
- 证据
- 运行记录
- 模板中心
- 设置

### L2 Context Sidebar

二级导航展示当前域资源，不是全局导航重复。

在“工作台 / 工作流”上下文下，默认展示：

- 分镜生成工作流
- 罗马广场讨论工作流
- 代码审查工作流
- 文档总结工作流

并展示上下文资源：

- 智能体
- 技能
- MCP
- 证据
- 运行记录

## 2. Canvas Rules

- 画布是主工作区
- 使用点阵 / 网格背景
- 节点必须有真实端口位置
- 连线必须是曲线且完整连接
- 不允许断线
- 不允许节点互相压住
- 必须能表达 fan-out / fan-in 的趋势

## 3. Required Node Set

最低必须有以下节点：

1. Trigger
2. Planner Agent
3. Discussion Agent A
4. Discussion Agent B
5. Summary Agent
6. Quality Agent

## 4. Node Card Structure

每张节点卡必须至少有：

- 编号
- 名称
- 角色或类型
- 状态 badge
- 输入
- 输出
- refs（evidence / output / tool / policy 中至少一个）

节点需要支持这些视觉状态：

- normal
- hover
- selected
- blocked
- awaiting_confirmation

## 5. Inspector Rules

右侧 Inspector 是选中对象详情区。

必须展示：

- Agent 名称
- 角色
- 目标
- 记忆摘要
- tools
- skills
- MCP refs
- 输入 / 输出 refs
- 质量门槛
- 证据 refs
- 最新输出摘要

## 6. Bottom Workbench Rules

底部工作台是：

- chat
- proposal timeline
- trace
- quality
- evidence

不是单纯“输入框 + 发送按钮”。

必须强调：

- 这是 workspace chat
- 不会自动发布
- 不会自动运行
- WorkflowDiff / confirmation / evidence chain 是核心概念

## 7. Visual Language

- 浅色主题
- 清晰边框与统一圆角
- 轻量阴影
- 现代 SaaS / AI 工作台质感
- 图标必须统一
- 中文文案清楚，不机械

## 8. Design Consistency

Gemini 输出必须保持以下一致性：

- 状态色系统一致
- 节点卡内间距一致
- rail / sidebar / canvas / inspector / workbench 层级一致
- 不能只做表格化信息堆砌

## 9. Evidence Boundary

生成页面时必须显式保留：

- `design_only`
- `not browser implementation evidence`
- `not BFF evidence`
- `not runtime evidence`
