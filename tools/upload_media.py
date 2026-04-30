"""
upload_media.py
Uploads images from .tmp/content/image/ to the WordPress media library
and maintains a manifest mapping local filename -> {id, source_url}.

Usage:
    python tools/upload_media.py                     # default dir + manifest
    python tools/upload_media.py --dir <path>        # alternate source dir
    python tools/upload_media.py --manifest <path>   # alternate manifest path
    python tools/upload_media.py --force             # re-upload everything
    python tools/upload_media.py --dry-run           # print actions, don't upload
    python tools/upload_media.py --production        # allow upload to prod WP

The manifest is keyed by path relative to the source dir, e.g.:
    {
      "hero.jpg":         { "id": 123, "source_url": "https://.../hero.jpg", "size": 4321 },
      "team/founder.png": { "id": 124, "source_url": "https://.../founder.png", "size": 8765 }
    }

Skip rule: if a file's size matches the manifest entry, the upload is skipped.
If the size differs, the old WP media item is deleted (force=true) and the file is re-uploaded.
"""

import argparse
import json
import mimetypes
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

MEDIA_ENDPOINT      = f"{WP_URL}/wp-json/wp/v2/media"
DEFAULT_SOURCE_DIR  = ROOT / ".tmp" / "content" / "image"   # legacy fallback
DEFAULT_MANIFEST    = ROOT / ".tmp" / "content" / "_media_manifest.json"  # legacy fallback
ALLOWED_EXTENSIONS  = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def check_env_guard(allow_production: bool) -> None:
    if WP_ENV == "production" and not allow_production:
        print(f"[BLOCKED] WP_ENV is set to 'production' in .env")
        print(f"          Target: {WP_URL}")
        print(f"          Refusing to upload without explicit --production flag.")
        sys.exit(1)
    if WP_ENV == "production" and allow_production:
        print(f"[WARN] Uploading to PRODUCTION: {WP_URL}")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)


def discover_images(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        return []
    files = []
    for p in source_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(p)
    return sorted(files)


def delete_media(media_id: int) -> bool:
    response = requests.delete(
        f"{MEDIA_ENDPOINT}/{media_id}",
        params={"force": "true"},
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        timeout=30,
    )
    return response.status_code in (200, 410)


def upload_image(file_path: Path) -> dict | None:
    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime:
        mime = "application/octet-stream"

    with open(file_path, "rb") as fp:
        response = requests.post(
            MEDIA_ENDPOINT,
            headers={
                "Content-Type": mime,
                "Content-Disposition": f'attachment; filename="{file_path.name}"',
            },
            data=fp.read(),
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            timeout=120,
        )

    if response.status_code in (200, 201):
        data = response.json()
        return {
            "id": data.get("id"),
            "source_url": data.get("source_url"),
            "size": file_path.stat().st_size,
        }

    print(f"  [ERROR] HTTP {response.status_code} uploading '{file_path.name}'")
    try:
        print(f"          {response.json()}")
    except Exception:
        print(f"          {response.text}")
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload images to WP media library.")
    parser.add_argument("--client", help='Client name, e.g. "ostra-bageriet". Sets default --dir and --manifest to clients/<name>/.tmp/content/...')
    parser.add_argument("--dir", default=None,
                        help="Source directory of images")
    parser.add_argument("--manifest", default=None,
                        help="Manifest path")
    parser.add_argument("--force", action="store_true",
                        help="Re-upload every file, ignoring the manifest")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without uploading")
    parser.add_argument("--production", action="store_true",
                        help="Allow uploading to a production WP")
    args = parser.parse_args()

    check_env_guard(args.production)

    if args.client:
        client_tmp = ROOT / "clients" / args.client / ".tmp"
        default_dir      = client_tmp / "content" / "image"
        default_manifest = client_tmp / "content" / "_media_manifest.json"
    else:
        default_dir      = DEFAULT_SOURCE_DIR
        default_manifest = DEFAULT_MANIFEST

    source_dir    = Path(args.dir).resolve()    if args.dir      else default_dir
    manifest_path = Path(args.manifest).resolve() if args.manifest else default_manifest
    manifest      = load_manifest(manifest_path)

    files = discover_images(source_dir)
    if not files:
        print(f"[INFO] No images found in {source_dir}")
        return

    print(f"[INFO] Found {len(files)} image(s) in {source_dir}")
    if args.dry_run:
        print("[DRY-RUN] No uploads will be performed.")

    uploaded = skipped = replaced = failed = 0

    for file_path in files:
        rel_key  = file_path.relative_to(source_dir).as_posix()
        size     = file_path.stat().st_size
        existing = manifest.get(rel_key)

        if existing and not args.force and existing.get("size") == size:
            print(f"  [SKIP] {rel_key} (already uploaded, id={existing.get('id')})")
            skipped += 1
            continue

        if existing and existing.get("id"):
            action = "REPLACE"
            print(f"  [{action}] {rel_key} (size changed: {existing.get('size')} -> {size})")
            if not args.dry_run:
                if not delete_media(existing["id"]):
                    print(f"           [WARN] failed to delete old media id={existing['id']}, uploading new copy anyway")
        else:
            action = "UPLOAD"
            print(f"  [{action}] {rel_key} ({size} bytes)")

        if args.dry_run:
            continue

        result = upload_image(file_path)
        if result is None:
            failed += 1
            continue

        manifest[rel_key] = result
        save_manifest(manifest_path, manifest)
        if action == "REPLACE":
            replaced += 1
        else:
            uploaded += 1
        print(f"           id={result['id']} url={result['source_url']}")

    local_keys   = {p.relative_to(source_dir).as_posix() for p in files}
    orphaned     = sorted(k for k in manifest.keys() if k not in local_keys)
    if orphaned:
        print(f"\n[WARN] {len(orphaned)} manifest entry(ies) no longer have a local file:")
        for k in orphaned:
            print(f"       - {k} (id={manifest[k].get('id')})  # not auto-deleted")

    print(f"\n[DONE] uploaded={uploaded} replaced={replaced} skipped={skipped} failed={failed}")
    print(f"       manifest: {manifest_path}")


if __name__ == "__main__":
    main()
