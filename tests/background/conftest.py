"""Directory-scoped test isolation for the supervisor draw/rest ladder.

CLASS FIX (R10), 2026-07-24, WEDGE3_AND_RUNG1_MECHANISE: the RUNG-1 publish-gate-wedge
detector (`supervisor._publish_gate_wedge_active`, wired as the TOP rung of both
`_self_refill_draw` and `_is_drained_and_gated`) reads the REAL on-disk
`.publish_gate_state.json` + `.last_tested_hash`. Any test in this directory that exercises
the draw/rest ladder WITHOUT isolating those two files silently leaks the live gate state: when
the real gate is wedged AND HEAD != last_tested_hash, the rung fires and every "map empty -> rest"
/ "draws forward-discovery" assertion flips (12 such tests red-ed the publish gate the moment the
rung landed -- the fork's own full-suite run false-greened only because HEAD == last_tested_hash
at that instant kept the detector transiently silent).

This is the exact "new always-drawable rung needs fixture isolation" class the F-lane draw hit
before (see test_supervisor.py::_isolate). Rather than re-patch each file on touch, this autouse
fixture neutralises the leak for the WHOLE directory: it points both state files at a clean,
absent tmp path (an absent/empty state => detector returns None => no phantom wedge). The one
test that genuinely needs a wedged state (test_publish_gate_wedge_draw.py) writes it in the test
BODY via its own monkeypatch, which runs after this fixture's setup and therefore wins; the tests
that already isolate explicitly (test_supervisor.py::_isolate) merely point at a different clean
tmp -- also non-wedged, so correctness is unaffected either way.
"""
import os
import subprocess
from pathlib import Path

import pytest

from background import (
    gap_ledger_reconciler,
    notification_digest,
    process_run_complete,
    sim_runner,
    supervisor,
)
from tests.background import env_constant_sync as _env_sync

REPO_ROOT = Path(__file__).resolve().parents[2]
_GIT_DIR = REPO_ROOT / ".git"


@pytest.fixture(autouse=True)
def _publisher_log_never_reaches_the_live_record(tmp_path, monkeypatch):
    """Default every test in tests/background/ to a CAPTURED publisher log rather than the live
    `docs/observability/sim-runner-log.md`.

    THE CLASS, and it is the same one this file's other autouse fixture exists for. The
    two-clocks fix (14219094c) added a `log()` call to `_run_gate_in`, and
    `background.live_ledger_guard` correctly refuses a test process writing a live observability
    record -- a guard earned on 2026-08-17, when exactly that overwrote the coupled gap ledger
    with a 276-invoice fixture book and republished the public Proof door's belief-vs-truth gap
    2.68x too low.

    So the guard is right and the tests are right; what was missing is the isolation. SIX tests
    across TWO files began failing on the guard rather than on their own subject
    (test_publish_scope.py x2, test_publish_decoupling_exit.py x4) -- and every one of them is
    inside `publish_scope.resolve_scope()`'s BLOCKING set, so they were blocking publishing while
    reporting a refusal that had nothing to do with what they assert.

    Fixed for the directory rather than per file, per R10 and per this conftest's own stated
    principle: the first two were patched individually earlier the same day, and the third file
    proved that was an instance fix on a class.

    REDIRECT THE DESTINATION, DO NOT REPLACE THE FUNCTION -- and that distinction is the whole
    fixture. My first version monkeypatched `prc.log` itself and broke FIVE tests that legitimately
    exercise it (verified by removing the fixture and re-running: 5 of 7 failures went green). The
    neighbouring fixture below has always redirected PATHS, never functions; I copied its placement
    and not its technique.

    Pointing `LOG_FILE` at a tmp file leaves `log()` fully intact -- it still formats, still calls
    `guard_live_ledger_write`, which still permits a non-live destination -- so a test asserting on
    logging behaviour sees the real thing, and nothing reaches
    `docs/observability/sim-runner-log.md`. The guard stays exactly as strict as it was.
    """
    from background import process_run_complete as prc
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "sim-runner-log.md", raising=False)


#: The path constants this directory's tests are redirected away from. NAMED AND MEASURED, not
#: swept: a version of this fixture that re-rooted EVERY upper-case `Path` attribute of every
#: imported `background.*` module was tried on 2026-08-31 and broke **153 tests** — it moved
#: `live_ledger_guard.LIVE_RECORD_DIR` (disarming the ledger guard), collided with fixtures that
#: `mkdir()` their own directories, and reddened `test_tree_divergence`'s porcelain wiring. Each
#: entry below is here because a test was measured hitting it:
#:
#:   LOG_FILE — ~50 daemons; `autonomous-runner-log.md` was 23% pytest output
#:
#: `STATUS_FILE` (agent_status, which every daemon calls), `STATE_FILE` (reconcile_watch) and
#: `REGISTRY_PATH` (console_sanctity) are MEASURED as needed too, and are NOT here: they only
#: become necessary once `docs/observability` is a protected surface, and redirecting them alone
#: reddened 86 tests in `process_run_complete`. They land with that promotion, not before it.
_REDIRECTED_CONSTANTS = ("LOG_FILE",)


@pytest.fixture(autouse=True)
def _no_daemon_log_reaches_the_live_record(tmp_path, monkeypatch):
    """The same fix as the fixture above, for EVERY daemon's `LOG_FILE` rather than the one that hurt.

    That fixture's own docstring makes this argument and then stops one module short: *"Fixed for
    the directory rather than per file… the first two were patched individually earlier the same
    day, and the third file proved that was an instance fix on a class."* `process_run_complete`
    was the third file. There are fifty more modules in `background/` with a `LOG_FILE`, and on
    2026-08-31 three of their ledgers turned out to be carrying test output —
    `autonomous-runner-log.md` was **23% pytest**, and a reader of it (this seat, answering the
    director) reported a usage limit that had never existed.

    THE SUBJECT IS DERIVED, never enumerated: any already-imported `background.*` module whose
    `LOG_FILE` resolves inside `docs/observability/` is redirected. A daemon written tomorrow is
    covered on the day its first test imports it, which is the difference between this and the
    hand-listed tuple `tests/production_surface_guard.py` spent three incidents growing out of.

    SCOPED TO `LOG_FILE`, AND THE SCOPE WAS MEASURED RATHER THAN CHOSEN. A wider version of this
    fixture — re-rooting every upper-case `Path` attribute of every imported background module —
    was tried on 2026-08-31 and **broke 11 tests across two modules that had been green**
    (`test_publish_provenance_banner_adoption` errored on `mkdir` of a directory the re-rooting had
    already created; `test_tree_divergence`'s porcelain-wiring leg went red). The narrow version
    closes the 102 tests the `docs/observability` surface promotion actually reddened, measured;
    the wide one closes more and costs more, and "more isolation is better" is an argument rather
    than a measurement. If the wider scope is wanted, it needs those 11 repaired first.

    REDIRECTS THE DESTINATION, NEVER REPLACES `log()` — see the fixture above on why that
    distinction is the whole thing. Every `log()` still formats, still calls the ledger guard, and
    a test asserting on logging behaviour reads the redirected file through the same constant.
    """
    import sys

    live_dir = (REPO_ROOT / "docs" / "observability").resolve()
    for name, module in list(sys.modules.items()):
        if not name.startswith("background.") or module is None:
            continue
        for attr in _REDIRECTED_CONSTANTS:
            current = getattr(module, attr, None)
            if not isinstance(current, Path):
                continue
            try:
                current.resolve().relative_to(live_dir)
            except (ValueError, OSError):
                continue  # already pointed somewhere harmless
            monkeypatch.setattr(module, attr, tmp_path / current.name, raising=False)


@pytest.fixture(autouse=True)
def _isolate_publish_gate_wedge_state(tmp_path, monkeypatch):
    """Default every test in tests/background/ to a NON-wedged publish-gate state so the
    RUNG-1 wedge detector cannot leak the real gate state into unrelated draw/rest assertions.
    Tests that need a specific wedged state override these paths in their own body."""
    monkeypatch.setattr(
        supervisor, "PUBLISH_GATE_STATE_FILE", tmp_path / ".publish_gate_state.json", raising=False
    )
    monkeypatch.setattr(
        supervisor, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash", raising=False
    )
    # RUNG-7 PLANNER (director ruling WORK_IS_THE_DEFAULT 2026-07-23): the planner reads the real
    # DIRECTOR_AXES.md, which is populated -> planner fires -> rest is never legitimate. That would
    # flip every "map empty -> rest" assertion in this dir (same fixture-isolation class as the wedge
    # state above). Default the axes path to an ABSENT tmp file so the planner does NOT fire by
    # default; the R15 planner tests point it at a populated file explicitly.
    monkeypatch.setattr(
        supervisor, "DIRECTOR_AXES_PATH", tmp_path / "DIRECTOR_AXES_absent.md", raising=False
    )
    # EIGHTH CLASS (2026-07-27, DIRECTOR_RULING_EIGHTH_CLASS): the `blocked_mints` level (wired into
    # authorized_set_enumeration + _is_drained_and_gated) reads the REAL docs/staging/in_progress/
    # for parked PLANNER_MINTED_* mints -- the live tree routinely holds a blocked batch, which would
    # flip every "map empty -> rest" assertion in this dir (the exact fixture-isolation class this
    # conftest already fixes for the wedge state + axes). Default STAGING_DIR to a clean empty tmp so
    # no blocked mints leak in; the EIGHTH-CLASS tests write mints into their own tmp staging body.
    _staging = tmp_path / "staging_isolated"
    (_staging / "in_progress").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(supervisor, "STAGING_DIR", _staging, raising=False)
    # RUNG 1b OPERATIONAL-LAYER PERSISTENT-RED (director console 2026-07-25): the FOURTH instance of
    # the same class this fixture already fixes three times above -- `_operational_red_persistent_draw`
    # reads the REAL .operational_layer_signal.json and sits ABOVE every product/HARDEN lane, so
    # whenever the live operational suite is red it wins the draw and flips every "map empty -> rest" /
    # "draws lane X" assertion in this directory. It really was red on 2026-08-08 (consecutive_red 4),
    # and it red-ed the publish gate through two unrelated files
    # (test_forward_discovery_draw.py, test_governance_refusal.py) whose subjects have nothing to do
    # with it. Default to an ABSENT tmp path -- absent => detector returns None (proven by
    # test_operational_red_persistent_draw.py::test_silent_on_absent_file), so no phantom red. The
    # rung's own tests set this path in their body, which runs after this fixture and therefore wins.
    monkeypatch.setattr(
        supervisor, "OPERATIONAL_LAYER_SIGNAL_FILE",
        tmp_path / ".operational_layer_signal_absent.json", raising=False,
    )
    # RUNG 4b STALE-GAP-ROW (2026-08-10) -- the FIFTH instance of this same class, and the one that
    # wedged publishing for the ~13 minutes it took to find it. `_stale_gap_row_draw` holds no path
    # of its own: it imports `background.gap_ledger_reconciler` and reconciles the REAL
    # docs/observability/coupled_gap_ledger.json against the REAL git history. At HEAD that ledger
    # had 13 refreshable rows, so the rung fired and refused rest -- reddening ELEVEN tests across
    # this directory whose subjects (forward-discovery, propose-half) have nothing to do with gap
    # measurements. The tree passed the identical tests only because the working copy of the ledger
    # happened to be freshly re-rendered; the gate judges a clean HEAD checkout, so the wedge was
    # invisible locally. Pin the reconciler's LEDGER_PATH at an ABSENT tmp file: absent => an empty
    # ledger => no row is refreshable => the rung is silent (asserted, not assumed, by
    # test_rest_ladder_isolation.py::test_the_gap_rung_is_silent_under_this_fixture). The rung's own
    # tests inject `work=` directly, so this pin cannot weaken them.
    monkeypatch.setattr(
        gap_ledger_reconciler, "LEDGER_PATH",
        tmp_path / "coupled_gap_ledger_absent.json", raising=False,
    )
    # OPS13 PRODUCT INTERLEAVE (2026-08-13) -- the SIXTH instance, caught the day it landed and
    # isolated in the same breath. `_apply_product_interleave` runs on every three-lane grant and
    # PERSISTS the unpaid-harness ledger, so any test in this directory that exercises the draw
    # writes its synthetic atom ids into the LIVE docs/observability/.product_interleave_state.json
    # -- observed: `{"owed": ["H1_test_atom", "H1_test_atom"]}` from
    # test_supervisor_blocker_precedence.py. The leak runs the other way too (a real owed id makes
    # the next test's arm force a product-side draw it did not ask for). An absent tmp path is a
    # clean slate, which is the state every test in here that is not about the interleave wants.
    monkeypatch.setattr(
        supervisor, "PRODUCT_INTERLEAVE_STATE_FILE",
        tmp_path / ".product_interleave_state_absent.json", raising=False,
    )
    # ANTI-LIVELOCK STALL TRACKER (2026-08-13) -- the SEVENTH instance, and the only one in this
    # fixture that is a FLAKE rather than a constant red, which is why it survived five rounds of
    # this same fix. `_self_refill_draw` records every primary pick into the REAL
    # docs/observability/.atom_stall_tracker.json, and ATOM_STALL_THRESHOLD is 2: two tests in one
    # process that happen to draw the SAME fixture atom with the same fingerprint flag it stalled,
    # and the next test needing that atom loses it from its own candidate set. Whether that happens
    # depends on the dial-weighted RNG, so the file passes alone and reds inside a long run -- the
    # "a control that must win a race has the weather as its subject" class. It red-ed
    # test_supervisor_blocker_precedence::test_an_unblocked_lane_atom_still_draws_the_same_cycle in
    # a 1,860-test gate run while passing standalone in the same tree. An absent tmp path means
    # nothing is stalled, which is what every test in here that is not ABOUT the backoff wants; the
    # ones that are (test_supervisor.py, test_pw4_episode_guards.py, test_draw_external_block.py,
    # test_frame_saturation_draw_marker.py, test_governance_refusal.py) already set this path in
    # their own body, which runs after this fixture and therefore still wins.
    monkeypatch.setattr(
        supervisor, "ATOM_STALL_STATE_FILE",
        tmp_path / ".atom_stall_tracker_absent.json", raising=False,
    )
    # G-N4 NOTIFICATION DIGEST (2026-08-14) -- the EIGHTH instance, and the one that held the
    # operational-layer signal RED for 9 consecutive hourly checks while the suite was GREEN by
    # hand. `deadmans_switch.run_cycle` calls `_flush_notification_digest()`, which reads the REAL
    # append-only docs/observability/ntfy_digest_queue.jsonl and SENDS through the same
    # ntfy_utils.send_ntfy that ~27 tests in test_deadmans_switch.py monkeypatch to capture -- so a
    # due digest lands in every one of those `assert calls == []` lists. That file's own `_isolate`
    # fixture neutralises six other run_cycle checks by name and never grew a seventh entry when
    # the digest landed, which is precisely why this pin belongs at DIRECTORY scope instead: the
    # next check to gain a real-state read is isolated here without anyone remembering to edit a
    # per-file list.
    #
    # It is a FLAKE of the nastiest shape (the "weather as its subject" class, like the stall
    # tracker above): DIGEST_INTERVAL_SECONDS is 6h and the high-water mark advances ONLY on a
    # CONFIRMED delivery (G-N5), so the queue is due for a few minutes a day -- and stays due
    # indefinitely if the send is dropped or rate-limited. The suite therefore passes standalone,
    # passes by hand, and reds inside the daemon's own hourly run, which spawns the pytest from
    # INSIDE run_cycle at a point where its own flush has not happened yet. Pinning BOTH paths at
    # absent tmp files gives an empty queue => `pending()` is empty => `flush()` returns None
    # without sending, whatever the clock says. test_notification_digest.py's `store` fixture sets
    # both paths in its own body, which runs after this one and therefore still wins, so the
    # digest's own R15 tests are untouched.
    monkeypatch.setattr(
        notification_digest, "QUEUE_FILE",
        tmp_path / "ntfy_digest_queue_absent.jsonl", raising=False,
    )
    monkeypatch.setattr(
        notification_digest, "STATE_FILE",
        tmp_path / ".ntfy_digest_state_absent.json", raising=False,
    )
    # RUNG 1d PRODUCER STARVATION, the READ side (2026-08-17). Caught by this directory's own class
    # control -- `test_rest_ladder_isolation.py::test_every_refusal_rung_is_silent_under_the_rest_
    # proof_setup` -- which names the required fix in its own failure message: pin the rung's live
    # INPUT here, never stub the rung in one test file. `_producer_starved_active` reads THREE live
    # paths, and the rung sits at PRIORITY ZERO, so whenever the real producer is unhealthy it wins
    # the draw and flips every "authorized set empty -> rest" assertion in this directory.
    #
    # It passed standalone and red-ed only inside the 18-minute full-directory run, which is the
    # transient-green this conftest's own docstring warns about: the rung was silent at the instant
    # the small run sampled it because the producer happened to be healthy just then. The live
    # producer's health is the weather, and a control whose subject is the weather is not a control.
    #
    # The reports dir is pinned at an EMPTY tmp directory rather than an absent one on purpose: an
    # absent/unreadable dir and an empty one both yield "no artefact age", which is silence, but an
    # empty REAL directory is the honest analogue of "this checkout has produced nothing", and the
    # rung's own tests build their artefacts in their own tmp dir anyway.
    monkeypatch.setattr(
        supervisor, "SIM_PRODUCER_STATE_FILE",
        tmp_path / ".sim_producer_state_absent.json", raising=False,
    )
    _empty_reports = tmp_path / "reports_isolated"
    _empty_reports.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(supervisor, "SIM_RUN_OUTPUT_DIR", _empty_reports, raising=False)
    monkeypatch.setattr(
        supervisor, "SIM_RUNNER_HOLD_FLAG",
        tmp_path / ".sim_runner_hold_absent", raising=False,
    )
    # THE BLOCKING-TEST RECORD (2026-08-26) -- the TENTH instance, and the one that held the
    # operational-layer signal RED for five consecutive hourly checks. `record_publish_gate_
    # failure` re-derives the wedge suspects on EVERY failure (H42, "evidence before suspicion"),
    # and that derivation reads the REAL docs/observability/.last_gate_blocking_tests.json:
    # last_blocking_tests -> blocking_test_files -> first_party_imports -> blame_commits, which
    # SHELLS `git log` once per suspect set. Two tests in test_background_worker.py
    # (test_processing_order_is_deterministic_sorted, test_no_published_run_yet_retires_nothing)
    # drive the rc=1 failure path with `subprocess.run` patched to COUNT calls -- and
    # `background_worker.subprocess` is the stdlib module object, so that patch is global and the
    # blame `git log` lands in the same list as the publisher invocations. Observed 2026-08-26
    # 07:07Z: `assert 6 == 3`, the three extra entries all `site/test_harness_delivery_record.py`,
    # the file the live record happened to name at that moment.
    #
    # THE WEATHER AS ITS SUBJECT, exactly like the stall tracker and the digest above: the record
    # is written by the last hook-chain refusal and expires after GATE_BLOCKING_TESTS_MAX_AGE_
    # SECONDS, so those two tests are green on a checkout whose last gate was clean, red for a few
    # hours after any refusal, and green again once it staled -- with nothing about their own
    # subject having changed. That is the whole of the RUNG-1b persistent red being drawn here.
    #
    # An ABSENT tmp path reads as ([], None) -- "this alarm does not know" -- which yields {} from
    # wedge_suspects, so no blame, no git, and no live docs/staging/ scan from linked_findings
    # either (an empty trail returns before it globs). The tests that are ABOUT the record write it
    # in their own body or pass `path=`, both of which win over this fixture.
    monkeypatch.setattr(
        process_run_complete, "GATE_BLOCKING_TESTS_FILE",
        tmp_path / ".last_gate_blocking_tests_absent.json", raising=False,
    )
    # RUNG 1d PRODUCER STARVATION (2026-08-17) -- the NINTH instance, and the first that leaks the
    # other way: a test WRITING live state that a priority-zero rung READS. `sim_runner.
    # record_run_outcome` defaults to the real `.sim_producer_state.json`, and the existing
    # `run_simulation()` tests drive its timeout/failure paths -- so a plain suite run stamped
    # `{"consecutive_failures": 6, "detail": "timeout after 0s: stuck at 2019-03-31 SP47",
    # "git": "abc1234"}` onto the machine's real producer-health file. Observed, not theorised,
    # within minutes of the rung landing. Left alone it is worse than the eight leaks above: those
    # flip assertions inside this directory, this one makes the LIVE draw ladder hand priority-zero
    # to "the producer is down" on a healthy machine, from a test.
    #
    # DONE AS A SWEEP, NOT A NINTH NAMED PATH. Every entry above is one module constant someone
    # remembered; the failure mode is the one nobody remembers, and `test_sim_runner.py` shows it
    # directly -- it isolates PROJECT_DIR, LOG_FILE, STAGING_DIR and REPORTS_DIR by hand, four
    # entries maintained per-file, and PRODUCER_STATE_FILE simply was not on that list because it
    # did not exist when the list was written. So this redirects EVERY `Path` constant on the
    # module that points into the real checkout, and a tenth one is covered on the day it lands.
    for _name in dir(sim_runner):
        if _name.startswith("__"):
            continue
        _value = getattr(sim_runner, _name, None)
        if not isinstance(_value, Path):
            continue
        try:
            _relative = _value.relative_to(REPO_ROOT)
        except ValueError:
            continue           # already outside the checkout: nothing to protect
        _redirected = tmp_path / "sim_runner_real_tree" / _relative
        _redirected.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(sim_runner, _name, _redirected, raising=False)


# ── THE GHOST-PUSHER TRIPWIRE (issue #11) ────────────────────────────────────────────────────
# WHAT THIS CATCHES. background/ is the half of this repo that holds push credentials, and its
# publish path commits and pushes as an ordinary side-effect of an ordinary function call. A test
# in this directory that forgets to point PROJECT_DIR at a tmp tree therefore does not merely
# "leak state" the way the fixtures above do -- it manufactures a REAL commit on the REAL
# checkout and fires a REAL `git push origin HEAD:main`. That is the proven cause of every
# unexplained main push of the week: test_process_run_complete.py reached
# `_refresh_published_liveness_on_skip` on the real tree and made a `chore(liveness)... (git=abc)`
# commit, which failed to land only for want of credentials on the machine that ran it.
#
# WHY A TRIPWIRE AND NOT JUST THE FIX. The instance fix (isolate that file's tests) and the class
# fix (the seat guard on the side-effect itself) are both in this change, but neither of them
# stops the NEXT test in this directory from calling the next credential-holding function on the
# real tree. R10: an absurdity-class defect is not closed by an instance fix. This asserts the
# invariant directly -- NO test in tests/background/ may move the real repo's HEAD -- so the whole
# class fails automatically and loudly, naming the test and the commit it manufactured.
#
# TWO SCOPES, ON PURPOSE. The per-test check is the diagnostic one: it fails the exact test that
# committed, which is the thing a person needs to know. The session-scoped one is the outer
# bound -- it catches a commit made anywhere the per-test window does not cover (session-scoped
# fixture setup/teardown, collection, a detached child that lands its commit after the last test).
#
# COST. The per-test check reads .git/HEAD and one ref file: no subprocess, microseconds, so it is
# affordable on every test in the directory. `git log` runs only on the failure path.


def _real_repo_head() -> str:
    """The real checkout's current HEAD sha, read from .git directly (no subprocess).

    Returns a sentinel string rather than raising on anything unexpected: this is a
    tripwire, and a tripwire that explodes on an odd checkout would fail honest tests.
    A sentinel still compares equal to itself, so the before/after check stays valid --
    it simply cannot detect a move it could not read.
    """
    try:
        if not _GIT_DIR.exists():
            # NO REPOSITORY AT ALL -- the publish gate's clean HEAD checkout
            # (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09) is a `git archive` extraction
            # with no .git, and there is no real checkout there for a test to ghost-push into.
            # Return a constant WITHOUT shelling out: the subprocess fallback below collided
            # with every test that stubs `subprocess.run`, whose stub answered this call with a
            # Mock/None and turned the tripwire into `AttributeError: 'NoneType' has no
            # attribute 'stdout'` -- 9 errors that exist only in the archive, never in the repo.
            # A constant also satisfies the tripwire honestly: before == after, nothing moved,
            # because nothing here could move.
            return "no-git-dir"
        git_dir = _GIT_DIR
        if not _GIT_DIR.is_dir():
            # A LINKED WORKTREE, READ FROM DISK AND NOT THROUGH `git` (2026-08-31).
            #
            # This used to shell out to `git rev-parse HEAD`, and the comment eight lines above
            # already explains why that is fatal here: **a test that stubs `subprocess.run` answers
            # this call**, the read comes back empty, HEAD appears to move from a real sha to
            # "unreadable", and the tripwire fails closed with GHOST PUSHER (unattributable). The
            # no-`.git` case was fixed exactly this way and the worktree case was left shelling out.
            #
            # MEASURED: **31 errors** across nine modules on an unmodified `origin/main` checkout,
            # for no reason but the environment. In the main repo `.git` is a DIRECTORY, the reader
            # never shells out, and the same tests are green — so the suite was worktree-hostile and
            # nobody could see it while everyone worked in the main tree.
            #
            # IT MATTERS NOW BECAUSE THE FIRST UNATTENDED WRITER LIVES IN A WORKTREE. `seat_executor`
            # gates its landings there; 31 ghost failures would either send it chasing nothing or,
            # far worse, teach it that reds in its own tree are normal.
            #
            # `.git` is `gitdir: <path>` and THAT directory holds this worktree's own HEAD. Refs
            # resolve against the COMMON dir two levels up (`.git/worktrees/<name>/../..`), the same
            # distinction `tools/surgical_land._object_store` turns on: a worktree's gitdir has its
            # own HEAD and index and none of the shared refs.
            pointer = _GIT_DIR.read_text().strip()
            if not pointer.startswith("gitdir:"):
                return "unreadable"
            git_dir = Path(pointer.split(":", 1)[1].strip())
            if not git_dir.is_absolute():
                git_dir = (REPO_ROOT / git_dir).resolve()
            head = (git_dir / "HEAD").read_text().strip()
            if not head.startswith("ref: "):
                return head  # detached HEAD -- what the executor's worktree always is
            ref = head[5:].strip()
            common = git_dir.parent.parent  # .git/worktrees/<name> -> .git
            loose = common / ref
            if loose.is_file():
                return loose.read_text().strip()
            packed = common / "packed-refs"
            if packed.is_file():
                for line in packed.read_text().splitlines():
                    if line.endswith(" " + ref):
                        return line.split()[0]
            return "unborn:" + ref
        head = (_GIT_DIR / "HEAD").read_text().strip()
        if not head.startswith("ref: "):
            return head  # detached HEAD: the sha is right there
        ref = head[5:].strip()
        loose = _GIT_DIR / ref
        if loose.is_file():
            return loose.read_text().strip()
        packed = _GIT_DIR / "packed-refs"
        if packed.is_file():
            for line in packed.read_text().splitlines():
                if line.endswith(" " + ref):  # "<sha> <ref>"
                    return line.split()[0]
        return "unborn:" + ref
    except (OSError, subprocess.SubprocessError):
        return "unreadable"


# ── TRIPWIRE vs COLLEAGUE (EPISODE4 item 1, 2026-08-09) ──────────────────────────────────────
# The guard above compared HEAD before/after and blamed "this test session" for ANY move. On a box
# where an autonomous worker commits several times an hour and the suite takes ~11 minutes, that
# is not a tripwire, it is a collision detector: a real D14 build commit landing mid-run failed a
# 22,525-green suite, the publish gate booked it as `test_regression`, and publishing could only
# succeed in the lulls between colleagues' commits. MEASURED cause, twice.
#
# THE DISCRIMINATOR. Git records no PID, so attribution has to be arranged in advance: this
# process stamps a sentinel COMMITTER identity into its own environment at conftest import, before
# any test spawns anything. Every `git commit` reached from inside this pytest process -- however
# many subprocess layers down -- inherits it. A colleague's commit, made from a different process
# tree, cannot carry it. So `before..after` partitions cleanly into "mine" and "theirs", and only
# "mine" is a ghost push.
#
# WHY COMMITTER AND NOT AUTHOR. Author survives rebases, cherry-picks and `--author` overrides;
# committer records who actually performed the commit, which is exactly the question.
#
# FAIL-CLOSED ON UNATTRIBUTABLE (R15). If HEAD moved and the log cannot be read, the check cannot
# answer -- and an unavailable check is a FAILED check. That is rare (a git hiccup), unlike a
# concurrent commit, which is routine; so the split keeps the guard's teeth without paying the
# false-positive tax it was actually costing.
GHOST_SENTINEL_EMAIL = "pytest-ghost-tripwire@invalid"
os.environ.setdefault("GIT_COMMITTER_EMAIL", GHOST_SENTINEL_EMAIL)

_ROW_SEP = "\x1f"


def partition_commits(rows: list[tuple[str, str, str]]) -> tuple[list[str], list[str]]:
    """PURE (mutation-testable). rows = [(sha, committer_email, subject)].

    -> (mine, theirs): commits this pytest process committed, and commits it did not.
    Only `mine` is a ghost push; `theirs` is a colleague working normally and must be ignored."""
    mine = [f"{sha} {subj}" for sha, email, subj in rows if email == GHOST_SENTINEL_EMAIL]
    theirs = [f"{sha} {subj}" for sha, email, subj in rows if email != GHOST_SENTINEL_EMAIL]
    return mine, theirs


def _commit_rows(before: str, after: str) -> list[tuple[str, str, str]] | None:
    """(sha, committer_email, subject) for before..after; None if unreadable (-> fail-closed)."""
    try:
        out = subprocess.run(
            ["git", "log", f"--format=%h{_ROW_SEP}%ce{_ROW_SEP}%s", f"{before}..{after}"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=15,
        )
        if out.returncode != 0:
            return None
    except (OSError, subprocess.SubprocessError):
        return None
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split(_ROW_SEP, 2)
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def ghost_verdict(before: str, after: str, rows: list[tuple[str, str, str]] | None,
                  where: str) -> str | None:
    """PURE (mutation-testable): the failure message, or None if this is not a ghost push.

    Kept pure and separate from `_assert_head_unmoved` deliberately -- the autouse per-test
    fixture below calls that function at teardown, so a test that monkeypatched its internals
    would trip the very tripwire it is testing. The decision has to be reachable without
    patching module globals."""
    if after == before:
        return None
    if rows is None:
        return (
            "GHOST PUSHER (unattributable): {} -- HEAD moved {} -> {} and `git log` could not be "
            "read, so this check could not tell a test's commit from a colleague's. R15: an "
            "unavailable check is a FAILED check.".format(where, before[:9], after[:9])
        )
    mine, theirs = partition_commits(rows)
    if not mine:
        return None  # a colleague committed while we ran -- routine here, never our tripwire
    return (
        "GHOST PUSHER: {} moved the REAL repo's HEAD.\n"
        "  {} -> {}\n"
        "  commit(s) THIS TEST PROCESS manufactured (committer {}):\n    {}\n"
        "{}"
        "A test in tests/background/ must never commit to the real checkout. This one reached a "
        "credential-holding publish path on the real tree -- almost always a missing "
        "`monkeypatch.setattr(<module>, \"PROJECT_DIR\", tmp_path)`. Isolate it; do not silence "
        "this fixture.".format(
            where, before[:9], after[:9], GHOST_SENTINEL_EMAIL,
            "\n    ".join(mine),
            "  (also in range, NOT ours: {})\n".format("; ".join(theirs)) if theirs else "",
        )
    )


def _assert_head_unmoved(before: str, where: str) -> None:
    after = _real_repo_head()
    if after == before:
        return
    msg = ghost_verdict(before, after, _commit_rows(before, after), where)
    if msg:
        pytest.fail(msg)


@pytest.fixture(autouse=True, scope="session")
def _no_test_may_commit_to_the_real_repo():
    """Outer bound: the real repo's HEAD is where it was when this session started."""
    before = _real_repo_head()
    yield
    _assert_head_unmoved(before, "this test session")


@pytest.fixture(autouse=True)
def _this_test_may_not_commit_to_the_real_repo(request):
    """Per-test tripwire: fails the exact test that manufactured the commit."""
    before = _real_repo_head()
    yield
    _assert_head_unmoved(before, request.node.nodeid)


# ── THE STALE-ENV-CONSTANT TRIPWIRE (H31) ────────────────────────────────────────────────────
# WHAT THIS CATCHES. A test that leaves a module-level env-derived constant (e.g.
# `background.ntfy_utils.WAKE_HMAC_KEY`) out of sync with os.environ poisons every later test in
# the process: four test_ntfy_utils.py signing tests failed purely on collection order while the
# test that broke them stayed green. Full rationale, and the AST-derived registry that makes this
# a CLASS guard rather than a list that decays, live in tests/background/env_constant_sync.py.
#
# WHY A HOOK AND NOT A FIXTURE. The defect IS a teardown-ordering defect, so the check must run
# after ALL fixture finalizers -- crucially after `monkeypatch` restores os.environ, since the
# expected value is computed FROM os.environ. A fixture finalizer's position relative to the
# test's own monkeypatch depends on setup order; `pytest_runtest_teardown(trylast=True)` is
# unambiguously last, because the internal impl that runs fixture finalizers is an ordinary
# hookimpl that trylast sorts behind. Verified empirically, not assumed.
#
# BASELINE-RELATIVE. Divergences already present when the session starts are recorded once and
# never re-reported, so a pre-existing oddity in the checkout cannot fail an unrelated test. Only
# a divergence a test INTRODUCES is attributed to it.

_ENV_CONSTANT_REGISTRY = _env_sync.build_registry()
_ENV_CONSTANT_BASELINE_BAD: set[str] = {
    c.dotted for c, _a, _e in _env_sync.diverged(_ENV_CONSTANT_REGISTRY)
}


@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    """Fail the test that desynchronised a module env constant -- and repair it, so the
    cascade stops here rather than reddening whatever happens to be collected next."""
    offenders = [
        (c, actual, expected)
        for c, actual, expected in _env_sync.diverged(_ENV_CONSTANT_REGISTRY)
        if c.dotted not in _ENV_CONSTANT_BASELINE_BAD
    ]
    if not offenders:
        return
    for const, _actual, _expected in offenders:
        _env_sync.repair(const)  # later tests must not inherit this
    pytest.fail(
        "{}\n\n{}".format(
            item.nodeid,
            "\n\n".join(_env_sync.describe(c, a, e) for c, a, e in offenders),
        ),
        pytrace=False,
    )
