"""
snapshot_live.py — pulla alla komponenter från live och spara som
clients/<client>/.last_pushed_components.json. Drift-checken i build_all.py
använder denna fil som 3-way baseline.

Princip: live är auktoritär. Source/bundle ska aldrig avvika från live utom
när du AVSIKTLIGT vill ändra. Snapshota efter varje wp-side backup-restore
eller större manuell ändring, så drift-check vet vad "korrekt state" är.

Användning:
    python tools/snapshot_live.py --client alvsjotandvard
    python tools/snapshot_live.py --client alvsjotandvard --production
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

import requests
from env_loader import ROOT, load_env

load_env()

WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
WP_ENV          = os.getenv("WP_ENV", "development").strip().lower()


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshota live-komponenter som drift-baseline.")
    parser.add_argument("--client", required=True, help='Klientnamn, t.ex. "alvsjotandvard".')
    parser.add_argument("--production", action="store_true", help="Tillåt mot WP_ENV=production.")
    args = parser.parse_args()

    if WP_ENV == "production" and not args.production:
        print(f"[BLOCKED] WP_ENV=production — kör med --production om du är säker.")
        sys.exit(1)
    if WP_ENV == "production":
        print(f"[WARN] Snapshotar från PRODUCTION: {WP_URL}")

    out_path = ROOT / "clients" / args.client / ".last_pushed_components.json"

    print(f"[INFO] Hämtar live-komponenter från {WP_URL}/wp-json/lumokit/v1/components ...")
    r = requests.get(
        f"{WP_URL}/wp-json/lumokit/v1/components",
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        print(f"[ERROR] Oväntat svar från endpoint: {type(data).__name__}")
        sys.exit(1)

    payload = {c["block_name"]: c for c in data if c.get("block_name")}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    print(f"[OK] {len(payload)} komponent(er) snapshotade till:")
    print(f"     {out_path.relative_to(ROOT)}")
    print(f"     Drift-check i build_all.py kommer nu jämföra source mot denna baseline.")


if __name__ == "__main__":
    main()
