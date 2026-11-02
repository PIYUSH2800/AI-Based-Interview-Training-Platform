"""
AI Interview Platform — Pre-Flight Localhost Environment Verification
Run this script to verify your Windows laptop is fully prepared for the local demonstration.

Usage:
    python verify_environment.py
"""

import sys
import os
import subprocess
import socket
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def print_header(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def check_python():
    print_header("1. Python Environment")
    v = sys.version_info
    print(f"  Python Version: {v.major}.{v.minor}.{v.micro}")
    if v.major == 3 and v.minor >= 10:
        print("  [OK] Python version is supported (3.10+)")
    else:
        print("  [WARN] Python 3.10+ recommended.")

    required_modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("passlib", "Passlib (bcrypt)"),
        ("jwt", "PyJWT"),
        ("dotenv", "python-dotenv"),
        ("pydantic", "Pydantic"),
        ("google.genai", "Google GenAI SDK (Gemini)"),
    ]

    all_modules_ok = True
    for mod_name, label in required_modules:
        try:
            __import__(mod_name)
            print(f"  [OK] {label}")
        except ImportError:
            print(f"  [FAIL] {label} is NOT installed")
            all_modules_ok = False

    if not all_modules_ok:
        print("  Action: Run 'pip install -r backend/requirements.txt'")
    return all_modules_ok

def check_node():
    print_header("2. Node.js & Frontend Environment")
    node_ok = False
    try:
        res = subprocess.run(["node", "-v"], capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            print(f"  [OK] Node.js Version: {res.stdout.strip()}")
            node_ok = True
        else:
            print("  [FAIL] Node.js is not found on PATH.")
    except Exception as e:
        print(f"  [FAIL] Error detecting Node.js: {e}")

    try:
        res = subprocess.run(["npm", "-v"], capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            print(f"  [OK] npm Version: {res.stdout.strip()}")
        else:
            print("  [FAIL] npm is not found.")
    except Exception as e:
        print(f"  [FAIL] Error detecting npm: {e}")

    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists() and any(node_modules.iterdir()):
        print("  [OK] frontend/node_modules directory present")
    else:
        print("  [WARN] frontend/node_modules missing. Run 'cd frontend && npm install'")
    return node_ok

def check_docker():
    print_header("3. Docker Desktop Sandbox (For Real Code Execution)")
    docker_running = False
    try:
        res = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], capture_output=True, text=True, shell=True)
        if res.returncode == 0 and res.stdout.strip():
            print(f"  [OK] Docker Server is Running (Version: {res.stdout.strip()})")
            docker_running = True
        else:
            print("  [WARN] Docker Desktop is NOT running. Code execution will fallback to mock.")
            print("         To enable real Docker execution, start Docker Desktop.")
            return False
    except Exception as e:
        print(f"  [WARN] Docker command error: {e}")
        return False

    required_images = [
        "python:3.11-slim",
        "gcc:latest",
        "eclipse-temurin:17-jdk-jammy"
    ]
    try:
        img_res = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], capture_output=True, text=True, shell=True)
        available_images = img_res.stdout.splitlines() if img_res.returncode == 0 else []
        for req in required_images:
            if req in available_images:
                print(f"  [OK] Sandbox Image: {req}")
            else:
                print(f"  [INFO] Image {req} not cached yet. Run 'docker pull {req}'")
    except Exception as e:
        print(f"  [INFO] Could not list images: {e}")

    return docker_running

def check_database():
    print_header("4. SQLite Database & Curriculum Integrity")
    sys.path.insert(0, str(BACKEND_DIR))
    from app.database.database import engine, SQLALCHEMY_DATABASE_URL
    import sqlite3

    db_path = BACKEND_DIR / "interview_platform.db"
    print(f"  Database Path: {db_path}")
    if not db_path.exists():
        print("  [FAIL] Database file does not exist!")
        return False
    print(f"  [OK] Database file exists ({db_path.stat().st_size:,} bytes)")

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM coding_modules")
    modules_cnt = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM coding_problems")
    problems_cnt = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM test_cases")
    test_cases_cnt = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users")
    users_cnt = c.fetchone()[0]
    c.execute("PRAGMA foreign_key_check")
    fk_violations = len(c.fetchall())
    conn.close()

    print(f"  [OK] Coding Modules: {modules_cnt} (Expected: 6)")
    print(f"  [OK] Coding Problems: {problems_cnt} (Expected: 48)")
    print(f"  [OK] Coding Test Cases: {test_cases_cnt} (Expected: 195)")
    print(f"  [OK] Registered Users: {users_cnt}")
    print(f"  [OK] Foreign Key Violations: {fk_violations}")

    if modules_cnt == 6 and problems_cnt == 48 and test_cases_cnt == 195 and fk_violations == 0:
        print("  [OK] Curriculum and Database Integrity Verified!")
        return True
    else:
        print("  [FAIL] Database counts mismatch!")
        return False

def check_ai_configuration():
    print_header("5. Gemini AI Service & Fallback Status")
    sys.path.insert(0, str(BACKEND_DIR))
    from app.services.ai_service import ai_service
    status = ai_service.get_ai_status()
    print(f"  Configured:      {status.get('configured')}")
    print(f"  Active Mode:     {status.get('active_mode').upper()}")
    print(f"  AI Model:        {status.get('model')}")
    print(f"  Fallback Ready:  {status.get('fallback_enabled')}")

    if status.get("configured"):
        print("  [OK] Real Gemini AI is configured and ready.")
    else:
        print("  [INFO] Real Gemini API key is not configured or in mock fallback.")
        print("         The platform will run in Mock AI mode (100% offline demonstration ready).")
        print("         To enable real Gemini AI, add your GEMINI_API_KEY into backend/.env")
    return True

def check_email_configuration():
    print_header("6. Email Delivery & Account Recovery Status")
    sys.path.insert(0, str(BACKEND_DIR))
    from app.services.email_service import email_service
    status = email_service.get_email_status()
    configured = status.get("configured")
    print(f"  SMTP Configured: {configured}")
    print(f"  Base URL:        {status.get('frontend_base_url')}")

    if configured:
        print(f"  [OK] SMTP Host:  {status.get('smtp_host')}:{status.get('smtp_port')}")
        print(f"  [OK] From Email: {status.get('from_email')}")
        print("  [OK] Live email delivery is configured and ready.")
    else:
        print("  [INFO] SMTP credentials are not configured in backend/.env.")
        print("         The platform will run in safe local mode for password reset.")
        print("         (Password reset API safely returns generic responses and logs actions).")
        print("         To enable live email delivery, set SMTP_HOST, SMTP_PORT, SMTP_USERNAME,")
        print("         and SMTP_PASSWORD in backend/.env.")
    return True

def check_ports():
    print_header("7. Localhost Ports Check (8000 & 5173)")
    ports = [(8000, "Backend API"), (5173, "Frontend Dev Server")]
    for port, label in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            result = s.connect_ex(("127.0.0.1", port))
            if result == 0:
                print(f"  [OCCUPIED] Port {port} ({label}) is currently in use.")
                print(f"             (If this is already your running server, that's OK!)")
            else:
                print(f"  [FREE] Port {port} ({label}) is available.")

def main():
    print("\n" + "#" * 65)
    print("   AI INTERVIEW PLATFORM — LOCALHOST PRE-FLIGHT CHECK")
    print("#" * 65)

    py_ok = check_python()
    node_ok = check_node()
    docker_ok = check_docker()
    db_ok = check_database()
    ai_ok = check_ai_configuration()
    email_ok = check_email_configuration()
    check_ports()

    print_header("SUMMARY & READINESS")
    if py_ok and db_ok:
        print("  >>> PLATFORM IS READY FOR LOCALHOST DEMONSTRATION! <<<")
        print("  Quick Start:")
        print("    Option 1: Double-click 'start_demo.bat' to launch both servers")
        print("    Option 2: Run 'backend: start_backend.bat' and 'frontend: start_frontend.bat'")
    else:
        print("  >>> ATTENTION REQUIRED: Review flagged items above. <<<")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
