**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the one launcher is a convention, not a rule, and nothing refuses a seventh throwaway

LATENT, and deliberately not higher: no published figure is wrong because of this, and no long
job is currently dying of it. It is a *recurrence* hazard — the remedy is now in one module with
three callers, and this project's own evidence is that a rule living only in its call sites gets
rediscovered by paying for it again.

**Filed:** 2026-09-08, delivery seat (isolated worktree).

---

## The premise, re-measured at draw time

The drawn item cites `fdc16f4c6`. `git merge-base --is-ancestor fdc16f4c6 origin/main` → **yes**,
it is already an ancestor. That commit **retired two sites into the launcher** (`tools/run_arms_rerun.py`
replacing a shell script that never launched; `measure_publish_gate_subject_cost` losing its private
`_systemd_run_argv` / `_unit_is_active` / `_clear_a_failed_unit` / `--detach`).

**The premise is NOT spent.** The retirement landed; the *census* did not. Checked directly:
`grep -rln launch_long_job` over the tree names nine files, all of them either the launcher, a
caller, or a caller's test. **No file refuses a new launch site.** That is the work.

---

## The defect, stated precisely enough to detect

`setsid` changes the SESSION and the PROCESS GROUP. A cgroup is neither. `worker-tick.service` is
`KillMode=control-group`, so when the launching oneshot finishes systemd SIGKILLs every process in
its cgroup — textbook POSIX detach included. The 2026-08-28 run recorded `pid==pgid==sess`, the
detach demonstrably HELD, and it died anyway. So did 09-07. So did 09-08.

Five launches of one measurement, four deaths, one cause, and the remedy rediscovered at least four
separate times because each site banked it privately in a `/var/tmp/*.sh`.

The remedy now exists once (`background/launch_long_job.py`). What does not exist is anything that
**refuses the next hand-rolled one**. A new module with `subprocess.Popen(..., start_new_session=True)`,
or a fresh `systemd-run` argv typed into a throwaway script, would be written, would pass every gate,
would look fine, and would die at the next cgroup teardown.

---

## PRE-REGISTRATION — filed BEFORE the machine census was run

The population was enumerated **by hand** first (grep, then a scratch AST walk for the
`start_new_session` keyword only). The predictions below are about what the *committed census module*
— which did not exist when this was written — will report over `git ls-files`. Recorded here so the
machine can refute the hand pass rather than confirm it.

**P1.** Excluding `background/launch_long_job.py`, the census reports **8** sightings:

| path | shape | n |
|---|---|---|
| `background/worker_tick.py` | detached session | 1 |
| `tools/scale_probe_10k.py` | detached session | 1 |
| `tests/tools/test_scale_probe_10k.py` | detached session | 1 |
| `tools/measure_publish_gate_subject_cost.py` | raw transient unit | 2 |
| `tests/background/test_launch_long_job.py` | raw transient unit | 1 |
| `tests/tools/test_measure_publish_gate_subject_cost.py` | raw transient unit | 2 |

**P2.** **Zero** shell sightings. All nine committed `*.sh` run their work in the FOREGROUND —
no `nohup`, no executed `setsid`, no trailing `&`, no `disown`. (`run_arms_with_the_skill_funnel_20260830.sh`
*describes* being launched as a transient unit, in a comment; the launching command itself was
hand-typed and was never committed. See the limit below.)

**P3.** `tools/run_arms_rerun.py` is **NOT** a sighting, despite containing the literal `systemd-run`
at line 8 — it is inside the module docstring, and the census must exclude docstrings or it measures
prose. This one is the discriminating prediction: it is the only place where "grep found it" and
"the census should report it" are predicted to disagree.

**P4.** The poison round fires on every shape. A synthesised tree containing each shape produces a
sighting of each shape — established BEFORE any mutation battery, because "survived" means two
opposite things and a census that can detect nothing survives everything.

**What would refute these:** any count differing from the table; any shell sighting; `run_arms_rerun.py`
appearing; or a shape the poison tree cannot make fire.

### RESULT — measured after the module was written

**P1 is REFUTED, and the refutation was the most useful thing in this turn.** The first census
returned **20** sightings, not 8. The predictions are kept above exactly as filed.

The refutation did **not** mean the hand pass had missed twelve launch sites. It meant the
*detector* was wrong: it asked `"systemd-run" in text`, a substring, and every one of the twelve
extras was **prose inside a code string** —

| what it counted | ×  |
|---|---|
| `reason="systemd-run is the mechanism under test"` (skipif markers) | 6 |
| `_Unbounded("systemd-run unavailable")` and the assertion comparing to it | 2 |
| `log("  ! systemd-run unavailable -- REFUSING ...")` and similar messages | 3 |
| `"...waiting does not grow a systemd-run"` | 1 |

A census whose own docstring says it detects the SHAPE and not the word was detecting the word —
in the one repository whose modules are mostly prose *about this exact defect*. The hand pass had
used exact equality and so never saw them; exact equality is the opposite error, blind to a shell
command string that spells the launch with its flags attached.

The discriminator is now: **basename equals the tool** (an argv element or a `which` argument,
`/usr/bin/systemd-run` included) **or opens a command line and carries a flag**. Held by
`test_the_discriminator_separates_using_the_tool_from_naming_it`, whose False rows are the verbatim
strings above rather than invented ones.

Re-run under the fixed discriminator: **9 sightings**, predicted in advance as 8 plus
`test_measure_publish_gate_subject_cost.py:3207` (`lambda _n: "/usr/bin/systemd-run"`), which only
basename-matching sees. That is the count now frozen as the floor.

**P2 HELD.** Zero shell sightings across all nine committed `*.sh`.
**P3 HELD.** `tools/run_arms_rerun.py` is not a sighting despite spelling the tool at line 8 — the
docstring exclusion works. This was the discriminating prediction and it discriminated.
**P4 HELD.** The poison tree fires all three shapes; asserted as a set equality against `ALL_SHAPES`
so a shape added to the enum with no detector behind it fails there rather than going unguarded.

---

## What was built

* **`tools/launch_shape_census.py`** — the census and its floor. `--list` reports, `--check`
  refuses. Floor keyed by `(path, shape) → (count, reason)`; **not** by line number, because a
  floor that goes red when an unrelated edit moves a line is one that gets silenced.
* **`tests/architecture/test_the_one_launcher_is_the_only_launcher.py`** — 22 tests, poison round
  first.
* **`tools/pre_commit_test_gate.py`** — the sixth `CONTROL_TESTS` entry.

### Two things this turn found that were not in the direction

**1. The control would have been unwired, and that is a documented recurring shape here.**
`pre_commit_test_gate` selects tests by filename **stem**. This census's subject set is the whole
repo; nothing about a new module containing `start_new_session=True` mentions this test's stem, so
per-file selection would have run it only when the test itself was edited — the case needing it
least — and stayed silent on the only case it exists for. That is the *identical* FAIL-SILENT-at-
selection shape the gate file already documents four times over (the wall, the seam, the lint
ratchet, the store contract), each added *after* it went red at HEAD. This one was caught before
shipping. It is now the sixth always-run entry.

**2. A mutation survived, and the survivor named a real gap.** Replacing the `now < allowed`
branch (FLOOR ROW UNMET) with `elif False:` left the suite **fully green** — the real tree matches
its floor exactly, so that branch is unreachable from the tree alone. It is the branch that catches
*a detector going blind*, which is the failure this whole file exists for, and it was the one thing
nothing could test. `test_all_three_verdicts_are_reachable` now asserts all three verdicts fire, as
one control over the partition rather than a leg apiece.

**Mutation round, run after the poison round: 8 written, 8 killed.** Detector blinded (each of the
three shapes), refusal fails open on growth, floor-rot refusal removed, substring draft restored,
exclusion set widened to silence the tick, prefilter drops everything.

### The prefilter, and why its proof costs what it saves

`_census_python` skips the AST parse for a file containing neither trigger literal — exactly
equivalent, not approximate, and it takes the repo-wide walk from **5.7s to ~0.1s**.

`test_the_prefilter_is_equivalent_to_parsing_everything` walks the tree **both ways** and requires
identical output, and substantially all of the file's 6.2s is that one control. It costs precisely
what the optimisation saves. That is the correct trade rather than an oversight: an unproven
prefilter on a control of this shape is a fail-open waiting to happen, and the cheap version of
this file is the one that quietly stops seeing things.

---

## What is next

* The **uncommitted hazard is untouched** and is the larger half. A `/var/tmp/*.sh` is invisible to
  a tree census by construction. The shape that would close it is a check at *launch* rather than
  at commit — something in the tick's own path that notices a descendant leaving without a
  transient unit. Not built here, and not obviously worth it.
* The census is **blind to two files by name** (itself and its test), because they hold its trigger
  strings. `test_the_launcher_is_excluded_and_nothing_else_quietly_joins_it` pins that set at two,
  so the cheapest route past this control — adding your file to `_BLIND_TO` — is a refusal.
* `tools/measure_publish_gate_subject_cost.py` keeps a `systemd-run --scope` argv, and it is
  correct that it does: a synchronous memory bound is a different mechanism from a detached launch
  and the launcher does not offer it. If a second caller ever wants a bounded foreground phase,
  *that* is the point at which `--scope` should move into a shared module — not before.

---

## What the census can and cannot see, stated on the surface

**It cannot see a `/var/tmp/*.sh`.** A tree census reads `git ls-files`; the throwaway scripts that
caused every one of these deaths were never committed, and this control would not have caught a
single one of them at the time. Saying otherwise would be the fail-open.

What it *does* buy, and why it is still worth the file: the retirement of those five scripts moved
the work **into committed modules**. `tools/run_arms_rerun.py` is the shape the next one takes now.
The census refuses a new committed site, and freezes the floor so an existing one cannot quietly
multiply. The uncommitted hazard is unchanged and is named here so nobody reads a green census as
covering it.

**`background/worker_tick.py` is a floor row with a reason, not an exemption.** It blocks until its
child exits, so that child is *supposed* to live inside the tick's cgroup — flagging it as a defect
would get the whole census silenced by the next reader, which is the direction's own warning. But
"exempt" and "invisible" are different: as a floor row its count is ratcheted, so a *second* detach
appearing in that file is still a refusal.
