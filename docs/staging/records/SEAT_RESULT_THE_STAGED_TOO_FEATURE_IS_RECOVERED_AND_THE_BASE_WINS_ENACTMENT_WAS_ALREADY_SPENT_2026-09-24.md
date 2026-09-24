**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — `--staged-too` recovered onto the current base; the item's headline ask was already spent

*Filed by the delivery seat from an isolated worktree, 2026-09-24. Claim id
`enact-the-four-path-base-wins-decision-on-the-shared-tree`. Prereg:
`SEAT_PREREG_RECOVERING_THE_STAGED_TOO_FEATURE_A_BASE_WINS_ENACTMENT_ORPHANED_INTO_A_PRESERVED_REF_2026-09-24.md`.*

---

## 1. The item's headline ask: SPENT, by another lane, 1h05m before the draw

The four-path base-wins enactment was already done on the shared tree:

| evidence | reading |
|---|---|
| `refs/preserved/base-wins-four-2026-09-24` = `92b6629dc`, 19:42:14, parent `63356067f` | the preservation ran; its message names all four paths |
| all four working copies rewritten 19:42:26 | the enactment ran, twelve seconds later |
| `disk == index == shared HEAD` on all four | base won; the 15:02:31 stash-pop bytes are gone |

So the item's own PATH CHECK was right to grade all four `already landed`, and its PATH DRIFT was
right that all four went `dirty → already landed` while it waited. **What remains on those paths is
not a base-wins conflict** — it is the shared tree being 37 behind origin/main, which is a different
claim (`advance-the-checkout-and-let-the-publisher-publish`) with a different cause. The shared tree
is also 3 AHEAD, so `advance_shared_tree` refuses on DIVERGENCE before grading any path.

## 2. What was still owed, and is now done

The item named it explicitly: *"those two need the hunks read against 777c4adb8/c72c41e4c by hand
and either dropped or re-authored on the current base."* `--base-wins` cannot do that read — it
discards wholesale into a ref. Done by hand here, and the hunks split cleanly in two:

**(a) DROPPED — the older draft of a restructure already in.** The preserved copy *deletes*
`_clock_disclosure` (landed `95ec3faa3`), *deletes* the `unread_populations` branch (rule 1b,
`777c4adb8`), reverts `_probe` to its pre-repair signature (repaired by `62abd5e49`), and collapses
the `noqa: PLC0414` re-export blocks `777c4adb8` created. Landing any of it reverts those four
commits. The item's reading of this half was correct.

**(b) RE-AUTHORED — a genuinely novel feature, superseded by nothing.** `--staged-too`, orphaned
into the preserved ref by the enactment itself.

### Why it was worth recovering, measured on the trunk

* `git grep staged_too\|staged-too origin/main` → **zero matches in any code or test file.** Four
  matches total, all prose inside staging documents.
* `origin/main:tools/refresh_to_head.py` carried `STAGED = "refused_holder_has_it_staged"`
  referenced in exactly **three** places — the constant and the one refusal returning it.
  **Nothing relaxed it.**
* Exactly one test asserted the refusal fires. None asserted it could be escaped, because it could
  not. **A refusal with no exit is a wedge** — and no other door reaches an index entry:
  `isolate_hunks` separates by author not age, `surgical_land --content` lands the revert.

The state is live, not hypothetical: the shared tree has staged entries right now
(`docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`).

## 3. THE PREDICTIONS, AND HOW THEY CAME OUT

**P1 — all six feature pieces re-author with no semantic conflict. CONFIRMED.** None of the four
landed commits touches the `if path in staged:` branch, so the feature was orthogonal as predicted.

**P2 — five to seven of the seven tests pass unmodified. CONFIRMED, at the top of the range: 7/7.**
Whole file 52 passed (45 pre-existing + 7 recovered).

**P3 — the named risk. ITS ANTECEDENT NEVER FIRED, and the worry behind it is REFUTED.** I predicted
that *if* a test failed it would be `test_the_staged_partition_stays_three_distinct_answers` or
`test_staged_too_clears_the_index_entry...`, from a fixture grade moved by rule 1b or
`_clock_disclosure`. No test failed, so the conditional is neither confirmed nor refuted — but the
underlying worry is directly refuted: the partition test expects a staged `RIVAL_KIND_A` with the
flag on to grade `REFRESHABLE`, and it passes. **The fixture grades did not move under rule 1b.**
I was wrong to price that as the likely failure; the feature's isolation from those commits was
stronger than I credited.

**P4 — the pre-existing `test_a_path_the_holder_has_staged_is_refused` stays green. CONFIRMED**, and
it turned out to be load-bearing (see MUT 4).

## 4. Mutation proof — a test green from birth is the shape that needs it

Seven tests arrived passing. Five mutations, each caught **by the leg written for it**, which is the
reading that matters: a mutation caught only by a different leg is the flattering one.

| mutation | first/primary catcher | other legs |
|---|---|---|
| 1 weld the door shut (`staged_too` never relaxes) | `..._clears_the_index_entry_as_well_as_the_working_copy` — the reachability leg | 4 more, incl. the partition |
| 2 drop the index/worktree disagreement guard | `..._refuses_when_the_index_and_the_worktree_are_different_rivals` | partition |
| 3 write the worktree but NOT the index entry | `..._clears_the_index_entry...` + `test_the_commit_that_index_would_make_no_longer_carries_the_revert` — the property leg | — |
| 4 flag DEFAULTS ON in `judge_copy` | `..._is_off_by_default_in_refresh_and_in_judge` | + the pre-existing staged test, + partition |
| 5 refusal no longer names its door | `test_the_staged_refusal_names_the_door_out_of_it` — alone, precisely | — |

**MUT 4 is the one worth naming.** A mutation on an optional argument's *default* normally goes
green, because every test names the argument explicitly. It does not go green here — three legs
catch it, because tests exist that pass no opinion at all. That trap was avoided by construction,
not by luck: the recovered suite has an explicit off-by-default leg, and the pre-existing refusal
test never names the flag.

The partition control asserts `states == [STAGED, REFRESHABLE, STAGED_DISAGREES]` as an ordered
equality over three shapes — three shapes, three states — so a two-shapes-one-state collapse
shows, which is the blindness an `N`-states-over-`N+1`-shapes control has.

## 5. What is NOT done, and is not mine to leave implied

* **The shared tree's checkout is still 37 behind / 3 ahead.** Untouched here, and it is the live
  wedge. `advance_shared_tree` refuses on DIVERGENCE before grading a path.
* **`--staged-too` has not been RUN on the shared tree.** It is landed and proven in test; applying
  it to the real staged entries is a deliberate act on a tree this session does not hold.
* The item's separately-parked headline (routing `advance_shared_tree` through origin/main's
  rulebook) stays refuted and unbuilt — P3 of the earlier prereg, 0 of 14 paths differing.

## 6. A pre-existing red on the trunk, measured in passing and NOT mine

The coupled run (`tests/tools/` + all of `tests/architecture/`, 849 passed) surfaced one failure:
`test_a_published_count_gates_on_its_denominators_grade.py::test_the_undeclared_quotient_debt_only_SHRINKS`,
naming `tools/fold_noise_floor_family.py:612/613` (`assert 2 <= 0`).

**The one-variable control was run rather than the flattering reading assumed:** the same test on a
throwaway pristine `origin/main` worktree fails identically. It is red at HEAD, my diff cannot reach
that file, and `git status tools/fold_noise_floor_family.py` is empty here. Not caused by this work
and not repaired by it. The subject is already carried by a live finding
(`SEAT_FINDING_THE_PINNED_SELECTION_RESIDUAL_IS_THE_CONTROL_ARM_CANCELLING_AND_THE_RE_DRAW_MISSING_THE_PRICED_DECISIONS_2026-09-24.md`),
so no new finding is minted for it — recorded here only so the 849/1 split is not read as mine.
