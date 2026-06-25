from __future__ import annotations

import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_CONSOLE = ROOT / "apps/workflow-console"
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/post-v15-product-runtime-hardening"
BFF_PORT = int(os.environ.get("PV16_BFF_PORT", "18045"))
PREVIEW_PORT = int(os.environ.get("PV16_PREVIEW_PORT", "4179"))
CDP_PORT = int(os.environ.get("PV16_CDP_PORT", "9340"))
LOCAL_CHROME = Path(os.environ.get("PV16_CHROME", "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"))


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"/tmp/harnessos-pydeps:{ROOT}:{env.get('PYTHONPATH', '')}"
    env["WORKFLOW_CONSOLE_PYTHON"] = "python3"
    env["WORKFLOW_CONSOLE_BFF_PORT"] = str(BFF_PORT)
    env["WORKFLOW_CONSOLE_PREVIEW_PORT"] = str(PREVIEW_PORT)
    env["VITE_BFF_PROXY_TARGET"] = f"http://127.0.0.1:{BFF_PORT}"
    env["VITE_HARNESSOS_DEMO_MODE"] = "false"
    env["PV16_CDP_URL"] = f"http://127.0.0.1:{CDP_PORT}"
    env["PV16_BASE_URL"] = f"http://127.0.0.1:{PREVIEW_PORT}"
    env["PV16_BFF_BASE"] = f"http://127.0.0.1:{BFF_PORT}"
    env["PV16_EVIDENCE_DIR"] = str(EVIDENCE_DIR)

    run(["node", "node_modules/typescript/bin/tsc", "-p", "tsconfig.json"], cwd=WORKFLOW_CONSOLE, env=env)
    run(["node", "node_modules/vite/bin/vite.js", "build"], cwd=WORKFLOW_CONSOLE, env=env)

    bff = subprocess.Popen(
        ["python3", "e2e/bff_smoke_server.py"],
        cwd=WORKFLOW_CONSOLE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    preview = subprocess.Popen(
        ["node", "node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", str(PREVIEW_PORT)],
        cwd=WORKFLOW_CONSOLE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    chrome = start_chrome()
    try:
        wait_for_url(f"http://127.0.0.1:{BFF_PORT}/__test/health", "PV16 test BFF")
        wait_for_url(f"http://127.0.0.1:{PREVIEW_PORT}", "workflow-console preview")
        wait_for_url(f"http://127.0.0.1:{CDP_PORT}/json/version", "Chrome CDP")
        run(["node", "e2e/pv16_cdp_acceptance.mjs"], cwd=WORKFLOW_CONSOLE, env=env)
        run(["python3", "tools/post_v15/run_product_runtime_hardening_acceptance.py"], cwd=ROOT, env=env)
    finally:
        terminate(chrome)
        terminate(preview)
        terminate(bff)
    return 0


def run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)
    if result.stdout.strip():
        print(result.stdout)


def start_chrome() -> subprocess.Popen[str]:
    if not LOCAL_CHROME.exists():
        raise SystemExit(f"Local Chrome is required for PV16 CDP acceptance: {LOCAL_CHROME}")
    return subprocess.Popen(
        [
            str(LOCAL_CHROME),
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={CDP_PORT}",
            "--user-data-dir=C:\\Temp\\harnessos-pv16-cdp-e2e",
            "about:blank",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def wait_for_url(url: str, label: str) -> None:
    deadline = time.time() + 45
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(0.5)
    raise SystemExit(f"Timed out waiting for {label} at {url}: {last_error}")


def terminate(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
