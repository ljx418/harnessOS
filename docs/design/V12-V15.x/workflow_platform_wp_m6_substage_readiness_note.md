# WP-M6 Substage Readiness Note

用途：在进入 WP-M6 实质开发前，固定正常路径数据驱动闭环的技术路线、证据要求和停止条件。
边界：本文是子阶段开工 readiness note，不是实现证据。不得据此声明前端功能已经完成、生产可用、完整 Workflow Studio GA、Agent executor ready 或产品级前端完成。

## 1. Decision

```text
substage=WP-M6_FRONTEND_FULL_DATA_DRIVEN_CLOSURE
readiness_status=ROUTE_RECORD_RETAINED_AFTER_WP_M6_PASS
selected_route=ROUTE_A_EXISTING_ROUTE_FAMILIES_PLUS_MINIMAL_WORKFLOW_PLATFORM_FACADE
implementation_status=PASSED_BOUNDED_ACCEPTANCE
can_start_wp_m7=YES_WITH_WP_M6_EVIDENCE
frontend_only_cleanup=NO_GO
```

WP-M6 采用 Route A：

- 复用 `/bff/v13/*`、`/bff/pv19/*`、`/bff/pv20/*`、`/bff/pv21/*` 已有 bounded review 路由族。
- 只在缺口处补充最小 `/bff/workflow-platform/*` facade / DTO composition。
- Browser 只允许通过 typed BFF client 读取工作台数据，不允许直接调用 runtime/store/Gateway/internal routes。
- 前端本地静态数据只能作为显式 fallback/fixture，不能作为 normal path 业务事实来源。

## 2. Route Options

| Route | Decision | Use when | Risk |
| --- | --- | --- | --- |
| Route A: Existing routes plus minimal facade | Selected | 当前已有 v13/pv19/pv20/pv21/workflow-platform routes 能覆盖大部分数据来源，只需补齐 DTO composition。 | 需要清晰记录每个 UI 区域的数据来源，避免 client composition 失控。 |
| Route B: Full workflow-platform facade first | Backup only | WP-M6 source inventory 证明 Route A route sprawl 会导致能力丢失、验收不可复现或证据不可追踪。 | 开发范围更大，可能推迟前端可见进展。 |
| Route C: Frontend-only static cleanup | No-Go | 不适用。 | 无法证明 BFF/DTO 数据驱动闭环，会制造 false green。 |

## 3. WP-M6 Work Items

| Work item | Required output | Pass rule |
| --- | --- | --- |
| Normal-path static source inventory | `frontend-data-source-closure-report.json` draft with UI regions and current source classification。 | `scenarioData`、`fallbackGraph`、静态 timeline、静态 Inspector、proposal-only chat 均被定位并分类。 |
| BFF/DTO source mapping | DTO snapshot and route map。 | 每个 UI region 都有 BFF/DTO/artifact ref source 或显式 fallback 条件。 |
| Frontend data replacement plan | Implementation task list tied to source map。 | 不删除已验收能力；只替换 normal path source。 |
| Fallback boundary | Screenshot/log requirement for fallback labels。 | fallback 必须显示 source、reason 和 non-claim boundary。 |
| Claim safety | No False Green scan。 | 禁止把 WP-M6 写成 frontend complete、product-grade 或 production ready。 |

## 4. Required Evidence For WP-M6 Exit

WP-M6 PASS 必须同时具备：

- `frontend-data-source-closure-report.json` validates against `schemas/frontend-data-source-closure-report.schema.json`。
- `normal_path_static_sources == 0`。
- `browser-network-log.json` proves allowed BFF routes only。
- `dto-snapshot.json` covers scenario, graph, Inspector, timeline, quality, evidence and chat initial context。
- screenshots prove normal path and fallback labels。
- PRD review confirms WP-FR-14 and WP-FR-20 boundaries。
- Target architecture review confirms browser -> typed client -> BFF/DTO -> store/runtime/evidence direction。
- No False Green and redaction scan pass。

## 5. Stop Conditions

WP-M6 必须停止并回到计划审查，如果出现任一情况：

- Source inventory 发现正常路径静态数据无法替换，且替换会丢失 WP-M1A 到 WP-M5A 已验收能力。
- Route A 无法提供稳定 BFF/DTO/artifact refs，需要 Route B 的 full workflow-platform facade 才能闭环。
- 实现方案变成前端-only cleanup、rename mock 或截图证明。
- Browser 需要绕过 BFF 直接访问 runtime/store/Gateway/internal routes。
- 任一报告把 fallback/design-only/mock 数据当成 normal path evidence。

如果触发 Route A vs Route B 取舍，必须单独记录 trade-off；未获明确批准前不得进入 WP-M7。

## 6. Final Readiness Opinion

```text
wp_m6_substage_readiness=PASS_FOR_ROUTE_A_IMPLEMENTATION
open_fatal_document_gap=NONE
open_major_document_gap=NONE
required_human_route_decision=NO
next_allowed_action=WP_M6_IMPLEMENTATION_ONLY
```

该记录说明 WP-M6 采用 Route A 并已通过有界证据验收。WP-M7、WP-M8、WP-M9、WP-M10 和 WP-M11 也已在同一证据包中完成逐阶段验收；若后续复审发现 WP-M6 evidence 失效，必须回退到本文定义的 stop conditions。
