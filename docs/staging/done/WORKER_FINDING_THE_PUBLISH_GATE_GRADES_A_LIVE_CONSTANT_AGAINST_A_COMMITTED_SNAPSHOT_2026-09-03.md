**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** PW3_suite_duration_watch

# The publish gate graded a live constant against a committed snapshot, and labelled the run with the wrong commit

**Filed:** 2026-09-03, worker tick, during the RUNG-1 publish-gate wedge (4 consecutive failures).
The wedge itself is fixed in this commit; the second half below is not.
**Class:** `measurements_that_mirror` — two figures compared as one quantity when they count
different populations.

---

## What was red

One test, across four gate runs:

    tests/background/test_suite_duration_watch.py::test_the_cadence_is_read_from_a_measurement_not_an_aspiration

It failed on its LOWER bound, by 4.5 seconds:

    assert 1500 >= 3009.0 * 0.5      # 1500 >= 1504.5   -> False

## Why, and it is not arithmetic

`measure_publish_cadence_seconds()` read `PROJECT_DIR/docs/staging{,/done}`, and `PROJECT_DIR` is
the tree the module was IMPORTED from. The publish gate imports it from a `git archive HEAD`
throwaway checkout (`process_run_complete._head_checkout`, director ruling
DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09). In that tree `docs/staging/done/` holds only the
markers that happen to be **committed**.

Measured 2026-09-03, both trees at the same HEAD `62ac7010d`:

| subject | markers | newest marker | median inter-arrival | admissible band for the constant |
|---|---|---|---|---|
| working tree | 1,470 | 21:28:50Z | 1,685.5s | [842.8, 1685.5] — 1500 **in band** |
| gate's HEAD checkout | 1,305 | 17:55:42Z (3.5h stale) | 3,009.0s | [1504.5, 3009.0] — 1500 **out, by 4.5s** |

`PUBLISH_CADENCE_SECONDS` was re-measured on 2026-08-26 **from the working tree** (median 1,526s,
rounded down to 1500). So the constant was calibrated on one series and graded against a different
one. Neither number is wrong; their comparison was never a quantity. This is the project's
recurring shape — *"before dividing two numbers, say out loud what each one counts"* — arriving
through the subject rather than through the arithmetic.

Note the two series differ in a way that is not merely lag: the working tree's recent gaps are the
**wedge's own fast retries** (~800s), so the live median is depressed by the very outage the
control was firing about. The committed snapshot is the pre-wedge world. A control whose reading
is moved by the incident it reports on is worth stating plainly.

## The repair (landed with this finding)

`cadence_measurement_subject()` names the subject and returns `(roots, reason)`, exactly one
non-None. Where git can answer, a linked worktree resolves to the **main** worktree — the
`process_run_complete._machine_data_dir()` doctrine ("the MAIN worktree, never the importing
tree") applied to the one data set that helper does not cover. Where git cannot answer at all, the
tree is provably a throwaway archive checkout that cannot observe the machine, and the answer is a
**refusal carrying its reason**, never a confident number off a stale snapshot.

Keyed to the property, not to today's answer: no constant moved. Re-keying `1500` to something in
`[1505, 1685.5]` would have cleared the wedge tonight and re-armed it the moment either series
drifted — the exact defect this test's own docstring records being fixed once already
(2026-08-26, "a control that goes stale the moment its subject changes").

R15, mutation-proven: restoring the `PROJECT_DIR` fall-back kills BOTH
`test_a_tree_that_cannot_see_the_machine_refuses_to_measure_a_cadence` and the original cadence
test — i.e. the mutation reproduces the wedge exactly. Verified in a real `git archive HEAD`
checkout, not only in the working tree.

### The first fix caught one throwaway shape of two, and the second one refused it

Recorded because it is the more useful half of this finding. The first version of the guard keyed
on **"is this tree a git repository"**. That is true of `process_run_complete`'s subject (`git
archive HEAD`, no repo) and FALSE of `tools/surgical_land`'s, which extracts and then runs `git
init` (`_make_standalone_repo`, so tests asking git a question get an answer rather than `fatal:
not a git repository`). So the guard cleared the publish gate and sailed straight into the landing
gate, which refused this very commit with the identical `1500 >= 3009.0 * 0.5`.

Two gates, two throwaway-tree shapes, one guard that had only met the first. The separating
property is not repo-ness but **ownership**: a throwaway checkout is standalone and has no
`origin`; the live tree and every linked worktree share this repository's config and do. Verified
across all four shapes on 2026-09-03 — main tree and both `/var/tmp/se-*` worktrees carry `origin`
and resolve to `/home/rich/synthetic-enterprise`; the `git init` checkout carries none; the `git
archive` extract is not a repo. Each shape now refuses with its own named reason, and
`test_a_standalone_gate_checkout_refuses_to_measure_a_cadence` is mutation-proven against the
`remote.origin.url` branch specifically.

The generalisable bit: **when a guard is narrowed to one subject class, count every class that
reaches it before believing it is done.** The landing gate and the publish gate build their
subjects differently, and nothing in either module says so.

**Cost of the control going quiet in the gate, stated rather than buried:** this test now SKIPS
inside the publish gate, so the gate no longer defends the constant. That is honest — the gate's
subject genuinely cannot observe the machine's publish cadence — but it is a real reduction in
where the control runs. It still runs in the working tree, which is where the constant is edited
and where every lane's suite runs. If that turns out to be too little, the fix is to give the gate
a marker series it CAN see, not to restore a number taken off a snapshot.

---

## STILL OPEN — the second half, and it is the one that misled the diagnosis

**`git_hash` on every publish-gate record names the MARKER's commit, not the commit under test.**

`parse_marker()` reads a `Git:` line out of the `run_complete_*.md` marker; that value is passed
through `run_fast_tests(git_hash)` as a **label only** and is never re-derived. The subject is
whatever `_head_checkout()` produces — a checkout of **current HEAD**.

Measured 2026-09-03: marker `run_complete_20260903T201326Z.md` carries `Git: 51ffdc454`; HEAD was
`62ac7010d`; the gate tested `62ac7010d` and recorded:

    {"timestamp": "2026-09-03T21:39:01Z", "git_hash": "51ffdc454", ..., "outcome": "fail"}

`docs/observability/.last_gate_blocking_tests.json` inherits the same wrong label via
`_write_blocking_tests`.

**Why this costs real time.** The wedge doorbell reasoned directly off it and told this tick:

> the report-only census enumerated the WHOLE red set at `51ffdc454`, **NOT at HEAD** `62ac7010d`
> … run `git log --oneline 51ffdc454..62ac7010d` — **a fix may already have landed, so re-check
> each before repairing it**

Every clause of that is false, and it sends the reader to diff three commits that cannot be
relevant. The census DID run at HEAD; only its label was stale. This is the *"a refusal that cites
an artefact has made a checkable claim and nothing opens it"* shape: the count was right and the
inference off it was rotten.

**Recommended repair** (not done in this bounded tick — it touches the publish path's records and
wants its own R15 pass): stamp the record from the checkout that was actually tested — `git
rev-parse HEAD` at `_head_checkout()` time — and keep the marker's hash, if it is worth keeping at
all, in a separate field that says what it is (`marker_git_hash`). A record whose subject and
label disagree is a control that cannot be read correctly, and the doorbell above is the proof
that it was not.
