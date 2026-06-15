import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SOURCE_DIR = path.dirname(fileURLToPath(import.meta.url));

export const PACKAGE_ROOT = path.resolve(SOURCE_DIR, "..");
export const REPO_ROOT = path.resolve(PACKAGE_ROOT, "../..");

export function resolveRepoPath(inputPath) {
  if (!inputPath) return inputPath;
  if (path.isAbsolute(inputPath)) return inputPath;
  return path.join(REPO_ROOT, inputPath);
}

export function resolvePackagePath(inputPath) {
  if (!inputPath) return inputPath;
  if (path.isAbsolute(inputPath)) return inputPath;
  return path.join(PACKAGE_ROOT, inputPath);
}

export function resolveReadablePath(inputPath, options = {}) {
  if (!inputPath) return inputPath;
  if (path.isAbsolute(inputPath)) return inputPath;
  const cwd = options.cwd || process.cwd();
  const candidates = [
    path.resolve(cwd, inputPath),
    path.join(PACKAGE_ROOT, inputPath),
    path.join(REPO_ROOT, inputPath)
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return candidates[0];
}

export const DEFAULT_FIXTURE = resolvePackagePath("fixtures/mission_tui_state_80x24.json");
export const DEFAULT_PYTHON = resolveRepoPath(".venv/bin/python");
