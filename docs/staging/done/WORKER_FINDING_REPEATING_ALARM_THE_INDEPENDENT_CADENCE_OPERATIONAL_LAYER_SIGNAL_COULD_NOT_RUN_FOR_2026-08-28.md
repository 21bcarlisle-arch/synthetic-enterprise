**Severity:** LATENT · **Lane:** H_harness

# [OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer signal could not RUN for 4 consecutive check(s) (rc=2): pytest was interrupted during COLLECTION, so the marke

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer signal could not RUN for 4 consecutive check(s) (rc=2): pytest was interrupted during COLLECTION, so the marker expression `operational or join_report_only or scale_report_only` never selected anything and NO operational test was executed. This is NOT a daemon-lifecycle regression -- nothing about the operational layer has been shown to be broken, and the published site/report is unaffected. The operational layer is UNMONITORED until these files import cleanly:
  - tests/tools/test_phase_rx_track_record.py

Repair the import error at those paths, not the daemons.
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-28T19:26:27+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## RESOLVED 2026-08-28 22:26 UTC — the cause, and what it was not

The alarm was right about the shape and right to refuse the daemon-lifecycle diagnosis.
**One unimportable test module blinded the entire suite**, because pytest aborts COLLECTION
globally: `Interrupted: 1 error during collection` means the marker expression
`operational or join_report_only or scale_report_only` never selected anything, so the signal
could not run at all. rc=2 for five consecutive hourly checks.

**Cause.** Commit `0850eadcd` (R3 of the sourced-acquisition finding) deleted
`RESI_OFFER_COST_GBP = 50.0` and `IC_OFFER_COST_GBP = 200.0` from
`company/analytics/counterfactual_retention.py` — correctly: a retention offer is a DISCOUNT on
the next term, not a cash payment, so it costs a share of that customer's own revenue and costs
nothing at all if the customer leaves. R3 updated two of the three consumers. The third,
`tests/tools/test_phase_rx_track_record.py`, still imported both deleted names.

**Why the commit gate did not see it.** `tools/pre_commit_test_gate.py` selects tests by
filename stem and import graph. R3 touched `counterfactual_retention.py` and
`run_live_decisions.py`; neither selects `test_phase_rx_track_record.py`, whose stem names a
phase rather than either module. A selection-based gate cannot see a consumer it did not select
— and for an ImportError specifically, the blast radius is not that file, it is the whole
suite. That asymmetry is the finding, and it is filed separately as a gap in the gate.

**Repair.** The three stale tests are restated against the landed producer rather than deleted:

- the resi reconstruction now rebuilds `p_retain x discount x term_revenue`. Its fixture moved
  from `current_rate=200.0` to `80.0`, because at 200 the proposed rate is a large DECREASE,
  churn lands at 0.05, 0.05 sits below every tier in `CURRENT_POLICY`, and the discount — the
  whole cost term the test exists to check — is structurally 0.0. A fixture parked on the
  no-offer branch cannot see a mispricing, so the test now asserts `discount_pct > 0.0` to stop
  it drifting back there.
- `test_retention_ev_uses_ic_offer_cost_for_ic_segment` is renamed to what it can now prove:
  the offer cost scales with the customer's OWN revenue, not a flat per-segment sum. The 4 GWh
  customer's offer costs about GBP 9.9k, not GBP 200.
- the direct `_offer_cost_gbp` test covers the new signature's three properties, including that
  an unpriceable offer returns `None` and not a fail-open 0.0 — a free offer is the most
  attractive thing on the page.

**Mutation-proven, three ways.** Dropping the probability weight (the flat-cash shape) reds 3
tests; a fail-open `0.0` for the unpriceable case reds 1; re-introducing a flat `50.0` reds 3.
Producer restored clean after each.

**Confirmed:** `pytest tests/ -q --collect-only` → **31,052 tests collected, zero errors**.
Signal re-run → `green: true, rc: 0, episode_closed: true, consecutive_red: 0`.

Ruff ratchet: I001 1347 → 1346, total 2334 → 2333. The deleted from-import carried the file's
one unsorted name list, so the floor moves DOWN and the new count is held. Sorted by hand, not
by `--fix`.

