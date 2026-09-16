**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-live-selection-headline-must-carry-the-interval-its-own-three-seeds-earn) · **Class:** `controls_that_cannot_fail`

# The selection leg's refusal never said the quantity has no sign, and at three seeds the gate that now says it is an equivalence

**2026-09-09, scheduled tick, LANE 0 DELIVERY.** The drawn direction said the page states the
thesis's central claim in the company's favour on one draw inside an interval five times its size.
The premise was half spent and the half that was left is the half that mattered.

---

## What the page already did, and what it did not

The drawn text said `current_world.selection_gbp = +£270.21` publishes with
`verdict_withheld_because: None`. That field is the **whole advantage's**, spread into
`current_world` by `_leg_in_this_world`; the selection leg has carried its own nested
`verdict_withheld_because` since 2026-09-04, and the headline has withheld its verdict since then.
So "the page states a positive selection number as resolved" was not true when this tick drew it.

What **was** true is the harm underneath it. Every word of the refusal was about STABILITY:

> THIS PAGE STATES NO VERDICT ON THAT FIGURE. It is a single draw, and the same contrast re-drawn 3
> times in this same world moves against a £2,279 spread — 1 of the 3 re-draws clears that spread
> and the rest do not…

A reader met `+£270`, was told the verdict depends on which draw was made, and was **never told the
quantity has no sign at all** — that the family runs −£3,075 to +£1,199 and its CENTRE is −£481. The
band table carries Lowest and Highest four hundred words further down; deriving "the centre of this
leg's own re-draws says the choosing is worth less than nothing" was left to the reader. This
project's rule is that "we cannot tell" belongs on the surface, not in a footnote.

## Why no control could catch it

`_verdict_stability` asks every seed's value through `_resolvable`, which is `abs(value) > stdev`.
It asks how FAR from zero a draw fell and never which SIDE. A family that straddles zero can be
unanimous about clearing its own spread and unanimous about nothing else — so `stable: True`
certifies a verdict whose direction the quantity does not have. The gate was blind to the sign
question **by construction**, and the page's own `_composition_in_this_world` had been refusing a
SHARE for exactly this property since 2026-09-08 without the LEG's verdict ever being asked it.

## The arithmetic, established BEFORE the gate was written

A family that straddles zero **cannot** be verdict-stable at three or four rows. With two draws at
+a and one at −b the sample standard deviation is (a+b)/√3, and `min(a, b) > 0.577(a+b)` has no
solution; the same holds at n=4. Confirmed analytically and by exhaustive search. It becomes
reachable at **n≥5** — `[−9.68, −9.79, −8.10, +8.40, −8.75]` is a family in which every draw clears
its own spread and the quantity still has no sign.

**So at today's seed count the new gate is an equivalence.** It can only fire where `stable` is
already False. That is written into `_verdict_stability`'s own comment rather than left for a later
session to find as a dead branch, and WITNESS C of the new control is the five-row floor that makes
it a gate rather than an assertion about nothing. A mutation removing the gate turns `resolved` from
`None` to `True` on that witness — a direction stated on a sign-changing quantity, which is the
defect.

## What landed

| change | where |
|---|---|
| `_sign_determined(values)` — one implementation of "do these re-draws fall on one side of zero", `None` when unaskable | `tools/generate_value_arms_data.py` |
| `verdict_stability.sign_determined`, per contrast | same |
| A second, independent withholding gate in `_leg_in_this_world`; both causes published when both fire, never one substituted for the other | same |
| `_no_sign_clause` — the refusal in words, with the CENTRE's side composed from the comparison and no figures recited (the band table is their one home) | same |
| `_leg_clause` composes one sentence per cause; the stability recital is no longer unconditional, because on a sign-only refusal "the rest do not" is a falsehood about its own numbers | same |
| The composition block's inline sign test now routes through the shared helper | same |
| `test_a_leg_whose_own_redraws_straddle_zero_states_no_direction_however_stable` — three witnesses: the live leg, a one-sided family (the clause must be ABSENT), and the five-row floor where the gate fires alone | `tests/tools/test_generate_value_arms_data.py` |
| `_assert_a_leg_with_no_sign_says_so_in_its_own_region` — both directions, keyed to `sign_determined`, per leg region; `no_sign` joined the mirror's field swap | `site/test_the_baseline_comparison_reaches_the_reader.py` |

The live page now reads, under the selection figure:

> AND THE QUANTITY DOES NOT CARRY A SIGN. The same contrast re-drawn 3 times in this same world
> falls on BOTH sides of zero… The CENTRE of that family is on the other side of zero from the
> published draw, so the draw's own sign is not the family's.

**Mutation round.** Clause dropped from the headline → 2 door rungs red. Clause printed
unconditionally → 3 red (both directions, so it is not a presence check). Withholding gate removed →
WITNESS C red with `resolved: True`. Suites: 135 generator, 110 door + 1 skipped, green.

## What this turn also carried, and why

`tools/generate_value_arms_data.py` and `site/test_the_baseline_comparison_reaches_the_reader.py`
were already modified in the working tree by the stranded 09-08b promotion lane (bucket reading
derived rather than pinned; the `_later_runs_in_this_world` per-run dedupe; the `_row` half-up
rounding). The drawn item directed landing those hunks. They are inseparable in practice — my edits
sit in the same functions — and the promoted artefacts they exist for
(`value_cycle_ab_s1_three_arm.json`, `value_cycle_ab_s1_noise_floor.json` and the dated
`..._noise_floor_20260908b.json`) were uncommitted too, so landing the prose without them would
publish a feed no committed tree can reproduce. All of it goes in one commit with its own result doc.

## And a red at HEAD that was blocking every lane, found by the gate refusing this landing

The first land was refused by three controls in `tests/tools/test_the_renewal_funnel.py`. They are
green in the shared working tree and **RED IN A CLEAN HEAD EXTRACT** — measured, not assumed, in
`git archive HEAD` with nothing of mine in it. The repair is a stranded uncommitted copy of that
test file, and HEAD plus that one file alone is 24/24 green, so it is self-contained.

The repair is the right one and its own docstrings say why: the controls were pinned to
`resolved_tariff_type is None` for a won ELECTRICITY leg — today's answer — and went red on
2026-09-07 when the census stopped restating a spelling `run_phase2b` had repaired on 2026-08-30.
**They went red because the reader got more honest**, which is this project's named backwards
direction for a control. The repaired versions key to the property (key-presence and the resolved
value COME APART, and both legs of the reachability boolean are exercised) and move the subject to a
gas leg, which is the only commodity the world's own read still resolves to `None`.

Carried into this commit with its own result doc, because a red at HEAD blocks every lane and the
cure was sitting on disk unlanded.

## What is NOT done

1. **The top-level payload adjacency stands.** `current_world.selection_gbp` sits beside a
   `verdict_withheld_because` that belongs to the whole advantage. The rendered page is not wrong —
   the headline reads the nested leg — but a machine consumer reading the two top-level fields
   together gets the flattering pair. Fixing it means the whole-advantage leg stops being spread
   into `current_world`, which touches every consumer of that block.
2. **The published feed names an untracked run.** `later_runs_in_this_world` scans the directory and
   found `value_cycle_ab_s1_three_arm_20260909.json`, written 02:25Z by another lane and not
   tracked. The row is truthful about the disk; a clean HEAD extract regenerates a feed without it.
   Pre-existing to the census's design, not to this change.
3. **n is still 3.** The gate above the equivalence threshold is untested by any real floor. A floor
   re-run with five or more seeds is what would make it load-bearing, and nobody has run one.
