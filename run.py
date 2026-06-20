import os
import platform
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"

system = platform.system()

if system == "Windows":

    if not VENV_PYTHON.exists():
        print("❌ Virtual Environment Python not found")
        print("Expected:", VENV_PYTHON)
        exit(1)

    command = f'"{VENV_PYTHON}" -m uvicorn app.main:app --reload'

else:
    command = "./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

print("🚀 Starting Server")
print("Python:", VENV_PYTHON)
print("Command:", command)

subprocess.call(command, shell=True)


# #!/bin/bash
# source venv/bin/activate
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000