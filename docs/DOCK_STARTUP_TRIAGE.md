# Madeira Dock startup triage (iOS 27)

## Reproduction

Device: iPhone 17 Pro, iOS 27 beta. Cat-Ling-derived Actions IPA. Wine desktop and Notepad work, but multiple installed Steam games remain at `Starting Madeira Dock...` / `Still starting Madeira Dock...`. Valve client components are installed. Steam UI not appearing is normal for headless Dock and does not establish a failure by itself.

## What this does and does not establish

This is a shared Dock startup failure candidate, **not** proof that `dockhost.exe` crashes or that image-map guard is broken. No guest Dock stage report was observed in the visible UI. Preserve the Steam prefix and authentication state during diagnosis.

## Investigate in order

1. Capture `[dock-launch]` lines, including `image-retire=1` and `image-map-guard=1`, plus the command used to start `explorer.exe /desktop=madeira,... dockhost.exe`.
2. Verify whether `C:\madeira-dock.txt` is created and whether `[dock-report]` stages advance. Do not log token contents or auth-file paths.
3. If the host starts but no report appears, distinguish PE loader failure, missing DLL/imports, and image-map deadlock before touching Steam authentication.
4. If a report appears, record numeric stages (`load-client-begin`, `probe-start-bits`, etc.) and the last stage reached. Preserve fail-closed behavior for unsupported Steam client DLL fingerprints.
5. Add a bounded startup watchdog with a diagnostic error state only after identifying the actual lifecycle callback. Never infer a process exit solely from the absence of a report.
6. Rebuild app and Dock submodule together, validate IPA contents, and test on device before claiming a fix.

## Safety

Do not print refresh tokens, usernames, SteamIDs, authentication file paths, or private Steam data. Do not bypass Steam license checks. Do not reset or delete the prefix as a first-line diagnostic step.

## Relevant implementation documentation

See `docs/MADEIRA_DOCK.md` for Dock session environment, `MADEIRA_IMAGE_MAP_GUARD`, `MADEIRA_JIT_IMAGE_RETIRE`, and report semantics. The Dock implementation is a separate Git submodule; changes to its source require a corresponding submodule commit and parent-repository pointer update.
