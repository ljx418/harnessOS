# HarnessOS V12 Light Studio Component Sheet Prompt

Mode: `gpt-image-2 skill Mode B host-native`

Purpose: generate the six-component design sheet for V12-0A design review.

Boundary:

- This is design-only prototype evidence.
- It is not browser implementation evidence.
- It must remain consistent with the overall workbench prompt.

Prompt:

```text
Create a single high-fidelity component design sheet for HarnessOS V12 Light Studio, consistent with the previous image. White/light gray background, blue accent, slate text, subtle shadows, 8px radius, shadcn/Radix-like components, lucide-like icons. Layout: six labeled component panels arranged in a tidy 3x2 grid, each panel showing realistic UI details, not abstract tables. Panel 1: 全局标题栏 with workspace/project/env/model/status chips and safe buttons 预览, 只读, 提交审批. Panel 2: 左侧导航 with vertical icon rail and secondary menu groups 工作台/智能体/工作流/技能/MCP/证据/运行/设置, clear active states and badges. Panel 3: 画布工作台 toolbar, dotted canvas sample, curved edge handles, zoom/minimap controls, read-only badge. Panel 4: Agent节点卡 showing role, goal, model/provider, status, multiple input/output ports, evidence chip, hover popover and dropdown detail. Panel 5: 右侧检查器 with tabs 概览/配置/工具/质量/证据, redacted refs and blocked reason style. Panel 6: Chat工作台 with independent chat history, natural-language input, command chips, proposal timeline, confirm/revise/reject controls disabled until WorkflowDiff. Include small state examples: API 在线/离线, 运行中/失败/阻断, 证据就绪/缺失. This is a design-only component sheet, not browser or runtime evidence. Crisp visual design, 16:9, no copied external product branding.
```

