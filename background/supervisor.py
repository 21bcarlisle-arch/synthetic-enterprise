"""THE SUPERVISOR -- sole authority for turn-granting (2026-07-09, doorbell
failure #4, R3 architecture-level rebuild, director-direct).

A single dumb loop. Every POLL_INTERVAL_SECONDS: if the session is idle AND
real work exists on disk (an open agenda, unprocessed staging, an urgent
from_rich message, a usage-limit pause that just ended, OR -- 2026-07-10,
SELF_DIRECTION_AND_PARALLELISM.md Problem 1, REDESIGNED same-day per a
director audit + R3 -- a dial-weighted draw from docs/design/
maturity_map.yaml's real capability atoms with an open gap, falling back to
the original PRIORITIES.md "## Backlog" prose scan only if the YAML is
unavailable), grant exactly one turn via the locked relay, verify it was
consumed, and log the decision either way -- every cycle, not just the
interesting ones.

The self-refill check (`_actionable_backlog_item()`) is a cheap mechanical
heuristic, not comprehension -- it never treats a BLOCKED or REVIEW GATE
line as self-refillable, and it never says what to do beyond "something is
open," matching R7 exactly like every other reason string here. The
granted session decides what's actually worth doing by reading
PRIORITIES.md itself, same as always.

Why this exists (three independent things broke the same night, see
docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md):

1. background/agenda.py's should_nudge() is nudge-ONCE-per-snapshot (R5's
   "never repeat an unchanged status" applied to turn-granting, not just
   alerting). One nudge fired, was logged delivered, and then never fired
   again for that snapshot -- even though the work behind it sat undone for
   5+ hours. Polling every cycle regardless of prior "success" kills this
   bug outright: `should_nudge` is never consulted at all any more.
2. staging_watcher.py -- a multi-responsibility daemon (git fetch, new-file
   notify, wake, agenda-nudge, monthly maintenance) -- went silently inert
   for 5+ hours while still alive (not hung: wchan=hrtimer_nanosleep, no
   blocking syscall observed), taking every one of those responsibilities
   down with it. A single-purpose daemon with no network calls and no other
   duties in its hot loop has a much smaller surface for this class of
   silent stall. THIS is why the supervisor never calls git, NTFY (except
   the rare stuck-escalation), or anything else that can block -- only
   local disk reads and the already-hardened tmux relay.
3. session_watchdog's autoloop DID keep polling every ~10 minutes and
   logged "delivered (confirmed)" 34 consecutive times over 5.5 hours --
   and produced no observable work. Verified pane-consumption is evidently
   not sufficient proof a turn actually executed (root cause not fully
   observable from outside the Claude Code CLI process -- see R9 note in
   the retrospective). Polling alone does not detect this; it just makes
   the same silent failure repeat faster. The supervisor additionally
   tracks a narrow key of real work-state (_stuck_key(), disk-persisted in
   STUCK_STATE_FILE) across cycles: if it keeps granting turns for the SAME
   unchanged key past STUCK_THRESHOLD_SECONDS of wall-clock time, that is
   no longer an ordinary retry -- it escalates with one NTFY (deduped per
   stuck key, R5-compliant) instead of retrying silently forever. This is
   the one piece beyond the director's literal spec, added because failure
   #4 specifically would NOT have been caught by polling cadence alone.
   REDESIGNED 2026-07-11 (R3, second failure of this exact mechanism,
   director-caught): the original in-memory grant-COUNT version's
   fingerprint included PRIORITIES.md's mtime and the raw unprocessed-
   staging list, so real work on OTHER items (editing PRIORITIES.md) and
   transient run_complete_*.md churn both reset the "unchanged" counter to
   1 every time, masking a full night where the actual blocker (two staged
   files) never moved. Replaced with a disk-persisted, wall-clock tracker
   keyed narrowly enough to exclude both noise sources -- see _stuck_key().

Every other turn-granting path (session_watchdog's autoloop nudge, its
REVIEW_GATE reply relay, staging_watcher's new-file wake and agenda-nudge,
dispatcher's URGENT promotion) still exists as an optional fast-path hint
-- when they work, the session responds sooner than the next supervisor
cycle. But none of them is load-bearing any more: if every one of them
silently fails simultaneously, exactly as happened tonight, the supervisor
still guarantees a turn within POLL_INTERVAL_SECONDS.

R7 applies to the granted-turn text itself: it carries ZERO content
authority, a doorbell only ("work exists, read it from disk yourself"),
never a directive -- same discipline as every other wake in this codebase.

4. WORK-GRANTING REDESIGN (2026-07-12, R3_WORK_GRANTING_REDESIGN.md, P0,
   9th idle variant, director-caught from the live console -- "the
   director is hand-typing 'self-refill next atom' -- he is manually
   performing the supervisor's core function"). Root cause named precisely
   in the redesign order: granting was TRIGGER-DRIVEN ("doorbell -> if
   nothing there -> idle") when it must be BACKLOG-DRIVEN ("doorbell (if
   any) -> handle it -> THEN draw the next atom from the map, always").
   The concrete bug: `find_work()`'s "unprocessed staging" check included
   `run_complete_*.md` -- the auto-process daemon's OWN routine
   coordination marker, landing every ~13min on sim_runner's own cadence,
   needing no granted turn at all to be handled -- in the SAME list used to
   decide "real work exists on the instruction channel." So as long as
   that marker sat in docs/staging/ (nearly always), `find_work()` returned
   "unprocessed staging -- run_complete_X.md" and NEVER reached the
   self-refill draw below it. The granted session then correctly concluded
   "that's the daemon's own work, nothing for me to do" -- individually
   correct, collectively wrong: ~35 open map atoms sat idle while this
   repeated every ~2 minutes. Fixed: (1) `_real_staged_instructions()`
   excludes daemon markers from the instruction-channel check entirely
   (`_is_daemon_marker()`); (2) the self-refill draw (`_self_refill_draw()`)
   is now UNCONDITIONAL -- it runs and gets appended to the reason even
   when a real agenda/urgent/staged item already fired, so a granted turn
   is never JUST daemon housekeeping with no real capability-building work
   attached; (3) `find_work()` now returns `(reason, map_exhausted)` --
   `map_exhausted` is True only when the self-refill draw itself found
   nothing (every atom blocked/complete, or the map unreadable), distinct
   from "didn't draw because something else took priority" (requirement 4:
   escalate on CANNOT-draw, never on didn't-draw); (4) an idle-turn counter
   (`_record_idle_turn()`/`IDLE_TURN_COUNTER_FILE`) instruments the
   "nothing to do" state directly rather than letting it pass silently
   (requirement 1: target is zero, and every occurrence is now visible in
   the log, not just inferred from its absence).
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import agenda as agenda_module  # noqa: E402

# THE READ SIDE ONLY. `background/delivery_seat.py` -- the session that WRITES direction -- is
# never imported here and must not be: the draw reads a validated file on disk and has no path to
# the thing that produced it. See docs/design/THE_DELIVERY_SEAT.md §2 for why that severance is
# the whole design, and background/daily_self_note.py for the law it is the other side of.
from background import direction as _direction  # noqa: E402
from background.agent_status import update_agent_status  # noqa: E402
from background.coupled_triad import (  # noqa: E402
    load_gap_ledger as _coupled_load_gap_ledger,
)
from background.coupled_triad import (  # noqa: E402
    world_l3_blocked as _coupled_world_l3_blocked,
)
from background.episode_monotonic import guard_episode  # noqa: E402  (PW4)
from background.notify import notify  # noqa: E402
from background.tmux_relay import is_session_idle  # noqa: E402 (read-only idle check)
from tools import maturity_map_store as map_store  # noqa: E402 (the map's canonical reader)
from tools import simplifications_store as _atom_store  # noqa: E402 (H41 record tenant)

SESSION_NAME = "claude"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "supervisor-log.md"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
USAGE_PAUSE_FILE = PROJECT_DIR / "docs" / "observability" / ".usage_pause.json"

POLL_INTERVAL_SECONDS = 120  # 2 minutes -- polling is explicitly permitted (director, 2026-07-09)

# If the same work-state fingerprint survives this many consecutive granted
# turns (~16 minutes at the default cadence), grants are no longer an
# ordinary retry -- something below the tmux layer is plausibly swallowing
# them. Escalate once per stuck fingerprint rather than retry silently
# forever.
STUCK_THRESHOLD_SECONDS = 3600  # 1 hour wall-clock (2026-07-11 redesign, R3 second
# failure of this mechanism -- director-caught: the old grant-COUNT threshold's
# fingerprint included PRIORITIES.md's mtime and the raw unprocessed-staging list,
# so a full night of zero progress on two genuinely stuck staged files (B2_OPEX_
# TAXONOMY_EXPANSION.md, HARNESS_BEST_PRACTICE_ADOPTION.md) never escalated --
# unrelated real work editing PRIORITIES.md (closing OTHER items) and transient
# run_complete_*.md markers coming and going both reset the "unchanged" counter
# to 1 every time, even though the actual director-relevant blocker never moved.
# Per R3 (two-strike redesign): eliminated the in-memory grant-count fingerprint
# entirely rather than patching it a third time. Replaced with a wall-clock,
# disk-persisted tracker (STUCK_STATE_FILE) keyed narrowly by _stuck_key() to
# exclude exactly those two noise sources, and durable across a daemon restart
# (the old in-memory globals reset silently on any supervisor.py restart, which
# was never itself flagged as a gap until now).
STUCK_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_stuck_state.json"
STUCK_SINCE_FIELDS = ("first_seen_at",)   # PW4 -- the episode start guard_episode protects

# ANTI_LIVELOCK_AND_WIDTH.md (P0, 2026-07-13, director-caught, "the tank just
# reset"): a livelock distinct from STUCK_THRESHOLD_SECONDS above -- that
# mechanism ALARMS after an hour of no progress but never stops re-selecting
# the same atom meanwhile. Real incident: W2_5_life_event_stream was granted
# every ~2min cycle for 61 straight minutes (00:46-01:23 UTC on 2026-07-13)
# before the STUCK escalation even fired, because it was genuinely the sole
# valid BUILD-tier candidate at the time and nothing in the draw itself
# remembers that the previous attempt produced no state change -- this is a
# SPIN, not a blocked atom (W2_5 was already fine: idle, level 2/target 3,
# expert_hour passed -- it needed a director/session-boundary event, not
# another draw). ATOM_STALL_STATE_FILE is the missing scheduler property
# ("backoff"): per-atom consecutive-draws-with-an-unchanged-fingerprint,
# soft-deprioritising (never permanently excluding -- a later fingerprint
# change, e.g. a real FRAME pass, clears it naturally) an atom that keeps
# being re-selected for no new reason. Opt-in via `exclude_stalled=True` on
# the draw functions below (default False preserves every pre-existing
# test's exact behaviour byte-for-byte); `_self_refill_draw()`, the real
# production entry point, is the one caller that opts in.
ATOM_STALL_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".atom_stall_tracker.json"
ATOM_STALL_THRESHOLD = 2  # consecutive same-fingerprint draws before deprioritising

# ANTI_LIVELOCK_AND_WIDTH.md item 2 ("use the width you built"):
# _maturity_map_draw_concurrent() already grants multiple disjoint BUILD
# atoms per cycle (MULTI_ATOM_DRAW.md); the idle-tier DISCOVER/FRAME draw
# never had the equivalent, so overnight width defaulted to 1 even with 24
# eligible atoms in the pool. DISCOVER/FRAME work writes no production
# code, so the file-scope-disjointness check the BUILD-tier concurrent draw
# needs does not apply between idle candidates the same way -- the one real
# shared resource is docs/design/maturity_map.yaml itself (every atom's own
# FRAME pass appends to its own simplifications entry in that one file).
# Each dispatched Agent fork must still read-edit-commit that file inside
# its own tree_lock acquisition (the exact discipline every single-atom
# FRAME pass this session already used) -- stated explicitly in the granted
# message, not assumed understood.
# NARROWED 6 -> 2 (director console, 2026-08-03, budget cut): DISCOVER/FRAME forks write no
# production code, but they carry the same per-turn context cost as a BUILD fork. Width 6 was the
# largest single contributor to the 12-fork raw draw. It stays >1 because this is the always-drawable
# idle lane and it must never be the reason the tick rests (R17).
IDLE_DISCOVER_FRAME_CONCURRENT_WIDTH = 2

# BOUNDED FAN-OUT (director P0, 2026-07-17): a HARD CEILING on the TOTAL concurrent Agent forks a
# single doorbell may instruct, across all three lanes combined. The per-lane widths above are now
# sub-limits under this global ceiling: without it a cycle could draw 1-3 BUILD + 3 SITE + 6
# DISCOVERY = up to ~12 forks ("the wreckage"); bounded to 3 disjoint forks it is recoverable
# ("3 misbehaving forks I can reason about"). The ceiling widens later ONLY by a deliberate
# director decision once bounded-parallel is proven boring -- a dial earned through trust, not before.
#
# NARROWED 3 -> 1 (director console, 2026-08-03, "18% of my weekly budget in under 10 hours ...
# fewer forks, only where genuinely parallel"): fan-out was measured as the dominant token line --
# 54 Agent spawns produced 5,479 of the day's 9,653 API calls and 655M of 1.23B cache-read tokens,
# because every fork turn re-reads a full context copy. One of that day's three Item E forks
# (sim/weather_weighting.py) also died leaving NO artefact on any branch, so the fan-out was buying
# orphan risk as well as tokens. Default is now SERIAL. A second fork is justified only by a
# genuinely disjoint file_scope on work large enough to outweigh a whole extra context stream --
# raise this deliberately for such a draw, do not leave it raised.
MAX_CONCURRENT_FORKS = 1

# THREE_LANES.md (2026-07-13, director-decided, "mechanise the three-lane
# draw so the supervisor draws SITE and DISCOVERY every cycle regardless of
# BUILD's state"): the SITE lane (`site/**`, disjoint by construction) is an
# ungated parallel lane -- it draws site-scoped atoms below target regardless
# of loop_stage. `site/**` shares no path with `sim/**`/`company/**`, so like
# the idle/DISCOVER-FRAME tier it needs no cross-atom disjointness scan; a
# modest width cap keeps a single grant readable while still fanning out.
# NARROWED 3 -> 1 (director console, 2026-08-03, budget cut): the SITE lane stays permanently
# parallel to BUILD (THREE_LANES.md) -- that is untouched. Only its WIDTH drops to serial.
SITE_LANE_CONCURRENT_WIDTH = 1

# R3_WORK_GRANTING_REDESIGN.md requirement 1+4 (2026-07-12, P0, 9th idle
# variant): "nothing to do" must be an impossible terminal state while the
# map has open atoms -- instrument it, count it, alarm it, target zero.
# This tracks the ONE case find_work() can now return no reason at all:
# the self-refill draw itself found no candidate (every atom blocked/
# complete/unreadable), distinct from "didn't draw because something else
# took priority" (that always produces a real reason string). Escalates
# once per TRANSITION into this state (R5: never repeat an unchanged
# status), not on every cycle it persists.
MAP_EXHAUSTED_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_map_exhausted_state.json"
IDLE_TURN_COUNTER_FILE = PROJECT_DIR / "docs" / "observability" / ".supervisor_idle_turn_count.json"
# BUILD-IN-PROGRESS guard (2026-07-19): the self-drawing loop (RC1 fix) draws a below-target
# build-stage atom every cycle -- so an atom being actively advanced by a LIVE Agent fork was
# re-offered every turn (the re-offer thrash the RC1 fix introduced). The orchestrator writes
# {atom_id: dispatch_ts} here on fork dispatch; the BUILD draw excludes fresh-marked ids. FAIL-OPEN
# on every error/staleness (a crashed orchestrator can never permanently starve an atom -- Rule 0).
BUILD_IN_PROGRESS_FILE = PROJECT_DIR / "docs" / "observability" / ".build_in_progress.json"
BUILD_IN_PROGRESS_TTL_SECONDS = 3600

# PUBLISH-GATE WEDGE RUNG 1 (director rulings UNWEDGE_PUBLISH_PRIORITY_ZERO 2026-07-23 +
# WEDGE3_AND_RUNG1_MECHANISE 2026-07-24, SECOND consumed-not-absorbed on the same rule). A publish
# gate that has been failing for >60 min while alerts fire and the tick idles is PRIORITY-ZERO
# drawable work -- it blocks ALL publishing, so it outranks every product/HARDEN lane. These two
# files are WRITTEN by background/process_run_complete.py (record_publish_gate_failure/_success --
# failures trimmed to a 1h window, cleared on the next clean publish). For .last_tested_hash the
# semantics are NOT restated here: process_run_complete.LAST_TESTED_HASH_CONTRACT is the one place
# they are stated (OPS2 criterion 5), because this file is the second of the two call sites that
# used to infer them from each other. The supervisor only READS them (never blocks: local disk
# reads only, per the module doctrine above). Detector: _publish_gate_wedge_active(); wired as TOP rung of
# _self_refill_draw and mirrored in _is_drained_and_gated. R15-proven both ways in
# test_publish_gate_wedge_draw.py.
PUBLISH_GATE_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".publish_gate_state.json"
LAST_TESTED_HASH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_hash"
# THE GREEN'S CLOCK (2026-08-20). `.last_tested_hash` records WHICH commit passed and nothing
# about WHEN, so the supersession check below borrowed git ancestry as its clock -- and since
# OPS3 made the publish queue a STACK (`order = list(reversed(pending))`), ancestry runs
# ANTI-CORRELATED with time across a drain. This sidecar is the clock, written by the same
# single writer on the same rc=0 (contract: process_run_complete.LAST_TESTED_HASH_CONTRACT).
LAST_TESTED_GREEN_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_green.json"
PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS = 60 * 60   # director ruling: a wedge older than 60 min is rung-1
PUBLISH_GATE_WEDGE_MIN_FAILURES = 3            # sustained, not a lone flake (mirrors the H15 alarm threshold)

# THE FAILURE KINDS THAT MEAN "NO TEST WAS JUDGED" -- the publisher writes these itself, one per
# rc, and until 2026-08-27 no reader consumed them. Each is set at a site whose own comment says
# why (`process_run_complete._record_publish_gate_outcome`): rc=77 "NAMED, not left to
# `_classify_gate_failure`, which would read rc=77 as 'test_regression' and send the RUNG-1 draw
# hunting a red test that is not the cause"; rc=78 the same sentence again for the inner clock;
# `deadline_kill` the same again for the two OUTER callers. Three sites, one intent, written down
# three times -- and the draw that the intent is ABOUT read the `reason` string and ignored the
# `kind` beside it, so it opened with "DIAGNOSE the failing test ... FIX the red test" every time.
#
# OBSERVED (2026-08-27, `.publish_gate_state.json`): four consecutive `commit_did_not_land`
# failures with `total_red: 0` and `blocking_tests: []` -- an accusation with no accused -- and a
# RUNG-1 draw sending priority-zero work to run a ~10-minute full suite for a red the record it
# was built from already said did not exist. The real cause was in the publisher's own log tail
# both times: `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS` at 05:28/06:39 and
# `FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED` at 07:13. Neither is a test.
#
# This is the LABEL-WITHOUT-A-READER shape, which is the sibling of the class this file already
# catalogues: a control that cannot fail. Here the control could not even be heard.
WEDGE_KINDS_NO_TEST_JUDGED = frozenset({
    "commit_did_not_land",   # rc=77: the scoped suite was GREEN; the pre-commit hook chain refused
    "gate_timeout",          # rc=78: the publisher's own clock expired before any verdict
    "deadline_kill",         # the CALLER's deadline killed the publisher mid-gate
})

# RUNG 1b -- PERSISTENT OPERATIONAL-LAYER RED (director console P0, 2026-07-25): a daemon-lifecycle
# RED that PERSISTS past paging is priority-zero DRAWABLE work, not an alarm to admire. The overnight
# incident: the operational-layer signal was RED for 13 consecutive hourly checks (a retired daemon's
# orphaned systemd unit failing the anti-drift reconcile, + a pixel-verification capability regression)
# and the ONLY response was an hourly page -- no draw rung ever surfaced "go fix the red daemon-lifecycle
# suite," so the tick rested beside it all night (consumed-not-absorbed, R17/MAKE_IT_STICK). This makes
# it a mechanism: past OPERATIONAL_RED_DRAWABLE_THRESHOLD consecutive reds, the tick DRAWS the fix.
# Signal source: process_run_complete.py's .operational_layer_signal.json ({consecutive_red, last_result}
# -- written by run_operational_layer_signal on each hourly deadman check). Supervisor only READS it.
# Detector: _operational_red_persistent_draw(); wired as RUNG 1b of _self_refill_draw and mirrored in
# _is_drained_and_gated. R15-proven both ways in test_operational_red_persistent_draw.py.
OPERATIONAL_LAYER_SIGNAL_FILE = PROJECT_DIR / "docs" / "observability" / ".operational_layer_signal.json"
OPERATIONAL_RED_DRAWABLE_THRESHOLD = 3   # director: persistent-RED = >3 consecutive checks -> drawable

# RUNG 1d -- PRODUCER STARVATION (2026-08-17). The SAME ruling as RUNG 1, applied to the other end of
# the same pipeline, because it has the SAME consequence and had only HALF the mechanism. Rung 1
# exists because a wedged PUBLISHER means nothing new reaches the live site. A dead PRODUCER means
# nothing new reaches the live site either -- and on 2026-08-17 the sim runner failed NINE consecutive
# times over 70 minutes on one KeyError while the tick worked three other lanes, because a failed run
# wrote a log line, an ntfy and an `agent_status` anomaly, and the draw ladder reads none of those.
#
# Rung 1 could not see it, and that is structural rather than an oversight: it keys on publish
# FAILURES, and a run that dies never attempts a publish, so `failures` stayed EMPTY -- which reads
# identically to a healthy gate. Rung 1b could not see it either: it keys on `pytest -m operational`,
# the daemon-lifecycle/IaC suite, and the daemon was ALIVE the whole time (green, consecutive_green=6,
# at 16:54Z with eight failures behind it). Between them, liveness was watched and OUTPUT was not.
#
# TWO LIMBS, because the two failure modes leave different evidence:
#   * DIAGNOSED -- the runner is alive and its runs fail. Keyed on .sim_producer_state.json (written
#     by sim_runner.record_run_outcome; the write rule is stated in exactly ONE place,
#     sim_runner.PRODUCER_STATE_FILE's contract, and this file only READS it).
#   * UNDIAGNOSED -- the runner is DEAD, wedged, or was never started, so it wrote no counter at all.
#     Keyed on the AGE OF THE NEWEST RUN ARTEFACT, which is written by the child process and not by
#     the runner's own bookkeeping. A state-file-only detector would be silent on exactly the outage
#     it most needs to catch, which is the fail-silent-on-missing shape R15 names.
# The artefact age is also the INDEPENDENCE cross-check for the diagnosed limb (anti-tautology): a run
# output newer than the newest recorded failure means a run has since succeeded and the counter is
# stale, so the rung goes quiet on its own without anyone clearing state by hand.
#
# A DIRECTOR HOLD IS NOT STARVATION: `.sim_runner_hold` present -> silent, because the runner is
# skipping runs on purpose and drawing "go fix the producer" would be a phantom every tick for as
# long as the hold stands (feedback_control_that_can_only_fail_wedges).
# Detector: _producer_starved_active(); wired as RUNG 1d of _self_refill_draw and mirrored in
# _is_drained_and_gated. R15-proven both ways in test_producer_starvation_draw.py.
SIM_PRODUCER_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".sim_producer_state.json"
SIM_RUNNER_HOLD_FLAG = PROJECT_DIR / "docs" / "review_gates" / ".sim_runner_hold"
SIM_RUN_OUTPUT_DIR = PROJECT_DIR / "docs" / "reports"
SIM_RUN_OUTPUT_GLOB = "run_output_*.json"
PRODUCER_STARVED_MIN_FAILURES = 3          # sustained, not a lone flake (mirrors rung 1's bar)
PRODUCER_STARVED_MIN_AGE_SECONDS = 30 * 60  # 5 lost cycles at the p50 cadence, on the DIAGNOSED limb only
# The UNDIAGNOSED limb's threshold is MEASURED, not guessed. It was first written as 45 min on the
# reasoning "a cycle is ~6 min, so 45 is seven lost cycles" -- which was wrong because it sized
# against the RUN and the real cycle is run + publish. Measured over the 2,977 inter-completion gaps
# in sim-runner-log.md: p50 9 min, p90 20, p95 32, p99 67. A 45-min bar sits between p95 and p99 and
# would have fired on 2.79% of gaps -- roughly 31 phantom PRIORITY-ZERO draws a week on a healthy
# pipeline, which is how a rung earns itself a kill flag. 3h is p99.7-ish, and the tail beyond it is
# dominated by genuine outages (today's was 3.0h) rather than slow publishes.
# It is also NOT a fresh arbitrary number: it is `publish_freshness.STALE_AFTER_SECONDS`, this
# project's existing definition of "the live site has gone stale", which is the consequence this
# rung exists to prevent. The two ends of the pipeline now use one staleness clock.
# The sharp instrument is the DIAGNOSED limb at 30 min; this limb is the backstop for a runner that
# writes no counter at all, where hours of latency is the correct trade against phantom draws.
PRODUCER_ARTEFACT_STALE_SECONDS = 3 * 60 * 60

# RUNG 4b -- STALE PUBLISHED GAP MEASUREMENTS (H_GAP_fabric_belief_truth_gap residual (d), 2026-08-10).
# The gap-ledger reconcile is report-only and had no consumer that could ACT on it, so five
# consecutive ticks cleared its drift set by hand. Detector: _stale_gap_row_draw(); wired as RUNG 4b
# of _self_refill_draw and mirrored in _is_drained_and_gated. Design: docs/design/GAP_TOOL_RERUN_OWNERSHIP.md.
_STALE_GAP_SUMMARY_CAP = 4   # how many rows the draw spells out; the overflow is stated, never dropped

# Names that live directly in docs/staging/ but are not real work items.
_IGNORED_STAGING_NAMES = {".gitkeep"}


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    # A TEST PROCESS MAY NOT APPEND TO THE LIVE SUPERVISOR LOG (2026-08-31). `tests/background/`
    # has redirected `LOG_FILE` for a while, but any test OUTSIDE that directory that reaches
    # supervisor code -- `test_canon_drift_check`, `test_discovery_pass_ceiling` -- wrote the real
    # ledger. That log is what a reader consults to find out what the machine drew and when; the
    # whole point of making `docs/observability` a surface is that such a record is evidence.
    #
    # BOTH HALVES: a test process writing a LIVE record, not a test process writing at all, so the
    # directory fixture that redirects `LOG_FILE` to tmp still exercises the real `log()`.
    # PRINTED REGARDLESS -- a test that drives the supervisor should still see its narration.
    from background.live_ledger_guard import in_test_process, is_live_record_path

    if in_test_process() and is_live_record_path(LOG_FILE):
        print(entry)
        return
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def ntfy(msg: str) -> None:
    # Supervisor pages are escalations (deduped by their callers); route through the one contract.
    notify(msg, kind="real_alarm")


def _unprocessed_staging_files() -> list[str]:
    """Top-level files directly in docs/staging/, IN DRAW ORDER -- excludes done/, fyi/,
    responses/, drafts/, reference/, console/ and any other subdirectory automatically
    (iterdir + is_file), and .gitkeep. Covers both staged instruction docs and
    from_rich_*.md files left in place by dispatcher.py (URGENT/NORMAL).

    ORDER, NOT ALPHABET (2026-08-28, director, having read all 49 files himself: "the draw
    takes files in alphabetical filename order, and that is the least of it"). This returned
    `sorted(names)` and `find_work()` renders the whole list into one comma-joined reason, so
    the ORDER of this list is the order of the queue a drawn turn reads. Alphabetical is not a
    queue discipline -- it is an accident of naming, and here the accident was systematic:
    `CLASS_` < `DIRECTOR_` < `WORKER_`, so the six standing registers that can NEVER be
    actioned sorted ahead of the director's guidance written that morning, and the guidance
    sorted ahead of every finding.

    `background/staging_rooms.py` owns the rank and the tie-break (age, not name) and is the
    single place either changes. The fallback keeps the old behaviour if that import ever
    fails: a draw that cannot rank its work must still SEE it, because an unranked queue is a
    nuisance and an invisible one is a stall.
    """
    if not STAGING_DIR.is_dir():
        return []
    try:
        from background import staging_rooms
        return [
            item.name for item in staging_rooms.work_queue(STAGING_DIR)
            if item.name not in _IGNORED_STAGING_NAMES
        ]
    except Exception:
        return sorted(
            p.name for p in STAGING_DIR.iterdir()
            if p.is_file() and p.name not in _IGNORED_STAGING_NAMES
        )


def _is_daemon_marker(name: str) -> bool:
    """True for a routine internal pipeline marker (sim_runner.py/
    process_run_complete.py's own coordination file), never a real
    director/advisor instruction. These self-process on the daemon's own
    cadence with no granted turn required at all -- confirmed directly,
    2026-07-12: dozens of these were picked up and fully processed by
    process_run_complete.py across this entire session with zero agent
    action needed."""
    return (
        (name.startswith("run_complete_") and name.endswith(".md"))
        or (name.startswith("run_pending_") and name.endswith(".md"))
    )


def _real_staged_instructions() -> list[str]:
    """R3_WORK_GRANTING_REDESIGN.md (P0, 9th idle variant, director-caught
    2026-07-12): daemon markers off the instruction channel. The prior
    `_unprocessed_staging_files()` included run_complete_*.md in the SAME
    list `find_work()` used to decide "real work exists on the instruction
    channel" -- so as long as the auto-process daemon's own routine marker
    sat in docs/staging/ (which it does almost continuously, landing every
    ~13min), find_work() returned early with "unprocessed staging --
    run_complete_X.md" and NEVER reached the maturity-map self-refill draw
    below it. The granted session then correctly concluded "that's the
    daemon's own work, nothing for me to do" and ended the turn -- which
    was individually correct (it WASN'T a real instruction) but collectively
    wrong, because "not a real instruction" should have fallen through to
    "so draw the next atom from the map instead," never to "so end the
    turn." This is the root cause named in the redesign order, not a
    coincidence: ~35 open map atoms sat idle while this repeated every
    ~2 minutes, because the doorbell-inspection step never got past a
    marker that was never supposed to gate it in the first place."""
    real = [name for name in _unprocessed_staging_files() if not _is_daemon_marker(name)]
    # DURABLE draw-visibility fix (2026-07-20, the 3-hour silent-stall root cause). in_progress/ is
    # excluded from the scan above (it is for BLOCKED items). But a worker that MIS-PARKS actionable
    # work there (declaring the open sub-item "authorised NOW") makes it invisible to the draw -- the
    # tick then rests over doable director work until a human notices. Surface such mis-parked work as
    # a real instruction so the tick DRAWS it and SELF-RECOVERS. Same canonical detection the deadman
    # [BLOCKED] net uses (background/staging_disposition) -> self-recovery and alarm can never drift.
    # Genuinely-blocked in_progress items (no worker banner / a real wall, not "authorised NOW") are
    # NOT surfaced, so a done-analysis-awaiting-a-director-[ACT] correctly stays parked. Fail-open.
    try:
        from background.staging_disposition import (
            misparked_actionable_in_progress,
            misparked_open_campaign_in_progress,
            selfdrawable_mint_in_progress,
        )
        real.extend("in_progress/" + n for n in misparked_actionable_in_progress(STAGING_DIR / "in_progress"))
        # SECOND net (2026-07-23 NIGHT_ENFORCEMENT addendum, the 20:00Z bug): a director-authored
        # CAMPAIGN doc parked here with a PROCEED-ABLE sub-item carries no worker banner (net above
        # misses it) and is not in CAMPAIGN_REGISTER.yaml (_open_campaign_draw misses it) -> the tick
        # idled beside open campaign work. Surface it too; de-dup if both nets flag the same doc.
        for n in misparked_open_campaign_in_progress(STAGING_DIR / "in_progress", CAMPAIGN_REGISTER_PATH):
            if "in_progress/" + n not in real:
                real.append("in_progress/" + n)
        # THIRD net (2026-07-24, waived-mint self-drawable-next-step blind spot): a director-waived
        # planner mint parked here between sub-steps with a genuinely self-drawable next step carries
        # neither a worker disposition banner nor the word "campaign" -> the two nets above miss it,
        # rungs 1-6 draw nothing, and rung-7 over-mints while the doable step sits parked. Surface it
        # so the draw self-recovers instead of minting a fresh batch. Fail-closed structured marker.
        for n in selfdrawable_mint_in_progress(STAGING_DIR / "in_progress", CAMPAIGN_REGISTER_PATH):
            if "in_progress/" + n not in real:
                real.append("in_progress/" + n)
        # FOURTH net DELETED 2026-08-03 (director console, finishing
        # DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY + NTFY_IS_THE_DIRECTOR): it surfaced any
        # staged doc carrying a `LEDGER: <ACTION> <target>` directive with no matching AUTHENTICATED
        # ledger entry, as "declared-but-unreleased -- needs a director act". That is the withdrawn
        # authority seam itself: the LEDGER:/BUILD_OPEN convention was deleted on 2026-07-29, so this
        # net could only ever re-manufacture work items whose stated resolution was a director
        # signature. It is gone with `parse_ledger_directives` / `report_ruling_release`.
    except Exception:  # a detection error must never break the draw
        pass
    return real


def _urgent_from_rich_pending(staged: list[str]) -> str | None:
    """Name of the first unprocessed from_rich_*.md file dispatcher.py has
    classified URGENT (its <!-- Dispatcher: URGENT --> header, prepended in
    place -- dispatcher.py never moves urgent/normal files out of
    docs/staging/, only fyi goes to staging/fyi/), or None."""
    for name in staged:
        if not (name.startswith("from_rich_") and name.endswith(".md")):
            continue
        try:
            content = (STAGING_DIR / name).read_text(encoding="utf-8")
        except OSError:
            continue
        if "Dispatcher: URGENT" in content:
            return name
    return None


def _pause_active_readonly() -> bool:
    """Same check as session_watchdog.usage_pause_active(), but read-only
    -- never deletes the file. session_watchdog remains the sole owner of
    writing/clearing .usage_pause.json and of the enter/exit NTFY
    transitions (background/session_watchdog.py); the supervisor only ever
    reads it, so the two processes can't race on mutating the same file."""
    if not USAGE_PAUSE_FILE.is_file():
        return False
    try:
        data = json.loads(USAGE_PAUSE_FILE.read_text(encoding="utf-8"))
        resume_at = datetime.fromisoformat(data["resume_at"])
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return False
    if resume_at.tzinfo is None:
        resume_at = resume_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < resume_at


PRIORITIES_PATH = PROJECT_DIR / "PRIORITIES.md"
MATURITY_MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"


def _actionable_backlog_item() -> str | None:
    """FALLBACK ONLY as of 2026-07-10 -- see `_maturity_map_draw()`, now the
    primary self-refill source. Kept only for the case maturity_map.yaml is
    ever missing/unreadable (graceful degradation, same style as the rest of
    this module), so self-refill never regresses to nothing.

    R3 note (2026-07-10, director audit -- "was that gap a session pause, an
    empty-agenda idle, or grants that produced nothing? ... if genuine idle,
    R3 applies to the refill logic"): this heuristic was found to be the
    root cause of a genuine 2h40m idle hole (11:00-14:40) -- it only scanned
    text AFTER the literal "## Backlog" heading for the exact substring "NOT
    YET STARTED", and by that date NONE of the real backlog bullets used
    that exact phrase (they said "NOT STARTED"/"BLOCKED"/"PARTIALLY CLOSED"
    etc.), while every item registered elsewhere in the file (the "# ==="
    sections above the Backlog heading) was structurally invisible to it
    regardless of wording. Same failure class as an earlier incident where a
    phrase accidentally DID match and caused repeated false grants -- two
    strikes on the same fragile prose-substring mechanism. Per R3 (redesign,
    not patch again), the primary mechanism is now the dial-weighted
    maturity-map draw below, which reads structured YAML fields
    (level_current/level_target) instead of matching free-form English
    prose that changes every time someone edits PRIORITIES.md."""
    try:
        text = PRIORITIES_PATH.read_text(encoding="utf-8")
    except OSError:
        return None
    # 2026-07-10, third instance of the same self-referential false-positive
    # class found in one self-audit (nineteenth dial-weighted draw): a raw
    # `text.find("## Backlog")` matches the FIRST occurrence of that
    # substring anywhere in the file -- including inside this very
    # docstring's own prose describing the mechanism, or inside a past
    # commit's write-up quoting the heading name in the file itself (both
    # observed live). A real markdown heading is always anchored at the
    # start of a line; a heading name merely mentioned mid-sentence is not.
    # `re.search(..., re.MULTILINE)` with `^` fixes this at the root rather
    # than continuing to reword prose to dodge the same substring forever.
    match = re.search(r"^## Backlog", text, re.MULTILINE)
    if match is None:
        return None
    idx = match.start()
    for line in text[idx:].split("\n"):
        if "NOT YET STARTED" in line and "BLOCKED" not in line and "REVIEW GATE" not in line:
            # Return a short, stable identifier (first ~80 chars) -- enough
            # for the log/fingerprint to distinguish backlog items from each
            # other without embedding the full line (R7: doorbell, not a
            # directive -- the granted session re-reads PRIORITIES.md itself).
            return line.strip().lstrip("#- ").strip()[:80]
    return None


# ABOLISHED PERMISSION BLOCKS (2026-07-29, DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY items 1-3).
# The ruling abolished `director_build_open` and `director_level_up` AS BLOCK TYPES, and deleted the
# BUILD_OPEN / LEVEL_UP_PROPOSED / ledger-release convention along with "every path that enumerates
# what a director must authorise". Clearing the 13 live instances in the map was a ONE-TIME DATA EDIT;
# a data edit is an exhortation, not a mechanism (MAKE_IT_STICK: "convert policy to mechanism, or
# accept it will evaporate"), and this exact block type is what made 31 atoms with a real level gap
# yield ZERO drawable work -- SILENTLY, because "nothing available" is the correct output from
# corrupted input. So the abolition lives HERE, in the predicate: a `blocked_on` that names a
# director-permission convention no longer suppresses anything, no matter who writes it or when.
_ABOLISHED_PERMISSION_BLOCK_TOKENS = (
    # the machine-readable tokens (2026-07-29 ruling items 1-3)
    "director_build_open", "director_level_up", "build_open", "level_up_proposed",
    "front_open", "gate_clear", "ledger-release", "ledger_release",
    # 2026-08-03: the PROSE forms. The token list alone left 6 parked mints "blocked" whose stated
    # reason was a permission ask spelled out in English -- "a director word authorising live
    # activation", "director ratification of the proposed set", "main-session/director design
    # adjudication". They are the same abolished act wearing a sentence instead of an identifier,
    # and matching only the identifier is how the convention survived its own deletion.
    "director ratification", "director word", "director authoris",
    "director-authoris", "awaiting the director", "awaiting director", "director opens",
    "needs a director", "director sign-off", "director signoff", "console-only", "console only",
    # DELIBERATELY NOT HERE: the bare adjectives "director-reserved" / "director must". They name
    # no ACT, so they cannot be shown to be an abolished one -- and R13 CURRICULUM reservations
    # ("director for any named curriculum-difficulty value", "director-reserved SE_DRAW population
    # activation") describe themselves exactly that way. Curriculum authorship is a question about
    # who writes the simulation's CONTENT, not about permission to build, and it was not part of
    # the 2026-07-29 rip-out. Fail-closed on the ambiguity: the cost of leaving one mint parked is
    # one parked mint; the cost of the other error is silently overriding a reservation the
    # director still holds. Caught by test_planner_rung's own fixture, which used exactly that
    # phrasing for a genuine block.
)


# "main-session/director DESIGN adjudication", "director-side adjudication" -- the word between
# "director" and "adjudication" varies, so this is a pattern rather than another literal.
_ABOLISHED_PERMISSION_BLOCK_PATTERNS = (
    re.compile(r"director[-\s]\w*\s*adjudication", re.I),
    re.compile(r"director[-\s]\w{0,12}\s*(approval|permission|go[- ]ahead)", re.I),
)


def _names_abolished_permission_block(reason: Any) -> bool:
    """True if a `blocked_on` reason is (or cites) one of the abolished director-permission
    conventions. Substring/case-insensitive on purpose: the live instances ranged from the bare token
    `director_level_up` to paragraphs of prose whose operative clause was "the executing act -- a
    per-atom BUILD_OPEN in gate_authorizations.jsonl -- is director-console-only"."""
    text = str(reason or "").lower()
    if any(tok in text for tok in _ABOLISHED_PERMISSION_BLOCK_TOKENS):
        return True
    return any(p.search(text) for p in _ABOLISHED_PERMISSION_BLOCK_PATTERNS)


def _is_externally_blocked(a: dict) -> bool:
    """True if an atom is blocked on a GENUINE external act (an upstream dependency, a real reserved
    wall) and therefore has NO drawable worker work right now -- honest: its gap to target is that
    external act, not remaining worker work. Such an atom is excluded from EVERY draw (BUILD and
    idle-DISCOVER, including the all-stalled fallback), so the loop never treadmills a
    worker-complete-but-blocked atom (H_draw_excludes_external_blocked_atoms). Cleared by removing
    the atom's `blocked_on` field.

    2026-07-29 (ruling items 1-3): a `blocked_on` naming an ABOLISHED director-permission convention
    does NOT block -- there is no such thing as needing a build opened, and levels are recorded, never
    gated. The ONE exception is the re-scoped reserved set (ruling item 5): if the reason describes a
    genuinely reserved real-world consequence -- real money, real people, a public claim in the
    company's name, a real person's safety -- it still blocks, even when it also mentions a permission
    token. That judgement is DELEGATED to `one_way_door.classify_action` (the sole enumeration) rather
    than forked here, so the two can never drift apart."""
    if not (isinstance(a, dict) and a.get("blocked_on")):
        return False
    reason = a.get("blocked_on")
    if not _names_abolished_permission_block(reason):
        return True  # a genuine upstream/dependency block -- untouched by the ruling
    try:
        from background import one_way_door as _owd
        verdict = _owd.classify_action(str(reason))
    except Exception as _owd_err:  # pragma: no cover - conservative on the SAFETY side only
        # An unavailable check is a FAILED check (R15 fail-silent). This branch is reached only for a
        # reason that already names a permission token, so erring toward "still blocked" costs one
        # un-drawn atom and is LOUD, whereas erring toward "drawable" could draw past a real wall.
        log(f"blocked_on reserved-check unavailable, holding {a.get('id')!r} (fail-loud): {_owd_err}")
        return True
    if verdict.is_one_way_door:
        return True  # a reserved real-world consequence, not permission theatre -- still blocks
    log(f"ABOLISHED PERMISSION BLOCK IGNORED (ruling 2026-07-29 items 1-3): atom {a.get('id')!r} "
        f"carries blocked_on={str(reason)[:120]!r}, which names a deleted director-permission "
        "convention and no longer suppresses any draw. Clear the field at next touch.")
    return False


def _delivery_lane_draw() -> str | None:
    """LANE 0 -- the delivery seat's own decisions, drawn as work.

    Director, 2026-08-25: *"orienting became autonomous while the actual building stayed gated on
    my keypress, which is the opposite of what I wanted."* The seat decides every three hours and,
    until this landed, four of its five decisions named work no draw could reach -- `direction.
    focus_weights` biases atoms the draw was already considering, and a focus id that is not an
    atom biases nothing. See `background/delivery_lane.py` for the measurement.

    It is drawn ALONGSIDE the three lanes and never instead of them: the combined message carries
    it first and the lanes below it unchanged. THREE_LANES.md exists because a cascade that
    returned on the first non-empty tier left SITE and DISCOVERY permanently idle, and a new tier
    that pre-empted them would be that regression wearing a delivery seat's clothes.

    Never raises -- see the helper's own docstring.

    `claim=False` BECAUSE THIS CALLER CANNOT DELIVER (2026-08-31). `grant_turn` below performs
    zero pane writes -- this module is the escalation watchdog and the pull-loop Stop hook is the
    transport. Claiming here took the item off the lane roughly a hundred times faster than the
    thing that could hand it to anyone: measured over the whole log, 68 delivery items were
    claimed by this call and **zero** doorbells were ever emitted. See `delivery_lane.draw`."""
    try:
        from background import delivery_lane
    except Exception:  # noqa: BLE001 - a lane that cannot import must not take the draw down
        return None
    return delivery_lane.draw(claim=False)


def _maturity_map_draw(rng: Any = None) -> str | None:
    """Primary self-refill source (2026-07-10, MATURITY_MAP.md Section 6/8:
    "Supervisor self-refill draws work from lanes proportional to dials").
    Reads docs/design/maturity_map.yaml, keeps atoms with a real gap
    (level_current is not None and level_current < level_target -- an
    atom with level_current: null is an honestly-unassessed atom, never
    self-refillable), and makes ONE weighted-random draw where each atom's
    weight is its own `dial_inherited` (the director-ratified per-lane dial
    from MATURITY_MAP.md Section 8) -- lanes with a higher dial are more
    likely to be drawn, matching the equaliser's intent, without the
    supervisor needing to understand what "DISCOVER" vs "BUILD" means (R7:
    the granted session reads the atom's own loop_stage/evidence itself and
    decides what kind of turn that implies).

    Still a cheap, blocking-call-free, no-comprehension read (module
    docstring's own constraint) -- one file read + one weighted choice, no
    network, no git. Returns None (graceful degradation) if the YAML is
    missing, unreadable, malformed, or has no atom with a real gap.

    2026-07-12 (MULTI_ATOM_DRAW.md, P0): now a thin wrapper over
    `_maturity_map_draw_concurrent()` -- that function's own primary-pick
    step is this exact same read+filter+weighted-choice logic (previously
    duplicated here; refactored out once, not re-duplicated, per R3's
    "eliminate the mechanism, not patch it again"). Returns only the
    primary pick's formatted string, so every existing caller/test of this
    function keeps its exact prior behaviour -- byte-for-byte, including
    RNG consumption (the concurrent function's own additional-candidate
    scan is deterministic dial-order sorting, never touches `rng`)."""
    atoms_drawn = _maturity_map_draw_concurrent(rng=rng)
    return _format_atom_draw(atoms_drawn[0]) if atoms_drawn else None


def _atom_level_hold_note(atom: dict) -> str:
    """One atom's `level_hold_note`, wherever it now lives -- the record of what
    PRIOR passes already built on this atom and why the level did not move.

    Same one-seam rule and same inline-wins convention as `_atom_evidence`, and
    it fails the same way if a reader is added that does not route through here.
    Degrades to `""` (never raises) because the draw's own contract is graceful
    degradation on a missing/unreadable store -- a draw that dies because a note
    file is malformed hands out no work at all, which is strictly worse than a
    draw that hands out work without its warning."""
    if "level_hold_note" in atom:
        return str(atom.get("level_hold_note") or "")
    aid = atom.get("id")
    if not aid:
        return ""
    try:
        return str(_atom_store.notes_for_atom(str(aid)).get("level_hold_note") or "")
    except Exception:
        return ""


def _format_atom_draw(atom: dict) -> str:
    """Shared formatting for one drawn atom's summary line -- factored out
    so both the single-atom message (_maturity_map_draw's own return, kept
    unchanged above) and the new multi-atom concurrent message below use
    the identical format.

    The `[LEVEL HELD BEFORE]` suffix is the SAME defect `_atom_name` exists to
    prevent, one field over, and it was live: on 2026-09-03 this line handed a
    bounded BUILD lane `EP13_adapter_carbon_intensity` under its MINT-TIME brief
    -- "Feeds E5_carbon_three_ledger, which today has no real feed behind it" --
    when every path in that atom's `file_scope` was already on disk, ten build
    passes deep, with 30,261 B recorded on WHY 2->3 still did not follow. A fork
    dispatched on that text rebuilds an adapter that exists. The note is rehomed
    out of the map, so seeing it costs a hydration call the bounded lane has no
    reason to make and the draw line gave it no reason to.

    Keyed to the PROPERTY (a hold note exists at all), never to today's answer:
    it lights for any atom whose level was held with a reason on file, and goes
    dark by itself when that note is retired. One atom in 83 carries one today,
    so this is a signal and not decoration -- and if that count ever climbs, the
    suffix is measuring the thing that made it climb."""
    line = (
        f"{atom['id']} -- {_atom_name(atom) or '?'} "
        f"(lane={atom.get('lane', '?')}, dial={atom.get('dial_inherited', '?')}, "
        f"level {atom['level_current']}->{atom['level_target']}, "
        f"loop_stage={atom.get('loop_stage', '?')})"
    )
    hold = _atom_level_hold_note(atom)
    if hold:
        line += (
            f" [LEVEL HELD BEFORE -- {len(hold):,} B of recorded reason why "
            f"{atom['level_current']}->{atom['level_target']} did not follow last time. "
            f"READ IT BEFORE BUILDING: simplifications_store.notes_for_atom"
            f"({str(atom['id'])!r})['level_hold_note']. The brief above is the "
            f"MINT-TIME one and may name as missing work that is already built.]"
        )
    return line


def _atom_file_scope(atom: dict) -> frozenset | None:
    """MULTI_ATOM_DRAW.md (P0, 2026-07-12, director-prompted): the set of
    file paths an atom's own BUILD work touches, per its schema-declared
    `file_scope` list (backfilled for every atom from its own `evidence`
    entries that are real .py paths -- derived from already-real,
    per-atom-curated data, not invented). Returns None if the key is
    genuinely absent (undeclared scope) -- distinct from an explicit empty
    list (a genuinely code-free atom, e.g. read-only research/charter work,
    which safely touches nothing and never conflicts with anything).
    Constraint 3 of the staged instruction: 'do not pretend disjointness
    that does not hold' -- an atom with undeclared scope must fail CLOSED
    (never eligible for a concurrent grant), not be assumed safe."""
    if "file_scope" not in atom:
        return None
    return frozenset(atom.get("file_scope") or [])


def _atoms_file_disjoint(a: dict, b: dict) -> bool:
    """True only if BOTH atoms have a declared file_scope and those scopes
    share no path. Two atoms with both-empty scope are trivially disjoint
    (neither touches any file, per _atom_file_scope's own convention)."""
    scope_a = _atom_file_scope(a)
    scope_b = _atom_file_scope(b)
    if scope_a is None or scope_b is None:
        return False
    return not (scope_a & scope_b)


def _is_compounding(a: dict) -> bool:
    """ONE_FRAMEWORK §7 sub-step 2 (C1/C7): the family-③ tie-break facet that
    MECHANISES COMPOUNDING_WORK_FIRST -- "work that shortens the feedback loop
    goes first" -- which was otherwise prose-only and unread by the draw (a
    decayed rule, MAKE_IT_STICK). A VIEW/DIAL facet exactly like value_stream:
    absent = not-compounding (the default), and its ONLY effect is to ORDER
    otherwise-equal (same-dial) candidates. LAW A: strictly a diagnostic/
    tie-break, NEVER a target or a gate -- the flag never makes an atom
    eligible, never displaces a higher dial, and a sole non-compounding
    candidate is still drawn. Pure/deterministic (reads one boolean field)."""
    return isinstance(a, dict) and a.get("compounding") is True


def _build_in_progress_ids() -> set:
    """Atom ids with a FRESH in-flight-fork marker -- excluded from the BUILD draw so the self-drawing
    loop never re-offers work a LIVE fork already owns. FAIL-OPEN: a missing/unreadable/malformed
    marker, or a stale entry (> BUILD_IN_PROGRESS_TTL_SECONDS), yields NO exclusion -- a broken guard
    must never stall the loop (Rule 0). Only the freshness-valid subset is returned."""
    try:
        import json as _json
        import time as _time
        data = _json.loads(BUILD_IN_PROGRESS_FILE.read_text(encoding="utf-8"))
        now = _time.time()
        return {aid for aid, ts in data.items()
                if isinstance(ts, (int, float)) and (now - ts) < BUILD_IN_PROGRESS_TTL_SECONDS}
    except Exception:
        return set()


def _unmerged_work_paths(root: Path | None = None) -> frozenset:
    """File paths carrying UNMERGED work anywhere in this checkout -- read from GIT REALITY
    (worktrees, unmerged branch tips, uncommitted worktree edits), never from a marker some
    dispatcher had to remember to write.

    WHY (2026-07-30, H10, the third consecutive blind dispatch): the sibling guard
    `_build_in_progress_ids` excludes atoms a live fork owns, but only if the orchestrator
    WROTE `.build_in_progress.json` at dispatch. On 2026-07-30 that file was `{}` while five
    forks held 4,270 uncommitted lines, so the draw re-offered SITE_EH1 twice and produced two
    rival implementations of one atom; a JSON record written to fix the same bug (`.forks_in_
    flight.json`) went unread by the very next tick and predicted its own decay. Both failed for
    ONE reason: they must be VOLUNTARILY MAINTAINED. Git cannot be forgotten -- a branch with
    commits not in main, or a dirty worktree, is a FACT of the repo. This guard reads that fact.

    GUARANTEE: an atom whose declared `file_scope` overlaps a path with unmerged work is not
    offered as fresh BUILD work while a non-collliding candidate exists, so the draw cannot mint
    a rival implementation of work already in flight.

    NOT A WALL (Rule 0): the caller applies this as a SOFT deprioritise -- if every candidate
    collides, the full set is restored rather than reporting false exhaustion. FAIL-OPEN by
    construction: any git failure/timeout returns an EMPTY set (no exclusion), because a broken
    guard must never stall the loop. An empty return is therefore indistinguishable from "no
    unmerged work" -- that is deliberate and is why this deprioritises rather than gates.
    """
    import subprocess
    base = Path(root) if root is not None else PROJECT_DIR
    paths: set = set()

    def _git(args: list, cwd: Path) -> str:
        try:
            r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                               text=True, timeout=20)
            return r.stdout if r.returncode == 0 else ""
        except Exception:
            return ""

    # (a) Committed work on any local branch not contained in main -- `main...b` diffs from the
    #     merge base, i.e. exactly what that branch CHANGED (not what main moved on past).
    #     Resolve the trunk rather than hardcoding "main": on a checkout without it, every
    #     `main..branch` would error and the guard would fail-open COMPLETELY and silently
    #     (an unavailable check is a FAILED check -- R15 fail-silent). Fall back to HEAD.
    default_ref = "main"
    if not _git(["rev-parse", "--verify", "--quiet", default_ref], base).strip():
        default_ref = _git(["symbolic-ref", "--short", "HEAD"], base).strip() or "HEAD"
    for line in _git(["for-each-ref", "--format=%(refname:short)", "refs/heads/"], base).splitlines():
        branch = line.strip()
        if not branch or branch == default_ref:
            continue
        ahead = _git(["rev-list", "--count", f"{default_ref}..{branch}"], base).strip()
        if not ahead.isdigit() or int(ahead) == 0:
            continue
        for p in _git(["diff", "--name-only", f"{default_ref}...{branch}"], base).splitlines():
            if p.strip():
                paths.add(p.strip())

    # (b) UNCOMMITTED edits in every linked worktree -- the state that nearly lost 4,270 lines.
    #     A dirty worktree is in-flight work even with zero commits on its branch.
    for line in _git(["worktree", "list", "--porcelain"], base).splitlines():
        if not line.startswith("worktree "):
            continue
        wt = line.split(" ", 1)[1].strip()
        if not wt or Path(wt) == base:
            continue
        for st in _git(["status", "--porcelain"], Path(wt)).splitlines():
            p = st[3:].strip() if len(st) > 3 else ""
            if " -> " in p:                      # renames: "old -> new"
                p = p.split(" -> ", 1)[1].strip()
            if p:
                paths.add(p)
    return frozenset(paths)


def _atom_collides_with_unmerged(atom: dict, unmerged: frozenset) -> bool:
    """True when this atom's declared file_scope overlaps a path carrying unmerged work.

    Directory-aware in BOTH directions, because file_scope mixes granularities: a scope entry
    may be a directory (`site`, `sim`, `site/company/`) containing a changed file, or a file
    (`site/index.html`) that IS the changed path. Undeclared scope (None) returns False -- this
    guard NEVER newly excludes an atom the existing disjointness rule already fails closed on
    (`_atom_file_scope` -> None is ineligible for a CONCURRENT grant anyway), so it cannot make
    the single-atom draw stricter than it was."""
    scope = _atom_file_scope(atom)
    if not scope or not unmerged:
        return False
    for entry in scope:
        e = str(entry).strip().rstrip("/")
        if not e:
            continue
        for changed in unmerged:
            if changed == e or changed.startswith(e + "/") or e.startswith(changed + "/"):
                return True
    return False


def _prefer_least_stalled(candidates: list, stall_state: dict, lane: str = "BUILD") -> list:
    """The anti-livelock preference, with the case that had become PERMANENT given an answer.

    TIER 1 (unchanged): prefer candidates the stall tracker has not flagged. Whenever any
    un-flagged candidate exists this returns exactly what the old two-line filter returned.

    TIER 2 IS THE FIX. When EVERY candidate is flagged, the old code returned the set
    UNRANKED -- Rule 0's "a guard never zeroes the feasible set", correctly applied and then
    stopping one step too early. Measured on the live tree, 2026-08-19 16:25, this was not the
    rare fallback it reads as; it was every cycle. The BUILD lane's pool reaching the picker
    was SEVEN atoms and all seven were flagged, so an atom with 1307 consecutive unchanged
    draws (`KNIFE3_wall_crossing_paydown`) was weighted identically to one with 6 (`EP6_wall_
    protocol_typing`, promoted to build that morning). The guard whose entire job is to rotate
    away from an atom the draw keeps re-selecting had folded into a no-op, and the tick that
    found this was itself the 44th draw of `H27_payment_belief_gap` -- 43 recorded passes since
    that atom's level last moved.

    HOW IT GOT THERE, because the composition is the lesson and neither guard is at fault
    alone: `_prefer_unmerged_free` (soft, above) had just dropped 22 of the 29 surviving
    candidates for overlapping unmerged worktree work. What it hands on is, by construction,
    the atoms this loop has drawn most -- and those are exactly the ones already flagged. Two
    soft preferences composed into a hard outcome that neither states.

    THE TIER 2 RULE, and it has no dial and no threshold on purpose: draw from the LEAST-
    stalled candidates -- those whose streak equals the minimum, ties kept whole. A minimum
    always exists, so this can never zero the set (Rule 0 holds structurally, not by comment);
    it is an ORDERING, so nothing is permanently excluded -- an atom rejoins the moment every
    rival has been drawn up to its own streak without moving. That is the director's ruling of
    2026-08-19 made mechanical: "make it impossible for the system to run indefinitely on work
    that cannot change its own state." Under tier 2 the only way to reach the stuck atom is for
    nothing else to be moving either, which is the one condition under which drawing it again
    is the honest answer.

    Deliberately NOT a probability weight. An inverse-staleness weight would have made the
    43-pass draw improbable; the ruling asked for impossible, and a weight leaves the tail.
    """
    if not candidates:
        return candidates
    unflagged = [a for a in candidates if not _is_atom_stalled(a.get("id"), stall_state)]
    if unflagged:
        return unflagged
    streaks = {
        a.get("id"): (stall_state.get(a.get("id")) or {}).get("consecutive_unchanged", 0)
        for a in candidates
    }
    floor = min(streaks.values())
    least = [a for a in candidates if streaks.get(a.get("id"), 0) <= floor]
    if len(least) != len(candidates):
        dropped = sorted(
            ((streaks.get(a.get("id"), 0), a.get("id")) for a in candidates if a not in least),
            reverse=True,
        )
        log(
            f"ANTI-LIVELOCK ({lane}): every candidate is stalled, so the draw goes to the "
            f"LEAST-stalled ({floor} unchanged draws) rather than to the whole set -- "
            f"deprioritising {[f'{aid}({n})' for n, aid in dropped]}. Each rejoins when the "
            "rest have been drawn up to its own streak without moving (Rule 0: an ordering, "
            "never an exclusion)."
        )
    return least


def _prefer_unmerged_free(candidates: list, lane: str = "BUILD") -> list:
    """Apply the unmerged-work guard as a SOFT preference to a candidate list.

    Shared by the two CODE-WRITING draws (BUILD and SITE) -- both mint rival implementations if
    they re-offer in-flight work, and the 2026-07-30 double-dispatch spanned both (SITE_EH1 has
    non-site scope entries so it draws in BUILD; SITE1_expert_doors is scope `['site']` so it
    draws in the SITE lane). The DISCOVER/FRAME lane is deliberately NOT filtered: it produces
    docs/thinking, where a second pass on the same atom is not a rival build.

    Rule 0 is structural here, not a comment: an all-colliding set is returned UNCHANGED, so this
    can never zero the feasible set. Fail-open on any error (git unavailable -> no exclusion)."""
    if not candidates:
        return candidates
    try:
        unmerged = _unmerged_work_paths()
        if not unmerged:
            return candidates
        free = [a for a in candidates if not _atom_collides_with_unmerged(a, unmerged)]
        if not free:
            log(f"UNMERGED-WORK guard ({lane}): every candidate overlaps unmerged work -- keeping "
                "full set (Rule 0: a guard never zeroes the feasible set)")
            return candidates
        if len(free) != len(candidates):
            dropped = [a.get("id") for a in candidates if a not in free]
            log(f"UNMERGED-WORK guard ({lane}): deprioritising {dropped} -- file_scope overlaps "
                "unmerged branch/worktree work (a fresh fork would mint a rival implementation)")
        return free
    except Exception as err:  # pragma: no cover - fail-open safety
        log(f"UNMERGED-WORK guard ({lane}) skipped (fail-open, never stalls the draw): {err}")
        return candidates


def _exclude_saturated_from_core_draw(candidates: list[dict]) -> list[dict]:
    """THE PASS CEILING, APPLIED TO THE CORE DRAW (director ruling 2026-08-19: "make it
    impossible for the system to run indefinitely on work that cannot change its own
    state"), at the ceiling appropriate to each candidate's own stage.

    EXTENDED TO `build` ON 2026-08-24, which reverses this function's original central
    decision. Everything below the next paragraph is the 2026-08-19 record and is kept
    because the asymmetry it argues is still live — only the conclusion "and therefore build
    is exempt" is dead. The premise was *"for a saturated build atom, drawing it again IS the
    promote path the ceiling demands"*: a claim about what a build pass does, asserted and
    never measured. Measured on 2026-08-24, `EP6_wall_protocol_typing` had taken **55 build
    passes since its level last moved** and `SITE2_two_sided_wall_exhibit` 18. Fifty-five
    passes is not a promote path being attempted; it is the unbounded run the ruling outlawed
    wearing the one stage label this gate was told to trust, and over the fortnight to that
    date EP6 alone consumed more passes than the whole map recorded level moves. The
    asymmetry survives as a DIAL rather than an exemption: `build` is gated at
    `discovery_pass_ceiling.BUILD_CEILING` (10) against `harden`'s 5, because a build pass
    can move a level and a harden pass cannot. The stage policy lives in the ceiling module;
    this function applies whatever it returns.

    The ceiling landed on 2026-08-19 and reached exactly ONE consumer --
    `_idle_discover_frame_draw`, which feeds only on `idle` atoms. This lane is the other
    place the ceiling has to bite, and it is the place the worst case actually lives:
    `_is_valid_candidate` above excludes only `loop_stage == "idle"`, so this "BUILD lane"
    in fact hands out every non-idle below-target atom -- `harden` included. That is the
    rung that drew `H27_payment_belief_gap` for its FORTY-EIGHTH pass, its forty-third since
    the atom last moved a level, with the ceiling shipped and watching a different lane.

    WHY `harden` AND `build` DIFFER BY 2x rather than being equal (the 2026-08-19 argument,
    which survives its own conclusion). A `build` draw at least ATTEMPTS the level move the
    ceiling is asking for, and the core BUILD rung has nothing beneath it -- narrowing it is
    a Rule-0 hazard in a way closing the discovery tier was not (discovery could close safely
    precisely because BUILD and HARDEN stayed open below it). An atom sitting at `harden` on
    level 2 of 3 for its eighth, thirteenth, forty-third pass is the opposite shape:
    hardening is not a level move and cannot become one, so the passes cannot terminate on
    their own. That asymmetry is this control's subject and it is what sets 10 against 5. Its
    null control is now `test_a_saturated_BUILD_atom_UNDER_the_build_ceiling_survives` --
    without that pin the two ceilings collapse into one and the asymmetry dies silently.

    FAILS OPEN, DELIBERATELY THE OPPOSITE DIRECTION TO `_idle_discover_frame_draw`. That tier
    fails toward an empty lane because its risk is the unbounded run. This one fails toward
    OFFERING, because it is a NARROWING of the primary state-moving lane and its risk is a
    broken ceiling silently starving the core draw. Nothing is lost by failing open here: the
    ruling's teeth are already in the discovery tier, and the unbounded-harden case is a
    quality defect, not a wall. RULE 0 backstop on top: if the exclusion would empty the
    candidate set, the full set is kept -- an empty feasible set is a defect in the dials.

    WHAT THIS DOES NOT COVER, named rather than left for the next reader to discover. LANE 2
    (SITE, `_site_lane_draw_concurrent`) selects below-target atoms REGARDLESS of loop_stage,
    so a `site/**`-scoped atom over its ceiling is still drawable there. This was structural
    rather than live on 2026-08-19 and is LIVE as of the build extension:
    `SITE1_expert_doors` and `SITE2_two_sided_wall_exhibit` are both `site/`-scoped and both
    over a ceiling. Left open deliberately and with a reason that is now stronger, not
    weaker -- SITE is the lane whose output a reader actually sees, it is the one place the
    fortnight's measurement says the project was UNDER-spending, and narrowing it would cut
    exactly the wrong thing. The ceiling's job here is to stop unbounded investigation, not
    to stop pages being finished."""
    if not candidates:
        return candidates
    try:
        from tools.discovery_pass_ceiling import core_draw_exclusions

        over_ceiling = core_draw_exclusions()
    except Exception as exc:  # noqa: BLE001 - see the fail-open paragraph above
        log(
            "CORE pass-ceiling gate skipped (fail-open, never narrows the core draw on a "
            f"broken ceiling): {exc}"
        )
        return candidates
    kept = [a for a in candidates if a.get("id") not in over_ceiling]
    if not kept:
        log(
            f"CORE pass-ceiling gate: all {len(candidates)} core candidate(s) are over their "
            "stage's pass ceiling -- keeping the full set (Rule 0: a guard never zeroes the "
            "feasible set). Every one of them is now a decision: land the level, retarget "
            "it, or close it."
        )
        return candidates
    if len(kept) != len(candidates):
        dropped = [a.get("id") for a in candidates if a not in kept]
        log(
            f"CORE pass-ceiling gate: excluding {dropped} from the core draw -- each has run "
            "past its stage's ceiling of passes since its level last moved (5 harden, 10 "
            "build; director ruling 2026-08-19, extended to build 2026-08-24 on the measured "
            "55-pass EP6 case). `python3 -m tools.discovery_pass_ceiling` lists the decision "
            "each one now is."
        )
    return kept


def _maturity_map_draw_concurrent(rng: Any = None, exclude_stalled: bool = False) -> list[dict]:
    """MULTI_ATOM_DRAW.md (P0, 2026-07-12, director-prompted, completes R3
    "be wider" as a property of the granting model, not a standing
    exhortation): "The supervisor draws ONE atom per turn. One atom = one
    lane = serial BY CONSTRUCTION... width must be a property of the
    granting model." Extends _maturity_map_draw's own dial-weighted primary
    pick with as many ADDITIONAL candidates as are PROVABLY file-scope-
    disjoint from every atom already selected -- checked via each atom's own
    declared file_scope, never assumed (constraint 1/3 of the staged
    instruction). Greedy in dial-weight order among the remainder, so the
    next most important disjoint atom is preferred when several exist.

    Deliberately duplicates (rather than refactors out of)
    _maturity_map_draw's own candidate-filtering logic
    (_dependencies_met/_is_valid_candidate) -- that function's 12+ existing
    tests directly verify its exact behaviour byte-for-byte; this keeps that
    guarantee intact rather than risking a regression from a shared-helper
    refactor. Returns a list of chosen atom dicts (possibly just one, when
    no disjoint additional candidate exists -- the old one-atom-per-cycle
    behaviour, preserved as the natural special case of this one), or an
    empty list if the map has no candidate at all.

    ANTI_LIVELOCK_AND_WIDTH.md (P0, 2026-07-13): `exclude_stalled` defaults
    to False so every pre-existing caller/test keeps this function's exact
    prior behaviour byte-for-byte. When True (the real production path,
    via `_self_refill_draw()`), soft-deprioritises any candidate the
    ATOM_STALL_STATE_FILE tracker already flagged stalled -- preferring a
    genuinely different atom when one exists, falling back to the full
    (including stalled) candidate set only when NO non-stalled candidate
    remains (a real hard block should still surface via STUCK_THRESHOLD_
    SECONDS's own hourly escalation, not silently report false exhaustion
    here). Records this cycle's primary pick into the tracker afterward,
    so the NEXT cycle's check reflects this draw."""
    try:
        import yaml
    except ImportError:
        return []
    try:
        atoms = map_store.load_atoms(MATURITY_MAP_PATH)
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(atoms, list):
        return []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}

    def _dependencies_met(atom: dict) -> bool:
        # Level-MATCHED dependency gate (DIRECTOR_DIRECTIVE_KEEP_BUILDING, 2026-07-21).
        # A dependency is satisfied when it is EITHER at its own target (the original
        # rule, preserved -- a "done" primitive) OR already at least as advanced as the
        # level THIS atom is trying to reach (level_current + 1). The old rule required
        # every dependency to sit at ITS OWN target, which serialised the whole chain on
        # the last atom's target and propagated any wall on an upstream TARGET (e.g.
        # W1_4's coupled-triad L3 wall) down every descendant: W1_5, which only wants
        # L1->L2 and is fully served by W1_4-at-L2, read as blocked and the loop rested
        # with genuinely-drawable work present. This OR form is strictly more permissive
        # than the old rule (it only ADDS a met-condition -- every dep the old rule
        # counted met, dep_level>=dep_target, is still met), so it can never newly block
        # a currently-drawable atom. It also mirrors the coupled-triad gate, which is
        # itself next-step-matched (level_current + 1 -- background/coupled_triad.py).
        my_level = atom.get("level_current")
        required = (my_level + 1) if isinstance(my_level, int) else None
        for dep_id in atom.get("depends_on") or []:
            dep = by_id.get(dep_id)
            if dep is None:
                return False
            if dep.get("loop_stage") == "idle":
                continue
            dep_level = dep.get("level_current")
            dep_target = dep.get("level_target")
            at_own_target = (
                isinstance(dep_level, int)
                and isinstance(dep_target, int)
                and dep_level >= dep_target
            )
            advanced_enough = (
                isinstance(dep_level, int) and required is not None and dep_level >= required
            )
            if not (at_own_target or advanced_enough):
                return False
        return True

    def _is_valid_candidate(a: dict) -> bool:
        if not isinstance(a, dict):
            return False
        level_current, level_target = a.get("level_current"), a.get("level_target")
        if level_current is None or level_target is None:
            return False
        dial = a.get("dial_inherited", 1)
        try:
            has_gap = level_current < level_target
            _ = max(1, dial)
        except TypeError:
            return False
        if not has_gap:
            return False
        if a.get("loop_stage") == "idle":
            return False
        return _dependencies_met(a)

    candidates = [a for a in atoms if _is_valid_candidate(a)]
    # Externally-blocked atoms (blocked_on a director act) are never drawable work -- drop them
    # before any fallback, so the only-blocked case returns empty rather than re-handing done work.
    candidates = [a for a in candidates if not _is_externally_blocked(a)]
    # BUILD-IN-PROGRESS guard (2026-07-19): drop atoms a LIVE fork already owns, so the self-drawing
    # loop doesn't re-offer in-flight work (the re-offer thrash the RC1 self-drawing fix introduced).
    # Fail-open (_build_in_progress_ids returns {} on any error/staleness -- never stalls the loop).
    _bip = _build_in_progress_ids()
    if _bip:
        candidates = [a for a in candidates if a.get("id") not in _bip]
    # DELETED 2026-08-03 (director console, finishing DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY
    # item 3): the SELF-GOVERNANCE SCOPE MODEL draw filter intersected BUILD candidates with
    # `authorized_build` (an OPEN front, or a per-atom BUILD_OPEN in the ledger). It existed SOLELY to
    # decide whether the director had permitted a BUILD, which is the exact thing item 3 abolishes --
    # "if a code path exists solely to decide whether the director has permitted something, delete it".
    # The 2026-07-29 sweep only deleted its enable-flag (`.fronts_enforcement_enabled`), leaving the
    # path dormant-but-armed: any recreation of that file would have silently re-gated the BUILD draw.
    # Dormant permission machinery is still permission machinery, so the call site is now GONE, not
    # flagged off -- and with its last caller removed, `background/fronts_reconciler.py` and
    # `background/fronts.yaml` (the declaration of "which regions the loop may BUILD in without
    # asking") were deleted outright rather than left as dead scaffolding for the convention to
    # regrow on. There is no front to be on, and no BUILD to be opened.
    # COUPLED_TRIAD binding rule 1 (director P1, COUPLED_TRIAD_DESIGN.md 4.1):
    # a WORLD atom stepping toward L3 is excluded from the BUILD draw until its
    # coupled company twin exists (>=L1) AND the pair's belief-vs-truth gap is
    # measured in the gap ledger. BUILD-lane only -- LANE 2 (SITE) and LANE 3
    # (DISCOVER/FRAME) are untouched, so a capped world atom still draws
    # thinking work elsewhere. Fails closed (missing/empty ledger -> blocked).
    if candidates:
        _gap_ledger = _coupled_load_gap_ledger()
        _kept = []
        for _a in candidates:
            _blocked, _reason = _coupled_world_l3_blocked(_a, atoms, _gap_ledger)
            if _blocked:
                log(f"COUPLED_TRIAD gate: excluding {_a.get('id')} from BUILD draw -- {_reason}")
            else:
                _kept.append(_a)
        candidates = _kept
    # PASS CEILING on the core draw (director ruling 2026-08-19; extended from harden-only to
    # build 2026-08-24, at a 2x ceiling -- see the helper). Placed HERE, with the hard
    # exclusions (coupled-triad above) rather than with the soft preferences below, on the lesson
    # commit d7d36b46a records: two SOFT guards composed into a no-op and the atom with 1,307
    # unchanged draws was weighted like the one promoted that morning. A prefer-then-fall-back
    # shape would have done nothing here for the same reason. Its own Rule-0 backstop lives
    # inside the helper, so a hard exclusion still cannot zero the lane.
    # COST, measured rather than assumed: `saturated_ids()` reads the ledger and every atom's
    # store, 2.1s per call on the live tree, and the discovery tier already pays it once per
    # cycle -- so this roughly doubles that to ~4s. Left UNCACHED deliberately: a cache keyed
    # on anything but the current stores is how a record starts outrunning the code it
    # describes, and 2s against a draw that already shells out to git for the unmerged-work
    # guard below is not where this loop's time goes.
    candidates = _exclude_saturated_from_core_draw(candidates)
    # UNMERGED-WORK guard (2026-07-30, H10 -- the fix the `.forks_in_flight.json` record itself
    # named after predicting its own decay). Prefer candidates whose file_scope does NOT overlap
    # work already sitting unmerged in a branch/worktree, so the draw cannot hand out an atom a
    # prior fork already built and thereby mint a RIVAL implementation (it did exactly that twice
    # for SITE_EH1 inside one hour). Backstops `_build_in_progress_ids` above, which fail-opens
    # whenever the dispatcher never wrote its marker -- the exact state that let this happen.
    # SOFT, per Rule 0: if EVERY candidate collides the full set is kept rather than reporting
    # false exhaustion. Mirrors `exclude_stalled`'s own prefer-then-fall-back shape.
    candidates = _prefer_unmerged_free(candidates, lane="BUILD")
    # ANTI-LIVELOCK, tiered since 2026-08-19: prefer un-flagged candidates, and when EVERY
    # candidate is flagged draw from the least-stalled rather than from the whole set. On this
    # lane the all-flagged case was not a fallback, it was the standing state -- see
    # `_prefer_least_stalled` for the measurement.
    if exclude_stalled and candidates:
        candidates = _prefer_least_stalled(candidates, _load_atom_stall_state(), lane="BUILD")
    if not candidates:
        return []
    weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]
    # THE DELIVERY SEAT STEERS HERE, and only here (docs/design/THE_DELIVERY_SEAT.md §5).
    # A WEIGHT, NEVER A GATE: `focus_weights` multiplies these dials and can never return
    # zero or change who is a candidate, so a wrong or stale direction record makes this
    # loop slower to reach something and never unable to. That is Rule 0 in one line -- an
    # empty feasible set is a defect in the dials, and a filter is a dial that can empty it.
    # Missing/malformed/expired direction returns these weights untouched, byte-for-byte.
    weights = _direction.focus_weights(candidates, weights)
    picker = rng or random
    primary = picker.choices(candidates, weights=weights, k=1)[0]
    # COMPOUNDING tie-break (ONE_FRAMEWORK §7 sub-step 2, C1/C7): AFTER the
    # dial-weighting has picked the primary, break a TIE among same-dial
    # candidates toward a compounding:true atom -- work that shortens the
    # feedback loop goes first (COMPOUNDING_WORK_FIRST). This is a TIE-BREAK,
    # never a gate (LAW A / R15): only candidates whose dial EQUALS the drawn
    # primary's are considered, so a higher-dial non-compounding atom is never
    # displaced (dial still dominates); the candidate set is untouched, so a
    # sole non-compounding candidate is STILL drawn. Deterministic: among
    # same-dial compounding equals it keeps the existing critical-path/order
    # tie-break (map order -- `candidates` preserves the yaml order the draw
    # already reads). Runs before the stall record so the tracker sees the
    # atom actually drawn.
    if not _is_compounding(primary):
        _primary_dial = primary.get("dial_inherited", 1)
        _same_dial_compounding = [
            c for c in candidates
            if c is not primary
            and c.get("dial_inherited", 1) == _primary_dial
            and _is_compounding(c)
        ]
        if _same_dial_compounding:
            primary = _same_dial_compounding[0]
    if exclude_stalled:
        stalled_now, count = _record_atom_draw_and_check_stall(primary["id"], _atom_fingerprint(primary))
        if count == ATOM_STALL_THRESHOLD:
            log(
                f"ANTI-LIVELOCK: {primary['id']} deprioritised after {count} "
                "consecutive draws with no state change -- a future draw "
                "prefers a different candidate until this atom's own state changes."
            )

    selected = [primary]
    remaining = [c for c in candidates if c is not primary]
    # Dial dominates (primary key, unchanged); COMPOUNDING is the secondary
    # tie-break among equal-dial additional picks (0 = compounding first, 1 =
    # not), then map order via the stable sort -- so ordering is identical to
    # before whenever no candidate is compounding (all rank 1). ONE_FRAMEWORK
    # §7 sub-step 2 (C1/C7): a tie-break on ORDER only, never a filter.
    remaining.sort(key=lambda a: (-(a.get("dial_inherited") or 1), 0 if _is_compounding(a) else 1))
    for atom in remaining:
        if all(_atoms_file_disjoint(atom, s) for s in selected):
            selected.append(atom)
    return selected


def _normalize_evidence_list(value: Any) -> list:
    """Coerce an atom's `evidence` field to a list of entries, tolerating the
    scalar-string hand-edit form (`evidence: docs/design/frame/X_FRAME.md`
    instead of a one-item list).

    WHY THIS EXISTS (2026-07-28 HARDEN red-team, R15 FAIL-SILENT -- the SAME
    hand-edit-typo class the 07-27 override-parse pass reasoned about, reaching a
    DIFFERENT consumer). `_atom_has_frame_doc` iterated `atom.get("evidence") or
    []` directly: a LIST iterates entries, but a scalar STRING iterates its
    CHARACTERS ('d','o','c',...), none of which start with `docs/design/`, so the
    function silently returned False -- reading an atom that carries a real,
    complete FRAME doc (pointed at by a mistyped scalar) as UN-saturated and
    RE-HANDING it to the idle draw every cycle: the exact treadmill (this atom's
    own DIAL defect, occurrences 1-5) it exists to stop, reached through a scalar
    typo. A scalar evidence pointer is semantically identical to a one-item list,
    so normalising it is strictly correct (no starve risk: a scalar pointing at a
    NON-FRAME path still reads un-saturated -> offered, unchanged). A genuinely
    unexpected type (dict/int/...) is LOGGED (surfaced, never swallowed) and read
    as no-evidence -- fail-loud on garbage, matching `_coerce_frame_saturated_
    override`. Sibling `_has_test_evidence` (line ~1499) already rejects a
    non-list evidence via `isinstance(ev, list)`; this normaliser is the
    fix-not-just-reject form, so the valid scalar-pointer case is handled rather
    than merely tolerated. R15 mutation-tested both directions."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    log(
        "H23 _atom_has_frame_doc: `evidence` is neither a list nor a string "
        f"({value!r}) -- treating as no evidence. A mistyped evidence field must "
        "not silently vanish (R15 FAIL-SILENT); fix the map value."
    )
    return []


def _atom_name(atom: dict) -> str:
    """One atom's BRIEF, wherever it now lives (the 2026-08-14 `name` drain).

    Same one-seam rule as `_atom_evidence` below, and the same failure it exists to
    prevent -- except that this one is what the DRAW SHOWS. The rehome's stated
    precondition was *hydrate, then move*: a drawn atom whose brief silently read
    `?` would strip the draw line of the only text saying what the work IS, and,
    for `KNIFE3_wall_crossing_paydown`, of a live DO-NOT-REDRAW-FROM-ZERO warning
    that carries the running cut counts. Nothing raises when that goes missing, so
    the hydration is wired here rather than left to each caller."""
    return _atom_store.atom_name(atom)


def _atom_evidence(atom: dict) -> Any:
    """One atom's `evidence` value, wherever it now lives (H41).

    `evidence` was rehomed out of the map into the per-atom record store
    (docs/design/simplifications/<id>.yaml, `map_records:`) because it was the bulk
    of the spine ratchet's refill. Every reader of the field routes through here so
    the rehome has ONE seam rather than one per call site -- and so a reader added
    later cannot silently read a field that is no longer inline and conclude the
    atom has no evidence. That failure would be invisible: `_atom_has_frame_doc`
    returning False for a FRAMED atom re-hands it to the idle draw forever (the
    exact treadmill `_normalize_evidence_list`'s docstring documents, reached by a
    different route), and `_has_harden_surface` returning False silently removes
    at-target atoms from the HARDEN lane.

    Inline WINS over stored, matching `simplifications_store.hydrate`: during a
    partial migration the inline value is the one the spine is actually showing."""
    if "evidence" in atom:
        return atom["evidence"]
    aid = atom.get("id")
    if not aid:
        return None
    return _atom_store.records_for_atom(str(aid)).get("evidence")


def _atom_has_frame_doc(atom: dict) -> bool:
    """True iff the atom already carries its OWN complete FRAME doc on disk:
    an `evidence` entry anywhere under `docs/design/` whose FILENAME contains
    `FRAME` (matching the `<id>_FRAME.md` / `<SLUG>_FRAME.md` convention) AND
    that resolves to an existing file under `PROJECT_DIR`. The filename `FRAME`
    requirement is what distinguishes a per-atom FRAME (`W1_10_FRAME.md`,
    `H20_PARALLEL_MAINTENANCE_LANE_FRAME.md`) from a SHARED survey listed as
    evidence (`LANE3_H17_BUILD_GATE_SURVEY_...md`, no `FRAME` in its filename)
    and from an earlier-stage DISCOVER doc (`..._DISCOVER.md`, likewise no
    `FRAME`) -- neither is the atom's FRAME-stage output, so an atom carrying
    only one of those still has genuine FRAME work left and must NOT read as
    saturated. Paths are repo-relative (as stored in `evidence`), resolved
    against `PROJECT_DIR` so the check is real filesystem state, never an
    assumed string match (R7: verify against disk). The resolved path must be a
    regular file with non-whitespace content -- an empty/stub file or a directory
    is not an honest FRAME output (see the inline note at the existence check).

    H23 residual-false-negative fix (2026-07-16, note[4]): the prefix was
    originally `docs/design/frame/`, which mis-read the ~11 atoms that carry a
    COMPLETE per-atom FRAME doc directly under `docs/design/` (the older,
    non-canonical path -- `docs/design/W1_10_FRAME.md`, `H20_..._FRAME.md`,
    `H21_..._FRAME.md`, ...) as un-saturated, re-handing them to the idle draw
    indefinitely -- the exact treadmill this atom exists to stop, just
    relocated. Broadening the prefix to `docs/design/` (any depth) is computed
    (cannot decay, MAKE_IT_STICK) and stays conservative: the `FRAME`-in-
    filename gate still excludes shared surveys and DISCOVER-stage docs, so a
    genuinely-unframed atom is never falsely marked saturated (proven by the
    mutation tests, both directions). Safe on the live map because every
    non-canonical `*_FRAME.md` is owned by exactly ONE atom (no shared
    FRAME-named doc outside `frame/`). A per-atom FRAME doc whose FILENAME
    carries neither `FRAME` nor the id/slug (e.g. G4's
    `UNIFIED_FAILURE_REGISTER.md`) is out of reach of any filename heuristic
    without risking a false-positive on a partial design doc -- for those the
    documented `frame_saturated: true` explicit override (a map-writer step)
    remains the intended escape."""
    if not isinstance(atom, dict):
        return False
    for e in _normalize_evidence_list(_atom_evidence(atom)):
        s = str(e)
        if not s.startswith("docs/design/"):
            continue
        # `FRAME` must appear as a delimited TOKEN in the filename (the
        # `<id>_FRAME.md` / `<SLUG>_FRAME.md` convention), NOT as a substring
        # embedded in a larger word. A bare `"FRAME" in name` substring test
        # (2026-07-25 HARDEN red-team finding) mis-reads `ONE_FRAMEWORK.md`,
        # `TIMEFRAME.md`, `..._REFRAMED_...md` as a per-atom FRAME doc and thus
        # falsely marks the atom FRAME-saturated -- STARVING a genuinely-unframed
        # atom from the idle DISCOVER/FRAME draw. That is the fail-toward-starve
        # wrong-side failure: the exact idle-hole this atom exists to prevent,
        # re-introduced via a substring collision (ONE_FRAMEWORK.md is a real,
        # heavily-cited repo file -- latent today, one `evidence:` edit from live).
        # Split on non-alphanumerics and require the whole token `FRAME`; every
        # legitimate `_FRAME`/`_FRAME_`-convention doc still matches (verified
        # against the live map), embedded-word collisions no longer do. R15
        # mutation-tested both directions (test_frame_saturation_draw_marker.py).
        if "FRAME" not in re.split(r"[^A-Z0-9]+", Path(s).name.upper()):
            continue
        # Existence alone is NOT enough: a 0-byte / whitespace-only stub (an
        # interrupted turn's placeholder, or a stray `touch`) is NOT an honest
        # FRAME-stage output, and an evidence entry that resolves to a DIRECTORY
        # (e.g. `docs/design/frame/`) is not a doc at all. Counting either as a
        # complete FRAME doc marks the atom saturated and STARVES it from the
        # idle FRAME draw -- the fail-toward-starve wrong-side failure this atom
        # exists to prevent (R15 FAIL-OPEN-on-empty: a check that passes on an
        # empty/malformed input is worse than none). Require a regular file with
        # non-whitespace content. A read error reads as "no honest FRAME output"
        # (fail-toward-offer = the safe side, consistent with this control's
        # whole philosophy). Live tree: every real FRAME doc is >5KB, so this
        # tightening changes behaviour only for genuine stubs (2026-07-27 HARDEN
        # red-team; R15 mutation-tested both directions).
        p = PROJECT_DIR / s
        try:
            if p.is_file() and p.read_text(encoding="utf-8", errors="ignore").strip():
                return True
        except OSError:
            continue
    return False


# YAML/hand-edit truthy/falsey token forms a map-writer might type for the
# `frame_saturated` override instead of a bare unquoted `true`/`false`. PyYAML
# already coerces an UNQUOTED true/false/yes/no/on/off to a Python bool, but a
# QUOTED value (`"false"`) or a bare integer (0/1) stays a non-bool -- and this
# atom's own history cites "a quoted level_current string" as a real hand-edit
# typo class, so the same class reaches the override here.
_FRAME_SATURATED_TRUE_TOKENS = {"true", "yes", "on", "1"}
_FRAME_SATURATED_FALSE_TOKENS = {"false", "no", "off", "0"}


def _coerce_frame_saturated_override(value: Any) -> bool | None:
    """Interpret an explicit `frame_saturated` map override robustly, returning
    True/False for a recognised override or None for "no honest override, fall
    through to the intrinsic has-FRAME-doc check".

    WHY THIS EXISTS (2026-07-27 HARDEN red-team, R15 FAIL-SILENT -- the SIBLING
    half of the class every prior H23 pass hardened: they all worked on
    `_atom_has_frame_doc`, none red-teamed the override-parse itself).
    `_is_frame_saturated` previously honoured the override ONLY when it was a
    genuine Python `bool` (`isinstance(explicit, bool)`), else silently fell
    through to the intrinsic check. But the override is the R11 escape hatch (a
    SAFETY-CONTROL override, and four live atoms rely on it), and BOTH escape
    directions FAIL SILENTLY on a non-bool value:
      * force-OFFER (`frame_saturated: false`) typed as a QUOTED string
        `"false"` (or `no`/`off`/`0`) -> not a bool -> intrinsic returns True on
        a FRAME-doc'd atom -> the atom STAYS saturated and is STARVED from the
        idle draw: the fail-toward-starve wrong-side failure, the exact idle-hole
        this atom exists to prevent, reached through the escape.
      * force-SKIP (`frame_saturated: true`) typed as `"true"` -> not a bool ->
        intrinsic returns False when the FRAME doc has a non-canonical filename
        (the whole reason the override is used -- the four live
        `frame_saturated: true` atoms carry DISCOVER-named docs) -> the atom
        reads un-saturated and is RE-HANDED every tick: the treadmill.
    Silently swallowing a mistyped safety-control override is R15 FAIL-SILENT --
    an override the checker cannot read is treated as ABSENT (an unavailable
    check is a failed check). Fix: accept the natural YAML/hand-edit token forms
    so the documented escape actually works when typed the way a map-writer would
    typo it, and LOG (surface, never swallow) a genuinely unrecognised value
    before falling through to intrinsic -- fail-loud on garbage, not
    silent-ignore. Falling through rather than crashing keeps one atom's typo
    from aborting the whole draw, matching the per-atom validation isolation
    elsewhere in this module. R15 mutation-tested both directions
    (test_frame_saturation_draw_marker.py)."""
    if value is None:
        return None
    if isinstance(value, bool):  # the canonical, PyYAML-parsed unquoted form
        return value
    if isinstance(value, int):  # bare 0/1 (bool is a subclass, handled above)
        if value in (0, 1):
            return bool(value)
    elif isinstance(value, str):
        token = value.strip().lower()
        if token in _FRAME_SATURATED_TRUE_TOKENS:
            return True
        if token in _FRAME_SATURATED_FALSE_TOKENS:
            return False
    log(
        "H23 _is_frame_saturated: unrecognised `frame_saturated` override "
        f"{value!r} (expected a bool or a true/false token) -- ignoring it and "
        "falling through to the intrinsic has-FRAME-doc check. Fix the map "
        "value: a mistyped safety-control override must not silently vanish "
        "(R15 FAIL-SILENT)."
    )
    return None


def _is_frame_saturated(atom: dict) -> bool:
    """H23_frame_saturation_draw_marker: an idle atom is FRAME-saturated when
    no honest FRAME-stage output remains -- it already carries its own complete
    FRAME doc, so the ONLY remaining path to `level_target` is BUILT code the
    epoch gate defers (an idle atom's gap is BUILD-gated by definition). Such an
    atom must NOT be re-handed to the idle DISCOVER/FRAME draw: re-emitting a
    duplicate FRAME is the exact churn SELF_INTERRUPT_DISCIPLINE + R12 forbid,
    and the 3x-then-recursive re-hand (occurrences 1-5, this atom's own history)
    is the DIAL defect it fixes.

    Saturation is computed INTRINSICALLY from map+disk state (has-FRAME-doc),
    deliberately NOT a marker a turn must remember to set -- MAKE_IT_STICK: a
    setter that a turn can forget decays (this finding evaporated as prose four
    times); a computed check cannot. An explicit boolean `frame_saturated` on
    the atom OVERRIDES the intrinsic check in BOTH directions -- `true`
    force-marks an atom whose FRAME doc is under a non-standard name, `false`
    force-offers a saturated atom that genuinely needs a FRAME revision. The
    override is the R11 escape so the state is a cache, never a permanent hold
    (no orphan transition). Auto-clear on BUILD-gate-open needs no code here:
    when the gate opens the atom's `loop_stage` flips off `idle`, it leaves the
    idle candidate pool entirely (the existing `loop_stage != "idle"` filter),
    and re-enters via the BUILD draw -- exactly 're-offer only when its
    BUILD-gate opens'."""
    if not isinstance(atom, dict):
        return False
    override = _coerce_frame_saturated_override(atom.get("frame_saturated"))
    if override is not None:
        return override
    return _atom_has_frame_doc(atom)


def _idle_discover_frame_draw(rng: Any = None) -> dict | None:
    """EPOCH_GATING_AND_ATOM_AUTHORSHIP.md (P0, 2026-07-12, director-prompted
    "why can't it think of its own work for future epochs"): Rule 1 --
    epoch gating (`loop_stage: idle`) gates BUILD only, never DISCOVER/
    FRAME/research/red-team/charter/design work. `_maturity_map_draw_
    concurrent()` correctly excludes every idle atom from BUILD candidacy
    (that exclusion is untouched, and its own 12+ tests keep passing
    unmodified) -- but until this function, an idle atom was excluded from
    EVERY draw, so a map with a real BUILD gap always found one, while a
    map with only idle atoms left silently reported "map_exhausted" even
    though all 31 parked atoms had real DISCOVER/FRAME work available. This
    is the second, separate tier `_self_refill_draw()` falls to: same
    dial-weighted-random convention as the BUILD draw (deliberately
    duplicated rather than shared, matching `_maturity_map_draw_
    concurrent()`'s own stated preference for keeping existing tested
    behaviour byte-for-byte rather than risking a shared-helper regression),
    but selecting only from `loop_stage == "idle"` atoms with a real gap
    (level_current < level_target) -- an idle atom already at/above target
    has no work left, discover/frame or otherwise. Returns None (graceful
    degradation) if the YAML is missing, unreadable, malformed, or has no
    idle atom with a real gap -- same failure contract as the BUILD draw."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        atoms = map_store.load_atoms(MATURITY_MAP_PATH)
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(atoms, list):
        return None

    def _is_valid_idle_candidate(a: dict) -> bool:
        if not isinstance(a, dict):
            return False
        if a.get("loop_stage") != "idle":
            return False
        level_current, level_target = a.get("level_current"), a.get("level_target")
        if level_current is None or level_target is None:
            return False
        dial = a.get("dial_inherited", 1)
        try:
            has_gap = level_current < level_target
            _ = max(1, dial)
        except TypeError:
            return False
        return has_gap

    candidates = [a for a in atoms if _is_valid_idle_candidate(a)]
    candidates = [a for a in candidates if not _is_externally_blocked(a)]  # never draw director-blocked atoms
    # H23: hard-skip FRAME-saturated atoms (no fallback -- unlike the stall
    # soft-deprioritise, which falls back). Preferring an un-saturated idle
    # atom is the whole point; if EVERY idle atom is saturated this is a TRUE
    # empty FRAME feasible set (Rule 0), not a spin -- return None so the turn
    # reports idle-with-reason rather than re-handing a saturated atom.
    non_saturated = [a for a in candidates if not _is_frame_saturated(a)]
    if candidates and not non_saturated:
        log(
            "IDLE DISCOVER/FRAME draw: all "
            f"{len(candidates)} idle atom(s) are FRAME-saturated (own FRAME doc "
            "present, gap BUILD-gated) -- no honest FRAME-stage work remains; "
            "returning empty (H23_frame_saturation_draw_marker) rather than "
            "re-handing a saturated atom."
        )
    candidates = non_saturated


    # THE PASS CEILING (director ruling, 2026-08-19): "make it impossible for the system to
    # run indefinitely on work that cannot change its own state." An atom that has taken
    # CEILING DISCOVER/FRAME passes with no level move since leaves this draw. It is not
    # punished and discovery is not made expensive -- the ruling forbids that lever -- the
    # LANE IS MADE FINITE. Its next honest answer is promote-to-build or close, and both
    # change state; investigating again is the one answer no longer available.
    #
    # Measured cause: 98 commits on 2026-08-18 produced ZERO recorded level moves, against 3
    # commits per move on 08-09. Eighty atoms sit below target and idle, and this tier feeds
    # on exactly that set, so the lane was inexhaustible BY CONSTRUCTION.
    #
    # FAIL-CLOSED TOWARD STOPPING, and deliberately the OPPOSITE direction to
    # `_is_frame_saturated` above. That one fails toward offering, because its risk is
    # starving real work. This one fails toward an empty tier, because its risk is the
    # indefinite run the ruling exists to end -- and it is safe to fail that way: BUILD and
    # HARDEN work stay drawable, only this tier closes, so the loop is pushed toward the work
    # that moves state rather than halted.
    try:
        from tools.discovery_pass_ceiling import saturated_ids

        over_ceiling = saturated_ids()
    except Exception as exc:  # noqa: BLE001 - an unreadable ceiling must not silently reopen the lane
        log(
            "IDLE DISCOVER/FRAME draw: the pass ceiling could not be computed "
            f"({exc}) -- returning empty rather than reopening an unbounded discovery lane "
            "(director ruling 2026-08-19). BUILD and HARDEN work are unaffected."
        )
        return None
    under_ceiling = [a for a in candidates if a.get("id") not in over_ceiling]
    if candidates and not under_ceiling:
        log(
            f"IDLE DISCOVER/FRAME draw: all {len(candidates)} idle atom(s) are OVER THE PASS "
            "CEILING -- each has been investigated repeatedly without its level moving. This "
            "is a TRUE empty discovery set, not a spin: every one of them is now a decision "
            "(promote to build, or close). `python3 -m tools.discovery_pass_ceiling` lists "
            "them."
        )
    candidates = under_ceiling

    if not candidates:
        return None
    weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]
    # THE DELIVERY SEAT STEERS HERE, and only here (docs/design/THE_DELIVERY_SEAT.md §5).
    # A WEIGHT, NEVER A GATE: `focus_weights` multiplies these dials and can never return
    # zero or change who is a candidate, so a wrong or stale direction record makes this
    # loop slower to reach something and never unable to. That is Rule 0 in one line -- an
    # empty feasible set is a defect in the dials, and a filter is a dial that can empty it.
    # Missing/malformed/expired direction returns these weights untouched, byte-for-byte.
    weights = _direction.focus_weights(candidates, weights)
    picker = rng or random
    return picker.choices(candidates, weights=weights, k=1)[0]


def _idle_discover_frame_draw_concurrent(
    rng: Any = None,
    width: int = IDLE_DISCOVER_FRAME_CONCURRENT_WIDTH,
    exclude_stalled: bool = False,
    exclude_ids: frozenset[str] | set[str] = frozenset(),
) -> list[dict]:
    """ANTI_LIVELOCK_AND_WIDTH.md item 2 (P0, 2026-07-13, director-prompted,
    "use the width you built"): `_maturity_map_draw_concurrent()` already
    grants multiple disjoint BUILD atoms per cycle; `_idle_discover_frame_
    draw()` above never had the equivalent, so overnight the idle/DISCOVER-
    FRAME tier defaulted to width=1 even with 24 eligible atoms sitting in
    the pool. DISCOVER/FRAME work writes no production code, so the file-
    scope-disjointness check the BUILD-tier concurrent draw needs does not
    apply between idle candidates the same way -- the one real shared
    resource is docs/design/maturity_map.yaml itself (every atom's own
    FRAME pass appends to its own simplifications entry in that one file);
    each dispatched Agent fork must still read-edit-commit that file inside
    its own tree_lock acquisition, the exact discipline every single-atom
    FRAME pass this session already used -- named explicitly in the granted
    message `_self_refill_draw()` builds from this function's output, not
    assumed understood.

    Deliberately simpler than the BUILD-tier concurrent draw: picks the
    dial-weighted primary (same convention as every other draw in this
    module), then fills up to `width` DISTINCT additional slots in dial-
    weight order among the remainder -- no disjointness scan needed, since
    idle/DISCOVER-FRAME candidates need no such check between each other.
    Returns a list of 0..width chosen atom dicts, never duplicating the
    primary pick (dispatching the identical atom to two forks would be
    pure waste). `exclude_stalled` mirrors `_maturity_map_draw_concurrent`'s
    own opt-in parameter exactly (default False preserves every other
    caller's behaviour; `_self_refill_draw()` opts in)."""
    try:
        import yaml
    except ImportError:
        return []
    try:
        atoms = map_store.load_atoms(MATURITY_MAP_PATH)
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(atoms, list):
        return []

    def _is_valid_idle_candidate(a: dict) -> bool:
        if not isinstance(a, dict):
            return False
        if a.get("loop_stage") != "idle":
            return False
        if a.get("id") in exclude_ids:
            return False
        level_current, level_target = a.get("level_current"), a.get("level_target")
        if level_current is None or level_target is None:
            return False
        dial = a.get("dial_inherited", 1)
        try:
            has_gap = level_current < level_target
            _ = max(1, dial)
        except TypeError:
            return False
        return has_gap

    candidates = [a for a in atoms if _is_valid_idle_candidate(a)]
    candidates = [a for a in candidates if not _is_externally_blocked(a)]  # never draw director-blocked atoms
    # H23: hard-skip FRAME-saturated atoms BEFORE the stall soft-filter (this
    # skip has no fallback -- all-saturated is a true empty FRAME feasible set,
    # returned as [], not a re-hand). This is the production path that was
    # re-handing the same 6+ FRAME-saturated BUILD-gated atoms 5x in one day.
    non_saturated = [a for a in candidates if not _is_frame_saturated(a)]
    if candidates and not non_saturated:
        log(
            "IDLE DISCOVER/FRAME concurrent draw: all "
            f"{len(candidates)} idle atom(s) are FRAME-saturated -- no honest "
            "FRAME-stage work remains; returning [] "
            "(H23_frame_saturation_draw_marker) rather than re-handing."
        )
    candidates = non_saturated
    if exclude_stalled and candidates:
        candidates = _prefer_least_stalled(candidates, _load_atom_stall_state(), lane="DISCOVERY")
    if not candidates:
        return []

    weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]
    # THE DELIVERY SEAT STEERS HERE, and only here (docs/design/THE_DELIVERY_SEAT.md §5).
    # A WEIGHT, NEVER A GATE: `focus_weights` multiplies these dials and can never return
    # zero or change who is a candidate, so a wrong or stale direction record makes this
    # loop slower to reach something and never unable to. That is Rule 0 in one line -- an
    # empty feasible set is a defect in the dials, and a filter is a dial that can empty it.
    # Missing/malformed/expired direction returns these weights untouched, byte-for-byte.
    weights = _direction.focus_weights(candidates, weights)
    picker = rng or random
    primary = picker.choices(candidates, weights=weights, k=1)[0]
    if exclude_stalled:
        stalled_now, count = _record_atom_draw_and_check_stall(primary["id"], _atom_fingerprint(primary))
        if count == ATOM_STALL_THRESHOLD:
            log(
                f"ANTI-LIVELOCK: {primary['id']} deprioritised after {count} "
                "consecutive draws with no state change -- a future draw "
                "prefers a different candidate until this atom's own state changes."
            )

    selected = [primary]
    remaining = [c for c in candidates if c is not primary]
    remaining.sort(key=lambda a: -(a.get("dial_inherited") or 1))
    for atom in remaining:
        if len(selected) >= width:
            break
        selected.append(atom)
    return selected


def _is_site_atom(a: dict) -> bool:
    """THREE_LANES.md Lane 2: an atom belongs to the SITE lane if ANY of its
    declared `file_scope` entries is exactly `site` or begins `site/` (e.g.
    `SITE1_expert_doors` -> ["site"], `BRAND1_identity_system` -> ["site",
    ...]). `site/**` is disjoint by construction from `sim/**`/`company/**`,
    so this lane is ungated and runs alongside BUILD permanently. An atom
    with no `file_scope` (undeclared) is never a SITE atom -- membership is a
    positive property, never assumed."""
    if not isinstance(a, dict):
        return False
    for path in a.get("file_scope") or []:
        p = str(path)
        if p == "site" or p.startswith("site/"):
            return True
    return False


def _site_lane_draw_concurrent(
    rng: Any = None,
    width: int = SITE_LANE_CONCURRENT_WIDTH,
    exclude_stalled: bool = False,
    exclude_ids: frozenset[str] | set[str] = frozenset(),
) -> list[dict]:
    """THREE_LANES.md (2026-07-13, director-decided, "the supervisor draws
    SITE and DISCOVERY every cycle regardless of BUILD's state"): the SITE
    lane draw. Selects `site/**`-scoped atoms (per `_is_site_atom`) that have
    a real gap (`level_current < level_target`), drawn for BUILD **regardless
    of loop_stage** -- SITE is an ungated parallel lane, so an idle/parked
    site atom (e.g. `SITE1_expert_doors`) is still drawable here even though
    epoch gating parks it for the sim/company BUILD lane. `site/**` is
    disjoint by construction from every other lane, so -- exactly like the
    idle/DISCOVER-FRAME tier -- this needs no cross-atom file-scope
    disjointness scan: it picks the dial-weighted primary (the module's
    standard convention), then fills up to `width` distinct additional slots
    in dial-weight order.

    `exclude_ids` de-dups across lanes: `_self_refill_draw()` passes the ids
    already drawn by the BUILD lane (BUILD wins over SITE for a given atom),
    so a site-scoped atom that is itself an active BUILD candidate is granted
    once, in the BUILD lane. `exclude_stalled` mirrors the other draws'
    opt-in anti-livelock backoff exactly (default False preserves every
    non-production caller). Same graceful-degradation contract as the other
    draws: returns [] on a missing/unreadable/malformed map or no candidate."""
    try:
        import yaml
    except ImportError:
        return []
    try:
        atoms = map_store.load_atoms(MATURITY_MAP_PATH)
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(atoms, list):
        return []

    def _is_valid_site_candidate(a: dict) -> bool:
        if not _is_site_atom(a):
            return False
        if a.get("id") in exclude_ids:
            return False
        if _is_externally_blocked(a):
            # Genuinely blocked on an EXTERNAL act (an upstream dependency, a reserved
            # real-world consequence): a fork would find nothing to build. Note this is
            # now a much smaller set -- since 2026-08-03 `_is_externally_blocked` ignores
            # every abolished permission convention, so "awaiting ratification" is no
            # longer a hold here or anywhere. Ungated means ignore loop_stage/epoch
            # parking -- NOT ignore a real blocked_on. Matches every other lane.
            return False
        level_current, level_target = a.get("level_current"), a.get("level_target")
        if level_current is None or level_target is None:
            return False
        dial = a.get("dial_inherited", 1)
        try:
            has_gap = level_current < level_target
            _ = max(1, dial)
        except TypeError:
            return False
        return has_gap

    candidates = [a for a in atoms if _is_valid_site_candidate(a)]
    # BUILD-IN-PROGRESS guard on the SITE lane too (2026-07-20): the guard in _self_refill_draw
    # covers only the BUILD lane, so the ungated SITE lane could still re-offer an atom a live fork
    # already owns (the same class as the site lane's earlier blocked_on / level-gap-only misses).
    # Drop site atoms a live fork owns so a focused SITE build (e.g. the P2 operational-window
    # rebuild of SITE1) isn't raced by the self-drawing scheduled loop. Fail-open
    # (_build_in_progress_ids returns {} on error/staleness -> never stalls the lane).
    _bip_site = _build_in_progress_ids()
    if _bip_site:
        candidates = [a for a in candidates if a.get("id") not in _bip_site]
    # UNMERGED-WORK guard on the SITE lane (2026-07-30, H10): same reason as the BUILD lane above --
    # the marker guard fail-opens when the dispatcher never wrote it, and SITE1_expert_doors (scope
    # ['site']) was re-drawn on this lane while two rival SITE_EH1 builds already sat unmerged in
    # worktrees touching site/. Soft preference; an all-colliding set is kept intact (Rule 0).
    candidates = _prefer_unmerged_free(candidates, lane="SITE")
    if exclude_stalled and candidates:
        candidates = _prefer_least_stalled(candidates, _load_atom_stall_state(), lane="SITE")
    if not candidates:
        return []

    weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]
    # THE DELIVERY SEAT STEERS HERE, and only here (docs/design/THE_DELIVERY_SEAT.md §5).
    # A WEIGHT, NEVER A GATE: `focus_weights` multiplies these dials and can never return
    # zero or change who is a candidate, so a wrong or stale direction record makes this
    # loop slower to reach something and never unable to. That is Rule 0 in one line -- an
    # empty feasible set is a defect in the dials, and a filter is a dial that can empty it.
    # Missing/malformed/expired direction returns these weights untouched, byte-for-byte.
    weights = _direction.focus_weights(candidates, weights)
    picker = rng or random
    primary = picker.choices(candidates, weights=weights, k=1)[0]
    if exclude_stalled:
        stalled_now, count = _record_atom_draw_and_check_stall(primary["id"], _atom_fingerprint(primary))
        if count == ATOM_STALL_THRESHOLD:
            log(
                f"ANTI-LIVELOCK: {primary['id']} deprioritised after {count} "
                "consecutive draws with no state change -- a future draw "
                "prefers a different candidate until this atom's own state changes."
            )

    selected = [primary]
    remaining = [c for c in candidates if c is not primary]
    remaining.sort(key=lambda a: -(a.get("dial_inherited") or 1))
    for atom in remaining:
        if len(selected) >= width:
            break
        selected.append(atom)
    return selected


def _blocking_roots(atom_id: str, by_id: dict, _seen: set | None = None) -> set[str]:
    """Transitive dependency walk (ADVISOR_ANSWER_CANNOT_DRAW.md, P0,
    2026-07-12): finds the REAL blocking root(s) beneath `atom_id` -- the
    genuinely-unbuilt, non-idle, actively-in-scope atom(s) that must move
    before `atom_id` can. Mirrors `_dependencies_met`'s parked-vs-unbuilt
    rule exactly: a `loop_stage: idle` (parked) link is never a blocker and
    is not descended into (its own state is a deliberate deferral, not
    something the diagnostic should chase further); an atom already at/above
    its own target is not a blocker either. A missing dependency id is
    reported as its own root (`missing:<id>`) since that is a real map
    defect, not something buildable. `_seen` guards against a cyclic
    `depends_on` graph (not expected, but a diagnostic must not hang on one)."""
    seen = _seen if _seen is not None else set()
    if atom_id in seen:
        return set()
    seen.add(atom_id)
    atom = by_id.get(atom_id)
    if atom is None:
        return {f"missing:{atom_id}"}
    lc, lt = atom.get("level_current"), atom.get("level_target")
    has_gap = lc is not None and lt is not None and lc < lt
    if not has_gap:
        return set()
    if atom.get("loop_stage") == "idle":
        return set()
    roots: set[str] = set()
    for dep_id in atom.get("depends_on") or []:
        roots |= _blocking_roots(dep_id, by_id, seen)
    return roots or {atom_id}


def diagnose_map_blocked_set(atoms: list | None = None) -> str:
    """Requirement 2/4 of ADVISOR_ANSWER_CANNOT_DRAW.md: on a genuine
    CANNOT-draw, report the full blocked-set and its blocking roots across
    ALL atoms with a real gap -- not just "no candidate" -- so the next
    escalation diagnoses itself instead of requiring a human to re-derive
    this by hand from the raw YAML (exactly what happened this time).
    Read-only, reuses the same YAML `_maturity_map_draw()` reads; safe to
    call whenever map_exhausted is True (rare by construction -- only fires
    on the transition, see check_map_exhausted_escalation)."""
    if atoms is None:
        try:
            atoms = map_store.load_atoms(MATURITY_MAP_PATH)
        except Exception:
            return "maturity map unreadable -- cannot diagnose the blocked-set"
    if not isinstance(atoms, list):
        return "maturity map malformed (not a list) -- cannot diagnose the blocked-set"
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}

    blocked = []
    for a in atoms:
        if not isinstance(a, dict) or "id" not in a:
            continue
        lc, lt = a.get("level_current"), a.get("level_target")
        has_gap = lc is not None and lt is not None and lc < lt
        if not has_gap or a.get("loop_stage") == "idle":
            continue
        roots: set[str] = set()
        for dep_id in a.get("depends_on") or []:
            roots |= _blocking_roots(dep_id, by_id)
        if roots:
            blocked.append((a["id"], sorted(roots)))

    idle_count = sum(1 for a in atoms if isinstance(a, dict) and a.get("loop_stage") == "idle")
    idle_below_target = sum(
        1 for a in atoms if isinstance(a, dict) and a.get("loop_stage") == "idle"
        and a.get("level_current") is not None and a.get("level_target") is not None
        and a.get("level_current") < a.get("level_target")
    )
    l0_count = sum(1 for a in atoms if isinstance(a, dict) and a.get("level_current") == 0)
    # HELD-FRONTIER annotation (DIRECTOR_DIRECTIVE_KEEP_BUILDING, 2026-07-21):
    # a build-stage atom whose deps are MET but that is still not drawable
    # (walled by the coupled-triad L3 gate, held on a director act, off an open
    # front, or owned by a live fork) is INVISIBLE to the dependency-root scan
    # above -- `_blocking_roots` on its deps returns empty, so it lands in
    # neither `blocked` nor the candidate pool. That invisibility is exactly why
    # the overnight rest READ as "drawable work ignored" when it was a correct
    # hold at a named wall. Surface those held-frontier atoms with the ACTUAL
    # gate holding each, so the rest diagnoses itself. Computed once, appended in
    # BOTH the no-dependency-blockage and the blocked branches.
    held = {
        aid: reason
        for aid, reason in build_atom_hold_reasons(atoms).items()
        if reason != "DRAWABLE" and not reason.startswith("blocked_by_dependency")
    }
    held_note = ""
    if held:
        held_note = " | held frontier (deps met, gated -- NOT a draw bug): " + "; ".join(
            f"{aid} -> {reason}" for aid, reason in sorted(held.items())
        )
    if not blocked:
        # ADVISOR_STEER_TWIN_READONLY.md (2026-07-12, real confusion this
        # caused): the OLD wording ("the map has genuinely no drawable gap
        # left") is true only about the NON-IDLE/BUILD candidate set this
        # function itself diagnoses -- but read on its own, it sounds like
        # "nothing to draw at all", which is false whenever idle atoms below
        # target exist (they are drawable for DISCOVER/FRAME via
        # `_idle_discover_frame_draw()`, a completely separate tier this
        # function says nothing about). Made that explicit rather than
        # implicit, so this message can never again be misread as "nothing
        # to do" when idle_below_target > 0.
        idle_note = (
            f" {idle_below_target} idle atom(s) remain below target and ARE drawable "
            "for DISCOVER/FRAME work (a separate tier, see _idle_discover_frame_draw) "
            "-- this message is scoped to BUILD-candidate blockage only, not \"nothing to do\"."
            if idle_below_target else ""
        )
        return (
            f"{len(atoms)} atoms, {idle_count} idle, {l0_count} at L0 -- no non-idle atom "
            "is blocked by an unmet dependency; no NON-IDLE BUILD candidate is blocked "
            "(every non-idle atom is either at target or already a valid candidate)."
            f"{idle_note}{held_note}"
        )
    lines = [f"{atom_id} <- blocked by {', '.join(roots)}" for atom_id, roots in blocked]
    return (
        f"{len(atoms)} atoms, {idle_count} idle, {l0_count} at L0, "
        f"{len(blocked)} non-idle atom(s) genuinely blocked: " + "; ".join(lines) + held_note
    )


def build_atom_hold_reasons(atoms: list | None = None) -> dict:
    """{atom_id: reason} for every BUILD-stage atom with a real level gap --
    the auditable answer to "why is the loop at rest / why is this atom not
    building?" (DIRECTOR_DIRECTIVE_KEEP_BUILDING, 2026-07-21; the overnight-rest
    incident: every build-stage atom was correctly held, but no diagnostic
    could SHOW it, so a correct hold read as a draw bug).

    Each reason is either ``"DRAWABLE"`` (the atom passes every candidate filter
    the concurrent BUILD draw applies, so it IS in the draw pool and MUST NOT be
    left undrawn while the loop rests) or the FIRST gate that removes it, in the
    same order the draw applies them:
      * ``blocked_by_dependency: <roots>`` -- an upstream dep is below target;
      * ``director_gate: blocked_on=<x>`` -- held on an external/director act;
      * ``fork_in_flight`` -- a live fork already owns it;
      * ``off_open_front`` -- fronts enforcement excludes it (off an open front);
      * ``coupled_triad_l3_wall: <why>`` -- the L3 step needs a mature company twin.

    R15 (a control that can FIRE): the failure signal is a ``DRAWABLE`` atom that
    coexists with the loop being at rest -- exactly the directive's incident,
    "a drawable in-front atom left undrawn at rest". A caller that knows the loop
    is drained (`_is_drained_and_gated()` / an empty concurrent draw) asserts this
    map yields NO ``DRAWABLE`` atom; a genuinely-buildable atom silently skipped by
    the loop makes that assertion fail. Pure read, fail-open (a broken sub-check
    never invents a hold that would mask a real drawable atom -- on error the more
    permissive branch is taken, so a masked hold can only ever turn a held atom
    into a louder ``DRAWABLE``, never the reverse)."""
    if atoms is None:
        try:
            atoms = map_store.load_atoms(MATURITY_MAP_PATH)
        except Exception:
            return {}
    if not isinstance(atoms, list):
        return {}
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and "id" in a}

    # Mirrors _maturity_map_draw_concurrent's own _dependencies_met exactly
    # (deliberately duplicated, same rationale as that function's inline copy:
    # keep this classifier in lockstep with the draw's real filter order) --
    # including the 2026-07-21 level-MATCHED rule: a dependency is met when it is
    # at its own target OR already at the level this atom is trying to reach
    # (level_current + 1). See the draw copy for the full rationale.
    def _deps_met(atom: dict) -> bool:
        my_level = atom.get("level_current")
        required = (my_level + 1) if isinstance(my_level, int) else None
        for dep_id in atom.get("depends_on") or []:
            dep = by_id.get(dep_id)
            if dep is None:
                return False
            if dep.get("loop_stage") == "idle":
                continue
            dl, dt_ = dep.get("level_current"), dep.get("level_target")
            at_own_target = isinstance(dl, int) and isinstance(dt_, int) and dl >= dt_
            advanced_enough = isinstance(dl, int) and required is not None and dl >= required
            if not (at_own_target or advanced_enough):
                return False
        return True

    try:
        bip = _build_in_progress_ids()
    except Exception:
        bip = set()
    # No fronts/BUILD_OPEN permission intersection here either (deleted 2026-08-03 with the draw-side
    # filter above): this function explains WHY an atom is not drawable, and "the director has not
    # opened its front" is no longer a reason that exists.
    gap_ledger = _coupled_load_gap_ledger()

    reasons: dict = {}
    for a in atoms:
        if not isinstance(a, dict) or "id" not in a:
            continue
        lc, lt = a.get("level_current"), a.get("level_target")
        has_gap = lc is not None and lt is not None and lc < lt
        if not has_gap or a.get("loop_stage") != "build":
            continue
        aid = a["id"]
        if not _deps_met(a):
            roots: set[str] = set()
            for dep_id in a.get("depends_on") or []:
                roots |= _blocking_roots(dep_id, by_id)
            reasons[aid] = "blocked_by_dependency: " + ", ".join(sorted(roots))
            continue
        if _is_externally_blocked(a):
            reasons[aid] = f"director_gate: blocked_on={a.get('blocked_on')}"
            continue
        if aid in bip:
            reasons[aid] = "fork_in_flight"
            continue
        try:
            blocked, why = _coupled_world_l3_blocked(a, atoms, gap_ledger)
        except Exception:
            blocked, why = False, ""
        if blocked:
            reasons[aid] = f"coupled_triad_l3_wall: {why}"
            continue
        # Passes every candidate filter the draw applies -> genuinely drawable.
        reasons[aid] = "DRAWABLE"
    return reasons


def _harden_at_target(a: dict) -> bool:
    """At its target and shipped (level_current == level_target, target > 0) -- the
    base eligibility for a Rule-0 HARDEN draw."""
    if not isinstance(a, dict):
        return False
    lc, lt = a.get("level_current"), a.get("level_target")
    if lc is None or lt is None:
        return False
    try:
        return lc == lt and lt > 0
    except TypeError:
        return False


def _has_harden_surface(a: dict) -> bool:
    """True if an at-target atom has something a HARDEN pass can actually re-verify /
    mutation-re-test / red-team -- a built control with a runnable test (G10 harden-
    ability gate, twin-approved 2026-07-17 via route_blocking_decision
    'G10_harden_ability_gate_build'). STRUCTURAL ONLY per the twin's R12 note (never
    keyed on bug-history/outcome, which would make harden-ability a target): a
    level < 2 atom is FRAME-only (its 'done' is merely being framed -- no control or
    exit-test exists yet), and an atom whose evidence points at no runnable test has
    no control to re-verify this pass. SOFT: callers only PREFER these, never zero the
    set on them (Rule 0)."""
    if not isinstance(a, dict):
        return False
    lc = a.get("level_current")
    try:
        if lc is None or lc < 2:
            return False
    except TypeError:
        return False
    ev = _atom_evidence(a)
    if not isinstance(ev, list):
        return False
    for e in ev:
        s = str(e)
        if s.startswith("tests/") or "/tests/" in s:
            return True
        # A test FILE: a WORD-BOUNDARIED `test`/`tests` token (delimited by start,
        # `/` or `_`) in a `.py` path -- NOT a loose `"test" in s` substring, which
        # false-qualifies non-test .py files whose NAME merely contains the letters
        # (`latest.py`, `contest_pricing.py`, `protest_handler.py` all matched the old
        # check) -- the same word-boundary false-positive class as the 2026-07-27
        # E2E->E2 commit-parser fix. Safe-side either way (this is a SOFT preference,
        # never a gate), but a tighter predicate spends idle HARDEN effort truer.
        if s.endswith(".py") and re.search(r"(?:^|[/_])tests?(?:[_./]|$)", s.lower()):
            return True
    return False


def _harden_criticality_weight(a: dict) -> int:
    """STRUCTURAL red-team-value bias (twin R12 note: NEVER outcome/bug-history):
    harness / safety-control lanes (lane starts with 'H') carry more value per HARDEN
    pass -- a control defect is costlier and structurally more likely than a settled
    domain data-shape drifting -- so they are PREFERENTIALLY drawn. Non-zero for every
    lane: a soft dial that biases, never excludes (Rule 0 / R12 diagnostic-not-target)."""
    return 3 if str(a.get("lane", "")).startswith("H") else 1


# =============================================================================
# AT-TARGET HARDEN COOLDOWN / ROTATION MEMORY (2026-07-25, H1 HARDEN red-team)
# -----------------------------------------------------------------------------
# The 2026-07-18 red-team of H1_supervisor_turn_granting FOUND (and registered,
# not-then-fixed, as a SELF_INTERRUPT queue item) that the Rule-0 at-target
# HARDEN draw had NO cooldown / rotation memory: it re-offered the SAME at-target
# atoms within a few turns, so an agent CHURNED re-verifying atoms it had verified
# minutes ago -- the at-target analogue of the idle-DISCOVER treadmill H23 fixed.
# Unlike FRAME (which genuinely SATURATES -> a flag), HARDEN is legitimately
# PERIODIC (a shipped atom CAN regress), so the correct damper is a COOLDOWN, not
# a saturation flag: skip an atom HARDEN-verified within the last
# HARDEN_COOLDOWN_HOURS so the draw ROTATES through the at-target pool -- BUT
# re-offer it immediately iff its content CHANGED since that pass (a commit touched
# its file_scope -> it may have regressed -> re-verify now). The real-world twin is
# exactly on point: an ops on-call auto-page rotation does not re-page the same
# still-open alert every two minutes; it rotates and backs off, but a CHANGED alert
# re-pages at once.
#
# SOFT DIAL (Rule 0): if the cooldown would EMPTY the pool (every at-target atom
# recently hardened + unchanged), fall back to the full pool -- a genuinely-empty
# HARDEN draw would false-trip the LOOP_BROKEN transport alarm and violate 'the
# to-do list is never empty'. INDEPENDENCE (R15): keyed on each atom's ACTUAL
# serialised content (`sha`) AND its file_scope source contents (`scope_sha`,
# 2026-07-27 H1 self-HARDEN red-team -- so a change to SHARED code under a sibling
# atom's note re-offers too), NEVER a constant -- a stale/constant marker that
# never invalidates is caught by the mutation test (a changed atom must re-offer
# within cooldown; an expired stamp must re-offer). FAIL-TOWARD-WORK: any missing/
# malformed record -> the atom is NOT in cooldown (re-offer), so a broken marker
# can never silence a real HARDEN draw.
# =============================================================================
HARDEN_COOLDOWN_PATH = PROJECT_DIR / "docs" / "observability" / ".harden_cooldown.json"
# 6 -> 24 (2026-07-28): the 6h window re-verified an UNCHANGED at-target atom up to
# 4x/day. With a 34-atom at-target pool and a dial*criticality-weighted pick, a
# high-weight harness atom (H10_worktree_isolation) was re-offered on every ~6h
# cooldown exit -- offered 5x in ~24h (08:17Z/15:37Z/21:38Z 07-27, 04:36Z/10:57Z
# 07-28), each a PURE TIME re-offer of a saturated, byte-unchanged control (16/16
# green, R15 both ways). That churn was flagged as a dial-tuning candidate in the
# H10 HARDEN passes #3 and #4 but only ever in prose (evaporating -- MAKE_IT_STICK).
# 24h caps redundant re-verification of a genuinely-unchanged control at once/day
# while LOSING ZERO regression coverage: any file_scope code change re-offers the
# atom INSTANTLY via `scope_sha`, independent of this time window (below).
HARDEN_COOLDOWN_HOURS = 24


def _atom_content_sha(a: dict) -> str:
    """Stable SHA of an atom's serialised content -- the 'has it CHANGED since its last
    HARDEN pass' signal (R15 independence: real content, never a constant). A HARDEN pass
    appends a dated note to the atom, so record_harden_pass stamps the POST-pass sha; a
    LATER change (a fix/regression note committed to file_scope) flips the sha and re-offers.
    Returns '' on any serialisation error (never matches a stored sha -> re-offer)."""
    try:
        return hashlib.sha256(
            json.dumps(a, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:16]
    except (TypeError, ValueError):
        return ""


def _file_scope_sha(a: dict, root: Path | None = None) -> str:
    """SHA of the CURRENT contents of an atom's file_scope SOURCE FILES -- the 'has the
    CONTROLLED CODE changed since its last HARDEN pass' signal, complementing _atom_content_sha
    (which only sees the atom's OWN maturity-map note). Closes a real blind spot found by the
    2026-07-27 H1 self-HARDEN red-team: many harness atoms SHARE background/supervisor.py in
    file_scope (H1, H19, H_forward_discovery_draw, OPS1, ...), so a commit hardening a SIBLING
    atom moves the shared code but appends its note to the SIBLING's entry -- leaving this atom's
    yaml, and thus its _atom_content_sha, untouched. Without this the cooldown would suppress a
    re-verify for up to HARDEN_COOLDOWN_HOURS even though code under this atom's control just
    moved. Keying on file_scope contents re-offers on ANY such change -- exactly the docstring's
    stated intent ('a commit touched its file_scope -> re-verify'), previously unimplemented.
    FAIL-OPEN: '' when file_scope is absent/non-list or NO scoped file exists/reads -- an empty
    signal never spuriously suppresses; it just falls back to the atom-content + time behaviour."""
    root = root or PROJECT_DIR
    scope = a.get("file_scope")
    if not isinstance(scope, list):
        return ""
    h = hashlib.sha256()
    saw = False
    for rel in sorted(str(p) for p in scope):
        try:
            data = (Path(root) / rel).read_bytes()
        except (OSError, TypeError, ValueError):
            continue                         # missing/unreadable -> contributes nothing (a
            # DELETED scoped file thus flips the sha too -> re-verify, which is correct)
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(data)
        saw = True
    return h.hexdigest()[:16] if saw else ""


def _load_harden_cooldown(path: Path | None = None) -> dict:
    """Load the {atom_id: {'at': iso, 'sha': content_sha}} rotation-memory marker. FAIL-OPEN
    to {} (missing/malformed -> no atom in cooldown -> the draw behaves exactly as it did
    before the cooldown existed): a broken marker must never silence a real HARDEN draw."""
    p = path or HARDEN_COOLDOWN_PATH
    try:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def _harden_in_cooldown(a: dict, cooldown: dict, now: datetime | None = None) -> bool:
    """True iff atom `a` was HARDEN-verified recently AND is UNCHANGED since -- so the
    rotation draw should skip it this pass. False (RE-OFFER) when: no record; a malformed
    record; the atom's content CHANGED since the record (sha mismatch -> may have regressed,
    re-verify now); or the cooldown window has elapsed. Every ambiguity resolves to False
    (fail toward offering work -- Rule 0 / 'the to-do list is never empty')."""
    if not isinstance(cooldown, dict):
        return False
    rec = cooldown.get(a.get("id"))
    if not isinstance(rec, dict):
        return False
    if rec.get("sha") != _atom_content_sha(a):
        return False                         # atom's own note changed -> re-offer now
    scope_sha = rec.get("scope_sha")
    if scope_sha is not None and scope_sha != _file_scope_sha(a):
        return False                         # file_scope CODE changed (possibly under a sibling
        # atom's note on a shared file) -> may have regressed -> re-verify now. Guarded on
        # `is not None` so a legacy record (pre-scope_sha) is back-compat: scope check skipped,
        # falls back to atom-content + time; the next record_harden_pass writes the new field.
    try:
        last = datetime.fromisoformat(rec["at"])
    except (KeyError, TypeError, ValueError):
        return False                         # unparseable stamp -> re-offer (fail toward work)
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    try:
        return (now - last) < timedelta(hours=HARDEN_COOLDOWN_HOURS)
    except (TypeError, ValueError):
        return False


def record_harden_pass(atom_id: str, path: Path | None = None,
                       map_path: Path | None = None, now: datetime | None = None) -> Path | None:
    """Stamp that a HARDEN pass on `atom_id` just COMPLETED: records {at: now, sha: the atom's
    CURRENT content sha} so `_harden_in_cooldown` rotates the draw PAST it until the cooldown
    elapses OR its content changes again. Called by the agent that finishes a Rule-0 HARDEN pass
    (dogfooded: this very pass stamps H1). MERGES into the existing marker (never clobbers other
    atoms' records). Returns None (no-op, no stamp) if yaml is unavailable or the atom id is not
    in the map -- never fabricates a stamp for a phantom atom."""
    p = path or HARDEN_COOLDOWN_PATH
    mp = map_path or MATURITY_MAP_PATH
    try:
        import yaml
    except ImportError:
        return None
    try:
        atoms = yaml.safe_load(Path(mp).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(atoms, list):
        return None
    atom = next((a for a in atoms if isinstance(a, dict) and a.get("id") == atom_id), None)
    if atom is None:
        return None
    cooldown = _load_harden_cooldown(p)
    now = now or datetime.now(timezone.utc)
    cooldown[atom_id] = {"at": now.isoformat(), "sha": _atom_content_sha(atom),
                         "scope_sha": _file_scope_sha(atom)}
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(cooldown, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return Path(p)


# A staged [DIRECTOR-RULING] / [STEER] header, in ANY bracketed tag that ENDS in RULING or STEER
# (matches [DIRECTOR-RULING], [STEER], [ADVISOR-STEER], [DIRECTOR-STEER]). Content detection is the
# R7-correct primary signal (act on real content, not a filename a daemon could spoof).
_DIRECTOR_RULING_STEER_HEADER_RE = re.compile(r"\[[A-Z0-9 _-]*(?:RULING|STEER)\]", re.IGNORECASE)


def _unconsumed_director_ruling_or_steer(staging_dir: Path | None = None) -> bool:
    """True iff an UNCONSUMED staged [DIRECTOR-RULING] or [STEER] sits directly in docs/staging/
    ROOT (NOT done/, in_progress/, fyi/, drafts/ -- those are consumed/parked).

    DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27 §1+§3: a staged ruling/steer is RUNG 1
    and must draw within ONE tick (§3); re-verifying at-target atoms (the RULE-0 HARDEN treadmill)
    while a ruling NAMES undone work is the exact busywork-bias the ruling forbids (§1: 'with ... an
    unminted ruling present, a HARDEN re-verify draw must FAIL'). So the HARDEN tier of
    `_self_refill_draw()` is SUPPRESSED while such a ruling is unconsumed -- the ruling (already the
    `find_work()` `primary` doorbell) then draws ALONE, never appended-to as
    'ALSO -- RULE 0 self-refill ... HARDEN'. This reproduces + fixes the 2026-07-27 08:23-10:25 state
    (twelve HARDEN re-verifies while one director ruling sat unconsumed for 55 minutes).

    Detection is by CONTENT header first (R7: real content, a daemon-marker filename cannot spoof a
    ruling), with a filename-convention fallback for the naming every ruling/steer uses. Daemon
    markers (run_complete_*.md etc.) are excluded via `_is_daemon_marker`. FAIL-SAFE toward the map,
    not the ruling: an unreadable/absent staging dir returns False (HARDEN stays available -- the
    anti-idleness direction), matching every other draw helper's fail-safe here."""
    d = staging_dir or STAGING_DIR
    try:
        files = [p for p in Path(d).glob("*.md") if not _is_daemon_marker(p.name)]
    except OSError:
        return False
    for p in files:
        if p.name.startswith(("DIRECTOR_RULING_", "DIRECTOR_STEER_", "ADVISOR_STEER_")):
            return True
        try:
            head = p.read_text(encoding="utf-8")[:600]
        except OSError:
            continue
        if _DIRECTOR_RULING_STEER_HEADER_RE.search(head):
            return True
    return False


# =============================================================================
# §2 + §4 of DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27:
# RULINGS AND STEERS ARE A MINT SOURCE, not only DIRECTOR_AXES.
# -----------------------------------------------------------------------------
# §0 diagnosis, verbatim: "Rung-7 mints from DIRECTOR_AXES only, so prose in
# rulings is invisible to it." §2: "Any ratified ruling or steer that names work
# is a mint source. On consumption, named work becomes atoms in the map with lane,
# target level, exit criteria and dependencies." §4: "Each ruling/steer closes with
# named deliverables ... The machine mints atoms from that block within one tick.
# A ruling arriving without one is a defect in the ruling -- say so and request it;
# do not silently absorb it." These functions parse that block and drive the mint
# instruction the drawn ruling-turn acts on (item 1 already makes a staged ruling
# DRAW first at rung 1 -- this makes the drawn turn MINT from its block, and flags
# the §4 defect when the block is absent). R15-proven both ways in test_supervisor.py.
# =============================================================================
_WORK_THIS_CREATES_RE = re.compile(
    r"^#{1,6}\s*WORK\s+THIS\s+CREATES\b[^\n]*\n(.*?)(?=\n#{1,6}\s|\Z)",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
# A named deliverable inside the block: a numbered ("1." / "1)") or bulleted ("-"/"*") line.
_DELIVERABLE_LINE_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.+?)\s*$", re.MULTILINE)


def work_this_creates_deliverables(text: str) -> list[str]:
    """The named deliverables from a ruling/steer's 'WORK THIS CREATES' block (§4). Returns the
    deliverable lines (numbered or bulleted, markdown emphasis stripped, truncated), or [] if the
    doc carries NO such block -- [] is the §4 DEFECT signal, never fabricated work. Independence
    (R15): keyed on the block's ACTUAL content via a heading regex, never a constant, so neutralising
    the parser makes the 'block present' case return [] (the mutation the test proves fires)."""
    m = _WORK_THIS_CREATES_RE.search(text or "")
    if not m:
        return []
    out: list[str] = []
    for dm in _DELIVERABLE_LINE_RE.finditer(m.group(1)):
        s = re.sub(r"[*`]", "", dm.group(1)).strip()
        if s:
            out.append((s[:200] + "…") if len(s) > 201 else s)
    return out


def _is_ruling_or_steer(name: str, head: str) -> bool:
    """A [DIRECTOR-RULING]/[STEER] doc, by filename convention OR content header (R7: content is the
    primary signal). Shares the header regex + naming prefixes with the item-1 draw suppressor so the
    two can never disagree about what counts as a ruling/steer."""
    return bool(
        name.startswith(("DIRECTOR_RULING_", "DIRECTOR_STEER_", "ADVISOR_STEER_"))
        or _DIRECTOR_RULING_STEER_HEADER_RE.search(head)
    )


def ruling_steer_missing_work_block(staging_dir: Path | None = None) -> list[str]:
    """Staged [DIRECTOR-RULING]/[STEER] docs in the staging ROOT that carry NO 'WORK THIS CREATES'
    block (§4 defect: 'A ruling arriving without one is a defect in the ruling -- say so and request
    it; do not silently absorb it.'). Returns sorted filenames. Daemon markers excluded; FAIL-SAFE
    toward no-phantom-defect: an unreadable staging dir / file returns []/skips."""
    d = staging_dir or STAGING_DIR
    try:
        files = [p for p in Path(d).glob("*.md") if not _is_daemon_marker(p.name)]
    except OSError:
        return []
    missing: list[str] = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if _is_ruling_or_steer(p.name, text[:600]) and not work_this_creates_deliverables(text):
            missing.append(p.name)
    return sorted(missing)


def ruling_mint_instruction(staged_names: list[str], staging_dir: Path | None = None) -> str | None:
    """§2+§4 doorbell enrichment: for each drawn [DIRECTOR-RULING]/[STEER] among `staged_names`, state
    the mint action the drawn turn must take -- 'mint one atom per named deliverable from its WORK THIS
    CREATES block' (§2: rulings/steers are a mint source; the machine mints from that block within one
    tick) -- or flag the §4 defect when the block is absent. Returns the clause, or None if no
    ruling/steer is in the set (so `find_work`'s primary is byte-identical for every non-ruling staged
    doc -- the common case, and what the existing tests assert). R15: keyed on each doc's ACTUAL parsed
    block, never a constant."""
    d = staging_dir or STAGING_DIR
    parts: list[str] = []
    for name in staged_names:
        if _is_daemon_marker(name):
            continue
        try:
            text = (Path(d) / name).read_text(encoding="utf-8")
        except OSError:
            continue
        if not _is_ruling_or_steer(name, text[:600]):
            continue
        deliverables = work_this_creates_deliverables(text)
        if deliverables:
            joined = "; ".join(f"({i + 1}) {dv}" for i, dv in enumerate(deliverables))
            parts.append(
                f"{name}: MINT one atom per named deliverable from its WORK THIS CREATES block "
                f"[{joined}] -- each with lane + target level + exit criteria + deps; a deliverable "
                f"ALREADY minted (an existing PLANNER_MINTED_* doc or a map atom) is NOT re-minted "
                f"(state which are already covered)."
            )
        else:
            parts.append(
                f"{name}: DEFECT (§4) -- NO 'WORK THIS CREATES' block. A ruling/steer arriving without "
                f"one is a defect in the ruling: mint what work you can identify from its body AND "
                f"request the block from the author -- do NOT silently absorb it."
            )
    if not parts:
        return None
    return (
        "RULINGS/STEERS ARE A MINT SOURCE (§2+§4 DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE "
        "2026-07-27): " + " | ".join(parts)
    )


_MISSING_BLOCK_ITEM_PREFIX = "ruling_missing_work_block:"


def surface_missing_work_block_defects(
    staging_dir: Path | None = None,
    register_path: Path | None = None,
    send_ntfy_fn: Any = None,
) -> list[str]:
    """§4 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27): a staged [DIRECTOR-RULING]/[STEER]
    that carries NO 'WORK THIS CREATES' block is a defect IN THE DOC. `ruling_steer_missing_work_block()`
    DETECTS the case; this function SURFACES it to a real consumer, closing the fail-silent gap that the
    detector was wired NOWHERE (an un-surfaced detector is a fail-silent control --
    feedback_fail_silent_control_patterns). Returns the list of currently-defective ruling names; the
    caller (`run_cycle`) logs them, which is the surface.

    IT DOES NOT PAGE THE DIRECTOR, and that is the whole design (2026-08-03, rip-out 102c29790 +
    THE_STANDARD, which governs where the 07-27 ruling's "say so and request it" conflicts). §4's ask
    used to become a durable [ACTION NEEDED] register item + an NTFY -- i.e. a "waiting on Rich" queue
    entry for something that is NOT one of the four reserved real-world classes. `register_item` now
    REFUSES exactly that, so the register/NTFY path was dead code the moment the guard landed. The
    machine's answer to a block-less doc is the one THE_STANDARD prescribes: absorb it -- the tick draws
    the staged doc and mints the work from the body -- and say what it did, never open a queue and wait.

    WHY THE DEAD PATH WAS REMOVED RATHER THAN LEFT UNREACHABLE (this is a defect, not tidying): the
    refusal is decided by `one_way_door.classify_action` over the item's `what` string, and that string
    INTERPOLATES THE RULING'S FILENAME. A ruling whose name happened to carry a reserved-class trigger
    word would have classified as reserved and slipped a page through, while its neighbours were
    refused -- a control whose firing depends on an unrelated filename. Deleting the path removes the
    nondeterminism instead of relying on the guard to keep catching it.

    STILL RECONCILES (R11 'no orphan transitions'): any legacy `ruling_missing_work_block:` item left in
    a live register from before the guard is cleared here, so a withdrawn convention's items leave the
    director window rather than lingering forever unresolvable.

    `send_ntfy_fn` is accepted and DELIBERATELY NEVER CALLED. It stays in the signature so the test can
    hold the teeth in the fail-open direction: if anyone re-wires a director page onto this defect class,
    `test_blockless_ruling_detected_but_never_pages` goes RED.

    R15 both ways: a block-less ruling -> returned (so it is logged) and NO register item, NO send;
    a ruling that gains a block, or is archived/parked, -> not returned and any legacy item cleared.
    Neutralising the detector (`ruling_steer_missing_work_block` -> []) makes the block-less case go
    UNDETECTED -> the surface returns nothing (the fail-open direction the test proves catchable).

    FAIL-SAFE: reconcile failures are best-effort and never raise into the caller -- run_cycle must never
    break because a defect could not be surfaced."""
    from background import action_needed

    missing = ruling_steer_missing_work_block(staging_dir)
    still_defective = {_MISSING_BLOCK_ITEM_PREFIX + name for name in missing}

    # RECONCILE: clear every legacy defect item. `still_defective` is intentionally computed and
    # compared even though nothing writes these items any more -- if a live register carries one for a
    # ruling that IS still block-less, clearing it would be a false "fixed"; it is left alone to be
    # cleared on the cycle after the doc is actually closed or parked.
    try:
        register = action_needed.load_register(register_path)
        for item_id in list(register):
            if item_id.startswith(_MISSING_BLOCK_ITEM_PREFIX) and item_id not in still_defective:
                action_needed.clear_item(item_id, path=register_path)
    except Exception:  # noqa: BLE001 -- a reconcile failure must not stop reporting live defects
        pass

    return missing


def _rule0_harden_draw(rng: Any = None) -> dict | None:
    """RULE 0 (2026-07-14, director, THE PRIME DIRECTIVE): the default state of
    the company is WORKING; an empty feasible set is a DEFECT IN THE DIALS, not a
    reason to hold. This is the FINAL widen tier of `_self_refill_draw()` -- when
    every below-target lane (BUILD/SITE/DISCOVERY) AND the backlog are empty, the
    below-target dial itself is yielded and this draws HARDEN/red-team work on an
    AT-target atom (level_current == level_target, target > 0). A shipped atom is
    never 'done': its exit tests can be re-verified, its controls mutation-re-
    tested, its invariants red-teamed, its real-world fidelity widened. Same
    dial-weighted-random convention as the other draws. Returns None only if the
    map has zero at-target atoms -- a genuinely empty map is a WALL, effectively
    never reached with 88 atoms."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        atoms = map_store.load_atoms(MATURITY_MAP_PATH)
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(atoms, list):
        return None

    at_target = [a for a in atoms if _harden_at_target(a)]
    if not at_target:
        return None                          # genuinely empty map = WALL (unchanged)
    # HARDEN-ABILITY GATE (G10, twin-approved 2026-07-17): PREFER at-target atoms that
    # have a real harden-able surface (a built control + runnable test), so an idle
    # HARDEN pass spends red-team effort where a control can actually fail rather than
    # on a FRAME-only atom with nothing to re-verify. SOFT DIAL (Rule 0): if NO atom
    # qualifies, fall back to the full at-target pool so the draw stays NON-EMPTY -- a
    # genuinely-empty draw here would false-trip the LOOP_BROKEN transport alarm.
    pool = [a for a in at_target if _has_harden_surface(a)] or at_target
    # ROTATION MEMORY (2026-07-25, H1 HARDEN red-team fix): skip atoms HARDEN-verified
    # within the cooldown window AND unchanged since, so the draw ROTATES the at-target
    # pool instead of re-handing the same atoms within a few turns (the churn the
    # 2026-07-18 red-team registered). SOFT (Rule 0): if that empties the pool (every
    # candidate recently hardened + unchanged) fall back so the draw stays non-empty.
    cooldown = _load_harden_cooldown()
    rotated = [a for a in pool if not _harden_in_cooldown(a, cooldown)]
    pool = rotated or pool
    # STRUCTURAL criticality bias (harness/control lanes preferred) folded into the
    # existing dial-weighted-random pick; both are diagnostics, never targets (R12).
    weights = [max(1, a.get("dial_inherited", 1)) * _harden_criticality_weight(a) for a in pool]
    picker = rng or random
    return picker.choices(pool, weights=weights, k=1)[0]


# =============================================================================
# THE TICK NEVER RESTS WHILE AUTHORIZED WORK EXISTS AT ANY PRIORITY
# -----------------------------------------------------------------------------
# HARD RULE (harness-level, alongside R1-R16; director console 2026-07-22).
# The draw ladder spans THREE authority levels: (1) CORE -- BUILD/SITE below
# target; (2) IDLE-ADVANCE -- DISCOVER/FRAME on idle atoms + the PRIORITIES
# backlog; (3) FORWARD-DISCOVERY -- the standing F1-F5 register (this lane).
# REST is legitimate ONLY with PROOF the authorized set is EMPTY AT EVERY
# LEVEL. The forward-discovery register is the ALWAYS-DRAWABLE final lane:
# OPTIONAL/preemptible DISCOVER tracks that YIELD to core but are drawn before
# the tick ever rests. Before 2026-07-22 this lane was DESIGNED (FORWARD_
# DISCOVERY_REGISTER.md; atom H_forward_discovery_draw, provenance:proposal,
# level 0) but NEVER WIRED INTO THE DRAW -- so a core-gated tick with a full
# register RESTED (the 95-min R13-wait stall, 2026-07-22). "Consumed" (steer
# actioned -> design doc + atom authored) is NOT "absorbed" (mechanism live in
# the running draw + R15-proven). A future stall of THIS class is an R10 breach
# of THIS RULE, not a new incident. R15-proven both ways in
# tests/background/test_forward_discovery_draw.py.
# =============================================================================
FORWARD_DISCOVERY_REGISTER_PATH = PROJECT_DIR / "docs" / "design" / "FORWARD_DISCOVERY_REGISTER.md"

# Where a graduated-to-FRAME track's BUILD PROPOSAL lands. A proposal artefact here (named
# `<Fn>_*.md`) is the concrete, self-releasing signal that the track's PROPOSE HALF is done --
# writing it DRAINS the propose-half draw (R11 no-orphan: the release triggers a real artefact,
# never nothing). Directory may not exist until the first proposal is written (that is fine --
# absent dir = no proposal written = every propose-half still drawable, the safe direction).
FORWARD_PROPOSAL_DIR_PATH = PROJECT_DIR / "docs" / "design" / "proposals"

# A drawable forward-discovery track header, e.g. "## F1 -- Simulating conversations".
_FWD_TRACK_RE = re.compile(r"^##\s*(F\d+)\s+[—-]\s+(.+?)\s*$", re.MULTILINE)

# The ranking-table row that carries each track's LIVE status in its last cell, e.g.
# "| **F1** | Simulating conversations | mission-required | **highest** ... | DISCOVER-complete ... |".
# The status cell is the authoritative per-track completion signal (one source, not scattered body
# prose). Greedy "(?:[^\n]*\|)" consumes every interior pipe up to the LAST one so the final capture
# is the status cell whatever the column count.
_FWD_STATUS_ROW_RE = re.compile(r"^\|\s*\*\*(F\d+)\*\*\s*\|(?:[^\n]*\|)\s*([^|\n]*?)\s*\|\s*$", re.MULTILINE)

# A whole track section, "## Fn ...\n<body up to the next ## Fn or EOF>" -- used only to surface each
# complete track's own 'Candidate graduation' line in the batched director [ACT] (never to self-open).
_FWD_SECTION_RE = re.compile(r"^##\s*(F\d+)\b[^\n]*\n(.*?)(?=^##\s*F\d+\b|\Z)", re.MULTILINE | re.DOTALL)


def _forward_discovery_tracks(register_path: Path | None = None) -> list[tuple[str, str]]:
    """Parse the forward-discovery register into ALL its DISCOVER tracks (F1..Fn),
    highest-rank first (file order). Returns [] if the register is
    absent/unreadable/empty. This is the STRUCTURAL parse (every track that exists);
    DRAWABILITY (which of these still has open DISCOVER work) is a separate filter
    applied in `_forward_discovery_draw` via `_forward_discovery_complete_ids`, so a
    fully-graduated register still parses non-empty here while offering nothing to draw.
    An ABSENT register IS an empty authorized set at this level -- exactly the PROOF that
    rest requires -- so this reports 'empty' honestly; the load-bearing anti-rest guarantee
    lives in the LADDER ORDER (this lane sits ABOVE rest in both `_self_refill_draw` and
    `_is_drained_and_gated`), never in pretending a missing file has work."""
    path = register_path or FORWARD_DISCOVERY_REGISTER_PATH
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    return [(m.group(1), m.group(2).strip()) for m in _FWD_TRACK_RE.finditer(text)]


def _forward_discovery_complete_ids(register_path: Path | None = None) -> set[str]:
    """Track ids whose ranking-table status cell reads 'DISCOVER-complete'. A DISCOVER-
    complete track has LEFT the authorized drawable set (director console 2026-07-22, R17
    fail-open fix): the DISCOVER work is done, so re-drawing it is the 'treadmill in new
    clothes' churn -- once complete, its only remaining move is a director GRADUATION call,
    surfaced once as an [ACT] (see `forward_discovery_graduation_proposal`), never re-drawn.

    R15 / FAIL-SAFE TOWARD WORK: on any read error, or a register with no status table, this
    returns the EMPTY set -- so nothing is excluded and every parsed track stays drawable. The
    harmful failure mode is resting when real DISCOVER work remains; erring toward 'drawable'
    keeps the anti-rest pressure. Keyed on the ACTUAL parsed status cell, never a constant, so a
    mutation that hard-codes 'all complete' is caught by the must-not-rest-with-open-track test."""
    path = register_path or FORWARD_DISCOVERY_REGISTER_PATH
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return set()
    return {
        m.group(1) for m in _FWD_STATUS_ROW_RE.finditer(text)
        if "discover-complete" in m.group(2).lower()
    }


def _forward_discovery_drawable_tracks(register_path: Path | None = None) -> list[tuple[str, str]]:
    """The tracks that are STILL DRAWABLE -- parsed tracks minus DISCOVER-complete ones. This is
    the authorized forward-discovery set the draw and the rest predicate both consult."""
    complete = _forward_discovery_complete_ids(register_path)
    return [t for t in _forward_discovery_tracks(register_path) if t[0] not in complete]


# The PROPOSE-HALF class fix (director ruling 2026-07-23, DIRECTOR_RULING_R17_BREACH_AND_CLASS_FIX;
# the R10-breach-of-R17 the ruling declares). The overnight stall: F1 was GRADUATED → FRAME and its
# BUILD PROPOSAL was drawable all night (proposing needs no gate -- that IS propose-then-proceed), but
# NO lane enumerated it, so the tick rested over doable work. The class (not the F1 instance): an atom
# whose BUILD is gated still has an UNGATED PROPOSAL step -- that step is ALWAYS drawable work. This
# names it in code as its own lane so a graduated-but-unproposed track can never again ground rest.
#
# A track's status cell records the propose-half when it names BOTH the FRAME stage it graduated to AND
# a "build proposal" step (the exact F1 shape: "GRADUATED → FRAME ... build proposal via gate"). This
# marker is what distinguishes a propose-half graduation from the other dispositions that carry NO build-
# proposal step: FOLDED (into site work), HELD (director-reserved), or a doc-only graduation. Keyed on
# the ACTUAL cell text (R15 independence -- a mutation hard-coding it is caught by the must-not-rest test).
_FWD_PROPOSE_HALF_MARKER = "build proposal"


def _proposal_written_ids(proposal_dir: Path | None = None) -> set[str]:
    """Track ids whose BUILD PROPOSAL artefact already exists on disk (`docs/design/proposals/<Fn>_*.md`).
    Writing the proposal DRAINS that track's propose-half -- a concrete, self-releasing transition
    (R11 no-orphan: the release is the artefact appearing, never a silent flag). FAIL-SAFE TOWARD WORK
    (R15): an absent/unreadable directory returns the EMPTY set, so NOTHING is counted as written and
    every propose-half stays drawable -- the harmful failure mode is resting over a propose step that is
    actually open, so ambiguity keeps the anti-rest pressure. Keyed on the ACTUAL files present, never a
    constant, so a mutation pretending 'all proposals written' is caught by the must-not-rest test."""
    d = Path(proposal_dir or FORWARD_PROPOSAL_DIR_PATH)
    try:
        return {
            m.group(1) for p in d.glob("F*.md")
            for m in [re.match(r"(F\d+)_", p.name)] if m
        }
    except OSError:
        return set()


def _forward_discovery_propose_half_tracks(
    register_path: Path | None = None, proposal_dir: Path | None = None
) -> list[tuple[str, str]]:
    """Graduated-to-FRAME tracks whose BUILD PROPOSAL is NOT yet written -- the ungated PROPOSE HALF of
    a BUILD-gated item, ALWAYS drawable (director ruling 2026-07-23, R17 class fix). Highest-rank first.
    A track is a drawable propose-half iff (a) its status cell records graduation to FRAME with a build-
    proposal step (the `_FWD_PROPOSE_HALF_MARKER`), AND (b) no proposal artefact exists for it yet. BOTH
    signals are real (register cell + filesystem), never a constant (R15); writing the proposal drains it.
    FAIL-SAFE: an unreadable register returns [] (this lane offers nothing) -- the anti-rest guarantee
    lives in the LADDER ORDER (this rung sits ABOVE rest in both `_self_refill_draw` and
    `_is_drained_and_gated`), never in pretending a missing file has work."""
    path = register_path or FORWARD_DISCOVERY_REGISTER_PATH
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    written = _proposal_written_ids(proposal_dir)
    titles = dict(_forward_discovery_tracks(register_path))
    out: list[tuple[str, str]] = []
    for m in _FWD_STATUS_ROW_RE.finditer(text):
        tid, cell = m.group(1), m.group(2).lower()
        if "frame" in cell and _FWD_PROPOSE_HALF_MARKER in cell and tid not in written:
            out.append((tid, titles.get(tid, "")))
    return out


def _propose_half_draw(
    register_path: Path | None = None, proposal_dir: Path | None = None
) -> str | None:
    """Draw the highest-ranked drawable PROPOSE HALF, or None if none is open. Sits in the ladder ABOVE
    the forward-discovery DISCOVER draw and the RULE-0 HARDEN treadmill: a graduated track's build
    proposal is the next real step toward opening a BUILD atom -- higher value than re-DISCOVERing a
    complete track or re-verifying a finished one. R7: this states what exists; the granted session
    writes the proposal (propose-then-proceed, no BUILD code, no map level change)."""
    tracks = _forward_discovery_propose_half_tracks(register_path, proposal_dir)
    if not tracks:
        return None
    tid, title = tracks[0]
    return (
        "PROPOSE-HALF self-refill (ALWAYS-DRAWABLE -- director ruling 2026-07-23, R17 class fix: a "
        "BUILD-gated item's ungated PROPOSAL step is drawable work; the tick NEVER rests over it): "
        f"{tid} -- {title}. Write the build proposal (the triad build plan) THROUGH THE GATE into "
        f"docs/design/proposals/{tid}_*.md -- propose-then-proceed, no BUILD code, no map level change; "
        "the proposal artefact IS the drawable deliverable, and writing it drains this rung."
    )


# A DISPOSITIONED track has a director GRADUATION RULING recorded in its status cell (graduated /
# held / folded / superseded). It has left the forward-discovery lane for good, so it must NOT be
# re-surfaced in the graduation [ACT] (that [ACT] is only for tracks AWAITING a ruling). A
# dispositioned track keeps 'DISCOVER-complete' in its cell too, so `_forward_discovery_complete_ids`
# already excludes it from the DRAWABLE set -- this predicate refines ONLY the [ACT], never rest/draw.
_FWD_DISPOSITIONED_RE = re.compile(r"graduat|\bheld\b|\bhold\b|folded|superseded", re.IGNORECASE)


def _forward_discovery_dispositioned_ids(register_path: Path | None = None) -> set[str]:
    """Track ids whose status cell records a director graduation ruling (graduated/held/folded/
    superseded). Fail-safe: on any error, the EMPTY set -- so an unparseable cell errs toward
    'still awaiting a ruling' (the [ACT] re-surfaces it), never toward silently dropping a track
    that genuinely needs the director. Keyed on the ACTUAL status cell, never a constant (R15)."""
    path = register_path or FORWARD_DISCOVERY_REGISTER_PATH
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return set()
    return {
        m.group(1) for m in _FWD_STATUS_ROW_RE.finditer(text)
        if _FWD_DISPOSITIONED_RE.search(m.group(2))
    }


def _forward_discovery_draw(rng: Any = None, register_path: Path | None = None) -> str | None:
    """THE ALWAYS-DRAWABLE LANE (director steer 2026-07-22 §3, SELF_MEASUREMENT_
    UNIFIED_DESIGN.md §3; mechanised 2026-07-22 under the HARD RULE above). When
    CORE (BUILD/SITE) and IDLE-ADVANCE (DISCOVER/FRAME + backlog) are all empty/
    gated, the draw falls through HERE instead of resting -- a standing F1-F5
    DISCOVER track from FORWARD_DISCOVERY_REGISTER.md. DISCOVER-ONLY, optional/
    preemptible (yields INSTANTLY to any core atom next cycle). Returns None
    ONLY when the register is genuinely empty/absent -- with F1-F5 standing,
    rare by construction, so the tick rests rarely and legitimately.

    Rank order = file order (F1 highest). Dial-weighted-random pick BIASED to
    rank so F1 (mission-required x highest) is preferred without starving lower
    tracks. INDEPENDENCE (R15): keyed on the ACTUAL parsed register content,
    never a constant -- emptying the register is caught by the genuinely-empty
    test; dropping this rung from the ladder is caught by the must-not-rest
    test (both in test_forward_discovery_draw.py)."""
    tracks = _forward_discovery_drawable_tracks(register_path)
    if not tracks:
        # Every track is DISCOVER-complete (or the register is empty/absent): the authorized
        # forward-discovery set is empty, so this lane offers nothing to draw and the tick may
        # rest with that PROOF (director console 2026-07-22, R17 fail-open fix). The graduation
        # of the complete tracks is a director [ACT], surfaced separately, not a draw.
        return None
    picker = rng or random
    weights = [len(tracks) - i for i in range(len(tracks))]
    track_id, title = picker.choices(tracks, weights=weights, k=1)[0]
    return (
        "FORWARD-DISCOVERY self-refill (ALWAYS-DRAWABLE lane -- core + idle-advance lanes "
        f"empty/gated, so the tick draws forward-discovery instead of resting): {track_id} -- {title}. "
        "DISCOVER-ONLY (optional/preemptible: yields INSTANTLY to any core atom next cycle; no BUILD "
        "code, no new map atoms). Work its 'Key DISCOVER questions' in docs/design/FORWARD_DISCOVERY_"
        "REGISTER.md; anchor to real sources, validate against an INDEPENDENT source (never SIM ground "
        "truth), honour the epistemic wall. NTFY only on a notable finding."
    )


CAMPAIGN_REGISTER_PATH = PROJECT_DIR / "docs" / "design" / "CAMPAIGN_REGISTER.yaml"


def _open_campaign_items(register_path: Path | None = None) -> list[tuple[str, str, str]]:
    """The SEVENTH-CLASS lane (director ruling 2026-07-23, DIRECTOR_RULING_CAMPAIGN_CONTINUATION):
    every OPEN item of every OPEN campaign in the machine-readable register. Returns a list of
    (campaign_id, item_id, item_title) -- unfinished work that is drawable WITHOUT a doorbell,
    because "an open campaign in PRIORITIES with unfinished items IS drawable work -- finishing
    surface N rolls directly into surface N+1".

    Reads docs/design/CAMPAIGN_REGISTER.yaml (R16: the ledger is authority, not PRIORITIES prose --
    the 14:03Z stall was the campaign living only as a comment block the draw could not see). An
    item counts as unfinished unless its status is exactly `landed`; a campaign contributes items
    only while its status is `open` (a `closed`/`cancelled` campaign leaves the drawable set, which
    is the "all items landed permits rest" half of the R15 pair).

    INDEPENDENCE (R15): keyed on the ACTUAL parsed register content, never a constant -- emptying
    the register (or landing every item) is caught by the may-rest test; dropping this rung from the
    ladder is caught by the must-not-rest test (both in test_open_campaign_draw.py)."""
    import yaml

    path = register_path or CAMPAIGN_REGISTER_PATH
    try:
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(doc, dict):
        return []
    out: list[tuple[str, str, str]] = []
    for camp in doc.get("campaigns") or []:
        if not isinstance(camp, dict):
            continue
        if str(camp.get("status", "")).strip().lower() != "open":
            continue
        cid = str(camp.get("id", "?"))
        for item in camp.get("items") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status", "")).strip().lower() == "landed":
                continue
            out.append((cid, str(item.get("id", "?")), str(item.get("title", "")).strip()))
    return out


def _open_campaign_draw(register_path: Path | None = None) -> str | None:
    """The SEVENTH-CLASS draw rung (director ruling 2026-07-23). Returns a draw message enumerating
    the OPEN items of every OPEN campaign, or None when no campaign has an unfinished item (rest is
    then legitimate on this level). Sits ABOVE the PRIORITIES backlog / propose-half / forward-
    discovery / HARDEN rungs: an open product campaign is the highest-value fallback when the three
    below-target lanes are empty (PRODUCT-FIRST). Preemptible -- yields to any below-target atom next
    cycle, same as the other fallback rungs.

    R15: this is the rung whose ABSENCE reproduced the 14:03Z stall (SITE_V5 open, surfaces 2-5
    drawable, the tick rested because no lane enumerated the campaign)."""
    items = _open_campaign_items(register_path)
    if not items:
        return None
    by_campaign: dict[str, list[str]] = {}
    for cid, iid, title in items:
        by_campaign.setdefault(cid, []).append(f"{iid} ({title})" if title else iid)
    blocks = "; ".join(
        f"{cid}: " + " | ".join(names) for cid, names in by_campaign.items()
    )
    return (
        "OPEN-CAMPAIGN self-refill (SEVENTH CLASS, director ruling 2026-07-23 -- an open campaign "
        "with unfinished items IS drawable work; finishing item N rolls into item N+1, NO doorbell): "
        f"{blocks}. Draw the next unfinished item of the highest-priority open campaign (SITE_V5 "
        "first: build surfaces 2->5 in order, each landed LIVE + Expert-Hour-reviewed against its "
        "single job before the next; iterate any DEPLOYED-but-FAILED surface in parallel and present "
        "it as SCORED RUBRIC ROWS). On landing a surface LIVE + pixel-verified (R11), mark its item "
        "`landed` in docs/design/CAMPAIGN_REGISTER.yaml the SAME commit. Per-surface DoD: each "
        "campaign's `dod` field."
    )


DECLARED_DEFECTS_REGISTER_PATH = PROJECT_DIR / "docs" / "design" / "DECLARED_DEFECTS_REGISTER.yaml"


def _open_declared_defects(register_path: Path | None = None) -> list[dict]:
    """RUNG 4 of the WORK-SOURCE HIERARCHY (director ruling 2026-07-23, WORK_IS_THE_DEFAULT): every
    DECLARED fidelity defect whose gap is still open. Returns the open defects sorted by priority
    (1 = highest), ties broken by declared_at (oldest first -- the spike tail, "untouched five days",
    sorts to the top). Reads docs/design/DECLARED_DEFECTS_REGISTER.yaml (R16: a machine-readable
    ledger, not FRAME prose -- the whole point is that a declared defect the draw could not SEE read
    as REST-LEGITIMATE while a top-priority defect sat open).

    A defect counts open unless its status is exactly `closed`; `closed` means the fidelity gap was
    re-measured shut, NOT merely that a plan was written (else the loop would idle beside a still-open
    gap the instant a `plan_doc` existed -- the exact failure this rung fixes).

    INDEPENDENCE (R15): keyed on the ACTUAL parsed register content, never a constant -- emptying the
    register (or closing every defect) is caught by the may-rest test; dropping this rung from the
    ladder is caught by the must-not-rest test (both in test_defect_backlog_draw.py)."""
    import yaml

    path = register_path or DECLARED_DEFECTS_REGISTER_PATH
    try:
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(doc, dict):
        return []
    out: list[dict] = []
    for d in doc.get("defects") or []:
        if not isinstance(d, dict):
            continue
        if str(d.get("status", "")).strip().lower() == "closed":
            continue
        out.append(d)
    out.sort(key=lambda d: (_as_int(d.get("priority"), 99), str(d.get("declared_at", "9999"))))
    return out


def _as_int(v: Any, default: int) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _declared_defect_backlog_draw(register_path: Path | None = None) -> str | None:
    """RUNG 4 draw (director ruling 2026-07-23, WORK_IS_THE_DEFAULT: "a declared defect that is not in
    the drawable set is a contradiction; enforce that as an invariant"). Returns a draw message for the
    highest-priority OPEN declared defect, or None when every declared defect is `closed` (rest is then
    legitimate ON THIS LEVEL). Sits ABOVE the PRIORITIES-prose backlog / propose-half / forward-discovery
    / HARDEN floor: a declared fidelity defect is real product work, higher value than re-DISCOVER or the
    HARDEN treadmill.

    If the top defect already has a `plan_doc`, the draw is to ADVANCE the fix per that plan; if not, the
    draw is to MINT the plan first (propose-then-proceed). Either way the defect stays drawable until its
    `closes_when` condition is measured -- being idle beside a declared defect is the failure (ruling).

    R15: this is the rung whose ABSENCE reproduced today's state -- spike-tail declared, no staged docs,
    `authorized_set_enumeration` all-empty -> REST-LEGITIMATE while the top defect sat open."""
    defects = _open_declared_defects(register_path)
    if not defects:
        return None
    top = defects[0]
    others = [str(d.get("id", "?")) for d in defects[1:]]
    plan = str(top.get("plan_doc") or "").strip()
    plan_clause = (
        f"Its attack plan is minted: {plan} -- ADVANCE the fix per that plan (propose-then-proceed, "
        "normal window)."
        if plan and plan.lower() not in ("none", "null")
        else "No plan_doc yet -- MINT the propose-doc first (propose-then-proceed), then advance."
    )
    tail = f" Also open (lower priority): {', '.join(others)}." if others else ""
    return (
        "DECLARED-DEFECT self-refill (RUNG 4, director ruling 2026-07-23 WORK_IS_THE_DEFAULT -- a "
        "declared fidelity defect that is not in the drawable set is a contradiction): top open defect "
        f"{top.get('id', '?')} -- {str(top.get('title', '')).strip()}. Evidence: "
        f"{str(top.get('evidence', '')).strip()} {plan_clause} It stays drawable until measured shut: "
        f"{str(top.get('closes_when', '')).strip()} On close, set status: closed in "
        f"docs/design/DECLARED_DEFECTS_REGISTER.yaml the SAME commit.{tail}"
    )


def _stale_gap_row_draw(work: list | None = None) -> str | None:
    """RUNG 4b -- A PUBLISHED GAP MEASUREMENT TAKEN BY CODE WE NO LONGER RUN.

    `background/gap_ledger_reconciler.py` has reported the coupled-gap family's staleness on five
    consecutive ticks and every one of those re-runs was done BY HAND, because the reconcile is
    report-only (G-R3) and no lane enumerated its output. That is the same shape as the overnight
    operational-red incident directly above: a control that pages and pages while no draw rung
    ever surfaces "go clear it". This is the rung. Ownership rationale, alternatives considered
    and what this deliberately does NOT do: `docs/design/GAP_TOOL_RERUN_OWNERSHIP.md`.

    Draws ONLY rows a re-run can actually clear (`refresh_work`), so the rung DRAINS: re-measuring
    W2_4_household_budget took 0.5s and moved the drift set 11 -> 10 with the row reading CURRENT
    after. `never_measured` -- a pair the map declares with no row and no producer to point at --
    is genuinely un-drainable and stays out, because a rung that can never drain wedges the ladder
    behind it (feedback_control_that_can_only_fail_wedges).

    `never_landed` USED TO BE EXCLUDED ALONGSIDE IT AND SHOULD NOT HAVE BEEN (2026-08-10). That
    status means a tool exists on disk and its output reaches no row -- if it is invocable, one
    command lands the row, and `tools/couple_cohort.py` sat in the drift set for two days as a
    permanent member no rung could act on while `python3 -m tools.couple_cohort` ran clean in
    seconds. It is drawn now when it has an invocable runner, and only then; the wedge guard
    survives as that narrower rule rather than as a ban on the whole status.

    Sits BELOW the declared-defect backlog (RUNG 4) and ABOVE propose-half / forward-discovery /
    the HARDEN treadmill: refreshing a stale number on a public door is real evidence work, better
    than re-verifying a finished atom, but it does not outrank an open product defect.

    FAIL-OPEN BY CONSTRUCTION on its own error (matching the rungs above it): a reconciler that
    cannot import or cannot read git returns no work and the ladder falls through to lower rungs.
    It can never invent a hold. `_is_drained_and_gated` mirrors it, so rest cannot be declared
    while a stale published number is refreshable."""
    if work is None:
        try:
            from background import gap_ledger_reconciler as _glr
            work = _glr.refresh_work(_glr.reconcile())
        except Exception:
            return None
    if not work:
        return None
    listed = work[:_STALE_GAP_SUMMARY_CAP]
    lines = "; ".join(
        f"{w['item']} ({w['status']}) -> "
        + (w["command"] or "NO INVOCABLE PRODUCER -- cannot be re-taken, file it as a defect")
        for w in listed
    )
    overflow = (
        f" (+{len(work) - len(listed)} more -- `python3 -m background.gap_ledger_reconciler "
        "--refresh-work` lists them all)"
        if len(work) > len(listed) else ""
    )
    no_runner = [w["item"] for w in work if w["no_runner"]]
    no_runner_clause = (
        f" {len(no_runner)} of these have NO invocable producer ({', '.join(no_runner[:3])}) -- "
        "that is a worse defect than staleness (a published number nobody can re-take) and wants a "
        "finding, not a re-run."
        if no_runner else ""
    )
    return (
        f"STALE-GAP-ROW self-refill (RUNG 4b): {len(work)} published coupled-gap measurement(s) "
        "were taken by code that has since changed -- a public door is showing a number produced "
        "by a program nobody runs. Re-take them and commit the ledger: "
        + lines + overflow + no_runner_clause
        + " ACCEPTANCE is not that the command ran: re-run `python3 -m "
        "background.gap_ledger_reconciler` and show the row reading CURRENT. Report any number "
        "that MOVED (a moved gap is a measurement worth a record, not a silent republish); if a "
        "command needs arguments this draw did not know, say so rather than skipping the row."
    )


def forward_discovery_law_status(register_path: Path | None = None) -> dict:
    """Live status of the HARD RULE 'THE TICK NEVER RESTS WHILE AUTHORIZED WORK
    EXISTS AT ANY PRIORITY' (director console 2026-07-22). Returned as data so
    the daily self-note (SM1, `background/daily_self_note.py` -- NOT YET BUILT;
    this is its named morning-report home per SELF_MEASUREMENT_UNIFIED_DESIGN.md
    'reuse don't accrete') can render one line every morning unprompted, and so
    the supervisor can log it live every cycle in the meantime.

    `wired` proves the always-drawable rung is actually in the ladder (not just
    designed) -- the exact 'consumed vs absorbed' check that this whole incident
    is about: a True here means the mechanism is LIVE in the running draw, not
    merely that a design doc exists.

    Reports DRAWABLE vs COMPLETE separately (R17 fail-open fix, director console
    2026-07-22): a DISCOVER-complete track has left the authorized set, so listing it as
    'backlog' would be the exact dishonesty the fix removes -- `drawable_tracks` is what
    actually keeps the tick working; `complete_tracks` are done and await a director
    graduation [ACT], not a re-draw."""
    all_tracks = _forward_discovery_tracks(register_path)
    complete = _forward_discovery_complete_ids(register_path)
    dispositioned = _forward_discovery_dispositioned_ids(register_path)
    drawable = [t[0] for t in all_tracks if t[0] not in complete]
    awaiting = sorted(complete - dispositioned)
    propose_half = [t[0] for t in _forward_discovery_propose_half_tracks(register_path)]
    wired = "_forward_discovery_draw" in globals() and callable(globals()["_forward_discovery_draw"])
    return {
        "rule": "THE TICK NEVER RESTS WHILE AUTHORIZED WORK EXISTS AT ANY PRIORITY",
        "always_drawable_lane_wired": wired,
        "forward_discovery_tracks": [t[0] for t in all_tracks],
        "drawable_tracks": drawable,
        "complete_tracks": sorted(complete),
        "awaiting_graduation": awaiting,          # DISCOVER-complete but no director ruling yet
        "dispositioned_tracks": sorted(dispositioned),  # director has ruled (graduated/held/folded)
        "propose_half_tracks": propose_half,      # graduated-to-FRAME, build proposal not yet written (R17 class fix 2026-07-23)
        "register_nonempty": bool(all_tracks),
        "drawable_nonempty": bool(drawable) or bool(propose_half),
        "rest_currently_legitimate_only_if": "core + idle-advance + propose-halves + forward-discovery-DRAWABLE ALL empty",
    }


def forward_discovery_law_status_line(register_path: Path | None = None) -> str:
    """One-line render of the above for the per-cycle supervisor log + the SM1
    morning note when it lands."""
    s = forward_discovery_law_status(register_path)
    drawable = ",".join(s["drawable_tracks"]) or "NONE"
    complete = ",".join(s["complete_tracks"]) or "NONE"
    propose = ",".join(s["propose_half_tracks"]) or "NONE"
    rest_ok = "REST-LEGITIMATE" if not s["drawable_nonempty"] else "must-draw"
    return (
        "TICK-NEVER-RESTS law: always-drawable lane "
        f"{'WIRED' if s['always_drawable_lane_wired'] else 'NOT-WIRED(!)'} | "
        f"forward-discovery drawable=[{drawable}] complete=[{complete}] | "
        f"propose-half open=[{propose}] | "
        f"{rest_ok} (rest legitimate only when core+idle+propose-half+forward-DRAWABLE all empty)"
    )


def authorized_set_enumeration() -> dict:
    """The WHOLE authorized set enumerated PER LEVEL with its drawable/empty verdict (director ruling
    2026-07-23, R17 class fix §2: 'Rest-legitimacy must enumerate the WHOLE authorized set -- core,
    idle-advance, propose-halves, site lane, discovery -- and publish that enumeration ... every time
    it rests. A lane-scoped proof can never again ground rest.'). Each value True = that level has
    drawable work (so rest is ILLEGITIMATE); False = empty/gated. Rest is legitimate ONLY when EVERY
    level is False. Each verdict is the SAME call the draw makes (independence, R15) -- never a constant.
    FAIL-SAFE TOWARD WORK: a per-level error reads True (drawable), so ambiguity FORBIDS rest -- the
    anti-idleness direction, matching `_is_drained_and_gated`'s own fail-safe. HARDEN is deliberately
    EXCLUDED: the RULE-0 HARDEN treadmill is what rest is legitimate INSTEAD of (it is the always-present
    at-target re-verify floor), so counting it would make rest impossible by construction."""
    none_drawn: frozenset = frozenset()

    def _safe(fn) -> bool:
        try:
            return bool(fn())
        except Exception:
            return True  # unsure -> assume work exists -> forbid rest (Rule 0 wins any tie)

    levels = [
        ("build", lambda: _maturity_map_draw_concurrent(exclude_stalled=True)),
        ("site", lambda: _site_lane_draw_concurrent(exclude_stalled=True, exclude_ids=none_drawn)),
        ("discover_frame", lambda: _idle_discover_frame_draw_concurrent(exclude_stalled=True, exclude_ids=none_drawn)),
        # SEVENTH CLASS (director ruling 2026-07-23): an open campaign with unfinished items forbids
        # rest -- enumerated as its own level so the whole-set proof includes it. A lane-scoped proof
        # can never again ground rest (the exact 14:03Z breach: SITE_V5 open, this level not counted).
        ("open_campaign", _open_campaign_draw),
        # RUNG 4 (director ruling 2026-07-23, WORK_IS_THE_DEFAULT): a declared fidelity defect that is
        # not in the drawable set is a contradiction. Its ABSENCE was today's state -- spike-tail
        # declared, this level uncounted, the whole-set proof read all-empty -> REST-LEGITIMATE.
        ("defect_backlog", _declared_defect_backlog_draw),
        ("backlog", _actionable_backlog_item),
        ("propose_half", _propose_half_draw),
        ("forward_discovery", _forward_discovery_draw),
        # RUNG 7 -- THE PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): the whole-set proof
        # must include whether the planner can still MINT from ratified goals. Its ABSENCE from this
        # enumeration was the 13:06Z breach -- "whole authorized set empty" published while ratified
        # goals had un-minted next steps. planner=Y => rest illegitimate (mint, don't rest).
        ("planner", _planner_rung_draw),
        # EIGHTH CLASS (director ruling 2026-07-27): a BLOCKED in_progress mint batch forbids rest.
        # Its ABSENCE from this enumeration was the 42h-stall breach -- "whole authorized set empty"
        # published with planner=. while 6 minted docs sat blocked in in_progress/. blocked_mints=Y
        # => rest illegitimate (escalate the blockers + mint around them, never rest quietly).
        ("blocked_mints", _blocked_mints_open),
        # GAP1 (director ruling PUBLISHED_GAPS_ARE_THE_BACKLOG 2026-07-28, BUILD_OPEN
        # `gap1_reader_contract_failopen_fix`): the published gap registers ARE the backlog, and
        # nothing read them as work. This detector reads the OPEN residue across all eight registers
        # from PRIMARY state (independent reader, invariant 1) so the whole-set rest proof includes
        # them -- Y => rest illegitimate while any register holds an open, un-triaged row.
        ("gap_register", _gap_register_open),
    ]
    return {name: _safe(fn) for name, fn in levels}


def authorized_set_enumeration_line() -> str:
    """One-line render of the whole-set enumeration for the per-cycle log + the daily self-note. Names
    EVERY level and whether it holds drawable work, so a rest is only ever published alongside proof that
    all six are empty -- the whole-set proof the ruling demands, never a lane-scoped one."""
    e = authorized_set_enumeration()
    drawable = [k for k, v in e.items() if v]
    parts = " ".join(f"{k}={'Y' if v else '.'}" for k, v in e.items())
    verdict = "REST-LEGITIMATE (whole authorized set empty)" if not drawable else f"MUST-DRAW: {','.join(drawable)}"
    line = f"AUTHORIZED-SET enumeration [{parts}] -> {verdict}"
    # EIGHTH CLASS enumeration-honesty (2026-07-27): whenever open mints exist, NAME each with its
    # blocking reason ON THE SAME LINE -- an enumeration that cannot see open mints is not an
    # enumeration. Never publish a bare "empty"/"drawable" verdict while items sit in in_progress/.
    blockers = open_mint_blockers()
    if blockers:
        detail = "; ".join(f"{n} -> {r}" for n, r in blockers)
        line += f" | OPEN MINTS ({len(blockers)}): {detail}"
    return line


def _first_graduation_line(body: str) -> str:
    """The track's own 'Candidate graduation' note (what would move to FRAME), extracted
    verbatim from its register section so the director [ACT] is GROUNDED, not invented. Falls
    back to a pointer if the track phrases it differently. Markdown emphasis stripped; truncated."""
    for pat in (r"[Cc]andidate graduation[^\n]*", r"graduation\s*=[^\n]*"):
        m = re.search(pat, body)
        if m:
            s = re.sub(r"[*`]", "", m.group(0)).strip()
            return (s[:220] + "…") if len(s) > 221 else s
    return "see this track's 'Candidate graduation' note in the register"


def forward_discovery_graduation_proposal(register_path: Path | None = None):
    """Build the batched director [ACT] for every DISCOVER-complete track (director console
    2026-07-22, R17 fail-open fix, decision 3). Returns (message, sorted_complete_ids) or None
    if no track is complete.

    GRADUATION IS DIRECTOR-RESERVED (the register's own discipline: a track graduates 'by explicit
    director steer'). This function only SURFACES, per complete track, its own candidate-graduation
    line (what would move to FRAME) and names what it needs from the director (his steer). It NEVER
    self-opens a track into FRAME/BUILD -- no atom is opened, no map level moves here."""
    path = register_path or FORWARD_DISCOVERY_REGISTER_PATH
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    # AWAITING = reached DISCOVER-complete but NOT yet ruled on by the director. A track the
    # director has already dispositioned (graduated/held/folded) has left the lane and must not be
    # re-surfaced -- else the [ACT] would keep asking for a call already made (director console
    # 2026-07-22: F1 graduated, F2 folded, F3/F5 held, F4 item-1 graduated -> awaiting becomes {}).
    awaiting = sorted(_forward_discovery_complete_ids(path) - _forward_discovery_dispositioned_ids(path))
    if not awaiting:
        return None
    titles = dict(_forward_discovery_tracks(path))
    sections = {m.group(1): m.group(2) for m in _FWD_SECTION_RE.finditer(text)}
    lines = [
        f"{tid} ({re.sub(r'[*_]', '', titles.get(tid, '')).strip()}): "
        f"{_first_graduation_line(sections.get(tid, ''))}"
        for tid in awaiting
    ]
    msg = (
        f"[ACT] Forward-discovery register: {len(awaiting)} track(s) now DISCOVER-complete and "
        "awaiting YOUR graduation call. The always-drawable lane has left them (rest is now "
        "legitimate, proof: authorized set empty at every level) -- I will NOT self-open any into "
        "FRAME/BUILD. Per track, candidate graduation (what would move to FRAME) -> what it needs "
        "from you = your explicit steer to graduate / hold / drop. Full detail: "
        "docs/design/FORWARD_DISCOVERY_REGISTER.md.\n" + "\n".join(f"  - {ln}" for ln in lines)
    )
    return msg, awaiting


def maybe_emit_graduation_proposal(register_path: Path | None = None, notify_fn=None) -> str | None:
    """Emit the batched graduation [ACT] ONCE per complete-set, from run_cycle's quiet-rest
    branch. Idempotency is the notify contract's own transition store (G-N1/R5), keyed on the
    sorted complete-id set: an unchanged all-complete state never re-pages (kills the every-4-min
    churn), while a NEW track completing later re-fires with the updated batch. Returns the sent
    message, or None if nothing is complete / the send was suppressed as unchanged.

    R15: keyed on the ACTUAL complete-id set (via `forward_discovery_graduation_proposal`), never a
    constant -- so the once-only guard tracks real state, and a set change is a real transition."""
    proposal = forward_discovery_graduation_proposal(register_path)
    if proposal is None:
        return None
    msg, complete_ids = proposal
    _notify = notify_fn or notify
    result = _notify(
        msg, kind="digest",
        transition_key="forward_discovery_graduation",
        state=",".join(complete_ids),
        headers={"Title": "[ACT] Forward-discovery graduation"},
    )
    if isinstance(result, str) and result.startswith("suppressed:"):
        return None
    return msg


def _current_head_hash() -> str | None:
    """The current repo HEAD (short), for the wedge detector's INDEPENDENCE cross-check.
    Read-only, fully defensive -- any git error returns None (the detector then keys on the
    failures list alone, never crashing the draw)."""
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except Exception:
        return None


def _head_commit_epoch() -> float | None:
    """HEAD's commit time as a unix epoch, for RUNG 1b's record-vs-tree freshness clause.
    Same defensive shape as _current_head_hash above -- any git error, an empty repo, or an
    unparseable stamp returns None, which every caller must treat as UNKNOWN (never as
    'nothing has landed')."""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            return None
        return float(r.stdout.strip())
    except Exception:
        return None


# The machine-generated commit subjects that are NOT evidence a seat advanced. Each is emitted by
# an unattended pipeline on its own cadence, whether or not any turn accomplished anything:
# `Auto-process run complete:` (process_run_complete's publish), and the chore(...) family the
# same publish path lands for re-rendered projections, provenance and liveness stamps. Counting
# these as progress is the FAIL-OPEN direction and the more dangerous one -- the publisher commits
# every cycle, so a stuck seat would go permanently unpaged. See _substantive_commits_since.
_HOUSEKEEPING_COMMIT_SUBJECT_PREFIXES = (
    "Auto-process run complete:",
    "chore(derived):",
    "chore(provenance):",
    "chore(liveness):",
)


def _substantive_commits_since(since_epoch: float) -> int | None:
    """How many NON-housekeeping commits have landed since `since_epoch`? None when UNKNOWABLE.

    This is the work-actually-happened signal the stuck escalation was missing. `_stuck_key` is
    built from the doorbell reason plus the resident staging list, and BOTH are structurally
    permanent: the CLASS_* docs re-render and `in_progress/` items are deliberately re-surfaced
    (CLAUDE.md), so that key can never close on its own. On 2026-08-24 it therefore paged
    "granting turns for ~60min with no state change" while ten commits landed between 09:16 and
    12:36 -- and the page is what made the director believe turns were being swallowed below tmux.
    A false page on a working machine is not a harmless false positive; it spends the one scarce
    resource (his attention) and misdirects it.

    Three-valued like _commit_is_ancestor: a git failure or an unparseable log returns None, which
    the caller must treat as a FAILED check. For an ALARM the safe failure is to page anyway --
    never to suppress on a check that did not run (R15 fail-silent)."""
    try:
        r = subprocess.run(
            ["git", "log", f"--since={int(since_epoch)}", "--pretty=%s"],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return sum(
        1 for line in r.stdout.splitlines()
        if line.strip() and not line.startswith(_HOUSEKEEPING_COMMIT_SUBJECT_PREFIXES)
    )


def _commit_is_ancestor(ancestor: str, descendant: str) -> bool | None:
    """Is `ancestor` reachable from `descendant`? True/False, or None when UNKNOWABLE.

    Three-valued on purpose: rc=0 is yes, rc=1 is no, and anything else (unknown object after a
    prune, a git failure, a timeout) is None -- which every caller must treat as "check
    unavailable" and therefore as a FAILED check (R15), never as a convenient False."""
    if not ancestor or not descendant:
        return None
    if "unknown" in (ancestor, descendant):
        return None
    try:
        r = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant],
                           cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    return {0: True, 1: False}.get(r.returncode)


def _gate_pass_supersedes_failures(last_tested: str, head: str | None, failures: list,
                                   green_ts: float | None = None) -> bool:
    """Has the gate recorded a pass STRICTLY AFTER the newest recorded failure, on HEAD's history?

    WHY THIS EXISTS (2026-08-12, observed): the independence cross-check above was exact HEAD
    equality (`.last_tested_hash == HEAD`), and that check is unsatisfiable in the one situation
    it most needs to answer. The gate's subject is a COMMIT; a green is stamped at the SHA the
    suite ran against. But publishing that green result itself lands a commit, and every other
    lane keeps landing too -- so by the time anyone reads the state, HEAD has moved past the SHA
    that passed and equality can never hold again.

    That made the detector SELF-PERPETUATING rather than merely stale: the phantom wedge fires a
    priority-zero doorbell, the tick it wakes does real work and commits it, HEAD moves one
    further from the recorded pass, and the next tick's draw is armed harder than the last. It
    ran to 201 consecutive "failures" over ~75h while publishing was healthy throughout -- the
    exact false-armed failure mode `record_publish_gate_outcome` had already fixed on its own
    side of this contract by keying on the MARKER's hash instead of HEAD. This is that same
    rule reaching the second consumer named in LAST_TESTED_HASH_CONTRACT.

    INDEPENDENCE IS PRESERVED, NOT TRADED AWAY (R15 anti-tautology). The verdict still needs two
    sources that cannot forge each other: the failure SHAs come from the publish-outcome state
    file, `.last_tested_hash` is written by exactly one writer -- the gate's own rc=0 -- and git
    ancestry supplies the ORDERING neither of them carries. A publisher that publishes nothing
    still cannot manufacture a green here, which is the property the whole contract rests on.

    ANCESTRY IS NO LONGER THE CLOCK (2026-08-20 -- the defect this paragraph exists to stop
    coming back). The two paragraphs above describe the shape the check had until the third
    consecutive RUNG-1 tick asked why the alarm kept firing on a gate that was green and
    publishing. The answer was the ORDERING INSTRUMENT, not either endpoint: this function asked
    `_commit_is_ancestor(newest_failure, last_tested)`, i.e. it read git ancestry as a proxy for
    "later in time". Since OPS3 (2026-08-14) the publish queue is drained NEWEST-MARKER-FIRST
    (`background_worker.py`: `order = list(reversed(pending))`, because every marker describes the
    same world-state and the newest dominates), and both SHAs being compared are marker subject
    commits -- so across one drain ancestry is ANTI-CORRELATED with time: the later a run is
    processed, the OLDER its commit. Observed live at 16:31Z on 2026-08-20: three failures
    ascending in `ts` (14:07/14:37/15:07Z) whose SHAs strictly DESCEND through history
    (81449dcb4 -> 8ba61d802 -> c24e81e07), and a green recorded at 15:34:03Z on 43766e01e, an
    ANCESTOR of all three. Twenty-seven minutes later by the clock, three commits earlier by
    ancestry, and the rung stayed armed. Full evidence:
    docs/staging/done/WORKER_FINDING_THE_WEDGES_ORDERING_INSTRUMENT_RUNS_BACKWARDS_SINCE_THE_
    QUEUE_BECAME_A_STACK_2026-08-20.md.

    So there are TWO questions and now TWO instruments, each answering the one it can:
      * ORDER -- `green_ts` (the recorded wall-clock of the gate's rc=0, from
        `.last_tested_green.json`) strictly greater than the NEWEST failure `ts`. `max()` over the
        rows, never the last row: the list's order is exactly what turned out not to be
        trustworthy, so the verdict must not depend on it.
      * PROVENANCE -- ancestry, kept for its other and still-valid job: the pass must be on
        HEAD's own history, because publishing happens from HEAD and a green on an abandoned
        branch says nothing about what HEAD will publish.

    FAIL-SAFE TOWARD DRAWING in every uncertain direction -- no recorded green clock (which is
    the state of every tree until the next green lands, deliberately), no usable failure `ts`, a
    green not strictly newer, a pass NOT on HEAD's history, or ancestry unknowable. The harmless
    error is drawing unwedge work one cycle too long; the harmful one is silencing the RUNG-1
    draw while publishing is genuinely frozen."""
    if not last_tested or not head:
        return False
    if green_ts is None:
        return False
    newest_failure_ts = None
    for f in failures:
        if not isinstance(f, dict):
            continue
        ts = f.get("ts")
        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            continue
        ts = float(ts)
        if newest_failure_ts is None or ts > newest_failure_ts:
            newest_failure_ts = ts
    if newest_failure_ts is None:
        return False
    # ORDER: strictly after, on the clock both sides actually carry.
    if not float(green_ts) > newest_failure_ts:
        return False
    # PROVENANCE: real history for the tree we are about to publish FROM.
    return _commit_is_ancestor(last_tested, head) is True


def _recorded_green_clock(
    last_tested: str,
    green_path: Path | None = None,
    last_tested_path: Path | None = None,
) -> float | None:
    """The wall-clock time the gate recorded its last GREEN, or None if there is no usable record.

    Written by exactly one writer, `process_run_complete._run_gate_in`, in the same rc=0 branch
    that writes `.last_tested_hash` -- so the independence the wedge cross-check rests on is
    unchanged: the failure rows come from the publish OUTCOME record, this comes from the gate's
    own return code, and a publisher that publishes nothing still cannot manufacture a green.

    THE TWO HALVES MUST DESCRIBE THE SAME GREEN, both ways round:
      * `sha` must equal the hash file's, so a sidecar left behind by an earlier green cannot
        lend its timestamp to a later hash (or the reverse, if either write ever half-lands).
      * the sidecar is looked for BESIDE the hash file whenever a caller redirects that path.
        A default that always pointed at the production file would make a redirected test read
        the real machine's green -- one half of the control reading a different tree from the
        other, which is the R15 pattern this whole repair is an instance of
        (`feedback_a_two_part_control_can_have_each_half_read_a_different_tree`).

    Absent, unreadable, malformed, wrong-sha or a non-numeric `ts` all return None, which the
    caller reads as "no green is claimed" and resolves toward DRAWING. An unavailable check is a
    FAILED check (R15)."""
    if not last_tested:
        return None
    gp = green_path
    if gp is None:
        gp = (Path(last_tested_path).parent / LAST_TESTED_GREEN_FILE.name
              if last_tested_path is not None else LAST_TESTED_GREEN_FILE)
    try:
        rec = json.loads(Path(gp).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict):
        return None
    ts = rec.get("ts")
    if isinstance(ts, bool) or not isinstance(ts, (int, float)):
        return None
    if str(rec.get("sha") or "").strip() != last_tested:
        return None
    return float(ts)


GATE_BLOCKING_TESTS_FILENAME = ".last_gate_blocking_tests.json"


def _live_gate_blocking_record(now=None, record_path=None):
    """(node_ids, git_hash) from the LIVE gate blocking record, or ([], None) for "I don't know".

    WHY THIS EXISTS (2026-08-20, `WORKER_FINDING_THE_WEDGE_STATE_LAUNDERS_THE_ALARMS_OWN_I_DONT_
    KNOW_INTO_A_CONFIDENT_STALE_ANSWER`). `process_run_complete.last_blocking_tests` has an
    explicit four-way honesty contract -- absent, unreadable, malformed and STALE all answer
    `([], None)`, because all four mean "this alarm does not know". That contract was in force and
    no reader asked it: `record_publish_gate_failure` copied the ANSWER into
    `.publish_gate_state.json` and dropped the WARRANT, and that copy carries no `ts` and no age
    bound of its own. So the one surface the RUNG-1 draw reads could not tell "the last gate's red
    was X" from "no gate has recorded a red since X was repaired" -- and on 2026-08-20 it spent
    three consecutive priority-zero ticks dispatching seven findings cited from a red that had
    been fixed an hour before the pin was taken.

    DELEGATION IS THE POINT, not an implementation convenience. Re-parsing the record here would
    be a second measurement of the same fact that can drift from the first (the mirror class this
    repo already catalogues); the honesty contract must live in exactly one place, and this asks
    it rather than restating it. The import is LAZY so the draw ladder does not pay the reader's
    import cost on every rung, and an unimportable/raising reader answers "I don't know" -- an
    unavailable check is a FAILED check (R15 fail-silent), and here failing means WITHHOLDING the
    citation, which is the safe direction: the draw still fires, it just stops naming suspects it
    cannot warrant.

    IT ASKS THE LEAF, NOT THE PUBLISHER (2026-08-21). This used to import
    `process_run_complete.last_blocking_tests`, and that ONE edge -- this module, which nearly
    every `tests/background/**` test imports, reaching the module that imports all five other
    publish-path modules -- put 36 harness self-governance test files inside the publish gate,
    measured on the real import graph. The contract still lives in exactly one place; that place
    is now `background/publish_gate_blocking_read.py`, a leaf that publishes nothing. DO NOT
    "simplify" this back to importing the publisher: `test_publish_scope.py::
    test_the_supervisor_does_not_import_the_publish_path` fails if the edge returns."""
    try:
        from background.publish_gate_blocking_read import read_blocking_record
    except Exception:  # pragma: no cover - import-time breakage of the reader's module
        return [], None
    # The production caller always DERIVES the path from the resolved state path (see
    # `_publish_gate_wedge_active`); this default is the standing location, resolved here rather
    # than read off the publisher's constant, which is the import this cut removes.
    if record_path is None:
        record_path = PROJECT_DIR / "docs" / "observability" / GATE_BLOCKING_TESTS_FILENAME
    try:
        return read_blocking_record(record_path, now=now)
    except Exception:  # pragma: no cover - defensive: never an exception into the draw ladder
        return [], None


def _blocking_record_is_about_head(record_hash: str | None, head: str | None) -> bool:
    """Was the live blocking record stamped at THE COMMIT THE DRAW IS ABOUT TO NAME?

    Prefix-tolerant because both sides are abbreviated independently (`git rev-parse --short`
    here, the marker's `Git:` line there) and the two abbreviations need not be the same length.
    Seven hex chars is git's own floor for an unambiguous short SHA. An absent or `unknown` hash
    answers False -- it cannot prove agreement, and the caller's job is to stop claiming one.

    WHAT THIS DELIBERATELY IS NOT: a citability test. See `_wedge_depth_clause`."""
    a = str(record_hash or "").strip()
    b = str(head or "").strip()
    if not a or not b or "unknown" in (a, b):
        return False
    shortest = min(len(a), len(b))
    if shortest < 7:
        return False
    return a[:shortest] == b[:shortest]


def _wedge_stale_payload_clause(named: int, cited: int) -> str:
    """The draw says out loud that it is WITHHOLDING a blocking payload it cannot warrant.

    Absent when there is nothing to withhold -- a clause that always prints cannot fail, and
    cannot be evidence that the withholding happened."""
    if named <= 0 and cited <= 0:
        return ""
    carried = []
    if named > 0:
        carried.append(f"{named} named blocking test(s)")
    if cited > 0:
        carried.append(f"{cited} cited finding(s)")
    return (
        " THE RECORDED BLOCKING PAYLOAD IS NOT CITABLE AND HAS BEEN WITHHELD: "
        f".publish_gate_state.json still carries {' and '.join(carried)} from an earlier failure, "
        f"but the live gate record ({GATE_BLOCKING_TESTS_FILENAME} -- the only copy that carries a "
        "freshness stamp) answers 'I do not know': absent, unreadable, malformed, or older than "
        "its age bound. Those names are NOT reproduced here, because a name copied out of a "
        "record that can no longer warrant it may be a red that has since been repaired. "
        "ENUMERATE AT HEAD before suspecting anything."
    )


def _wedge_no_test_judged_clause(failures, payload_citable: bool) -> str:
    """Countermand "FIX the red test" when the RECORD ITSELF says no test was ever judged.

    The draw's fixed opening is written for the common wedge -- a red in the publish scope -- and
    for that wedge it is right. It is not conditional, so it is also what a worker reads when the
    publisher recorded `commit_did_not_land`: scoped suite GREEN, commit refused by a NON-TEST
    pre-commit gate (orphan-ratchet, the finding-class consolidation gate, the level-promotion
    gate). Following it costs a full ~10-minute suite run and ends green, which reads as "the
    wedge cleared itself" rather than "I looked in the wrong place" -- so the actual refusing gate
    is never named and the next cycle refuses again. Four cycles on 2026-08-27; twelve on 08-25.

    WHY `kind` AND NOT THE PROSE: `reason` is a human sentence assembled per call site and would
    have to be pattern-matched, which is the mirror class -- a second derivation of a fact that
    already has a field. `kind` is the field, the publisher's three sites set it deliberately for
    this exact reader (see WEDGE_KINDS_NO_TEST_JUDGED), and it is a closed set.

    FAIL-SAFE DIRECTION IS TOWARD THE OLD PROSE, deliberately, and this is the whole safety
    argument. Silence here leaves the draw saying "run the suite": expensive and sometimes
    misdirected, never unsafe. Printing this clause when a test IS red would tell a worker not to
    look for it, which is. So every gate is a reason to stay quiet:
      * a citable blocking payload (`payload_citable`) -- a named red outranks any kind label;
      * any in-window failure whose kind is NOT in the no-test-judged set, including a missing,
        empty, non-string or unrecognised one. A state file written before `kind` existed, or by
        a future writer with a fourth kind, says nothing and is heard as nothing.
    So the clause needs UNANIMITY among the in-window failures, not a majority and not the last
    one: a wedge that is half test-regression is a wedge with a red in it.

    Returns "" or a leading-space clause. Never raises -- a malformed `failures` is not-unanimous
    by construction, because a non-dict entry has no readable kind."""
    if payload_citable or not failures:
        return ""
    kinds = []
    for f in failures:
        kind = f.get("kind") if isinstance(f, dict) else None
        if not isinstance(kind, str) or kind not in WEDGE_KINDS_NO_TEST_JUDGED:
            return ""
        kinds.append(kind)
    named = ", ".join(sorted(set(kinds)))
    return (
        " NO TEST WAS EVER JUDGED IN THIS EPISODE -- THE OPENING INSTRUCTION ABOVE DOES NOT APPLY. "
        f"Every one of the {len(kinds)} in-window failures is recorded by the publisher as "
        f"`{named}`, which is the publisher stating that its OWN scoped suite did not return a "
        "red: the commit was refused by a non-test pre-commit gate, or no verdict was reached "
        "before a clock expired. There is no red test to find, and running the gate's pytest argv "
        "will cost ~10 minutes and come back green -- which looks like a self-clearing wedge and "
        "is how this episode repeats. DO THIS INSTEAD: read the refusing gate's own banner in the "
        "publisher log tail (`docs/observability/sim-runner-log.md`, the lines just above "
        "`Commit/push failed`) -- the pre-commit chain prints which hook refused and what repairs "
        "it. Then run THAT gate alone against the working tree to confirm it still refuses at "
        "HEAD before repairing anything; the hook chain stops at the first refusal, so a second "
        "gate may be behind it."
    )


def _publish_gate_wedge_active(
    now: float | None = None,
    head: str | None = None,
    state_path: Path | None = None,
    last_tested_path: Path | None = None,
    green_path: Path | None = None,
) -> str | None:
    """RUNG 1 (PRIORITY ZERO) detector: is the publish gate WEDGED and older than 60 minutes?

    Returns an unwedge draw message if so, else None. This is the highest rung -- a wedged publish
    gate blocks ALL publishing, so it outranks every product/HARDEN lane (director rulings
    UNWEDGE_PUBLISH_PRIORITY_ZERO 2026-07-23 + WEDGE3_AND_RUNG1_MECHANISE 2026-07-24). Mechanised
    because the prose rule was CONSUMED-NOT-ABSORBED twice: 2h17m of alarms fired into tick silence
    on both 2026-07-23 and 2026-07-24 because no draw rung ever surfaced 'go fix the failing gate'.

    Signal source: process_run_complete.py's .publish_gate_state.json (`failures` list trimmed to a
    1h window and CLEARED on the next clean publish; `alerted_at`/`wedge_since` timestamps) plus
    .last_tested_hash, whose write rule is stated in exactly one place --
    `process_run_complete.LAST_TESTED_HASH_CONTRACT`. Read it before changing what this branch
    treats as "a pass at HEAD": the cross-check below is only independent while that rule holds,
    and the composition is pinned in tests/background/test_publish_gate_subject_is_head.py.

    Two-part predicate:
      * WEDGED (precise, so no phantom draw): `failures` has >= PUBLISH_GATE_WEDGE_MIN_FAILURES
        entries (a sustained wedge fails every ~10min, never a lone flake), AND -- INDEPENDENCE
        (R15, anti-tautology) -- an INDEPENDENT signal confirms it: the gate has recorded NO pass
        that SUPERSEDES those failures. A pass counts as superseding when `.last_tested_hash` is
        HEAD itself, or (2026-08-12) when it names a commit on HEAD's history whose RECORDED
        GREEN CLOCK is strictly newer than the newest recorded failure `ts` -- because publishing
        a green result is itself a commit, so exact HEAD equality is unsatisfiable precisely when
        the gate is healthy and busy. Either way the failures are stale and this returns None.
        The clock is `.last_tested_green.json`, NOT git ancestry: ancestry was the clock until
        2026-08-20 and it runs backwards across a stack-drained publish queue -- see
        `_gate_pass_supersedes_failures`, which carries the evidence.
      * OLDER THAN 60 MIN (generous, fail-safe TOWARD drawing): age = now - the OLDEST available
        wedge timestamp (wedge_since if the writer stamped it, else alerted_at, else the earliest
        in-window failure ts). MIN() maximises measured age because the harmful failure mode is NOT
        drawing unwedge work while wedged; drawing it when marginal is cheap.

    FAIL-SAFE: an unreadable/absent/malformed state file returns None (no phantom wedge -- the lower
    rungs still draw real work), never an exception into the draw ladder. R15-proven both ways
    (fires on this morning's exact recorded state; silent on a passed/empty gate) in
    test_publish_gate_wedge_draw.py."""
    now = time.time() if now is None else now
    sp = state_path or PUBLISH_GATE_STATE_FILE
    try:
        state = json.loads(Path(sp).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    failures = state.get("failures") or []
    if not isinstance(failures, list) or len(failures) < PUBLISH_GATE_WEDGE_MIN_FAILURES:
        return None
    # INDEPENDENCE (R15): cross-check against .last_tested_hash -- keyed on real cross-process state,
    # never the same source the failures came from. A pass at HEAD => stale failures => no draw.
    head = head if head is not None else _current_head_hash()
    lp = last_tested_path or LAST_TESTED_HASH_FILE
    try:
        last_tested = Path(lp).read_text().strip()
    except OSError:
        last_tested = ""
    if head and last_tested and head == last_tested:
        return None
    # ...and the same question asked in the form the gate can actually answer: a green is stamped
    # at the SHA the suite ran, but publishing it moves HEAD past that SHA, so equality alone
    # leaves the detector armed forever on a healthy pipeline. See the helper's docstring.
    # The clock is looked for BESIDE the RESOLVED hash path, never beside the module default --
    # so every caller and every test that redirects one half redirects both, and the two halves
    # of this control can never read different trees. See `_recorded_green_clock`.
    green_ts = _recorded_green_clock(last_tested, green_path=green_path, last_tested_path=lp)
    if _gate_pass_supersedes_failures(last_tested, head, failures, green_ts):
        return None
    # AGE: oldest available wedge signal. Fail-safe toward drawing.
    ts_candidates = [float(f["ts"]) for f in failures
                     if isinstance(f, dict) and isinstance(f.get("ts"), (int, float))]
    for key in ("wedge_since", "alerted_at"):
        v = state.get(key)
        if isinstance(v, (int, float)):
            ts_candidates.append(float(v))
    if not ts_candidates:
        return None
    age = now - min(ts_candidates)
    if age < PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS:
        return None
    age_min = int(age // 60)
    last_reason = ""
    if isinstance(failures[-1], dict):
        last_reason = str(failures[-1].get("reason", ""))
    # ALARM->DIAL (2026-08-09, DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH draw 2b): the alarm
    # enumerated the findings filed against this wedge into the state file; the draw names them
    # as the work. This is what "an alarm raises its own cure's draw priority" means concretely --
    # RUNG 1 is already priority zero, so a finding named here has been lifted out of the staging
    # backlog (where it loses to feature work, as the cure for the 7h episode of 2026-08-08 did)
    # and into the highest rung of the ladder. Bounded and defensive: a malformed list is ignored.
    #
    # ...BUT ONLY IF THE RECORD STILL WARRANTS IT (2026-08-20, the laundering finding). The
    # blocking payload below -- `cited_findings`, `blocking_tests`, `red_census`, `total_red` --
    # is a CACHE of `last_blocking_tests()`, written once per failure and never re-derived
    # between them. The cache must AGREE WITH the live record, not substitute for it: when the
    # record answers "I don't know", its own contract says every reader must hear that, and this
    # is the reader. The record is looked for BESIDE THE RESOLVED state path, never beside a
    # module default, so a test that redirects one half redirects both and the two halves of this
    # control can never read different trees -- the same rule as `_recorded_green_clock`.
    live_nodes, live_hash = _live_gate_blocking_record(
        now=now, record_path=Path(sp).parent / GATE_BLOCKING_TESTS_FILENAME)
    payload_citable = bool(live_nodes)
    cited = state.get("cited_findings")
    cited = [str(f) for f in cited][:8] if isinstance(cited, list) else []
    named_blocking = len(state.get("blocking_tests") or [])
    stale_payload_clause = "" if payload_citable else _wedge_stale_payload_clause(
        named_blocking, len(cited))
    if not payload_citable:
        cited = []
    cure_clause = (
        " FILED FINDINGS ALREADY HOLDING THE SUSPECTS -- draw these FIRST, before any product or "
        "HARDEN work, and dispose of each (fix, or re-freeze with provenance): "
        + ", ".join(cited) + "."
    ) if cited else ""
    episode = state.get("episode_failures")
    episode_clause = (
        f" EPISODE: {episode} consecutive failures since the wedge began -- this is not a fresh hour."
        if isinstance(episode, int) and episode > len(failures) else ""
    )
    # THE DRAW MUST BE TOLD THE DEPTH, NOT JUST THE FIRST RED (2026-08-14, the 252-cycle wedge).
    # The gate runs fail-fast, so the node ids above are one red unless the report-only census
    # ran. Without this clause the drawn worker reads "BLOCKING TEST: x" and repairs x -- which
    # is correct, and was correct five times running while the wedge stood. Defensive by the same
    # rule as `cited`: anything but an explicit COMPLETE/PARTIAL reads as unknown depth, because
    # a state file written before this field existed knew only the fail-fast red.
    # DEPTH IS PART OF THE SAME CACHED PAYLOAD, so it falls with it: an uncitable record cannot
    # substantiate "the census enumerated the WHOLE red set at this HEAD" either, and
    # `_wedge_depth_clause`'s own default for an unsubstantiated claim is a loud DEPTH UNKNOWN.
    depth_clause = _wedge_depth_clause(
        state.get("red_census") if payload_citable else None,
        state.get("total_red") if payload_citable else None,
        named_blocking if payload_citable else 0,
        record_hash=live_hash if payload_citable else None,
        head=head)
    # WHAT THE DRAW COULD NOT SEE UNTIL NOW (2026-08-17): that the world moved after the reading
    # was taken. Both are TEXT ONLY and neither can return None -- see their docstrings. They come
    # BEFORE `depth_clause` because the in-flight one countermands that clause's own instruction.
    superseded_clause = _wedge_superseded_hash_clause(failures, head)
    in_flight_clause = _wedge_in_flight_clause(_live_publish_gate_runs())
    # ...and that the reading was never ABOUT a test (2026-08-27). Grouped with the other two
    # countermands and placed before `depth_clause` for the same reason they are: that clause's
    # own default ("run the gate's argv without `-x`") is an instruction to go and enumerate reds,
    # and this one is the statement that there are none to enumerate.
    no_test_judged_clause = _wedge_no_test_judged_clause(failures, payload_citable)
    # AND IT REPLACES THAT CLAUSE RATHER THAN ARGUING WITH IT. Two instructions in one payload,
    # the contradicting one LAST, is how the 2026-08-27 draw read: "there is no red" followed by
    # "enumerate the reds -- run the gate's argv without `-x`", which is the ~10-minute run this
    # clause exists to prevent. Safe to drop because it is provably the SAME string every time
    # this fires: the clause requires `payload_citable` False, which already forces census and
    # total to None/0 above, so `_wedge_depth_clause` can only be returning its DEPTH UNKNOWN
    # default. Nothing that could name a red is being suppressed -- pinned by
    # `test_depth_unknown_is_the_only_clause_the_countermand_can_displace`.
    if no_test_judged_clause:
        depth_clause = ""
    return (
        "PUBLISH-GATE WEDGE self-refill (RUNG 1, PRIORITY ZERO -- director rulings "
        "UNWEDGE_PUBLISH_PRIORITY_ZERO 2026-07-23 + WEDGE3_AND_RUNG1_MECHANISE 2026-07-24): the "
        f"publish gate has been FAILING for ~{age_min} min ({len(failures)} failures in-window, no "
        f"pass at HEAD {head or '?'}) and is BLOCKING ALL publishing -- this OUTRANKS every product/"
        "HARDEN lane. DIAGNOSE the failing test with evidence (R9): run the exact gate "
        "`SIM_FAST_MODE=1 python3 -m pytest tests/ -m 'not operational' <heavy-ignores>` (see "
        "background/process_run_complete.py::publish_gate_pytest_argv), FIX the red test, flush the "
        "run_complete queue, and R11-verify the folded live site. NTFY the director the one-line "
        f"cause.{superseded_clause}{in_flight_clause}{no_test_judged_clause}"
        f"{stale_payload_clause}{depth_clause}"
        f"{episode_clause}{cure_clause}"
        f" Last recorded failure: {last_reason}"
    )


def _wedge_depth_clause(census, total_red, named, record_hash=None, head=None) -> str:
    """How many tests are red behind the fail-fast verdict -- or an explicit statement that the
    draw does not know. Split out so it can be put on trial directly (R15: a control's scope must
    be inspectable), and so the three answers are one function rather than three format strings.

    UNKNOWN IS THE DEFAULT AND IT IS LOUD. "Fix the named test" is what a worker does with a
    fail-fast node id, and it is right; it is also exactly what happened on each of five
    consecutive unwedge ticks against one stack of five reds. The clause the worker needs is not
    "here is a test", it is "this may be one layer of several".

    ...AND IT MUST NAME THE COMMIT IT COUNTED ON (2026-08-21, observed live). This clause said
    "red at THIS HEAD" unconditionally, while the count comes from a record stamped at whatever
    commit the gate cycle carried. At HEAD `e778b4ac0` the record named `f983f074c`, 42 commits
    back -- with `4b171cee8`, which repairs four of the five tests it named, sitting between them.
    A worker reading "5 tests are red at this HEAD" starts from "find the red"; the true state was
    "four of these were fixed two commits ago". `_publish_gate_wedge_active` had the hash in hand
    and dropped it into `_live_hash` -- the leading underscore was the defect, written down.

    THE REPAIR IS TEXT, NOT SUPPRESSION, and that is the whole design decision. Withholding the
    payload on a hash mismatch was the first draft and it is WRONG: the record's `git_hash` is the
    MARKER's commit, not the checkout the suite ran in (the two-clocks split, 14219094c), so it
    differs from HEAD on almost every healthy cycle. Suppressing on that would silence the suspect
    list permanently -- fail-closed into useless, which R15 counts as a failed control, not a safe
    one. So the count still prints in full; only the false claim about WHICH TREE it describes is
    withdrawn, on the same "deliberately weaker than a verdict" principle as
    `_wedge_superseded_hash_clause`. An unknown/absent hash keeps the old wording: it cannot prove
    disagreement either, and inventing a caveat is its own noise."""
    total = total_red if isinstance(total_red, int) and total_red > 0 else named
    # WHERE the count was measured, and it only ever WEAKENS the claim -- never the count itself.
    if record_hash and head and not _blocking_record_is_about_head(record_hash, head):
        where = (f"at `{record_hash}`, NOT at HEAD `{head}` (the gate record names that commit; "
                 f"run `git log --oneline {record_hash}..{head}` -- a fix may already have landed, "
                 "so re-check each before repairing it)")
    else:
        where = "at this HEAD"
    if census == "complete":
        if total <= 1:
            return (f" DEPTH: the report-only census enumerated the WHOLE red set {where} and "
                    "it is ONE test -- repairing it should clear the wedge.")
        return (f" DEPTH: {total} tests are red {where} -- the report-only census enumerated "
                "the WHOLE set. This is a STACK, not one defect: fix them TOGETHER in this tick. "
                "Repairing the named one and re-running hands the next layer to the next tick, "
                "which is how the 2026-08-14 wedge ran 252 cycles.")
    if census == "partial":
        return (f" DEPTH: AT LEAST {total} tests are red {where} (the census hit its own "
                "failure bound, so there may be more). Treat this as a stack.")
    if census == "hook_chain":
        # Written by `process_run_complete._record_commit_refusal_reds`: the publisher's own
        # scoped gate was GREEN and the pre-commit HOOK CHAIN refused. The chain stops at the
        # first refusing hook, so this set is complete for that hook and silent about the rest.
        return (f" DEPTH: {total} test(s) are red {where}, named by the PRE-COMMIT HOOK CHAIN "
                "that refused the publish commit -- the publisher's own scoped gate was GREEN, "
                "so do NOT go looking for a red in the publish scope. The hooks behind the "
                "refusing one never ran; treat this as a stack and fix them together.")
    return (" DEPTH UNKNOWN: the gate is fail-fast and no report-only census is on record, so the "
            "test named above may be one red of several. Enumerate before assuming it is the only "
            "one -- run the gate's argv without `-x`.")


def _wedge_superseded_hash_clause(failures, head, is_ancestor=None) -> str:
    """Has HEAD moved past the commit EVERY in-window failure was recorded at?

    WHY THIS IS TEXT AND NOT A `return None` (2026-08-17, the finding that specified this repair,
    `WORKER_FINDING_THE_WEDGE_DRAW_NEVER_READS_THE_COMMIT_ITS_OWN_FAILURE_RECORDS_NAME`). When the
    failures name an OLD commit there is still genuinely no green at HEAD, so the draw must keep
    firing: R15 and Rule 0 both point at failing safe TOWARD drawing, and a repair that suppressed
    the draw here would blind RUNG 1 to any wedge that survives a commit -- strictly worse than
    saying nothing. The defect this closes is in what the draw SAYS. "No pass at HEAD" reads as
    "failing at HEAD", so a worker acting on it at priority zero starts from "find the red" when
    the true state can be "the fix landed 20 minutes ago and its verification is running now".
    That misread has now cost two consecutive priority-zero ticks (11:08 and 11:16 UTC on
    2026-08-17), which is what moved this from QUEUED to built.

    The independence question this does NOT answer: whether a fix landed. It cannot -- a commit
    between the failure and HEAD may be unrelated. It reports the ORDERING and hands the reader
    the one command that settles it. That is deliberately weaker than a verdict.

    UNKNOWN PRINTS NOTHING, on the same defensive rule as `cited`/`depth_clause`: a record with no
    `git_hash`, a MIXED set (some failures at one commit, some at another -- the wedge outlived a
    commit, which is the case this must never soften), a hash equal to HEAD, or git unable to
    answer the ancestry all read as unknown and change the message not at all."""
    is_ancestor = _commit_is_ancestor if is_ancestor is None else is_ancestor
    if not head or not failures:
        return ""
    hashes = set()
    for f in failures:
        if not isinstance(f, dict):
            return ""
        gh = str(f.get("git_hash") or "").strip()
        if not gh or gh == "unknown":
            return ""
        hashes.add(gh)
    # A MIXED SET IS THE DANGEROUS ONE, so it reads as unknown: failures at more than one commit
    # mean the wedge SURVIVED a commit, and that is precisely when the reader must not be told
    # "HEAD has moved on, maybe it's fixed".
    if len(hashes) != 1:
        return ""
    only = hashes.pop()
    if only == head:
        return ""
    if is_ancestor(only, head) is not True:
        return ""
    return (
        f" HEAD HAS MOVED SINCE EVERY RECORDED FAILURE: all {len(failures)} of them were recorded "
        f"at `{only}`, which is a STRICT ANCESTOR of HEAD `{head}` -- so a fix may ALREADY have "
        f"landed and none of these failures has been reproduced at the tree you would be "
        f"diagnosing. Run `git log --oneline {only}..{head}` FIRST. This does not mean the wedge "
        "is over (there is still no recorded green at HEAD, which is why this draw fired) -- it "
        "means the red you are being sent to find may no longer exist."
    )


def _live_publish_gate_runs(ps_fn=None) -> list[dict]:
    """Live `process_run_complete.py` processes as [{pid, elapsed_s}], newest-agnostic.

    UNAVAILABLE READS AS NONE, and that direction is the safe one here -- unlike a control, this
    feeds a WARNING that suppresses part of the remedy. Failing to warn leaves the draw exactly as
    it was before this existed; warning falsely would tell a worker not to run the gate during a
    real wedge, which is the harmful direction. `ps` missing, erroring, or timing out -> []."""
    try:
        if ps_fn is not None:
            out = ps_fn()
        else:
            out = subprocess.run(
                ["ps", "-eo", "pid,etimes,args"],
                capture_output=True, text=True, timeout=10,
            ).stdout
    except Exception:
        return []
    runs = []
    for line in (out or "").splitlines():
        if "process_run_complete.py" not in line or "grep" in line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            runs.append({"pid": int(parts[0]), "elapsed_s": int(parts[1])})
        except ValueError:
            continue
    return runs


def _wedge_in_flight_clause(runs) -> str:
    """Say a gate run is ALREADY RUNNING, and countermand the remedy that would race it.

    The draw's own instruction is "run the gate's argv without `-x`" (see `_wedge_depth_clause`'s
    UNKNOWN branch). That instruction is correct when nothing is running and ACTIVELY HARMFUL when
    something is: this box is a 15 GB cgroup, not the 32 GB of physical RAM (cf.
    `WORKER_FINDING_THE_CEILING_WAS_SIZED_FROM_A_PROCESS_AND_APPLIED_TO_A_CGROUP_2026-08-11`), so a
    second full suite beside a live one can OOM-kill the real gate -- and that kill is recorded as
    a `test_regression`, i.e. the next failure in the episode, MANUFACTURED by the instruction
    meant to diagnose it (`WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10`).
    The clause must therefore not merely inform; it must withdraw the instruction in words."""
    if not runs:
        return ""
    r = max(runs, key=lambda x: x.get("elapsed_s", 0))
    mins = int(r.get("elapsed_s", 0)) // 60
    return (
        f" A GATE RUN IS IN FLIGHT RIGHT NOW: process_run_complete.py PID {r.get('pid')}, running "
        f"~{mins} min. DO NOT run the gate's argv beside it -- a second full suite on this 15GB "
        "cgroup can OOM the live one, and that kill is recorded as the episode's next failure, so "
        "the diagnosis would MANUFACTURE the red it went looking for. The 'enumerate without `-x`' "
        "instruction above is SUSPENDED while this line is present: wait for this run and read its "
        "outcome instead."
    )


def _operational_red_stale_record_prefix(state: dict, head_time_fn=None, head_hash_fn=None) -> str:
    """RUNG 1b's record-vs-tree freshness clause, factored out so it can be put on trial directly
    (R15: a control's scope must be inspectable). Returns the RE-RUN-FIRST prefix when HEAD was
    committed strictly AFTER the signal record was written, else "".

    Three-valued in effect, and the UNKNOWN branch is the important one: no `last_run_ts`, an
    unparseable stamp, or git unavailable all return "" -- the draw is printed UNCHANGED and
    UNSOFTENED. An unavailable check is a failed check (R15), and the failure mode of this one must
    be 'diagnose from scratch', never 'assume a fix landed'."""
    try:
        record_ts = float(state.get("last_run_ts"))
    except (TypeError, ValueError):
        return ""
    head_ts = (head_time_fn or _head_commit_epoch)()
    if head_ts is None or not (float(head_ts) > record_ts):
        return ""
    sha = (head_hash_fn or _current_head_hash)() or "HEAD"
    age_min = int(max(0.0, float(head_ts) - record_ts) // 60)
    return (
        f"RE-RUN THE SIGNAL FIRST -- this RED record was written {age_min} min BEFORE the current "
        f"HEAD ({sha}) was committed, so a fix may already have landed and the record simply has not "
        "been re-read (the check is HOURLY). Run "
        "`python3 -c \"from background.process_run_complete import run_operational_layer_signal as r; "
        "r(force=True)\"` and, if it comes back GREEN, the draw is discharged: say so and move to the "
        "next rung. Only if it is STILL RED does the diagnosis below apply. || "
    )


def _operational_red_persistent_draw(
    now: float | None = None,
    state_path: Path | None = None,
    head_time_fn=None,
    head_hash_fn=None,
) -> str | None:
    """RUNG 1b (PRIORITY ZERO) detector: has the operational-layer signal been RED for MORE than
    OPERATIONAL_RED_DRAWABLE_THRESHOLD consecutive checks? Returns a remediation draw message if so,
    else None.

    Director console P0 (2026-07-25): a persistent operational RED is priority-zero drawable work,
    not an alarm to admire. The overnight incident this mechanises: the operational-layer signal was
    RED for 13 consecutive hourly checks (an orphaned systemd unit for a retired daemon failing the
    anti-drift reconcile, plus a pixel-verification capability regression), and the ONLY response was
    an hourly page -- no draw rung surfaced 'go fix the red daemon-lifecycle suite', so the tick
    rested beside it all night (consumed-not-absorbed; the exact class R17/MAKE_IT_STICK forbids).

    Signal source: process_run_complete.py's .operational_layer_signal.json ({consecutive_red,
    consecutive_green, last_result, ...}) -- WRITTEN by run_operational_layer_signal on each hourly
    deadman check, READ-ONLY here (local disk read only, per the module doctrine).

    Predicate (fail-safe TOWARD drawing -- a false draw only costs one diagnostic turn that finds
    nothing and rests, self-correcting; a false SILENCE is the overnight stall):
      * last_result in ('red', 'red_blocked') -- the signal's own verdict; a green result never
        draws even if a stale counter lingers. 'red_blocked' (2026-08-20) is a run that never
        REACHED the suite because collection was interrupted: still unmonitored, so still
        drawable, but it draws a DIFFERENT message (repair the import, not the daemons) -- see
        the branch below, AND
      * consecutive_red > OPERATIONAL_RED_DRAWABLE_THRESHOLD (past PAGING, which fires at 2 -- so
        this is the ESCALATION when paging did not get it fixed: >3 consecutive = drawable).

    Note the drawable bar (>3) is deliberately HIGHER than the paging bar (2, OPERATIONAL_LAYER_
    PERSISTENT_RED_THRESHOLD in process_run_complete.py): page first, and only mechanise into a draw
    once the alarm has demonstrably not been actioned across several checks.

    FAIL-SAFE: an unreadable/absent/malformed state file returns None (no phantom draw -- the lower
    rungs still draw real work), never an exception into the draw ladder. R15-proven both ways (fires
    on the overnight consecutive_red=13/red state; silent on green, on a below-threshold red, and on
    a malformed file) in test_operational_red_persistent_draw.py.

    THE RECORD IS NOT REQUIRED TO BE CURRENT (2026-08-14, observed live). The signal is re-read on an
    HOURLY cadence, so between a fix landing and the next check the record still says RED -- and this
    rung, reading the record alone, keeps handing PRIORITY-ZERO to work that is already done, above
    every other lane, for up to an hour. It happened the tick after `fb1493702` fixed the 9-hour red:
    the record was written 15:38, the fix committed 16:11, and the very next draw was the same
    already-discharged diagnosis.

    The fix is NOT to suppress a stale draw. The stated fail-safe direction is toward drawing, and
    the record freezes red exactly when the deadman DIES -- so 'old record => stay silent' would
    reintroduce the overnight fail-silent this rung exists to kill. Instead the draw still fires and
    the message CHANGES: when HEAD was committed AFTER the record was written, it leads with RE-RUN
    THE SIGNAL FIRST (naming the sha), because re-running is ~10 minutes and a fresh diagnosis of an
    already-fixed red is a whole wasted tick. UNKNOWN either way (git unavailable, no `last_run_ts`)
    prints the base message unchanged -- an unavailable check never gets to soften the draw."""
    now = time.time() if now is None else now
    sp = state_path or OPERATIONAL_LAYER_SIGNAL_FILE
    try:
        state = json.loads(Path(sp).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    # 'red_timeout' (2026-08-21) joins the drawable set for the same reason 'red_blocked' did:
    # the layer is UNMONITORED and the stated fail-safe direction here is toward drawing. Adding
    # the value to `process_run_complete` without adding it here would have swapped a retry storm
    # for a fail-SILENT -- the exact trade this rung exists to refuse.
    if state.get("last_result") not in ("red", "red_blocked", "red_timeout"):
        return None
    try:
        consecutive_red = int(state.get("consecutive_red") or 0)
    except (TypeError, ValueError):
        return None
    if consecutive_red <= OPERATIONAL_RED_DRAWABLE_THRESHOLD:
        return None
    # A BLOCKED signal still draws -- it is unmonitored, which is the state this rung exists
    # for -- but it must not draw the DAEMON diagnosis. `red_blocked` means pytest was
    # interrupted during COLLECTION, so no operational test ran and nothing about the daemons
    # has been shown to be wrong; the repair is the import error. Sending the worker to
    # "regenerate the process-set manifest" is what cost 23 pages on 2026-08-20
    # (WORKER_FINDING_A_SALVAGE_PARKED_THE_PRODUCER_HALF...). Silence is NOT the alternative:
    # the stated fail-safe direction here is toward drawing.
    # A TIMED-OUT signal draws its own diagnosis for the same reason a BLOCKED one does: the
    # suite ran and did not finish, so nothing about the daemons has been shown to be wrong and
    # the daemon message would send the reader to the wrong place. The question here is a
    # DURATION, and on 2026-08-21 the answer was that this check was the box contention that
    # starved the publish gate for 34 hours -- so the draw names the cadence decision, not a bug.
    if state.get("last_result") == "red_timeout":
        return _operational_red_stale_record_prefix(state, head_time_fn, head_hash_fn) + (
            "OPERATIONAL-LAYER TIMED-OUT self-refill (RUNG 1b, PRIORITY ZERO): the "
            f"operational-layer signal has TIMED OUT for {consecutive_red} consecutive checks -- "
            "it ran and did not finish, so it has produced NO verdict and the operational layer "
            "is UNMONITORED. This is NOT a daemon-lifecycle defect: do NOT hunt a capability "
            "regression, nothing about the daemons has been shown to be broken. It is a DURATION "
            "question, and it is expensive -- this check holds the box for its full timeout every "
            "time it fails this way, which is what starved the publish gate on 2026-08-21. "
            "DECIDE THE CADENCE (director console 2026-08-21: 'what genuinely must run before a "
            "publish and what belongs somewhere else entirely, on its own cadence'): measure how "
            "long `operational_layer_pytest_argv()` actually needs, then either give it a budget "
            "it can meet or narrow what it runs. Raising the timeout to fit is the move that "
            "produced this state -- prefer narrowing. Record the decision and NTFY the director."
        )
    if state.get("last_result") == "red_blocked":
        blocked = [str(p) for p in (state.get("blocked_by") or [])]
        named = ("\n".join("  - " + p for p in blocked) if blocked
                 else "  (the state file names none -- re-run the signal to list them)")
        return _operational_red_stale_record_prefix(state, head_time_fn, head_hash_fn) + (
            "OPERATIONAL-LAYER BLOCKED self-refill (RUNG 1b, PRIORITY ZERO): the operational-layer "
            f"signal has failed to RUN for {consecutive_red} consecutive hourly checks. pytest was "
            "interrupted during COLLECTION, so the marker expression never selected anything and "
            "NO operational test executed. This is NOT a daemon-lifecycle defect -- do NOT "
            "regenerate the process-set manifest or hunt a capability regression; nothing about "
            "the daemons has been shown to be broken. The operational layer is UNMONITORED until "
            f"these files import cleanly:\n{named}\n"
            "REPAIR THE IMPORT (R4: the nearest working analogue is the same file importing "
            "cleanly at HEAD -- `git status` these paths first; a half-landed rename or a salvage "
            "that parked a producer and left its consumers is the usual cause). Then confirm with "
            "`python3 -m pytest tests/ -q --collect-only` that collection is clean, re-run the "
            "signal, and NTFY the director the cause."
        )
    return _operational_red_stale_record_prefix(state, head_time_fn, head_hash_fn) + (
        "OPERATIONAL-LAYER PERSISTENT-RED self-refill (RUNG 1b, PRIORITY ZERO -- director console "
        "2026-07-25): the operational-layer signal (`pytest -m operational`, the daemon-lifecycle / "
        f"IaC-reconcile / capability suite) has been RED for {consecutive_red} consecutive hourly "
        "checks -- past paging, so paging did NOT get it fixed. This is priority-zero drawable work "
        "and OUTRANKS every product/HARDEN lane. DIAGNOSE with evidence (R9): run the exact signal "
        "`python3 -m pytest tests/ -q -m operational` (see "
        "background/process_run_complete.py::operational_layer_pytest_argv), NAME the failing "
        "daemon-lifecycle/capability defect one line, FIX it (regenerate the process-set manifest / "
        "restore the capability), confirm the suite GREEN, and NTFY the director the cause. The "
        "signal clears itself on the next hourly check once the suite passes."
    )


def _newest_run_artefact_age_seconds(
    now: float | None = None,
    reports_dir: Path | None = None,
) -> float | None:
    """Age in seconds of the newest simulation run output, or None if there are none
    (or the directory is unreadable).

    INDEPENDENCE (R15): this is the age of a file the CHILD process writes on a
    successful run (`tools.run_annual_report --save-json`), never of the runner's own
    bookkeeping. That is what lets it both cross-check and stand in for
    `.sim_producer_state.json` -- a detector keyed only on a counter is blind to the
    process that stopped writing counters.
    """
    now = time.time() if now is None else now
    directory = reports_dir or SIM_RUN_OUTPUT_DIR
    try:
        mtimes = [p.stat().st_mtime for p in Path(directory).glob(SIM_RUN_OUTPUT_GLOB)]
    except OSError:
        return None
    if not mtimes:
        return None
    return now - max(mtimes)


def _producer_starved_active(
    now: float | None = None,
    state_path: Path | None = None,
    reports_dir: Path | None = None,
    hold_flag: Path | None = None,
    oom_clause_fn=None,
) -> str | None:
    """RUNG 1d (PRIORITY ZERO) detector: is the SIMULATION PRODUCER down?

    Returns a remediation draw message if so, else None. See the RUNG 1d block beside
    PRODUCER_STARVED_MIN_FAILURES for why this rung exists, why rungs 1 and 1b were
    both structurally blind to the 2026-08-17 outage, and why it has two limbs.

    FAIL-SAFE: every read is guarded and a hold silences the rung, so the worst case is
    one diagnostic turn that finds a healthy producer and rests -- never an exception
    into the draw ladder, and never a phantom that cannot drain.
    """
    now = time.time() if now is None else now

    # THE OOM DOOR (2026-08-24). Both limbs below read inputs that an OOM kill cannot reach:
    # the state file needs a Python-level exception to record anything, and artefact age is
    # equally consistent with "dead" and "killed every time". Asked ONLY when a limb is already
    # about to fire -- a journal read costs a couple of seconds and must not sit on the draw
    # ladder's hot path. Guarded: this rung never raises into the draw.
    def _oom_clause() -> str:
        try:
            if oom_clause_fn is not None:
                clause = oom_clause_fn()
            else:
                from background.oom_watch import producer_oom_clause

                clause = producer_oom_clause()
        except Exception:
            clause = None
        return f" {clause}" if clause else ""

    # A hold is a DELIBERATE stop, not an outage. Checked first: while it stands, no
    # amount of producer silence is drawable work.
    flag = hold_flag or SIM_RUNNER_HOLD_FLAG
    try:
        if Path(flag).exists():
            return None
    except OSError:
        pass

    artefact_age = _newest_run_artefact_age_seconds(now=now, reports_dir=reports_dir)

    state: dict = {}
    try:
        loaded = json.loads(Path(state_path or SIM_PRODUCER_STATE_FILE).read_text())
        if isinstance(loaded, dict):
            state = loaded
    except (OSError, ValueError):
        state = {}

    # ---- LIMB 1: DIAGNOSED -- the runner is alive and its runs keep failing.
    if state.get("last_result") == "failed":
        try:
            streak = int(state.get("consecutive_failures") or 0)
        except (TypeError, ValueError):
            streak = 0
        first_ts = state.get("first_failure_ts")
        last_ts = state.get("last_failure_ts")
        outage = (now - first_ts) if isinstance(first_ts, (int, float)) else 0.0
        # INDEPENDENCE (anti-tautology): a run artefact NEWER than the newest recorded
        # failure means a run has since succeeded, so the counter is stale and this
        # returns None without anyone clearing state by hand. Keyed on the child's
        # output, never on the same bookkeeping the streak came from.
        superseded = (
            artefact_age is not None
            and isinstance(last_ts, (int, float))
            and (now - artefact_age) > last_ts
        )
        if (streak >= PRODUCER_STARVED_MIN_FAILURES
                and outage > PRODUCER_STARVED_MIN_AGE_SECONDS
                and not superseded):
            detail = str(state.get("detail") or "no diagnostic captured")
            return (
                f"PRODUCER STARVATION self-refill (RUNG 1d, PRIORITY ZERO -- the RUNG 1 ruling "
                f"applied to the other end of the same pipeline): the simulation runner has failed "
                f"{streak} consecutive runs over {outage / 3600:.1f}h and NOTHING new has reached "
                f"the live site in that window. Failing with: {detail}. This outranks every "
                f"product/HARDEN lane for the same reason a wedged publish gate does -- a dead "
                f"PRODUCER and a wedged PUBLISHER have the identical consequence, and the site goes "
                f"stale through a door none of the publish alarms watch. DIAGNOSE with evidence "
                f"(R9): the full child traceback is in docs/observability/sim-runner-log.md, and "
                f"the failure is REPRODUCIBLE in the foreground (`python3 -m tools.run_annual_report "
                f"--save-json /tmp/probe.json`) -- never infer the cause from the one-line detail "
                f"above. NAME the defect one line, FIX it, and close the CLASS rather than the "
                f"instance (R10) if the break came from a rename or a contract change: the reader "
                f"that crashed is rarely the only one. The rung clears itself on the next "
                f"successful run; do NOT edit the counter by hand.{_oom_clause()}"
            )

    # ---- LIMB 2: UNDIAGNOSED -- no artefact for a long time and no failure counter to
    # explain it. This is the runner DEAD/wedged/never-started case, which the limb above
    # cannot see precisely because a dead runner writes nothing.
    if artefact_age is not None and artefact_age > PRODUCER_ARTEFACT_STALE_SECONDS:
        last_result = state.get("last_result") or "no state recorded"
        return (
            f"PRODUCER SILENT self-refill (RUNG 1d, PRIORITY ZERO): no simulation run output has "
            f"been written for {artefact_age / 3600:.1f}h (newest docs/reports/run_output_*.json), "
            f"and the producer's own state says '{last_result}'. Whether that means the runs are "
            f"FAILING, being KILLED, or NOT HAPPENING is not decided by either input above -- "
            f"read the OOM-door clause at the end of this message before assuming any of them "
            f"(2026-08-24: this sentence used to assert the runs were absent outright, and was "
            f"wrong for four hours while every one of them was being OOM-killed mid-flight). "
            f"A silent producer takes the live site stale exactly as a wedged "
            f"publish gate does, and no publish alarm watches this door. DIAGNOSE with evidence "
            f"(R9): is the sim_runner process alive (`ps -eo pid,etime,cmd | grep sim_runner`), is "
            f"its unit up, is `.sim_runner_hold` absent (this rung already checked, but re-check "
            f"whether it SHOULD be held), and does a foreground run get further than the daemon "
            f"does? A restart (R2: committed is not running) is the repair ONLY if the runs are "
            f"genuinely absent -- if the clause below names OOM kills, systemd has already "
            f"restarted it once per kill and a further one is not a repair. Confirm a run output "
            f"lands before calling it fixed.{_oom_clause()}"
        )

    return None


DIRECTOR_AXES_PATH = PROJECT_DIR / "docs" / "design" / "DIRECTOR_AXES.md"
FIDELITY_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "fidelity_evidence_ledger.json"
PLANNER_RUNG_DISABLED_FLAG = PROJECT_DIR / "docs" / "observability" / ".planner_rung_disabled"
# GAP1 detector-level kill flag (2026-07-28, GAP_REGISTER_MINT_SOURCE_CONTRACT (b)): a shadow rail
# for the `gap_register` enumeration level -- a `.gap_register_level_disabled` flag instantly reverts
# the draw-core to its prior behaviour with no code change (a draw-core change must be killable, same
# discipline as PLANNER_RUNG_DISABLED_FLAG). Absent -> level active.
GAP_REGISTER_LEVEL_DISABLED_FLAG = PROJECT_DIR / "docs" / "observability" / ".gap_register_level_disabled"
PLANNER_MINTED_PREFIX = "PLANNER_MINTED_"
# REST-WITH-PROOF marker (2026-07-25, PLANNER_MINTED_planner_rest_with_proof_saturation):
# when a planner turn concludes NO un-minted, non-walled ratified-goal next-step exists (every
# ratified step already minted-and-blocked or walled), it writes this dated verdict. The planner
# then RESTS-WITH-PROOF (returns None) instead of RE-FIRING into the proven-empty state, but ONLY
# while the marker stays FRESH: same UTC day, DIRECTOR_AXES content unchanged, and no in_progress/
# mint flipped blocked -> self-drawable. Any of those change -> the marker is stale -> re-plan.
PLANNER_REST_PROOF_PATH = PROJECT_DIR / "docs" / "observability" / ".planner_rest_with_proof.json"

# EIGHTH CLASS -- the pending-batch deadlock (2026-07-27, DIRECTOR_RULING_EIGHTH_CLASS_...).
# A rest-with-proof over an ALL-BLOCKED in_progress batch grounded a 42-hour silent rest: the proof
# stayed "fresh" for the WHOLE UTC day (the date/axes/blocked-set all unchanged), so the planner
# never re-examined whether a ratified goal had become mintable-around, and the tick rested. The
# director's ruling: "A blocked batch is a reason to plan MORE, never a licence to rest." So while
# ANY blocked mint is open, a rest-proof is fresh for at most this bounded window from `written_at`;
# past it the proof goes stale and the planner RE-EXAMINES (mints around remaining ratified goals,
# or re-proves). This bounds re-planning to ~once per window (one bounded worker, NOT a per-tick
# treadmill) instead of once-per-day, so a genuinely-mintable goal can never sit unminted for 42h.
# Matched to the deadman's own 2h open-mint escalation threshold so the two clocks agree.
PLANNER_REST_PROOF_MAX_AGE_SECONDS = 2 * 60 * 60


def _director_axes_present(axes_path: Path | None = None) -> bool:
    """True if DIRECTOR_AXES has at least one RATIFIED axis (a '### <n>. <name>' heading under
    '## v1 axes'). The planner mints the next proposals FROM these ratified goals; their ABSENCE is
    the only genuinely-exhausted state (rest below rung 7). Independence (R15): keyed on the axes
    file's ACTUAL content, never a constant. FAIL-CLOSED for MINTING (absent/unreadable -> not
    present -> planner does not fire) so a missing axes file can never fabricate a phantom mint."""
    p = axes_path or DIRECTOR_AXES_PATH
    try:
        text = Path(p).read_text(encoding="utf-8")
    except OSError:
        return False
    return bool(re.search(r"^###\s+\d+\.\s+\S", text, re.MULTILINE))


def _pending_planner_mints(staging_dir: Path | None = None) -> bool:
    """True if a PLANNER_MINTED_* batch is still UNCONSUMED -- i.e. one or more
    `PLANNER_MINTED_*.md` files sit directly in docs/staging/ (NOT in done/,
    in_progress/, fyi/ -- those are consumed/parked). This is RUNG 1 (staged docs):
    while a minted batch is pending, the unprocessed-staging path draws it, so the
    planner must NOT mint another batch on top -- otherwise every tick appends 'MINT
    the next batch' regardless of the pile, an unbounded-accretion treadmill (observed
    live 2026-07-24: 5 minted docs pending yet enumeration still showed planner=Y).
    Makes the mechanism enforce _planner_rung_draw's own docstring contract ('rung 1
    gates it; no per-cycle churn'), which was previously prose-only. FAIL-CLOSED for
    MINTING: if the directory can't be read we assume a batch may be pending (return
    True -> planner stays quiet) rather than mint blindly."""
    d = staging_dir or STAGING_DIR
    try:
        return any(p.name.startswith(PLANNER_MINTED_PREFIX) for p in Path(d).glob("*.md"))
    except OSError:
        return True


def _axes_content_sha(axes_path: Path | None = None) -> str:
    """SHA-256 of the DIRECTOR_AXES file's ACTUAL content. Independence (R15): the rest-proof
    marker is keyed on this real content hash, never a constant -- a new director axis or ruling
    changes the file, changes the hash, and invalidates any prior rest proof so the planner
    RE-PLANS. Returns "" (never matches a recorded hash) if the file is unreadable, so an absent/
    unreadable axes file can never validate a stale proof."""
    p = axes_path or DIRECTOR_AXES_PATH
    try:
        text = Path(p).read_text(encoding="utf-8")
    except OSError:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _in_progress_minted_slugs(staging_dir: Path | None = None) -> dict[str, list[str]]:
    """Partition PLANNER_MINTED_* docs parked in docs/staging/in_progress/ by their SUPERVISOR_DRAW
    marker into {'blocked': [...], 'self_drawable': [...]} (both sorted). The draw-marker is read
    from the `<!-- SUPERVISOR_DRAW: ... -->` line. FAIL-CLOSED to 'blocked' for an UNMARKED parked
    mint (per 04fe15d69: an unmarked in_progress mint is invisible to the draw) so a missing marker
    never fabricates phantom drawable work. Used by the rest-proof freshness check: a mint that
    flips blocked->self-drawable (newly unblocked) invalidates the proof and re-plans."""
    d = staging_dir or STAGING_DIR
    ip = Path(d) / "in_progress"
    blocked: list[str] = []
    drawable: list[str] = []
    try:
        files = sorted(ip.glob(PLANNER_MINTED_PREFIX + "*.md"))
    except OSError:
        return {"blocked": [], "self_drawable": []}
    for f in files:
        try:
            head = f.read_text(encoding="utf-8")[:600]
        except OSError:
            continue
        if re.search(r"SUPERVISOR_DRAW:\s*self-drawable", head):
            drawable.append(f.name)
        elif _mint_blocker_is_abolished_permission(f):
            # 2026-08-03 (director console, finishing DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY):
            # a mint whose ONLY stated blocker is an abolished permission convention
            # (director_level_up / director_build_open / a LEDGER: release / a ratification) is
            # SELF-DRAWABLE, whatever its marker says. Same abolition `_is_externally_blocked`
            # applies to map atoms, applied here to parked mints -- without it the two disagreed:
            # the map said "drawable", the mint doc said "waiting on the director", and 17 mints sat
            # in in_progress/ being re-enumerated every tick as OPEN MINTS awaiting an act that no
            # longer exists. Mechanism, not a one-time edit: a mint written tomorrow citing a dead
            # convention is drawn too, and the flip is logged loudly by the caller.
            drawable.append(f.name)
        else:
            blocked.append(f.name)
    return {"blocked": sorted(blocked), "self_drawable": sorted(drawable)}


def _mint_blocker_is_abolished_permission(path: Path) -> bool:
    """True iff a parked mint's stated blocking reason names ONLY an abolished director-permission
    convention -- and does NOT also describe one of the four reserved real-world consequences.
    Delegated to `one_way_door.classify_action` for the reserved half (the SOLE enumeration), so a
    mint genuinely blocked on real money / real people / a public claim / a real person's safety
    still blocks even when it also cites a permission token. FAIL-CLOSED to False (stays blocked) on
    any read error -- an unreadable mint is not evidence of drawability."""
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return False
    reason = _extract_blocking_reason(body)
    if not _names_abolished_permission_block(reason):
        return False
    try:
        from background import one_way_door as _owd
        return not _owd.classify_action(reason).is_one_way_door
    except Exception:
        return False


def _extract_blocking_reason(body: str) -> str:
    """Pull the one-line blocking reason from a parked PLANNER_MINTED_* doc. Prefers an explicit
    'UNBLOCKS ON:' / 'UNBLOCKS:' clause (the convention every mint carries), then a 'BLOCKING
    SUB-ITEM' heading, else a short generic. Markdown emphasis stripped, truncated. Used only for
    the enumeration/[ACT] payload (director-facing honesty), never for a draw decision."""
    for pat in (
        r"UNBLOCKS?(?:\s+ON)?:\s*([^\n]+)",
        r"BLOCKING SUB-ITEM[^\n]*:\s*\*?\*?([^\n]+)",
        r"blocked_on:\s*([^\n]+)",
    ):
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            s = re.sub(r"[*`>~]", "", m.group(1)).strip()
            if s:
                return (s[:200] + "…") if len(s) > 201 else s
    return "blocked (reason unstated in the mint doc)"


def open_mint_blockers(staging_dir: Path | None = None) -> list[tuple[str, str]]:
    """(filename, blocking-reason) for every BLOCKED PLANNER_MINTED_* mint parked in in_progress/.
    EIGHTH CLASS enumeration-honesty (2026-07-27, DIRECTOR_RULING): 'Any lane reporting empty while
    items exist in in_progress/ must instead report them WITH their blocking reason. An enumeration
    that cannot see open mints is not an enumeration.' Reads the SAME blocked set the rest-proof uses
    (`_in_progress_minted_slugs`), so the enumeration and the draw can never disagree. Self-drawable
    mints are EXCLUDED (they are surfaced by the RUNG-1 selfdrawable path, not a blocker)."""
    d = staging_dir or STAGING_DIR
    ip = Path(d) / "in_progress"
    out: list[tuple[str, str]] = []
    for name in _in_progress_minted_slugs(d)["blocked"]:
        try:
            body = (ip / name).read_text(encoding="utf-8")
        except OSError:
            body = ""
        out.append((name, _extract_blocking_reason(body)))
    return out


def _gap_register_open(disabled_flag: Path | None = None) -> bool:
    """GAP1 detector level (2026-07-28, GAP_REGISTER_MINT_SOURCE_CONTRACT (b), director BUILD_OPEN
    `gap1_reader_contract_failopen_fix` in gate_authorizations.jsonl). True iff any published gap
    register holds an OPEN row -- the ruling's acceptance turns on this: *a saturation/rest claim is
    impossible while any published register holds an open, un-triaged item.* Reads the residue from
    the INDEPENDENT `background/gap_register_scan` (imports nothing from this module -- invariant 1,
    LAW-C: a reader restating the tick's own belief could not falsify a saturation claim). FAIL-SAFE
    toward work: any read/import error -> True (forbid rest, the Rule-0 direction). SHADOW RAIL: a
    `.gap_register_level_disabled` flag reverts to the prior behaviour with no code change."""
    flag = disabled_flag or GAP_REGISTER_LEVEL_DISABLED_FLAG
    try:
        if Path(flag).exists():
            return False  # shadow-disabled -> level contributes nothing
    except OSError:
        pass
    try:
        from background.gap_register_scan import gap_register_open

        return bool(gap_register_open())
    except Exception:  # noqa: BLE001 -- an unreadable register is a FAILED read -> forbid rest
        return True


def _blocked_mints_open(staging_dir: Path | None = None) -> bool:
    """True iff any BLOCKED PLANNER_MINTED_* mint is open in in_progress/. Director ruling EIGHTH
    CLASS: 'A blocked batch is a reason to plan more, never a licence to rest' -- so this level
    FORBIDS rest (wired into `authorized_set_enumeration` and `_is_drained_and_gated`), while the
    2h rest-proof age cap bounds how often the planner actually re-examines. FAIL-SAFE TOWARD WORK:
    keyed on the real in_progress blocked set, never a constant."""
    return bool(_in_progress_minted_slugs(staging_dir)["blocked"])


def _planner_rest_proof_fresh(
    axes_path: Path | None = None,
    staging_dir: Path | None = None,
    proof_path: Path | None = None,
    today: str | None = None,
) -> bool:
    """True iff a FRESH rest-with-proof marker authorises the planner to rest instead of re-firing.
    'Fresh' means, all three (any failing -> re-plan):
      1. `date` == today's UTC date (daily re-check -- a new day always re-plans);
      2. `axes_sha` == the current DIRECTOR_AXES content hash (a new axis/ruling re-plans);
      3. the recorded `minted_blocked_slugs` STILL exactly equals the current in_progress/ blocked
         set AND no in_progress/ mint is now self-drawable (a mint newly unblocked re-plans).
    FAIL-CLOSED: a missing / malformed / non-dict marker returns False (mint, don't fabricate a
    rest). This is the anti-treadmill guarantee: rest only with a proof that still matches reality,
    never a stale/constant marker that would silence the planner forever (R15 mutation-tested both
    ways in test_planner_rung.py)."""
    p = proof_path or PLANNER_REST_PROOF_PATH
    try:
        marker = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(marker, dict):
        return False
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if marker.get("date") != today:
        return False
    if marker.get("axes_sha") != _axes_content_sha(axes_path):
        return False
    cur = _in_progress_minted_slugs(staging_dir)
    if cur["self_drawable"]:
        return False  # a parked mint newly drawable -> real RUNG-1 work exists -> re-plan
    if sorted(marker.get("minted_blocked_slugs") or []) != cur["blocked"]:
        return False  # the blocked set changed (mint consumed / new wall) -> re-plan
    # EIGHTH CLASS (2026-07-27): a proof over an ALL-BLOCKED batch may ground rest for at most
    # PLANNER_REST_PROOF_MAX_AGE_SECONDS from `written_at` -- past that the planner MUST re-examine
    # (mint around remaining ratified goals, or re-prove), never rest a whole working day on it. When
    # NO mint is blocked (cur["blocked"] empty) the age cap does not apply -- a genuinely-exhausted
    # rest below rung 7 is still legitimate for the full UTC day (the axes/day checks bound it).
    if cur["blocked"]:
        try:
            written = datetime.fromisoformat(marker.get("written_at", ""))
            if written.tzinfo is None:
                written = written.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - written).total_seconds()
        except (TypeError, ValueError):
            return False  # a proof with no/garbled written_at cannot age-gate -> fail-closed -> re-plan
        if age >= PLANNER_REST_PROOF_MAX_AGE_SECONDS:
            return False  # blocked-batch proof aged out -> re-examine, don't rest (the 42h-stall fix)
    return True


def write_planner_rest_proof(
    minted_blocked_slugs: list[str],
    proof_summary: str,
    axes_path: Path | None = None,
    proof_path: Path | None = None,
) -> Path:
    """Write the dated rest-with-proof verdict a planning turn produces when it concludes NO
    un-minted, non-walled ratified-goal next-step exists. Records {date, axes_sha,
    minted_blocked_slugs, proof_summary} so `_planner_rest_proof_fresh` can later confirm the
    verdict still matches reality. The planner then rests-with-proof until the day rolls, the axes
    change, or a blocked mint is unblocked -- never a silent forever-rest."""
    p = proof_path or PLANNER_REST_PROOF_PATH
    marker = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "axes_sha": _axes_content_sha(axes_path),
        "minted_blocked_slugs": sorted(minted_blocked_slugs),
        "proof_summary": proof_summary,
        "written_at": datetime.now(timezone.utc).isoformat(),
    }
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    return Path(p)


def _planner_rung_draw(
    axes_path: Path | None = None,
    disabled_flag: Path | None = None,
    staging_dir: Path | None = None,
) -> str | None:
    """RUNG 7 -- THE PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23, commit 48495a455).

    When rungs 1-6 are genuinely empty, the planner MINTS the next batch of proposals from the
    director's ratified goals rather than resting -- 'Planning is work; resting instead of planning
    is the breach.' Returns a bounded planning-turn doorbell if DIRECTOR_AXES holds ratified goals
    (minting from ratified goals is authorized+expected), else None (genuinely-exhausted -> rest
    below rung 7; pre-go-live that state should be structurally unreachable).

    SHADOW RAIL: a `.planner_rung_disabled` flag file instantly reverts to the prior behaviour
    (RULE-0 HARDEN treadmill / rest) with no code change -- a draw-core change must be killable.

    This is the DETECTOR + DOORBELL only. The spawned bounded worker does the actual reading (axes,
    epoch arc, fidelity ledger, open campaigns) and writes propose-then-proceed docs into
    docs/staging/. Once minted, those occupy RUNG 1 (staged docs) and are drawn there -- so the
    planner re-fires only once a whole minted batch is consumed. That gate is now MECHANISED
    (`_pending_planner_mints`): while any `PLANNER_MINTED_*.md` sits unconsumed in staging root the
    planner returns None (no per-cycle churn). It was previously prose-only, and on 2026-07-24 the
    code did NOT enforce it -- 5 minted docs pended yet the enumeration still showed planner=Y, the
    unbounded-accretion treadmill MAKE_IT_STICK warns about. R15 both ways in test_planner_rung.py:
    axes-populated+lanes-empty+no-pending-batch MINTS; axes-absent RESTS; pending-batch RESTS.

    REST-WITH-PROOF (2026-07-25, PLANNER_MINTED_planner_rest_with_proof_saturation): a SECOND
    treadmill exists once mints move to in_progress/ (parked-blocked) -- `_pending_planner_mints`
    only sees staging ROOT, so a fully-blocked parked batch reads as consumed and the planner
    RE-FIRES every tick into a proven-empty ratified-goal set. A planning turn that PROVES no
    un-minted non-walled step exists writes a dated verdict via `write_planner_rest_proof`; while
    that proof stays FRESH (`_planner_rest_proof_fresh`) the planner rests-with-proof. Keyed on live
    state (UTC day + axes content hash + in_progress blocked-slug set), never a constant, so it
    re-plans the moment a new ruling/day/unblocked-mint appears -- R15 both ways in
    test_planner_rung.py."""
    flag = disabled_flag or PLANNER_RUNG_DISABLED_FLAG
    try:
        if Path(flag).exists():
            return None
    except OSError:
        pass
    if not _director_axes_present(axes_path):
        return None
    # RUNG 1 GATES RUNG 7: a minted batch already pending in staging means the
    # unprocessed-staging path is drawing it -- do NOT mint another on top (the
    # per-cycle-churn treadmill this rung's docstring already promised was gated).
    if _pending_planner_mints(staging_dir):
        return None
    # REST-WITH-PROOF GATE (2026-07-25): when a prior planning turn proved every ratified-goal
    # next-step is ALREADY minted-and-blocked or walled, it wrote a dated verdict marker. While that
    # proof stays FRESH (same UTC day, DIRECTOR_AXES content unchanged, no in_progress/ mint newly
    # unblocked) the planner RESTS-WITH-PROOF rather than RE-FIRING a bounded worker into the
    # proven-empty state every tick -- the anti-treadmill guarantee R17 demands, keyed on live state
    # not a constant so a new ruling / a new day / an unblocked mint re-plans immediately.
    if _planner_rest_proof_fresh(axes_path, staging_dir):
        return None
    return (
        "RUNG 7 PLANNER self-refill (director ruling WORK_IS_THE_DEFAULT 2026-07-23): rungs 1-6 are "
        "empty but the director's ratified goals are NOT -- minting from ratified goals is AUTHORIZED "
        "and EXPECTED; resting instead of planning is the breach. Run a BOUNDED planning turn: read "
        "docs/design/DIRECTOR_AXES.md (ratified axes), the epoch arc (docs/design/maturity_map.yaml), "
        "the fidelity ledger (docs/observability/fidelity_evidence_ledger.json) and the open-campaign "
        "register (docs/design/CAMPAIGN_REGISTER.yaml), then MINT the next batch (up to ~5) of "
        "propose-then-proceed docs into docs/staging/ named '" + PLANNER_MINTED_PREFIX + "<slug>_<date>.md'. "
        "Each names the axis / fidelity-ledger row / campaign follow-on it serves, the real-world "
        "fidelity gained, and its propose-then-proceed window. Director-reserved walls stay untouched "
        "(one-way doors, L3 levels, curriculum values, generator ground truth). If -- and ONLY if -- "
        "you PROVE no un-minted, non-walled ratified-goal next-step exists (every ratified step is "
        "already minted-and-blocked or walled), call background.supervisor.write_planner_rest_proof("
        "minted_blocked_slugs, proof_summary) to record the premise-FALSE verdict and REST-WITH-PROOF "
        "instead of minting a duplicate -- that marker makes the planner rest honestly until the day "
        "rolls, the axes change, or a blocked mint is unblocked. Otherwise MINT and STOP -- the minted "
        "docs become RUNG-1 staged work the next tick draws. This IS work; do not rest without proof."
    )


# ── RUNG 1c: DELETED 2026-08-03 ──────────────────────────────────────────────────────────────
# `_director_act_rung_zero_draw()` drew, at rung zero, any AUTHENTICATED director LEVEL_UP_PROPOSED
# sitting unconsumed (ledger ratified L{N}, map still below it) -- built because a signed act had
# once waited ~11h behind cooldown/HARDEN re-verifies. Both halves of its premise are now gone: the
# director does not ratify levels (2026-07-29 ruling item 2), and `is_valid_level_up` no longer
# recognises a LEVEL_UP_PROPOSED act at all, so this rung could only ever fire on legacy ledger
# history. The agent records its own level move and moves the map cell in the same act -- there is
# no second party's act left to consume, and therefore no latency to prioritise away.


def _blocking_lane_draw(staging_dir: Path | None = None) -> tuple[str | None, frozenset[str]]:
    """RUNG 1c REVIVED, 2026-08-12 -- BLOCKING FINDING LANE PRECEDENCE, atom
    `OPS12_blockers_ahead_of_disposition` (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE
    2026-08-12, clause 3): "a BLOCKING finding draws ahead of the general disposition queue,
    ahead of latent findings, and ahead of new feature work in its own lane; the drain
    proceeds around it."

    Reads OPS9's severity parse (`background.finding_severity.scan_staging_root` +
    `blocking_by_lane`) over the REAL staging root -- deliberately never a second hand-kept
    list, per this atom's own exit criterion 1 ("the ordering is read from the OPS9 severity
    parse, never from a second hand-kept list that could disagree with it").

    Returns `(reason, blocked_lanes)`:
      * `reason` is a human-readable string NAMING the blocking finding(s) by filename
        (exit criterion 3: "the draw REASON names the blocker, so a tick that jumped the
        queue can be audited afterwards from the log alone"), or `None` when there is
        nothing to report (no blocker, and the index read cleanly).
      * `blocked_lanes` is the set of lanes carrying a live BLOCKING finding. The caller
        (`_self_refill_draw`) uses this to exclude SAME-LANE new-feature-work candidates
        from this cycle's BUILD/SITE/DISCOVERY draw -- and ONLY same-lane candidates,
        never any other lane's (exit criterion 2, "NON-BLOCKING ELSEWHERE": "a draw in
        another lane is unaffected... the half a naive global priority would break").

    FAIL-OPEN CHECK (exit criterion 5): if the severity index itself cannot be read (the
    module is missing, the staging root is unreadable), this returns a `reason` that SAYS
    SO explicitly and an EMPTY `blocked_lanes` -- the caller therefore falls back to the
    ordinary draw order, but VISIBLY (the message is logged), never by silently resuming
    recency order the way a re-ranking control quietly stops re-ranking. Distinguishing
    "index unreadable" from "index read clean, zero blockers" is why this can't just
    return `None` on both -- a `None` reason on the unreadable path would be exactly the
    silent fallback this criterion forbids.
    """
    root = staging_dir if staging_dir is not None else STAGING_DIR
    try:
        from background.finding_severity import blocking_by_lane, scan_staging_root
        by_lane = blocking_by_lane(scan_staging_root(root))
    except Exception as exc:  # module missing, root unreadable, or any parse-path failure
        return (
            "BLOCKING-FINDING INDEX UNREADABLE (RUNG 1c fail-open check, OPS12 exit "
            f"criterion 5): could not read the OPS9 severity parse over {root} "
            f"({exc.__class__.__name__}) -- blocker precedence cannot be computed this "
            "cycle; falling back to the ordinary draw order VISIBLY, not by silently "
            "resuming recency order."
        ), frozenset()
    if not by_lane:
        return None, frozenset()
    # Deterministic tie-break across lanes (alphabetical) -- the draw itself is a SET
    # (blocked_lanes filters every candidate in every affected lane this cycle; nothing
    # is left to choose between), so this only orders which lane's names lead the message.
    lane, findings = sorted(by_lane.items())[0]
    names = ", ".join(f.path.name for f in findings)
    return (
        f"BLOCKING FINDING (RUNG 1c, OPS12 clause 3): lane {lane} carries a live BLOCKING "
        f"finding -- {names} -- drawing ahead of the general disposition queue, latent "
        f"findings, and new feature work in lane {lane}; the drain proceeds around it "
        "(other lanes unaffected)."
    ), frozenset(by_lane.keys())


# ─────────────────────────────────────────────────────────────────────────────
# OPS13 -- THE PRODUCT INTERLEAVE (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE
# _2026-08-12, clause 4: "The product interleave arms NOW, unconditionally. One
# world/customer/product atom per harness atom, every session, regardless of staging
# depth. It is no longer coupled to a document count.")
#
# WHY THE COUNT IS GONE: the previous trigger (DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_
# INTERLEAVE_2026-08-10) armed the interleave only once the staging root fell below 20
# files -- "a number that measures the rate of self-scrutiny, not the state of the
# project, and which has grown every day since the rule was made", withdrawn by the same
# hand that proposed it. NOTHING below reads the staging directory; a named test varies
# staging depth from 0 to 200 documents and asserts the arm does not move (exit 1).
#
# WHY IT TAKES THE SLOT RATHER THAN WIDENING: MAX_CONCURRENT_FORKS is 1 (TOKEN BUDGET IS
# BINDING AGAIN, 2026-08-03 -- SERIAL BY DEFAULT, because each extra concurrent context
# stream re-reads its whole context every turn and cache-read volume is the bill). Adding
# a second fork every time a harness atom draws would buy the pairing with exactly the
# spend that ruling cut. So the interleave ALTERNATES: a grant that takes the harness side
# and leaves the product side unserved records the harness atom as OWED, and the next
# grant's product side is forced -- the product atom takes the slot and the displaced
# harness atom is simply not granted this cycle (it was never drawn, so it is not owed).
# Where width genuinely exists (MAX_CONCURRENT_FORKS > 1) the pair is drawn in the SAME
# grant and nothing is owed. One product atom per harness atom either way.
#
# PER GRANT, WHICH IS STRICTER THAN PER SESSION (exit 2): a grant is the finest boundary
# the supervisor actually has -- one drawn doorbell, one worker invocation. Enforcing the
# pairing per grant enforces it per session by construction, and it makes the exit
# criterion's own example ("a session drawing two harness atoms and no product atom")
# directly checkable.
#
# SILENCE IS THE FAILURE (exit 4): `product_interleave_digest_line()` returns a non-empty
# line on EVERY path -- paired, violated, armed-and-found-nothing, clause-2 substituted,
# and the no-atom-drawn case (a priority rung, a fallback rung, or a rest). `find_work()`
# logs it every cycle unconditionally, so a day the interleave did not happen READS as
# such. An interleave line that is simply absent on the bad day is the fail-silent shape
# this atom exists to forbid.
# ─────────────────────────────────────────────────────────────────────────────

#: The harness side of the interleave. Everything else in the map is the product side --
#: see `_is_product_atom` for why that complement is deliberate.
HARNESS_LANES = frozenset({"H_harness"})

PRODUCT_INTERLEAVE_STATE_FILE = (
    PROJECT_DIR / "docs" / "observability" / ".product_interleave_state.json"
)

#: How many unpaid harness ids the ledger carries. DELIBERATELY TINY: an unbounded debt
#: ledger accumulates noise (a test run, a replayed cycle, a daemon restart mid-grant) that
#: nothing can ever pay down, and a debt that can never reach zero stops informing anyone.
#: The alternation only needs one grant of memory; three is slack, not a budget. A phantom
#: entry that does survive (a test fixture's atom id, a replayed cycle) costs at most one
#: extra forced PRODUCT draw before it is paid off -- the direction the ruling wants erred in.
_INTERLEAVE_OWED_CAP = 3

_INTERLEAVE_PREFIX = "PRODUCT INTERLEAVE (OPS13, clause 4)"

#: Set by `_self_refill_draw` on EVERY call: the interleave record for the grant it just
#: made, or None when the cycle drew no maturity-map atom at all (a priority rung, a
#: fallback rung, or a rest). Read by `find_work`, so ONE log call covers every path and
#: no path can go quiet.
_LAST_INTERLEAVE_RECORD: dict | None = None


def _is_harness_atom(atom: dict) -> bool:
    return isinstance(atom, dict) and (atom.get("lane") or "") in HARNESS_LANES


def _is_product_atom(atom: dict) -> bool:
    """The product side is world/customer/product work -- i.e. every lane that is not the
    harness itself. Defined as the COMPLEMENT on purpose: a lane added to the map tomorrow
    counts as product work without anyone remembering to extend a list here, and the
    failure direction of a mis-classification is a product atom read as harness (which
    UNDER-reports the pairing and shows up as a violation in the digest), never the
    reverse -- a harness atom quietly counted as its own product partner would make the
    interleave self-satisfying, which is the one shape that cannot be noticed."""
    if not isinstance(atom, dict):
        return False
    lane = atom.get("lane")
    return bool(lane) and lane not in HARNESS_LANES


def _load_interleave_state() -> tuple[list[str], str | None]:
    """(owed_harness_ids, error). An absent file is a clean slate and NOT an error; an
    unreadable or malformed one resets the list but returns a NAMED error that the digest
    line carries, because a debt ledger that quietly resets always reads paid."""
    if not PRODUCT_INTERLEAVE_STATE_FILE.exists():
        return [], None
    try:
        data = json.loads(PRODUCT_INTERLEAVE_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return [], f"owed ledger UNREADABLE ({exc.__class__.__name__}) -- reset to empty"
    if not isinstance(data, dict) or not isinstance(data.get("owed"), list):
        return [], "owed ledger MALFORMED (no 'owed' list) -- reset to empty"
    return [str(x) for x in data["owed"]], None


def _save_interleave_state(owed: list[str], record: dict) -> None:
    payload = {
        "owed": list(owed),
        "last_harness": list(record.get("harness") or []),
        "last_product": list(record.get("product") or []),
        "updated": datetime.now(timezone.utc).isoformat(),
    }
    try:
        PRODUCT_INTERLEAVE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        PRODUCT_INTERLEAVE_STATE_FILE.write_text(json.dumps(payload, sort_keys=True))
    except OSError as exc:
        log(f"{_INTERLEAVE_PREFIX}: could not persist the owed ledger ({exc}) -- the pairing "
            "debt will not survive this cycle; the digest line still names this grant's pair.")


class _LanePreferringPicker:
    """A drop-in for the `random` module as the map draws use it (`.choices(population,
    weights=..., k=1)`), which picks the dial-weighted primary ONLY from atoms satisfying
    `predicate`, falling back to the unfiltered population when none does.

    Reusing the REAL draw with a narrowed picker -- rather than re-implementing "which
    atoms are drawable" here -- is the point: dependency-met, externally-blocked,
    build-in-progress, unmerged-work, coupled-triad and anti-livelock filtering all stay in
    ONE place. A second copy of that ladder is exactly how a draw filter drifts out of
    agreement with the draw it is supposed to mirror, and this project has already filed
    that class twice."""

    def __init__(self, predicate, rng=None):
        self._predicate = predicate
        self._rng = rng or random

    def choices(self, population, weights=None, k=1):
        weights = list(weights) if weights is not None else [1] * len(population)
        kept = [(c, w) for c, w in zip(population, weights) if self._predicate(c)]
        if not kept:
            return self._rng.choices(population, weights=weights, k=k)
        return self._rng.choices([c for c, _ in kept], weights=[w for _, w in kept], k=k)


def _product_side_draw(exclude_ids, blocked_lanes=frozenset(), rng=None) -> tuple[dict | None, str]:
    """One product-lane atom for the interleave slot: (atom, "BUILD"|"DISCOVERY"), or
    (None, "") when the map has no drawable product-lane atom this cycle.

    The BUILD lane is tried first. An idle/parked product atom is still legitimate
    product-side work (EPOCH_GATING_AND_ATOM_AUTHORSHIP: parked is parked for BUILD ONLY --
    DISCOVER/FRAME on it is available now), but it must be granted as DISCOVER/FRAME and
    never as BUILD, or the interleave would instruct BUILD code on an epoch-gated atom to
    satisfy its own pairing rule. Which is why the lane the atom belongs in comes back with
    it rather than being guessed at the call site."""
    exclude = set(exclude_ids or ())
    blocked = frozenset(blocked_lanes or ())

    def _wanted(a) -> bool:
        return (
            _is_product_atom(a)
            and a.get("id") not in exclude
            and a.get("lane") not in blocked
        )

    picker = _LanePreferringPicker(_wanted, rng=rng)
    for kind, draw in (
        ("BUILD", lambda: _maturity_map_draw_concurrent(rng=picker, exclude_stalled=True)),
        ("DISCOVERY", lambda: _idle_discover_frame_draw_concurrent(
            rng=picker, exclude_stalled=True, exclude_ids=frozenset(exclude))),
    ):
        try:
            for atom in draw():
                if _wanted(atom):
                    return atom, kind
        except Exception as exc:  # a draw failure is never allowed to break the cycle
            log(f"{_INTERLEAVE_PREFIX}: {kind}-side product draw failed ({exc!r}) -- continuing")
    return None, ""


def _apply_product_interleave(build_atoms, site_atoms, discovery_atoms,
                              blocked_lanes=frozenset(), rng=None) -> dict:
    """Arm the interleave for THIS grant, and return the record the digest line renders.

    MUTATES `build_atoms` / `site_atoms` / `discovery_atoms` in place when it draws the
    product side -- appending when the fork budget has room, otherwise displacing the
    lowest-precedence harness atom (DISCOVERY, then SITE, then BUILD) so the grant's WIDTH
    is unchanged. Never raises: the pairing rule must not be able to break the draw."""
    owed_in, state_error = _load_interleave_state()
    granted = list(build_atoms) + list(site_atoms) + list(discovery_atoms)
    harness = [a.get("id") for a in granted if _is_harness_atom(a)]
    product = [a.get("id") for a in granted if _is_product_atom(a)]

    # Clause 2: "a lane carrying a live BLOCKING finding takes the repair as its product-side
    # draw until cleared." A blocker in a PRODUCT lane therefore SATISFIES the pairing -- the
    # product side of this grant is the repair -- and the digest must name the substitution
    # rather than reporting a pair that was not drawn.
    clause2 = sorted(lane for lane in (blocked_lanes or frozenset()) if lane not in HARNESS_LANES)

    record: dict = {
        "harness": list(harness),
        "product": list(product),
        "carried_in": list(owed_in),
        "clause2_lanes": clause2,
        "armed": False,
        "arm_result": None,
        "displaced": None,
        "violation": False,
        "owed": list(owed_in),
        "state_error": state_error,
    }

    # THE ARM. Unconditional -- the only inputs are what this grant drew, what the previous
    # grant left owed, and clause 2. No staging depth, no document count, no date.
    #
    # WHEN IT FIRES, and why it is not simply "whenever a harness atom is drawn": at
    # MAX_CONCURRENT_FORKS=1 an arm that displaced on every harness grant would mean the product
    # side ALWAYS wins and the harness side NEVER draws -- a 0:1 ratio, not the 1:1 the ruling
    # asks for. (Observed against the real map before this branch existed: the grant for
    # SITE2_two_sided_wall_exhibit was displaced by EP7_adapter_elexon_insights with nothing
    # owed either way.) So:
    #   * free width  -> ADD the product atom, pairing inside this grant;
    #   * a DEBT owed by a previous grant -> FORCE it, displacing if there is no room;
    #   * neither -> grant the harness atom, record the debt, NAME the violation, and the next
    #     grant's arm forces the product side. That is the alternation.
    _room = MAX_CONCURRENT_FORKS - len(granted)
    if (harness or owed_in) and not product and not clause2 and (_room > 0 or owed_in):
        record["armed"] = True
        atom, kind = _product_side_draw(
            exclude_ids={a.get("id") for a in granted}, blocked_lanes=blocked_lanes, rng=rng)
        if atom is None:
            record["arm_result"] = "no drawable product-lane atom in the map this cycle"
        else:
            room = _room
            target = build_atoms if kind == "BUILD" else discovery_atoms
            if room > 0:
                target.append(atom)
                record["arm_result"] = f"ADDED to LANE {kind} (fork budget had room)"
            else:
                displaced = None
                for lane_list in (discovery_atoms, site_atoms, build_atoms):
                    for i in range(len(lane_list) - 1, -1, -1):
                        if _is_harness_atom(lane_list[i]):
                            displaced = lane_list.pop(i)
                            break
                    if displaced is not None:
                        break
                target.append(atom)
                record["displaced"] = displaced.get("id") if displaced else None
                record["arm_result"] = (
                    f"TOOK THE SLOT in LANE {kind} (fork budget full at "
                    f"{MAX_CONCURRENT_FORKS}; SERIAL BY DEFAULT means the interleave "
                    "alternates rather than widens)"
                )
            # Recompute from the mutated lists -- the record must state what was ACTUALLY
            # granted, never what the arm intended to grant.
            granted = list(build_atoms) + list(site_atoms) + list(discovery_atoms)
            harness = [a.get("id") for a in granted if _is_harness_atom(a)]
            product = [a.get("id") for a in granted if _is_product_atom(a)]
            record["harness"], record["product"] = list(harness), list(product)

    # THE LEDGER. Every harness atom granted is a debt; every product atom granted, and a
    # clause-2 substitution, is a payment. FIFO, so the oldest unpaired harness atom is the
    # one a later product draw settles.
    owed_now = list(owed_in) + list(harness)
    for _ in range(len(product) + (1 if clause2 else 0)):
        if owed_now:
            owed_now.pop(0)
    owed_now = owed_now[-_INTERLEAVE_OWED_CAP:]

    record["violation"] = bool(harness) and not product and not clause2
    record["owed"] = owed_now
    _save_interleave_state(owed_now, record)
    return record


def product_interleave_digest_line(record: dict | None = None) -> str:
    """The tick digest's interleave line. NEVER empty, on ANY path (exit 4) -- including
    `record is None`, which is the cycle that drew no maturity-map atom at all. Reading the
    line must be enough to answer "did the product side get served this session, and if not,
    why not" without opening anything else."""
    parts = [f"{_INTERLEAVE_PREFIX}: ARMED UNCONDITIONALLY (no staging-depth term)"]
    if record is None:
        owed, err = _load_interleave_state()
        parts.append(
            "NO maturity-map atom drawn this cycle (a priority rung, a fallback rung or a "
            "rest) -- no harness/product pair to report"
        )
        parts.append(f"owed carried: {len(owed)}" + (f" ({', '.join(owed)})" if owed else ""))
        if err:
            parts.append(err)
        return " | ".join(parts)

    harness = record.get("harness") or []
    product = record.get("product") or []
    parts.append("harness drawn: " + (", ".join(harness) if harness else "none"))
    parts.append("product drawn: " + (", ".join(product) if product else "none"))
    if record.get("clause2_lanes"):
        parts.append(
            "CLAUSE-2 SUBSTITUTION: the product-side slot is the BLOCKING-finding repair in "
            f"lane(s) {', '.join(record['clause2_lanes'])} (a lane carrying a live blocker takes "
            "the repair as its product-side draw until cleared)"
        )
    if record.get("armed"):
        parts.append(f"arm fired: {record.get('arm_result')}")
        if record.get("displaced"):
            parts.append(
                f"harness atom {record['displaced']} NOT granted this cycle (displaced by the "
                "product side; it is not owed because it was never drawn)"
            )
    if record.get("violation"):
        parts.append(
            f"INTERLEAVE VIOLATION -- {len(harness)} harness atom(s) drawn and NO product atom: "
            + ", ".join(harness)
            + ". Named here rather than passing quietly; the product side is now OWED and the "
            "next grant's arm forces it -- at fork budget 1 the pair completes ACROSS two "
            "grants, so this is a deferred pairing, not a lost one"
        )
    elif harness and product:
        parts.append("pairing: PAIRED in this grant")
    elif product and not harness:
        parts.append("pairing: product-side draw, no harness atom this grant (nothing owed by it)")
    owed = record.get("owed") or []
    parts.append(f"owed carried: {len(owed)}" + (f" ({', '.join(owed)})" if owed else ""))
    if record.get("state_error"):
        parts.append(record["state_error"])
    return " | ".join(parts)


def _self_refill_draw_ladder() -> str | None:
    """The backlog-driven draw itself (maturity map, falling back to
    PRIORITIES.md prose only if the YAML is unavailable) -- factored out so
    find_work() can call it UNCONDITIONALLY (R3_WORK_GRANTING_REDESIGN.md
    requirement 2: "every granted turn ends with real work drawn... THEN
    draw the next atom from the map, always"), not merely as a fallback
    reached only when nothing else fired.

    MULTI_ATOM_DRAW.md (P0, 2026-07-12): the draw can now grant MORE THAN
    ONE atom per cycle when additional candidates are provably file-scope-
    disjoint from the primary pick (_maturity_map_draw_concurrent). The
    single-atom message format is preserved byte-for-byte when only one
    atom is drawn (the common case today, and the exact string this
    function's own existing tests assert on) -- the multi-atom message only
    appears when a genuine concurrent grant exists. The message itself
    names the expected action ("one agent per atom") since R7 still applies:
    this function states what exists, the granted session (reading its own
    doorbell) decides to fan out via parallel Agent dispatches.

    EPOCH_GATING_AND_ATOM_AUTHORSHIP.md (2026-07-12): when no BUILD
    candidate exists, falls to a SECOND tier -- `_idle_discover_frame_draw_
    concurrent()` -- before the PRIORITIES.md backlog fallback, so a map
    with real BUILD work is unchanged, but a map with only epoch-parked
    atoms left now grants real DISCOVER/FRAME work instead of falling all
    the way through to backlog-or-nothing. The message explicitly forbids
    BUILD output on this tier, matching Rule 1 (gating applies to BUILD
    only).

    ANTI_LIVELOCK_AND_WIDTH.md (P0, 2026-07-13): this is the ONE production
    entry point that opts into `exclude_stalled=True` on every draw lane
    (every other caller/test keeps the default False, i.e. unaffected) --
    the anti-livelock backoff and the idle-tier width fix both apply here,
    where a real turn is actually about to be granted, not at the low-level
    draw functions' own default behaviour.

    THREE_LANES.md (2026-07-13, director-decided, in-console: "mechanise the
    three-lane draw so the supervisor draws SITE and DISCOVERY every cycle
    regardless of BUILD's state. Prose decays; you proved it in three
    hours."): this is the durable anti-decay mechanism replacing the old
    if/elif CASCADE -- which tried the BUILD tier first and RETURNED the
    moment any BUILD atom existed, so it NEVER reached the DISCOVER/FRAME
    tier while BUILD had work and had NO SITE lane at all. A gated/empty
    BUILD lane is NEVER a reason for SITE/DISCOVERY to idle. All THREE lanes
    now draw EVERY cycle and combine into ONE grant message:
      * Lane 1 BUILD -- `_maturity_map_draw_concurrent` (loop_stage=build,
        below target, disjoint scopes; 1-3 concurrent).
      * Lane 2 SITE  -- `_site_lane_draw_concurrent` (site/**-scoped, below
        target, REGARDLESS of loop_stage -- an ungated parallel lane).
      * Lane 3 DISCOVERY -- `_idle_discover_frame_draw_concurrent` (idle
        atoms, real DISCOVER/FRAME gap, doc-only, no BUILD code).
    De-dup runs strictly across lanes: an atom drawn in an earlier lane is
    excluded from later ones (BUILD wins over SITE wins over DISCOVERY), so a
    site-scoped BUILD candidate is granted once, in the BUILD lane. The
    per-lane `atoms-drawn-per-cycle` counts are `log()`ged EVERY cycle so a
    digest/log reader sees each lane's independent activity directly, per the
    staged instruction's own DoD. `map_exhausted` (find_work) is True only
    when ALL THREE lanes AND the backlog fallback are genuinely empty."""
    # OPS13 (clause 4): reset the interleave record FIRST, so a cycle that returns from any
    # priority/fallback rung below leaves `None` behind -- "no maturity-map atom drawn" -- rather
    # than the previous cycle's pair. `find_work` logs the line off this either way; a stale
    # record read as this cycle's pair is the same fail-silent shape as no line at all.
    global _LAST_INTERLEAVE_RECORD
    _LAST_INTERLEAVE_RECORD = None
    # RUNG 1 -- PUBLISH-GATE WEDGE (PRIORITY ZERO, director rulings 2026-07-23/24). Checked FIRST,
    # above every product/HARDEN lane: a publish gate wedged >60 min blocks ALL publishing, so
    # unwedging it is the single highest-value draw. Its ABSENCE was the exact 2h17m tick-silence
    # stall on both 2026-07-23 and 2026-07-24 (the prose rule consumed-not-absorbed twice). R15:
    # proven to fire on the wedged state and stay silent on a passed/empty gate.
    wedge = _publish_gate_wedge_active()
    if wedge:
        log("PUBLISH-GATE WEDGE (RUNG 1, PRIORITY ZERO): gate wedged >60min -> drawing unwedge work "
            "above every product/HARDEN lane (director ruling WEDGE3_AND_RUNG1_MECHANISE 2026-07-24)")
        return wedge
    # RUNG 1b -- PERSISTENT OPERATIONAL-LAYER RED (PRIORITY ZERO, director console 2026-07-25).
    # Checked above every product/HARDEN lane: a daemon-lifecycle RED that has persisted past paging
    # is the exact overnight stall (13 consecutive reds, hourly page, tick rested beside it) this
    # mechanises away. R15: proven to fire on the persistent-red state and stay silent on green.
    op_red = _operational_red_persistent_draw()
    if op_red:
        log("OPERATIONAL-LAYER PERSISTENT-RED (RUNG 1b, PRIORITY ZERO): operational suite RED past "
            "paging threshold -> drawing the daemon-lifecycle fix above every product/HARDEN lane "
            "(director console 2026-07-25)")
        return op_red
    # RUNG 1d -- PRODUCER STARVATION (2026-08-17). Checked beside rungs 1/1b because it is the
    # SAME consequence: rung 1 catches a publisher that cannot push, this catches a producer with
    # nothing to push. Its absence was the 70 minutes of 2026-08-17 in which nine identical
    # KeyError failures fired nine ntfys and drew nothing, while rung 1 read an empty failure list
    # (a dead run never attempts a publish) and rung 1b read GREEN (the daemon was alive; only its
    # output was broken). R15: proven to fire on that recorded state and stay silent on a healthy
    # producer, on a held one, and on a stale counter a later success superseded.
    producer = _producer_starved_active()
    if producer:
        log("PRODUCER STARVATION (RUNG 1d, PRIORITY ZERO): the simulation producer is down -> "
            "drawing the producer fix above every product/HARDEN lane (the RUNG 1 ruling applied "
            "to the other end of the same pipeline, 2026-08-17)")
        return producer

    # RUNG 1c -- BLOCKING FINDING LANE PRECEDENCE (OPS12, clause 3). Computed BEFORE the
    # three-lane draw so a live BLOCKING finding can exclude same-lane "new feature work"
    # candidates from THIS cycle -- never other lanes' (_blocking_lane_draw's own docstring,
    # exit criterion 2). The message (if any) is prepended to whatever this cycle draws,
    # so a blocker with no other-lane work still returns alone, and a blocker alongside
    # other-lane work names both.
    blocker_reason, blocked_lanes = _blocking_lane_draw()
    if blocker_reason:
        log(blocker_reason)

    build_atoms = _maturity_map_draw_concurrent(exclude_stalled=True)
    build_atoms = [a for a in build_atoms if a.get("lane") not in blocked_lanes]
    drawn_ids: set[str] = {a["id"] for a in build_atoms if "id" in a}

    site_atoms = _site_lane_draw_concurrent(exclude_stalled=True, exclude_ids=frozenset(drawn_ids))
    site_atoms = [a for a in site_atoms if a.get("lane") not in blocked_lanes]
    drawn_ids |= {a["id"] for a in site_atoms if "id" in a}

    discovery_atoms = _idle_discover_frame_draw_concurrent(exclude_stalled=True, exclude_ids=frozenset(drawn_ids))
    discovery_atoms = [a for a in discovery_atoms if a.get("lane") not in blocked_lanes]

    # BOUNDED FAN-OUT (director P0, 2026-07-17): cap the COMBINED fork count at MAX_CONCURRENT_FORKS
    # BEFORE assembly -- no 12-fork blooms. Priority BUILD > SITE > DISCOVERY (matches the cross-lane
    # de-dup precedence at line ~1113). Scopes are already disjoint by the de-dup above; the ceiling
    # only trims how MANY of those disjoint atoms one doorbell fans out to at once.
    _raw = (len(build_atoms), len(site_atoms), len(discovery_atoms))
    _budget = MAX_CONCURRENT_FORKS
    build_atoms = build_atoms[:_budget]
    _budget -= len(build_atoms)
    site_atoms = site_atoms[:max(0, _budget)]
    _budget -= len(site_atoms)
    discovery_atoms = discovery_atoms[:max(0, _budget)]

    # OPS13 -- THE PRODUCT INTERLEAVE (clause 4), applied AFTER the fork-budget cap so the arm
    # sees the grant that is actually going out, and BEFORE the per-lane counts are logged so
    # those counts report the post-interleave truth. Mutates the three lane lists in place; the
    # record it returns is what the digest line renders in `find_work`.
    if build_atoms or site_atoms or discovery_atoms:
        _LAST_INTERLEAVE_RECORD = _apply_product_interleave(
            build_atoms, site_atoms, discovery_atoms, blocked_lanes=blocked_lanes)

    # DoD: per-lane atoms-drawn-per-cycle logged EVERY cycle (not only on a
    # concurrent grant) so a starved lane is visible as a zero, not a silence.
    log(
        "THREE-LANE self-refill (atoms-drawn-per-cycle): "
        f"BUILD={len(build_atoms)}, SITE={len(site_atoms)}, DISCOVERY={len(discovery_atoms)}"
    )
    # Live per-cycle status of the always-drawable HARD RULE (until SM1's daily self-note
    # renders it every morning). Makes 'is the anti-rest lane actually wired' visible EVERY
    # cycle -- the consumed-vs-absorbed check the 2026-07-22 stall was about.
    log(forward_discovery_law_status_line())
    # WHOLE-SET enumeration every cycle (director ruling 2026-07-23, R17 class fix §2): a rest is only
    # ever published alongside proof ALL SIX levels are empty -- a lane-scoped proof can never again
    # ground rest. Published here (status line) and in the daily self-note (r17_status).
    log(authorized_set_enumeration_line())
    if sum(_raw) > MAX_CONCURRENT_FORKS:
        log(
            f"BOUNDED FAN-OUT: capped {sum(_raw)} available atoms -> {MAX_CONCURRENT_FORKS} concurrent "
            f"forks (BUILD>SITE>DISCOVERY); raw lanes were BUILD={_raw[0]} SITE={_raw[1]} DISCOVERY={_raw[2]}"
        )

    # Preserve the exact pre-existing single-atom BUILD message byte-for-byte
    # -- but ONLY when a lone BUILD atom is genuinely all there is this cycle
    # (existing callers/NTFY parsing depend on this exact string), and ONLY when no
    # RUNG 1c blocker fired (OPS12 exit criterion 3: a blocker's draw must always name
    # itself in the returned reason, so it can never be silently dropped from this
    # byte-preserved short path).
    if (blocker_reason is None and len(build_atoms) == 1
            and not site_atoms and not discovery_atoms):
        return f"self-refill from maturity map (dial-weighted): {_format_atom_draw(build_atoms[0])}"

    sections: list[str] = []
    if build_atoms:
        lines = "; ".join(_format_atom_draw(a) for a in build_atoms)
        if len(build_atoms) == 1:
            sections.append(f"LANE 1 BUILD (1 atom, dispatch one Agent fork): {lines}")
        else:
            sections.append(
                f"LANE 1 BUILD ({len(build_atoms)} CONCURRENT disjoint atoms -- dispatch one "
                f"Agent fork per atom, per MULTI_ATOM_DRAW.md): {lines}"
            )
    if site_atoms:
        lines = "; ".join(_format_atom_draw(a) for a in site_atoms)
        sections.append(
            f"LANE 2 SITE ({len(site_atoms)} atom(s) -- build site/** in parallel; an UNGATED "
            "lane, disjoint by construction from sim/company (THREE_LANES.md), drawn regardless "
            "of loop_stage; dispatch one Agent fork per atom and pixel-verify each per R11): "
            + lines
        )
    if discovery_atoms:
        lines = "; ".join(_format_atom_draw(a) for a in discovery_atoms)
        sections.append(
            f"LANE 3 DISCOVER/FRAME only ({len(discovery_atoms)} atom(s) -- BUILD gated pending "
            "epoch sequencing (EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1; do NOT write BUILD "
            "code for any of these atoms); dispatch one Agent fork per atom, each independently "
            "read-edit-commit docs/design/maturity_map.yaml inside its own tree_lock "
            "acquisition, never a batched shared edit): " + lines
        )

    if sections:
        combined = (
            "self-refill from maturity map -- THREE-LANE draw "
            f"(BOUNDED PARALLEL: <={MAX_CONCURRENT_FORKS} concurrent Agent forks, disjoint scopes; "
            "FORK LIFECYCLE -- each fork MUST come home: on success merge its branch to main via "
            "tree_lock, on failure reap it; NO orphaned branches): "
            + " || ".join(sections)
        )
        # OPS12 exit criterion 3: a blocker (real or fail-open) that fired this cycle is named
        # IN the returned reason, never only in the log -- so a tick that jumped the queue, or
        # fell back because the index was unreadable, is auditable from the reason string alone.
        return f"{blocker_reason}; {combined}" if blocker_reason else combined

    # RUNG 1c CONTINUED (OPS12 exit criterion 1): a real blocker excluded every same-lane
    # candidate and left nothing else to draw this cycle -- return it ALONE, ahead of the
    # general disposition queue (campaign/backlog/propose-half/forward-discovery/HARDEN
    # rungs below), rather than falling through to them. The fail-open message (blocked_lanes
    # empty) never takes this path: nothing was excluded, so the ordinary rungs below still
    # get a fair chance to draw, which is the "fall back to the ordinary draw order" half of
    # exit criterion 5.
    if blocker_reason and blocked_lanes:
        return blocker_reason

    # OPEN-CAMPAIGN LANE (SEVENTH CLASS, director ruling 2026-07-23): the three below-target lanes
    # are empty here -> before ANY lower rung or rest, draw the next unfinished item of an OPEN
    # campaign. This sits ABOVE backlog/propose-half/forward-discovery/HARDEN because an open PRODUCT
    # campaign is the highest-value fallback (PRODUCT-FIRST). Its ABSENCE was the exact 14:03Z stall:
    # SITE_V5 open with surfaces 2-5 drawable, the tick rested because no lane enumerated the campaign.
    campaign_item = _open_campaign_draw()
    if campaign_item:
        log(
            "OPEN-CAMPAIGN: below-target lanes empty/gated -> drawing the next unfinished item of an "
            "open campaign (finishing item N rolls into N+1, no doorbell; R17 SEVENTH CLASS 2026-07-23)"
        )
        return campaign_item

    # RUNG 4 -- DECLARED-DEFECT BACKLOG (director ruling 2026-07-23, WORK_IS_THE_DEFAULT): the
    # below-target lanes and every open campaign are empty here -> before ANY lower rung or rest,
    # draw the highest-priority open declared fidelity defect. "A declared defect that is not in the
    # drawable set is a contradiction." Its ABSENCE was today's exact state: spike-tail declared top
    # priority, no staged docs, the whole-set enumeration all-empty -> the tick called rest legitimate
    # while a five-day-untouched defect sat open. Sits ABOVE the PRIORITIES-prose fallback / propose-
    # half / forward-discovery / HARDEN floor -- a declared fidelity gap is real product work.
    defect_item = _declared_defect_backlog_draw()
    if defect_item:
        log(
            "DECLARED-DEFECT: below-target + open-campaign lanes empty/gated -> drawing the "
            "highest-priority open declared defect (RUNG 4; WORK_IS_THE_DEFAULT 2026-07-23)"
        )
        return defect_item

    # RUNG 4b -- STALE PUBLISHED GAP MEASUREMENT (2026-08-10, H_GAP residual (d)): the declared-defect
    # backlog is empty here -> before any lower rung or rest, re-take any coupled-gap number whose
    # producing code has changed since it was measured. Its ABSENCE is why five consecutive ticks
    # re-ran these tools by hand while the reconcile paged: report-only drift with no rung behind it is
    # exactly the operational-red failure mode one rung up. Below RUNG 4 (an open product defect
    # outranks a stale number), above propose-half/forward-discovery/HARDEN (real evidence work beats
    # re-verifying a finished atom).
    stale_gap_item = _stale_gap_row_draw()
    if stale_gap_item:
        log(
            "STALE-GAP-ROW: below-target + campaign + declared-defect lanes empty/gated -> drawing "
            "the re-measurement of published coupled-gap rows whose producing code has changed "
            "(RUNG 4b; docs/design/GAP_TOOL_RERUN_OWNERSHIP.md)"
        )
        return stale_gap_item

    backlog_item = _actionable_backlog_item()
    if backlog_item:
        return f"self-refill from PRIORITIES.md backlog (fallback, maturity map unavailable): {backlog_item}"

    # PROPOSE-HALF LANE (director ruling 2026-07-23, R17 CLASS FIX): a BUILD-gated item whose
    # graduation carries an ungated build-PROPOSAL step is drawable in that propose half -- ALWAYS.
    # This rung sits ABOVE forward-discovery DISCOVER and the HARDEN treadmill: writing a graduated
    # track's build proposal is the next real step toward a BUILD atom, higher value than re-DISCOVER
    # or re-verify. Its ABSENCE was the exact overnight R10-breach (F1 graduated to FRAME, proposal
    # drawable all night, no lane enumerated it -> the tick rested over doable work).
    propose_item = _propose_half_draw()
    if propose_item:
        log(
            "PROPOSE-HALF: core+idle+backlog empty/gated -> drawing an ungated build-proposal step "
            "(a BUILD-gated item's propose half is always drawable; R17 class fix 2026-07-23)"
        )
        return propose_item

    # ALWAYS-DRAWABLE LANE (HARD RULE, director console 2026-07-22): CORE (BUILD/SITE) +
    # IDLE-ADVANCE (DISCOVER/FRAME + backlog) are all empty/gated here -> fall through to the
    # FORWARD-DISCOVERY register (F1-F5) BEFORE the Rule-0 HARDEN treadmill or any rest. This is
    # the ladder rung whose ABSENCE caused the 95-min R13-wait stall (the register was full; the
    # tick rested because this lane was never wired). Preferred over the HARDEN treadmill the
    # director declines every cycle: standing DISCOVER work beats re-verifying finished atoms.
    forward_item = _forward_discovery_draw()
    if forward_item:
        return forward_item

    # RUNG 7 -- THE PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): rungs 1-6 are empty,
    # so BEFORE falling to the RULE-0 HARDEN treadmill (re-verifying finished atoms -- the work the
    # director declines every cycle), MINT the next batch from the director's ratified goals. This is
    # the rung whose ABSENCE let the 13:06Z tick publish "whole authorized set empty" while owed work
    # (SITE_MODEL_SPINE evidence pages, premise-demand publish, follow-ons) sat un-minted as prose.
    # Preferred over the HARDEN treadmill: planning new work beats re-verifying done work.
    planner_item = _planner_rung_draw()
    if planner_item:
        log("RUNG 7 PLANNER: rungs 1-6 empty + ratified goals present -> MINTING the next batch "
            "(propose-then-proceed) rather than resting or re-verifying finished atoms "
            "(director ruling WORK_IS_THE_DEFAULT 2026-07-23)")
        return planner_item

    # §1+§3 SUPPRESSION (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27): before the
    # RULE-0 HARDEN floor, check for an unconsumed staged [DIRECTOR-RULING]/[STEER]. If one is
    # present it is RUNG 1 (`find_work`'s `primary`) and MUST draw within one tick (§3); re-verifying
    # at-target atoms while a ruling names undone work is the busywork-bias the ruling forbids (§1).
    # Return None so the ruling draws ALONE -- never appended to as 'ALSO -- RULE 0 self-refill ...
    # HARDEN'. Placed HERE (the caller), not in `_rule0_harden_draw`, so the pure draw stays testable
    # without STAGING_DIR isolation (test_harden_ability_gate reads the real docs/staging/): the
    # suppression is a CALLER-level rung-order rule, not a property of the at-target pick itself.
    # R15 reproduces the 2026-07-27 08:23-10:25 state (HARDEN candidate + unconsumed ruling -> None).
    if _unconsumed_director_ruling_or_steer():
        log(
            "RULE 0 HARDEN tier SUPPRESSED: an unconsumed staged [DIRECTOR-RULING]/[STEER] is RUNG 1 "
            "and must draw first -- re-verifying at-target atoms while a ruling names undone work is "
            "the busywork-bias DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27 §1+§3 forbids"
        )
        return None
    # RULE 0 (2026-07-14, director, THE PRIME DIRECTIVE): an empty feasible set
    # is a DEFECT IN THE DIALS, not a reason to hold. Every below-target lane and
    # the backlog are empty -> yield the below-target dial and draw HARDEN/red-
    # team work on an at-target atom, so the draw is provably non-empty while ANY
    # atom exists. Only a map with zero at-target atoms (a genuinely empty map =
    # a wall) returns None.
    harden_atom = _rule0_harden_draw()
    if harden_atom is not None:
        log(
            "RULE 0: all below-target lanes + backlog empty -> yielded the below-target "
            f"dial to HARDEN/red-team at-target atom {harden_atom.get('id')}"
        )
        return (
            "RULE 0 self-refill (dial yielded -- no below-target work anywhere; the to-do "
            f"list is never empty): HARDEN/red-team the AT-target atom {_format_atom_draw(harden_atom)} "
            "-- re-verify its exit tests still hold, mutation-re-test a control, red-team its "
            "invariants, or widen its real-world fidelity. NTFY the director this dial was yielded."
        )
    return None


def _priority_zero_active() -> bool:
    """Is one of the PRIORITY-ZERO rungs live -- wedged publish gate, dead producer, persistent
    operational red?

    Asked through the ladder's OWN predicates rather than by sniffing the message it returns: a
    string test would break the first time a rung reworded itself, and would break silently, in
    the direction of diluting an emergency.

    FAILS TOWARD THE EMERGENCY. Any error reads as "yes, something is wrong", because the harmful
    mistake here is handing a worker a delivery item alongside a dead pipeline; the harmless one
    is delaying a delivery item by one thirty-minute tick.
    """
    try:
        if _publish_gate_wedge_active():
            return True
        if _producer_starved_active():
            return True
        if _operational_red_persistent_draw():
            return True
    except Exception:  # noqa: BLE001 - see docstring
        return True
    return False


def _self_refill_draw() -> str | None:
    """The whole draw: LANE 0 (the delivery seat's decision) PLUS the ladder, never one instead of
    the other.

    ALONGSIDE IS THE WHOLE DESIGN (docs/design/THE_DELIVERY_SEAT.md 5b). The first version of this
    let a delivery item RETURN, and three R17 tests caught it inside the hour: with the three map
    lanes gated, `PROPOSE-HALF` and `FORWARD-DISCOVERY` stopped firing because the delivery item
    returned above them. That is exactly the shape `THREE_LANES.md` was written against -- a
    cascade that returns on the first non-empty tier starves every tier below it -- and the
    forward-discovery lane is the always-drawable floor R17 exists to protect. A new tier at the
    top of that ladder is that regression wearing a delivery seat's clothes, and it took a
    delivery seat about forty minutes to build one.

    So the seat's decision is PREPENDED to whatever the ladder produces. Every rung keeps firing
    exactly as before, every existing assertion on the ladder's own string still holds, and
    nothing below can be starved by a seat that names work every three hours.

    When the lane is empty -- no live direction, every item an atom, or all of them claimed -- the
    return value is byte-identical to the ladder's, which is what it was before this existed.
    """
    if _priority_zero_active():
        # AN EMERGENCY IS THE WHOLE MESSAGE. Rungs 1/1b/1d exist because a wedged publish gate, a
        # dead producer or a persistent operational red each stop the project outright, and they
        # outrank every product lane by ruling. Prepending a delivery item to one of them would
        # hand a worker two things to do with the urgent one second -- diluting the exact
        # precedence those rungs were built to assert. `test_producer_starvation_draw.py` asserts
        # the equality that catches this, and it caught it.
        #
        # The delivery seat AGREES, which is the reassuring part: its own second focus item on the
        # day this landed was "publish-path-lands". A seat that decides what matters would put the
        # outage first too.
        return _self_refill_draw_ladder()

    delivery = _delivery_lane_draw()
    ladder = _self_refill_draw_ladder()
    if delivery:
        log("LANE 0 DELIVERY: drew the delivery seat's own decision ahead of the dial-weighted "
            "lanes, ALONGSIDE them (background/delivery_lane.py)")
    if delivery and ladder:
        return f"{delivery} || {ladder}"
    return delivery or ladder


def _is_drained_and_gated() -> bool:
    """DRAINED-AND-GATED predicate (ADVISOR_STEER_IDLE_TREADMILL_AND_GHOST_WORKTREE_2026-07-18,
    item 1). True iff there is NO below-target buildable work anywhere -- the BUILD, SITE and
    DISCOVER/FRAME lanes AND the PRIORITIES backlog are all genuinely empty -- so the ONLY thing
    the self-refill draw could offer is at-target HARDEN re-verification of already-finished atoms
    while the remaining below-target work is blocked on a director act. That is a LEGITIMATE
    RESTING STATE, not idleness-as-avoidance: by construction, reaching it means every below-
    target/SITE/DISCOVER/FRAME lane is genuinely empty (if ANY had work it would be drawn and
    delivered, never rested on) and the only remaining draw is the RULE-0 HARDEN treadmill the
    director has correctly declined every cycle.

    Mirrors H23's `_is_frame_saturated` style: a standalone, computed predicate the draw consults.
    INDEPENDENCE (R15): keyed on the ACTUAL emptiness of the three real lanes + the backlog (the
    same calls `_self_refill_draw` makes), NEVER on a constant -- so a mutation that hard-codes it
    True is caught by the real-work test (a below-target atom present -> the BUILD lane is non-empty
    -> this returns False). FAIL-SAFE TOWARD WORK: any error -> False (never rest while unsure; the
    harmful failure mode is resting when real work exists, so ambiguity keeps the anti-idleness
    pressure -- Rule 0's 'the to-do list is never empty' wins any tie)."""
    try:
        # RUNG 1 -- PUBLISH-GATE WEDGE (PRIORITY ZERO, director rulings 2026-07-23/24): rest is
        # NEVER legitimate while the publish gate is wedged >60min -- that is the highest-priority
        # drawable work. Mirror of the top rung added to `_self_refill_draw`; without it,
        # `_is_drained_and_gated` would green-light the exact 2h17m rest the draw now refuses.
        if _publish_gate_wedge_active():
            return False
        # RUNG 1b -- PERSISTENT OPERATIONAL-LAYER RED (PRIORITY ZERO, director console 2026-07-25):
        # rest is NEVER legitimate while the operational suite has been RED past paging. Mirror of the
        # rung added to `_self_refill_draw`; without it, `_is_drained_and_gated` would green-light the
        # exact overnight rest the draw now refuses (13 consecutive reds, tick resting beside them).
        if _operational_red_persistent_draw():
            return False
        # RUNG 1d -- PRODUCER STARVATION (2026-08-17): rest is NEVER legitimate while the
        # simulation producer is down. Mirror of the rung added to `_self_refill_draw`;
        # without it, `_is_drained_and_gated` would green-light rest beside a pipeline that
        # has stopped producing anything to publish -- which is what "the three lanes are
        # empty" looked like for 70 minutes on 2026-08-17.
        if _producer_starved_active():
            return False
        # RUNG 1c -- BLOCKING FINDING LANE PRECEDENCE (OPS12, clause 3): rest is never
        # legitimate while a BLOCKING finding sits live in any lane -- it is real, ahead-
        # of-everything-else work by the ruling's own words. Mirror of the rung added to
        # `_self_refill_draw`; without it, a lane-scoped proof (every OTHER lane genuinely
        # empty) could ground rest while a known-untrustworthy instrument sits unrepaired,
        # exactly the state clause 3 exists to make undrawable-as-rest.
        _blocker_reason, _blocked = _blocking_lane_draw()
        if _blocker_reason and _blocked:
            return False
        if _maturity_map_draw_concurrent(exclude_stalled=True):
            return False
        # BUILD empty (returned above if not) -> nothing was drawn, so exclude_ids is empty; an
        # emptiness check is RNG-independent (a lane is empty or not regardless of which atom it
        # would pick), so re-running the same draws the refill uses cannot flap.
        none_drawn: frozenset = frozenset()
        if _site_lane_draw_concurrent(exclude_stalled=True, exclude_ids=none_drawn):
            return False
        if _idle_discover_frame_draw_concurrent(exclude_stalled=True, exclude_ids=none_drawn):
            return False
        if _actionable_backlog_item():
            return False
        # OPEN-CAMPAIGN LANE (SEVENTH CLASS, director ruling 2026-07-23): rest is illegitimate while
        # an open campaign has any unfinished item. Mirror of the rung added to `_self_refill_draw`;
        # without it, `_is_drained_and_gated` would green-light the exact 14:03Z rest the draw now
        # refuses. A lane-scoped proof can never again ground rest -- the WHOLE set, open campaigns
        # included, must be empty (ruling §2).
        if _open_campaign_draw():
            return False
        # RUNG 4 -- DECLARED-DEFECT BACKLOG (director ruling 2026-07-23, WORK_IS_THE_DEFAULT): rest is
        # illegitimate while any declared fidelity defect is still open. Mirror of the rung added to
        # `_self_refill_draw`; without it, `_is_drained_and_gated` would green-light the exact today-
        # state rest the draw now refuses (spike-tail declared, whole-set read all-empty). A declared
        # defect not in the drawable set is a contradiction -- the WHOLE set, defects included, must be
        # empty before rest (ruling rung 4).
        if _declared_defect_backlog_draw():
            return False
        # RUNG 4b -- STALE PUBLISHED GAP MEASUREMENT (2026-08-10): rest is illegitimate while a public
        # door shows a gap number produced by code that has changed and a re-run would clear it. Mirror
        # of the rung added to `_self_refill_draw`; without it, `_is_drained_and_gated` would green-light
        # rest over work the draw itself refuses -- the mirror-drift shape that made the earlier rungs
        # necessary one at a time.
        if _stale_gap_row_draw():
            return False
        # PROPOSE-HALF LANE (director ruling 2026-07-23, R17 CLASS FIX): rest is illegitimate while a
        # BUILD-gated item's ungated build-PROPOSAL step is still open. This is the mirror of the rung
        # added to `_self_refill_draw`; without it, `_is_drained_and_gated` would green-light a rest the
        # draw has already refused (the exact overnight breach: a graduated-but-unproposed track present,
        # the tick resting over it). A lane-scoped proof can never again ground rest -- the WHOLE set,
        # propose-halves included, must be empty (ruling §2).
        if _propose_half_draw():
            return False
        # ALWAYS-DRAWABLE LANE (HARD RULE, director console 2026-07-22): rest is legitimate ONLY
        # with PROOF the authorized set is empty AT EVERY LEVEL -- including forward-discovery.
        # While the F1-F5 register has a drawable track, this is NOT a resting state (the tick must
        # draw it, not rest). This is the mirror of the rung added to `_self_refill_draw`; without
        # it, `_is_drained_and_gated` would green-light a rest that `_self_refill_draw` has already
        # refused, and find_work's rest branch (`refill and _is_drained_and_gated()`) would fire.
        if _forward_discovery_draw():
            return False
        # RUNG 7 -- THE PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): rest is illegitimate
        # while the planner can still MINT from ratified goals. Mirror of the rung added to
        # `_self_refill_draw`; without it, `_is_drained_and_gated` would green-light the exact 13:06Z
        # rest the draw now refuses. Rest is legitimate ONLY below rung 7 -- when even planning can
        # propose nothing within ratified scope (axes absent). Pre-go-live that is structurally
        # unreachable, which is the point.
        if _planner_rung_draw():
            return False
        # EIGHTH CLASS (director ruling 2026-07-27): rest is illegitimate while a BLOCKED in_progress
        # mint batch is open -- "a blocked batch is a reason to plan more, never a licence to rest".
        # Mirror of the enumeration `blocked_mints` level; without it, `_is_drained_and_gated` would
        # green-light the exact 42h rest, and the deadman's proven-rest fold (which trusts THIS
        # predicate) would keep suppressing the [STALL] alarm beside 6 blocked mints. The 2h rest-proof
        # age cap bounds how often the planner re-examines; this bounds the tick from resting AT ALL
        # while mints sit blocked (it does at-target HARDEN + the deadman escalates the blockers).
        if _blocked_mints_open():
            return False
        # All real lanes + backlog + forward-discovery + planner empty. It is a RESTING state only if
        # at-target HARDEN atoms exist; otherwise a genuinely-empty map = a WALL (map_exhausted).
        return _rule0_harden_draw() is not None
    except Exception:
        return False


ORIGIN_STAGING_SYNC_STAMP = PROJECT_DIR / "docs" / "observability" / ".origin_staging_sync.json"
ORIGIN_STAGING_SYNC_INTERVAL_SECONDS = 90


def _default_git_runner(*args: str):
    import subprocess as _sp
    return _sp.run(["git", *args], cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=45)


def _sync_origin_staging(_runner=None) -> list[str]:
    """RC3 fix (2026-07-19, director-priority): a RESTED loop must WAKE on an origin-[ADVISOR-STAGED]
    doc, not only on console/interactive input. The staging bridge commits advisor docs to ORIGIN;
    the local tree that `find_work` reads never auto-pulled, so an origin-staged directive stayed
    invisible until a human pulled -- the 2026-07-19 unconsumed-doc failure (LOOP_CONTINUITY_FAILURE_
    DIAGNOSIS.md, RC3). This fetches origin and writes any root-level `docs/staging/*.md` present on
    origin but not locally into the local tree (via `git show`, so NO index pollution), so the normal
    staging scan sees them next cycle. Rate-limited (INTERVAL) and FAIL-SAFE in every mode: a git or
    network error, or a missing stamp, is a silent no-op -- the sync is a convenience, never a gate,
    and must never stall the loop (Rule 0). Returns the list of filenames pulled (for logging/tests)."""
    run = _runner or _default_git_runner
    try:
        import json as _json
        import time as _time
        try:
            last = float(_json.loads(ORIGIN_STAGING_SYNC_STAMP.read_text()).get("ts", 0))
        except Exception:
            last = 0.0
        now = _time.time()
        if (now - last) < ORIGIN_STAGING_SYNC_INTERVAL_SECONDS:
            return []
        run("fetch", "origin", "main", "-q")
        r = run("ls-tree", "--name-only", "origin/main", "docs/staging/")
        origin_md = {ln.strip() for ln in (r.stdout or "").splitlines()
                     if ln.strip().endswith(".md") and ln.strip().count("/") == 2}
        # Exclude a doc already present locally in the ROOT *or* consumed into done/
        # or in_progress/ (2026-07-21 class-fix): comparing origin-root against local-
        # root ONLY would re-materialise a doc that was consumed into a subdir back
        # into the root every cycle, re-jamming the scan and re-pinging the director
        # (the same incomplete-exclusion class as staging_watcher.check_remote). Match
        # by basename mapped to the root key form so a done/X.md subtracts origin's X.md.
        local_md = set()
        for _sub in ("", "done", "in_progress"):
            _d = STAGING_DIR / _sub if _sub else STAGING_DIR
            if _d.is_dir():
                local_md |= {f"docs/staging/{p.name}" for p in _d.iterdir() if p.suffix == ".md"}
        pulled = []
        for f in sorted(origin_md - local_md):
            show = run("show", f"origin/main:{f}")
            if getattr(show, "returncode", 1) == 0:
                (PROJECT_DIR / f).write_text(show.stdout, encoding="utf-8")
                pulled.append(f.split("/")[-1])
        if pulled:
            log(f"RC3 origin-staging sync: pulled {len(pulled)} origin-staged doc(s) into the local "
                f"tree so the draw sees them: {', '.join(pulled)}")
        try:
            ORIGIN_STAGING_SYNC_STAMP.write_text(_json.dumps({"ts": now}))
        except Exception:
            pass
        return pulled
    except Exception:
        return []  # fail-safe: an origin-sync error never stalls the loop


def find_work(resumed_from_pause: bool) -> tuple[str | None, bool]:
    """Return (reason, map_exhausted). `reason` is a human-readable string
    if any real work exists (an instruction-channel doorbell, and/or a
    self-refill draw), else None. `map_exhausted` is True only when the
    self-refill draw itself found no candidate at all (every atom
    blocked/complete/unreadable) -- distinct from "didn't draw because an
    agenda/urgent item took priority" (requirement 4: escalate on
    CANNOT-draw, never on didn't-draw). Checked fresh every cycle -- no
    "already nudged" memory, by design (that memory is exactly what caused
    failure #4's silent gap).

    R3_WORK_GRANTING_REDESIGN.md (P0, 9th idle variant, 2026-07-12,
    director-caught): work-granting was TRIGGER-DRIVEN ("doorbell -> if
    nothing there -> idle") when it must be BACKLOG-DRIVEN ("doorbell (if
    any) -> handle it -> THEN draw the next atom from the map, always").
    Two changes from the pre-redesign version: (1) the "unprocessed
    staging" check now uses `_real_staged_instructions()`, which excludes
    routine daemon markers (run_complete_*.md) -- these used to look like
    "real work exists on the instruction channel" and short-circuit this
    function before it ever reached the self-refill draw, even though the
    daemon marker needed no granted turn to be handled at all. (2) the
    self-refill draw is now UNCONDITIONAL: it runs and gets appended to the
    reason even when a real agenda/urgent/staged item already fired, so a
    granted turn is never JUST "here's today's daemon housekeeping" with no
    real capability-building work attached."""
    if resumed_from_pause:
        return "usage-limit pause just ended -- resume work", False

    primary: str | None = None

    # RC3 (2026-07-19): pull any origin-[ADVISOR-STAGED] docs into the local tree BEFORE the staging
    # scan, so a rested loop wakes on an origin-staged directive (not only console input). Fail-safe.
    _sync_origin_staging()

    agenda = agenda_module.load_agenda()
    if agenda:
        primary = f"agenda open -- phase '{agenda.get('phase', '?')}', step '{agenda.get('step', '?')}'"
    else:
        staged = _real_staged_instructions()
        urgent = _urgent_from_rich_pending(staged)
        if urgent:
            primary = f"urgent from_rich queued -- {urgent}"
        elif staged:
            primary = f"unprocessed staging -- {', '.join(staged)}"
            # §2+§4 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27): a drawn
            # [DIRECTOR-RULING]/[STEER] is a MINT SOURCE -- instruct the drawn turn to mint one atom
            # per named deliverable from its WORK THIS CREATES block (or flag the §4 missing-block
            # defect). None for every non-ruling staged doc, so `primary` is byte-identical there.
            mint = ruling_mint_instruction(staged)
            if mint:
                primary = f"{primary}; {mint}"

    refill = _self_refill_draw()

    # OPS13 exit criterion 4 -- SILENCE IS THE FAILURE. Logged on EVERY cycle, unconditionally,
    # BEFORE any of the returns below: paired, violated, armed-and-found-nothing, clause-2
    # substituted, or no atom drawn at all. The one thing this line may never do is not appear
    # -- an interleave line absent on the bad day is indistinguishable from an interleave that
    # never fired, which is the fail-silent shape the atom exists to forbid (and this project's
    # daily digest already has a branch that can skip itself entirely -- see OPS14).
    log(product_interleave_digest_line(_LAST_INTERLEAVE_RECORD))

    if primary and refill:
        return f"{primary}; ALSO -- {refill}", False
    if primary:
        return primary, False

    # DRAINED-AND-GATED QUIET WAIT (ADVISOR_STEER 2026-07-18, item 1): if the ONLY thing the
    # refill can offer is at-target HARDEN re-verification -- every below-target BUILD/SITE/
    # DISCOVER/FRAME lane AND the backlog empty, remaining work blocked on a director act --
    # settle into a quiet wait instead of re-offering the HARDEN treadmill every cycle (the
    # director has correctly declined it repeatedly). (None, map_exhausted=False) is a THIRD,
    # legitimate state: NOT real work, but NOT a broken/exhausted map either; consumers
    # (run_cycle, the pull-loop Stop hook) rest quietly on it and never alarm/thrash. RULE 0's
    # 'the to-do list is never empty' is UNTOUCHED for the real-work case: the instant any below-
    # target/DISCOVER/FRAME/SITE work or a staged doc exists, a lane / `primary` above fires and
    # this branch is never reached -- only re-verifying finished atoms while blocked on a human
    # settles quiet. The check is placed AFTER `primary` so a new staged doc/agenda always wins.
    if refill and _is_drained_and_gated():
        log("DRAINED-AND-GATED quiet wait -- no below-target/SITE/DISCOVER/backlog work; the only "
            "draw would be at-target HARDEN re-verification while blocked on a director act. "
            "Settling quiet (not exhausted, not an idle defect); a genuinely new signal wakes it.")
        return None, False

    if refill:
        return f"agenda+staging empty -- {refill}", False

    # Nothing anywhere -- requirement 1: this must be an impossible
    # terminal state while the map has open atoms, so reaching here means
    # the map itself is genuinely exhausted (every atom blocked/complete)
    # or unreadable, which is itself a finding worth surfacing once
    # (see _check_map_exhausted_escalation), not a silent "idle, no work".
    return None, True


def _stuck_key(reason: str) -> str:
    """The narrow, comparable state used to detect 'no real progress' --
    deliberately NOT the full find_work() reason string or a broad snapshot
    of everything on disk (2026-07-11 redesign; see STUCK_THRESHOLD_SECONDS
    for why the prior broad fingerprint silently masked a full night of a
    genuinely stuck 'unprocessed staging' case).

    Two specific exclusions, both confirmed root causes:
    - run_complete_*.md markers are excluded from the staging list used
      here. They self-process on sim_runner's/background_worker's own
      pipeline cadence; their transient appearance/disappearance is routine
      housekeeping, not evidence a DIFFERENT stuck staged file has moved.
    - PRIORITIES.md's mtime is folded in ONLY for the self-refill-from-
      backlog path, where an edited file genuinely is the progress signal
      (a self-refill turn closing item X changes the file even though the
      next self-refill draw's reason text might otherwise look the same).
      For the unprocessed-staging/urgent/agenda paths it is irrelevant noise
      -- real work closing some OTHER, unrelated item was resetting the
      stuck-clock for these two untouched files every time overnight."""
    agenda = agenda_module.load_agenda()
    if agenda:
        return json.dumps({"kind": "agenda", "updated_at": agenda.get("updated_at")}, sort_keys=True)
    if "self-refill from PRIORITIES.md backlog" in reason:
        try:
            priorities_mtime = PRIORITIES_PATH.stat().st_mtime
        except OSError:
            priorities_mtime = None
        return json.dumps({"kind": "backlog", "priorities_mtime": priorities_mtime}, sort_keys=True)
    # Reuse the single source of truth for "what's a routine daemon marker"
    # (_is_daemon_marker) rather than a second, independently-drifting copy
    # of the same exclusion list.
    non_transient_staged = _real_staged_instructions()
    return json.dumps({"kind": "staging", "reason": reason, "staged": non_transient_staged}, sort_keys=True)


def _load_stuck_state() -> dict:
    if not STUCK_STATE_FILE.exists():
        return {}
    try:
        return json.loads(STUCK_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_stuck_state(state: dict) -> None:
    STUCK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STUCK_STATE_FILE.write_text(json.dumps(state, sort_keys=True))


_STUCK_VOLATILE_NUMBER_RE = re.compile(r"\d+")
# ...and the PLURAL the number drives. "1 file"/"2 files" and "1 time"/"2 times" survive digit
# normalisation as `# file` vs `# files`, which is still a churning key -- caught by this atom's
# own replay test rather than reasoned about, which is why it is here. Deliberately narrow: it
# strips a terminal `s` ONLY from the word immediately following a normalised number, so it can
# never merge two differently-NAMED items (`# atoms_pending` is untouched -- `s_` is not a word
# boundary), and it is deterministic.
_STUCK_VOLATILE_PLURAL_RE = re.compile(r"(#\s+\w+?)s\b")


def _stuck_episode_key(reason: str) -> str:
    """PW4 -- THE CLOSE CONDITION for the supervisor stuck episode: the WORK changed, not its
    WORDING.

    `first_seen_at` is an episode start and `_check_stuck_escalation` both writes it and reads
    it to decide escalation, so the census flags it as self-clearing. Its episode identity came
    from `_stuck_key`, which folds the free-text `reason` in verbatim -- and these reasons
    RENDER counts, elapsed minutes, levels and dates into the prose ("...3 unprocessed
    staging...", "...level 0->2...", a date stamp). Every re-render was a different key, so
    `first_seen_at` was re-stamped and one long stall read as a series of short ones: the 2h
    threshold could never be reached while the numbers moved. Same shape as the publish gate,
    keyed on a string instead of a clock.

    THE CONDITION: the episode closes when the reason's NUMBER-NORMALISED form changes, or when
    the evidence `_stuck_key` already carries changes -- the agenda's `updated_at`,
    PRIORITIES.md's mtime, or the set of genuinely-staged instructions. All of those are read
    off the filesystem and off find_work's live draw at each call, never off
    `.supervisor_stuck_state.json` (R15 anti-tautology): the state file cannot vouch for its own
    episode ending.

    WHY NORMALISE RATHER THAN DROP THE REASON: dropping it entirely would make every draw made
    against the same staging backlog ONE episode, and the supervisor legitimately draws
    DIFFERENT atoms hour to hour -- that would page "stuck on the same work" at work that is
    genuinely moving. A control false-positive jams the channel as effectively as a blind one.
    Normalising the digits collapses the re-renders and keeps distinct work distinct, because
    what distinguishes one atom or staged file from another is its NAME, not its numbers."""
    parsed = json.loads(_stuck_key(reason))
    if "reason" in parsed:
        normalised = _STUCK_VOLATILE_NUMBER_RE.sub("#", parsed["reason"])
        parsed["reason"] = _STUCK_VOLATILE_PLURAL_RE.sub(r"\1", normalised)
    return json.dumps(parsed, sort_keys=True)


def _check_stuck_escalation(reason: str) -> None:
    """Wall-clock, disk-persisted escalation (2026-07-11 redesign) -- see
    STUCK_THRESHOLD_SECONDS and _stuck_key(). Persisting to disk (rather
    than an in-memory counter) means a supervisor.py restart mid-stuck-
    period does not silently reset the clock either -- another latent gap
    the prior in-memory-only design had.

    PW4: the episode is keyed on _stuck_episode_key (the observed work), not on the reason
    prose, and the write goes through the class guard so a re-key cannot move the start
    forward. `escalated` rides the episode too -- a reason churn that no longer resets the
    clock must not re-arm the page either, or one stall would page repeatedly (R5)."""
    key = _stuck_key(reason)
    episode_key = _stuck_episode_key(reason)
    state = _load_stuck_state()
    now = time.time()
    episode_closed = state.get("episode_key") != episode_key
    proposed = {
        "key": key,
        "episode_key": episode_key,
        "first_seen_at": now,
        "escalated": False if episode_closed else bool(state.get("escalated")),
    }
    state = guard_episode(state, proposed, since_fields=STUCK_SINCE_FIELDS,
                          episode_closed=episode_closed)
    _save_stuck_state(state)
    if episode_closed:
        return
    first_seen_at = state.get("first_seen_at", now)
    elapsed = now - first_seen_at
    if elapsed >= STUCK_THRESHOLD_SECONDS and not state.get("escalated"):
        minutes = int(elapsed // 60)
        # THE SECOND CLOSE CONDITION (2026-08-24): the doorbell key has not changed, but did the
        # SEAT actually move? _stuck_key's staging list is permanently resident, so the key alone
        # can only ever say "the same work is still on the list" -- never "nothing happened".
        # Real landings mean turns are being delivered and used, which is the precise claim this
        # page makes; so the episode closes on the work, not on the shopping list. None (git
        # unavailable) is a FAILED check and deliberately does NOT suppress: an alarm fails toward
        # paging.
        landed = _substantive_commits_since(first_seen_at)
        if landed:
            log(f"STUCK escalation suppressed -- {landed} substantive commit(s) landed in the "
                f"last ~{minutes}min, so turns are being delivered and used; the doorbell is "
                f"resident work, not a stall. Episode reset. -- {reason}")
            state = guard_episode(
                state, {"key": key, "episode_key": episode_key, "first_seen_at": now,
                        "escalated": False},
                since_fields=STUCK_SINCE_FIELDS, episode_closed=True)
            _save_stuck_state(state)
            return
        # `reason` is the DOORBELL -- the raw work order find_work() hands the tick. Interpolated
        # whole, it put 114 staged filenames on the director's phone on 2026-08-13. He needs the
        # STATE (turns granted for an hour, nothing moving) and one handle on the work, not the
        # machine's shopping list. `background/doorbell_redaction.py` is the backstop that makes
        # this true of every sender; this is the sender that made it necessary.
        from background.doorbell_redaction import summarise_work_order as _summarise_work_order
        ntfy(
            f"Supervisor: granting turns for ~{minutes}min for the same work "
            f"({_summarise_work_order(reason)}) with no state change -- something below the tmux "
            "layer may be swallowing turns (see doorbell failure #4), or "
            "this is genuinely blocked and needs your input."
        )
        log(f"STUCK escalation sent -- ~{minutes}min unchanged -- {reason}")
        state["escalated"] = True
        _save_stuck_state(state)


def _atom_fingerprint(atom: dict) -> str:
    """A cheap, stable signature of an atom's own mutable state -- used by
    the anti-livelock stall tracker (ATOM_STALL_STATE_FILE) to detect "this
    atom was re-selected but genuinely nothing about it changed since last
    time." Built from fields a real FRAME/BUILD/HARDEN pass always touches
    when it makes real progress (level, loop_stage, simplifications count,
    expert-hour timestamp) -- deliberately NOT a hash of the whole atom
    dict, since unrelated cosmetic reformatting elsewhere in the same YAML
    file must not read as progress on THIS atom."""
    expert_hour = atom.get("expert_hour") or {}
    parts = (
        str(atom.get("level_current")),
        str(atom.get("level_target")),
        str(atom.get("loop_stage")),
        # simplifications moved to the sibling store (retro FM-1); the map now
        # carries the count directly. The fingerprint only ever needed the count
        # (a note being appended == progress), so this is value-identical.
        str(atom.get("simplifications_count") or 0),
        str(expert_hour.get("last")),
    )
    return "|".join(parts)


# Positions in the "|"-joined _atom_fingerprint above.
_FP_LEVEL_CURRENT, _FP_LEVEL_TARGET, _FP_LOOP_STAGE, _FP_SIMPLIFICATIONS, _FP_EXPERT_HOUR = range(5)
ATOM_STALL_STREAK_FIELDS = ("consecutive_unchanged",)


def _atom_fingerprint_progressed(old: str | None, new: str) -> bool:
    """PW4 -- THE CLOSE CONDITION for an atom's stall episode: the atom actually MOVED.

    `consecutive_unchanged` is an episode counter and `_record_atom_draw_and_check_stall` writes
    the same field its own stall check reads, so the census flags it as self-clearing. The
    episode used to close on ANY fingerprint difference -- and two of the five fingerprint
    components change without the atom advancing:

      * `expert_hour.last` -- a HARDEN pass that RE-STAMPS an at-target atom and does nothing
        else. That is the livelock the stall tracker exists to catch, and it was resetting the
        very counter meant to catch it: draw, re-stamp, count back to 1, forever.
      * `level_target` -- re-planning where the atom is GOING. It says nothing about whether the
        atom has moved, and an atom re-targeted mid-stall would read as fresh.

    THE CONDITION: `level_current` changed, `loop_stage` changed, or `simplifications_count`
    went UP. Those three are the atom's own advancing state in `docs/design/maturity_map.yaml`,
    read from the map at draw time and never from `.atom_stall_tracker.json` (R15
    anti-tautology).

    `simplifications_count` is required to INCREASE, not merely differ, because it is a count:
    a count that drops is bookkeeping (a note rehomed, a store rebuilt), not work done.

    An absent prior fingerprint is a close -- a first draw starts a fresh episode, and there is
    no earlier episode it could be shortening.

    A fingerprint whose SHAPE is not the 5-part one above degrades to plain inequality -- the
    pre-PW4 behaviour -- rather than to `True`. `True` would have been fail-open in the worst
    way: if _atom_fingerprint's format ever changed, every atom's episode would close on every
    draw and the stall tracker would silently stop tracking, with nothing red to say so."""
    if not old:
        return True
    o, n = old.split("|"), new.split("|")
    if len(o) != 5 or len(n) != 5:
        return old != new
    if o[_FP_LEVEL_CURRENT] != n[_FP_LEVEL_CURRENT]:
        return True
    if o[_FP_LOOP_STAGE] != n[_FP_LOOP_STAGE]:
        return True
    try:
        return int(n[_FP_SIMPLIFICATIONS]) > int(o[_FP_SIMPLIFICATIONS])
    except (TypeError, ValueError):
        return False         # unparseable counts cannot evidence progress -- the episode stands


def _load_atom_stall_state() -> dict:
    if not ATOM_STALL_STATE_FILE.exists():
        return {}
    try:
        return json.loads(ATOM_STALL_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_atom_stall_state(state: dict) -> None:
    ATOM_STALL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ATOM_STALL_STATE_FILE.write_text(json.dumps(state, sort_keys=True))


def _is_atom_stalled(atom_id: str, state: dict | None = None) -> bool:
    """Read-only check used by candidate filters (never mutates the
    tracker) -- kept separate from _record_atom_draw_and_check_stall()
    below, which only the function that actually SELECTS the primary pick
    should call (merely checking candidacy must not itself count as a
    draw)."""
    state = state if state is not None else _load_atom_stall_state()
    return bool(state.get(atom_id, {}).get("stalled"))


def _record_atom_draw_and_check_stall(atom_id: str, fingerprint: str) -> tuple[bool, int]:
    """Update the per-atom stall tracker with this cycle's draw, returning
    (is_now_stalled, consecutive_unchanged_count). Ratchets a per-atom
    counter: same atom_id drawn again with the SAME fingerprint as last
    recorded -> increment; anything else (a different atom drawn, or this
    atom genuinely changed) -> reset to 1. Reaching ATOM_STALL_THRESHOLD
    flags stalled=True -- read by _is_atom_stalled() to soft-deprioritise
    (never permanently exclude -- a later fingerprint change resets the
    count and clears the flag naturally, since a fresh count of 1 is well
    under threshold) an atom the draw keeps reselecting for no new reason."""
    state = _load_atom_stall_state()
    entry = state.get(atom_id, {})
    # PW4: the episode closes on PROGRESS, not on any fingerprint difference (see
    # _atom_fingerprint_progressed).
    episode_closed = _atom_fingerprint_progressed(entry.get("fingerprint"), fingerprint)
    count = 1 if episode_closed else entry.get("consecutive_unchanged", 0) + 1
    proposed = {
        "fingerprint": fingerprint,
        "consecutive_unchanged": count,
        "last_drawn_at": time.time(),
    }
    proposed = guard_episode(entry, proposed, streak_fields=ATOM_STALL_STREAK_FIELDS,
                             episode_closed=episode_closed)
    # `stalled` is DERIVED from the guarded count, never carried through the guard -- a boolean
    # is not an episode and a stale True must not survive an evidenced close.
    count = proposed["consecutive_unchanged"]
    stalled = count >= ATOM_STALL_THRESHOLD
    proposed["stalled"] = stalled
    state[atom_id] = proposed
    _save_atom_stall_state(state)
    return stalled, count


def _load_idle_turn_count() -> int:
    if not IDLE_TURN_COUNTER_FILE.exists():
        return 0
    try:
        return json.loads(IDLE_TURN_COUNTER_FILE.read_text()).get("count", 0)
    except (json.JSONDecodeError, OSError):
        return 0


def _record_idle_turn() -> int:
    """R3_WORK_GRANTING_REDESIGN.md requirement 1: instrument the impossible
    state, don't just prevent it silently. Returns the new total (all-time,
    persisted) count of cycles where find_work() found genuinely nothing --
    target is zero; every increment is itself visible in the log, not just
    inferred from its absence."""
    count = _load_idle_turn_count() + 1
    IDLE_TURN_COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    IDLE_TURN_COUNTER_FILE.write_text(json.dumps({"count": count}, sort_keys=True))
    return count


def _load_map_exhausted_state() -> dict:
    if not MAP_EXHAUSTED_STATE_FILE.exists():
        return {}
    try:
        return json.loads(MAP_EXHAUSTED_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_map_exhausted_state(state: dict) -> None:
    MAP_EXHAUSTED_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MAP_EXHAUSTED_STATE_FILE.write_text(json.dumps(state, sort_keys=True))


def check_map_exhausted_escalation(map_exhausted: bool) -> None:
    """R3_WORK_GRANTING_REDESIGN.md requirement 4: escalate on CANNOT-draw,
    never on didn't-draw. `map_exhausted` is True only when find_work()'s
    self-refill draw genuinely found no candidate at all -- every atom
    blocked/complete, or the map is unreadable. That is itself a real
    finding (either the whole map is done, which would be remarkable, or
    something is wrong with the map/its dependency graph) -- fire ONE NTFY
    on the TRANSITION into this state (R5: never repeat an unchanged
    status), not every cycle it persists, and clear cleanly the moment real
    work resumes so a later genuine recurrence escalates again."""
    state = _load_map_exhausted_state()
    was_exhausted = state.get("exhausted", False)
    if map_exhausted and not was_exhausted:
        # ADVISOR_ANSWER_CANNOT_DRAW.md (P0, 2026-07-12): the escalation
        # itself was correct and valuable last time, but "no candidate" made
        # the advisor re-derive the blocked-set and its roots by hand from
        # the raw YAML. Upgraded to self-diagnose: report the blocked-set
        # and its blocking roots directly in the NTFY.
        diagnosis = diagnose_map_blocked_set()
        ntfy(
            "Supervisor: the maturity-map self-refill draw found NO candidate "
            "atom at all with no agenda/urgent/staged instruction either -- "
            "this is a genuine CANNOT-draw, not a routine idle tick. "
            f"Diagnosis: {diagnosis}"
        )
        log("MAP-EXHAUSTED escalation sent -- self-refill found no candidate at all")
        _save_map_exhausted_state({"exhausted": True})
    elif not map_exhausted and was_exhausted:
        log("Map-exhausted state cleared -- real work available again")
        _save_map_exhausted_state({"exhausted": False})


# Auto-clear (ADVISOR_STEER_OVERNIGHT.md item 2, 2026-07-11 -- authorized
# in-console 2026-07-11 morning via mid-turn window message, genuineness
# confirmed by Rich over NTFY the same day: "CONFIRMED: all recent mid-turn
# window messages were genuinely me -- the sequencing/auto-clear one...
# Act on all of them." docs/staging/done/from_rich_20260711_105502.md).
# The feature was authorized but never built -- a real session sat at 649k
# [tokens] begging for a manual /clear the same night this was staged.
#
# Approximation, stated plainly rather than hidden: there is no token-count
# API available to an external daemon, so this uses the current session's
# own transcript FILE SIZE (bytes) as a proxy, calibrated empirically
# against this actual project's transcripts (JSONL structural overhead --
# tool_use/tool_result blocks, timestamps, escaping -- inflates bytes/token
# well above plain text's ~4:1 ratio; this session's own transcript ran
# ~25 bytes/token at a self-reported ~649k-token mark). Recalibrate this
# constant if it drifts badly from reality; it is a proxy, not a promise.
AUTO_CLEAR_BYTES_THRESHOLD = 10_000_000  # ~400k tokens at the ~25 bytes/token calibration above
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects" / "-home-rich-synthetic-enterprise"
AUTO_CLEAR_LOG_FILE = PROJECT_DIR / "docs" / "observability" / "supervisor-auto-clear-log.md"


def _latest_transcript_size_bytes() -> int | None:
    """Size in bytes of the most-recently-modified session transcript in
    this project's Claude Code projects directory -- a proxy for "the
    currently active session's context size" (there is no direct API to ask
    an external daemon process for another process's live token count).
    Returns None if the directory or any transcript is missing (fails
    closed -- no transcript found means no auto-clear decision can be made,
    not "assume huge and clear")."""
    if not CLAUDE_PROJECTS_DIR.is_dir():
        return None
    transcripts = list(CLAUDE_PROJECTS_DIR.glob("*.jsonl"))
    if not transcripts:
        return None
    latest = max(transcripts, key=lambda p: p.stat().st_mtime)
    try:
        return latest.stat().st_size
    except OSError:
        return None


def _git_tree_clean() -> bool:
    """True if the working tree has no uncommitted changes -- part of the
    "clean boundary" test (work pushed, nothing in flight). Fails closed
    (False, i.e. NOT clean / do not clear) on any error, since a spurious
    clear mid-uncommitted-work is the harmful failure mode, not a missed
    clear opportunity."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return False
        return result.stdout.strip() == ""
    except Exception:
        return False


def should_auto_clear() -> bool:
    """Both halves of the authorized condition: context > ~400k (transcript-
    size proxy) AND a clean boundary (session idle -- reusing the exact same
    is_session_idle() gate turn-granting itself trusts -- and the working
    tree has no uncommitted changes, i.e. nothing in flight). Fails closed
    (False) if the transcript size can't be determined at all, rather than
    guessing."""
    size = _latest_transcript_size_bytes()
    if size is None or size < AUTO_CLEAR_BYTES_THRESHOLD:
        return False
    if not is_session_idle(SESSION_NAME):
        return False
    return _git_tree_clean()


def grant_turn(reason: str) -> bool:
    """PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the
    supervisor NO LONGER types a turn-grant into the live 'claude' pane.
    Keystroke injection is deleted (banned; five deaths). The pull-loop Stop
    hook (.claude/hooks/pull_next_work.py) is the transport now -- it calls the
    SAME find_work() draw at every turn boundary and feeds the result back as
    the next input, never touching the pane.

    The supervisor is retained as an INDEPENDENT ESCALATION watchdog over that
    transport: it still polls, still draws (for the escalation signal), still
    alarms on stuck/exhausted states -- it just no longer delivers work itself.
    grant_turn is kept only so run_cycle's structure and the escalation tests
    stay intact; it performs ZERO pane writes. Returns True (the draw is
    logged; the pull-loop delivers it)."""
    log(f"Work identified for the pull-loop to deliver at the next turn boundary -- {reason}")
    return True


# Mutable across main() loop iterations.
_was_paused = False


def run_cycle() -> None:
    global _was_paused

    paused_now = _pause_active_readonly()
    if paused_now:
        log("Usage pause active -- skipping (no grant)")
        _was_paused = True
        return
    resumed_from_pause = _was_paused
    _was_paused = False

    # §4 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27): surface any staged [DIRECTOR-
    # RULING]/[STEER] that lacks a 'WORK THIS CREATES' block, so a machine-detectable defect never
    # silently drops. THIS LOG LINE IS THE SURFACE (2026-08-03): it does NOT page the director -- a
    # missing block is a defect in the DOC, not one of the four reserved classes, so the tick absorbs it
    # by drawing the doc and minting from the body. Runs BEFORE the session-busy short-circuit so it is
    # recorded even while the session is working. Best-effort: a failure never breaks the cycle.
    try:
        defects = surface_missing_work_block_defects()
        if defects:
            log(f"§4 missing 'WORK THIS CREATES' block surfaced for: {', '.join(defects)}")
    except Exception as e:  # noqa: BLE001
        log(f"§4 missing-block surface failed (non-fatal): {e}")

    # PULL-LOOP MIGRATION (2026-07-15): the supervisor no longer types into the
    # pane, so it no longer needs to clear copy-mode or auto-inject /clear
    # before a send (those existed only to make an injection land cleanly).
    # It still reads idle state read-only, purely so its escalation log line
    # reflects whether the session is actively working.
    if not is_session_idle(SESSION_NAME):
        log("Session busy -- skipping this cycle")
        return

    reason, map_exhausted = find_work(resumed_from_pause)
    check_map_exhausted_escalation(map_exhausted)
    if reason is None:
        if map_exhausted:
            total = _record_idle_turn()
            log(f"Idle, no work -- map genuinely exhausted (all-time idle-turn count: {total})")
        else:
            # DRAINED-AND-GATED quiet wait (ADVISOR_STEER 2026-07-18, item 1): a LEGITIMATE
            # resting state -- below-target work exhausted, the remainder blocked on a director
            # act, so the only draw would be at-target HARDEN re-verification. NOT an idle defect
            # (do NOT increment the anti-idleness idle-turn counter, whose target is zero) and NOT
            # exhausted (no map-exhausted escalation). A genuinely new signal wakes it next turn.
            log("Drained-and-gated quiet wait -- resting (blocked on a director act); not "
                "exhausted, not an idle defect. A genuinely new signal wakes it immediately.")
            # R17 fail-open fix (director console 2026-07-22): if we are resting because the
            # forward-discovery register is fully DISCOVER-complete, surface each complete
            # track's graduation proposal to the director ONCE (batched [ACT], transition-keyed
            # so it never re-pages unchanged) -- then rest. Do NOT self-open any track. Non-fatal.
            try:
                emitted = maybe_emit_graduation_proposal()
                if emitted:
                    log("Forward-discovery graduation [ACT] emitted (batched, once per complete-set).")
            except Exception as e:  # noqa: BLE001
                log(f"Graduation proposal emit failed (non-fatal, rest continues): {e}")
        return

    _check_stuck_escalation(reason)

    # No pane write (pull-loop is the transport now). grant_turn only logs the
    # draw + runs the escalation bookkeeping; the pull-loop delivers the work.
    grant_turn(reason)


def main() -> None:
    log("Supervisor started -- escalation watchdog over the pull-loop transport")
    update_agent_status(
        "supervisor", status="idle",
        last_action="Supervisor started",
        role="Escalation watchdog over the pull-loop transport: polls every 2min, draws work for the stuck/exhausted escalation signal, alarms if the map stops making progress (turn delivery is the pull-loop Stop hook's job -- no pane injection)",
        produces="stuck-state / map-exhausted NTFY escalation",
    )
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Supervisor cycle error: {e}")
        try:
            stuck_state = _load_stuck_state()
            elapsed_min = int((time.time() - stuck_state.get("first_seen_at", time.time())) // 60)
            update_agent_status(
                "supervisor", status="idle",
                last_action=f"Cycle complete -- current stuck-key unchanged for ~{elapsed_min}min",
                is_heartbeat=True,  # liveness ping, not a real action (R10 status-semantics sweep, 2026-07-24)
            )
        except Exception:
            pass
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/supervisor.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("supervisor")
    main()
