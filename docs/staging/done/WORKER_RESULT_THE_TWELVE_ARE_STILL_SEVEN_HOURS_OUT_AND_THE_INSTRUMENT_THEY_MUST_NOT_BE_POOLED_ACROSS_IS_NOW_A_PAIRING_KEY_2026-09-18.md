**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value_arms_floor_family

# RESULT — the twelve are still seven hours out, and the instrument they must not be pooled across is now a pairing key

**Filed:** 2026-09-18 03:54 UTC, with `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
still non-existent and PID 3819244 alive at 09:42:39 elapsed. **Claim id:**
`read-next12-alone-as-the-last-family-on-the-old-instrument-and-label-it-so`

---

## 1. The drawn precondition is unmet, re-measured rather than taken on the item's word

The item says *"When PID 3819244 writes … read the twelve seeds ALONE."* It has not written.

| what | reading |
|---|---|
| artefact | absent — `ls` on the exact path and on `value_cycle_ab_s1_noise_floor*.json` both empty |
| process | alive, `cwd` `/var/tmp/se-floorrun-20260917b`, stdout `/var/tmp/longjob-floor-next12-20260917.log` |
| progress | **40** `Starting treasury:` markers at 03:54 UTC |
| ruler | **6 markers per seed** — the completed `floor_auc_20260917.log` did 18 for 3 seeds |
| seeds done | 40 / 6 = **6.7 of 12** |

**ETA ~10:52 UTC**, and the working is here so the next session does not re-derive it: the run
`exec`'d at 19:11:48 UTC (it burned its first 3615s waiting for `longjob-floor-auc-20260917` to
free ~6.6 GB — line 15 of its own log), so 522 min have bought 40 markers at 13.05 min each, and
the 32 remaining are 418 min. That is **within 40 minutes of the 11:31 UTC** the corrected ETA in
`PREREG_THE_NEXT12_FAMILY_IS_STAMPED_A_SALVAGE_COMMIT_AND_SHARES_AN_INSTRUMENT_WITH_THE_AUC_THREE_2026-09-17.md`
named, which is the first time two independent readings of this run's clock have agreed. The
twice-per-leg marker was counted correctly on both.

**So nothing in this turn reports a seed, a mean, a sem or a sign.** Seven hours is not a wait a
bounded invocation can hold, and no part of the reading can be brought forward: the twelve do not
exist yet in any partial form the log exposes.

## 2. What was done instead, and why it is the same item rather than a substitute

The item has three clauses and only the first needs the artefact:

> read the twelve seeds ALONE … **Stamp the artefact and any page that reads it with the
> instrument it was drawn on: two arms over unequal priced populations.** … Done means the twelve
> are reported alone, **labelled**, and **no post-fix family has been pooled with them.**

Clauses two and three were prose. Nothing in the tree could label a family with its instrument,
and nothing could refuse a pool across a change of one. Both are now mechanisms, and both were
buildable without a single seed.

**The hole, stated exactly.** `FOLD_MUST_AGREE` had four keys — `world_identity.digest`,
`redraw_scope.mode`, `clock`, `symbol_patched`. Every one guards the WORLD or the CUT. None of
them moves when what `selection_gbp` *means* moves. The reproduction check cannot cover the gap
either: it fires only on seeds two members SHARE, and families drawn days apart on fresh seeds
share none — which is the case for every fold this lane is about to want. So a family drawn before
`flat_at_level` is made to meet the value arm's population and one drawn after would have folded
silently, and the fold would have named no reason at all, because there was no reason to name.

That is not hypothetical. It is how the published eighteen came to be spliced across an objective
change (`WORKER_RESULT_THE_EIGHTEEN_SEED_FAMILY_IS_SPLICED_ACROSS_AN_OBJECTIVE_CHANGE_AND_THE_TWENTY_FOUR_SEED_PRICE_CAME_OFF_THE_SPLICE_2026-09-17.md`).

## 3. The mechanism

**`arm_population_pair(result)`** — `tools/run_value_cycle_ab.py`. Per seed row, under
`arm_populations`. It compares `decision_shape` against `level_arm_decision_shape` — two blocks the
run has ALREADY assembled, so this costs no re-run and no extra pass.

It compares the **pair** `(priced, declined)` and not a reconstructed priced count, for two
reasons and the second is the load-bearing one:

1. `arm_decision_shape` returns `priced` as `len(log)` — every renewal the arm SAW — and its two
   early-return branches do not hold `priced - declined` as an identity, so subtracting would
   publish a negative population on the branch where an arm declined everything.
2. **The declines ARE the subject.** The value arm sees 129 renewals and refuses 64; the level arm
   prices what it is handed. A check that compared only `priced` would call that pair EQUAL — the
   exact reading
   `WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS_OVER_DIFFERENT_PRICED_POPULATIONS_AND_SIXTY_FOUR_DECLINES_ARE_NOT_ROSTER_DIVERGENCE_2026-09-18.md`
   refutes. Mutation M2 in §5 is that comparison, and it fires.

**`arm_population_instrument(rows)`** — the family's own answer, four-valued:
`one-population` / `two-populations` / `mixed-across-seeds` / `None`. The fourth value is why this
is a function and not an `all()`: a family whose seeds DISAGREE is on neither instrument, and if it
reported the same `None` an un-instrumented artefact reports, the fold would read the two as
agreeing. That is R15's *"a `None` that declares its reason and a `None` that is silence collapse
into the flattering branch"*, and the control asserts all four `repr`s are distinct.

**It is keyed to the property, not to today's answer.** It does not know which side of the
`FLAT_AT_LEVEL` repair it is on and must not. When the arms are made to meet one population it
reads `one-population` without being edited; if anything later parts them again it reads
`two-populations` without being edited. A constant naming the repair would go stale the first time
something else moved the arms apart.

**`FOLD_MUST_AGREE` gains `arm_population_instrument.instrument`**, and `fold_floors` re-derives
the block from the POOLED rows rather than carrying `first`'s — a folded family that gets re-folded
later needs a block describing itself, and `seeds_measured` carried from one member would be a
count about the wrong family.

**The page carries it as a sixth pairing key.** `generate_value_arms_data._selection_leg` already
published five — clock, staleness, world, admission, tree. The five all take for granted that every
seed measured the same thing and then qualify the pairing; this one asks whether they did.
`_arm_population_instrument_caveat` writes a distinct sentence at each of the four readings, and
the unstamped sentence says UNMEASURED — *"not established either way"* — rather than resolving in
the flattering direction. It is derived from the artefact, so it empties itself on the first
stamped family; nothing has to remember to delete it.

## 4. What this does to the twelve, which is the whole point

The run in flight was `exec`'d by a tree that predates all of this, so **the twelve will answer
`None`** — and `None` against any stamped member is a REFUSAL. That is fail-closed and it is
deliberate: it is now structurally impossible to pool those twelve with any family drawn after the
arms are repaired, which is exactly what the item asks for and what could previously only be asked
for in prose.

**It does not break the pre-registered fifteen.** `value_cycle_ab_s1_noise_floor_auc3_20260917.json`
is also unstamped, so it also answers `None`, and two unstamped members still fold. The secondary
reading fixed in advance by the next12 prereg survives this change untouched — which was checked
before the key was added, not discovered afterwards.

## 5. The mutations, and all three fire

Applied in-process, never in the shared tree — a mutation written into this tree reddens another
lane's in-flight gate.

| # | mutation | honest | mutated | control that goes red |
|---|---|---|---|---|
| M1 | drop `arm_population_instrument.instrument` from `FOLD_MUST_AGREE` | fold REFUSED | **folded = True** | `test_a_fold_refuses_to_pool_two_families_drawn_on_DIFFERENT_instruments` |
| M2 | compare `priced` only, ignore `declined` | `same_population = False` | **True** | `test_the_arm_population_pair_reaches_every_answer_it_can_give` |
| M3 | collapse `mixed-across-seeds` to `None` | 4 distinct `repr`s | 3 | `test_the_family_instrument_separates_a_MIXED_family_from_an_unmeasured_one` |

**Reachability is asserted before refusal, in the same control.** A guard that refused every fold
passes every refusal assertion written here, so `test_a_fold_refuses_to_pool_two_families_drawn_on_DIFFERENT_instruments`
asserts a same-instrument pair DOES fold, and `test_an_UNSTAMPED_family_folds_only_with_other_unstamped_families`
asserts two legacy members still fold. 298 tests green across the three affected suites.

## 6. Still owed, and it is one clause of three

Clause one. When the artefact lands at ~10:52 UTC: read the twelve alone — mean, sem,
sems-from-zero — report them whatever they say, and do not queue further seeds on this instrument.
The two prereg predictions to check against the delivered file are `producing_commit.commit ==
a178b56d6…` and 12 seed rows at world digest `39a192ce04c1eda8`.

**One thing the next session should not re-derive:** the artefact will NOT carry
`arm_population_instrument`, because the running process imported its code before this landed.
That is the expected reading and not a defect — see §4. Its absence is what protects it.

## 7. Not mine, observed in passing

`background/finding_classes --check` is RED on six TWO ROOMS collisions, all preregs, root copies
written at 03:51 UTC — **nine minutes into this turn**, all six within one second of each other,
byte-identical to their `records/` copies, with at least one showing staged-delete index residue.
That is another lane's live bulk archival mid-flight, and the mtimes are the proof. Left alone
deliberately: deleting a room out from under a running archival is how a lane loses work. Recorded
here so the next reader does not diagnose it a second time.
