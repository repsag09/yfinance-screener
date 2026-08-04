#!/usr/bin/env python3
"""
relays_entry.py
Relays.app entrypoint wrapper for the stock-screener Alpaca integration.

This file is a small wrapper that invokes stock-screener/trade.py using subprocess
so the existing CLI continues to work unchanged.

relays.app can call handler(event) as the entrypoint. The handler returns a JSON-serializable
result with stdout/stderr and the exit code from the invoked script.

Environment variables used:
- SCAN_PATH (default: stock-screener/stocks_scan.csv)
- RUN_REAL (set to "true" to submit paper orders; default: false)
- PAPER_CAPITAL (optional override; default 5000)
- POSITION_PCT (optional override; default 0.10)
- APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL (Alpaca keys; set in relays UI)

Example relays.env settings:
  RUN_REAL=false
  SCAN_PATH=stock-screener/stocks_scan.csv
  PAPER_CAPITAL=5000
  POSITION_PCT=0.10

"""
import os
import subprocess
import logging
import json
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def _build_command(scan: str, dry_run: bool, capital: str | None, position_pct: str | None) -> list:
    cmd = ["python", "stock-screener/trade.py", "--scan", scan]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--no-dry-run")
    if capital:
        cmd.extend(["--capital", capital])
    if position_pct:
        cmd.extend(["--position-pct", position_pct])
    return cmd


def handler(event: Any = None) -> Dict[str, Any]:
    """Entry point for relays.app. Returns a dict with the run result.

    The 'event' parameter is accepted for compatibility with platforms that pass an event.
    """
    scan = os.getenv("SCAN_PATH", "stock-screener/stocks_scan.csv")
    run_real = os.getenv("RUN_REAL", "false").lower() in ("1", "true", "yes")
    dry_run = not run_real
    capital = os.getenv("PAPER_CAPITAL")
    position_pct = os.getenv("POSITION_PCT")

    cmd = _build_command(scan=scan, dry_run=dry_run, capital=capital, position_pct=position_pct)

    logging.info("Running command: %s", " ".join(cmd))
    try:
        completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
        result = {
            "ok": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "dry_run": dry_run,
            "scan_path": scan,
        }
        logging.info("Command finished with returncode=%s", completed.returncode)
        return result
    except Exception as e:
        logging.exception("Failed to run trade script")
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    # Allow manual local invocation for testing
    out = handler()
    print(json.dumps(out, indent=2))
