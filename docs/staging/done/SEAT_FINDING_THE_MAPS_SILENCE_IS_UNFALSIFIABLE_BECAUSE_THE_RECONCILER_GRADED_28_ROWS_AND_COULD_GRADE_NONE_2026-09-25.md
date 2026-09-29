**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The map's silence is UNFALSIFIABLE: the only instrument that can tell "no atom advanced" from "an atom advanced and nobody wrote it down" grades 28 of 110 live atoms, and today it could grade none of them

Answers `docs/staging/records/SEAT_PREREG_WHETHER_THE_MAPS_SILENCE_IS_NO_ADVANCE_OR_AN_ABANDONED_RECORD_2026-09-25.md`.
Seven predictions, **four confirmed, two refuted, one confirmed on the wrong half** — all recorded
below beside the predictions, not instead of them. The two refutations are where the answer is.

Drawn on the scheduled tick of 2026-09-25 as LANE 0 DELIVERY, claim
`is-the-map-silent-because-nothing-advanced-or-because-advances-stopped-being-recorded`. The item
asked which of two causes explains the map going 245 commits without a `level_current` move:
**cause A**, atoms are not advancing; **cause B**, they are advancing and the map is no longer where
that is recorded. It said the two have opposite remedies and that picking the flattering one costs a
turn. It is worse than that: **neither cause can currently be established**, and that is the
finding.

Predecessors, read first and not re-derived:
`SEAT_FINDING_THE_NEXT_STEP_GATE_IS_REACHABLE_ON_ONE_COMMIT_IN_200_AND_NO_ATOM_HAS_MOVED_IN_241_2026-09-25.md`
and `SEAT_FINDING_THE_NEXT_STEP_GATE_NOW_ASKS_THE_MAP_DIFF_AND_THE_MAP_HAS_NOT_MOVED_IN_245_COMMITS_2026-09-25.md`.
Both establish the silence. This is the third report of it and the first to ask its cause.

## The answer, in one paragraph

**Cause B, as the item framed it, is refuted.** No artefact in the tree records an atom level
advance in the window. **Cause A is consistent with every reading and is NOT established**, because
the only mechanism in the repository that can distinguish "this atom has not advanced" from "this
atom advanced and the row was never moved" is
`tools/level_zero_contradicted_by_its_own_controls.py`; its population is 28 of the 110 live atoms;
and run just now it reports **`{"contradicted": 0, "ungradable": 28}`** — 28 of 28, every row in its
population, ungradable. **It graded nothing.** `contradicted: 0` out of 0 graded is the reading a
reader takes as a clean bill of health, and it is the reading the seat has now taken twice without
asking the denominator. So the honest verdict is the third one: *the map's silence is unfalsifiable,
for 110 of 110 live atoms.*

## Why this is BLOCKING and not a reading

`tools/lane_formation.py` derives `buildable_lanes` from `level_current` + `loop_stage`, and the
draw ranks off it — the same argument
`level_zero_contradicted_by_its_own_controls.py`'s own docstring makes for why it earns its place.
An unfalsifiable level field is therefore an unfalsifiable input to **direction**: a row that is
wrong keeps winning draws already paid for, and a row that is right is indistinguishable from it.
Both of the remedies the item named are live decisions the director cannot currently make on
evidence, and the next lane to report "the map is quiet" will report it a fourth time.

## The premise, re-measured before the work rather than taken from the item

* `git rev-list --count --first-parent 86504d951..origin/main` = **248** (the item said 245; it grew
  under me, which is the expected direction). `origin/main` = `d013d27f7`, which is this worktree's
  HEAD, so the two agree for every reading here.
* **0 commits touch `docs/design/maturity_map.yaml` in the window** — and 0 touch
  `docs/design/maturity_map_closed.yaml`, on `--first-parent` AND on the full walk. The premise
  stands and widens: not one commit touched EITHER half of the map.
* The draw's DUPLICATE-WORK note calling this id "already held by another writer" is this draw's own
  write: `claimed_at` is `1790318113.0965347` in BOTH `docs/observability/.seat_work_in_hand.json`
  and `docs/observability/.delivery_lane_claims.json`, identical to the microsecond and 58 seconds
  old when read. One write, not two writers.

## The instrument the item prescribed, and why it cannot answer the question — P1, P2

The item prescribed intersecting the window's commit paths with each open atom's `file_scope`.

| | measured | predicted |
|---|---|---|
| **P1** commits touching ANY live atom's `file_scope` | **208 of 248** | ≥180 — **CONFIRMED** |
| **P2** commits touching a ≥2-segment (specific) live `file_scope` | **176 of 248** | 60–140 — **REFUTED, high** |

P2 was the prediction that the specificity split would rescue the instrument. It does not. The
intersection is dominated by scopes that every commit on this trunk touches by construction:
`OPS8`'s scope is `site/data` (regenerated on every publish), `A51`'s is `docs/staging/records` (so
every finding filed counts as work on A51), `G4`'s and `H40`'s are `tools` and `tests`. And **30 of
the 110 live atoms declare an EMPTY `file_scope`**, so the prescribed instrument is structurally
blind to 27% of the population it was meant to survey. A count that is 208, 176 or 0 is consistent
with both causes. **It is not a discriminator and it should not be reported as one.**

## Cause B is refuted — P3 CONFIRMED

Cause B asserts a record exists somewhere. That is falsifiable, and one counter-example would have
been enough. There is none:

| candidate store | last written | in the window? |
|---|---|---|
| `docs/design/maturity_map.yaml` | `86504d951`, 2026-09-22 | **no** |
| `docs/design/maturity_map_closed.yaml` | `f620fed2c`, 2026-09-17 | **no** |
| `docs/claude/phase-history.md` | `87857df30`, **2026-07-14** | no |
| `docs/status/LATEST.md` | `60c8c1d4b`, 2026-09-21 | no — and that is *earlier* than the map's own last commit, because the publisher is wedged (separate live claim `publish-gate-wedge-is-the-wedge-alarm-itself`) |
| `docs/design/simplifications/` | 1 commit in window | that commit is a merge; no level field moved |
| `docs/observability/.atom_stall_tracker.json` | live | **cannot be the store**: its `fingerprint` is `level\|target\|loop_stage\|…` READ FROM THE MAP, so it is a derivative and not an independent record |
| `docs/staging/` | **430 new documents in the window** | 4 mention a level move, and **3 of those 4 are the meta-findings about this very silence** |

**430 new staging documents and not one records an advance.** Nowhere else holds the record. The
map is still the only place a level lives.

## The anti-tautology control, which is where the framing broke — P6

A near-zero count is what a broken query also returns, so the same query was run over the **248
first-parent commits immediately BEFORE `86504d951`**: **9 map commits**, of which exactly **one**
moves a level VALUE (`0022641d8`, `W2_34` 1→2); one mints a new row at 0; one rewrites a trailing
comment on a level that stays at 2. The query sees map commits when they exist. But the comparison
window is not the healthy one the item's framing assumes — **it contains ONE advance, not many.**

So the rate became the question. Over the last **1500 first-parent commits (2026-09-02 → 2026-09-25)**,
comparing the parsed map blob before and after each of the **78** map commits, **per atom id**:

| bin (250 first-parent commits each) | dates | level ADVANCES | mints | rows removed (refiled to closed) |
|---|---|---|---|---|
| 5 (oldest) | 2026-09-02 .. 09-04 | 3 | 0 | 0 |
| 4 | 2026-09-04 .. 09-06 | 5 | 34 | 13 |
| 3 | 2026-09-06 .. 09-09 | 5 | 9 | 3 |
| 2 | 2026-09-09 .. 09-17 | 3 | 2 | 3 |
| 1 | 2026-09-17 .. 09-22 | 1 | 1 | 0 |
| 0 (current) | 2026-09-22 .. 09-25 | **0** | 0 | 0 |

**17 per-atom advances in 1500 commits — about 1 per 88.** P6 predicted 20–60 "level-multiset moves"
and the multiset measure returns **39**: confirmed on the number and **wrong on the quantity**, because
39 bundles mints and closures with advances. The per-atom walk is the honest instrument and it says
**17**. P6's decisive half — "no earlier bin is as low as the current one" — holds: 3, 5, 5, 3, 1, 0.
**The map did not go quiet. It decayed to quiet over three weeks**, and "245 commits without a move"
describes the last step of a ramp rather than a stop. That is the shape to report, and it is not the
shape either cause names.

## What the 17 advances were, and the reconciler P6 turned up — P7 REFUTED, decisively

At least **5 of the 17** say in their own subject that the work was *already done and the map did not
say so*: `7f24e4ac3` "W2_30's level 2 was **earned and unrecorded**"; `e6c6ea178` "the map said zero
about work **its own controls prove is done**, and four rows were…"; `a43ee63fe` "a level-zero row
was refused on a suite that was green four days before the atom…"; `5d804d671` "the bound was
already on the deployed page and nothing would have gone red…". The map was never a *timely* record.
It was a **periodically-reconciled** one.

The reconciler is `tools/level_zero_contradicted_by_its_own_controls.py` — 41 KB, written for exactly
this class, and its docstring states the defect in the same words: *"the work had landed… and the row
still read 0. Nothing anywhere could notice."* **It has no production caller.** Nothing in the hook
chain, no daemon, no gate invokes it; its own usage line says *"Run standalone"*; the last evidence of
anyone running it is 2026-09-17, one day before the last bin in which any atom advanced.

**P7 predicted it would report ≥1 CONTRADICTED row and ≥20 UNGRADABLE. Run just now:**

```
[level-zero] 28 row(s) at level 0 / build CANNOT BE GRADED. …it does not refuse.
--json  ->  {"contradicted": 0, "ungradable": 28}
```

**≥20 ungradable: confirmed (28). ≥1 contradicted: REFUTED — and the refutation is not the
flattering reading.** `contradicted: 0` is not "no row is contradicted". Its population is the 28
live atoms at `level_current: 0` + `loop_stage: build`, and **all 28 of the 28 are ungradable**. The
graded denominator is **zero**. Nothing was weighed. A reader — this seat, twice — takes
`contradicted: 0` as evidence the map is honest, and it is the fail-silent signature: *a screen whose
green is produced by its own inability to run.*

## What is outside the instrument entirely

| live atoms | count | graded by the reconciler? |
|---|---|---|
| `level_current: 0`, `loop_stage: build` | 28 | in population — **28/28 ungradable, 0 graded** |
| `level_current: 0`, `loop_stage: idle`/`harden` | 49 | **no** |
| `level_current: >=1` (10 at 1/build, 3 at 1/idle, 12 at 2/build, 8 at 2/harden) | 33 | **no** |

**82 of 110 live atoms are outside the instrument by construction**, including all 33 that sit at
level 1 or 2 — which is precisely where the *next* advance would come from, and where "earned and
unrecorded" costs the most because the row is not obviously stale. The one class of level defect this
repository built a detector for is the 0→anything class; the 1→2 and 2→3 classes have never had one.
`docs/observability/.atom_stall_tracker.json` agrees and cannot help: **99 of 103 tracked atoms are
`stalled: true`**, median `consecutive_unchanged` 346, and its fingerprint is read from the map, so it
restates the silence rather than testing it.

## The allocation reading the director is owed either way — P4, P5

P4 predicted the verdict would be cause A with the refinement that the in-scope work is harness and
landing mechanics rather than atom subjects. **The refinement is confirmed; the verdict is not
available.** Of the 248 first-parent commits in the window:

* **115 touch no authored path at all** — only `docs/staging/`, `docs/observability/`, `logs/`,
  `docs/status/` or the regenerated `site/data/`. 133 touch at least one authored path.
* By subject: **127 (51.2%) mechanics only**, 88 (35.5%) neither, 21 (8.5%) both, **12 (4.8%) domain
  only**. P5 predicted >60% mechanics among specific-scope commits and measured 47.2% —
  **REFUTED as written, and the miss is the classifier's**: hand-reading the 88 "neither" subjects
  finds them mechanics too ("the alarm document stops being its own state store", "the one-home
  control is keyed to the WIRING"). The number to key to is the one that does not depend on a keyword
  list: **domain-subject commits are 4.8%–12% of the window, and the rest is harness.** Recorded that
  way because a share of a keyword bucket rots and a share of a hand-read population does not.
* Hand-reading the 33 domain commits: ~21 are non-merge, of which roughly **9 are corrections or
  withdrawals of a claim this company had already published** (a thesis withdrawn as a coin flip, a
  refuted bill-stress term bounded, a probe found scoring every household at £1,700, a page's
  "ceiling" found to be the dice's own probability). Correction is value. **By this project's own
  convention it moves no level** — `docs/design/simplifications/ARCH1_internal_seams.yaml` says it in
  as many words: *"level_current STAYS 0 (measurement moves no level)"*.
* **Exactly one commit in 248 names a live atom**: `9ca0d887d` "W1_14 **step 1**: the demand-shape and
  forward-price legs read the world's own per-cell weather". Step 1. Mid-advance, level correctly
  unmoved. This reproduces the predecessor finding's 1-in-200 through an independent route.

So the trunk's own account of itself is: **a fortnight spent on landing mechanics, controls and
retractions, with ~5–12% on domain subjects and one atom explicitly mid-step.** That account is
consistent with cause A. It is not proof of it, because a tree where 82 of 110 live atoms have no
level instrument cannot produce proof of it.

## Verdict on the two `next_step_gate` triggers, which the item asked for

Neither is ornamental and neither is vindicated. **Both are unfalsifiable for the same reason the map
is.** The map-diff trigger can only fire on a commit that moves a level: at the measured historical
rate that is ~1 commit in 88, and in the window it is 0 in 248. Its green says nothing about whether
successors are being declared, because the question is never asked. That is not a reason to remove it
— it is correct, cheap and now proved reachable against a real index — but **a green
`next_step_gate` must not be reported without its denominator**, and `escape_rate`'s printed sentence
(now 8 declared / 6 escaped, all six reasons about landing mechanics) is the only place that
denominator currently appears at all.

## The gate fired on this commit, and what it got right and wrong

Recorded because it happened while landing this document, not reconstructed afterwards. The first
attempt at the commit was refused:

```
[next-step-gate] COMMIT REFUSED.
This commit advances A51_the_plain_english_report_on_the_use_case_register_reaches_the_director,
OPS8_last_known_good_staleness_banner and records no next step.
```

**It is the first commit in this stretch to reach the gate at all, and it does not advance either
atom.** It names them because their `file_scope` entries — `docs/staging/records` and `site/data` —
are the two that make the prescribed intersection meaningless, which is the finding. So the message
leg cannot distinguish *names an atom* from *advances an atom*, and its refusal sentence asserts the
second. That is a true positive for "a commit mentioning an open atom owes a successor" and a false
one for the sentence it prints. It cost one cycle and it is the cheaper half of the gate, so this is
a note on the wording, not a case for removing the leg: the leg is why the trailer below exists.

## Nothing is repaired here, and what the remedy is

The item was right that the causes have opposite remedies, and the measurement says **neither remedy
is the next move**. The next move is the third one, and it is not a new register — the mechanism
exists and is unrun:

1. **Make `contradicted: 0` unable to read as a clean bill of health.** 0 of 0 graded and 0 of 28
   graded are different facts and the surface prints the same number. Fail closed and say so on the
   surface: the count carries its denominator or it is not published. *This is the one change of the
   three that is a control defect rather than a backlog, and it is the smallest.*
2. **Discharge the 28 ungradable rows against the causes the tool already prints per row** — it names
   the cause and the repair for each (`file_scope` naming a directory not the files it writes; a named
   control that was never written; a pointer that rotted). Nothing here needs designing.
3. **The 1→2 and 2→3 classes have no instrument at all.** 33 live atoms. That is a gap to file, not a
   thing to build inside this claim.

## Falsifiers

* Re-run `python3 -m tools.level_zero_contradicted_by_its_own_controls --json`. If `ungradable` is
  below 28 with `contradicted` still 0, the graded denominator has become non-zero and cause A gains
  its first real evidence. If `contradicted` is ever ≥1, cause B's true half — *earned and recorded
  nowhere* — is live and this finding's verdict is confirmed from the other side.
* `git log --first-parent --format=%h -- docs/design/maturity_map.yaml | head -1` — if it is no longer
  `86504d951`, every count here is stale by the amount the map moved.
* The rate table is reproducible from `d013d27f7` by comparing the parsed map blob at each map commit's
  parent and itself, per atom id. If a re-run over the same 1500 commits does not return 17 advances
  in bins 3/5/5/3/1/0, the walk is wrong and the decay claim goes with it.

## Remedy 1 is landed, in the same turn, and the other two are not

Recorded here rather than in a second document, because a remedy filed away from the measurement it
answers is how this class survives. **Still BLOCKING: remedies 2 and 3 stand.**

`tools/level_zero_contradicted_by_its_own_controls.py` now carries the denominator on both
surfaces. Against the live map, before and after:

```
before:  {"contradicted": 0, "ungradable": 28}
after:   {"contradicted": 0, "ungradable": 28, "population": 28, "graded": 0}

[level-zero] ⚠ NOTHING WAS GRADED. All 28 row(s) in the partition are ungradable, so this pass
weighed no evidence: a count of 0 contradicted rows here is NOT a verdict about the map, it is
"cannot tell".
```

The population is counted through `is_candidate`, the same predicate `assess` filters on, so the
denominator cannot come to describe a population that has moved; and by membership rather than by
subtraction, so a caller handing `main` verdicts about rows outside the partition cannot drive it
negative. **The exit code deliberately does not move**: "cannot grade this row" is argued in the
module docstring as a finding about the row and not a verdict about the work, and fail-closed here is
a claim on the surface — "cannot tell" said out loud, in the place the misread happened — not a
refusal that would wedge the orientation that calls it.

Four controls, in `tests/tools/test_level_zero_contradicted_by_its_own_controls.py`, each
mutation-proven against the leg written for it and not another:

| control | mutation that must red it | result |
|---|---|---|
| `test_a_pass_that_GRADED_NOTHING_says_so_and_never_lets_zero_read_as_clean` | `if graded:` → `if True:` (the vacuous branch deleted) | RED |
| `test_BOTH_denominator_states_are_reachable_in_one_pass` | the same, AND `if graded:` → `if False:` (the line made unconditional the other way) | RED on both |
| `test_the_JSON_surface_carries_the_denominator_and_not_only_the_two_lists` | the two new keys dropped from the payload | RED |
| `test_the_denominator_counts_THE_PARTITION_and_not_the_whole_live_map` | `is_candidate` dropped from the population | RED |

The partition control is the one that matters: a denominator line printed unconditionally would pass
the vacuous arm on its own, so the graded arm asserts the vacuous sentence is **absent** rather than
asserting some other word is present — the shape that otherwise survives the unconditional mutation.
