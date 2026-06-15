# HarnessOS V12 Light Studio Overall Workbench Prompt

Mode: `gpt-image-2 skill Mode B host-native`

Purpose: generate the target overall workbench concept image for V12-0A design review.

Boundary:

- This is design-only prototype evidence.
- It is not browser, BFF, DTO, runtime or Xpert parity evidence.
- It must not be used to claim product-grade frontend completion.

Prompt:

```text
Create a high-fidelity product UI concept image for HarnessOS V12 Light Studio Workbench. Style: clean modern SaaS workbench, inspired by Codex CLI clarity and Xpert-like node canvas density, but original. Use a consistent light theme: warm white background, pale dotted canvas, blue primary accents, slate text, subtle shadows, 8px corner radius, lucide-like outline icons. Chinese UI labels only, crisp but not excessive. Overall screen composition: top global bar with workspace/project/env/model/provider status chips and safe action buttons; left vertical icon rail plus secondary navigation showing 工作台, 智能体, 工作流, 技能, MCP, 证据, 运行; center read-only canvas with curved connected edges and six nodes: 触发器, 规划Agent, 讨论Agent A, 讨论Agent B, 总结Agent, 质检Agent; each node shows role, status, input/output ports, evidence chip; right inspector panel for selected 总结Agent showing 角色, 目标, 记忆摘要, 工具, 技能, MCP, 质量, 证据; bottom/right chat workbench with user goal input and proposal timeline. Add small status badges: API 在线, 运行中, 证据就绪, 等待确认. This is design-only prototype, no production-ready claim. Render as a polished browser-app screenshot, 16:9, sharp, coherent, no brand logos copied from other products.
```

