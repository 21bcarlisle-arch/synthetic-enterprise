**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — is the map silent because nothing advanced, or because advances stopped being recorded there?

Written BEFORE any of the five measurements below was run. Drawn on the scheduled tick of
2026-09-25 as LANE 0 DELIVERY, claim
`is-the-map-silent-because-nothing-advanced-or-because-advances-stopped-being-recorded`.

Predecessors, both read first and neither re-derived here:
`docs/staging/SEAT_FINDING_THE_NEXT_STEP_GATE_IS_REACHABLE_ON_ONE_COMMIT_IN_200_AND_NO_ATOM_HAS_MOVED_IN_241_2026-09-25.md`
(the census) and
`docs/staging/SEAT_FINDING_THE_NEXT_STEP_GATE_NOW_ASKS_THE_MAP_DIFF_AND_THE_MAP_HAS_NOT_MOVED_IN_245_COMMITS_2026-09-25.md`
(the wiring that acts on it). Both establish the silence; neither asks its cause.

## Premise, re-measured at draw time rather than taken from the item

`git rev-list --count --first-parent 86504d951..origin/main` = **248** (the item said 245; it grew
under me, which is the expected direction). `git log --first-parent 86504d951..origin/main --
docs/design/maturity_map.yaml` is **empty**. The premise stands. `origin/main` is `d013d27f7`,
which is also this worktree's HEAD, so HEAD and the trunk agree for this reading.

The draw's DUPLICATE-WORK note names this same id as "already held by another writer". It is not:
`claimed_at` is `1790318113.0965347` in BOTH `docs/observability/.seat_work_in_hand.json` and
`docs/observability/.delivery_lane_claims.json`, identical to the microsecond and 58 seconds old at
the time I read it. That is one write — this draw's own. Carrying on with the work, not the
disposition.

## What the two causes are, said before they are measured

* **Cause A — nothing advanced.** The 110 live atoms are genuinely not moving: the commits are
  being spent on something that is not any atom's declared subject. Then both `next_step_gate`
  triggers are correct and idle, and the finding is a reading for the director about allocation.
* **Cause B — advances are not recorded in the map.** Atoms are moving and the record moved
  somewhere else. Then the map-diff trigger watches an abandoned record, `level_promotion_gate`
  guards a file nothing writes, and this is a control defect, not a reading.

## The instrument, and why the item's prescribed one is not enough on its own

The item prescribes: intersect the paths of the window's commits with each open atom's `file_scope`
and count those that landed inside an open scope while the level stayed put. **That count cannot
distinguish A from B by itself**, because a `file_scope` of `docs/design` or `company` matches
nearly every commit on this trunk. A high number would be consistent with both causes and with
neither. So it is run as declared, AND split by scope specificity, AND a direct test of cause B is
run beside it: cause B asserts a *record exists somewhere*, which is a falsifiable claim about
stores, not about commits.

## The five predictions, each falsifiable, recorded before measuring

**P1 — the prescribed intersection is near-tautological.** ≥180 of the 248 first-parent commits
touch at least one live atom's declared `file_scope`. *Refuted if fewer than 120 do.*

**P2 — restricted to live atoms whose `file_scope` names a path two or more segments deep (a
specific scope), the count falls a long way: 60–140 commits.* Wide band because I have not read the
scopes; the claim being tested is the CONTRAST with P1, not the level. *Refuted if it lands outside
60–140, and the direction of the miss is the interesting part.*

**P3 — cause B has no store, and this is the decisive leg.** No artefact in the tree records an
atom level advance dated after 2026-09-22. Specifically: `docs/design/maturity_map_closed.yaml` has
**0** commits in the window; no promotion ledger, stall tracker, phase-history entry or status page
records an atom reaching a new level in the window. *Refuted by ONE such record — and one is
enough, because cause B only needs the record to have moved house.*

**P4 — the verdict will be CAUSE A**, with a refinement neither cause states: the work landing
inside open atoms' scopes is harness, landing-mechanics and findings work that happens to fall in a
declared scope, not work on the atom's own subject. *Refuted if P3 is refuted, or if commits in
specific scopes plainly discharge a declared level residual.*

**P5 — of the commits landing in a SPECIFIC live atom's scope, more than 60% have subjects about
gates, landing, findings, publishing or reconciliation rather than about the atom's domain
subject.** This is the allocation reading the director is owed either way. *Refuted below 60%.*

## What done means for this claim

The cause is NAMED with the evidence beside it, the two `next_step_gate` triggers are graded
correct-and-idle or ornamental on that basis, and nothing is repaired in this pass — the item says
so and it is right, because the two causes have opposite remedies.

## P6 — appended 2026-09-25 AFTER P1–P5 were measured and BEFORE P6 was run

The anti-tautology control for P3 (run the same map query over the 248 first-parent commits BEFORE
`86504d951`) returned **9 map commits, of which exactly ONE moves a level VALUE** — `0022641d8`,
W2_34 1→2. One of the other two adds a new atom at 0 and the third rewrites a trailing comment on a
level that stays at 2. So the previous window was not the healthy comparison the item's framing
assumes, and the rate question is now the live one. Registering before running it:

**P6 — the advance rate is low across the whole period, not newly low.** Over the last 1500
first-parent commits, binned in 250s, level-VALUE advances total **between 20 and 60** (≥1 per 100
commits over the period), and the current 250-bin is the **lowest** of the six. *Refuted if the
total is under 20 or over 60, and — the claim that matters — refuted if any earlier bin is as low as
the current one, which would make "the map went quiet" the wrong description of a rate that was
always this low.*

## P7 — appended 2026-09-25 AFTER P6 was measured and BEFORE P7 was run

P6 turned up the thing that decides this. Of the **17 per-atom level advances in 1500 first-parent
commits**, at least five say in their own subject that the work was *already done and the map did
not say so* (`7f24e4ac3` "W2_30's level 2 was earned and unrecorded"; `e6c6ea178` "the map said zero
about work its own controls prove is done, and four rows were…"; `a43ee63fe`; `5d804d671`). So the
map was never a timely record — it was a **periodically-reconciled** one, and the reconciler is
`tools/level_zero_contradicted_by_its_own_controls.py`, which grades a `level_current: 0` row
against the controls its own row names. **It has no production caller**: its docstring says "Run
standalone", nothing in the hook chain or any daemon invokes it, and the last evidence of anyone
running it is 2026-09-17.

**P7 — the reconciler, run now, reports at least one CONTRADICTED row and at least twenty
UNGRADABLE ones.** The UNGRADABLE floor is close to arithmetic: 30 of the 110 live atoms declare an
EMPTY `file_scope` and so name no control at all. The CONTRADICTED claim is the real prediction and
the one that decides the cause: a contradicted row is an atom whose work IS done and whose level is
recorded nowhere, which is cause B's true half arriving by a route the item did not name — not
"recorded somewhere else" but "earned and recorded nowhere until a hand-run pass notices".
*Refuted if it reports zero CONTRADICTED rows, which would make cause A clean and the map's silence
an honest account of the work.*
