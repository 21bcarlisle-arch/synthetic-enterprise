**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `decide-what-selects-a-control-whose-subject-is-a-whole-package`) · **Class:** controls_that_cannot_fail

# RESULT — the strict eighteen are all green, and the list is now the whole instrument

Takes items **0** and **1** of the "what is next" list in
`SEAT_RESULT_SELECTING_A_CONTROL_BY_WHAT_IT_SCANS_IS_THE_ALWAYS_RUN_LIST_SPELLED_DIFFERENTLY_2026-09-10.md`.
Pre-registered before any of it ran:
`docs/staging/records/PREREG_HOW_MANY_OF_THE_STRICT_EIGHTEEN_ARE_GREEN_IN_A_GATE_SHAPED_EXTRACT_2026-09-10.md`.

The selector question is **closed**. Door 3 was refuted on measurement by the previous turn; this
turn does not re-open it, it pays for the answer. **The list is the instrument, and the list now
covers the whole affordable unit** — the eighteen strict-dataflow census members are on
`CONTROL_TESTS`, so `--strict-dataflow` returns **0** at this commit and a nineteenth instance
appears as a 1 rather than as silence.

## Item 0's blocker was discharged by the tree, not by me

The previous turn backed out its wiring because the tree was three commits behind origin and
origin's `fcbf92b9b` carried an atomic pair (the ninth `CONTROL_TESTS` entry *and* the nine
`refuse_if_foreign` guards that make it green). In this worktree
`git rev-list --count HEAD..origin/main` is **0**, and the census independently confirms the pair
arrived whole: `already on CONTROL_TESTS` reads **6** where the previous turn measured 5.

## Predictions, graded beside the result

| quantity | predicted (band) | measured | verdict |
|---|---|---|---|
| of the 18, green in a gate-shaped clean extract | 15 (11–18) | **18** | held, at the band's upper edge |
| of the reds, a GENUINE drift rather than machine state | 1 (0–3) | **0** | held, at the band's lower edge |
| wall-clock of the green subset, one invocation | 38s (15–70s) | **30.5s / 30.0s** | held |

Two of three landed on a band edge, and **both point estimates were wrong in the same direction as
the previous seat's**: I under-estimated how clean this tree is, having spent the turn reading about
two controls that had rotted. The class is real and its current damage is zero.

**Q2 = 0 is the answer that weakens my own change, and it is reported first because of that.**
Eighteen controls that no commit can select have, between them, drifted not at all. The two
demonstrated drifts (`test_live_ledger_guard.py`, 74 → 86 writers over fourteen days;
`test_seat_guard_daemons.py`, nine entrypoints over nine) may therefore be the whole of the damage
rather than a sample of it. What this batch buys is **prospective** — the commit that adds the
nineteenth unguarded writer now runs the control that counts them — and it is honest to say that it
buys no repair of anything currently broken. That was written into the prereg before the answer so
it could not be dropped afterwards.

## What it costs, measured one variable at a time

| run | tests | pytest | wall |
|---|---|---|---|
| `CONTROL_TESTS` as it stood | 423 | **64.6s** | 66.1s |
| `CONTROL_TESTS` + the eighteen | 815 | **96.6s** | 99.5s |
| **marginal** | +392 | **+32.0s** | +33.4s |

The marginal is within a rounding of the batch measured alone (30.5s), so there is essentially no
fixture sharing to be had — stated because "it will be cheaper in the batch" is the comfortable
assumption and it is false here.

**+32.0s is +49% on the `CONTROL_TESTS` run itself**, and 5.3% of the 600s budget the standing
finding tracks. That is the largest single addition this list has ever taken, and it is put in
those terms rather than as "5.3%" because the percentage is the flattering framing of the two.

The prereg fixed the threshold before the answer: *green subset above 70s → add a subset and say
what was dropped.* It came in at 30.5s, so all eighteen go in, and I am not re-cutting the
threshold now that I can see a number I dislike.

**Where a future prune should look, so that it can be argued from a number.** Six of the eighteen
carry 32.5s of the 37.1s the files cost run singly — **88% of the cost on 88 of the 392 tests**.
The other twelve are **304 tests for 4.6s**. Cost here does not track test count at all, so a prune
by "how many tests does it run" would take the wrong twelve. Take from the six.

*(Corrected beside the claim: I first wrote 273 for that figure, which was an arithmetic slip —
the twelve cheap files are 304 tests. The commit that landed the gate comment carries the wrong
number and the commit beside this document corrects it, rather than the record being quietly
revised.)*

## Graded in a gate-shaped extract, and that was not fastidiousness

`tests/test_isolation_guards.py` is **red in the shared tree and green in a clean one** — other
lanes' test processes leave live-ledger fingerprints behind. Had this been graded where the previous
turn had to grade it, that file would have been withheld on evidence that is not about the file.

The extract is built the way `surgical_land` builds the one it actually gates in — `git archive` →
`_make_standalone_repo` (real index, HEAD at the parent, read-only alternates) →
`_overlay_untracked_data` — because an index-keyed control fails closed where there is no index and
a data-reading one fails on an absent cache, and both read as a red that is really a wrong harness.
Eighteen files graded singly, then the batch twice.

## Two things found on the way, both worth more than the batch

**1. A path in a prose comment is NOT a reachability edge, and citing the census does not wire it.**
Item 0 asks for the census to be "cited from `pre_commit_test_gate.py`". I wrote the citation, then
checked whether it discharged the orphan row — it does not, in either spelling
(`python3 -m tools.whole_tree_subject_census` or `tools/whole_tree_subject_census.py`). That is
**correct behaviour and recent**: `capability_index._path_references` stopped treating comment and
docstring paths as edges on **2026-09-08**, because 307 such edges were the sole reachability of 34
modules and an editorial reword of one sentence could refuse every lane in the tree. So the citation
is for the reader, which is what item 0 actually asked for, and
`docs/design/orphan_baseline.json`'s row stands unchanged — the census is still deliberately
dormant, and shrinking that floor would rest on reachability that is not real.

**Worth flagging to the next session as a habit that is now wrong:** "cite the module to wire the
orphan" was true here until two days ago and is the sort of thing a seat carries forward without
re-checking. I did, and it cost one measurement to find out.

**2. `head_red_observed.json` already held the answer to Q2, and no isolated worktree can read it.**
Zero of the eighteen are named in the latest nightly run — so the nightly census had already
established that none had drifted, and my three minutes of grading re-derived a published fact.
Except that it did not, **because in this worktree that file is the 2026-09-02 ENOSPC wreck**: 830
red, 760 of them `OSError`, and it names **67 test ids belonging to the strict eighteen**. Reading
the instrument here would have returned exactly the wrong answer, with confidence.

That is a **second live instance** of the defect filed as BLOCKING in
`SEAT_FINDING_THE_FOURTEEN_DAY_RED_WAS_SURFACED_3421_TIMES_AND_THE_REGISTER_EVERY_CLEAN_WORKTREE_READS_IS_THE_830_ROW_WRECK_2026-09-10.md`
— the nightly census writes into the shared working tree and nothing commits it — and it is the
first instance where the cost is *a wrong answer to a live question* rather than a stale register
nobody read. It is not fixed here: it belongs to that finding, and fixing it in passing would put
the repair somewhere nobody would look for it.

## What landed

- `tools/pre_commit_test_gate.py` — the eighteen, under **one** comment rather than eighteen. The
  nine entries above it each argue the same class from first principles; a tenth restatement would
  be reciting a rule, and the census is what makes one statement sufficient. The comment carries
  the argument once, the re-derivation command, the grading environment, the cost, and the
  concentration.
- `tests/tools/test_pre_commit_test_gate_censused_batch.py` — controls keyed to the **property**,
  with the poison round run before the green was believed.

## What is next

1. **The nineteenth.** Nothing yet refuses a new whole-directory-subject test that is not listed.
   The previous turn declined a meta-control on CLAUDE.md's *"a control that only guards your own
   controls is usually not worth having"*, and while the pool was 18-and-growing that was right —
   it could not fix what was already there. **The pool is now 0, which changes the argument**: a
   guard that runs the census predicate over the STAGED test files only is O(staged), costs
   milliseconds, and refuses at the commit that creates the defect rather than watching for it
   afterwards. That is the shape CLAUDE.md prefers, not the shape it warns about. It is the next
   increment and it is deliberately not taken here, because the batch is worth landing on its own.
2. **The 91 loose members are not owed a line each** — unchanged from the previous turn, and the
   +49% measured above is the reason it is not a close call.
3. `head_red_observed.json` and `HEAD_RED_REGISTER.md` reaching git, under the BLOCKING finding
   that owns them. Instance 2 above is evidence for it, not a second finding.
