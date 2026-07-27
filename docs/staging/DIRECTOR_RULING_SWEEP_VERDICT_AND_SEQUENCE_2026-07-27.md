# [DIRECTOR-RULING] — Suppression sweep accepted. Close the registration hole; Law C first; merit-order is the next product draw. (2026-07-27)

**Type:** [DIRECTOR-RULING] via advisor bridge. Verdict on `docs/observability/suppression_audit_2026-07-27.md`.

## 0. The sweep is ACCEPTED

Twelve mechanisms enumerated from the trailing-14-day log, each classified by failure direction, seven remediated or compliant, five open and assigned. The `what_still_pages` declaration with a fail-closed validator is the right mechanisation of the standing consequence. **Do not re-file the remediated rows** (2, 4, 5, 8, 9, 11, 12) — re-work on already-closed findings is its own waste class.

**Rows 8 and 11 are hereby the reference templates** for every future gate: the self-verifying push (fails noisy) and the BUILD-IN-PROGRESS guard (fails open toward work). A new suppression that cannot be written in one of those two shapes needs a stated reason.

## 1. Close the registration hole — the sweep's own honest gap (priority)

The audit states it plainly under scope honesty: the validator enforces the declaration on **registered** suppressions, but *registering* a newly-written one remains a convention. That is the identical shape as every failure this week — a sound mechanism with an optional path into it.

**Build the lint:** a check over `background/**` that identifies suppression-shaped code — quiet/early returns on a gate path, cooldown or throttle timestamps, `skip`/`suppress`/`fold`/`quiet` markers, any branch that returns "nothing to do" — and **fails the gate when such code is not present in `suppression_register.json`.** 

**It will produce false positives, and that is correct.** Under LAW A the required failure direction is noise. A developer silencing the lint must register the mechanism (with its `what_still_pages`) or state why it is not a suppression — either outcome is the goal. Do not tune the lint toward quiet to reduce its noise; add register entries instead. R15: an unregistered suppression added in a test fixture must fail the gate; a registered one with a declared pager must pass.

## 2. Sequence the three law-mints: C, then B, then A

**LAW C first — rows 6 and 7.** The enumeration publishing *"whole authorized set empty"* and the daily note reporting the law's **status** rather than its **effect** are the two mechanisms that made 42 hours invisible. Until the watchdog and the note derive their verdicts from **primary state** — the actual contents of `in_progress/`, the campaign registers, the defect ledger, the maturity map — every other control still rests on the machine's self-report, which is the thing that failed. R15: falsify the enumeration in a test; the watchdog and the note must both still report the truth.

**LAW B second — rows 1 and 10.** The pending-batch gate is still global rather than per-cluster; the external-blocked exclusion may leak across sibling lanes. This is what allowed one director-held population decision to stop the site, price-engine, billing and discovery lanes.

**LAW A third — row 3.** Real, but it already has the deadman's 6h hard cap as an independent backstop, so it is the least exposed. Give it its explicit re-arm when C and B are done.

## 3. The next PRODUCT draw, named now: merit-order reconstruction

This morning has been entirely machinery. That was legitimate — it was breakage remediation — but PRODUCT-FIRST stands: machinery only until the breakage is closed. **When the three law-mints and the lint have landed, the next product draw is the merit-order / gas-first reconstruction of the price engine.** It is simultaneously: the written unblock condition on the SSP baseline hold (2026-07-25), the answer to Board Spec 004's reconstructibility test (*"power must be substantially reconstructible from gas, carbon, demand and wind on ordinary days, or it was not formed, only generated"*), and the convergence point with Spec 001's gas-first finding. The director's standing instruction governs it: **right in the end, not looking right now** — mechanism diagnosis, never tuning toward the benchmark (R12), and the per-cell lift table stays the fixed scorecard with the naive baseline unmoved.

MC-2's collateral death-test continues in the value-chain lane and is unaffected by this sequencing.

**Risk & proportionality:** the lint touches the commit gate and will be noisy by design; the law-mints touch watchdog, gate and reporting logic — failing tests first, own commits. Tag: **proceed in the stated order.**

— Advisor bridge, carrying the director's ruling, 2026-07-27.
