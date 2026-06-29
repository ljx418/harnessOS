# PV19 Runtime Workflow Platform Acceptance Gate

用途：定义 PV19 的验收门槛、出门条件和阻断条件。
阅读对象：测试、审计、产品、开发人员。
边界：本文定义验收规则；只有实现和证据包通过后才允许 bounded review 声明。

## 1. Required PASS Gates

| Gate | PASS condition |
| --- | --- |
| G1 文档完整 | PV19 PRD、架构、计划、里程碑、门槛、gap、DTO、runner、audit、drawio 存在。 |
| G2 工作台体验 | 用户可打开真实工作台，看到 canvas、Inspector、版本、运行和 evidence 区域。 |
| G3 编排闭环 | 节点、边、参数、人工节点保存为 WorkflowSpecGraph 并通过 validation。 |
| G4 发布闭环 | WorkflowDiff 经过用户确认后生成 WorkflowVersion，并可 readback。 |
| G5 Runtime 运行 | WorkflowInstance 按发布版本运行，inspect 返回真实状态和 runtime refs。 |
| G6 人工交互 | 人工动作改变后端状态，生成 audit trail，流程继续或安全终止。 |
| G7 Evidence | artifacts、trace、quality、audit、claim-to-evidence 可在工作台审查。 |
| G8 边界安全 | 浏览器 route denylist、redaction、No False Green 全部 PASS。 |
| G9 平台通用性 | 业务样例没有引入业务专用 Core/Gateway/App shell 分支。 |

## 2. User-Visible Exit Conditions

用户在一个浏览器路径内必须能看到：

1. 当前 workspace / project / workflow。
2. 可编辑工作流画布和节点配置。
3. WorkflowDiff 变更摘要。
4. 发布版本号和确认记录。
5. 运行实例进度。
6. 至少一个人工交互卡点及处理结果。
7. 最终产物、trace、quality、audit 和 evidence 摘要。

## 3. Evidence Exit Conditions

证据包必须证明：

- Browser E2E 使用真实页面操作，不只调用 API。
- BFF route log 覆盖所有关键动作。
- DTO snapshot 可追踪 scope、workflow、version、run、human action 和 evidence。
- Runtime report 包含 WorkflowVersion、WorkflowInstance、node status 和 event refs。
- Human interaction report 包含操作者、动作、前后状态和 audit refs。
- Claim matrix 中每条正向声明都有至少一个证据引用。

## 4. Blocking Conditions

任一条件出现即不得出门：

- 根路径仍是主要交付首页且显示空白实例。
- 运行由 UI 模拟或测试 route 假造。
- 发布版本和运行版本无法对应。
- 人工操作不影响后端状态。
- 证据由前端构造而非后端 evidence read model。
- 浏览器绕过 BFF 访问 runtime truth。
- 为业务样例定制平台核心。
- 出现不允许的完成声明。

## 5. Allowed Claim

```text
PV19 complete: runtime-backed workflow platform closed loop ready for bounded review.
```

## 6. Forbidden Interpretations

- 不得声明 HarnessOS production ready。
- 不得声明 Xpert parity complete。
- 不得声明 product-grade frontend complete。
- 不得声明 complete Workflow Studio ready。
- 不得声明 Agent executor ready。
- 不得声明业务样例已经完整产品化。
- 不得把 drawio、截图或介绍文档声明为 runtime evidence。
