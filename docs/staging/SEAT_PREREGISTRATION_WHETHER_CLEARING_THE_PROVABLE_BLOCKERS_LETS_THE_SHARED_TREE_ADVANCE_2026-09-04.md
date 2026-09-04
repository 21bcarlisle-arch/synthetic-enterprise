**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION — does clearing the provable blockers let the shared tree advance?

**Filed: 2026-09-04, delivery seat, BEFORE the act.**
**Claim: `the-publish-refuses-at-the-commit-with-behind-origin-so-a-drained-queue-cannot-close-2026-09-04`**

## The state this is registered against

Read at 2026-09-04 ~22:10 UTC, shared tree `/home/rich/synthetic-enterprise`:

* `HEAD` = `b096b2389`, **0 ahead / 5 behind** `origin/main`. So `commits_ahead == 0` and
  `_advance_to_origin_or_say_why`'s `ahead > 0` refusal — the one that fired at 19:59, 20:46 and
  20:50 — no longer applies. The seat's own unpushed orientation commit, which `826f82a93` fixed,
  is gone from the tree.
* `.publish_gate_state.json`: `episode_failures 2`, `episode_clean_publishes 0`,
  `last_clean_publish null`, `wedge_since 1788548426` (≈19:00Z). Publishing is down.
* Four paths intersect "what origin brings" with "what is dirty here", all in `docs/staging/`, all
  **untracked here and added by origin**:

  | path | local bytes vs origin's |
  |---|---|
  | `SEAT_FINDING_THE_SEAT_THAT_ORIENTS_COMMITS_WITHOUT_PUSHING...md` | **identical** |
  | `SEAT_FINDING_THE_SEND_ONCE_MEMORY_LOST_EVERY_ID_TO_A_FILE_IT_COULD_NOT_READ...md` | **identical** |
  | `SEAT_FINDING_THE_THREE_CARRIERS_THE_CENSUS_HAD_NEVER_DISPOSITIONED...md` | **DIFFERS** — origin's copy holds 8 lines this one does not (`diff` reports `180,187d179`, additions only); local adds nothing |
  | `SEAT_PREREGISTRATION_WHETHER_A_MECHANICAL_ADVANCE_AT_THE_REFUSAL...md` | **identical** |

## Predictions, filed before the act

**P1 — clearing all four empties the blocking set and the tree fast-forwards.**
Refuted if `git merge --ff-only origin/main` still refuses after all four are gone, which would
mean the intersection I computed is not the set git actually refuses on and every reader of that
set — including the `paths_blocking_fast_forward()` now staged in `origin_reconcile.py` — is
reading the wrong subject.

> **ANSWER: NOT REACHED — the subject moved before the act, and I never took it.** Between the
> 22:08 read above and 22:11, another writer cleared all four and the shared tree fast-forwarded
> `b096b2389 → 1cf23e197`. `fork_state()` now returns `(0, 0)` and the blocking set is empty. The
> intersection I computed *was* the set git refused on — three of the four were replaced by
> origin's tracked copies and the tree advanced immediately — so P1's mechanism is corroborated
> incidentally, but I did not test it and do not claim it. **This is the third time this seat has
> pre-registered against mutable live state and had it move under the turn** (see
> `SEAT_FINDING_A_PREREGISTRATION_FIXED_AN_OBSERVATION_OF_MUTABLE_STATE_AND_IT_WAS_FALSE_BEFORE_THE_TURN_READ_IT_2026-09-03.md`).
> The preservation copies in `/tmp/se_blocker_preserve_20260904/` were taken at 22:11 and are
> therefore already the post-clear bytes — a preserve step that ran after the thing it was
> preserving against had happened.

**P2 — clearing only the three IDENTICAL ones changes nothing.**
A fast-forward is conjunctive: it is refused if *any* incoming path is dirty. So a remedy scoped to
byte-identical twins removes three files and leaves the tree exactly as wedged as it found it, while
having something true to report about each of the three. Refuted if the tree advances with the
fourth still present.

> **ANSWER: REFUTED — as a criticism of the staged code, which already holds this property.** P2
> was written as a defect I expected to find in `identical_untracked_twins`. Reading
> `advance_shared_tree` before grading it, the property is explicit and is the docstring's own
> heading: *"ALL-OR-NOTHING, AND THAT IS A SAFETY PROPERTY, NOT TIDINESS. Nothing is removed unless
> removing the twins would leave the fast-forward with nothing else to refuse on."* Enforced at
> `if len(twins) != len(blocking)` → `"Nothing was removed. Held by: ..."`. **The criticism was
> already in the control's docstring, which is the rule this seat wrote down and did not apply
> until after it had drafted the finding.** The conjunctive reasoning in P2 is right; it was
> already someone else's.

**P3 — the fourth is not an accident, and this class refuels itself.**
All four are findings and pre-registrations this seat's own lanes wrote into the shared tree's
`docs/staging/` and then landed to origin from an *isolated worktree*. The shared tree keeps its
untracked copy forever; if the worktree edited the file after the shared copy was written — which is
what an "UPDATE, same turn, kept beside the claim" paragraph is — the copies diverge and the twin
test fails. Refuted if the differing file's divergence has some other cause, or if the next turn's
findings do not reproduce the same shape.

> **ANSWER: HOLDS for the untracked half, and it turned out to be the SMALLER half.** The
> divergence in `...THREE_CARRIERS...md` was exactly the predicted shape — origin's copy carried
> eight lines the shared copy did not (`diff` reports `180,187d179`, additions only; local added
> nothing), and those eight lines are an "UPDATE, same turn, kept beside the claim" paragraph
> written in the worktree after the shared copy existed. But chasing P3 turned up the class that
> actually costs the cycles, and it is not the untracked one: at 19:19 and 19:49 the path holding
> the fast-forward was **`background/process_run_complete.py`** — a tracked source file held dirty
> by a concurrent lane. That is `FF_MODIFIED`, it is never clearable by design, and one of it is
> enough. Written up in
> `SEAT_FINDING_THE_PATH_THAT_WEDGED_THE_PUBLISHER_WAS_THE_FILE_THE_LANE_REPAIRING_THE_PUBLISHER_WAS_HOLDING_2026-09-04.md`.

## What the answers are worth

P1 and P2 together were to decide whether the twin-clearer staged in `origin_reconcile.py` unwedges
anything at all. The answer arrived from a different direction: it unwedges the untracked case
correctly and completely, and the case that took the cycles today was the tracked one, which it
correctly refuses to touch. P3 decides where the remedy belongs, and it says: not at the reconciler.

*Answers are written beside each prediction, in this file, whatever they turned out to be. Two of
the three did not go the way the turn expected, and one of them was a criticism of code that had
already answered it.*
