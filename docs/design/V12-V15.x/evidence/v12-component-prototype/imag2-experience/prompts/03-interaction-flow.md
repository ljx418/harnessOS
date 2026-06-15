# HarnessOS V12 Light Studio Interaction Flow Prompt

Mode: `gpt-image-2 skill Mode B host-native`

Purpose: generate a user flow concept image for V12-0A design review.

Boundary:

- This is design-only prototype evidence.
- It describes the intended interaction route but does not prove execution.
- It must stay consistent with the same Light Studio component set.

Prompt:

```text
Create a high-fidelity user interaction flow infographic for HarnessOS V12 Light Studio, consistent with previous Light Studio images. Use the same light SaaS style, blue accents, slate typography, subtle shadows, shadcn-like UI blocks, Chinese labels. Show a left-to-right journey with 6 steps, each represented by a small realistic UI scene and a connector line: 1 用户输入自然语言目标 in independent Chat Workbench; 2 系统生成 WorkflowDiff 提案 with timeline states 解析中/生成中/等待确认; 3 画布预览只读工作流 graph with nodes and curved edges; 4 用户点击 Agent 节点 and right inspector opens role/goal/tools/skills/MCP/evidence; 5 用户选择 确认/修订/拒绝 with permission and policy state visible; 6 输出结果预览 with quality report and evidence chain refs. Include visible state machine badges: idle, receiving input, planning, proposal ready, awaiting confirmation, running, completed, blocked, failed. Add boundary notes in small Chinese text: 设计原型, 不作为运行证据, 不跳过确认. Make it look like a polished product design flow board, not a generic diagram, 16:9.
```

