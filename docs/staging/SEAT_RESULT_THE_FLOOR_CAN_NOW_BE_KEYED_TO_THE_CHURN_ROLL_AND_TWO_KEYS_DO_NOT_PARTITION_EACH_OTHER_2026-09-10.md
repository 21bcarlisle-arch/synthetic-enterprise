**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery · **Class:** measurements_that_mirror

# RESULT — the floor can now be keyed to the churn roll, and two keys do not partition each other

Discharges item **3** of
`SEAT_FINDING_THE_FLOOR_DECOMPOSITIONS_REST_OF_BOOK_HALF_IS_EMPTY_ON_THIS_BOOK_SO_ITS_SHARE_IS_AN_IDENTITY_2026-09-10.md`,
handed on unchanged by
`SEAT_RESULT_THE_DEGENERATE_HALF_IS_WITHDRAWN_AT_THE_PRODUCER_AND_THE_PAGES_LOWER_BOUND_TURNED_OUT_TO_BE_ATTAINED_2026-09-10.md`.

Pre-registered before any of it was measured:
`docs/design/PREREGISTRATION_WHETHER_THE_REST_OF_THE_BOOK_REACHES_A_CHURN_ROLL_AND_WHETHER_REDRAWING_IT_MOVES_SELECTION_2026-09-10.md`.

**What did NOT happen this turn is at the bottom, and it is the larger half.**

---

## The quantity the rest of the book has

`simulation.customer_events.roll_lifecycle_event` takes its renewal dice —
`_random.Random(f"{billing_account}_{term_start_str}").random()` — at the top of the decision,
**above and outside** the `if differential:` block that guards the elasticity draw. `differential`
falls back to the run-level parameter when an account has no offered rate, which is every account
the value arm did not price. So an unpriced household rolls and never draws.

That line is now `churn_roll_for_renewal(billing_account, term_start_str)`, extracted and
**otherwise untouched**: same seed string, same `Random`, same `.random()`. It has a name so a floor
leg can replace it, exactly as it replaces the elasticity symbol.

**The signature deliberately takes no `base_seed`, and that is load-bearing.** Threading the run
seed into that string would move every roll in the 2016–2025 record — a baseline change (R13), not a
harness convenience. A floor re-draws it by substituting the function; the substitute composes its
own namespaced stream (`floor{seed}_{account}_{term}`), which is the same uniform distribution
re-drawn rather than a different one.

`test_extracting_the_churn_roll_did_not_move_one_byte_of_the_world` recomputes the pre-extraction
expression rather than pinning today's floats, so it stays true of any build seeded the same way.
Reordering the seed string turns it red.

## What landed

* **`noise_floor(..., redraw_key=)`** — `elasticity` (default, every leg on disk) or `churn_roll`.
  Every reachability guard carries over to the new key: a patch that fires zero times, a leg that
  re-draws nobody, and a leg that holds nobody fixed all RAISE. A dead churn-roll symbol raises at
  lookup rather than arriving as a suspiciously stable spread.
* **`partition_probe`** — ONE pass with **pass-through** recorders on both symbols, counting which
  households take which draw and how the priced roster cuts them, plus the cross-tabulation
  (`accounts_that_roll_but_never_draw`) that sizes the reachable complement. `--partition-probe`
  on the CLI. The artefact on disk from 2026-09-10 had **no committed producer**; now it has one,
  and it answers for both keys in the pass that previously answered for one.
* **`decompose_floor`** reads each leg's `redraw_key` and publishes `legs_share_one_call_stream`.

## The design finding, which is the load-bearing half and was predicted before any number existed

**An elasticity-keyed `only` leg and a churn-roll-keyed `except` leg are not a partition of one call
stream.** They are two different perturbations over two different halves. Their variances have no
reason to sum; they may overlap, cancel or compound, and nothing here measures which.

So `v_only + v_except` is not a variance, `priced_share_of_variance` is a ratio of two figures whose
ratio is not a quantity, and `reconciliation_ratio` compares that non-sum against a third leg keyed
to a fourth thing. `KEYS_DERIVED_FROM_A_ONE_CALL_STREAM_PARTITION` names the twelve keys that run
through the sum — including `reconciliation_reading`, because it asserts *in words* that the legs
partition one call stream, and a withheld number beside a paragraph asserting the withheld thing is
worse than either alone — and a mixed-key split sets every one to `None` with a reason naming both
keys.

**What survives is the point of the exercise.** `rest_of_book_sd_gbp` and `irreducible_sd_gbp` are
`sqrt(v_except)` and need only the `except` leg; `larger_settled_book_would_resolve_it` is that
spread against the contrast. Those three ARE the question "does the wider book's churn cascade land
in this net at all", and a mixed-key split answers it. Withdrawing the same list the degenerate half
withdraws would have suppressed the one number the re-keying exists to produce — so this is a
**second** list, not an extension of the first.

The control asserts both sides on one pair of fixtures differing in nothing but the `except` leg's
key: what goes must be present on the single-key split, or the withholding proves nothing.

## Mutation-proven, not asserted

| Mutation | Went red |
|---|---|
| churn-roll re-draw returns the REAL roll (the fail-silent zero) | reach control + held-half control |
| mixed-key withdrawal disabled | mixed-split control |
| churn-roll seed string reordered | world-did-not-move control + held-half control |
| probe recorder no longer pass-through | probe control |

78 pass in `tests/tools/test_value_cycle_ab_noise_floor.py`; 192 in `test_run_value_cycle_ab.py`,
185 in `test_generate_value_arms_data.py`, 28 in `test_customer_events.py`, 152 across
`tests/design/` + the static ratchet. Epistemic verifier PASS over 556 files.

## What was NOT measured, and why — this is a mechanism, not a result about the world

**Prediction 1 is still a derivation.** No probe was run on the real book this turn.
`floor_run_headroom_refusal()` refuses: two other floor legs are already running in this guest
(pids 1072649, 1146711, holding 13,303 MB and still growing) and a probe is one full three-arm pass
that peaks where the legs peak. **The probe path takes the same refusal** rather than being exempted
for "only probing" — exempting it is how three passes end up sharing a guest sized for two, and an
OOM-killed probe writes no artefact and reads exactly like one still running.

So, unchanged from the pre-registration and stated rather than implied:

* **Q1 — does the complement reach a churn roll?** Derived from the source and asserted over a
  fixture shaped like the book. **Not observed on the real book.** Prediction 1b (>300 outside-roster
  accounts) has no evidence at all yet.
* **Q2 — does re-drawing it move `selection_gbp`?** The fixture says yes; the fixture is not the
  world. **Nothing here licenses any statement about the size of the cascade's contribution**, and
  the value-arms page's withheld figures stay withheld.
* **Q3 — the mixed-key design claim.** Acted on before any number existed, as filed. Still
  falsifiable: if the elasticity assignment's effect on `selection_gbp` turns out to be *entirely*
  mediated by the roll it perturbs, the two legs do partition and the withholding is over-cautious.
  I do not believe that and have not tried to establish it.

**The cheapest next step is now cheap.** `--partition-probe` costs one pass and answers Q1 for both
keys; the nine-seed `except` leg costs about six hours and should not be launched until the probe
says the complement is peopled. That ordering is the whole reason the probe exists: the same
question previously cost 39 minutes and a refusal.

## Handed on

Run the probe when the guest is free, then the nine-seed churn-roll `except` leg at world
`39a192ce04c1eda8`, then `--decompose`. Record whether prediction 1b was wrong in either direction —
it is a number I had no basis for and said so.
