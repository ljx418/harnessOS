import { useCallback, useEffect, useState } from "react";
import "./pv16-product-runtime-hardening.css";

type CheckStatus = "PASS" | "FAIL" | "BLOCKED" | "DENIED";

interface ProductRuntimeState {
  schema_version: string;
  entities: ProductEntities;
  workflow_spec: WorkflowSpecHandoff;
  deployment_profile: DeploymentProfile;
  journey: ProductRuntimeJourney;
}

interface ProductEntities {
  workspace: { workspace_id: string; name: string; audit_ref: string };
  project: { project_id: string; name: string; audit_ref: string };
  app: { app_id: string; name: string; audit_ref: string };
  station_agent: {
    agent_id: string;
    display_name: string;
    role: string;
    goal: string;
    audit_ref: string;
    tool_binding_refs: string[];
    skill_binding_refs: string[];
    mcp_binding_refs: string[];
  };
  ownership_result: string;
  policy_result: string;
  redaction_status: string;
}

interface EntityMutationResult {
  status: CheckStatus;
  reason?: string;
  durable_entity_mutation?: boolean;
  mutated_entity_refs?: string[];
  entities?: ProductEntities;
  audit_ref: string;
}

interface WorkflowSpecHandoff {
  workflow_id: string;
  workflow_version_ref: string;
  workflow_diff_ref: string;
  confirmation_state: string;
  runtime_gateway: string;
  audit_ref: string;
}

interface RuntimeRunInspectReport {
  status: CheckStatus;
  run_ref: string;
  workflow_instance_id: string;
  workflow_version_ref: string;
  runtime_backed: boolean;
  runtime_status: string;
  runtime_event_refs: string[];
  trace_refs: string[];
  artifact_refs: string[];
  quality_refs: string[];
  audit_ref: string;
}

interface RuntimeInspection {
  status: CheckStatus;
  run_ref: string;
  runtime_backed: boolean;
  progress: Array<{ step: string; status: string; evidence_ref: string }>;
  audit_ref: string;
}

interface DeploymentProfile {
  profile_id: string;
  profile_kind: string;
  checks: string[];
  rollback_notes: string;
  not_production_ga: boolean;
  audit_ref: string;
}

interface DeploymentSmoke {
  status: CheckStatus;
  command: string;
  command_output: string[];
  health_checks: Array<{ check_id: string; status: string; output: string }>;
  rollback_notes: string;
  not_production_ga: boolean;
  audit_ref: string;
}

interface ProductRuntimeJourney {
  status: CheckStatus;
  steps: Array<{ step_id: string; label: string; status: string; evidence_ref: string }>;
  allowed_claim: string;
}

export function PV16ProductRuntimeHardening() {
  const [state, setState] = useState<ProductRuntimeState | null>(null);
  const [mutation, setMutation] = useState<EntityMutationResult | null>(null);
  const [denial, setDenial] = useState<EntityMutationResult | null>(null);
  const [runtimeRun, setRuntimeRun] = useState<RuntimeRunInspectReport | null>(null);
  const [runtimeInspect, setRuntimeInspect] = useState<RuntimeInspection | null>(null);
  const [deploymentSmoke, setDeploymentSmoke] = useState<DeploymentSmoke | null>(null);
  const [loadingLabel, setLoadingLabel] = useState("加载 PV16 产品运行时证据");
  const [actionLog, setActionLog] = useState<string[]>(["页面初始化"]);

  const recordAction = useCallback((label: string) => {
    setActionLog((current) => [label, ...current].slice(0, 12));
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadState() {
      try {
        await readJson("/bff/pv16/system/health");
        const payload = await readJson<ProductRuntimeState>("/bff/pv16/product-runtime/state");
        if (cancelled) return;
        setState(payload);
        setLoadingLabel("");
        recordAction("已加载 PV16 BFF DTO");
      } catch {
        if (!cancelled) {
          setLoadingLabel("PV16 BFF 数据加载失败");
          recordAction("PV16 BFF 加载失败");
        }
      }
    }
    void loadState();
    return () => {
      cancelled = true;
    };
  }, [recordAction]);

  async function runEntityMutation() {
    setLoadingLabel("执行产品实体持久化变更");
    const result = await postJson<EntityMutationResult>("/bff/pv16/entities/mutate", {
      scope: {
        workspace_id: state?.entities.workspace.workspace_id,
        project_id: state?.entities.project.project_id,
        app_id: state?.entities.app.app_id,
      },
      policy_ref: "policy:pv16-local-entity-mutation",
      mutation: {
        station_agent_display_name: "质量检查 Agent / PV16",
        goal: "检查总结质量、生成运行证据并保持脱敏审计引用",
      },
    });
    setMutation(result);
    if (result.entities && state) {
      setState({ ...state, entities: result.entities });
    }
    setLoadingLabel("");
    recordAction("PV16-S1 entity mutation PASS");
  }

  async function runOwnershipDenial() {
    setLoadingLabel("执行 ownership denial 负向验收");
    const result = await postJson<EntityMutationResult>("/bff/pv16/entities/mutate", {
      scope: { workspace_id: "ws-forbidden", project_id: "proj-forbidden", app_id: "app-forbidden" },
      policy_ref: "policy:pv16-local-entity-mutation",
      mutation: { station_agent_display_name: "Denied" },
    });
    setDenial(result);
    setLoadingLabel("");
    recordAction("PV16-S1 ownership denial captured");
  }

  async function runRuntimePilot() {
    setLoadingLabel("确认 WorkflowSpec 并检视本地 runtime");
    const result = await postJson<RuntimeRunInspectReport>("/bff/pv16/runtime/confirm-run", {});
    const inspection = await readJson<RuntimeInspection>(`/bff/pv16/runtime/inspect/${encodeURIComponent(result.run_ref)}`);
    setRuntimeRun(result);
    setRuntimeInspect(inspection);
    setLoadingLabel("");
    recordAction("PV16-S2 runtime-backed run/inspect PASS");
  }

  async function runDeploymentSmoke() {
    setLoadingLabel("执行 deployment hardening smoke");
    const result = await postJson<DeploymentSmoke>("/bff/pv16/deployment/hardening-smoke", {});
    setDeploymentSmoke(result);
    setLoadingLabel("");
    recordAction("PV16-S3 deployment hardening smoke PASS");
  }

  const entities = state?.entities;
  const workflow = state?.workflow_spec;
  const journey = state?.journey;

  return (
    <main className="pv16-runtime" data-testid="pv16-product-runtime-hardening">
      <header className="pv16-header">
        <div>
          <p>PV16 产品运行时加固 Pilot</p>
          <h1>Setup → Studio → Run Review → Operations</h1>
        </div>
        <div className="pv16-source" data-testid="pv16-bff-source">
          BFF-backed · runtime-backed pilot · bounded review
        </div>
      </header>

      <section className="pv16-grid">
        <section className="pv16-card pv16-entities" data-testid="pv16-entity-crud">
          <CardTitle title="PV16-S1 产品实体持久化" meta={mutation?.audit_ref || entities?.station_agent.audit_ref || "等待 BFF"} />
          <EntityRows entities={entities} />
          <div className="pv16-button-row">
            <button type="button" data-testid="pv16-run-entity-mutation" onClick={() => void runEntityMutation()}>
              更新 Station Agent
            </button>
            <button type="button" data-testid="pv16-run-ownership-denial" onClick={() => void runOwnershipDenial()}>
              验证越权拒绝
            </button>
          </div>
          <ResultLine label="mutation" value={mutation?.status || "未执行"} />
          <ResultLine label="denial" value={denial?.status || "未执行"} />
        </section>

        <section className="pv16-card" data-testid="pv16-workflow-spec">
          <CardTitle title="WorkflowSpec Handoff" meta={workflow?.audit_ref || "等待 BFF"} />
          <dl className="pv16-dl">
            <div><dt>Workflow</dt><dd>{workflow?.workflow_id || "-"}</dd></div>
            <div><dt>Version</dt><dd>{workflow?.workflow_version_ref || "-"}</dd></div>
            <div><dt>Diff</dt><dd>{workflow?.workflow_diff_ref || "-"}</dd></div>
            <div><dt>Gateway</dt><dd>{workflow?.runtime_gateway || "-"}</dd></div>
          </dl>
          <button type="button" data-testid="pv16-confirm-runtime-run" onClick={() => void runRuntimePilot()}>
            确认并检视运行
          </button>
        </section>

        <section className="pv16-card pv16-runtime-card" data-testid="pv16-runtime-inspect">
          <CardTitle title="PV16-S2 Runtime Inspect" meta={runtimeRun?.audit_ref || "等待执行"} />
          <ResultLine label="status" value={runtimeRun?.status || "未执行"} />
          <ResultLine label="runtime_backed" value={runtimeRun ? String(runtimeRun.runtime_backed) : "未执行"} />
          <p className="pv16-strong">{runtimeRun?.run_ref || "等待 run ref"}</p>
          <EvidenceList title="Trace refs" values={runtimeRun?.trace_refs || []} />
          <EvidenceList title="Artifact refs" values={runtimeRun?.artifact_refs || []} />
          <div className="pv16-progress">
            {(runtimeInspect?.progress || []).map((item) => (
              <article key={item.step}>
                <strong>{item.step}</strong>
                <span>{item.status}</span>
                <small>{item.evidence_ref}</small>
              </article>
            ))}
          </div>
        </section>

        <section className="pv16-card" data-testid="pv16-deployment-hardening">
          <CardTitle title="PV16-S3 Deployment Hardening" meta={deploymentSmoke?.audit_ref || state?.deployment_profile.audit_ref || "等待 BFF"} />
          <p className="pv16-strong">{state?.deployment_profile.profile_kind || "等待 profile"}</p>
          <button type="button" data-testid="pv16-run-deployment-smoke" onClick={() => void runDeploymentSmoke()}>
            运行 hardening smoke
          </button>
          <pre>{(deploymentSmoke?.command_output || ["等待 smoke 输出"]).join("\n")}</pre>
        </section>

        <section className="pv16-card pv16-journey" data-testid="pv16-product-runtime-journey">
          <CardTitle title="PV16-S4 产品旅程" meta={journey?.allowed_claim || "等待 BFF"} />
          {(journey?.steps || []).map((step) => (
            <article key={step.step_id}>
              <strong>{step.label}</strong>
              <span>{step.status}</span>
              <small>{step.evidence_ref}</small>
            </article>
          ))}
          <p className="pv16-boundary">该结论仅表示 pilot ready for review，不等于生产级交付、完整 Studio 或产品级前端完成。</p>
        </section>

        <section className="pv16-card pv16-log" data-testid="pv16-action-log">
          <CardTitle title="动作日志" meta={loadingLabel || "PV16 evidence review ready"} />
          <ol>
            {actionLog.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ol>
        </section>
      </section>
    </main>
  );
}

function EntityRows({ entities }: { entities?: ProductEntities }) {
  const rows = [
    ["Workspace", entities?.workspace.name, entities?.workspace.audit_ref],
    ["Project", entities?.project.name, entities?.project.audit_ref],
    ["App", entities?.app.name, entities?.app.audit_ref],
    ["Station Agent", entities?.station_agent.display_name, entities?.station_agent.audit_ref],
  ];
  return (
    <div className="pv16-entity-list">
      {rows.map(([label, value, audit]) => (
        <article key={label || ""}>
          <span>{label}</span>
          <strong>{value || "等待 BFF"}</strong>
          <small>{audit || "-"}</small>
        </article>
      ))}
    </div>
  );
}

function CardTitle({ title, meta }: { title: string; meta: string }) {
  return (
    <div className="pv16-card-title">
      <span>{title}</span>
      <small>{meta}</small>
    </div>
  );
}

function ResultLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="pv16-result">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EvidenceList({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="pv16-evidence-list">
      <span>{title}</span>
      {(values.length ? values : ["等待证据引用"]).map((value) => (
        <small key={value}>{value}</small>
      ))}
    </div>
  );
}

async function readJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(url: string, data: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(data),
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  return payload as T;
}
