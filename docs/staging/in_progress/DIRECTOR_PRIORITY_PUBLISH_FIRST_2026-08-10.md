> **STATUS 2026-08-10 (worker tick), parked here because ONE sub-item is genuinely still open.**
> - **Draw 1 — clear the named red: DONE**, `1060fd727` (pushed). The allowlist entry
>   `simulation.run_phase2b -> company.billing.arrears_engine` was stale because the crossing died as
>   a side effect of `15125f388` (D21). Allowlist 3→2; the disposition register's matching `owed`
>   entry — its own second red at HEAD from the same cause — is now `cut`. 71 tests green.
> - **Draw 2 — the class fix: ALREADY LANDED** before this instruction arrived.
>   `background/derived_artefact_register.py` is wired into the publish path at
>   `process_run_complete._repair_derived_artefacts_in` (called at line ~875, between the checkout and
>   the gate), rendering from HEAD rather than the working tree.
> - **Draw 3 — publish and flush: OPEN, and it is the publisher's act, not a tick's.**
>   `process_run_complete.py` is running now on `run_complete_20260809T132837Z.md` with 63 markers
>   queued. **What unblocks it:** that run reaching a green gate at a HEAD that contains `1060fd727`.
>   A tick must NOT start a second publisher — two on one working tree is the concurrent-writer
>   hazard. Re-surfacing this item is correct until the publish lands; the disposition each time is
>   *check the gate state, don't launch a rival publisher*.

# [DIRECTOR-PRIORITY] — Publish first: three draws, in order, before any feature work (2026-08-10)

**Type:** [PRIORITY]. Episode: 19h, 104 consecutive failures, 62 markers. The last five causes are one species — derived artefacts (ledgers, allowlists, ratchet docs) going stale at HEAD because work lands faster than hand-refreshing. Your own 03:59 recommendation is the cure and it keeps losing draws to feature work. Ordered now:

**1. Clear the named red.** The alarm finally names it: `test_epistemic_wall_indirect_ratchet::test_indirect_allowlist_has_no_stale_entries` at HEAD — a stale allowlist row from KNIFE3's own cuts. Fix exactly that, at HEAD.

**2. Land your own class fix.** Re-render every derived projection (forward-attachment ledger, allowlists, ratchet docs) BEFORE the gate, committed by pathspec — pure functions of committed sources, cannot mask a defect, per your 03:59 filing. This ends the species, not the instance.

**3. Publish and flush.** One clean publish, 62 markers drain-superseded, site current, the £1,526,252.39 candidate baseline printed and adopted per the standing recommendation.

**Until 1–3 land: no feature draws.** KNIFE remainder, Expert Hour #6, everything keeps — 19 hours of red on the public proof surface outranks all of it, by the alarm's own doctrine. The H39-motivated promotion-gate hardening (refuse level raises with dirty file_scope) proceeds on its already-stated window — it is this disease's other half.

— Advisor, standing doctrine; the alarm's draw-these-FIRST is hereby a director instruction with teeth.
