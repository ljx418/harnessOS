import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, GitBranch, GitCompareArrows, History, PlayCircle, RotateCcw, Save, ShieldCheck, UserCheck } from "lucide-react";
import type {
  PV21EvidenceSummaryDTO,
  PV21GraphValidationDTO,
  PV21HumanActionDTO,
  PV21RunDTO,
  PV21StudioStateDTO,
  PV21VersionsDTO,
  PV21WorkflowDiffDTO,
  PV21WorkflowGraphDTO,
  PV21WorkflowVersionDTO,
} from "../../api/types.js";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import "./pv21-complete-workflow-studio.css";

type LoadState = "loading" | "ready" | "error";

export function PV21CompleteWorkflowStudio() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<PV21StudioStateDTO | null>(null);
  const [graph, setGraph] = useState<PV21WorkflowGraphDTO | null>(null);
  const [validation, setValidation] = useState<PV21GraphValidationDTO | null>(null);
  const [diff, setDiff] = useState<PV21WorkflowDiffDTO | null>(null);
  const [versions, setVersions] = useState<PV21VersionsDTO | null>(null);
  const [published, setPublished] = useState<PV21WorkflowVersionDTO | null>(null);
  const [rollback, setRollback] = useState<PV21WorkflowVersionDTO | null>(null);
  const [run, setRun] = useState<PV21RunDTO | null>(null);
  const [humanAction, setHumanAction] = useState<PV21HumanActionDTO | null>(null);
  const [evidence, setEvidence] = useState<PV21EvidenceSummaryDTO | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  async function refreshState() {
    const payload = await workflowConsoleClient.getPV21StudioState();
    setState(payload);
    setGraph(payload.draft_graph);
    return payload;
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoadState("loading");
        const payload = await workflowConsoleClient.getPV21StudioState();
        if (cancelled) return;
        setState(payload);
        setGraph(payload.draft_graph);
        setSelectedNodeId(payload.draft_graph.nodes[0]?.node_id || null);
        setLoadState("ready");
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "PV21 工作台加载失败");
          setLoadState("error");
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function runAction(name: string, action: () => Promise<void>) {
    try {
      setBusyAction(name);
      setError(null);
      await action();
      await refreshState();
    } catch (err) {
      setError(err instanceof Error ? err.message : "PV21 操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  const workflowId = state?.workflow.workflow_template_id || graph?.workflow_id || "";
  const activeVersionId = rollback?.workflow_version_id || versions?.published_version_id || state?.published_version?.workflow_version_id || published?.workflow_version_id || "";
  const activeRunId = run?.run_id || "";
  const selectedNode = graph?.nodes.find((node) => node.node_id === selectedNodeId) || graph?.nodes[0] || null;
  const rollbackCandidate = useMemo(() => {
    const candidates = versions?.rollback_candidates || [];
    return candidates[0] || state?.version_history.find((item) => item.workflow_version_id !== activeVersionId)?.workflow_version_id || "";
  }, [activeVersionId, state, versions]);
  const statusCards = [
    { label: "Graph", value: graph ? `${graph.nodes.length} 节点 / ${graph.edges.length} 边` : "等待读取", icon: <GitBranch size={18} /> },
    { label: "Validate", value: validation?.status || graph?.validation_status || "等待校验", icon: <CheckCircle2 size={18} /> },
    { label: "Diff", value: diff?.diff_id ? "已生成" : "等待生成", icon: <GitCompareArrows size={18} /> },
    { label: "Version", value: activeVersionId || "等待发布", icon: <ShieldCheck size={18} /> },
    { label: "Run", value: run?.state || "等待运行", icon: <PlayCircle size={18} /> },
    { label: "Human Gate", value: humanAction?.resulting_run_state || gateStatus(run), icon: <UserCheck size={18} /> },
  ];

  if (loadState === "loading") {
    return <main className="pv21-studio pv21-studio--state" data-testid="pv21-complete-workflow-studio">正在加载 PV21 完整 Workflow Studio…</main>;
  }

  if (loadState === "error") {
    return (
      <main className="pv21-studio pv21-studio--state pv21-studio--error" data-testid="pv21-complete-workflow-studio">
        <strong>PV21 工作台加载失败</strong>
        <span>{error}</span>
      </main>
    );
  }

  return (
    <main className="pv21-studio" data-testid="pv21-complete-workflow-studio">
      <header className="pv21-studio__header">
        <div>
          <span className="pv21-studio__eyebrow">PV21 Complete Workflow Studio</span>
          <h1>完整 Workflow Studio 候选工作台</h1>
          <p>打开工作台 → 编辑画布 → 校验 → Diff → 发布 → 运行 → 人工交互 → 证据 → 回滚</p>
        </div>
        <div className="pv21-studio__contract" data-testid="pv21-platform-contract">
          <span>平台红线</span>
          <strong>业务不定制 workflow core / Gateway core / App shell</strong>
        </div>
      </header>

      {error ? <div className="pv21-studio__error">{error}</div> : null}

      <section className="pv21-studio__cards" aria-label="PV21 status">
        {statusCards.map((card) => (
          <article key={card.label} className="pv21-card">
            {card.icon}
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>

      <section className="pv21-studio__layout">
        <article className="pv21-panel pv21-panel--library" data-testid="pv21-node-library">
          <h2>节点库</h2>
          {(state?.node_library || []).map((node) => (
            <button key={String(node.node_template_id)} type="button" disabled={busyAction !== null}>
              <span>{String(node.label || node.type)}</span>
              <small>{String(node.description || "")}</small>
            </button>
          ))}
        </article>

        <article className="pv21-panel pv21-panel--canvas" data-testid="pv21-workflow-canvas">
          <div className="pv21-panel__heading">
            <h2>Workflow Graph</h2>
            <button
              type="button"
              disabled={busyAction !== null || !graph || !workflowId}
              onClick={() =>
                void runAction("save-graph", async () => {
                  const nextGraph = {
                    ...graph!,
                    nodes: graph!.nodes.map((node, index) =>
                      index === 0 ? { ...node, params: { ...(node.params || {}), pv21_saved: true }, metadata: { ...(node.metadata || {}), prompt_ref: "pv21.prompt.saved.v1" } } : node,
                    ),
                  };
                  const result = await workflowConsoleClient.savePV21WorkflowGraph(workflowId, nextGraph);
                  setGraph(result.graph);
                  setValidation(result.validation);
                })
              }
            >
              <Save size={16} /> 保存 Draft
            </button>
          </div>
          <div className="pv21-canvas">
            {(graph?.nodes || []).map((node, index, nodes) => (
              <button
                key={node.node_id}
                type="button"
                className={`pv21-node pv21-node--${node.type} ${selectedNode?.node_id === node.node_id ? "pv21-node--active" : ""}`}
                onClick={() => setSelectedNodeId(node.node_id)}
              >
                <span>{node.type}</span>
                <strong>{node.label}</strong>
                <small>{node.station_id}</small>
                {index < nodes.length - 1 ? <i aria-hidden="true">→</i> : null}
              </button>
            ))}
          </div>
          <dl>
            <div><dt>Workflow</dt><dd>{workflowId}</dd></div>
            <div><dt>Draft revision</dt><dd>{graph?.draft_revision ?? "-"}</dd></div>
            <div><dt>Validation</dt><dd>{validation?.status || graph?.validation_status || "-"}</dd></div>
          </dl>
        </article>

        <article className="pv21-panel" data-testid="pv21-inspector">
          <h2>Inspector</h2>
          <dl>
            <div><dt>Node</dt><dd>{selectedNode?.label || "-"}</dd></div>
            <div><dt>Type</dt><dd>{selectedNode?.type || "-"}</dd></div>
            <div><dt>Executor</dt><dd>{String(selectedNode?.executor_binding || "generic")}</dd></div>
            <div><dt>Approval</dt><dd>{String(selectedNode?.policy?.approval_required ?? false)}</dd></div>
          </dl>
          <div className="pv21-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("validate", async () => {
                  setValidation(await workflowConsoleClient.validatePV21WorkflowGraph(workflowId));
                })
              }
            >
              <CheckCircle2 size={16} /> 校验图
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("diff", async () => {
                  setDiff(await workflowConsoleClient.createPV21WorkflowDiff(workflowId, { base_version_id: activeVersionId, draft_revision: graph?.draft_revision }));
                })
              }
            >
              <GitCompareArrows size={16} /> 生成 Diff
            </button>
          </div>
          <p data-testid="pv21-validation-summary">{validation ? `${validation.status} / errors ${validation.errors.length}` : "等待校验"}</p>
        </article>

        <article className="pv21-panel" data-testid="pv21-version-run">
          <h2>版本与运行</h2>
          <dl>
            <div><dt>Diff</dt><dd>{diff?.diff_id || "等待生成"}</dd></div>
            <div><dt>Active version</dt><dd data-testid="pv21-active-version">{activeVersionId || "等待发布"}</dd></div>
            <div><dt>Versions</dt><dd>{versions?.versions.length ?? state?.version_history.length ?? 0}</dd></div>
            <div><dt>Run</dt><dd data-testid="pv21-run-state">{run?.state || "等待运行"}</dd></div>
          </dl>
          <div className="pv21-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("publish", async () => {
                  const result = await workflowConsoleClient.publishPV21Workflow(workflowId, {
                    draft_revision: graph?.draft_revision || 1,
                    diff_id: diff?.diff_id,
                    version: `pv21-${Date.now()}`,
                  });
                  setPublished(result.version);
                  setVersions(await workflowConsoleClient.listPV21WorkflowVersions(workflowId));
                })
              }
            >
              <ShieldCheck size={16} /> 发布版本
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId || !activeVersionId}
              onClick={() =>
                void runAction("run", async () => {
                  setRun(await workflowConsoleClient.startPV21WorkflowRun(workflowId, activeVersionId));
                })
              }
            >
              <PlayCircle size={16} /> 运行工作流
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("versions", async () => {
                  setVersions(await workflowConsoleClient.listPV21WorkflowVersions(workflowId));
                })
              }
            >
              <History size={16} /> 刷新版本
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId || !rollbackCandidate}
              onClick={() =>
                void runAction("rollback", async () => {
                  const result = await workflowConsoleClient.rollbackPV21Workflow(workflowId, rollbackCandidate);
                  setRollback(result.published_version);
                  setVersions(await workflowConsoleClient.listPV21WorkflowVersions(workflowId));
                })
              }
            >
              <RotateCcw size={16} /> 回滚版本
            </button>
          </div>
        </article>

        <article className="pv21-panel" data-testid="pv21-human-gate">
          <h2>人工交互</h2>
          <dl>
            <div><dt>Pending</dt><dd>{run?.pending_human_gates.length ?? 0}</dd></div>
            <div><dt>Gate</dt><dd>{String(run?.current_human_gate?.approval_id || "等待运行")}</dd></div>
            <div><dt>After</dt><dd data-testid="pv21-human-action-after">{humanAction?.resulting_run_state || "-"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null || !activeRunId}
            onClick={() =>
              void runAction("human", async () => {
                const result = await workflowConsoleClient.submitPV21HumanAction(activeRunId, String(run?.current_human_gate?.station_id || ""));
                setHumanAction(result);
                setRun(await workflowConsoleClient.inspectPV21Run(activeRunId));
              })
            }
          >
            <UserCheck size={16} /> 人工审批通过
          </button>
        </article>

        <article className="pv21-panel pv21-panel--evidence" data-testid="pv21-evidence">
          <h2>Evidence Review</h2>
          <dl>
            <div><dt>Allowed prefix</dt><dd>{evidence?.route_boundary.allowed_prefix || "/bff/pv21"}</dd></div>
            <div><dt>No False Green</dt><dd>{evidence?.no_false_green_status || "not_run"}</dd></div>
            <div><dt>Missing refs</dt><dd>{evidence?.missing_refs.join(", ") || "等待审查"}</dd></div>
            <div><dt>Claim</dt><dd>{evidence?.allowed_claim || "等待证据"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null || !activeRunId}
            onClick={() =>
              void runAction("evidence", async () => {
                setEvidence(await workflowConsoleClient.getPV21RunEvidence(activeRunId));
              })
            }
          >
            审查证据
          </button>
        </article>
      </section>
    </main>
  );
}

function gateStatus(run: PV21RunDTO | null) {
  if (!run) return "等待运行";
  if (run.pending_human_gates.length > 0) return "等待人工审批";
  if (run.approval_refs.length > 0) return "已记录审批";
  return run.state || "等待运行";
}
