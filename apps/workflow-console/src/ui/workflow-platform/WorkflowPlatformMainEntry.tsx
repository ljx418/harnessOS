import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent, WheelEvent } from "react";
import {
  Activity,
  Boxes,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock3,
  Code2,
  FileText,
  GitCompareArrows,
  Globe2,
  Layers3,
  MessageSquare,
  Minus,
  MousePointer2,
  PanelLeft,
  PanelRight,
  Play,
  PlayCircle,
  Plus,
  RotateCcw,
  Save,
  Server,
  Settings,
  Shield,
  ShieldCheck,
  Video,
  Workflow,
  Zap,
} from "lucide-react";
import type {
  PV20AgentExecutionActionDTO,
  PV20AgentExecutionContractDTO,
  PV20AgentExecutionEvidenceDTO,
  PV20AgentExecutorStateDTO,
  PV21EvidenceSummaryDTO,
  PV21GraphValidationDTO,
  PV21HumanActionDTO,
  PV21RunDTO,
  PV21StudioStateDTO,
  PV21WorkflowDiffDTO,
  PV21WorkflowGraphDTO,
  PV21WorkflowVersionDTO,
} from "../../api/types.js";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import "./workflow-platform-main-entry.css";

type LoadState = "loading" | "ready" | "error";
type ScenarioId = "document_summary" | "code_review" | "meeting_brief";
type CanvasAction =
  | "load"
  | "wheel_zoom"
  | "pan_canvas"
  | "node_drag"
  | "right_area_drag"
  | "free_connect"
  | "cancel_connect"
  | "invalid_connect"
  | "select_node"
  | "save_graph"
  | "validate_graph"
  | "workflow_diff"
  | "publish"
  | "run"
  | "human_gate"
  | "evidence_review"
  | "executor_action";

interface PlatformNode {
  id: string;
  label: string;
  type: string;
  stationId: string;
  x: number;
  y: number;
  status: string;
}

interface PlatformEdge {
  id: string;
  source: string;
  target: string;
  status?: "draft" | "saved";
}

interface ActionRecord {
  action_id: string;
  type: CanvasAction;
  target: string;
  expected: string;
  actual: string;
  status: "PASS" | "FAIL";
}

interface ScenarioDefinition {
  id: ScenarioId;
  title: string;
  goal: string;
  inputLabel: string;
  inputRef: string;
  graphSummary: string;
  output: string;
  resourceMap: string[];
}

const scenarioDefinitions: ScenarioDefinition[] = [
  {
    id: "document_summary",
    title: "文档 / 知识总结",
    goal: "把项目规划文档整理成带证据引用的中文摘要。",
    inputLabel: "docs/design/V12-V15.x/workflow_platform_main_entry_prd.md",
    inputRef: "repo://docs/design/V12-V15.x/workflow_platform_main_entry_prd.md",
    graphSummary: "Input -> Retrieval/Read -> Summarizer Agent -> Human Review -> Report Output",
    output: "中文摘要、来源引用、缺口列表、人工审查记录",
    resourceMap: ["Skill: document-ingestion", "Tool: repository.read", "MCP: data_service_mcp"],
  },
  {
    id: "code_review",
    title: "代码审查 / 变更风险检查",
    goal: "对工作流平台入口改动做文件级风险和测试建议检查。",
    inputLabel: "apps/workflow-console/src/App.tsx + current git diff",
    inputRef: "repo://apps/workflow-console/src/App.tsx",
    graphSummary: "Code Input -> Static Scan -> Test Runner -> Risk Agent -> Human Gate -> Issue Output",
    output: "文件级问题、测试输出、风险等级、建议修复清单",
    resourceMap: ["Skill: code-review", "Tool: static.scan", "MCP: repository_index"],
  },
  {
    id: "meeting_brief",
    title: "会议 / 访谈整理",
    goal: "把阶段验收讨论文本整理成决策、行动项和待确认问题。",
    inputLabel: "TASKS.md 当前主线与用户验收要求摘录",
    inputRef: "repo://TASKS.md",
    graphSummary: "Transcript Input -> Extractor Agent -> Decision Classifier -> Task Planner -> Human Gate -> Brief Output",
    output: "会议简报、行动项、决策记录、开放问题",
    resourceMap: ["Skill: meeting-minutes", "Tool: transcript.extract", "MCP: evidence_store"],
  },
];

const defaultPositions = [
  { x: 70, y: 170 },
  { x: 300, y: 170 },
  { x: 530, y: 82 },
  { x: 530, y: 258 },
  { x: 760, y: 170 },
  { x: 990, y: 170 },
];

const NODE_CARD_WIDTH = 210;
const NODE_PORT_Y = 56;

const railNavItems = [
  { label: "工作流", icon: Boxes, active: true },
  { label: "空间资源", icon: Globe2, active: false },
  { label: "运行态", icon: Activity, active: false },
  { label: "图层", icon: Layers3, active: false },
  { label: "服务", icon: Server, active: false },
  { label: "治理", icon: Shield, active: false },
  { label: "审计", icon: Clock3, active: false },
];

const prototypeSceneItems = [
  { key: "rome-forum", scenarioId: "document_summary" as ScenarioId, label: "罗马广场讨论工作流", icon: MessageSquare, count: "6 站" },
  { key: "storyboard", scenarioId: "meeting_brief" as ScenarioId, label: "视频分镜创作工作流", icon: Video, count: "6 站" },
  { key: "code-review", scenarioId: "code_review" as ScenarioId, label: "代码审查工作流", icon: Code2, count: "6 站" },
  { key: "doc-summary", scenarioId: "document_summary" as ScenarioId, label: "文档总结工作流", icon: FileText, count: "6 站" },
];

const contextStats = [
  { label: "关联智能体", value: "6", tone: "blue" },
  { label: "就绪技能库", value: "12", tone: "violet" },
  { label: "MCP 服务器", value: "4", tone: "green" },
  { label: "存证单据链", value: "18", tone: "amber" },
];

export function WorkflowPlatformMainEntry() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<PV21StudioStateDTO | null>(null);
  const [graph, setGraph] = useState<PV21WorkflowGraphDTO | null>(null);
  const [nodes, setNodes] = useState<PlatformNode[]>([]);
  const [edges, setEdges] = useState<PlatformEdge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [validation, setValidation] = useState<PV21GraphValidationDTO | null>(null);
  const [diff, setDiff] = useState<PV21WorkflowDiffDTO | null>(null);
  const [published, setPublished] = useState<PV21WorkflowVersionDTO | null>(null);
  const [run, setRun] = useState<PV21RunDTO | null>(null);
  const [humanAction, setHumanAction] = useState<PV21HumanActionDTO | null>(null);
  const [evidence, setEvidence] = useState<PV21EvidenceSummaryDTO | null>(null);
  const [executorState, setExecutorState] = useState<PV20AgentExecutorStateDTO | null>(null);
  const [executorContract, setExecutorContract] = useState<PV20AgentExecutionContractDTO | null>(null);
  const [executorEvidence, setExecutorEvidence] = useState<PV20AgentExecutionEvidenceDTO | null>(null);
  const [executorAction, setExecutorAction] = useState<PV20AgentExecutionActionDTO | null>(null);
  const [activeScenario, setActiveScenario] = useState<ScenarioId>("document_summary");
  const [scenarioStatus, setScenarioStatus] = useState<Record<ScenarioId, "idle" | "running" | "passed" | "failed">>({
    document_summary: "idle",
    code_review: "idle",
    meeting_brief: "idle",
  });
  const [actionLog, setActionLog] = useState<ActionRecord[]>([]);
  const [viewport, setViewport] = useState({ scale: 1, x: 0, y: 0 });
  const [connectionDraft, setConnectionDraft] = useState<{ source: string; x: number; y: number } | null>(null);

  const canvasRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{ nodeId: string; startX: number; startY: number; nodeX: number; nodeY: number } | null>(null);
  const panRef = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);
  const publishedRef = useRef<PV21WorkflowVersionDTO | null>(null);

  const workflowId = state?.workflow.workflow_template_id || graph?.workflow_id || "";
  const activeVersionId = published?.workflow_version_id || state?.published_version?.workflow_version_id || "";
  const selectedNode = nodes.find((node) => node.id === selectedNodeId) || nodes[0] || null;
  const selectedScenario = scenarioDefinitions.find((item) => item.id === activeScenario) || scenarioDefinitions[0];
  const allScenarioPassed = scenarioDefinitions.every((scenario) => scenarioStatus[scenario.id] === "passed");
  const executorRunId = executorState?.workflow_instance.workflow_instance_id || executorContract?.workflow_instance.workflow_instance_id || "";
  const selectedSceneTitle = prototypeSceneItems.find((item) => item.scenarioId === activeScenario)?.label || "罗马广场讨论工作流";
  const zoomPercent = Math.round(viewport.scale * 100);

  const edgePaths = useMemo(
    () =>
      edges
        .map((edge) => {
          const source = nodes.find((node) => node.id === edge.source);
          const target = nodes.find((node) => node.id === edge.target);
          if (!source || !target) return null;
          const startX = source.x + NODE_CARD_WIDTH;
          const startY = source.y + NODE_PORT_Y;
          const endX = target.x;
          const endY = target.y + NODE_PORT_Y;
          const mid = Math.max(60, Math.abs(endX - startX) / 2);
          return { ...edge, path: `M ${startX} ${startY} C ${startX + mid} ${startY}, ${endX - mid} ${endY}, ${endX} ${endY}` };
        })
        .filter(Boolean) as Array<PlatformEdge & { path: string }>,
    [edges, nodes],
  );

  const recordAction = useCallback((type: CanvasAction, target: string, actual = "completed", status: "PASS" | "FAIL" = "PASS") => {
    setActionLog((current) =>
      [
        {
          action_id: `${type}-${Date.now()}`,
          type,
          target,
          expected: "completed",
          actual,
          status,
        },
        ...current,
      ].slice(0, 80),
    );
  }, []);

  async function refreshState() {
    const payload = await workflowConsoleClient.getPV21StudioState();
    setState(payload);
    setGraph(payload.draft_graph);
    publishedRef.current = payload.published_version || null;
    const mappedNodes = mapGraphNodes(payload.draft_graph);
    const mappedEdges = mapGraphEdges(payload.draft_graph);
    setNodes((current) => (current.length > 0 ? mergeNodeData(current, mappedNodes) : mappedNodes));
    setEdges((current) => (current.length > 0 ? current : mappedEdges));
    setSelectedNodeId((current) => current || mappedNodes[0]?.id || null);
    return payload;
  }

  async function refreshExecutorState() {
    const nextState = await workflowConsoleClient.getPV20AgentExecutorState();
    setExecutorState(nextState);
    const runId = nextState.workflow_instance.workflow_instance_id;
    const [contract, nextEvidence] = await Promise.all([
      workflowConsoleClient.getPV20AgentExecutionContract(runId),
      workflowConsoleClient.getPV20AgentExecutionEvidence(runId),
    ]);
    setExecutorContract(contract);
    setExecutorEvidence(nextEvidence);
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoadState("loading");
        await refreshState();
        await refreshExecutorState();
        if (!cancelled) {
          recordAction("load", "workflow-platform-main-entry");
          setLoadState("ready");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "工作流平台加载失败");
          setLoadState("error");
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [recordAction]);

  useEffect(() => {
    function handleMove(event: PointerEvent) {
      if (dragRef.current) {
        const next = screenToCanvas(event.clientX, event.clientY);
        const start = screenToCanvas(dragRef.current.startX, dragRef.current.startY);
        const nextNodes = nodes.map((node) =>
          node.id === dragRef.current?.nodeId
            ? { ...node, x: Math.max(0, dragRef.current.nodeX + next.x - start.x), y: Math.max(0, dragRef.current.nodeY + next.y - start.y) }
            : node,
        );
        setNodes(nextNodes);
        return;
      }
      if (panRef.current) {
        setViewport((current) => ({
          ...current,
          x: panRef.current!.originX + event.clientX - panRef.current!.startX,
          y: panRef.current!.originY + event.clientY - panRef.current!.startY,
        }));
        return;
      }
      if (connectionDraft) {
        const next = screenToCanvas(event.clientX, event.clientY);
        setConnectionDraft({ ...connectionDraft, x: next.x, y: next.y });
      }
    }
    function handleUp() {
      if (dragRef.current) {
        const dragged = dragRef.current;
        dragRef.current = null;
        const finalNode = nodes.find((node) => node.id === dragged.nodeId);
        recordAction((finalNode?.x ?? dragged.nodeX) >= 700 ? "right_area_drag" : "node_drag", dragged.nodeId);
      }
      if (panRef.current) {
        panRef.current = null;
        recordAction("pan_canvas", "canvas");
      }
    }
    window.addEventListener("pointermove", handleMove);
    window.addEventListener("pointerup", handleUp);
    return () => {
      window.removeEventListener("pointermove", handleMove);
      window.removeEventListener("pointerup", handleUp);
    };
  }, [connectionDraft, nodes, recordAction, viewport.scale]);

  function screenToCanvas(clientX: number, clientY: number) {
    const rect = canvasRef.current?.getBoundingClientRect();
    return {
      x: (clientX - (rect?.left || 0) - viewport.x) / viewport.scale,
      y: (clientY - (rect?.top || 0) - viewport.y) / viewport.scale,
    };
  }

  function onWheel(event: WheelEvent<HTMLDivElement>) {
    event.preventDefault();
    const nextScale = Math.min(1.6, Math.max(0.65, viewport.scale + (event.deltaY > 0 ? -0.08 : 0.08)));
    setViewport((current) => ({ ...current, scale: Number(nextScale.toFixed(2)) }));
    recordAction("wheel_zoom", "canvas", `scale:${nextScale.toFixed(2)}`);
  }

  function startNodeDrag(event: ReactPointerEvent, node: PlatformNode) {
    event.preventDefault();
    event.stopPropagation();
    setSelectedNodeId(node.id);
    recordAction("select_node", node.id);
    dragRef.current = { nodeId: node.id, startX: event.clientX, startY: event.clientY, nodeX: node.x, nodeY: node.y };
  }

  function startPan(event: ReactPointerEvent) {
    if (event.button !== 0 || connectionDraft) return;
    panRef.current = { startX: event.clientX, startY: event.clientY, originX: viewport.x, originY: viewport.y };
  }

  function startConnection(event: ReactPointerEvent, nodeId: string) {
    event.preventDefault();
    event.stopPropagation();
    const node = nodes.find((item) => item.id === nodeId);
    if (!node) return;
    setConnectionDraft({ source: nodeId, x: node.x + NODE_CARD_WIDTH, y: node.y + NODE_PORT_Y });
  }

  function finishConnection(event: ReactPointerEvent, targetId: string) {
    if (!connectionDraft) return;
    event.preventDefault();
    event.stopPropagation();
    if (connectionDraft.source === targetId) {
      recordAction("invalid_connect", targetId, "self connection denied", "PASS");
      setConnectionDraft(null);
      return;
    }
    const edgeId = `wp-edge-${connectionDraft.source}-${targetId}`;
    if (!edges.some((edge) => edge.id === edgeId)) {
      setEdges((current) => [...current, { id: edgeId, source: connectionDraft.source, target: targetId, status: "draft" }]);
    }
    recordAction("free_connect", `${connectionDraft.source}->${targetId}`);
    setConnectionDraft(null);
  }

  function cancelConnection() {
    if (!connectionDraft) return;
    recordAction("cancel_connect", connectionDraft.source);
    setConnectionDraft(null);
  }

  async function runAction(name: string, action: () => Promise<void>) {
    try {
      setBusyAction(name);
      setError(null);
      await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : "工作流平台操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  function buildGraphPayload(): PV21WorkflowGraphDTO {
    const base = graph || state!.draft_graph;
    return {
      ...base,
      nodes: base.nodes.map((node) => {
        const local = nodes.find((item) => item.id === node.node_id);
        return {
          ...node,
          metadata: {
            ...(node.metadata || {}),
            workflow_platform_position: local ? { x: Math.round(local.x), y: Math.round(local.y) } : undefined,
            workflow_platform_scenario: activeScenario,
          },
        };
      }),
      edges: edges.map((edge, index) => {
        const source = nodes.find((node) => node.id === edge.source);
        const target = nodes.find((node) => node.id === edge.target);
        return {
          edge_id: edge.id,
          source: edge.source,
          target: edge.target,
          from_station_id: source?.stationId || edge.source,
          to_station_id: target?.stationId || edge.target,
          order: index,
          metadata: { workflow_platform_edge: true, status: edge.status || "draft" },
        };
      }),
      layout: {
        ...(base.layout || {}),
        workflow_platform_nodes: Object.fromEntries(nodes.map((node) => [node.id, { x: Math.round(node.x), y: Math.round(node.y) }])),
      },
    };
  }

  async function saveGraph() {
    await runAction("save-graph", async () => {
      const result = await workflowConsoleClient.savePV21WorkflowGraph(workflowId, buildGraphPayload());
      setGraph(result.graph);
      setValidation(result.validation);
      recordAction("save_graph", workflowId);
    });
  }

  async function validateGraph() {
    await runAction("validate-graph", async () => {
      setValidation(await workflowConsoleClient.validatePV21WorkflowGraph(workflowId));
      recordAction("validate_graph", workflowId);
    });
  }

  async function createDiff() {
    await runAction("create-diff", async () => {
      const nextDiff = await workflowConsoleClient.createPV21WorkflowDiff(workflowId, {
        base_version_id: activeVersionId,
        draft_revision: graph?.draft_revision,
      });
      setDiff(nextDiff);
      recordAction("workflow_diff", workflowId);
    });
  }

  async function publishVersion() {
    await runAction("publish-version", async () => {
      const result = await workflowConsoleClient.publishPV21Workflow(workflowId, {
        draft_revision: graph?.draft_revision || 1,
        diff_id: diff?.diff_id,
        version: `wp-${Date.now()}`,
      });
      setPublished(result.version);
      publishedRef.current = result.version;
      recordAction("publish", result.version.workflow_version_id);
    });
  }

  async function runScenario(scenarioId = activeScenario) {
    const scenario = scenarioDefinitions.find((item) => item.id === scenarioId) || selectedScenario;
    await runAction(`run-${scenarioId}`, async () => {
      setScenarioStatus((current) => ({ ...current, [scenario.id]: "running" }));
      let nextVersion = publishedRef.current;
      if (!nextVersion) {
        const latestGraph = await workflowConsoleClient.getPV21WorkflowGraph(workflowId);
        setGraph(latestGraph);
        const nextValidation = await workflowConsoleClient.validatePV21WorkflowGraph(workflowId);
        setValidation(nextValidation);
        const latestVersionId = state?.published_version?.workflow_version_id || "";
        const nextDiff = await workflowConsoleClient.createPV21WorkflowDiff(workflowId, { base_version_id: latestVersionId, draft_revision: latestGraph.draft_revision });
        setDiff(nextDiff);
        nextVersion = (
          await workflowConsoleClient.publishPV21Workflow(workflowId, {
            draft_revision: latestGraph.draft_revision || 1,
            diff_id: nextDiff.diff_id,
            version: `wp-${scenario.id}-${Date.now()}`,
          })
        ).version;
        setPublished(nextVersion);
        publishedRef.current = nextVersion;
      }
      const nextRun = await workflowConsoleClient.startPV21WorkflowRun(workflowId, nextVersion.workflow_version_id, {
        scenario_id: scenario.id,
        scenario_goal: scenario.goal,
        scenario_input_refs: [scenario.inputRef],
        scenario_payload: {
          input_label: scenario.inputLabel,
          graph_summary: scenario.graphSummary,
          expected_output: scenario.output,
        },
      });
      setRun(nextRun);
      recordAction("run", scenario.id);
      const humanGate = nextRun.current_human_gate || nextRun.pending_human_gates?.[0];
      const humanGateStationId = String(humanGate?.station_id || "");
      if (!humanGateStationId) {
        throw new Error(`Human gate station missing for ${scenario.id}`);
      }
      const nextHumanAction = await workflowConsoleClient.submitPV21HumanAction(nextRun.run_id, humanGateStationId);
      setHumanAction(nextHumanAction);
      recordAction("human_gate", scenario.id);
      const inspected = await workflowConsoleClient.inspectPV21Run(nextRun.run_id);
      setRun(inspected);
      const nextEvidence = await workflowConsoleClient.getPV21RunEvidence(nextRun.run_id);
      setEvidence(nextEvidence);
      recordAction("evidence_review", scenario.id);
      setScenarioStatus((current) => ({ ...current, [scenario.id]: "passed" }));
    });
  }

  async function runAllScenarios() {
    for (const scenario of scenarioDefinitions) {
      setActiveScenario(scenario.id);
      await runScenario(scenario.id);
    }
  }

  async function runExecutorAction(kind: "skill" | "tool" | "mcp") {
    if (!executorRunId) return;
    await runAction(`executor-${kind}`, async () => {
      const result =
        kind === "skill"
          ? await workflowConsoleClient.executePV20AgentSkill(executorRunId)
          : kind === "tool"
            ? await workflowConsoleClient.executePV20AgentTool(executorRunId)
            : await workflowConsoleClient.executePV20AgentMcp(executorRunId);
      setExecutorAction(result);
      await refreshExecutorState();
      recordAction("executor_action", kind);
    });
  }

  if (loadState === "loading") {
    return <main className="workflow-platform workflow-platform--state" data-testid="workflow-platform-main-entry">正在加载工作流平台主入口…</main>;
  }

  if (loadState === "error") {
    return (
      <main className="workflow-platform workflow-platform--state workflow-platform--error" data-testid="workflow-platform-main-entry">
        <strong>工作流平台加载失败</strong>
        <span>{error}</span>
      </main>
    );
  }

  return (
    <main className="workflow-platform workflow-platform--op" data-testid="workflow-platform-main-entry">
      <aside className="workflow-platform__rail" aria-label="工作流平台导航">
        <div className="workflow-platform__rail-logo">
          <Layers3 size={26} />
        </div>
        <nav>
          {railNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.label} type="button" className={item.active ? "is-active" : ""} aria-label={item.label}>
                <Icon size={24} />
              </button>
            );
          })}
        </nav>
        <button type="button" className="workflow-platform__rail-settings" aria-label="设置">
          <Settings size={24} />
        </button>
      </aside>

      <section className="workflow-platform__shell">
        <header className="workflow-platform__appbar">
          <div className="workflow-platform__brand">
            <div className="workflow-platform__brand-mark">
              <Layers3 size={24} />
            </div>
            <div>
              <strong>HarnessOS</strong>
              <span>LIGHT STUDIO</span>
            </div>
          </div>
          <div className="workflow-platform__workspace-pill">
            <span>空间: {state?.workspace.display_name || "Demo_Space"}</span>
            <ChevronDown size={16} />
          </div>
          <div className="workflow-platform__appbar-spacer" />
          <button type="button" className="workflow-platform__status-chip">
            <Settings size={16} />
            仿真状态调节
            <ChevronDown size={14} />
          </button>
          <span className="workflow-platform__status-chip is-online">API 在线</span>
          <span className="workflow-platform__status-chip is-ready">闲置就绪</span>
          <span className="workflow-platform__status-chip is-waiting">等待确认</span>
          <span className="workflow-platform__status-chip is-design">DESIGN ONLY</span>
          <div className="workflow-platform__status" data-testid="workflow-platform-route-assertion">
            workflow-platform / BFF only / bounded review
          </div>
        </header>

      {error ? <div className="workflow-platform__error">{error}</div> : null}

      <section className="workflow-platform__summary" data-testid="workflow-platform-first-screen-summary">
        <SummaryCard label="Workspace" value={state?.workspace.display_name || "-"} />
        <SummaryCard label="Project" value={state?.project.display_name || "-"} />
        <SummaryCard label="Workflow" value={state?.workflow.name || workflowId || "-"} />
        <SummaryCard label="Graph" value={`${nodes.length} 节点 / ${edges.length} 边`} />
        <SummaryCard label="Run" value={run?.state || "等待运行"} />
        <SummaryCard label="Evidence" value={evidence?.no_false_green_status || state?.evidence_health.status || "等待证据"} />
      </section>

      <section className="workflow-platform__main">
        <aside className="workflow-platform__left">
          <div className="workflow-platform__left-head">
            <div>
              <h1>工作流平台</h1>
              <p>项目级工作流编排与上下文资源</p>
            </div>
            <span>V13-OP</span>
            <ChevronRight size={18} />
          </div>
          <section className="workflow-platform__scene-list">
            <h2>核心工作流场景 (L2)</h2>
            {prototypeSceneItems.map((scene) => {
              const Icon = scene.icon;
              return (
                <button
                  key={scene.key}
                  type="button"
                  className={scene.scenarioId === activeScenario ? "is-active" : ""}
                  data-testid={`workflow-platform-scenario-${scene.key}`}
                  onClick={() => setActiveScenario(scene.scenarioId)}
                >
                  <Icon size={20} />
                  <strong>{scene.label}</strong>
                  <span>{scene.count}</span>
                </button>
              );
            })}
          </section>
          <section className="workflow-platform__context-stats">
            <h2>上下文审计数</h2>
            {contextStats.map((item) => (
              <div key={item.label} className={`workflow-platform__stat-dot is-${item.tone}`}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </section>
          <div className="workflow-platform__scenario" data-testid="workflow-platform-scenario-detail">
            <strong>{selectedScenario.goal}</strong>
            <span>输入：{selectedScenario.inputLabel}</span>
            <span>路径：{selectedScenario.graphSummary}</span>
            <span>产物：{selectedScenario.output}</span>
          </div>
          <footer>
            <strong>HarnessOS L2 Routing</strong>
            <span>本层资源动态随 L1 / 场景路由切换</span>
          </footer>
        </aside>

        <section className="workflow-platform__center">
          <div className="workflow-platform__toolbar">
            <span>仿真控制:</span>
            <button type="button" className="is-icon is-play" onClick={() => void runScenario()} disabled={busyAction !== null || !workflowId} aria-label="播放当前场景"><Play size={17} /></button>
            <button type="button" className="is-icon" onClick={() => void runAllScenarios()} disabled={busyAction !== null || !workflowId} aria-label="快进运行全部场景"><Zap size={17} /></button>
            <button type="button" className="is-icon" onClick={cancelConnection} disabled={!connectionDraft} aria-label="撤销连线草稿"><RotateCcw size={17} /></button>
            <span className="workflow-platform__sim-state">空闲 (Ready to Play)</span>
            <button type="button" onClick={() => void saveGraph()} disabled={busyAction !== null || !workflowId}><Save size={15} />保存</button>
            <button type="button" onClick={() => void validateGraph()} disabled={busyAction !== null || !workflowId}><CheckCircle2 size={15} />校验</button>
            <button type="button" onClick={() => void createDiff()} disabled={busyAction !== null || !workflowId}><GitCompareArrows size={15} />Diff</button>
            <button type="button" onClick={() => void publishVersion()} disabled={busyAction !== null || !workflowId}><ShieldCheck size={15} />发布</button>
            <button type="button" onClick={() => void runScenario()} disabled={busyAction !== null || !workflowId}><PlayCircle size={15} />运行当前场景</button>
            <button type="button" onClick={() => void runAllScenarios()} disabled={busyAction !== null || !workflowId}><Workflow size={15} />运行三场景</button>
            <button type="button" onClick={cancelConnection} disabled={!connectionDraft}><MousePointer2 size={15} />取消连线</button>
            <div className="workflow-platform__zoom">
              <button type="button" aria-label="缩小"><Minus size={14} /></button>
              <strong>{zoomPercent}%</strong>
              <button type="button" aria-label="放大"><Plus size={14} /></button>
            </div>
            <PanelLeft size={20} className="workflow-platform__panel-icon" />
            <PanelRight size={20} className="workflow-platform__panel-icon" />
          </div>

          <div
            ref={canvasRef}
            className="workflow-platform__canvas"
            data-testid="workflow-platform-canvas"
            onWheel={onWheel}
            onPointerDown={startPan}
          >
            <div
              className="workflow-platform__world"
              style={{ transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.scale})` }}
            >
              <svg className="workflow-platform__edges" width="1320" height="720" data-testid="workflow-platform-edge-layer">
                <defs>
                  <marker id="wp-arrow" markerWidth="16" markerHeight="16" refX="13" refY="8" orient="auto">
                    <path d="M 0 0 L 16 8 L 0 16 z" fill="#10b981" />
                  </marker>
                  <marker id="wp-arrow-draft" markerWidth="16" markerHeight="16" refX="13" refY="8" orient="auto">
                    <path d="M 0 0 L 16 8 L 0 16 z" fill="#2563eb" />
                  </marker>
                </defs>
                {edgePaths.map((edge) => (
                  <path
                    key={edge.id}
                    d={edge.path}
                    className={edge.status === "draft" ? "is-draft" : ""}
                    markerEnd={edge.status === "draft" ? "url(#wp-arrow-draft)" : "url(#wp-arrow)"}
                  />
                ))}
                {connectionDraft ? (
                  <line
                    x1={(nodes.find((node) => node.id === connectionDraft.source)?.x || 0) + NODE_CARD_WIDTH}
                    y1={(nodes.find((node) => node.id === connectionDraft.source)?.y || 0) + NODE_PORT_Y}
                    x2={connectionDraft.x}
                    y2={connectionDraft.y}
                    className="is-draft-line"
                  />
                ) : null}
              </svg>
              {nodes.map((node, index) => (
                <article
                  key={node.id}
                  className={`workflow-platform-node ${selectedNodeId === node.id ? "is-selected" : ""} ${node.status === "pending" ? "is-pending" : ""}`}
                  style={{ left: node.x, top: node.y }}
                  data-testid={`workflow-platform-node-${node.id}`}
                  onPointerDown={(event) => startNodeDrag(event, node)}
                >
                  <button type="button" className="workflow-platform-node__in" onPointerUp={(event) => finishConnection(event, node.id)} aria-label={`连接到 ${node.label}`} />
                  <div className="workflow-platform-node__title">
                    <span>{index + 1}</span>
                    <strong>{node.label}</strong>
                    <em>{node.status === "pending" ? "待人工" : "已完成"}</em>
                  </div>
                  <dl>
                    <div><dt>{node.type.includes("human") ? "状态" : "角色"}</dt><dd>{node.type}</dd></div>
                    <div><dt>证据</dt><dd>{node.stationId}</dd></div>
                  </dl>
                  <button type="button" className="workflow-platform-node__out" onPointerDown={(event) => startConnection(event, node.id)} aria-label={`从 ${node.label} 发起连线`} />
                </article>
              ))}
            </div>
            <div className="workflow-platform__minimap" aria-hidden="true">
              <strong>MINIMAP 拓扑投影</strong>
              <svg viewBox="0 0 170 88">
                <polyline points="20,52 52,68 84,50 118,72 150,58" />
                <circle cx="20" cy="52" r="7" />
                <circle cx="52" cy="68" r="5" />
                <circle cx="84" cy="50" r="5" />
                <circle cx="118" cy="72" r="5" />
                <circle cx="150" cy="58" r="5" className="is-blue" />
                <circle cx="150" cy="40" r="5" className="is-amber" />
              </svg>
            </div>
            <div className="workflow-platform__canvas-toast">
              实时画布：已自适应 {nodes.length} / {nodes.length || 6} 磁吸边 <i /> 活动场景：{selectedSceneTitle}
            </div>
          </div>
        </section>

        <aside className="workflow-platform__right">
          <section className="workflow-platform__profile-card" data-testid="workflow-platform-inspector">
            <header>
              <span>{Math.max(1, nodes.findIndex((node) => node.id === selectedNode?.id) + 1)}</span>
              <div>
                <h2>{selectedNode?.label || "总结 Agent"}</h2>
                <p>选中节点 · PROFILE</p>
              </div>
              <ChevronRight size={22} />
            </header>
            <dl>
              <div><dt>角色定义 (ROLE)</dt><dd>{selectedNode?.type || "观点总结者 (Scribe)"}</dd></div>
              <div><dt>目标规范 (GOAL)</dt><dd>{selectedScenario.goal}</dd></div>
              <div><dt>记忆摘要 (MEMORY DIGEST)</dt><dd>{selectedScenario.output}</dd></div>
              <div><dt>Validation</dt><dd>{validation?.status || graph?.validation_status || "-"}</dd></div>
              <div><dt>Diff</dt><dd>{diff?.diff_id || "等待生成"}</dd></div>
              <div><dt>Version</dt><dd>{activeVersionId || "等待发布"}</dd></div>
              <div><dt>Human Gate</dt><dd>{humanAction?.resulting_run_state || run?.state || "等待运行"}</dd></div>
            </dl>
          </section>

          <section className="workflow-platform__resource-card" data-testid="workflow-platform-executor-panel">
            <div className="workflow-platform__resource-grid">
              <div>
                <h2>挂载工具 (TOOLS)</h2>
                {selectedScenario.resourceMap.slice(0, 2).map((item) => <span key={item} className="workflow-platform__resource">{item}</span>)}
              </div>
              <div>
                <h2>就绪技能 (SKILLS)</h2>
                <span className="workflow-platform__resource">insight-extraction</span>
                <span className="workflow-platform__resource">local-review</span>
              </div>
            </div>
            <h2>MCP 协议引用</h2>
            <p>mcp://consensus-broker-server</p>
            <div className="workflow-platform__executor-actions">
              <button type="button" onClick={() => void runExecutorAction("skill")} disabled={busyAction !== null || !executorRunId}>执行 Skill</button>
              <button type="button" onClick={() => void runExecutorAction("tool")} disabled={busyAction !== null || !executorRunId}>读取 Tool</button>
              <button type="button" onClick={() => void runExecutorAction("mcp")} disabled={busyAction !== null || !executorRunId}>执行 MCP</button>
            </div>
            <p>Contract: {executorContract?.agent_execution_contract.execution_envelope_id || "-"}</p>
            <p>Evidence: {executorEvidence?.route_boundary.status || "-"}</p>
            <p>Last action: {executorAction?.execution.status || "等待操作"}</p>
          </section>

          <section className="workflow-platform__quality-card" data-testid="workflow-platform-exit-status">
            <ShieldCheck size={24} />
            <div>
              <h2>质量门槛规范 {allScenarioPassed ? "（已通过）" : "（待验收）"}</h2>
              <p>{allScenarioPassed ? "三个必验业务场景已通过" : "等待三个必验业务场景全部通过"}</p>
              <p>保留完整的双向分歧、禁止在未达成共识时进行人代或指令合并；断言中必须锚定引用 evidence refs。</p>
            </div>
          </section>
        </aside>
      </section>

      <section className="workflow-platform__bottom">
        <article data-testid="workflow-platform-evidence-panel">
          <h2>Evidence Panel</h2>
          <p>Artifact {evidence?.artifact_refs.length ?? 0} / Trace {evidence?.trace_refs.length ?? 0} / Quality {evidence?.quality_refs.length ?? 0} / Claim {evidence?.claim_refs.length ?? 0} / Redaction {evidence?.redaction_refs.length ?? 0}</p>
          <p>Allowed claim: {evidence?.allowed_claim || "等待运行证据"}</p>
          <p>范围边界：当前只证明 WP-M1 至 WP-M4 的受限验收路径，不扩大为 GA、外部产品对齐或无限制自动执行口径</p>
        </article>
        <article data-testid="workflow-platform-action-log">
          <h2>Action Log</h2>
          <ul>{actionLog.slice(0, 20).map((item) => <li key={item.action_id}>{item.type} / {item.target} / {item.status}</li>)}</ul>
        </article>
        <article>
          <h2>出门状态</h2>
          <p>{allScenarioPassed ? "三个必验业务场景已通过" : "等待三个必验业务场景全部通过"}</p>
        </article>
      </section>
      </section>
    </main>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="workflow-platform-summary-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function mapGraphNodes(graph: PV21WorkflowGraphDTO): PlatformNode[] {
  return graph.nodes.map((node, index) => {
    const saved = node.metadata?.workflow_platform_position;
    const pos = typeof saved === "object" && saved !== null && "x" in saved && "y" in saved ? (saved as { x: number; y: number }) : defaultPositions[index] || { x: 80 + index * 210, y: 170 };
    return {
      id: node.node_id,
      label: node.label,
      type: node.type,
      stationId: node.station_id,
      x: pos.x,
      y: pos.y,
      status: String(node.metadata?.status || graph.validation_status || "ready"),
    };
  });
}

function mapGraphEdges(graph: PV21WorkflowGraphDTO): PlatformEdge[] {
  return graph.edges.map((edge) => ({ id: edge.edge_id, source: edge.source, target: edge.target, status: "saved" }));
}

function mergeNodeData(current: PlatformNode[], next: PlatformNode[]) {
  return next.map((node) => {
    const existing = current.find((item) => item.id === node.id);
    return existing ? { ...node, x: existing.x, y: existing.y } : node;
  });
}
