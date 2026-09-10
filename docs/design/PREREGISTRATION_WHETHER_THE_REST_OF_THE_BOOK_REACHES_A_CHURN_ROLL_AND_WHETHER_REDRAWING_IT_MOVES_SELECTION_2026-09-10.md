# PRE-REGISTRATION — does the rest of the book reach a churn roll, and does re-drawing it move `selection_gbp`?

**Written 2026-09-10, before any of the three measurements below was run.** Lane 0 delivery, claim
`a-floor-keyed-to-the-rest-of-the-books-churn-cascade-not-to-an-elasticity-draw-it-never-reaches`.

Discharges item **3** of
`docs/staging/SEAT_FINDING_THE_FLOOR_DECOMPOSITIONS_REST_OF_BOOK_HALF_IS_EMPTY_ON_THIS_BOOK_SO_ITS_SHARE_IS_AN_IDENTITY_2026-09-10.md`,
handed on unchanged by
`docs/staging/SEAT_RESULT_THE_DEGENERATE_HALF_IS_WITHDRAWN_AT_THE_PRODUCER_AND_THE_PAGES_LOWER_BOUND_TURNED_OUT_TO_BE_ATTAINED_2026-09-10.md`.

---

## Why a prediction is being filed at all

Two of the three questions below have answers I do not have. The third I claim to be able to derive
from the source, and I am writing that derivation down **before** running the probe precisely because
the last one of these was a derivation that the production path then confirmed — and it would have
been just as valuable had it refuted me. A prediction filed after the answer is not a prediction.

## The state this starts from, which is not predicted — it is on disk

`docs/observability/value_cycle_ab_s1_floor_partition_probe_20260910.json` (world
`39a192ce04c1eda8`, commit `c066c114b`): **298 elasticity calls, 67 accounts, 100-account roster,
`accounts_that_drew_outside_the_roster: 0`.** The `except` leg keyed to the elasticity draw re-draws
nobody and refuses. That is measured, confirmed by the production path, and not at issue here.

## Q1 — does the complement reach a churn roll?

`simulation.customer_events.roll_lifecycle_event` takes `roll = _random.Random(f"{billing_account}_
{term_start_str}").random()` at the top of the decision, *before* and *outside* the `if differential:`
block that guards the elasticity draw. `differential` falls back to the run-level
`price_differential_pct` when the account has no offered rate, which is every account the value arm
did not price.

**PREDICTION 1.** A full pass at the base seed in world `39a192ce04c1eda8` makes **strictly more
churn rolls than elasticity draws**, and **more than 100 distinct accounts** roll — i.e.
`accounts_that_rolled_outside_the_roster > 0`, which is the exact quantity that was `0` for
elasticity.

**Confidence: high, and it is a derivation from the source, not a guess.** What would refute it: the
run never calling `roll_lifecycle_event` for unpriced accounts at all (a funnel that filters to the
priced roster upstream of the decision). If that is what comes back, the rest of the book has no
churn cascade *in this instrument* either, item 3 is answerable "no such quantity exists here", and
that is a larger finding than the one this work was drawn to fix.

**PREDICTION 1b, the one I am least sure of.** I predict the outside-roster rolls come from
**more than 300** distinct billing accounts. I have no basis for the number beyond the finding's
"~2,000 households" and the observation that only 67 reach a renewal that draws elasticity; the
ratio between "accounts in the book" and "accounts reaching a renewal point in the window" is a
quantity I have not looked at. **If this is badly wrong in either direction it is informative and I
will say so beside the answer rather than revising the prediction.**

## Q2 — does re-drawing the complement's churn roll move `selection_gbp`?

**PREDICTION 2.** The `except` leg keyed to the churn roll returns a **non-zero** `selection_gbp`
spread across seeds — i.e. not the identical `2176.657272` on every seed that the elasticity-keyed
leg returned over its five accounts.

**Confidence: moderate.** The mechanism is real (a different set of unpriced households churns → a
different settled book → a different realised median level → a different `level_gbp_per_mwh`, which
is one of the two legs `selection_gbp` is the residual of). But "real mechanism" and "moves the
figure by more than float noise" are different claims and I have not measured the second.

**I do not predict the sign, and I do not predict the magnitude against the ±£1,810.50 already
published.** Stating either would be inventing a number to fill a slot. What I will record is
whether the rest-of-book spread is larger or smaller than the priced-only one, as an observation.

**PREDICTION 2b — what would make me wrong in an uninteresting way.** If the churn roll is re-drawn
for the complement and `selection_gbp` comes back *identical across seeds*, the first thing to
suspect is **not** "the cascade does not matter" but the same fail-silent shape as before: the
re-draw reaching no call site that feeds the arm. The guards carry over from the elasticity leg
(`calls["n"] == 0`, `calls["redrawn"] == 0`, `calls["held"] == 0` all RAISE), so this cannot be
reported as a floor of zero — but a leg that redraws 400 accounts and still returns an identical
figure would be a *third* thing, and I am writing down now that I would treat that as a finding about
the funnel and not as a result about the world.

## Q3 — the design claim, which is the load-bearing one and is not a measurement

A churn-roll-keyed `except` leg and an elasticity-keyed `only` leg **are not a partition of one call
stream.** They are two different quantities re-drawn over two different halves.

**PREDICTION 3, filed as a claim I intend to act on before any number exists:**
`decompose_floor`'s reconciliation (`v_only + v_except ≈ v_all`) has **no reason to hold** across
legs with different keys, and `priced_share_of_variance = v_only/(v_only + v_except)` is **not a
share of anything** when its two terms count different things. Publishing either would be this
project's own recurring shape — two correct figures whose ratio is not a quantity.

So the mechanism must:

* **publish** `irreducible_sd_gbp` — it is `sqrt(v_except)` and needs only the `except` leg, which
  is the one figure the page actually asked for and the one that answers "does the wider book's
  churn cascade land in this net at all";
* **withhold** `priced_share_of_variance`, `reconciliation` and everything derived from the sum,
  with a reason naming the two keys, exactly as the degenerate half is withheld today;
* **refuse to infer** either leg's key from its filename or from an absent field.

**This prediction is falsifiable and I would rather be refuted than right:** if someone establishes
that the elasticity assignment and the churn roll are in fact nested — that the elasticity draw's
effect on `selection_gbp` is *entirely* mediated by the roll it perturbs — then the two legs do
partition and the share is real. I do not believe that (elasticity also moves `felt` and the bill
scale, not only the roll), and I have not tried to establish it. **If it turns out to be true, the
withholding above is over-cautious and should be undone.**

## What "done" means for this claim

Not "the nine-seed leg has run" — nine full three-arm passes at ~39 min each is ~6 hours and cannot
be a turn. Done is:

1. The complement's quantity is **named and reachable**: a probe on disk answering Q1 in world
   `39a192ce04c1eda8`, with its counts, the same shape as the elasticity partition probe.
2. A floor leg **can be keyed to it**: `noise_floor` takes the key, the reachability guards fire on
   the new key too, and a mutation that points it at a dead symbol goes red.
3. `decompose_floor` **knows the difference** and withholds what the mixed-key split cannot support,
   naming both keys.
4. The nine-seed production leg is **launched or its cost is stated**, and whichever it is, is said
   plainly rather than implied.

Item 4 explicitly may not land this turn. Items 1–3 are the increment.

---

# GRADED, 2026-09-10 — kept beside the predictions, not revised into agreement

Measured by `tools/run_value_cycle_ab.py --partition-probe` at commit `a9ae86351`, world
`39a192ce04c1eda8`, full window, against the 100-account roster in
`value_cycle_ab_s1_three_arm.json`. Artefact:
`docs/observability/value_cycle_ab_floor_partition_probe_both_keys.json`.

| Prediction | Called | Measured | Verdict |
|---|---|---|---|
| P1 — more churn rolls than elasticity draws | yes | 315 vs 298 | **holds** |
| P1 — more than 100 distinct accounts roll | >100 | **70** | **FAILS** |
| P1 — `accounts_that_drew_outside_the_roster > 0` for the roll | >0 | **2** | holds, barely |
| P1b — more than 300 outside-roster accounts | >300 | **2** | **FAILS BADLY** |
| P2 — a churn-roll `except` leg returns a non-zero spread | yes | not run — see below | **unresolved** |
| P3 — the two keys do not partition, so the share must be withheld | acted on | acted on | stands, untested |

## P1b was wrong by more than two orders of magnitude, and the reason is the finding

I predicted >300 outside-roster accounts on the strength of the prior finding's "~2,000 households"
and got **2**. I said at the time I had no basis for the number. I did not have the one fact that
governs it: **the book settled in this window is 164 billing accounts, and only 70 of them reach a
renewal point at all.** The arm's priced roster is 100. A roster of 100 inside a rolling population
of 70 has almost no complement — by arithmetic, not by choice of key.

**So the diagnosis behind this whole item was half wrong.** The elasticity complement is empty
because the draw sits behind a price gate — that part is true and measured. But the complement was
never going to be *large* under any key, because the rest of the book **does not renew in this
window**. Re-keying moved `except_leg_would_refuse` from `true` to `false`; it did not move the
sample size from useless to useful.

The sentence I wrote in the code — "the quantity the rest of the book HAS" — is right about the
mechanism and wrong about the magnitude, and it now says so beside itself.

## What this does to P2, which is why it was not run

A nine-seed churn-roll `except` leg is about six hours of compute and would measure `V_rest` over
**two households** (`PROS-2020-0287`, `PROS-2020-0303`). The finding this work descends from already
ruled that a `V_rest` over one household is worth no more than the five-account one on disk. Two is
that same category. **Spending the six hours would buy a number that cannot support the claim it
would be published under**, so I did not start it, and that is a decision rather than a deferral.

P2 therefore stays unresolved, and it is unresolved for a better reason than when it was written.
