import os
import sys
import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def run_seed(mode="STARTER", seed=20261022):
    print(f"[*] Seeding database in {mode} mode with seed {seed}...")
    cmd = [sys.executable, str(ROOT_DIR / "backend" / "generator" / "generator.py"), "--mode", mode, "--seed", str(seed), "--seed-db"]
    subprocess.run(cmd, check=True)

def run_validate():
    print("[*] Running automated relational & reproducibility validation...")
    cmd = [sys.executable, str(ROOT_DIR / "backend" / "generator" / "validator.py")]
    subprocess.run(cmd, check=True)

def run_test():
    print("[*] Running Pytest test suite...")
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "-v"]
    subprocess.run(cmd, check=True)

def run_server(host="127.0.0.1", port=8000):
    print(f"[*] Starting SkillPath AI backend on http://{host}:{port}...")
    import uvicorn
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)

def main():
    parser = argparse.ArgumentParser(description="SkillPath AI Platform Master CLI")
    parser.add_argument("--seed", action="store_true", help="Seed database with synthetic dataset")
    parser.add_argument("--mode", default="STARTER", choices=["STARTER", "FULL"], help="Dataset size (STARTER or FULL)")
    parser.add_argument("--validate", action="store_true", help="Run automated data validation")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument("--server", action="store_true", help="Start FastAPI web server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()

    if args.seed:
        run_seed(mode=args.mode)
    elif args.validate:
        run_validate()
    elif args.test:
        run_test()
    elif args.server:
        run_server(host=args.host, port=args.port)
    else:
        # Default: if database does not exist, seed it, then start server
        db_path = ROOT_DIR / "skillpath.db"
        if not db_path.exists():
            print("[*] Database not found. Seeding initial starter database...")
            run_seed(mode="STARTER")
        run_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
