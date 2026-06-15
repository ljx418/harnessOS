import fs from "node:fs";
import { resolveReadablePath } from "./paths.js";

export function loadDotenvEnv(options = {}) {
  const cwd = options.cwd || process.cwd();
  const files = options.files || [
    ".env.v10-llm.local",
    ".env.local",
    ".env"
  ];
  const env = { ...process.env };
  const loaded = [];
  for (const file of files) {
    const filePath = resolveReadablePath(file, { cwd });
    if (!fs.existsSync(filePath)) continue;
    const values = parseDotenv(fs.readFileSync(filePath, "utf8"));
    for (const [key, value] of Object.entries(values)) {
      if (shouldSkipEnvValue(key, value)) continue;
      if (env[key] === undefined || env[key] === "") {
        env[key] = value;
      }
    }
    loaded.push(filePath);
  }
  return { env, loaded };
}

function shouldSkipEnvValue(key, value) {
  const text = String(value || "").trim();
  if (!text) return true;
  if (!/_API_KEY$/.test(key)) return false;
  const lower = text.toLowerCase();
  return (
    lower.includes("your-") ||
    lower.includes("placeholder") ||
    lower.includes("replace-me") ||
    lower === "test-key" ||
    lower === "sk-test-realistic-secret"
  );
}

export function parseDotenv(content) {
  const values = {};
  for (const rawLine of String(content || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index <= 0) continue;
    const key = line.slice(0, index).trim();
    let value = line.slice(index + 1).trim();
    if (
      (value.startsWith("\"") && value.endsWith("\"")) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    values[key] = value;
  }
  return values;
}
