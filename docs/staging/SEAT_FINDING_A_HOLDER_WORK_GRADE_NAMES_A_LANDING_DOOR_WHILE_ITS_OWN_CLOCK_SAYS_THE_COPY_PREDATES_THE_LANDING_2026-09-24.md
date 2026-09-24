**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — a `holder work` grade names a landing door while its own clock, in scope, says the copy predates that landing

Drawn as `judge-the-advance-with-the-bases-rules-not-the-behind-checkouts`. Pre-registration:
`docs/staging/records/SEAT_PREREG_CAN_THE_ADVANCE_BE_JUDGED_BY_ORIGINS_RULEBOOK_INSTEAD_OF_THE_CHECKOUTS_2026-09-24.md`.
Landed this turn: the disclosure below, with two mutation-proven controls.

---

## The premise, re-measured first

All three commits the item cites (`c72c41e4c`, `398040a36`, `777c4adb8`) are ancestors of
`origin/main`. The DETECTION half is landed and spent. The two duplicate-work candidates were read
and are dispositioned at the foot of this note.

What is NOT spent: the shared tree is live in the state the finding describes — HEAD `61b67fa0d`,
**32 behind / 3 ahead**, with BOTH `tools/refresh_to_head.py` and `tools/stale_copy_refusal.py` in
`git diff --name-only HEAD origin/main`. So `stale_judges` reads non-empty right now.

---

## P3 REFUTED, and it is recorded here beside the prediction rather than quietly dropped

The pre-registration predicted (70%) that on the live 32-behind tree at least one blocking path
would grade differently under the checkout's rulebook and origin's. **It does not.** A two-arm
differential over all **14** paths `paths_blocking_fast_forward` returns for the shared tree —
arm A `PYTHONPATH=/home/rich/synthetic-enterprise` (the working copies a daemon actually imports),
arm B a `git archive origin/main` export of `tools/` + `background/`, same root, same base,
same 14 paths — returns **0 of 14 differing**.

P1 was refuted too, in the useful direction: the two-dir export imported and judged on the FIRST
attempt. P2 (the null arm, a tree level with origin) confirmed — both rulebooks agree where no
judge is in the gap, which is what makes the P3 zero a reading and not an artefact.

**What this changes.** The stale-rulebook defect is REAL and its detector is correct; it is not
BITING on today's blocking set. So the remedy the item names — routing `advance_shared_tree`'s
judgement through origin's code — is a mechanism built for a divergence that currently measures
zero, and it would be the second-largest thing in this module. **It is not the next thing.** The
feasibility is established and recorded above so the next session does not re-derive it; the build
is deferred, by measurement rather than by preference.

The shared tree is additionally **3 ahead**, so `advance_shared_tree` refuses on DIVERGENCE before
it grades any path at all. Nothing here would move it. Saying otherwise would have been the
multi-variable attribution error.

---

## What IS biting, measured on the live tree, and what was landed for it

`judge_copy` computes `clock = opinion(root, path, head_text, work_text, parent=base)` at the top
and holds it in scope throughout. The `SUPPLIES_NEW` (holder work) return **discarded it** and
printed, unconditionally and without qualification:

> this copy SUPPLIES 3 name(s) origin/main does not have, so it is not a copy origin/main
> supersedes — it is holder work. Use `python3 -m tools.isolate_hunks --survey
> tools/refresh_to_head.py` and land hunk(s) 1, 3, 4, 7 over HEAD

with `clock.rule == "predates_landing"` sitting in the same frame. **The door named writes bytes
that predate the commit they land over.**

Measured on the live shared tree, 2026-09-24 — every working copy stamped **15:02:31** by one
stash-pop, against a later landing on its own path:

| path | grade | clock says | origin's last commit |
|---|---|---|---|
| `tools/refresh_to_head.py` | holder work | `predates_landing` | `777c4adb8` 17:10 |
| `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` | holder work | `predates_landing_by_clock` | `c72c41e4c` 18:24 |
| `tests/background/test_publish_gate_wedge_draw.py` | holder work | `predates_landing_carrying_some` | `b3aa159dd` |
| `tests/tools/test_refresh_to_head.py` | REPLACEMENT | — | `777c4adb8` 17:10 |
| `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` | REPLACEMENT | — | `89e94ec5a` 16:30 |

The silence had already propagated past the tool. **The delivery lane's own PATH CHECK reads this
grade**, and the item that produced this turn was handed `tools/refresh_to_head.py — [dirty]
differs from HEAD and reverts no landing` about a copy whose own clock calls it the older draft.
A session acts on that line before it reads any code.

### The one route by which the clock DID reach a reader, and why it reached nobody

A clause appended only `if base_wins` — *"`--base-wins` DOES NOT REACH A COPY WITH A LANDABLE HUNK,
however stale the clock says it is"*. Available precisely to the operator who had already typed the
flag that proves they suspected it; absent for every automated caller and every default
invocation, which is all of them.

### The repair: a DISCLOSURE, not a re-grade

`_clock_disclosure(clock, base)` in `tools/refresh_to_head.py`, appended unconditionally to both
`SUPPLIES_NEW` returns (the Python branch and the JSON branch).

The grade is **left alone on purpose**. `--keep` genuinely has a selection on these copies, so they
are not REPLACEMENTs and `--base-wins` correctly does not reach them; re-grading would discard work
a door could have saved, which is the harm `REPLACEMENT` exists to avoid. The two controls answer
different questions — `SUPPLIES_NEW` is about SYMBOLS, the clock is about TIME — and both can be
true at once. The contradiction is real and belongs to the operator. What was wrong was that only
one of the two spoke.

Keyed to `rule.startswith(PREDATES)` — the **stem of the family**, not today's three members. A
fourth predates rule is disclosed the day it is written; against a tuple of three it would be
silently undisclosed and nothing would go red. All three members are live on the tree right now,
which is how the stem was chosen rather than assumed.

### The controls, and the mutations they were proven against

- `test_a_holder_work_grade_discloses_the_clock_that_disagrees_with_the_door_it_names` — two arms,
  `k.py`/`K_STALE_BUT_LANDABLE` (clock refuses) and `m.py`/`HOLDER_APPENDS` (clock has no
  complaint), asserted to be in the SAME state so the clock is the only variable.
- `test_the_disclosure_reaches_every_member_of_the_predates_family` — all three rules, plus the
  quiet-clock arm.

Three mutations run, each caught by the leg written for it:

| mutation | fires |
|---|---|
| drop `_clock_disclosure(clock, base)` from the `SUPPLIES_NEW` return | disclosure test |
| narrow `startswith(PREDATES)` to `== PREDATES` | family test |
| return the clause unconditionally | **both** |

The third is the one worth recording. Written first as `assert "predates" not in fresh.reason`,
the anti-tautology arm **passed** the unconditional mutation — the clause renders as *"the verdict
on this copy is [no complaint]"*, which contains no such word — and a sibling test caught it
instead. That is *a mutation caught by a different leg than the one written for it*, the flattering
reading. The arm is now keyed to `_DISCLOSURE_MARK`, the clause's own signature, and fires itself.

---

## The four-path decision the item asked for

The item asked me to decide the rework the classifiers refuse to touch. **Decided: the base wins on
all four. None of them is a landing.**

The evidence is the clock, not a preference. All four copies carry the same 15:02:31 stash-pop
mtime; origin's last commit to each of their paths is 16:30, 17:10, 17:10 and 18:24 — every one
later. `777c4adb8` is rule 1b's own commit, which restructured the imports those hunks sit in, so
the hunks are the older draft of a restructure that is already in.

- `tools/refresh_to_head.py`, `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_...md` —
  graded holder work, and the prescribed `isolate_hunks --keep` + `--content` door **must not be
  taken**: it lands 15:02 bytes over a 17:10/18:24 commit. `--base-wins` does not reach them (a
  landable hunk exists), which is correct and is exactly why the disclosure above had to be built:
  the tool cannot enact this decision, so it must at minimum SAY it.
- `tests/tools/test_refresh_to_head.py`, `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_...md`
  — REPLACEMENT, no landable hunk. The door is
  `python3 -m tools.refresh_to_head --base-wins --write --slug <name> <path>`, run **on the shared
  tree**, which preserves the bytes to `refs/preserved/*` and verifies the recovery route before
  writing.

**Not enacted this turn, and that is a limit and not an oversight:** those are the SHARED tree's
working copies, and this turn ran in an isolated worktree that cannot reach them. Recorded as the
decision with its evidence and its named door, for a session holding the shared tree.

*This turn's own landing on `tools/refresh_to_head.py` does not go through that door and does not
revert `777c4adb8`: the worktree copy is HEAD's bytes, and the change is an addition on top.*

---

## Dispositions

- `judge-the-advance-with-the-bases-rules-not-the-behind-checkouts` — **this item.** The draw's
  note that it "is ALREADY HELD under this very id" is the draw citing its own claim row, the
  known shape. Carried on.
- `the-refresh-door-probes-against-the-judgement-base-not-the-parent` — **genuinely different work
  on the same file.** That claim is about `_probe` reading the judgement base rather than the
  parent; this is about `SUPPLIES_NEW` discarding the clock. Different function, different defect.
  Deliberately did not touch `_probe`. Not released, not folded.

## What is left

1. Enact the four-path decision on the shared tree (needs a session holding it).
2. The origin-rulebook seam: feasibility established, currently measuring zero divergence on the
   blocking set. Re-measure before building — the P3 differential above is ~20 lines and reusable.
3. The shared tree is 3 ahead and cannot fast-forward at all. That is a separate wedge with a
   separate cause and it is the one actually holding the checkout.
