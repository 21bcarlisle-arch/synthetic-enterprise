**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# "That instrument has never reported" is not a reading of the world — the sixth cause's instrument is absent from the only tree that would run it

Claim id: `the-seventh-publish-cause-is-whatever-the-newly-named-refusal-now-shows`.
Class: `publish_gate_and_wedge`. Measured 2026-09-24 ~09:10Z from an isolated seat worktree at
`origin/main` (`8191fb188`), reading the SHARED tree `/home/rich/synthetic-enterprise` for state.

**Deliberately LATENT, not BLOCKING.** The blocking reading of this subject is already filed twice in
this lane — `SEAT_FINDING_THE_CHECKOUT_CANNOT_ADVANCE_BECAUSE_A_PRODUCERS_OUTPUT_IN_AN_AUTHORED_TREE_IS_INVISIBLE_TO_THE_GENERATED_ORACLE_2026-09-24.md`
and `SEAT_FINDING_THE_DECLARED_BOOT_STAMPER_HAS_STAMPED_NOTHING_SINCE_2026_09_04_SO_NO_DAEMONS_CODE_VERSION_IS_KNOWN_2026-09-24.md`.
A third blocker on the same mechanism would drain the lane no faster and would hide that this
document's main content is a REFUTATION and a CLEARED falsifier, not a new obstruction.

## The pre-registration this refutes, and it was written before the answer

The drawn item predicted, in its own words, that the state file would name one of two causes:

> cause will be `scoped_suite_red` (a real red at a graded sha) or `scoped_gate_unjudged` (the gate
> refused without judging) … That instrument has never reported. The series' causes are SERIAL, so a
> seventh should be expected rather than hoped against, and the first reading of the new instrument
> is where it will show.

**Both are refuted, and not by "not yet".** By construction: there is no tree in which that
instrument can run. The seventh cause is therefore not a refusal the instrument named — it is that
the instrument is not there to name one.

## The measurement

`4a030f9f5` (the sixth-cause repair) is an ancestor of `origin/main` — the premise holds, the work
landed. It is **not** an ancestor of the shared tree's HEAD (`7964c134c`).

```
deploy_restart.checkout_drift()   # shared tree, 2026-09-24 ~09:07Z
  {'behind': 3, 'ahead': 2, 'contains_origin': False, 'gap_paths': 14, 'unresolved': None}

git merge-base --is-ancestor 4a030f9f5 HEAD   ->  NO
```

Every symbol of the repair, grepped in the shared WORKING COPY — the bytes the publisher imports,
not a stamp and not a commit id:

```
EXIT_SCOPED_GATE_REFUSED  -> 0 in background/process_run_complete.py, 0 in background/publish_cause.py
SCOPED_SUITE_RED          -> 0, 0
SCOPED_GATE_UNJUDGED      -> 0, 0
_scoped_gate_cause        -> 0, 0
tests/background/test_the_scoped_gates_refusal_names_which_refusal_it_was.py  -> No such file
```

The three commits the checkout lacks are exactly the ones carrying it: `4a030f9f5`, `9c4731438`,
`8191fb188` — 14 files, `background/process_run_complete.py` +212 and `background/publish_cause.py`
+32 among them.

**And the clock forbids it twice.** The two recorded failures both PREDATE the landing:

| recorded | cause | |
|---|---|---|
| 06:55:10Z | `unattributed` | 1h27m BEFORE the repair landed |
| 07:39:21Z | `behind_origin` | 43m BEFORE the repair landed |
| 08:22:40Z | — | `4a030f9f5` committed |

`background/supervisor.py` (pid 3620344) booted **06:10Z** — before the commit existed. So even once
the checkout advances, the running process holds pre-repair code. **The restart is still the wrong
remedy first**: drift is stamp-vs-disk, and restarting before the checkout advances would make the
detector agree with itself and hide the gap.

## Why this is the load-bearing defect and not just bad luck

`cause: unattributed` at 06:55Z is **the old code's generic fall-through**, not the new instrument
saying "we cannot tell". The record cannot tell those two apart, and nothing in it tries: it carries
`git_hash` — the sha being *graded* — and nowhere the code version of the tree that *recorded* it.

That is a FAIL-SILENT on the instrument itself, and it already bit. The item read "that instrument
has never reported" as evidence about the world, when it was evidence about a checkout. Every future
reader of this file inherits the same trap: an absent namer and a namer that declined are the same
bytes.

## What IS now established, and it is progress — a cleared falsifier

The parked BLOCKING finding above named two causes for why the reconciler never closes the fork. Its
**cause 1** — a producer's output inside an authored tree being invisible to the generated-path
oracle — is now **CLOSED**, and by that finding's own one-variable control. `ef7a8f89e` ("teach the
generated-path oracle that a producer which COMPOSES its filename is still a producer") HAS reached
the shared checkout (`merge-base --is-ancestor ef7a8f89e HEAD` -> YES), and the verdict flips:

```
origin_reconcile._split_generated(['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'])
  finding, 2026-09-24 earlier:  ([], ['…SEAT_CLAIM…'], '')     # generated EMPTY, classified AUTHORED
  now, shared tree:             (['…SEAT_CLAIM…'], [], '')     # classified GENERATED
```

The gap has fallen with it: **12 behind / 3 ahead → 3 behind / 2 ahead.** That finding should be
re-read before it is worked, not re-derived.

## Why I did not close the fork myself

A reconcile was **already in flight** when I looked — pid 268484, 8m29s elapsed:

```
python3 -m tools.surgical_land --merge origin/main -m "merge origin/main: automatic reconciliation
  in an isolated worktree … Closed by `background/origin_reconcile` on the deadman cadence"
```

The sanctioned cadence is doing the work. A second `surgical_land --merge` from this seat would be a
rival landing on the same base. A gate run for another lane was also live (pid 269227), and
`background/supervisor.py` is one of the draw's named contested paths — so the daemon files in the
gap are precisely the ones I must not edit this turn.

## Pre-registration — filed BEFORE checking, answer not known when written

Of the in-flight reconcile (pid 268484):

1. It **lands** the merge, and the shared checkout comes to contain `4a030f9f5`.
2. `contains_origin` **stays False** afterwards, because the tree's own 2 commits (`7964c134c`,
   `199743f80`) still have not reached origin — a merge closes the behind leg, not the ahead leg.
3. `last_clean_publish` does **NOT** move this cycle (still 2026-09-21T18:15Z), because the
   supervisor process holds 06:10Z code whatever the checkout says.

Result of checking these is recorded in the RESULT note beside this document. If 1 is wrong the
reconcile refused and the fork is a seat judgement; if 3 is wrong then the publisher reloads code
per-cycle and the boot-stamp reading in this lane is weaker than it looks.

## What done means for the next piece

Not "the seventh cause is named". The seventh cause IS this document. Done is:

**A publish failure record says whether its own namer was present in the tree that wrote it.**

One leg, keyed to the property and not to today's answer: the record already carries the graded
`git_hash`; it must also carry whether the recording tree's `publish_cause` could emit the scoped
causes at all. Then `unattributed` splits into "declined" and "no namer here", the two readings stop
being the same bytes, and this trap cannot be re-entered. It is mutation-provable — delete the
presence field and a record that lies goes green.

Do NOT build it while the daemon files are mid-merge. The order is: reconcile lands → checkout
contains origin → restart the supervisor (and only then, because restarting first blinds the
detector) → the instrument gets its genuine first reading → then add the presence leg.
