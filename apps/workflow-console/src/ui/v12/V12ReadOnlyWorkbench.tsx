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
const entityItems = [
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

export function V12ReadOnlyWorkbench() {
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
              API Health OK
            </Badge>
            <Badge variant="default">local BFF projection</Badge>
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
                  <KeyValue label="goal" value="检查总结质量并生成可审计 quality report" />
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
                  <span>禁用原因：V12 仅验证产品实体、BFF 边界和只读画布投影。编辑、发布、运行留给 V13 及后续阶段。</span>
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
                  <span>目标：把本地 Markdown 技术文档总结成可审计工作流</span>
                  <span>状态：awaiting_user_confirmation</span>
                  <span>WorkflowDiff：diff-v12-readonly-proposal-ref</span>
                  <span>边界：提案证据，不发布、不运行</span>
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
