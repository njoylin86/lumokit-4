"""
drift_check.py — 3-way diff mellan bundle.json (source), live WP options,
och .last_pushed.json (snapshot från senaste lyckade push).

Förhindrar regression-typ från 2026-05-18: hela bundlen pushas vid varje deploy,
så om någon direkt-patchat live utan att uppdatera build_bundle.py blir patchen
överskriven nästa gång build_all.py körs. Drift-checken stoppar push i det läget.

Användning från build_all.py:
    drift = check_drift(bundle_components, wp_url, auth, snapshot_path)
    if drift.has_blocking_drift and not force_overwrite_drift:
        drift.print_report()
        sys.exit(1)
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


def _norm_component(c: dict) -> dict:
    """Reducera komponent till de fält som påverkar rendering — ignorerar
    nycklar som ACF kan lägga till (t.ex. WP-specifika defaultvärden)."""
    return {
        "html_template": (c.get("html_template") or "").strip(),
        "schema": c.get("schema") or [],
    }


def _eq(a: dict, b: dict) -> bool:
    return _norm_component(a) == _norm_component(b)


@dataclass
class ComponentDiff:
    block_name: str
    status: str  # "NEW" | "NOOP" | "SAFE" | "DRIFT" | "CONFLICT" | "NO_SNAPSHOT_DIFF"
    bundle_size: int = 0
    live_size: int = 0
    note: str = ""

    @property
    def blocking(self) -> bool:
        return self.status in ("DRIFT", "CONFLICT", "NO_SNAPSHOT_DIFF")


@dataclass
class DriftReport:
    diffs: list[ComponentDiff] = field(default_factory=list)
    have_snapshot: bool = False

    @property
    def has_blocking_drift(self) -> bool:
        return any(d.blocking for d in self.diffs)

    def by_status(self, status: str) -> list[ComponentDiff]:
        return [d for d in self.diffs if d.status == status]

    def print_report(self, force_overwrite_drift: bool = False) -> None:
        noop = self.by_status("NOOP")
        new = self.by_status("NEW")
        safe = self.by_status("SAFE")
        drift = self.by_status("DRIFT")
        conflict = self.by_status("CONFLICT")
        unknown = self.by_status("NO_SNAPSHOT_DIFF")

        print()
        print("=" * 72)
        print(" DRIFT-CHECK")
        print("=" * 72)
        if not self.have_snapshot:
            print(" [INFO] Ingen .last_pushed.json — kör 2-way diff (bundle vs live).")
            print("        Efter denna lyckade push sparas snapshot för 3-way nästa gång.")
            print()

        print(f"  NEW      (skapas)              : {len(new)}")
        print(f"  NOOP     (oförändrade, skippas): {len(noop)}")
        print(f"  SAFE     (source-ändring)      : {len(safe)}")
        print(f"  DRIFT    (live > source)       : {len(drift)}")
        print(f"  CONFLICT (båda ändrade)        : {len(conflict)}")
        if unknown:
            print(f"  DIFF     (utan snapshot)       : {len(unknown)}")
        print()

        for label, items in (("DRIFT", drift), ("CONFLICT", conflict), ("DIFF (utan snapshot)", unknown)):
            if not items:
                continue
            print(f"  ⚠️  {label}:")
            for d in items:
                print(f"     - {d.block_name:50s}  bundle={d.bundle_size:6d}  live={d.live_size:6d}  {d.note}")
            print()

        if self.has_blocking_drift:
            if force_overwrite_drift:
                print("  ⚠️  --force-overwrite-drift aktiv — pushar trots drift.")
            else:
                print("  [ABORT] Pushen skulle skriva över ändringar på live som inte finns i source.")
                print("          Antingen:")
                print("            1) Uppdatera build_bundle.py så source matchar live, eller")
                print("            2) Pulla live-versionen och baka in den i source, eller")
                print("            3) Kör med --force-overwrite-drift om du VET att source är rätt.")
        print("=" * 72)


def pull_live_components(wp_url: str, auth: tuple[str, str], timeout: int = 60) -> dict[str, dict]:
    """Returnerar dict[block_name -> component] från /lumokit/v1/components."""
    r = requests.get(
        f"{wp_url.rstrip('/')}/wp-json/lumokit/v1/components",
        auth=auth, timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        return {}
    return {c["block_name"]: c for c in data if c.get("block_name")}


def load_snapshot(path: Path) -> dict[str, dict] | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(raw, list):
        return {c["block_name"]: c for c in raw if c.get("block_name")}
    if isinstance(raw, dict):
        return raw
    return None


def save_snapshot(path: Path, components: list[dict]) -> None:
    """Spara komponenter som pushats. Kör efter lyckad push i build_all.py."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {c["block_name"]: c for c in components if c.get("block_name")}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def check_drift(
    bundle_components: list[dict],
    wp_url: str,
    auth: tuple[str, str],
    snapshot_path: Path,
) -> DriftReport:
    """3-way diff. Hämtar live från WP. Klassificerar varje komponent."""
    bundle_map = {c["block_name"]: c for c in bundle_components if c.get("block_name")}
    live_map = pull_live_components(wp_url, auth)
    snap_map = load_snapshot(snapshot_path)
    have_snap = snap_map is not None

    report = DriftReport(have_snapshot=have_snap)

    for name, b in bundle_map.items():
        b_size = len(b.get("html_template") or "")
        if name not in live_map:
            report.diffs.append(ComponentDiff(name, "NEW", b_size, 0))
            continue

        live = live_map[name]
        live_size = len(live.get("html_template") or "")

        if _eq(b, live):
            report.diffs.append(ComponentDiff(name, "NOOP", b_size, live_size))
            continue

        # bundle ≠ live — klassificera med snapshot
        if not have_snap:
            report.diffs.append(ComponentDiff(
                name, "NO_SNAPSHOT_DIFF", b_size, live_size,
                "skiljer från live; ingen snapshot för 3-way"
            ))
            continue

        snap = snap_map.get(name)
        if snap is None:
            # Snapshot saknar denna komponent — antagligen ny i source sedan senaste snapshot
            report.diffs.append(ComponentDiff(
                name, "NO_SNAPSHOT_DIFF", b_size, live_size,
                "saknas i snapshot — okänt ursprung"
            ))
            continue

        bundle_changed = not _eq(b, snap)
        live_changed = not _eq(live, snap)

        if not bundle_changed and live_changed:
            report.diffs.append(ComponentDiff(
                name, "DRIFT", b_size, live_size,
                "source orörd, live ändrad sen senaste push"
            ))
        elif bundle_changed and not live_changed:
            report.diffs.append(ComponentDiff(name, "SAFE", b_size, live_size))
        elif bundle_changed and live_changed:
            report.diffs.append(ComponentDiff(
                name, "CONFLICT", b_size, live_size,
                "både source och live har ändrats sen senaste push"
            ))
        else:
            # Bägge orörda men ändå _eq False? Numerisk normaliseringskrock.
            report.diffs.append(ComponentDiff(name, "NOOP", b_size, live_size))

    return report
