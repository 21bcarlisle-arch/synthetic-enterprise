**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: does a caller suite that REACHES `ops_repo` prove anything about it?

**Written 2026-09-06, delivery seat, isolated worktree at `da7336230`, claim id
`converged-battery-next-subject`. Every prediction below is fixed BEFORE the battery runs, and
this file lands in its own commit ahead of any result so the ordering is in the record and not in
a claim about the record.**

---

## Why this subject, and what the drawn direction got wrong about it

The direction named `background/ops_repo.py` as the next converged subject on the strength of the
screen's row: **3 first-party callers, no test importer at all.** That row is stale by one day.
`SEAT_FINDING_A_CONVERGED_HELPER_HAD_THREE_CALLERS_ZERO_TEST_IMPORTERS_AND_THE_REFUSAL_LEFT_BEHIND_AT_TWO_OF_THEM_2026-09-05.md`
examined it, found the refusal missing at the choke point, repaired it, and wrote the module's
first suite — `tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py`.

That does not retire the subject. It *sharpens* it, and into exactly the question the previous
subject could not answer.

`direction.py`'s fourth column was eight green cells that were never once at risk: the suite never
reached the module. The poison round exists because "the contract held" and "the suite never ran
the line" are the same green. **`ops_repo` is the mirror case.** All three caller suites import
their caller at module level, and each caller imports `ops_repo` at module level — confirmed
before writing this, by importing each suite module and checking `background.ops_repo` in
`sys.modules`: all three present, both chosen control suites clean. So the poison round is
predicted to redden all three.

If those three reaching suites then kill nothing, this is the first subject in the sweep where a
whole caller column is **REACHABLE AND UNPROVED** — the reading that the direction.py column was
mistaken for, established rather than assumed. That distinction is the entire reason the floor
runs first, and until now the sweep has only ever produced the other answer.

## The mechanism under test, stated before the measurement

Each caller suite patches `commit_and_push` **by name in the caller's namespace**
(`patch("background.ntfy_mirror.commit_and_push")` and its two siblings). So the import happens,
the module object is real, and the function body is never entered. My model says: import-level
reachability, zero behavioural coverage of `commit_and_push`.

`ops_tree_lock` is the exception and it is why this is worth running rather than asserting.
Nothing patches it — `ntfy_mirror.append_mirror_entry`, `director_input_log.append_entry` and
`backup_company_data.backup_once` all execute `with ops_tree_lock():` for real, against the real
`~/synthetic-enterprise-ops/.ops.lock`. The lock contracts (M7, M8) are therefore **executed** by
the caller suites. Executed is not observed: no caller suite contends for the lock, so I predict
both mutations still survive. That is a genuinely uncertain cell and the one that can refute my
model of "patched by name ⇒ proves nothing".

## The eight contracts and the predictions

Each is one edit to `background/ops_repo.py`, target asserted present exactly once by the engine.
`repair` is `tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py`, scored
as its own column and never folded into `survived_all` — the pre-registered population is the
three CALLER suites.

| id | the contract as the module states it | prediction: 3 caller suites | prediction: repair suite |
|---|---|---|---|
| M1 | the write REFUSES under a test process at all | all survive | DIES |
| M2 | the refusal is the FIRST statement — after the `git add` it has already staged a test's bytes in the real repo | all survive | DIES |
| M3 | the refusal carries its OWN TYPE, so a caller can tell "the harness stopped me" from "the write broke" | all survive | DIES |
| M4 | ONLY a nothing-to-commit failure is swallowed | all survive | DIES |
| M5 | a nonzero commit return code is inspected at all | all survive | DIES |
| M6 | the push actually happens | all survive | DIES |
| M7 | the lock is EXCLUSIVE — a shared lock admits two holders | all survive | DIES |
| M8 | the lock deadline is REACHABLE — an unbounded wait is not a timeout | all survive | DIES |

**Summary prediction, fixed now: `survived_all` is TRUE for all eight; `caught_by_own_suite` is
TRUE for all eight; `reaches_subject` is TRUE for all three caller suites and FALSE for both
controls; no suite grades the text.**

That is a uniform prediction and I am stating it as one rather than hedging it into
unfalsifiability. Every way it can be wrong is informative:

* **A caller suite kills anything** — most plausibly M7 or M8, the two the callers really execute
  — and "patched by name ⇒ proves nothing" is too strong as a general claim about this shape.
* **The repair suite misses one** — then a contract on a module repaired *yesterday*, with a suite
  written specifically as its repair, is standing on nothing, and the sweep's finding survives its
  own remedy.
* **A control suite reddens under the poison** — the floor is measuring the harness, and the whole
  reachability column is void including direction.py's, which used the same engine.

## What a result here cannot establish

Three suites is the whole caller population, so unlike `segment_vocabulary` (ten graded of 265
reaching) there is no sampling bound to declare. But the screen remains a proxy: it is blind to
callers reached by subprocess or dynamic dispatch. And a green repair column proves the eight
contracts I chose to write down, not the module.

`M8` mutates a blocking-acquire deadline. The 2026-09-05 finding records that this exact mutation
**hangs** rather than fails when the control is written the obvious way, and that the hang took
the mutation harness's restore step with it. The repair suite's lock leg now bounds the second
acquirer with a thread join, so it should be a named assertion in ~10s. If the run stalls, that
is the prediction failing, not the tool.

## Next subject, named now so it cannot be chosen after the answer

`tools/generate_company_data.py` — 4 first-party callers, and in `tests/` only as a string inside
a manifest. It is the last of the screen's three zero-importer modules.
