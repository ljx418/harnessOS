# Workflow Platform Main Entry Development And Acceptance Plan

用途：把工作流平台首入口目标拆成后续可执行开发阶段和验收门槛。
边界：本文是计划，不是实现证据；当前阶段仅完成文档开发。

## 1. Stage Position

WP-M0 是 PV21 bounded candidate 之后、PV22 implementation 之前的主线对齐门禁。

```text
PV21 bounded candidate
  -> WP-M0 Workflow Platform main-entry documentation gate
  -> WP-M1 main entry implementation
  -> WP-M2 canvas interaction hardening
  -> WP-M3 runtime/evidence convergence
  -> WP-M4 governed Agent executor product integration
  -> PV22 external app contract implementation
```

WP-M0 不替代 PV22，也不把 PV21 升级为 GA。它只确保后续开发不再偏离“工作流平台首入口”目标。

## 2. Substages

| Stage | Goal | Development output | Acceptance output |
| --- | --- | --- | --- |
| WP-M0 | 文档和架构对齐。 | PRD、架构、计划、里程碑、验收门槛、任务矩阵、drawio、文档审计。 | Document support audit PASS。 |
| WP-M1 | 首入口和信息架构。 | 根入口默认 Workflow Platform，导航/状态/空态统一。 | 首屏 browser screenshot、route assertion、No False Green PASS。 |
| WP-M2 | 画布交互专项。 | 滚轮缩放、平移、节点拖拽、自由连线、取消连线、箭头可见性。 | Canvas E2E action log、截图、edge quality report PASS。 |
| WP-M3 | 运行与证据闭环融合。 | WorkflowDiff -> publish -> run -> human gate -> evidence review 同屏。 | BFF route log、DTO snapshot、runtime inspect、evidence panel PASS。 |
| WP-M4 | Agent executor 产品化融合。 | Agent/Tool/Skill/MCP 资源面板和受治理执行入口。 | Executor evidence refs、approval/denial fixtures、copy scan PASS。 |
| WP-M5 | 外部接入前置检查。 | PV22 以 Workflow Platform 为接入目标重检。 | PV22 readiness update PASS。 |

## 3. Development Principles

- 后续代码实现优先复用 PV21 shell，再吸收 V13 canvas、PV19 runtime loop 和 PV20 executor evidence path。
- 后续 BFF/DTO 实现默认复用 `/bff/pv21/*`、`/bff/pv20/*` 和必要的 `/bff/pv19/*` route family；除非 readiness audit 说明必要，否则不先新增大而全的 `/bff/workflow-platform/*` facade。
- 不创建新的孤立演示页作为首入口。
- 首入口必须服务人类审查和真实使用路径，而不是只服务阶段验收。
- 每个子阶段开始前必须有独立 implementation-readiness audit。
- 每个子阶段完成后必须有 PRD review、target architecture review、E2E evidence、No False Green 和 redaction scan。
- 每个子阶段必须按 `workflow_platform_main_entry_bff_dto_contract.md` 和 `workflow_platform_main_entry_acceptance_runner_spec.md` 生成证据。

## 4. Evidence Requirements

| Evidence | Required from | Notes |
| --- | --- | --- |
| `browser-action-log.json` | WP-M1+ | 包含真实用户操作序列。 |
| `browser-network-log.json` | WP-M1+ | 证明浏览器只使用允许 BFF routes。 |
| `dto-snapshot.json` | WP-M1+ | 记录首入口 state / graph / evidence DTO。 |
| `canvas-edge-quality-report.json` | WP-M2 | 记录缩放、拖拽、连线、取消、箭头可见性检查。 |
| `runtime-inspect-report.json` | WP-M3 | 证明 WorkflowVersion -> WorkflowInstance -> StationRun readback。 |
| `evidence-panel-report.json` | WP-M3+ | 证明 artifact/trace/quality/audit/claim/redaction 分类显示。 |
| `agent-executor-integration-report.json` | WP-M4 | 证明受治理执行入口和 denial path。 |
| `user-scenario-report.json` | WP-M3+ | 证明基础 Agent 工作流和三个必验业务场景完成端到端路径。 |
| `no-false-green-scan.txt` | all stages | 禁止虚假完成声明。 |
| `acceptance-report.html` | all stages | 中文、人类可读、含截图证据。 |

## 5. PRD Review Loop

每个子阶段完成后必须回答：

- 用户是否能从首入口理解当前系统能做什么。
- 用户是否能完成该阶段承诺的工作流动作。
- 用户是否能用平台完成文档/知识总结、代码审查、会议/访谈整理三个具体业务场景，而不是只看到抽象能力。
- UI 是否把受限能力说清楚。
- 文档是否把完成状态和后续目标混在一起。
- 是否出现 production ready、product-grade frontend complete、complete Workflow Studio ready、Agent executor ready 或 Xpert parity complete 误报。

## 6. Scenario Acceptance

WP-M3 的出门验收必须包含：

- 基础 Agent 工作流端到端路径：画布拖拽、节点拖拽、自由连线、配置、保存、校验、Diff、发布、运行、Human Gate、Evidence Review。
- 三个 required business scenarios 全部通过：文档/知识总结、代码审查、会议/访谈整理。
- 中文 HTML 验收报告必须把每个业务场景写成“用户输入 -> 平台动作 -> 人工审查点 -> 输出产物 -> 证据”的结构。

WP-M4 的出门验收必须进一步证明：

- 三个业务场景中的 Agent/Tool/Skill/MCP 入口均是受治理能力。
- Approval、denial、timeout/cancel/retry 或 redaction 至少覆盖一个负向或边界用例。
- UI copy 不暗示 unrestricted automation 或 Agent executor ready。

## 7. Stop Conditions

出现以下任一情况必须停止进入下一阶段：

- Browser 直接调用 internal runtime/store route。
- UI 模拟 runtime truth 并被写成真实运行证据。
- 画布核心动作没有自动化 action log 或截图证据。
- 文档把 WP-M0 写成实现完成。
- 文档或 UI 出现禁止 claim。
- PV22 implementation 被提前写成已验收。
- 只展示应用前景但没有跑通 required scenario，却声明用户场景验收通过。
- 创意分镜规划被写成真实视频渲染完成。

## 8. WP-M0 Document Acceptance

WP-M0 仅在以下条件满足后通过：

- 新增文档集齐全。
- Drawio 页数不超过 8 页，并且每页中文、无重复冲突。
- PRD、架构、里程碑、验收门槛和任务矩阵互相一致。
- 文档审计结论为 `GO for implementation planning only`。
- Claim scan 未发现 forbidden positive claims。
- BFF/DTO 合约、acceptance runner 规格和 implementation readiness audit 均存在且互相一致。
