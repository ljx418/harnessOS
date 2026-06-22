# HarnessOS Project Introduction Poster Copy

Status: design / marketing review package.

This copy is for a user-facing project introduction poster set. It is not
runtime evidence, BFF evidence, browser implementation evidence, production
readiness evidence, Xpert parity evidence or complete Workflow Studio evidence.

## Target Audience

| Audience | Pain | Message |
| --- | --- | --- |
| AI 工作室负责人 | 想把重复创作、研发、审查流程产品化，但担心 AI 黑盒不可控。 | HarnessOS 把多 Agent 分工、产物、质量和证据链放在同一个工作台里。 |
| 技术 / 产品负责人 | 需要快速试验 Agent 工作流，同时保留审批、证据和回溯能力。 | 先生成 WorkflowSpec / Diff，再由用户确认关键动作。 |
| 业务审计 / 运营用户 | 想知道 AI 结果从哪里来、是否可靠、哪里失败。 | 每个工位都有角色、输入、输出、质量报告和证据引用。 |

## Master Poster

Title:

```text
HarnessOS
把自然语言变成可审查的多 Agent 工作流
```

Subtitle:

```text
描述目标，生成工作流，观察每个 Agent，审查产物与证据，再决定是否确认下一步。
```

Five-step quick path:

```text
1. 输入目标
2. 生成草案
3. 查看 Agent 分工
4. 审查产物与证据
5. 用户确认下一步
```

Boundary line:

```text
当前海报用于产品介绍与设计审查，不代表生产可用、完整 Workflow Studio 或 Xpert 追平。
```

## Poster 01 - Quickstart

Title:

```text
五步上手：从一句话到可审查工作流
```

Steps:

```text
输入自然语言目标 -> 系统生成工作流草案 -> 画布展示 Agent 工位 -> 用户审查质量与证据 -> 确认后进入受控执行或修订
```

User promise:

```text
你不需要先写复杂 DSL；先把目标说清楚，HarnessOS 帮你把目标拆成可观察、可审计、可恢复的 Agent 工位。
```

## Poster 02 - Workflow Map

Title:

```text
一套工作台，覆盖多类 AI 工作流
```

Workflow families:

```text
多 Agent 讨论：罗马广场式多角色辩论、互相质询、总结共识与分歧。
视频创作：点子 -> brief -> 脚本 -> 分镜 -> 图像产物 -> 质量检查。
文档总结：读取本地文档，输出摘要、风险、行动项和证据引用。
代码提案：生成计划、diff proposal、测试建议和 review handoff，不自动 commit/push/deploy。
证据审计：打开 Runtime Report、Quality Report、Evidence Chain 和 redaction 状态。
```

## Poster 03 - Use Cases

Title:

```text
面向小团队的真实应用场景
```

Use cases:

```text
创作团队：用分镜工作流把创意变成可审查创作包。
研发团队：让多个 Agent 评审方案、生成代码提案和测试计划。
知识团队：总结本地 Markdown、会议材料和技术文档。
产品团队：把用户目标拆成 WorkflowSpec、Diff 和验收门槛。
审计团队：追踪每个结论的 Agent、attempt、artifact 和 evidence ref。
```

## Poster 04 - Business Outcomes

Title:

```text
可能带来的团队结果
```

Outcomes:

```text
把一次性 AI 对话沉淀成可复用工作流。
减少“AI 输出不知道从哪来”的审计成本。
让小工作室用标准化 Agent 工位交付创作、研发和审查任务。
让失败、阻断、等待确认不再静默发生。
把产物、质量、证据链变成可交接资产。
```

## Poster 05 - Trust And Evidence

Title:

```text
每一步都能解释，每个结果都有证据
```

Trust system:

```text
Agent 角色：谁负责这个工位。
输入输出：每个节点消费什么、产出什么。
质量门槛：是否通过 Quality Agent 检查。
证据链：artifact ref、runtime report、quality report、redaction status。
用户确认：高风险动作先生成提案，再等待确认。
```

## Forbidden Positive Claims

Do not use these phrases as positive claims:

```text
production ready
Xpert parity complete
complete Workflow Studio ready
Agent executor ready
生产可用
已完全追平 Xpert
完整 Workflow Studio 已完成
Agent 执行器已完成
```

