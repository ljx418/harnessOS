import { useEffect, useMemo, useState } from "react";
import { workflowConsoleClient } from "../../api/workflowConsoleClient.js";
import type {
  PV20AgentExecutionActionDTO,
  PV20AgentExecutionContractDTO,
  PV20AgentExecutionEvidenceDTO,
  PV20AgentExecutorStateDTO,
} from "../../api/types.js";
import "./pv20-agent-executor.css";

type BusyAction = "load" | "skill" | "tool" | "mcp" | null;

export function PV20AgentExecutor() {
  const [state, setState] = useState<PV20AgentExecutorStateDTO | null>(null);
  const [contract, setContract] = useState<PV20AgentExecutionContractDTO | null>(null);
  const [evidence, setEvidence] = useState<PV20AgentExecutionEvidenceDTO | null>(null);
  const [lastAction, setLastAction] = useState<PV20AgentExecutionActionDTO | null>(null);
  const [busy, setBusy] = useState<BusyAction>("load");
  const [error, setError] = useState<string | null>(null);

  const runId = state?.workflow_instance.workflow_instance_id || contract?.workflow_instance.workflow_instance_id || "";
  const result = contract?.agent_execution_result || state?.agent_execution_result;
  const refs = useMemo(
    () => [
      { label: "Skill refs", value: result?.skill_call_refs?.length || 0 },
      { label: "Tool refs", value: result?.tool_call_refs?.length || 0 },
      { label: "MCP refs", value: result?.mcp_call_refs?.length || 0 },
      { label: "Approval refs", value: result?.approval_refs?.length || 0 },
    ],
    [result],
  );

  async function refresh() {
    setBusy("load");
    setError(null);
    try {
      const nextState = await workflowConsoleClient.getPV20AgentExecutorState();
      setState(nextState);
      const nextRunId = nextState.workflow_instance.workflow_instance_id;
      const [nextContract, nextEvidence] = await Promise.all([
        workflowConsoleClient.getPV20AgentExecutionContract(nextRunId),
        workflowConsoleClient.getPV20AgentExecutionEvidence(nextRunId),
      ]);
      setContract(nextContract);
      setEvidence(nextEvidence);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PV20 Agent executor 加载失败");
    } finally {
      setBusy(null);
    }
  }

  async function runAction(action: Exclude<BusyAction, "load" | null>) {
    if (!runId) return;
    setBusy(action);
    setError(null);
    try {
      const payload =
        action === "skill"
          ? await workflowConsoleClient.executePV20AgentSkill(runId)
          : action === "tool"
            ? await workflowConsoleClient.executePV20AgentTool(runId)
            : await workflowConsoleClient.executePV20AgentMcp(runId);
      setLastAction(payload);
      const [nextContract, nextEvidence] = await Promise.all([
        workflowConsoleClient.getPV20AgentExecutionContract(runId),
        workflowConsoleClient.getPV20AgentExecutionEvidence(runId),
      ]);
      setContract(nextContract);
      setEvidence(nextEvidence);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PV20 Agent executor 操作失败");
    } finally {
      setBusy(null);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  if (busy === "load" && !state) {
    return <main className="pv20-agent pv20-agent--state" data-testid="pv20-agent-executor">正在加载 PV20 Agent executor evidence…</main>;
  }

  return (
    <main className="pv20-agent" data-testid="pv20-agent-executor">
      <header className="pv20-agent__header">
        <div>
          <span className="pv20-agent__eyebrow">PV20 Complete Agent Executor</span>
          <h1>Agent 执行器审查台</h1>
          <p>contract / skill / tool / MCP / approval evidence</p>
        </div>
        <button type="button" onClick={() => void refresh()} disabled={busy !== null}>
          刷新证据
        </button>
      </header>

      {error ? <div className="pv20-agent__error" data-testid="pv20-agent-error">{error}</div> : null}

      <section className="pv20-agent__cards" aria-label="PV20 executor summary">
        <Metric label="Run" value={runId || "-"} />
        <Metric label="Stage" value={evidence?.allowed_claim ? "bounded review" : state?.stage || "-"} />
        <Metric label="Execution" value={result?.execution_status || "-"} />
        <Metric label="Route" value={evidence?.route_boundary.allowed_prefix || "/bff/pv20"} />
      </section>

      <section className="pv20-agent__layout">
        <article className="pv20-panel" data-testid="pv20-contract-panel">
          <h2>Execution Contract</h2>
          <dl>
            <div><dt>Agent</dt><dd>{contract?.agent_execution_contract.agent_id || "-"}</dd></div>
            <div><dt>StationRun</dt><dd>{contract?.agent_execution_contract.station_run_id || "-"}</dd></div>
            <div><dt>Operation</dt><dd>{contract?.agent_execution_contract.operation || "-"}</dd></div>
            <div><dt>Forbidden</dt><dd>{contract?.agent_execution_contract.forbidden_operation_refs?.slice(0, 3).join(", ") || "-"}</dd></div>
          </dl>
        </article>

        <article className="pv20-panel" data-testid="pv20-result-panel">
          <h2>Execution Refs</h2>
          <div className="pv20-agent__ref-grid">
            {refs.map((item) => <Metric key={item.label} label={item.label} value={String(item.value)} />)}
          </div>
          <div className="pv20-agent__actions">
            <button type="button" onClick={() => void runAction("skill")} disabled={!runId || busy !== null}>执行 Skill</button>
            <button type="button" onClick={() => void runAction("tool")} disabled={!runId || busy !== null}>读取 Tool</button>
            <button type="button" onClick={() => void runAction("mcp")} disabled={!runId || busy !== null}>执行 MCP</button>
          </div>
          <p data-testid="pv20-last-action">{lastAction ? `${lastAction.stage} ${lastAction.execution.status}` : "等待操作"}</p>
        </article>

        <article className="pv20-panel pv20-panel--wide" data-testid="pv20-evidence-panel">
          <h2>Evidence Boundary</h2>
          <p className="pv20-agent__claim">{evidence?.allowed_claim || state?.allowed_claim || "-"}</p>
          <div className="pv20-agent__claims">
            {(evidence?.claim_matrix || []).map((claim) => (
              <div key={claim.claim}>
                <strong>{claim.status}</strong>
                <span>{claim.claim}</span>
              </div>
            ))}
          </div>
          <h3>Not claimed</h3>
          <ul>
            {(evidence?.not_claimed || []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </article>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="pv20-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
