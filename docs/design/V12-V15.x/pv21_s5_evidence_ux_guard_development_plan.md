# PV21-S5 Evidence UX Guard Development Plan

用途：定义 PV21-S5 的开发、验收和审计闭环。
阅读对象：开发、测试、产品、审计人员。
边界：本文是子阶段计划，不是实现证据。

## Scope

PV21-S5 完成 evidence summary、browser E2E、截图证据、No False Green、redaction 和 platform generality review。

## Development Tasks

- 后端新增 evidence route，聚合 artifact、trace、quality、approval、claim、redaction refs 和 missing_refs。
- 前端 evidence panel 显示 evidence health、claim matrix、route boundary 和 redaction 状态。
- 新增 browser E2E / CDP acceptance runner 和 HTML 报告。

## Acceptance

- Evidence summary report PASS。
- Browser screenshots 覆盖 home、canvas edit、version/run/evidence。
- Forbidden route scan PASS。
- No False Green、redaction、platform generality scans PASS。

## Audit Opinion

Go. 主要风险是 evidence 缺失却写 PASS。`missing_refs` 必须显式展示，且 aggregate runner 不得把 blocked 当 PASS。

