#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { loadState, summarizeAcceptance, validateMissionTuiState } from "./state.js";
import { renderMissionTui } from "./renderer.js";
import { writeHtmlExplainer } from "./html-explainer.js";
import { runInteractiveSession } from "./interactive.js";
import { runAgentBackedInteractiveSession, runAgentBackedOnceCli } from "./agent-backed-interactive.js";
import { DEFAULT_FIXTURE, DEFAULT_PYTHON } from "./paths.js";

function parseArgs(argv) {
  const args = {
    fixture: DEFAULT_FIXTURE,
    columns: 80,
    rows: 24,
    json: false,
    validate: false,
    interactive: false,
    agentBacked: false,
    agentBackedOnce: null,
    python: DEFAULT_PYTHON,
    dotenv: null,
    model: null,
    domain: null,
    timeoutMs: 30000,
    html: null,
    out: null
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--fixture") args.fixture = argv[++index];
    else if (arg === "--columns") args.columns = Number(argv[++index]);
    else if (arg === "--rows") args.rows = Number(argv[++index]);
    else if (arg === "--json") args.json = true;
    else if (arg === "--validate") args.validate = true;
    else if (arg === "--interactive") args.interactive = true;
    else if (arg === "--agent-backed") args.agentBacked = true;
    else if (arg === "--agent-backed-once") args.agentBackedOnce = argv[++index];
    else if (arg === "--python") args.python = argv[++index];
    else if (arg === "--dotenv") args.dotenv = argv[++index];
    else if (arg === "--model") args.model = argv[++index];
    else if (arg === "--domain") args.domain = argv[++index];
    else if (arg === "--timeout-ms") args.timeoutMs = Number(argv[++index]);
    else if (arg === "--html") args.html = argv[++index];
    else if (arg === "--out") args.out = argv[++index];
  }
  return args;
}

export function run(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args.agentBackedOnce) {
    return runAgentBackedOnceCli(args);
  }
  if (args.agentBacked) {
    return runAgentBackedInteractiveSession(args);
  }
  if (args.interactive) {
    return runInteractiveSession(args);
  }
  const state = loadState(args.fixture);
  const errors = validateMissionTuiState(state);
  if (args.validate && errors.length > 0) {
    console.error(JSON.stringify({ status: "FAIL", errors }, null, 2));
    return 2;
  }
  if (args.html) {
    fs.mkdirSync(path.dirname(args.html), { recursive: true });
    writeHtmlExplainer(state, args.html);
  }
  const output = args.json
    ? JSON.stringify({ ...summarizeAcceptance(state), errors }, null, 2)
    : renderMissionTui(state, { columns: args.columns, rows: args.rows });
  if (args.out) {
    fs.mkdirSync(path.dirname(args.out), { recursive: true });
    fs.writeFileSync(args.out, `${output}\n`, "utf8");
  } else {
    console.log(output);
  }
  return errors.length === 0 ? 0 : 1;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const result = run();
  if (result && typeof result.then === "function") {
    result.then((code) => {
      process.exitCode = code;
    });
  } else {
    process.exitCode = result;
  }
}
