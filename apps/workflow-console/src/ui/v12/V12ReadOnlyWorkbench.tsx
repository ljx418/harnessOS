import { useEffect, useState } from "react";
import { Activity, Bot, Boxes, CheckCircle2, ChevronDown, CircleSlash, FileText, Gauge, GitBranch, Info, KeyRound, LayoutGrid, Link2, MessageSquareText, Network, Play, Plus, Search, ShieldCheck, Sparkles } from "lucide-react";
import { v41WorkflowNodes } from "../../fixtures/workflowStudioFixtures.js";
import { Badge } from "../../components/ui/badge.js";
import { Button } from "../../components/ui/button.js";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card.js";
import { ScrollArea } from "../../components/ui/scroll-area.js";
import { Separator } from "../../components/ui/separator.js";
import { Tabs, TabsList, TabsTrigger } from "../../components/ui/tabs.js";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../../components/ui/tooltip.js";
import { WorkflowCanvas } from "../workflow/WorkflowCanvas.js";
import "./v12-readonly-workbench.css";

const selectedNode = v41WorkflowNodes.find((node) => node.id === "quality_check") ?? v41WorkflowNodes[0];
const fallbackEntityItems = [
  { label: "工作空间", value: "技术内容工作室", icon: Boxes },
  { label: "项目", value: "本地知识总结项目", icon: LayoutGrid },
  { label: "应用", value: "Markdown 工作流应用", icon: Bot },
  { label: "服务账号", value: "svc-v12-readonly-ref", icon: KeyRound },
  { label: "证据范围", value: "read_only_canvas_fixture", icon: ShieldCheck },
];

const toolbarActions = [
  { label: "添加节点", icon: Plus, reason: "V12 只读画布阶段：需要 V13 WorkflowDiff 确认后才允许编辑" },
  { label: "发布 / 运行", icon: Play, reason: "V12 不允许发布或运行工作流" },
];

const inspectorRows = [
  ["选中节点", selectedNode.name],
  ["Agent / Role", selectedNode.type],
  ["状态", selectedNode.status],
  ["输入证据", selectedNode.inputArtifact],
  ["输出证据", selectedNode.outputArtifact],
  ["质量状态", selectedNode.qualityStatus],
];

interface V12WorkbenchBffState {
  healthStatus: string;
  workspaceName: string;
  projectName: string;
  appName: string;
  serviceAccountRef: string;
  canvasReadModelId: string;
  selectedNodeRef: string;
  inspectorGoal: string;
  inspectorAuditRef: string;
  goalSummary: string;
  proposalState: string;
  workflowDiffRef: string;
  proposalEvents: Array<{ event_id: string; label: string; state: string; risk_level: string }>;
  interactionStates: Array<{ state: string; visible: boolean; description: string }>;
  disabledReasons: Array<{ action_id: string; label: string; reason: string }>;
  handoffState: string;
  loadedFromBff: boolean;
}

const fallbackBffState: V12WorkbenchBffState = {
  healthStatus: "fallback",
  workspaceName: "技术内容工作室",
  projectName: "本地知识总结项目",
  appName: "Markdown 工作流应用",
  serviceAccountRef: "svc-v12-readonly-ref",
  canvasReadModelId: "canvas-v12-local-markdown-summary",
  selectedNodeRef: "quality_check",
  inspectorGoal: "检查总结质量并生成可审计 quality report",
  inspectorAuditRef: "audit://v12/fallback/inspector-quality-check",
  goalSummary: "把本地 Markdown 技术文档总结成可审计工作流",
  proposalState: "awaiting_user_confirmation",
  workflowDiffRef: "diff-v12-readonly-proposal-ref",
  proposalEvents: [
    { event_id: "fallback-goal", label: "目标已接收", state: "goal_received", risk_level: "low" },
    { event_id: "fallback-proposal", label: "WorkflowDiff 提案已生成", state: "proposal_ready", risk_level: "medium" },
  ],
  interactionStates: [
    { state: "selected", visible: true, description: "quality_check 节点高亮并同步 Inspector" },
    { state: "denied", visible: true, description: "发布/运行动作被边界策略阻止" },
  ],
  disabledReasons: toolbarActions.map((action) => ({ action_id: action.label, label: action.label, reason: action.reason })),
  handoffState: "not_confirmed",
  loadedFromBff: false,
};

export function V12ReadOnlyWorkbench() {
  const [bffState, setBffState] = useState<V12WorkbenchBffState>(fallbackBffState);

  useEffect(() => {
    let cancelled = false;

    async function loadV12BffProjection() {
      try {
        const health = await fetch("/bff/v12/system/health").then((response) => response.json());
        const workspaces = await fetch("/bff/v12/workspaces").then((response) => response.json());
        const workspace = workspaces.workspaces[0];
        const projects = await fetch(`/bff/v12/workspaces/${workspace.workspace_id}/projects`).then((response) => response.json());
        const project = projects.projects[0];
        const apps = await fetch(`/bff/v12/projects/${project.project_id}/apps`).then((response) => response.json());
        const app = apps.apps[0];
        await fetch(`/bff/v12/apps/${app.app_id}/station-agents`).then((response) => response.json());
        const canvas = await fetch(`/bff/v12/apps/${app.app_id}/canvas`).then((response) => response.json());
        const selected = canvas.nodes.find((node: { node_id: string }) => node.node_id === "quality_check") ?? canvas.nodes[0];
        const inspector = await fetch(`/bff/v12/canvas/nodes/${selected.node_id}/inspector`).then((response) => response.json());
        const conversations = await fetch(`/bff/v12/apps/${app.app_id}/workbench/conversations`).then((response) => response.json());
        const proposalTimeline = conversations.proposal_timeline;
        const workflowDiff = await fetch(`/bff/v12/workflow-diff/${proposalTimeline.workflow_diff_proposal_ref}`).then((response) => response.json());
        const interactionTrace = await fetch(`/bff/v12/apps/${app.app_id}/interaction-trace`).then((response) => response.json());
        if (!cancelled) {
          setBffState({
            healthStatus: health.status,
            workspaceName: workspace.name,
            projectName: project.name,
            appName: app.name,
            serviceAccountRef: "svc-v12-readonly-redacted-ref",
            canvasReadModelId: canvas.canvas_read_model_id,
            selectedNodeRef: inspector.selected_node_ref,
            inspectorGoal: inspector.goal,
            inspectorAuditRef: inspector.audit_ref,
            goalSummary: conversations.conversations[0]?.goal_summary ?? fallbackBffState.goalSummary,
            proposalState: proposalTimeline.current_state,
            workflowDiffRef: workflowDiff.proposal_id,
            proposalEvents: proposalTimeline.events,
            interactionStates: interactionTrace.state_fixtures,
            disabledReasons: interactionTrace.disabled_action_reasons,
            handoffState: "not_confirmed",
            loadedFromBff: true,
          });
        }
      } catch (error) {
        console.warn("Failed to load V12 BFF projection; using read-only fallback.", error);
      }
    }

    void loadV12BffProjection();
    return () => {
      cancelled = true;
    };
  }, []);

  async function postProposalDecision(action: "revise" | "reject" | "confirm-handoff") {
    const response = await fetch(`/bff/v12/workbench/proposals/${bffState.workflowDiffRef}/${action}`, { method: "POST" });
    const result = await response.json();
    setBffState((current) => ({
      ...current,
      proposalState: result.decision ?? result.handoff_state ?? current.proposalState,
      handoffState: result.handoff_state ?? current.handoffState,
    }));
  }

  const entityItems = [
    { ...fallbackEntityItems[0], value: bffState.workspaceName },
    { ...fallbackEntityItems[1], value: bffState.projectName },
    { ...fallbackEntityItems[2], value: bffState.appName },
    { ...fallbackEntityItems[3], value: bffState.serviceAccountRef },
    fallbackEntityItems[4],
  ];

  return (
    <TooltipProvider delayDuration={120}>
      <div className="v12-workbench" data-testid="v12-readonly-workbench">
        <nav className="v12-rail" aria-label="全局导航">
          <div className="v12-rail__brand">
            <Sparkles size={18} />
          </div>
          {[LayoutGrid, Bot, Activity, FileText, Network].map((Icon, index) => (
            <button aria-label={`导航 ${index + 1}`} className={index === 0 ? "v12-rail__item v12-rail__item--active" : "v12-rail__item"} key={index} type="button">
              <Icon size={18} />
            </button>
          ))}
        </nav>

        <header className="v12-topbar">
          <div className="v12-topbar__title">
            <strong>HarnessOS Product Workbench</strong>
            <span>V12 产品壳 / 只读画布基础 / BFF 边界</span>
          </div>
          <Tabs className="v12-tabs" defaultValue="canvas">
            <TabsList>
              <TabsTrigger value="canvas">画布</TabsTrigger>
              <TabsTrigger value="agents">Agent</TabsTrigger>
              <TabsTrigger value="evidence">证据</TabsTrigger>
            </TabsList>
          </Tabs>
          <div className="v12-topbar__status" data-testid="v12-api-health">
            <Badge variant="success">
              <CheckCircle2 size={13} />
              API Health {bffState.healthStatus === "ok" ? "OK" : "Fallback"}
            </Badge>
            <Badge variant="default" data-testid="v12-bff-source">{bffState.loadedFromBff ? "real BFF projection" : "local fallback projection"}</Badge>
          </div>
      </header>

        <aside className="v12-sidebar" data-testid="v12-entity-sidebar">
          <ScrollArea className="v12-scroll">
            <Card>
              <CardHeader>
                <CardTitle>产品实体</CardTitle>
                <Badge>Studio</Badge>
              </CardHeader>
              <CardContent className="grid gap-2">
                {entityItems.map((item) => (
                  <Entity icon={item.icon} key={item.label} label={item.label} value={item.value} />
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>BFF 边界</CardTitle>
                <ShieldCheck className="text-blue-600" size={16} />
              </CardHeader>
              <CardContent>
                <ul className="v12-boundary-list" data-testid="v12-bff-boundary">
                  <li>浏览器只允许读取 BFF / DTO 投影</li>
                  <li>禁止直连内部 RPC 与 runtime</li>
                  <li>WorkflowDiff 未确认前不能 publish/run</li>
                  <li>CanvasReadModel：{bffState.canvasReadModelId}</li>
                  <li>WorkflowDiff：{bffState.workflowDiffRef}</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Station Agent Profile</CardTitle>
                <Bot className="text-blue-600" size={16} />
              </CardHeader>
              <CardContent>
                <dl className="v12-profile" data-testid="v12-agent-profile">
                  <KeyValue label="role" value="reviewer" />
                  <KeyValue label="goal" value={bffState.inspectorGoal} />
                  <KeyValue label="memory" value="summary_ref: memory-v12-quality-agent" />
                  <KeyValue label="model_profile" value="provider_ref:minimax-or-deepseek-redacted" />
                  <KeyValue label="tools / skills / MCP" value="quality.review / markdown.summary / mcp:readonly-docs" />
                  <KeyValue label="policy" value="readonly_projection_only" />
                </dl>
              </CardContent>
            </Card>
          </ScrollArea>
        </aside>

        <main className="v12-canvas-region">
          <div className="v12-canvas-toolbar">
            <div className="v12-canvas-toolbar__title">
              <GitBranch size={17} />
              <span>只读 Workflow Canvas Foundation</span>
              <Badge variant="default">read-only projection</Badge>
            </div>
            <div className="v12-actions">
              <Button size="sm" variant="outline">
                <Search size={14} />
                搜索
              </Button>
              <div className="v12-actions" data-testid="v12-disabled-actions">
                {toolbarActions.map((action) => (
                  <Tooltip key={action.label}>
                    <TooltipTrigger asChild>
                      <span>
                        <Button disabled size="sm" title={action.reason} variant="secondary">
                          <action.icon size={14} />
                          {action.label}
                        </Button>
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>{action.reason}</TooltipContent>
                  </Tooltip>
                ))}
              </div>
            </div>
          </div>
          <div className="v12-interaction-strip" data-testid="v12-interaction-states">
            {bffState.interactionStates.map((item) => (
              <span key={item.state} data-state={item.state}>
                {item.state}：{item.description}
              </span>
            ))}
          </div>
          <WorkflowCanvas readOnly />
        </main>

        <aside className="v12-inspector" data-testid="v12-node-inspector">
          <ScrollArea className="v12-scroll">
            <Card>
              <CardHeader>
                <CardTitle>节点 Inspector</CardTitle>
                <Badge variant="warning">待确认</Badge>
              </CardHeader>
              <CardContent>
                <div className="v12-selected-node">
                  <div className="v12-selected-node__icon">质</div>
                  <div>
                    <strong>{selectedNode.name}</strong>
                    <span>Reviewer / quality gate</span>
                  </div>
                </div>
                <Separator className="my-3" />
                <dl className="v12-inspector-grid">
                  {inspectorRows.map(([label, value]) => (
                    <KeyValue key={label} label={label} value={value} />
                  ))}
                </dl>
                <div className="v12-disabled-reason" data-testid="v12-disabled-action-reason">
                  <CircleSlash size={16} />
                  <span>禁用原因：{bffState.disabledReasons.map((item) => `${item.label}：${item.reason}`).join("；")}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Chat Workbench 提案</CardTitle>
                <MessageSquareText className="text-blue-600" size={16} />
              </CardHeader>
              <CardContent>
                <div className="v12-proposal" data-testid="v12-workflowdiff-handoff">
                  <span>目标：{bffState.goalSummary}</span>
                  <span>状态：{bffState.proposalState}</span>
                  <span>WorkflowDiff：{bffState.workflowDiffRef}</span>
                  <span>边界：提案证据，不发布、不运行</span>
                  <span>选中节点：{bffState.selectedNodeRef}</span>
                  <span>审计引用：{bffState.inspectorAuditRef}</span>
                  <span>交接状态：{bffState.handoffState}</span>
                  <div className="v12-proposal-events" data-testid="v12-proposal-timeline">
                    {bffState.proposalEvents.map((event) => (
                      <span key={event.event_id}>
                        {event.label} / {event.state} / risk:{event.risk_level}
                      </span>
                    ))}
                  </div>
                  <label className="v12-goal-box">
                    <span>Goal input</span>
                    <input data-testid="v12-goal-input" readOnly value={bffState.goalSummary} />
                  </label>
                  <div className="v12-proposal-actions">
                    <Button data-testid="v12-revise-proposal" size="sm" type="button" variant="outline" onClick={() => void postProposalDecision("revise")}>
                      修订提案
                    </Button>
                    <Button data-testid="v12-reject-proposal" size="sm" type="button" variant="outline" onClick={() => void postProposalDecision("reject")}>
                      拒绝提案
                    </Button>
                    <Button data-testid="v12-open-graph-review" size="sm" type="button" variant="secondary" onClick={() => void postProposalDecision("confirm-handoff")}>
                      打开图审查
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </ScrollArea>
        </aside>

        <footer className="v12-evidence" data-testid="v12-evidence-strip">
          <span>
            <Link2 size={14} />
            证据包：docs/design/V12-V15.x/evidence/v12-readiness/
          </span>
          <span>
            <Info size={14} />
            No False Green：仅允许基线待审声明，不做生产级或完整工作台声明
          </span>
        </footer>
      </div>
    </TooltipProvider>
  );
}

function Entity({ icon: Icon, label, value }: { icon: typeof Bot; label: string; value: string }) {
  return (
    <div className="v12-entity">
      <Icon size={16} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="v12-kv-row">
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
