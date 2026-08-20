> **PARKED IN `in_progress/` 2026-08-17 — one sub-item genuinely still open.**
>
> **LANDED this tick (commit below):** RUNG 1d PRODUCER STARVATION in full — `background/sim_runner.py`'s
> `record_run_outcome()` + `PRODUCER_STATE_FILE`, `background/supervisor.py`'s `_producer_starved_active()`
> wired as RUNG 1d of `_self_refill_draw` and mirrored in `_is_drained_and_gated`, the
> `tests/background/conftest.py` path sweep, and the four test files that prove it both ways
> (45 producer-rung + rest-ladder, 128 wedge/operational/sim-runner/isolation, all green at land).
> This is exactly the unit §5 named as landable alone, and it is now in a commit rather than in a tree.
>
> **STILL OPEN — the blocking sub-item, unchanged:** §5's coupled pair. The `run_phase4c` reader fix
> (`simulation/run_phase4c_on_phase2b.py`) and its repo-wide census control
> (`tests/saas/test_net_after_cts_and_blindfold_arithmetic.py`) still cannot land without the
> margin-basis repair (`saas/cost_to_serve.py` and the rest of that lane), and that repair is still
> uncommitted at HEAD — re-verified this tick, not inherited: `git show HEAD:saas/cost_to_serve.py`
> still emits `net_margin_gbp` at line 146 and `git show HEAD:simulation/run_phase4c_on_phase2b.py`
> still reads it, so HEAD remains self-consistent and landing either half alone breaks it.
>
> **WHAT UNBLOCKS IT:** the margin-basis lane
> (`WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK`)
> landing its own files, at which point these two paths land in or immediately after that commit.
> Also still open and NOT fixed on sight, per §4: the general test-isolation-by-enumeration class
> (`WORKER_FINDING_A_TEST_ISOLATES_THE_PATHS_IT_THOUGHT_OF_2026-08-10.md`) and the FUNCTIONS-side
> log leak, which no path sweep reaches.

# [WORKER-FINDING] Nine identical failures drew nothing because the producer had the alarm and the publisher had the mechanism (2026-08-17)

**Severity:** BLOCKING (the instance is fixed and live) · **Lane:** H_harness / OPS
**Class:** alarm-without-a-draw, on the un-mechanised half of a symmetric pipeline.

Director asked two questions on top of the repair: *why did nine identical failures over 70
minutes not draw themselves ahead of other work*, and *should "producer down" be as loud as
"publisher wedged", given they have the same consequence and only one is alarmed properly.*
Both are answered below with evidence. The answer to the second is **no, it was not, and now
it is** — RUNG 1d is built, wired, R15-proven and running.

---

## 1. The instance: what actually broke

`simulation/run_phase4c_on_phase2b.py:403` read
`cost_to_serve['portfolio']['net_margin_gbp']`. Today's margin-basis repair **deleted** that
key from the cost-to-serve view, deliberately, and says so in
`saas/cost_to_serve.py`'s own docstring:

> `net_margin_gbp` is DELETED rather than redefined, deliberately. Rebinding the name to the
> true net would have handed every existing reader a silently different number; deleting it
> makes an un-migrated reader raise KeyError, which is the fail-closed half of the same
> choice (R15).

So the KeyError was the repair **working as designed**. The defect is not the deletion — it is
that the migration was done reader-by-reader and guarded file-by-file. The repair migrated the
sibling `tools/run_phase4b_on_phase2b.py` (which now prints all three margin lines, each named
for its basis) and left `run_phase4c`, which is the one the runner actually executes via
`tools/run_annual_report.py`.

The existing guard could not catch it. `test_the_reporting_layer_no_longer_reads_cost_to_serve_
net_margin_gbp` greps **one file** (`saas/reporting/annual_report.py`) for **one spelling** of
the read. `run_phase4c` held the same read in a different file, so it passed the suite and then
failed nine consecutive scheduled runs.

**Fixed:** `run_phase4c` now prints gross / contribution / net-of-all-costs, matching its 4b
sibling. Two runs green since (17:27Z, 17:42Z, 287s each); `published_age_seconds` back to 286s.

**Closed as a CLASS (R10), not an instance:** a repo-wide census in
`tests/saas/test_net_after_cts_and_blindfold_arithmetic.py` — no module in `simulation/ saas/
company/ tools/ site/ background/ sim/ interface/ functions/` may read `net_margin_gbp` off a
cost-to-serve view, resolved from **bindings** rather than variable names.

> Naming was tried first and was wrong on the first real file it met: `annual_report.py` reads
> `_hl_cts["net_margin_gbp"]`, where `_hl_cts` is the LEDGER headline, which genuinely has that
> key. A census that must be taught about names like that one-by-one is the same file-by-file
> guard the class exists to replace.

R15 both ways, including the exact line that broke nine runs and the settlement-record reads
that must **not** fire.

---

## 2. Q1 — why did nine identical failures not draw themselves?

**Because nothing the runner writes on failure is a draw source.** Measured, not inferred.
`sim_runner.run_simulation()`'s failure path did exactly three things:

| what it wrote | who reads it |
|---|---|
| a line in `docs/observability/sim-runner-log.md` | a human |
| `notify(..., kind="real_alarm")` → ntfy | a human's phone |
| `update_agent_status(..., status="error", anomaly=...)` | **nothing in the draw ladder** |

`grep -n "sim.runner" background/supervisor.py` returns three hits, all of them comments about
marker cadence. The producer's health has never been an input to `_self_refill_draw`.

And the three watchers that could plausibly have seen it were each blind, structurally:

1. **RUNG 1, the publish-gate wedge** keys on publish FAILURES. A run that dies never attempts a
   publish, so nine dead runs produced **zero** entries and `failures` stayed EMPTY — which reads
   identically to a healthy gate. Fail-open on empty (R15's second killer pattern).
2. **RUNG 1b, operational-layer red** keys on `pytest -m operational` — the daemon-lifecycle /
   IaC-reconcile suite. The daemon was **alive** the whole time. The signal recorded
   `{"consecutive_green": 6, "last_result": "green"}` at 16:54Z with eight failures already
   behind it. It measures LIVENESS; the broken thing was the OUTPUT.
3. **The content-freshness clocks** (`publish_freshness.snapshot()`, read by the deadman) key on
   commit/publish recency by ANY writer. A concurrent SITE lane kept committing and publishing
   (13ccd5c9f at 16:22Z, 4b36dc08a after it), so at 17:25Z `published_age_seconds` read **1.9h**
   against a real producer outage of **3.0h**. That is `publish_freshness.py`'s own stated defect
   — *"content moving by luck is not a healthy pipeline"* — reappearing one level up: it was
   written to stop the SITE's heartbeat masking the SITE's content freeze, and here the SITE's
   content masked the SIM's.

Even at the 3h mark the deadman's content alarm is **notify-only** by its own docstring
("REPORT-ONLY here ... this makes a stale LIVE one loud"). The tenth response would have been a
tenth page.

There is a second, smaller half worth naming: **R5 was breached too.** R5 says alarms fire on
state transitions only and never repeat an unchanged status. Nine identical
`[SIM] Run FAILED — KeyError: 'net_margin_gbp'` messages is a per-failure send, not a
per-transition one. So the outage was simultaneously **not drawable** and **repetitive enough to
read as noise** — worse than either alone.

---

## 3. Q2 — should "producer down" be as loud as "publisher wedged"?

**Yes, and the project's own rulings already say so; only the publisher end had been mechanised.**

RUNG 1 exists because *"2h17m of alarms fired into tick silence on both 2026-07-23 and
2026-07-24 because no draw rung ever surfaced 'go fix the failing gate'"* — the same rule
consumed-not-absorbed twice before it became code. Every word of that reasoning transfers: a
wedged PUBLISHER and a dead PRODUCER have the **identical consequence** (nothing new reaches the
live site), and today the producer end cost 70 minutes to the same shape of silence.

MAKE_IT_STICK is explicit that this is not a prose fix: *"a rule lives in CLAUDE.md AND as
enforced code, or not at all; prose-only is worse than no rule."*

**Built, not recommended: RUNG 1d — PRODUCER STARVATION, priority zero.**

- `sim_runner.record_run_outcome()` writes `.sim_producer_state.json` on every **terminal**
  outcome — success clears, failure/timeout/crash increments. Wired into all four terminal paths
  (a census test counts them, because a path that forgets to write leaves the rung blind to
  exactly the outage it exists to catch).
- `supervisor._producer_starved_active()` has **two limbs**, because the two failure modes leave
  different evidence:
  - *diagnosed* — ≥3 consecutive failures sustained >30 min (runner alive, runs failing);
  - *undiagnosed* — newest `run_output_*.json` older than 3h (runner **dead**, wedged or
    never started, so it wrote no counter at all). A state-file-only detector is blind to
    precisely the outage it most needs to catch.

**That 3h is measured, and the first number was wrong.** It was written as 45 min on the
reasoning "a run cycle is ~6 min, so that is seven lost cycles" — which sized against the RUN
when the real cycle is run + PUBLISH. Checked against the 2,977 inter-completion gaps in the
runner's own log: p50 9 min, p90 20, p95 32, p99 67. A 45-min bar sits between p95 and p99 and
would have fired on **2.79% of gaps — roughly 31 phantom PRIORITY-ZERO draws a week on a
healthy pipeline**, which is how a rung earns itself a kill flag rather than trust. It was
caught by measuring rather than by it firing, but it was live on the box for ~15 minutes before
the re-deploy.

3h is not a fresh arbitrary number either: it is `publish_freshness.STALE_AFTER_SECONDS`, this
project's existing definition of "the live site has gone stale" — the exact consequence this
rung exists to prevent. Both ends of the pipeline now use one staleness clock, and a test pins
that equality so they cannot drift apart. The sharp instrument remains the *diagnosed* limb at
30 min, which is what catches an outage of today's shape; this limb is a backstop where hours of
latency is the right trade against phantom draws.
- **INDEPENDENCE (anti-tautology):** the artefact age is written by the child process, not by the
  runner's bookkeeping, so a later successful run supersedes a stale counter and the rung drains
  itself. Nobody edits state by hand.
- **A director hold is not starvation:** `.sim_runner_hold` present → silent.
- Wired as RUNG 1d of `_self_refill_draw` **and** mirrored in `_is_drained_and_gated`, so rest is
  never legitimate while the producer is down.

**R15, proven both ways** (`tests/background/test_producer_starvation_draw.py`, 24 tests):
fires on the recorded 2026-08-17 state and on the dead-runner case; silent on a healthy
producer, a lone flake, a young streak, a hold, an absent/malformed file, and a superseded
counter. Three mutations each kill their own named test: unwiring the draw, deleting the rest
mirror, and re-stamping `first_failure_ts` on every failure (which would pin the measured outage
near zero and make the rung unreachable — the fail-silent shape the whole mechanism exists to
remove). Two further tests pin *why rungs 1 and 1b were blind*, so if either ever gains the
ability to see a producer outage, they fail and 1d can be reconsidered — the justification is
testable, not asserted.

**Deployed (R2):** `sim-runner` and `supervisor` restarted 17:37Z; the live runner wrote a clean
`{"last_result": "ok", "consecutive_failures": 0, "git": "ea67bc2ba", "elapsed_s": 287}` at
17:42Z. Committed-is-not-running was checked, not assumed.

---

## 4. Two findings raised in passing, NOT fixed on sight

**(a) The 2026-08-10 test-isolation-by-enumeration class is still open, and it bit this work
twice.** `WORKER_FINDING_A_TEST_ISOLATES_THE_PATHS_IT_THOUGHT_OF_2026-08-10.md` predicted this
exactly: isolation written as an enumeration of the paths a test happened to need is correct only
against the code as it stood that day. Within minutes of RUNG 1d landing, the ordinary
`run_simulation()` tests stamped
`{"consecutive_failures": 6, "detail": "timeout after 0s: stuck at 2019-03-31 SP47", "git":
"abc1234"}` onto the machine's **real** producer-health file — i.e. a test could make the live
draw ladder hand priority-zero to "the producer is down" on a healthy box. `test_sim_runner.py`
isolates `PROJECT_DIR`, `LOG_FILE`, `STAGING_DIR` and `REPORTS_DIR` by hand; `PRODUCER_STATE_FILE`
was not on that list because it did not exist when the list was written.

Closed for `sim_runner` as a **sweep** rather than a tenth remembered name: the directory conftest
now redirects *every* `Path` constant on the module that points into the real checkout, so the
next one is covered on the day it lands. Mutation-proven (delete the sweep → the control fails).
**The general class is still open** — the same sweep shape would close it for
`process_run_complete`, which is still writing test lines like `git=abc1234` into the live
`sim-runner-log.md` today, and for the other writers that finding enumerates.

**(b) The same leak exists on FUNCTIONS, which no path sweep can reach.** `supervisor.log` and
`sim_runner.log` append to the real operational logs and are not injectable. This work's own
tests wrote eleven `PRODUCER STARVATION (RUNG 1d, PRIORITY ZERO): the simulation producer is
down` lines into the live `supervisor-log.md` while the producer was healthy — and they were
briefly diagnosed as a real false positive on the rung they describe. That is the cost precisely
stated: **a test's output that is indistinguishable from an incident.** Patched in this test;
both logs' polluted lines were removed (11 from `supervisor-log.md`, 9 from `sim-runner-log.md`);
the class is queued, not fixed on sight.

---

## 5. State of the change, and the one thing that is NOT landable alone

Uncommitted, deliberately. **The `run_phase4c` fix and its census control cannot be committed
without the margin-basis repair**, and that repair is itself uncommitted — which is the subject
of `6ccb58c7` ("the margin-basis repair ... is in NO commit"). At HEAD, `cost_to_serve.py` still
produces `net_margin_gbp` and `run_phase4c` still reads it, so HEAD is self-consistent; landing
the reader fix alone would break it in the mirror direction. These two must land together.

The RUNG 1d work (`sim_runner`, `supervisor`, the conftest sweep and the three test files) has no
dependency on that lane and is landable on its own.

**Green at time of writing:** 24 producer-rung, 14 rest-ladder isolation, 18
net-after-CTS/census, 114 sim-runner + wedge + operational-red, 253 controls, 2250 saas +
interfaces.
