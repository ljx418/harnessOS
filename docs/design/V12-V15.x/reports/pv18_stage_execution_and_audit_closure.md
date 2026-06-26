# PV18 Knowledge OPC 阶段执行与审计闭环

用途：记录本阶段开发执行、端到端验收、PRD 规格检视和出门结论。  
阅读对象：开发者、审计者、产品评审者和后续自动化 Agent。  
边界：本文只描述 PV18 bounded review 阶段，不声明生产可用，不声明完整 Workflow Studio 或 Agent executor 完备。

## 本阶段目标

- 在工作流平台上实现一个可运行的知识运营业务工作流。
- 业务路径覆盖 workspace、source import、build、query、citation、quality feedback、correction plan、evidence review。
- 前端只调用 `/bff/pv18/knowledge/*`，不得直连 runtime store、connector internal route 或 data_service 内部接口。
- data_service 使用真实 `data_service_mcp` 的 `mcp_stdio` 路径验收。
- 不因 OPC 知识业务对工作流平台做定制化分支，保持 BFF / Gateway / Connector / Evidence 的通用边界。

## 已完成开发

- PV18 BFF 支持真实 data_service MCP source import、build、query 路径。
- build/query 使用独立 acceptance workspace，避免 data_service workspace archive 后影响后续查询。
- PV18 工作台支持用户输入 source title、source content 和 question。
- E2E route-log 支持 PV18 `/bff/pv18/*` 路由边界取证。
- PV18 acceptance runner 增加截图、真实 `mcp_stdio` data_service 和 no-false-green 门槛。
- 新增 CDP 自动化验收脚本，使用真实页面路径生成截图和证据包。

## 端到端验收结论

结论：PASS。

- 真实 data_service：`data_service_mcp / mcp_stdio`。
- citation：`source_ref_count=16`。
- correction：`requires_human_review=true`，`auto_publish_allowed=false`。
- browser boundary：未发现 `/v1/rpc`、`/internal/runtime`、`/runtime/store`、`/api/runtime`、`/debug/runtime` 或 `data_service_mcp/internal`。
- platform generality：`knowledge_only_platform_changes=[]`。
- no-false-green：未发现禁止的正向过度声明。

## 2026-06-27 阶段性复审

结论：PASS。

- 重新对照 PV18 原始 PRD 检查 workspace、source import、build、query/citation、quality feedback、correction plan 和 evidence review。
- 重新执行真实 `data_service_mcp / mcp_stdio` 预检、PV18 BFF 测试、前端 TypeScript / build、Chrome CDP headless E2E 和 acceptance runner。
- 重新生成截图证据和 evidence package，`acceptance-data.json` 的 `created_at` 已更新为 `2026-06-27T00:00:00Z`。
- 修订主线文档旧口径：PV18 不再标记为仅文档阶段或未实现；当前状态为 bounded review implementation passed。
- 未发现致命或重大规格偏差；剩余风险仍限于 CI 浏览器依赖、本地 data_service 环境依赖和生产级能力未覆盖。

## 证据入口

- `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/acceptance-data.json`
- `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/knowledge-console-screenshot.png`
- `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/query-and-citation-screenshot.png`
- `docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization/evidence-review-screenshot.png`
- `docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json`
- `docs/design/V12-V15.x/reports/pv18_knowledge_opc_visual_acceptance_report.html`

## PRD 规格检视

结论：PASS。

- 用户可完成从资料导入到证据审查的完整知识运营工作流。
- 查询结果必须有 citation 才能支撑回答；验收未把无引用回答标记为 verified。
- 质量反馈和修正计划保留人工审查门槛。
- 当前能力只支持 bounded review，不扩大为生产级能力声明。

## 目标架构检视

结论：PASS。

- Browser -> PV18 BFF -> Gateway / ConnectorExecutionRuntime -> data_service_mcp 的边界成立。
- 前端未直连 runtime store 或 data_service 内部路径。
- 业务输入作为 DTO payload 进入通用 BFF，不新增只适用于知识业务的平台 runtime 分支。
- Evidence package 覆盖 DTO、route log、artifact lineage、claim matrix、redaction scan 和截图。

## 剩余风险

- Linux Playwright 浏览器缺少 `libnspr4.so`，本次改用 Windows Chrome CDP headless 验收；建议后续在 CI 镜像内安装 Playwright 依赖。
- data_service MCP 仍依赖本地 `/mnt/c/workspace/data_service/backend/.venv-wsl` 环境；迁移 CI 时需要固定依赖安装步骤。
- PV18 当前仍是 bounded review 能力，不覆盖多租户生产隔离、长时任务恢复、生产部署回滚或完整权限治理。
