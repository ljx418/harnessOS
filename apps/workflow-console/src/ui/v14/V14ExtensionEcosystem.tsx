import { useCallback, useEffect, useMemo, useState } from "react";
import "./v14-extension-ecosystem.css";

const APPROVED_PACKAGE_ID = "pkg-v14-tool-quality-review-pack";
const UNSAFE_PACKAGE_ID = "pkg-v14-unsafe-shell-executor";
const AGENT_ID = "agent-v12-quality-reviewer-real";

type ExtensionPackage = {
  schema_version: string;
  package_id: string;
  display_name: string;
  package_kind: "plugin" | "skill" | "tool_capability" | "mcp_connector";
  publisher: string;
  version: string;
  trust_level: string;
  status: string;
  requested_permissions: string[];
  required_credential_refs: string[];
  redacted_config_refs: string[];
  capability_refs: string[];
  scope_requirements: string[];
  blocked_fields?: string[];
  audit_ref: string;
};

type CompatibilityDecision = {
  schema_version: string;
  package_id: string;
  status: "approved" | "denied";
  compatible: boolean;
  reasons: string[];
  blocked_permissions: string[];
  required_scope: ActivationScope;
  runtime_backed: boolean;
  audit_ref: string;
};

type ActivationScope = {
  workspace_id: string;
  project_id: string;
  app_id: string;
  agent_id: string;
  station_id: string;
};

type InstallDecision = {
  schema_version: string;
  package_id: string;
  decision: string;
  scope: ActivationScope;
  requires_user_confirmation?: boolean;
  runtime_backed: boolean;
  audit_ref: string;
};

type ActivationDecision = {
  schema_version: string;
  package_id: string;
  decision: string;
  scope: ActivationScope;
  active_capability_refs: string[];
  global_activation: boolean;
  runtime_backed: boolean;
  audit_ref: string;
};

type CapabilityBinding = {
  schema_version: string;
  agent_id: string;
  station_id: string;
  scope: ActivationScope;
  bound_capabilities: Array<{
    capability_ref: string;
    package_id: string;
    activation_ref: string;
    allowed_actions: string[];
  }>;
  denied_global_capabilities: string[];
  runtime_backed: boolean;
  audit_ref: string;
};

type UnsafeDenial = {
  schema_version: string;
  package_id: string;
  status: string;
  denial_reason: string;
  blocked_fields: string[];
  blocked_permissions: string[];
  active_capability_created: boolean;
  runtime_backed: boolean;
  audit_ref: string;
};

type AuditRef = {
  schema_version: string;
  audit_ref: string;
  status: string;
  policy_refs: string[];
  redaction_status: string;
  runtime_backed: boolean;
};

const fallbackScope: ActivationScope = {
  workspace_id: "ws-v12-technical-content-real",
  project_id: "proj-v12-local-knowledge-real",
  app_id: "app-v12-markdown-workflow-real",
  agent_id: AGENT_ID,
  station_id: "quality_check",
};

export function V14ExtensionEcosystem() {
  const [packages, setPackages] = useState<ExtensionPackage[]>([]);
  const [selectedPackageId, setSelectedPackageId] = useState(APPROVED_PACKAGE_ID);
  const [selectedPackage, setSelectedPackage] = useState<ExtensionPackage | null>(null);
  const [compatibility, setCompatibility] = useState<CompatibilityDecision | null>(null);
  const [unsafeCompatibility, setUnsafeCompatibility] = useState<CompatibilityDecision | null>(null);
  const [installDecision, setInstallDecision] = useState<InstallDecision | null>(null);
  const [activationDecision, setActivationDecision] = useState<ActivationDecision | null>(null);
  const [binding, setBinding] = useState<CapabilityBinding | null>(null);
  const [unsafeDenial, setUnsafeDenial] = useState<UnsafeDenial | null>(null);
  const [auditRef, setAuditRef] = useState<AuditRef | null>(null);
  const [loadingLabel, setLoadingLabel] = useState("加载 V14 扩展生态数据");
  const [actionLog, setActionLog] = useState<string[]>(["页面初始化"]);

  const selectedScope = useMemo(() => compatibility?.required_scope || fallbackScope, [compatibility]);

  const recordAction = useCallback((label: string) => {
    setActionLog((current) => [label, ...current].slice(0, 10));
  }, []);

  const loadPackage = useCallback(
    async (packageId: string) => {
      const [detailResponse, compatibilityResponse] = await Promise.all([
        fetch(`/bff/v14/extensions/packages/${packageId}`),
        fetch(`/bff/v14/extensions/packages/${packageId}/compatibility-check`, { method: "POST" }),
      ]);
      const detail = (await detailResponse.json()) as ExtensionPackage;
      const decision = (await compatibilityResponse.json()) as CompatibilityDecision;
      setSelectedPackage(detail);
      setCompatibility(decision);
      setSelectedPackageId(packageId);
      recordAction(`查看扩展：${detail.display_name}`);
    },
    [recordAction],
  );

  useEffect(() => {
    let cancelled = false;
    async function loadRegistry() {
      try {
        await fetch("/bff/v14/system/health");
        const response = await fetch("/bff/v14/extensions/packages");
        const registry = (await response.json()) as { packages: ExtensionPackage[] };
        const unsafeDecisionResponse = await fetch(`/bff/v14/extensions/packages/${UNSAFE_PACKAGE_ID}/compatibility-check`, {
          method: "POST",
        });
        const unsafeDecision = (await unsafeDecisionResponse.json()) as CompatibilityDecision;
        if (cancelled) return;
        setPackages(registry.packages);
        setUnsafeCompatibility(unsafeDecision);
        await loadPackage(APPROVED_PACKAGE_ID);
        setLoadingLabel("");
      } catch {
        if (!cancelled) {
          setLoadingLabel("V14 BFF 数据加载失败");
          recordAction("BFF 加载失败");
        }
      }
    }
    void loadRegistry();
    return () => {
      cancelled = true;
    };
  }, [loadPackage, recordAction]);

  async function activateSelectedPackage() {
    if (!compatibility?.compatible) return;
    setLoadingLabel("写入 scoped activation decision");
    const installResponse = await fetch(`/bff/v14/extensions/packages/${selectedPackageId}/install-decision`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ scope: selectedScope }),
    });
    const install = (await installResponse.json()) as InstallDecision;
    const activationResponse = await fetch(`/bff/v14/extensions/packages/${selectedPackageId}/activate`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ scope: selectedScope }),
    });
    const activation = (await activationResponse.json()) as ActivationDecision;
    const bindingResponse = await fetch(`/bff/v14/agents/${AGENT_ID}/capability-bindings`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ scope: selectedScope, activation_ref: activation.audit_ref }),
    });
    const nextBinding = (await bindingResponse.json()) as CapabilityBinding;
    setInstallDecision(install);
    setActivationDecision(activation);
    setBinding(nextBinding);
    setLoadingLabel("");
    recordAction("已完成受控激活和 Agent 能力绑定");
  }

  async function denyUnsafePackage() {
    setLoadingLabel("记录 unsafe denial");
    const denialResponse = await fetch(`/bff/v14/extensions/packages/${UNSAFE_PACKAGE_ID}/unsafe-denial`, { method: "POST" });
    const denial = (await denialResponse.json()) as UnsafeDenial;
    const auditResponse = await fetch(`/bff/v14/extensions/audit/${encodeURIComponent(denial.audit_ref)}`);
    const audit = (await auditResponse.json()) as AuditRef;
    setUnsafeDenial(denial);
    setAuditRef(audit);
    setLoadingLabel("");
    recordAction("不安全扩展已拒绝并记录审计引用");
  }

  return (
    <main className="v14-extension-ecosystem" data-testid="v14-extension-ecosystem">
      <header className="v14-extension-ecosystem__header">
        <div>
          <p>V14 受治理扩展生态 Pilot</p>
          <h1>扩展注册表与 Agent 能力绑定</h1>
        </div>
        <div className="v14-extension-ecosystem__source" data-testid="v14-bff-source">
          BFF-backed · runtime_backed=false
        </div>
      </header>

      <section className="v14-extension-ecosystem__grid">
        <aside className="v14-card v14-registry" data-testid="v14-package-registry">
          <div className="v14-card__title">
            <span>扩展包</span>
            <small>{packages.length} 个本地审查包</small>
          </div>
          <div className="v14-package-list">
            {packages.map((item) => (
              <button
                key={item.package_id}
                className={item.package_id === selectedPackageId ? "is-selected" : ""}
                type="button"
                onClick={() => void loadPackage(item.package_id)}
              >
                <strong>{item.display_name}</strong>
                <span>{kindLabel(item.package_kind)} · {statusLabel(item.status)}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="v14-card v14-detail" data-testid="v14-package-detail">
          <div className="v14-card__title">
            <span>{selectedPackage?.display_name || "扩展详情"}</span>
            <small>{selectedPackage?.version || "等待选择"}</small>
          </div>
          {selectedPackage ? (
            <div className="v14-detail__content">
              <dl>
                <div>
                  <dt>类型</dt>
                  <dd>{kindLabel(selectedPackage.package_kind)}</dd>
                </div>
                <div>
                  <dt>信任级别</dt>
                  <dd>{selectedPackage.trust_level}</dd>
                </div>
                <div>
                  <dt>审计引用</dt>
                  <dd>{selectedPackage.audit_ref}</dd>
                </div>
              </dl>
              <TagGroup title="权限" values={selectedPackage.requested_permissions} />
              <TagGroup title="能力" values={selectedPackage.capability_refs} />
              <TagGroup title="脱敏配置" values={selectedPackage.redacted_config_refs} />
            </div>
          ) : (
            <p className="v14-muted">{loadingLabel}</p>
          )}
        </section>

        <section className="v14-card v14-compatibility" data-testid="v14-compatibility-status">
          <div className="v14-card__title">
            <span>兼容性决策</span>
            <small>{compatibility?.audit_ref || "等待 BFF 决策"}</small>
          </div>
          <div className={compatibility?.compatible ? "v14-decision is-pass" : "v14-decision is-denied"}>
            {compatibility?.compatible ? "兼容：允许进入 scoped activation" : "拒绝：不可激活"}
          </div>
          <ul className="v14-reasons">
            {(compatibility?.reasons || []).map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          {unsafeCompatibility ? (
            <div className="v14-negative-fixture">
              <strong>负向样例</strong>
              <span>{unsafeCompatibility.reasons.join(" / ")}</span>
            </div>
          ) : null}
        </section>

        <section className="v14-card v14-scope" data-testid="v14-scope-selector">
          <div className="v14-card__title">
            <span>作用域</span>
            <small>不会全局激活</small>
          </div>
          <ScopeRows scope={selectedScope} />
          <button
            className="v14-primary-button"
            data-testid="v14-activate-package"
            type="button"
            disabled={!compatibility?.compatible}
            onClick={() => void activateSelectedPackage()}
          >
            激活到当前 Agent/Station
          </button>
          <p className="v14-muted">发布、运行、执行插件代码均不属于 V14 pilot。</p>
        </section>

        <section className="v14-card v14-binding" data-testid="v14-agent-binding-panel">
          <div className="v14-card__title">
            <span>Agent 能力绑定</span>
            <small>{binding?.audit_ref || "等待激活"}</small>
          </div>
          <div className="v14-binding__status">
            <strong>{activationDecision ? "已 scoped activation" : "未激活"}</strong>
            <span>{installDecision?.decision || "需要兼容性通过后确认"}</span>
          </div>
          <TagGroup title="已绑定能力" values={binding?.bound_capabilities.map((item) => item.capability_ref) || []} />
          <TagGroup title="拒绝的全局能力" values={binding?.denied_global_capabilities || ["tool:unsafe.shell"]} />
        </section>

        <section className="v14-card v14-denial" data-testid="v14-unsafe-denial-panel">
          <div className="v14-card__title">
            <span>Unsafe Denial</span>
            <small>策略拒绝与审计</small>
          </div>
          <button className="v14-danger-button" data-testid="v14-deny-unsafe-package" type="button" onClick={() => void denyUnsafePackage()}>
            拒绝未审 Shell 执行器
          </button>
          <div className="v14-denial__reason" data-testid="v14-denial-reason">
            {unsafeDenial?.denial_reason || "等待拒绝动作"}
          </div>
          <TagGroup title="阻断字段" values={unsafeDenial?.blocked_fields || []} />
          <p className="v14-muted">{auditRef ? `${auditRef.audit_ref} · redaction=${auditRef.redaction_status}` : "审计引用将在拒绝后显示"}</p>
        </section>
      </section>

      <footer className="v14-card v14-log">
        <div>
          <strong>动作日志</strong>
          <span>{loadingLabel || "验收动作已记录"}</span>
        </div>
        <ol data-testid="v14-action-log">
          {actionLog.map((item, index) => (
            <li key={`${item}-${index}`}>{item}</li>
          ))}
        </ol>
      </footer>
    </main>
  );
}

function TagGroup({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="v14-tag-group">
      <span>{title}</span>
      <div>
        {values.length ? values.map((value) => <em key={value}>{value}</em>) : <em>暂无</em>}
      </div>
    </div>
  );
}

function ScopeRows({ scope }: { scope: ActivationScope }) {
  return (
    <dl className="v14-scope-rows">
      {Object.entries(scope).map(([key, value]) => (
        <div key={key}>
          <dt>{scopeLabel(key)}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function kindLabel(kind: ExtensionPackage["package_kind"]) {
  switch (kind) {
    case "plugin":
      return "Plugin";
    case "skill":
      return "Skill";
    case "mcp_connector":
      return "MCP";
    case "tool_capability":
      return "Tool";
  }
}

function statusLabel(status: string) {
  if (status === "approved") return "已审查";
  if (status === "unsafe_denied") return "已拒绝";
  return status;
}

function scopeLabel(key: string) {
  const labels: Record<string, string> = {
    workspace_id: "Workspace",
    project_id: "Project",
    app_id: "App",
    agent_id: "Agent",
    station_id: "Station",
  };
  return labels[key] || key;
}
