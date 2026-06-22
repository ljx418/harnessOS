# HarnessOS V12 User Scenarios And Acceptance

## Required Scenarios

Gemini 生成的页面必须能表达以下五类工作流场景：

### 1. 多 Agent 讨论

- 用户给出一个讨论主题
- 多个 Agent 从不同角色讨论
- Summary Agent 汇总结论
- Quality Agent 检查观点覆盖和证据引用

### 2. 视频分镜创作

- 用户输入一个视频创意
- 系统规划分镜工作流
- 输出 style / storyboard / quality 审查节点

### 3. 文档总结

- 用户要求读取本地文档
- 工作流展示 document read -> summary -> risk -> evidence

### 4. 代码提案

- 用户描述变更目标
- 系统展示 diff proposal、测试建议、review handoff
- 不得暗示自动 commit / push / deploy

### 5. 证据审计

- 用户可以查看 trace、quality、evidence refs
- 可以看出哪些节点已完成、阻断、等待确认

## Required Visible States

页面必须能让审查者看到这些状态：

- API 在线
- API 离线
- API 限流
- 未配置 provider
- 节点 hover
- 节点 selected
- blocked
- awaiting confirmation
- evidence ready
- evidence missing
- invalid edge or denied action hint

## Acceptance Conditions

Gemini 输出的网页原型如果要被认为“可审查”，至少要满足：

1. L1 / L2 信息架构清楚
2. 画布是低代码工作流画布，不是卡片墙
3. 节点、端口、连线完整，不重叠，不断线
4. Inspector 信息可读，不严重截断
5. 底部工作台不是普通聊天框
6. 至少可以感知到 5 个场景能力
7. 页面显式声明 `design_only`
8. 没有 forbidden positive claims

## Not Acceptable

以下情况视为不通过：

- 页面只有聊天框，没有画布
- 左侧导航没有层级逻辑
- 节点无端口或无连线
- 节点 / 文本重叠严重
- Inspector 信息无法阅读
- 把设计图包装成实现证据
- 声称 Xpert 已追平
- 声称完整 Workflow Studio ready
- 声称 production ready

## Expected Review Output

Gemini 最终应给出：

- 生成的 HTML 原型代码
- 自审说明
- remaining gaps
- `PASS / CONDITIONAL_GO / NO_GO`
