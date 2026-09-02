# [SEAT FINDING] The publish gate judged a HEAD 31 commits behind origin, and nothing in the wedge machinery reads origin

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, from a reproduction and a node-name diff, not from reading.

**Subject:** `background/process_run_complete.py` (`_head_checkout`, `run_fast_tests`),
`background/supervisor.py` wedge alarm, the wedge doorbell

---

## What happened

The publish gate was red for ~11h on two nodes in `tests/tools/test_head_green_census.py`. The
episode counter reached 17 consecutive failures. The drawn doorbell described a stack of defects to
find and fix.

There was no defect to find. **The repair was already on `origin/main`** — commit `66c4e780b`,
*"salvage the census lane's orphaned overlay check, which its own working copy would have
reverted"*, which had committed the very `_install_fake_register` helper that closes both red
nodes. Local `main` was **31 commits behind** `origin/main` when this tick began.

The gate builds its subject with `git archive HEAD` (director ruling
PUBLISH_GATE_SUBJECT_2026-08-09 — *"publishing tests committed truth only; the working tree belongs
to the lanes"*). `HEAD` is **local** main. So for eleven hours the gate re-measured a commit that
the rest of the machine had already moved past, and reported its staleness as a code red.

## The measurement

    $ git rev-list --left-right --count HEAD...origin/main
    0    31

    $ comm -23 <ours-test-names> <origin-test-names>
    (empty)

Every test node in the local lane's work already existed on origin. The `_install_fake_register`
helper is byte-identical on both sides (md5 `ccf44de9f73a9e42e885ffeeb5bf0c95`). Origin was a
strict superset in both changed files.

## Why nothing noticed

The ruling that made the gate's subject `HEAD` was right, and is not what failed. What failed is
that **no part of the wedge machinery asks whether `HEAD` is current.** The gate, the episode
counter, the blocking-tests file, the alarm and the doorbell all reason about `HEAD` as though it
were the machine's state. None of them fetches, and none compares against `origin/main`.

A fork is therefore indistinguishable from a red — and it degrades in exactly the wrong direction:
the longer the fork lasts, the more confident the alarm becomes (17 consecutive failures reads as
a deep defect, and is in fact 17 measurements of the same stale commit).

## What it cost

A tick spent diagnosing, reproducing and re-landing a repair that already existed. Local commit
`5260c6859` duplicated origin's work and added nothing — filed here rather than hidden, because it
is the second time this class has been recorded (see
`feedback: an isolated worktree can duplicate a whole item another lane lands concurrently`, and
`the drawn repair can already be sitting finished and unlanded in the shared tree`). Both prior
records say *fetch origin before starting AND before landing*. This tick did run
`HEAD...origin/main` at the start, saw `0 31`, and still went on to diagnose the red as a code
defect — because knowing the counts is not the same as asking **"is the thing I am about to build
already there?"** The cheap question that would have ended the tick in two minutes is a diff of
test node names between the two sides, and it was only run at merge time.

## The repair this asks for

Smallest mechanism that can fail: **the wedge alarm must state the fork distance beside the red.**
A gate failure at a `HEAD` that is behind `origin/main` is not a code red and must not be counted
into the episode — it is a fork, and the action is to merge, not to diagnose. Keyed to the
property, not to today's answer: the check is `HEAD` vs `origin/main`, not a pinned sha.

This is a one-leg check on a path that already exists, and it deletes the whole class: no episode
of this shape can survive the alarm naming its own distance from origin.

## Second, separate defect found on the way

The failure rows are stamped with a `git_hash` parsed from the `run_complete_*.md` **marker** (the
sha when the *simulation run* finished), not the sha of the checkout the gate actually judged. Of
this episode's four rows, three were recorded after `83c63ac58` landed at 18:30 and all four are
labelled `6c44b2109`. The doorbell read that as *"HEAD has moved past every recorded failure, so a
fix may already have landed"* — accidentally true, for entirely the wrong reason.

`_head_checkout()` already computes `head_sha = _head_sha()` to build the subject and simply does
not yield it. This is the same class as
`test_the_recorded_head_is_the_commit_the_SUITE_RAN_not_the_one_HEAD_reached_afterwards`, which was
fixed for the census's own row and left live in the publisher's.
