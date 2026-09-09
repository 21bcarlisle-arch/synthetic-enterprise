# RESULT — the 09-08b pair is promoted, and the page's prose was pinned to the run it replaced

**Severity:** RECORDED · **Lane:** G_data_learning ·
**Claim (Lane 0 delivery):** `promote-the-09-08b-value-arms-pair-once-its-floor-lands`

## What was drawn, and what the premise turned out to be

Drawn: wait for the noise floor (PID 2900491), check its stamp, promote the pair onto
`THREE_ARM_PATH` and `NOISE_FLOOR_PATH` in ONE commit, republish, then decide the
`CURRENT_WORLD_*` pair.

**The floor had already finished.** PID 2900491 was gone; the artefact was on disk at
`docs/observability/value_cycle_ab_s1_noise_floor_20260908b.json`, untracked, `generated_at`
**2026-09-08T23:29:22Z**. The direction's estimate was ~01:24Z; it landed ~2h earlier. Nothing was
waited on.

**The stamp check passed and it was the gate on the whole thing.** Floor 23:29:22Z against arms
21:01:30Z, so the bound is newer than the figure it bounds; world digest `39a192ce04c1eda8` on both;
`redraw_scope.mode: all`, the only leg whose spread bounds the published contrast. Had it stamped
earlier the promotion would have been abandoned, not shipped with a caveat.

## The promotion, and the six predictions scored on the REAL feed

`docs/staging/SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_09_08b_RUN_MAKES_THE_PROOF_PAGE_SAY_2026-09-08.md`
scored all six by calling `build()` on the candidates. They are re-scored here **on
`site/data/value_arms.json` as actually published**, which is the only scoring that was not
available when they were filed.

| | Predicted | On the published feed | |
|---|---|---|---|
| P1 | headline falls to £323.52; share 0.7867 → 0.9814 | `realised.split.selection_gbp` **323.52**, share **0.98146** | **CONFIRMED** |
| P2 | staleness caveat stays `None` only if the floor is newer | `error_bar.staleness_caveat: None`, floor 23:29:22Z > arms 21:01:30Z | **CONFIRMED** |
| P3 | ratio > 5, `distinguishable_from_zero` false | ratio **7.084**, false | **CONFIRMED** |
| P4 | `fixed_horizon.available` and `survivorship.available` both true | survivorship **true**; fixed_horizon **withheld** | **REFUTED, and by the code** |
| P5 | the DIFFERENT WORLDS whole-page caveat clears | `world_caveat: None` | **CONFIRMED** |
| P6 | `later_runs_in_this_world` fires and names `_20260908b.json` | fires, names it — **once**, see below | **CONFIRMED** |

**P4 is refuted and the refutation is not the artefact's.** The run carries
`method_skill.fixed_horizon.available: true, decisions_priced: 214`, exactly as the pre-registration
established by reading. Between that reading (22:15Z) and this publication, `62334dc76` — *"the
honest concordance now carries the bound its own sample earns, on every cut"* — landed, and the
feed now withholds the fixed-horizon cut because *"the run that produced this artefact ranked its
priced decisions and never permuted them, so the estimand would go out as a point estimate with no
bound of its own"*. The prediction was right about the artefact and wrong about the page, because
the page got stricter in between. Recorded rather than re-scored: a prediction filed before the
answer and refuted by a later commit is worth more than one quietly amended.

## The judgement the direction reserved: `CURRENT_WORLD_*` stays put

Both options were honest. **Both were measured, and the door refused one.**

Pointing both constants at the 09-08b pair makes the current-world block a tautology the page
announces in words (`_against_the_superseded_panel`'s `the_same_run` branch: *"the two figures are
one figure printed twice, not a comparison"*). That was the initial decision. It was **reverted**
after promoting, rebuilding and running the door: both blocks then publish the same selection figure
of £324, and `_the_legs_own_regions` in `site/test_the_baseline_comparison_reaches_the_reader.py`
refuses it — *"the selection leg's own figure renders 2 times in this headline, so neither this rung
nor a reader can tell where the advantage's statement ends and the leg's begins — and the two carry
different verdicts"*. A page a reader cannot attribute a verdict on is worse than an older contrast
that names its own successor. **Held at the 00:19:54Z / 04:10:26Z pair**, where
`later_runs_in_this_world` fires and names the newer run, so the page states its own staleness.

The rejected option is written into the constant's comment, not deleted.

## Four defects the promotion exposed, all of the same class

None was in the promotion. All four are **prose or fixtures pinned to the run the promotion
replaced**, and none could be seen until the path they hang off moved.

1. **The bucket table's reading asserted four things about the 2026-08-31 run, in prose.** That the
   least-confident band mostly stayed, that the most confident *"kept none of them"*, that flipping
   the labels reads monotone the right way, and that *"every band is single-digit"*. The promoted
   run realises 63/53/74/77 on 8/40/23/52 decisions: all four false, on the live page.
   `_bucket_reading` now derives the direction, both ends' rates, the flip claim and the smallest
   band from the rows. **The stale sentence understated the arm** — it told a reader the belief was
   backwards on a run where it mostly is not — which is why "delete the flattering half" is not the
   remedy: prose keyed to one run is wrong in whichever direction the next run falls.
2. **Twelve controls in `tests/tools/test_generate_value_arms_data.py` took their witness from the
   canonical paths.** Ten needed a floor newer than the run they bound and got a dated fixture
   against a promoted run, so the STALENESS guard refused them while each reported the failure of
   the world, leg or stability guard it names — a mutation battery whose witnesses die on a third
   guard says SURVIVED for everything. `_stamped_after` now derives the fixture's stamp from the run
   rather than the artefact. Two used `THREE_ARM` / `NOISE_FLOOR` as the *"names no world"* witness
   and held that property by accident; they now cite `THREE_ARM_NO_WORLD` and `NOISE_FLOOR_NO_WORLD`
   (world stamping began 2026-09-03, so a pre-09-03 dated copy can never gain one). One pinned the
   literal `"20 decisions"`, which is what the 08-31 run's buckets tallied.
3. **`_against_the_superseded_panel` told a reader the panel it names is BELOW.** It renders in
   `#arms-composition`; `#arms-realised` is anchor 7 against 9, i.e. **above**. Four sentences, one
   home, false in it. Found by registering the referent in the pointer rung, not by reading the
   prose — and the two symbols it needed were red at HEAD before this turn.
4. **The door rounds half-UP and the rung predicting its cells rounded half-to-EVEN.** No band had
   ever landed on a half until 0.625; then the rung expected `62%` of a page rendering `63%` and
   named the table as missing when it was there and correct.

## The census counted one run twice, and the promotion convention guarantees it

Promotion here is a file copy — the dated original stays on disk so superseded-with-provenance
survives — so the newest run is **always** on disk under two names, and
`_later_runs_in_this_world` globbed both. `_the_later_runs_disagree` counts those rows into a
sentence: *"N later runs over the SAME world exist and are not published above"*. It would have said
2 and printed one run's figures twice. Now one row per `(generated_at, producing_commit)`, keeping
the **dated** name — `THREE_ARM_PATH` is a moving pointer and a reader who follows it next week
reads a different run — with the losing name kept in `also_on_disk_as`. Unstamped files are never
folded: a missing `producing_commit` is not evidence two files are one run.

This is live, not latent, precisely because `CURRENT_WORLD_*` was held.

## What is next

- **Another lane landed `value_cycle_ab_s1_three_arm_20260909.json` (01:24:34Z) mid-turn.** It is in
  the live world, it is later than everything here, and the census names it. It has **no matching
  noise floor**, so promoting it would republish an unbounded headline — the documented defect. Its
  floor is the next thing this page needs, and it is a run, not an edit.
- The 29-implementations-of-one-git-rule census (`shared_tree` in `background/` and `tools/`) named
  in the same direction is untouched and still owed.
