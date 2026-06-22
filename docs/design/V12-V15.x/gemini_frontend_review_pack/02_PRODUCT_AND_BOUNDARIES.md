# HarnessOS V12 Product Vision And Boundaries

## Product Goal

HarnessOS V12 的目标不是直接交付完整浏览器工作台，而是为下一阶段前端实现提供一个可审查、可冻结、可生成的高保真原型输入包。

当前目标体验：

- 用户用自然语言描述目标
- 系统将目标组织成可解释的多 Agent 工作流
- 用户能够看到每个 Agent / Station 的职责、状态、工具、证据和质量门槛
- 用户可以在浏览器工作台中观察提案、追踪状态、查看证据
- 高风险动作仍然必须经过确认，不允许把原型误读为真实执行界面

## Target Users

- AI 工作室负责人
- 产品 / 研发团队负责人
- 需要审计 AI 工作流结果的业务用户

## V12 Scope

V12 当前只覆盖：

- product shell
- 工作流平台信息架构
- read-only canvas foundation
- Agent / Station inspector
- workspace chat workbench
- proposal / trace / quality / evidence review surfaces
- V12-0P 高保真原型冻结输入

V12 当前不覆盖：

- 真实浏览器实现完成
- BFF 已实现
- runtime 已接通
- 完整 Workflow Studio
- Xpert 级实现完成

## Hard Product Boundary

### This package can support

- V12-0P 高保真原型生成
- 外部设计审查
- Figma 替代型网页原型生成
- V12 browser implementation readiness audit 输入

### This package cannot prove

- browser implementation complete
- runtime execution
- provider invocation
- BFF route implementation
- WorkflowSpec 持久化能力
- complete Workflow Studio readiness

## Browser And Runtime Boundary

Gemini 生成的页面必须保留这些边界：

- 浏览器页面不能暗示它可以直接调用 internal runtime
- 浏览器页面不能暗示它可以直接 mutate WorkflowDraft / WorkflowVersion / WorkflowInstance
- 浏览器页面不能暗示它可以直接写 StationRun / Artifact
- 页面中的对话框、按钮、节点状态都只能表达 `proposal / review / explainability`

## Required UX Direction

Gemini 输出需要体现这些产品气质：

- 类似现代 AI workbench 的清爽结构
- 像低代码画布，而不是纯聊天页面
- 强调可解释性、证据、审查、确认边界
- 支持多 Agent 协作场景的表达
- 左侧层级关系清晰：L1 产品域，L2 当前域资源与工作流

## Allowed Review Statement

```text
V12 Gemini generation package ready for external review.
```

## Forbidden Positive Claims

- Xpert parity complete
- Xpert-level UX complete
- product-grade frontend complete
- complete Workflow Studio ready
- production ready
- Agent executor ready
- 已完全追平 Xpert
- 产品级前端已完成
- 完整工作流工作台已完成
- 生产可用
- Agent 执行器已完成
