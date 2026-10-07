# The company cannot learn a retention offer's effect on staying from its own record

**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted`

Claim `retention-guard-weighs-the-offers-learned-incremental-effect`, 2026-10-07. The item asked
for a census before any guard uses a learned effect: how many offered and un-offered renewals near
the 0.30 threshold does the book hold, and what bound does that sample earn? If the bound is too
wide to decide on, record that and stop. **It is too wide, so this records it and stops.** No code
changed. `counterfactual_retention._RETENTION_EFFECTIVENESS = 0.20` was not adopted.

**What the item said to read first does not exist.**
`SEAT_RESULT_THE_RETENTION_GUARD_NETS_BAD_DEBT_AND_ON_THE_CHOSEN_BOOK_IT_WITHDRAWS_NOTHING_2026-10-07.md`
is in no tree, worktree or commit. At 09:50 the two arms that would produce it
(`tools._c29_retention_engagement_arm off|nets`, in `/var/tmp/se-retguard-arms`) were queued behind
pid 415593 and had not run. The bad-debt netting itself was being landed by
`surgical_land`. So the item's "73 calls offered, 11 to POOR/CRITICAL" is from a run whose output
I could not find. The census below is from today's standing run output instead.

## 1. The census

Source: `docs/reports/run_output_f07af3845_20261007T063005Z.json`, `customer_events`. These are 154
renewal decisions across 78 accounts, 2016-12 to 2025, with 70 offers. Only company observables
were read: `company_churn_estimate` (the belief the guard reads), `retention_offered` (its own act)
and `event_type` (who left it). A household that declined the fix and stayed counts as staying.

| belief band | offered | n | left | left share |
|---|---|---|---|---|
| 0.00–0.10 | no | 35 | 5 | 0.14 |
| 0.10–0.20 | no | 27 | 7 | 0.26 |
| 0.20–0.25 | no | 7 | 2 | 0.29 |
| 0.25–0.30 | no | 15 | 2 | 0.13 |
| 0.30–0.35 | yes | 16 | 3 | 0.19 |
| 0.35–0.40 | yes | 14 | 4 | 0.29 |
| 0.40–0.50 | yes | 10 | 1 | 0.10 |
| 0.50+ | yes | 30 | 1 | 0.03 |

**On every one of the 154 renewals, `offered` equals `belief > 0.30`.** The value test never
refused: value is 4.9–15.7x the cost. So **no belief band holds both an offered and an un-offered
renewal.** "Offered vs not-offered at a similar churn belief" has no members in this record. Its
policy is deterministic, so the only comparison it allows is across the threshold. That
comparison mixes the offer with whatever the belief itself predicts.

## 2. The bound

The effect is the reduction in the share that leaves: un-offered minus offered. The 95% interval
is Newcombe's difference of two Wilson intervals, which treats the two sides as exchangeable. That
is generous, because nothing adjusts for the slope in belief.

| window | offered left | un-offered left | effect | 95% |
|---|---|---|---|---|
| 0.25–0.35 | 3/16 | 2/15 | −0.054 | [−0.315, +0.220] |
| 0.20–0.40 | 7/30 | 4/22 | −0.052 | [−0.258, +0.182] |
| 0.10–0.50 | 8/40 | 11/49 | +0.024 | [−0.151, +0.189] |

**What deciding needs.** An offer pays when effect × value > cost, so the break-even effect is
cost/value: **0.064 to 0.204** across the book. Every interval above runs from "the offer makes
leaving likelier" to "above every break-even". At p ≈ 0.15, a ±0.05 half-width needs about **392
renewals per side, inside the band**. Ten years gave the 0.25–0.35 window 31 renewals across both
sides. So this book would need roughly 25 times its record, and even then the design gives a
discontinuity, not an experiment.

## 3. Why it cannot be learned yet

1. **Identification.** The guard offers to everyone above 0.30, so the record has no un-offered
   renewal above it. A learned effect needs some offers withheld at random above the threshold.
   That would be a holdout, which is a company decision this record does not contain.
2. **Size.** About 7 renewals a year fall in the 0.30–0.40 band. A holdout at that rate would
   take decades to reach a decidable bound. So for this book a holdout is not a route either. It
   could become one only for a book an order of magnitude larger.

## 4. What the published record does establish, and what it does not

Ofgem's EFTC trial (2019, n = 19,553, one supplier, a letter at fixed-term end): **external
switching was 6% in both arms.** The contact moved households to re-fix internally (14% → 23%)
and did not move how many left (`docs/market_research/how_households_respond_to_supplier_contact.md`
§2.1). That was a reminder, not a discount. The effect of a retention DISCOUNT's size on leaving is
not published (§4 item 2 there: EFTC ran at one saving level). The knowledge map's *Retention
offers* row already carries that gap.

What follows for the guard:

- **There is no learned effect to give it, and no published one.** An honest guard carries the
  effect as a declared `None` with this record as its reason. It does not carry 0.20.
- **EFTC is evidence against the guard's implicit assumption, not a value for it.** The guard
  acts as if an offer saves the account for certain. The one published trial of a supplier
  contact at this decision point found no effect on external loss. Writing that in as a zero
  effect would withdraw every offer. That too would be a number standing in for a discount
  study nobody has run.

## 5. Re-running the census

When the book or the policy changes (a holdout, a guard that can refuse), recount it from the
latest `run_output_*.json`. Bin `customer_events` by `company_churn_estimate`, split by
`retention_offered`, and count `event_type == "churned"`. The question to ask first is whether any
band now holds both kinds of renewal. If none does, the bound cannot move.
