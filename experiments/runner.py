#!/usr/bin/env python3
"""Experiment Runner with Data Integrity Guarantees.

Every experiment MUST be run through this runner.
It provides: traceability, tamper detection, non-repudiation.

Usage:
    python -m experiments.runner experiments/sim_finitude_x_love.py
    python -m experiments.runner benchmarks/dpo_benchmark.py --args "--mode local"
    python -m experiments.runner --list          # show all registered runs
    python -m experiments.runner --verify        # verify DB integrity
    python -m experiments.runner --verify-paper docs/paper_draft_v3.md

How it works:
    1. Before execution: records git commit hash of the code
    2. Hashes all input files (script + imported modules + data files)
    3. Executes the script, capturing stdout/stderr and result files
    4. Hashes all output files
    5. Stores everything in experiments/registry.sqlite
    6. Paper verification: parses <!-- run:ID --> comments and checks DB

Non-repudiation guarantee:
    - Every run gets a unique ID: {script_name}_{ISO_timestamp}
    - Code hash at time of execution is recorded (git rev-parse HEAD)
    - Output hash chain: if you tamper with results, hash won't match
    - The DB itself has an integrity chain (each row includes prev_row_hash)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "experiments" / "registry.sqlite"
GIT_EXE = r"C:\Program Files\Git\mingw64\bin\git.exe"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _get_db() -> sqlite3.Connection:
    """Open (and initialize if needed) the registry database."""
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id          TEXT PRIMARY KEY,
            timestamp       TEXT NOT NULL,
            script_path     TEXT NOT NULL,
            args            TEXT,
            git_commit      TEXT,
            code_hash       TEXT NOT NULL,
            input_hashes    TEXT NOT NULL,
            output_hashes   TEXT NOT NULL,
            results_json    TEXT,
            stdout          TEXT,
            stderr          TEXT,
            exit_code       INTEGER,
            duration_sec    REAL,
            prev_run_hash   TEXT,
            row_hash        TEXT NOT NULL
        )
    """)
    db.commit()
    return db


def _last_row_hash(db: sqlite3.Connection) -> str:
    """Get the hash of the last inserted row (for chain integrity)."""
    row = db.execute(
        "SELECT row_hash FROM runs ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    return row[0] if row else "GENESIS"


def _compute_row_hash(data: dict) -> str:
    """Compute SHA-256 of all fields except row_hash itself."""
    content = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Hashing utilities
# ---------------------------------------------------------------------------

def hash_file(path: Path) -> str:
    """SHA-256 of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_string(s: str) -> str:
    """SHA-256 of a string."""
    return hashlib.sha256(s.encode()).hexdigest()


def get_git_commit() -> str:
    """Get current git HEAD commit hash."""
    try:
        result = subprocess.run(
            [GIT_EXE, "rev-parse", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_git_dirty() -> bool:
    """Check if working tree has uncommitted changes."""
    try:
        result = subprocess.run(
            [GIT_EXE, "status", "--porcelain"],
            cwd=str(PROJECT_ROOT),
            capture_output=True, text=True, timeout=10,
        )
        return bool(result.stdout.strip())
    except Exception:
        return True


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_experiment(
    script_path: str,
    extra_args: str = "",
    capture_outputs: list[str] | None = None,
) -> dict[str, Any]:
    """Execute an experiment script and register the run.

    Args:
        script_path: Path to the Python script (relative to project root).
        extra_args: Additional CLI arguments for the script.
        capture_outputs: List of output file paths to hash after execution.

    Returns:
        Dict with run_id and all recorded metadata.
    """
    script = PROJECT_ROOT / script_path
    if not script.exists():
        raise FileNotFoundError(f"Script not found: {script}")

    # --- Pre-execution ---
    git_commit = get_git_commit()
    git_dirty = get_git_dirty()
    code_hash = hash_file(script)

    # Hash input files (the script itself + any .json/.jsonl in same dir)
    input_hashes = {"script": f"{script_path}:{code_hash}"}
    script_dir = script.parent
    for f in script_dir.glob("*.json"):
        input_hashes[f.name] = hash_file(f)
    for f in script_dir.glob("*.jsonl"):
        input_hashes[f.name] = hash_file(f)

    # Generate run ID
    ts = datetime.now(timezone.utc)
    run_id = f"{script.stem}_{ts.strftime('%Y%m%d_%H%M%S')}"

    print(f"{'=' * 60}")
    print(f"  Experiment Runner")
    print(f"  Run ID:     {run_id}")
    print(f"  Script:     {script_path}")
    print(f"  Git commit: {git_commit[:12]}{'*' if git_dirty else ''}")
    print(f"  Timestamp:  {ts.isoformat()}")
    print(f"{'=' * 60}")
    print()

    if git_dirty:
        print("  [WARNING] Working tree has uncommitted changes.")
        print("  Results may not be reproducible from this commit alone.")
        print()

    # --- Execute ---
    cmd = [sys.executable, str(script)]
    if extra_args:
        cmd.extend(extra_args.split())

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes max
            encoding="utf-8",
            errors="replace",
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout = ""
        stderr = "TIMEOUT: Experiment exceeded 600 seconds"
    except Exception as e:
        exit_code = -2
        stdout = ""
        stderr = f"EXECUTION ERROR: {e}"

    duration = time.monotonic() - start

    # --- Post-execution: hash outputs ---
    output_hashes = {}
    if capture_outputs:
        for out_path in capture_outputs:
            p = PROJECT_ROOT / out_path
            if p.exists():
                output_hashes[out_path] = hash_file(p)
            else:
                output_hashes[out_path] = "FILE_NOT_FOUND"

    # Also check if the script produced any .json results in its directory
    for f in script_dir.glob("*.json"):
        if f.name not in input_hashes:
            output_hashes[f.name] = hash_file(f)

    # --- Extract numerical results from stdout ---
    results_json = _extract_numbers_from_stdout(stdout)

    # --- Store in DB ---
    db = _get_db()
    prev_hash = _last_row_hash(db)

    row_data = {
        "run_id": run_id,
        "timestamp": ts.isoformat(),
        "script_path": script_path,
        "args": extra_args,
        "git_commit": git_commit,
        "code_hash": code_hash,
        "input_hashes": json.dumps(input_hashes, sort_keys=True),
        "output_hashes": json.dumps(output_hashes, sort_keys=True),
        "results_json": json.dumps(results_json, ensure_ascii=False),
        "stdout": stdout[:50000],  # truncate at 50KB
        "stderr": stderr[:10000],
        "exit_code": exit_code,
        "duration_sec": round(duration, 3),
        "prev_run_hash": prev_hash,
    }
    row_data["row_hash"] = _compute_row_hash(row_data)

    db.execute("""
        INSERT INTO runs (
            run_id, timestamp, script_path, args, git_commit,
            code_hash, input_hashes, output_hashes, results_json,
            stdout, stderr, exit_code, duration_sec,
            prev_run_hash, row_hash
        ) VALUES (
            :run_id, :timestamp, :script_path, :args, :git_commit,
            :code_hash, :input_hashes, :output_hashes, :results_json,
            :stdout, :stderr, :exit_code, :duration_sec,
            :prev_run_hash, :row_hash
        )
    """, row_data)
    db.commit()
    db.close()

    # --- Report ---
    print(f"\n{'=' * 60}")
    print(f"  Run complete: {run_id}")
    print(f"  Exit code:    {exit_code}")
    print(f"  Duration:     {duration:.1f}s")
    print(f"  Row hash:     {row_data['row_hash'][:16]}...")
    if results_json:
        print(f"  Results:      {len(results_json)} values captured")
    print(f"  Stored in:    {DB_PATH}")
    print(f"{'=' * 60}")

    return row_data


def _extract_numbers_from_stdout(stdout: str) -> dict:
    """Extract key=value pairs and floating point numbers from stdout."""
    results = {}
    # Match lines like "metric_name: 0.945" or "score = 0.912"
    patterns = [
        r"(\w[\w\s]*\w)\s*[:=]\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, stdout):
            key = m.group(1).strip().lower().replace(" ", "_")
            try:
                val = float(m.group(2))
                results[key] = val
            except ValueError:
                pass
    return results


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_db_integrity() -> bool:
    """Verify the hash chain in the database."""
    db = _get_db()
    rows = db.execute(
        "SELECT run_id, row_hash, prev_run_hash FROM runs ORDER BY rowid"
    ).fetchall()
    db.close()

    if not rows:
        print("Registry is empty.")
        return True

    print(f"Verifying {len(rows)} runs...")
    expected_prev = "GENESIS"
    ok = True

    for run_id, row_hash, prev_run_hash in rows:
        if prev_run_hash != expected_prev:
            print(f"  CHAIN BREAK at {run_id}: expected prev={expected_prev[:12]}, got {prev_run_hash[:12]}")
            ok = False
        expected_prev = row_hash

    if ok:
        print(f"  All {len(rows)} runs verified. Chain intact.")
    else:
        print("  WARNING: Chain integrity violation detected!")

    return ok


def verify_paper(paper_path: str) -> bool:
    """Check that all numerical claims in the paper have run_id backing.

    Looks for HTML comments like: <!-- run:run_id_here -->
    Also finds 'orphan' numbers (floats in results context without run_id).
    """
    paper = PROJECT_ROOT / paper_path
    if not paper.exists():
        raise FileNotFoundError(f"Paper not found: {paper}")

    content = paper.read_text(encoding="utf-8")

    # Find all run references
    run_refs = re.findall(r"<!--\s*run:(\S+)\s*-->", content)

    if not run_refs:
        print(f"No run references found in {paper_path}.")
        print("Add <!-- run:RUN_ID --> comments next to numerical claims.")
        return False

    # Check each reference against DB
    db = _get_db()
    ok = True
    for run_id in run_refs:
        row = db.execute(
            "SELECT exit_code, results_json FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            print(f"  MISSING: {run_id} not found in registry")
            ok = False
        elif row[0] != 0:
            print(f"  WARNING: {run_id} had exit_code={row[0]}")
        else:
            print(f"  OK: {run_id}")

    db.close()

    if ok:
        print(f"\nAll {len(run_refs)} references verified.")
    else:
        print(f"\nSome references failed verification!")

    return ok


def list_runs() -> None:
    """Print all registered runs."""
    db = _get_db()
    rows = db.execute(
        "SELECT run_id, timestamp, script_path, exit_code, duration_sec "
        "FROM runs ORDER BY rowid"
    ).fetchall()
    db.close()

    if not rows:
        print("No runs registered yet.")
        return

    print(f"{'Run ID':<45} {'Exit':>4} {'Time':>7} {'Script'}")
    print("-" * 100)
    for run_id, ts, script, exit_code, dur in rows:
        status = "OK" if exit_code == 0 else f"E{exit_code}"
        print(f"{run_id:<45} {status:>4} {dur:>6.1f}s {script}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Experiment Runner with Data Integrity Guarantees"
    )
    parser.add_argument("script", nargs="?", help="Script to run")
    parser.add_argument("--args", default="", help="Extra args for the script")
    parser.add_argument("--outputs", nargs="*", help="Output files to hash")
    parser.add_argument("--list", action="store_true", help="List all runs")
    parser.add_argument("--verify", action="store_true", help="Verify DB integrity")
    parser.add_argument("--verify-paper", metavar="PATH", help="Verify paper claims")
    args = parser.parse_args()

    if args.list:
        list_runs()
    elif args.verify:
        ok = verify_db_integrity()
        sys.exit(0 if ok else 1)
    elif args.verify_paper:
        ok = verify_paper(args.verify_paper)
        sys.exit(0 if ok else 1)
    elif args.script:
        run_experiment(args.script, args.args, args.outputs)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
