# [DIRECTOR-PRIORITY] — Sim-runner red loop: triage first (2026-08-08)

**Type:** [PRIORITY FLAG — director-instructed, advisor-staged, 15:40 BST]. Not a diagnosis; a draw-priority.

**Observed (mirror, all UTC):** six consecutive sim run failures — 13:53 (200s), 14:01 (184s), 14:09 (184s), then **post-`10e8ca6` landing**: 14:18 (187s), 14:26 (177s), 14:34 (180s). Deterministic duration band; ~8-min retry cadence; log at machine-local `sim-runner-log.md`. The stranded-build landing did NOT cure it.

**Request:** after the current turn completes, make this loop the first draw — it burns cycles every 8 minutes, masks wake health, and each failed run may be appending markers/logs (the lifecycle class). Batch consumption second; the 28 documents keep.

**Suspect classes, offered not prescribed:** (a) week-merge × runtime interaction — a sim-side reader of something the week changed (the simplifications extraction ported six consumers; sim-path readers were believed zero — verify, don't trust); (b) local cache/state staleness against merged expectations; (c) pre-existing run-marker backlog physics. The log will out-vote all three.

— Advisor, on the director's explicit instruction; see-and-correct applies to everything here.
