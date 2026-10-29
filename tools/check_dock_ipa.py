#!/usr/bin/env python3
"""Check that a Madeira IPA contains the Dock host matching its runtime manifest.

Usage: python3 tools/check_dock_ipa.py path/to/Madeira.ipa
This is a static packaging check, not a runtime startup test.
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

PREFIX = "Payload/Madeira.app/"
DOCK = "arm64ec-windows/dockhost.exe"
MANIFEST = "runtime-build.json"


def check(ipa: Path) -> None:
    with zipfile.ZipFile(ipa) as archive:
        names = set(archive.namelist())
        manifest_path = PREFIX + MANIFEST
        if manifest_path not in names:
            raise ValueError("Missing runtime-build.json")
        manifest = json.loads(archive.read(manifest_path))
        files = manifest["components"]["dock"]["files"]
        if DOCK not in files:
            raise ValueError("Dock executable absent from manifest")
        for path, expected in files.items():
            member = PREFIX + path
            if member not in names:
                raise ValueError(f"Missing packaged Dock component: {path}")
            payload = archive.read(member)
            actual = hashlib.sha256(payload).hexdigest()
            if actual.lower() != expected.lower():
                raise ValueError(f"Checksum mismatch: {path}")
            if path == DOCK:
                if payload[:2] != b"MZ":
                    raise ValueError("Dock executable lacks MZ header")
                if len(payload) < 0x40:
                    raise ValueError("Dock executable truncated")
                pe_offset = int.from_bytes(payload[0x3c:0x40], "little")
                if payload[pe_offset:pe_offset + 4] != b"PE\x00\x00":
                    raise ValueError("Dock executable lacks PE signature")
            print(f"OK {path}: {len(payload)} bytes")
    print("Dock packaging checks passed. Device startup remains unverified.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 tools/check_dock_ipa.py Madeira.ipa")
    try:
        check(Path(sys.argv[1]))
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        sys.exit(f"FAIL: {exc}")
