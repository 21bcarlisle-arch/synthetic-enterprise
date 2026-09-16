**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-ledger-guard-ratchet-repair-and-let-the-bound-fall-to-what-it-reaches`) · **Class:** controls_that_cannot_fail

**Discharged:** `tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded`, `tools/pre_commit_test_gate.py` — all nine entrypoints now call refuse_if_foreign as the first act of their \_\_main\_\_ block, the UNIVERSAL\_MODULES allowlist is still empty, and the falsifier is on the CONTROL\_TESTS list so it runs on every code commit instead of only when someone edits it.

# FINDING — a second whole-`background/` ratchet is silently red at HEAD, and nine daemon entrypoints are unguarded

Found by the census run to discharge item 3 of
`SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET_HAS_BEEN_RED_AT_HEAD_FOR_TWO_WEEKS...` — "why
nothing selected this test for two weeks", whose closing claim was *"the same silence would cover
any other ratchet in `tests/background/`"*.

**That claim was a claim to check, not a finding to build on. It is true, and here is the instance.**

```
tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded
AssertionError: background/*.py entrypoints with no seat guard as the FIRST act of their
__main__ block: ['commit_narrative.py', 'doomed_at_teardown.py', 'head_red_register.py',
'launch_liveness.py', 'launch_long_job.py', 'long_job.py', 'origin_reconcile.py',
'publish_standing_red.py', 'weekly_rhythm.py']
```

## It is red at HEAD, not in my tree

Graded in a clean detached worktree at `a06109741` with nothing of this lane's in it — the same
discipline the ledger-guard repair had to be re-done under after its first draft censused a dirty
shared tree. `1 failed, 22 passed`. Identical failure and identical nine names in the working tree
and in the clean extract, so this is not one lane's in-flight work being called drift.

## It is the same class, exactly

`_background_modules()` AST-walks **every** `background/*.py` looking for a `__main__` block with
no `refuse_if_foreign(...)` as its first act. Subject set = the whole package. Selection in
`tools/pre_commit_test_gate.py` is by filename **stem**, so the only commit that RUNS this test is
one touching `background/seat_guard_daemons.py` — or the test itself. Any of the nine modules could
have landed its unguarded entrypoint green, and nine of them did.

It is present in `docs/observability/head_red_observed.json` and **absent from
`head_red_baseline.json`** — unregistered in both directions, the identical signature to the
ledger-guard ratchet. That is not coincidence and it is the mechanism, stated in the sibling
finding and now confirmed twice: **a red that blocks nothing is never triaged into a baseline,
because nothing ever surfaces it to be triaged.**

> **CORRECTED 2026-09-10, beside the claim. The last sentence above is FALSE, and so is the
> reading of the evidence in the sentence before it.** It *was* surfaced: the nightly unscoped
> census named this exact test id as red on seven of seven journalled nights, recorded it with age
> (`runs_red: 9`, `first_seen: 2026-09-02`), rendered it into `HEAD_RED_REGISTER.md`, and the
> supervisor doorbell named that register in **3,421** log lines. Nothing was silent; it was
> published into an undifferentiated 139-name blob and read by nobody. Separately, the "present in
> `head_red_observed.json`" evidence was read from the **shared working tree** — at HEAD, where
> this finding graded its redness, that file holds only the 2026-09-02 wreck and does **not**
> contain this test id at all. Measurement and mechanism:
> `SEAT_FINDING_THE_FOURTEEN_DAY_RED_WAS_SURFACED_3421_TIMES_AND_THE_REGISTER_EVERY_CLEAN_WORKTREE_READS_IS_THE_830_ROW_WRECK_2026-09-10.md`.
> The nine unguarded entrypoints, and everything else this finding says, are unaffected.

## The self-referential bit worth not glossing

`head_red_register.py` — the module whose entire job is recording which tests are red at HEAD — is
itself one of the nine unguarded entrypoints, and its own red is one of the two this pair of
findings is about. The register cannot see itself, and nothing selected the test that would have
said so.

## Why BLOCKING

The seat guard is what stops a *foreign* daemon — another machine's session, a stale service unit —
running a `background/` entrypoint against this tree. Nine unguarded entrypoints include
`launch_long_job.py` and `long_job.py`, which are the sanctioned launcher and the thing it
launches, and `origin_reconcile.py`, which moves refs. This is not a bookkeeping discrepancy.

## Deliberately NOT fixed in this turn, and the reason is structural

Guarding nine entrypoints is a separate subject from test selection, and doing it inside a commit
about the selector would hide it — the same argument the sibling finding made for not fixing the
ledger writers inside the site-pipeline commit, which was right then and is right here.

**More importantly: `tests/background/test_seat_guard_daemons.py` was NOT added to `CONTROL_TESTS`
alongside its twin, precisely because it is red.** Adding a red test to a list that runs on every
code commit would wedge every lane in the tree — a strictly worse failure than the one being fixed,
and the exact move the ledger-guard finding warned against in its own terms ("if a lane needs this
green to land, that is a fact to state, not a reason to bank the drift"). The omission is written
into `CONTROL_TESTS` as a comment naming this document, so it is visible rather than a gap nobody
recorded.

## What is next

1. **Guard the nine entrypoints** with `refuse_if_foreign("<module>")`, or justify specific ones
   onto `UNIVERSAL_MODULES` with the argument beside the row. Let the red fall out of the work.
   Do not widen `UNIVERSAL_MODULES` to clear the count — that is this repo's "raise the bound"
   move wearing a different hat.
2. **Then add `tests/background/test_seat_guard_daemons.py` to `CONTROL_TESTS`**, in the same
   change, and delete the placeholder comment that names this document. The line is written and
   argued already; it is waiting on the green.
3. The wider census — **27 test files repo-wide** with a whole-tree subject and a stem-only
   selector — is reported in
   `SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS_AND_MY_BAND_SAID_TWENTY_2026-09-10.md`.
   That is a different and larger question than these two instances, and it is NOT answered by
   adding twenty-seven lines to an always-run list.

---

## RESULT 2026-09-10 — items 1 and 2 are done, and the selector hole is narrower than this document said

Premise re-measured before starting: `bea5c02f2` is an ancestor of `origin/main`, this worktree is
level with origin, and the red reproduced with the identical nine names. Not spent.

**Item 1.** All nine carry `refuse_if_foreign("<stem>")` as the first act of their `__main__`
block, using the try/except import idiom the other guarded daemons use — chosen because both launch
forms are live for these modules, and both were exercised. **`UNIVERSAL_MODULES` is unchanged and
still empty.** No module was argued onto it: the finding's own warning against widening the
allowlist to clear the count was the right one, and none of the nine had a case. Their being
resident-seat machinery is exactly why they need the guard, not an exemption from it.

**Item 2.** `tests/background/test_seat_guard_daemons.py` is on `CONTROL_TESTS`; the placeholder
comment naming this document is gone, replaced by the entry and its argument.

### The green is not the evidence — the AST lock proves the LINE, not the GUARD

The structural lock is a source walk. It goes green on a `refuse_if_foreign` call that is never
reached, and it would go equally green on nine daemons that now refuse *everything* — the trap
CLAUDE.md names ("a guard that refuses everything passes all of them"). So both directions were run
as real subprocesses, per R15:

* **Foreign** (tmp HOME, no marker, no `SE_SEAT`): all nine, in **both** launch forms
  (`python3 background/x.py` and `python3 -m background.x`) — 18 runs, every one `rc=0`, stdout
  empty, stderr exactly `seat-guard: foreign, <stem> not starting`. Empty stdout is the load-bearing
  part: it proves nothing before the guard produced output, i.e. the guard is genuinely first and no
  import-time work precedes it. `git status --porcelain` byte-identical before and after.
* **Resident** (tmp HOME *with* the marker, no `SE_SEAT` override, so the production discriminator
  is what is under test): eight reached their own argparse and printed `usage: <stem>.py`, proving
  pass-through into their own code without doing any real work. `long_job.py` has no argparse; its
  `main()` is `print(render())` and is read-only, so it was run for real — it printed its job table
  and left the tree unchanged.

### Sharper than this document claimed, and measured rather than asserted

This finding said the only commit that runs the test is one touching `background/seat_guard_daemons.py`
"— or the test itself". There is no such module, so the second half was the whole of it.
`select_targets` was called directly:

| staged path | targets | selects this test |
|---|---|---|
| `background/_seat.py` | 17 | no |
| `background/supervisor.py` | 19 | no |
| `background/commit_narrative.py` | 17 | no |
| `background/origin_reconcile.py` | 17 | no |
| `background/head_red_register.py` | 17 | no |
| `background/launch_long_job.py` | 18 | no |
| `background/long_job.py` | 17 | no |
| `.claude/hooks/_seat.py` | 17 | no |
| `tests/background/test_seat_guard_daemons.py` | 18 | **yes** |

Subject set = every `background/*.py`; selector set = **exactly one path, the control itself**.
That is strictly worse than the ledger-writer ratchet, which at least fired when
`background/live_ledger_guard.py` was touched. Note the two rows that matter most: neither
`background/_seat.py` nor `.claude/hooks/_seat.py` — the adapter and the actual discriminator —
selects it. And a new daemon arrives as a *new* `background/*.py`, which is precisely the commit
that selects nothing. Nine modules landed unguarded through that hole; the tenth would have too.

Cost of the entry, measured on this machine over three runs: **1.64 / 1.67 / 1.70s** for all 23
tests. It is not free — the file starts real daemon subprocesses to prove inertness — but it is
0.28% of the 600s budget the lint entry cites, and it is cheap because the guard works: a foreign
daemon dies in milliseconds. If that number ever climbs, the guard has broken.

### What is still open

Item 3 is untouched and stays open: the repo-wide census of **27** whole-tree-subject / stem-only-selector
test files, reported in
`SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS_AND_MY_BAND_SAID_TWENTY_2026-09-10.md`.
Two instances have now been closed one at a time, which is evidence the class is real and *not* a
reason to add twenty-five more lines to an always-run list. The general question — what selects a
control whose subject is a whole package — is the successor, and it is not answered here.
