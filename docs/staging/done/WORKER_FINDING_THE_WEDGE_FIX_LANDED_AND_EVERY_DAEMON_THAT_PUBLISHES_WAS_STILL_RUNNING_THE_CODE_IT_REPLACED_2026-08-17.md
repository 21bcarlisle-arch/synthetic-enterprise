# [WORKER-FINDING] The wedge fix landed at 13:29 and the daemon that published at 14:10 was still running the code it replaced (2026-08-17)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the deployment gap is
DISCHARGED in this tick by restarting the stale units; `OPS3_first_post_ruling_publish`
exit criterion (4) is left honestly OPEN, because the counter must return to zero through
a real cycle and never by hand.
**Discharged:** `systemctl --user restart sim-runner.service background-worker.service`,
verified by `background.boot_sha.read_boot_sha` and `process_reconciler.evaluate_boot_sha_drift`
(both quoted below).

## How it was found

Drawing `OPS3_first_post_ruling_publish` — "one publish cycle green, the wedge counter back
to zero through a real pass". `cb82f3af5` had landed the RUNG-1 repair four hours earlier
and its commit message states the measured cause correctly. The counter had not moved.

The obvious reading was that the repair was wrong. **It is not.** Every claim below is
`observed-with-evidence` (R9); nothing here is inferred.

## The evidence chain, closed

`docs/observability/sim-runner-log.md`, the last publish of the marker in question:

```
- [2026-08-17 14:10 UTC] [process_run] Publish gate: run_complete_20260817T130225Z.md
  exited 0 but no suite PASS is recorded for git=unknown -- publishing nothing is not
  evidence the gate is healthy, so the wedge streak is left exactly as it was found.
```

The same three facts, read off disk at HEAD `61d1f8daf` after that line was written:

| fact | value | source |
|---|---|---|
| `docs/staging/done/run_complete_20260817T130225Z.md` reads | `Git: 32ffa211a` | the marker |
| `.last_tested_hash` reads | `32ffa211a` | written only by the gate's own rc=0 |
| `_marker_git_hash('docs/staging/run_complete_20260817T130225Z.md')` | `32ffa211a` | HEAD code |
| `_green_is_on_record_for('32ffa211a')` | `True` | HEAD code |

So at HEAD the repair does exactly what it says: it locates the archived marker, reads
`32ffa211a`, matches the suite's own PASS record for that same commit, and takes the clear
branch. The gate had passed for precisely that commit. The running process still said
`git=unknown`.

## The defect

The daemons were running the code the repair replaced.

```
PID 514  /usr/bin/python3 background/sim_runner.py       started Mon Aug 17 10:36:46 2026
PID 499  /usr/bin/python3 background/background_worker.py started Mon Aug 17 10:36:46 2026
```

`background.boot_sha.read_boot_sha('sim-runner')` → `1f7fafc0253ca6e009c4d01bb62cda3b0a16ce92`.

```
$ git merge-base --is-ancestor cb82f3af5 1f7fafc02   →  rc=1  (the fix is NOT in the boot code)
$ git show 1f7fafc02:background/process_run_complete.py | grep -n '_marker_git_hash'
  (no output — the function does not exist at the boot SHA)
$ git show 1f7fafc02:background/process_run_complete.py | grep -n 'parse_marker(Path(marker))'
  4513:            git_hash = parse_marker(Path(marker)).get("git_hash", "unknown")
```

The units are `WorkingDirectory=/home/rich/synthetic-enterprise` and load their modules at
import, so a commit to `background/process_run_complete.py` reaches a long-lived daemon
only when that daemon restarts. Nothing restarted them. **R2, exactly as written: a code
fix is deployed only once the running process has been restarted with it. Committed !=
running.**

The project's own instrument already knew. `process_reconciler.evaluate_boot_sha_drift()`,
run at HEAD before the restart, returned `stale = ["background-worker", "deadmans-switch",
"naive-organ", "sim-runner", "supervisor"]` with `background/process_run_complete.py` named
in every one of those five `stale_detail` lists, `vacuous: false`, population 11. PW1 built
that signal to be actionable rather than always-red, and it was green-for-the-quiet and
red-for-exactly-this. **The signal fired; no one was reading it.** That is the part worth
generalising — the gap here is not detection, it is that nothing turns a RED drift row into
a restart.

## What this cost

`episode_failures: 257` and `wedge_since` pinned to 2026-08-09 — an 8-day wedge clock —
against a pipeline whose gate was passing. The RUNG-1 priority-zero doorbell fired every
tick for that whole window, so this defect did not merely fail to clear an alarm; it spent
the top of the queue. The last four hours of it were spent against a repair that was
already correct and already committed.

## What was done, and the verification

`systemctl --user restart sim-runner.service background-worker.service` → rc=0, both
`active`. New PIDs `319119` / `319121`, started `Mon Aug 17 15:18:08 2026`. Both units'
`ExecStartPre` re-stamps the boot SHA, so the drift row that follows is re-derived from
observed reality rather than asserted:

```
HEAD                        : 61d1f8dafd066c393d11da2c5a81307d37aa6d4a
sim-runner        boot sha  : 61d1f8dafd066c393d11da2c5a81307d37aa6d4a  == HEAD
background-worker boot sha  : 61d1f8dafd066c393d11da2c5a81307d37aa6d4a  == HEAD
```

**The signal discriminated rather than flipping wholesale**, which is the property PW1 was
built for and the reason this is evidence and not a claim. For both daemons the stale set
went `23 -> 11` modules and `background/process_run_complete.py` — the module carrying the
repair, and the only one this restart was for — **dropped out**. The 11 that remain are
every one of them an *uncommitted working-tree* edit belonging to another lane
(`background/gap_metric.py`, `background/supervisor.py`, `saas/clv_model.py`,
`saas/cost_to_serve.py`, `saas/enterprise_value.py`, `saas/reporting/annual_report.py`,
`simulation/policy_costs.py`, `simulation/run_phase4c_on_phase2b.py`, and three
`tools/generate_*.py`). A restart cannot deploy code nobody has committed, so that residue
is correct to still be flagged and is not this finding's to clear.

**An open question, deliberately not answered here.** These units run
`WorkingDirectory=/home/rich/synthetic-enterprise`, so a daemon restarted at 15:18 imported
the working tree *as it then stood*, including those 11 uncommitted files — while the drift
signal computes `git diff <boot_sha> -> working tree` and therefore reports them stale. If
that reading is right the signal over-reports for a freshly-restarted daemon. It is stated
as a QUESTION, not a finding: it needs `loaded_code_drift` read properly against what the
process actually imported before anyone asserts PW1 has a defect, and this tick's job was
the publish.

## Ordering, and a correction to my own first reasoning

I first intended to commit before restarting, on the theory that booting at a newer HEAD
would align the next marker's `Git:` with the gate's checkout. **That theory is wrong and
is recorded here rather than quietly dropped.** Neither value depends on the daemon's boot
SHA: the marker's hash comes from `git rev-parse` at run start and the gate's subject from
`git rev-parse HEAD` at gate time, both read live. The only thing that actually aligns them
is HEAD being QUIET across the cycle — which is the real argument for landing this commit
now, before the next cycle opens, rather than during one.

## What is QUEUED, not fixed (SELF_INTERRUPT_DISCIPLINE)

**The gate stamps a commit it did not necessarily test.** `_process` passes the MARKER's
`git_hash` into `run_fast_tests(git_hash)`, and on rc=0 `_run_gate_in` writes exactly that
hash to `.last_tested_hash` (`background/process_run_complete.py:1893`). But the subject it
ran against is `_head_checkout()`, which materialises **`git rev-parse HEAD` at gate time**
(`_head_sha`, line 1472). When HEAD is quiet across the cycle these coincide and the stamp
is true. When another lane lands during the ~10–20 minute gate run, `.last_tested_hash`
names the marker's commit while the tree tested was a later one — the stamp names something
that was not the subject.

Both directions of that are real: the wrong-subject label above, and the reverse case the
router's own docstring already anticipates ("HEAD moves under a long publish cycle... a
HEAD-keyed check would refuse to clear after a genuinely green gate"). The clean resolution
is probably to materialise **the marker's own commit** rather than current HEAD, which makes
subject, stamp and key one commit and dissolves both directions at once — but that is a
change to the gate's subject, which is a director ruling
(`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09`, "a clean HEAD checkout"), and it is not
what is blocking the machine right now. **Queued, not fixed on sight.** It needs its own
atom, its own R15 mutation both ways, and a reading of whether the ruling's "HEAD" meant
"committed truth" (which the marker's commit also is) or literally the tip.

## Why the existing controls did not catch it

`test_the_publish_gate_wedge_clears_on_a_green_publish`-family tests all exercise the
FUNCTION. A function test cannot observe that the process holding the old function object
in memory is the one actually publishing — the subject of an R2 defect is the process
table, never the module. The control that CAN see it is `evaluate_boot_sha_drift`, and it
had no consumer with a hand. There is no test in this repo that fails when a daemon's
loaded code is stale, because staleness is a property of the live box.

**R10 (class, not instance).** The instance fix is "restart two units". The class fix is a
consumer for the drift signal: a daemon whose own import closure is RED against the working
tree gets restarted, or gets an alarm that says so in words a tick will act on. Filed as a
candidate atom rather than built here, because the safe form of "the machine restarts its
own daemons" needs designing (a restart loop that fights a crash loop is worse than the
staleness), and this tick's job was the publish.
