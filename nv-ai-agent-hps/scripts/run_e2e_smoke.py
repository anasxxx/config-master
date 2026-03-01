import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "SIT" / "ConfigMaster-Backend"
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"
SMOKE_SCRIPT = ROOT / "nv-ai-agent-hps" / "scripts" / "smoke_test_bank_pipeline.py"


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def main() -> int:
    backend = subprocess.Popen(
        ["cmd", "/c", "mvnw.cmd spring-boot:run"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        for _ in range(120):
            if port_open("127.0.0.1", 8084):
                break
            time.sleep(1)
        else:
            print("BACKEND_NOT_READY")
            return 1

        proc = subprocess.run(
            [str(PYTHON_EXE), str(SMOKE_SCRIPT), "--generate-token", "--verify"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode
    finally:
        backend.terminate()
        try:
            backend.wait(timeout=5)
        except Exception:
            backend.kill()


if __name__ == "__main__":
    raise SystemExit(main())
