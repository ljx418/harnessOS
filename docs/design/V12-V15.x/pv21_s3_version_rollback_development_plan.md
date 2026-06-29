# PV21-S3 Diff Version Publish Rollback Development Plan

用途：定义 PV21-S3 的开发、验收和审计闭环。
阅读对象：开发、测试、产品、审计人员。
边界：本文是子阶段计划，不是实现证据。

## Scope

PV21-S3 完成 diff、versions list、publish 和 rollback。运行、human gate 和 evidence 在后续子阶段完成。

## Development Tasks

- 后端新增 diff、versions、publish 和 rollback routes。
- Publish 必须要求 user confirmation。
- Rollback 必须要求 user confirmation，并保留旧 versions、runs 和 evidence。
- Rollback 不得删除历史；若底层 repository 没有 active-version mutation，则使用可审计的 active published version 指针更新或 rollback version record。

## Acceptance

- Version publish report PASS。
- Versions list 包含历史版本和 active published version。
- Rollback report PASS，历史版本和旧 run 数量不减少。
- Agent/source 自动 publish 或 rollback 被拒绝。

## Audit Opinion

Go with caution. rollback 语义是本子阶段最大风险，必须以“不删除历史”和 audit refs 为出门底线。

