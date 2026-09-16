**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** measurements_that_mirror

# RESULT — all six predictions hold, including the derivation I refused, and publishing the run alone would cost the page every directional bound

Grades `docs/staging/records/SEAT_PREREGISTRATION_WHICH_OF_THE_FOUR_BRIDGE_LEGS_ADMIT_THE_DEPARTURES_2026-09-09.md`
(P1–P6, filed before `_leg_conditioning` was written) and
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_LEG_CONDITIONING_RUN_COSTS_THE_REST_OF_THE_PAGE_2026-09-09.md`
(Q1–Q5, filed at 12:45Z while the run was executing).

**The premise check on the drawn item is spent and the item is not.** `856d7bb6b` is an ancestor of
`origin/main`, as the draw said. What it landed was the *instrument*; what was missing was a run
carrying it, and `method_skill.fixed_horizon.leg_conditioning` on the live feed read
`available: false` when this turn started.

The run: `python3 -m tools.run_value_cycle_ab --level-arm`, unit
`longjob-three-arm-legcond-20260909b`, 12:38:48Z → 13:15:17Z, artefact
`docs/observability/value_cycle_ab_s1_three_arm_20260909b.json`, world digest `39a192ce04c1eda8`.

---

## P1–P6: six for six

```
priced decisions the world recorded as a departure: 40
priced decisions that could not be keyed:            0
```

| leg | decisions | admits departures | cannot see | survivor cut? |
|---|---:|---:|---:|---|
| 0 `the_published_population_ratio_outcome` | 168 | **0** | 40 | yes |
| 1 `settled_only_ratio_outcome` | 124 | **0** | 40 | yes |
| 2 `settled_only_pounds_outcome` | 124 | **0** | 40 | yes |
| 3 `every_priced_decision_pounds_outcome` — the estimand | 161 | **37** | 3 | **no** |

| | Predicted | Measured | |
|---|---|---|---|
| **P1** | leg 0 admits 0 | 0 of 40 | **CONFIRMED** |
| **P2** | leg 1 admits 0 | 0 of 40 | **CONFIRMED** |
| **P3** | leg 2 admits 0 **and** the same population as leg 1 | 0 of 40; 124 = 124 | **CONFIRMED** |
| **P4** | leg 3 admits a non-zero count | 37 | **CONFIRMED** |
| **P5** | leg 3 admits **37**, priced departures **40**, so **3** excluded | exactly (37, 40, 3) | **CONFIRMED** |
| **P6** | every excluded departure excluded for `horizon_open_at_the_end_of_the_settled_book` | `{"horizon_open_at_the_end_of_the_settled_book": 3}`, nothing else | **CONFIRMED** |

**So the item's premise is refuted for the leg it matters most for.** The Lane 0 item that
commissioned the instrument said all four numbers are statements about survivors. Three are. The
worse-than-chance estimand — 0.4210 at p = 0.0045 — is computed over a population containing 37
measured departures and is not a survivor cut. The adverse figure is about the book.

### P5, which is the one worth having

P5 recorded the arithmetic I **refused to publish**: 40 dropped by the concordance minus 37 scored
at zero by the estimand, therefore 3 excluded. Two funnels, two gate orders, and a difference that
is not a quantity — this project's most expensive recurring shape. Measured properly, on the
`(account, term_start)` key in one pass from every priced decision's own recorded fate, the answer
is **exactly 3**.

**Both halves of that are true and neither cancels the other, so both are written down.** The
refusal was epistemically right: nothing established that the two counts were commensurable, and a
sentence built from them would have been a guess that happened to land. The number it would have
produced was right. What the measurement bought is not the 3 — it is *knowing* the 3, and knowing
where it went: `why_the_estimand_cannot_see_them` is a single censoring reason, which is a bound a
longer run lifts. Had it come back as a coverage or join reason it would have been a defect in the
estimand, and no amount of correct arithmetic on the two published counts could have told the two
apart. **The refusal is what made the answer knowledge instead of a coincidence**, and P5 is the
only reason that can be said rather than asserted.

### The declared limit, restated because it held

The estimand is **less** conditioned than the concordance, not unconditioned. The residue is 3 of
40 and the page carries it beside the admission. A surface reading "the estimand admits the
departures" with no residue would over-claim in the direction that flatters the estimand.

---

## The column renders. And it is not published, and that is the finding.

Driven through `site/_live_harness.mjs` against the real door with the promoted feed, the bridge
table renders the counts and not the named absence:

```
0.5338  0.4494–0.5504 · p 0.191  168   0 of 40   every decision whose term settled, on the ratio
0.4993  0.4410–0.5582 · p 0.989  124   0 of 40   ... less the terms whose 365 days had not closed
0.5130  0.4403–0.5588 · p 0.666  124   0 of 40   those decisions, in pounds
0.4210  0.4458–0.5540 · p 0.004  161  37 of 40   every decision the arm priced, in pounds
```

**And promoting it to the canonical path would take every directional claim off the page.** Q1–Q5:

| | Predicted | Measured | |
|---|---|---|---|
| **Q1** | every published figure reproduces bit-identically | 0 diffs across four legs, four intervals, `n`, `survivorship` 40/40/0/0, `level_vs_selection`, world digest | **CONFIRMED** |
| **Q2** | `staleness_caveat` flips `None` → fires | fires: floor 06:57:00Z against point 13:15:17Z | **CONFIRMED** |
| **Q3** | that sentence's causal clause is **false** | it asserted the 2026-08-28 market change unconditionally, for an interval of seven hours in one world | **CONFIRMED — repaired below** |
| **Q4 — will not move** | `one_world_across_every_figure` stays true | true, one digest, `runs_measured_in_a_superseded_world` empty | **CONFIRMED** |
| **Q5 — least sure** | 0 bounds lost | **10 lost, 3 gained** | **REFUTED** |

```
BOUNDS LOST:  contrast_bounds.available True -> False
              value_advantage_gbp  {stdev,min,max}_gbp   -> absent
              level_advantage_gbp  {stdev,min,max}_gbp   -> absent
              selection_gbp        {stdev,min,max}_gbp   -> absent
BOUNDS GAINED: leg_conditioning.available False -> True
               pair_strata.strata.cross.null_95_{low,high}
```

`contrast_bounds` is what **every directional claim on the page is gated on**. The trade is one
column, one stratum figure and a provenance line, against the headline's ability to name a winner.
**That trade is refused.** The run stays on disk; the promotion waits for the nine-seed floor now in
flight (`longjob-noise-floor-20260909b`, started 09:05Z, 27 passes, so mid-afternoon), and then it is a pair move that costs
nothing. Q5 was the prediction most likely to be wrong and it was wrong in the direction that
changed the decision, which is the whole reason it was written down at 12:45Z rather than
reconstructed now.

**The 09-09 result document's "what is next" said the counts light up on the next three-arm run.
They do. What it did not say is that the page cannot have them until the floor lands beside them,
and nothing in either document had asked.**

---

## Two defects found on the way, both filed, both repaired

1. **`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`**
   — Q3's false clause is one of three faces of it. The floor artefact carries no book identity, so
   the floor/run pairing can only be argued from timestamps, and a timestamp is wrong both ways:
   it refused this pair (provably the same world, `git diff` over `simulation/ company/ saas/ sim/`
   empty between the two producing commits) and it **admitted**, measured, a floor from world
   `ffffffffffffffff` against the live run because it was stamped one second later. The second half
   is the fail-open and nothing had named it. The caveat's clause is now composed from the two
   artefacts; `_seed_spreads` refuses a floor whose world is not the figure's; the door control
   that was asserting `"DEFEND" in rendered` is moved onto the property.
2. **`SEAT_FINDING_THE_CROSS_STRATUMS_BOUNDED_BRANCH_STATED_A_BARE_NUMBER_AND_NO_ARTEFACT_ON_DISK_COULD_REACH_IT_2026-09-09.md`**
   — the first run to carry `pair_strata` executed a branch no artefact in the tree could reach, and
   it printed the cross concordance without the interval its own pairs earn. The door control
   refused it in one line, correctly, having never had a feed that could make it fire.

Seven controls added or repaired across the two, all mutation-proved; **one mutation SURVIVED and
is recorded as an equivalence rather than a kill**, with the leg that separates it added.

---

## What is next

1. **The pair promotion, when `longjob-noise-floor-20260909b` finishes.** Copy
   `value_cycle_ab_s1_three_arm_20260909c.json` and the new floor to the canonical paths together,
   re-run `generate_value_arms_data`, and the column, the cross stratum's bounded figure and the
   directional claims are all live at once. `..._20260909b.json` is the run graded above;
   `..._20260909c.json` is the same run re-taken with defect 2 repaired, and is the one to promote.
2. **`noise_floor` should stamp a book identity onto its artefact.** Both directions of defect 1
   close for one reason instead of being patched one at a time. Not done here: it needs a floor
   re-run, and the one in flight would have to be redone to carry it.
3. **A branch a landed producer cannot reach from any artefact on disk is a class, not an
   instance.** Defect 2 is the second half of `pair_strata`'s own prose, green in every suite,
   unreachable by every feed. There is no census of that shape and this is the first time it has
   been named here. Filed as a thread to pull, not as work claimed.

---

## Addendum, 14:00Z — the corrected run exists and the door is green on it

Written after the fact and marked as such. When the section above was drafted,
`value_cycle_ab_s1_three_arm_20260909c.json` was still executing and everything said about it was a
statement of intent.

It finished at 13:58:12Z, world digest `39a192ce04c1eda8`. **P1–P6 grade identically** — 0/0/0/37
of 40, residue 3, single censoring reason — and **0 published-figure diffs** against the run graded
above, so nothing in the grading rests on which of the two artefacts a reader opens. It carries the
repaired sentence:

> *"The departure is carried by the 4,588 cross pairs, which read 0.2686 against the 0.4105–0.5887
> a no-information signal reaches on this stratum's own 4,588 pairs: in 73% of
> departure-against-survivor pairs the arm had given the DEPARTURE the higher margin."*

Driven through the real door on a feed built from it, **the whole capabilities suite passes: 123
passed, 0 skipped.** Two of those are worth naming because they were not exercisable before:

- `test_the_attribution_of_the_inversion_reaches_the_reader_BESIDE_the_figure` — the control that
  refused the `..._20260909b` feed in one line — now passes on the branch it had never seen.
- `test_an_error_bar_older_than_its_figure_says_so_on_the_page` **runs instead of skipping**. On
  the live feed the caveat is `None` and it skips, so the assertions repaired today had no subject.
  On this feed the caveat fires, and they hold: the rendered sentence names both run stamps and
  says what is known about whether the two runs share a world. **The repair is exercised, not
  asserted** — which is the one thing a control repaired against a feed that cannot reach it could
  not otherwise claim.

`..._20260909c.json` is the artefact to promote when the floor lands. `..._20260909b.json` stays as
the run P1–P6 were graded against.
