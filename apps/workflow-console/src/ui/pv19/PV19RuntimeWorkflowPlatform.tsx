import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, GitBranch, GitCompareArrows, PlayCircle, ShieldCheck, UserCheck } from "lucide-react";
import type {
  PV19EvidenceSummaryDTO,
  PV19GraphValidationDTO,
  PV19HumanActionDTO,
  PV19PublishResultDTO,
  PV19RunDTO,
  PV19WorkbenchStateDTO,
  PV19WorkflowDiffDTO,
  PV19WorkflowGraphDTO,
} from "../../api/types.js";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import "./pv19-runtime-workflow-platform.css";

type LoadState = "loading" | "ready" | "error";

export function PV19RuntimeWorkflowPlatform() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<PV19WorkbenchStateDTO | null>(null);
  const [graph, setGraph] = useState<PV19WorkflowGraphDTO | null>(null);
  const [validation, setValidation] = useState<PV19GraphValidationDTO | null>(null);
  const [diff, setDiff] = useState<PV19WorkflowDiffDTO | null>(null);
  const [publish, setPublish] = useState<PV19PublishResultDTO | null>(null);
  const [run, setRun] = useState<PV19RunDTO | null>(null);
  const [inspect, setInspect] = useState<PV19RunDTO | null>(null);
  const [humanAction, setHumanAction] = useState<PV19HumanActionDTO | null>(null);
  const [evidence, setEvidence] = useState<PV19EvidenceSummaryDTO | null>(null);

  async function refreshState() {
    const payload = await workflowConsoleClient.getPV19WorkbenchState();
    setState(payload);
    return payload;
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoadState("loading");
        const payload = await workflowConsoleClient.getPV19WorkbenchState();
        if (cancelled) return;
        setState(payload);
        const graphPayload = await workflowConsoleClient.getPV19WorkflowGraph(payload.workflow.workflow_template_id);
        if (cancelled) return;
        setGraph(graphPayload);
        setLoadState("ready");
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "PV19 工作台加载失败");
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
      setError(err instanceof Error ? err.message : "PV19 操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  const workflowId = state?.workflow.workflow_template_id || graph?.workflow.workflow_template_id || "";
  const activeRunId = inspect?.workflow_instance.workflow_instance_id || run?.workflow_instance.workflow_instance_id || state?.active_run?.workflow_instance_id || "";
  const statusCards = useMemo(
    () => [
      { label: "Graph", value: graph ? `${graph.graph.nodes.length} 节点 / ${graph.graph.edges.length} 边` : "等待读取", icon: <GitBranch size={18} /> },
      { label: "Validate", value: validation?.status || "等待校验", icon: <CheckCircle2 size={18} /> },
      { label: "Diff", value: diff?.workflow_diff.workflow_patch_id ? "已生成" : "等待生成", icon: <GitCompareArrows size={18} /> },
      { label: "Version", value: publish?.workflow_version_id || state?.active_version?.workflow_version_id || "等待发布", icon: <ShieldCheck size={18} /> },
      { label: "Run", value: inspect?.status?.status || run?.workflow_instance.status || "等待运行", icon: <PlayCircle size={18} /> },
      { label: "Human Gate", value: gateStatus(inspect || run), icon: <UserCheck size={18} /> },
    ],
    [diff, graph, inspect, publish, run, state, validation],
  );

  if (loadState === "loading") {
    return <main className="pv19-platform pv19-platform--state" data-testid="pv19-runtime-platform">正在加载 PV19 完整工作流平台…</main>;
  }

  if (loadState === "error") {
    return (
      <main className="pv19-platform pv19-platform--state pv19-platform--error" data-testid="pv19-runtime-platform">
        <strong>PV19 工作台加载失败</strong>
        <span>{error}</span>
      </main>
    );
  }

  return (
    <main className="pv19-platform" data-testid="pv19-runtime-platform">
      <header className="pv19-platform__header">
        <div>
          <span className="pv19-platform__eyebrow">PV19 Runtime-backed Workflow Studio</span>
          <h1>完整工作流平台验证台</h1>
          <p>读取图 → 校验图 → 生成 Diff → 发布版本 → 运行工作流 → 人工审批 → 审查证据</p>
        </div>
        <div className="pv19-platform__contract" data-testid="pv19-platform-contract">
          <span>通用性红线</span>
          <strong>{graph?.platform_contract.core_customization_allowed === false ? "业务不定制平台核心" : "等待确认"}</strong>
        </div>
      </header>

      {error ? <div className="pv19-platform__error">{error}</div> : null}

      <section className="pv19-platform__cards" aria-label="PV19 status">
        {statusCards.map((card) => (
          <article key={card.label} className="pv19-card">
            {card.icon}
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>

      <section className="pv19-platform__layout">
        <article className="pv19-panel pv19-panel--graph" data-testid="pv19-workflow-graph">
          <div className="pv19-panel__heading">
            <h2>Workflow Graph</h2>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("graph", async () => {
                  setGraph(await workflowConsoleClient.getPV19WorkflowGraph(workflowId));
                })
              }
            >
              读取图
            </button>
          </div>
          <div className="pv19-graph">
            {(graph?.graph.nodes || []).map((node, index, nodes) => (
              <div key={node.station_id} className={`pv19-node ${node.approval_required ? "pv19-node--gate" : ""}`}>
                <div>
                  <span>{node.role || "station"}</span>
                  <strong>{node.name || node.station_id}</strong>
                  <small>{node.station_id}</small>
                </div>
                {index < nodes.length - 1 ? <i aria-hidden="true">→</i> : null}
              </div>
            ))}
          </div>
          <dl>
            <div><dt>Workflow</dt><dd>{workflowId}</dd></div>
            <div><dt>Draft revision</dt><dd>{graph?.draft.revision ?? state?.draft.revision ?? "-"}</dd></div>
            <div><dt>Human gates</dt><dd>{graph?.graph.human_gate_nodes.join(", ") || "等待读取"}</dd></div>
            <div><dt>Runtime backed</dt><dd>{String(graph?.platform_contract.runtime_backed ?? state?.health.runtime_backed ?? "-")}</dd></div>
          </dl>
        </article>

        <article className="pv19-panel" data-testid="pv19-graph-validation">
          <h2>Validate / Diff</h2>
          <dl>
            <div><dt>Validation</dt><dd>{validation?.status || "等待校验"}</dd></div>
            <div><dt>Errors</dt><dd>{validation?.errors.length ?? 0}</dd></div>
            <div><dt>Patch</dt><dd>{diff?.workflow_diff.workflow_patch_id || "等待生成"}</dd></div>
            <div><dt>Boundary</dt><dd>{diff?.workflow_diff.confirmation_boundary || "发布前需人工确认"}</dd></div>
          </dl>
          <div className="pv19-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("validate", async () => {
                  setValidation(await workflowConsoleClient.validatePV19WorkflowGraph(workflowId));
                })
              }
            >
              校验图
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("diff", async () => {
                  setDiff(await workflowConsoleClient.createPV19WorkflowDiff(workflowId));
                })
              }
            >
              生成 Diff
            </button>
          </div>
        </article>

        <article className="pv19-panel" data-testid="pv19-publish-run">
          <h2>Publish / Run</h2>
          <dl>
            <div><dt>Published version</dt><dd>{publish?.workflow_version_id || state?.active_version?.workflow_version_id || "等待发布"}</dd></div>
            <div><dt>Run</dt><dd>{activeRunId || "等待运行"}</dd></div>
            <div><dt>Status</dt><dd data-testid="pv19-run-status">{inspect?.status?.status || run?.workflow_instance.status || "等待运行"}</dd></div>
            <div><dt>Trace refs</dt><dd>{inspect?.trace_refs.length ?? run?.trace_refs.length ?? 0}</dd></div>
          </dl>
          <div className="pv19-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !workflowId}
              onClick={() =>
                void runAction("publish", async () => {
                  const currentState = state || (await refreshState());
                  setPublish(
                    await workflowConsoleClient.publishPV19Workflow(workflowId, {
                      user_confirmed: true,
                      source: "workflow_console",
                      idempotency_key: `pv19-publish-${Date.now()}`,
                      expected_draft_revision: currentState.draft.revision,
                      workflow_patch_id: diff?.workflow_diff.workflow_patch_id,
                      version: `pv19-${Date.now()}`,
                    }),
                  );
                })
              }
            >
              发布版本
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !workflowId || !(publish?.workflow_version_id || state?.active_version?.workflow_version_id)}
              onClick={() =>
                void runAction("run", async () => {
                  const versionId = publish?.workflow_version_id || state?.active_version?.workflow_version_id || "";
                  const started = await workflowConsoleClient.startPV19WorkflowRun(workflowId, {
                    user_confirmed: true,
                    source: "run_panel",
                    idempotency_key: `pv19-run-${Date.now()}`,
                    workflow_version_id: versionId,
                    input: { sample: "knowledge_opc", review_goal: "验证通用工作流平台闭环" },
                  });
                  setRun(started);
                  setInspect(await workflowConsoleClient.inspectPV19Run(started.workflow_instance.workflow_instance_id));
                })
              }
            >
              运行工作流
            </button>
          </div>
        </article>

        <article className="pv19-panel" data-testid="pv19-human-gate">
          <h2>Human Gate</h2>
          <dl>
            <div><dt>Pending gates</dt><dd>{inspect?.pending_human_gates.length ?? run?.pending_human_gates.length ?? 0}</dd></div>
            <div><dt>Approval</dt><dd>{inspect?.pending_human_gates[0]?.approval_id || run?.pending_human_gates[0]?.approval_id || "等待审批"}</dd></div>
            <div><dt>Before</dt><dd>{String(humanAction?.before_state.status || "-")}</dd></div>
            <div><dt>After</dt><dd data-testid="pv19-human-action-after">{String(humanAction?.after_state.status || "-")}</dd></div>
          </dl>
          <div className="pv19-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !activeRunId}
              onClick={() =>
                void runAction("inspect", async () => {
                  setInspect(await workflowConsoleClient.inspectPV19Run(activeRunId));
                })
              }
            >
              Inspect
            </button>
            <button
              type="button"
              disabled={busyAction !== null || !activeRunId || !hasPendingGate(inspect || run)}
              onClick={() =>
                void runAction("approve", async () => {
                  const approved = await workflowConsoleClient.submitPV19HumanAction(activeRunId, {
                    user_confirmed: true,
                    source: "human_gate_panel",
                    idempotency_key: `pv19-approve-${Date.now()}`,
                    action_type: "approve",
                    reason: "人工审查通过",
                  });
                  setHumanAction(approved);
                  setInspect(await workflowConsoleClient.inspectPV19Run(activeRunId));
                })
              }
            >
              人工审批通过
            </button>
          </div>
        </article>

        <article className="pv19-panel pv19-panel--wide" data-testid="pv19-evidence">
          <h2>Evidence Review</h2>
          <dl>
            <div><dt>Allowed prefix</dt><dd>{evidence?.route_boundary.allowed_prefix || "/bff/pv19"}</dd></div>
            <div><dt>Missing</dt><dd>{evidence?.missing_evidence.join(", ") || "等待审查"}</dd></div>
            <div><dt>Claims</dt><dd>{evidence?.claims.length ?? 0}</dd></div>
            <div><dt>Allowed claim</dt><dd>{evidence?.allowed_claim || "等待证据汇总"}</dd></div>
            <div><dt>Generality</dt><dd>{evidence?.platform_generality.status || "等待审查"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null || !activeRunId}
            onClick={() =>
              void runAction("evidence", async () => {
                const latest = await workflowConsoleClient.inspectPV19Run(activeRunId);
                setInspect(latest);
                setEvidence(await workflowConsoleClient.getPV19RunEvidence(activeRunId));
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

function hasPendingGate(run: PV19RunDTO | null): boolean {
  return Boolean(run?.pending_human_gates?.length);
}

function gateStatus(run: PV19RunDTO | null): string {
  if (!run) return "等待运行";
  if (run.pending_human_gates.length > 0) return "等待人工审批";
  if (run.human_gate_refs?.length) return "已记录审批";
  return "无审批记录";
}
