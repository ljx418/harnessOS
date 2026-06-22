# HarnessOS V12 Gemini Generation Pack

Status: `GENERATION_INPUT_READY`

这个目录不再是“审查现有方案”的旧包，而是给 Gemini 直接生成新前端原型用的最小输入包。

目标：

- 让 Gemini 在单一目录内拿到完整上下文；
- 生成一个新的、可独立审查的 HarnessOS V12 Light Studio 前端网页原型；
- 用于替代 Figma 原型阶段的第一轮高保真网页生成；
- 保持 `design_only` 边界，避免虚假实现声明。

## Package Goal

Gemini 应基于本目录中的文件生成：

- 一个新的浏览器原型页面；
- 必要的 CSS / JS；
- 一个自审说明；
- 一个结构化结论，说明该页面是否足以进入下一轮审查。

## File List

| File | Purpose |
| --- | --- |
| `01_GEMINI_GENERATION_PROMPT.md` | 给 Gemini 的主提示词。 |
| `02_PRODUCT_AND_BOUNDARIES.md` | 产品目标、当前阶段边界、禁止声明。 |
| `03_FROZEN_UX_DECISIONS.md` | 已冻结的 IA、画布、Inspector、工作台设计决策。 |
| `04_USER_SCENARIOS_AND_ACCEPTANCE.md` | 典型场景与审查门槛。 |
| `05_STARTER_PROTOTYPE_LIGHT_STUDIO.html` | 可直接打开的 starter HTML 原型。 |
| `06_REFERENCE_RENDER.png` | 当前方向的参考渲染图，用于视觉对齐。 |
| `07_REVIEW_CHECKLIST.json` | 机器可读的生成与审查要求。 |
| `08_MANIFEST.json` | 包清单、边界声明、允许/禁止口径。 |

## Hard Boundary

本包只能支持：

- Gemini 生成新的前端设计原型
- 外部设计审查
- V12-0P 高保真网页原型讨论
- browser implementation readiness audit 的输入准备

本包不能证明：

- 浏览器实现已完成
- BFF 已实现
- runtime 已实现
- Xpert parity complete
- complete Workflow Studio ready
- production ready

## Allowed Wording

```text
V12 Gemini generation package ready for external review.
```

## Forbidden Positive Interpretations

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
