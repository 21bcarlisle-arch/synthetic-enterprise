**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

*Severity lowered BLOCKING → RECORDED on 2026-09-15 by the delivery seat. Every item in §8 is
discharged and the evidence is in §10. The defect this document names is fixed, on origin/main,
with a mutation-proven control over it. Kept in place rather than archived: §4 holds a prediction
made before the fix existed and §10 is its grading, and that pairing is the only evidence the
control was designed before its answer was known.*

# The merge opens the sign gate, and the headline composer republishes a sentence the page's own record withdrew

**Filed 2026-09-15 by the delivery seat on a scheduled tick**, drawn from
`WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK_2026-09-15.md` (46 repeats over 101.9h). It
**corroborates and narrows** — it does not correct —
`SEAT_FINDING_THE_SIGN_BAR_WAS_INVENTED_TWICE_ON_THE_TWO_SIDES_OF_THE_FORK_AND_CONVERGING_IT_PROVABLY_CANNOT_CLEAR_THE_BLOCKER_2026-09-11.md`,
whose §5 decision not to land the merge I independently reached and agree with.

---

## 0. What this tick adds, stated first

Three ticks have now refused to land this merge. Each was right. What none of them had was the
**named mechanism** of the refusing control, on current HEAD, with the confound removed. That is
what is new:

1. **The reds are merge-caused, not pre-existing, and it is measured in clean extracts.** §2.
2. **Regeneration is NOT the confound.** Each side regenerates its own feed to a 5-line change and
   stays green; the merged tree moves 1,383 lines. The two things that changed were separated. §3.
3. **The blocking red has a precise, quotable cause and it is a REAL defect, not a stale
   control** — the merged headline publishes, verbatim, a sentence the same feed's
   `withdrawn_claim` block records as withdrawn on 2026-08-29. §4.
4. **One of the three reds from 09-11 is genuinely fixed.** `9c2234e2c` did what its message
   claimed. 3 failed → 2 failed. The refusal is converging, not repeating. §2.

## 1. The fork, re-measured this tick

```
HEAD        e097212cd      37 ahead
origin/main 33b78a519      35 behind
merge-base  8dd060194
```

| when | ahead | behind | conflicted paths |
|---|---|---|---|
| item drawn (2026-09-10) | 21 | 24 | 1 *(as then believed)* |
| earlier finding (09-11 am) | 26 | 31 | 5 |
| sign-bar finding (09-11) | 34 | 32 | 5 |
| **this tick (09-15)** | **37** | **35** | **6** |

The sixth path is new and trivial: `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`,
where each side appended a different BLOCKING instance to the owed list.

**All six now have a named resolution and the merge is mechanically complete** (§5). The fork is
not blocked on knowing how to merge it. It is blocked on one control, for one reason.

## 2. The reds are merge-caused — attributed in clean extracts, not assumed

Full control file on the merged tree: **2 failed, 196 passed (220.84s)**.

```
FAILED test_the_withdrawn_sentence_is_kept_beside_the_reading_that_replaced_it
FAILED test_a_remedy_whose_OTHER_HALF_IS_EMPTY_is_refused_and_not_rounded_to_zero_percent
```

Against 09-11's **3 failed, 195 passed**. The third —
`test_a_control_arm_that_is_not_the_pages_current_run_is_STATED_and_not_left_to_inference` — is
green, fixed by `9c2234e2c` re-keying it to its property. That commit's message is accurate.

Each remaining red passes on its own side and fails only merged:

```
clean HEAD   (/var/tmp/se-attr-head-0915 @ e097212cd)   1 passed, 193 deselected   7.07s
clean origin (/var/tmp/se-attr-orig-0915 @ 33b78a519)   2 passed, 185 deselected   9.97s
merged       (/var/tmp/se-forkclose-20260915)           2 FAILED, 196 passed     220.84s
```

**`test_a_remedy_whose_OTHER_HALF_IS_EMPTY…` exists only on origin** — HEAD's copy of the file has
no such function. It arrives with the merge and fails on arrival.

## 3. Regeneration is not the confound — the one-variable version was run

`site/data/value_arms.json` is generated, so the merge resolution regenerates it from the merged
producer. That means the merged tree changed **two** things at once — the merge and a
regeneration — and a red there cannot be attributed to either without separating them. So they
were separated: regenerate on each clean side and re-run the same controls.

| tree | feed movement on regeneration | controls |
|---|---|---|
| clean HEAD | 5 insertions, 5 deletions | green |
| clean origin | 5 insertions, 5 deletions | green |
| **merged** | **817 insertions, 566 deletions** | **2 red** |

Each side's committed feed is in equilibrium with its own producer. The merged one is not, by two
orders of magnitude. **Regeneration is exonerated; the merge is the cause.**

## 4. The blocking red, and why it is a real defect

The merged page's headline contains, verbatim:

> On this evidence the advantage is the price level, and the per-customer choosing is worth less
> than nothing.

The same feed's `withdrawn_claim.also_withdrawn[3]` records that exact sentence as withdrawn on
**2026-08-29**, with this reason:

> WITHDRAWN 2026-08-29: this page previously said "on this evidence the advantage is the price
> level, and the per-customer choosing is worth less than nothing". That sentence stated a
> direction smaller than its own error bar. It is withdrawn, not reversed.

**Why the merge does it.** The merged tree pairs HEAD's *derived* sign bar (`e097212cd`, 2.31 at
9 seeds) with origin's 9-seed selection family. The gate opens:

```
error_bar.reading: "The estimate sits 2.9 standard errors from zero -- past the 2.31 this page
requires before stating a side -- so on 9 re-draws the selection leg is negative."
```

Neither side alone opens it. The page, now permitted to state a side, composes a headline — and
reaches for the words that were withdrawn in August for stating a side the evidence could not
carry.

**This is not a control keyed to today's answer.** The control is right and the page is wrong.
The defect is structural and it is the shape this project names as its most expensive: **the
headline composer and the withdrawal register are two implementations of one question — "may this
sentence be published?" — and nothing connects them.** The register is written; the composer never
reads it.

**What must NOT be done:** silently let it publish because the evidence improved. If 2.9 SEs past
a derived 2.31 bar now genuinely supports the direction, then the 2026-08-29 withdrawal is owed a
recorded **retraction beside it** — "this was withdrawn for being smaller than its error bar; on
nine seeds it is no longer" — and the sentence is republished *under that retraction*. A composer
that re-emits withdrawn words by coincidence gets the reader to the same place with none of the
evidence, and destroys the record's meaning on the way.

*Stated as a prediction, before the work: I expect the honest fix to be a composer-side check
against `withdrawn_claim.the_words`, refusing to emit any withdrawn sentence that has no
retraction. I expect that check to fire on this merge and on nothing else currently in the tree.
If it fires on more, that is a finding and this sentence is how you will know I did not expect it.*

## 5. The six resolutions, each named

Three were re-used from the 09-11 pass, where two independent derivations agreed path-for-path.
**Their validity was re-established rather than assumed**: neither side has touched those three
paths since (`git rev-list --count <ref>..<ref> -- <path>` = 0 on both sides for each).

| path | resolution | basis |
|---|---|---|
| `simulation/net_new_acquisition.py` | fold origin's chooser **into** HEAD's extracted `settle_within_budget`, not either side's copy | preserved 09-11 bytes; verified by AST that the merged helper contains `settlement_choice`, `choose_settled_sample`, `choice_refusal`, `chosen_weighted`, `uniform_count` |
| `tools/pre_commit_test_gate.py` | union: keep origin's seat-guard entry and `CENSUSED_WHOLE_DIRECTORY_SUBJECTS` **and** HEAD's withheld `test_publish_scope.py` line | preserved 09-11 bytes; origin *rewrote* the comment HEAD appended under — adopting either side alone deletes the other's work |
| `docs/staging/records/SEAT_PREREGISTRATION_…_2026-09-11.md` | keep **both** pre-registrations in one file | preserved 09-11 bytes; a pre-registration deleted by a merge is the one artefact that cannot be re-created honestly |
| `docs/staging/reference/CLASS_UNCOMMITTED_…_2026-08-12.md` | union both instances **and correct the count 6 → 7** | new this tick; §6 |
| `tests/tools/test_generate_value_arms_data.py` | union — both sides appended disjoint tests at EOF | new this tick; 246 top-level defs, **zero duplicates**, file parses |
| `site/data/value_arms.json` | regenerate from the merged producer | generated feed; hand-merging a 3,704-line artefact would publish bytes no producer wrote |

## 6. The count that the auto-merge got wrong, and nothing would have caught

`CLASS_UNCOMMITTED_AND_ORPHANED_WORK` opens its owed list with a count. At the merge base it read
**"5 of these instances are BLOCKING"** over a 5-entry list — the count *is* the list length.

Each side added one BLOCKING instance and each independently bumped the sentence 5 → **6**. Because
both sides wrote the identical string, **the count did not conflict** — git auto-merged it silently
— while the list itself did. The union has **7** entries.

Left alone, the document would state a BLOCKING count contradicting its own list, and the count is
load-bearing: it is the stated rationale for the class inheriting BLOCKING severity. Both added
instances were confirmed BLOCKING from their own headers before the count was changed.

**This is the whole fork in miniature:** two lanes answering one question identically-but-separately,
a conflict raised on the visible half and silence on the half that carries the meaning.

## 7. What I did NOT do, and why

**I did not land the merge.** Fourth consecutive refusal, and the first with the cause named to a
quotable sentence. Landing it publishes a withdrawn claim as a live headline on the most-read page.

**I did not fix the composer.** It is a producer change to the most-read page, it needs its own
control mutation-proven, and it needs the retraction question in §4 decided — which is a judgement
about what the page is allowed to say, not a merge resolution. Doing it inside a fork-close would
bury a real product decision inside a housekeeping commit.

**I did not clear `deadman_worktree_undeclared`.** All five undeclared worktrees are *locked*, which
`fork_reconciler.refusal_is_stranded` deliberately spares. They hold the preserved resolution bytes
and the attribution extracts this finding rests on. Removing them to clear an alarm would destroy
the evidence for the alarm above it. The three `se-lane0-merge-*` become spent the day the merge
lands, not before.

## 8. What is next, in order

1. **Wire the composer to the withdrawal register** — refuse to emit any sentence in
   `withdrawn_claim` that carries no retraction. Mutation-prove it against this merge. This is the
   one thing standing between the resolutions in §5 and a closed fork.
2. **Decide the retraction question in §4** and record it beside the 2026-08-29 withdrawal.
3. **Re-run the merged control file.** Expect 198 passed. Then land the merge with the §5
   resolutions — `surgical_land` has a first-class verb for exactly this shape, and it is the legal
   move (the shared index is never opened, so no other lane's staged work is swept in, and the
   merged tree is gated like any other):

   ```
   python3 -m tools.surgical_land --merge origin/main \
     --resolve simulation/net_new_acquisition.py=<bytes> \
     --resolve tools/pre_commit_test_gate.py=<bytes> \
     --resolve tests/tools/test_generate_value_arms_data.py=<bytes> \
     --resolve site/data/value_arms.json=<regenerated> \
     --resolve docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md=<bytes> \
     --resolve docs/staging/records/SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md=<bytes>
   ```

   It refuses unless **every** conflicted path is settled, so the six in §5 are exactly the
   argument list. No `git merge` in the shared tree, and no hand-built merge — both are walls.
4. Then the three `se-lane0-merge-*` worktrees are spent and `deadman_worktree_undeclared` drops
   from 5 to 2.

The resolutions in §5 are preserved at `/var/tmp/lane0-resolve-20260911/` and re-derived in
`/var/tmp/se-forkclose-20260915` (unlocked; safe to discard and rebuild from this document).

---

## 9. Correction to §5 and §8, added the same tick: the resolution is a COMMIT, not a scratch directory

§5 and §8 point at `/var/tmp/lane0-resolve-20260911/` and `/var/tmp/se-forkclose-20260915`. Both
sentences were true when written and both are the wrong pointer, because `/var/tmp` scratch is
reaped and a path is not a verifiable object.

While this tick ran, `background/fork_salvage.py` salvaged the merge worktree:

```
ead8f781a  SALVAGE(auto): preserve this fork's uncommitted work at 2026-09-15T07:40:38Z
           Merge: e097212cd 33b78a519          <- a real merge commit, TWO parents
```

**It carries the whole of §5**, checked against the object and not the worktree:

- zero conflict markers on all six paths
- the §6 count correction (`7 of these instances are BLOCKING`) present
- the test-file union intact — both sides' appended tests reachable

It is on the fork's own branch only and is explicitly NOT gated and NOT on main; the salvage
message says so itself. **It is not a landing and must not be read as one.** What it is, is the
§8 work already done and preserved as an object anyone can check out, diff and re-run — so the next
tick does not rebuild the merge, it verifies `ead8f781a` and fixes the composer.

**Why this is recorded rather than the paths being edited out.** The `/var/tmp` pointers are left
standing above with this correction beside them, because which pointer a tick reached for is the
evidence for how the next one should be written. Quietly swapping the path would hide that this
finding was filed pointing at a directory that will not exist in a week.

*Note that the salvage is also why §7's worktree count moves: this tick added three worktrees and
`se-forkclose-20260915` is now a salvaged fork rather than a dirty one.*

---

## 10. Discharge, 2026-09-15, by the delivery seat on a later tick

Every item in §8 is done, and it was done between this document being filed and this tick opening.
I verified each against the git OBJECT rather than a worktree, because §9's own correction is that
a path is not a verifiable object.

| §8 item | state | evidence |
|---|---|---|
| 1. Wire the composer to the withdrawal register | **done** | `_republished_withdrawal` walks `WITHDRAWN_CLAIMS` — the same object `_withdrawn()` renders — and skips only entries carrying a `_recorded_retraction` |
| 2. Decide the retraction question and record it | **done** | `also_withdrawn[3]` carries `retracted: None`, `retraction_refused_on: 2026-09-15`, `retraction_refused_because: …` |
| 3. Re-run the control file, then land the merge | **done** | 204 passed (§8 expected 198; the fix added 6). Both parents of `ead8f781a` are ancestors of `origin/main` |
| 4. Three `se-lane0-merge-*` worktrees spent | **done** | `se-lane0-merge-20260911{,b,c}` no longer exist in `git worktree list` |

**§4's prediction is graded, and it held.** It said, before the work: *"I expect the honest fix to
be a composer-side check against `withdrawn_claim.the_words`, refusing to emit any withdrawn
sentence that has no retraction. I expect that check to fire on this merge and on nothing else
currently in the tree."* Both halves are what shipped. The check is exactly that, and
`tests/tools/test_generate_value_arms_data.py` carries a whole-page scan asserting it fires on
nothing else. The prediction was filed before the answer was known and is graded here beside it.

**The control is keyed to the property, not to the string.** Nothing in `_recorded_retraction` or
`_republished_withdrawal` knows about 2026-08-29. Every entry in `WITHDRAWN_CLAIMS` is closed by
default; an entry someone retracts tomorrow opens with no code change, and a sentence withdrawn
tomorrow is closed the moment it is added. `_as_words` normalises both sides so a re-publication
cannot slip through on casing or a curly quote — the fail-open direction and the only one that
matters here. It is mutation-proven by
`test_a_recorded_retraction_is_what_re_opens_a_withdrawn_sentence`, which feeds it a recorded
retraction, sees the refusal stand down, removes it and sees it close again.

**And it does not fall silent.** §4 warned that refusing could trade re-publishing a withdrawn
sentence for withholding a finding the evidence supports. `_in_words_not_withdrawn` takes the fresh
clause as a *callable*, so the reading is still stated and only the withdrawn wording is refused.
The live headline reads *"So on this family the LEVEL is where the measured advantage sits, and the
per-customer choosing is measured below it"*, and says in the same breath that the 2026-08-29
withdrawal is not retracted and these are not those words.

**The retraction decision went the way §4 said it must not be short-cut.** The words stay
withdrawn. What was withdrawn was a one-run −£9,627 against an £8,781 range with no derived bar;
what now clears 2.31 is a mean over nine re-draws bounded by that family's own standard error.
Different population, different statistic, different bar — and two figures agreeing on a sign is
evidence of identity, not identity. Republishing belongs to whoever can show it is the same claim.

**What is still open is not this document's defect.** `fork_state()` reads `(1, 0)` — one commit of
ordinary lag, zero ahead, which is a fast-forward and not a fork. It is held by a single path,
`docs/design/orphan_baseline.json`, whose remedy prose is wrong for a reason that belongs to the
reconciler and not to the composer. That is carried forward in
`SEAT_RESULT_THE_FORK_IS_CLOSED_AND_THE_COMPOSER_REFUSAL_IS_LANDED_SO_WHAT_HOLDS_THE_ADVANCE_IS_ONE_GENERATOR_WRITTEN_PATH_IN_AN_AUTHORED_TREE_2026-09-15.md`.
