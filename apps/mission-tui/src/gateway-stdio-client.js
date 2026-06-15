import { spawn } from "node:child_process";
import { EventEmitter } from "node:events";

export class GatewayStdioClient extends EventEmitter {
  constructor(options = {}) {
    super();
    this.python = options.python || "./.venv/bin/python";
    this.cwd = options.cwd || process.cwd();
    this.module = options.module || "apps.gateway.stdio_server";
    this.timeoutMs = Number(options.timeoutMs || 30000);
    this.env = options.env || process.env;
    this.process = null;
    this.nextId = 1;
    this.pending = new Map();
    this.stdoutBuffer = "";
    this.stderrBuffer = "";
    this.stderrLines = [];
  }

  start() {
    if (this.process) return;
    this.process = spawn(this.python, ["-m", this.module], {
      cwd: this.cwd,
      env: this.env,
      stdio: ["pipe", "pipe", "pipe"]
    });
    this.process.stdout.setEncoding("utf8");
    this.process.stderr.setEncoding("utf8");
    this.process.stdout.on("data", (chunk) => this.#onStdout(chunk));
    this.process.stderr.on("data", (chunk) => this.#onStderr(chunk));
    this.process.on("error", (error) => this.#rejectAll(error));
    this.process.on("exit", (code, signal) => {
      this.#rejectAll(new Error(`gateway stdio exited code=${code} signal=${signal}`));
    });
  }

  async initialize(params = {}) {
    return this.request("initialize", params);
  }

  async startSession(params = {}) {
    return this.request("session.start", params);
  }

  async startTurn(params = {}) {
    return this.request("turn.start", params);
  }

  async request(method, params = {}) {
    this.start();
    const id = `tui_${this.nextId++}`;
    const payload = { id, method, params };
    const response = await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`gateway stdio request timed out: ${method}`));
      }, this.timeoutMs);
      this.pending.set(id, { resolve, reject, timeout });
      this.process.stdin.write(`${JSON.stringify(payload)}\n`, "utf8", (error) => {
        if (error) {
          clearTimeout(timeout);
          this.pending.delete(id);
          reject(error);
        }
      });
    });
    if (response.error) {
      const message = response.error.message || response.error.code || "gateway rpc error";
      const error = new Error(message);
      error.code = response.error.code;
      error.data = response.error.data;
      throw error;
    }
    return response.result || {};
  }

  close() {
    if (!this.process) return;
    const child = this.process;
    this.process = null;
    if (!child.killed) {
      child.stdin.end();
      child.kill();
    }
  }

  #onStdout(chunk) {
    this.stdoutBuffer += chunk;
    let newlineIndex = this.stdoutBuffer.indexOf("\n");
    while (newlineIndex >= 0) {
      const line = this.stdoutBuffer.slice(0, newlineIndex).trim();
      this.stdoutBuffer = this.stdoutBuffer.slice(newlineIndex + 1);
      if (line) this.#handleLine(line);
      newlineIndex = this.stdoutBuffer.indexOf("\n");
    }
  }

  #onStderr(chunk) {
    this.stderrBuffer += chunk;
    let newlineIndex = this.stderrBuffer.indexOf("\n");
    while (newlineIndex >= 0) {
      const line = this.stderrBuffer.slice(0, newlineIndex).trim();
      this.stderrBuffer = this.stderrBuffer.slice(newlineIndex + 1);
      if (line) {
        this.stderrLines.push(line);
        this.emit("stderr-line", line);
      }
      newlineIndex = this.stderrBuffer.indexOf("\n");
    }
  }

  #handleLine(line) {
    let response;
    try {
      response = parseGatewayResponseLine(line);
    } catch (error) {
      this.emit("protocol-error", { line, message: error.message });
      return;
    }
    const pending = this.pending.get(response.id);
    if (!pending) {
      this.emit("unmatched-response", response);
      return;
    }
    clearTimeout(pending.timeout);
    this.pending.delete(response.id);
    pending.resolve(response);
  }

  #rejectAll(error) {
    for (const [id, pending] of this.pending.entries()) {
      clearTimeout(pending.timeout);
      pending.reject(error);
      this.pending.delete(id);
    }
  }
}

export function parseGatewayResponseLine(line) {
  const payload = JSON.parse(line);
  if (!payload || typeof payload !== "object") {
    throw new Error("gateway response must be an object");
  }
  if (!Object.prototype.hasOwnProperty.call(payload, "id")) {
    throw new Error("gateway response missing id");
  }
  if (!Object.prototype.hasOwnProperty.call(payload, "result")) {
    throw new Error("gateway response missing result");
  }
  if (!Object.prototype.hasOwnProperty.call(payload, "error")) {
    throw new Error("gateway response missing error");
  }
  return payload;
}
