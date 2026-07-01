import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import type {
  PV20AgentExecutionActionDTO,
  PV20AgentExecutionEvidenceDTO,
  PV20AgentExecutorStateDTO,
  PV21EvidenceSummaryDTO,
  PV21RunDTO,
  WorkflowPlatformBusinessOutputDTO,
  WorkflowPlatformScenarioProjectionDTO,
} from "../../api/types.js";
import "./v13-editable-studio.css";

const WORKFLOW_ID = "wf-v13-markdown-summary-studio-pilot";
const DIFF_ID = "diff-v13-editable-studio-pilot-001";
const MIN_CANVAS_WIDTH = 940;
const MIN_CANVAS_HEIGHT = 520;
const NODE_WIDTH = 145;
const NODE_HEIGHT = 104;
const NODE_PORT_Y = 47;
const NODE_GRID = 8;
const CANVAS_OFFSET_X = 8;
const CANVAS_OFFSET_Y = 22;
const CANVAS_PADDING = 160;
const EDGE_PORT_GAP = 10;
const EDGE_NODE_GAP = 18;
const VISUAL_NODE_IDS = ["start_goal", "folder_reader", "quality_gate", "evidence_review", "summary_agent", "final_markdown"] as const;
const VISUAL_EDGES: StudioEdge[] = [
  { id: "start-folder", source: "start_goal", target: "folder_reader" },
  { id: "folder-quality", source: "folder_reader", target: "quality_gate" },
  { id: "folder-evidence", source: "folder_reader", target: "evidence_review" },
  { id: "quality-summary", source: "quality_gate", target: "summary_agent" },
  { id: "evidence-summary", source: "evidence_review", target: "summary_agent" },
  { id: "summary-final", source: "summary_agent", target: "final_markdown" },
];

type WorkflowGraphNode = {
  node_id: string;
  label: string;
  node_kind: string;
  status: string;
  position: { x: number; y: number };
  agent_profile_ref?: string;
  capability_ref?: string;
};

type WorkflowGraphEdge = {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
};

type WorkflowSpecGraph = {
  schema_version: string;
  workflow_id: string;
  workspace_id: string;
  project_id: string;
  app_id: string;
  version_ref: string;
  runtime_backed: boolean;
  nodes: WorkflowGraphNode[];
  edges: WorkflowGraphEdge[];
  evidence_refs: string[];
  audit_ref: string;
  created_at: string;
};

type ValidationResult = {
  schema_version: string;
  status: "PASS" | "FAIL";
  errors: Array<{ code: string; message: string }>;
  runtime_backed: boolean;
  audit_ref: string;
};

type WorkflowDiff = {
  schema_version: string;
  proposal_id: string;
  status: string;
  changed_node_refs: string[];
  changed_edge_refs: string[];
  confirmation_boundary: string;
  runtime_backed: boolean;
  publish_or_run_started: boolean;
  graph_validation?: ValidationResult;
};

type NodeInspector = {
  schema_version: string;
  selected_node_ref: string;
  label: string;
  node_kind: string;
  status: string;
  editable_fields: string[];
  blocked_fields: string[];
  agent_profile_ref?: string | null;
  capability_ref?: string | null;
  runtime_backed: boolean;
  audit_ref: string;
};

type StudioNode = {
  id: string;
  label: string;
  nodeKind: string;
  status: string;
  x: number;
  y: number;
  badge: string;
  metaLabel: string;
  metaValue: string;
  evidence: string;
  agentProfileRef?: string;
  capabilityRef?: string;
};

type StudioEdge = {
  id: string;
  source: string;
  target: string;
};

type ConnectionDraft = {
  sourceId: string;
  currentX: number;
  currentY: number;
};

type CanvasViewport = {
  scale: number;
  x: number;
  y: number;
};

type CanvasSize = {
  width: number;
  height: number;
};

type ScenarioId = "roma" | "storyboard" | "codereview" | "docsummary";
type BusinessScenarioId = "document_summary" | "code_review" | "meeting_brief";
type L1RouteId = "workbench" | "agents" | "workflows" | "skills" | "mcp" | "evidence" | "runs" | "settings";
type BottomTab = "timeline" | "trace" | "quality" | "evidence";
type NodeRunState = "idle" | "active" | "completed" | "blocked";
type EdgeVisualState = "idle" | "selected" | "running" | "completed" | "blocked";
type SimulationMode = "idle" | "playing" | "paused" | "blocked";
type ApiState = "online" | "offline" | "rate_limited" | "unconfigured";
type RunState = "idle" | "in_progress" | "blocked" | "failed";
type CapabilityParityStatus = "pending" | "PASS" | "FAIL";
type CapabilityParityItem = {
  id: string;
  label: string;
  route_family: "/bff/v13" | "/bff/pv21" | "/bff/pv20";
  target_surface: string;
  status: CapabilityParityStatus;
  evidence_ref: string;
};
type CapabilityParityReport = {
  schema_version: "workflow_platform.capability_parity_report.v1";
  status: CapabilityParityStatus;
  baseline_homepage: "V13EditableStudio";
  deprecated_homepage: "WorkflowPlatformMainEntry";
  items: CapabilityParityItem[];
  no_false_green: string[];
  updated_at: string;
};

type ScenarioNode = {
  title: string;
  type: string;
  metaLabel: string;
  metaValue: string;
};

type ScenarioInspector = {
  name: string;
  role: string;
  goal: string;
  digest: string;
  tools: string;
  skills: string;
  mcp: string;
  quality: string;
  evidence: string;
};

type ScenarioData = {
  name: string;
  agentsCount: string;
  skillsCount: string;
  mcpCount: string;
  evidenceCount: string;
  layout: Array<{ x: number; y: number }>;
  nodes: ScenarioNode[];
  inspector: ScenarioInspector[];
  timeline: Array<{ time: string; msg: string; state: string }>;
};

type ChatMessage = {
  id: string;
  role: string;
  body: string;
  tone: "assistant" | "user" | "system";
};

const fallbackGraph: WorkflowSpecGraph = {
  schema_version: "v13.workflow_spec_graph.v1",
  workflow_id: WORKFLOW_ID,
  workspace_id: "ws-v12-technical-content-real",
  project_id: "proj-v12-local-knowledge-real",
  app_id: "app-v12-markdown-workflow-real",
  version_ref: "workflow-version:v13-local-fallback",
  runtime_backed: false,
  nodes: [
    { node_id: "start_goal", label: "目标输入", node_kind: "start", status: "configured", position: { x: 40, y: 180 } },
    { node_id: "folder_reader", label: "读取 Markdown 文件夹", node_kind: "tool", status: "configured", capability_ref: "tool:folder.readonly_scan", position: { x: 205, y: 180 } },
    { node_id: "quality_gate", label: "质量检查", node_kind: "quality_gate", status: "configured", capability_ref: "tool:quality.review", position: { x: 385, y: 90 } },
    { node_id: "evidence_review", label: "证据审查", node_kind: "evidence", status: "configured", position: { x: 385, y: 270 } },
    { node_id: "summary_agent", label: "总结 Agent", node_kind: "station", status: "configured", agent_profile_ref: "agent-v12-quality-reviewer-real", position: { x: 565, y: 180 } },
    { node_id: "final_markdown", label: "输出 Markdown 总结", node_kind: "end", status: "configured", position: { x: 725, y: 180 } },
  ],
  edges: VISUAL_EDGES.map((edge) => ({
    edge_id: edge.id,
    source_node_id: edge.source,
    target_node_id: edge.target,
  })),
  evidence_refs: ["evidence://v13/light-studio/fallback"],
  audit_ref: "audit://v13/light-studio/fallback",
  created_at: "2026-06-24T00:00:00Z",
};

const scenarioData: Record<ScenarioId, ScenarioData> = {
  roma: {
    name: "罗马广场讨论工作流",
    agentsCount: "6",
    skillsCount: "12",
    mcpCount: "4",
    evidenceCount: "18",
    layout: [
      { x: 38, y: 180 },
      { x: 205, y: 180 },
      { x: 385, y: 90 },
      { x: 385, y: 270 },
      { x: 565, y: 180 },
      { x: 725, y: 180 },
    ],
    nodes: [
      { title: "对话输入", type: "触发", metaLabel: "事件", metaValue: "topic" },
      { title: "规划 Agent", type: "智能", metaLabel: "角色", metaValue: "v13-op-plan" },
      { title: "讨论 Agent A", type: "智能", metaLabel: "立场", metaValue: "观点A" },
      { title: "讨论 Agent B", type: "智能", metaLabel: "立场", metaValue: "观点B" },
      { title: "总结 Agent", type: "总结", metaLabel: "角色", metaValue: "storyboard-ev" },
      { title: "质检 Agent", type: "审计", metaLabel: "状态", metaValue: "review-ref" },
    ],
    inspector: [
      { name: "对话输入", role: "事件监听器", goal: "监听来自工作空间对话框的特定 Prompt 激活。", digest: "识别出针对罗马广场辩题的触发命令。", tools: "workspace.read, regex.parser", skills: "intent-analysis", mcp: "mcp://system-event-bus", quality: "输入参数合规，内容不为空。", evidence: "None" },
      { name: "规划 Agent", role: "辩题规划师", goal: "基于目标辩题规划辩证探讨角度。", digest: "分派批判派和相对派作为两端推演工作站。", tools: "planner.optimizer", skills: "workflow-scheduling", mcp: "mcp://planner-executor", quality: "WorkflowDraft 包含双向边与证据锚点。", evidence: "spec-draft-v13.json" },
      { name: "讨论 Agent A", role: "批判主义代理人", goal: "代表严格理性立场，对断言提出否定与追问。", digest: "形成批判节点报告，并保留关键反思证据。", tools: "rational.verifier", skills: "dialectic-scrutiny", mcp: "mcp://critic-broker", quality: "否定论点必须引用至少 1 个证据。", evidence: "socrates-critique.json" },
      { name: "讨论 Agent B", role: "相对主义代理人", goal: "代表经验相对立场，为主观体验提供防御。", digest: "强调个体差异与感知限度，作为总结中心输入。", tools: "phenomenon.indexer", skills: "subjective-modeling", mcp: "mcp://experience-broker", quality: "必须保留不可消弭的分歧点。", evidence: "protagoras-defense.json" },
      { name: "总结 Agent", role: "观点总结者", goal: "提炼共识、保留分歧，生成最终工作区对话报告。", digest: "整合批判性反思与相对主义辩护，生成分治框架。", tools: "markdown.summary, consensus.synthesizer", skills: "insight-extraction", mcp: "mcp://consensus-broker-server", quality: "保留完整双方分歧，断言必须锚定 evidence refs。", evidence: "storyboard-evidence.json" },
      { name: "质检 Agent", role: "审计守卫", goal: "校验最终总结文本中所有观点引用的真实性。", digest: "当前因一个存证单据缺失处于待确认阻塞状态。", tools: "compliance.tester", skills: "forensic-auditing", mcp: "mcp://chain-of-trust", quality: "100% 交叉溯源。", evidence: "review-ref.json" },
    ],
    timeline: [
      { time: "15:38:12", msg: "【触发】事件捕获器：/discuss 指令激活", state: "成功" },
      { time: "15:38:15", msg: "【规划】编排规划师下发 2 组探索 Spec 规约", state: "完成" },
      { time: "15:38:36", msg: "【智能体 A】生成批判立场存证 receipt-934a", state: "完成" },
      { time: "15:38:41", msg: "【智能体 B】提交相对辩词存证 receipt-122c", state: "完成" },
      { time: "15:39:02", msg: "【总结】观点融合中心合成共识与分歧大纲", state: "处理中" },
    ],
  },
  storyboard: {
    name: "视频分镜创作工作流",
    agentsCount: "6",
    skillsCount: "16",
    mcpCount: "5",
    evidenceCount: "22",
    layout: [
      { x: 38, y: 90 },
      { x: 190, y: 180 },
      { x: 345, y: 90 },
      { x: 505, y: 180 },
      { x: 660, y: 90 },
      { x: 725, y: 270 },
    ],
    nodes: [
      { title: "剧本输入", type: "触发", metaLabel: "脚本", metaValue: "script" },
      { title: "导演助手", type: "智能", metaLabel: "规划", metaValue: "v13-sb-plan" },
      { title: "艺术总监", type: "智能", metaLabel: "色彩", metaValue: "palette" },
      { title: "摄影指导", type: "智能", metaLabel: "机位", metaValue: "lens-seq" },
      { title: "合成 Agent", type: "合成", metaLabel: "交付", metaValue: "storyboard-json" },
      { title: "版权守卫", type: "审计", metaLabel: "卡口", metaValue: "ip-audit" },
    ],
    inspector: [
      { name: "剧本输入", role: "创意输入端", goal: "解析文本小说，生成底层分镜描述单元。", digest: "提取赛博都市街角与阴雨关键词。", tools: "nlp.parser", skills: "creative-parsing", mcp: "mcp://creative-bus", quality: "输入创意分词满足脚本最低标准。", evidence: "None" },
      { name: "导演助手", role: "分镜规划师", goal: "生成包含动作和场景的分镜蓝图。", digest: "生成 12 帧故事板草案骨架。", tools: "blueprint.generator", skills: "directing-assist", mcp: "mcp://directing-server", quality: "输出符合 StoryboardSpec。", evidence: "v13-sb-plan.json" },
      { name: "艺术总监", role: "色彩艺术顾问", goal: "计算画幅色彩基调、冷暖度与光照分布。", digest: "计算出蓝灰色雨夜基底。", tools: "palette.generator", skills: "color-grading", mcp: "mcp://diffusion-service", quality: "色轮对比度满足电影美学标准。", evidence: "palette-v13.json" },
      { name: "摄影指导", role: "镜头轨迹推演", goal: "计算机位平摇、推拉轨迹与焦距景深。", digest: "生成广角转中景的平滑镜头轨迹参数。", tools: "lens.calculator", skills: "camera-movement", mcp: "mcp://unreal-engine-mcp", quality: "轨迹与对焦符合物理镜头组标准。", evidence: "lens-sequence.json" },
      { name: "合成 Agent", role: "全镜合并中心", goal: "合成最终故事板预览与 JSON 交付物。", digest: "合成 12 帧故事板草案及引用参数。", tools: "canvas.stitcher", skills: "visual-synthesis", mcp: "mcp://image-processor", quality: "帧关联完整，无坐标溢出。", evidence: "storyboard-json.json" },
      { name: "版权守卫", role: "创意合规安全闸", goal: "审查人物、背景及元素是否涉嫌侵权。", digest: "检测到相似画面，要求人工调整确认。", tools: "trademark.scanner", skills: "ip-compliance", mcp: "mcp://ip-database", quality: "无版权红线侵权。", evidence: "ip-audit.json" },
    ],
    timeline: [
      { time: "11:12:01", msg: "【剧本】创意剧本解析完毕", state: "成功" },
      { time: "11:12:05", msg: "【导演】下发 12 帧视觉分镜场景 Spec", state: "完成" },
      { time: "11:12:20", msg: "【艺术】电影级配色表生成", state: "完成" },
      { time: "11:12:35", msg: "【摄影】机位及焦距坐标测算就绪", state: "完成" },
      { time: "11:12:50", msg: "【合成】分镜合成完毕，等待版权质检", state: "完成" },
    ],
  },
  codereview: {
    name: "代码审查工作流",
    agentsCount: "6",
    skillsCount: "14",
    mcpCount: "4",
    evidenceCount: "15",
    layout: [
      { x: 38, y: 180 },
      { x: 205, y: 180 },
      { x: 385, y: 70 },
      { x: 385, y: 290 },
      { x: 565, y: 180 },
      { x: 725, y: 180 },
    ],
    nodes: [
      { title: "Git Hook", type: "触发", metaLabel: "事件", metaValue: "diff" },
      { title: "编排 Planner", type: "智能", metaLabel: "调度", metaValue: "v13-cr-spec" },
      { title: "代码规范", type: "智能", metaLabel: "静检", metaValue: "lint-report" },
      { title: "安全审计", type: "智能", metaLabel: "SAST", metaValue: "sec-vulner" },
      { title: "合并整合", type: "合并", metaLabel: "报告", metaValue: "cr-summary" },
      { title: "安全合规", type: "审计", metaLabel: "卡口", metaValue: "auth-review" },
    ],
    inspector: [
      { name: "Git Hook", role: "事件监听器", goal: "捕获 Git 代码推送并触发 diff 分解事件。", digest: "检测到 feature-v13-light 提交变动。", tools: "github.webhook", skills: "event-broker", mcp: "mcp://git-provider", quality: "Diff 格式正确且无二进制文件。", evidence: "None" },
      { name: "编排 Planner", role: "审查编排官", goal: "基于规范与变更领域分派审查。", digest: "识别出前端 CSS 与 JS 交互模块变动。", tools: "eslint.ast-parser", skills: "clean-code-audit", mcp: "mcp://ast-broker", quality: "符合项目静态检查准入。", evidence: "lint-report.json" },
      { name: "代码规范", role: "代码规范卫士", goal: "扫描变量冗余与规范错失。", digest: "发现样式和事件监听风险项。", tools: "eslint.ast-parser", skills: "clean-code-audit", mcp: "mcp://ast-broker", quality: "无关键代码规范阻塞。", evidence: "lint-report.json" },
      { name: "安全审计", role: "安全合规官", goal: "扫描凭据和 XSS 注入风险。", digest: "未发现硬编码凭据，存在一处 DOM 写入警示。", tools: "semgrep.engine", skills: "vulnerability-detection", mcp: "mcp://security-feed", quality: "无 Critical 或 High 风险。", evidence: "sec-vulner.json" },
      { name: "合并整合", role: "差异合并报告者", goal: "汇聚规范与安全审计报告。", digest: "输出 3 条改进建议，附带 lint-ref 和 sec-ref。", tools: "diff.synthesizer", skills: "report-consolidation", mcp: "mcp://merge-service", quality: "总结具备事实根据。", evidence: "cr-summary.json" },
      { name: "安全合规", role: "安全门槛决策者", goal: "核对敏感模块改动是否符合发布规范。", digest: "检测到外部路径变更，等待团队审查批准。", tools: "compliance.gatekeeper", skills: "policy-enforcement", mcp: "mcp://corporate-policies", quality: "符合安全合规准入。", evidence: "auth-review.json" },
    ],
    timeline: [
      { time: "09:30:10", msg: "【捕获】Git PR Webhook diff 解析完成", state: "成功" },
      { time: "09:30:12", msg: "【规划】CI 调度中心完成 AST 与 SAST 拓扑", state: "完成" },
      { time: "09:30:25", msg: "【静态分析】发现 2 处语法规则警告", state: "完成" },
      { time: "09:30:31", msg: "【SAST】审计结束，发现隔离警示", state: "完成" },
      { time: "09:30:45", msg: "【合并】差异报告生成，等待人工合规授权", state: "完成" },
    ],
  },
  docsummary: {
    name: "文档总结工作流",
    agentsCount: "6",
    skillsCount: "11",
    mcpCount: "3",
    evidenceCount: "12",
    layout: [
      { x: 38, y: 180 },
      { x: 175, y: 180 },
      { x: 315, y: 180 },
      { x: 455, y: 180 },
      { x: 600, y: 180 },
      { x: 735, y: 180 },
    ],
    nodes: [
      { title: "文档上传", type: "触发", metaLabel: "输入", metaValue: "raw-pdf" },
      { title: "结构解析", type: "智能", metaLabel: "切片", metaValue: "v13-doc-spec" },
      { title: "事实抽取", type: "智能", metaLabel: "事实", metaValue: "fact-bank" },
      { title: "反思查漏", type: "智能", metaLabel: "核验", metaValue: "hallu-check" },
      { title: "精简撰写", type: "撰写", metaLabel: "摘要", metaValue: "executive" },
      { title: "信源追溯", type: "就绪", metaLabel: "追溯", metaValue: "evidence-ref" },
    ],
    inspector: [
      { name: "文档上传", role: "文件接口端", goal: "加载 PDF 字符并转换为带页面标定的文本树。", digest: "成功载入审查报告，共 14 页。", tools: "pdf.ocr-loader", skills: "document-ingestion", mcp: "mcp://filesystem-mcp", quality: "文档包含 OCR 字符图层。", evidence: "None" },
      { name: "结构解析", role: "结构化切片师", goal: "切分节、目、页，作为后续总结段落。", digest: "提取核心章节与细分段落。", tools: "doc-parser.tree", skills: "layout-analysis", mcp: "mcp://layout-server", quality: "格式标准度 100%。", evidence: "v13-doc-spec.json" },
      { name: "事实抽取", role: "事实信息抽取器", goal: "抽取明确事实、哈希、模型供应商。", digest: "抽取 24 处关键断言。", tools: "fact.extractor", skills: "entity-extraction", mcp: "mcp://fact-store", quality: "提取结果带页码锚定。", evidence: "fact-bank.json" },
      { name: "反思查漏", role: "事实核验警卫", goal: "核验事实中是否包含上下文误解。", digest: "核实关于 browser 证据边界的结论。", tools: "cross.verifier", skills: "logic-checking", mcp: "mcp://verification-agent", quality: "排除幻觉率达 100%。", evidence: "hallu-check.json" },
      { name: "精简撰写", role: "资深文案编辑", goal: "合并事实为高信息密度 summary。", digest: "报告编写完成，突出边界警示。", tools: "editor.writer", skills: "executive-synthesis", mcp: "mcp://scribe-broker", quality: "摘要不夹杂未存证断言。", evidence: "executive-summary.json" },
      { name: "信源追溯", role: "信源守卫官", goal: "提供百分百交叉溯源。", digest: "所有段落与要点均可双向追踪。", tools: "audit.tracker", skills: "source-tracing", mcp: "mcp://compliance-blockchain", quality: "追溯关联率 100%。", evidence: "evidence-ref.json" },
    ],
    timeline: [
      { time: "14:20:02", msg: "【读取】14 页规范文档输入就绪", state: "成功" },
      { time: "14:20:05", msg: "【切片】结构切片师完成段落位置标记", state: "完成" },
      { time: "14:20:21", msg: "【提取】事实性特征信息提取完毕", state: "完成" },
      { time: "14:20:30", msg: "【核验】防幻觉纠偏机制比对通过", state: "完成" },
      { time: "14:20:44", msg: "【撰写】摘要及信源存证单据链输出完毕", state: "完成" },
    ],
  },
};

const l1Routes: Array<{ id: L1RouteId; title: string; subtitle: string }> = [
  { id: "workbench", title: "工作流平台", subtitle: "项目级工作流编排与上下文资源" },
  { id: "agents", title: "智能体目录", subtitle: "当前项目活跃 Agent / Station 目录表" },
  { id: "workflows", title: "工作流配置", subtitle: "WorkflowSpec 拓扑定义与草稿配置" },
  { id: "skills", title: "技能注册表", subtitle: "提示词微模型与动作策略" },
  { id: "mcp", title: "MCP 目录", subtitle: "外部工具、数据库和上下文服务器挂载" },
  { id: "evidence", title: "区块链存证", subtitle: "双向可信交叉信源链审计中心" },
  { id: "runs", title: "审计 Run 实例", subtitle: "实时日志抓取、调试与阻断详情" },
  { id: "settings", title: "审计规约设置", subtitle: "隔离期安全合规决策参数" },
];

const tabs: Array<{ id: BottomTab; label: string }> = [
  { id: "timeline", label: "时间线进度" },
  { id: "trace", label: "Trace 追溯日志" },
  { id: "quality", label: "合规质量规则" },
  { id: "evidence", label: "审计存证详情" },
];

const initialScenarioNodes: StudioNode[] = buildStudioNodes(fallbackGraph.nodes, "roma");
const initialScenarioEdges: StudioEdge[] = VISUAL_EDGES;
const initialNodeRunStates: NodeRunState[] = ["idle", "idle", "idle", "idle", "idle", "idle"];
const initialCapabilityParityReport: CapabilityParityReport = {
  schema_version: "workflow_platform.capability_parity_report.v1",
  status: "pending",
  baseline_homepage: "V13EditableStudio",
  deprecated_homepage: "WorkflowPlatformMainEntry",
  updated_at: new Date(0).toISOString(),
  no_false_green: ["not_production_ready", "not_product_grade_frontend_complete", "not_agent_executor_ready"],
  items: [
    {
      id: "wp-m1-homepage-route",
      label: "首页入口使用 PV13 Light Studio",
      route_family: "/bff/v13",
      target_surface: "root empty route and ?studio=workflow-platform",
      status: "pending",
      evidence_ref: "browser:root-route:v13-editable-studio",
    },
    {
      id: "wp-m3-pv21-runtime-loop",
      label: "PV21 保存、校验、发布、运行、人工审查、证据回读",
      route_family: "/bff/pv21",
      target_surface: "workflow runtime scenario panel",
      status: "pending",
      evidence_ref: "route:/bff/pv21/*",
    },
    {
      id: "wp-m4-pv20-executor-loop",
      label: "PV20 受治理 Skill / Tool / MCP 执行证据",
      route_family: "/bff/pv20",
      target_surface: "governed executor panel",
      status: "pending",
      evidence_ref: "route:/bff/pv20/*",
    },
  ],
};

export function V13EditableStudio() {
  const [baseGraph, setBaseGraph] = useState<WorkflowSpecGraph>(fallbackGraph);
  const [nodes, setNodes] = useState<StudioNode[]>(initialScenarioNodes);
  const [edges, setEdges] = useState<StudioEdge[]>(initialScenarioEdges);
  const [selectedNodeId, setSelectedNodeId] = useState("summary_agent");
  const [inspector, setInspector] = useState<NodeInspector | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [diff, setDiff] = useState<WorkflowDiff | null>(null);
  const [handoffRef, setHandoffRef] = useState("");
  const [loadingLabel, setLoadingLabel] = useState("加载 V13 Light Studio 数据");
  const [actionLog, setActionLog] = useState<string[]>(["页面初始化"]);
  const [activeTab, setActiveTab] = useState<BottomTab>("timeline");
  const [viewport, setViewport] = useState<CanvasViewport>({ scale: 1, x: CANVAS_OFFSET_X, y: CANVAS_OFFSET_Y });
  const [workspaceSize, setWorkspaceSize] = useState<CanvasSize>({ width: MIN_CANVAS_WIDTH, height: MIN_CANVAS_HEIGHT });
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [activeL1Route, setActiveL1Route] = useState<L1RouteId>("workbench");
  const [currentScenario, setCurrentScenario] = useState<ScenarioId>("roma");
  const [nodeRunStates, setNodeRunStates] = useState<NodeRunState[]>(initialNodeRunStates);
  const [simulationMode, setSimulationMode] = useState<SimulationMode>("idle");
  const [simulationStep, setSimulationStep] = useState(0);
  const [apiState, setApiState] = useState<ApiState>("online");
  const [runState, setRunState] = useState<RunState>("idle");
  const [stateMenuOpen, setStateMenuOpen] = useState(false);
  const [chatText, setChatText] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "initial-assistant",
      role: "Summary Agent (总结者 ID=5)",
      body: "当前处于 design_only 水印隔离防护期。WorkflowDiff 已准备交接审查，发布和运行仍被后续阶段阻断。",
      tone: "assistant",
    },
  ]);
  const [traceLines, setTraceLines] = useState<string[]>([
    "[TRACE] Station summary_agent entered handoff review.",
    "[INFO] Browser boundary: /bff/v13/* only.",
    "[INFO] publish_or_run_started=false.",
    "[INFO] evidence refs committed for design review.",
  ]);
  const [toast, setToast] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [connectionDraft, setConnectionDraft] = useState<ConnectionDraft | null>(null);
  const [runtimeReviewStatus, setRuntimeReviewStatus] = useState("未运行");
  const [executorReviewStatus, setExecutorReviewStatus] = useState("未运行");
  const [capabilityParityReport, setCapabilityParityReport] = useState<CapabilityParityReport>(initialCapabilityParityReport);
  const [pv21RunId, setPv21RunId] = useState("");
  const [pv20RunId, setPv20RunId] = useState("");
  const [scenarioProjection, setScenarioProjection] = useState<WorkflowPlatformScenarioProjectionDTO | null>(null);
  const [businessOutputs, setBusinessOutputs] = useState<Partial<Record<BusinessScenarioId, WorkflowPlatformBusinessOutputDTO>>>({});
  const [businessProjectionStatus, setBusinessProjectionStatus] = useState("加载 WP-M5A DTO 投影");

  const canvasRef = useRef<HTMLDivElement | null>(null);
  const canvasWorldRef = useRef<HTMLDivElement | null>(null);
  const viewportRef = useRef<CanvasViewport>({ scale: 1, x: CANVAS_OFFSET_X, y: CANVAS_OFFSET_Y });
  const simulationTimer = useRef<number | null>(null);
  const dragState = useRef<{ nodeId: string; startX: number; startY: number; nodeX: number; nodeY: number; latestX: number; latestY: number } | null>(null);

  const currentGraph = useMemo(() => toWorkflowGraph(baseGraph, nodes, edges), [baseGraph, nodes, edges]);
  const worldSize = useMemo(() => computeCanvasWorldSize(nodes, workspaceSize, viewport.scale), [nodes, workspaceSize, viewport.scale]);
  const selectedNode = nodes.find((node) => node.id === selectedNodeId) || nodes[4] || nodes[0];
  const selectedIndex = Math.max(0, nodes.findIndex((node) => node.id === selectedNodeId));
  const scenario = scenarioData[currentScenario];
  const currentBusinessScenarioId = scenarioToBusinessScenarioId(currentScenario);
  const currentBusinessOutput = currentBusinessScenarioId ? businessOutputs[currentBusinessScenarioId] : undefined;
  const currentScenarioProjection = currentBusinessScenarioId
    ? scenarioProjection?.scenarios.find((item) => item.scenario_id === currentBusinessScenarioId)
    : undefined;
  const localInspector = scenario.inspector[selectedIndex] || scenario.inspector[4];
  const activeRoute = l1Routes.find((route) => route.id === activeL1Route) || l1Routes[0];
  const simulationStatusLabel = simulationMode === "playing" ? "仿真播放中" : simulationMode === "paused" ? "仿真暂停" : simulationMode === "blocked" ? "等待人工确认" : "空闲";

  const recordAction = useCallback((label: string) => {
    setActionLog((current) => [label, ...current].slice(0, 50));
  }, []);

  const updateCapabilityParity = useCallback((itemId: string, status: CapabilityParityStatus, evidenceRef: string) => {
    setCapabilityParityReport((current) => {
      const items = current.items.map((item) => (item.id === itemId ? { ...item, status, evidence_ref: evidenceRef } : item));
      const reportStatus = items.every((item) => item.status === "PASS") ? "PASS" : items.some((item) => item.status === "FAIL") ? "FAIL" : "pending";
      return { ...current, items, status: reportStatus, updated_at: new Date().toISOString() };
    });
  }, []);

  const showToast = useCallback((message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 3000);
  }, []);

  const validateGraph = useCallback(async (graph: WorkflowSpecGraph) => {
    const response = await fetch(`/bff/v13/workflows/${WORKFLOW_ID}/graph/validate`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ graph }),
    });
    const result = (await response.json()) as ValidationResult;
    setValidation(result);
    return result;
  }, []);

  const requestDiff = useCallback(
    async (graph: WorkflowSpecGraph, label: string) => {
      setLoadingLabel(label);
      await validateGraph(graph);
      const response = await fetch(`/bff/v13/workflows/${WORKFLOW_ID}/diff`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ graph }),
      });
      const result = (await response.json()) as WorkflowDiff;
      setDiff(result);
      setLoadingLabel("");
      return result;
    },
    [validateGraph],
  );

  const fetchInspector = useCallback(
    async (nodeId: string) => {
      const response = await fetch(`/bff/v13/studio/node-inspector/${nodeId}`);
      const result = (await response.json()) as NodeInspector;
      setInspector(result);
      return result;
    },
    [],
  );

  function commitGraph(nextNodes: StudioNode[], nextEdges: StudioEdge[], label: string) {
    void requestDiff(toWorkflowGraph(baseGraph, nextNodes, nextEdges), label);
  }

  useEffect(() => {
    let cancelled = false;
    async function loadGraph() {
      try {
        await fetch("/bff/v13/system/health");
        const response = await fetch(`/bff/v13/workflows/${WORKFLOW_ID}/graph`);
        const graph = (await response.json()) as WorkflowSpecGraph;
        if (cancelled) return;
        const studioNodes = buildStudioNodes(graph.nodes, "roma");
        const studioEdges = normalizeStudioEdges(graph.edges, studioNodes);
        setBaseGraph(graph);
        setNodes(studioNodes);
        setEdges(studioEdges);
        setSelectedNodeId("summary_agent");
        await fetchInspector("summary_agent");
        await requestDiff(toWorkflowGraph(graph, studioNodes, studioEdges), "生成初始 WorkflowDiff");
      } catch {
        if (cancelled) return;
        setBaseGraph(fallbackGraph);
        setNodes(initialScenarioNodes);
        setEdges(initialScenarioEdges);
        setValidation({
          schema_version: "v13.workflow_graph_validation_result.v1",
          status: "FAIL",
          errors: [{ code: "BFF_LOAD_FAILED", message: "BFF 数据加载失败，已显示本地降级图" }],
          runtime_backed: false,
          audit_ref: "audit://v13/studio-pilot/load-failed",
        });
      } finally {
        if (!cancelled) setLoadingLabel("");
      }
    }
    void loadGraph();
    return () => {
      cancelled = true;
    };
  }, [fetchInspector, requestDiff]);

  useEffect(() => {
    let cancelled = false;
    async function loadBusinessProjection() {
      try {
        const projection = await workflowConsoleClient.getWorkflowPlatformScenarioProjection();
        const outputs = await Promise.all(
          projection.scenarios.map(async (item) => [item.scenario_id, await workflowConsoleClient.getWorkflowPlatformBusinessOutput(item.scenario_id)] as const),
        );
        if (cancelled) return;
        setScenarioProjection(projection);
        setBusinessOutputs(Object.fromEntries(outputs) as Partial<Record<BusinessScenarioId, WorkflowPlatformBusinessOutputDTO>>);
        setBusinessProjectionStatus("DTO/evidence projection loaded");
        setTraceLines((current) => ["[WP-M5A] scenario projection loaded from /bff/workflow-platform/scenarios.", ...current].slice(0, 16));
        recordAction("WP-M5A 业务场景投影已由 BFF DTO 加载");
      } catch (error) {
        if (cancelled) return;
        const message = errorMessage(error);
        setBusinessProjectionStatus(`fallback/design reference: ${message}`);
        setTraceLines((current) => [`[WP-M5A] projection fallback active: ${message}`, ...current].slice(0, 16));
        recordAction(`WP-M5A 业务投影加载失败，使用 fallback：${message}`);
      }
    }
    void loadBusinessProjection();
    return () => {
      cancelled = true;
    };
  }, [recordAction]);

  useEffect(() => {
    viewportRef.current = viewport;
  }, [viewport]);

  useEffect(() => {
    const workspace = canvasRef.current;
    if (!workspace) return;
    const syncWorkspaceSize = () => {
      const rect = workspace.getBoundingClientRect();
      setWorkspaceSize({ width: Math.max(1, rect.width), height: Math.max(1, rect.height) });
    };
    syncWorkspaceSize();
    const observer = new ResizeObserver(syncWorkspaceSize);
    observer.observe(workspace);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && connectionDraft) {
        event.preventDefault();
        cancelFreeConnection("自由连线取消：Esc");
        return;
      }
      const target = event.target as HTMLElement | null;
      if (target && ["INPUT", "TEXTAREA"].includes(target.tagName)) return;
      if (event.key === "=" || event.key === "+") {
        event.preventDefault();
        adjustZoom(viewportRef.current.scale + 0.1);
      } else if (event.key === "-" || event.key === "_") {
        event.preventDefault();
        adjustZoom(viewportRef.current.scale - 0.1);
      } else if (event.key === "0") {
        event.preventDefault();
        adjustZoom(1);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [connectionDraft]);

  useEffect(() => {
    if (simulationMode !== "playing") return;
    if (simulationStep >= 6) {
      blockSimulationAtGate();
      return;
    }
    simulationTimer.current = window.setTimeout(() => advanceSimulationStep(), 1800);
    return () => {
      if (simulationTimer.current) window.clearTimeout(simulationTimer.current);
    };
  }, [simulationMode, simulationStep]);

  function selectNode(nodeId: string, shouldOpenInspector = true) {
    setSelectedNodeId(nodeId);
    const node = nodes.find((entry) => entry.id === nodeId);
    recordAction(`选中节点：${node?.label || nodeId}`);
    if (shouldOpenInspector) setRightCollapsed(false);
    void fetchInspector(nodeId);
  }

  function switchL1Route(routeId: L1RouteId) {
    setActiveL1Route(routeId);
    setLeftCollapsed(false);
    recordAction(`L1 路由切换：${routeId}`);
    showToast(`已切换至一级业务域：${l1Routes.find((route) => route.id === routeId)?.title || routeId}`);
  }

  function switchScenario(nextScenario: ScenarioId) {
    const nextNodes = applyScenarioToNodes(nodes, nextScenario);
    setCurrentScenario(nextScenario);
    setNodes(nextNodes);
    setEdges(VISUAL_EDGES);
    resetSimulationStateOnly();
    setSelectedNodeId(nextNodes[4]?.id || "summary_agent");
    const source = scenarioToBusinessScenarioId(nextScenario) ? "DTO-backed business projection with visual fallback" : "optional visual matrix / future scenario";
    setTraceLines((current) => [`[INFO] scenario switched to ${nextScenario}; ${source}.`, ...current].slice(0, 12));
    recordAction(`场景转换：${scenarioData[nextScenario].name}`);
    showToast(`场景转换，拓扑配置已重组：${scenarioData[nextScenario].name}`);
    void fetchInspector(nextNodes[4]?.id || "summary_agent");
    commitGraph(nextNodes, VISUAL_EDGES, "校验场景拓扑");
  }

  function addQualityNode() {
    if (nodes.some((node) => node.id === "manual_quality_review")) {
      recordAction("质量节点已存在");
      void requestDiff(currentGraph, "刷新 WorkflowDiff");
      return;
    }
    const nextNodes = [
      ...nodes,
      {
        id: "manual_quality_review",
        label: "质量复核",
        nodeKind: "quality_gate",
        status: "draft",
        x: 725,
        y: 340,
        badge: "质检",
        metaLabel: "工具",
        metaValue: "quality.review",
        evidence: "manual-quality",
        capabilityRef: "tool:quality.review",
      },
    ];
    setNodes(nextNodes);
    recordAction("添加节点：人工质量复核");
    showToast("已添加 proposal-only 质量复核节点");
    commitGraph(nextNodes, edges, "校验新增节点");
  }

  function connectEvidenceNode() {
    if (!nodes.some((node) => node.id === "manual_quality_review")) {
      recordAction("连接节点被阻断：缺少人工质量复核节点");
      showToast("请先添加质量节点，再连接复核路径");
      return;
    }
    if (!nodes.some((node) => node.id === selectedNodeId)) {
      recordAction("连接节点被阻断：目标节点不存在");
      showToast("请选择一个有效目标节点后再连接");
      return;
    }
    const exists = edges.some((edge) => edge.id === "manual-quality-merge");
    const nextEdges = exists
      ? edges
      : [...edges, { id: "manual-quality-merge", source: "manual_quality_review", target: selectedNodeId || "summary_agent" }];
    setEdges(nextEdges);
    recordAction("连接节点：人工质量复核 -> 审查汇合");
    showToast("已连接复核路径，仍需 WorkflowDiff 人工确认");
    commitGraph(nodes, nextEdges, "校验新增连接");
  }

  function moveSelectedNode() {
    const nextNodes = nodes.map((node) => (node.id === selectedNodeId ? { ...node, ...clampNodePosition(node.x + 24, node.y + 16, worldSize) } : node));
    setNodes(nextNodes);
    recordAction(`移动节点：${selectedNodeId}`);
    commitGraph(nextNodes, edges, "校验节点位置");
  }

  function configureSelectedNode() {
    const nextNodes = nodes.map((node) =>
      node.id === selectedNodeId ? { ...node, label: `${node.label.replace(" · 已复核", "")} · 已复核`, status: "reviewed" } : node,
    );
    setNodes(nextNodes);
    recordAction(`配置节点：${selectedNodeId}`);
    showToast("已生成节点配置草案，等待人工审查");
    commitGraph(nextNodes, edges, "校验节点配置");
  }

  async function reviseDiff() {
    const response = await fetch(`/bff/v13/workflow-diff/${DIFF_ID}/revise`, { method: "POST" });
    const result = await response.json();
    recordAction(`修订提案：${result.decision}`);
    showToast("WorkflowDiff 已进入 revise_requested 状态");
  }

  async function rejectDiff() {
    const response = await fetch(`/bff/v13/workflow-diff/${DIFF_ID}/reject`, { method: "POST" });
    const result = await response.json();
    recordAction(`拒绝提案：${result.decision}`);
    showToast("WorkflowDiff 已被拒绝，未发布也未运行");
  }

  async function confirmHandoff() {
    const response = await fetch(`/bff/v13/workflow-diff/${DIFF_ID}/confirm-publish-handoff`, { method: "POST" });
    const result = await response.json();
    setHandoffRef(result.handoff_ref);
    setModalOpen(false);
    setNodeRunStates((current) => current.map((state, index) => (index === 5 ? "completed" : state)));
    recordAction(`确认交接：${result.handoff_state}`);
    showToast("已模拟签署交接确认；未启动发布或运行");
  }

  async function runRuntimeScenarioLoop() {
    setRuntimeReviewStatus("运行中");
    recordAction("运行三场景：开始 PV21 能力覆盖验收");
    try {
      const studio = await workflowConsoleClient.getPV21StudioState();
      const workflowId = studio.workflow.workflow_template_id;
      const graph = await workflowConsoleClient.getPV21WorkflowGraph(workflowId);
      const saved = await workflowConsoleClient.savePV21WorkflowGraph(workflowId, graph);
      const validation = await workflowConsoleClient.validatePV21WorkflowGraph(workflowId);
      const diffResult = await workflowConsoleClient.createPV21WorkflowDiff(workflowId, { draft_revision: saved.graph.draft_revision });
      const versionsBefore = await workflowConsoleClient.listPV21WorkflowVersions(workflowId);
      const publishResult = await workflowConsoleClient.publishPV21Workflow(workflowId, {
        diff_id: diffResult.diff_id,
        draft_revision: saved.graph.draft_revision,
        version: `wp-m3-${Date.now()}`,
      });
      const runResult = await workflowConsoleClient.startPV21WorkflowRun(workflowId, publishResult.version.workflow_version_id, {
        sample: "workflow_platform_main_entry",
        real_input_refs: ["TASKS.md", "workflow_platform_main_entry_prd.md", "WorkflowStudioLayout.tsx"],
        scenario_count: 3,
      });
      setPv21RunId(runResult.workflow_instance.workflow_instance_id);
      const inspected = await workflowConsoleClient.inspectPV21Run(runResult.workflow_instance.workflow_instance_id);
      const pendingGate = inspected.pending_human_gates[0];
      const stationId = typeof pendingGate?.station_id === "string" ? pendingGate.station_id : undefined;
      await workflowConsoleClient.submitPV21HumanAction(runResult.workflow_instance.workflow_instance_id, stationId);
      const evidence = await workflowConsoleClient.getPV21RunEvidence(runResult.workflow_instance.workflow_instance_id);
      const rollbackTarget = versionsBefore.published_version_id || publishResult.version.workflow_version_id;
      await workflowConsoleClient.rollbackPV21Workflow(workflowId, rollbackTarget);
      setRuntimeReviewStatus(runtimeScenarioSummary(validation.status, inspected, evidence));
      updateCapabilityParity("wp-m1-homepage-route", "PASS", "browser:root-route:v13-editable-studio");
      updateCapabilityParity("wp-m3-pv21-runtime-loop", evidence.no_false_green_status === "pass" ? "PASS" : "FAIL", `workflow_instance:${runResult.workflow_instance.workflow_instance_id}`);
      setRunState("blocked");
      setTraceLines((current) => [`[PV21] run ${runResult.workflow_instance.workflow_instance_id} evidence=${evidence.no_false_green_status}`, ...current].slice(0, 12));
      recordAction("运行三场景：PV21 保存/发布/运行/人工审查/证据回读完成");
      showToast("PV21 运行闭环已完成，可在证据面板复核");
    } catch (error) {
      const message = errorMessage(error);
      setRuntimeReviewStatus(`失败：${message}`);
      updateCapabilityParity("wp-m3-pv21-runtime-loop", "FAIL", `error:${message}`);
      recordAction(`运行三场景失败：${message}`);
      showToast("PV21 能力覆盖失败，需复核证据");
    }
  }

  async function runGovernedExecutorLoop() {
    setExecutorReviewStatus("运行中");
    recordAction("执行器验收：开始 PV20 Skill / Tool / MCP 覆盖");
    try {
      const state = await workflowConsoleClient.getPV20AgentExecutorState();
      const runId = state.workflow_instance.workflow_instance_id;
      setPv20RunId(runId);
      await workflowConsoleClient.getPV20AgentExecutionContract(runId);
      await workflowConsoleClient.executePV20AgentSkill(runId, "plan");
      await workflowConsoleClient.executePV20AgentTool(runId);
      await workflowConsoleClient.executePV20AgentMcp(runId);
      const evidence = await workflowConsoleClient.getPV20AgentExecutionEvidence(runId);
      setExecutorReviewStatus(executorScenarioSummary(state, evidence));
      updateCapabilityParity("wp-m4-pv20-executor-loop", evidence.missing_evidence.length === 0 ? "PASS" : "FAIL", `workflow_instance:${runId}`);
      recordAction("执行器验收：PV20 Skill / Tool / MCP 证据回读完成");
      showToast("PV20 受治理执行器证据已完成");
    } catch (error) {
      const message = errorMessage(error);
      setExecutorReviewStatus(`失败：${message}`);
      updateCapabilityParity("wp-m4-pv20-executor-loop", "FAIL", `error:${message}`);
      recordAction(`执行器验收失败：${message}`);
      showToast("PV20 执行器覆盖失败，需复核证据");
    }
  }

  async function executeSingleExecutorAction(action: "skill" | "tool" | "mcp") {
    try {
      const runId = pv20RunId || (await workflowConsoleClient.getPV20AgentExecutorState()).workflow_instance.workflow_instance_id;
      setPv20RunId(runId);
      let result: PV20AgentExecutionActionDTO;
      if (action === "skill") {
        result = await workflowConsoleClient.executePV20AgentSkill(runId, "plan");
      } else if (action === "tool") {
        result = await workflowConsoleClient.executePV20AgentTool(runId);
      } else {
        result = await workflowConsoleClient.executePV20AgentMcp(runId);
      }
      recordAction(`执行器动作：${action} -> ${result.execution.status}`);
      showToast(`执行器动作已完成：${action}`);
    } catch (error) {
      const message = errorMessage(error);
      recordAction(`执行器动作失败：${action} -> ${message}`);
      showToast(`执行器动作失败：${action}`);
    }
  }

  function startSimulation() {
    setSimulationMode("playing");
    setRunState("in_progress");
    recordAction("启动仿真：V13 design_only stream");
    showToast("仿真播放开始；第 6 站会进入人工确认卡口");
  }

  function pauseSimulation() {
    setSimulationMode("paused");
    recordAction("暂停仿真");
    showToast("仿真执行已暂停");
  }

  function stepSimulation() {
    if (simulationStep >= 6) {
      showToast("已到达最后一步，请重置后再试");
      return;
    }
    advanceSimulationStep();
    setSimulationMode("paused");
    recordAction(`步进节点：${simulationStep + 1}`);
  }

  function resetSimulation() {
    resetSimulationStateOnly();
    setRunState("idle");
    setSelectedNodeId(nodes[4]?.id || "summary_agent");
    recordAction("重置仿真状态");
    showToast("仿真流程已完全重置");
  }

  function resetSimulationStateOnly() {
    if (simulationTimer.current) window.clearTimeout(simulationTimer.current);
    setSimulationMode("idle");
    setSimulationStep(0);
    setNodeRunStates(initialNodeRunStates);
    setModalOpen(false);
  }

  function advanceSimulationStep() {
    setSimulationStep((current) => {
      const next = Math.min(6, current + 1);
      const nextStates = nodes.slice(0, 6).map((_, index) => {
        if (index + 1 < next) return "completed";
        if (index + 1 === next) return next === 6 ? "blocked" : "active";
        return "idle";
      }) as NodeRunState[];
      setNodeRunStates(nextStates);
      const nextNode = nodes[next - 1];
      if (nextNode) setSelectedNodeId(nextNode.id);
      injectSimulationOutput(next, nextNode?.label || `Station ${next}`);
      if (next >= 6) blockSimulationAtGate();
      return next;
    });
  }

  function blockSimulationAtGate() {
    setSimulationMode("blocked");
    setRunState("blocked");
    setNodeRunStates((current) => current.map((state, index) => (index < 5 ? "completed" : "blocked")));
    setModalOpen(true);
    recordAction("仿真阻断：等待人工确认");
  }

  function injectSimulationOutput(step: number, nodeLabel: string) {
    const inspectorInfo = scenario.inspector[step - 1] || scenario.inspector[4];
    const body =
      step === 6
        ? "质检卡点已拦截。当前为 design_only 交互审查，必须由人工确认 WorkflowDiff handoff，浏览器不会触发 publish/run。"
        : `Station ${step} 已进入交互仿真：${inspectorInfo.goal}`;
    const message: ChatMessage = { id: `sim-${Date.now()}-${step}`, role: `Station ${step} - ${inspectorInfo.name}`, body, tone: "assistant" };
    setChatMessages((current) => [...current, message].slice(-8));
    setTraceLines((current) => [
      `[${new Date().toLocaleTimeString()}] TRACE: Station ID=${step} (${nodeLabel}) entered design_only state.`,
      `[${new Date().toLocaleTimeString()}] INFO: Mounted tools: [${inspectorInfo.tools}]. Evidence hash preview only.`,
      ...current,
    ].slice(0, 16));
  }

  function setSystemState(category: "api" | "run", state: ApiState | RunState) {
    if (category === "api") {
      setApiState(state as ApiState);
      showToast(`API 状态切换：${state}`);
    } else {
      setRunState(state as RunState);
      showToast(`运行状态切换：${state}`);
    }
    setStateMenuOpen(false);
  }

  function appendSlashCommand(command: string) {
    setChatText(`${command} `);
    recordAction(`装填指令：${command}`);
  }

  function sendChatMessage() {
    const text = chatText.trim();
    if (!text) return;
    setChatText("");
    const userMessage: ChatMessage = { id: `user-${Date.now()}`, role: "管理员", body: text, tone: "user" };
    setChatMessages((current) => [...current, userMessage, buildCommandReply(text)].slice(-10));
    applyChatCommandEffect(text);
    recordAction(`Chat 指令已进入 proposal-only 队列：${text}`);
  }

  function applyChatCommandEffect(text: string) {
    const normalized = text.toLowerCase();
    if (normalized.startsWith("/stations")) {
      setActiveTab("timeline");
      selectNode(nodes[1]?.id || "folder_reader", false);
      showToast("已聚焦工作站拓扑；仅更新浏览器审查视图");
      return;
    }
    if (normalized.startsWith("/evidence")) {
      setActiveTab("evidence");
      selectNode(nodes[5]?.id || "final_markdown", false);
      showToast("已切换到证据链审查；runtime_backed=false");
      return;
    }
    if (normalized.startsWith("/diff")) {
      setActiveTab("trace");
      selectNode(nodes[4]?.id || "summary_agent", false);
      setTraceLines((current) => ["[INFO] Chat /diff highlighted WorkflowDiff proposal path; publish_or_run_started=false.", ...current].slice(0, 16));
      showToast("已高亮 WorkflowDiff 审查路径，等待人工确认");
      return;
    }
    if (normalized.startsWith("/help")) {
      setActiveTab("timeline");
      showToast("已展示可用 proposal-only 指令");
    }
  }

  function adjustZoom(nextZoom: number, anchor?: { clientX: number; clientY: number }) {
    const nextScale = clamp(Math.round(nextZoom * 100) / 100, 0.5, 2);
    setViewport((current) => {
      if (!anchor && nextScale === 1) return { scale: 1, x: CANVAS_OFFSET_X, y: CANVAS_OFFSET_Y };
      const workspace = canvasRef.current;
      if (!workspace) return { ...current, scale: nextScale };
      const rect = workspace.getBoundingClientRect();
      const anchorX = anchor?.clientX ?? rect.left + rect.width / 2;
      const anchorY = anchor?.clientY ?? rect.top + rect.height / 2;
      const worldPoint = {
        x: (anchorX - rect.left - current.x) / current.scale,
        y: (anchorY - rect.top - current.y) / current.scale,
      };
      return {
        scale: nextScale,
        x: anchorX - rect.left - worldPoint.x * nextScale,
        y: anchorY - rect.top - worldPoint.y * nextScale,
      };
    });
  }

  function handleCanvasWheel(event: React.WheelEvent<HTMLDivElement>) {
    event.preventDefault();
    const currentScale = viewportRef.current.scale;
    const nextScale = currentScale * Math.exp(-event.deltaY * 0.0012);
    recordAction(`画布缩放：${Math.round(nextScale * 100)}%`);
    adjustZoom(nextScale, { clientX: event.clientX, clientY: event.clientY });
  }

  function clientPointToWorld(clientX: number, clientY: number): { x: number; y: number } {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    const current = viewportRef.current;
    return {
      x: clamp((clientX - rect.left - current.x) / current.scale, 0, worldSize.width),
      y: clamp((clientY - rect.top - current.y) / current.scale, 0, worldSize.height),
    };
  }

  function cancelFreeConnection(actionLabel = "自由连线取消") {
    setConnectionDraft(null);
    recordAction(actionLabel);
    showToast("自由连线已取消");
  }

  function handlePortPointerDown(event: React.PointerEvent<HTMLSpanElement>, node: StudioNode) {
    if (event.button !== 0) {
      cancelFreeConnection("自由连线取消：非主键操作");
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);
    const start = getNodePort(node, "out");
    setConnectionDraft({ sourceId: node.id, currentX: start.x + 32, currentY: start.y });
    selectNode(node.id, false);
    recordAction(`开始自由连线：${node.label}`);
  }

  function handlePortPointerMove(event: React.PointerEvent<HTMLSpanElement>) {
    if (!connectionDraft) return;
    event.preventDefault();
    event.stopPropagation();
    const point = clientPointToWorld(event.clientX, event.clientY);
    setConnectionDraft((current) => (current ? { ...current, currentX: point.x, currentY: point.y } : current));
  }

  function handlePortPointerUp(event: React.PointerEvent<HTMLSpanElement>) {
    const draft = connectionDraft;
    if (!draft) return;
    event.preventDefault();
    event.stopPropagation();
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    setConnectionDraft(null);
    const targetPort = document
      .elementsFromPoint(event.clientX, event.clientY)
      .find((element) => element instanceof HTMLElement && element.classList.contains("in") && element.classList.contains("v13-node-port")) as HTMLElement | undefined;
    const targetNodeId = targetPort?.closest<HTMLElement>("[data-node-id]")?.dataset.nodeId;
    finishFreeConnection(draft.sourceId, targetNodeId || "");
  }

  function handlePortPointerCancel(event: React.PointerEvent<HTMLSpanElement>) {
    if (!connectionDraft) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    cancelFreeConnection();
  }

  function finishFreeConnection(sourceId: string, targetId: string) {
    if (!targetId) {
      cancelFreeConnection("自由连线取消：未命中输入端口");
      return;
    }
    if (sourceId === targetId) {
      cancelFreeConnection("自由连线取消：不能连接自身");
      return;
    }
    const sourceNode = nodes.find((node) => node.id === sourceId);
    const targetNode = nodes.find((node) => node.id === targetId);
    if (!sourceNode || !targetNode) {
      recordAction("自由连线被阻断：节点不存在");
      showToast("自由连线失败：源节点或目标节点不存在");
      return;
    }
    if (edges.some((edge) => edge.source === sourceId && edge.target === targetId)) {
      selectNode(targetId, false);
      cancelFreeConnection(`自由连线取消：${sourceNode.label} -> ${targetNode.label} 已存在`);
      return;
    }
    const nextEdge = { id: buildManualEdgeId(sourceId, targetId, edges), source: sourceId, target: targetId };
    const nextEdges = [...edges, nextEdge];
    setEdges(nextEdges);
    selectNode(targetId, false);
    recordAction(`自由连线创建：${sourceNode.label} -> ${targetNode.label}`);
    showToast("已创建自由连接，正在生成 WorkflowDiff proposal");
    commitGraph(nodes, nextEdges, "校验自由连线拓扑");
  }

  function handleNodePointerDown(event: React.PointerEvent<HTMLButtonElement>, node: StudioNode) {
    if ((event.target as HTMLElement).closest("button") !== event.currentTarget) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    dragState.current = {
      nodeId: node.id,
      startX: event.clientX,
      startY: event.clientY,
      nodeX: node.x,
      nodeY: node.y,
      latestX: node.x,
      latestY: node.y,
    };
    selectNode(node.id);
  }

  function handleNodePointerMove(event: React.PointerEvent<HTMLButtonElement>) {
    const drag = dragState.current;
    if (!drag) return;
    const next = clampNodePosition(drag.nodeX + (event.clientX - drag.startX) / viewportRef.current.scale, drag.nodeY + (event.clientY - drag.startY) / viewportRef.current.scale, worldSize);
    drag.latestX = next.x;
    drag.latestY = next.y;
    const { x, y } = next;
    setNodes((current) => current.map((node) => (node.id === drag.nodeId ? { ...node, x, y } : node)));
  }

  function handleNodePointerUp(event: React.PointerEvent<HTMLButtonElement>) {
    const drag = dragState.current;
    if (!drag) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    dragState.current = null;
    const nextNodes = nodes.map((node) => (node.id === drag.nodeId ? { ...node, x: drag.latestX, y: drag.latestY } : node));
    setNodes(nextNodes);
    recordAction(`拖拽节点：${drag.nodeId}`);
    commitGraph(nextNodes, edges, "校验拖拽后拓扑");
  }

  function handleNodePointerCancel(event: React.PointerEvent<HTMLButtonElement>) {
    const drag = dragState.current;
    if (!drag) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    dragState.current = null;
    recordAction(`拖拽取消：${drag.nodeId}`);
  }

  return (
    <div className="v13-light-studio" data-testid="v13-editable-studio">
      <header className="v13-light-topbar">
        <button className="v13-brand" onClick={() => showToast("HarnessOS V13 Light Studio 已就绪进行外部设计审查")} type="button">
          <div className="v13-brand__mark">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 2 3 6.6l9 4.7 9-4.7L12 2Z" />
              <path d="M3 12.1 12 17l9-4.9" />
              <path d="M3 17.2 12 22l9-4.8" />
            </svg>
          </div>
          <div>
            <strong>HarnessOS</strong>
            <span>LIGHT STUDIO</span>
          </div>
        </button>
        <button className="v13-top-select" type="button">
          空间: <strong>Demo Space</strong>
          <span>⌄</span>
        </button>
        <div className="v13-topbar__spacer" />
        <div className="v13-state-menu-wrap">
          <button className="v13-top-select" data-testid="v13-state-menu" type="button" onClick={() => setStateMenuOpen((value) => !value)}>
            仿真状态调节 <span>⌄</span>
          </button>
          {stateMenuOpen ? (
            <div className="v13-state-menu">
              <strong>API 状态</strong>
              {(["online", "offline", "rate_limited", "unconfigured"] as ApiState[]).map((state) => (
                <button key={state} onClick={() => setSystemState("api", state)} type="button">
                  {apiStateLabel(state)}
                </button>
              ))}
              <strong>Run 状态</strong>
              {(["idle", "in_progress", "blocked", "failed"] as RunState[]).map((state) => (
                <button key={state} onClick={() => setSystemState("run", state)} type="button">
                  {runStateLabel(state)}
                </button>
              ))}
            </div>
          ) : null}
        </div>
        <StatusPill tone={apiStateTone(apiState)} label={apiStateLabel(apiState)} />
        <StatusPill tone={runStateTone(runState)} label={runStateLabel(runState)} />
        <StatusPill tone="amber" label="等待确认" />
        <span className="v13-design-only">DESIGN ONLY</span>
        <span className="v13-route-assertion" data-testid="workflow-platform-route-assertion">
          首页基线：workflow-platform → V13EditableStudio
        </span>
      </header>

      <div className="v13-light-body">
        <nav className="v13-l1-rail" aria-label="全局导航">
          {l1Routes.map((route, index) => (
            <button
              className={activeL1Route === route.id ? "is-active" : ""}
              data-testid={`v13-l1-route-${route.id}`}
              key={route.id}
              onClick={() => switchL1Route(route.id)}
              type="button"
              aria-label={route.title}
            >
              <RailIcon index={index} />
            </button>
          ))}
        </nav>

        <aside className={leftCollapsed ? "v13-l2-sidebar is-collapsed" : "v13-l2-sidebar"}>
          <div className="v13-l2-sidebar__header">
            <div>
              <h2>
                {activeRoute.title} <span>V13-0P</span>
              </h2>
              <p>{activeRoute.subtitle}</p>
            </div>
            <button type="button" onClick={() => setLeftCollapsed((value) => !value)} aria-label="切换左侧栏">
              ‹
            </button>
          </div>
          <div className="v13-l2-sidebar__body">
            <L2Content activeRoute={activeL1Route} currentScenario={currentScenario} onScenarioChange={switchScenario} scenario={scenario} />
          </div>
          <div className="v13-l2-sidebar__footer">
            <strong>HarnessOS L2 Routing</strong>
            <span>本层资源动态随 L1 / 场景路由切换</span>
          </div>
        </aside>

        <main className="v13-canvas-shell">
          <div className="v13-canvas-toolbar">
            <div className="v13-sim-controls">
              <span>仿真控制:</span>
              {simulationMode === "playing" ? (
                <button data-testid="v13-sim-pause" type="button" onClick={pauseSimulation} aria-label="暂停仿真">
                  ❚❚
                </button>
              ) : (
                <button data-testid="v13-sim-play" type="button" onClick={startSimulation} aria-label="启动仿真">
                  ▶
                </button>
              )}
              <button data-testid="v13-sim-step" type="button" onClick={stepSimulation} aria-label="步进仿真">
                ≫
              </button>
              <button data-testid="v13-sim-reset" type="button" onClick={resetSimulation} aria-label="重置仿真">
                ↻
              </button>
              <strong data-testid="v13-validation-status">
                {simulationStatusLabel} · 校验: {validation?.status || "PENDING"}
              </strong>
            </div>
            <div className="v13-canvas-tools">
              <button type="button" onClick={() => adjustZoom(viewport.scale - 0.1)}>
                −
              </button>
              <button className="v13-zoom-reset" type="button" onClick={() => adjustZoom(1)}>
                {Math.round(viewport.scale * 100)}%
              </button>
              <button type="button" onClick={() => adjustZoom(viewport.scale + 0.1)}>
                +
              </button>
              <button data-testid="v13-cancel-connection" type="button" onClick={() => cancelFreeConnection("自由连线取消：按钮")}>
                取消连线
              </button>
              <span />
              <button className={leftCollapsed ? "" : "is-on"} type="button" onClick={() => setLeftCollapsed((value) => !value)}>
                ◧
              </button>
              <button className={rightCollapsed ? "" : "is-on"} type="button" onClick={() => setRightCollapsed((value) => !value)}>
                ◨
              </button>
            </div>
          </div>

          <div
            className={connectionDraft ? "v13-canvas-workspace is-connecting" : "v13-canvas-workspace"}
            onContextMenu={(event) => {
              if (!connectionDraft) return;
              event.preventDefault();
              cancelFreeConnection("自由连线取消：右键");
            }}
            onWheel={handleCanvasWheel}
            ref={canvasRef}
          >
            <div
              className="v13-canvas-zoom"
              ref={canvasWorldRef}
              style={{ height: worldSize.height, transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.scale})`, width: worldSize.width }}
            >
              <svg className="v13-canvas-edges" viewBox={`0 0 ${worldSize.width} ${worldSize.height}`} aria-hidden="true">
                <defs>
                  <marker id="v13-edge-arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke" />
                  </marker>
                  <marker id="v13-draft-arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
                  </marker>
                </defs>
                {edges.map((edge) => {
                  const source = nodes.find((node) => node.id === edge.source);
                  const target = nodes.find((node) => node.id === edge.target);
                  if (!source || !target) return null;
                  const sourceIndex = nodes.findIndex((node) => node.id === source.id);
                  const targetIndex = nodes.findIndex((node) => node.id === target.id);
                  const sourceState = nodeRunStates[sourceIndex] || "idle";
                  const targetState = nodeRunStates[targetIndex] || "idle";
                  const edgeState = getEdgeVisualState(edge, selectedNodeId, sourceState, targetState);
                  return (
                    <path
                      className={edgeClassName(edgeState)}
                      d={buildEdgePath(source, target)}
                      data-edge-id={edge.id}
                      data-edge-state={edgeState}
                      data-source-node-id={edge.source}
                      data-target-node-id={edge.target}
                      key={edge.id}
                      markerEnd="url(#v13-edge-arrow)"
                    />
                  );
                })}
                {connectionDraft ? (
                  <path
                    className="v13-canvas-edge is-drafting"
                    d={buildConnectionPreviewPath(nodes.find((node) => node.id === connectionDraft.sourceId), connectionDraft)}
                    data-edge-id="connection-preview"
                    data-edge-state="drafting"
                    markerEnd="url(#v13-draft-arrow)"
                  />
                ) : null}
              </svg>
              {nodes.map((node, index) => (
                <button
                  className={nodeClassName(selectedNodeId === node.id, nodeRunStates[index], index)}
                  data-node-id={node.id}
                  data-testid={`v13-node-${index + 1}`}
                  key={node.id}
                  onClick={() => selectNode(node.id)}
                  onPointerDown={(event) => handleNodePointerDown(event, node)}
                  onPointerMove={handleNodePointerMove}
                  onPointerUp={handleNodePointerUp}
                  onPointerCancel={handleNodePointerCancel}
                  onLostPointerCapture={handleNodePointerCancel}
                  style={{ left: node.x, top: node.y }}
                  type="button"
                >
                  <span className="v13-node-port in" data-port-side="in" title={`连接到 ${node.label}`} />
                  <span
                    className="v13-node-port out"
                    data-port-side="out"
                    data-testid={`v13-node-${index + 1}-out-port`}
                    onPointerDown={(event) => handlePortPointerDown(event, node)}
                    onPointerMove={handlePortPointerMove}
                    onPointerUp={handlePortPointerUp}
                    onPointerCancel={handlePortPointerCancel}
                    onLostPointerCapture={handlePortPointerCancel}
                    title={`从 ${node.label} 发起连接`}
                  />
                  <div className="v13-light-node__title">
                    <span>{index + 1}</span>
                    <strong title={node.label}>{node.label}</strong>
                    <em title={nodeRunStates[index] || node.badge}>{nodeRunStates[index] === "active" ? "流式中" : nodeRunStates[index] === "completed" ? "已完成" : nodeRunStates[index] === "blocked" ? "待人工" : node.badge}</em>
                  </div>
                  <div className="v13-light-node__body">
                    <p>
                      <span>{node.metaLabel}:</span>
                      <strong title={node.metaValue}>{node.metaValue}</strong>
                    </p>
                    <p>
                      <span>证据:</span>
                      <strong title={node.evidence}>{node.evidence}</strong>
                    </p>
                  </div>
                </button>
              ))}
            </div>
            <div className="v13-canvas-status">
              实时画布：已激活 {nodes.slice(0, 6).length} / 6 站点 <span>活动场景：{scenario.name}</span>
            </div>
            <div className="v13-minimap" data-testid="v13-minimap">
              <strong>MINIMAP 拓扑投影</strong>
              <svg viewBox="0 0 120 70">
                {edges.slice(0, 6).map((edge) => {
                  const sourceIndex = nodes.findIndex((node) => node.id === edge.source);
                  const targetIndex = nodes.findIndex((node) => node.id === edge.target);
                  if (sourceIndex < 0 || targetIndex < 0) return null;
                  return <line key={edge.id} x1={miniX(nodes[sourceIndex].x, worldSize.width)} y1={miniY(nodes[sourceIndex].y, worldSize.height)} x2={miniX(nodes[targetIndex].x, worldSize.width)} y2={miniY(nodes[targetIndex].y, worldSize.height)} />;
                })}
                {nodes.slice(0, 6).map((node, index) => (
                  <circle className={nodeRunStates[index]} cx={miniX(node.x, worldSize.width)} cy={miniY(node.y, worldSize.height)} key={node.id} r={selectedNodeId === node.id ? 4.5 : 3} />
                ))}
              </svg>
            </div>
          </div>

          <section className="v13-bottom-workbench">
            <article className="v13-chat-panel">
              <div className="v13-panel-title">
                <strong>WORKSPACE CHAT 对话工作台</strong>
                <span>{loadingLabel || "设计隔离草稿策略"}</span>
              </div>
              <div className="v13-chat-messages">
                {chatMessages.map((message) => (
                  <div className={`v13-chat-message is-${message.tone}`} key={message.id}>
                    <strong>{message.role}:</strong>
                    <p>{message.body}</p>
                  </div>
                ))}
              </div>
              <div className="v13-slash-row">
                {["/stations", "/evidence", "/diff", "/help"].map((command) => (
                  <button key={command} type="button" onClick={() => appendSlashCommand(command)}>
                    {command} {slashCommandLabel(command)}
                  </button>
                ))}
              </div>
              <label className="v13-chat-input">
                <textarea
                  data-testid="v13-chat-input"
                  onChange={(event) => setChatText(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      sendChatMessage();
                    }
                  }}
                  placeholder="在此键入指令、发送反馈 or 点选上方的斜杠提示..."
                  value={chatText}
                />
                <button data-testid="v13-chat-send" type="button" onClick={sendChatMessage}>
                  →
                </button>
              </label>
            </article>

            <article className="v13-timeline-panel">
              <div className="v13-tabs">
                {tabs.map((tab) => (
                  <button className={activeTab === tab.id ? "is-active" : ""} key={tab.id} onClick={() => setActiveTab(tab.id)} type="button">
                    {tab.label}
                  </button>
                ))}
              </div>
              <div className="v13-tab-content">
                {activeTab === "timeline" ? <TimelineContent actionLog={actionLog} scenario={scenario} /> : null}
                {activeTab === "trace" ? <TraceContent lines={traceLines} /> : null}
                {activeTab === "quality" ? <QualityContent scenario={scenario} /> : null}
                {activeTab === "evidence" ? <EvidenceContent diff={diff} handoffRef={handoffRef} scenario={scenario} /> : null}
              </div>
            </article>
          </section>
        </main>

        <aside className={rightCollapsed ? "v13-right-inspector is-collapsed" : "v13-right-inspector"} data-testid="v13-node-inspector">
          <div className="v13-profile-title">
            <span>{Math.max(1, selectedIndex + 1)}</span>
            <div>
              <strong>{localInspector?.name || inspector?.label || selectedNode?.label || "总结 Agent"}</strong>
              <small>选中节点 · PROFILE</small>
            </div>
            <button type="button" onClick={() => setRightCollapsed((value) => !value)}>
              ›
            </button>
          </div>
          <InspectorField label="角色定义 (ROLE)" value={localInspector?.role || selectedNode?.metaValue || inspector?.node_kind || "观点总结者"} />
          <InspectorField label="目标规范 (GOAL)" value={localInspector?.goal || "提炼共识、保留分歧，生成最终工作区对话报告。"} />
          <InspectorField label="记忆摘要 (MEMORY DIGEST)" value={`${localInspector?.digest || selectedNodeId}；runtime_backed=false。`} large />
          <div className="v13-inspector-grid">
            <InspectorField label="挂载工具 (TOOLS)" value={localInspector?.tools || inspector?.capability_ref || selectedNode?.capabilityRef || "markdown.summary"} compact />
            <InspectorField label="就绪技能 (SKILLS)" value={localInspector?.skills || "insight-extraction"} compact />
          </div>
          <InspectorField label="MCP 协议引用" value={localInspector?.mcp || "mcp://consensus-broker-server"} />
          <div className="v13-quality-card">
            <strong>质量门槛规范（已通过）</strong>
            <p>{localInspector?.quality || "断言中必须锚定引用 evidence refs。"}</p>
          </div>
          <div className="v13-capability-panel" data-testid="workflow-platform-capability-parity">
            <div data-testid="workflow-platform-exit-status">
              <strong>能力覆盖状态：{capabilityParityReport.status}</strong>
              <span>PV13 首屏 + PV21 运行闭环 + PV20 受治理执行器</span>
            </div>
            <div className="v13-capability-panel__actions">
              <button data-testid="workflow-platform-run-three-scenarios" type="button" onClick={runRuntimeScenarioLoop}>
                运行三场景
              </button>
              <button data-testid="workflow-platform-run-executor-loop" type="button" onClick={runGovernedExecutorLoop}>
                验收执行器
              </button>
            </div>
            <div className="v13-capability-panel__matrix">
              {capabilityParityReport.items.map((item) => (
                <p key={item.id}>
                  <span>{item.status}</span>
                  <strong>{item.label}</strong>
                  <small>{item.evidence_ref}</small>
                </p>
              ))}
            </div>
            <div className="v13-capability-panel__status">
              <span>运行闭环：{runtimeReviewStatus}</span>
              <span>执行器：{executorReviewStatus}</span>
            </div>
          </div>
          <div className="v13-executor-panel" data-testid="workflow-platform-executor-panel">
            <strong>受治理 Agent Executor</strong>
            <span>Evidence DTO · Run: {pv20RunId || "等待读取"} · PV21 Run: {pv21RunId || "等待运行"}</span>
            <div>
              <button type="button" onClick={() => executeSingleExecutorAction("skill")}>
                执行 Skill
              </button>
              <button type="button" onClick={() => executeSingleExecutorAction("tool")}>
                读取 Tool
              </button>
              <button type="button" onClick={() => executeSingleExecutorAction("mcp")}>
                执行 MCP
              </button>
            </div>
          </div>
          <div className="v13-business-output-panel" data-testid="workflow-platform-business-output">
            <strong>WP-M5A 业务产物投影</strong>
            <span data-testid="workflow-platform-business-output-status">
              {businessProjectionStatus} · {currentBusinessScenarioId || "future_optional"}
            </span>
            {currentBusinessOutput ? (
              <>
                <p>
                  <b>{currentBusinessOutput.output_summary.title}</b>
                  {currentBusinessOutput.output_summary.body}
                </p>
                <small>Artifact: {currentBusinessOutput.output_summary.artifact_refs[0]}</small>
                <small>Human review: {currentBusinessOutput.output_summary.human_review_ref}</small>
                <small>Evidence: {Object.keys(currentBusinessOutput.evidence_refs).join(" / ")}</small>
              </>
            ) : (
              <p>当前场景为可视化或后续扩展场景；不会被计入 WP-M5A 三类业务产物出门条件。</p>
            )}
            <em data-testid="workflow-platform-mock-boundary">
              {currentScenarioProjection?.fallback_boundary ||
                "scenarioData / fallbackGraph 仅作为视觉 fallback 或 design reference；业务出门以 BFF DTO 和 evidence refs 为准。"}
            </em>
          </div>
          <InspectorField label="存证链路关系" value={localInspector?.evidence || inspector?.audit_ref || "storyboard-evidence.json"} />
          <div className="v13-actions">
            <button data-testid="v13-add-node" type="button" onClick={addQualityNode}>
              添加质量节点
            </button>
            <button data-testid="v13-connect-node" type="button" onClick={connectEvidenceNode}>
              连接复核路径
            </button>
            <button data-testid="v13-move-node" type="button" onClick={moveSelectedNode}>
              移动选中节点
            </button>
            <button data-testid="v13-configure-node" type="button" onClick={configureSelectedNode}>
              配置选中节点
            </button>
          </div>
          <button className="v13-submit-review" data-testid="v13-confirm-handoff" type="button" onClick={confirmHandoff}>
            提交审计确认规约
          </button>
          <div className="v13-hidden-actions">
            <button data-testid="v13-revise-diff" type="button" onClick={reviseDiff}>
              修订提案
            </button>
            <button data-testid="v13-reject-diff" type="button" onClick={rejectDiff}>
              拒绝提案
            </button>
          </div>
          <div className="v13-boundary" data-testid="v13-bff-source">
            BFF-backed · runtime_backed=false · handoff only
          </div>
          <div className="v13-handoff">
            {handoffRef ? <strong data-testid="v13-handoff-ref">交接引用：{handoffRef}</strong> : <span>等待 WorkflowDiff 审查确认</span>}
          </div>
        </aside>
      </div>

      {modalOpen ? (
        <div className="v13-modal-backdrop" data-testid="v13-sandbox-modal">
          <div className="v13-modal">
            <strong>高风险 WorkflowDiff 交接确认</strong>
            <p>当前仅模拟人工确认交接。确认后写入 handoff ref，不会启动 publish、run 或 runtime mutation。</p>
            <div>
              <button type="button" onClick={() => setModalOpen(false)}>
                关闭预览
              </button>
              <button type="button" onClick={confirmHandoff}>
                模拟签署
              </button>
            </div>
          </div>
        </div>
      ) : null}
      <div className={toast ? "v13-toast is-visible" : "v13-toast"} data-testid="v13-toast">
        {toast}
      </div>
      <div className="v13-action-log" data-testid="v13-action-log" aria-live="polite">
        {actionLog.join("\n")}
      </div>
      <div className="v13-compat-action-log" data-testid="workflow-platform-action-log" aria-live="polite">
        {actionLog.join("\n")}
      </div>
      <div className="v13-workflow-diff" data-testid="v13-workflow-diff" aria-live="polite">
        WorkflowDiff: {diff?.status || "等待生成"} · {diff?.confirmation_boundary || "handoff_only_no_publish_no_run"}
      </div>
    </div>
  );
}

function L2Content({
  activeRoute,
  currentScenario,
  onScenarioChange,
  scenario,
}: {
  activeRoute: L1RouteId;
  currentScenario: ScenarioId;
  onScenarioChange: (scenarioId: ScenarioId) => void;
  scenario: ScenarioData;
}) {
  if (activeRoute === "workbench") {
    return (
      <>
        <SectionLabel>核心工作流场景 (L2)</SectionLabel>
        {(Object.keys(scenarioData) as ScenarioId[]).map((scenarioId) => (
          <button
            className={currentScenario === scenarioId ? "v13-scenario is-active" : "v13-scenario"}
            data-testid={`v13-scenario-${scenarioId}`}
            key={scenarioId}
            onClick={() => onScenarioChange(scenarioId)}
            type="button"
          >
            <span>{currentScenario === scenarioId ? "▣" : "□"}</span>
            <strong>{scenarioData[scenarioId].name}</strong>
            <small>6 站</small>
          </button>
        ))}
        <SectionLabel>上下文审计计数</SectionLabel>
        <MetricRow label="关联智能体" value={scenario.agentsCount} tone="blue" />
        <MetricRow label="就绪技能库" value={scenario.skillsCount} tone="indigo" />
        <MetricRow label="MCP 服务器" value={scenario.mcpCount} tone="green" />
        <MetricRow label="存证单据链" value={scenario.evidenceCount} tone="amber" />
      </>
    );
  }
  const cards: Record<L1RouteId, string[]> = {
    workbench: [],
    agents: ["Socrates 批判派 · 运行中", "Protagoras 经验派 · 运行中", "Scribe 观点总结 · 就绪"],
    workflows: ["当前草稿 V13-0P-Draft", "存证模式 哈希强校签", "Station 磁吸连线合规"],
    skills: ["dialectic-scrutiny", "insight-extraction", "clean-code-audit"],
    mcp: ["consensus-broker · 4 tools", "unreal-engine-mcp · 12 tools", "filesystem-mcp · read only"],
    evidence: ["V13-OP-PLAN · hash preview", "SOCRATES-CRITIQUE · receipt", "WORKFLOWDIFF-HANDOFF · pending"],
    runs: ["Instance #3942 · 卡点挂起", "规则拦截率 100%", "publish_or_run_started=false"],
    settings: ["双角色交叉确认 · 开启", "Design Only · 强保护", "高风险动作 · 人工交接"],
  };
  return (
    <div className="v13-l2-card-list">
      <SectionLabel>{l1Routes.find((route) => route.id === activeRoute)?.title || activeRoute}</SectionLabel>
      {cards[activeRoute].map((item) => (
        <div className="v13-l2-card" key={item}>
          {item}
        </div>
      ))}
    </div>
  );
}

function StatusPill({ label, tone }: { label: string; tone: "green" | "blue" | "amber" | "red" | "slate" }) {
  return (
    <span className={`v13-status-pill is-${tone}`}>
      <i />
      {label}
    </span>
  );
}

function RailIcon({ index }: { index: number }) {
  const icons = [
    "M4 4h7v7H4zM13 4h7v5h-7zM13 11h7v9h-7zM4 13h7v7H4z",
    "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 0v18M3 12h18",
    "M3 12h4l3-8 5 16 3-8h3",
    "M12 3 4 7l8 4 8-4-8-4Zm-8 9 8 4 8-4M4 17l8 4 8-4",
    "M4 5h16v6H4zM4 13h16v6H4z",
    "M12 21s7-4 7-10V5l-7-3-7 3v6c0 6 7 10 7 10Z",
    "M12 6v6l4 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z",
    "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z",
  ];
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={icons[index]} />
    </svg>
  );
}

function SectionLabel({ children }: { children: string }) {
  return <div className="v13-section-label">{children}</div>;
}

function MetricRow({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="v13-metric-row">
      <span className={`is-${tone}`} />
      <strong>{label}</strong>
      <em>{value}</em>
    </div>
  );
}

function InspectorField({ compact = false, label, large = false, value }: { compact?: boolean; label: string; large?: boolean; value: string }) {
  return (
    <div className={large ? "v13-inspector-field is-large" : compact ? "v13-inspector-field is-compact" : "v13-inspector-field"}>
      <label>{label}</label>
      <p title={value}>{value}</p>
    </div>
  );
}

function TimelineContent({ actionLog, scenario }: { actionLog: string[]; scenario: ScenarioData }) {
  const rows = [...scenario.timeline, { time: "15:38:41", msg: actionLog[0] || "等待交互动作", state: "记录" }];
  return (
    <ol className="v13-timeline-list">
      {rows.map((row) => (
        <li key={`${row.time}-${row.msg}`}>
          <span>{row.time}</span>
          <i className={row.state === "处理中" ? "is-processing" : ""} />
          <strong>{row.msg}</strong>
          <em>{row.state}</em>
        </li>
      ))}
    </ol>
  );
}

function TraceContent({ lines }: { lines: string[] }) {
  return <pre className="v13-trace-box">{lines.join("\n")}</pre>;
}

function QualityContent({ scenario }: { scenario: ScenarioData }) {
  return (
    <div className="v13-quality-rules">
      <strong>质量规则 PASS</strong>
      <p>{scenario.inspector[5].quality} WorkflowDiff 必须人工确认；浏览器不得直接写 runtime truth。</p>
    </div>
  );
}

function EvidenceContent({ diff, handoffRef, scenario }: { diff: WorkflowDiff | null; handoffRef: string; scenario: ScenarioData }) {
  return (
    <div className="v13-evidence-list">
      <strong>{diff?.proposal_id || DIFF_ID}</strong>
      <span>{handoffRef || "handoff pending"}</span>
      <span>{scenario.inspector[4].evidence}</span>
      <span>runtime_backed=false</span>
    </div>
  );
}

function scenarioToBusinessScenarioId(scenarioId: ScenarioId): BusinessScenarioId | null {
  if (scenarioId === "docsummary") return "document_summary";
  if (scenarioId === "codereview") return "code_review";
  if (scenarioId === "roma") return "meeting_brief";
  return null;
}

function buildStudioNodes(graphNodes: WorkflowGraphNode[], scenarioId: ScenarioId): StudioNode[] {
  const source = graphNodes.length >= 4 ? graphNodes : fallbackGraph.nodes;
  return VISUAL_NODE_IDS.map((nodeId, index) => source.find((node) => node.node_id === nodeId) || fallbackGraph.nodes[index]).map((node, index) =>
    toStudioNode(node, scenarioId, index),
  );
}

function normalizeStudioEdges(graphEdges: WorkflowGraphEdge[], studioNodes: StudioNode[]): StudioEdge[] {
  const nodeIds = new Set(studioNodes.map((node) => node.id));
  if (VISUAL_NODE_IDS.every((nodeId) => nodeIds.has(nodeId))) return VISUAL_EDGES;
  const filtered = graphEdges
    .filter((edge) => nodeIds.has(edge.source_node_id) && nodeIds.has(edge.target_node_id))
    .map((edge) => ({ id: edge.edge_id, source: edge.source_node_id, target: edge.target_node_id }));
  return filtered.length > 0 ? filtered : VISUAL_EDGES;
}

function toStudioNode(node: WorkflowGraphNode, scenarioId: ScenarioId, index: number): StudioNode {
  const scenario = scenarioData[scenarioId];
  const visual = scenario.nodes[index] || scenarioData.roma.nodes[index];
  const layout = scenario.layout[index] || scenarioData.roma.layout[index];
  return {
    id: node.node_id,
    label: visual.title,
    nodeKind: node.node_kind,
    status: node.status,
    x: layout.x,
    y: layout.y,
    badge: visual.type,
    metaLabel: visual.metaLabel,
    metaValue: visual.metaValue,
    evidence: node.capability_ref || visual.metaValue,
    agentProfileRef: node.agent_profile_ref,
    capabilityRef: node.capability_ref,
  };
}

function applyScenarioToNodes(nodes: StudioNode[], scenarioId: ScenarioId): StudioNode[] {
  return nodes.map((node, index) => {
    const visual = scenarioData[scenarioId].nodes[index] || scenarioData.roma.nodes[index] || scenarioData.roma.nodes[5];
    const layout = scenarioData[scenarioId].layout[index] || scenarioData.roma.layout[index] || scenarioData.roma.layout[5];
    return {
      ...node,
      label: visual.title,
      x: layout.x,
      y: layout.y,
      badge: visual.type,
      metaLabel: visual.metaLabel,
      metaValue: visual.metaValue,
      evidence: node.capabilityRef || visual.metaValue,
    };
  });
}

function toWorkflowGraph(baseGraph: WorkflowSpecGraph, nodes: StudioNode[], edges: StudioEdge[]): WorkflowSpecGraph {
  const nodeIds = new Set(nodes.map((node) => node.id));
  return {
    ...baseGraph,
    runtime_backed: false,
    nodes: nodes.map((node) => ({
      node_id: node.id,
      label: node.label,
      node_kind: node.nodeKind || "station",
      status: node.status || "draft",
      position: { x: Math.round(node.x), y: Math.round(node.y) },
      ...(node.agentProfileRef ? { agent_profile_ref: node.agentProfileRef } : {}),
      ...(node.capabilityRef ? { capability_ref: node.capabilityRef } : {}),
    })),
    edges: edges
      .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
      .map((edge) => ({
        edge_id: edge.id,
        source_node_id: edge.source,
        target_node_id: edge.target,
      })),
  };
}

function buildCommandReply(text: string): ChatMessage {
  const normalized = text.toLowerCase();
  if (normalized.startsWith("/stations")) {
    return {
      id: `reply-${Date.now()}`,
      role: "Planner Agent (规划调度 ID=2)",
      body: "工作站拓扑清单：Station 1 触发、Station 2 规划、Station 3/4 并行探索、Station 5 合并、Station 6 审计卡口。",
      tone: "assistant",
    };
  }
  if (normalized.startsWith("/evidence")) {
    return {
      id: `reply-${Date.now()}`,
      role: "Auditor Agent (合规审计 ID=6)",
      body: "存证链审计结果：当前仅展示 design_only 证据引用，真实发布和运行仍需后续阶段证据。",
      tone: "assistant",
    };
  }
  if (normalized.startsWith("/diff")) {
    return {
      id: `reply-${Date.now()}`,
      role: "Scribe (观点总结 ID=5)",
      body: "WorkflowDiff 已生成 proposal preview，必须通过人工确认交接；publish_or_run_started=false。",
      tone: "assistant",
    };
  }
  if (normalized.startsWith("/help")) {
    return {
      id: `reply-${Date.now()}`,
      role: "Light Studio 导航助手",
      body: "可用指令：/stations 查看工作站，/evidence 查看存证链，/diff 查看差异审查。",
      tone: "assistant",
    };
  }
  return {
    id: `reply-${Date.now()}`,
    role: "Summary Agent (总结者 ID=5)",
    body: "收到反馈。该消息仅进入 proposal-only 队列，不会变更 runtime truth。",
    tone: "assistant",
  };
}

function slashCommandLabel(command: string): string {
  return {
    "/stations": "工作站",
    "/evidence": "存证链",
    "/diff": "审查差异",
    "/help": "帮助",
  }[command] || "";
}

function apiStateLabel(state: ApiState): string {
  return {
    online: "API 在线",
    offline: "API 离线",
    rate_limited: "API 限流",
    unconfigured: "API 未配",
  }[state];
}

function runStateLabel(state: RunState): string {
  return {
    idle: "闲置就绪",
    in_progress: "流式执行中",
    blocked: "节点阻断",
    failed: "执行失败",
  }[state];
}

function apiStateTone(state: ApiState): "green" | "amber" | "red" | "slate" {
  if (state === "online") return "green";
  if (state === "rate_limited") return "amber";
  if (state === "offline") return "red";
  return "slate";
}

function runStateTone(state: RunState): "blue" | "amber" | "red" | "slate" {
  if (state === "in_progress") return "blue";
  if (state === "blocked") return "amber";
  if (state === "failed") return "red";
  return "slate";
}

function nodeClassName(selected: boolean, state: NodeRunState | undefined, index: number): string {
  const classes = ["v13-light-node"];
  if (selected) classes.push("is-selected");
  if (state) classes.push(`is-${state}`);
  if (index === 5) classes.push("is-gate");
  return classes.join(" ");
}

function edgeClassName(state: EdgeVisualState): string {
  return `v13-canvas-edge is-${state}`;
}

function getEdgeVisualState(edge: StudioEdge, selectedNodeId: string, sourceState: NodeRunState, targetState: NodeRunState): EdgeVisualState {
  if (targetState === "blocked") return "blocked";
  if (sourceState === "active" || targetState === "active") return "running";
  if (sourceState === "completed" && targetState === "completed") return "completed";
  if (edge.source === selectedNodeId || edge.target === selectedNodeId) return "selected";
  return "idle";
}

function getNodePort(node: StudioNode, side: "in" | "out"): { x: number; y: number } {
  return {
    x: side === "out" ? node.x + NODE_WIDTH : node.x,
    y: node.y + NODE_PORT_Y,
  };
}

function buildEdgePath(source: StudioNode, target: StudioNode): string {
  const sourcePort = getNodePort(source, "out");
  const targetPort = getNodePort(target, "in");
  const start = { x: sourcePort.x + EDGE_PORT_GAP, y: sourcePort.y };
  const end = { x: targetPort.x - EDGE_PORT_GAP, y: targetPort.y };
  return buildPortPath(start, end);
}

function buildConnectionPreviewPath(source: StudioNode | undefined, draft: ConnectionDraft): string {
  const sourcePort = source ? getNodePort(source, "out") : { x: 0, y: 0 };
  const start = { x: sourcePort.x + EDGE_PORT_GAP, y: sourcePort.y };
  return buildPortPath(start, { x: draft.currentX, y: draft.currentY });
}

function buildPortPath(start: { x: number; y: number }, end: { x: number; y: number }): string {
  const horizontalDistance = end.x - start.x;
  if (horizontalDistance >= 40) {
    const control = clamp(Math.abs(horizontalDistance) * 0.45, 44, 96);
    return `M ${start.x} ${start.y} C ${start.x + control} ${start.y}, ${end.x - control} ${end.y}, ${end.x} ${end.y}`;
  }
  const verticalDirection = end.y >= start.y ? 1 : -1;
  const busX = start.x + clamp(Math.abs(horizontalDistance) + EDGE_NODE_GAP * 2, 56, 96);
  const busY = end.y + verticalDirection * EDGE_NODE_GAP;
  return `M ${start.x} ${start.y} C ${start.x + 36} ${start.y}, ${busX} ${start.y}, ${busX} ${busY} C ${busX} ${end.y}, ${end.x - 36} ${end.y}, ${end.x} ${end.y}`;
}

function buildManualEdgeId(sourceId: string, targetId: string, edges: StudioEdge[]): string {
  const base = `manual__${sourceId}__${targetId}`;
  if (!edges.some((edge) => edge.id === base)) return base;
  let index = 2;
  while (edges.some((edge) => edge.id === `${base}__${index}`)) index += 1;
  return `${base}__${index}`;
}

function clampNodePosition(x: number, y: number, canvasSize: CanvasSize): { x: number; y: number } {
  const snappedX = Math.round(x / NODE_GRID) * NODE_GRID;
  const snappedY = Math.round(y / NODE_GRID) * NODE_GRID;
  return {
    x: clamp(snappedX, 0, canvasSize.width - NODE_WIDTH),
    y: clamp(snappedY, 0, canvasSize.height - NODE_HEIGHT),
  };
}

function miniX(x: number, canvasWidth: number): number {
  return Math.round((x / canvasWidth) * 104 + 8);
}

function miniY(y: number, canvasHeight: number): number {
  return Math.round((y / canvasHeight) * 54 + 8);
}

function computeCanvasWorldSize(nodes: StudioNode[], workspaceSize: CanvasSize, scale: number): CanvasSize {
  const maxNodeX = nodes.reduce((max, node) => Math.max(max, node.x + NODE_WIDTH + CANVAS_PADDING), MIN_CANVAS_WIDTH);
  const maxNodeY = nodes.reduce((max, node) => Math.max(max, node.y + NODE_HEIGHT + CANVAS_PADDING), MIN_CANVAS_HEIGHT);
  const visibleWorldWidth = Math.max(MIN_CANVAS_WIDTH, (workspaceSize.width - CANVAS_OFFSET_X * 2) / scale);
  const visibleWorldHeight = Math.max(MIN_CANVAS_HEIGHT, (workspaceSize.height - CANVAS_OFFSET_Y * 2) / scale);
  return {
    width: Math.ceil(Math.max(MIN_CANVAS_WIDTH, visibleWorldWidth, maxNodeX)),
    height: Math.ceil(Math.max(MIN_CANVAS_HEIGHT, visibleWorldHeight, maxNodeY)),
  };
}

function runtimeScenarioSummary(validationStatus: PV21RunDTO["state"] | string, inspected: PV21RunDTO, evidence: PV21EvidenceSummaryDTO): string {
  const runStatus = inspected.workflow_instance.status;
  return `校验 ${validationStatus} · Run ${runStatus} · No False Green ${evidence.no_false_green_status}`;
}

function executorScenarioSummary(state: PV20AgentExecutorStateDTO, evidence: PV20AgentExecutionEvidenceDTO): string {
  return `${state.stage} · ${state.status} · 缺失证据 ${evidence.missing_evidence.length}`;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
