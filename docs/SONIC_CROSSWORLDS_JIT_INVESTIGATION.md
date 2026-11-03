# Sonic Racing: CrossWorlds — JIT-pool exhaustion investigation

Status: **diagnosis confirmed from device log; runtime fix not yet implemented or tested.**

## Reproduction

- Madeira v0.2.0 (5), iPhone18,2, iOS 27.2
- Steam app 2486820
- Configured JIT pool: 1152 MB
- Game executable fixed-base window: 368 MB
- Available JIT region: 384 MB
- Windows process launch: `CreateProcess() returned 8`

## Evidence from user log

```text
[exe-window] widened to [0x140000000,0x157000000) 368MB for a large fixed-base image
ml1036: free holes >=64MB ... 0x135c8c000+163MB 0x157000000+396MB 0x1709a8000+246MB
ml1036: no hole fits a 1152MB pool — SHRINKING to 384MB
JIT pool: RX=0x157000000, RW=0x7000000000, size=384MB
```

The runtime finds no contiguous hole for the requested pool while holding the fixed-base executable window. The 384 MB fallback is insufficient for the game launch.

## Required implementation

1. Compare this fork against upstream `willfaust/Madeira` main and sync source plus git submodule SHAs before editing.
2. Locate `ml1036` pool-placement logic and `ml977` fixed-base executable-window reservation.
3. Instrument largest-hole discovery **before** JIT pool reservation, and log region provenance/VM protections.
4. Evaluate early placement or reservation that preserves the 368 MB executable window without overlapping iOS mappings. Do not assume moving the JIT pool into guest space is safe.
5. Ensure fallback handles allocation failure without corrupting mappings.
6. Add a regression test that models a 368 MB fixed-base image plus a 1152 MB JIT request and validates safe non-overlap.
7. Build and test on iOS with JIT and Memory+; verify actual pool size and absence of `0xc0000017` / `CreateProcess() returned 8`.

## Acceptance criteria

- Fixed-base executable window and JIT RX/RW mappings do not overlap.
- Requested JIT allocation succeeds where supported by actual free VA; otherwise a precise diagnostic explains the blocking map.
- Sonic Racing executable passes PE loading on the test device.
- No regression for smaller fixed-base images.

**No working fix, IPA, or successful gameplay is claimed by this document.**
