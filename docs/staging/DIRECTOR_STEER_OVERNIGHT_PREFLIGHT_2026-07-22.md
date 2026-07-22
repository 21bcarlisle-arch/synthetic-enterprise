# DIRECTOR STEER — Overnight pre-flight: verify the restarts, freeze the novelty, state the queue (2026-07-22)

**Type:** [STEER] — tonight-scoped. Purpose: maximise the probability of the first clean night under R17. The wiring ratification is in flight; this governs how tonight ends and runs.

## 1. Pre-flight evidence before the wiring turn ends (R9 — evidence, not narrative)

Before closing the current turn, verify and NTFY as a single pre-flight report:
- `ntfy_responder` and `supervisor` both up post-restart, fresh PIDs, boot SHA = the wired commit.
- One **signed test message** through the director-NTFY path end-to-end (sign → verify → ledger as a no-op) — proving the channel live, not just tested.
- `worker-tick` timer active with next-fire confirmed.
- Deadman consuming the rest-legitimate status line (tonight's earlier false STALL class — if its fix is in, prove it; if not, say so plainly rather than let it page falsely at 3am).
- **The known env-launch gap, checked tonight in the one place it matters:** every unit spawned by tonight's restarts has the NTFY env sourced. Not a blind fix of the whole class — a targeted verification that *tonight's* processes can page.

## 2. The overnight queue, stated explicitly (no drained-ambiguity)

The F1 conversations triad build proceeds when its propose-then-proceed window expires — that is the night's core work, hours of it, within standing authority, own commits. Behind it: any spec-reconciliation follow-ups already authorized. If all of that genuinely drains: forward-discovery register is empty by your own dispositions, so **rest-with-proof is the correct state** — publish the proof line and rest. A quiet night of proven rest is a SUCCESS, not a stall.

## 3. Novelty freeze until daylight

Tonight, touch **no further architecture**: no new daemons, no gate changes beyond the ratified wiring, no draw-logic edits, no scheduler experiments. Additive build work only (F1, follow-ups). Anything structural you become convinced of tonight: write the proposal, park it, morning [ACT]. The failure pattern all week has been one novel class per day — tonight we ship zero new classes.

**Risk & proportionality:** verification + queue statement + a restraint rule — all reversible, nothing built. Tag: **narrow/reversible — do it as the wiring turn's closing act.**

— Advisor, carrying the director's intent for a clean first night, 2026-07-22.
