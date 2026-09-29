**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The shared term is the control arm, and it cancels: the residual moves only when a PRICED decision moves

Answers the question `224ed807c` handed on and the 09-22 finding
(`SEAT_FINDING_THE_NARROW_WIDTH_BEHIND_THE_PUBLISHED_SELECTION_SIGN_IS_A_REPEATED_DRAW_2026-09-22.md`)
left open: *which term do both value arms consume identically that the elasticity re-draw does not
reach?* It is not a tree, not a seed set and not a re-draw that failed to fire. **It is the control
arm, and the mechanism is arithmetic.**

## The mechanism, in three lines of the producer's own code

`tools/run_value_cycle_ab.py::level_vs_selection`:

```
value_advantage = value_m["total_net_gbp"] - control_net
level_advantage = level_m["total_net_gbp"] - control_net
selection_gbp   = value_advantage - level_advantage        # == value_net - level_net
```

**`control_net` cancels algebraically.** The residual is the two surviving arms' difference, and
those two arms differ by the renewal-margin rule and by nothing else — `flat_at_level` prices
exactly the renewals the value arm priced, through the same guards, under the same ceiling.

So every pound the elasticity re-draw moves **outside** the renewals the value arm priced lands in
`value_net` and `level_net` **identically**, cancels in the residual, and surfaces in both
*advantages* as the same number, because both subtract the same `control_net`. A seed pair whose
priced decisions did not change therefore reports its two advantages moving in lockstep to the last
digit and its residual not moving at all.

**That is not a small dispersion. It is a structural zero.**

## Measured, not argued — and the evidence was already on disk

Ten seed pairs of the five-seed HEAD family (`value_cycle_ab_s1_noise_floor_five_seed_head_20260924.json`,
landed at `224ed807c`). The lockstep is **exactly coextensive with an unchanged decision set, in
both directions, with no exceptions**:

| pair | `scored_decisions` identical | advantages in lockstep | Δ`selection_gbp` |
|---|---|---|---|
| 11-12 | no | no | −226.395 |
| 11-13 | no | no | −295.584 |
| 11-14 | no | no | −226.395 |
| 11-15 | no | no | −226.395 |
| 12-13 | no | no | −69.189 |
| **12-14** | **yes** | **yes** (both moved 162.0809719999961) | **0.0** |
| **12-15** | **yes** | **yes** | **0.0** |
| 13-14 | no | no | +69.189 |
| 13-15 | no | no | +69.189 |
| **14-15** | **yes** | **yes** (both moved 0.0) | **0.0** |

**12-vs-14 is the decisive row.** A genuinely different world — both advantages moved by
£162.0809719999961 — with an unchanged decision set and a residual identical to fifteen digits.
That is the 09-22 finding's "mechanism 2" (`a residual pinned across a pass that genuinely
differed`) with its cause named: the pass differed *outside the priced renewals*.

This cost no compute. The family was already landed; `scored_decisions` had been on the row since
2026-09-19 for an unrelated reason (the AUC's own null), and it is the only field that could
answer this. **The eleven-hour re-run the cheapest-looking route would have bought was never
needed.**

## Why the re-draw mostly misses

The elasticity leg re-draws ~293 call sites per seed and the value arm prices ~20 renewals. The
residual's entire support is whether a *priced* household's decision flips. Most re-draws move the
rest of the book, land in both arms identically, and cancel. **`n` distinct decision sets, not `n`
seeds, is the count a spread over this instrument is entitled to** — and the published floor states
a NEGATIVE selection sign at 2.50 sems over eighteen draws, five of which repeat.

**The sem is rewarded by the pinning**, which `224ed807c` already recorded as the defect reading as
a result: the harder the instrument pins, the more confident it reports itself to be. A family that
pinned all five draws would report a spread of zero and declare itself infinitely confident.

## What this commit changes

1. **The row can now say which arm moved.** `control_net_gbp`, `value_arm_net_gbp` and
   `level_arm_net_gbp` are on every seed row. Their absence is why no floor artefact on disk could
   attribute its own pinning: the row published two *differences* of three levels it dropped, so
   "the control arm moved alone" and "both other arms moved together" were the same row. They are
   **subscripted, not `.get`** — `level_vs_selection` writes all three unconditionally once
   `available` is True, so a run reaching the writer without them is a changed contract and refuses
   rather than writing three silent `None`s a consumer would difference. Three fixtures in the
   control suite published a `level_vs_selection` the real block never produces; that refusal found
   them, and they are fixed.
2. **`priced_decision_fingerprint`** on every row: the identity of the decision set the residual was
   taken over, digested from the row's own roster (built once, used twice — a second construction
   would let the digest and the roster drift apart). **Unknown is not agreement:** a seed that
   measured no belief fingerprints `None`, while a seed that priced nothing scorable gets a real
   digest of the empty list. Collapsing those would let a consumer count two un-measured seeds as
   one repeated draw and shrink a spread that is already too narrow — the exact direction this
   instrument errs in.
3. **Six mutations, all proven to bite**, in `tests/tools/test_value_cycle_ab_noise_floor.py` §14:
   a constant fingerprint reds the SEPARATES leg; a per-call-unique one reds the JOINS leg (one
   control over the whole partition, because each leg alone is passed by a broken writer);
   `None`→`[]` reds the UNKNOWN leg; swapping the level arm's net onto the value arm's key reds the
   reconciliation; keying the artefact control on book size instead of the decision set reds it; and
   truncating the family to a pair with no repeat reds the reachability assertion, so the rare
   branch this control exists for is proven *takeable* and not only *correct*.

## What it does NOT establish, and what is owed

- **Does not** establish the true dispersion. It establishes that the published sd is part
  dispersion and part pinning, and that until this commit nothing on disk could separate them.
- **Does not** withdraw the published sign. Same reason as 09-22: that is a change to what the page
  claims and the order is evidence first, constant second. The finding stays BLOCKING.
- **Owed next, and handed on:** `fold_noise_floor_family` should count **distinct fingerprints**
  beside `n` and carry that count to the reader, so a family reports the draws it is entitled to
  rather than the seeds it ran. Until it does, this field is recorded and unread — and a field
  nobody reads is not a control.
  - **DONE at `6f040e8d2` (2026-09-24), and it answers with a BOUND rather than a number.**
    `summarise` now publishes `priced_decision_draws`. Exact where every row carries a fingerprint;
    elsewhere a floor from the contrapositive of the coextension recorded above — two seeds whose
    residuals *differ* cannot have met one decision set — which is the only reading available on
    the families that were actually published, because none of them records a roster. Measured:
    the published eighteen is **between 15 and 18 draws**, which re-derives from the artefact the
    "five of which repeat" this document counted by hand; `..._five_seed_head_20260924.json` is
    **exactly 3 draws over 5 seeds**, its digests *derived* from the `scored_decisions` rosters it
    carries, using the producer's own function — without that derivation the only family on disk
    that records its decision sets would have read as five unknowns. Unknowns are never collapsed:
    they add nothing at the floor and a whole draw at the ceiling. The floor carries its own
    falsifier and is withdrawn, loudly, on any family where a fingerprint appears on two seeds
    whose residuals differ.
  - **CLOSED at `2ed53bcaf` (2026-09-24). The page states it.** `_error_bar` now publishes
    `priced_decision_draws`, and the capabilities page renders "those 18 seeds are between 15 and
    18 distinct draws of it" in amber, with the reason it is a RANGE beside it. The count is
    DERIVED through `fold_noise_floor_family`'s own function over the floor's own seed rows, so it
    has one home and no watched artefact was re-folded -- which is what let this land without
    owing the served family's promotion in the same commit. The sentence stating the bar no longer
    calls the seed count a draw count ("18 draws set" -> "18 seed re-draws set").
    - `the_published_n_overstates_the_draws` is THREE-VALUED, and its first draft was wrong in the
      flattering direction: written `at_most < seeds` it returned `False` on this very family --
      18 seeds, 15 to 18 draws -- and `False` there reads as "the standard error is taken over the
      count it is entitled to". Caught by printing the block at real inputs before shipping it,
      not by more thinking. `False` is now reserved for the family KNOWN clean, `True` for the one
      KNOWN to overstate, `None` for the one that cannot tell. Both reachable branches are
      exercised on real families on disk: this floor reads `None`, and
      `..._five_seed_head_20260924.json` reads `True` at 5 seeds and exactly 3 draws.
    - The re-grade at the floor is NAMED, never recomputed: `width_if_each_value_counted_once` has
      recomputed this interval over the same 15 since 2026-09-23, and `the_floor_regrade_agrees`
      witnesses that the two counts still coincide -- a claim that can go false the day a family
      lands carrying real fingerprints, because two distinct decision sets can return one residual.
    - Six mutations proven to bite, three on the renderer and three on the producer, and the three
      rendered readings are asserted PAIRWISE DISTINCT rather than leg by leg. The colour leg's own
      first draft could not fail: `arms-errorbar` opens with an unconditional amber heading, so
      `"var(--amber)" in raw` was true of every branch and it graded the heading instead of the
      sentence under test. Found by running it; it is now scoped to its own span.

  - **WHAT IS STILL OWED, and it is no longer the reader's half:** the headline sem is still taken
    over 18. That is the honest figure to publish while the count is a BOUND -- substituting a
    floor for `n` would state a confidence the evidence does not establish, and the sensitivity at
    that floor is already published beside it (2.4954 sems -> 2.4941; the family still clears). The
    arithmetic can only move to the entitled count on a family that RECORDS its rosters, which no
    published floor does. So the next piece is a re-fold or re-run of the served family carrying
    `scored_decisions`, after which `draws_the_spread_is_entitled_to` is EXACT and
    `sems_to_state_a_sign` can take it. That is a different piece of work with a different
    blocker, and it should be drawn on its own terms rather than inside this one.

  - **WHAT THIS BULLET SAID BEFORE `2ed53bcaf`, kept beside what closed it — a claim about what was
    owed, left next to its result, is the only evidence the order was decided before the answer was
    known:**
    `generate_value_arms_data` does not read the new block, and no published floor artefact has
    been re-folded to carry one — deliberately, because regenerating a watched artefact makes its
    promotion owed in the same commit and the served family is the republish lane's. So the page
    still prints `n` seeds as `n` draws beside a sem that is an upper bound on this family's
    confidence. **The finding stays BLOCKING for that reason and not for the one above.**

**Reversal:** `git revert`. Two additive row fields, three fixture corrections and one control
section; no constant moves and no published figure changes.

---

### Incident recorded in passing: this turn used `git stash` on the shared tree

To check whether a red in `tests/tools/test_selection_variance_decomposition.py` predated this work,
this seat ran `git stash` — which is on the never-do list for exactly the reason that followed. It
swept **436 paths of several lanes' uncommitted work** into a stash entry, and `git stash pop` then
refused repeatedly because daemons re-dirtied a *different* set of state files between each attempt:
the blocker set moved faster than the pop could clear it.

Everything was recovered and verified byte-identical, by partitioning the stash's paths against disk
(`disk == HEAD` ⇒ the stash holds work disk lost, restore it; `disk` already dirty ⇒ the daemon's
copy is newer, leave it) and restoring the 426-path safe subset with `git restore --source`. The 11
files reset to HEAD to attempt the pop were copied aside first and restored from that copy.

**Two things worth the next session's attention.** `git restore --source=stash@{0}` silently skipped
the one path that existed in the stash but in neither HEAD nor the index — an untracked file — and
it had to be written out with `git show`. And the completeness sweep could not see that miss:
`git diff --quiet HEAD -- <path>` is quiet for an untracked path *whatever its content*, so the
detector reported the file still lost after it had been correctly restored, and would equally have
reported it safe had it not been. **A recovery sweep built on `git diff HEAD` is blind to exactly
the class of file a stash is most likely to strand.** Confirmed by md5 instead.

The stash entry is **deliberately left in place** as the copy of record; it is not dropped.

The red itself does predate this work: it is in another lane's untracked
`tests/tools/test_selection_variance_decomposition.py` and reproduced identically with this change
absent.

---

## 2026-09-25 — the reader's half is PAID, and this stays BLOCKING for a narrower reason

The bullet above said *"what is still owed, and it is no longer the reader's half: the headline sem
is still taken over 18"*. **Half of that was wrong about itself.** The page stated the count and not
what the count was WORTH — it printed "those 18 seeds are between 15 and 18 distinct draws" and then
a confidence over 18, with nothing anywhere saying what 15 would have earned. `summarise` has
published `selection_leg_regraded_over_draws` since `6f040e8d2` and **`generate_value_arms_data` read
it nowhere**: the whole-leg regrade was in the same position `priced_decision_fingerprint` had been
in the day this finding was filed — recorded and unread. A count without its consequence asks the
reader to finish the arithmetic on the strongest claim the page makes.

**Landed:** `_draws_this_family_is_entitled_to` now carries `the_leg_regraded_over_those_draws`,
read from the artefact's own block when it has one and derived through `regrade_over_distinct_draws`
otherwise — the two provenances asked independently, because a family folded between `6f040e8d2` and
the regrade's own landing carries a count and no regrade, and inheriting the count's verdict would
report an absent regrade as an artefact's answer. `site/capabilities/index.html` renders three
states: the sign does not survive the correction (amber), the sign is unchanged (muted — a large
correction that leaves the claim standing is a reassuring reading, and colouring it as a warning
teaches the reader to discount the colour), and cannot be graded (amber, with the reason on the
surface). **Every family on disk renders the third and no published figure moved.**

Five mutations proven to bite, and a sixth read GREEN and was **a no-op, not an equivalence** — the
pattern it substituted ended `+ ';'` where the file has `+ ';">'`, so it never applied. Re-applied
against the real text it reds the colour leg. Recorded because "the mutation did not fire" has three
causes and the flattering one is never the default reading.

**Not what the drawn item asked for.** The item said to let `sems_to_state_a_sign` take the entitled
count. That moves ONE of the three terms a repeated draw touches and grades a sem taken over seeds at
a bar earned by draws; `regrade_over_distinct_draws` records the argument at length and recomputes
the whole leg. The page reads that block rather than substituting an `n`.

**Why this still BLOCKS, and it is now one thing only.** The count is still a BOUND, because no
family on disk records its rosters and the item's offered alternative — *re-fold* the served family
— is **impossible**: both members of the served fold carry zero `scored_decisions`, measured, and a
fold cannot pool what its members never wrote. The only route is a re-run, and it is in flight:
unit `longjob-floor18-head-rosters-20260925`, the served family's own 18 seeds, six legs of three at
`ba9bc6733`, worktree `/var/tmp/se-floor18-head-20260925`. Its five predictions are pre-registered
before any leg finished, with the P5 numbers computed in advance, in
`docs/staging/records/SEAT_PREREG_THE_EIGHTEEN_SEED_RE_RUN_AT_HEAD_REPRODUCES_THE_SERVED_RESIDUALS_2026-09-25.md`.
When it lands the regraded reading appears on the page with nobody editing a string, which is what
landing the reader's half FIRST bought.

**Reversal:** `git revert`. One additive payload key, one renderer function, two controls; no
constant moves and no published figure changes.
