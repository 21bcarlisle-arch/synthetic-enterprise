#!/usr/bin/env python3
import ast
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
from pathlib import Path

# THIS MODULE IS RUN AS A SCRIPT PATH, SO THE REPO ROOT IS NOT ON sys.path (2026-08-17, the
# 258th failure of the wedge episode -- and the FIRST one whose cause was visible, because
# 0a3b39ee9 had just stopped the publish path swallowing its own crashes).
#
# WHAT BROKE. Both daemons launch this file the same way -- `subprocess.run([sys.executable,
# ".../background/process_run_complete.py", marker], cwd=PROJECT_DIR)` (sim_runner.py::197,
# background_worker.py::395). Python seeds sys.path[0] from the SCRIPT'S DIRECTORY, never from
# cwd, so inside that process `background/` is the root and `import background` cannot resolve.
# Setting cwd=PROJECT_DIR looks like it should fix that and does nothing at all.
#
# The file already knew this: three call sites below catch `ModuleNotFoundError` and retry the
# flat name, each commented "launched as `python3 background/process_run_complete.py`". A
# top-level `from background.publish_step_ledger import ...` landed the day before with no such
# guard, and a top-level import has no second chance -- every publish died at line 16 before
# main() was reached. The one invocation that DID work was the smoke check in start_worker.sh,
# `python3 -c 'import background.process_run_complete'`, because `-c` puts cwd on sys.path: the
# check and the daemons disagreed about how the module is entered, so the check was green
# throughout (R15 wrong-subject -- the control tested an entry mode nothing uses).
#
# WHY A PATH BOOTSTRAP RATHER THAN A FOURTH try/except. The try/except idiom is per-import and
# defers the failure: a bare `except ModuleNotFoundError: pass` here is what produced the OTHER
# traceback in the same log -- `NameError: name 'PublishStepLedger' is not defined`, 2,600 lines
# later inside generate_dashboard_json, with the true cause long gone. Putting the root on
# sys.path fixes the entry mode ONCE, for this import and every future one, and is a no-op under
# `-m` (the root is already there, and the insert is idempotent).
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from background.live_ledger_guard import guard_live_ledger_write  # noqa: E402 -- ditto
from background.publish_step_ledger import PublishStepLedger  # noqa: E402 -- needs the path above

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"
LATEST_MD = PROJECT_DIR / "docs" / "status" / "LATEST.md"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
LAST_TESTED_HASH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_hash"
# THE GREEN'S CLOCK, written beside it by the same writer in the same rc=0 branch (2026-08-20).
# `.last_tested_hash` says WHICH commit passed and nothing about WHEN, so its wedge-detector
# consumer borrowed git ancestry as a clock -- and ancestry runs backwards across a
# stack-drained publish queue. See LAST_TESTED_HASH_CONTRACT below.
LAST_TESTED_GREEN_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_green.json"
# THE ONE PLACE THE `.last_tested_hash` CONTRACT IS STATED (OPS2, 2026-08-10). It had two
# readers inferring the semantics from each other's call sites, which is how a cross-check
# quietly stops being independent.
LAST_TESTED_HASH_CONTRACT = """\
`.last_tested_hash` holds ONE line: the 40-char (or abbreviated) SHA of the commit the publish
gate last ran to GREEN.

WRITTEN by exactly one writer, `_run_gate_in`, and only when the suite returned rc=0. Never on a
red, never on a timeout, never on an unavailable checkout -- `test_a_timed_out_gate_blocks_the_
publish` pins the timeout case, because a gate that did not finish must not leave a claim that it
passed. It is therefore a claim about COMMITTED TRUTH, not about the working tree: since
DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09 the gate's subject is a clean checkout of that
SHA, so "the tree happened to be green while N lanes were mid-edit" is no longer expressible here.

READ by two consumers, for two different questions:
  * `run_fast_tests` -- SKIP: this same SHA already passed, so do not re-run the suite. Safe
    precisely because the subject is the SHA and nothing else.
  * `supervisor.py::_publish_gate_wedge_draw` -- INDEPENDENCE: the wedge state file says the gate
    has been failing; if `.last_tested_hash` equals current HEAD then those failures are STALE
    (a later cycle passed at HEAD) and no wedge work is drawn. The independence only holds while
    this file is written from the gate's own return code and the state file from the publish
    OUTCOME record -- two sources, one check. Anything that stamps this file without a green
    suite collapses that into a tautology and blinds the wedge draw.

Absent/unreadable means "no green is claimed": the gate runs, and the wedge draw treats the
cross-check as unavailable rather than as a pass. Both directions are the fail-safe one.

THE CLOCK IS A SECOND FILE, `.last_tested_green.json` = {"sha": <same hash>, "ts": <epoch>}
(2026-08-20). This file holds a SHA and no time, so the wedge detector had to infer "which came
last" from git ancestry -- and since OPS3 made the publish queue a STACK (newest marker first),
ancestry is anti-correlated with time across a drain: on 2026-08-20 a green recorded 27 minutes
AFTER the newest failure sat 3 commits BEHIND it in history, and the RUNG-1 alarm stayed armed
for three consecutive ticks on a gate that was green and publishing.

The sidecar is ADDITIVE and the one-line file above is unchanged, so `run_fast_tests`' SKIP
consumer is untouched. It is written by the SAME writer, in the SAME rc=0 branch, immediately
after the hash -- so the independence stated above is unchanged: it still comes from the gate's
own return code and not from the publish outcome record. Its write is best-effort and wrapped:
a monitoring record must never break the pipeline it monitors. If it is missing, stale or
mismatched, the wedge draw reads "no green is claimed" and stays ARMED, which is the fail-safe
direction -- so a failed sidecar write costs a phantom draw, never a silenced alarm.
"""
LAST_PUSH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_push_time.json"
RUN_LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".process_run_complete.lock"
# EX_TEMPFAIL. A lock-skip ("another instance already holds the run lock") is
# NEITHER a success NOR a processing failure -- the marker was left untouched.
# It used to return 0, indistinguishable from a real publish, which meant
# background_worker's sweep recorded a publish-gate SUCCESS for a marker it had
# not published -- clearing the H15 wedge streak and auto-resolving the open
# [ACTION NEEDED] item while the pipeline was still wedged (observed
# 2026-07-29 16:53Z: two markers logged "Processed", both untouched, one minute
# before the lock holder itself failed the gate). See _record_publish_gate_outcome.
EXIT_LOCK_SKIPPED = 75
# THE SIBLING HALF OF THAT SAME FAIL-OPEN, closed 2026-08-12
# (WORKER_FINDING_A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_2026-08-10, BLOCKING). A marker
# another publisher archived between this caller's glob and this process opening it is a
# DUPLICATE: nothing was published, nothing was touched, and it is evidence of exactly as little
# about the gate's health as a lock-skip. It returned 0 for two weeks, so the worker's sweep
# logged "Processed" for it and called `_record_marker_published()` -- PW4's one evidenced close
# of the zero-progress episode -- for a marker this sweep never published. Observed 2026-08-10:
# 43 duplicate lines and 188 "Publish gate recovered" lines while the live site had not advanced
# for 31 hours. The 2026-07-29 fix gave the lock-skip its own code and left this door returning 0
# (cf. feedback_audit_sibling_half_for_hardened_class).
EXIT_NOTHING_PUBLISHED = 76
# THE THIRD DOOR OF THAT SAME FAIL-OPEN, closed 2026-08-19
# (WORKER_FINDING_THE_PUBLISH_COMMIT_STOPPED_LANDING_WHILE_RUNS_KEPT_ARCHIVING_2026-08-19,
# BLOCKING). The two codes above cover a publish that never STARTED. This one covers a publish
# that ran the whole way and whose COMMIT then did not land -- the pre-commit hook chain refused
# it, it outran the hook deadline, the push never reached origin, or the provenance check
# fail-closed. `_process` logged the failure and returned 0 anyway, so the ONE input the wedge
# detector consumes could not tell "published" from "refused".
#
# AND IT DID NOT ONLY FAIL TO ALERT -- IT ACTIVELY DISARMED. rc=0 is routed through
# `_green_is_on_record_for`, whose evidence is `.last_tested_hash`. On this path the scoped suite
# WAS green (the refusal came later, from the pre-commit gate, on a red the publish did not
# cause), so that check passed and `record_publish_gate_success()` cleared the streak.
#
# OBSERVED, not inferred (docs/observability/sim-runner-log.md, 2026-08-19): FOURTEEN consecutive
# "Commit/push failed (commit_refused)" between 01:56Z and 11:45Z -- gate output naming
# "FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED", i.e. an unrelated lane's red on the
# shared tree -- with "Publish gate recovered -- cleared wedge state, re-armed alarm." logged in
# the middle of it at 07:23Z, `.publish_gate_state.json` reading `failures: []` throughout, and
# poesys.net serving figures 11.5 hours stale while every run archived itself as done.
EXIT_PUBLISH_DID_NOT_LAND = 77
# THE INNER CLOCK, closed 2026-08-21
# (WORKER_FINDING_A_PUBLISH_TIMEOUT_IS_RECORDED_AS_A_TEST_REGRESSION_AND_THE_SCOPE_CANNOT_MEET_ITS_CAP_2026-08-21,
# BLOCKING, recommendation 1). The publisher has TWO clocks over the same gate. The OUTER one
# belongs to the caller -- `sim_runner` and `background_worker` both kill the publisher on their
# own deadline and both already record `kind="deadline_kill"` with no invented return code,
# under a comment that says why: "rc=124 WAS: the classifier maps any rc>0 to test_regression,
# which is how a stopwatch became 145 recorded test failures and sent the RUNG-1 draw after a
# gate that was never judged."
#
# The INNER clock -- `GATE_SUITE_TIMEOUT_SECONDS`, the publisher's own budget, whose verdict is
# `_gate_timed_out()` -- had no such carve-out. It set `tests_ok=False` and fell into the same
# `return 1` as a genuine red, so `_classify_gate_failure` read it as `test_regression`: the
# defect this project closed on the outer half, still live on the inner one.
#
# OBSERVED, not inferred (docs/observability/.publish_gate_state.json + sim-runner-log.md,
# 2026-08-21): both recorded failures read `test_regression` while `total_red` was 0 and
# `blocking_tests` was empty -- an accusation with no accused. The 16:03Z one is provably a
# stopwatch: "Fast test suite timed out (>300s) -- NOT committing" immediately above "Scoped
# publish-path gate FAILED". Over 2026-08-20/21, 3 of 46 refusals of a 32-hour wedge were this.
#
# NOT `deadline_kill`, deliberately: that label states the CALLER's deadline killed the
# publisher, which is a different fact about a different clock, and filing this under it would
# make the payload name the wrong process to go and look at. Same class, own name.
#
# NOT in NO_PUBLISH_EXIT_CODES, for the reason given below EXIT_PUBLISH_DID_NOT_LAND: a gate
# that could not answer is a FAILED gate (R15 -- an unavailable check is a failed check), so it
# must reach `record_publish_gate_failure` and keep the wedge streak. What changes is what the
# alarm SAYS, never whether it fires.
EXIT_GATE_TIMED_OUT = 78
# THE FOURTH CLOCK, closed 2026-08-30. The same defect as the two above, on the one clock nobody
# had counted: `tree_lock()`. `git_commit_push` entered it OUTSIDE its own try, so on a busy tree
# `TreeLockTimeout` propagated all the way out of `main()` as an uncaught traceback -- rc=1, the
# generic code, which `_classify_gate_failure` reads as `test_regression`.
#
# OBSERVED, not inferred (docs/observability/.publish_gate_state.json + sim-runner-log.md,
# 2026-08-30 12:29Z): the log for that cycle reads "Tests skipped -- already passed for
# git=09b90343d" three lines above "Publish-gate failure #3 (test_regression, rc=1)". The suite
# was never even RUN, let alone red, and the state file recorded `blocking_tests: []` with
# `total_red: 0` -- an accusation with no accused, for the third time in this module's history.
# Two of the seven failures of that wedge episode were this, and the RUNG-1 draw that came to
# diagnose it was sent hunting a red test that did not exist.
#
# NOT `commit_did_not_land` (rc=77), deliberately: that label tells the reader the pre-commit
# hook chain refused the commit and to go and read the hook output. Here the hook chain never
# ran -- another writer held the tree lock for the full 60s -- so filing it there would point at
# a gate that never spoke. Same class, own name, per the two carve-outs above.
#
# CONTENTION IS NOT A REGRESSION and it is not a wedge either: this cycle publishes nothing and
# the NEXT one retries. But it is still a FAILED publish (R15: an unavailable check is a failed
# check), so it keeps the streak and fires the alarm -- what changes is only what the alarm SAYS.
EXIT_TREE_LOCK_UNAVAILABLE = 79
# The register callers switch on. rc=0 asserts ONE thing -- this process retired the marker and
# the published surfaces are current. Anything that publishes nothing states so with its own
# code; `tests/background/test_a_duplicate_marker_is_not_a_publish.py` fails by name on a new
# `return 0` in `_process` so a later no-op path cannot quietly rejoin the class (R10).
#
# EXIT_PUBLISH_DID_NOT_LAND IS DELIBERATELY NOT IN HERE. This tuple means "evidence of NOTHING
# about the gate's health -- record neither a success nor a failure". A refused commit is
# evidence of a FAILURE and must reach `record_publish_gate_failure`; filing it here would close
# the alarm door a second time, in the name of the fix that opened it.
NO_PUBLISH_EXIT_CODES = (EXIT_LOCK_SKIPPED, EXIT_NOTHING_PUBLISHED)
RUN_INSIGHTS_PATH = PROJECT_DIR / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT_DIR / "docs" / "observability" / "run_history.json"
# H11_naive_organ (L2): the deliberately-amnesiac question organ's log + the
# LATEST.md digest block it feeds. The organ FIRES from run_naive_organ_step()
# below, wired into the live publish cycle.
NAIVE_ORGAN_LOG = PROJECT_DIR / "docs" / "observability" / "naive_organ_log.jsonl"
ORGAN_BLOCK_START = "<!-- NAIVE_ORGAN_ASKS -->"
ORGAN_BLOCK_END = "<!-- /NAIVE_ORGAN_ASKS -->"
# G5_effort_sizing_discipline (L2): remaining-effort / estimate-vs-actual /
# XL-decompose-signal digest block, same block-managed-in-LATEST.md pattern
# as the naive-organ block above. Rendering lives in
# background/effort_digest.py; the numbers come from tools/effort_calibration.py.
EFFORT_BLOCK_START = "<!-- EFFORT_SIZING_DIGEST -->"
EFFORT_BLOCK_END = "<!-- /EFFORT_SIZING_DIGEST -->"
# Change-detection gate (DIRECTOR_SEQUENCE_AND_TOKEN_ECONOMY.md, 2026-07-08):
# the sim is deterministic over frozen historical data, so every ~10-min cycle
# produced a byte-identical £1,535,308 result and yet still regenerated every
# report/site artifact, ran the test suite, and committed -- dozens of identical
# commits per day, pure token/CI burn. This file stores a fingerprint of the
# last FULLY-processed run; a new run whose fingerprint matches is skipped
# (one log line, marker archived, no regen/test/commit). The fingerprint
# deliberately does NOT key on the marker's git_hash -- that advances every
# cycle from the auto-commit itself, so it could never dedup -- and DOES include
# the UTC date so the once-per-day legitimate advances (rolling Elexon SSP
# fetch, live-decision days_to_renewal / market_data_stale_days) still produce
# exactly one processed commit per day.
LAST_FINGERPRINT_FILE = PROJECT_DIR / "docs" / "observability" / ".last_processed_fingerprint.json"
# No-orphan-transitions fix (2026-07-10, CLAIM_EQUALS_PIXEL.md/END_TO_END_
# VERIFICATION.md, director-flagged incident): the change-detection gate
# above is correct in general, but it has no concept of "the CODE changed
# even though headline figures barely moved" -- releasing a publish hold
# (docs/review_gates/.sim_runner_hold) after a fix whose real-world P&L
# impact happens to be small silently produced a fingerprint match against
# the pre-fix run, so the hold-release triggered nothing and the live site
# stayed on stale, pre-fix figures for hours. background/sim_runner.py now
# touches this flag the moment it detects a hold was just cleared; the next
# _process() call consumes it (bypassing the fingerprint-skip check exactly
# once, regardless of whether the figures look identical) and deletes it, so
# a hold-release always forces a real regen/test/commit/deploy.
FORCE_REPUBLISH_FLAG = PROJECT_DIR / "docs" / "review_gates" / ".force_republish_once"
# DEPLOY_CONTENTION_BATCH_COMMITS.md (2026-07-04): sim_runner cycles every
# ~10 min and each cycle committed+pushed unconditionally (LATEST.md's
# timestamp always differs), giving ~6 pushes/hour -- enough to contend with
# GitHub Pages' build throttling (58 failed "Deploy to GitHub Pages" runs,
# each superseded by the next push before it finished) and to burn through
# Cloudflare Pages' free-tier build quota. Commits still happen every cycle
# (free, local, no deploy trigger) but the push itself -- the thing that
# actually fires a Pages/Cloudflare build -- is throttled to at most once
# per PUSH_THROTTLE_SECONDS; the next successful push carries every commit
# accumulated since the last one.
PUSH_THROTTLE_SECONDS = 30 * 60
# The publish commit runs the FULL pre-commit hook chain (tools/git-hooks/pre-commit:
# status-honesty, pre_commit_test_gate, level_promotion_gate, site_lane_gate,
# moap_coherence_gate, ruling_archive_question_gate). Because a publish stages
# site/data/**, site_lane_gate takes its BROAD branch and runs the whole site suite --
# 27.3s measured on its own, 2026-08-03, against the 30s cap this call used to carry.
# The old cap was chosen when the hooks were trivial; it silently became a function of
# how many tests exist rather than of whether the commit is healthy, and a timeout there
# was UNCAUGHT (see git_commit_push) so it took the whole publish down as rc=1.
# Sized to BOTH constraints: ~10x the measured hook-chain cost (so growth in the suite
# does not silently re-create the wedge), while still fitting inside the 900s cap
# background_worker.py::process_leftover_run_markers puts on this whole process -- the
# fast-test gate already spends ~420s of that. A cap larger than the caller's budget
# would just move the kill one level up and lose the log line that explains it.
#
# LIVENESS MUST NEVER BE EASIER TO PUBLISH THAN CONTENT (2026-08-13, director; the eighteen-hour
# freeze). This constant was 300s and `_commit_and_push_paths` -- the heartbeat and the banner --
# hard-coded 600s for the SAME hook chain. Nobody chose that asymmetry; the two numbers were
# written months apart. But it is the precise shape that manufactures a masked freeze: as the
# chain slows, it crosses the CONTENT threshold first and the LIVENESS one second, so there is a
# whole band of hook-chain cost in which the site's "I am alive" signal publishes on schedule and
# its figures cannot publish at all. On 2026-08-12 the chain entered that band and stayed there:
# twenty-one consecutive content commits killed at 300s, and a `chore(liveness)` heartbeat landing
# on origin every thirty minutes throughout.
#
# So the two paths now share ONE number, and the invariant is stated as a test rather than as a
# comment (`test_liveness_is_never_easier_to_publish_than_content`): whatever budget the liveness
# commit gets, the content commit gets at least as much. Set to the larger of the two former
# values -- widening content, never narrowing liveness, because the failure being closed is
# content dying early and the correct direction of a fix that could be wrong is "publish the
# figures too". It still fits inside the 900s cap `background_worker.py::process_leftover_run_
# markers` puts on this whole process.
#
# 600 -> 840 (2026-08-25), AND THE NUMBER IS THE SMALL HALF OF THIS CHANGE. Publishing was down
# 12.2 hours across twelve consecutive `commit_did_not_land` episodes with `total_red: 0` and the
# publisher's own scoped suite GREEN every time. The cause was this deadline: the hook chain runs
# a full test gate and was outrunning 600s. `docs/observability/publish_gate_duration.jsonl` shows
# the publisher's own comparable gate at 456s at 07:42 and 557s at 17:38 ON THE SAME DAY -- a 22%
# rise in ten hours -- so 600 had stopped being a deadline and become a coin toss on machine load.
#
# WHAT WAS NOT DONE, because the director ruled on it (2026-08-21): *"A 75-minute gate is absurd
# on its face and neither of us said so."* NO GATE BUDGET GROWS HERE. `GATE_SUITE_TIMEOUT_SECONDS`
# is untouched at 3800 and `PUBLISH_PATH_TIMEOUT_SECONDS` at 4700. 840 fits inside the 900s the
# publish path ALREADY reserves for everything after the gate, so this takes room that was
# allocated rather than asking for more -- and `test_the_deadline_leaves_room_for_the_publish_
# path_after_the_gate` still holds.
#
# AND THE REAL REPAIR IS NOT THIS. The publisher pays for TWO full suite runs per cycle: its own
# scoped gate, and then a comparable chain again inside `git commit`. Halving that is the fix with
# headroom in it; raising a deadline only buys time against a curve that is still rising. That
# change touches the commit gate, which is a wall, and needs its own design and its own controls.
# Recorded here so the next reader knows this constant is a STOPGAP with a measurement behind it,
# not an answer.
#
# THE MEASUREMENT THAT WAS MISSING is now taken: `_record_commit_hook_duration` times this call
# and records it against THIS deadline, so the hook chain's cost is observed rather than inferred
# from the publisher's separate gate. Twelve timeouts happened with nothing recording how long the
# thing that timed out actually took.
#: The worst comparable full-suite gate run measured on this machine, WITH THE DATE IN THE NAME.
#: The constant this replaces was `measured_hook_chain_seconds = 30  # ... 2026-08-03`, and its
#: date sat in a comment nobody re-read while the real cost grew twentyfold. A date in the
#: IDENTIFIER is visible at every call site and in every diff.
#: Source: `docs/observability/publish_gate_duration.jsonl`, worst of the last twenty runs on
#: 2026-09-04 (674s; the same series read 557s on 2026-08-25, so the chain grew 21% in ten days).
#: RE-MEASURED 2026-09-04 because the live half of the control had gone red, not because the
#: staleness assert tripped: `worst <= 1.6 * MEASURED` was still green at 674/557 = 1.21x. The
#: number was re-taken while it could still be taken calmly.
MEASURED_GATE_SECONDS_2026_09_04 = 674

#: How much room the deadline must have over measured reality. 1.25 rather than the old 5x: a
#: large multiple over a small stale number is what made the previous control unable to fail.
COMMIT_DEADLINE_HEADROOM = 1.25

# THIS IS THE LAST RAISE THAT FITS. 880 IS NOT A ROUND NUMBER, IT IS THE CEILING MINUS THE PUSH.
#
# 840 (14 min) went red on 2026-09-04: 1.25 * 674 = 843, so the deadline was three seconds under
# its own floor and every publish commit was refused by the control rather than by a hook. Four
# hours of publishing, fourteen queued runs.
#
# THE BOX THIS NUMBER NOW SITS IN, both walls measured, not asserted:
#   * FLOOR   843s -- COMMIT_DEADLINE_HEADROOM * MEASURED_GATE_SECONDS_2026_09_04, rising with
#     the suite. At the observed +21%/10d it reaches 880 in roughly a week.
#   * CEILING 900s -- PUBLISH_PATH_ALLOWANCE_SECONDS. `test_the_deadline_leaves_room_for_the_
#     publish_path_after_the_gate` requires slack >= this deadline, and the allowance may not
#     grow: the director ruled on 2026-08-21 that no gate budget grows here ("A 75-minute gate is
#     absurd on its face and neither of us said so"). GATE_SUITE_TIMEOUT_SECONDS stays 3800 and
#     PUBLISH_PATH_TIMEOUT_SECONDS stays 4700.
# 880 leaves the 20s the post-gate push actually costs. The room between floor and ceiling is now
# 57 seconds, and the next raise does not exist.
#
# SO THE NEXT READER DOES NOT GO LOOKING FOR ONE: when this reds again, raising it is not
# available and neither is growing the allowance. The repair is the one the 2026-08-25 note above
# already named and deferred -- the publisher pays for TWO comparable full-suite runs per cycle,
# its own scoped gate and then the hook chain again inside `git commit`. Halving that is the only
# move that creates room. It touches the commit gate, which is a wall, so it needs its own design
# and its own controls. Filed: docs/staging/SEAT_FINDING_THE_COMMIT_DEADLINE_IS_BOXED_BETWEEN_TWO
# _CONTROLS_AND_THE_ROOM_IS_57_SECONDS_2026-09-04.md.
GIT_COMMIT_HOOK_TIMEOUT_SECONDS = 880


# THE KILL'S OWN DIAGNOSTIC WAS BLOCK-BUFFERED AWAY (2026-08-13, R15 fail-silent).
#
# The TimeoutExpired handler below has promised, since H30, to print "hook output before the
# kill (names the SLOW hook)". It has never once delivered it. Both of today's kills
# (sim-runner-log.md, 2026-08-13 01:30 UTC and 2026-08-12) logged the fallback branch --
# "hook output: nothing captured before the kill" -- so seven commit timeouts have named the
# chain and never the link, and diagnosing which hook is slow costs a whole tick each time.
#
# The cause is NOT that the streams are dropped. `subprocess.run(capture_output=True,
# timeout=N)` does populate `TimeoutExpired.stdout/.stderr` on this platform, and
# `child_diagnostics.stderr_tail` already decodes the bytes it hands back undecoded. Measured
# on this box (python 3.14.4), a child that prints and then hangs:
#
#     default                -> exc.stdout = None
#     PYTHONUNBUFFERED=1     -> exc.stdout = b'HOOK: pre_commit_test_gate starting\n'
#
# Every hook in the chain is `python3 tools/<gate>.py`. Python block-buffers stdout when it is
# a pipe rather than a tty, so each hook's progress sits in the HOOK's own 8KB userspace buffer
# and dies with it -- unflushed bytes are not in the pipe for the kill path to collect. The
# capture was correct; there was simply nothing on the wire. A diagnostic that exists only on a
# tty is a diagnostic that is absent from every autonomous run, which is all of them.
#
# git passes its environment to its hooks, so setting this on `git commit` reaches every link.
# FAIL-SAFE: unbuffering can only make output arrive EARLIER; it cannot change a hook's verdict,
# so the worst case of getting this wrong is a slightly slower write, never a wrong commit.
GIT_COMMIT_HOOK_ENV_UNBUFFERED = "PYTHONUNBUFFERED"


def _commit_hook_env(base=None):
    """The environment `git commit` runs its hook chain under — the inherited environment
    plus unbuffered hook stdout, so a hook killed by the deadline has already put its progress
    on the wire. Never mutates the caller's environment."""
    env = dict(os.environ if base is None else base)
    env[GIT_COMMIT_HOOK_ENV_UNBUFFERED] = "1"
    return env
# H15_publish_gate_failure_alert (2026-07-14): the publish gate (fast-test
# suite + the processor's return code) can fail SILENTLY and repeatedly. The
# real worked example was pytest OOM-killed (rc=-9 -> "Tests FAILED - not
# committing") every ~10-min cycle for ~45min while run_complete markers piled
# up unpublished with NO alert -- a silent pipeline wedge. This state file
# tracks recent consecutive publish-gate FAILURES: N within a window fires ONE
# [ACTION NEEDED] alert (re-armed by a cooldown so a persistently-wedged
# pipeline can't spam), and a clean publish CLEARS it. R15: the mechanism is
# mutation-tested to FIRE on N consecutive failures, to NOT fire on a single
# transient failure or after recovery, and to FAIL-CLOSED (fire on the first
# failure) when its own gate-state file is unreadable rather than silently
# resetting the counter -- an unavailable check is a failed check.
PUBLISH_GATE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_gate_state.json"
PUBLISH_GATE_FAILURE_THRESHOLD = 3          # N consecutive failures inside the window
PUBLISH_GATE_WINDOW_SECONDS = 60 * 60       # 1h: a wedge fails every ~10min, so 3/hour is the signal
PUBLISH_GATE_COOLDOWN_SECONDS = 60 * 60     # re-arm: at most one alert NTFY per hour while it stays wedged
PUBLISH_GATE_ITEM_ID = "publish_gate_wedged"

# ── EPISODE MEMORY + ALARM→DIAL (2026-08-09, DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH) ──
# The census that produced this: 10 wedge alarms on 2026-08-08 across a SEVEN-HOUR live
# episode, and 150 in the mirror lifetime including an unbroken hourly wall across Aug 1-3.
# Every one of them was TRUE and every one described a 60-minute window, so a seven-hour
# episode narrated itself, ten times, as a fresh hour. Two properties close that:
#
#   (a) EPISODE MEMORY -- the alarm carries `wedge_since` (already persisted, never
#       surfaced), `episode_failures` (the whole streak, NOT the window-trimmed `failures`
#       list) and `markers_pending` (run_complete markers piling up unpublished). A reader
#       can then tell hour one from hour seven without correlating ten pages by hand.
#   (b) ALARM->DIAL -- the alarm ENUMERATES the filed findings sitting unactioned in
#       docs/staging/ and persists them to the state file, where the supervisor's RUNG-1
#       unwedge draw reads them back and names them as the work. On 2026-08-08 the cure for
#       this exact wedge sat filed as WORKER_FINDING_RUFF_RATCHET_RED_AT_HEAD while the
#       chronic red lost every draw to feature work. An alarm that only addresses the
#       director cannot raise its own cure's priority; this one does.
PUBLISH_GATE_FINDING_GLOB = "WORKER_FINDING_*.md"
PUBLISH_GATE_MAX_CITED_FINDINGS = 8   # bounded: an alarm is a page, not a directory listing

# ── Publish-gate BLOCKING SCOPE (R10 class closure, 2026-07-18) ───────────────
# The overnight wedge (2026-07-16, TONIGHT_FIXES.md Item 4 + follow-up L166-171)
# had a STRUCTURAL root, not just the watchdog import bug that triggered it: the
# publish gate ran the ENTIRE ~18k-test suite with `-x`, so ONE red test ANYWHERE
# -- including the operational layer that validates the DAEMONS, never the
# published CONTENT -- wedged the live-site publish for hours (a daemon-lifecycle
# watchdog test raised AttributeError and blocked publishing ~21x overnight while
# the site went stale). The gate's remit is "do not ship a broken SURFACE";
# daemon/session lifecycle health is a SEPARATE concern already covered by
# health_check monitoring and the H22 3.7 red-gate-test sweep.
#
# The partition is keyed on WHAT A TEST VALIDATES, not its directory -- because
# tests/background MIXES daemon-lifecycle tests (which must not wedge publishing)
# with a handful of CONTENT-validating ones (test_effort_digest renders the
# EFFORT SIZING block into LATEST.md; test_atom_status_merge folds published atom
# level_current; test_status_honesty is the LATEST.md honesty gate). A directory
# ignore would fail-OPEN on those -- worse than the wedge. So the unit is an
# EXPLICIT, greppable `@pytest.mark.operational` marker on each daemon-lifecycle
# test module; the gate runs `-m "not operational"`. Content-, surface-generating,
# and safety-WALL tests stay UNMARKED and therefore keep BLOCKING.
#   * HEAVY ignores  -- excluded for SPEED (full-sim integration tests, 150-480s each).
#   * operational marker -- excluded for SCOPE (this class closure).
# The legitimate gate is UNCHANGED: any red publish-SURFACE test still blocks the
# publish (do not ship broken/wrong content), alarms transition-only (R5), and
# clears on the next clean publish (R11 release path).
PUBLISH_GATE_HEAVY_IGNORES = [
    "tests/simulation/test_run_phase2b.py",
    "tests/simulation/test_run_phase2b_event_log.py",
    "tests/simulation/test_run_phase4c_on_phase2b.py",
    "tests/simulation/test_phase40b_gas_pass_through.py",
    "tests/simulation/test_phase24a_ic_customer.py",
    "tests/simulation/test_phase40a_pass_through.py",
    "tests/simulation/test_phase40c_deemed_rate.py",
    "tests/simulation/test_phase41a_flex.py",
]
# Deselect the daemon-lifecycle layer by MARKER (see @pytest.mark.operational,
# registered in tests/conftest.py). Keyed on what a test validates, not its path.
#
# `join_report_only` (2026-08-08, AO3_join_test_tier) is the SECOND deselected
# class and is deliberately TEMPORARY. The director pre-ruled the join tier's
# first landing report-only -- join tests may be brittle at first, and a red one
# would otherwise wedge the live-site publish -- so tests/system/** alarms but
# cannot block. Drop this conjunct once the tier has run a stable week; the delay
# is the director's, not a judgement call (docs/design/JOIN_TEST_TIER.md §3).
#
# `scale_report_only` (2026-08-09, AO4_scale_constraints_executable) is the THIRD,
# on the same terms and for the same reason: the five production-readiness
# constraints (C-S1..C-S5) land as checks that MEASURE the tree as it is, and two
# of them are red on arrival by design -- one of them is the money-in-duplicate
# drift the director cites by name. Softening a check because it went red on
# landing would be R12. Deselecting it is how a truthful red alarms without
# wedging the live site. It carries its OWN marker rather than reusing the join
# tier's so the two tiers promote on their own stable weeks -- one marker would
# mean promoting either promotes both.
#
# Adding a deselected class opens a fail-open channel by construction: any content
# test could be silenced by taking the marker. Closed by CONTAINMENT -- no module
# outside tests/system/ may carry either (tests/system/test_report_only_landing.py,
# mutation-proven both ways).
PUBLISH_GATE_MARKER_EXPR = (
    "not operational and not join_report_only and not scale_report_only"
)


# WHAT A PUBLISH GATE IS FOR (director, 2026-08-21: *"Say what the gate is actually for and how
# long that should take."*)
#
# It answers ONE question: would publishing this run put a wrong number or a false claim in
# front of a reader? That is a question about the OUTPUT, not about whether all the code in the
# repository is correct.
#
# I ADDED A HAND-WRITTEN `PUBLISH_GATE_SCOPE` HERE AND DELETED IT AGAIN THE SAME DAY. It was
# sixteen hand-listed paths, and it was dead: the gate's real entry point `_scoped_gate_argv()`
# passes `"tests/"` explicitly, so the default was never read. Worse, it duplicated
# `background/publish_scope.py`, which has done this since 2026-08-10 and does it BETTER --
# resolving publish-path sources to blocking test files through the static import graph, so the
# set is DERIVED and cannot go stale the way a hand list does. I wrote a long note calling my
# version the answer without discovering the one already there.
#
# So the scope lives in `publish_scope.resolve_scope()` and nowhere else. The remaining work
# the director asked for is to narrow what THAT resolves to (currently 6 sources -> 199 test
# files, ~21 minutes), not to add a second opinion beside it.
#
# The rest of the split stands and is unchanged by any of this: code correctness -> commit time
# (stem selection); repo-wide invariants -> commit time (the always-run list); daemon health ->
# the `operational` marker on its own cadence; everything, unscoped and with no -x -> the
# nightly head-green-census, which is deliberately the WIDER of the two and must never be
# narrowed to match the gate.


def publish_gate_pytest_argv(test_root="tests/"):
    """The exact pytest argv the publish gate runs. Factored out so the blocking SCOPE is a
    single testable surface (R15: a control's scope must be inspectable).

    This builds the UNSCOPED argv. The gate does not run it as-is: `_scoped_gate_argv()` takes
    it as a base and narrows it through `publish_scope.resolve_scope()`. Timing this function is
    therefore NOT timing the gate -- doing exactly that on 2026-08-21 produced a 300s bound off
    a ~40s measurement and wedged publishing twice.
    """
    argv = [sys.executable, "-m", "pytest", test_root, "-x", "-q", "--tb=short",
            "-m", PUBLISH_GATE_MARKER_EXPR]
    for ignore in PUBLISH_GATE_HEAVY_IGNORES:
        argv.append("--ignore=" + ignore)
    return argv


# ── H23_publish_gate_scope_marker (L3): independent-cadence green signal for
# the DESELECTED operational layer ────────────────────────────────────────────
# The partition above is correct SCOPE (a red daemon-lifecycle test must never
# wedge the live-site publish) but leaves an R11 orphan on its own: deselected
# from the content gate must not mean uncovered by ANY gate. This gives the
# operational layer (`pytest -m operational`) its own, independent-cadence
# green signal, wired onto the existing deadman's-switch timer
# (background/deadmans_switch.py::run_cycle -> _check_operational_layer_signal),
# NOT onto every 5-min deadman cycle or every content-publish cycle -- the
# suite is slow, so it self-throttles to at most once per
# OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS via a last-run timestamp in its own
# state file (the same throttle shape as _push_due()/LAST_PUSH_FILE above).
#
# R5 transition-only + persistent-red paging: a SINGLE red result is logged
# and recorded to state but never pages -- a lone flake must not page. Only a
# PERSISTENT red (>= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD consecutive
# checks) fires a real_alarm through the one notify() contract, keyed so an
# unchanged RED never re-pages faster than OPERATIONAL_LAYER_RE_ESCALATE_
# SECONDS. Recovery (red -> green) after a persistent-red page is itself a
# transition and pages once.
#
# DECOUPLING (by construction, not just convention): this signal owns its own
# state file (OPERATIONAL_LAYER_STATE_FILE, distinct from PUBLISH_GATE_STATE_
# FILE), its own pytest argv (the marker-expression COMPLEMENT of the content
# gate's), and is never called from anywhere in the commit/push/report/site
# regeneration path above -- it cannot block, skip, or alter what the content
# gate publishes, and a red result here can never touch content_gate_pytest_
# argv's own -m expression or PUBLISH_GATE_STATE_FILE. Purely observational.
OPERATIONAL_LAYER_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".operational_layer_signal.json"
# The TRUE complement of PUBLISH_GATE_MARKER_EXPR, and it has to stay true: this
# signal exists because "deselected from the content gate" must never mean
# "covered by NO gate" (R11, no orphan transitions). When the join tier joined the
# deselected set (2026-08-08, AO3_join_test_tier) this expression had to widen with
# it -- `not (A and B)` is `(not A) or (not B)` -- or tests/system/** would have
# been dropped from the content gate AND never picked up here, which is strictly
# worse than leaving it blocking. Drops back to plain "operational" when the join
# tier is promoted out of report-only (docs/design/JOIN_TEST_TIER.md §3), and it
# widened again for the scale tier on the same rule (2026-08-09,
# AO4_scale_constraints_executable) -- a deselected marker that is not also added
# HERE orphans the tier it deselects, which is the whole defect this expression
# exists to prevent (`feedback_deselecting_a_marker_orphans_the_tier`).
OPERATIONAL_LAYER_MARKER_EXPR = "operational or join_report_only or scale_report_only"
OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS = 60 * 60   # hourly -- suite is slow; deadman cycles every 5min
OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD = 2       # consecutive red checks before paging (no single-flake page)
OPERATIONAL_LAYER_RE_ESCALATE_SECONDS = 60 * 60      # re-page hourly while red persists (matches deadman cadence)
OPERATIONAL_LAYER_TRANSITION_KEY = "operational_layer_signal"
OPERATIONAL_LAYER_DIGEST_MAX_LINES = 12              # failure lines carried into the log + RED page (R5 payload)

# R5 THE ALERT MUST CARRY ITS OWN DIAGNOSTIC PAYLOAD (2026-08-08, worker tick).
# This signal paged RED four times carrying `rc=1` and nothing else, because the
# runner discarded the subprocess's output -- so every page said "something under
# `-m operational` failed, go look" and a whole diagnostic tick was spent
# rediscovering a cause the failing run had already printed. Identical in class to
# the sim_runner finding of the same day (WORKER_FINDING_SIM_RED_LOOP_ROOT_CAUSE):
# a monitor whose only artefact is a return code cannot satisfy R5, however
# correct its transition logic is.
_OPERATIONAL_LAYER_NO_OUTPUT = "(no output captured from the run -- cause unavailable)"

# PW4 -- THE CLOSE CONDITION for the operational-layer red episode.
#
# `consecutive_red` is an episode counter (>=OPERATIONAL_RED_DRAWABLE_THRESHOLD makes the
# supervisor draw it at priority zero) and this module read-modify-writes it, so the census
# flags it as self-clearing. Guarding it needs an answer to "what EVIDENCES that the red
# episode ended", and for THIS control `rc == 0` is not that answer.
#
# WHY NOT rc == 0: pytest exits 0 when every selected test SKIPPED. The operational marker
# selects daemon-lifecycle tests -- exactly the tests most likely to skip themselves when the
# thing they drive (tmux, a systemd unit, a live daemon) is absent. That is the R15 FAIL-OPEN
# pattern in its purest form: the check passes on empty. A green that executed nothing is
# indistinguishable, at rc level, from a green that proved the daemons recovered, and only one
# of those is evidence the red is over.
#
# THE CONDITION: rc == 0 AND the run reports at least one test PASSED. Independent of
# `.operational_layer_signal.json` by construction (R15 anti-tautology) -- it is read off the
# subprocess's own summary line, never off the state whose episode it closes.
#
# FAIL DIRECTION: toward REMEMBERING the episode. An unparseable/absent summary means we
# cannot demonstrate a recovery, so the episode stands. That deliberately cannot wedge the
# alarm permanently the way an always-red detector would: the counter simply stops moving in
# either direction until a parseable green arrives, and the vacuous green is LOGGED by name so
# the state is diagnosable rather than mute.
_PYTEST_PASSED_RE = re.compile(r"(\d+) passed")


def operational_layer_passed_count(result):
    """How many tests the operational run actually PASSED, or None if it cannot be told.

    None and 0 are opposite facts here and are kept apart on purpose: 0 means the run
    demonstrably passed nothing (all skipped/deselected), None means the run's own output was
    unavailable, so the question is unanswered. Neither closes an episode; only a positive
    count does."""
    chunks = []
    for attr in ("stdout", "stderr"):
        val = getattr(result, attr, None)
        if isinstance(val, bytes):
            val = val.decode("utf-8", "replace")
        if isinstance(val, str) and val.strip():
            chunks.append(val)
    if not chunks:
        return None
    matches = _PYTEST_PASSED_RE.findall("\n".join(chunks))
    if not matches:
        return None
    return max(int(m) for m in matches)


def operational_layer_episode_closed(result, rc):
    """The named close condition, in one place so the test can put it on trial directly."""
    return rc == 0 and (operational_layer_passed_count(result) or 0) >= 1


# THE VACUOUS RED -- the exact mirror of the PW4 vacuous-green guard above
# (2026-08-20, WORKER_FINDING_A_SALVAGE_PARKED_THE_PRODUCER_HALF_AND_LEFT_THE_CONSUMER_HALF_IN_THE_TREE).
#
# PW4 asks "did this green actually RUN anything?" because rc==0 is fail-open on an empty
# run. Nobody was asking the same question of a RED, and rc!=0 is fail-open in the mirror
# direction: it cannot tell "the operational layer regressed" from "pytest never got as far
# as selecting the operational layer".
#
# THE OBSERVED DEFECT. `operational_layer_pytest_argv()` is the marker COMPLEMENT of the
# content gate, and that independence is real at SELECTION time -- but it does not survive
# COLLECTION. Two unimportable files under `tests/company/` (a KNIFE3 salvage that parked a
# producer and left its consumers in the tree) interrupted collection, so pytest reported
# `26758 deselected ... 2 errors` and exited non-zero having run NO operational test at all.
# The signal recorded a red, the red went persistent, and `docs/observability/supervisor-log.md`
# carries 23 PERSISTENT-RED pages dated 2026-08-20 -- every one of them naming a
# daemon-lifecycle regression that did not exist, against an operational layer that was never
# actually exercised. An import error UPSTREAM of selection reports as the selected suite's
# failure.
#
# WHAT THIS CHANGES, AND WHAT IT DELIBERATELY DOES NOT. It does NOT make the run green:
# an unavailable check is a FAILED check (R15 fail-silent doctrine), the suite is genuinely
# unmonitored while collection is broken, and that must still escalate on the same cadence.
# `consecutive_red` therefore keeps incrementing exactly as before. What changes is the
# DIAGNOSIS the page carries (R5: the alert names its own cause), because the cost here was
# never the paging -- it was 23 pages pointing the drawn worker at the wrong subsystem, the
# failure mode `supervisor.py`'s own draw comment already warns about ("the drawn worker
# reads BLOCKING TEST: x and repairs x").
#
# INDEPENDENCE (R15 anti-tautology): read off the subprocess's own output, never off
# `.operational_layer_signal.json` -- the same construction, and the same reason, as the
# pass-count above.
_PYTEST_COLLECTION_INTERRUPT_RE = re.compile(
    r"Interrupted:\s*\d+\s+errors?\s+during\s+collection", re.I)
#: pytest names each uncollectable file on its own `ERROR <path>` line.
_PYTEST_COLLECT_ERROR_FILE_RE = re.compile(r"^ERROR\s+(\S+)", re.M)


def _operational_layer_result_text(result):
    """The run's combined stdout+stderr, or "" when it captured nothing."""
    chunks = []
    for attr in ("stdout", "stderr"):
        val = getattr(result, attr, None)
        if isinstance(val, bytes):
            val = val.decode("utf-8", "replace")
        if isinstance(val, str) and val.strip():
            chunks.append(val)
    return "\n".join(chunks)


def operational_layer_collection_blocked(result, rc):
    """The files that stopped this run REACHING the operational layer, or () if it got there.

    Non-empty means the red is VACUOUS: pytest was interrupted during collection, so the
    marker expression never selected anything and the run is evidence of nothing about the
    operational layer either way.

    FAIL DIRECTION: toward calling it an ordinary red. A run whose output is unavailable, or
    whose interrupt banner cannot be parsed, returns () and is reported as a plain
    operational-layer failure -- under-claiming "the signal was blocked" is the safe error,
    because that claim is the one that would excuse a real regression."""
    if rc == 0:
        return ()
    text = _operational_layer_result_text(result)
    if not text or not _PYTEST_COLLECTION_INTERRUPT_RE.search(text):
        return ()
    return tuple(dict.fromkeys(_PYTEST_COLLECT_ERROR_FILE_RE.findall(text)))


def operational_layer_failure_digest(result, max_lines=OPERATIONAL_LAYER_DIGEST_MAX_LINES):
    """The failing-run payload carried into the log and the RED page.

    Prefers pytest's own `short test summary info` FAILED/ERROR lines (the
    densest naming of the defect); falls back to the tail of combined output
    when that section is absent (a collection error, an interpreter crash, a
    timeout). FAIL-LOUD, never fail-silent (R15): when no output is available
    at all -- an injected runner that returns only a returncode, a killed
    process -- it returns an explicit "cause unavailable" marker rather than
    an empty string that would read in the page as "nothing to report"."""
    chunks = []
    for attr in ("stdout", "stderr"):
        val = getattr(result, attr, None)
        if isinstance(val, bytes):
            val = val.decode("utf-8", "replace")
        if isinstance(val, str) and val.strip():
            chunks.append(val)
    if not chunks:
        return _OPERATIONAL_LAYER_NO_OUTPUT

    lines = [ln.rstrip() for ln in "\n".join(chunks).splitlines() if ln.strip()]
    summary = [ln for ln in lines if ln.startswith(("FAILED", "ERROR"))]
    picked = summary[:max_lines] if summary else lines[-max_lines:]
    if not picked:
        return _OPERATIONAL_LAYER_NO_OUTPUT
    omitted = len(summary) - len(picked) if summary else 0
    if omitted > 0:
        picked = picked + ["... and {} more failing test(s)".format(omitted)]
    return "\n".join(picked)


def operational_layer_pytest_argv(test_root="tests/"):
    """The exact pytest argv the independent operational-layer signal runs --
    the COMPLEMENT of publish_gate_pytest_argv's deselection above. Factored
    out for the same reason (R15: a control's scope must be inspectable)."""
    return [sys.executable, "-m", "pytest", test_root, "-q", "--tb=short",
            "-m", OPERATIONAL_LAYER_MARKER_EXPR]


def _read_operational_layer_state():
    """FAIL-CLOSED read (R15 fail-silent doctrine, same shape as
    _read_publish_gate_state above): an unreadable/corrupt state file resets
    the streak counters to zero rather than assuming a prior green, and
    reports state_unavailable=True so a caller can choose to treat it as due
    immediately rather than silently skip."""
    if not OPERATIONAL_LAYER_STATE_FILE.exists():
        return {"last_run_ts": None, "last_result": None, "consecutive_red": 0,
                "consecutive_green": 0, "state_unavailable": False}
    try:
        st = json.loads(OPERATIONAL_LAYER_STATE_FILE.read_text())
        if not isinstance(st, dict):
            raise ValueError("operational-layer state is not an object")
        st.setdefault("last_run_ts", None)
        st.setdefault("last_result", None)
        st.setdefault("consecutive_red", 0)
        st.setdefault("consecutive_green", 0)
        st["state_unavailable"] = False
        return st
    except (json.JSONDecodeError, OSError, ValueError):
        return {"last_run_ts": None, "last_result": None, "consecutive_red": 0,
                "consecutive_green": 0, "state_unavailable": True}


OPERATIONAL_LAYER_STREAK_FIELDS = ("consecutive_red",)


def _write_operational_layer_state(state, *, episode_closed=False):
    """Persist the signal state, with the PW4 guard on the red episode counter.

    `episode_closed` is `operational_layer_episode_closed(...)` -- the caller's EVIDENCED claim
    that a green actually executed something. Only `consecutive_red` is guarded:
    `consecutive_green` is not an episode any alarm reads for severity, and resetting a green
    streak over-reports rather than under-reports, which is the direction this class of guard
    deliberately does not police."""
    out = {
        "last_run_ts": state.get("last_run_ts"),
        "last_result": state.get("last_result"),
        "consecutive_red": state.get("consecutive_red", 0),
        "consecutive_green": state.get("consecutive_green", 0),
        # The uncollectable files behind a "red_blocked" (always present, [] when the run
        # reached the suite) so the RUNG 1b draw can NAME them instead of sending the worker
        # to the daemons -- R5's payload requirement applied to the DRAW, not just the page.
        "blocked_by": list(state.get("blocked_by") or ()),
    }
    out = guard_episode(_read_operational_layer_state() if OPERATIONAL_LAYER_STATE_FILE.exists()
                        else None,
                        out,
                        streak_fields=OPERATIONAL_LAYER_STREAK_FIELDS,
                        episode_closed=episode_closed)
    OPERATIONAL_LAYER_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    OPERATIONAL_LAYER_STATE_FILE.write_text(json.dumps(out, sort_keys=True))


def _operational_layer_check_due(now, state):
    """True if the throttle interval has elapsed (or no run is on record, or
    the state file itself was unreadable -- fail toward running the check
    rather than silently skipping it forever)."""
    if state.get("state_unavailable"):
        return True
    last_run = state.get("last_run_ts")
    if last_run is None:
        return True
    try:
        return (float(now) - float(last_run)) >= OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS
    except (TypeError, ValueError):
        return True


def run_operational_layer_signal(*, now=None, runner=None, notify_fn=None, log_fn=None, force=False):
    """Independent-cadence green signal for the DESELECTED operational layer
    (H23 L3). Runs `pytest -m operational`, records green/red to its OWN state
    file, and pages the director ONLY on a PERSISTENT red (>= N consecutive
    checks) -- a single red logs but never pages (R5: no flake pages).
    Recovery (red -> green) following a persistent-red page is itself a
    transition and pages once.

    Deliberately DECOUPLED from the content publish gate: this never runs
    publish_gate_pytest_argv(), never reads/writes PUBLISH_GATE_STATE_FILE,
    and its result cannot reach commit_and_push_if_changed or the report/site
    regeneration path -- nothing in this module calls it from there. Purely
    observational.

    `runner` -- injectable callable(argv) -> object with a `.returncode`
    attribute, defaulting to a real `subprocess.run` of
    operational_layer_pytest_argv(). Tests stub this so the real (slow) suite
    never runs in the unit test. Fully defensive: any internal error is
    logged and swallowed -- a monitoring check must never raise into its
    caller (matches every other check in deadmans_switch.py)."""
    log_fn = log_fn or log
    if notify_fn is None:
        from background.notify import notify as _notify
        notify_fn = _notify
    now = float(now) if now is not None else time.time()
    try:
        state = _read_operational_layer_state()
        if not force and not _operational_layer_check_due(now, state):
            return {"ran": False, "reason": "throttled"}

        if runner is None:
            def runner(argv):
                # capture_output so a red can NAME its cause (R5): without it the
                # subprocess inherits fd 1/2 and the only artefact identifying the
                # failure is written to the daemon's stream and lost unread.
                return subprocess.run(argv, cwd=str(PROJECT_DIR), timeout=1800,
                                      capture_output=True, text=True)
        result = runner(operational_layer_pytest_argv())
        rc = getattr(result, "returncode", None)
        is_green = (rc == 0)
        digest = "" if is_green else operational_layer_failure_digest(result)

        consecutive_red = int(state.get("consecutive_red") or 0)
        consecutive_green = int(state.get("consecutive_green") or 0)
        paged = False
        # PW4: a green only CLOSES the red episode if it demonstrably ran something.
        episode_closed = operational_layer_episode_closed(result, rc)
        blocked_by = operational_layer_collection_blocked(result, rc)

        if is_green and not episode_closed:
            # A VACUOUS GREEN (rc=0, nothing passed). The red episode stands: this run is
            # evidence of nothing, exactly as a lock-skip is evidence of nothing to the publish
            # gate. Recorded by name so the state is diagnosable rather than a mute plateau.
            passed = operational_layer_passed_count(result)
            log_fn(
                "Operational-layer signal: rc=0 but the run demonstrated no recovery ({}) -- "
                "the red episode is PRESERVED at consecutive_red={}, not cleared. A green that "
                "executed nothing cannot close a red episode (PW4)."
                .format("0 tests passed" if passed == 0 else "no pass count in the run's output",
                        consecutive_red))
            _write_operational_layer_state({
                "last_run_ts": now,
                "last_result": "green_unevidenced",
                "consecutive_red": consecutive_red,
                "consecutive_green": consecutive_green,
            }, episode_closed=False)
            return {"ran": True, "green": True, "episode_closed": False, "rc": rc,
                    "consecutive_red": consecutive_red, "consecutive_green": consecutive_green,
                    "paged": False, "digest": ""}

        if is_green:
            was_persistent_red = consecutive_red >= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD
            consecutive_red = 0
            consecutive_green += 1
            if was_persistent_red:
                notify_fn(
                    "[OPERATIONAL LAYER RECOVERED] The independent-cadence operational-layer "
                    "signal (`pytest -m operational`, deselected from the content publish gate) "
                    "is GREEN again after a persistent red. Daemon-lifecycle tests recovered; "
                    "the live site/report was never affected by the prior red.",
                    kind="real_alarm", transition_key=OPERATIONAL_LAYER_TRANSITION_KEY, state="GREEN",
                )
                paged = True
                log_fn("Operational-layer signal: RECOVERED (green after persistent red) -- paged")
            else:
                log_fn("Operational-layer signal: green (consecutive_green={})".format(consecutive_green))
        else:
            consecutive_green = 0
            consecutive_red += 1
            if consecutive_red >= OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD:
                if blocked_by:
                    notify_fn(
                        "[OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer "
                        "signal could not RUN for {} consecutive check(s) (rc={}): pytest was "
                        "interrupted during COLLECTION, so the marker expression `{}` never "
                        "selected anything and NO operational test was executed. This is NOT a "
                        "daemon-lifecycle regression -- nothing about the operational layer has "
                        "been shown to be broken, and the published site/report is unaffected. "
                        "The operational layer is UNMONITORED until these files import cleanly:"
                        "\n{}\n\nRepair the import error at those paths, not the daemons."
                        .format(consecutive_red, rc, OPERATIONAL_LAYER_MARKER_EXPR,
                                "\n".join("  - " + p for p in blocked_by)),
                        kind="real_alarm", transition_key=OPERATIONAL_LAYER_TRANSITION_KEY,
                        state="RED", re_escalate_after=OPERATIONAL_LAYER_RE_ESCALATE_SECONDS,
                    )
                    paged = True
                    log_fn("Operational-layer signal: BLOCKED at collection, persistent ({} "
                           "consecutive) -- paged; the suite never ran. Uncollectable:\n{}"
                           .format(consecutive_red, "\n".join("  - " + p for p in blocked_by)))
                else:
                    notify_fn(
                        "[OPERATIONAL LAYER RED] The independent-cadence operational-layer signal "
                        "(`pytest -m operational`, deselected from the content publish gate so it can "
                        "never wedge the live site) has been RED for {} consecutive check(s) (rc={}). "
                        "This does NOT affect the published site/report -- it is a daemon-lifecycle "
                        "test regression. Failing tests:\n{}"
                        .format(consecutive_red, rc, digest),
                        kind="real_alarm", transition_key=OPERATIONAL_LAYER_TRANSITION_KEY, state="RED",
                        re_escalate_after=OPERATIONAL_LAYER_RE_ESCALATE_SECONDS,
                    )
                    paged = True
                    log_fn("Operational-layer signal: RED, persistent ({} consecutive) -- paged; "
                           "failing:\n{}".format(consecutive_red, digest))
            elif blocked_by:
                log_fn(
                    "Operational-layer signal: BLOCKED at collection (consecutive_red={}, below "
                    "persistent threshold {}) -- logged, not paged; the suite never ran. "
                    "Uncollectable:\n{}".format(
                        consecutive_red, OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD,
                        "\n".join("  - " + p for p in blocked_by)))
            else:
                log_fn(
                    "Operational-layer signal: red (consecutive_red={}, below persistent threshold "
                    "{}) -- logged, not paged (single flake); failing:\n{}".format(
                        consecutive_red, OPERATIONAL_LAYER_PERSISTENT_RED_THRESHOLD, digest))

        # "red_blocked" is recorded as its own value rather than folded into "red": a reader
        # of this state file (and the supervisor draw that reads it) must be able to tell
        # "the operational layer regressed" from "the operational layer was never run",
        # which is the whole distinction this guard exists to make. It is NOT a green -- the
        # streak counters above are untouched by the classification.
        _write_operational_layer_state({
            "last_run_ts": now,
            "last_result": "green" if is_green else ("red_blocked" if blocked_by else "red"),
            "consecutive_red": consecutive_red,
            "consecutive_green": consecutive_green,
            "blocked_by": blocked_by,
        }, episode_closed=episode_closed)
        return {"ran": True, "green": is_green, "episode_closed": episode_closed, "rc": rc,
                "consecutive_red": consecutive_red, "blocked_by": blocked_by,
                "consecutive_green": consecutive_green, "paged": paged, "digest": digest}
    except subprocess.TimeoutExpired as exc:
        # THE RETRY STORM, closed 2026-08-21 (the 34-hour publishing outage).
        #
        # This check is DECOUPLED from the publish gate in state -- it never reads or writes
        # PUBLISH_GATE_STATE_FILE, exactly as the docstring above says. It was never decoupled
        # in RESOURCES, and that is the half that wedged publishing.
        #
        # OBSERVED, not inferred (sim-runner-log.md + .operational_layer_signal.json, 2026-08-21):
        # a timeout landed in the generic handler below, which logged "(swallowed)" and returned
        # WITHOUT writing state. `last_run_ts` therefore never advanced -- measured 6.0h stale
        # against a 1.0h throttle -- so `_operational_layer_check_due()` answered True on EVERY
        # 5-minute deadman cycle and relaunched a 30-minute full-suite pytest each time. The box
        # was occupied near-continuously by a check that has timed out 50 times and produced no
        # verdict since 12:41Z, while the publish gate needed that same box: the gate's own suite
        # then overran 300s, its budget was raised to 3400s to compensate, and it overran that
        # too (17:37Z). 46 refusals, 169 unpublished runs, 34 hours.
        #
        # THE SWALLOW WAS NEVER THE DEFECT -- a monitoring check must not raise into the deadman.
        # The defect is that swallowing also discarded the STAMP, so "could not answer" was
        # indistinguishable from "never asked" and the retry had no throttle. Stamping `now` is
        # what stops the storm: at most one attempt per interval.
        #
        # OWN NAME, SAME CLASS (the EXIT_GATE_TIMED_OUT reasoning at the top of this module,
        # applied to the other clock). NOT folded into "red": nothing about the operational layer
        # has been shown to regress, and a red page sends the reader to the daemons. NOT folded
        # into "red_blocked" either: that means pytest died during COLLECTION and its page names
        # import errors to repair, which would point at files that are fine. A timeout is its own
        # fact -- the suite ran and did not finish.
        #
        # NOT A GREEN, and the streak advances (R15: an unavailable check is a FAILED check). A
        # check that cannot answer must never read as healthy, or this goes silent for another
        # 6 hours -- which is precisely what it just did.
        try:
            prior = _read_operational_layer_state()
        except Exception:
            prior = {}
        consecutive_red = int(prior.get("consecutive_red") or 0) + 1
        log_fn(
            "Operational-layer signal: suite TIMED OUT after {}s -- recorded as 'red_timeout' "
            "(consecutive_red={}) and STAMPED, so the throttle engages and the next attempt is "
            "one interval away, not one deadman cycle. R15: an unavailable check is a failed "
            "check, never a skipped one.".format(getattr(exc, "timeout", "?"), consecutive_red))
        try:
            _write_operational_layer_state({
                "last_run_ts": now,
                "last_result": "red_timeout",
                "consecutive_red": consecutive_red,
                "consecutive_green": 0,
            }, episode_closed=False)
        except Exception as write_exc:
            # The stamp is the whole point, so a failure to write it is loud rather than swallowed
            # into the same silence this handler exists to end.
            log_fn("Operational-layer signal: FAILED to record the timeout stamp ({}) -- the "
                   "retry throttle is NOT engaged for this cycle.".format(write_exc))
        return {"ran": False, "reason": "timeout", "last_result": "red_timeout",
                "consecutive_red": consecutive_red}
    except Exception as exc:
        log_fn("Operational-layer signal check error (swallowed): {}".format(exc))
        return {"ran": False, "reason": "error", "error": str(exc)}


sys.path.insert(0, str(PROJECT_DIR))

from background import (  # noqa: E402
    finding_severity,  # (OPS9 header parser; exoneration field)
    publish_cause,  # (which of the four an rc=77 was, and the observation that decided it)
    publish_gate_blocking_read,  # (the record's honesty contract)
    publish_provenance,  # BOUND HERE ON PURPOSE — see below
)

# ONE GENERATION PER CYCLE (2026-09-01). This was five lazy `from background import
# publish_provenance` statements inside the publish path, and a publish cycle here runs for
# ~25 minutes while other lanes land commits into the same tree. On 2026-09-01 a publisher
# started at 02:40 from pre-merge source, the 02:49 merge rewrote BOTH sides of this call, and
# at 03:05 the lazy import handed that old process the NEW module: an old call site that passes
# no `population` met a new checker that requires one. The stamp was refused by its own
# fail-closed guard, the commit was refused behind it, and the publish gate wedged — with
# nothing in the tree wrong and every test green, which is why it read as self-clearing and
# repeated. sys.modules caches on first import, so binding at module scope pins the module to
# the same generation as the call sites that use it. An old process then publishes an old-shape
# stamp (correct for its own code) and the next cycle upgrades it; a mixed pair is what could
# not be made to work.
from background.child_diagnostics import (  # noqa: E402  (H30)
    STDERR_TAIL_LINES,
    failure_detail,
    stderr_tail,
)
from background.episode_monotonic import guard_episode  # noqa: E402  (PW2)
from background.tree_lock import TreeLockTimeout, tree_lock  # noqa: E402


@contextmanager
def _run_lock():
    """Non-blocking exclusive lock so at most one process_run_complete.py
    instance does the heavy pipeline (report regen, dashboard/site build,
    full test suite -- ~5-10 min) at a time.

    sim_runner.py invokes this script synchronously right after writing a
    run_complete marker. background_worker.py separately sweeps staging/
    every 30 min for "leftover" markers still sitting in the root (the
    marker only moves to done/ at the very end of a successful run) and
    re-invokes this script on any it finds -- with no way to tell a marker
    that is genuinely abandoned (prior invocation crashed/timed out) apart
    from one that is simply still being processed by a live sim_runner
    invocation. Observed directly 2026-07-06: two instances running the
    full pipeline concurrently on the same marker. Losing this lock is not
    an error -- it just means another instance already has the marker in
    hand, so this invocation exits immediately and leaves the marker for
    that instance to archive."""
    RUN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(RUN_LOCK_FILE, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        yield False
        return
    try:
        yield True
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def _run_fingerprint(data):
    """Stable content fingerprint of a run's meaningful outputs + the UTC date.

    Excludes volatile fields (timestamps, marker git_hash). Two runs with the
    same fingerprint would regenerate byte-identical business surfaces, so the
    second is pure burn. Includes the UTC date so a new calendar day always
    processes at least once (carrying that day's live-decision / rolling-fetch
    advance), even if the sim result itself is unchanged.

    AND INCLUDES WHICH WORLD IT RAN IN (2026-09-04). "Byte-identical business surfaces" was the
    whole justification for skipping, and it was measured over headline FIGURES only. A re-fit of
    the departure level that moved the world without moving those figures past their rounding
    would have been skipped as pure burn -- so the first publish carrying the new world's
    disclosure would never have happened, and the page would go on claiming a world that no
    longer existed. That is the residual named at the end of instance 10 of
    `no_caller_and_never_runs`, and it could not be closed until the stamp existed to key to.

    `None` on every run written before that stamp, which is the correct behaviour and not a
    fail-open: an absent world matches an absent world, so the gate behaves exactly as it did
    before for old artefacts, and starts discriminating the moment runs can answer."""
    ret_log = data.get("retention_log", [])
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "world_level_digest": (
            ((data.get("_cache_meta") or {}).get("world_level") or {}).get("digest")
        ),
        "total_net_gbp": round(data.get("total_net_gbp", 0), 2),
        "total_gross_gbp": round(data.get("total_gross_gbp", 0), 2),
        "enterprise_value_gbp": round(data.get("enterprise_value_gbp", 0), 2),
        "final_treasury_gbp": round(data.get("final_treasury_gbp", 0), 2),
        "starting_treasury_gbp": round(data.get("starting_treasury_gbp", 0), 2),
        "total_capital_gbp": round(data.get("total_capital_gbp", 0), 2),
        "net_margin_after_cost_to_serve_gbp": round(data.get("net_margin_after_cost_to_serve_gbp", 0), 2),
        "committee_wake_ups_total": data.get("committee_wake_ups_total", 0),
        "bills_total": data.get("bills_total", 0),
        "offers": len(ret_log),
        "retained": sum(1 for r in ret_log if r.get("outcome") == "retained"),
        "no_offer_churns": len(data.get("no_offer_churn_log", [])),
        "churned_accounts": len(data.get("churned_billing_accounts", [])),
        "administration_event": bool(data.get("administration_event")),
    }


def _read_last_fingerprint():
    if not LAST_FINGERPRINT_FILE.exists():
        return None
    try:
        return json.loads(LAST_FINGERPRINT_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _write_last_fingerprint(fp):
    LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_FINGERPRINT_FILE.write_text(json.dumps(fp, sort_keys=True))


# THE PUBLISH COMMIT MUST NOT ARCHIVE WHAT IT DID NOT AUTHOR (2026-08-18, BLOCKING finding
# WORKER_FINDING_THE_RUN_COMPLETE_SWEEP_STAGES_THE_WHOLE_ARCHIVE_DIRECTORY_AND_COMMITS_WITHOUT_A_PATHSPEC).
#
# `git_commit_push` used to stage `docs/staging/done` as a DIRECTORY, so `git add` swept every
# file underneath it -- including a finding document another lane had moved into `done/` seconds
# earlier and had not committed. Commit `96c665098` did exactly that to two BLOCKING findings
# from two other lanes and carried NEITHER of their repairs.
#
# Moving a document into `done/` is not filing, it is the step that ENDS its drawability: the
# staging scanners read the root, not `done/`. So the sweep performed the one irreversible
# bookkeeping move in this system on documents it did not author and could not check.
#
# The fix is to make the publish structurally incapable of it rather than careful about it: this
# process records the markers IT archived, by name, and the commit list is built from that record.
# A path this process did not move cannot appear in it, whatever else is sitting in `done/`.
_MARKERS_ARCHIVED_BY_THIS_RUN: list[str] = []


def _record_archived_marker(dest):
    """Note that THIS process moved `dest` into done/, so the publish may commit it."""
    path = str(dest)
    if path not in _MARKERS_ARCHIVED_BY_THIS_RUN:
        _MARKERS_ARCHIVED_BY_THIS_RUN.append(path)


def _archive_marker(marker):
    """Move a processed/skipped marker into done/ so markers don't accumulate."""
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    dest = DONE_DIR / marker.name
    try:
        marker.rename(dest)
        _record_archived_marker(dest)
        return True
    except FileNotFoundError:
        if dest.exists():
            _record_archived_marker(dest)
            return True
        return False
    except OSError:
        # Cross-device or similar — fall back to copy + unlink.
        import shutil
        shutil.copy2(str(marker), str(dest))
        marker.unlink(missing_ok=True)
        _record_archived_marker(dest)
        return True


def log(msg):
    # A TEST PROCESS MAY NOT WRITE THE LIVE sim-runner-log (2026-08-21). This is the file the
    # PUBLISHING DOWN alarm sends a human to, and on 2026-08-21 it took six fabricated gate
    # verdicts from pytest tmp roots during a 26-hour publishing outage. Same choke-point
    # refusal as `deadmans_switch.log` and `suite_duration_watch.record` -- one rule for the
    # class, not a third guard. Rationale and both R15 legs:
    # tests/background/test_process_run_complete.py::test_the_live_sim_runner_log_refuses_a_test_process
    dest = guard_live_ledger_write(LOG_FILE, writer="process_run_complete.log")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = "- [{}] [process_run] {}".format(ts, msg)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "a") as f:
        f.write("\n" + entry)
    print(entry, flush=True)


def parse_marker(marker_path):
    text = marker_path.read_text()
    result = {}
    for line in text.splitlines():
        if line.startswith("JSON: "):
            result["json_path"] = Path(line[6:].strip())
        elif line.startswith("Git: "):
            result["git_hash"] = line[5:].strip()
        elif line.startswith("Duration: "):
            m = re.search(r"Duration:\s*([\d.]+)s", line)
            result["elapsed_s"] = float(m.group(1)) if m else 0.0
        elif line.startswith("Finished: "):
            result["finished"] = line[10:].strip()
    return result


def regenerate_report(json_path):
    result = subprocess.run(
        [sys.executable, "-m", "saas.reporting.annual_report", "--from-json", str(json_path)],
        cwd=str(PROJECT_DIR),
        timeout=120,
    )
    return result.returncode == 0


def update_latest_md(data, elapsed_s, git_hash="unknown"):
    text = LATEST_MD.read_text()
    ts_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = re.sub(r"Last updated: \S+", "Last updated: {}".format(ts_now), text)

    ledger = data.get("_ledger_headline", {})
    net = data.get("total_net_gbp", ledger.get("net_margin_gbp", 0))  # total_net_gbp includes bad debt + hedging costs
    gross = ledger.get("gross_margin_gbp", data.get("total_gross_gbp", 0))
    capital = data.get("total_capital_gbp", 0)
    t_start = data.get("starting_treasury_gbp", 0)
    t_end = data.get("final_treasury_gbp", 0)
    committee = data.get("committee_wake_ups_total", 0)
    bills = data.get("bills_total", 0)
    ev = data.get("enterprise_value_gbp", 0)
    net_cts = data.get("net_margin_after_cost_to_serve_gbp", 0)
    ret_log = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])
    churned = data.get("churned_billing_accounts", [])
    mins = elapsed_s / 60

    offers = len(ret_log)
    retained = sum(1 for r in ret_log if r.get("outcome") == "retained")
    no_offer_churns = len(no_offer)
    churn_count = len(churned)

    parts = [
        "**Latest simulation results (2016–2025)** — auto-processed ({:.0f}s / {:.0f} min):".format(elapsed_s, mins),
        "- Net margin: \xa3{:,.2f} | Gross: \xa3{:,.2f} | Capital: \xa3{:,.0f}".format(net, gross, capital),
        "- Treasury: \xa3{:,.0f} → \xa3{:,.0f} | {} committee interventions | {} bills issued".format(t_start, t_end, committee, bills),
        "- Enterprise value: \xa3{:,.2f} | Net after CTS: \xa3{:,.0f}".format(ev, net_cts),
        "- Retention: {} offers, {}/{} retained | {} no-offer churns | {} total churned accounts".format(
            offers, retained, offers, no_offer_churns, churn_count),
    ]
    new_block = "\n".join(parts)

    start_marker = "**Latest simulation results"
    try:
        start_idx = text.index(start_marker)
        end_idx = text.find("\n\n", start_idx)
        if end_idx == -1:
            end_idx = len(text)
        text = text[:start_idx] + new_block + text[end_idx:]
    except ValueError:
        # Block not yet present — append to end on first auto-process
        text = text.rstrip() + "\n\n" + new_block + "\n"
        log("Created 'Latest simulation results' block in LATEST.md")
    # Update "Net position:" summary line in Last Run section
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = re.sub(
        r"Net position: .*",
        "Net position: \xa3{:,.0f} (git {}, {})".format(net, git_hash, date_str),
        text,
    )
    LATEST_MD.write_text(text)


def _update_latest_md_organ_section():
    """Maintain the 'NAIVE ORGAN asks:' block in LATEST.md (the digest sink,
    design §3.2). Managed between HTML-comment markers, same shape as the
    'Latest simulation results' block — replaced in place, appended on first
    run."""
    from background import naive_organ
    section = naive_organ.render_digest_section()
    body = section if section else "_No open naive-organ questions._"
    block = "{}\n{}\n{}".format(ORGAN_BLOCK_START, body, ORGAN_BLOCK_END)
    text = LATEST_MD.read_text()
    if ORGAN_BLOCK_START in text and ORGAN_BLOCK_END in text:
        s = text.index(ORGAN_BLOCK_START)
        e = text.index(ORGAN_BLOCK_END) + len(ORGAN_BLOCK_END)
        text = text[:s] + block + text[e:]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    LATEST_MD.write_text(text)


def _update_latest_md_effort_section():
    """Maintain the 'EFFORT SIZING' block in LATEST.md (G5_effort_sizing_
    discipline L2 digest sink) -- managed between HTML-comment markers, same
    shape as the naive-organ block above. Replaced in place, appended on
    first run."""
    from background import effort_digest
    section = effort_digest.render_digest_section()
    body = section if section else "_Effort sizing data unavailable this run._"
    block = "{}\n{}\n{}".format(EFFORT_BLOCK_START, body, EFFORT_BLOCK_END)
    text = LATEST_MD.read_text()
    if EFFORT_BLOCK_START in text and EFFORT_BLOCK_END in text:
        s = text.index(EFFORT_BLOCK_START)
        e = text.index(EFFORT_BLOCK_END) + len(EFFORT_BLOCK_END)
        text = text[:s] + block + text[e:]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    LATEST_MD.write_text(text)


def run_effort_digest_step():
    """G5_effort_sizing_discipline L2 live hook: refresh the 'EFFORT SIZING'
    LATEST.md block every publish cycle. Fully defensive (matches
    run_naive_organ_step()'s own discipline): sizing is a DIAL, and this
    digest section must NEVER be able to break publishing -- any failure is
    logged and swallowed, never raised."""
    try:
        _update_latest_md_effort_section()
    except Exception as exc:
        log("Effort-sizing digest section skipped: {}".format(exc))


def run_naive_organ_step():
    """H11_naive_organ LIVE HOOK (L2 = habitual firing). Run the 7 SYSTEM
    detectors over the live observable state (map + run_history + logs) and ask
    the amnesiac Opus organ once per NEW fired contradiction (debounced). Output
    is QUESTIONS to naive_organ_log.jsonl + the 'NAIVE ORGAN asks:' block in
    LATEST.md — NEVER actions (safe by construction, SELF_INTERRUPT_DISCIPLINE
    QUEUE), so this cannot change what the pipeline does, only surface doubt.

    Fully defensive: any failure is logged and swallowed — the organ NEVER
    breaks publishing. Skipped under pytest (PYTEST_CURRENT_TEST) so the test
    suite never spawns a real `claude -p` Opus subprocess, and via
    NAIVE_ORGAN_DISABLE=1 as a kill switch."""
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("NAIVE_ORGAN_DISABLE") == "1":
        return
    try:
        from background import naive_organ
        written = naive_organ.run_organ_cycle(max_new=3)
        log("Naive organ: {} new question(s) asked (open: {})".format(
            len(written), naive_organ.hit_rate()["open"]))
    except Exception as exc:
        log("Naive organ cycle skipped: {}".format(exc))
    try:
        _update_latest_md_organ_section()
    except Exception as exc:
        log("Naive organ digest section skipped: {}".format(exc))


def run_fast_tests(git_hash: str):
    """Returns (passed: bool, timed_out: bool). Skips if git_hash already tested."""
    if LAST_TESTED_HASH_FILE.exists():
        if LAST_TESTED_HASH_FILE.read_text().strip() == git_hash:
            log("Tests skipped — already passed for git={}".format(git_hash))
            return True, False

    full_env = dict(os.environ)
    full_env["SIM_FAST_MODE"] = "1"
    try:
        # THE GATE'S SUBJECT IS A CLEAN CHECKOUT OF HEAD (director ruling
        # DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09): "publishing tests committed truth
        # only; the working tree belongs to the lanes."
        #
        # WHY. The gate used to run in PROJECT_DIR, so its subject was the live working tree --
        # shared with every lane. One lane's uncommitted work therefore halted publishing for the
        # whole machine, and was invisible at HEAD. Measured twice on 2026-08-09: first a single
        # uncommitted isort fix, then KNIFE2's 19 staged-but-uncommitted files, which held
        # publishing down from 12:56Z on three reds that a fresh checkout passes.
        #
        # This is the MINIMAL implementation the ruling asked for tonight: `git archive HEAD`
        # into a throwaway dir (measured 0.46s / 130MB / 8,444 files, so it is cheap enough to do
        # every cycle) and run the same argv there. The polished version -- a proper worktree
        # lifecycle, cleanup on crash, R15 both ways -- is its own atom.
        #
        # WHAT THIS DELIBERATELY DOES NOT CHANGE: tests that assert about the LIVE box (systemd
        # units, daemon liveness) still observe the real machine, because their subject is the
        # box, not the tree. Only the CODE under test moves to HEAD.
        with _head_checkout() as head_dir:
            if head_dir is None:
                return _checkout_unavailable_verdict()
            _repair_derived_artefacts_in(head_dir)
            return _run_gate_in(head_dir, full_env, git_hash)
    except subprocess.TimeoutExpired:
        return _gate_timed_out()


# SELF-HEALING DERIVED ARTEFACTS (2026-08-10, R10 class closure for the fourth wedge of the
# same shape; register: background/derived_artefact_register.py).
#
# WHY. A `docs/design/*.md` projection goes stale whenever an ordinary act moves its sources --
# minting an atom into the maturity map, archiving a finding to `staging/done/`. Its blocking
# `--check` test then reds at HEAD, and because the publish path only commits AFTER a green
# gate, the repair can never land: publishing deadlocks until a worker tick hand-runs `--write`.
# That happened four times on 2026-08-09/10, costing hours each. The regeneration step existed
# and simply had no caller.
#
# WHERE, and why here rather than in the staging-archive path (the open question the filed
# finding left): today's drift was caused by a MAP MINT, not a staging archive, so an
# archive-path repair would not have prevented it. This point is trigger-agnostic -- it repairs
# whatever went stale, however it went stale, at the one moment staleness does harm.
#
# WHAT IT DOES TO THE GATE'S SUBJECT. The rendering is written into the HEAD checkout as well as
# the working tree, so the gate tests HEAD *plus a mechanical re-derivation of HEAD's own
# sources* -- and `git_commit_push` then publishes that same rendering in this cycle, so the
# checkout is never ahead of what lands. This is a deliberate, narrow qualification of
# DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09: what is tested is still committed truth, plus
# the projection that committed truth *entails*. It cannot mask a real defect, because a
# projection is a pure function of committed sources -- if the re-derivation differs from what is
# committed, the committed copy was stale, which is the bug being repaired and not a finding
# about the code. Nothing else in the checkout is touched.
#
# FAIL-OPEN BY DESIGN, DELIBERATELY: a repair that cannot run logs and returns, and the gate then
# reds on the true unrepaired state. That is the honest outcome -- this helper must never be able
# to turn a red gate green by crashing.
#
# ── THE BLOCKING SCOPE, DECIDED RATHER THAN INHERITED (2026-08-28, delivery seat) ──────────────
#
# THE QUESTION, put by the seat that drew the fifth publish stoppage of this shape: should a stale
# DESIGN DOCUMENT be able to stop the company's FIGURES publishing at all? A reader wanting the
# margin does not care whether `docs/design/BLOCKED_ATOM_VISIBILITY.md` carries this morning's
# parked-atom count, and on 2026-08-28 that document held the road shut for 4.5 hours while the
# arrears went from two run markers to eleven.
#
# THE DECISION: THE SCOPE STAYS WIDE. Written down here, deliberately, rather than narrowed --
# and the reason is that the narrowing is a cure for the wrong disease. Every one of the five
# stoppages was a projection that could not converge, never a projection that was merely stale;
# staleness alone is REPAIRED above and lands pre-gate, which is exactly the design working. The
# 2026-08-28 instance was a document whose derivation read the pass-ceiling store and rolled the
# draw's own rng, so it re-rendered into a moving target and `MAX_REPAIR_PASSES` was exhausted --
# the artefact's own defect, repaired at source in `background/blocked_atom_visibility.py`.
# Carving design docs out of the gate would have published figures on 2026-08-28 and left that
# defect in place, to be re-found by the next artefact that acquires a live input.
#
# WHAT THE NARROW SCOPE WOULD ACTUALLY COST, which is why this is not the cheap win it looks:
# the register cannot tell a "design document" from a projection whose staleness means a
# PUBLISHED FIGURE IS WRONG -- `forward_attachment_register` exits non-zero on a content
# violation, not a rendering lag, and `tools/generate_projections_page.py` renders a reader-facing
# surface. A split on the `docs/design/` prefix would therefore be an exclusion scoped by
# DIRECTORY over a set that mixes both kinds, which is the shape that hides what it mixes. Doing
# it properly means each REGISTER entry declaring whether its staleness impugns a figure, and
# that declaration is the atom, not a comment.
#
# THE REAL RESIDUE, named so the next seat does not re-derive it: non-convergence is LOUD IN THE
# LOG AND SILENT EVERYWHERE ELSE. Nobody was woken for 4.5h because the site kept serving the
# last VERIFIED run behind a banner that works exactly as designed. That is a defect in the
# ALARM, not in the coupling, and it is where the next cut belongs -- an R5 state-transition NTFY
# on `converged == False`. Not built here: this turn's mandate was the wedge, and a new alarm
# added to patch a symptom is the accretion OPERATIONAL_LAYER_DESIGN forbids.
def _repair_derived_artefacts_in(head_dir):
    """Re-render stale derived artefacts from committed truth, into the checkout AND the tree."""
    try:
        from background import derived_artefact_register as dar
        res = dar.repair_from(head_dir, PROJECT_DIR)
    except Exception as exc:  # noqa: BLE001 -- see FAIL-OPEN note above
        log("Derived-artefact repair skipped (non-fatal): {}".format(exc))
        return
    if res["repaired"]:
        log("Derived-artefact repair: re-rendered {} stale projection(s) from HEAD -- {}.".format(
            len(res["repaired"]), ", ".join(res["repaired"])))
        _land_repaired_artefacts(res["repaired"])
    if not res["converged"]:
        log("Derived-artefact repair did NOT converge after {} pass(es): {} still stale. This is "
            "a real defect, not slow convergence, and it is a WEDGE: the gate reds until it is "
            "repaired AT SOURCE. Two shapes seen -- two projections invalidating each other, or "
            "(2026-08-28) ONE projection invalidating itself because its derivation reads live "
            "state. Diagnose by rendering the named artefact twice in two processes with the map "
            "untouched: if the two renderings differ, a draw/ledger/rng input is leaking in and "
            "no number of repair passes can converge.".format(
                res["passes"], ", ".join(res["still_stale"])))


# THE REPAIR LANDS BEFORE THE GATE, NOT AFTER IT (2026-08-12, closing the last BLOCKING member of
# CLASS_PUBLISH_GATE_AND_WEDGE: WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND).
#
# THE DEADLOCK. The repair above wrote correct bytes into the working tree on every cycle and
# logged "Committed with this run" 81 times running -- and was committed by none of them. The
# publish path commits only after a GREEN gate, and the staleness IS what reds the gate. So a
# repair built to end this wedge class sat one step downstream of the thing it repairs: the
# eighth, tenth and eleventh wedges were all closed by a human-equivalent tick hand-landing the
# same bytes the daemon had already written. The finding named the fix -- commit the repair
# pre-gate by pathspec -- and it stayed unbuilt for two days while the class kept recurring.
#
# WHY surgical_land AND NOT `git commit`. Two reasons, both walls. (1) HOOK-BYPASS IS A WALL
# (DIRECTOR_RULING 2026-08-09): this commit must face the same gate as any other, and it does --
# `land()` runs the repo's own pre-commit hook against the tree the commit WOULD create, and
# REFUSES on red. It is not a bypass; it is the gate run one step earlier, on a smaller subject.
# (2) The shared tree always holds other lanes' uncommitted work, and a `git commit` from a
# daemon would sweep it; `land()` names its paths and touches nothing else.
#
# WHAT IT CANNOT DO, stated because a repair that could force its own landing would be worse than
# the deadlock: it cannot turn a red HEAD green. If the resulting tree fails for ANY other reason
# the landing is refused, the bytes stay in the working tree exactly as before, and the gate then
# reds on the true state. The only thing it changes is that a staleness which is a pure function
# of committed sources stops being un-landable.
#
# FAIL-OPEN, same direction as its caller: any failure here logs and returns. A publish cycle must
# never die because a repair could not be committed.
def _land_repaired_artefacts(repaired):
    """Land the re-rendered projections by pathspec, gated, BEFORE the publish gate runs."""
    try:
        from tools import surgical_land
    except Exception as exc:  # noqa: BLE001 -- see FAIL-OPEN note above
        log("Derived-artefact repair not landed (surgical_land unavailable): {}".format(exc))
        return
    message = (
        "chore(derived): land {} re-rendered projection(s) pre-gate -- {}\n\n"
        "A derived artefact went stale against its committed sources, which reds the gate; the "
        "repair that fixes it used to be committed only AFTER a green gate, so it could never "
        "land (WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10). "
        "Pure re-derivation from committed truth: no source changed.".format(
            len(repaired), ", ".join(repaired))
    )
    try:
        sha = surgical_land.land(PROJECT_DIR, list(repaired), message)
    except surgical_land.LandingRefused as exc:
        log("Derived-artefact repair NOT landed -- the gate refused the repaired tree, so the "
            "staleness is not the only thing red: {}".format(str(exc)[:1500]))
        return
    except Exception as exc:  # noqa: BLE001
        log("Derived-artefact repair landing skipped (non-fatal): {}".format(exc))
        return
    log("Derived-artefact repair LANDED pre-gate as {} -- {}".format(sha[:9], ", ".join(repaired)))


# A FULL DISK MUST SAY SO (2026-08-09, third publish wedge).
#
# The checkout is ~130MB extracted plus git's own index and objects, and it lands on whatever
# filesystem tempfile uses -- here a 7.8GB tmpfs. When that tmpfs was exhausted (4.4GB of repo
# checkouts abandoned by the DIAGNOSTIC ticks of the two earlier wedges, not by the gate, which
# cleans up in its own `finally`), git failed in two ways that both name the wrong subject:
#
#   * `git init` -> rc=128, `fatal: cannot mkdir`  -- true, and says nothing about disk;
#   * an OSError whose text was `git is not installed` -- actively misleading, sending the
#     reader after a missing binary while git was installed and working.
#
# Neither line contains the word "space", so the failure reads as a code or environment fault
# at exactly the moment publishing is wedged and a tick is looking for a red test. HEAD may be
# perfectly green -- it was.
#
# So the check moves BEFORE the extraction, where the cause is still legible. FAIL-CLOSED, same
# reasoning as _make_checkout_a_repo: a checkout that cannot be materialised is an unavailable
# check, and an unavailable check is a FAILED check (R15). The point of the pre-flight is not to
# turn a red into a green -- it is to make the log line name the real subject.
HEAD_CHECKOUT_MIN_FREE_MB = 400


def _free_mb(path):
    """Free megabytes on the filesystem holding `path`, or None if it cannot be read.

    None -- rather than 0 or a large number -- so the caller decides explicitly what an
    unreadable filesystem means, instead of the check silently failing open on a big number or
    silently wedging publishing on a small one."""
    try:
        return shutil.disk_usage(str(path)).free // (1024 * 1024)
    except OSError:
        return None


# ── THE CHECKOUT IS REUSED BETWEEN CYCLES (OPS2_publish_gate_head_worktree, 2026-08-10) ──────
#
# The minimal implementation extracted HEAD into a fresh `mkdtemp` every cycle. Extraction is
# cheap (0.46s) but a fresh tree has no `__pycache__`, so ~3,000 modules plus every test module's
# pytest-rewritten bytecode compiled COLD on every publish cycle -- a permanent per-cycle tax,
# not a one-off (the first clean-checkout run was still at 41% at 11 minutes against an in-tree
# suite of 10m33s). Measured both sides after this change: see the atom record in
# docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md.
#
# SO: one directory, refreshed IN PLACE to the new SHA (`read-tree -u --reset` + `git clean`
# keeping bytecode), not recreated. Still not `git worktree add`: that registers state in the
# real repo which survives a SIGKILL (rc=-9 is a known gate outcome), and the whole point of the
# archive form is that deleting the directory deletes every trace.
#
# THE THREE LIFECYCLE HAZARDS A REUSED DIRECTORY INTRODUCES, each closed here rather than left
# to convention:
#   * TWO PUBLISHERS -- a second gate refreshing the tree under a running suite would corrupt
#     both. An `flock` makes the reuse exclusive; a publisher that cannot take it falls back to
#     a throwaway checkout (slower, cold, correct) rather than waiting or sharing.
#   * TEST DEBRIS -- files a suite writes into the checkout would otherwise accumulate and make
#     the gate non-hermetic (cycle N's leftovers judging cycle N+1). `git clean -xdf` at refresh
#     removes everything not in HEAD except the bytecode and the DATA overlay.
#   * CRASH -- `finally:` does not run under SIGKILL. The reused directory is safe by
#     construction (there is one, and the next cycle reuses it), but throwaway dirs from the old
#     form and from fallback cycles do leak, so every cycle sweeps stale ones BEFORE the disk
#     pre-flight -- which makes the third wedge's exhausted-tmpfs failure self-healing.
# THE GATE'S CHECKOUTS LIVE ON DISK, NOT IN RAM (2026-08-11).
#
# `tempfile.gettempdir()` is `/tmp`, and on this box `/tmp` is **tmpfs** -- 7.8G, backed by the
# same 15.9G of RAM the suites need. A HEAD checkout is 8,662 files, and with the reuse
# elimination every concurrent publisher materialises its own. Three at 08:22Z exhausted it:
#
#     Publish gate: could not make the HEAD checkout a git repo: git is not installed
#     Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
#
# "cannot mkdir" is ENOSPC wearing a misleading message, and "git is not installed" is the
# diagnosis the code then printed -- git is installed; the filesystem was full. Same class as
# the tmpfs preflight finding in MEMORY_CLEANSE step 3: measure RAM, not the filesystem.
#
# Worse, the existing `_free_mb` pre-flight was measuring tmpfs, so it read "free" while the
# free bytes it was counting WERE the contended RAM -- a pre-flight that cannot see the
# resource it exists to protect. Pointing the root at ext4 makes that check mean what it says
# and takes the checkouts out of the OOM budget entirely: 894G free on /dev/sdd against 7.8G
# of RAM-backed /tmp.
#
# `/var/tmp` is the correct choice by convention too: it is for data that should survive across
# a run and is not expected to be RAM-backed. Overridable for tests and for a box where
# /var/tmp is itself tmpfs.
HEAD_CHECKOUT_ROOT = Path(os.environ.get("SE_GATE_CHECKOUT_ROOT", "/var/tmp"))
HEAD_CHECKOUT_PREFIX = "publish-gate-head-"
REUSED_HEAD_CHECKOUT_NAME = HEAD_CHECKOUT_PREFIX + "reused"

# THE ONE-LINE SWITCH FOR THE R3 ELIMINATION (2026-08-11). False => every cycle gets its own
# throwaway checkout and the shared mutable directory is never created. See `_head_checkout`
# for the full record; in short, the reused tree was reset under a live suite four separate
# times and each time the gate reported a red that said nothing about any test. The cost of
# False is cold bytecode per cycle; the cost of True was a 41-hour outage.
REUSE_HEAD_CHECKOUT = False
REUSED_HEAD_CHECKOUT_LOCK_NAME = REUSED_HEAD_CHECKOUT_NAME + ".lock"
# (REUSED_CHECKOUT_KEEP is defined with UNTRACKED_DATA_OVERLAY below, which it extends.)
# A throwaway checkout older than this was abandoned by a killed process. The bound is well
# clear of GATE_SUITE_TIMEOUT_SECONDS so a LIVE fallback checkout can never be swept out from
# under its own suite.
STALE_HEAD_CHECKOUT_AGE_SECONDS = 3 * 3600


def _sweep_stale_head_checkouts(now=None):
    """Delete abandoned publish-gate checkouts. Returns the number removed.

    `finally:` does not run when the gate is SIGKILLed (rc=-9 is a known outcome and the OOM
    killer is the known cause), so leaked 130MB directories are expected, not hypothetical --
    4.4GB of them exhausted the tmpfs on 2026-08-09 and wedged publishing with a message about
    git. Never raises: a sweep that fails must cost space, never a publish."""
    now = time.time() if now is None else now
    removed = 0
    try:
        candidates = sorted(HEAD_CHECKOUT_ROOT.glob(HEAD_CHECKOUT_PREFIX + "*"))
    except OSError:
        return 0
    for path in candidates:
        if path.name in (REUSED_HEAD_CHECKOUT_NAME, REUSED_HEAD_CHECKOUT_LOCK_NAME):
            continue
        try:
            if not path.is_dir() or now - path.stat().st_mtime < STALE_HEAD_CHECKOUT_AGE_SECONDS:
                continue
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
        except OSError:
            continue
    if removed:
        log("Publish gate: swept {} abandoned HEAD checkout(s) from {} -- these are the debris "
            "of runs that were killed before their cleanup could run.".format(
                removed, HEAD_CHECKOUT_ROOT))
    return removed


# ── THE SWEEP WAS SCOPED TO THE WRONG POPULATION (fifteenth wedge, 2026-08-10) ───────────────
#
# `_sweep_stale_head_checkouts` above owns `publish-gate-head-*` "and nothing else", and its test
# pins that. The scoping is right -- a daemon must not free-fire at directories it does not own --
# but the claim built on top of it, that the exhausted-tmpfs failure is therefore SELF-HEALING,
# was false, and publishing wedged on the same exhaustion again for 22h36m / 126 cycles.
#
# MEASURED, at the moment of the recurrence: /tmp is a 7.8G tmpfs -- RAM, not disk -- and held
# 5.0G. Of the 3.9G reclaimed by hand, the sweep above could see NONE of it:
#
#   2.4G  /tmp/pytest-of-rich/pytest-{0,31,36,122,154,158,176,214,234,235,240,254,259}
#   1.1G  ad-hoc diagnostic checkouts: gate_verify, wedge-diag2-*, headchk, gatechk2,
#         gatechk.GNMR, headtree_probe, headprobe2, publish-gate-verify-*
#   190M  publish-gate-head-9z78t7lu -- the only match, and at 20 min old CORRECTLY spared
#
# The failure presented as `git is not installed` and `fatal: cannot mkdir`, because ENOMEM on a
# tmpfs surfaces at fork/mkdir, not as "no space". That is the third wedge's signature exactly.
#
# THE POPULATION HAS TWO HALVES AND THEY CLOSE DIFFERENTLY:
#   * PYTEST TEMPS -- mechanised here. pytest retains its last 3 numbered roots itself, but that
#     pruning is per-invocation and best-effort: a suite SIGKILLed mid-run (rc=-9, the known gate
#     outcome) never prunes, so the roots accumulate exactly when the gate is already in trouble.
#     Same 3h bound as above, and the newest few are kept whatever their age, so a running
#     suite's own root can never be taken out from under it.
#   * DIAGNOSTIC CHECKOUTS -- NOT mechanised, deliberately. They carry names invented ad-hoc by
#     whoever was investigating (`headchk`, `gatechk.GNMR`), and no glob can distinguish those
#     from a directory this process has no business deleting. Closed as a CONVENTION instead:
#     a wedge investigation materialises HEAD under HEAD_CHECKOUT_PREFIX so the sweep above owns
#     it. Filed with the finding; the irony is on the record, that the debris of fourteen wedge
#     investigations is what caused the fifteenth.
PYTEST_TEMP_ROOT_GLOB = "pytest-of-*"
PYTEST_TEMP_KEEP_NEWEST = 3

# ── LIVENESS IS PROVED, NOT INFERRED FROM A CLOCK (2026-08-12, the nineteenth wedge, defect 2)
#
# The age bound below could not close the exhaustion loop and was not editable on its own terms.
# `STALE_HEAD_CHECKOUT_AGE_SECONDS` is 3h because a shorter clock can delete a RUNNING suite's
# root -- worse than the leak -- and `test_the_age_bound_cannot_delete_a_running_suites_checkout`
# pins it above GATE_SUITE_TIMEOUT_SECONDS * 1.5. But the tmpfs fills in ~80 minutes, so a 3h
# drain reclaims nothing. Both constraints are real; the way out is to stop asking the clock.
#
# MEASURED on this box at 05:12Z, with the gate live and publishing wedged ~19h:
#
#   pytest-104  lock pid 667899  DEAD   567M      pytest-139  no lock  clean exit    4.6M
#   pytest-114  lock pid 691903  DEAD   156M      pytest-140  no lock  clean exit    7.2M
#   pytest-116  lock pid 695508  DEAD   724M      pytest-141  no lock  clean exit    600K
#   pytest-128  lock pid 836345  LIVE   567M  <-- the gate's own running suite
#   pytest-134  lock pid 840851  DEAD   559M
#
# Two things that decide this design, neither of them a guess:
#
#   1. 2.0G of PROVABLE debris (four dead-lock roots) was entirely invisible to the 3h clock --
#      the oldest was 1h old, the newest 16 minutes. The clock cannot see what it is for.
#   2. The LIVE root, `pytest-128`, was the FOURTH-newest by mtime. `PYTEST_TEMP_KEEP_NEWEST = 3`
#      was therefore protecting `pytest-139/140/141` -- three finished sessions holding 12M --
#      and NOT protecting the one running suite on the box. The keep-newest window is a proxy
#      for liveness that, measured against the real population, had it exactly backwards.
#
# THE HOLDER IS PROVABLE HERE, so it is proved. pytest's own `create_cleanup_lock` writes the
# session's PID into `<numbered root>/.lock` and unlinks it from an atexit hook. That gives three
# distinguishable states, and the ambiguous one is the whole reason the clock was being used:
#
#   lock present, pid live   -> HELD    -- never swept, at ANY age (strictly safer than the 3h
#                                          bound, which deletes a suite still running at 3h01)
#   lock present, pid gone   -> DEBRIS  -- a SIGKILLed session; atexit never ran. rc=-9 is the
#                                          gate's known outcome, so this is the common case.
#   lock absent              -> DEBRIS  -- atexit DID run: the session finished and let go.
#
# NOT `/proc`-reference scanning, which the finding proposed and which MEASUREMENT REFUTED: at
# 05:12Z no live process referenced any pytest root through its cwd, its open fds, or its memory
# maps -- including pid 836345, the suite that was demonstrably running inside `pytest-128`.
# pytest closes the lock fd immediately after writing it. A reference scan would have read the
# live suite's own root as unheld and deleted it: fail-open, in the one direction that matters.
PYTEST_TEMP_LOCK_NAME = ".lock"
# The create race, and nothing else: pytest makes the numbered directory a moment before it makes
# the lock, so a root observed in that window is lockless and NOT yet debris. Also absorbs any
# pytest that numbers a root without locking it. Deliberately minutes, not hours -- it guards an
# interval measured in milliseconds and is not doing the work the age bound was doing.
PYTEST_TEMP_MIN_AGE_SECONDS = 600

# THIS SWEEP'S SUBJECT IS PYTEST'S FILESYSTEM, NOT THE CHECKOUTS' (2026-08-12, the nineteenth
# wedge). It was rooted at HEAD_CHECKOUT_ROOT and was CORRECT on arrival (21467f98d, 2026-08-10)
# because that constant was then "/tmp". The next day, 53e82b105 moved the CHECKOUTS off tmpfs
# onto disk -- right for checkouts, and it silently carried this sweep to /var/tmp with them,
# because one constant was serving two subjects that live on two different filesystems. From
# that commit until this one the drain globbed `/var/tmp/pytest-of-*`, which cannot exist:
# pytest builds its numbered roots under `tempfile.gettempdir()`, and nothing sets TMPDIR here.
#
# MEASURED at the moment of this finding: `/var/tmp/pytest-of-*` -> no match, while
# `/tmp/pytest-of-rich` held 3.3G across nine roots and /tmp was at 69% of a 7.8G tmpfs. The
# sweep had reclaimed nothing for 19 hours and said nothing, because its log line only fires
# when it removes something -- a silent zero reads exactly like a clean filesystem.
#
# So it is DERIVED FROM PYTEST'S OWN RULE rather than borrowed from a neighbour: whatever
# directory pytest would put a basetemp in is the directory this drains. Overridable for tests
# and for a box that sets TMPDIR. Its sibling `_sweep_stale_head_checkouts` keeps
# HEAD_CHECKOUT_ROOT -- the two subjects are now independently movable, which is the property
# whose absence caused this.
PYTEST_TEMP_ROOT_PARENT = Path(os.environ.get("SE_GATE_PYTEST_TEMP_ROOT", tempfile.gettempdir()))


HOLDER_HELD = "held"
HOLDER_DEBRIS = "debris"
HOLDER_UNPROVEN = "unproven"
# Clock skew between the lock's mtime and /proc's boot-time arithmetic. A PID that started more
# than this AFTER its lock was written cannot be the process that wrote it -- the number was
# recycled and the real holder is gone.
PID_REUSE_SLACK_SECONDS = 60


def _process_start_epoch(pid):
    """Wall-clock start time of `pid`, or None if it cannot be established.

    The pid-reuse guard. Without it, "there is a process numbered 836345" is not evidence that
    the session which wrote 836345 into the lock is still running -- Linux recycles PIDs, and a
    sweep that skips a root on a recycled number leaks forever rather than for one cycle."""
    try:
        stat = Path("/proc/{}/stat".format(int(pid))).read_text()
        # `comm` is parenthesised and may itself contain spaces and ')': split after the LAST
        # one, so field 3 is tail[0] and `starttime` (field 22) is tail[19].
        tail = stat[stat.rindex(")") + 2:].split()
        ticks = float(tail[19])
        btime = next(float(line.split()[1])
                     for line in Path("/proc/stat").read_text().splitlines()
                     if line.startswith("btime "))
        return btime + ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError, StopIteration, TypeError):
        return None


def _pytest_root_holder(path):
    """Who holds this numbered pytest root: (verdict, pid). See the block comment above.

    HOLDER_UNPROVEN is returned whenever the evidence is unreadable or self-inconsistent, and
    the caller then falls back to the age bound. An unavailable check is a FAILED check (R15):
    it must never become permission to delete."""
    lock = path / PYTEST_TEMP_LOCK_NAME
    try:
        raw = lock.read_text().strip()
    except FileNotFoundError:
        # pytest's atexit hook unlinked it: the session finished and let this root go.
        return HOLDER_DEBRIS, None
    except OSError:
        return HOLDER_UNPROVEN, None
    if not raw.isdigit():
        # Not the lock shape this reasoning is built on -- say so rather than guess.
        return HOLDER_UNPROVEN, None
    pid = int(raw)
    if not Path("/proc/{}".format(pid)).exists():
        if not Path("/proc/self").exists():
            # No procfs at all: every pid would read as dead and the sweep would delete the box.
            return HOLDER_UNPROVEN, pid
        return HOLDER_DEBRIS, pid          # SIGKILLed session; its atexit never ran.
    started = _process_start_epoch(pid)
    if started is None:
        return HOLDER_UNPROVEN, pid
    try:
        written = lock.stat().st_mtime
    except OSError:
        return HOLDER_UNPROVEN, pid
    if started > written + PID_REUSE_SLACK_SECONDS:
        return HOLDER_DEBRIS, pid          # A recycled number, not the session that locked this.
    return HOLDER_HELD, pid


def _sweep_stale_pytest_temp_roots(now=None):
    """Delete abandoned pytest temp roots on PYTEST'S filesystem. Returns the number removed.

    A root is swept when its HOLDER is proved gone, not when a clock says it is old -- see the
    block comment above for the measurement that decided this. The age bound survives only as
    the fallback for a root whose holder cannot be established.

    Never raises: like the checkout sweep, a sweep that fails must cost space, never a publish."""
    now = time.time() if now is None else now
    removed = 0
    held = unproven = 0
    try:
        parents = sorted(PYTEST_TEMP_ROOT_PARENT.glob(PYTEST_TEMP_ROOT_GLOB))
    except OSError:
        return 0
    for parent in parents:
        try:
            # Numbered roots only. `pytest-current` and friends are SYMLINKS into them; removing
            # a link would leave the bytes and lose the handle.
            numbered = [p for p in parent.iterdir()
                        if p.is_dir() and not p.is_symlink()
                        and p.name.startswith("pytest-") and p.name[7:].isdigit()]
        except OSError:
            continue
        # Newest-first, so the keep-window is the most recent roots regardless of the age bound.
        numbered.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        for rank, path in enumerate(numbered):
            try:
                verdict, _pid = _pytest_root_holder(path)
                age = now - path.stat().st_mtime
                if verdict == HOLDER_HELD:
                    # At ANY age. The 3h bound used to delete this root out from under a suite
                    # still running at 3h01; proof does not expire.
                    held += 1
                    continue
                if verdict == HOLDER_UNPROVEN:
                    # Exactly the pre-2026-08-12 rule, unchanged: keep-newest window, then age.
                    unproven += 1
                    if rank < PYTEST_TEMP_KEEP_NEWEST or age < STALE_HEAD_CHECKOUT_AGE_SECONDS:
                        continue
                elif age < PYTEST_TEMP_MIN_AGE_SECONDS:
                    continue                          # inside the create race; not yet debris
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
            except OSError:
                continue
    if removed:
        log("Publish gate: swept {} abandoned pytest temp root(s) from {} -- holder proved gone "
            "(dead lock PID, or no lock at all). Spared: {} PROVED HELD by a live session, {} "
            "unproven and left to the {}h age bound.".format(
                removed, PYTEST_TEMP_ROOT_PARENT, held, unproven,
                STALE_HEAD_CHECKOUT_AGE_SECONDS // 3600))
    elif not parents:
        # A SILENT ZERO WAS THE NINETEENTH WEDGE. "Removed nothing" and "there is nothing here
        # to remove, and there never could be" are the same silence, and the second one is a
        # misrouted drain. Say which, once, at the cost of one line per cycle.
        log("Publish gate: no pytest temp roots under {} -- nothing to sweep (if the tmpfs is "
            "filling, this drain is pointed at the wrong filesystem).".format(
                PYTEST_TEMP_ROOT_PARENT))
    return removed


@contextmanager
def _reused_checkout_lock():
    """Hold the reused checkout exclusively for this cycle, or yield None if another holds it.

    NON-BLOCKING on purpose: waiting would serialise two publishers behind a ~10-minute suite for
    no gain, and sharing would let one refresh the tree the other is running in."""
    lock_path = HEAD_CHECKOUT_ROOT / REUSED_HEAD_CHECKOUT_LOCK_NAME
    handle = None
    try:
        handle = open(str(lock_path), "a+")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        if handle is not None:
            handle.close()
        yield None
        return
    try:
        yield lock_path
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        handle.close()


# A HUNG GIT IS A GATE THAT DID NOT FINISH. The three helpers below re-raise TimeoutExpired
# rather than folding it into "checkout unavailable": `run_fast_tests` owns the timeout verdict
# (`_gate_timed_out`), which BLOCKS and records the run as timed-out. Both answers block, so this
# is not a safety question -- it is a naming one, and a 300s `git archive` that never returned
# should be recorded as the timeout it was rather than as a generic failure to materialise.
def _head_sha():
    """The SHA the gate is about to judge, or None if git cannot say."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                              capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        raise
    except (OSError, subprocess.SubprocessError) as exc:
        log("Publish gate: `git rev-parse HEAD` could not run: {}".format(exc))
        return None
    if head.returncode != 0:
        log("Publish gate: `git rev-parse HEAD` failed rc={} -- {}".format(
            head.returncode, stderr_tail(head.stderr)))
        return None
    return head.stdout.strip()


def _materialise_head_into(dest: Path, head_sha: str) -> bool:
    """Extract HEAD into an EMPTY directory and make it a standalone repo. True on success."""
    try:
        archive = subprocess.run(["git", "archive", head_sha], cwd=str(PROJECT_DIR),
                                 capture_output=True, timeout=300)
        if archive.returncode != 0:
            log("Publish gate: `git archive HEAD` failed rc={} -- {}".format(
                archive.returncode, stderr_tail(archive.stderr.decode("utf-8", "replace"))))
            return False
        untar = subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout,
                               capture_output=True, timeout=300)
        if untar.returncode != 0:
            log("Publish gate: extracting HEAD failed rc={}".format(untar.returncode))
            return False
    except subprocess.TimeoutExpired:
        raise
    except (OSError, subprocess.SubprocessError) as exc:
        log("Publish gate: could not materialise HEAD into {}: {}".format(dest, exc))
        return False
    return _make_checkout_a_repo(dest, head_sha)


def _object_store() -> Path:
    """The repo's real object directory, which is NOT always `<project>/.git/objects`.

    IN A LINKED WORKTREE `.git` IS A FILE, not a directory, so the literal path does not exist and
    `git read-tree` refuses the alternates line with "unable to normalize alternate object path".
    The publish gate could therefore not materialise HEAD from ANY worktree, and returned None --
    which `_head_checkout`'s caller correctly reads as "the gate cannot run". That is every landing
    made from an isolated writer through `tools/surgical_land`, i.e. the whole route
    `background/seat_executor` and `tools/promote_worktree_landing` exist to use. It was found by
    a merge commit refusing in the worktree it was being reconciled in.

    ASKED OF GIT RATHER THAN ASSEMBLED FROM `PROJECT_DIR`, because git is the only thing that knows
    where the common directory is; a worktree's `.git` file can point anywhere.

    WHEN GIT CANNOT SAY, this returns the legacy path -- deliberately, and it is not a fail-open:
    it reproduces exactly today's behaviour, and the caller's existing fail-closed branch still
    refuses to run the gate on a checkout that could not be built.
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0 or not r.stdout.strip():
            return PROJECT_DIR / ".git" / "objects"
        common = Path(r.stdout.strip())
        if not common.is_absolute():
            common = (PROJECT_DIR / common).resolve()
        return common / "objects"
    except (OSError, subprocess.SubprocessError):
        return PROJECT_DIR / ".git" / "objects"


def _checkout_is_usable(path: Path) -> bool:
    """Is this an existing checkout this process can legitimately refresh in place?

    Deliberately checks the ALTERNATES line too: a directory that borrows a different (or a
    since-deleted) object store cannot answer git questions about this HEAD, and rebuilding is
    cheap. Anything unexpected reads as unusable -- the fallback is a rebuild, never a guess."""
    try:
        if not (path / ".git" / "HEAD").is_file():
            return False
        alternates = path / ".git" / "objects" / "info" / "alternates"
        return alternates.read_text().strip() == str(_object_store())
    except OSError:
        return False


def _refresh_checkout_to(path: Path, head_sha: str) -> bool:
    """Move an existing checkout to `head_sha` in place, keeping bytecode. True on success.

    `read-tree -u --reset` is the whole update: it rewrites the index to the new commit and
    updates the working tree to match, including deleting files the new commit does not have.
    `git clean` then removes what a previous suite wrote, minus REUSED_CHECKOUT_KEEP."""
    try:
        (path / ".git" / "HEAD").write_text(head_sha + "\n")
        read_tree = subprocess.run(["git", "read-tree", "-u", "--reset", head_sha],
                                   cwd=str(path), capture_output=True, text=True, timeout=300)
        if read_tree.returncode != 0:
            log("Publish gate: refreshing the reused checkout to {} failed rc={} -- {}".format(
                head_sha[:9], read_tree.returncode, stderr_tail(read_tree.stderr)))
            return False
        clean_argv = ["git", "clean", "-xdfq"]
        for keep in REUSED_CHECKOUT_KEEP:
            clean_argv += ["-e", keep]
        clean = subprocess.run(clean_argv, cwd=str(path), capture_output=True, text=True,
                               timeout=300)
        if clean.returncode != 0:
            log("Publish gate: cleaning the reused checkout failed rc={} -- {}".format(
                clean.returncode, stderr_tail(clean.stderr)))
            return False
    except subprocess.TimeoutExpired:
        raise
    except (OSError, subprocess.SubprocessError) as exc:
        log("Publish gate: could not refresh the reused checkout: {}".format(exc))
        return False
    return True


def _reused_checkout_is_in_use(path: Path) -> bool:
    """Is a LIVE process still working inside `path`? Asked while holding the reuse lock.

    THE LOCK IS NOT ENOUGH, AND THE LOG SHOWS WHY (2026-08-10). `flock` is held on a file
    descriptor owned by the publisher PROCESS, but the suite runs in a GRANDCHILD. When the
    publisher is SIGKILLed by a caller's deadline, `subprocess.run`'s kill reaches the direct
    child only: the pytest process keeps running, `cwd` still inside this directory, while the
    dead parent's descriptor closes and RELEASES the lock. The next cycle then legitimately
    takes that lock and calls `read-tree -u --reset` / `git clean -xdf` / `rmtree` on a tree a
    live suite is reading. Both reds of 2026-08-10 are that, and neither is about any test:

        18:25Z  ModuleNotFoundError: No module named 'tools.test_execution_metric'
                  -- at pytest_sessionfinish, the module gone from under the run
        18:51Z  FileNotFoundError: '/tmp/publish-gate-head-reused'
                  -- at os.chdir(session.startpath), the directory itself gone

    So the lock answers "is another publisher COORDINATING with me", and this answers "is
    anyone actually IN there" -- which is the question that matters to a destructive refresh.
    `/proc/<pid>/cwd` is the only first-hand answer available; a process that has the path as
    its working directory is in it, whatever it believes about locks.

    FAIL-SAFE IS `True` ONLY ON A POSITIVE SIGHTING. An unreadable /proc entry is a process
    that is exiting or not ours to see, never a reason to declare the directory busy forever
    -- a guard that latches on would wedge publishing exactly as hard as the bug it prevents.
    A /proc that cannot be enumerated at all reads as not-in-use: on a box without procfs this
    guard simply does not apply, and the pre-existing behaviour stands.

    SELF-OCCUPANCY IS THE STRONGEST SIGHTING, NOT AN EXCLUSION (2026-08-10, the RECURRENCE).
    The first version of this guard skipped `os.getpid()`, on the reasonable-sounding ground
    that a process asking "is anyone in there" cannot mean itself. It can, and that is the one
    case that matters: `tests/background/test_publish_gate_head_checkout_is_a_repo.py` calls
    `_head_checkout()` against the REAL root (it does not redirect `HEAD_CHECKOUT_ROOT` the way
    the sandboxed modules do), and it is inside the gate's own blocking scope. So when a killed
    publisher orphans its suite, the lock is free AND the caller standing in the directory IS
    the occupant -- the guard answered False about itself and the refresh reset the tree under
    the running suite. The same red therefore came back TWICE after the fix landed at 19:08Z:

        20:18Z  ModuleNotFoundError: No module named 'tools.test_execution_metric'
        20:47Z  the same, and the traceback is the proof of the swap -- the suite STARTED at a
                commit whose conftest imports at line 219 and the traceback rendered lines
                250/265, i.e. two LATER commits' conftest. The files changed under the run."""
    try:
        target = path.resolve()
    except OSError:
        return False

    def _inside(cwd: Path) -> bool:
        return cwd == target or target in cwd.parents

    # Asked first, and first-hand: `os.getcwd()` needs no procfs, so this half of the guard
    # still holds on a box where /proc cannot be enumerated at all.
    try:
        if _inside(Path(os.getcwd())):
            return True
    except OSError:
        pass
    try:
        pids = [entry for entry in os.listdir("/proc") if entry.isdigit()]
    except OSError:
        return False
    for entry in pids:
        try:
            cwd = Path(os.readlink("/proc/{}/cwd".format(entry)))
        except OSError:
            continue
        if _inside(cwd):
            return True
    return False


def _prepare_reused_checkout(head_sha: str):
    """The reused directory at `head_sha`, or None if it cannot be produced."""
    path = HEAD_CHECKOUT_ROOT / REUSED_HEAD_CHECKOUT_NAME
    if _checkout_is_usable(path):
        if _refresh_checkout_to(path, head_sha):
            _overlay_untracked_data(path)
            return path
        log("Publish gate: the reused HEAD checkout could not be refreshed -- rebuilding it from "
            "scratch (this cycle pays the cold-bytecode cost).")
        shutil.rmtree(path, ignore_errors=True)
    else:
        shutil.rmtree(path, ignore_errors=True)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log("Publish gate: could not create the reused HEAD checkout at {}: {}".format(path, exc))
        return None
    if not _materialise_head_into(path, head_sha):
        shutil.rmtree(path, ignore_errors=True)
        return None
    _overlay_untracked_data(path)
    return path


@contextmanager
def _head_checkout():
    """Materialise HEAD into a checkout the gate can run in. Yields a Path, or None.

    None means the gate must NOT run (R15: an unavailable check is a failed check) -- the caller
    treats it as a block, not as a pass.

    Ordering is deliberate: sweep first (it is what frees the space), then the disk pre-flight
    (so an exhausted filesystem still names DISK rather than git), then the SHA, then the
    checkout itself."""
    _sweep_stale_head_checkouts()
    _sweep_stale_pytest_temp_roots()
    tmp_root = str(HEAD_CHECKOUT_ROOT)
    free_mb = _free_mb(tmp_root)
    if free_mb is not None and free_mb < HEAD_CHECKOUT_MIN_FREE_MB:
        log("Publish gate: DISK, not code -- only {}MB free on {} and a HEAD checkout needs "
            "~{}MB, so it was not materialised. HEAD may be green; nothing here says a test "
            "failed. Reclaim space on {} (abandoned repo checkouts left by diagnostic runs are "
            "the known cause) and the next cycle proceeds unchanged.".format(
                free_mb, tmp_root, HEAD_CHECKOUT_MIN_FREE_MB, tmp_root))
        yield None
        return
    head_sha = _head_sha()
    if head_sha is None:
        yield None
        return
    if not REUSE_HEAD_CHECKOUT:
        # R3 ELIMINATION, not a fifth patch (2026-08-11, publishing down 41h, 216 markers).
        # The shared mutable checkout has produced a FALSE RED four times by the record kept in
        # `_reused_checkout_is_in_use`'s own docstring -- 18:25Z, 20:18Z, 20:47Z (twice AFTER the
        # 19:08Z fix), and 08:10Z today, every one of them the same `ModuleNotFoundError: No
        # module named 'tools.test_execution_metric'` raised at `pytest_sessionfinish` because
        # the tree was reset under a live suite. R3 is explicit that a second failure of one
        # mechanism means ELIMINATE OR REDESIGN, never patch again, and the last two patches
        # were themselves defeated by the case the guard cannot see: `flock` lives on the
        # publisher PROCESS, the suite runs in a GRANDCHILD, so a deadline-SIGKILLed publisher
        # releases the lock while its pytest keeps reading the directory.
        #
        # The optimisation being given up is warm bytecode. What it bought was speed; what it
        # cost was a gate that could not pass at all, which is the whole of a 41-hour outage.
        # A fast gate that never passes is worth strictly less than a slow one that does, and
        # the throwaway path below is already the documented "correctness before speed" branch,
        # exercised on every lock contention -- so this takes an existing, proven path always,
        # rather than adding a new one.
        #
        # REVERSIBLE IN ONE LINE: set REUSE_HEAD_CHECKOUT = True. Re-enable only once the
        # grandchild-outlives-the-lock case is closed by construction (a cgroup/process-group
        # kill that reaps the suite with its parent, or a per-cycle directory that is never
        # shared), not by another liveness heuristic.
        reason = ("DISABLED -- the shared checkout produced four false reds by resetting the "
                  "tree under a live suite (R3 elimination, 2026-08-11)")
    else:
        with _reused_checkout_lock() as held:
            if held is not None:
                if not _reused_checkout_is_in_use(
                        HEAD_CHECKOUT_ROOT / REUSED_HEAD_CHECKOUT_NAME):
                    yield _prepare_reused_checkout(head_sha)
                    return
                # The lock is free but the directory is NOT: an earlier publisher was killed and
                # left its suite running in there (see `_reused_checkout_is_in_use`). Refreshing
                # it now would corrupt that run AND produce a red here that says nothing about
                # the code. Same fallback as lock contention, for the same reason.
                reason = ("free of its lock but a live process is still running inside it -- an "
                          "orphaned suite from a killed publisher")
            else:
                # Another publisher owns the reused checkout for the length of its suite.
                reason = "held by another publisher"
    # Correctness before speed: this cycle gets its own throwaway tree, cold bytecode and all,
    # and deletes it.
    log("Publish gate: the reused HEAD checkout is {} -- using a throwaway checkout for this "
        "cycle (correct, but cold).".format(reason))
    tmp = tempfile.mkdtemp(prefix=HEAD_CHECKOUT_PREFIX, dir=str(HEAD_CHECKOUT_ROOT))
    try:
        if not _materialise_head_into(Path(tmp), head_sha):
            yield None
            return
        _overlay_untracked_data(Path(tmp))
        yield Path(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# A CHECKOUT WITH NO HISTORY IS NOT A CHECKOUT OF HEAD (2026-08-09, R10 class closure).
#
# The first `git archive` extraction had no `.git`, so every test that asks git a question died
# in it -- not with an assertion about the code, but with `fatal: not a git repository`. Two
# instances inside one evening, both patched at the instance:
#
#   * 576105747 -- the ghost-pusher tripwire, taught not to shell out;
#   * tests/background/test_blocked_atom_visibility.py::test_the_real_staleness_clocks_... which
#     reads AO11's own `git blame` of the map, and which wedged the publish gate at HEAD.
#
# R10 forbids closing that class one instance at a time, and the population is open-ended: any
# test that reads history, blame, or a SHA is a future instance. So the SUBJECT is fixed instead.
#
# WHAT THIS IS, precisely: a STANDALONE repo, not a link to the real one. `git init` creates its
# own `.git`, an `objects/info/alternates` line lends it the real repo's object store READ-ONLY,
# and `.git/HEAD` is the raw SHA (detached). `git read-tree` then fills the index so the checkout
# reads as tracked-and-CLEAN rather than 8,444 untracked files -- a test asking "is this tree
# clean?" gets the true answer for HEAD, which is yes.
#
# WHY NOT `git worktree add`: it registers state in the real repo that survives this process
# being SIGKILLed (rc=-9 is a known gate outcome), which is exactly what the archive form was
# chosen to avoid. Nothing here touches the real repo's index, refs, or worktree list; deleting
# the tmpdir deletes every trace. Measured: init+alternates+read-tree 0.02s, and `git blame` of
# the map inside the result 0.65s.
#
# FAIL-CLOSED (R15): if the repo cannot be made, the gate does not run. A checkout where git
# questions cannot be answered is not committed truth, and publishing on it would be publishing
# on an unavailable check.
def _make_checkout_a_repo(checkout: Path, head_sha: str) -> bool:
    """Turn an extracted HEAD tree into a real standalone git repo at `head_sha`."""
    try:
        init = subprocess.run(["git", "init", "-q"], cwd=str(checkout),
                              capture_output=True, text=True, timeout=60)
        if init.returncode != 0:
            log("Publish gate: `git init` in the HEAD checkout failed rc={} -- {}".format(
                init.returncode, stderr_tail(init.stderr)))
            return False
        alternates = checkout / ".git" / "objects" / "info" / "alternates"
        alternates.parent.mkdir(parents=True, exist_ok=True)
        alternates.write_text(str(_object_store()) + "\n")
        (checkout / ".git" / "HEAD").write_text(head_sha + "\n")
        read_tree = subprocess.run(["git", "read-tree", head_sha], cwd=str(checkout),
                                   capture_output=True, text=True, timeout=120)
        if read_tree.returncode != 0:
            log("Publish gate: `git read-tree {}` in the HEAD checkout failed rc={} -- {}".format(
                head_sha[:9], read_tree.returncode, stderr_tail(read_tree.stderr)))
            return False
        return True
    except (OSError, subprocess.SubprocessError) as exc:
        log("Publish gate: could not make the HEAD checkout a git repo: {}".format(exc))
        return False


# DATA IS NOT CODE. The ruling moved the gate's subject to committed CODE; it did not say the
# suite should run without the machine's data. These paths are untracked BY DESIGN -- a 291MB
# Elexon/NESO cache and the npm tree -- so `git archive HEAD` cannot contain them, and a checkout
# without them fails 85 tests for reasons that have nothing to do with whether HEAD is publishable
# (measured: `FileNotFoundError: sim/cache/elexon_demand_full.json` under 25 of them alone).
#
# SYMLINKED, not copied: 291MB per publish cycle would be absurd, and the suite only reads them.
# A named, explicit list rather than "everything gitignored" -- sweeping in .venv/.pytest_cache
# would reintroduce exactly the working-tree coupling the ruling removed.
UNTRACKED_DATA_OVERLAY = ("sim/cache", "node_modules")

# Kept across a refresh of the reused checkout (see _refresh_checkout_to). `__pycache__` is the
# entire reason the directory is reused at all; the overlay entries are symlinks to the machine's
# untracked DATA, which `git clean` would otherwise delete every cycle. Everything else a suite
# left behind is debris and goes, so cycle N's leftovers can never judge cycle N+1.
REUSED_CHECKOUT_KEEP = ("__pycache__",) + UNTRACKED_DATA_OVERLAY


def _machine_data_dir() -> Path:
    """WHERE THE MACHINE'S UNTRACKED DATA LIVES -- the MAIN worktree, never the importing tree.

    `PROJECT_DIR` is the tree this module was imported from, and for the publish gate that is
    always `/home/rich/synthetic-enterprise`, so the difference never showed. The census reuses
    this helper on purpose (so the two cannot drift about what "a checkout of HEAD" means) and
    the census CAN be launched from a linked worktree -- where `PROJECT_DIR / "sim/cache"` is
    whatever a stray run happened to leave behind.

    MEASURED 2026-09-02, from a worktree, with the census's own `head_subject_checkout`: the
    subject's `sim/cache` symlink resolved to a directory holding ONE of the machine's twelve
    cache files, and 25 tests in `tests/sim/test_renewable_capacity_trend.py` failed on the
    absent `elexon_demand_full.json` -- the exact file and the exact count this constant's own
    comment names four lines up. Those reds reached the HEAD-red register and were drawn as work
    that HEAD does not owe.

    `git rev-parse --git-common-dir` names the ONE `.git` every linked worktree shares, and its
    parent is the main worktree. Falls back to `PROJECT_DIR` when git cannot answer, which is
    exactly today's behaviour -- so this can only ever fix a linked-worktree caller and can never
    change what the gate already does.
    """
    try:
        proc = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                              cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return PROJECT_DIR
    common = (proc.stdout or "").strip()
    if proc.returncode != 0 or not common:
        return PROJECT_DIR
    main_worktree = Path(common).parent
    return main_worktree if main_worktree.is_dir() else PROJECT_DIR


def _overlay_untracked_data(checkout: Path) -> None:
    """Symlink the machine's untracked DATA into a HEAD checkout. Never raises: a missing
    overlay makes tests fail loudly, which is a better failure than the gate refusing to run.

    The source is the MACHINE's data (`_machine_data_dir`), not the importing tree's -- see that
    docstring for the 29 reds the difference manufactured."""
    source = _machine_data_dir()
    for rel in UNTRACKED_DATA_OVERLAY:
        src = source / rel
        dst = checkout / rel
        if not src.exists() or dst.exists():
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(src, target_is_directory=src.is_dir())
        except OSError as exc:
            log("Publish gate: could not overlay {} into the HEAD checkout: {}".format(rel, exc))


def _green_clock_path() -> Path:
    """WHERE the sidecar goes: beside the hash file it describes, DERIVED at call time.

    CAUGHT IN THE ACT, 2026-08-20, before this repair had landed. The first draft wrote
    `LAST_TESTED_GREEN_FILE` -- the module default -- and the live
    `docs/observability/.last_tested_green.json` was found holding `{"sha": "deadbeef", ...}`,
    a fixture value, stamped 17:41:55Z, later than the real green at 17:03:38Z. The writer is
    `tests/background/test_process_run_complete.py:1325`, which redirects `LAST_TESTED_HASH_FILE`
    into `tmp_path` and drives the rc=0 branch with `git_hash="deadbeef"`: it isolated the path
    its author thought of, and the sidecar -- added days after that fixture was written -- was
    not one of them. That test file is in the publish gate's own scoped list, so it fired on
    every publish cycle.

    THE FIX IS THE DERIVATION, NOT A REDIRECT IN THAT ONE FIXTURE. `supervisor._recorded_green_clock`
    already states this rule for the READ side ("the sidecar is looked for BESIDE the hash file
    whenever a caller redirects that path"), and a writer that ignored the rule its own reader
    states is the two-halves-read-different-trees pattern this whole repair is an instance of
    (`feedback_a_two_part_control_can_have_each_half_read_a_different_tree`). Deriving the
    location means every caller that redirects the hash -- which is every sandbox, because the
    hash file is the one two other consumers depend on -- redirects the sidecar with it, and
    cannot fail to think of it. `LAST_TESTED_GREEN_FILE` survives as the production default and
    as the NAME both halves agree on.

    The damage this class can do here is bounded and worth stating, because it is why this is a
    defect and not a catastrophe: `_recorded_green_clock` requires `sha` to equal the hash file's,
    so a fixture-authored sidecar reads as "no green is claimed" and leaves RUNG 1 ARMED. A
    phantom draw, never a silenced alarm -- the same fail direction as losing the write entirely."""
    return LAST_TESTED_HASH_FILE.parent / LAST_TESTED_GREEN_FILE.name


def _record_gate_green_clock(git_hash: str, now: float | None = None) -> bool:
    """Stamp WHEN this green was recorded, beside the SHA that says WHICH commit it was.

    Called from exactly one place -- the rc=0 branch of `_run_gate_in`, immediately after
    `.last_tested_hash` -- so the two files are one record with one writer and one trigger. The
    full rationale, and why a SHA alone could not answer the question its consumer was asking it,
    is in LAST_TESTED_HASH_CONTRACT.

    BEST-EFFORT BY DESIGN, and the fail direction is stated rather than left to be discovered:
    an exception here must never red a publish that the suite already passed, and the consumer
    (`supervisor._recorded_green_clock`) treats a missing/malformed sidecar as "no green is
    claimed" and keeps the RUNG-1 alarm ARMED. So the cost of losing this write is a phantom
    unwedge draw, never a silenced one. Returns whether the stamp landed, so the caller's tests
    can put both directions on trial instead of inferring them."""
    try:
        _green = _green_clock_path()
        guard_live_ledger_write(_green, writer="process_run_complete._record_gate_green_clock")
        _green.write_text(json.dumps(
            {"sha": git_hash, "ts": time.time() if now is None else float(now)}))
        return True
    except (OSError, TypeError, ValueError) as exc:  # noqa: BLE001 - see the docstring
        log(f"gate green clock not stamped (publish unaffected, wedge alarm stays armed): {exc}")
        return False


def _run_gate_in(cwd: Path, full_env: dict, git_hash: str):
    """Run the publish-gate argv in `cwd` and record the outcome. Split out so the checkout
    lifecycle above stays readable and the run itself stays testable."""
    # Blocking scope = publish-SURFACE tests only (see publish_gate_pytest_argv:
    # heavy ignores for speed, operational ignores for R10 class closure).
    #
    # R5/R9 (2026-07-29, a ~67-min publish wedge whose ONLY record was the
    # string "Tests FAILED - not committing"): the gate's own output was
    # discarded, so the blocking test was unknowable from the log and the
    # failure could not be diagnosed after the fact -- the site data has
    # since been regenerated, so the red is not reproducible later. An
    # alarm must carry its diagnostic payload, so capture the run and log
    # the failing node IDs. Capture is bounded (tail only) so a pathological
    # suite can never balloon the log.
    #
    # PW3_suite_duration_watch: the wall-clock of THIS run is the only place the gate's duration
    # exists (the checkout's own docs/observability is thrown away with it), so it is measured
    # here and recorded against the SHA it judged. A timeout is recorded too — the run that hits
    # the wall is the most informative point in the series, and it is the one that would
    # otherwise be missing from it.
    #
    # SCOPED TO WHAT IT PROTECTS (2026-08-10, DIRECTOR_RULING_PUBLISH_DECOUPLING). The argv
    # below is no longer the whole tree: `background/publish_scope.py` narrows the BLOCKING
    # set to the tests that transitively import the code producing or rendering a published
    # number. Reds outside that set no longer wedge the public surface -- they are run by the
    # remainder pass after the publish and ANNOTATE the page instead. Every failure path in
    # that module degrades to this same argv unnarrowed, so the worst case of the scoping
    # machinery breaking is exactly today's behaviour.
    started = time.monotonic()
    gate_argv, gate_scope = _scoped_gate_argv(run_root=cwd)
    log("Publish gate scope: {}".format(gate_scope["reason"]))

    # A BROKEN CHECKOUT IS AN ABSENT ONE (2026-08-12, the sixteenth wedge).
    #
    # `run_fast_tests` already refuses to run when `_head_checkout()` yields None, and that
    # refusal is the right one -- `_checkout_unavailable_verdict` is reused verbatim here
    # rather than restated, so there stays ONE answer to "the gate has no subject".
    #
    # What it could not see is a checkout that was CREATED and then not populated: `git init`
    # failed with rc=128 `fatal: cannot mkdir` at 02:04Z, the directory existed, `head_dir`
    # was therefore not None, and the gate ran the full suite against a tree holding none of
    # the repo. Measured over 2026-08-10 18:15Z -> 2026-08-12 02:11Z: 28 cycles resolved their
    # scope against such a root, against 64 that resolved normally -- 30% of every gate cycle,
    # each one silently widened from 134 scoped files to the whole tree, which is precisely
    # the "publish iff everything is green, i.e. publish never" condition the decoupling was
    # built to end. Each was logged as a rotted declaration; the declaration was intact.
    #
    # The scope resolver is the only party that reads the root's contents, so it is the only
    # one that can tell a materialised checkout from an empty directory -- hence the flag
    # rather than a second existence check here (which would drift from the first).
    #
    # R15: an unavailable check is a FAILED check, and it must not be recorded as a red TEST.
    # Returning here skips `_log_gate_failure_payload` deliberately: there are no failing
    # tests to name, and naming some anyway is the defect this whole episode is made of
    # (WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN).
    if gate_scope.get("root_unavailable"):
        return _checkout_unavailable_verdict()

    try:
        result = subprocess.run(
            gate_argv,
            cwd=str(cwd),
            env=full_env,
            timeout=GATE_SUITE_TIMEOUT_SECONDS,
            capture_output=True,
            text=True,
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        _record_gate_duration(time.monotonic() - started, git_hash, "timeout")
        raise
    _record_gate_duration(time.monotonic() - started, git_hash,
                          "pass" if result.returncode == 0 else "fail")
    if result.returncode == 0:
        LAST_TESTED_HASH_FILE.write_text(git_hash)
        _record_gate_green_clock(git_hash)
        _clear_blocking_tests()
    else:
        # THE VERDICT IS ALREADY DECIDED. `result.returncode` above is the publish verdict and
        # nothing below can change it -- the census is a REPORT run, its return code is never
        # read, and it runs here (inside the checkout, before it is torn down) purely so the
        # doorbell names every red rather than the first. See GATE_RED_CENSUS_* above.
        census = run_red_census(gate_argv, cwd, full_env, _parse_failed_node_ids(
            "{}\n{}".format(result.stdout or "", result.stderr or "")))
        _log_gate_failure_payload(result, git_hash, census=census)
    return result.returncode == 0, False


def _scoped_gate_argv(run_root=None):
    """(argv, scope) for the BLOCKING gate, for a suite that will run with cwd=`run_root`.

    Never raises: an unresolvable scope is the full suite, i.e. the pre-decoupling gate (see
    background/publish_scope.py, R15).

    `run_root` IS THE GATE'S SUBJECT, and the scope must be derived from it rather than from
    PROJECT_DIR. The gate's subject has been a clean HEAD checkout since
    DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09 ("the working tree belongs to the
    lanes"), but the scope introduced on 2026-08-10 kept resolving against the working tree
    -- so the argv named test files by a path that only existed in an uncommitted lane's
    tree, and the checkout answered with rc=4 rather than a red. That re-coupled every lane's
    uncommitted work to the public surface through the new layer, one day after the checkout
    ruling decoupled it at the old one. Resolving here against `run_root` makes both halves
    of the gate -- what it runs, and what it runs it against -- the same committed truth."""
    base = publish_gate_pytest_argv("tests/")
    root = PROJECT_DIR if run_root is None else Path(run_root)
    try:
        from background import publish_scope
        scope = publish_scope.resolve_scope(root=root)
        return publish_scope.scoped_pytest_argv(base, scope, run_root=root), scope
    except Exception as exc:  # noqa: BLE001 -- an unavailable scoper must not narrow anything
        return base, {"full_suite": True, "tests": [], "sources": [],
                      "reason": "scope module unavailable ({}: {}) -- full suite blocks, as "
                                "before the decoupling.".format(type(exc).__name__, exc)}


def _record_gate_duration(elapsed: float, git_hash: str, outcome: str) -> None:
    """Hand the gate's measured wall-clock to the duration watch (PW3_suite_duration_watch).

    Import is local and the whole call is guarded: the watch is an OBSERVER of the publish path
    and must never be able to red it — an unavailable watch costs one missing point in a series,
    which is strictly better than a blocked publish."""
    try:
        from background.suite_duration_watch import record_gate_run
        record_gate_run(elapsed, GATE_SUITE_TIMEOUT_SECONDS, git_hash, outcome)
    except Exception as exc:  # noqa: BLE001 -- see docstring; never raise into the publish path
        log("Suite duration watch unavailable (publish unaffected): {}".format(exc))


def _publish_tree_divergence():
    """Measure and PUBLISH how much uncommitted work is squatting in the shared tree, by lane.

    The other half of DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09: moving the gate's subject
    to a clean HEAD checkout means a lane's uncommitted work can no longer halt publishing --
    which also means nothing would notice it at all. So the cost is NAMED here instead. Verbatim:
    *"squatting gets named daily, never punished via the public site."*

    NEVER PUNISHES, structurally and not merely by intent: this returns None, so there is no
    value the caller could branch on even by mistake, and the whole body is wrapped -- an
    observer that can raise into the publish path it observes is itself a defect.

    Measured just before the gate, so the artefact records the tree as it was when the run was
    judged rather than after the publish commit has swept part of it away."""
    try:
        from background import tree_divergence as _td
        m = _td.measure()
        _td.write_artifact(m)
        if m.get("unavailable"):
            # An unavailable measure must reach the SAME naming path as a squat, not this
            # function's blanket `except`. Reading the counts here would raise, get swallowed
            # below, and restore the exact silence the fail-open repair just removed -- the
            # defect climbing one layer up (WORKER_FINDING_TREE_DIVERGENCE_FAILS_OPEN_TO_A
            # _CLEAN_TREE_2026-08-10). `breaches()` names it; the notify below sends it.
            log("Tree divergence: UNAVAILABLE — {}".format(m.get("unavailable_reason")))
        else:
            log("Tree divergence: {} source file(s) vs HEAD, oldest {}h — top: {}".format(
                m["total_files"], m["oldest_age_hours"], _td.top_squatters(m)))
        found = _td.breaches(m)
        if found:
            # "NAMED DAILY" is exactly notify's transition_key + re_escalate_after contract:
            # a CHANGED squat pages at once, an UNCHANGED one re-pages every 24h and is silent in
            # between. Keying `state` on the lane table rather than the raw counts means the
            # generated-file churn that moves the total every cycle does not re-page; a lane
            # appearing, growing or leaving does. Without re_escalate_after a standing squat
            # would page once and then be silent forever, which is the opposite of daily.
            from background import notification_digest
            from background.notify import notify
            # ROUTED ON MAGNITUDE, NOT CATEGORY ALONE (2026-08-26). G-N3 batches "divergence",
            # and for the ordinary two-files-over that is exactly right. But routing on the
            # category by itself made 436 files at 29x the line read like three files at 1.2x:
            # the breach was named correctly every day for six days and absorbed every time,
            # because a digest line is what the reader had learned to skim. Report-only stays
            # report-only -- this still blocks nothing and returns None -- but a breach this
            # far out now arrives as its own message instead of as one line among many.
            sev = _td.severity(m)
            digest_class = None if sev["severe"] else notification_digest.DIVERGENCE
            prefix = ("[TREE DIVERGENCE — {}x OVER] ".format(sev["worst_multiple"])
                      if sev["severe"] and sev["worst_multiple"] else "[TREE DIVERGENCE] ")
            notify(prefix + "; ".join(found)
                   + (". " + sev["reason"] + "." if sev["severe"] else "")
                   + " By lane: " + _td.top_squatters(m)
                   + ". Report only — the publish gate's subject is HEAD, so this blocks nothing."
                   + (" Walk it by lane and land what is finished; a sweep that only makes the"
                      " count fall is the same defect wearing a smaller number."
                      if sev["severe"] else ""),
                   kind="real_alarm",
                   topic_class=digest_class,
                   # The transition/re-escalate contract is UNCHANGED and still decides whether
                   # there is anything to say at all. Severity decides only how it travels, so
                   # a standing severe squat still pages once a day rather than every cycle.
                   transition_key="tree_divergence",
                   # THE IDENTITY OF THE SQUAT, not a rendering of it. `top_squatters` was the
                   # state here and carries an age in hours, so the state changed on every cycle
                   # and the transition check could never suppress a repeat -- 27 pages of one
                   # condition in a day. See `tree_divergence.divergence_state`.
                   state=_td.divergence_state(m),
                   re_escalate_after=24 * 3600)
    except Exception as exc:  # noqa: BLE001 -- see docstring; never raise into the publish path
        log("Tree-divergence measure unavailable (publish unaffected): {}".format(exc))


def _checkout_unavailable_verdict():
    """The verdict when committed truth could not be materialised: BLOCK.

    Its own function so the branch is nameable and MUTABLE in a test (R15): patch it to return
    `(True, False)` and the publish path proceeds unverified, which is exactly what this verdict
    prevents and what `test_publish_gate_subject_is_head.py` demonstrates both ways.

    R15: an unavailable check is a FAILED check. There is no third answer here -- a gate with no
    subject has not run, and 'has not run' must never read as 'passed'."""
    log("Publish gate: could NOT materialise a clean HEAD checkout -- not committing. "
        "R15: the gate's subject is committed truth; if it cannot be produced, the "
        "gate has not run.")
    return False, False


def _gate_timed_out():
    """The timeout verdict, split out so `run_fast_tests` reads as checkout -> run -> verdict."""
    # R15 FAIL-OPEN, closed 2026-08-09. This branch used to `return True, True` on the
    # reasoning that "timeout is a resource constraint, not a test failure". Two things
    # were wrong with that, both observed live during the second publish wedge:
    #
    #   1. The suite takes ~613s (measured: 22,525 passed in 612.94s) against what was a
    #      600s timeout, so it did not time out under load -- it timed out ROUTINELY. The
    #      gate could not pass; it could only time out and then publish unverified.
    #   2. A timeout returning True walks the whole success path: the marker is archived,
    #      the commit is attempted, and -- the part that mattered -- the publish-gate
    #      outcome is recorded as rc=0, which CLEARS wedge_since/episode_failures and
    #      re-arms the alarm. So a gate that never ran silently disarmed the alarm that
    #      exists to say it never ran. Markers were consumed and archived with nothing
    #      published, which is strictly worse than a wedge: a wedge at least alarms.
    #
    # R15 is explicit that an unavailable check is a FAILED check, and the safe direction
    # for a check that cannot answer is "do not publish". So a timeout now BLOCKS, and the
    # timeout is generous enough (3x the measured runtime) that hitting it is a real
    # anomaly worth wedging on rather than the normal case.
    log("Fast test suite timed out (>{}s) -- NOT committing. R15: an unavailable check is "
        "a FAILED check; a gate that did not finish cannot authorise a publish."
        .format(GATE_SUITE_TIMEOUT_SECONDS))
    return False, True


def _gate_refusal(timed_out, git_hash, blocking):
    """What a refused gate is called: (exit code, log line, banner reason).

    ONE function because the three facts must not be able to drift apart -- the code the wedge
    detector classifies on, the line the log carries, and the sentence the public banner
    publishes are the same claim about the same cycle. 2026-08-21 is what it looks like when
    they are stated separately: the state file said `test_regression` with `total_red: 0`, and
    the banner told the visitor the suite was "red at git=..." on a cycle where no test had been
    judged at all.

    A RED and a TIMEOUT are both refusals and both keep the wedge streak. They differ in what
    they licence a reader to do: a red names a node to run, a timeout names no node and means
    the tests are UNJUDGED. See EXIT_GATE_TIMED_OUT.
    """
    if timed_out:
        return (
            EXIT_GATE_TIMED_OUT,
            "Scoped publish-path gate DID NOT FINISH (>{}s) - not committing content; the "
            "tests are UNJUDGED, not red".format(GATE_SUITE_TIMEOUT_SECONDS),
            "scoped publish-path gate did not finish within {}s at git={}; the suite is "
            "UNJUDGED, not red -- no test is implicated".format(
                GATE_SUITE_TIMEOUT_SECONDS, git_hash),
        )
    return (
        1,
        "Scoped publish-path gate FAILED - not committing content",
        "scoped publish-path suite red at git={}; blocking tests: {}".format(
            git_hash, ", ".join(blocking or ()) or "see sim-runner-log"),
    )


# ── THE BOUND IS DERIVED FROM THE SUBJECT THE GATE ACTUALLY RUNS (OPS2 criterion 2) ─────────
#
# Was 600s, which the suite itself exceeded (612.94s measured 2026-08-09 for 22,525 tests), so
# the gate timed out on essentially every cycle. That was raised to 1800s as "3x the measured
# runtime" -- but the 613s it was 3x OF was the IN-TREE subject, and the ruling has since moved
# the gate's subject to a clean HEAD checkout. The bound was never re-derived against the thing
# it now bounds.
#
# MEASURED on the new subject (docs/observability/publish_gate_subject_cost.json, HEAD
# 3ee4541a7, 2026-08-10): a COLD checkout run takes **1291.9s** for 23,249 passed. 1800s is
# 1.39x that -- and a cold cycle is not exotic, it is what every fallback throwaway checkout and
# every rebuilt-corrupt checkout pays. Since the timeout now fail-CLOSES (`_gate_timed_out`
# BLOCKS), an undersized bound does not degrade the gate, it WEDGES PUBLISHING -- the same
# defect as the 600s bound, in the same direction, against a subject nobody re-measured.
#
# So: >= 2x the worst runtime measured on the real subject. 2 * 1291.9 = 2583.8 -> 2600s.
#
# AND THE DERIVATION IS CHECKED AGAINST ITS OWN EVIDENCE, NOT AGAINST A SECOND COPY OF IT. Until
# now the only control on this number was `test_the_gate_timeout_exceeds_the_suites_own_runtime`,
# which compares this constant against `MEASURED_SUITE_SECONDS = 1291.9` -- a second HAND-COPIED
# transcription of the same phase. Two constants copied from one measurement cannot disagree
# unless a human re-copies one of them, so the control could only ever fail on a typo, never on
# the thing that actually goes wrong here: the measured runtime MOVING. That is not hypothetical
# and it is not slow -- this bound has been undersized twice (600s, then 1800s), both times
# because the suite grew or the subject changed underneath a number nobody re-derived, and since
# the timeout fail-CLOSES an undersized bound WEDGES PUBLISHING.
#
# Meanwhile the measurement harness computes `implied_timeout_floor_2x` into the record and
# NOTHING READ IT -- a derived value with no consumer, this project's no-caller class exactly.
# `measured_gate_timeout_floor` below is that consumer, and
# `test_the_timeout_clears_the_floor_the_measurement_implies` reds when the record says the floor
# has risen past this constant. The record is the evidence; this is the claim; a control that
# compares them can fail.
#
# RE-DERIVED 2600 -> 2900 (2026-08-11, OPS2 criterion 2, launch 11 of the measurement). The
# control below did exactly what it was built to do: the shipped subject is a genuinely cold
# throwaway checkout every cycle since the R3 elimination, it measured 1411.2s (23,710 passed,
# rc=1 -- a red suite that ran to completion and reported), and 1411.2 * 2 = 2822 overtook the
# 2600s bound derived against the old 1291.9s phase. That phase had run in the since-deleted
# shared directory with bytecode from outside its own run, so it was never the shipped subject.
# `test_the_timeout_clears_the_floor_the_measurement_implies` reddened on this before any human
# looked, which is the control working rather than a regression.
#
# RE-DERIVED AGAIN, 2900 -> 3600 (2026-08-11, same day, launch 13). The control fired a SECOND
# time, mid-tick, on a phase the measurement banked while a worker was mid-commit: the gate scope
# ran green at 15:20Z and red at 15:35Z with no source change between them, because
# `throwaway_checkout` was re-timed at 1784.6s (23,831 passed, rc=1, `ran_to_completion: true`,
# cwd /var/tmp/publish-gate-head-s9eknacc) and 1784.6 * 2 = 3569 overtook 2900.
#
# THE SUBJECT DID NOT GET SLOWER BY 373s BECAUSE OF DRIFT -- read the summaries side by side:
# 23,710 tests at 1411.2s, then 23,831 at 1784.6s. The suite GREW by 121 tests, and it was also
# sharing this box with the in-tree baseline phase and a worker's own test runs. Both effects push
# the same way and neither is separable from this record, so the number is treated as what it is:
# a real, completed timing of the shipped subject under realistic contention. Erring high costs a
# longer wait on a genuinely hung gate; erring low WEDGES PUBLISHING, and this bound has now been
# undersized four times (600, 1800, 2600, 2900).
#
# RE-DERIVED A THIRD TIME, 3600 -> 4500 (2026-08-11, launch 13's `in_tree_baseline`). The control
# fired again in the working tree before this tick read anything: floor 3735 against a 3600 bound.
# The new worst phase is `in_tree_baseline` at 1867.6s with rc=-15 -- SIGTERM mid-suite, so its
# seconds is a LOWER BOUND on the runtime it was heading for. That is admissible HERE and only
# here: a lower bound can push a floor UP, which is the safe direction, and the same harness rule
# (`_ran_to_completion_from`) refuses it as a ratio denominator, where it would only overstate.
#
# THE MARGIN IS THE THING THAT WAS ACTUALLY WRONG, and it is why this bound has now been undersized
# FIVE times (600, 1800, 2600, 2900, 3600). Every re-derivation chased the floor with a token
# headroom -- 2900 sat 78s over its floor, 3600 sat 31s over its floor -- and each was overtaken
# within hours; the 3600 one within a single worker tick. Meanwhile the floor itself moved
# 2822 -> 3569 -> 3735 in ONE DAY, on a suite that gained 121 tests between two launches of the
# same phase. A margin smaller than the observed drift is a bound that reds again within a day,
# and each of those reds takes the write-time gate scope down mid-tick.
#
# So the margin is set to the observed drift rather than to a round-up: 3735 + 765 = 4500, where
# 765s is what the floor moved across 2026-08-11's own re-timings. Erring high costs a longer wait
# on a genuinely hung gate; erring low WEDGES PUBLISHING. The caller's bound
# (PUBLISH_PATH_TIMEOUT_SECONDS below) is DERIVED from this constant, so it moves with it and
# cannot drift -- that pair drifting apart is what wedged publishing for 41 hours on 2026-08-10.
# 4500 -> 300 -> 1800 (2026-08-21). The middle step was MINE AND IT WAS WRONG, and it wedged
# publishing for two cycles, so the reasoning is left in full rather than tidied away.
#
# I lowered this to 300 after timing `publish_gate_pytest_argv()` at ~40s. That function is NOT
# what the gate runs. The real call site is `_scoped_gate_argv()`, which passes `"tests/"`
# explicitly and then narrows through `background/publish_scope.resolve_scope()` -- a DERIVED
# scoper that has existed since 2026-08-10 and resolves 6 publish-path sources to 199 blocking
# test files through the static import graph. I timed a code path that never executes, and set a
# production timeout from it. Observed consequence, twice: `304.05s ceiling=300 outcome=timeout`.
#
# 3400 is read from the RECORD of the thing that actually runs. 310 completed real gate runs in
# `publish_gate_duration.jsonl`: median 1199s, p90 1384s, MAX 1674s. The existing rule is that
# the bound must clear the healthy case by 2x, because a routine timeout is a publish BLOCK --
# 2 x 1674 = 3349, so 3400.
#
# AND THAT ARITHMETIC CORRECTS SOMETHING I TOLD THE DIRECTOR. The old 4500 was ~2.7x the worst
# observed run: a defensible margin, not a number nobody was watching. The bound is not generous
# because it grew unwatched; it is generous BECAUSE THE GATE GENUINELY TAKES TWENTY MINUTES. The
# absurdity he named is real, but it lives in the scope, not in this constant -- and every one of
# the six re-derivations above was honestly chasing a subject that kept getting slower.
#
# So this number cannot come down by being written smaller. `resolve_scope()` currently resolves
# 6 publish-path sources to ~200 blocking test files through the static import graph; the
# director's target of a gate faster than the 5-minute cadence it gates needs THAT set to shrink.
# That is real work on a derived mechanism and it is not done here.
#
# 3400 -> 3800 (2026-08-21, same day, and the third correction to this constant in one afternoon).
# THE 3400 WAS READ OFF THE WRONG RECORD, AND THIS MODULE ALREADY OWNED A FUNCTION THAT SAYS SO.
# `measured_gate_timeout_floor()` below is the consumer `test_publish_gate_subject_is_head.py::
# test_the_timeout_clears_the_floor_the_measurement_implies` reads, and it does not read
# `publish_gate_duration.jsonl` at all -- it reads `publish_gate_subject_cost.json`, the harness's
# own timed measurement, whose worst banked phase is 1876.4s and whose floor at 2x is therefore
# **3752**. So 3400 shipped 352s BELOW the floor its own control enforces, and that control is
# inside `resolve_scope()`'s 200-file blocking set. The gate runs `-x`. From the moment 3400
# landed, every publish attempt reddened on the bound's own guard before it could time out at all:
# a wedge caused by the repair for the wedge.
#
# Two records, one number, and the derivation used the one nothing checks against. Worse, the
# figure it took from the duration series -- "MAX 1674s" over 310 COMPLETED runs -- is survivorship
# bias in the literal sense: the same file holds `4503.53` and `4503.70`, the two most recent real
# gate runs, both censored at the 4500s ceiling they were killed by. A maximum computed over the
# survivors of a bound cannot see the runs that bound truncated, so it re-derives itself downward
# every time the gate gets slow enough to be killed.
#
# 3800 is the lowest round number above the floor `measured_gate_timeout_floor()` actually returns.
# It is a FALL from the 4500 that stood before today, so the ratchet below keeps its meaning; it is
# above the floor, so the guard passes; and it is honest, which 3400 was not.
GATE_SUITE_TIMEOUT_SECONDS = 3800

# ── THE ABSOLUTE CAP (director, 2026-08-21) ──────────────────────────────────────────────
# *"A 75-minute gate is absurd on its face and neither of us said so. Nothing watches the
# absolute number -- only headroom against a budget that grew to fit."*
#
# Read the comment block above this line as evidence rather than as history. It re-derives the
# bound SIX times -- 600, 1800, 2600, 2900, 3600, 4500 -- each derivation careful, measured and
# honest, and each asking exactly one question: WHAT DOES THE SUITE NEED? It states the
# asymmetry that makes that question monotonic in its own words: *"erring low WEDGES
# PUBLISHING."* Nothing in it ever asks what a publish gate can AFFORD, so there was no
# counter-pressure and the number could only ever go up. It went 30 -> 75 minutes in nineteen
# hours on 2026-08-10/11.
#
# This constant is the counter-pressure, and the whole point is that it is NOT derived from the
# suite. It is derived from the CADENCE OF THE THING BEING GATED: the sim completes a run about
# every 5 minutes. A gate slower than that is not verifying the current state of the repository,
# it is reporting on a tree several generations old -- at 21 minutes it lagged by four runs, at
# 75 by fifteen. A verdict that arrives that late is not a gate, it is an obituary.
#
# Crossing it must therefore be a DECISION, not a re-derivation. `tests/background/
# test_publisher_deadline_exceeds_its_gate.py` fails if GATE_SUITE_TIMEOUT_SECONDS rises above
# this, so the seventh raise cannot be another careful paragraph -- it has to delete this
# constant, in the open, and argue with the sentence above.
#
# A RATCHET, NOT A TARGET, and that is the correction that makes it work.
#
# My first attempt made this an aspirational cap (300s, the publish cadence) and set the bound to
# match. The bound was then below what the gate actually needs, and publishing timed out twice.
# An aspirational cap on a measured quantity does not make the quantity smaller; it just breaks
# the thing being measured, or -- if someone softens it instead -- becomes the seventh
# re-derivation wearing a new hat.
#
# So this is monotonic instead: the bound may FALL freely and may NEVER RISE. That is exactly the
# property the director asked for -- "so this can't grow back one reasonable addition at a time"
# -- and unlike a target it is satisfiable today and still fails loudly tomorrow. Six raises got
# here; there is no seventh without deleting this line in the open.
#
# The 5-minute target is not abandoned, it is just not enforceable by a constant. It is recorded
# beside the bound above, where the work that would earn it is named.
#
# 3400 -> 3800, IN THE OPEN, as the paragraph above requires (2026-08-21, hours after 3400 landed).
# This is the correction of an arithmetic error, not the seventh re-derivation, and the difference
# is checkable rather than rhetorical: 3400 was set equal to a bound that this module's OWN floor
# function scores at 3752, so "satisfiable today" -- the one property the paragraph above claims
# distinguishes a ratchet from a target -- was FALSE ON ARRIVAL by 352 seconds. An unsatisfiable
# ratchet is an aspirational cap with better prose, which is exactly the failure the 300s attempt
# already made once today; it does not slow the suite down, it stops the gate.
#
# What the ratchet is FOR still holds and is unchanged: the number may fall freely and may never
# rise. 3800 is a fall from the 4500 that stood before today, so nothing has grown back -- the
# afternoon's net movement on this constant is -700s, and every future move must still be a
# reduction. What changed is that the ceiling is now a value the gate can actually pass under.
#
# TO THE NEXT READER WHO WANTS THIS HIGHER: do not. The two runs that would justify it (4503.5s and
# 4503.7s, 2026-08-20T21:10Z and 2026-08-21T14:42Z) are the ONLY real gate runs since the last
# successful publish, and both coincided with a second and third pytest suite live on the same box
# -- the write-time gate and the operational suite. Contention is not runtime. The three runs
# before them, on a quiet box, took 1248s, 1303s and 1323s.
PUBLISH_GATE_CEILING_RATCHET_SECONDS = 3800

# The record the harness writes (tools/measure_publish_gate_subject_cost.py) and the factor the
# bound is derived at. The factor lives HERE, next to the constant it justifies, and the harness's
# own `implied_timeout_floor_2x` is read when present -- so a completed record can never be
# under-read by a re-derivation that drifted from it.
GATE_SUBJECT_COST_RECORD = PROJECT_DIR / "docs" / "observability" / "publish_gate_subject_cost.json"
GATE_TIMEOUT_SAFETY_FACTOR = 2.0


def measured_gate_timeout_floor(record_path=None):
    """The lowest `GATE_SUITE_TIMEOUT_SECONDS` the MEASURED runtimes justify, or None.

    None means the record cannot answer -- absent, unreadable, malformed, or carrying no phase
    with a numeric runtime. None is NOT "no floor": the caller (a control) treats a record that
    cannot answer as a failed check, because this bound's whole history is of being justified
    against evidence nobody re-read.

    WORKS ON A PARTIAL RECORD, deliberately. The measurement is a ~50-minute three-phase job that
    has been killed or deferred eight times; a floor that waits for `complete: true` is a control
    that has never once fired. Every phase the record banks is admitted-quiet by construction
    (the harness DEFERS rather than timing a suite beside a live publisher), so the worst banked
    phase is a real runtime whether or not its siblings exist yet.

    WORST OF ALL PHASES, including `in_tree_baseline`, mirroring the harness's own
    `worst_legitimate_seconds` rather than inventing a second rule for the same name. The gate no
    longer runs in-tree, but the in-tree suite is the same tests: if it is the slowest thing
    measured, the bound clears it. Erring high costs a longer wait on a genuinely hung gate;
    erring low wedges publishing, which is the failure this atom exists to close."""
    try:
        record = json.loads(Path(record_path or GATE_SUBJECT_COST_RECORD).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None
    seconds = []
    phases = record.get("phases")
    if isinstance(phases, dict):
        for phase in phases.values():
            value = phase.get("seconds") if isinstance(phase, dict) else None
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                seconds.append(float(value))
    floors = [s * GATE_TIMEOUT_SAFETY_FACTOR for s in seconds]
    stated = record.get("implied_timeout_floor_2x")
    if isinstance(stated, (int, float)) and not isinstance(stated, bool) and stated > 0:
        floors.append(float(stated))
    return int(max(floors)) if floors else None

# ── THE CALLER'S BOUND IS DERIVED FROM THIS ONE, NOT RESTATED (2026-08-10, the wedge that
# outlived every red test it was blamed on) ──────────────────────────────────────────────
#
# THE SAME DEFECT AS THE BLOCK ABOVE, ONE LAYER UP. `background_worker.py::
# process_leftover_run_markers` -- the ONLY path that drains a lock-skipped marker, and so
# the only publisher running while a backlog exists -- wrapped this whole process in an
# INDEPENDENT `timeout=900`. Independent bounds drift, and this pair drifted apart in the
# worst possible direction: the gate's own budget was re-derived 600 -> 1800 -> 2600s
# against the cold-HEAD-checkout subject the ruling moved it to, while the caller's 900s cap
# stayed calibrated to the warm in-tree gate. The comment at PUSH_THROTTLE_SECONDS above
# still records the dead premise in its own words -- "fitting inside the 900s cap ... the
# fast-test gate already spends ~420s of that". It spends up to 2600s now.
#
# OBSERVED, not inferred (2026-08-10 17:44Z, docs/observability/background-worker-log.md):
#   process_leftover_run_markers error: Command '[...process_run_complete.py,
#   docs/staging/run_complete_20260809T131422Z.md]' timed out after 900 seconds
# 95 markers pending, 142 consecutive recorded "failures", and the named blocking test
# (test_every_live_hit_is_dispositioned) PASSING at HEAD. The gate was not red. The caller
# was killing the gate before it could return a verdict, and a kill with no return code
# reached the wedge detector as nothing at all.
#
# So the caller no longer carries a number. It IMPORTS this one, and this one is the gate's
# own bound plus what the rest of the publish path costs after the gate returns green (site
# regeneration, report, mirror, the hook-chain commit at GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
# the push). A wrapper bound BELOW the work it wraps does not bound anything -- it just
# decides the inner gate's verdict by stopwatch, and loses the log line that would explain
# it. `tests/background/test_publisher_deadline_exceeds_its_gate.py` reds if this stops
# exceeding GATE_SUITE_TIMEOUT_SECONDS.
PUBLISH_PATH_ALLOWANCE_SECONDS = 15 * 60
PUBLISH_PATH_TIMEOUT_SECONDS = GATE_SUITE_TIMEOUT_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS

# Bound on how much of a red gate's output reaches the log (chars).
GATE_FAILURE_TAIL_CHARS = 4000

# ── THE PAYLOAD MUST NAME A TEST THE GATE ACTUALLY RAN (2026-08-12, the eighteenth wedge;
# WORKER_FINDING_THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN) ──────────────────────────
#
# WHY. The previous parser scanned the gate subprocess's ENTIRE combined stdout+stderr for
# any line beginning "FAILED "/"ERROR ". Tests inside the blocking scope run NESTED pytest
# invocations and print their output; pytest replays that inside a `--- Captured stdout call
# ---` block, where a `startswith` check cannot tell it from the gate's own summary. The
# operational-layer signal is one such nested run, and it reports the COMPLEMENT marker set
# -- so the payload named `test_supervisor.py` tests that are module-level `@pytest.mark.
# operational`, i.e. tests the gate is STRUCTURALLY INCAPABLE of running (186 deselected,
# 0 collected, under the gate's own `-m` expression), while the real blocker -- an ENOSPC
# out of a tmpfs at 67% -- appeared nowhere in the list.
#
# That list is not merely internal. It reaches the PUBLIC surface: `paused_reason` in
# https://poesys.net/data/publish_provenance.json (HTTP 200, 2026-08-12 02:0xZ) served the
# wrong five test names under the company's own name. It also feeds the RUNG-1 priority-zero
# doorbell, so every tick after a red was sent to the wrong suspects -- the same
# "0/8, 0/8, 0/8, and this one's cause was not on the list either" shape the block below
# records for the `filed_findings()` mechanism this one replaced. The cure had replaced one
# wrong list with another wrong list.
#
# WHAT. Parse ONLY pytest's own short-summary section, and take the LAST one in the stream.
# Ordering makes this exact rather than heuristic: pytest emits captured-output blocks in the
# FAILURES section, which is always ABOVE its own "short test summary info" header, so a
# nested run's summary can never be the final one. Everything before that last header is
# somebody else's output by construction.
#
# FAIL-SILENT IS THE TRAP HERE (R15), so note what this deliberately does NOT do: when there
# is no summary section at all -- a hard crash, an OOM, a killed subprocess -- it returns []
# rather than falling back to the old whole-stream scan. The caller already distinguishes
# that case in its own words ("no FAILED/ERROR summary line found", with the rc), and an
# ABSENT answer read as absent is the discipline GATE_BLOCKING_TESTS_FILE below already
# commits to: "fabricating a plausible suspect is the defect being closed".
_PYTEST_SUMMARY_HEADER = re.compile(r"^=+\s*short test summary info\s*=+\s*$")


def _parse_failed_node_ids(out):
    """pytest's own ``FAILED <nodeid>`` / ``ERROR <nodeid>`` short-summary lines.

    Factored out of `_log_gate_failure_payload` so the BLOCKING gate and the non-blocking
    remainder pass read a red the same way -- two parsers would eventually disagree about what
    counts as a failure, and the annotation would quietly stop matching the block.

    Scoped to the LAST short-summary section (see the block above): a nested pytest run's
    output is replayed inside the FAILURES section, which always precedes the outer run's own
    summary header, so anything above that final header belongs to somebody else."""
    lines = (out or "").splitlines()
    start = None
    for i, ln in enumerate(lines):
        if _PYTEST_SUMMARY_HEADER.match(ln):
            start = i + 1
    if start is None:
        return []
    node_ids = []
    for ln in lines[start:]:
        if ln.startswith(("FAILED ", "ERROR ")):
            node_ids.append(ln.strip())
        elif _PYTEST_SUMMARY_HEADER.match(ln):
            break
    return node_ids


# ── NAMING THE GATE THAT REFUSED, WHEN NO TEST DID (2026-09-02, 18.7h of publishing down) ────
#
# WHY. `_parse_failed_node_ids` above answers "which tests went red". The pre-commit chain runs
# several gates BEFORE the test gate, each able to short-circuit it, and on those cycles the
# honest answer to that question is "none" -- which the publisher already logged, in those
# words, while `.publish_gate_state.json` went on naming five tests an earlier cycle had left
# behind. The refusing gate's own banner was in the same buffer the classifier was reading.
#
# WHAT THIS IS NOT. It is not a second opinion about test failure: it runs ONLY when
# `_parse_failed_node_ids` returned nothing, so the two parsers can never disagree about a red.
# It answers the different question the reader actually has -- "then what DID refuse?"
#
# THE BANNERS ARE MATCHED, NOT THE EXIT CODES. Each gate prints a distinctive line; an rc is a
# number several gates share. Keyed to the banner means a gate that changes its wording goes
# UNNAMED (which reads as unnameable, the honest answer) rather than misattributed to whichever
# gate happened to sit first in a table -- the fail-safe direction, and the same one
# `publish_cause.read_cause` takes.
#
# ORDER IS THE CHAIN'S ORDER. The chain short-circuits, so when more than one banner is present
# the FIRST matching entry is the one that refused; the rest are downstream noise or a replay.
#
# ── THE 2026-09-03 CORRECTION: FIVE OF THE SEVEN ENTRIES MATCHED NOTHING ANY GATE PRINTS ─────
#
# The paragraph above is right about the DIRECTION of the risk and was wrong that the risk was
# in the future. It argues a reworded banner degrades safely to UNNAMED. True — and the table it
# was defending had already degraded, at birth, for five of its seven rows. Measured against the
# strings the gates actually emit:
#
#   WRITE-TIME GATE  the gate prints `[write-time-gate] ❌ COMMIT REFUSED`. The table's uppercase
#                    spaced form appears in the module's LINE-1 DOCSTRING and nowhere else, so a
#                    grep for it in the source says PRESENT and the process prints it never.
#   LEVEL PROMOTION  the gate prints `[level-gate] ❌ COMMIT REFUSED`. Nothing prints this.
#   LIVE LEDGER      the guard RAISES `LiveLedgerWriteUnderTest`; it prints no banner at all, and
#                    it is not a hook-chain gate — it is a runtime write guard. Dropped, not
#                    re-worded: an entry for a gate that cannot refuse a commit is noise.
#   FINDING SEVERITY the refusal is the test gate's, and its words are the STAGING-DOCUMENT line
#                    below. Nothing anywhere prints this pair of words.
#   I001             ruff's code, and the pre-commit chain does not invoke ruff. Four characters
#                    is also far too short to be evidence of anything. Dropped.
#
# So a level-promotion refusal — the SECOND gate in the chain, the one most likely to stop a
# publish after the test gate — reported "no gate banner this classifier knows", i.e. UNNAMEABLE,
# about a refusal that names itself on the very next line. That is the defect this block was
# written to end, surviving inside the fix for it.
#
# WHY IT SURVIVED: the table was checked by fixtures the test file supplies, so both sides of
# every leg were written from the same guess about what a gate prints. Nothing compared the
# table to a gate. `tests/background/test_a_refusing_gate_banner_is_a_string_a_gate_prints.py`
# is that comparison, and it is keyed to the PROPERTY (every needle is a non-docstring string
# literal in the file named as its emitter) rather than to today's wording — so a gate that
# rewords goes RED HERE instead of quietly unnameable in the register.
#
# NEEDLES ARE ALL-OF, NOT ONE SUBSTRING. `write-time gate` is why: it assembles its line as
# f"[write-time-gate] {head}", where `head` is `❌ COMMIT REFUSED` in gate mode and
# `⚠️  WARN ONLY` in warn mode. Matching the prefix alone would name it as the refuser on a run
# where it deliberately did NOT refuse — the false-positive direction, which is not fail-safe and
# is the one the original comment did not consider.
#
# ORDER, NOW ACTUALLY THE CHAIN'S. pre-commit runs the test gate, then level-promotion, then
# (five gates this table does not name) the orphan ratchet; commit-msg runs the write-time gate
# only after all of pre-commit passed. The old table had orphan-ratchet first and level-promotion
# fourth, which is backwards. Write-time is LAST on purpose: it is the only entry whose needles
# could co-occur with an earlier gate's refusal, and last means the earlier gate wins.
#
# COVERAGE, 2026-09-03: the eleven gates that used to report UNNAMED now have rows, each needle
# read from the refusal branch of the gate that prints it (never from a module name — inventing
# one is what produced the five dead rows above). Two refusal paths remain unnameable and are
# declared in `_UNNAMEABLE_REFUSAL_PATHS` below rather than guessed at.
#
# A GATE MAY HOLD MORE THAN ONE ROW. Needles are ALL-OF, so a gate with two unrelated refusal
# messages cannot be expressed as one row: `half-hourly-dependency` refuses both for a NEW read
# and for a frozen read that is GONE, and those share no literal that a passing run does not also
# print. Two rows under one name is the honest form; `_parse_refusing_gate` returns the first
# match, and both carry the same name, so the reader sees one gate either way.
#
# Each entry is (name, needles, emitter) — `emitter` is the file that PRINTS the needles and is
# what the control checks against.
_REFUSING_GATE_BANNERS = (
    ("finding-class consolidation",
     ("❌ FINDING-CLASS CONSOLIDATION BROKEN",), "tools/pre_commit_test_gate.py"),
    ("finding-severity gate",
     ("❌ A STAGING DOCUMENT THIS COMMIT WRITES HAS NO PARSEABLE SEVERITY HEADER",),
     "tools/pre_commit_test_gate.py"),
    ("level-promotion gate", ("[level-gate] ❌",), "tools/level_promotion_gate.py"),
    ("site-lane gate", ("[site-lane] ❌",), "tools/site_lane_gate.py"),
    ("moap-coherence gate",
     ("[moap-coherence] ❌ COMMIT REFUSED",), "tools/moap_coherence_gate.py"),
    ("ruling-archive-question gate",
     ("[archive-question-gate] ❌ COMMIT REFUSED",), "tools/ruling_archive_question_gate.py"),
    ("consolidation-rhythm gate",
     ("COMMIT REFUSED -- this commit closes epoch(s)",), "tools/consolidation_rhythm.py"),
    # ONLY the unavailable path. The violation path prints f"[{tag}] ..." where `tag` is
    # SIZE-RATCHET or SIZE-RATCHET WARN, so the token that separates a refusal from warn mode is
    # built by interpolation and is not a literal anything can check — and the same prefix is
    # printed on a return-0 override path. Declared unnameable below instead of half-matched.
    ("size-ratchet gate",
     ("[SIZE-RATCHET] CHECK UNAVAILABLE -- refusing:",), "tools/size_ratchet_gate.py"),
    ("orphan-ratchet",
     ("orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS",), "tools/orphan_ratchet.py"),
    ("company-network-isolation gate",
     ("company-network-isolation: COMMIT REFUSED.",), "tools/company_network_isolation.py"),
    ("file-scope-generated-paths gate",
     ("file-scope-generated-paths: COMMIT REFUSED.",), "tools/file_scope_generated_paths.py"),
    ("annual-report-import ratchet",
     ("annual-report-import-ratchet: COMMIT REFUSED.",), "tools/annual_report_import_ratchet.py"),
    ("half-hourly-dependency ratchet",
     ("half-hourly-dependency: A NEW HALF-HOURLY READ OF THE RETAINED BOOK.",),
     "tools/half_hourly_dependency_ratchet.py"),
    ("half-hourly-dependency ratchet",
     ("frozen read(s) are gone -- re-freeze to lower the ",),
     "tools/half_hourly_dependency_ratchet.py"),
    ("running-total-order gate",
     ("running-total-order: COMMIT REFUSED.",), "tools/running_total_order.py"),
    ("scope-evidence ratchet", ("[scope-evidence] ❌",), "tools/scope_evidence_ratchet.py"),
    ("write-time gate",
     ("[write-time-gate] ", "❌ COMMIT REFUSED"), "tools/write_time_gate.py"),
)

# THE REFUSALS THAT STILL CANNOT BE NAMED, and why each one resists a needle rather than merely
# lacking one. This exists so `UNNAMED` keeps reading as "we cannot tell" and never as "not a
# gate" — the 18.7-hour misdiagnosis. Each entry is (what refuses, where, why it has no needle).
_UNNAMEABLE_REFUSAL_PATHS = (
    ("status-honesty", "tools/git-hooks/pre-commit",
     "the banner is echoed by the SHELL HOOK; background/status_honesty.py itself prints only "
     "JSON. The control reads Python source for printed literals, so a shell emitter has no "
     "checkable string and a row for it could not be verified against anything."),
    ("size-ratchet gate, violation path", "tools/size_ratchet_gate.py",
     "the refusal and the warn-only pass differ by an INTERPOLATED tag, not by any literal, and "
     "the shared prefix is also printed on a return-0 override path. A needle on the prefix "
     "would name it as the refuser of commits it let through."),
)


def _parse_refusing_gate(text):
    """The NAME of the non-test gate whose banner is in the hook chain's output, or None.

    None means "the output named no gate this parser knows", which is a fact a reader can act
    on -- it says look at the hook output itself -- and never a guess at a gate.

    ALL of an entry's needles must be present. One needle that happens to appear is not evidence
    the gate refused; see the `write-time gate` warn-mode case in the block above."""
    hay = text or ""
    for name, needles, _emitter in _REFUSING_GATE_BANNERS:
        if all(needle in hay for needle in needles):
            return name
    return None


def _log_gate_failure_payload(result, git_hash="unknown", census=None):
    """Log WHICH tests blocked the publish, not just THAT they did.

    Called only on a red gate. Emits the failing node IDs (pytest's own
    ``FAILED <nodeid>`` / ``ERROR <nodeid>`` short-summary lines) plus a bounded
    tail of the combined output, so a wedge is diagnosable from the log alone
    after the underlying site data has been regenerated away.

    ALSO PUBLISHES those node IDs to GATE_BLOCKING_TESTS_FILE, because the log is not
    readable by the process that raises the alarm -- see that constant's own note."""
    out = "{}\n{}".format(result.stdout or "", result.stderr or "")
    node_ids = _parse_failed_node_ids(out)
    if node_ids:
        log("Publish gate RED -- blocking test(s): {}".format("; ".join(node_ids[:20])))
    else:
        log("Publish gate RED (rc={}) -- no FAILED/ERROR summary line found".format(
            result.returncode))
    # The census (when the caller ran one) SUPERSEDES the fail-fast list, and is guaranteed by
    # `run_red_census` to be a superset of it -- so this can only ever add node ids, never lose
    # the one the verdict itself named.
    census_ids, census_status = (census if census else (node_ids, CENSUS_FAIL_FAST_ONLY))
    _write_blocking_tests(census_ids, git_hash, census=census_status)
    tail = out.strip()[-GATE_FAILURE_TAIL_CHARS:]
    if tail:
        log("Publish gate RED output tail:\n{}".format(tail))


# ── THE ALARM MUST CARRY THE ONE FACT THAT IDENTIFIES THE WEDGE (2026-08-10, seventh
# publish wedge; R5 "alerts carry the diagnostic payload", R10 class closure) ────────────
#
# WHY. `_log_gate_failure_payload` above has always extracted the blocking node IDs -- and
# then dropped them into a log file that the ALARM cannot read. `record_publish_gate_failure`
# runs in a DIFFERENT PROCESS (background_worker sweeps markers by shelling out to this file,
# so it only ever sees an exit code), and was given `reason="process_run_complete rc=1 on
# run_complete_<stamp>.md"` -- the marker's name, which identifies nothing. To fill the hole
# the alarm cited `filed_findings()`: the eight most recently modified WORKER_FINDING_*.md in
# staging, ranked by mtime and linked to the failure by nothing at all. Measured outcome, four
# consecutive episodes (see WORKER_REPORT_{PUBLISH,FIFTH,SIXTH}_WEDGE_*): 0/8, 0/8, 0/8, and
# this one's cause -- a ruff-ratchet regression at HEAD -- was not on the list either. The
# list was near-identical every time while the cause differed every time, which is the tell.
#
# WHAT. One file, written by the only code that knows the answer, read by the alarm. Same
# cross-process shape as `.last_tested_hash`, and the same fail-safe discipline:
#   * WRITTEN on every red gate (including the empty-list case: "the gate was red and printed
#     no FAILED line" is itself diagnostic, and distinguishable from "nobody wrote anything").
#   * DELETED on a green gate -- a stale red's node IDs must never be citable against a later,
#     unrelated failure. That is this mechanism's own version of the tautology it replaces.
#   * STALE (older than GATE_BLOCKING_TESTS_MAX_AGE_SECONDS) or malformed reads as UNKNOWN,
#     and the alarm then SAYS "unrecorded". It never falls back to a guess: fabricating a
#     plausible suspect is the defect being closed, so an absent answer must read as absent.
GATE_BLOCKING_TESTS_FILE = PROJECT_DIR / "docs" / "observability" / ".last_gate_blocking_tests.json"
# THE ATTRIBUTED CAUSE of a publish that did not land, written by `git_commit_push` at the
# moment it takes one of its four rc=77 paths and read by `record_publish_gate_outcome` in a
# LATER PROCESS, which otherwise sees only the exit code. See `background/publish_cause.py` for
# why an exit code cannot carry this and why the record is keyed to its own commit.
PUBLISH_CAUSE_FILE = PROJECT_DIR / "docs" / "observability" / ".last_publish_cause.json"
# Two full gate timeouts. Comfortably longer than any real red-to-alarm gap (the recorder runs
# seconds after the gate returns) and far short of the multi-hour episodes, so a wedge whose
# cause has since been repaired cannot keep re-citing yesterday's test.
GATE_BLOCKING_TESTS_MAX_AGE_SECONDS = 2 * GATE_SUITE_TIMEOUT_SECONDS
# Raised 5 -> 12 with the RED CENSUS below. Under `-x` this cap could never bind (there was only
# ever one node id to cite); with the census the record finally has a whole red set to truncate,
# and the episode that motivated it had FIVE. Still bounded -- an alarm is a page, not a directory
# listing -- and `_blocking_clause` now says how many were withheld rather than silently dropping
# them, which is the difference between a cap and a lie.
GATE_MAX_CITED_BLOCKING_TESTS = 12

# ── THE WEDGE DRAW MUST SEE THE WHOLE RED SET, NOT THE FIRST ONE (2026-08-14, the 252-cycle
# wedge; WORKER_FINDING_THE_WEDGE_WAS_FIVE_INSTANCES_OF_ONE_CLASS_AND_pytest_x_SERVED_THEM_ONE_
# AT_A_TIME, control 2 -- "the cheap one ... it is the recommendation") ──────────────────────
#
# WHY. The blocking gate runs under `-x`, so a red gate reports exactly ONE failing node id no
# matter how many are red. Measured: the publish gate was RED at every HEAD since `19d8f94da` --
# 252 consecutive failures, ~7,163 min -- and that was not one defect with a long tail but FIVE
# separate instances of one mechanism, stacked behind `-x` and served one per tick. Each tick
# diagnosed the layer it was shown, repaired it, landed it, and handed the next layer to the next
# tick. The same flag produced the eleventh wedge's "four flapping tests" that were really a
# STACK of three (`WORKER_FINDING_THE_ELEVENTH_WEDGE_WAS_A_STACK_NOT_A_BUG`). An enumerator that
# stops at one is not an enumerator: it reads "1 red" identically whether there is one or thirty,
# so the doorbell's node id carried no information about DEPTH -- and depth is the whole question
# when deciding whether an unwedge tick will be the last one.
#
# WHAT. On a red gate ONLY, re-run the gate's own argv once with fail-fast dropped, purely to
# REPORT, and record the whole red set. Three properties this must have, each a test below:
#   * THE BLOCKING VERDICT IS UNTOUCHED. The census runs AFTER the verdict is decided, its
#     return code is never read, and any failure of it degrades to today's behaviour (the
#     fail-fast node id alone, labelled as such). `-x` stays on the gate: it returns the publish
#     path's latency to the lanes, and -- the reason that matters here -- a red suite run to
#     completion near the timeout becomes a TIMEOUT, which carries NO node ids at all. Trading a
#     reliable one for a possible five is the wrong direction.
#   * IT CAN NEVER OUTLIVE THE PUBLISH PATH'S OWN BOUND. Its budget is DERIVED from what is left
#     of PUBLISH_PATH_TIMEOUT_SECONDS, not hand-typed -- a wrapper bound below the work it wraps
#     is the exact defect recorded at PUBLISH_PATH_ALLOWANCE_SECONDS above (41h wedge). Too
#     little budget left => the census is SKIPPED and says so; it never runs unbounded.
#   * "ONE RED" AND "WE ONLY LOOKED AT ONE" ARE DISTINGUISHABLE. Every record carries the census
#     STATUS, and the alarm states it. Without that field a complete census reporting one red is
#     byte-identical to no census at all, which is this finding's own subject one level up.
GATE_RED_CENSUS_MAXFAIL = 50          # a catastrophic red stops the census, not the box
GATE_RED_CENSUS_MAX_SECONDS = 20 * 60  # ceiling; the real bound is the derived budget below
GATE_RED_CENSUS_MIN_SECONDS = 90      # below this a census cannot finish anything; skip honestly
GATE_RED_CENSUS_PATH_MARGIN_SECONDS = 120  # what the red path still needs after the census
# Set once, at import, so "how much of the publish path have we spent" is measurable from
# anywhere in it. monotonic: never moves backwards, never NTP-corrected.
_PROCESS_STARTED_MONOTONIC = time.monotonic()

# The census's three honest answers, plus the two ways it declines. `fail_fast_only` is the
# pre-2026-08-14 behaviour and is what every degradation lands on.
CENSUS_COMPLETE = "complete"            # ran to the end: this IS the whole red set
CENSUS_PARTIAL = "partial"              # hit GATE_RED_CENSUS_MAXFAIL -- there may be more
CENSUS_FAIL_FAST_ONLY = "fail_fast_only"  # no census: the `-x` node id is all that is known
# A FOURTH provenance, because the source is a different suite (2026-08-26): the node ids came
# from the PRE-COMMIT HOOK CHAIN, which the publisher shells out to and whose output it captures.
# That chain stops at the FIRST refusing hook, so its red set is complete for the hook that
# refused and says nothing about the hooks behind it -- neither "the whole red set" nor "we
# stopped at one test" nor "no census ran" describes that, and reusing `partial` would have made
# the alarm claim a 50-failure bound that never fired. See `_record_commit_refusal_reds`.
CENSUS_HOOK_CHAIN = "hook_chain"


def red_census_argv(gate_argv):
    """The REPORT-ONLY argv: the blocking gate's OWN argv, fail-fast dropped, failures bounded.

    Composed from the gate argv rather than rebuilt, so the census can never end up enumerating
    a different suite than the one that went red (two argv builders would drift, and the census
    would then confidently name reds from a population the verdict never saw). The fail-fast
    strip is delegated to `publish_scope.remainder_pytest_argv` -- the same primitive the
    non-blocking annotation pass uses -- for the same reason: ONE definition of "without -x".
    """
    try:
        from background import publish_scope
        argv = list(publish_scope.remainder_pytest_argv(list(gate_argv)))
    except Exception:  # noqa: BLE001 -- an unavailable scoper must not cost us the census
        argv = [a for a in gate_argv if a not in ("-x", "--exitfirst")]
    argv = [a for a in argv if not str(a).startswith("--maxfail")]
    argv.append("--maxfail={}".format(GATE_RED_CENSUS_MAXFAIL))
    return argv


def _remaining_path_budget_seconds(*, cap, margin, minimum, now_monotonic=None, started=None):
    """Seconds a post-gate step may run for, DERIVED from the publish path's own remaining bound.

    ONE definition, because the two steps that need it drifted apart when there were two
    (2026-08-20): the census derived correctly while the remainder annotation carried
    `GATE_SUITE_TIMEOUT_SECONDS` -- 5x the entire post-gate allowance it lives in -- and the
    caller killed a GREEN, PUBLISHED cycle at 5400s, recording it as a gate failure. A second
    copy of this arithmetic is how that happens; a second CALLER of this function is not.

    The budget is (what the caller allows) - (what we have already spent) - (what the path
    still needs after us), capped at `cap`, and floored to 0 below `minimum` -- 0 meaning
    "do not start", never "you have no time, go anyway"."""
    now = time.monotonic() if now_monotonic is None else float(now_monotonic)
    start = _PROCESS_STARTED_MONOTONIC if started is None else float(started)
    budget = min(cap, PUBLISH_PATH_TIMEOUT_SECONDS - (now - start) - margin)
    return budget if budget >= minimum else 0.0


def red_census_budget_seconds(now_monotonic=None, started=None):
    """Seconds the census may run for, DERIVED from the publish path's own remaining bound.

    Returns 0 when there is not enough left to be worth starting. The publish path is killed by
    its caller at PUBLISH_PATH_TIMEOUT_SECONDS; a census that ran past that would be killed
    mid-write and take the fail-fast record with it, turning a diagnostic improvement into a
    LOST payload. So the budget is (what the caller allows) - (what we have already spent) -
    (what the red path still needs after us), capped, and floored at zero."""
    return _remaining_path_budget_seconds(
        cap=GATE_RED_CENSUS_MAX_SECONDS,
        margin=GATE_RED_CENSUS_PATH_MARGIN_SECONDS,
        minimum=GATE_RED_CENSUS_MIN_SECONDS,
        now_monotonic=now_monotonic, started=started,
    )


def _default_census_runner(argv, cwd, env, timeout):
    return subprocess.run(argv, cwd=cwd, env=env, timeout=timeout,
                          capture_output=True, text=True, errors="replace")


def run_red_census(gate_argv, cwd, full_env, fail_fast_ids, *, runner=None, budget=None):
    """(node_ids, status) -- the WHOLE red set behind the fail-fast verdict, best effort.

    NEVER raises and NEVER returns less than it was given: the result always starts from
    `fail_fast_ids` (the node id the blocking verdict actually named) and the census only ADDS
    to it. A census that crashed, timed out, was skipped for budget, or somehow failed to
    re-observe the gate's own red therefore degrades to exactly today's payload -- labelled
    `fail_fast_only` so the reader is never told a truncated set is a complete one."""
    known = [str(n) for n in (fail_fast_ids or [])]

    def _key(line):
        """The NODE ID, stripped of pytest's own outcome word.

        The two runs are independent, so the same test can arrive as `FAILED x` from one and
        `ERROR x` from the other (a fixture that errors under load, collection order). Deduping
        on the decorated line would then report one test twice and inflate the depth claim --
        and an inflated depth is the same kind of lie as a truncated one."""
        s = str(line).strip()
        for word in ("FAILED ", "ERROR "):
            if s.startswith(word):
                return s[len(word):].strip()
        return s

    seen = {_key(n) for n in known}

    def _merged(extra):
        out = list(known)
        for n in extra:
            if _key(n) not in seen:
                seen.add(_key(n))
                out.append(str(n))
        return out

    budget = red_census_budget_seconds() if budget is None else float(budget)
    if budget <= 0:
        log("Publish gate red census SKIPPED: no budget left inside the publish path's bound "
            "-- the blocking test above is the fail-fast one, and may not be the only red.")
        return known, CENSUS_FAIL_FAST_ONLY
    argv = red_census_argv(gate_argv)
    try:
        result = (runner or _default_census_runner)(argv, str(cwd), full_env, budget)
    except subprocess.TimeoutExpired:
        log("Publish gate red census TIMED OUT after {:.0f}s -- reporting the fail-fast test "
            "only.".format(budget))
        return known, CENSUS_FAIL_FAST_ONLY
    except Exception as exc:  # noqa: BLE001 -- a diagnostic must never red the path it observes
        log("Publish gate red census unavailable ({}: {}) -- reporting the fail-fast test "
            "only.".format(type(exc).__name__, exc))
        return known, CENSUS_FAIL_FAST_ONLY
    out = "{}\n{}".format(getattr(result, "stdout", "") or "",
                          getattr(result, "stderr", "") or "")
    ids = _parse_failed_node_ids(out)
    if not ids:
        # The census ran and printed no summary section at all (crash, OOM, collection error).
        # An absent answer reads as absent -- it is NOT evidence that the fail-fast red is alone.
        log("Publish gate red census produced no FAILED/ERROR summary (rc={}) -- reporting the "
            "fail-fast test only.".format(getattr(result, "returncode", "?")))
        return known, CENSUS_FAIL_FAST_ONLY
    merged = _merged(ids)
    status = CENSUS_PARTIAL if len(ids) >= GATE_RED_CENSUS_MAXFAIL else CENSUS_COMPLETE
    log("Publish gate red census: {} red test(s) behind the fail-fast verdict ({}).".format(
        len(merged), status))
    return merged, status


def _write_blocking_tests(node_ids, git_hash, census=CENSUS_FAIL_FAST_ONLY):
    """Publish the red gate's blocking node IDs for the alarm process. Never raises.

    `total_red` is the size of the set BEFORE the citation cap, so a reader can tell a cap that
    bound from one that did not -- the cap must never be able to look like the answer."""
    try:
        GATE_BLOCKING_TESTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        GATE_BLOCKING_TESTS_FILE.write_text(json.dumps(
            {"ts": time.time(), "git_hash": str(git_hash),
             "census": str(census), "total_red": len(node_ids),
             "node_ids": [str(n) for n in node_ids[:GATE_MAX_CITED_BLOCKING_TESTS]]},
            sort_keys=True))
    except OSError as exc:
        log("Publish gate: could not record the blocking test(s) for the alarm: {}".format(exc))


def _clear_blocking_tests():
    """A green gate retires the previous red's node IDs. Never raises."""
    try:
        GATE_BLOCKING_TESTS_FILE.unlink()
    except FileNotFoundError:
        pass
    except OSError as exc:
        log("Publish gate: could not clear the stale blocking-test record: {}".format(exc))


# ── THE RECORD MUST CARRY WHAT THE PUBLISHER ALREADY SAW (2026-08-26, five consecutive
# refusals recorded as `blocking_tests: []`) ─────────────────────────────────────────────────
#
# WHY. `_log_gate_failure_payload` above closes this hole for the publisher's OWN scoped gate.
# It does nothing for the OTHER red the publisher meets: the pre-commit HOOK CHAIN, which runs
# inside `git commit` and refuses on its own suite. On that path the publisher's scoped gate was
# GREEN -- so `_clear_blocking_tests` had just deleted the record -- and the hook chain's verdict
# was captured, tailed into `sim-runner-log.md`, and dropped. Observed 2026-08-26 04:40Z: the log
# names six failing node ids and "[test-gate] TESTS FAILED -- COMMIT REFUSED", while
# `.publish_gate_state.json` read `blocking_tests: []`, `total_red: 0`, `suspects: {}` through
# five consecutive refusals. That is FAIL-SILENT at the RECORD layer (R15): the diagnostic was
# taken and thrown away, so the wedge draw, the alarms and four direction records reasoned about
# a deadline while the machine held the answer -- the 840s deadline raised the day before was
# bought with this blindness, and the gate that night finished in 636s and was refused on TESTS.
#
# WHAT. The same cross-process file the alarm already reads, written by the only code that holds
# the hook chain's output. Two properties this must have, both mutation-tested:
#   * A REFUSAL CARRYING A RED POPULATES IT. Parsed from `_parse_failed_node_ids`, the same
#     parser the blocking gate uses, so the two can never disagree about what a failure is.
#   * A REFUSAL CARRYING NO RED WRITES NOTHING. A parser that always finds something is the
#     fail-open twin of the fail-silent it replaces: a non-test refusal (scope-evidence,
#     level-promotion, the finding-class gate) and a clean empty index must both leave the
#     record ABSENT, which every reader already renders as "unrecorded" rather than as a guess.
# BOTH STREAMS, IN FULL, not the `_tail` the log line uses: `stderr_tail(...) or
# stderr_tail(...)` returns ONE stream, and the hook chain's pytest writes its summary to stdout
# while git writes its own errors to stderr -- so the log's own tail can be the stream that does
# NOT carry the answer, and its 40-line bound can cut the summary section off the top.
def _record_commit_refusal_reds(stdout, stderr, git_hash="unknown"):
    """Publish the node IDs the pre-commit HOOK CHAIN named, for the alarm. Never raises.

    Returns the node ids recorded -- empty when the refusal named no test, which is a fact and
    not a failure of this function."""
    try:
        node_ids = _parse_failed_node_ids("{}\n{}".format(stdout or "", stderr or ""))
    except Exception as exc:  # noqa: BLE001 -- a diagnostic must never red the path it observes
        log("Publish commit refusal: could not parse the hook chain's output ({}: {}) -- "
            "no blocking test recorded.".format(type(exc).__name__, exc))
        return []
    if not node_ids:
        # THE ANSWER WAS IN THE BUFFER THIS FUNCTION ALREADY HELD (2026-09-02). Saying only
        # "no blocking test" is true and useless: it leaves the reader with the stale list a
        # previous cycle wrote. Name the gate when its banner is here, and say plainly that
        # nothing named it when it is not -- unnameable must read as unnameable.
        gate = _parse_refusing_gate("{}\n{}".format(stdout or "", stderr or ""))
        log("Publish commit REFUSED with no FAILED/ERROR summary in the hook chain's output -- "
            "recording NO blocking test. {} An absent answer must read as absent, never as a "
            "guess.".format(
                "The gate that refused is the {}: running the test suite will not clear "
                "it.".format(gate) if gate else
                "No gate banner this classifier knows was in the output either, so the refusal "
                "is UNNAMEABLE from here -- read the hook output itself, and do not read an "
                "earlier cycle's blocking list as this cycle's cause."))
        return []
    log("Publish commit REFUSED by the hook chain -- blocking test(s): {}".format(
        "; ".join(node_ids[:GATE_MAX_CITED_BLOCKING_TESTS])))
    _write_blocking_tests(node_ids, git_hash, census=CENSUS_HOOK_CHAIN)
    return node_ids


def last_blocking_tests(now=None, path=None):
    """(node_ids, git_hash) from the last red gate, or ([], None) if not knowably recent.

    ([], None) is returned for absent, unreadable, malformed AND stale -- all four mean the
    same thing to a reader, which is "this alarm does not know", and the alarm says so.

    THE BODY LIVES IN A LEAF NOW (2026-08-21). The contract is unchanged and still has exactly
    one implementation; it moved to `background/publish_gate_blocking_read.py` because the
    supervisor's RUNG-1 draw asks it, and importing THIS module to ask put every
    supervisor-importing test inside the publish gate -- 36 test files of harness
    self-governance that cannot make a published figure wrong. See that module's docstring for
    the measurement. The POLICY stays here (the age bound is derived from this module's own
    gate timeout) and is passed at call time, so monkeypatching either constant on this module
    still steers the read exactly as before."""
    return publish_gate_blocking_read.read_blocking_record(
        path if path is not None else GATE_BLOCKING_TESTS_FILE,
        now=now,
        max_age=GATE_BLOCKING_TESTS_MAX_AGE_SECONDS,
        max_cited=GATE_MAX_CITED_BLOCKING_TESTS,
    )


def last_red_census(now=None, path=None):
    """(status, total_red) for the record `last_blocking_tests` just read.

    Kept a SEPARATE reader rather than widening that tuple: every caller of it wants the node
    ids, only the payload builders want the census, and a four-tuple would have had three call
    sites unpacking a field they ignore.

    Every unreadable shape answers `fail_fast_only` -- the census is a claim of COMPLETENESS,
    and a record that cannot substantiate that claim must not make it. A record written before
    this field existed reads as `fail_fast_only` too, which is exactly what it was."""
    p = Path(path) if path is not None else GATE_BLOCKING_TESTS_FILE
    now = time.time() if now is None else float(now)
    try:
        rec = json.loads(p.read_text())
        if not isinstance(rec, dict):
            return CENSUS_FAIL_FAST_ONLY, 0
        ts = rec.get("ts")
        if not isinstance(ts, (int, float)) or now - float(ts) > GATE_BLOCKING_TESTS_MAX_AGE_SECONDS:
            return CENSUS_FAIL_FAST_ONLY, 0
        status = rec.get("census")
        if status not in (CENSUS_COMPLETE, CENSUS_PARTIAL, CENSUS_FAIL_FAST_ONLY,
                          CENSUS_HOOK_CHAIN):
            return CENSUS_FAIL_FAST_ONLY, 0
        total = rec.get("total_red")
        return str(status), int(total) if isinstance(total, int) else 0
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return CENSUS_FAIL_FAST_ONLY, 0


def _run_weather_data(git_hash="unknown"):
    from tools.fetch_weather_data import generate_weather_data
    generate_weather_data(git_hash=git_hash)


def _fmt_gbp(v):
    """Format a GBP value with sign and £ prefix, e.g. £+225,920 or £-3,766."""
    sign = "+" if v >= 0 else ""
    return "\xa3{}{:,.0f}".format(sign, v)


def _cohort_coverage_gate_permits_publish():
    """Coverage-report PUBLISH GATE — director condition #3 of the generator
    population activation (POPULATION_ACTIVATION_AND_RUN_LEDGER 2026-07-25 §1.3;
    POOL_VS_BOOK_LAMBDA_STANDS 2026-07-27): when the R13 draw is ACTIVE
    (``SE_DRAW_POPULATION=1``) no derived figure may reach a surface until the
    realised-cohort coverage report is emitted and passes the redundancy floor —
    "a thin draw stops the number reaching a surface" (ruling §3). Thin cells are
    reported (in the written artifact + this log), never smoothed (R12).

    Returns True (publish may proceed) / False (block, caller NTFYs on gate fail).

    INERT WHEN OFF: reads the activation env var DIRECTLY (same signal
    ``live_population.draw_population_enabled`` uses) and returns True with ZERO
    new import/exception surface, so today's static-book publish path stays
    byte-identical and this gate can never jam it (the control-false-positive
    failure mode). FAIL-CLOSED WHEN ON: any exception building the report is a
    FAILED gate (R15 fail-silent doctrine — an unavailable check is a failed
    check), so it blocks rather than falling through to publication."""
    import os
    if os.environ.get("SE_DRAW_POPULATION", "") != "1":
        return True  # R13 draw inactive -> static-book path, inert & byte-identical
    try:
        from tools.generate_cohort_coverage import build_artifact, write_artifact
        artifact = build_artifact()
        write_artifact(artifact)
        gate_ok = bool(artifact.get("gate_ok"))
    except Exception as exc:  # noqa: BLE001 - unavailable coverage build == FAILED gate
        log("Coverage gate: realised-coverage report FAILED to build ({}); "
            "blocking publish (fail-closed, R15)".format(exc))
        return False
    if not gate_ok:
        cov = artifact.get("coverage", {}) or {}
        log("Coverage gate BLOCKED publish: realised draw fails the redundancy "
            "floor; thin cells NAMED = {}".format(cov.get("thin_cells", [])))
        return False
    log("Coverage gate PASSED: realised-cohort coverage meets floor; report written.")
    return True


def _trigger_frozen_baseline_refresh_out_of_band(git_hash="unknown"):
    """Spawn the weekly frozen-policy baseline refresh as a DETACHED background
    process when (and only when) it is stale -- never block the publish path.

    The refresh itself (tools.run_frozen_baseline.generate) holds a non-blocking
    single-writer lock, so spawning it every cycle a stale baseline is seen
    cannot stack overlapping multi-minute decade replays: the second and later
    spawns take the lock's absence and exit at once. Detached via
    start_new_session so it outlives this publish process; its output is
    discarded (it writes site/state/frozen_policy_baseline.json directly)."""
    sys.path.insert(0, str(PROJECT_DIR))
    from tools.run_frozen_baseline import should_refresh_baseline
    if not should_refresh_baseline():
        return
    proc = subprocess.Popen(
        [sys.executable, "-m", "tools.run_frozen_baseline", "--if-stale"],
        cwd=str(PROJECT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    log("Frozen-policy baseline stale -> refresh spawned OUT OF BAND (PID {}); "
        "publishing continues with the existing baseline (never blocks).".format(proc.pid))


def generate_dashboard_json(json_path, git_hash="unknown"):
    """Generate site/data/dashboard.json and every downstream site/state artifact.

    Returns False if the cross-surface consistency gate failed (Part C of the
    website-integrity fix: a mismatch must be surfaced loudly, never shipped
    silently) so the caller can NTFY immediately. The gate result is captured
    but must NOT short-circuit the rest of this function -- every generator
    below (shadow HTML, PROJECT_STATE.txt, billing ledger, population
    anchoring, customers.json, supplier.json, live decisions, scenario
    analysis, GitHub Pages mirror) has to run every cycle regardless of the
    gate outcome. (QG_REOPENED_R2.md, 2026-07-04: an early `return ok` here
    made all of the below dead code since Phase QF -- none of it had run on
    any auto-processed cycle since.)"""
    ok = True
    # Coverage-report publish gate (director condition #3). MUST run before any
    # derived-figure generator below so a thin R13 draw cannot reach a surface.
    # Inert while SE_DRAW_POPULATION is off (byte-identical); fail-closed when on.
    if not _cohort_coverage_gate_permits_publish():
        return False
    # PER-STEP PUBLISH LEDGER (2026-08-17, BLOCKING finding
    # WORKER_FINDING_THE_PUBLISH_PATH_SWALLOWED_199_GENERATOR_CRASHES).
    # Every `except Exception: log(...)` below converts a generator failure into a
    # SILENTLY FROZEN artefact: the file the failed step should have refreshed stays on
    # the publish path and keeps being served, and every control that reads it is
    # satisfied by it. 199 crashes ran for four days that way. The swallow is correct
    # (one dead generator must not cost the other twenty their publish); the SILENCE is
    # the defect. Steps converted to `_ledger.step(...)` record which artefact they did
    # NOT refresh, publish that to site/data/publish_steps.json, and NTFY once on the
    # clean->degraded transition (R5).
    _ledger = PublishStepLedger(run_stamp=git_hash, log=log)
    try:
        # Frozen-policy baseline (weekly, expensive): a full-decade replay x2
        # under CURRENT_POLICY vs NAIVE_POLICY, each invoking the real risk
        # committee (localhost Ollama LLM calls) -- MINUTES of wall-clock,
        # longer than a whole publish cycle. It MUST NOT run synchronously here.
        # PURPOSE/GUARANTEE (2026-07-29 wedge retro): the publish path is bounded
        # and never blocks on this OPTIONAL weekly artifact. Running it inline
        # wedged publishing -- 22 run_complete markers backed up, background_worker's
        # 900s per-marker timeout killing the processor and re-attempting forever,
        # the baseline 15 days stale so should_refresh_baseline() fired every cycle.
        # When stale we spawn the refresh OUT OF BAND (detached, single-writer
        # lock in run_frozen_baseline.generate) and continue immediately with the
        # existing baseline; the fresh result is picked up next cycle.
        # generate_dashboard_data below reads whatever frozen_policy_baseline.json
        # is on disk, so a deferred refresh never blanks the surface.
        _trigger_frozen_baseline_refresh_out_of_band(git_hash)
    except Exception as exc:
        log("Frozen-policy baseline out-of-band trigger failed (non-fatal): {}".format(exc))
    with _ledger.step("Margin bridge generation", ["site/data/margin_bridge.json"]):
        # D2_three_clocks (2026-07-12, ADVISOR_STEER_TWIN_READONLY.md real
        # finding): the settlement<->billed reconciliation bridge existed
        # only as a standalone script, never wired into the run pipeline --
        # "a first-class, always-on mechanism" per this atom's own
        # registration text. Must run before generate_dashboard_data, which
        # now reads its output (_check_bridge_reconciles).
        from tools.generate_margin_bridge import generate as gen_bridge
        bridge = gen_bridge(json_path)
        log("Generated site/data/margin_bridge.json (gap={:,.2f}, unexplained={:,.2f})".format(
            bridge.get("total_gap_gbp", 0.0), bridge.get("unexplained_remainder_gbp", 0.0)))
    # `ok` is the CONSISTENCY-GATE verdict, a different subject from "did this step
    # run": a generation exception must not false-alarm the gate (its own note below),
    # so the pre-set survives the step and only the ledger records the failure.
    ok = True
    with _ledger.step("Dashboard data generation", ["site/data/dashboard.json"]):
        from tools.generate_dashboard_data import generate
        ok = generate(json_path)
        if ok:
            log("Generated site/data/dashboard.json")
        else:
            log("CONSISTENCY GATE FAILED — dashboard/exec-summary surfaces disagree (see stderr above)")
    with _ledger.step("Customer data generation", ["site/data/customers/"]):
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    with _ledger.step("Billing ledger generation", ["site/state/billing_ledger.json"]):
        # Must run before generate_invoice_data: real per-invoice bill-equation
        # data (usage, rate, standing charge) is wired from this ledger into the
        # customer JSON here; also must run before generate_shadow_html which reads
        # it independently.
        from tools.generate_billing_ledger import generate as gen_ledger
        gen_ledger(json_path)
        log("Generated site/state/billing_ledger.json")
    with _ledger.step("Invoice data generation", ["site/data/customers/"]):
        from tools.generate_invoice_data import generate as gen_inv
        gen_inv(json_path)
        log("Generated customer invoice JSON")
    with _ledger.step("Payment ledger generation", ["site/data/customers/"]):
        # Must run after generate_billing_ledger (real payments/arrears_history
        # source) and generate_invoice_data (patches the same customer JSON
        # files, this generator only adds a new "ledger" key alongside them).
        # BILLING_AND_PAYMENTS_LEDGER.md: Statement/Cashflow views.
        from tools.generate_payment_ledger_data import generate as gen_pay_ledger
        gen_pay_ledger()
        log("Generated per-account payment ledger JSON (BILLING_AND_PAYMENTS_LEDGER.md Statement/Cashflow)")
    with _ledger.step("Customer consumption generation", ["site/data/customers/"]):
        from tools.generate_customer_consumption import generate as gen_consumption
        gen_consumption(json_path)
        log("Generated customer consumption JSON (USAGE panel)")
    with _ledger.step("Customer reaction-chain generation", ["site/data/customers/"]):
        # Must run after generate_customer_data/generate_invoice_data/
        # generate_customer_consumption: patches real timeline "effect"
        # annotations (item 3) and the reaction_chain (item 4) onto the
        # per-customer JSON those steps already produced.
        from tools.generate_customer_reaction_chain import generate as gen_reaction
        gen_reaction(json_path)
        log("Generated customer timeline effects + reaction_chain (CUSTOMER_360_REDESIGN.md v4 items 3-4)")
    with _ledger.step("Portfolio event stream generation", ["site/data/dashboard.json"]):
        # Must run after generate_dashboard_data (dashboard.json must exist)
        # and generate_billing_ledger (arrears-opened events need it).
        # SUPPLIER_TAB_OVERHAUL.md THE SPINE: portfolio event stream.
        from tools.generate_portfolio_event_stream import generate as gen_pes
        gen_pes(json_path)
        log("Generated portfolio event stream onto dashboard.json (SUPPLIER_TAB_OVERHAUL.md spine)")
    with _ledger.step("Sim data generation", ["site/data/sim_data.json"]):
        from tools.generate_sim_data import generate as gen_sim
        gen_sim(git_hash)
        log("Generated site/data/sim_data.json")
    with _ledger.step("Customer sample generation", ["site/data/customer_sample.json"]):
        from tools.generate_customer_sample import generate as gen_sample
        gen_sample(json_path)
        log("Generated site/data/customer_sample.json")
    # R11 no-orphan-transition fix (2026-07-14, surfaced by SITE1 Director-door
    # cold-eyes): these two generators were NOT wired into the pipeline, so
    # site/data/director_twin.json + provisional_plan.json froze/drifted after
    # every run. Wire them so the director-facing surfaces stay current.
    try:
        from tools.generate_director_twin_data import main as gen_twin
        gen_twin()
        log("Generated site/data/director_twin.json")
    except Exception as exc:
        log("Director twin data generation failed: {}".format(exc))
    try:
        from tools.generate_provisional_plan_data import main as gen_plan
        gen_plan()
        log("Generated site/data/provisional_plan.json")
    except Exception as exc:
        log("Provisional plan data generation failed: {}".format(exc))
    # Same no-orphan-transition rule, applied at the point the defect would be created
    # rather than after it froze (SITE_director_window_delta_view, 2026-08-03). The
    # delta feed is derived from the OTHER director feeds, so leaving it unwired would
    # freeze it against feeds that keep moving -- the exact 2026-07-14 failure above,
    # one layer up. Note this regenerates the DELTA only; the last-look STAMP is
    # deliberately never advanced here (it moves only on an explicit --mark-seen), or
    # the baseline would re-base every run and the panel would read "nothing changed"
    # forever.
    try:
        # Import generate(), NOT main(): main() is the CLI entry point and parses
        # sys.argv, so an in-process call inherited THIS process's arguments and
        # argparse exited with SystemExit(2) -- a BaseException the `except Exception`
        # below does not catch, i.e. it would abort the whole publish mid-way rather
        # than degrade to a logged failure. Caught by
        # test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status.
        from tools.generate_director_data import generate as gen_director_delta
        gen_director_delta()
        log("Generated site/data/director_delta.json")
    except Exception as exc:
        log("Director delta data generation failed: {}".format(exc))
    try:
        # SITE_evidence_pages_behind_nodes: /evidence/ renders the primary-state
        # evidence behind every model-on-a-page node -- atom levels, ledger records,
        # cited artefacts, test counts. It derives ENTIRELY from sources that move on
        # their own (docs/design/maturity_map.yaml, gate_authorizations.jsonl,
        # test_execution_log.jsonl), so leaving it unwired would have frozen the page
        # at whatever was committed the day it was built while the map moved beneath
        # it -- an evidence surface that silently describes a past state is worse than
        # no evidence surface. Same orphan-transition defect as the 2026-07-14
        # director_twin.json/provisional_plan.json freeze; closed here rather than
        # filed as a finding.
        #
        # generate() raises EvidenceSourceUnavailable BEFORE writing on a missing or
        # empty source, so a bad source leaves the PREVIOUS page live rather than
        # replacing it with a plausible blank (fail-closed, its own docstring).
        # RETIRED from the cycle 2026-08-20. /evidence/ is deleted (director ruling: the five
        # tabs are the site) and its 301 lands on /harness/. Leaving this call in is not a
        # harmless no-op: it RECREATED site/evidence/index.html thirty minutes after the
        # directory was deleted, and the page reappeared on the live site. A generator that
        # outlives its page is how a deleted surface comes back, and it is the mechanical form
        # of the "permanent limbo" the ruling names.
        #
        # THE PAYLOAD IS WIRED BACK, THE PAGE IS NOT (2026-08-22). The clause above reasoned
        # about the PAGE and took the PAYLOAD with it, and the payload has a second consumer:
        # `generate_capabilities_door` (the very next step) reads site/data/evidence.json for
        # the "Checked by N automated checks, last run <date>" line on the LIVE Capabilities
        # door. With this step dropped, evidence.json froze at 2026-08-20T06:59Z while the
        # door's own feed kept being rewritten every cycle -- observed 2026-08-22: a
        # capabilities_door.json stamped 10:02:21Z publishing `last_run 2026-08-20` to nine
        # capabilities. A stale figure inside a fresh feed is worse than a stale page, because
        # nothing on the surface says it is old.
        #
        # Safe to call now because the RESURRECTION IS FIXED AT THE SINK, not here:
        # generate() no longer mkdirs the door's directory and writes the page only if that
        # directory already exists, so this call cannot bring /evidence/ back. That is the
        # order this project keeps having to relearn -- the caller is not the fix.
        from tools.generate_evidence_data import generate as gen_evidence
        _ev = gen_evidence()
        log("Refreshed site/data/evidence.json ({} citations; no page -- /evidence/ retired)"
            .format(_ev["totals"]["citations"]))
    except Exception as exc:
        log("Evidence step failed: {}".format(exc))
    try:
        # SITE7: the Capabilities door. Every status on it is DERIVED from the work record
        # and the boundary walker, so a feed not regenerated here is a page that silently
        # freezes at whatever was true the day it was built -- the same orphan-transition
        # defect the evidence page directly above was wired in to close. Fail-closed by
        # construction: generate() raises CapabilitySourceUnavailable BEFORE writing on a
        # missing source or a phantom citation, so a bad source leaves the PREVIOUS feed
        # live rather than replacing it with a plausible blank.
        from tools.generate_capabilities_door import generate as gen_capabilities_door
        gen_capabilities_door()
        log("Generated site/data/capabilities_door.json (SITE7 Capabilities door)")
    except Exception as exc:
        log("Capabilities door generation failed: {}".format(exc))
    try:
        # SITE5: which Knowledge pages are due for review. The rule itself is
        # site/knowledge/review_state.py; running it here is what stops it being a rule
        # exercised only by its own test (the no-caller class the orphan ratchet refused
        # this module's first landing for). The log line is the operator signal -- staleness
        # surfaces without anyone opening the site -- and the artefact is what the Knowledge
        # index will render so a reader sees which pages are stale BEFORE clicking in.
        from tools.generate_knowledge_review import generate as gen_k_review
        from tools.generate_knowledge_review import needs_attention, unwritten
        _kr = gen_k_review()
        # TWO numbers, deliberately. The first counts pages a reader could be MISLED by --
        # written but unchecked, or checked too long ago. The second counts topics with no
        # page yet. Writing a page moves it from the second to the first and reduces neither
        # risk; only a check against the published source does that.
        log("Generated site/data/knowledge_review.json -- {} Knowledge page(s) could mislead "
            "a reader, {} not written yet {}".format(
                needs_attention(_kr), unwritten(_kr), _kr["tally"]))
    except Exception as exc:
        log("Knowledge review generation failed: {}".format(exc))
    try:
        # G13: the proof-of-caller for the projection store. G12 built the store on 2026-08-11
        # and NOTHING READ IT for eight days -- the "design with no caller" the founding
        # instruction was written to end, reproduced by the very atom meant to prevent it.
        # Running the feed generator here is what makes the store a dependency of publishing
        # rather than a thing that exists. Same shape and same failure posture as the two
        # generators above: a raise leaves the PREVIOUS feed live rather than replacing it
        # with a plausible blank.
        from tools.generate_projections_page import generate as gen_projections
        _pj = gen_projections()
        log("Generated site/data/projections.json from the projection store (G13 proof-of-caller)")
    except Exception as exc:
        log("Projections page generation failed: {}".format(exc))
    try:
        # Must run after generate_customer_reaction_chain (timeline/reaction_chain
        # patched) and generate_customer_sample (churn_accuracy_by_renewal source).
        # WEBSITE_AS_SHOWCASE.md tab 4: case-study recommender.
        from tools.generate_case_study_recommender import generate as gen_case_studies
        gen_case_studies()
        log("Generated site/data/case_studies.json (WEBSITE_AS_SHOWCASE.md tab 4 case-study recommender)")
    except Exception as exc:
        log("Case-study recommender generation failed: {}".format(exc))
    try:
        # RETIRED from the cycle 2026-08-20, same reason as the evidence page above: the
        # /shadow/ mirror is deleted and this call put it straight back. It was an INTERNAL
        # surface that was nonetheless published at a second root on the public site, carrying
        # the full internal vocabulary -- exactly the hidden page the ruling is about.
        pass
    except Exception as exc:
        log("Shadow mirror step failed: {}".format(exc))
    try:
        from tools.generate_project_state import generate as gen_state
        gen_state()
        log("Generated site/state/PROJECT_STATE.txt")
    except Exception as exc:
        log("PROJECT_STATE generation failed: {}".format(exc))
    try:
        from tools.generate_phases_json import generate as gen_phases
        gen_phases()
        log("Generated site/data/phases.json")
    except Exception as exc:
        log("phases.json generation failed: {}".format(exc))
    # RETIRED from the cycle 2026-08-20 (director: "we built too much surface too early and
    # it's slowing us down"). site/data/test_mix.json was fetched by exactly one page,
    # /project/, which 301'd to /proof/ on 2026-07-23 and is now deleted. Generating it cost
    # 30-40s of pytest --collect-only subprocesses EVERY publish cycle -- roughly 7% of an
    # 8-9 minute cycle, spent on a file no reader could ever load, for four weeks.
    #
    # The comment that used to sit here justified the cost as "a <10% time addition
    # (BUDGET_UNCONSTRAINED.md)". That document's premise was withdrawn as false on
    # 2026-08-03 and CLAUDE.md says never to cite it again; it was still load-bearing here.
    #
    # tools/generate_test_mix_data.py is KEPT and still runnable on demand -- the composition
    # breakdown is a real harness measurement, it just does not need recomputing every cycle
    # for nobody. Wire it back the moment a reachable page renders it.
    try:
        from tools.generate_capabilities_json import generate as gen_capabilities
        gen_capabilities()
        log("Generated site/data/capabilities.json")
    except Exception as exc:
        log("capabilities.json generation failed: {}".format(exc))
    try:
        from tools.generate_maturity_map_data import generate as gen_maturity_map
        gen_maturity_map()
        log("Generated site/data/maturity_map.json")
    except Exception as exc:
        log("maturity_map.json generation failed: {}".format(exc))
    try:
        from tools.generate_simplified_data import generate as gen_simplified
        gen_simplified()
        log("Generated site/data/simplified.json")
    except Exception as exc:
        log("simplified.json generation failed: {}".format(exc))
    try:
        # PRODUCTION_READINESS_EVIDENCE_PASS.md's Part A found company/data/*.db
        # (the company's own operational financial/customer state) had NO
        # off-machine copy at all -- matches the "unrecoverable canonical data"
        # immediate-action carve-out. Rides along on the existing run-complete
        # cycle rather than a new standalone schedule; safe to run every cycle
        # (byte-identical DBs produce a clean no-op commit).
        from background.backup_company_data import backup_once
        backed_up = backup_once()
        log("Backed up company/data/*.db to ops repo: {}".format(backed_up))
    except Exception as exc:
        log("company/data backup failed: {}".format(exc))
    try:
        from tools.generate_saas_coverage_data import generate as gen_saas_coverage
        gen_saas_coverage()
        log("Generated site/data/saas_coverage.json")
    except Exception as exc:
        log("saas_coverage.json generation failed: {}".format(exc))
    try:
        from tools.generate_system_status import generate as gen_system_status
        gen_system_status()
        log("Generated site/data/system_status.json")
    except Exception as exc:
        log("system_status.json generation failed: {}".format(exc))
    try:
        from tools.population_anchor import generate as gen_anchor
        gen_anchor(json_path)
        log("Generated site/state/population_anchoring.json")
    except Exception as exc:
        log("Population anchoring failed: {}".format(exc))
    try:
        from tools.generate_customers_json import generate as gen_customers
        gen_customers(json_path)
        log("Generated site/data/customers.json")
    except Exception as exc:
        log("customers.json generation failed: {}".format(exc))
    try:
        from tools.generate_supplier_json import generate as gen_supplier
        gen_supplier(json_path)
        log("Generated site/data/supplier.json")
    except Exception as exc:
        log("supplier.json generation failed: {}".format(exc))
    try:
        from tools.project_portfolio_to_2026 import generate as gen_portfolio
        gen_portfolio(json_path)
        log("Generated site/state/live_portfolio.json")
    except Exception as exc:
        log("Live portfolio generation failed: {}".format(exc))
    try:
        # S1 Option A: extend the real Elexon SSP cache forward past 2025-06-07 on a
        # rolling basis BEFORE the live decision reads market state, so market_as_of_date
        # advances as real settlement data is published. Fully defensive (never raises,
        # never corrupts the frozen historical cache) -- a network-less/failed run is a
        # no-op and the decision falls back to the last known real price, honestly labelled.
        from background.refresh_elexon_ssp_rolling import refresh as refresh_ssp
        st = refresh_ssp()
        log("Rolling Elexon SSP refresh: {} ({} new records)".format(
            st.get("status"), st.get("fetched_records", 0)))
    except Exception as exc:
        log("Rolling Elexon SSP refresh failed (non-fatal): {}".format(exc))
    try:
        from tools.run_live_decisions import run_decisions
        run_decisions()
        log("Generated site/state/live_decisions_latest.json")
    except Exception as exc:
        log("Live decisions generation failed: {}".format(exc))
    try:
        from tools.run_live_decisions import run_scenario_analysis
        run_scenario_analysis()
        log("Generated site/state/scenario_analysis_latest.json")
    except Exception as exc:
        log("Scenario analysis generation failed: {}".format(exc))
    try:
        # Must run after run_live_decisions (reads live_decisions_log.jsonl it appends
        # to) and before generate_method_data (folds the scorecard onto the public
        # Method page -- S1 Decision 2: public from day one, misses included).
        from tools.generate_track_record_scorecard import generate as gen_scorecard
        gen_scorecard()
        log("Generated site/state/track_record_scorecard.json (Phase RX / S1 Option B)")
    except Exception as exc:
        log("Track record scorecard generation failed: {}".format(exc))
    try:
        from tools.generate_method_data import generate as gen_method
        gen_method()
        log("Generated site/data/method.json")
    except Exception as exc:
        log("method.json generation failed: {}".format(exc))
    try:
        # G11 activity-cost + utilisation (Method-door section): a reporting layer
        # over git history + the token log + the escalation register. Wired here
        # for the SAME R11 no-orphan-transition reason as the doors below -- a
        # generated surface must ride the regen cycle or it silently freezes
        # against its live sources. Its data file is ALSO in git_commit_push's
        # commit-list (both halves wired). DIAGNOSTIC never a target (R12).
        from tools.generate_activity_cost_data import generate as gen_activity_cost
        gen_activity_cost()
        log("Generated site/data/activity_cost.json (G11 activity-cost + utilisation)")
    except Exception as exc:
        log("activity_cost.json generation failed: {}".format(exc))
    try:
        # Door 4 THE PROOF + Door 3 THE COMPANY: their generators were built with
        # the pages but NOT wired here, so the pages froze against their own live
        # sources (Door-4 cold-eyes caught it: proof.json showed 60 atoms vs a live
        # 61). Run AFTER the maturity-map/scorecard/dashboard regen above (their
        # inputs) and BEFORE the GitHub-pages mirror below (so the mirror ships the
        # fresh copies). R11 no-orphan-transition: a generated surface must ride the
        # regen cycle or it silently decays.
        from tools.generate_proof_data import generate as gen_proof
        gen_proof()
        log("Generated site/data/proof.json (Door 4 THE PROOF)")
    except Exception as exc:
        log("proof.json generation failed: {}".format(exc))
    try:
        from tools.generate_company_data import generate as gen_company
        gen_company()
        log("Generated site/data/company.json (Door 3 THE COMPANY)")
    except Exception as exc:
        log("company.json generation failed: {}".format(exc))
    try:
        # The growth curve WITH the reason it has that shape (director, 2026-08-24: "if our own
        # code binds growth rather than the simulated economics, say so on the site"). The
        # campaign has been writing docs/observability/book_growth_campaign.json every run and
        # NOTHING read it, so a year flattened by our settlement engine reached the site looking
        # exactly like a supplier that ran out of money. Wired HERE, on the regen cycle, for the
        # R11 no-orphan-transition reason: a generated surface that does not ride the cycle
        # freezes against its live source, and this one exists precisely to track it.
        from tools.generate_book_growth_data import generate as gen_growth
        grown = gen_growth()
        log("Generated site/data/book_growth.json ({} year(s), engine-bound: {})".format(
            len(grown.get("years") or []), grown.get("engine_bound_years")))
    except Exception as exc:
        log("book_growth.json generation failed: {}".format(exc))
    try:
        # THE BASELINE THE PUBLISHED SUPPLIER HAS TO BEAT (site/data/value_arms.json). The
        # director's thesis: "there has to be a BASELINE to beat -- the same book run by a
        # supplier applying flat rules with no per-customer view -- or 'it performed well' means
        # nothing." The three-arm A/B measured it and reached no reader: publishing the
        # profitable half while withholding the comparison that qualifies it is the closest
        # thing to a misleading claim this project has. Wired HERE for two reasons: the R11
        # no-orphan-transition reason its neighbours carry, AND because the feed re-checks every
        # publish whether the run being published is still the same supplier as the A/B's
        # control arm -- a check that only means something if it runs on the publish path.
        from tools.generate_value_arms_data import generate as gen_value_arms
        arms = gen_value_arms()
        log("Generated site/data/value_arms.json (available={}, same supplier as the published "
            "run={})".format(arms.get("available"),
                             ((arms.get("realised") or {}).get("is_the_published_supplier")
                              or {}).get("same_supplier")))
    except Exception as exc:
        log("value_arms.json generation failed: {}".format(exc))
    try:
        # Explore stage 3's SECOND CLOCK (site/data/explore_hh_days.json). The stage is titled
        # "electricity across a day" and rendered it by YEAR, in the same table as gas, which
        # made the two clocks one clock and lost the thing that stage exists to teach. Wired
        # here for the same R11 no-orphan-transition reason as its neighbours: it names two
        # DATED days out of a meter's record and corroborates them against the company's own
        # published feed, so it must ride the cycle or it freezes against both sources.
        from tools.generate_explore_hh_day import generate as gen_hh_day
        hh_day = gen_hh_day()
        log("Generated site/data/explore_hh_days.json ({} meter(s) with a day, {} without)"
            .format(len(hh_day.get("accounts") or {}),
                    len(hh_day.get("accounts_without_half_hourly") or [])))
    except Exception as exc:
        log("explore_hh_days.json generation failed: {}".format(exc))
    try:
        # Door 5 THE WORLD operational window -- the intra-day wholesale market feed
        # (site/data/market.json). Reads docs/market_data/price_feed.json and derives
        # the movement (latest / trajectory / session range / last change) so the
        # World panel can show what the market is DOING, not its annual mean
        # (director, 2026-07-20). Wired here for the SAME R11 no-orphan-transition
        # reason as the doors below -- a generated surface must ride the regen cycle
        # or it silently freezes against its live source. Its output file is picked
        # up by the site/data/*.json commit glob further down (no explicit path append
        # needed -- that is the durable class-fix for the orphaned-at-commit gap).
        from tools.generate_market_data import generate as gen_market
        gen_market()
        log("Generated site/data/market.json (Door 5 intra-day market feed)")
    except Exception as exc:
        log("market.json generation failed: {}".format(exc))
    try:
        # Door 5 THE WORLD: the two-sided epistemic-wall page (SIM ground truth vs
        # COMPANY observation + divergence) + the anchors register. Wired here for
        # the SAME R11 no-orphan-transition reason as Door 3/4 above -- a generated
        # surface must ride the regen cycle or it silently freezes against its live
        # sources (the exact orphaned-generator defect Door 4's cold-eyes caught).
        # Runs AFTER the dashboard/sim_data/anchoring regen it reads from.
        from tools.generate_world_data import generate as gen_world
        gen_world()
        log("Generated site/data/world.json (Door 5 THE WORLD)")
    except Exception as exc:
        log("world.json generation failed: {}".format(exc))
    try:
        # Door 5 demand-arrow evidence: the WORDS->DIAGRAM->EVIDENCE campaign
        # requires the weather->demand arrow of the World causal spine to carry its
        # belief-vs-truth chart. A rendering of the already-measured W1_5 coupled-gap
        # result -- wired here for the same R11 no-orphan-transition reason as world.json
        # (a generated surface must ride the regen cycle or it silently freezes).
        from tools.generate_premise_demand_data import generate as gen_premise_demand
        gen_premise_demand()
        log("Generated site/data/premise_demand.json (Door 5 demand-arrow evidence)")
    except Exception as exc:
        log("premise_demand.json generation failed: {}".format(exc))
    # (2026-07-20 v4 site rebuild) The combined "Method + Simplified" casebook surface
    # (site/method-casebook/) was RETIRED -- redundant with the separate canonical Method
    # (roles/rules/loop/retro/track-record) and Simplified (register) doors, which cover its
    # content. Its generator + commit-list entries removed with it.
    try:
        from tools.mirror_github_pages import mirror as mirror_gh_pages
        mirrored = mirror_gh_pages()
        log("Mirrored {} file(s) to docs/shadow + docs/state for GitHub Pages".format(len(mirrored)))
    except Exception as exc:
        log("GitHub Pages mirror failed: {}".format(exc))
    # Publish the per-step record LAST, so it describes the cycle that just ran, and
    # alert only on the clean<->degraded transition (R5). Wrapped because a diagnostic
    # must never red the path it observes -- but note the asymmetry that keeps this from
    # being the very defect it closes: a write failure leaves NO ledger on disk, and
    # `publish_step_ledger.read_ledger` RAISES on a missing ledger rather than reporting
    # a clean one. An unwritten record reads as UNKNOWN, never as "everything published".
    try:
        _ledger.write()
        _transition = _ledger.notify_on_transition()
        if _ledger.degraded():
            log("PUBLISH DEGRADED: {} of {} step(s) failed -- STALE on the publish path: {}".format(
                len(_ledger.failing_steps()), len(_ledger.steps),
                ", ".join(_ledger.stale_artefacts()) or "no named artefact"))
        if _transition:
            log("Publish-step ledger: NTFY sent on transition {}".format(_transition))
    except Exception as exc:  # noqa: BLE001 -- see above; absence of the file is the signal
        log("Publish-step ledger write/alert failed: {}".format(exc))
    return ok


def generate_site(data, elapsed_s, git_hash, finished_ts):
    """No-op: site/index.html is a static SPA that reads site/data/dashboard.json."""
    pass


# ── WHY A FAILED PUBLISH AND AN EMPTY ONE MUST NOT BE THE SAME ANSWER ────────────────────────
#
# `git_commit_push` returns a bare False for six different things, and `_process` used to treat
# all six identically: log one line and write the run's fingerprint anyway. Two of the six mean
# "there was nothing to publish" and four mean "the publish FAILED". Writing the fingerprint is
# correct for the first pair and catastrophic for the second, because the change-detection gate
# then SKIPS every subsequent identical cycle -- so the commit-timeout branch's own promise,
# "Nothing committed; retrying next cycle", was false the moment it was made. That is the second
# half of the 2026-08-13 freeze: the first commit died on the hook deadline at 22:29, the
# fingerprint recorded the run as processed, and the retry the log promised never ran again for
# that output. Only a CHANGE in the sim's figures could break the loop.
#
# So the outcome is now NAMED, not inferred from a boolean, and `_process` fingerprints on
# exactly the two no-op reasons. New failure paths added here default to NOT fingerprinting:
# `RETRYABLE_PUBLISH_OUTCOMES` is the small closed set, and everything unlisted is treated as a
# failure worth retrying, so forgetting to classify a future branch fails toward re-publishing.
PUBLISHED = "published"                       # the commit reached origin
NOTHING_TO_COMMIT = "nothing_to_commit"       # the index was empty -- a real no-op
COMMITTED_PUSH_THROTTLED = "committed_push_throttled"   # landed locally, push deferred by design
COMMIT_TIMEOUT = "commit_timeout"             # the hook chain outran the deadline
COMMIT_REFUSED = "commit_refused"             # a gate said no, or git failed
PUSH_DID_NOT_REACH_ORIGIN = "push_did_not_reach_origin"
PROVENANCE_REFUSED = "provenance_refused"     # fail-closed: we would have published a false stamp
BEHIND_ORIGIN = "behind_origin"               # origin is ahead: a commit here CANNOT be pushed
TREE_LOCK_UNAVAILABLE = "tree_lock_unavailable"   # another writer held the tree lock; nothing ran
#: Outcomes after which re-running this identical cycle would genuinely find nothing to do. Every
#: other outcome leaves the fingerprint alone so the next cycle really does retry.
RETRYABLE_PUBLISH_OUTCOMES = frozenset({PUBLISHED, NOTHING_TO_COMMIT, COMMITTED_PUSH_THROTTLED})
#: Outcomes that report their OWN exit code rather than the generic EXIT_PUBLISH_DID_NOT_LAND,
#: because the reader is sent somewhere different to look. Kept as a mapping beside the closed
#: set above so `publish_exit_code` stays the single place both answers are decided.
NAMED_PUBLISH_EXIT_CODES = {TREE_LOCK_UNAVAILABLE: EXIT_TREE_LOCK_UNAVAILABLE}
#: The four outcomes that all report rc=77, mapped onto the causes the LATER process records.
#: Two vocabularies rather than one because they answer different questions and are read by
#: different people: an outcome decides what THIS process does next (fingerprint? which exit
#: code?), a cause tells a reader of the alarm what happened and what to go and look at. The
#: mapping is the seam between them and is asserted exhaustive by a control -- an outcome added
#: here without a cause reads as `unattributed`, which is honest, and the control says so.
PUBLISH_CAUSE_FOR_REASON = {
    COMMIT_REFUSED: publish_cause.GATE_REFUSAL,
    COMMIT_TIMEOUT: publish_cause.DEADLINE_KILL,
    PUSH_DID_NOT_REACH_ORIGIN: publish_cause.PUSH_NEVER_LANDED,
    PROVENANCE_REFUSED: publish_cause.PROVENANCE_REFUSED,
    BEHIND_ORIGIN: publish_cause.BEHIND_ORIGIN,
}
#: The cause a COMMIT_REFUSED cycle records when the hook chain named NO red test (2026-09-02).
#: NOT in the table above, and that is the content of this constant rather than an omission: the
#: table is keyed by OUTCOME, and this process takes the same outcome either way -- the commit was
#: refused, the cycle retries. The split is in the OBSERVATION only (did the chain name a red?),
#: which is known at exactly one branch, so the override is read there and the name lives here so
#: it is greppable and so the closed-set control below can see both routes.
NON_TEST_REFUSAL_CAUSE = publish_cause.NON_TEST_GATE_REFUSAL
#: Every cause produced by an explicit override at the branch that observed it, rather than by the
#: outcome table. Held equal to the vocabulary WITH the table by a control -- a cause that neither
#: route can produce is a branch no reader will ever see, and that property is what the control
#: protects. This set is load-bearing (the refusal branch reads `NON_TEST_REFUSAL_CAUSE` itself),
#: never a list written beside the code that could drift from it.
PUBLISH_CAUSE_OVERRIDES = frozenset({NON_TEST_REFUSAL_CAUSE})


def publish_exit_code(reason):
    """The exit code a COMPLETED publish cycle reports, from the outcome `git_commit_push` named.

    THE SAME CLOSED SET DECIDES BOTH ANSWERS. This reads `RETRYABLE_PUBLISH_OUTCOMES` -- the set
    that already decides whether to fingerprint the cycle -- so "this cycle is unfinished, retry
    it" and "this cycle did not publish, alarm on it" can never drift apart into two lists that
    disagree about the same outcome. Before 2026-08-19 only the first of those two consequences
    existed: the fingerprint was correctly withheld fourteen times running while the exit code
    said 0 every time, so the pipeline knew it had to retry and the alarm was told it had
    succeeded. See EXIT_PUBLISH_DID_NOT_LAND for the incident.

    Extracted as a function, not left inline at the return, because it is the whole content of
    that finding and a test must be able to enumerate it exhaustively over every outcome
    constant this module declares.

    FAIL-CLOSED: an unrecognised or missing reason is NOT a publish. A future outcome added
    without being classified therefore reports "did not land" and gets an alarm, rather than
    inheriting rc=0 and the silence that cost 11.5 hours of stale public figures.

    `NAMED_PUBLISH_EXIT_CODES` is consulted only AFTER the retryable set, so an outcome can
    never buy itself a 0 by naming a code: the two questions stay in the order that makes
    "did this publish?" answerable without knowing what the code is for.
    """
    if reason in RETRYABLE_PUBLISH_OUTCOMES:
        return 0
    return NAMED_PUBLISH_EXIT_CODES.get(reason, EXIT_PUBLISH_DID_NOT_LAND)


def _git_knows_path(path) -> bool:
    """Is `path` legal as a commit pathspec even though it is not on disk?

    A path staged as a DELETION is gone from the worktree but must stay in the pathspec, or the
    deletion stays staged forever and the next writer commits it. `HEAD:<rel>` resolves for a
    blob or a tree, which is exactly the "git has heard of this" question.
    """
    try:
        rel = os.path.relpath(str(path), str(PROJECT_DIR))
        return subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", "HEAD:{}".format(rel)],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30,
        ).returncode == 0
    except Exception:  # noqa: BLE001 -- an unanswerable question is not a licence to include
        return False


def _commit_pathspec(files, extra_relative=()):
    """The paths the publish commit may touch, and nothing else.

    `git commit -m msg` commits the whole INDEX, so anything any other writer had staged --
    before this process took the tree lock, which is why the lock never protected against it --
    went out under the publish's own message. The fix is the shape this module already uses 400
    lines below: `git commit -m msg -- <paths>`.

    Two properties this function owes the caller:

      * DROP WHAT GIT CANNOT MATCH. An unmatched pathspec makes git reject the WHOLE commit
        ("did not match any file(s) known to git"), so one absent optional artefact would take
        the entire publish down -- trading a scoping defect for an availability one.
      * NEVER RETURN EMPTY. `git commit -m msg --` with no paths is a bare index commit again,
        i.e. the exact defect, arrived at by degradation. The caller refuses instead.

    Note the deliberate cost: a partial commit takes the WORKTREE copy of each named path, not
    the index copy. For this surface they are the same file (everything here was just `git
    add`ed from the worktree two lines earlier), and taking the worktree copy of OUR OWN
    artefacts is strictly better than taking the index copy of EVERYONE'S.
    """
    spec, seen = [], set()
    for candidate in list(files) + [str(PROJECT_DIR / rel) for rel in extra_relative]:
        if candidate in seen:
            continue
        seen.add(candidate)
        if Path(candidate).exists() or _git_knows_path(candidate):
            spec.append(candidate)
    return spec


def _clear_two_rooms_before_commit() -> dict:
    """Clear a staging duplicate that appeared DURING this run, immediately before committing.

    THE REPAIR ALREADY EXISTED AND ALREADY RAN. It ran too early to help.
    `background_worker` calls `staging_two_rooms_repair.observe()` once at the TOP of its cycle
    and then spends the rest of that cycle inside this publish, which routinely takes forty-five
    minutes. `finding_classes --check` is a pre-commit gate, so the refusal is evaluated at the
    FAR END of that interval. The window in which a duplicate can wedge a publish is therefore
    exactly the window in which the repairer cannot get another turn — and the next turn only
    comes after the publish it would have saved has already been refused.

    Measured, 2026-09-04: the sweep sat clean at 12:30, two preregistrations were written into
    both the root and `records/` at 13:01 and 13:06, and the commit at the end of that same cycle
    was refused on them. `staging_two_rooms_repair.classify` graded BOTH `redundant` — the repair
    was one function call away for the whole 45 minutes and structurally could not be reached.

    So the repair moves to the point of use. This is the same shape as re-reading a fork
    measurement immediately before acting on it rather than at the top of the turn: a check whose
    subject can change under you is worth only as much as its recency at the moment of decision.

    NOT a replacement for the worker's sweep, which still catches duplicates that appear while no
    publish is running. Two call sites of one repair, because they cover different intervals.

    Never raises. A publish must not die of its own housekeeping — the failure this fixes is a
    refused commit, and turning that into a crashed publisher would be a worse outage than the
    one it prevents.
    """
    try:
        from background import staging_two_rooms_repair
        return staging_two_rooms_repair.repair(staging=PROJECT_DIR / "docs" / "staging")
    except Exception as exc:  # noqa: BLE001
        return {"repaired": [], "conflicts": [], "error": str(exc)}


COMMIT_HOOK_DURATION_PATH = (
    PROJECT_DIR / "docs" / "observability" / "commit_hook_duration.jsonl")


def _record_commit_hook_duration(elapsed_seconds: float, git_hash: str, outcome: str) -> None:
    """How long the pre-commit HOOK CHAIN actually took, recorded against the deadline that
    actually kills it.

    THE THING THAT TIMES OUT WAS THE ONE THING UNMEASURED. `publish_gate_duration.jsonl` records
    the publisher's OWN scoped gate and grades its headroom against `GATE_SUITE_TIMEOUT_SECONDS`
    (3800s), reporting `band: ok, headroom_ratio: 0.85` -- while the commit that runs a comparable
    chain was being killed at 600s. Two deadlines differing by a factor of six, and the one the
    instrument grades against is not the one that binds. Twelve consecutive publish failures on
    2026-08-25 produced no record of how long the chain took, only that it exceeded a number.

    A SEPARATE LEDGER, deliberately: this is a different subject from the publisher's scoped gate,
    and folding the two series together would make both unreadable. The same recorder, so the
    banding, the headroom ratio and the transition alarm are the ones already trusted elsewhere.

    NEVER RAISES. An observer that can take down the publish it observes is itself a defect.
    """
    try:
        from background.suite_duration_watch import record_gate_run

        record_gate_run(float(elapsed_seconds), GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
                        str(git_hash or "unknown"), outcome, COMMIT_HOOK_DURATION_PATH)
    except Exception:  # noqa: BLE001 - see docstring
        pass


def _git_said_nothing_to_commit(tail) -> bool:
    """Did git refuse because the index was EMPTY, rather than because a hook said no?

    ONE predicate, shared with `_commit_and_push_paths`, which needs the same distinction to
    decide whether to log loudly. Two copies of this test drifting apart would let a hook refusal
    read as a clean no-op on one path and an alarm on the other."""
    return bool(tail) and "nothing to commit" in tail.lower()


def _git_add_or_refuse(args, *, timeout, label) -> bool:
    """`git add` the given argv tail, and answer whether it ACTUALLY staged.

    THE ADD'S RETURN CODE WAS NEVER READ, SO THE COMMIT'S ERROR BECAME THE DIAGNOSIS
    (2026-08-25, WORKER_FINDING_A_STALE_INDEX_LOCK...). A stale `.git/index.lock` --
    1,274,828 bytes, no git process alive -- made `git add` fail with *"Unable to create
    '.git/index.lock': File exists"*. That stderr was captured into a variable nobody read
    and discarded. Nothing was staged, so the `git commit -- <pathspec>` that followed was
    handed paths the index had never heard of, and reported:

        error: pathspec 'docs/staging/done/run_complete_...md' did not match any file(s)

    about a file that existed, was not ignored, and was perfectly legal to add. Nine
    consecutive publish cycles failed that way and the reader was sent after the LAST LINK
    for 1h43m while the cause sat in a discarded pipe.

    `git add` is ALL-OR-NOTHING: one bad path, or one lock, and NOTHING is staged. So an
    unchecked rc here can only ever produce a misleading downstream error, never a truthful
    one -- which is why this is a shared helper and not a fix at the one site that was
    caught. Every add on the publish path answers here or the class comes back.

    Deliberately NOT a stale-lock reaper: deleting a lock automatically is how a LIVE
    `git commit` gets its index corrupted, and this repository's pre-commit gates hold that
    lock legitimately for forty-five minutes at a stretch. Say the truth loudly; let a seat
    decide. (Confirmed at the fix: the lock present while writing this was a live gate's,
    not a stale one.)
    """
    try:
        result = subprocess.run(["git", "add"] + list(args), cwd=str(PROJECT_DIR),
                                timeout=timeout, capture_output=True, text=True)
    except subprocess.TimeoutExpired as exc:  # noqa: PERF203 -- a hung add is a refusal too
        log("{}: `git add` TIMED OUT after {}s -- nothing is staged, so the commit that "
            "would follow could only report a confusing pathspec error. Refusing this cycle; "
            "the next one retries. ({})".format(label, timeout, exc))
        return False
    if result.returncode != 0:
        # BOTH streams: git puts "Unable to create index.lock" on stderr, but a pathspec
        # complaint can land on stdout, and an empty diagnostic here is the whole defect.
        tail = (stderr_tail(getattr(result, "stderr", None))
                or stderr_tail(getattr(result, "stdout", None))
                or "no output captured from `git add`")
        log("{}: `git add` FAILED (rc={}) -- NOTHING IS STAGED. This, not any pathspec error "
            "from the commit that would follow, is the cause. Refusing this cycle so the "
            "next one retries.\n{}".format(label, result.returncode, tail))
        return False
    return True


#: How long to wait on the network read that decides whether origin has moved. Generous, because
#: the alternative to a slow answer here is a commit that cannot be pushed; and bounded, because
#: this runs inside a publish cycle that must finish.
DIVERGENCE_FETCH_TIMEOUT_SECONDS = 60


def _commits_origin_is_ahead_by():
    """How many commits origin/main holds that local HEAD does not. `None` means UNREADABLE.

    GROUND TRUTH, NOT THE TRACKING REF. `refs/remotes/origin/main` is only as fresh as the last
    successful fetch, and a REJECTED push is exactly the case where it may not have been updated
    -- so reading it would answer "zero" in the one state this function exists to detect. This
    fetches an explicit refspec and reads FETCH_HEAD, which is what the remote said just now.
    Same lesson, same file: `_push_reached_origin` reads `ls-remote` and not the tracking ref,
    for the 3.5-hour origin-freeze of 2026-07-24.

    `None` is a real third answer and is NOT folded into zero. `git rev-list --count` always
    prints an integer, so an empty or unparseable stdout means git did not answer the question,
    not that the answer was nought -- and "missing reads as zero" is the fail-open shape that
    would let this guard pass in precisely the conditions (no network, broken remote) under
    which a commit is least likely to reach origin.
    """
    try:
        fetched = subprocess.run(["git", "fetch", "--quiet", "origin", "main"],
                                 cwd=str(PROJECT_DIR), capture_output=True, text=True,
                                 timeout=DIVERGENCE_FETCH_TIMEOUT_SECONDS)
        if fetched.returncode != 0:
            return None
        counted = subprocess.run(["git", "rev-list", "--count", "HEAD..FETCH_HEAD"],
                                 cwd=str(PROJECT_DIR), capture_output=True, text=True,
                                 timeout=DIVERGENCE_FETCH_TIMEOUT_SECONDS)
        if counted.returncode != 0:
            return None
        return int((counted.stdout or "").strip())
    except (ValueError, OSError, subprocess.SubprocessError):
        return None


def _divergence_refusal():
    """The evidence string for refusing to commit, or `None` when committing is legal.

    THE RETRY IS THE THING THAT WIDENS THE FORK (2026-09-01). Measured that morning:
    `origin/main..HEAD` = 3, `HEAD..origin/main` = 23, and two of the three local commits were
    `Auto-process run complete` -- produced by this loop, after this loop's push had already
    been rejected non-fast-forward. The push path treated the rejection as a transient and
    re-attempted identically; being behind origin is a STATE, and every attempt added another
    unpushable commit to the side of the fork that could not move.

    REFUSE RATHER THAN INTEGRATE, and the choice is not a preference. The only sanctioned
    reconciliation in this repository is `python3 -m tools.surgical_land --merge origin/main`
    (CLAUDE.md's hook-bypass wall), which gates the whole tree and takes longer than a publish
    cycle; and there are routinely three lanes with uncommitted work in this tree. A daemon that
    merged unattended would be deciding, every twelve minutes, to move other people's work. So
    the publish path stops, says the state and the remedy, and the site keeps serving its last
    honest figures -- which it was doing anyway, since nothing committed here could be pushed.
    """
    ahead = _commits_origin_is_ahead_by()
    if ahead == 0:
        return None
    if ahead is None:
        return ("origin is UNREADABLE (`git fetch origin main` or the rev-list that follows it "
                "did not answer), so whether a commit here could be pushed cannot be "
                "established -- refusing rather than creating one that may be rejected")
    return ("origin/main is {} commit(s) AHEAD of HEAD, so a commit created here could only be "
            "rejected non-fast-forward and would widen the fork by one more. Reconcile first: "
            "`python3 -m tools.surgical_land --merge origin/main`".format(ahead))


def git_commit_push(git_hash, net_margin, outcome=None):
    """Commit and push the publish surface. Returns True iff the content is committed.

    `outcome`, when given, is a dict this fills with {"reason": <one of the constants above>} so
    the caller can tell a no-op from a failure. Optional and keyword-safe on purpose: every
    existing caller and test passes two positional args and is unaffected.

    `_outcome`'s `evidence` argument is what closes the nine-episode attribution hole (see
    PUBLISH_CAUSE_FILE): this function is the ONE funnel every publish outcome passes through,
    so the cause record is written in exactly one place and no future branch can name an
    outcome without passing through the write."""
    def _outcome(reason, value, evidence=None, cause=None):
        if outcome is not None:
            outcome["reason"] = reason
        # The observation that decided it, recorded WHERE IT WAS OBSERVED. A reason with no
        # evidence writes nothing rather than an empty attribution -- `publish_cause` maps only
        # the four rc=77 reasons, so the retryable outcomes and TREE_LOCK_UNAVAILABLE (which
        # carries its own exit code and its own alarm text) fall through silently by design.
        #
        # `cause` OVERRIDES the reason->cause table for the one outcome whose reason is not
        # fine-grained enough to carry its own answer (2026-09-02). COMMIT_REFUSED is a single
        # OUTCOME -- this process does the same thing next either way -- covering two distinct
        # EXPERIENCES: the test gate judged and named reds, or a non-test gate refused ahead of
        # it and nothing was judged at all. The table maps outcomes, and it is still the only
        # writer; the split belongs to the observation at the branch that made it, which is the
        # only place the red count is known. See `publish_cause.NON_TEST_GATE_REFUSAL`.
        if evidence is not None:
            publish_cause.record_cause(PUBLISH_CAUSE_FILE,
                                       cause or PUBLISH_CAUSE_FOR_REASON.get(reason),
                                       evidence, git_hash)
        return value

    report = PROJECT_DIR / "docs" / "reports" / "ANNUAL_REPORT.md"
    site_index = PROJECT_DIR / "site" / "index.html"
    site_data = PROJECT_DIR / "site" / "data" / "dashboard.json"
    site_customers = PROJECT_DIR / "site" / "data" / "customers"
    site_sample = PROJECT_DIR / "site" / "data" / "customer_sample.json"
    site_shadow = PROJECT_DIR / "site" / "shadow"
    files = [str(report), str(LATEST_MD)]
    # H11_naive_organ: commit the organ's question log alongside the run whose
    # publish cycle produced it (LATEST.md's digest block is already tracked).
    if NAIVE_ORGAN_LOG.exists():
        files.append(str(NAIVE_ORGAN_LOG))
    if site_index.exists():
        files.append(str(site_index))
    if site_data.exists():
        files.append(str(site_data))
    # The provenance/freshness banner travels WITH the content it describes on a green cycle
    # (on a red cycle it goes alone, via _publish_provenance_banner). Same commit = the stamp
    # and the figures it vouches for can never be a cycle apart on origin.
    site_provenance = PROJECT_DIR / "site" / "data" / "publish_provenance.json"
    if site_provenance.exists():
        files.append(str(site_provenance))
    if site_customers.exists():
        files.append(str(site_customers))
    if site_sample.exists():
        files.append(str(site_sample))
    if site_shadow.exists():
        files.append(str(site_shadow))
    site_state_sample = PROJECT_DIR / "site" / "state" / "customer_sample.json"
    if site_state_sample.exists():
        files.append(str(site_state_sample))
    site_state_project = PROJECT_DIR / "site" / "state" / "PROJECT_STATE.txt"
    if site_state_project.exists():
        files.append(str(site_state_project))
    docs_status_project = PROJECT_DIR / "docs" / "status" / "PROJECT_STATE.txt"
    if docs_status_project.exists():
        files.append(str(docs_status_project))
    site_state_billing = PROJECT_DIR / "site" / "state" / "billing_ledger.json"
    if site_state_billing.exists():
        files.append(str(site_state_billing))
    site_state_anchor = PROJECT_DIR / "site" / "state" / "population_anchoring.json"
    if site_state_anchor.exists():
        files.append(str(site_state_anchor))
    site_data_customers = PROJECT_DIR / "site" / "data" / "customers.json"
    if site_data_customers.exists():
        files.append(str(site_data_customers))
    site_data_supplier = PROJECT_DIR / "site" / "data" / "supplier.json"
    if site_data_supplier.exists():
        files.append(str(site_data_supplier))
    site_state_scenario = PROJECT_DIR / "site" / "state" / "scenario_analysis_latest.json"
    if site_state_scenario.exists():
        files.append(str(site_state_scenario))
    site_state_decision_log = PROJECT_DIR / "site" / "state" / "live_decisions_log.jsonl"
    if site_state_decision_log.exists():
        files.append(str(site_state_decision_log))
    # Phase RO (NAV_STORY_PLATFORM_METHOD.md): site/index.html moved from the
    # Supplier dashboard to the new Home/Story landing; the dashboard itself
    # now lives at site/supplier/, and the new Platform section needs both its
    # static page and its generated data file tracked here or they never get
    # picked up by the auto-commit pipeline.
    site_supplier_html = PROJECT_DIR / "site" / "supplier" / "index.html"
    if site_supplier_html.exists():
        files.append(str(site_supplier_html))
    site_saas_coverage_json = PROJECT_DIR / "site" / "data" / "saas_coverage.json"
    if site_saas_coverage_json.exists():
        files.append(str(site_saas_coverage_json))
    site_method_html = PROJECT_DIR / "site" / "method" / "index.html"
    if site_method_html.exists():
        files.append(str(site_method_html))
    site_method_json = PROJECT_DIR / "site" / "data" / "method.json"
    if site_method_json.exists():
        files.append(str(site_method_json))
    # G11 activity-cost + utilisation section rides the Method door -- its data
    # file must be tracked here or the regenerated-but-uncommitted file stays
    # frozen on the live site (same orphan-transition reasoning as the blocks above).
    site_activity_cost_json = PROJECT_DIR / "site" / "data" / "activity_cost.json"
    if site_activity_cost_json.exists():
        files.append(str(site_activity_cost_json))
    site_case_studies_json = PROJECT_DIR / "site" / "data" / "case_studies.json"
    if site_case_studies_json.exists():
        files.append(str(site_case_studies_json))
    site_track_record_json = PROJECT_DIR / "site" / "state" / "track_record_scorecard.json"
    if site_track_record_json.exists():
        files.append(str(site_track_record_json))
    # Door 5 THE WORLD (two-sided epistemic-wall page + anchors register): the
    # page and its generated data file must be tracked here or the auto-commit
    # pipeline never picks up the freshly-regenerated world.json (same reasoning
    # as the Platform/Method blocks above -- a regenerated-but-uncommitted file
    # stays frozen on the live site).
    # 2026-08-20: site/world/index.html is DELETED (director ruling -- the five tabs are the
    # site). world.json is still generated and still tracked here: Capabilities reads it. The
    # PAGE went; the DATA has a reader, which is the same split made for dashboard.json.
    site_world_json = PROJECT_DIR / "site" / "data" / "world.json"
    if site_world_json.exists():
        files.append(str(site_world_json))
    # Door 5 operational window: the intra-day market feed derived from
    # price_feed.json. Tracked explicitly here (matching world/company/proof
    # above) AND covered by the site/data/*.json glob below -- belt-and-braces so
    # a regenerated-but-uncommitted market.json can never freeze on the live site.
    site_market_json = PROJECT_DIR / "site" / "data" / "market.json"
    if site_market_json.exists():
        files.append(str(site_market_json))
    # Door 4 THE PROOF + Door 3 THE COMPANY: their generators were wired into the
    # regen block above, but their data/page files were NOT added to this commit-
    # list -- so they regenerated every run yet the fresh copy was never committed,
    # leaving the deployed pages frozen (the same orphaned-at-commit gap Door 5
    # closed for world.json; caught by Door 5's cold-eyes). Track them here too.
    # Doors 3/4 (The Company, The Proof): page + generated data file tracked here or the
    # regenerated JSON stays frozen on the live site (the orphaned-at-commit gap Door 5
    # closed for world.json). (method-casebook retired 2026-07-20 -- entries removed.)
    # 2026-08-20: both PAGES are deleted; both DATA files stay and are still tracked here.
    # proof.json is what /harness/ renders -- including the store-agreement audit, which
    # followed the figures to their new page rather than dying with the old one. company.json
    # feeds Capabilities. A regenerated-but-uncommitted copy would freeze on the live site
    # exactly as before, so the reasoning above is unchanged; only the pages are gone.
    for _door_file in (
        PROJECT_DIR / "site" / "data" / "proof.json",
        PROJECT_DIR / "site" / "data" / "company.json",
    ):
        if _door_file.exists():
            files.append(str(_door_file))
    # R10 CLASS-CLOSURE for the orphaned-at-commit gap (SITE1 Expert-Hour,
    # 2026-07-16): the block above and the explicit method.json/world.json/etc.
    # appends fixed this gap ONE FILE AT A TIME, so three MORE generated data
    # files silently recurred it -- simplified.json (live showed 168/48 vs a real
    # 291/93, hiding ~42% of the "nothing filtered" register), provisional_plan.json
    # (2 days stale on the director page), system_status.json (6 days stale, the
    # action-needed queue). generate_*_data() writes every one of these under
    # site/data/ each cycle, so the durable fix is to commit the WHOLE generated
    # data surface, not to add another explicit path line each time a door is
    # built. Any future site/data/*.json is now tracked automatically.
    site_data_dir = PROJECT_DIR / "site" / "data"
    if site_data_dir.is_dir():
        for _gen_json in sorted(site_data_dir.glob("*.json")):
            files.append(str(_gen_json))
    # THE SAME CLASS, ON THE OTHER GENERATED DIRECTORY (2026-08-17, the three-day content
    # freeze). Everything above closed the orphaned-at-commit gap for `site/data/` with a glob and
    # then went straight back to hand-listing `site/state/` one path at a time -- customer_sample,
    # PROJECT_STATE, billing_ledger, population_anchoring, scenario_analysis_latest,
    # live_decisions_log, track_record_scorecard. Three files this cycle's own log says it
    # regenerates were never on that list and so were regenerated every cycle and committed by
    # none: `live_portfolio.json`, `live_decisions_latest.json`, `frozen_policy_baseline.json`.
    #
    # THAT IS NOT A COSMETIC STALENESS. `site/proof/`'s predictions ledger takes the PREDICTION
    # from `track_record_scorecard.json` (listed, committed) and the OUTCOME from
    # `live_portfolio.json` (not listed, never committed) -- so the published pair was guaranteed
    # to drift apart, and `site/proof/test_predictions_ledger_can_fail.py` refused this very
    # publish for exactly that reason: green in the working tree where both files are fresh, red
    # in the tree the commit would create where only one of them is.
    #
    # TRACKED FILES ONLY, deliberately: `site/state/` also accumulates ~23 untracked
    # `live_decisions_YYYYMMDD.json` dailies, and a bare glob would sweep every one of them into
    # a content publish. A file has to be added to git once, by whoever built it; from then on
    # its refresh is committed automatically and cannot silently freeze on the live site.
    site_state_dir = PROJECT_DIR / "site" / "state"
    if site_state_dir.is_dir():
        try:
            _tracked = subprocess.run(
                ["git", "ls-files", "-z", "--", "site/state"], cwd=str(PROJECT_DIR),
                capture_output=True, text=True, timeout=60,  # H30: stderr captured, not discarded
            )
            if _tracked.returncode == 0:
                for _rel in _tracked.stdout.split("\0"):
                    if _rel:
                        files.append(str(PROJECT_DIR / _rel))
            else:
                log("site/state tracked-file census failed (rc={}): {} -- falling back to the "
                    "explicit appends above".format(_tracked.returncode, _tracked.stderr.strip()))
        except Exception as _exc:  # noqa: BLE001 -- never take the publish down over a path list
            log("site/state paths not added to the commit (non-fatal): {}".format(_exc))
    # GitHub Pages mirror (docs/staging/ADVISOR_GITHUBIO_MIRROR.md): the advisor's
    # fetch path to poesys.net proved persistently stale independent of any CD
    # incident, so shadow pages + state JSONs also ship from docs/ (GitHub Pages),
    # same as docs/status/PROJECT_STATE.txt already does.
    docs_shadow = PROJECT_DIR / "docs" / "shadow"
    if docs_shadow.exists():
        files.append(str(docs_shadow))
    docs_state = PROJECT_DIR / "docs" / "state"
    if docs_state.exists():
        files.append(str(docs_state))
    # THIS RUN'S OWN MARKERS, BY NAME -- never `DONE_DIR` wholesale. See
    # `_MARKERS_ARCHIVED_BY_THIS_RUN` for what the directory add did to two other lanes'
    # BLOCKING findings. The reason for staging anything here at all is unchanged (a
    # `run_complete_*.md` moved to done/ and never committed sits untracked forever, observed
    # 7+ times); what changes is that the set is now exactly what this process moved.
    for _archived_marker_path in _MARKERS_ARCHIVED_BY_THIS_RUN:
        if Path(_archived_marker_path).exists():
            files.append(_archived_marker_path)
    # The derived-artefact repair (_repair_derived_artefacts_in) re-renders stale docs/design
    # projections in the working tree; without this they would be repaired every cycle and
    # committed by none, so the wedge would return on the next run. Driven off the REGISTER
    # rather than a path list, so a future derived artefact is committed automatically -- the
    # same class-closure shape as the site/data/*.json glob above, for the same reason.
    try:
        from background.derived_artefact_register import REGISTER as _DERIVED
        for _art in _DERIVED:
            _rendered = PROJECT_DIR / _art.rendered
            if _rendered.exists():
                files.append(str(_rendered))
    except Exception as _exc:  # noqa: BLE001 -- never take the publish down over a path list
        log("Derived-artefact paths not added to the commit (non-fatal): {}".format(_exc))
    # THE FIXTURE TOOK THE GREEN CYCLE, AND THE GUARD WAS ONLY ON THE RED ONE (2026-08-12).
    # `_provenance_is_publishable` was wired into `_commit_and_push_paths` alone -- the liveness
    # heartbeat and the red-cycle banner. But this function is the path that commits
    # site/data/dashboard.json AND site/data/publish_provenance.json together on every GREEN
    # cycle, and it is the path the ESTABLISHED incident actually took (`d4d1a04e6` published
    # `run_output_abc1234_...json` to origin). So the checker's own docstring -- "publishing a
    # false provenance is impossible from here" -- was true of the function it sat in and false
    # of the publisher: a control whose subject is narrower than the class it names.
    #
    # Same fail-closed direction as everywhere else on this surface: nothing publishes this
    # cycle, loudly, and the site keeps serving its last honest state. An unverified page is an
    # availability cost; a page stamped with a run that never happened is a public lie.
    if not _provenance_is_publishable(files, label="Auto-process publish"):
        return _outcome(PROVENANCE_REFUSED, False,
                        evidence="the fail-closed provenance check refused the stamp for "
                                 "git={} before any git command ran -- nothing was staged, "
                                 "no hook chain started and no push was attempted".format(
                                     git_hash))

    # BEFORE ANYTHING IS STAGED. The order is the whole repair: integrate (or refuse) BEFORE the
    # next publish commit is created, never after it has been rejected. See `_divergence_refusal`.
    # Building `files` above stages nothing -- it is a list of paths -- so this still runs before
    # the first `git add`, which is what that property is about.
    #
    # AND IT SITS AFTER THE PROVENANCE CHECK, DELIBERATELY (2026-09-01). It used to be the first
    # statement in this function, which made the provenance refusal's own recorded evidence --
    # "before any git command ran" -- false: the divergence read had already run `git fetch` and
    # `git rev-list`. Two fail-closed refusals in a row cannot mask each other into publishing, so
    # the order is free to be chosen, and the cheap LOCAL check belongs in front of the one that
    # opens a network round trip with a 60s timeout to answer a question we no longer need asked.
    _behind = _divergence_refusal()
    if _behind is not None:
        log("Publish commit REFUSED before staging: {}.".format(_behind))
        from background.notify import notify
        notify(
            "[SIM] PUBLISH REFUSED, ORIGIN AHEAD -- {} -- no commit was created, so the fork is "
            "not one wider than it was. Nothing is wrong with the run or the suite; the tree "
            "needs reconciling.".format(_behind),
            kind="real_alarm",
        )
        return _outcome(BEHIND_ORIGIN, False, evidence=_behind)

    msg = "Auto-process run complete: report + LATEST.md + site/ (git={}, net=\xa3{:,.0f})".format(
        git_hash, net_margin
    )
    # Serialize against other git writers (interactive session, autonomous_runner
    # turns, a concurrent process_run_complete.py invocation) -- see
    # background/tree_lock.py. Without this, a `git add` from another writer
    # staged between this one's add and commit gets swept into this commit
    # (observed directly: a manually-staged code change landed inside an
    # unrelated auto-process commit message).
    #
    # ACQUISITION IS GUARDED SEPARATELY FROM THE BODY (2026-08-30, see
    # EXIT_TREE_LOCK_UNAVAILABLE). Losing the lock is a contention outcome this publisher
    # already knows how to name; letting it escape `main()` as an uncaught TreeLockTimeout
    # made it rc=1, which the wedge classifier reads as a red test. ExitStack, rather than an
    # outer `try` around the whole `with`, so the except clause below can ONLY see a failure
    # to ACQUIRE -- a TreeLockTimeout raised from anywhere INSIDE the body would be a
    # different fact (a nested acquisition, i.e. the deadlock shape documented at
    # `_git_add_or_refuse`) and must not be mislabelled as contention in its turn.
    stack = ExitStack()
    try:
        stack.enter_context(tree_lock())
    except TreeLockTimeout as exc:
        log("Auto-process publish: tree lock held by another writer ({}) -- publishing NOTHING "
            "this cycle and retrying next. No test was run, so no test is implicated.".format(exc))
        return _outcome(TREE_LOCK_UNAVAILABLE, False)
    with stack:
        try:
            if not _git_add_or_refuse(files, timeout=120, label="Auto-process publish"):
                return _outcome(COMMIT_REFUSED, False,
                                evidence="`git add` of the publish surface failed, so NOTHING "
                                         "was staged -- the hook chain never ran and no test "
                                         "was judged. See the `git add` FAILED line in "
                                         "docs/observability/sim-runner-log.md")
            # Publish the pre-gate inbox fold too (maturity_map.yaml change + the deleted
            # atom_status inboxes) so a reconciled map lands WITH the run it belongs to,
            # never dangling uncommitted. -A stages the inbox DELETIONS. No-op if nothing
            # was folded this cycle.
            if not _git_add_or_refuse(
                    ["-A", "docs/design/maturity_map.yaml", "docs/design/maturity_map_closed.yaml",
                     "docs/design/atom_status"],
                    timeout=120, label="Auto-process publish (map fold)"):
                return _outcome(COMMIT_REFUSED, False,
                                evidence="`git add` of the maturity-map fold failed, so the "
                                         "commit was never attempted -- the hook chain never "
                                         "ran and no test was judged. See the `git add` FAILED "
                                         "line in docs/observability/sim-runner-log.md")
            # COMMIT TIMEOUT (2026-08-03): this is NOT a bare `git commit` -- it runs
            # the whole pre-commit hook chain (tools/git-hooks/pre-commit: status-honesty,
            # pre_commit_test_gate, level_promotion_gate, site_lane_gate,
            # moap_coherence_gate, ruling_archive_question_gate). A publish commit stages
            # site/data/**, which fires site_lane_gate's BROAD trigger -- the WHOLE site
            # suite, measured at 27.3s on its own, against the 30s cap this used to carry.
            # The cap was set when the hooks were trivial and quietly became a
            # publish-blocker as the suite grew: the deadline is now a property of how many
            # tests exist, not of whether the commit is healthy.
            # H30 (2026-08-08): BOTH streams, because the diagnostic here is the
            # pre-commit HOOK CHAIN's output (a gate refusal, a failing test),
            # which the hooks split across stdout and stderr. Without it,
            # "Nothing to commit or commit failed" below is unfalsifiable: a
            # clean no-op and a gate rejection produce the identical log line.
            # UNBUFFERED (2026-08-13): see GIT_COMMIT_HOOK_ENV_UNBUFFERED. Without it the
            # TimeoutExpired branch below prints "nothing captured before the kill" every
            # time, because each hook's progress is still in its own userspace buffer.
            # PATHSPEC, NOT THE INDEX (2026-08-18) -- see `_commit_pathspec`. The two
            # `docs/design` paths are the ones the `-A` add above stages, including the
            # atom_status inbox DELETIONS, so they must be named here or the fold never lands.
            pathspec = _commit_pathspec(
                files, ("docs/design/maturity_map.yaml", "docs/design/maturity_map_closed.yaml",
                        "docs/design/atom_status"))
            if not pathspec:
                log("Publish commit REFUSED: nothing in the publish surface is known to git, "
                    "so there is no pathspec to commit. Committing the bare index here would "
                    "carry whatever another lane had staged -- refusing instead; the site keeps "
                    "serving its last honest state and the next cycle retries.")
                # COMMIT_REFUSED, deliberately not NOTHING_TO_COMMIT: the latter is in
                # RETRYABLE_PUBLISH_OUTCOMES and would fingerprint this cycle as a genuine
                # no-op, so the run would never be published again. An empty pathspec is a
                # broken state, and the next cycle must really retry it.
                return _outcome(COMMIT_REFUSED, False)
            # A staging duplicate written WHILE this run was going refuses the commit below,
            # and the worker's own sweep ran before this run started. Repair at the point of
            # use -- see `_clear_two_rooms_before_commit` for the 45-minute blind window.
            _rooms = _clear_two_rooms_before_commit()
            if _rooms.get("repaired"):
                log("Cleared {} redundant staging duplicate(s) that would have refused this "
                    "publish commit: {}".format(len(_rooms["repaired"]),
                                                ", ".join(_rooms["repaired"])))
            if _rooms.get("conflicts"):
                # Said BEFORE the refusal rather than after it, so the log reads as a diagnosis
                # rather than a surprise. This branch cannot fix itself: the repairer is timid by
                # construction and will not delete a copy that carries text the other room lacks.
                log("TWO ROOMS, not safely repairable, so the commit below is expected to be "
                    "REFUSED and every other commit in the tree with it: {} -- resolve by hand."
                    .format(", ".join(_rooms["conflicts"])))
            _hook_started = time.monotonic()
            result = subprocess.run(["git", "commit", "-m", msg, "--"] + pathspec,
                                    cwd=str(PROJECT_DIR),
                                    timeout=GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
                                    env=_commit_hook_env(),
                                    capture_output=True, text=True)
            _record_commit_hook_duration(time.monotonic() - _hook_started, git_hash,
                                         "pass" if result.returncode == 0 else "refused")
        except subprocess.TimeoutExpired as exc:
            # UNCAUGHT, THIS CRASHED THE PUBLISH (CLAUDE.md's own standing learning:
            # "sim_runner TimeoutExpired must be caught -- uncaught exception kills the
            # loop"). It propagated out of _process(), so process_run_complete exited
            # rc=1 having logged NEITHER "Nothing to commit or commit failed" NOR "Done"
            # -- the wedge detector recorded it as a test_regression, which it was not,
            # and the diagnosis pointed at the test suite for hours. A slow hook chain
            # must degrade to "retry next cycle", never take the pipeline down, and must
            # say SO in the log.
            _hook_elapsed = time.monotonic() - _hook_started
            _record_commit_hook_duration(_hook_elapsed, git_hash, "timeout")
            _tail = stderr_tail(exc.stderr) or stderr_tail(exc.stdout)
            log("Commit TIMED OUT after {}s ({}) -- the pre-commit hook chain outran its "
                "deadline. Nothing committed; retrying next cycle. If this repeats, the "
                "hook chain (not the run) is the cause.{}".format(
                    GIT_COMMIT_HOOK_TIMEOUT_SECONDS, exc.__class__.__name__,
                    "\n  hook output before the kill (names the SLOW hook):\n{}".format(_tail)
                    if _tail else "\n  hook output: nothing captured before the kill"))
            # THE EVIDENCE IS A STOPWATCH, NOT A STATUS. A killed child has no return code to
            # reason from -- the elapsed wall time against the budget that killed it is the
            # only observation that separates this from a refusal, and it is exact.
            return _outcome(COMMIT_TIMEOUT, False,
                            evidence="the pre-commit hook chain was killed after {:.0f}s "
                                     "against its own {}s budget -- the suite was still "
                                     "running, so NO test returned a verdict and none is "
                                     "implicated".format(_hook_elapsed,
                                                         GIT_COMMIT_HOOK_TIMEOUT_SECONDS))
        if result.returncode != 0:
            # H30: which of the two it was is now IN the log, not inferred.
            _tail = (stderr_tail(getattr(result, "stderr", None))
                     or stderr_tail(getattr(result, "stdout", None)))
            log("Nothing to commit or commit failed (rc={}){}".format(
                result.returncode,
                "\n  git/hook output (last {} lines):\n{}".format(STDERR_TAIL_LINES, _tail)
                if _tail else "\n  git said nothing -- consistent with an empty index"))
            # H30 named the two in the LOG; this makes the caller able to act on the difference.
            # An empty index is a no-op; a hook refusal is a publish that FAILED and must retry.
            # Note the direction: an unreadable tail reads as REFUSED, never as a clean no-op --
            # the same fail-toward-retrying rule as RETRYABLE_PUBLISH_OUTCOMES.
            refused = not _git_said_nothing_to_commit(_tail)
            if refused:
                # The hook chain's verdict reaches the RECORD, not just this log line -- see
                # `_record_commit_refusal_reds`. Keyed on the REFUSAL, not on the no-op, so the
                # empty-index case cannot write a record at all.
                _reds = _record_commit_refusal_reds(getattr(result, "stdout", None),
                                                    getattr(result, "stderr", None), git_hash)
                # The red COUNT is part of the evidence, including when it is zero: "refused
                # naming no test" is what a non-test gate (orphan-ratchet, finding-class,
                # level-promotion) looks like, and saying so is what stops the reader running
                # the suite. Zero reds here is a fact about the refusal, not a missing answer.
                # WHICH REFUSAL THIS WAS, decided by the observation and not by the exit code:
                # zero reds means no test returned a verdict, so the cause must be the one
                # `publish_cause.no_test_was_judged` answers True for -- otherwise the stale
                # blocking list from an earlier cycle survives into the record every reader
                # quotes. That is the 18.7h wedge of 2026-09-02, where five GREEN tests were
                # named as the blockers of an orphan-ratchet refusal.
                _gate = _parse_refusing_gate("{}\n{}".format(
                    getattr(result, "stdout", None) or "", getattr(result, "stderr", None) or ""))
                return _outcome(
                    COMMIT_REFUSED, False,
                    cause=None if _reds else NON_TEST_REFUSAL_CAUSE,
                    evidence="`git commit` returned rc={} and the pre-commit hook chain named "
                             "{} red test(s){}".format(
                                 result.returncode, len(_reds),
                                 (" -- so the refusal came from a NON-TEST gate, {}. No test was "
                                  "judged, so no blocking list describes this cycle; read the "
                                  "hook output in docs/observability/sim-runner-log.md rather "
                                  "than running the suite".format(
                                      "namely the {}".format(_gate) if _gate else
                                      "and no banner this classifier knows named which one")
                                  ) if not _reds
                                 else " -- recorded in .last_gate_blocking_tests.json against "
                                      "this same commit"))
            return _outcome(NOTHING_TO_COMMIT, False)

        if not _push_due():
            log("Committed locally, push deferred (throttled to every {}min)".format(
                PUSH_THROTTLE_SECONDS // 60
            ))
            return _outcome(COMMITTED_PUSH_THROTTLED, True)

        # SELF-VERIFYING PUSH (2026-07-24, 3.5h origin-freeze incident): a bare
        # `git push` that returns rc=0 WITHOUT advancing origin (a phantom
        # "Everything up-to-date" against a stale remote-tracking ref) must NOT
        # reset the throttle -- that is exactly what froze origin for 3.5h: every
        # cycle recorded a "successful" push that never reached origin, so _push_due
        # stayed False and 15 real commits piled up locally, unseen by the advisor
        # bridge (which depends on this pipeline). Explicit refspec (never rely on
        # bare-push upstream resolution) + ground-truth verification via ls-remote
        # (the real remote, not the local tracking ref). _record_push_time fires
        # ONLY on a VERIFIED advance; a phantom logs LOUD and leaves the throttle
        # untouched so the NEXT cycle retries immediately instead of deferring.
        # H30: git reports auth failure, a rejected non-fast-forward and a dead
        # remote ALL on stderr, and this alert previously carried only `rc=1`
        # for every one of them -- the three have completely different fixes.
        push = subprocess.run(["git", "push", "origin", "HEAD:main"],
                              cwd=str(PROJECT_DIR), timeout=60,
                              stderr=subprocess.PIPE, text=True)
        local_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                                    capture_output=True, text=True, timeout=15).stdout.strip()
        remote_head = ""
        try:
            ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/main"],
                                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30)
            remote_head = ls.stdout.split()[0] if ls.stdout.strip() else ""
        except Exception as exc:
            log("Push verify: ls-remote failed ({}) -- cannot confirm origin advanced".format(exc))
        if _push_reached_origin(push.returncode, remote_head, local_head):
            _record_push_time()
            _record_content_published()
            return _outcome(PUBLISHED, True)
        from background.notify import notify
        notify(
            "[SIM] PUSH DID NOT REACH ORIGIN (rc={}, origin={}, head={}) -- {} -- publish pipeline "
            "commits are stacking LOCALLY and the advisor bridge is blind. NOT recording a push "
            "time; next cycle retries. If this repeats, the remote-tracking ref or auth is the "
            "cause.".format(push.returncode, (remote_head or "?")[:9], (local_head or "?")[:9],
                            failure_detail(getattr(push, "stderr", None))),
            kind="real_alarm",
        )
        _tail = stderr_tail(getattr(push, "stderr", None))
        log("PUSH did NOT advance origin (rc={}, origin={}, head={}) -- throttle left untouched, "
            "will retry next cycle{}".format(
                push.returncode, (remote_head or "?")[:9], (local_head or "?")[:9],
                "\n  git push stderr:\n{}".format(_tail) if _tail
                else "\n  git push stderr: EMPTY (consistent with a phantom up-to-date)"))
        # THE EVIDENCE IS THE REMOTE REF, read by ls-remote above -- not the push's exit status,
        # which returned 0 while origin stood still for 3.5 hours in the 2026-07-24 incident.
        # The commit is on this machine and the hook chain passed to get it there, so this is
        # the one rc=77 cause where the reader must be told NOT to look at the tests at all.
        return _outcome(
            PUSH_DID_NOT_REACH_ORIGIN, False,
            evidence="the commit LANDED locally (HEAD {}) and `git ls-remote` shows "
                     "origin/main still at {} -- the hook chain passed, so no test is "
                     "implicated; the remote ref, not the push's rc={}, is the evidence"
                     .format((local_head or "?")[:9],
                             (remote_head or "unreadable")[:9], push.returncode))


def _push_reached_origin(push_rc: int, remote_head: str, local_head: str) -> bool:
    """A push counts as SUCCESS only if it advanced origin to the local HEAD.

    The 3.5h origin-freeze (2026-07-24): a bare `git push` returned rc=0 while
    origin did NOT advance (phantom "Everything up-to-date"), and the caller
    recorded a push time anyway -- so _push_due() stayed False and every real
    push was deferred behind a success that never happened. This makes the
    success condition GROUND-TRUTH: rc==0 AND the real remote head (from
    ls-remote, not the local tracking ref) equals local HEAD. A phantom rc=0
    with a stale/behind remote head returns False -> no throttle reset -> retry.
    """
    return push_rc == 0 and bool(remote_head) and remote_head == local_head


def _record_content_published() -> None:
    """Stamp the content-publish clock (background/publish_freshness.py). Called from the ONE
    place that has proved origin advanced, alongside `_record_push_time`, and never from a path
    that has not. Non-fatal: freshness bookkeeping must not fail a publish that just succeeded."""
    try:
        from background import publish_freshness
        publish_freshness.record_published()
    except Exception as exc:  # noqa: BLE001
        log("Content-publish stamp skipped (non-fatal): {}".format(exc))


def _push_due() -> bool:
    """True if PUSH_THROTTLE_SECONDS have elapsed since the last recorded
    successful push (or none has ever been recorded)."""
    if not LAST_PUSH_FILE.exists():
        return True
    try:
        last = json.loads(LAST_PUSH_FILE.read_text())["ts"]
    except (json.JSONDecodeError, KeyError, TypeError, OSError):
        return True
    return (datetime.now(timezone.utc).timestamp() - last) >= PUSH_THROTTLE_SECONDS


def _record_push_time() -> None:
    LAST_PUSH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_PUSH_FILE.write_text(json.dumps({"ts": datetime.now(timezone.utc).timestamp()}))


# ── Fault #1 (2026-07-25 overnight publish-freeze): liveness publication must NOT
# be coupled to business-output-change ──────────────────────────────────────────
LIVENESS_SURFACE_FILES = (
    "site/data/tick_heartbeat.json",
    "docs/observability/agent_status.json",
)


def _refresh_published_liveness_on_skip(git_hash: str) -> bool:
    """Publish ONLY the liveness surface on a change-detection SKIP. Returns True
    iff a fresh liveness commit reached origin this call.

    ROOT CAUSE (director-flagged, 2026-07-25): the worker-tick heartbeat
    (site/data/tick_heartbeat.json) is rewritten on disk every 60s, but it only
    reaches origin as a SIDE-EFFECT of a CONTENT publish (commit_and_push_if_
    changed of site/). When the sim output is byte-identical across runs -- the
    common at-rest case, net=£1,521,070 for hours -- the change-detection gate
    SKIPs every cycle, so no content publish happens and the PUBLISHED heartbeat
    freezes for hours while every daemon is healthy. Overnight this froze the live
    site's liveness signal for ~4h though nothing had died. A liveness signal whose
    freshness depends on the business OUTPUT changing is the defect -- fail-silent:
    a heartbeat frozen because healthy-and-unchanged is indistinguishable on origin
    from one frozen because dead.

    Fix: on a SKIP, when a push is DUE (the SAME 30-min throttle as content, so no
    per-cycle commit spam -- the very thing the change-detection gate exists to
    prevent), commit+push ONLY the liveness files via the SAME self-verifying push
    (ground-truth ls-remote, records the throttle only on a verified advance). This
    bounds published-heartbeat staleness to <= PUSH_THROTTLE_SECONDS instead of
    unbounded, with no regen/report/site/test. Commits ONLY the explicit paths
    (never the whole index) so a concurrent writer's staged work is never swept in.

    SEAT GUARD, FIRST ACT -- THE GHOST PUSHER (issue #11, closed here). The
    `__main__` guard at the bottom of this file stops the DAEMON on foreign soil,
    but this function is the only place in the module that commits and pushes
    without going through `__main__` at all: anything that IMPORTS
    process_run_complete and calls `_process()` on a fingerprint-matching marker
    lands here directly, entrypoint guard untouched. That is not hypothetical --
    tests/background/test_process_run_complete.py did exactly that, and every
    unexplained `main` push this week was a test run manufacturing a real
    `chore(liveness)` commit against whatever checkout it happened to be in.

    So the guard moves to the SIDE-EFFECT, not the entrypoint: no matter who
    calls, on what soil, via which import path, the commit+push below is reached
    only from the resident seat. A foreign caller gets one stderr line and False
    (never sys.exit -- this runs inside a live publish path that must survive a
    refusal; the caller treats False exactly as it treats "throttled").

    Deliberately NOT wrapped in a try/except: if the seat guard itself cannot
    load, the ImportError propagates and nothing is committed. R15 FAIL-SILENT --
    an unavailable check is a FAILED check, and the safe direction for a check
    that cannot answer is "do not push".
    """
    try:  # seat guard, FIRST act -- see the docstring (background/_seat.py)
        from background._seat import is_resident_seat
    except ModuleNotFoundError:  # launched as `python3 background/process_run_complete.py`
        from _seat import is_resident_seat  # type: ignore[no-redef]
    if not is_resident_seat():
        print("seat-guard: foreign, liveness publish refused "
              "(process_run_complete._refresh_published_liveness_on_skip)", file=sys.stderr)
        return False
    if not _push_due():
        return False
    files = [str(PROJECT_DIR / rel) for rel in LIVENESS_SURFACE_FILES
             if (PROJECT_DIR / rel).exists()]
    if not files:
        return False
    msg = ("chore(liveness): publish heartbeat while sim output unchanged (git={}) -- "
           "decouples published liveness from content-change (Fault#1 2026-07-25)".format(git_hash))
    # Shared with the provenance banner (_commit_and_push_paths): same narrow-pathspec,
    # never-hold-the-lock-across-commit, self-verifying-push discipline. Extracted rather than
    # cloned when the banner needed the identical shape -- SP3's own instruction.
    if not _commit_and_push_paths(files, msg, label="Liveness heartbeat", git_hash=git_hash):
        return False
    _record_push_time()
    return True


# ── THE ANNOTATION PASS: reds that no longer block still have to be SEEN ─────────────────
#
# Narrowing the blocking scope is only honest if the rest keeps being measured. "Other reds
# become the page annotation" (the ruling) is a promise that the site TELLS you about them --
# and a promise nobody can keep if nothing runs them. So the complement runs here: after the
# publish (never before -- it must not add a second of latency to the thing it is not allowed
# to block), on its own cadence (the suite is slow; the same self-throttle shape as the
# operational-layer signal), writing what it finds into the published banner.
#
# R11, NO ORPHAN TRANSITIONS: this is the RELEASE side of the deselection. A test dropped from
# the blocking set and picked up by nothing would be strictly worse than the wedge -- it would
# be a green-looking site over an unmeasured tree. `feedback_deselecting_a_marker_orphans_the
# _tier` is the same defect one layer down, and it is the reason this function exists at all
# rather than the scoping landing on its own.
REMAINDER_ANNOTATION_INTERVAL_SECONDS = 60 * 60

#: The largest budget an attempt has been observed to be INSUFFICIENT at, from the worker log:
#: 3800, 3800, 3664, 3528 -- four attempts, four timeouts, two of them at
#: `GATE_SUITE_TIMEOUT_SECONDS` exactly. This is a floor read off the record, not a guess at how
#: long the suite takes: what is known is that 3800s is not enough, and 3800s is the most this path
#: is allowed to give. Raise it only by re-measuring, never to make a branch reachable.
REMAINDER_OBSERVED_INSUFFICIENT_SECONDS = 3800
REMAINDER_ANNOTATION_STATE_FILE = (
    PROJECT_DIR / "docs" / "observability" / ".remainder_annotation.json")
# What the page says when the remainder run failed but its transcript could not be read (see
# run_remainder_annotation_step). It is a red, not an absence: the visitor is told the check
# broke rather than being shown a clean count that nothing measured.
REMAINDER_UNREADABLE_MARKER = (
    "UNREADABLE: the remainder run exited rc={rc} but emitted no pytest summary section "
    "(truncated transcript -- an OOM kill has this shape); no red could be named")


def _open_findings_count():
    """How many worker findings are staged and unactioned -- the "N open findings" the ruling
    puts on the page. Counted from the same glob the gate's alarm cites, so the page and the
    alarm cannot disagree about what "open" means."""
    try:
        docs = [p for p in STAGING_DIR.glob(PUBLISH_GATE_FINDING_GLOB) if p.is_file()]
    except OSError:
        return None
    return len(docs)


def _remainder_due(now=None):
    now = time.time() if now is None else float(now)
    try:
        last = json.loads(REMAINDER_ANNOTATION_STATE_FILE.read_text()).get("last_run_ts")
        return now - float(last) >= REMAINDER_ANNOTATION_INTERVAL_SECONDS
    except (OSError, ValueError, TypeError, AttributeError):
        return True


def _remainder_argv():
    from background import publish_scope
    return publish_scope.remainder_pytest_argv(publish_gate_pytest_argv("tests/"))


# What the publish path still needs after the annotation (the agent_status refresh, the
# archive, the return through the caller), and the floor below which a suite cannot finish
# anything worth publishing. Same two knobs as the census, same reasoning.
REMAINDER_PATH_MARGIN_SECONDS = 120
REMAINDER_MIN_SECONDS = 90


def remainder_budget_seconds(now_monotonic=None, started=None):
    """Seconds the non-blocking annotation may run for. Capped at the gate's own bound so this
    step can never become the longest thing in the path, but the BINDING term is what the
    publish path has left -- which is the term it did not have."""
    return _remaining_path_budget_seconds(
        cap=GATE_SUITE_TIMEOUT_SECONDS,
        margin=REMAINDER_PATH_MARGIN_SECONDS,
        minimum=REMAINDER_MIN_SECONDS,
        now_monotonic=now_monotonic, started=started,
    )


def _default_remainder_runner(argv, timeout=None):
    """Run the non-blocking remainder inside what the publish path has LEFT, never inside a
    bound of its own.

    THE DEFECT THIS CLOSES (observed 3x on 2026-08-20, first `TIMED OUT processing ... after
    5400s` at 16:37Z). This step's own docstring says it "must never be able to affect" the
    publish it follows. It could not red the publish -- it could, and did, KILL IT: bounded at
    `GATE_SUITE_TIMEOUT_SECONDS` (4500s) while the whole post-gate allowance is
    `PUBLISH_PATH_ALLOWANCE_SECONDS` (900s), it believed it had budget for 17m32s after its
    caller's deadline had already killed the process. The kill routes to
    `record_publish_gate_failure(kind="deadline_kill")`, so a cycle whose gate PASSED and whose
    commit LANDED was recorded as the episode's next failure, `record_publish_gate_success`
    never ran, and the wedge could not clear. The observer became the outage.

    Raising when the budget is gone is deliberate: `run_remainder_annotation_step` wraps this
    whole call and logs it as a non-fatal skip. Returning a clean CompletedProcess instead
    would put "0 non-blocking reds" on the live page for a suite that never ran, which is the
    fail-silent its caller explicitly guards against three lines further down."""
    budget = remainder_budget_seconds() if timeout is None else float(timeout)
    if budget <= 0:
        raise RuntimeError(
            "no budget left in the publish path's own deadline ({}s) for the remainder "
            "annotation -- skipping it rather than being killed mid-run and recorded as a "
            "gate failure against a publish that already landed".format(
                PUBLISH_PATH_TIMEOUT_SECONDS))
    env = dict(os.environ)
    env["SIM_FAST_MODE"] = "1"
    return subprocess.run(argv, cwd=str(PROJECT_DIR), env=env,
                          timeout=budget,
                          capture_output=True, text=True, errors="replace")


def _annotation_measured_on(git_hash):
    """WHICH TREE the remainder suite just counted reds on. The commit, AND whether it was alone.

    `_default_remainder_runner` runs pytest with `cwd=PROJECT_DIR` — the SHARED WORKING TREE,
    which on this machine carries several lanes' uncommitted work at any moment. So `git_hash`
    names the commit being PUBLISHED, and the count was taken on that commit plus whatever else
    happened to be lying in the tree. Those are two different objects and the banner used to
    publish the number as though they were one.

    THE DIRTY ANSWER IS THE HONEST ONE and it is not a degraded case: it is what actually happens
    on nearly every cycle here. Reporting `TREE_COMMIT` unconditionally, or defaulting to it when
    the `git status` probe fails, would be the misattribution `MEASURED_ON_FIELDS` exists to stop
    — so an unreadable probe reads as WORKING TREE, the answer that claims less.
    """
    _prov = publish_provenance

    tree_state = _prov.TREE_WORKING
    try:
        dirt = subprocess.run(["git", "status", "--porcelain"], cwd=str(PROJECT_DIR),
                              capture_output=True, text=True, timeout=60)
        if dirt.returncode == 0 and not dirt.stdout.strip():
            tree_state = _prov.TREE_COMMIT
    except Exception:  # noqa: BLE001 -- an observer that can red its subject is a defect
        pass
    return {"git_commit": git_hash, "tree_state": tree_state}


def _stamp_remainder_attempt(git_hash, reason: str) -> None:
    """Record that an attempt HAPPENED, without recording a result it did not produce.

    One writer for both non-completing paths -- the pre-flight skip and the timeout -- because two
    copies of "stamp the clock but never the reds" is the duplication that lets one of them drift
    into publishing an all-clear for a suite that never ran."""
    try:
        REMAINDER_ANNOTATION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        REMAINDER_ANNOTATION_STATE_FILE.write_text(json.dumps(
            {"last_run_ts": time.time(), "rc": None, "git_hash": git_hash,
             "outcome": "unavailable", "reason": str(reason)[:400]}, indent=2) + "\n")
    except Exception:  # noqa: BLE001 -- the observer still may not red its subject
        pass


def run_remainder_annotation_step(git_hash, *, force=False, runner=None):
    """Run the NON-BLOCKING remainder and record its reds into the published banner.

    Returns the annotation state written, or None if not due / unavailable. Wrapped whole:
    this observes the publish it follows and must never be able to affect it.
    """
    try:
        _prov = publish_provenance
        findings = _open_findings_count()
        if not (force or _remainder_due()):
            # Findings are cheap to count, so refresh that half every cycle even when the
            # suite is throttled -- a stale finding count on a live page is a small lie that
            # costs nothing to avoid.
            return _prov.record_annotation(open_findings=findings) if findings is not None else None

        # A STEP THAT CANNOT FINISH AT ANY BUDGET IT CAN BE GIVEN MUST NOT BE ATTEMPTED.
        #
        # Measured 2026-09-04, from this module's own constants and the worker log, not inferred:
        # `remainder_budget_seconds` is capped at `GATE_SUITE_TIMEOUT_SECONDS` = 3800, and the four
        # recorded attempts timed out at 3800, 3800, 3664 and 3528 -- TWO OF THEM AT THE CAP
        # EXACTLY. The remainder is the whole suite (`pytest tests/`), so it needs more than the
        # maximum this path is allowed to give it, and the cap may not grow: the director ruled on
        # 2026-08-21 that no gate budget grows here.
        #
        # So it is not occasionally unlucky, it is STRUCTURALLY incapable of completing in this
        # path, and every attempt spends ~an hour of held publish lock to produce nothing. Skipping
        # costs nothing that was ever delivered -- the annotation has not completed once in the
        # log's history -- and the page already carries the reds' own `checked_at`, so the staleness
        # it leaves is visible rather than silent.
        #
        # KEYED TO THE COMPARISON, NOT TO TODAY'S ANSWER. The day the remainder is given a budget
        # larger than an attempt has been observed to need -- a faster suite, a narrower selection,
        # or its own timer outside this path -- it runs again with no edit here. AND THE RUN BRANCH
        # DOES NOT FIRE IN PRODUCTION TODAY, which is said plainly rather than left for a reader to
        # discover: on this machine the budget is always exactly the cap. The reachability control
        # is `test_the_remainder_still_runs_when_it_is_given_a_budget_it_can_finish_in`.
        # ONLY FOR THE DEFAULT RUNNER, and that is the guard's actual subject rather than a test
        # convenience: the cost being avoided is `_default_remainder_runner` spawning a real
        # whole-suite pytest inside the publish path's own budget. A caller that SUPPLIES a runner
        # is supplying the work and spends none of that budget, so the pre-flight does not apply to
        # it. In production `runner` is always None, so the guard always applies there.
        budget = remainder_budget_seconds()
        if runner is None and budget <= REMAINDER_OBSERVED_INSUFFICIENT_SECONDS:
            _stamp_remainder_attempt(
                git_hash,
                "skipped before starting: {:.0f}s of budget against attempts that have needed more "
                "than {:.0f}s (4 of 4 timed out, two at the cap). Running it here spends the "
                "publish lock to produce nothing.".format(
                    budget, REMAINDER_OBSERVED_INSUFFICIENT_SECONDS))
            log("Remainder annotation NOT ATTEMPTED: {:.0f}s budget cannot finish a suite that has "
                "needed more than {:.0f}s in every recorded attempt. Throttle clock stamped.".format(
                    budget, REMAINDER_OBSERVED_INSUFFICIENT_SECONDS))
            return None

        result = (runner or _default_remainder_runner)(_remainder_argv())
        reds = _parse_failed_node_ids(getattr(result, "stdout", "") or "")
        # A NON-ZERO RC WITH NOTHING TO SHOW IS "UNREADABLE", NEVER "CLEAN" (2026-08-12).
        #
        # `_parse_failed_node_ids` answers "" for a transcript carrying no summary section of
        # its own, and that is the right answer for the BLOCKING gate: its consumer renders
        # UNRECORDED. This consumer is different -- an empty list here reaches the live page as
        # "0 non-blocking reds", i.e. an all-clear, next to a run that plainly failed. A
        # truncated transcript is the known shape of an OOM kill on this box, so the fail-silent
        # is reachable, not theoretical.
        if result.returncode != 0 and not reds:
            reds = [REMAINDER_UNREADABLE_MARKER.format(rc=result.returncode)]
        REMAINDER_ANNOTATION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        REMAINDER_ANNOTATION_STATE_FILE.write_text(json.dumps(
            {"last_run_ts": time.time(), "rc": result.returncode, "reds": reds[:32],
             "git_hash": git_hash}, indent=2) + "\n")
        state = _prov.record_annotation(open_findings=findings, nonblocking_reds=reds,
                                        measured_on=_annotation_measured_on(git_hash))
        log("Remainder annotation: rc={}, {} non-blocking red(s), {} open finding(s) -- "
            "published as page annotation, NOT as a block.".format(
                result.returncode, len(reds), findings))
        return state
    except Exception as exc:  # noqa: BLE001 -- an observer that can red its subject is a defect
        # THE CHEAP HALF IS REFRESHED ON THIS PATH TOO, AND UNTIL 2026-09-03 IT WAS NOT.
        #
        # The not-due branch above already carries the argument, in its own words: "Findings are
        # cheap to count, so refresh that half every cycle even when the suite is throttled -- a
        # stale finding count on a live page is a small lie that costs nothing to avoid." That
        # branch fires when the hourly throttle says wait. THIS branch fires when the suite runs
        # and dies, and it recorded nothing at all — so the principle was written down, implemented
        # on one of the two branches, and missing from the one that actually fires.
        #
        # It fires ALWAYS. `_default_remainder_runner` is given whatever the publish path has left,
        # the suite does not finish in it, and the timeout lands here. 23 times in the two days to
        # 2026-09-03 and on every cycle that day; the last success was 2026-09-01 05:53Z.
        #
        # MEASURED, which is why this is a repair and not a tidy-up: the live banner said
        # "Published with 55 open findings" while the true count was 16. Frozen at 06:22Z on
        # 2026-09-01, published continuously for two days, 3.4x the truth. `site/data/
        # publish_provenance.json` was being rewritten every cycle — 17:54 mtime on the day this
        # was found — so nothing looked stale; it was the ANNOTATION BLOCK inside a fresh file that
        # had stopped moving.
        #
        # Only the findings half is refreshed. The red count is a property of a TREE and this path
        # has no tree to name it on, so re-publishing it would be inventing a measurement — the
        # exact refusal `record_annotation` enforces two modules away. The reds keep their own
        # `checked_at`, which now reaches the reader (`site/assets/freshness-banner.js`) instead of
        # sitting in the feed where it has been all along.
        try:
            findings = _open_findings_count()
            if findings is not None:
                publish_provenance.record_annotation(open_findings=findings)
        except Exception:  # noqa: BLE001 -- the observer still may not red its subject
            pass
        # STAMP THE ATTEMPT, NOT THE SUCCESS. The throttle's clock was written only on the
        # success path, so a step that ALWAYS fails was never throttled: it came due again on the
        # very next publish cycle, spent the whole remaining budget, timed out, and left the clock
        # where it was. Measured 2026-09-04 -- last stamp 76.4 hours old, four attempts in the log
        # window and four timeouts, so for three days every publish cycle paid an hour of held run
        # lock for nothing. An interval bounds how often a step is ATTEMPTED, not how often it
        # succeeds; keying it to success makes a permanently-failing step a permanent tax and hides
        # it behind an honest, isolated "skipped (non-fatal)" every cycle.
        #
        # NO `reds` IS WRITTEN. A run that produced no transcript measured no tree, and an empty
        # list reaches the page as "0 non-blocking reds" beside a suite that never ran.
        _stamp_remainder_attempt(git_hash, exc)
        log("Remainder annotation skipped (non-fatal): {} -- throttle clock stamped anyway, so "
            "this cannot run again for {:.0f} min.".format(
                exc, REMAINDER_ANNOTATION_INTERVAL_SECONDS / 60))
        return None


def _publish_provenance_banner(git_hash, *, reason=None):
    """Publish the staleness BANNER while the numbers stay put (ruling property 3).

    THE ONE THING THAT MUST NOT FREEZE. On a red scoped gate the publisher returns before
    `git_commit_push`, so the live site keeps serving the last verified snapshot -- correct,
    and until now completely silent about it. This pushes `site/data/publish_provenance.json`
    ALONE, so the visitor is told "verification paused since T; showing run R" without a
    single unverified figure reaching the surface.

    WHY THIS CANNOT SMUGGLE CONTENT OUT. The pathspec is one file, and the freshness fields
    inside it are unreachable from here: `record_paused` cannot write `showing_run` or
    `last_verified` (background/publish_provenance.py, mutation-proven). So the worst this
    path can do is publish a MORE pessimistic statement about the same numbers.

    Returns True iff a banner commit reached origin this call. Never raises into the publish
    path: a banner that cannot be published must not also break the return code that says the
    gate was red.
    """
    try:  # seat guard, FIRST act -- same reasoning as the liveness refresh above
        from background._seat import is_resident_seat
    except ModuleNotFoundError:  # launched as `python3 background/process_run_complete.py`
        from _seat import is_resident_seat  # type: ignore[no-redef]
    if not is_resident_seat():
        print("seat-guard: foreign, provenance banner publish refused "
              "(process_run_complete._publish_provenance_banner)", file=sys.stderr)
        return False
    try:
        _prov = publish_provenance
        state = _prov.record_paused(reason=reason)
        log("Provenance banner: {}".format(_prov.banner_line(state)))
        target = str(_prov.PROVENANCE_FILE)
    except Exception as exc:  # noqa: BLE001 -- see docstring
        log("Provenance banner write failed (non-fatal): {}".format(exc))
        return False

    msg = ("chore(provenance): verification paused banner (git={}) -- the site keeps serving "
           "the last VERIFIED run and now says so; no unverified figure published "
           "(DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10 property 3)".format(git_hash))
    try:
        return _commit_and_push_paths([target], msg, label="Provenance banner", git_hash=git_hash)
    except Exception as exc:  # noqa: BLE001 -- see docstring
        log("Provenance banner publish raised (non-fatal): {}".format(exc))
        return False


def _provenance_is_publishable(paths, *, label="publish") -> bool:
    """True unless `paths` includes the provenance file and its contents must not be published.

    Returns True when the provenance is not in this commit at all -- this guards one file, and
    is not a general commit gate. Every refusal is LOGGED with the violations, because the
    defect it closes published in silence and a quiet refusal would only move the silence.
    """
    prov_path = PROJECT_DIR / "site" / "data" / "publish_provenance.json"
    dash_path = PROJECT_DIR / "site" / "data" / "dashboard.json"
    try:
        resolved = {Path(p).resolve() for p in paths}
        in_commit = {prov_path.resolve(), dash_path.resolve()} & resolved
        if not in_commit:
            return True
    except OSError:
        return True
    try:
        _prov = publish_provenance
        violations = []
        if prov_path.resolve() in in_commit:
            violations += _prov.publishable_violations(
                _prov.read(prov_path), repo_root=PROJECT_DIR)
        # The same identity claim, in the file that carries every published FIGURE. A dashboard
        # stamped with a run that does not exist is a page of numbers attributed to nothing.
        if dash_path.resolve() in in_commit and dash_path.exists():
            meta = json.loads(dash_path.read_text()).get("meta")
            if meta is not None:
                violations += _prov.dashboard_meta_violations(meta, repo_root=PROJECT_DIR)
    except Exception as exc:  # noqa: BLE001 -- an unavailable checker is a FAILED check
        log("{} REFUSED: the provenance check could not run ({}: {}) -- an unavailable check "
            "is a failed check, so nothing is published this cycle.".format(
                label, type(exc).__name__, exc))
        return False
    if violations:
        log("{} REFUSED -- REFUSING TO PUBLISH A FALSE PROVENANCE:\n  {}\n  Nothing was "
            "committed. The site keeps serving its last honest state. This is the fixture-value "
            "class (WORKER_FINDING_TEST_FIXTURE_VALUES_REACHED_THE_LIVE_PUBLISH_STATE_"
            "2026-08-11); the values above name the cycle that produced it.".format(
                label, "\n  ".join(violations)))
        return False
    return True


def _commit_and_push_paths(paths, msg, *, label, git_hash="unknown"):
    """Commit exactly `paths` and self-verify the push against origin. Returns True iff origin
    ADVANCED to this HEAD.

    THE SHARED PRIMITIVE, extracted rather than cloned (SP3 size+clone ratchet: "extract a
    shared primitive rather than obfuscating the duplicate"). Two callers need the same narrow
    publish -- the liveness heartbeat refresh on a change-detection SKIP, and the provenance
    banner on a red gate -- and both for the same reason: a surface whose whole job is to say
    the system is alive/behind must not be published as a side-effect of publishing content,
    because the case it exists for is exactly the case where content does not publish.

    Three properties every caller inherits, none of them optional:
      * NARROW PATHSPEC -- commits ONLY these paths, never the whole index, so a concurrent
        writer's staged work can never be swept into a heartbeat or a banner commit.
      * NEVER HOLDS THE LOCK ACROSS THE COMMIT -- the pre-commit gate takes the real tree lock
        itself, so committing under it deadlocks (2026-08-03, 8 TreeLockTimeout). `git add`
        under the lock; commit unlocked, by pathspec.
      * SELF-VERIFYING PUSH -- ground-truth `ls-remote`, never the push's own rc. A phantom
        "up to date" must not be recorded as a publish.
    """
    # PUBLISHING A FALSE PROVENANCE IS IMPOSSIBLE FROM HERE (2026-08-11, director P1).
    #
    # This is the ONE chokepoint every provenance commit passes through -- the red-cycle banner
    # and the green-cycle content commit both arrive here -- so the check lives here rather than
    # at each caller. A guard placed per-caller protects the callers somebody thought of; this
    # one protects the FILE, which is the thing with a public consequence.
    #
    # It asserts on the VALUE, not the writer, because the writer is unknown: a test fixture
    # literal ("run_verified.json") was rendered into a banner and pushed to origin at 08:58Z
    # and the mechanism is still NOT ESTABLISHED. Fail-closed -- if git cannot confirm the
    # commit is real, we refuse and the site stays honestly paused rather than publishing a
    # claim we cannot stand behind.
    if not _provenance_is_publishable(paths, label=label):
        return False
    # THE SAME REFUSAL AT THE OTHER COMMIT SITE. The liveness heartbeat and the provenance banner
    # deepen a fork exactly as a content commit does, and a guard placed only where the incident
    # was observed is what makes a class recur -- the note on `_git_add_or_refuse` above is the
    # same lesson, learned in this function. On a behind-origin tree the banner cannot reach
    # origin either, so refusing costs nothing that was going to be published.
    _behind = _divergence_refusal()
    if _behind is not None:
        log("{} commit REFUSED before staging: {}.".format(label, _behind))
        return False
    with tree_lock():
        # THE SAME UNCHECKED ADD, at the site the finding did not name (2026-08-25). The
        # banner/heartbeat path stages exactly as blindly as the publish path did, so a lock
        # here produces the same misleading pathspec error one function down. Fixing only the
        # caught instance is what makes a class recur -- see `_git_add_or_refuse`.
        if not _git_add_or_refuse(list(paths), timeout=30, label=label):
            return False
    # The SAME budget the content commit gets, from the SAME constant -- see
    # GIT_COMMIT_HOOK_TIMEOUT_SECONDS for why a liveness path with its own, larger number is the
    # mechanism that hides a content freeze rather than a harmless duplication.
    result = subprocess.run(["git", "commit", "-m", msg, "--"] + list(paths),
                            cwd=str(PROJECT_DIR), timeout=GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
                            env=_commit_hook_env(), capture_output=True, text=True)
    if result.returncode != 0:
        _tail = (stderr_tail(getattr(result, "stderr", None))
                 or stderr_tail(getattr(result, "stdout", None)))
        # Byte-identical to the committed copy is the EXPECTED steady state (a banner whose
        # paused_since does not re-stamp; a heartbeat that has not ticked) and stays quiet.
        # Anything else -- a hook refusal, a lock, a broken index -- says what it was, because
        # a banner silently refused by a gate is the failure this whole build exists to end.
        if _tail and "nothing to commit" not in _tail.lower():
            log("{} commit FAILED (rc={}):\n{}".format(label, result.returncode, _tail))
            # R10, the class and not the instance: this is the SAME hook chain refusing the SAME
            # tree, and a banner/heartbeat refusal discards the node ids exactly as the content
            # path did. Guarded by the same "not a clean no-op" test the log line uses.
            _record_commit_refusal_reds(getattr(result, "stdout", None),
                                        getattr(result, "stderr", None), git_hash)
        return False
    push = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=str(PROJECT_DIR),
                          timeout=60, stderr=subprocess.PIPE, text=True)
    local_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                                capture_output=True, text=True, timeout=15).stdout.strip()
    remote_head = ""
    try:
        ls = subprocess.run(["git", "ls-remote", "origin", "refs/heads/main"],
                            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30)
        remote_head = ls.stdout.split()[0] if ls.stdout.strip() else ""
    except Exception as exc:  # noqa: BLE001 -- an unverifiable push reads as NOT pushed
        log("{} push verify: ls-remote failed ({})".format(label, exc))
    if _push_reached_origin(push.returncode, remote_head, local_head):
        log("{} published to origin.".format(label))
        return True
    log("{} push did NOT advance origin (rc={}, origin={}, head={}) -- retry next cycle.".format(
        label, push.returncode, (remote_head or '?')[:9], (local_head or '?')[:9]))
    return False


def _run_history_max_net():
    hp = PROJECT_DIR / "docs" / "observability" / "run_history.json"
    if not hp.exists():
        return 0.0
    try:
        import json as _j
        history = _j.loads(hp.read_text())
        return max((h.get("net_margin_gbp", 0) for h in history), default=0.0)
    except Exception:
        return 0.0


# ── H15: publish-gate failure alerting (silent-wedge detector) ───────────────

def _classify_gate_failure(rc):
    """Cheap OOM-vs-regression classification from a processor return code.

    A negative code == the child was killed by signal -rc (subprocess
    convention); -9 = SIGKILL, overwhelmingly the OOM-killer / a resource
    limit rather than a code regression. A positive non-zero code is a real
    processing/test failure ('Tests FAILED', report regen failed, ...)."""
    if rc is None:
        return "unknown"
    try:
        rc = int(rc)
    except (TypeError, ValueError):
        return "unknown"
    if rc < 0:
        return "resource_kill" if rc == -9 else "signal_kill"
    if rc == 0:
        return "pass"
    return "test_regression"


#: THE KINDS FOR WHICH NO TEST WAS JUDGED. Each of these means the suite never returned a
#: verdict -- it timed out, or it was never reached at all -- so the alarm must not attach
#: `blocking`/`suspects` to it. Those are derived from whatever an EARLIER cycle left behind,
#: which on these kinds is evidence about a different cycle: naming nobody beats naming the
#: innocent. This is a SET rather than three `kind != "..."` comparisons because it was two
#: separate comparisons for nine days and the second carve-out (2026-08-30) had to find both.
#: `tests/background/test_publish_gate_alert.py` holds it to the class.
UNJUDGED_GATE_KINDS = frozenset({"gate_timeout", "tree_lock_unavailable"})


def _gate_failure_label(kind):
    return {
        "resource_kill": "resource kill (SIGKILL/OOM -- almost certainly memory, NOT a code regression)",
        "signal_kill": "killed by a signal (a resource/environment problem, not a normal test failure)",
        "deadline_kill": ("killed by the CALLER's deadline before the gate returned a verdict -- "
                          "NOT a test failure, and the tests it was running are unjudged"),
        "gate_timeout": ("the publisher's OWN gate clock (GATE_SUITE_TIMEOUT_SECONDS) expired "
                         "before the suite returned a verdict -- NOT a test failure, and the "
                         "tests it was running are unjudged. Nothing here says a test is red; "
                         "read the gate's wall time against its bound, not the test list"),
        "tree_lock_unavailable": ("another writer held the tree lock for the whole timeout, so "
                                  "the publisher never reached its commit -- NOT a test failure "
                                  "and NOT a hook refusal: nothing was judged. Contention, not "
                                  "regression; the next cycle retries"),
        "test_regression": "test failure or processing error (rc>0 -- a real regression is possible)",
        "commit_did_not_land": ("the publish COMMIT did not land -- the publisher's OWN scoped "
                                "suite was GREEN, so this is NOT a publish-path regression: the "
                                "pre-commit hook chain refused the commit (most often another "
                                "lane's red on the shared tree), outran the hook deadline, or "
                                "the push never reached origin. Read the 'git/hook output' tail "
                                "in the log -- it names the refusing gate"),
        "unknown": "unknown cause (return code unavailable)",
    }.get(kind, kind)


def _read_publish_gate_state():
    """Load the wedge-state file. FAIL-CLOSED (R15 fail-silent doctrine): an
    unreadable/corrupt state is itself a failed check -- signalled via
    state_unavailable=True so the current failure escalates immediately rather
    than being lost to a silent reset that would suppress the alarm."""
    if not PUBLISH_GATE_STATE_FILE.exists():
        return {"failures": [], "alerted_at": None, "state_unavailable": False}
    try:
        st = json.loads(PUBLISH_GATE_STATE_FILE.read_text())
        if not isinstance(st, dict):
            raise ValueError("gate state is not an object")
        st.setdefault("failures", [])
        st.setdefault("alerted_at", None)
        # wedge_since (2026-07-24, WEDGE3_AND_RUNG1_MECHANISE): the PERSISTENT start-of-streak
        # timestamp -- NOT trimmed to the 1h window like `failures`, so it is the only field that
        # can measure a wedge older than the window. Set on the first failure of a streak, preserved
        # across every later failure, cleared to None on the next clean publish. The supervisor's
        # RUNG-1 unwedge draw (background/supervisor.py::_publish_gate_wedge_active) reads it to
        # decide ">60 min". Without it the ">60 min" rule was un-mechanisable (window trimming caps
        # the oldest surviving `failures`/`alerted_at` timestamp below 60 min for a live wedge) --
        # the exact reason the prose rule was consumed-not-absorbed twice.
        st.setdefault("wedge_since", None)
        # EPISODE MEMORY: the whole-streak failure count. `failures` above is trimmed to the
        # 1h window, so it can never describe an episode longer than the window -- that is
        # precisely how seven hours read as ten fresh hours. Defaults to the in-window count
        # for a state file written before this field existed (never to 0, which would
        # UNDER-report a live episode -- the fail-open direction).
        st.setdefault("episode_failures", len(st.get("failures") or []))
        st.setdefault("cited_findings", [])
        # The blocking node IDs of the latest red (see GATE_BLOCKING_TESTS_FILE). Empty means
        # "not known", never "nothing blocked" -- the reader must not treat it as the latter.
        st.setdefault("blocking_tests", [])
        # The blame trail derived from those node ids (H42). {} means "no blocking test was
        # recorded", never "the trail is clean".
        st.setdefault("suspects", {})
        # HOW MUCH OF THE RED SET the blocking_tests above are (2026-08-14 red census). A state
        # file written before this field existed knew only the fail-fast red, and that is exactly
        # what the default says -- never `complete`, which would claim a depth nobody measured.
        st.setdefault("red_census", CENSUS_FAIL_FAST_ONLY)
        st.setdefault("total_red", len(st.get("blocking_tests") or []))
        st["state_unavailable"] = False
        return st
    except (json.JSONDecodeError, OSError, ValueError):
        return {"failures": [], "alerted_at": None, "wedge_since": None,
                "episode_failures": 0, "cited_findings": [], "blocking_tests": [],
                "suspects": {}, "red_census": CENSUS_FAIL_FAST_ONLY, "total_red": 0,
                "state_unavailable": True}


PUBLISH_GATE_SINCE_FIELDS = ("wedge_since",)
PUBLISH_GATE_STREAK_FIELDS = ("episode_failures",)


def _write_publish_gate_state(state, *, episode_closed=False):
    """Persist the wedge state, with the PW2 guard on the episode-scoped fields.

    `episode_closed` is the CALLER'S EVIDENCED CLAIM that the wedge episode really ended. Every
    failure path passes False, so a failure can no longer move `wedge_since` forward or drop
    `episode_failures` -- the 2026-08-09 defect, where a 10h26m outage paged as a fresh 14
    minutes because each round of failures rewrote the clock the alarm was about to read.

    This is the CLASS guard (`background/episode_monotonic.py`), not an instance patch on this
    file -- R10, and the steer said so explicitly. The census
    (`background/self_clearing_alarm_census.py`) is what says which other state files need it."""
    out = {"failures": state.get("failures", []), "alerted_at": state.get("alerted_at"),
           "wedge_since": state.get("wedge_since"),
           "episode_failures": state.get("episode_failures", 0),
           "cited_findings": state.get("cited_findings", []),
           "blocking_tests": state.get("blocking_tests", []),
           "suspects": state.get("suspects", {}),
           "red_census": state.get("red_census", CENSUS_FAIL_FAST_ONLY),
           "total_red": state.get("total_red", 0)}
    out = guard_episode(_read_publish_gate_state() if PUBLISH_GATE_STATE_FILE.exists() else None,
                        out,
                        since_fields=PUBLISH_GATE_SINCE_FIELDS,
                        streak_fields=PUBLISH_GATE_STREAK_FIELDS,
                        episode_closed=episode_closed)
    PUBLISH_GATE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLISH_GATE_STATE_FILE.write_text(json.dumps(out, sort_keys=True))


def pending_run_complete_markers(staging_dir=None):
    """How many run_complete markers are queued unpublished RIGHT NOW.

    Read off the real staging directory, never off the gate's own state -- the count is
    the wedge's CONSEQUENCE measured independently of its cause (R15 anti-tautology), so a
    gate-state file that lies cannot make the backlog look small. An unreadable staging
    directory returns None ("unknown"), never 0: zero and unknown are opposite facts."""
    sd = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    try:
        return len(list(sd.glob("run_complete_*.md")))
    except OSError:
        return None


# ── THE SUSPECTS COME FROM THE RED, NOT FROM THE INBOX ────────────────────────────────
# (2026-08-10, atom H42_wedge_suspect_list_rederived_from_the_red, ratified as a mint by
#  DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION_2026-08-10.)
#
# WHAT WAS HERE. `filed_findings()`: the eight most recently modified WORKER_FINDING_*.md in
# docs/staging/, printed under the wedge alarm's blocking test as "also filed and unactioned".
# Ranked by mtime; linked to the failure by NOTHING. Its own clause had to confess the
# measurement -- 0/8 named the cause in each of FIVE consecutive episodes (WORKER_REPORT_
# {PUBLISH,FIFTH,SIXTH,THIRTEENTH}_WEDGE_SUSPECT_DISPOSITION_*) -- and the director priced it
# at twenty minutes of every responder's time per episode. The tell was that the list was
# near-identical every time while the cause differed every time: a set that does not move when
# the thing it describes moves is not measuring that thing.
#
# WHAT REPLACES IT. A blame trail rooted in the ONE fact the alarm already knows for certain:
# the blocking node id from `.last_gate_blocking_tests.json`. Its test FILE, the first-party
# modules that file IMPORTS, and the recent commits touching either. A staged finding is cited
# only if its text NAMES something on that trail -- a link, not a coincidence of filing date.
#
# THE DISCIPLINE IT INHERITS. `_blocking_clause` never degrades to a guess, and neither does
# this: no recorded blocking test => NO suspect block at all. Unreadable, malformed and STALE
# gate state all read as "unrecorded" (see `last_blocking_tests`), never as "no suspects" --
# that distinction is the FAIL-SILENT killer pattern and it is what the recency list violated.
#
# AND IT IS MEASURED (R12: the hit rate is a DIAGNOSTIC, never a target; no finding may be
# archived to move it). Every closed episode appends a hit/miss to WEDGE_SUSPECT_HIT_RATE_FILE
# and the alarm carries the running rate, so a re-derivation that is ALSO useless is visible
# rather than assumed better -- the failure mode of the thing it replaces.
WEDGE_SUSPECT_BLAME_DAYS = 7          # a wedge's cause older than a week is not a recent change
WEDGE_MAX_SUSPECT_MODULES = 8         # bounded: an alarm is a page, not an import graph
WEDGE_MAX_SUSPECT_COMMITS = 6
WEDGE_GIT_TIMEOUT_SECONDS = 30
# Top-level packages that are OURS. An import outside these (pytest, json, yaml) cannot be the
# regression the gate is reporting, and blaming a stdlib module is how a suspect list becomes
# noise again.
FIRST_PARTY_PACKAGES = frozenset({
    "background", "company", "interface", "saas", "sim", "simulation", "site", "tools",
})
WEDGE_SUSPECT_HIT_RATE_FILE = PROJECT_DIR / "docs" / "observability" / ".wedge_suspect_hit_rate.json"
WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES = 20


def blocking_test_files(node_ids):
    """The repo-relative test FILES named by a gate's blocking node ids.

    Accepts pytest's short-summary form as recorded (`FAILED path::test`, `ERROR path - msg`)
    and the bare node id. Anything that does not resolve to a `.py` path is dropped rather
    than guessed at."""
    files = []
    for raw in node_ids or []:
        s = str(raw).strip()
        for prefix in ("FAILED ", "ERROR "):
            if s.startswith(prefix):
                s = s[len(prefix):].strip()
        s = s.split("::")[0].split(" ")[0].strip()
        if s.endswith(".py") and s not in files:
            files.append(s)
    return files


def first_party_imports(test_file, project_dir=None):
    """The repo module FILES a test file imports — the blame surface of its red.

    Parsed from the source (ast), never imported: the module that wedged the gate may be the
    one that cannot be imported. Unreadable or unparseable reads as an EMPTY trail, which the
    caller renders as "none resolvable" — an honest absence, not a fabricated suspect."""
    root = Path(project_dir) if project_dir is not None else PROJECT_DIR
    try:
        tree = ast.parse((root / test_file).read_text(errors="replace"), filename=str(test_file))
    except (OSError, SyntaxError, ValueError):
        return []
    mods = []

    def _add(dotted):
        parts = [p for p in str(dotted or "").split(".") if p]
        if not parts or parts[0] not in FIRST_PARTY_PACKAGES:
            return
        # Longest resolvable prefix wins: `background.a.b` resolves to background/a/b.py if it
        # exists, else background/a/b/__init__.py, else back off to background/a.py.
        for i in range(len(parts), 0, -1):
            stem = Path(*parts[:i])
            for rel in (stem.with_suffix(".py"), stem / "__init__.py"):
                if (root / rel).is_file():
                    name = rel.as_posix()
                    if name not in mods:
                        mods.append(name)
                    return

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                _add(alias.name)
        elif isinstance(node, ast.ImportFrom) and not node.level:
            base = node.module or ""
            _add(base)
            for alias in node.names:
                _add("{}.{}".format(base, alias.name) if base else alias.name)
    return mods[:WEDGE_MAX_SUSPECT_MODULES]


def blame_commits(paths, days=WEDGE_SUSPECT_BLAME_DAYS, limit=WEDGE_MAX_SUSPECT_COMMITS,
                  project_dir=None):
    """Recent commits touching any of `paths`. Never raises; an unavailable git reads EMPTY,
    which the caller renders as "no commit touched these", so a git failure cannot invent a
    suspect either."""
    if not paths:
        return []
    root = Path(project_dir) if project_dir is not None else PROJECT_DIR
    try:
        res = subprocess.run(
            ["git", "log", "--no-merges", "--since={} days ago".format(days),
             "--pretty=format:%h %s", "-n", str(limit), "--"] + [str(p) for p in paths],
            cwd=str(root), capture_output=True, text=True, timeout=WEDGE_GIT_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError):
        return []
    if res.returncode != 0:
        return []
    return [ln.strip() for ln in (res.stdout or "").splitlines() if ln.strip()][:limit]


def wedge_suspects(blocking, project_dir=None):
    """The suspect set DERIVED FROM THE RED: {} when the blocking test is unrecorded.

    An empty dict is the whole point — the caller must print NO suspect block rather than
    fall back to whatever happens to be lying in staging."""
    files = blocking_test_files(blocking)
    if not files:
        return {}
    modules = []
    for f in files:
        for m in first_party_imports(f, project_dir=project_dir):
            if m not in modules:
                modules.append(m)
    modules = modules[:WEDGE_MAX_SUSPECT_MODULES]
    return {"test_files": files, "modules": modules,
            "commits": blame_commits(files + modules, project_dir=project_dir)}


def _exonerated_for(text, test_files, repo_root):
    """True when this document's PARSED HEADER declares it not a suspect for every blocking
    test of the red in hand.

    The link below is lexical, and an accusation and a refutation are the same tokens — so a
    document that answers the draw correctly (which it can only do by naming the cause) scores
    as a BETTER suspect than one that says nothing. `**Not-a-suspect-for:**` is the finding's
    own answer, made readable by the instrument it answers. Fail-closed and never raises: an
    absent, malformed, unverifiable or out-of-scope claim leaves the document CITED."""
    if not test_files:
        return False
    try:
        exoneration = finding_severity.parse_exoneration(text, repo_root)
    except Exception:  # an unavailable check is a FAILED check: keep the suspect
        return False
    return bool(exoneration and exoneration.covers(test_files))


def linked_findings(suspects, staging_dir=None, limit=PUBLISH_GATE_MAX_CITED_FINDINGS,
                    repo_root=None):
    """Staged findings whose TEXT names something on the red's blame trail.

    The link is the point: a finding filed five minutes ago about an unrelated subsystem is
    not evidence, and citing it is the defect this replaces. Ranked by how much of the trail
    a finding names (ties by filename, so the list is deterministic), bounded, and EMPTY when
    the trail is empty. Only the scanned staging ROOT counts — a finding in done/ has been
    dispositioned. Never raises.

    A document whose header EXONERATES it for this red's blocking tests is DROPPED, not
    down-ranked (see `_exonerated_for`): down-ranking would still surface it once the eight
    slots were not full, which is the state every real wedge has been in."""
    trail = list(suspects.get("test_files") or []) + list(suspects.get("modules") or []) if suspects else []
    if not trail:
        return []
    needles = set()
    for t in trail:
        needles.add(str(t))
        needles.add(Path(str(t)).name)
        needles.add(Path(str(t)).stem)
    sd = Path(staging_dir) if staging_dir is not None else STAGING_DIR
    try:
        docs = [p for p in sd.glob(PUBLISH_GATE_FINDING_GLOB) if p.is_file()]
    except OSError:
        return []
    test_files = [str(t) for t in (suspects.get("test_files") or [])] if suspects else []
    root = repo_root if repo_root is not None else PROJECT_DIR
    scored = []
    for p in docs:
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        hits = sum(1 for n in needles if n in text)
        if hits and not _exonerated_for(text, test_files, root):
            scored.append((-hits, p.name))
    scored.sort()
    return [name for _, name in scored[:limit]]


def _load_suspect_hit_rate(path=None):
    """The measured record of past suspect lists. Unreadable/malformed reads as EMPTY, which
    the phrase below renders as "not yet measured" — never as a flattering score."""
    p = Path(path) if path is not None else WEDGE_SUSPECT_HIT_RATE_FILE
    try:
        rec = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError, ValueError):
        return []
    eps = rec.get("episodes") if isinstance(rec, dict) else None
    return [e for e in eps if isinstance(e, dict)] if isinstance(eps, list) else []


def _append_suspect_outcome(entry, path=None):
    """Append one closed episode's outcome, bounded. Never raises."""
    p = Path(path) if path is not None else WEDGE_SUSPECT_HIT_RATE_FILE
    try:
        eps = _load_suspect_hit_rate(p)
        eps.append(entry)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"episodes": eps[-WEDGE_SUSPECT_HIT_RATE_MAX_EPISODES:]},
                                sort_keys=True))
    except (OSError, TypeError, ValueError) as exc:
        log("Publish gate: could not record the suspect-list outcome: {}".format(exc))


def suspect_hit_rate_phrase(path=None):
    """The running hit rate, carried in every alarm.

    MEASURED, not asserted: "hit" means the commits that landed while the episode was open
    touched a path this alarm had NAMED. That is weaker than "the list named the cause" (the
    human judgement the old 0/8 came from) and the phrase says so, because overstating a
    self-measurement is how the thing being replaced survived five episodes. Episodes where NO
    list was emitted (the blocking test was unrecorded) are counted separately, never as hits:
    a list that was never printed cannot have been useful.

    R12: a diagnostic. It is not a target, and no finding may be archived to move it."""
    eps = _load_suspect_hit_rate(path)
    scored = [e for e in eps if isinstance(e.get("hit"), bool)]
    no_list = len(eps) - len(scored)
    if not scored:
        return ("SUSPECT HIT RATE: not yet measured ({} closed episode(s) emitted no suspect "
                "list because the blocking test was unrecorded).".format(no_list))
    hits = sum(1 for e in scored if e["hit"])
    return ("SUSPECT HIT RATE: {}/{} closed episodes where the repair touched a path this "
            "alarm had named ({} more emitted no list at all). Diagnostic only -- never a "
            "target (R12); if it stays at 0 the re-derivation is as useless as the recency "
            "list it replaced and should be said so.".format(hits, len(scored), no_list))


def _paths_changed_since(since, project_dir=None):
    """Repo paths touched by commits landed since `since` (epoch seconds).

    None means UNMEASURABLE (no start time, git unavailable) — which the scorer records as an
    unmeasured episode, never as a hit. A self-measurement that fails open flatters itself."""
    if not isinstance(since, (int, float)):
        return None
    root = Path(project_dir) if project_dir is not None else PROJECT_DIR
    stamp = datetime.fromtimestamp(float(since), timezone.utc).isoformat()
    try:
        res = subprocess.run(
            ["git", "log", "--no-merges", "--since={}".format(stamp), "--name-only",
             "--pretty=format:"],
            cwd=str(root), capture_output=True, text=True, timeout=WEDGE_GIT_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return {ln.strip() for ln in (res.stdout or "").splitlines() if ln.strip()}


def _measure_suspect_list(prev, now, project_dir=None):
    """Score a CLOSING episode's suspect list and append it to the hit-rate record.

    The score is deliberately narrow and deliberately stated as such (see
    `suspect_hit_rate_phrase`): did the repair that closed the episode touch a path this alarm
    had NAMED? Three outcomes, and only one of them is a hit:
      * no list emitted (blocking test unrecorded)  -> hit=None, counted as "emitted no list"
      * emitted, but the change set is unmeasurable -> hit=None, flagged unmeasurable
      * emitted and measurable                      -> hit=True/False
    Never raises: an accounting failure must not break the recovery path it observes."""
    prev = prev if isinstance(prev, dict) else {}
    suspects = prev.get("suspects")
    paths = ((list(suspects.get("test_files") or []) + list(suspects.get("modules") or []))
             if isinstance(suspects, dict) else [])
    entry = {"closed_at": now, "suspects": len(paths),
             "blocking_tests": [str(b) for b in (prev.get("blocking_tests") or [])][
                 :GATE_MAX_CITED_BLOCKING_TESTS]}
    if not paths:
        entry["hit"] = None
    else:
        touched = _paths_changed_since(prev.get("wedge_since"), project_dir=project_dir)
        if touched is None:
            entry["hit"] = None
            entry["unmeasurable"] = True
        else:
            entry["hit"] = any(p in touched for p in paths)
    _append_suspect_outcome(entry)
    return entry


def _suspect_clause(blocking, suspects, linked):
    """The suspect block — derived from the red above, or ABSENT.

    No recorded blocking test => the empty string. `_blocking_clause` has already told the
    reader the id is unrecorded and told them not to infer a cause; appending a guess here
    would undo exactly that."""
    if not blocking or not suspects:
        return ""
    modules = suspects.get("modules") or []
    out = (" SUSPECTS (re-derived from the blocking test above -- NOT what was filed most "
           "recently): first-party modules that test imports: {}.".format(
               ", ".join(modules) if modules else "none resolvable"))
    commits = suspects.get("commits") or []
    if commits:
        out += " Commits touching those paths in the last {} days: {}.".format(
            WEDGE_SUSPECT_BLAME_DAYS, "; ".join(commits))
    else:
        out += (" NO commit in the last {} days touched those paths -- so the cause is more "
                "likely environmental (memory, a stale derived artefact, a data file) than a "
                "code change.".format(WEDGE_SUSPECT_BLAME_DAYS))
    if linked:
        out += " Filed findings whose text NAMES one of those paths (draw these first): {}.".format(
            ", ".join(linked))
    return out


def _episode_phrase(wedge_since, episode_failures, now):
    """One line of EPISODE memory: how long, how many, since when. Degrades to an explicit
    'unknown' rather than to a plausible-looking zero — an under-stated episode is exactly
    the defect being fixed."""
    if not isinstance(wedge_since, (int, float)):
        return "EPISODE: start time unrecorded (this alarm cannot bound the episode)."
    age_min = int(max(0.0, now - float(wedge_since)) // 60)
    since_iso = datetime.fromtimestamp(float(wedge_since), timezone.utc).strftime("%Y-%m-%dT%H:%M UTC")
    return ("EPISODE: wedged since {} -- {}h{:02d}m and {} consecutive failures in THIS "
            "episode (not a fresh hour).").format(
                since_iso, age_min // 60, age_min % 60, episode_failures)


def _census_clause(census, total_red, shown):
    """How much of the red set the line above is -- the difference between "one red" and "we
    stopped at one". Silence here is what let five instances of one class be served one per tick
    across 252 gate cycles; a depth claim that cannot be wrong is not a depth claim."""
    if census == CENSUS_COMPLETE:
        withheld = (" ({} more withheld -- read the census in "
                    "docs/observability/sim-runner-log.md)".format(total_red - shown)
                    if total_red > shown else "")
        return (" THAT IS THE WHOLE RED SET: {} test(s) red at this HEAD, enumerated by a "
                "report-only re-run without fail-fast{}. Fix them TOGETHER -- fixing one and "
                "re-running is how this wedge lasted 252 cycles.".format(total_red, withheld))
    if census == CENSUS_PARTIAL:
        return (" AT LEAST {} test(s) are red at this HEAD (the report-only census hit its own "
                "{}-failure bound, so there may be more). This is a STACK, not a single "
                "defect.".format(total_red, GATE_RED_CENSUS_MAXFAIL))
    if census == CENSUS_HOOK_CHAIN:
        return (" {} test(s) were named by the PRE-COMMIT HOOK CHAIN that refused the publish "
                "commit -- that is the whole red set of the hook that refused, and the hooks "
                "behind it never ran, so there may be more. Fix these TOGETHER and expect the "
                "next hook to have its own say.".format(total_red))
    return (" DEPTH UNKNOWN: the gate runs fail-fast and the report-only census did not run "
            "(no budget, timed out, or unavailable -- see the log), so this may be one red of "
            "many. Do NOT read it as the only one.")


def _blocking_clause(blocking, blocking_hash, census=CENSUS_FAIL_FAST_ONLY, total_red=0):
    """The one line that identifies the wedge -- or an honest statement that it is unknown.

    NEVER degrades to a guess. "Unrecorded" is a fact a reader can act on (go read the gate log);
    a fabricated suspect is the defect this whole payload replaces."""
    if blocking:
        at = " (gate subject {})".format(blocking_hash) if blocking_hash else ""
        return ("BLOCKING TEST{}: {}. Run exactly that node id against a clean checkout of "
                "HEAD.".format(at, "; ".join(blocking))
                + _census_clause(census, max(int(total_red or 0), len(blocking)), len(blocking)))
    return ("BLOCKING TEST: UNRECORDED -- the gate's failing node id was not captured (no red "
            "gate has run since this record was last cleared, or the record went stale). Read "
            "docs/observability/sim-runner-log.md for the last 'Publish gate RED' line; do NOT "
            "infer a cause from the backlog list below.")


def _fire_publish_gate_alert(recent, kind, rc, git_hash, unavailable, send_ntfy_fn,
                             *, wedge_since=None, episode_failures=0, now=None,
                             cited=None, markers_pending=None, blocking=None,
                             blocking_hash=None, suspects=None,
                             census=CENSUS_FAIL_FAST_ONLY, total_red=0,
                             cause=None, cause_evidence=None):
    now = time.time() if now is None else float(now)
    window_min = PUBLISH_GATE_WINDOW_SECONDS // 60
    n = len(recent)
    detail = _gate_failure_label(kind)
    count_phrase = "an unknown number of" if unavailable else str(n)
    suspects = wedge_suspects(blocking) if suspects is None else dict(suspects or {})
    cited = list(cited if cited is not None else linked_findings(suspects))
    markers = markers_pending if markers_pending is not None else pending_run_complete_markers()
    markers_phrase = "unknown (staging unreadable)" if markers is None else str(markers)
    what = ("The run-complete PUBLISH GATE has failed {} time(s) in a row within the "
            "last {} min -- the site/report pipeline is WEDGED and run_complete markers "
            "are piling up unpublished. Latest cause: {} (rc={}, git={}). {} "
            "Markers pending: {}.").format(
                count_phrase, window_min, detail, rc, git_hash,
                _episode_phrase(wedge_since, episode_failures, now), markers_phrase)
    if unavailable:
        what += (" NOTE: the gate-state file was unreadable, so this alert fired "
                 "fail-closed on the first failure rather than risk staying silent.")
    if kind == "tree_lock_unavailable":
        # THE THIRD MEMBER OF THE SAME CLASS (2026-08-30, see EXIT_TREE_LOCK_UNAVAILABLE).
        # Contention is the one wedge cause where the RIGHT action is to do nothing: the next
        # cycle retries and gets the lock. Sending the RUNG-1 draw after a red here does not
        # just waste the draw, it spends the attention the streak was raised to buy.
        how = ("NO TEST WAS JUDGED -- another writer held the tree lock for the whole "
               "timeout, so the publisher never reached its commit. Do NOT hunt a red and do "
               "NOT read the hook output: neither ran. Check for a long-running writer "
               "(`fuser -v docs/observability/.tree.lock`); a single occurrence is normal "
               "contention and clears itself on the next cycle. A STREAK of these is the real "
               "finding -- it means a writer is holding the lock longer than the publish "
               "cadence, and that writer is the subject, not any test.")
    elif kind == "gate_timeout":
        # THE READER IS NOT SENT AFTER A TEST THAT WAS NEVER JUDGED (2026-08-21, see
        # EXIT_GATE_TIMED_OUT). The standing clause below says "rc>0 means run that test at
        # HEAD" -- true of a red, a lie about a stopwatch, and the reason the RUNG-1 draw
        # spent a 32-hour wedge hunting nodes that pass.
        how = ("NO TEST WAS JUDGED -- the gate's own clock expired at "
               "{}s. Do NOT hunt a red: measure the gate's SCOPE against its bound "
               "(`python3 -m background.publish_scope`) and read the wall time in "
               "docs/observability/sim-runner-log.md. The alarm clears automatically on the "
               "next clean publish."
               ).format(GATE_SUITE_TIMEOUT_SECONDS)
    else:
        how = _blocking_clause(blocking, blocking_hash, census, total_red) + (
               " rc=-9 is almost certainly OOM (free memory or cut test parallelism), "
               "NOT a code bug; rc>0 means run that test at HEAD to find the regression. Full "
               "output: docs/observability/sim-runner-log.md, 'Publish gate RED output tail'. "
               "The alarm clears automatically on the next clean publish.")
    if cause and cause != publish_cause.UNATTRIBUTED:
        # THE ATTRIBUTION GOES ON THE PAGE, ahead of the standing prose, because the standing
        # prose is written for the common wedge and the whole point of the attribution is that
        # this is a different one. `_gate_failure_label` above still names the KIND; this names
        # which of the four that kind was and what was observed to decide it.
        how = ("ATTRIBUTED CAUSE: `{}` -- {}. {}").format(cause, cause_evidence, how)
    elif kind == "commit_did_not_land":
        # UNATTRIBUTED IS A RESULT AND IT IS SAID OUT LOUD. Silence here would leave the reader
        # with the standing "run that test at HEAD" prose and no way to know it was never
        # established -- which is the nine-episode failure this closes, one layer up.
        how = ("CAUSE NOT ESTABLISHED: {}. Do not assume a red -- read the publisher's own tail "
               "in docs/observability/sim-runner-log.md and `git ls-remote origin "
               "refs/heads/main` against HEAD before suspecting a test. {}").format(
                   cause_evidence or "no cause record was available", how)
    if kind not in UNJUDGED_GATE_KINDS and not publish_cause.no_test_was_judged(cause):
        # Suspects are DERIVED FROM `blocking`, which on a timeout is whatever an earlier cycle
        # left behind -- so on this kind they are not weak evidence, they are evidence about a
        # different cycle. Naming nobody beats naming the innocent.
        how += _suspect_clause(blocking, suspects, cited)
        how += " " + suspect_hit_rate_phrase()
    why = ("A silently-wedged publish gate stops the live site and report updating with "
           "NO other signal -- this is the exact ~45-min silent stall of 2026-07-14 (H15).")
    msg = "[ACTION NEEDED] {}\nWhat: {}\nHow: {}\nWhy: {}".format(PUBLISH_GATE_ITEM_ID, what, how, why)
    if send_ntfy_fn is None:
        from background.notify import notify
        send_ntfy_fn = lambda m: notify(m, kind="real_alarm")
    sent_id = send_ntfy_fn(msg)
    # Durable register + daily re-ping while it stays wedged (best-effort -- a
    # register failure must never suppress the NTFY that already went out).
    # CLASS FIX (2026-07-18): register_item() never advances the send-clock any
    # more -- only a CONFIRMED successful send (a truthy id) does, via
    # mark_sent(). A failed send here leaves the item due, so the deadman's
    # daily due_for_reping() sweep retries instead of the item silently
    # looking "recently pinged" on a page that never reached the phone.
    try:
        from background import action_needed
        action_needed.register_item(PUBLISH_GATE_ITEM_ID, what=what, how=how, why=why)
        if sent_id:
            action_needed.mark_sent(PUBLISH_GATE_ITEM_ID)
    except Exception as exc:
        log("Publish-gate action_needed register skipped: {}".format(exc))
    return msg


def record_publish_gate_failure(reason, rc=None, git_hash="unknown", *, now=None, send_ntfy_fn=None,
                                kind=None, cause=None, cause_evidence=None):
    """Record ONE publish-gate failure and fire a single [ACTION NEEDED] alert
    once N failures accumulate within the window (re-armed by a cooldown so a
    persistently-wedged pipeline can't spam). Returns a small result dict for
    callers/tests. Fully defensive -- never raises into the caller (a
    monitoring failure must not break the pipeline it monitors)."""
    try:
        now = float(now) if now is not None else time.time()
        state = _read_publish_gate_state()
        unavailable = bool(state.get("state_unavailable"))
        # An OBSERVED kind beats an inferred one. `_classify_gate_failure` reads a return
        # code, but a child killed by its caller's deadline never produces one -- and the
        # classifier's only honest answer for "no rc" is "unknown", while a caller that
        # invented an rc to get past it would be recording a fabrication. So a caller that
        # WATCHED the kill states the kind; everyone else still infers it from rc, unchanged.
        kind = kind if kind else _classify_gate_failure(rc)
        failures = [f for f in state.get("failures", [])
                    if isinstance(f, dict) and now - float(f.get("ts", 0)) <= PUBLISH_GATE_WINDOW_SECONDS]
        # `cause` is a FIELD beside `kind`, not a widening of it, for the reason the supervisor's
        # own `WEDGE_KINDS_NO_TEST_JUDGED` comment gives: `reason` is a human sentence that would
        # have to be pattern-matched, and `kind` is a closed set three other readers switch on.
        # The attribution is a third, finer answer to "what happened", so it gets its own field
        # and every existing reader is untouched.
        cause = cause if cause else publish_cause.UNATTRIBUTED
        # A REFUSAL TO ATTRIBUTE MUST NAME ITS REASON, ON EVERY BRANCH (2026-09-04). Only the
        # rc=77 caller passes a cause, because only it consults `read_cause` -- which by contract
        # ALWAYS returns a sentence, on the attribution and on the refusal alike. Every other
        # branch (rc=78, rc=79, and the generic fall-through that catches rc=1) passed neither,
        # so `str(cause_evidence or "")` stored the empty string and the record read
        # `"cause": "unattributed", "cause_evidence": ""` -- "we cannot tell" with no reason,
        # which is the one shape this project's rule on refusals forbids.
        #
        # OBSERVED, not inferred: `.publish_gate_state.json` at 2026-09-04 11:18:50Z carried
        # exactly that pair for `process_run_complete rc=1 on run_complete_20260904T104410Z.md`,
        # and the reader it was written for -- the RUNG-1 draw, and the seat brief quoting it --
        # got a verdict with nothing behind it. The prose in `_fire_publish_gate_alert` already
        # falls back to "no cause record was available"; the RECORD did not, and that module's
        # own comment says why that is the wrong way round: the record is the thing that gets
        # quoted.
        #
        # THE CAUSE IS NOT INVENTED HERE, only the reason for its absence. Reading
        # `PUBLISH_CAUSE_FILE` on these branches would attribute from the exit status -- the
        # publisher reaches them precisely when it did NOT observe one of the five named causes,
        # so any record at this hash is a different cycle's. That is the inference
        # `publish_cause` exists to refuse; the honest `unattributed` stands and now says why.
        evidence = str(cause_evidence or "").strip()
        if not evidence:
            evidence = ("recorded with no observation attached (rc={}, kind={}) -- {}".format(
                rc, kind,
                "this exit path names no cause, so which one it was is NOT established here"
                if str(cause) == publish_cause.UNATTRIBUTED
                else "the cause beside it was named without the observation that decided it"))
        failures.append({"ts": now, "reason": str(reason), "rc": rc, "kind": kind,
                         "git_hash": git_hash, "cause": str(cause),
                         "cause_evidence": evidence})
        count = len(failures)
        # PERSISTENT wedge-start (2026-07-24): preserve the existing streak start; only stamp `now`
        # when the streak is starting (no prior wedge_since). Survives the 1h window trim above so a
        # long wedge's true age stays measurable. Cleared to None by record_publish_gate_success.
        prev_wedge_since = state.get("wedge_since")
        wedge_since = prev_wedge_since if isinstance(prev_wedge_since, (int, float)) else now
        # EPISODE MEMORY: counts the whole streak, so it keeps rising after the window trim
        # drops older entries from `failures`. Cleared only by record_publish_gate_success.
        prev_episode = state.get("episode_failures")
        episode_failures = (int(prev_episode) if isinstance(prev_episode, int) else count - 1) + 1
        threshold_met = unavailable or count >= PUBLISH_GATE_FAILURE_THRESHOLD
        last_alert = state.get("alerted_at")
        armed = last_alert is None or (now - float(last_alert)) >= PUBLISH_GATE_COOLDOWN_SECONDS
        fired = False
        alerted_at = last_alert
        # EVIDENCE BEFORE SUSPICION (R9): re-read on every failure, not only at fire time, so
        # the state file the RUNG-1 draw reads names the CURRENT red's test even between pages.
        blocking, blocking_hash = last_blocking_tests(now=now)
        # NO GREEN TEST MAY APPEAR IN A BLOCKING LIST (2026-08-30, item (b) of the same
        # direction as `publish_cause`). `last_blocking_tests` is bounded by AGE alone, so on a
        # cause where nothing was judged -- a deadline kill, a push that never landed, a
        # provenance refusal -- it returns whatever an EARLIER cycle left behind. That is not
        # weak evidence about this failure, it is evidence about a different one, and the state
        # file is what the RUNG-1 draw and the director's own brief read: four green tests were
        # named as blockers of a wedge they had nothing to do with. Suppressed at the RECORD,
        # not only in the alarm prose, because the record is the thing that gets quoted.
        #
        # Keyed to the PROPERTY (did anything judge a test?), never to today's answer, and it
        # fails toward SHOWING the list: only a positively-attributed no-test-judged cause
        # suppresses. See `publish_cause.no_test_was_judged`.
        if publish_cause.no_test_was_judged(cause) and blocking:
            log("Publish gate: suppressing {} carried-forward blocking test(s) -- this failure "
                "is attributed to `{}`, on which NO test returned a verdict, so the record from "
                "git={} describes a different cycle.".format(
                    len(blocking), cause, (blocking_hash or "unknown")[:9]))
            blocking, blocking_hash = [], None
        # Read from the SAME record, at the same moment, so the depth claim can never describe a
        # different red than the node ids beside it.
        census, total_red = last_red_census(now=now)
        if blocking_hash is None and publish_cause.no_test_was_judged(cause):
            # The census counts the SAME record just suppressed. Leaving `total_red: 3` beside
            # `blocking_tests: []` would be the accusation-with-no-accused shape inverted, and
            # a depth claim about reds that were never this cycle's is still a claim.
            census, total_red = CENSUS_FAIL_FAST_ONLY, 0
        # SUSPECTS FROM THE RED (H42): re-derived on every failure, not only at fire time, so
        # the state file the RUNG-1 draw reads describes the CURRENT red between pages too. An
        # unrecorded blocking test yields {} and therefore NO suspects and NO citations --
        # never the recency fallback this replaced.
        suspects = wedge_suspects(blocking)
        cited = linked_findings(suspects)
        if threshold_met and armed:
            # ALARM->DIAL: the citation is persisted as well as paged, because the supervisor's
            # RUNG-1 unwedge draw reads the state file, not the NTFY.
            _fire_publish_gate_alert(failures, kind, rc, git_hash, unavailable, send_ntfy_fn,
                                     wedge_since=wedge_since, episode_failures=episode_failures,
                                     now=now, cited=cited, blocking=blocking,
                                     blocking_hash=blocking_hash, suspects=suspects,
                                     census=census, total_red=total_red,
                                     cause=cause, cause_evidence=cause_evidence)
            alerted_at = now
            fired = True
        _write_publish_gate_state({"failures": failures, "alerted_at": alerted_at,
                                   "wedge_since": wedge_since,
                                   "episode_failures": episode_failures,
                                   "cited_findings": cited,
                                   "blocking_tests": blocking,
                                   "red_census": census, "total_red": total_red,
                                   "suspects": suspects})
        log("Publish-gate failure #{} ({}, rc={}) -- alert {}".format(
            count, kind, rc, "FIRED" if fired else ("armed/cooldown" if threshold_met else "below threshold")))
        return {"count": count, "kind": kind, "threshold_met": threshold_met, "fired": fired}
    except Exception as exc:
        log("record_publish_gate_failure error (swallowed): {}".format(exc))
        return {"count": 0, "kind": "error", "threshold_met": False, "fired": False}


def _green_is_on_record_for(git_hash, last_tested_path=None):
    """Did the SUITE record a pass for exactly this commit? The one question rc=0 cannot answer.

    Reads `.last_tested_hash`, whose contract is stated once at the top of this module: written
    by `_run_gate_in` and ONLY on rc=0 from the suite. That makes it the single piece of state
    in the pipeline that a run publishing nothing cannot manufacture -- which is exactly what
    `record_publish_gate_outcome` needs before it is allowed to call a wedge recovered.

    FAIL-SAFE IS FALSE IN EVERY UNCERTAIN DIRECTION -- missing file, unreadable file, absent or
    "unknown" hash. An unavailable check is a FAILED check (R15), and here the harmless error is
    leaving an alarm armed one cycle too long; the harmful one is disarming the RUNG-1 draw
    while publishing is frozen, which is the defect actually observed on 2026-08-11."""
    if not git_hash or git_hash == "unknown":
        return False
    try:
        return (last_tested_path or LAST_TESTED_HASH_FILE).read_text().strip() == git_hash
    except OSError:
        return False


def _marker_git_hash(marker):
    """The commit a marker was produced at, read WHEREVER THE MARKER NOW LIVES.

    THE DEFECT THIS CLOSES (observed 2026-08-17, the wedge that could not end).
    `record_publish_gate_outcome` read the hash with `parse_marker(Path(marker))` at the path it
    was HANDED. But a SUCCESSFUL publish archives the marker to done/ as its last act, and only
    then does the caller route the return code -- so on the success path that path is always
    gone. `parse_marker` raised, the bare except left `git_hash = "unknown"`, and
    `_green_is_on_record_for("unknown")` is False BY DESIGN. Every genuinely green publish was
    therefore recorded "unproven" and the streak preserved:

        [2026-08-17 13:01 UTC] Publish gate: run_complete_20260817T122429Z.md exited 0 but no
        suite PASS is recorded for git=unknown -- ... the wedge streak is left exactly as it was
        found.

    while that marker reads `Git: 6a132fa61` and `.last_tested_hash` read `6a132fa61` -- the
    gate had passed for exactly that commit, 6 minutes earlier. The success path could not fire,
    so `episode_failures` climbed to 257 and `wedge_since` stayed pinned to 2026-08-09 against a
    pipeline that was publishing. An alarm whose CLEAR path is unreachable is not a strict alarm;
    it is a broken one, and it fires the RUNG-1 priority-zero draw every tick.

    Asking the archive policy where the file is now is what `_process` above already does for the
    same reason. FAIL-SAFE IS PRESERVED IN THE DIRECTION THAT MATTERS: a marker that is genuinely
    nowhere, or unreadable, still yields "unknown" and still clears nothing (R15 -- an unavailable
    check is a failed check). What changes is only that a marker which was archived BECAUSE the
    publish succeeded stops being read as evidence of nothing.

    Independence is untouched (R15 anti-tautology): the hash still comes from the marker, written
    by the sim runner before the gate ran, and the pass still comes from `.last_tested_hash`,
    written only by the gate's own rc=0. Two sources, neither derived from the other -- the fix
    changes which DIRECTORY one of them is read from, not who wrote it."""
    path = Path(marker)
    if not path.is_file():
        try:
            from background import staging_archive_policy
            located = staging_archive_policy.locate(path.name, done_dir=DONE_DIR)
        except Exception:
            located = None
        if located is None:
            return "unknown"
        path = located
    try:
        return parse_marker(path).get("git_hash", "unknown")
    except Exception:
        return "unknown"


def record_publish_gate_success(*, now=None, markers_pending=None):
    """A clean publish CLEARS the wedge state: resets the consecutive-failure streak, re-arms the
    alarm, and resolves the durable action_needed item if one was open. Idempotent; never raises.

    THE EPISODE CLOSES ONLY ON EVIDENCE (PW2, 2026-08-09). The old docstring said this cleared on
    "a clean publish (or a clean skip)" -- and that parenthetical was the defect. A path that
    published NOTHING could zero `wedge_since`/`episode_failures`, so the next failure opened a
    FRESH episode and the alarm truthfully described 14 minutes of a 10h26m outage.

    The evidence is `pending_run_complete_markers()`: the queue this pipeline exists to drain,
    read off the real staging directory and therefore INDEPENDENT of the gate's own state (R15
    anti-tautology -- a gate-state file that lies cannot make the backlog look drained). Zero
    markers pending is a demonstrated end of episode. Anything else -- markers still queued, or
    an unreadable staging dir -- clears the ALARM (`failures`, `alerted_at`, so nothing spams and
    no phantom rung-1 draw fires: that draw needs >= 3 in-window failures) while PRESERVING the
    episode memory, so a resumed wedge is still measured from where it really began."""
    try:
        had_state = False
        prev = {}
        if PUBLISH_GATE_STATE_FILE.exists():
            prev = _read_publish_gate_state()
            had_state = bool(prev.get("failures")) or prev.get("alerted_at") is not None
        pending = (pending_run_complete_markers() if markers_pending is None else markers_pending)
        episode_closed = (pending == 0)
        # THE SUSPECT LIST IS SCORED WHEN THE EPISODE IT DESCRIBED CLOSES (H42). Only on a
        # demonstrated close of a real episode -- a green gate with no wedge behind it has no
        # list to score, and scoring it would pad the denominator with free wins.
        if episode_closed and had_state:
            # SCORING THE LIST MAY NOT DECIDE WHETHER THE WEDGE CLEARS (2026-08-31).
            #
            # `_measure_suspect_list` writes `.wedge_suspect_hit_rate.json` -- a DIAGNOSTIC about
            # how good this pipeline's guesses were. It sat un-wrapped, one line above the clear,
            # inside the function's outer `except`: so any failure to write that side-file
            # abandoned the whole function and `_write_publish_gate_state` never ran. The observable
            # behaviour of "the hit-rate file is unwritable" was **the publish gate stays wedged**,
            # with `episode_failures` still standing and only a swallowed log line to say why.
            #
            # A full disk, a read-only mount, or a permissions change on docs/observability were
            # all enough. Found when the test-isolation sink began refusing that write and three
            # tests reported "a clean publish must CLEAR the wedge streak" -- the tests were right
            # and had been describing a real failure mode nobody had reached yet.
            #
            # Same class as the lane wall hook found the same afternoon: a control that enforces
            # only while an auxiliary WRITE succeeds. Fail-closed on unreadable input is a rule
            # here; this is its mirror and had no rule at all.
            try:
                _measure_suspect_list(prev, float(now) if now is not None else time.time())
            except Exception as exc:  # noqa: BLE001 - diagnostics may never gate a recovery
                log("Suspect-list scoring skipped (the wedge still clears): {}".format(exc))
        _write_publish_gate_state({"failures": [], "alerted_at": None, "wedge_since": None,
                                   "episode_failures": 0, "cited_findings": [], "suspects": {}},
                                  episode_closed=episode_closed)
        if had_state:
            log("Publish gate recovered -- cleared wedge state, re-armed alarm.")
            try:
                from background import action_needed
                reg = action_needed.load_register()
                if PUBLISH_GATE_ITEM_ID in reg and not reg[PUBLISH_GATE_ITEM_ID].get("resolved"):
                    ts = datetime.now(timezone.utc).isoformat()
                    action_needed.resolve_item(
                        PUBLISH_GATE_ITEM_ID,
                        answer="Auto-resolved: the publish gate recovered and a run published cleanly at {}.".format(ts))
            except Exception as exc:
                log("Publish-gate action_needed resolve skipped: {}".format(exc))
        return had_state
    except Exception as exc:
        log("record_publish_gate_success error (swallowed): {}".format(exc))
        return False


def record_publish_gate_outcome(marker, rc, *, kind=None):
    """Route ONE run-complete processing return code into the publish-gate wedge
    detector. THE shared router for every caller that publishes a marker.

    WHY IT LIVES HERE (2026-08-03, this exact defect): this routing used to
    exist ONLY as `background_worker._record_publish_gate_outcome`, wired into
    `process_leftover_run_markers()`'s sweep. But that sweep is NOT the path
    that actually publishes in the steady state -- `background/sim_runner.py`
    publishes the marker it just wrote, every cycle, and fed its return code to
    NOBODY. The detector was therefore blind to the ONLY healthy publisher and
    saw only the sweep, which by construction chews the STALE backlog. Result
    (observed 2026-07-30..08-03): sim_runner published cleanly every ~10 min --
    04:02Z "Committed locally... Done" -- while the sweep failed on 4-day-old
    markers, so the wedge streak only ever grew. The alarm stayed armed for
    ~5960 min against a pipeline that was working, firing a PRIORITY-ZERO
    doorbell each tick for a wedge that no longer existed.

    R10 (class, not instance): the fix is not "also call it from sim_runner" as
    a second copy -- it is ONE router that every publish path must feed, so a
    THIRD publisher added later cannot reintroduce a half-blind detector by
    forgetting to duplicate the logic.

    THREE outcomes, not two (fail-open closed 2026-07-29, preserved here): a
    lock-skip (EXIT_LOCK_SKIPPED) means the caller did NOT publish the marker
    -- evidence of NOTHING about the gate's health -- so it records NEITHER a
    success NOR a failure and leaves the streak exactly as it found it.
    Recording it as a success actively DISARMED the detector. Since 2026-08-12
    the same is true of EXIT_NOTHING_PUBLISHED (a duplicate marker another
    publisher already archived) -- both live in NO_PUBLISH_EXIT_CODES and both
    record neither, because "I published nothing" is one fact, not two.

    FOUR OUTCOMES NOW: rc=0 MEANS THE PUBLISHER EXITED CLEANLY, NOT THAT THE GATE PASSED
    (2026-08-11, the same fail-open one rung further out). The publisher returns 0 from every
    path that legitimately publishes NOTHING -- a fingerprint/duplicate-marker skip being the
    common one -- and each of those was routed straight into `record_publish_gate_success`,
    which cleared `failures`/`alerted_at` and logged "Publish gate recovered". So a run that
    never opened the gate DISARMED the wedge alarm, which is precisely the defect the lock-skip
    branch above was written to close, arriving through the neighbouring door.

    OBSERVED, not inferred (docs/observability/sim-runner-log.md, 2026-08-11 07:50Z): "Publish
    gate recovered -- cleared wedge state, re-armed alarm." logged in the same second as
    "Starting run" -- no gate ran between them -- against a `.last_tested_hash` still pinned at
    `dfefd0a14` from 2026-08-09. That file is written ONLY on rc=0 from the suite, so the gate
    had not passed for 41 hours while the state file read "not wedged". 197 such lines are in
    the log; the alarm they disarmed is the RUNG-1 priority-zero draw.

    THE EVIDENCE IS INDEPENDENT AND EXACT (R15 anti-tautology). Not "did the publisher exit 0"
    -- that is the claim under test -- but "did the suite record a PASS for THE COMMIT THIS
    MARKER WAS PUBLISHED AT", read off `.last_tested_hash`, whose sole writer is the gate's own
    return code (see LAST_TESTED_HASH_CONTRACT). Keyed on the MARKER's hash rather than current
    HEAD deliberately: HEAD moves under a long publish cycle as other lanes land, so a
    HEAD-keyed check would refuse to clear after a genuinely green gate and leave the alarm
    armed on a healthy pipeline -- the 5960-min false-armed defect this router exists to
    prevent. Absent/unreadable/unparseable => no green is claimed => "unproven", never a clear.

    Defensive by construction: a monitoring failure must never break the
    pipeline it monitors. Returns "success" / "failure" / "skipped" / "unproven" / None
    (None == the router itself errored) so callers and tests can assert which
    branch ran.
    """
    try:
        if rc in NO_PUBLISH_EXIT_CODES:
            return "skipped"
        # Read the hash WHEREVER THE MARKER IS NOW -- a successful publish archives it before
        # this router ever runs, and reading only the handed path made every green publish
        # "unproven". See _marker_git_hash.
        git_hash = _marker_git_hash(marker)
        if rc == EXIT_PUBLISH_DID_NOT_LAND:
            # NAMED, not left to `_classify_gate_failure`, which would read rc=77 as
            # "test_regression" and send the RUNG-1 draw hunting a red test that is not the
            # cause. The publisher WATCHED this one: its scoped suite was green and the COMMIT
            # was refused, so the payload says so and points at the hook chain's output.
            # ONE CAUSE, NAMED, WITH THE OBSERVATION THAT DECIDED IT (2026-08-30). This sentence
            # used to end "refused/timed out/never reached origin" -- three alternatives in one
            # breath, which is not a diagnosis, and nine consecutive episodes of it produced no
            # attribution at all while origin sat five commits behind HEAD. The publisher knew
            # which of the four it was at the moment it happened and threw it away between
            # processes; `publish_cause` carries it across. Absent or from another commit reads
            # as UNATTRIBUTED and SAYS so -- "we cannot tell" is a result, a disjunction is not.
            cause, cause_evidence = publish_cause.read_cause(
                PUBLISH_CAUSE_FILE, git_hash, max_age=GATE_BLOCKING_TESTS_MAX_AGE_SECONDS)
            record_publish_gate_failure(
                "the publish COMMIT did not land for {} -- the publisher's own scoped suite was "
                "GREEN. Cause: {} ({})".format(Path(marker).name, cause, cause_evidence),
                rc=rc, git_hash=git_hash, kind="commit_did_not_land",
                cause=cause, cause_evidence=cause_evidence,
            )
            return "failure"
        if rc == EXIT_GATE_TIMED_OUT:
            # NAMED for the same reason as the code above, and for the reason `deadline_kill`
            # is named on the two OUTER callers: `_classify_gate_failure` would read rc=78 as
            # "test_regression" and send the RUNG-1 draw hunting a red test that does not
            # exist. The publisher's OWN clock stopped this one, and it knows that.
            record_publish_gate_failure(
                "the publisher's own gate clock expired on {} before the suite returned a "
                "verdict -- NO test was judged, so no test is implicated".format(
                    Path(marker).name),
                rc=rc, git_hash=git_hash, kind="gate_timeout",
            )
            return "failure"
        if rc == EXIT_TREE_LOCK_UNAVAILABLE:
            # NAMED for the third time and the same reason (see EXIT_TREE_LOCK_UNAVAILABLE):
            # `_classify_gate_failure` would read this as "test_regression" and send the RUNG-1
            # draw hunting a red test. Nothing was judged -- the publisher never got the lock.
            record_publish_gate_failure(
                "the tree lock was held by another writer for the whole timeout on {} -- the "
                "publisher never reached its commit, NO test was run, so no test is "
                "implicated".format(Path(marker).name),
                rc=rc, git_hash=git_hash, kind="tree_lock_unavailable",
            )
            return "failure"
        if rc == 0:
            if not _green_is_on_record_for(git_hash):
                log("Publish gate: {} exited 0 but no suite PASS is recorded for git={} "
                    "-- publishing nothing is not evidence the gate is healthy, so the wedge "
                    "streak is left exactly as it was found.".format(
                        Path(marker).name, git_hash))
                return "unproven"
            record_publish_gate_success()
            return "success"
        record_publish_gate_failure(
            "process_run_complete {} on {}".format(
                "killed by the caller's deadline" if kind == "deadline_kill"
                else "rc={}".format(rc),
                Path(marker).name),
            rc=rc, git_hash=git_hash, kind=kind,
        )
        return "failure"
    except Exception as exc:
        log("record_publish_gate_outcome error (swallowed): {}".format(exc))
        return None


def maybe_ntfy(data, net_margin, insights=None):
    """Send NTFY for notable exceptions. Returns log message if sent, else None."""
    admin = data.get("administration_event")
    from background.notify import notify
    if admin:
        date_str = admin.get("date", "unknown date") if isinstance(admin, dict) else str(admin)
        notify(
            "[SIM] ADMINISTRATION EVENT on {} - net margin £{:,.0f}. Check annual report.".format(
                date_str, net_margin
            ),
            kind="real_alarm",
        )
        return "NTFY sent: administration event on {}".format(date_str)
    prev_best = _run_history_max_net()
    is_new_high = net_margin > prev_best * 1.01 and prev_best > 0
    is_new_low = net_margin < prev_best * 0.5 and prev_best > 1_000_000
    if not (is_new_high or is_new_low):
        return None
    tag = "[NEW HIGH]" if is_new_high else "[NEW LOW]"
    summary = getattr(insights, "executive_summary", "") if insights else ""
    acts = list(getattr(insights, "recommended_actions", ()) if insights else [])
    msg = "[SIM] {} Net margin £{:,.0f}".format(tag, net_margin)
    if summary:
        msg += " -- " + str(summary)[:120]
    if acts:
        msg += " | Action: " + str(acts[0])[:80]
    notify(msg, kind="real_alarm")
    return "NTFY sent: {} net margin £{:,.0f}".format(tag, net_margin)



def main(marker_path_str):
    """COUPLING (2026-07-13, director-flagged; the exit-code half FIXED
    2026-07-29): a lock-skip below returns EXIT_LOCK_SKIPPED (75), a THIRD
    outcome distinct from both "ran to completion" (0) and "a real processing
    error" (1, inside `_process()`). It used to return 0, so no caller could
    tell a skip from a real publish -- and `background_worker`'s sweep
    therefore fed rc==0 into `record_publish_gate_success()`, wiping the H15
    wedge streak for a marker it had never published (fail-open: the detector
    disarmed by its own input). Callers must now treat 75 as "still pending,
    nobody published it": no success, no failure. `background/sim_runner.py`
    only
    ever calls this with the ONE marker it just created THIS cycle -- it
    never re-scans staging/ for a marker it was told (by this exact log
    line) would be "picked up next cycle if still present." That promise
    is not kept by this function or by sim_runner.py; it is kept ENTIRELY
    by `background/background_worker.py::process_leftover_run_markers()`,
    which unconditionally re-globs every `run_complete_*.md` in staging/ at
    the top of its own loop, every cycle, regardless of peak hours or queue
    state -- see that function's own docstring for the other half of this
    coupling. A marker skipped here WILL still be processed, just not by
    sim_runner.py's own retry (there is none) -- by background_worker.py's
    sweep instead."""
    with _run_lock() as acquired:
        if not acquired:
            log("Another process_run_complete instance is already running -- "
                "skipping {} (will be picked up by background_worker.py's "
                "process_leftover_run_markers() sweep, not by sim_runner.py "
                "itself retrying)".format(
                    Path(marker_path_str).name))
            return EXIT_LOCK_SKIPPED
        return _process(marker_path_str)


def _process(marker_path_str):
    marker = Path(marker_path_str).resolve()
    if not marker.exists():
        # Archived markers live in done/ OR in the exhaust tree (AO10), so ask
        # the policy where it is rather than globbing one directory -- a
        # duplicate that reads as "not found" returns 1 and alarms for nothing.
        from background import staging_archive_policy
        archived = staging_archive_policy.locate(Path(marker_path_str).name, done_dir=DONE_DIR)
        if archived is not None:
            log("Already archived at {} (duplicate run): {} -- NOTHING was published by this "
                "process, so this is evidence of nothing about the gate's health "
                "(rc={})".format(
                    archived.parent.name, Path(marker_path_str).name, EXIT_NOTHING_PUBLISHED))
            return EXIT_NOTHING_PUBLISHED
        log("Marker not found: {}".format(marker))
        return 1

    log("Processing {}".format(marker.name))
    fields = parse_marker(marker)
    json_path = fields.get("json_path")
    git_hash = fields.get("git_hash", "unknown")
    elapsed_s = fields.get("elapsed_s", 0.0)

    if not json_path or not json_path.exists():
        log("JSON not found: {}".format(json_path))
        return 1

    data = json.loads(json_path.read_text())
    net_margin = data.get("total_net_gbp", 0)

    # Change-detection gate: if this run's meaningful outputs are identical to
    # the last fully-processed run (same headline figures, same UTC date), the
    # entire regen/test/commit pipeline below would reproduce byte-identical
    # surfaces -- skip it, log one line, archive the marker. An administration
    # event always processes (never skipped) so the NTFY exception path fires.
    # A pending FORCE_REPUBLISH_FLAG (a hold was just released) also forces
    # processing through regardless of fingerprint match -- see its own
    # comment above for why: a code fix can change correctness without
    # moving headline figures enough to break the fingerprint match.
    fingerprint = _run_fingerprint(data)
    # R3 two-strike redesign (2026-07-12, director page comment "/project/
    # data looks stale"): a real, code-only change (a new UI feature, a new
    # billing mechanism with no material P&L impact) previously left every
    # tracked headline figure unchanged, so the gate silently skipped
    # publishing for ~5 hours straight across 7+ real commits -- the exact
    # same class of incident FORCE_REPUBLISH_FLAG was built for (the
    # hold-release case), recurring on a different trigger (an ordinary
    # commit, not a hold release). Folding the producing commit's hash into
    # the compared fingerprint closes the class generally: ANY new commit
    # since the last published run now breaks the equality check and forces
    # a republish, regardless of whether financial headline figures moved --
    # while a genuinely unchanged commit across consecutive cycles (the
    # common case) still skips exactly as before.
    fingerprint["source_git_hash"] = git_hash
    last_fp = _read_last_fingerprint()
    forced = FORCE_REPUBLISH_FLAG.exists()
    if last_fp == fingerprint and not fingerprint["administration_event"] and not forced:
        _archive_marker(marker)
        log("SKIP (change-detection gate): identical to last processed run "
            "[net=\xa3{:,.0f}, date={}] -- no regen/test/commit. Archived {}.".format(
                net_margin, fingerprint["date"], marker.name))
        # Fault #1 (2026-07-25): even on a content SKIP, keep the PUBLISHED liveness
        # surface fresh on origin (throttled) -- the on-disk heartbeat updates every
        # 60s but only reached origin via a content publish, so an unchanged-output
        # night froze the live-site heartbeat ~4h though the machine was healthy.
        try:
            _refresh_published_liveness_on_skip(git_hash)
        except Exception as exc:  # never let liveness publishing break the SKIP path
            log("Liveness refresh on SKIP raised (non-fatal): {}".format(exc))
        return 0
    if forced:
        log("FORCED processing (a hold was just released) -- bypassing change-detection gate "
            "regardless of fingerprint match [net=\xa3{:,.0f}, date={}].".format(
                net_margin, fingerprint["date"]))
        FORCE_REPUBLISH_FLAG.unlink()

    log("Regenerating ANNUAL_REPORT.md from {}".format(json_path.name))
    if not regenerate_report(json_path):
        log("Report regeneration failed")
        return 1

    log("Updating LATEST.md")
    update_latest_md(data, elapsed_s, git_hash)

    # Run insights (so-what layer) MUST be regenerated before the dashboard/
    # site build below: generate_dashboard_data.py reads run_insights.json
    # straight off disk for the exec-summary section, separately from the
    # run_output.json it loads for the totals section. Building the dashboard
    # first would bake in the PREVIOUS run's exec summary next to this run's
    # totals -- exactly the contradiction the website-integrity fix closed.
    log("Generating run insights (so-what layer)")
    run_insights = None
    try:
        from tools.generate_insights import append_run_history, generate_insights, save_insights
        run_insights = generate_insights(data, git_hash)
        save_insights(run_insights, RUN_INSIGHTS_PATH)
        append_run_history(run_insights, RUN_HISTORY_PATH)
        log("Run insights saved: {}".format(run_insights.executive_summary[:80]))
    except Exception as exc:
        log("Run insights generation skipped: {}".format(exc))

    # H11_naive_organ live hook: run AFTER run_history.json is appended above so
    # the flat-metric detectors (T1/T5) see this run's figure. Questions only.
    run_naive_organ_step()

    # G5_effort_sizing_discipline L2 live hook: refresh the 'EFFORT SIZING'
    # digest block (remaining-effort / estimate-vs-actual / XL-decompose
    # signal). Reads maturity_map.yaml directly; independent of run_history.
    run_effort_digest_step()

    log("Generating site/data/dashboard.json")
    consistency_ok = generate_dashboard_json(json_path, git_hash)
    if not consistency_ok:
        from background.notify import notify
        notify(
            "[SIM] CONSISTENCY GATE FAILED (git={}) — dashboard totals and exec-summary "
            "insights disagree on a headline number. Site figures may be untrustworthy "
            "until this is fixed. See docs/observability/sim-runner-log.md for detail.".format(git_hash),
            kind="real_alarm",
        )
        log("NTFY sent: consistency gate failure")
    generate_site(data, elapsed_s, git_hash, fields.get("finished"))

    try:
        from tools.revenue_sanity_check import run_check
        _ok, sanity_report = run_check(data)
        status = "PASS" if _ok else "ANOMALIES"
        log("Revenue sanity: {} — see annual report".format(status))
    except Exception as exc:
        log("Revenue sanity check skipped: {}".format(exc))

    log("Publishing market price feed")
    try:
        from simulation.publish_market_feed import publish as _publish_feed
        _publish_feed()
        log("Price feed published to docs/market_data/price_feed.json")
    except Exception as exc:
        log("Price feed publication skipped: {}".format(exc))

    log("Publishing HH consumption data feed")
    try:
        from simulation.publish_consumption_data import publish_consumption
        publish_consumption()
        log("Consumption feed published to docs/market_data/consumption_feed.json")
    except Exception as exc:
        log("Consumption feed publication skipped: {}".format(exc))

    # THE GRID-INTENSITY SHAPE FEED, and it must run AFTER the consumption feed and after
    # `generate_explore_hh_day` above -- it sizes its own record window from the dated days
    # those two publish, so a feed built first would carry a fortnight of half hours and none
    # of the days anyone actually has a meter read for. That was the failure on its first run:
    # the Explore page would have shown a household's half-hourly consumption beside no carbon
    # at all. Not zero carbon -- none, silently.
    log("Publishing grid carbon-intensity shape feed")
    try:
        from tools.generate_grid_intensity_feed import generate as gen_intensity
        _feed = gen_intensity()
        log("Grid intensity feed published: {} record(s) over {}..{}, {} year(s) summarised"
            .format(len(_feed.get("records") or []),
                    (_feed.get("records_cover") or {}).get("from"),
                    (_feed.get("records_cover") or {}).get("to"),
                    len(_feed.get("by_year") or {})))
    except Exception as exc:
        log("Grid intensity feed publication skipped: {}".format(exc))

    # THE BASELINE TO BEAT (director, 2026-08-25: "Average behaviour is the control -- the same
    # book run by a supplier applying flat rules with no per-customer view. Without that
    # comparison, 'it performed well' means nothing."). Two arms over the live book, every cycle,
    # so the control cannot drift away from the supplier it describes and the comparison cannot
    # freeze against a book that has moved. Cheap: two JSON reads and a few hundred decisions.
    log("Comparing pricing arms against the flat-rule control")
    try:
        from tools.couple_value_based_pricing import generate as gen_arms
        _arms = gen_arms()
        log("Pricing arms: {} account(s) priced, {} differ from the control, fit to run: {}"
            .format(_arms.get("accounts_priced"), _arms.get("differs_from_control"),
                    (_arms.get("verdict") or {}).get("fit_to_run")))
    except Exception as exc:
        log("Pricing-arm comparison skipped: {}".format(exc))

    # The mission's own number, on the days Explore already shows. Same R11 no-orphan-transition
    # reason as its neighbours: a generated surface that does not ride the regen cycle freezes
    # against its live source, and this one is downstream of THREE of them.
    log("Generating explore carbon layer")
    try:
        from tools.generate_explore_carbon import generate as gen_carbon
        _carbon = gen_carbon()
        log("Generated site/data/explore_carbon.json ({} measured account-day(s); {} of {} "
            "accounts have a half-hourly-capable meter)".format(
                len([a for a in _carbon.get("accounts") or [] if "co2e_kg_timed" in a]),
                _carbon.get("half_hourly_capable_meters"), _carbon.get("accounts_on_book")))
    except Exception as exc:
        log("explore_carbon.json generation skipped: {}".format(exc))

    log("Fetching weather data (Open-Meteo)")
    try:
        _run_weather_data(git_hash)
        log("Weather data written to site/data/weather.json")
    except Exception as exc:
        log("Weather data fetch skipped: {}".format(exc))

    # PRE-GATE RECONCILIATION (2026-07-16, class fix for the stale-live-state test
    # wedge): fold any atom_status inbox a fork wrote (F1, in its own commit) into the
    # working-tree map BEFORE the gate, so the map-reconciliation CONTROL tests a
    # RECONCILED map, not a fork/fold-race transient. An unfolded W1_8 inbox intermittently
    # failed test_no_unfolded_atom_status_inbox_at_rest and wedged the publish gate. This
    # closes the whole reconciliation-race CLASS (any pending fork report), not one atom.
    # Working-tree fold is enough for the gate; git_commit_push includes the map so the
    # fold is published, not left dangling. tree_lock serialises against the daemon's own
    # fold. Non-fatal: a fold error must never crash the publish.
    try:
        from background.tree_lock import tree_lock as _tree_lock
        from tools import merge_atom_status as _mas
        with _tree_lock():
            # suppression-lint: not-a-suppression _folded -- functional reduce (atom_status inbox reconciliation), not a page/alarm suppression
            _folded = _mas.merge()
        if _folded:
            log("Pre-gate fold: reconciled {} pending atom_status inbox(es) into the map: {}".format(
                len(_folded), _folded))
    except Exception as _exc:
        log("Pre-gate inbox fold skipped (non-fatal): {}".format(_exc))

    _publish_tree_divergence()

    log("Running fast test suite (SIM_FAST_MODE=1)")
    tests_ok, timed_out = run_fast_tests(git_hash)
    if not tests_ok:
        # BEHIND, NEVER FROZEN, NEVER SILENT (ruling property 3). The content publish is
        # correctly refused -- do not ship figures the publish path's own suite says may be
        # wrong -- but the site must not go quiet about it. The banner (and ONLY the banner)
        # goes to origin, so the visitor sees the last verified run under a dated
        # "verification paused since T" line instead of a stamp that has silently stopped
        # moving. 25 hours of exactly that silence is what this ruling was written from.
        # A TIMEOUT IS NOT A RED (2026-08-21, see EXIT_GATE_TIMED_OUT). Both refuse the
        # publish and both keep the streak; only one of them is entitled to say a test failed.
        code, log_line, reason = _gate_refusal(timed_out, git_hash, last_blocking_tests()[0])
        log(log_line)
        _publish_provenance_banner(git_hash, reason=reason)
        return code
    if timed_out:
        log("WARNING: tests timed out — results unverified but committing")

    # Move the marker to done/ BEFORE committing so the archive itself lands in
    # the same commit as the run it documents, instead of sitting untracked
    # forever (observed: 7+ done/ markers never made it into any commit).
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        marker.rename(DONE_DIR / marker.name)
        _record_archived_marker(DONE_DIR / marker.name)
        log("Moved {} to done/".format(marker.name))
    except FileNotFoundError:
        if (DONE_DIR / marker.name).exists():
            # Recorded even on the concurrent-processing branch: the marker IS in done/ and
            # uncommitted, and whichever process notices it should be the one that lands it.
            _record_archived_marker(DONE_DIR / marker.name)
            log("{} already in done/ (processed concurrently)".format(marker.name))
        else:
            log("WARNING: {} vanished from staging and not in done/".format(marker.name))

    # NEWEST-VERIFIED ALWAYS FLOWS (ruling property 1). Stamped BEFORE the commit so the
    # provenance lands in the SAME commit as the run it describes -- a stamp published a cycle
    # later would claim a verification time for figures that were already on the site, which
    # is the fake-fresh sin with an off-by-one. This is the only advance of `last_verified`
    # there is, and it is reachable only from here, downstream of a green scoped gate.
    try:
        _prov = publish_provenance
        # THE POPULATION TRAVELS WITH THE CLAIM (2026-08-31). The publisher already holds the run
        # it is about to attribute the page to, so it costs one dict to say what was in it. Without
        # this the page names a run and says nothing about it -- and the run itself is 27 MB and is
        # not retained, so "showing run X" was a citation nobody could follow. See
        # `publish_provenance.population_of`.
        _state = _prov.record_verified(
            run_id=json_path.name, git_commit=git_hash,
            population=_prov.population_of(data),
            generated_at=(data.get("meta") or {}).get("generated_at"))
        log("Provenance: {}".format(_prov.banner_line(_state)))
    except Exception as exc:  # noqa: BLE001 -- provenance must never break a green publish
        log("Provenance stamp skipped (non-fatal): {}".format(exc))

    log("Committing and pushing (net=\xa3{:,.0f})".format(net_margin))
    publish_outcome = {}
    if not git_commit_push(git_hash, net_margin, outcome=publish_outcome):
        log("Commit/push failed ({})".format(
            publish_outcome.get("reason", "reason not recorded")))

    # Record this run's fingerprint AFTER a full process so the next identical cycle is skipped
    # by the change-detection gate above -- but ONLY when re-running it would genuinely find
    # nothing to do (RETRYABLE_PUBLISH_OUTCOMES: it published, the index was empty, or it is
    # committed and waiting on the push throttle).
    #
    # THE EIGHTEEN-HOUR FREEZE WAS THE OTHER BRANCH (2026-08-13). This was unconditional, and
    # the comment defending it -- "written even if the commit was a no-op (nothing changed)" --
    # was reasoning about ONE of the ways `git_commit_push` returns False while the code applied
    # to all six. A commit killed by the hook deadline therefore recorded the run as fully
    # processed, and the change-detection gate then skipped every identical cycle after it. The
    # timeout branch logs "Nothing committed; retrying next cycle"; this line is what made that
    # promise false, and the retry it named could only ever happen if the sim's own figures
    # changed. Twenty-one consecutive timeouts, and the fingerprint kept every one of them from
    # being retried.
    reason = publish_outcome.get("reason")
    if reason in RETRYABLE_PUBLISH_OUTCOMES:
        _write_last_fingerprint(fingerprint)
    else:
        log("Fingerprint NOT recorded (publish outcome: {}) -- this cycle is unfinished, so the "
            "next identical run must re-attempt it rather than be skipped as already "
            "processed.".format(reason or "unknown"))

    # The complement of the scoped gate: run it AFTER the publish (it may not add latency to
    # what it may not block) and put its reds on the page as an annotation. See the function's
    # own docstring for why the narrowing is only honest with this in place.
    run_remainder_annotation_step(git_hash)

    # Keep agent_status.json financial metrics current (phase/tests preserved by phase-close)
    try:
        import json as _json

        from background.agent_status import STATUS_FILE, update_sim_metrics
        _existing = _json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
        update_sim_metrics(
            phase=_existing.get("phase", 0),
            tests_passing=_existing.get("tests_passing", 0),
            treasury_gbp=data.get("final_treasury_gbp", 0),
            net_margin_gbp=data.get("total_net_gbp", 0),
            enterprise_value_gbp=data.get("enterprise_value_gbp", 0),
        )
    except Exception as exc:
        log("agent_status metrics update skipped: {}".format(exc))

    ntfy_msg = maybe_ntfy(data, net_margin, run_insights)
    if ntfy_msg:
        log(ntfy_msg)

    # THE EXIT CODE NOW CARRIES THE OUTCOME (2026-08-19, see EXIT_PUBLISH_DID_NOT_LAND).
    # `reason` is the same value the fingerprint decision above already acted on -- this is
    # the second consequence it always should have had. rc=0 keeps asserting exactly one
    # thing: this process retired the marker AND the published surfaces are current.
    rc = publish_exit_code(reason)
    if rc == 0:
        log("Done")
        return 0
    log("Done, but THE PUBLISH DID NOT LAND (outcome: {}) -- the surfaces this process "
        "regenerated are still local, the marker is archived, and the live site keeps serving "
        "the older snapshot. Reporting rc={} so the publish-gate wedge detector records a "
        "FAILURE: a refused commit used to exit 0 and CLEAR the streak.".format(
            reason or "not recorded", rc))
    return rc


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/process_run_complete.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("process_run_complete")
    if len(sys.argv) != 2:
        print("Usage: {} <path/to/run_complete_TIMESTAMP.md>".format(sys.argv[0]))
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
