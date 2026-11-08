"""Run browser tests with disposable data and no external API credentials."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for(url, process):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("An isolated test server exited before it was ready")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError):
            pass
        time.sleep(0.2)
    raise RuntimeError("An isolated test server did not become ready")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required")
    api_port, web_port = free_port(), free_port()
    while web_port == api_port:
        web_port = free_port()
    base = f"http://127.0.0.1:{web_port}"
    processes = []
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    with tempfile.TemporaryDirectory(prefix="respect-e2e-") as temporary:
        directory = Path(temporary)
        assert directory.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
        environment = {**os.environ, "MONGO_URI": "", "MONGO_HOST": "", "SQLITE_PATH": str(directory / "test.db"), "BOOTSTRAP_ADMIN_USERNAME": "admin", "BOOTSTRAP_ADMIN_PASSWORD": "Isolated-E2E-Admin-Only!42", "RIOT_API_KEY": "", "HENRIK_API_KEY": "", "STEAM_WEB_API_KEY": "", "FACEIT_API_KEY": "", "FORTNITE_API_KEY": "", "COOKIE_SECURE": "false", "CORS_ORIGINS": base, "BACKEND_URL": f"http://127.0.0.1:{api_port}", "E2E_BASE_URL": base, "E2E_ADMIN_PASSWORD": "Isolated-E2E-Admin-Only!42"}
        with (directory / "api.log").open("w+", encoding="utf-8") as api_log, (directory / "web.log").open("w+", encoding="utf-8") as web_log:
            try:
                api = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(api_port), "--log-level", "error"], cwd=ROOT / "respect-backend", env=environment, stdout=api_log, stderr=subprocess.STDOUT, creationflags=flags)
                processes.append(api)
                wait_for(f"http://127.0.0.1:{api_port}/api/health", api)
                web = subprocess.Popen([node, str(ROOT / "respect-frontend/node_modules/next/dist/bin/next"), "start", "--hostname", "127.0.0.1", "--port", str(web_port)], cwd=ROOT / "respect-frontend", env=environment, stdout=web_log, stderr=subprocess.STDOUT, creationflags=flags)
                processes.append(web)
                wait_for(base, web)
                print("Browser tests use disposable SQLite data and isolated server ports.", flush=True)
                result = subprocess.run([node, str(ROOT / "respect-frontend/node_modules/@playwright/test/cli.js"), "test", *sys.argv[1:]], cwd=ROOT / "respect-frontend", env=environment, creationflags=flags, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
                print(result.stdout, flush=True)
                return result.returncode
            finally:
                for process in reversed(processes):
                    process.terminate()
                for process in reversed(processes):
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                print("Isolated servers stopped; disposable data will be removed.", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
