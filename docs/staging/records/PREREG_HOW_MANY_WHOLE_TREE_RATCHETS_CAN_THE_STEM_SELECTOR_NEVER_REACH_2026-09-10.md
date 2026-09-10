**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-ledger-guard-ratchet-repair-and-let-the-bound-fall-to-what-it-reaches`) · **Class:** controls_that_cannot_fail

# PREREG — how many whole-tree ratchets can the stem selector never reach?

Written BEFORE the census is run. Item 3 of
`SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET_HAS_BEEN_RED_AT_HEAD_FOR_TWO_WEEKS...` asks why
nothing selected `tests/background/test_live_ledger_guard.py` for fourteen days. The mechanism is
now established and is NOT the question below:

`tools/pre_commit_test_gate.py` selects by **filename stem** — a staged `background/X.py` selects
`tests/**/test_X.py` and `tests/**/test_X_*.py` — plus a fixed `CONTROL_TESTS` list that runs
whenever any code file is staged. `test_live_ledger_guard.py` is **not** in `CONTROL_TESTS`, so its
only selector is `background/live_ledger_guard.py` itself. Its SUBJECT is every `background/*.py`
that writes under `docs/observability/`. Subject set = a directory; selector set = one stem. Twelve
writers landed in modules whose stems reach no part of this test, so nothing ran it and the red at
HEAD blocked nothing.

That much is read off the code and is not a measurement.

## The question whose answer I do not know

**How many OTHER tests have the same shape** — a population computed by globbing a source
directory, a bound asserted over it, and no `CONTROL_TESTS` membership to make it run when that
directory changes?

The finding claims "the same silence would cover any other ratchet in `tests/background/`". That is
a claim to check, not a finding to build on.

## Predicate I will count (fixed now, so it cannot be tuned to the answer)

A test file counts as an UNREACHABLE WHOLE-TREE RATCHET when all three hold:

1. It globs or walks a NON-`tests/` source directory to build its population (an AST-visible
   `glob`/`rglob`/`iterdir`/`os.walk` whose receiver or literal argument names a source tree).
2. It asserts a comparison against an integer literal over a length or a count derived from that
   population (the ratchet bound).
3. It is absent from `CONTROL_TESTS` in `tools/pre_commit_test_gate.py`.

Leg 3 is the selection defect; legs 1–2 are what make the defect silent rather than merely narrow.

## Predictions

- **In `tests/background/` alone: 3 (band 1–6)**, `test_live_ledger_guard.py` among them.
- **Across all of `tests/`: 11 (band 5–20)**.
- **`CONTROL_TESTS` already contains at least three tests of exactly this shape** — the list's own
  comments say so at length for `test_static_quality_ratchet.py`, `test_epistemic_wall_ratchet.py`
  and `test_segment_case_guard.py`. So the class is RECOGNISED and has been fixed ten times
  one-instance-at-a-time. I predict the fix pattern already exists and this is not a new mechanism
  to invent. **If that holds, adding a register/meta-control would be building a thing that watches
  the work; the honest move is to add the missed instances to the list and say how many were
  missed.**
- **Cost:** I predict the whole `tests/background/test_live_ledger_guard.py` file runs in **under
  3 seconds** (15 tests, 1.6s measured in this worktree), so `CONTROL_TESTS` membership is
  affordable. If a found instance costs more than ~10s I will say so rather than add it silently.

## What would refute the framing

If the census returns **0 or 1** outside `test_live_ledger_guard.py`, the finding's "not specific
to this file" claim is wrong and this is an INSTANCE, not a class — I will say so plainly and fix
the instance only.

If it returns **more than 20**, adding them all to an always-run list is not affordable and the
answer is a different instrument, not a longer list. I will report the count and the cost rather
than pick the flattering half.

## Recorded before the answer

No part of the census has been run at the time of writing. The only number already in hand is the
1.6s local runtime of the one test file, which is stated above as a measurement, not a prediction.
