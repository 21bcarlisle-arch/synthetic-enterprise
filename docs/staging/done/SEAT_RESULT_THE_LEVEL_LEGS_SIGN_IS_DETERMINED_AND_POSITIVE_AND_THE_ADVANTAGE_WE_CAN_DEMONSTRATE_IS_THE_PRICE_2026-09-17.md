**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-level-selection-split-cannot-be-read-and-that-is-the-thesis-question`)

**Knowledge:** none new. No domain constant moves. This reads a leg that was already on disk and
repairs the summariser that was not reading it.

# The level leg's sign is determined and positive, and the advantage we can demonstrate is the price

Delivery seat, 2026-09-17. Scores
`docs/staging/records/SEAT_PREREG_CAN_THE_LEVEL_LEGS_SIGN_BE_READ_OFF_THE_FLOORS_ALREADY_ON_DISK_2026-09-17.md`,
written before any statistic was computed and unedited. Beside the 09-08 write-up, which stands.

---

## The answer

**The LEVEL leg's sign is DETERMINED and POSITIVE at 18 independent draws.** The bound:

| leg | what it is | n | mean | sem | positive on | sign stateable |
|---|---|---|---|---|---|---|
| **value** | the arm beat the control by | 18 | **£18,655.02** | £463.02 | 18/18 | **yes**, 40.3 sems |
| **level** | a FLAT rule at the same median margin beat the control by | 18 | **£19,279.15** | £305.85 | 18/18 | **yes**, 63.0 sems |
| **selection** | what the inference itself was worth | 18 | **−£624.13** | £347.16 | 9/18 | **no**, 1.80 sems |

`docs/observability/value_cycle_ab_s1_noise_floor_folded18_20260917.json`, world
`39a192ce04c1eda8`, `redraw_mode=all`, `redraw_key=elasticity` — the per-household
price-sensitivity variable the direction names, and nothing else, re-drawn per seed.

The level leg spans £16,811.75 to £20,843.24 and does not come within thirteen of its own standard
deviations of zero. Exact sign test, distribution-free and assuming nothing: **18 of 18 positive,
two-sided p = 7.6 × 10⁻⁶.** The verdict is robust to which bar is applied — the coarse 2.0 the
producer uses and the honest t(17) = 2.110 give the same answer on both legs, and the selection
leg is *further* from stateable under the stricter one.

**What that means, in the unflattering direction, which is the direction it points.** The flat rule
— same median margin for everybody, no per-customer inference of any kind — beats the control by
**more** than the arm does. Selection is worth −£624, indistinguishable from zero and, as far as
this instrument can see, slightly negative. On this book, over 18 draws of the variable the arm is
supposed to be exploiting, **the advantage we can demonstrate is the price level.** The
director's distinction — inference, never access — is not demonstrated here. It is not refuted
either; the selection leg's sign is still unstateable, and "we cannot tell" is what that half
earns. But the half that CAN be read reads against the thesis.

**This is a finding about what we can show, not a licence to tune the arm until selection wins.**
R12.

## The two things the direction required held fixed, and both are now stated

**1. `flat_at_level` takes its level from each run's own realised median margin.** On this book that
confound is **measured dead, not argued away**: `level_gbp_per_mwh` reads **20.0 on all 18 draws**,
and on all 27 rows across all three nine-seed floors. The level arm is not being redefined by its
own result here, because its own result does not move under the re-draw. That is a property of this
book and not a general safety — the 2026-09-03 three-seed family had it at 47.0/45.75/47.5, three
different levels on three seeds, and on that family the confound was live. It is pinned by
realisation and declared, and it must be re-read on any new book rather than assumed.

**2. `discrimination_auc` beside the advantage: UNAVAILABLE, on all 18 draws, and that goes on the
surface.** Not one floor artefact ever written records it. So these advantage figures have **no
discrimination reading beside them at all**, and none can be recovered without re-running the seeds.
This is the direction's own bar — *"a re-run that reports a new advantage figure without
`discrimination_auc` beside it is NOT done"* — and the honest report is that the requirement cannot
be met from disk. The repair below makes the next floor meet it; it cannot retro-fit these.

The 0.4653 the direction quotes is the 2026-08-27 run's figure and is superseded: current three-arm
runs in this world read 0.6148–0.6285. That does not rescue anything. `site/data/value_arms.json`
already carries the retraction of the argument built on it, and the reason is exactly the reason
this matters — *the same estimator has scored 0.646, 0.672, 0.465, 0.465 and 0.130 across five runs
in four days.* An unbounded statistic cannot attribute an advantage. **A floor family is the only
instrument in this repo that draws the advantage more than once, so it is the only thing that could
ever bound the AUC, and it was throwing the AUC away.**

## The defect: a leg nobody summarised reads exactly like a leg with nothing in it

`level_advantage_gbp` has been in **every seed row of every floor ever written**.
`fold_noise_floor_family.summarise` and `run_value_cycle_ab.noise_floor`'s summary block both read
`selection_gbp` alone. Every page-side mechanism in `tools/generate_value_arms_data.py` is pointed
at the selection leg.

So the surface has been publishing *"the level-versus-selection split cannot be read"* since
2026-09-09 while **one of its two legs had a determined sign sitting in the rows**, eight days
unread. The sentence was true of the selection half and false of the level half, and the half it
was false about is the one that reads against the company.

This did not need a run. It needed a `_spread` call.

## What the prereg predicted, scored

| # | predicted | measured | |
|---|---|---|---|
| P1 | `level_advantage_gbp > 0` on every nine-seed-era seed, no exceptions | 27/27 rows, 18/18 folded | ✅ |
| P2 | `level_gbp_per_mwh == 20.0` on every one — confound pinned in fact | 20.0 on all 27 | ✅ |
| P3 | the selection leg still crosses zero | 9/18 positive, 1.80 sems | ✅ |
| P4 | 95% interval strictly above zero, p < 0.01 | [£18,634, £19,924], p = 7.6e-6 | ✅ |
| P5 | the AUC is discarded by the row builder, so no floor on disk can bound it | absent from all 14 floor artefacts | ✅ |

**And the caveat the prereg registered fired, which is the part worth keeping.** It said: *"if the
floors share seed VALUES they are not independent draws at all but one draw under three trees, and
the pooled count collapses."* They do. `_20260909b` and `_20260910` run the **same nine seed
values** under different trees. **27 rows are 18 draws.** Had that gone unnoticed the family would
have been published at n=27 with a standard error shrunk by a factor measuring nothing — and
`fold_noise_floor_family` refuses it by name, which is why the tool was used instead of a hand
pool. The refusal is now pinned against that real pair on disk and not only a synthetic one.

## What landed

1. **`fold_noise_floor_family.summarise` reads both legs** — `level_leg`, `value_leg` and
   `selection_leg`, each with its spread, sem, a distribution-free positive-seed count, and the
   producer's own `distance_to_a_sign`. **Both legs judged at the same bar**, because the contrast
   between their verdicts is the whole claim and a split verdict produced by two different rules
   would read on the surface exactly like a finding. The four pre-existing fields keep their names
   and values, so every consumer keyed to them is untouched.

   This is the change that makes the 18 draws already on disk readable **today**, with no re-run.

2. **`run_value_cycle_ab.noise_floor` records the AUC per seed** — `discrimination_auc`,
   `auc_population` (the statistic is noise when one side is small) and
   `auc_scored_share_of_priced`, with `auc_unavailable_because` when the run could not score it.
   Fails closed per row: an unmeasured AUC is `None`, **never 0.5**, because 0.5 is a real reading
   meaning "the belief knows nothing" and the two license opposite conclusions about the thesis.

3. **The folded 18-draw family** at
   `docs/observability/value_cycle_ab_s1_noise_floor_folded18_20260917.json`, carrying
   `producing_commit: None` with its reason — two trees drew these rows and the fold refuses to
   name one of them.

4. **Seven controls, each named for its defect, all five mutations firing.** Level leg given its
   own looser bar → the same-bar control fires. AUC bounded from whichever rows answered → the
   fail-open control fires. `distinguishable_from_zero` hardcoded → the poison round fires. Level
   leg aliased back to selection → the poison round fires. An unmeasured AUC written as 0.5 → three
   fire. The verdict partition is asserted **reachable** before any test is allowed to mean
   anything by it, over the real summariser — the R15 trap this repo entered three times in one
   afternoon.

## What is still owed, in order

1. **The surface.** This result is in an artefact and a document; the page still says the split
   cannot be read, full stop. `tools/generate_value_arms_data.py` reads the selection leg only, and
   `CURRENT_WORLD_NOISE_FLOOR_PATH` points at the unfolded nine-seed floor. Making the page state
   *"the level leg's sign is determined and positive at n=18; the selection leg's is not at 1.80 of
   2.11 standard errors"* is the next piece, and it is a door-test change, not a constant move.
2. **A floor that carries its own AUC.** One leg, ~1h10m, 6.4 GB — launch through a transient user
   unit and record with `background/launch_liveness --record`. Until one runs, every published
   advantage in this family states its discrimination as unavailable, which is honest and is not an
   answer.
3. **Five more draws would settle the selection leg**, if its mean and sd stayed put — `n=23`
   against today's 18, from `distance_to_a_sign`. That is arithmetic at today's numbers and is not
   a forecast: new draws move both.

## Reversal

Every part is a file and the summariser change is additive. Revert the commit: `summarise` returns
its four original fields, the folded artefact and its two sources stay on disk, and no page moves
because none reads the new block yet.
