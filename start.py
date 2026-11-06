from __future__ import annotations

import os
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    app_root = Path(__file__).resolve().parent
    os.environ.setdefault("ACTACITE_DB_PATH", str(app_root / "data" / "actacite.sqlite3"))
    shutil.copyfile(app_root / "static" / "manus-routes.json", "/tmp/actacite-manus-routes.json")
    for temp_dir in (
        "/tmp/nginx-client-body",
        "/tmp/nginx-proxy",
        "/tmp/nginx-fastcgi",
        "/tmp/nginx-uwsgi",
        "/tmp/nginx-scgi",
    ):
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        os.chmod(temp_dir, 0o733)

    streamlit = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.address=127.0.0.1",
            "--server.port=3001",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
            "--browser.gatherUsageStats=false",
        ],
        cwd=app_root,
    )
    nginx = subprocess.Popen(
        ["nginx", "-g", "daemon off;", "-c", str(app_root / "nginx.conf")], cwd=app_root
    )

    def stop(_signum: int, _frame: object) -> None:
        for process in (nginx, streamlit):
            if process.poll() is None:
                process.terminate()
        for process in (nginx, streamlit):
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while True:
        if streamlit.poll() is not None:
            raise SystemExit(f"Streamlit exited with status {streamlit.returncode}")
        if nginx.poll() is not None:
            raise SystemExit(f"Nginx exited with status {nginx.returncode}")
        time.sleep(1)


if __name__ == "__main__":
    main()
