from __future__ import annotations

import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_CONSOLE = ROOT / "apps/workflow-console"
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/pv17-product-closed-loop"
BFF_PORT = int(os.environ.get("PV17_BFF_PORT", "18046"))
PREVIEW_PORT = int(os.environ.get("PV17_PREVIEW_PORT", "5173"))
CDP_PORT = int(os.environ.get("PV17_CDP_PORT", "9341"))
RUNTIME_ROOT = Path(os.environ.get("PV17_RUNTIME_ROOT", "/tmp/harnessos-pv17-runtime"))


def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["HARNESS_V3_5_DEV_MODE"] = "1"
    env["PV17_RUNTIME_ROOT"] = str(RUNTIME_ROOT)
    env["API_CORS_ORIGINS"] = f'["http://127.0.0.1:{PREVIEW_PORT}","http://localhost:{PREVIEW_PORT}"]'
    env["VITE_BFF_PROXY_TARGET"] = f"http://127.0.0.1:{BFF_PORT}"
    env["VITE_BFF_BASE_URL"] = f"http://127.0.0.1:{BFF_PORT}/bff"
    env["VITE_HARNESSOS_DEMO_MODE"] = "false"
    env["PV17_CDP_URL"] = f"http://127.0.0.1:{CDP_PORT}"
    env["PV17_BASE_URL"] = f"http://127.0.0.1:{PREVIEW_PORT}"
    env["PV17_BFF_BASE"] = f"http://127.0.0.1:{BFF_PORT}"
    env["PV17_EVIDENCE_DIR"] = str(EVIDENCE_DIR)

    shutil.rmtree(EVIDENCE_DIR, ignore_errors=True)
    shutil.rmtree(RUNTIME_ROOT, ignore_errors=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)

    run(["node", "node_modules/typescript/bin/tsc", "-p", "tsconfig.json"], cwd=WORKFLOW_CONSOLE, env=env)
    run(["node", "node_modules/vite/bin/vite.js", "build"], cwd=WORKFLOW_CONSOLE, env=env)

    bff = subprocess.Popen(
        [
            python_executable(),
            "-m",
            "uvicorn",
            "tools.pv17.formal_bff_server:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(BFF_PORT),
        ],
        cwd=ROOT,
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
    chrome = start_chrome(env)
    try:
        wait_for_url(f"http://127.0.0.1:{BFF_PORT}/health", "PV17 formal FastAPI")
        wait_for_url(f"http://127.0.0.1:{PREVIEW_PORT}", "workflow-console preview")
        wait_for_url(f"http://127.0.0.1:{CDP_PORT}/json/version", "Chrome CDP")
        run(["node", "e2e/pv17_cdp_acceptance.mjs"], cwd=WORKFLOW_CONSOLE, env=env)
        run([python_executable(), "tools/pv17/run_product_closed_loop_acceptance.py"], cwd=ROOT, env=env)
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


def start_chrome(env: dict[str, str]) -> subprocess.Popen[str]:
    chrome_path = find_chrome()
    if chrome_path is None:
        raise SystemExit("Chrome or Chromium is required for PV17 CDP acceptance.")
    user_data_dir = "C:\\Temp\\harnessos-pv17-cdp-e2e" if chrome_path.startswith("/mnt/c/") else "/tmp/harnessos-pv17-cdp-e2e"
    return subprocess.Popen(
        [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={user_data_dir}",
            "about:blank",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def find_chrome() -> str | None:
    explicit = os.environ.get("PV17_CHROME")
    candidates = [
        explicit,
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def wait_for_url(url: str, label: str) -> None:
    deadline = time.time() + 60
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


def python_executable() -> str:
    local = ROOT / ".venv/bin/python"
    return str(local) if local.exists() else "python3"


if __name__ == "__main__":
    raise SystemExit(main())
