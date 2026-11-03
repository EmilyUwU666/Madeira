#!/usr/bin/env python3
"""Regression fixture for Sonic Racing CrossWorlds memory-layout diagnostics.

This checks a captured log, not the iOS allocator itself.
Run: python3 tests/host/check-sonic-jit-log.py path/to/madeira-log.txt
"""
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: check-sonic-jit-log.py <madeira-log.txt>")
log = Path(sys.argv[1]).read_text(errors="replace")
assert "SonicRacingCrossWorlds" in log, "Not a Sonic Racing launch log"
assert "widened to [0x140000000" in log, "Missing fixed-base image-window diagnostic"
requested = re.search(r"no hole fits a (\d+)MB pool.*SHRINKING to (\d+)MB", log)
assert requested, "Missing pool shrink diagnostic"
want, actual = map(int, requested.groups())
print(f"Requested JIT pool: {want} MB; mapped fallback: {actual} MB")
assert actual < want, "Expected the captured fallback to be smaller"
if actual < 500:
    print("WARNING: fallback is below Madeira's documented 500 MB low-pool threshold")
print("This fixture verifies diagnostics only; it does not prove a runtime fix.")
