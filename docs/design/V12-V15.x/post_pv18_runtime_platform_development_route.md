# Post-PV18 Runtime Platform Development Route

用途：记录用户认可的 PV19 之后主线开发路线，并把每个目标拆成明确开发阶段。
阅读对象：产品、架构、开发、测试、审计人员。
边界：本文是路线图和阶段定义，不是实现证据；不得据此声明生产可用、完整 Workflow Studio、完整 Agent executor 或商业化完成。

## 1. Route Summary

本路线优先证明“完整工作流平台受控闭环”，然后补齐执行器、工作台完整性、外部接入、生产治理、业务产品化和商业化准备。

| Order | Stage | Development goal | Exit claim boundary |
| --- | --- | --- | --- |
| 1 | PV19：Runtime-backed Workflow Studio Closed Loop | 用户在工作台编排、发布、运行、处理人工交互并审查证据。 | bounded runtime workflow platform closed loop ready for review。 |
| 2 | PV20：Complete Agent Executor | 通用 Agent executor 可执行受治理的 agent/tool/skill/MCP 节点。 | governed Agent executor implementation ready for bounded review。 |
| 3 | PV21：Complete Workflow Studio | Studio 具备版本、发布、回滚、运行、审计和完整画布工作台能力。 | complete Workflow Studio candidate ready for bounded review。 |
| 4 | WP-M0：Workflow Platform Main Entry Alignment | 把后续实现主线重新对齐到工作流平台首入口，并生成 PRD、架构、验收和 drawio 文档门禁。 | documentation ready for implementation review only。 |
| 5 | WP-M1-M4：Workflow Platform MVP Candidate | 首入口、画布交互、运行证据闭环和受治理 Executor 产品化融合。 | workflow platform MVP candidate ready for bounded review。 |
| 6 | PV22：Path B External App Contract | 外部 App 可通过 SDK、BFF 模板、capability token 和 contract 接入稳定工作流平台。 | external app contract ready for bounded integration review。 |
| 7 | PV23：Path D Production Governance Hardening | 租户、凭证、审计留存、部署恢复和运维 smoke 成体系。 | production governance hardening ready for pre-production review。 |
| 8 | PV24：Business Pack Productization | Meeting / Knowledge / Interview / Investment / Video Studio 逐步产品化。 | selected business pack ready for bounded product review。 |
| 9 | PV25：Open-source / Commercial Readiness | 发布、贡献、部署、许可、计费、限额和商业化材料准备。 | open-source/commercial readiness candidate ready for review。 |

## 2. Stage Definitions

### PV19 - Runtime-backed Workflow Studio Closed Loop

目标：把 V13 Studio、PV17 product closed loop 和 PV18 real business evidence 收敛为一条通用平台闭环。

最低开发内容：

- 工作台默认入口可用，不再以空白根路径作为交付体验。
- 画布编辑 readback 为 WorkflowSpecGraph。
- WorkflowDiff 经用户确认后发布 WorkflowVersion。
- Runtime 按 WorkflowVersion 启动 WorkflowInstance。
- 至少一个 human gate 改变后端 runtime 状态。
- 同一工作台展示 artifact、trace、quality、audit、claim evidence。

出门条件：

- Browser E2E、BFF route log、DTO snapshot、runtime report、human action report、claim matrix、redaction、No False Green 全部 PASS。

### PV20 - Complete Agent Executor

目标：补齐通用 Agent executor，使 workflow 中的 Agent 节点不是 UI 模拟或业务 runner 特例。

最低开发内容：

- 定义 Agent node execution contract。
- 支持 tool / skill / MCP 调用、approval gate、timeout、cancel、retry。
- 支持 executor sandbox、scope、credential redaction 和 audit。
- 支持 station/node 输入输出、artifact refs、trace refs、quality refs。
- 用至少两个非同构节点验证 executor 通用性。

出门条件：

- Agent executor E2E PASS。
- 负向用例覆盖越权 tool、缺少 approval、timeout、cancel、secret redaction。
- 不声明 unrestricted automation 或 production agent readiness。

### PV21 - Complete Workflow Studio

目标：把 V13/PV19 工作台推进为完整 Studio 候选能力。

当前状态：PV21 bounded candidate 已完成并通过阶段性验收；它证明默认 Studio 入口、BFF DTO 边界、graph save/validate/diff、publish/rollback、runtime run、human gate 和 evidence review 的有界闭环。它不证明生产可用、产品级前端完成或完整 Workflow Studio GA。

规范文档：

- `pv21_complete_workflow_studio_prd.md`
- `pv21_complete_workflow_studio_target_architecture.md`
- `pv21_complete_workflow_studio_bff_dto_contract.md`
- `pv21_complete_workflow_studio_acceptance_runner_spec.md`
- `pv21_complete_workflow_studio_development_and_acceptance_plan.md`
- `pv21_complete_workflow_studio_milestone_roadmap.md`
- `pv21_complete_workflow_studio_acceptance_gate.md`
- `pv21_complete_workflow_studio_current_gap_analysis.md`
- `pv21_complete_workflow_studio_implementation_task_matrix.md`
- `pv21_complete_workflow_studio_implementation_readiness_audit.md`
- `pv21_complete_workflow_studio_document_support_audit.md`
- `pv21_complete_workflow_studio_gap_analysis.drawio`
- `pv21_stage_execution_audit_closure.md`
- `evidence/pv21-complete-workflow-studio/acceptance-data.json`
- `evidence/pv21-complete-workflow-studio/pv21-acceptance-report.html`

已完成的有界开发内容：

- 默认 Studio 入口与候选工作台。
- 节点库、画布、Inspector、基础错误反馈和 validation 状态。
- WorkflowVersion 管理、publish、rollback、run history。
- WorkflowDiff 审查、版本比较、审计追踪。
- 画布状态、运行状态和 evidence 状态在同一产品表面一致。
- Chrome CDP 浏览器截图、BFF 测试和 evidence package。

剩余边界：

- 复杂拖拽式画布、完整节点增删和高级布局仍属于后续 UX hardening。
- 可访问性、复杂错误状态、长文本和产品级前端仍未作为 GA 完成声明。

出门条件：

- Bounded Studio scenario matrix PASS。
- 版本、回滚、运行、审计闭环 PASS。
- No False Green、redaction、platform generality PASS。

### WP-M0 - Workflow Platform Main Entry Alignment

目标：把 PV21 bounded Studio candidate、V13 canvas pilot、PV19 runtime loop、PV20 governed executor path 和 PV22 external app readiness 统一到“工作流平台作为首入口”的后续开发方向。

当前状态：文档开发阶段。WP-M0 只证明文档可以支撑后续实现计划，不证明任何新增代码能力已经完成。

规范文档：

- `workflow_platform_main_entry_prd.md`
- `workflow_platform_main_entry_target_architecture.md`
- `workflow_platform_main_entry_development_and_acceptance_plan.md`
- `workflow_platform_main_entry_milestone_roadmap.md`
- `workflow_platform_main_entry_acceptance_gate.md`
- `workflow_platform_main_entry_current_gap_analysis.md`
- `workflow_platform_main_entry_implementation_task_matrix.md`
- `workflow_platform_main_entry_document_support_audit.md`
- `workflow_platform_main_entry_gap_analysis.drawio`

最低文档内容：

- 工作流平台首入口目标体验。
- 当前架构与目标架构差异。
- 具体代码实体和分层交互。
- WP-M1 到 WP-M5 开发及验收计划。
- 项目里程碑、验收门槛和出门条件。
- No-Go 和 forbidden claim。

出门条件：

- 文档集完整。
- drawio 不超过 8 页，中文，架构实体明确。
- 文档审计结论为可以支撑后续实现计划。
- 不声明 implementation complete、production ready、complete Workflow Studio GA 或 Agent executor ready。

### PV22 - Path B External App Contract

目标：让外部应用或新业务 App 可以按标准方式接入 HarnessOS。

当前状态：PV22-R0 文档与 readiness、WP-M5B readiness refresh 以及 PV22-S1 到 PV22-SA 有界实现验收已完成。该结论只支持外部应用接入契约进入 bounded integration review，不支持生产可用、外部生态完成或商业化完成声明。

规范文档：

- `pv22_external_app_contract_prd.md`
- `pv22_external_app_contract_target_architecture.md`
- `pv22_external_app_contract_bff_dto_contract.md`
- `pv22_external_app_contract_development_and_acceptance_plan.md`
- `pv22_external_app_contract_milestone_roadmap.md`
- `pv22_external_app_contract_acceptance_gate.md`
- `pv22_external_app_contract_current_gap_analysis.md`
- `pv22_external_app_contract_implementation_task_matrix.md`
- `pv22_external_app_contract_implementation_readiness_audit.md`
- `pv22_external_app_contract_document_support_audit.md`

最低开发内容：

- 冻结 external app protocol version。
- 整理 Python SDK、TypeScript SDK、BFF template 和 reference app。
- 定义 capability token、scope binding、method/event/error registry。
- 提供最小接入样例和负向权限样例。

出门条件：

- Python/TypeScript SDK smoke PASS。
- BFF template smoke PASS。
- Reference app E2E PASS。
- Auth/scope negative fixture PASS。

### PV23 - Path D Production Governance Hardening

目标：为后续生产可用讨论补齐治理和运维前置条件。

最低开发内容：

- Tenant isolation。
- Credential lifecycle、rotation、revocation。
- Audit retention、export、incident timeline。
- Deployment runbook、health check、rollback smoke。
- CI default suite 和 explicit integration suite。

出门条件：

- Tenant denial fixtures PASS。
- Credential rotation/revocation PASS。
- Audit export 和 incident timeline PASS。
- Deployment smoke 和 rollback notes PASS。

### PV24 - Business Pack Productization

目标：把 reference pack / stub pack 分批推进为真实业务产品候选。

建议顺序：

1. Knowledge OPC 正式产品化。
2. Meeting 工作流产品化。
3. Interview 面试流程。
4. Video Studio 真实渲染链路。
5. Investment 投研流程。

最低开发内容：

- 每个业务 Pack 有明确输入、输出、质量门槛、人工审查、artifact lineage。
- 业务逻辑保留在 Pack / domain adapter / BFF facade，不污染平台核心。
- 每个业务 Pack 都有独立 PRD、架构、runner、evidence package。

出门条件：

- Selected pack E2E PASS。
- Artifact lineage、trace、quality、redaction、claim evidence PASS。
- Platform generality review PASS。

### PV25 - Open-source / Commercial Readiness

目标：让项目具备对外发布、安装、贡献、部署和商业评估基础。

最低开发内容：

- Contributor docs、development setup、release pipeline。
- License / CLA / security policy。
- Deployment docs、sample apps、runbooks。
- Billing / quota / rate limit strategy。
- Public-facing project introduction 和 audit guide。

出门条件：

- Fresh machine setup smoke PASS。
- Release artifact checklist PASS。
- License/security docs reviewed。
- Commercial readiness checklist reviewed。

## 3. Cross-Stage Rules

- 每个阶段开始前必须有独立 PRD、目标架构、开发计划、验收门槛和 readiness audit。
- 每个阶段结束前必须有 browser/API/runtime evidence、No False Green、redaction 和 claim-to-evidence。
- 不得把后续阶段目标提前写成本阶段完成事实。
- 不得为了业务 Pack 产品化定制 workflow core、Gateway core 或 App shell。
- 任何 production ready 声明必须等 PV23 之后另设生产验收阶段。
