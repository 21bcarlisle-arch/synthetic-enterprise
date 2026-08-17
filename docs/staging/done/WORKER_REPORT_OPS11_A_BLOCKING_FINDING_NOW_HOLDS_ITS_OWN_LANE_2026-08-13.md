# [WORKER-REPORT] OPS11 — a BLOCKING finding now holds its own lane, and nothing else (2026-08-13)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the mechanism is landed and proven both
ways; nothing here is owed.

**Atom:** `OPS11_blocking_lane_refusal` **L0 → L2**, self-certified into
`gate_authorizations.jsonl` (R16). Deliverable 3 of the WORK THIS CREATES block in
`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 2.

## What landed

A BLOCKING finding says an instrument in that area may be wrong. Certifying a new level while
that instrument is the thing doing the certifying means the new work is certified by the lie.
Until today that was a sentence in a ruling; now it is a refusal.

**It fires at both places a level is actually recorded**, and that is not belt-and-braces:

* `background.gate_authorization.record_level_up_self_certified` raises `LaneBlockedError`
  **before** appending — a refused raise leaves **no row**, because the row is exactly what the
  commit gate later reads as authority.
* `tools/level_promotion_gate.py` gains a **third control**, after the recorded-check and the
  built-check. A row recorded while the lane was clear still satisfies the recorded-check on a
  commit made days later, so only this half sees the lane **at the moment the map moves**.

Both read **one** implementation (`gate_authorization.lane_blockers`). The risk with a second
copy is never that it agrees with itself; it is that it drifts.

The refusal names **every** blocking finding and its repo-relative path. That is the exit
criterion, not decoration: a refusal that does not say what blocks it cannot be discharged.

## The lane bound, proven in both directions

The real-world twin is a calibration hold — one bench is out of certification and stops issuing
certificates; the rest of the lab works on. A repo-wide freeze would be routed around inside a
day, so the lane bound is what makes the control survivable rather than a politeness.

At the writer: `test_a_live_in_lane_blocker_refuses_the_level_record` and
`test_a_blocker_in_another_lane_does_not_refuse` (the *same* blocker, D_billing_metering
untouched, row lands). At the gate:
`test_a_raise_in_an_UNHELD_lane_PASSES_while_the_other_lane_is_held` puts both atoms through
**one** call, so the two directions cannot be separately arranged.

Verified live against the real `maturity_map.yaml`: with a synthetic BLOCKING document in a copy
of the staging root, OPS11's own raise was refused by name and a `D_billing_metering` raise
recorded in the same sequence.

## R11 — the RELEASE is tested, not just the hold

Clause 2 gives two releases and both are asserted **on the ledger** (the row actually lands),
never on the absence of an exception — a hold whose release does nothing is the defect R11 names.

1. **Repair** — the document gains a checked `**Discharged:**` line, which
   `finding_severity.parse_severity_file` already reads down to RECORDED. The release is the
   *same parse* as the hold, so there is no second list that could disagree. A discharge citing a
   test node that does not exist releases nothing
   (`test_a_discharge_naming_a_nonexistent_test_releases_nothing`).
2. **Record and accept** — a `LIMITATION_ACCEPTED` row naming the lane, the finding, and why the
   move is sound in spite of it. It is per-`(lane, finding)` on purpose: a blanket "accept this
   lane" row would clear findings nobody enumerated, which is the shape of every rubber stamp.
   It keys on the **basename**, so archiving the finding to `done/` does not un-release it.

## Fail-closed, and why that is not a wedge

An absent or unreadable staging root, an UNCLASSIFIED document, and an atom whose lane cannot be
determined all read as UNKNOWN and **refuse** — an unavailable check is a FAILED check. This
project has wedged its own publishing with fail-closed controls before, so the reasoning is
stated **in the code**: it is safe here only because release 2 always exists and depends on
nothing the check depends on. Writing a ledger row cannot become unavailable when the index does.
`test_an_absent_staging_root_refuses_and_is_still_dischargeable` proves both halves in one test.

An UNCLASSIFIED document holds **every** lane, deliberately — its severity could be BLOCKING and
its lane is unknown, so attributing it to no lane would make mangling a header the cheapest way
to clear a hold. The cheaper fix is one header line.

## R15, both ways

Each mutation is loaded from a **copy** of the module under a fresh name, with a
uniqueness-asserted anchor so a no-op mutation cannot pass for the wrong reason:

* **blocking check dropped** — kills `test_a_live_in_lane_blocker_refuses_the_level_record`; the
  unaffected-lane direction still passes under it.
* **lane scope dropped** (every lane refused) — kills
  `test_a_blocker_in_another_lane_does_not_refuse`; the hold still holds under it.

The second direction is the one that matters most here: without it the control could be "proven"
by a version that refuses everything, which is precisely the freeze clause 2 forbids. The gate
half carries the same pair as neuter tests.

`tests/background/test_gate_authorization.py` 23 passed · `tests/tools/test_level_promotion_gate.py`
30 passed · the seven suites that import `gate_authorization` 202 passed, 1 skipped.

## What this does NOT prove, stated because it bounds the claim

`python3 -m background.finding_severity` today: **94 documents, 0 BLOCKING**, 55 LATENT, 39
RECORDED, 0 UNCLASSIFIED. OPS9 measured 35 blockers (29 of them H_harness) on 2026-08-12; OPS10's
consolidation and the discharge field have since cleared them. **So this control lands quiescent
and refuses nothing today.** Its firing is proven on synthetic populations and on the real map
with a synthetic blocker — not yet on a live one. The first real BLOCKING finding in any lane is
what exercises it in anger, and the honest reading is that today it is armed, not tested by
weather.

The atom's own L0→L2 record went through the refusal it just built (H_harness clear), which is
the smallest true statement of the mechanism working end to end.

## Not done, deliberately

`OPS12_blockers_ahead_of_disposition` — the other consumer of the OPS9 parse — is a separate
atom. This one refuses raises; it does not re-order the draw.
