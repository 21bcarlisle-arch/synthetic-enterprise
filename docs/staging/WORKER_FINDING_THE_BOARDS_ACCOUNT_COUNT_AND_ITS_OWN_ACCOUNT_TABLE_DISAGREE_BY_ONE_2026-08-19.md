# [WORKER-FINDING] The published account count is 9 and the account table beside it holds 8 (2026-08-19)

**Severity:** LATENT · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-19 worker tick, LANE 1 BUILD draw on `EP1_clv_three_horizon` (pass 10), while
measuring the new estimator's first reading against the published book.
**Subject:** `docs/reports/run_output_latest.json` — `enterprise_value_account_count` against
`by_billing_account`, in the same file.
**Measured at:** HEAD `c9430c326`, the committed artefact as it sits on disk. Everything below is
`observed-with-evidence` unless labelled `inferred` (R9).

## The disagreement

`enterprise_value_account_count` reads **9**. The per-account table in the same artefact holds 13
accounts, of which:

```
still_supplied == True                8   ['C2','C7','C8','C9','C_IC1','C_IC2','C_IC3','C_IC4']
clv_gbp is not None                   8   ['C2','C7','C8','C9','C_IC1','C_IC2','C_IC3','C_IC4']
supplied but unvalued                 0   []
valued but not supplied               0   []
```

The two sets are **identical**, so this is not a filtering choice reconciling 8 to 9. `9` is not
the count of supplied accounts, not the count of valued accounts, and not the count of accounts
in the table. Whatever it counts is not present in the artefact it is published in.

`enterprise_value_account_count` is written from `build_enterprise_value`'s
`portfolio.account_count`, which is `len(by_customer)` — the roster the headline
`enterprise_value_gbp` (£1,283,769.58) is summed over. So `inferred`: either the headline is a sum
over 9 accounts while the table shows 8, or the count and the table were written from different
runs. Both are one artefact publishing two populations for one book, which is the shape R14 and
pass 6's design constraint each exist to refuse — a number without its population, and here the
number and the population are printed side by side and disagree.

## Why LATENT rather than BLOCKING

The gap is one account out of eight or nine and moves no verdict that this tick could find; it is
a reconciliation defect in a published artefact rather than a red gate, and `blocking_by_lane`
shows B_commercial clear. Filing BLOCKING would hold the lane for a discrepancy whose direction is
not yet known, which is the false-blocker error
`WORKER_FINDING_THE_POPULATION_DRAW_IS_LIVE_ON_DISK_WHILE_ITS_ROSTER_FIX_IS_UNCOMMITTED_2026-08-13`
named. It is not RECORDED either: the figure is on the live site's household panel lineage, and a
published count that no population in its own file reproduces is not a note.

## Discharge condition

Establish which of the two is right — regenerate the artefact from the current tree and re-read
both (the "regenerate the published artefact to find the fix that never reached it" move), since a
stale-write explanation and a live-disagreement explanation predict different results and this
tick did not distinguish them. Then either the count or the table is repaired, and a control
asserts they agree **on the artefact**, not on the objects that produced it — an independence the
two currently do not have, because a control reading `len(by_customer)` on both sides would be the
tautology R15 names.

**Not fixed this tick:** `saas/enterprise_value.py` and the report generators are outside
`EP1_clv_three_horizon`'s `file_scope`, and SELF_INTERRUPT_DISCIPLINE queues a worker's own
finding by default.
