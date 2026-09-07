**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Two controls were red at HEAD, and one was pinned to a run output that drifts by design

**Found:** 2026-09-07, delivery seat, while landing the commons supersession control. Both reds
refused that landing and neither was caused by it. Both are fixed in the same commit.
**Class:** `controls_that_cannot_fail`.

## How they were found

`surgical_land` gates the tree the commit would create, and a red gate is never retried. Two suites
failed that had nothing to do with the change. Both were proved pre-existing before anything was
touched: the first in a clean `git worktree` extract at HEAD, the second by reading the ledger blob
out of `HEAD` itself and counting it.

## Red 1 — a population floor pinned to one run's exact output

`tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` asserted
`bills >= 11_000`, dated at "11,549 bills over 251 accounts on 2026-09-02".

`docs/state/billing_ledger.json` is **tracked, and rewritten by `process_run_complete` on every
run.** The bill count across consecutive auto-commits:

| commit | bills | accounts |
|---|---|---|
| `a4d068de6` | 11,019 | 251 |
| `96adc38cd` | 11,019 | 251 |
| `f53998359` | **10,909** | 251 |
| `4a56ebfe8` (HEAD) | **10,909** | 251 |

**Nothing was lost.** Accounts are stable at 251 throughout; the bill count moves with the run
window. The floor was set at the top of that range, so an ordinary shorter run walked the tree into
a standing red — and because the ledger is a data surface, the red fired for **every lane whose
commit selected a file any billing module reads**. It was reached here through
`uk_vat_rates.json`, which has nothing to do with billing populations.

**Fixed by keying the floor to the stable quantity**: accounts `>= 240` carries the anti-emptiness
guarantee the control was written for, and the bill floor stays at `>= 8_000` as a coarse "the
invoices did not vanish" check, set below the observed range instead of at its top. The substantive
assertion — every bill equals the sum of its own printed components — is untouched.

This is the repo's own recurring shape, stated in CLAUDE.md: *key a control to the property, not to
today's answer.* A floor that goes red because a legitimate run was shorter is red for a reason
nobody can act on, and the only available action is to weaken it — which is how controls die.

## Red 2 — three constants discovered and never classified

`tests/architecture/test_switching_rate_commons.py` refused three names in
`company/crm/enriched_churn_estimate.py`: `payment_method_engagement_reading`,
`derived_payment_method_engagement_factor` and `_CIM_ENGAGEMENT_PRIOR_LOG_VARIANCE`. They landed
with `fdfa0c94f` and the register was never filled in, so the control did exactly its job and then
sat red at HEAD.

**Fixed by classifying them, not by filtering them.** All three are per-channel quantities, not
book levels: the first two are a dimensionless multiplier around 1.0 for how much one payment
channel shops relative to the market, and the third is a variance in log space. Holding any of them
to the published switching band would compare a ratio, or a second moment, with a per-cent level —
the before-you-divide defect that file exists over. Reasons are recorded in `_NOT_A_LEVEL_READING`
beside the existing `admissible_svt_churn` entry, which is the same shape.

## What this says beyond the two instances

**A red at HEAD is invisible until someone tries to commit, and then it is charged to whoever tries.**
Neither of these was in any lane's queue. Red 1 in particular was reached through an artefact with
no relationship to it, so the lane that pays is picked by the data-surface graph rather than by who
broke it. The seat is the only place that can hold this — a bounded tick that hits it has no way to
tell "pre-existing" from "mine", and the cheapest wrong move is to assume it is yours and weaken
something.

**A control over a REGENERATED artefact needs its floor keyed to what does not regenerate.** Red 1
would recur at the next short run under any floor within the drift range. Accounts is stable because
the population is; bills are not, because the window is not.

## What is next

1. Sweep the other controls that assert against `docs/state/billing_ledger.json` or any other
   `process_run_complete` output for floors pinned inside the run-to-run drift range. This one was
   found by tripping over it; there is no reason to think it is the only one.
2. A landing that adds a discovered-but-unclassified name should not be able to leave the register
   unfilled — Red 2 is the register working and the commit gate not asking.
