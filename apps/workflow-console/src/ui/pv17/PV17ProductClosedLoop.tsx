import { useEffect, useMemo, useState } from "react";
import { Activity, FileCheck2, GitBranch, Play, ShieldCheck, SquarePen, Workflow } from "lucide-react";
import type {
  PV17EntityMutationResultDTO,
  PV17EvidenceSummaryDTO,
  PV17ProductConsoleStateDTO,
  PV17PublishResultDTO,
  PV17RuntimeInspectDTO,
  PV17RunConfirmResultDTO,
  PV17StudioWorkflowDTO,
  PV17SystemHealthDTO,
  PV17WorkflowPatchResultDTO,
} from "../../api/types.js";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import "./pv17-product-closed-loop.css";

type LoadState = "loading" | "ready" | "error";

export function PV17ProductClosedLoop() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<PV17SystemHealthDTO | null>(null);
  const [state, setState] = useState<PV17ProductConsoleStateDTO | null>(null);
  const [studio, setStudio] = useState<PV17StudioWorkflowDTO | null>(null);
  const [mutation, setMutation] = useState<PV17EntityMutationResultDTO | null>(null);
  const [patch, setPatch] = useState<PV17WorkflowPatchResultDTO | null>(null);
  const [publish, setPublish] = useState<PV17PublishResultDTO | null>(null);
  const [run, setRun] = useState<PV17RunConfirmResultDTO | null>(null);
  const [inspect, setInspect] = useState<PV17RuntimeInspectDTO | null>(null);
  const [evidence, setEvidence] = useState<PV17EvidenceSummaryDTO | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const selectedWorkflow = state?.workflows[0] || null;
  const selectedVersion = publish
    ? {
        workflow_template_id: publish.publish.workflow_template_id,
        workflow_version_id: publish.publish.workflow_version_id,
        version: publish.publish.version,
      }
    : studio?.versions[0] || null;
  const selectedInstanceId = run?.workflow_instance.workflow_instance_id || state?.active_run?.workflow_instance_id || "";

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoadState("loading");
        const [healthPayload, statePayload] = await Promise.all([
          workflowConsoleClient.getPV17SystemHealth(),
          workflowConsoleClient.getPV17ProductConsoleState(),
        ]);
        if (cancelled) return;
        setHealth(healthPayload);
        setState(statePayload);
        const workflowId = statePayload.workflows[0]?.workflow_template_id;
        if (workflowId) {
          const studioPayload = await workflowConsoleClient.getPV17StudioWorkflow(workflowId);
          if (!cancelled) setStudio(studioPayload);
        }
        if (!cancelled) setLoadState("ready");
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "PV17 数据加载失败");
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "PV17 操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  const cards = useMemo(
    () => [
      { label: "Workspace", value: state?.workspace.display_name || state?.workspace.entity_id || "-", icon: <Activity size={18} /> },
      { label: "Project", value: state?.project.display_name || state?.project.entity_id || "-", icon: <GitBranch size={18} /> },
      { label: "App", value: state?.app.display_name || state?.app.entity_id || "-", icon: <Workflow size={18} /> },
      { label: "Station Agent", value: String(state?.station_agents.length || 0), icon: <ShieldCheck size={18} /> },
      { label: "Workflow", value: selectedWorkflow?.name || selectedWorkflow?.workflow_template_id || "-", icon: <SquarePen size={18} /> },
      { label: "Evidence", value: state?.evidence_summary.status || "-", icon: <FileCheck2 size={18} /> },
    ],
    [selectedWorkflow, state],
  );

  if (loadState === "loading") {
    return <main className="pv17-loop pv17-loop--state" data-testid="pv17-product-closed-loop">正在加载 PV17 产品闭环…</main>;
  }

  if (loadState === "error") {
    return (
      <main className="pv17-loop pv17-loop--state pv17-loop--error" data-testid="pv17-product-closed-loop">
        <strong>PV17 产品闭环加载失败</strong>
        <span>{error}</span>
      </main>
    );
  }

  return (
    <main className="pv17-loop" data-testid="pv17-product-closed-loop">
      <header className="pv17-loop__header">
        <div>
          <span className="pv17-loop__eyebrow">PV17 Product Closed Loop</span>
          <h1>产品闭环审查台</h1>
          <p>setup → Product Console → Mission Studio → confirm run → inspect → evidence</p>
        </div>
        <div className="pv17-loop__status" data-testid="pv17-system-health">
          <span>{health?.status || "unknown"}</span>
          <strong>{health?.gateway_status || "gateway unknown"}</strong>
        </div>
      </header>

      {error ? <div className="pv17-loop__error">{error}</div> : null}

      <section className="pv17-loop__cards" aria-label="PV17 product context">
        {cards.map((card) => (
          <article key={card.label} className="pv17-card">
            {card.icon}
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>

      <section className="pv17-loop__grid">
        <article className="pv17-panel" data-testid="pv17-product-console-state">
          <h2>Product Console</h2>
          <dl>
            <div><dt>Workspace</dt><dd>{state?.workspace.entity_id}</dd></div>
            <div><dt>Project</dt><dd>{state?.project.entity_id}</dd></div>
            <div><dt>App</dt><dd>{state?.app.entity_id}</dd></div>
            <div><dt>Active run</dt><dd>{selectedInstanceId || "等待运行"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null}
            onClick={() =>
              void runAction("entity", async () => {
                const result = await workflowConsoleClient.mutatePV17Entity("station-agents", {
                  entity_kind: "station_agent",
                  operation: "upsert",
                  user_confirmed: true,
                  source: "product_console",
                  idempotency_key: `pv17-agent-${Date.now()}`,
                  payload: {
                    entity_id: "station_agent:pv17-reviewer",
                    display_name: "PV17 审查 Station Agent",
                    role: "reviewer",
                    goal: "审查运行、证据和 No-Go 边界。",
                    model_refs: ["model:redacted"],
                    skill_refs: ["governance.review"],
                    mcp_refs: [],
                  },
                });
                setMutation(result);
              })
            }
          >
            配置 Station Agent
          </button>
          <ResultLine label="mutation" value={mutation?.status} />
        </article>

        <article className="pv17-panel" data-testid="pv17-mission-studio-state">
          <h2>Mission Studio</h2>
          <dl>
            <div><dt>Workflow</dt><dd>{studio?.workflow_template.workflow_template_id || selectedWorkflow?.workflow_template_id}</dd></div>
            <div><dt>Draft revision</dt><dd>{studio?.draft.revision ?? "-"}</dd></div>
            <div><dt>Nodes</dt><dd>{studio?.graph.nodes.length ?? 0}</dd></div>
            <div><dt>Patch queue</dt><dd>{studio?.patch_queue.length ?? 0}</dd></div>
            <div><dt>Patch</dt><dd data-testid="pv17-patch-status">{patch?.status || "等待 patch"}</dd></div>
            <div><dt>Published</dt><dd data-testid="pv17-publish-status">{publish?.status || "等待发布"}</dd></div>
          </dl>
          <div className="pv17-panel__actions">
            <button
              type="button"
              disabled={!selectedWorkflow || busyAction !== null}
              onClick={() =>
                void runAction("patch", async () => {
                  if (!selectedWorkflow) return;
                  const result = await workflowConsoleClient.proposePV17Patch(selectedWorkflow.workflow_template_id, {
                    source: "inspector",
                    intent_type: "inspector_update",
                    operation: "update_station_prompt",
                    workflow_instance_id: selectedInstanceId,
                    payload: { station_id: "station_b", prompt_ref: `pv17.prompt.${Date.now()}` },
                  });
                  setPatch(result);
                  const refreshed = await workflowConsoleClient.getPV17StudioWorkflow(selectedWorkflow.workflow_template_id);
                  setStudio(refreshed);
                })
              }
            >
              提出 Patch
            </button>
            <button
              type="button"
              disabled={!selectedWorkflow || !studio?.draft.revision || busyAction !== null}
              onClick={() =>
                void runAction("publish", async () => {
                  if (!selectedWorkflow || !studio?.draft.revision) return;
                  const result = await workflowConsoleClient.publishPV17Workflow(selectedWorkflow.workflow_template_id, {
                    user_confirmed: true,
                    source: "mission_studio",
                    idempotency_key: `pv17-publish-${Date.now()}`,
                    expected_draft_revision: studio.draft.revision,
                    version: `pv17-${Date.now()}`,
                  });
                  setPublish(result);
                  const refreshed = await workflowConsoleClient.getPV17StudioWorkflow(selectedWorkflow.workflow_template_id);
                  setStudio(refreshed);
                })
              }
            >
              发布版本
            </button>
          </div>
        </article>

        <article className="pv17-panel" data-testid="pv17-runtime-inspect-state">
          <h2>Run Inspect</h2>
          <dl>
            <div><dt>Version</dt><dd>{selectedVersion?.version || "-"}</dd></div>
            <div><dt>Runtime refs</dt><dd>{inspect?.runtime_event_refs.length ?? run?.runtime_event_refs.length ?? 0}</dd></div>
            <div><dt>Trace refs</dt><dd>{inspect?.trace_refs.length ?? run?.trace_refs.length ?? 0}</dd></div>
            <div><dt>Quality refs</dt><dd>{inspect?.quality_refs.length ?? 0}</dd></div>
          </dl>
          <div className="pv17-panel__actions">
            <button
              type="button"
              disabled={!selectedWorkflow || !selectedVersion || busyAction !== null}
              onClick={() =>
                void runAction("run", async () => {
                  if (!selectedWorkflow || !selectedVersion) return;
                  const result = await workflowConsoleClient.confirmPV17Run(selectedWorkflow.workflow_template_id, {
                    user_confirmed: true,
                    source: "run_panel",
                    idempotency_key: `pv17-run-${Date.now()}`,
                    workflow_template_id: selectedWorkflow.workflow_template_id,
                    workflow_version_id: selectedVersion.workflow_version_id,
                  });
                  setRun(result);
                })
              }
            >
              <Play size={16} />
              确认运行
            </button>
            <button
              type="button"
              disabled={!selectedInstanceId || busyAction !== null}
              onClick={() =>
                void runAction("inspect", async () => {
                  const result = await workflowConsoleClient.inspectPV17Instance(selectedInstanceId);
                  setInspect(result);
                })
              }
            >
              Inspect
            </button>
          </div>
        </article>

        <article className="pv17-panel" data-testid="pv17-evidence-review-state">
          <h2>Evidence Review</h2>
          <dl>
            <div><dt>Allowed prefix</dt><dd>{evidence?.route_boundary.allowed_prefix || "/bff/pv17"}</dd></div>
            <div><dt>Missing</dt><dd>{evidence?.missing_evidence.join(", ") || "等待审查"}</dd></div>
            <div><dt>Claims</dt><dd>{evidence?.claims.length ?? 0}</dd></div>
            <div><dt>Redaction</dt><dd>{evidence?.redaction.status || "redacted"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={!selectedInstanceId || busyAction !== null}
            onClick={() =>
              void runAction("evidence", async () => {
                const result = await workflowConsoleClient.getPV17EvidenceSummary(selectedInstanceId);
                setEvidence(result);
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

function ResultLine(props: { label: string; value?: string }) {
  if (!props.value) return null;
  return (
    <p className="pv17-result-line">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </p>
  );
}
