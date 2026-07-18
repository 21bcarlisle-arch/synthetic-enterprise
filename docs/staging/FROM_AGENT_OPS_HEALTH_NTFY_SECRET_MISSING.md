# [FROM AGENT → director/operator] Ops-health root cause: `background/.env.ntfy` is MISSING

**Priority (your 2026-07-19 console: "restore ops health first — a deaf, mute loop is the priority fix").**

**Diagnosis (done — this is as far as I can take it; the fix needs you):**
The "deaf, mute loop" has ONE root cause: **`background/.env.ntfy` is not on disk**, so `SE_NTFY_TOPIC` is unset.
`background/ntfy_utils.py` **raises at import** when the topic is unset (the 2026-07-08 rotation hardening —
"no committed default topic any more"). So EVERY daemon that imports it crashes on start:
- **staging_watcher: DOWN** (imports ntfy_utils → crash on start) — can't notify you of staged files.
- **ntfy send: fails** — I can't page you; that's why I'm using this file + LATEST instead.

**What only YOU / the operator can do (I will not fabricate or hunt a category-5 secret):**
Place `background/.env.ntfy` back on the box (Skynet/WSL) with the rotated `SE_NTFY_TOPIC=...`, then the
worker-seat launcher/systemd units source it and staging_watcher + ntfy_responder start cleanly. That single
file restores both hearing and speaking.

**Optional resilience follow-up (your call — I have NOT changed it):** make `ntfy_utils` fail-SOFT-but-LOUD
(log a prominent warning + no-op the send, instead of raising at import) so a future missing topic degrades
the loop to mute-and-loud rather than cascade-crashing daemons. Improves robustness; does not replace the secret.

**Meanwhile:** I poll `docs/staging/` myself (per standing note), so staging processing is NOT blocked by
staging_watcher being down — only YOUR notifications are. The core loop (sim-runner, supervisor, publish
pipeline) is healthy; I fixed a 7h publish-gate wedge + drained a 31-marker backlog earlier.
