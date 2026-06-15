import fs from "node:fs";

export function writeHtmlExplainer(state, outputPath) {
  const blocks = (state.transcript_items || []).map((item) => {
    const evidence = (item.evidence_refs || []).map((ref) => `<code>${escapeHtml(ref)}</code>`).join(" ");
    return `<article class="block"><h3>${escapeHtml(item.type)} · ${escapeHtml(item.status)}</h3><p>${escapeHtml(item.text || item.preview_text || item.agent_goal || item.operation || item.id)}</p><p>${evidence}</p></article>`;
  }).join("\n");
  const html = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>Mission TUI Evidence Explainer</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0b1020;color:#e5e7eb;margin:0;padding:28px}
    .wrap{max-width:1100px;margin:0 auto}.badge{display:inline-block;background:#164e63;color:#a5f3fc;padding:4px 8px;border-radius:6px}
    .warn{background:#431407;border:1px solid #f97316;padding:12px;border-radius:8px}.block{background:#111827;border:1px solid #374151;border-radius:8px;padding:14px;margin:12px 0}
    code{background:#020617;color:#93c5fd;padding:2px 5px;border-radius:4px}
  </style>
</head>
<body><main class="wrap">
  <p class="badge">supporting explainer only</p>
  <h1>Mission TUI 证据解释页</h1>
  <p class="warn">本页面是辅助审计导出，不是主 TUI，不是 runtime truth，也不能替代真实 TUI 截图。</p>
  <h2>目标</h2><p>${escapeHtml(state.goal || "")}</p>
  <h2>状态</h2><p>${escapeHtml(JSON.stringify(state.status_line || {}))}</p>
  <h2>Blocks</h2>${blocks}
</main></body></html>`;
  fs.writeFileSync(outputPath, html, "utf8");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
