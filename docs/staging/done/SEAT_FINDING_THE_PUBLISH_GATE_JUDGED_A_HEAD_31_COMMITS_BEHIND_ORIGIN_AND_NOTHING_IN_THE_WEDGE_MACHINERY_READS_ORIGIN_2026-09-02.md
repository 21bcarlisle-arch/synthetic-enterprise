# [SEAT FINDING] The publish gate judged a HEAD 31 commits behind origin, and the behind-origin refusal sits downstream of the gate that returns before it

*(Filename and the second half of the original title — "nothing in the wedge machinery reads
origin" — are superseded by the CORRECTION below. The behind-origin check exists; it is
unreachable in this case. Filename kept because the class register cites it.)*

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

> **CORRECTION, made an hour after filing and kept beside the claim it replaces.** The title and
> this section originally said *"no part of the wedge machinery asks whether `HEAD` is current"*.
> **That is false, and the truth is worse.** The check exists —
> `process_run_complete.BEHIND_ORIGIN` / `_divergence_refusal()`, with real-git controls in
> `tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`, built
> on 2026-09-01 for this exact condition. I found it by reading the test selection of the publish
> cycle that was running while I filed. The filename is left unchanged because the class register
> now cites it.

The ruling that made the gate's subject `HEAD` was right, and is not what failed. Nor is the
behind-origin refusal missing. **What failed is their ORDER.**

    line 6471   tests_ok, timed_out = run_fast_tests(git_hash)     # the gate: archives local HEAD
    line 6472   if not tests_ok:  ... return _gate_refusal(...)    # EARLY RETURN -> test_regression
    ...
    line 4478   _behind = _divergence_refusal()                    # in the COMMIT path only

`_divergence_refusal()` is only reached once the gate is **green**. So when the tree is behind
origin *and* the stale `HEAD` is red — which is precisely the wedge this control was written for —
the gate returns first and the behind-origin refusal can never fire. The control is structurally
unreachable in its own case.

This is the R15 shape the project already names: a control that cannot fail in the situation it
exists for. It is invisible because it looks present, is tested, and its tests pass — they
exercise the commit path, where it does run.

The comment at line 4475 says *"two fail-closed refusals in a row cannot mask each other into
publishing, so the order is free to be chosen."* True of the **publish verdict**, and it is why
nothing is being published wrongly. But the order is not free of **classification**: whichever
refusal fires first is the one that names the cause, and the gate firing first files a fork as a
`test_regression`. The episode counter then reads 17 consecutive failures as depth, when it is 17
measurements of one superseded commit.

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

Smaller than the version I first wrote, because the mechanism is already built and merely sits
downstream of the thing that returns before it. **Move the existing `_divergence_refusal()` read
in front of `run_fast_tests()`**, and when origin is ahead, refuse with `BEHIND_ORIGIN` instead of
running the gate at all.

Three properties it must have, none keyed to today's answer:

1. A gate failure at a `HEAD` behind `origin/main` is classified `behind_origin`, **never**
   `test_regression`. Different cause, different remedy: merge, not diagnose.
2. It must not count into the episode. The counter is meant to measure a deepening defect, and
   17 measurements of one superseded commit is not depth.
3. The check is `HEAD` vs `origin/main`, not a pinned sha, so it stays true after this fork is
   reconciled — the same discipline the existing behind-origin controls already chose.

**The control this needs is one the existing test file cannot provide.** Its cases all run the
commit path, where the refusal already fires. The missing case is *origin ahead AND the gate red*,
asserting the recorded cause is `behind_origin` — which fails today, and is the mutation that
proves the reordering did something.

Not fixed in this tick: this is a change to the publish path's ordering while a publish cycle is
live in the tree, and the drawn work (unwedge, merge, push) is complete. It should be drawn next,
and it is small.

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
