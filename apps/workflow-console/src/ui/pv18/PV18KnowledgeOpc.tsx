import { useEffect, useMemo, useState } from "react";
import { BookOpenCheck, FilePlus2, GitBranch, ListChecks, SearchCheck, ShieldCheck } from "lucide-react";
import type {
  PV18BuildStatusDTO,
  PV18CorrectionPlanDTO,
  PV18EvidenceSummaryDTO,
  PV18KnowledgeSourceDTO,
  PV18KnowledgeStateDTO,
  PV18QualityFeedbackDTO,
  PV18QueryResultDTO,
} from "../../api/types.js";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import "./pv18-knowledge-opc.css";

type LoadState = "loading" | "ready" | "error";

const DEFAULT_SOURCE_TITLE = "HarnessOS PV18 业务验收资料";
const DEFAULT_SOURCE_CONTENT =
  "HarnessOS 通过 BFF DTO、Pack、Connector、Gateway、Artifact、Trace 和 Evidence 边界验证业务工作流。PV18 Knowledge OPC 只验证 bounded 业务闭环，不声明上线运营就绪。";
const DEFAULT_QUERY = "HarnessOS 如何用业务工作流验证平台能力？";

export function PV18KnowledgeOpc() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<PV18KnowledgeStateDTO | null>(null);
  const [source, setSource] = useState<(PV18KnowledgeSourceDTO & { status?: string }) | null>(null);
  const [build, setBuild] = useState<PV18BuildStatusDTO | null>(null);
  const [query, setQuery] = useState<PV18QueryResultDTO | null>(null);
  const [quality, setQuality] = useState<PV18QualityFeedbackDTO | null>(null);
  const [correction, setCorrection] = useState<PV18CorrectionPlanDTO | null>(null);
  const [evidence, setEvidence] = useState<PV18EvidenceSummaryDTO | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [sourceTitleInput, setSourceTitleInput] = useState(DEFAULT_SOURCE_TITLE);
  const [sourceContentInput, setSourceContentInput] = useState(DEFAULT_SOURCE_CONTENT);
  const [queryInput, setQueryInput] = useState(DEFAULT_QUERY);

  async function refresh() {
    const payload = await workflowConsoleClient.getPV18KnowledgeState();
    setState(payload);
  }

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoadState("loading");
        const payload = await workflowConsoleClient.getPV18KnowledgeState();
        if (cancelled) return;
        setState(payload);
        setLoadState("ready");
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "PV18 Knowledge OPC 加载失败");
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
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "PV18 操作失败");
    } finally {
      setBusyAction(null);
    }
  }

  const cards = useMemo(
    () => [
      { label: "Workspace", value: state?.workspace.display_name || "-", icon: <BookOpenCheck size={18} /> },
      { label: "Connector", value: connectorStatus(state), icon: <GitBranch size={18} /> },
      { label: "Sources", value: String((state?.sources.length || 0) + (source && !(state?.sources.length || 0) ? 1 : 0)), icon: <FilePlus2 size={18} /> },
      { label: "Builds", value: String((state?.builds.length || 0) + (build && !(state?.builds.length || 0) ? 1 : 0)), icon: <ListChecks size={18} /> },
      { label: "Queries", value: String((state?.queries.length || 0) + (query && !(state?.queries.length || 0) ? 1 : 0)), icon: <SearchCheck size={18} /> },
      { label: "Evidence", value: evidence?.status || state?.evidence_summary.status || "-", icon: <ShieldCheck size={18} /> },
    ],
    [build, evidence, query, source, state],
  );

  if (loadState === "loading") {
    return <main className="pv18-opc pv18-opc--state" data-testid="pv18-knowledge-opc">正在加载 PV18 Knowledge OPC…</main>;
  }

  if (loadState === "error") {
    return (
      <main className="pv18-opc pv18-opc--state pv18-opc--error" data-testid="pv18-knowledge-opc">
        <strong>PV18 Knowledge OPC 加载失败</strong>
        <span>{error}</span>
      </main>
    );
  }

  return (
    <main className="pv18-opc" data-testid="pv18-knowledge-opc">
      <header className="pv18-opc__header">
        <div>
          <span className="pv18-opc__eyebrow">PV18 Knowledge OPC</span>
          <h1>知识运营工作流台</h1>
          <p>workspace → source → build → query → citation → quality → correction → evidence</p>
        </div>
        <div className="pv18-opc__status" data-testid="pv18-platform-generality">
          <span>平台红线</span>
          <strong>{evidence?.platform_generality?.status || "通用平台不定制"}</strong>
        </div>
      </header>

      {error ? <div className="pv18-opc__error">{error}</div> : null}

      <section className="pv18-opc__cards" aria-label="PV18 Knowledge OPC context">
        {cards.map((card) => (
          <article key={card.label} className="pv18-card">
            {card.icon}
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </article>
        ))}
      </section>

      <section className="pv18-opc__grid">
        <article className="pv18-panel" data-testid="pv18-workspace-state">
          <h2>Workspace</h2>
          <dl>
            <div><dt>Workspace</dt><dd>{state?.workspace.workspace_id}</dd></div>
            <div><dt>Scope</dt><dd>{String(state?.scope.project_id || "-")}</dd></div>
            <div><dt>Boundary</dt><dd>{state?.workspace.data_boundary}</dd></div>
            <div><dt>Connector</dt><dd>{state?.connector_health.connector_id}</dd></div>
            <div><dt>Execution</dt><dd>{state?.connector_health.execution_mode || "-"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null}
            onClick={() =>
              void runAction("workspace", async () => {
                await workflowConsoleClient.upsertPV18KnowledgeWorkspace({ display_name: "PV18 Knowledge OPC Workspace" });
              })
            }
          >
            准备 Workspace
          </button>
        </article>

        <article className="pv18-panel" data-testid="pv18-source-build-state">
          <h2>Source / Build</h2>
          <label className="pv18-field">
            <span>Source title</span>
            <input
              data-testid="pv18-source-title-input"
              value={sourceTitleInput}
              onChange={(event) => setSourceTitleInput(event.target.value)}
            />
          </label>
          <label className="pv18-field">
            <span>Source content</span>
            <textarea
              data-testid="pv18-source-content-input"
              rows={7}
              value={sourceContentInput}
              onChange={(event) => setSourceContentInput(event.target.value)}
            />
          </label>
          <dl>
            <div><dt>Source</dt><dd>{sourceTitle(source, state) || "等待导入"}</dd></div>
            <div><dt>Artifact refs</dt><dd>{source?.artifact_refs.length ?? state?.sources[0]?.artifact_refs.length ?? 0}</dd></div>
            <div><dt>Build</dt><dd data-testid="pv18-build-status">{build?.status || state?.builds[0]?.status || "等待 build"}</dd></div>
            <div><dt>Next</dt><dd>{build?.next_actions?.[0] || state?.builds[0]?.next_actions?.[0] || "导入 source"}</dd></div>
          </dl>
          <div className="pv18-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null || !sourceContentInput.trim()}
              onClick={() =>
                void runAction("source", async () => {
                  const result = await workflowConsoleClient.importPV18KnowledgeSource({
                    title: sourceTitleInput.trim() || DEFAULT_SOURCE_TITLE,
                    content: sourceContentInput.trim(),
                  });
                  setSource(result);
                })
              }
            >
              导入 Source
            </button>
            <button
              type="button"
              disabled={busyAction !== null}
              onClick={() =>
                void runAction("build", async () => {
                  const result = await workflowConsoleClient.startPV18KnowledgeBuild({ mode: "bounded_review" });
                  setBuild(result);
                })
              }
            >
              启动 Build
            </button>
          </div>
        </article>

        <article className="pv18-panel" data-testid="pv18-query-citation-state">
          <h2>Query / Citation</h2>
          <label className="pv18-field">
            <span>Question</span>
            <textarea
              data-testid="pv18-query-input"
              rows={4}
              value={queryInput}
              onChange={(event) => setQueryInput(event.target.value)}
            />
          </label>
          <dl>
            <div><dt>Query</dt><dd>{query?.query_id || "等待提问"}</dd></div>
            <div><dt>Citation</dt><dd data-testid="pv18-citation-status">{query?.citation_coverage.status || "等待 citation"}</dd></div>
            <div><dt>Sources</dt><dd>{query?.source_refs.length ?? 0}</dd></div>
            <div><dt>Artifacts</dt><dd>{query?.artifact_refs.length ?? 0}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null || !queryInput.trim()}
            onClick={() =>
              void runAction("query", async () => {
                const result = await workflowConsoleClient.queryPV18Knowledge({ query: queryInput.trim() || DEFAULT_QUERY });
                setQuery(result);
              })
            }
          >
            提问并生成引用
          </button>
        </article>

        <article className="pv18-panel" data-testid="pv18-quality-correction-state">
          <h2>Quality / Correction</h2>
          <dl>
            <div><dt>Quality</dt><dd>{quality?.quality_status || "等待质量检查"}</dd></div>
            <div><dt>Correction</dt><dd data-testid="pv18-correction-status">{correction?.status || "等待修正计划"}</dd></div>
            <div><dt>Human review</dt><dd>{correction ? String(correction.requires_human_review) : "-"}</dd></div>
            <div><dt>Auto publish</dt><dd>{correction ? String(correction.auto_publish_allowed) : "-"}</dd></div>
          </dl>
          <div className="pv18-panel__actions">
            <button
              type="button"
              disabled={busyAction !== null}
              onClick={() =>
                void runAction("quality", async () => {
                  const result = await workflowConsoleClient.createPV18QualityFeedback({ low_signal_sources: [], issues: [] });
                  setQuality(result);
                })
              }
            >
              质量检查
            </button>
            <button
              type="button"
              disabled={busyAction !== null}
              onClick={() =>
                void runAction("correction", async () => {
                  const result = await workflowConsoleClient.createPV18CorrectionPlan({});
                  setCorrection(result);
                })
              }
            >
              生成修正计划
            </button>
          </div>
        </article>

        <article className="pv18-panel pv18-panel--wide" data-testid="pv18-evidence-state">
          <h2>Evidence Review</h2>
          <dl>
            <div><dt>Allowed prefix</dt><dd>{evidence?.route_boundary.allowed_prefix || "/bff/pv18/knowledge"}</dd></div>
            <div><dt>Missing</dt><dd>{evidence?.missing_evidence.join(", ") || state?.evidence_summary.missing_evidence.join(", ") || "等待审查"}</dd></div>
            <div><dt>Claims</dt><dd>{evidence?.claims.length ?? state?.evidence_summary.claims.length ?? 0}</dd></div>
            <div><dt>Redaction</dt><dd>{evidence?.redaction.status || "redacted"}</dd></div>
          </dl>
          <button
            type="button"
            disabled={busyAction !== null}
            onClick={() =>
              void runAction("evidence", async () => {
                const result = await workflowConsoleClient.getPV18EvidenceSummary();
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

function sourceTitle(source: (PV18KnowledgeSourceDTO & { status?: string }) | null, state: PV18KnowledgeStateDTO | null): string {
  const current = source?.source_reference.title || state?.sources[0]?.source_reference?.title;
  return typeof current === "string" ? current : "";
}

function connectorStatus(state: PV18KnowledgeStateDTO | null): string {
  if (!state) return "-";
  const mode = state.connector_health.execution_mode;
  const real = state.connector_health.real_data_service;
  if (mode) {
    return real ? `${state.connector_health.status} / real` : `${state.connector_health.status} / ${mode}`;
  }
  return state.connector_health.status;
}
