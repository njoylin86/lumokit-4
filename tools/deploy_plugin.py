"""
deploy_plugin.py
Uploads wp-plugin/lumokit-bridge.php to the WordPress host via SFTP.

Reads SFTP credentials from .env:
  SFTP_HOST
  SFTP_PORT          (default 22)
  SFTP_USERNAME
  SFTP_PASSWORD
  SFTP_PLUGIN_PATH   (path on server)

Usage:
  python3 tools/deploy_plugin.py
"""

import os
import sys
from pathlib import Path

from env_loader import ROOT, load_env

load_env()

LOCAL_FILE = ROOT / "wp-plugin" / "lumokit-bridge.php"


def main() -> None:
    host     = os.getenv("SFTP_HOST", "").strip()
    port     = int(os.getenv("SFTP_PORT", "22") or "22")
    user     = os.getenv("SFTP_USERNAME", "").strip()
    password = os.getenv("SFTP_PASSWORD", "")
    remote   = os.getenv("SFTP_PLUGIN_PATH", "").strip()

    if not all([host, user, password, remote]):
        print("[SKIP] SFTP credentials not set in .env (SFTP_HOST/USERNAME/PASSWORD/PLUGIN_PATH).")
        print("       Fill them in to enable automatic plugin deploy.")
        sys.exit(0)

    if not LOCAL_FILE.exists():
        print(f"[ERROR] Local plugin file not found: {LOCAL_FILE}")
        sys.exit(1)

    try:
        import paramiko
    except ImportError:
        print("[ERROR] paramiko not installed. Run: pip install paramiko")
        sys.exit(1)

    print(f"[INFO] Connecting to {user}@{host}:{port} ...")
    transport = paramiko.Transport((host, port))
    transport.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Create remote directory tree if it doesn't exist
    remote_dir = str(Path(remote).parent)
    dirs = remote_dir.replace("\\", "/").split("/")
    current = ""
    for part in dirs:
        if not part:
            continue
        current = current + "/" + part if current else part
        try:
            sftp.stat(current)
        except FileNotFoundError:
            print(f"[INFO] Creating remote dir: {current}")
            sftp.mkdir(current)

    print(f"[INFO] Uploading {LOCAL_FILE.name} → {remote}")
    sftp.put(str(LOCAL_FILE), remote)

    sftp.close()
    transport.close()
    print(f"[OK]   Plugin deployed.")


if __name__ == "__main__":
    main()
