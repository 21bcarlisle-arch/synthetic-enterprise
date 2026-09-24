"""A frozen toolchain has to reach someone who can act, and "I cannot tell" is not "current".

THE DEFECT (2026-07-09 to 2026-09-25, 78 days). The CLI's auto-updater printed *"Auto-update
failed: no write permission to npm prefix"* under every report. The cause was diagnosed correctly
and is still written at `background/start_worker.sh:38-43` -- the SYSTEM npm's prefix is `/usr`,
root-owned, while `claude` runs from a user-owned NVM install. The response was
`DISABLE_AUTOUPDATER=1` on every launch path, on the stated reasoning that the mismatch *"is inside
the closed-source CLI binary, not something this repo can patch directly"*.

**The cause was right and the conclusion was wrong.** `npm install -g` run with NVM's OWN npm -- the
one whose prefix is user-owned -- updates the running install in 33 seconds with no sudo. Nothing in
the CLI needed patching.

AND THE SUPPRESSION WAS AIMED AT EVERY READER EXCEPT THE ONE WHO COULD ACT. `DISABLE_AUTOUPDATER=1`
was set in `autonomous_runner`, `start_worker.sh`, `seat_executor`, `worker_tick` and
`delivery_seat`, and in no shell rc -- so the daemons were silent and the DIRECTOR'S OWN CONSOLE was
the single surface still printing the failure, which is the one place it would be read as cosmetic.

WHAT IT COST: the install froze at 2.1.226 while the published version reached 2.1.282. 2.1.226
predates Claude Opus 5.5, so `/model opus-5-5` answered "not found" and a model at 20% lower token
cost with 60% cheaper cache reads could not be selected. A frozen toolchain removes capability
silently.

THESE LEGS ARE ABOUT THE THREE PROPERTIES THE OLD WARNING LACKED, not about today's versions:
keyed to the PROPERTY so they survive a version bump; UNKNOWN kept distinct from CURRENT so an
unreachable registry can never read as health; and the FIX carried, because its absence is what let
the remedy be rediscovered from scratch 78 days later.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import toolchain_freshness as tf


class _Proc:
    def __init__(self, stdout: str = "", returncode: int = 0):
        self.stdout = stdout
        self.returncode = returncode


def _run_returning(version: str, rc: int = 0):
    def _run(cmd, **kwargs):
        return _Proc(stdout=version + "\n", returncode=rc)
    return _run


def _fresh_state(tmp_path: Path, monkeypatch) -> Path:
    state = tmp_path / "toolchain_freshness.json"
    monkeypatch.setattr(tf, "STATE_PATH", state)
    return state


# ===========================================================================
# 1. UNKNOWN IS NOT CURRENT. The whole defect in one property.
# ===========================================================================

def test_an_unreachable_registry_is_reported_as_unknown_and_never_as_current(tmp_path, monkeypatch):
    """The failure mode that cost 78 days: a check that cannot answer must not answer "fine".

    Asserted on all three of the observable surfaces at once -- the snapshot, the prose and the
    exit code -- because they are what different callers read, and the old warning was ignorable
    precisely because one surface said less than another.
    """
    _fresh_state(tmp_path, monkeypatch)

    def _explode(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 1)

    snap = tf.snapshot(_run=_explode)
    assert snap["cannot_tell"], "an unreachable registry produced no cannot_tell reason"
    assert snap["behind"] is None, (
        "behind was decided without reading the registry -- a False here is the exact shape that "
        "lets an outage read as 'up to date'"
    )
    assert tf.is_stale(snap) is False, "unknown must not masquerade as stale either"
    assert "UNKNOWN" in tf.describe(snap), tf.describe(snap)
    assert tf.describe(snap) != tf.describe(
        {"installed": "1.0.0", "latest": "1.0.0", "behind": False, "cannot_tell": None}
    ), "the unknown message is indistinguishable from the current message"


def test_the_three_exit_codes_are_distinct_so_a_caller_can_tell_unknown_from_current(
        tmp_path, monkeypatch):
    """rc 0 current / rc 1 behind / rc 2 cannot tell.

    A two-code version is the bug, not a simplification: it forces the unreachable case to share an
    exit status with one of the two real answers, and whichever it shares it with becomes a lie.
    """
    _fresh_state(tmp_path, monkeypatch)
    monkeypatch.setattr(tf, "installed_version", lambda: "2.1.282")
    monkeypatch.setattr(tf, "fix_command", lambda: "npm install -g x")

    monkeypatch.setattr(tf, "latest_version", lambda **kw: "2.1.282")
    assert tf.main(["--check"]) == 0

    monkeypatch.setattr(tf, "latest_version", lambda **kw: "2.1.300")
    assert tf.main(["--check"]) == 1

    def _cannot(**kw):
        raise tf.CannotTell("registry unreachable")
    monkeypatch.setattr(tf, "latest_version", _cannot)
    assert tf.main(["--check"]) == 2


# ===========================================================================
# 2. THE FIX IS CARRIED, AND IT NAMES A PREFIX WE OWN.
# ===========================================================================

def test_the_fix_command_names_an_npm_whose_prefix_we_own_and_never_sudo():
    """The 78-day defect was calling an npm with a root-owned prefix. The remedy must not restate it.

    Asserted on the LIVE install rather than a fixture, because what must hold is a fact about this
    machine: the npm named here has to be the one whose prefix owns the running binary.
    """
    fix = tf.fix_command()
    assert "sudo" not in fix, (
        f"the fix uses sudo: {fix!r}. A root-owned file in a user prefix moves the failure to the "
        "next update rather than removing it."
    )
    assert "install -g @anthropic-ai/claude-code" in fix, fix
    assert "/usr/bin/npm" not in fix, (
        f"the fix names the SYSTEM npm: {fix!r}. Its prefix is /usr and root-owned -- calling it is "
        "the original defect, restated as the remedy."
    )

    # THE PREFIX GUARD, and it caught a real defect in the first draft of `fix_command` (2026-09-25).
    # npm is a shim that resolves `node` from PATH, so NVM's npm called by ABSOLUTE PATH from a
    # shell without NVM loaded runs under the SYSTEM node and reports prefix '/usr' -- reproducing
    # the exact permission failure this module describes. So the fix must carry a PATH= prefix, and
    # this leg asserts the prefix as the command WOULD ACTUALLY RUN IT.
    assert fix.startswith('PATH="') or fix.split()[0] == "npm", (
        f"the fix does not put the resolved node's bin on PATH: {fix!r}. Called bare, NVM's npm "
        "resolves the system node and reports a root-owned prefix -- the original defect."
    )
    prefix = tf.effective_prefix()
    if prefix is not None:
        assert not prefix.startswith("/usr"), (
            f"the fix would run with prefix {prefix!r}, which is root-owned. This is the 2026-07-09 "
            "defect reproduced by its own remedy."
        )
        assert Path(prefix).exists() and Path(prefix).stat().st_uid == Path.home().stat().st_uid, (
            f"prefix {prefix!r} is not owned by the user running this"
        )


def test_the_stale_message_carries_the_fix_and_says_a_restart_is_needed(tmp_path, monkeypatch):
    """A warning nobody can act on is what this replaces.

    The restart clause is load-bearing and not politeness: a running process holds the binary it
    started with, so 'updated' and 'in effect' are different states, and a message that implied the
    first meant the second would be false the moment it was acted on.
    """
    _fresh_state(tmp_path, monkeypatch)
    monkeypatch.setattr(tf, "installed_version", lambda: "2.1.226")
    monkeypatch.setattr(tf, "fix_command", lambda: "/home/u/.nvm/bin/npm install -g pkg")
    snap = tf.snapshot(_run=_run_returning("2.1.282"))
    assert tf.is_stale(snap)
    message = tf.describe(snap)
    assert "/home/u/.nvm/bin/npm install -g pkg" in message, message
    assert "RESTART" in message.upper(), message
    assert "2.1.226" in message and "2.1.282" in message, message


# ===========================================================================
# 3. KEYED TO THE PROPERTY, NOT TO TODAY'S VERSION OR YESTERDAY'S ERROR STRING.
# ===========================================================================

def test_the_control_survives_a_version_bump_and_still_catches_a_freeze(tmp_path, monkeypatch):
    """Keyed to the GAP, so both numbers moving together stays green and a freeze still reds.

    A leg pinned to '2.1.282 is current' would go red on the next release -- and a control that
    reds on the world being fine is one that gets deleted, taking the real property with it.
    """
    _fresh_state(tmp_path, monkeypatch)
    monkeypatch.setattr(tf, "fix_command", lambda: "npm install -g x")

    monkeypatch.setattr(tf, "installed_version", lambda: "9.9.500")
    assert tf.is_stale(tf.snapshot(_run=_run_returning("9.9.500"))) is False

    monkeypatch.setattr(tf, "installed_version", lambda: "9.9.100")
    assert tf.is_stale(tf.snapshot(_run=_run_returning("9.9.500"))) is True


def test_one_release_behind_is_not_a_finding_but_a_freeze_is(tmp_path, monkeypatch):
    """The threshold exists so this cannot become wallpaper -- the fate of the warning it replaces.

    Asserted over the whole partition rather than one side: a control that fired on every release
    would be ignored within a week, and one that never fired is what we already had.
    """
    _fresh_state(tmp_path, monkeypatch)
    monkeypatch.setattr(tf, "fix_command", lambda: "npm install -g x")
    monkeypatch.setattr(tf, "installed_version", lambda: "2.1.281")
    assert tf.is_stale(tf.snapshot(_run=_run_returning("2.1.282"))) is False, (
        "one release behind is reported as a finding; releases land most days and this will be "
        "ignored by the end of the week"
    )
    monkeypatch.setattr(tf, "installed_version", lambda: "2.1.226")
    assert tf.is_stale(tf.snapshot(_run=_run_returning("2.1.282"))) is True, (
        "56 releases behind -- the real freeze -- is not reported at all"
    )


# ===========================================================================
# 4. IT DOES NOT NAG, AND IT DOES NOT GO SILENT EITHER.
# ===========================================================================

def test_it_reports_once_per_version_pair_rather_than_every_tick(tmp_path, monkeypatch):
    """A daily repeat of an unchanged fact is how a real signal becomes wallpaper.

    And the second half matters as much: when the pair CHANGES it must speak again, or a machine
    that fell further behind would be quieter than one that just fell behind.
    """
    _fresh_state(tmp_path, monkeypatch)
    monkeypatch.setattr(tf, "installed_version", lambda: "2.1.226")
    monkeypatch.setattr(tf, "fix_command", lambda: "npm install -g x")

    sent: list[str] = []
    snap = tf.snapshot(_run=_run_returning("2.1.282"))
    assert tf.raise_if_stale(_defer=lambda m, **k: sent.append(m), _snap=snap) is not None
    assert len(sent) == 1

    assert tf.raise_if_stale(_defer=lambda m, **k: sent.append(m), _snap=snap) is None, (
        "the same unchanged freeze was reported twice"
    )
    assert len(sent) == 1

    moved = tf.snapshot(_run=_run_returning("2.1.300"))
    assert tf.raise_if_stale(_defer=lambda m, **k: sent.append(m), _snap=moved) is not None, (
        "the gap widened and nothing was said -- falling further behind must not buy silence"
    )
    assert len(sent) == 2


def test_recording_a_report_does_not_destroy_the_measurement_clock(tmp_path, monkeypatch):
    """`record_reported` and `cached_snapshot` share one file, and a wholesale rewrite in either
    direction silently re-arms the other. Here that would mean a registry call on every tick."""
    state = _fresh_state(tmp_path, monkeypatch)
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"measured_at": 1234.0, "snapshot": {"installed": "x"}}) + "\n")
    tf.record_reported({"installed": "a", "latest": "b", "cannot_tell": None})
    after = json.loads(state.read_text())
    assert after.get("measured_at") == 1234.0, (
        "record_reported dropped the cache clock, so the next tick re-measures over the network"
    )
    assert after.get("last_reported"), "the report was not recorded at all"


# ===========================================================================
# 5. AND IT IS ACTUALLY WIRED. An unwired mechanism has no red state.
# ===========================================================================

def test_the_toolchain_block_is_wired_into_the_tick_heartbeat():
    """`run_health_check()` has NO production caller -- only tests -- so wiring this there would
    have produced a green control with no runtime effect. It hangs off the tick heartbeat instead,
    which is written every tick and fetched by the site.

    Checked at the CALL SITE, and the positive control is that the record key is found: a rename
    that made this pattern match nothing would leave the leg green for ever, which is the failure
    this repository has already been bitten by more than once.
    """
    source = (Path(tf.__file__).resolve().parent / "worker_tick.py").read_text()
    assert "def _toolchain_block(" in source, (
        "worker_tick no longer defines _toolchain_block -- either the wiring was removed or it was "
        "renamed and this control is now blind. It must not be read as 'still wired'."
    )
    assert '"toolchain": _toolchain_block()' in source, (
        "_toolchain_block is defined but not placed in the heartbeat record, so nothing calls it "
        "and the freeze reaches no reader again"
    )


def test_the_tick_block_reports_unknown_rather_than_swallowing_an_error(monkeypatch):
    """The block must never return {} on failure. An absent block reads to every consumer as
    'nothing to say', which is indistinguishable from 'current' -- the same fail-silent shape the
    content-publish block above it was written to remove."""
    from background import worker_tick

    def _explode(*a, **k):
        raise RuntimeError("no npm anywhere")
    monkeypatch.setattr(tf, "cached_snapshot", _explode)
    block = worker_tick._toolchain_block()
    assert block.get("cannot_tell"), f"the failure was swallowed into {block!r}"
    assert block.get("stale") is None, (
        "stale was decided despite the check failing -- False here would publish a frozen "
        "toolchain as healthy"
    )


def test_the_disabled_autoupdater_note_still_names_this_module():
    """The suppression and its replacement must point at each other.

    `start_worker.sh` carries the 2026-07-09 reasoning that the problem was unpatchable here. That
    note is why nobody re-asked for 78 days, so leaving it standing alone would let the next reader
    reach the same conclusion. If the note moves, this leg reds rather than going quiet.
    """
    script = (Path(tf.__file__).resolve().parent / "start_worker.sh").read_text()
    assert "DISABLE_AUTOUPDATER" in script, (
        "start_worker.sh no longer disables the auto-updater; this module's premise has changed "
        "and its reasoning needs re-reading rather than silently continuing"
    )
    assert "toolchain_freshness" in script, (
        "the DISABLE_AUTOUPDATER note does not point at background/toolchain_freshness.py. The "
        "note's own reasoning -- that the mismatch is unpatchable here -- is what let this sit for "
        "78 days; a reader who finds the note must be sent to the thing that replaced it."
    )
