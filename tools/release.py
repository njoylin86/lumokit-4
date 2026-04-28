"""
release.py — automatiserad versionshantering för LumoKit.

Hanterar TVÅ saker:

1. Bridge-versionen (wp-plugin/lumokit-bridge.php)
   python3 tools/release.py bridge patch    (1.0.0 → 1.0.1, bugfix)
   python3 tools/release.py bridge minor    (1.0.0 → 1.1.0, ny feature)
   python3 tools/release.py bridge major    (1.0.0 → 2.0.0, breaking change)

2. Klient-releases (taggar nuvarande state som <client>/vN.M.P)
   python3 tools/release.py client patricia-teles patch  (1.0.0 → 1.0.1)
   python3 tools/release.py client patricia-teles minor  (1.0.0 → 1.1.0)
   python3 tools/release.py client patricia-teles major  (1.0.0 → 2.0.0)

Båda kommandona:
  - Bumpar version-konstant (om bridge)
  - Frågar om commit-meddelande och release-anteckningar
  - Skapar och pushar git-tag automatiskt
  - Uppdaterar CHANGELOG.md (för klient)
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRIDGE_FILE = ROOT / "wp-plugin" / "lumokit-bridge.php"
VERSION_RE = re.compile(r"define\(\s*'LUMOKIT_BRIDGE_VERSION',\s*'([0-9]+\.[0-9]+\.[0-9]+)'\s*\)")


def run(cmd: list[str], check: bool = True) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if check and result.returncode != 0:
        print(f"[ERROR] {' '.join(cmd)}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def bump_version(current: str, kind: str) -> str:
    major, minor, patch = (int(x) for x in current.split("."))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unknown bump kind: {kind}")


def latest_client_tag(client: str) -> str | None:
    out = run(["git", "tag", "-l", f"{client}/v*"], check=False)
    if not out:
        return None
    versions = []
    for tag in out.splitlines():
        m = re.match(rf"^{re.escape(client)}/v([0-9]+)\.([0-9]+)\.([0-9]+)$", tag)
        if m:
            versions.append(tuple(int(x) for x in m.groups()))
    if not versions:
        return None
    versions.sort()
    last = versions[-1]
    return f"{last[0]}.{last[1]}.{last[2]}"


def confirm_clean_tree() -> None:
    out = run(["git", "status", "--porcelain"], check=False)
    if out.strip():
        print("[ERROR] Du har ocommittade ändringar. Committa eller stash:a först.")
        print(out)
        sys.exit(1)


def release_bridge(kind: str) -> None:
    text = BRIDGE_FILE.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if not m:
        print("[ERROR] LUMOKIT_BRIDGE_VERSION-konstant saknas i lumokit-bridge.php.")
        sys.exit(1)
    current = m.group(1)
    new = bump_version(current, kind)

    print(f"\n  Bridge-version: {current} → {new}  ({kind} bump)")
    note = input("  Vad ändrades? (kort beskrivning, sparas i tag-meddelandet): ").strip()
    if not note:
        print("[ABORTED] Ingen beskrivning angiven.")
        sys.exit(0)

    confirm_clean_tree()

    BRIDGE_FILE.write_text(VERSION_RE.sub(
        f"define( 'LUMOKIT_BRIDGE_VERSION', '{new}' )", text), encoding="utf-8")

    run(["git", "add", str(BRIDGE_FILE)])
    run(["git", "commit", "-m", f"bridge: bump to v{new}\n\n{note}"])
    run(["git", "tag", "-a", f"bridge/v{new}", "-m", f"Bridge v{new}: {note}"])
    print(f"\n[OK] Tagged bridge/v{new}. Push:")
    print(f"     git push origin master bridge/v{new}")


def release_client(client: str, kind: str) -> None:
    client_dir = ROOT / "clients" / client
    if not client_dir.exists():
        print(f"[ERROR] Klient-mappen finns inte: {client_dir.relative_to(ROOT)}")
        sys.exit(1)

    last = latest_client_tag(client)
    new = bump_version(last or "0.0.0", kind) if last else "1.0.0"

    if last:
        print(f"\n  Klient: {client}")
        print(f"  Senaste tag: {client}/v{last} → ny tag: {client}/v{new}  ({kind} bump)")
    else:
        print(f"\n  Klient: {client}  (ingen tidigare tag)")
        print(f"  Första release: {client}/v{new}")
    note = input("  Vad är nytt i denna release? (kort beskrivning): ").strip()
    if not note:
        print("[ABORTED] Ingen beskrivning angiven.")
        sys.exit(0)

    confirm_clean_tree()

    # Append to CHANGELOG.md
    changelog = client_dir / "CHANGELOG.md"
    today = date.today().isoformat()
    bridge_version = "unknown"
    text = BRIDGE_FILE.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    if m:
        bridge_version = m.group(1)

    new_entry = (
        f"## [{new}] - {today}\n"
        f"- Bridge version: {bridge_version}\n"
        f"- {note}\n\n"
    )
    if changelog.exists():
        existing = changelog.read_text(encoding="utf-8")
        # Insert under the title (first line) if format matches
        lines = existing.splitlines(keepends=True)
        title_end = 1 if lines and lines[0].startswith("#") else 0
        new_text = "".join(lines[:title_end]) + "\n" + new_entry + "".join(lines[title_end:])
    else:
        new_text = f"# Changelog — {client}\n\n" + new_entry
    changelog.write_text(new_text, encoding="utf-8")

    run(["git", "add", str(changelog)])
    run(["git", "commit", "-m", f"client: {client} v{new}\n\n{note}"])
    run(["git", "tag", "-a", f"{client}/v{new}", "-m", f"{client} v{new}: {note}"])
    print(f"\n[OK] Tagged {client}/v{new}. Push:")
    print(f"     git push origin master {client}/v{new}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    target = sys.argv[1]
    if target == "bridge":
        release_bridge(sys.argv[2])
    elif target == "client":
        if len(sys.argv) < 4:
            print("Usage: tools/release.py client <name> <patch|minor|major>")
            sys.exit(1)
        release_client(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown target: {target}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
