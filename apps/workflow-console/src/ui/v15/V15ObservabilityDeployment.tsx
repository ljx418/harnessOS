import { useCallback, useEffect, useState } from "react";
import "./v15-observability-deployment.css";

type TraceEvent = {
  event_id: string;
  stage: string;
  status: string;
  label: string;
  evidence_ref: string;
};

type TraceTimeline = {
  schema_version: string;
  events: TraceEvent[];
  audit_ref: string;
  runtime_backed: boolean;
};

type MetricsSnapshot = {
  schema_version: string;
  metrics: Record<string, number | string>;
  audit_ref: string;
  runtime_backed: boolean;
};

type AuditExportPackage = {
  schema_version: string;
  export_ref: string;
  included_evidence_refs: string[];
  redaction_status: string;
  audit_ref: string;
  runtime_backed: boolean;
};

type IncidentTimeline = {
  schema_version: string;
  incidents: Array<{ incident_id: string; severity: string; status: string; summary: string; evidence_ref: string }>;
  audit_ref: string;
  runtime_backed: boolean;
};

type DeploymentProfile = {
  schema_version: string;
  profile_id: string;
  profile_kind: string;
  frontend_base_url_ref: string;
  bff_base_url_ref: string;
  checks: string[];
  rollback_notes: string;
  not_production_ga: boolean;
  audit_ref: string;
};

type HealthCheckResult = {
  schema_version: string;
  status: "PASS" | "FAIL" | "BLOCKED";
  checks: Array<{ check_id: string; status: string; output: string }>;
  not_production_ga: boolean;
  audit_ref: string;
};

type DeploymentSmokeResult = {
  schema_version: string;
  status: "PASS" | "FAIL" | "BLOCKED";
  command: string;
  command_output: string[];
  rollback_notes: string;
  not_production_ga: boolean;
  audit_ref: string;
};

type FinalScenarioMatrix = {
  schema_version: string;
  scenarios: Array<{ scenario_id: string; label: string; status: string; evidence_ref: string }>;
  allowed_claim: string;
  audit_ref: string;
  runtime_backed: boolean;
};

export function V15ObservabilityDeployment() {
  const [traceTimeline, setTraceTimeline] = useState<TraceTimeline | null>(null);
  const [metricsSnapshot, setMetricsSnapshot] = useState<MetricsSnapshot | null>(null);
  const [auditExport, setAuditExport] = useState<AuditExportPackage | null>(null);
  const [incidentTimeline, setIncidentTimeline] = useState<IncidentTimeline | null>(null);
  const [deploymentProfile, setDeploymentProfile] = useState<DeploymentProfile | null>(null);
  const [healthCheck, setHealthCheck] = useState<HealthCheckResult | null>(null);
  const [deploymentSmoke, setDeploymentSmoke] = useState<DeploymentSmokeResult | null>(null);
  const [finalScenarioMatrix, setFinalScenarioMatrix] = useState<FinalScenarioMatrix | null>(null);
  const [loadingLabel, setLoadingLabel] = useState("加载 V15 运维与部署证据");
  const [actionLog, setActionLog] = useState<string[]>(["页面初始化"]);

  const recordAction = useCallback((label: string) => {
    setActionLog((current) => [label, ...current].slice(0, 10));
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadEvidence() {
      try {
        await fetch("/bff/v15/system/health");
        const [trace, metrics, audit, incidents, profile, matrix] = await Promise.all([
          readJson<TraceTimeline>("/bff/v15/observability/trace-timeline"),
          readJson<MetricsSnapshot>("/bff/v15/observability/metrics-snapshot"),
          readJson<AuditExportPackage>("/bff/v15/observability/audit-export"),
          readJson<IncidentTimeline>("/bff/v15/observability/incidents"),
          readJson<DeploymentProfile>("/bff/v15/deployment/profile"),
          readJson<FinalScenarioMatrix>("/bff/v15/final-scenario-matrix"),
        ]);
        if (cancelled) return;
        setTraceTimeline(trace);
        setMetricsSnapshot(metrics);
        setAuditExport(audit);
        setIncidentTimeline(incidents);
        setDeploymentProfile(profile);
        setFinalScenarioMatrix(matrix);
        setLoadingLabel("");
        recordAction("已加载 V15 只读证据 DTO");
      } catch {
        if (!cancelled) {
          setLoadingLabel("V15 BFF 数据加载失败");
          recordAction("BFF 加载失败");
        }
      }
    }
    void loadEvidence();
    return () => {
      cancelled = true;
    };
  }, [recordAction]);

  async function runHealthCheck() {
    setLoadingLabel("执行本地健康检查");
    const result = await postJson<HealthCheckResult>("/bff/v15/deployment/health-check", {});
    setHealthCheck(result);
    setLoadingLabel("");
    recordAction("本地健康检查 PASS");
  }

  async function runDeploymentSmoke() {
    setLoadingLabel("执行 bounded deployment smoke");
    const result = await postJson<DeploymentSmokeResult>("/bff/v15/deployment/smoke", {});
    setDeploymentSmoke(result);
    setLoadingLabel("");
    recordAction("bounded deployment smoke PASS");
  }

  return (
    <main className="v15-observability-deployment" data-testid="v15-observability-deployment">
      <header className="v15-header">
        <div>
          <p>V15 运维 / 部署 / 最终交互基线</p>
          <h1>前端交互基线审查台</h1>
        </div>
        <div className="v15-source" data-testid="v15-bff-source">
          BFF-backed · read-only · not production GA
        </div>
      </header>

      <section className="v15-grid">
        <section className="v15-card v15-trace" data-testid="v15-trace-timeline">
          <CardTitle title="Trace Timeline" meta={traceTimeline?.audit_ref || "等待 BFF"} />
          <div className="v15-timeline">
            {(traceTimeline?.events || []).map((event) => (
              <article key={event.event_id}>
                <strong>{event.stage} · {event.status}</strong>
                <span>{event.label}</span>
                <small>{event.evidence_ref}</small>
              </article>
            ))}
          </div>
        </section>

        <section className="v15-card" data-testid="v15-metrics-snapshot">
          <CardTitle title="Metrics Snapshot" meta={metricsSnapshot?.audit_ref || "等待 BFF"} />
          <div className="v15-metrics">
            {Object.entries(metricsSnapshot?.metrics || {}).map(([key, value]) => (
              <div key={key}>
                <span>{metricLabel(key)}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="v15-card" data-testid="v15-audit-export">
          <CardTitle title="Audit Export" meta={auditExport?.redaction_status || "等待 BFF"} />
          <p className="v15-strong">{auditExport?.export_ref || "尚未加载"}</p>
          <EvidenceList values={auditExport?.included_evidence_refs || []} />
        </section>

        <section className="v15-card" data-testid="v15-incident-timeline">
          <CardTitle title="Incident Timeline" meta={incidentTimeline?.audit_ref || "等待 BFF"} />
          {(incidentTimeline?.incidents || []).map((incident) => (
            <article className="v15-incident" key={incident.incident_id}>
              <strong>{incident.severity} · {incident.status}</strong>
              <span>{incident.summary}</span>
            </article>
          ))}
        </section>

        <section className="v15-card v15-deployment">
          <CardTitle title="Deployment Profile" meta={deploymentProfile?.profile_kind || "等待 BFF"} />
          <dl>
            <div>
              <dt>Frontend</dt>
              <dd>{deploymentProfile?.frontend_base_url_ref || "-"}</dd>
            </div>
            <div>
              <dt>BFF</dt>
              <dd>{deploymentProfile?.bff_base_url_ref || "-"}</dd>
            </div>
            <div>
              <dt>Rollback</dt>
              <dd>{deploymentProfile?.rollback_notes || "-"}</dd>
            </div>
          </dl>
          <button data-testid="v15-run-health-check" type="button" onClick={() => void runHealthCheck()}>
            运行健康检查
          </button>
          <button data-testid="v15-run-deployment-smoke" type="button" onClick={() => void runDeploymentSmoke()}>
            运行部署烟测
          </button>
        </section>

        <section className="v15-card" data-testid="v15-health-result">
          <CardTitle title="Health Result" meta={healthCheck?.audit_ref || "等待执行"} />
          <p className={healthCheck?.status === "PASS" ? "v15-status-pass" : "v15-muted"}>{healthCheck?.status || "未执行"}</p>
          {(healthCheck?.checks || []).map((check) => (
            <div className="v15-check" key={check.check_id}>
              <strong>{check.check_id} · {check.status}</strong>
              <span>{check.output}</span>
            </div>
          ))}
        </section>

        <section className="v15-card" data-testid="v15-smoke-output">
          <CardTitle title="Smoke Output" meta={deploymentSmoke?.audit_ref || "等待执行"} />
          <p className="v15-strong">{deploymentSmoke?.command || "未执行"}</p>
          <pre>{(deploymentSmoke?.command_output || ["等待 bounded smoke 输出"]).join("\n")}</pre>
        </section>

        <section className="v15-card v15-matrix" data-testid="v15-final-scenario-matrix">
          <CardTitle title="Final Scenario Matrix" meta={finalScenarioMatrix?.allowed_claim || "等待 BFF"} />
          {(finalScenarioMatrix?.scenarios || []).map((scenario) => (
            <article key={scenario.scenario_id}>
              <strong>{scenario.label}</strong>
              <span>{scenario.status}</span>
              <small>{scenario.evidence_ref}</small>
            </article>
          ))}
        </section>
      </section>

      <footer className="v15-card v15-log">
        <div>
          <strong>动作日志</strong>
          <span>{loadingLabel || "V15 evidence review ready"}</span>
        </div>
        <ol data-testid="v15-action-log">
          {actionLog.map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ol>
      </footer>
    </main>
  );
}

function CardTitle({ title, meta }: { title: string; meta: string }) {
  return (
    <div className="v15-card-title">
      <span>{title}</span>
      <small>{meta}</small>
    </div>
  );
}

function EvidenceList({ values }: { values: string[] }) {
  return (
    <ul className="v15-evidence-list">
      {values.map((value) => (
        <li key={value}>{value}</li>
      ))}
    </ul>
  );
}

async function readJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${url}`);
  return (await response.json()) as T;
}

async function postJson<T>(url: string, data: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error(`Request failed: ${url}`);
  return (await response.json()) as T;
}

function metricLabel(key: string) {
  const labels: Record<string, string> = {
    accepted_stage_count: "已验收阶段",
    v15_scenario_count: "V15 场景",
    failed_scenario_count: "失败场景",
    blocked_scenario_count: "阻塞场景",
    redaction_scan_status: "脱敏扫描",
    claim_scan_status: "声明扫描",
  };
  return labels[key] || key;
}
