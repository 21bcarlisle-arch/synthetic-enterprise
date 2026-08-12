# [ADVISOR-PROPOSAL] — Seat cut-over: the option this week proved we need (2026-08-07)

**Severity:** LATENT · **Lane:** A_strategy_governance

**Type:** [PROPOSAL — requirements, not mechanisms]. Director-prompted after a five-day seat outage. Lands in the OPS lane ("Running the Machine"), where the posture shelf already holds the never-built DR atom — this is its flesh. Evidence: 2026-08-03→08 the resident seat was dark and unreachable; work continued only by improvised cloud sessions; no sanctioned path existed to stand a replacement seat. Problem and requirements below; every mechanism is the worker's.

## What already exists (built this week, accidentally as DR)
Residency = one marker file; every guard keys on it (PRs #7/#12/#13). The restart runbook is already a bring-up-on-any-box procedure whose final proof (the tick draws work) is box-independent. The architecture's own laws minimise seat-local state: repo is truth, caches re-prefetch, the event spine is pushed.

## The requirements (the missing three-quarters)
**R1 — The seat must be standable from OFF the seat.** A dead box cannot be a dependency of its own replacement. Therefore: (a) a bootstrap path, versioned IN the repo, that takes a fresh Ubuntu box to seat-ready (units, dirs, deps) minus secrets; (b) a **secrets escrow** — the small set that makes a box the seat (NTFY credentials, git credential, Claude auth) held safely off-box by the director; (c) an explicit census of anything else seat-local, each item classified CACHE (re-derivable — the 123MB market data), MOVABLE (nothing should be in this class), or LOSABLE-WITH-EYES-OPEN (uncommitted work — see R3).
**R2 — Two cut-over classes, both written down.** Class A *graceful* (old seat reachable): quiesce → final push → marker deleted there → marker created here → runbook Phases 1–4 → old box demoted. Class B *dead-box* (this week's case): stand new seat from repo + escrow alone; accept the loss class in R3. This week we needed Class B and it did not exist.
**R3 — The uncommitted-age alarm.** The only thing Class B can lose is work not yet on origin. The seat therefore self-checks local-ahead-of-origin age and alarms past a threshold — the dead-man's principle applied to unpushed state.
**R4 — One seat on Earth.** The marker exists on exactly one box; cut-over is the only sanctioned way it moves; creating a second marker is the double-launch class at full scale and the guards' structural-lock thinking should extend here (a seat that detects a second resident heartbeat on origin screams).
**R5 — The drill, or it's fiction.** Checks must be seen to fail — applied to infrastructure: the seat's own Birth Certificate gains its *proven failure* field only when a dead-box rebirth has been executed at least once on a scratch box, timed. Cadence thereafter per epoch boundary. A cold standby landing zone (a capacity-tested free-tier or ~€4 VM, bootstrap proven once, then left off) turns cut-over from days into hours at ≈£0 — with one named design decision on any non-x86/GPU-less target: the local-model routing (smaller model or API) is the director's call, not an implementation detail.

## Acceptance (falsifiable)
The option EXISTS when: R1's bootstrap + escrow are real; both class procedures are written; the alarm runs; and one timed Class-B drill has succeeded end-to-end, its duration recorded. Until then, DR remains a level-0 atom and this week remains repeatable.

— Advisor proposal, 2026-08-07; mechanisms, sequencing, and the map filing are the worker's.
