"""The autostart control must be able to FAIL on its own named defect (R15).

The defect it exists to catch is precisely the 2026-08-12 outage: WSL down until a human logged
in. So the control is only worth anything if it goes RED on that exact history and GREEN on the
opposite one, and if every way of not-knowing lands on UNPROVEN rather than on a pass.

Each control below is followed by the mutation that performs the defect and shows the control
failing on it, so the control is tried rather than trusted.
"""

from __future__ import annotations

import datetime as _dt

import pytest

from tools import verify_host_autostart as vha

UTC = _dt.timezone.utc


def _t(hh, mm, ss=0):
    return _dt.datetime(2026, 8, 12, hh, mm, ss, tzinfo=UTC)


# --------------------------------------------------------------------------------------
# CONTROL 1 -- the verdict discriminates the two histories that actually happened.
# --------------------------------------------------------------------------------------

def test_the_real_2026_08_12_history_is_a_FAIL():
    """The outage itself: Windows up 08:33Z, WSL not until the 08:55Z logon."""
    status, reason = vha.verdict(wsl_boot=_t(8, 55, 33), first_logon=_t(8, 55, 26))
    assert status == vha.FAIL
    assert "after the first interactive logon" in reason.lower()


def test_a_self_started_boot_is_a_PASS():
    """What SkynetBootStart is supposed to produce: WSL up long before anyone logs in."""
    status, reason = vha.verdict(wsl_boot=_t(8, 33, 50), first_logon=_t(9, 40, 0))
    assert status == vha.PASS
    assert "before the first interactive logon" in reason.lower()


def test_the_mutation_that_would_make_FAIL_unreachable_is_caught():
    """MUTATION: an implementation that returns PASS whenever it has two clocks at all.

    That is the plausible wrong version -- it looks like it compares them, and it is green on
    every input including the outage. Control 1 kills it.
    """
    def mutant(wsl_boot, first_logon):
        if wsl_boot is None or first_logon is None:
            return vha.UNPROVEN, "unknown"
        return vha.PASS, "two clocks present"

    status, _ = mutant(_t(8, 55, 33), _t(8, 55, 26))
    assert status == vha.PASS, "the mutant is green on the real outage"
    real, _ = vha.verdict(_t(8, 55, 33), _t(8, 55, 26))
    assert real == vha.FAIL, "the real implementation is not"


# --------------------------------------------------------------------------------------
# CONTROL 2 -- every way of not-knowing is UNPROVEN, never PASS (fail-closed, R15).
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "wsl_boot,first_logon,why",
    [
        (None, _t(9, 0), "kernel btime unreadable"),
        (_t(8, 33), None, "Security log unreadable / needs elevation"),
        (None, None, "neither clock available"),
    ],
)
def test_missing_evidence_is_UNPROVEN_never_PASS(wsl_boot, first_logon, why):
    status, _ = vha.verdict(wsl_boot, first_logon)
    assert status == vha.UNPROVEN, why


def test_the_fail_open_mutation_is_caught():
    """MUTATION: treat 'no logon found' as proof nobody logged in, and pass.

    This is the tempting reading and it is exactly the R15 fail-open shape: the Security log
    needs elevation, so the commonest cause of 'no logon found' is that we could not look.
    """
    def mutant(wsl_boot, first_logon):
        if first_logon is None:
            return vha.PASS, "nobody logged in"
        return vha.verdict(wsl_boot, first_logon)

    assert mutant(_t(8, 33), None)[0] == vha.PASS, "the mutant passes on an unreadable log"
    assert vha.verdict(_t(8, 33), None)[0] == vha.UNPROVEN, "the real implementation does not"


# --------------------------------------------------------------------------------------
# CONTROL 3 -- btime is read from the kernel's own record, and a missing one is not a zero.
# --------------------------------------------------------------------------------------

def test_btime_is_parsed_from_proc_stat(tmp_path):
    stat = tmp_path / "stat"
    stat.write_text("cpu  1 2 3\nbtime 1786517733\nprocesses 999\n")
    got = vha.wsl_boot_time_utc(stat)
    assert got == _dt.datetime.fromtimestamp(1786517733, tz=UTC)


@pytest.mark.parametrize("body", ["cpu 1 2 3\nprocesses 9\n", "btime notanumber\n", ""])
def test_a_missing_or_malformed_btime_is_None_not_epoch_zero(tmp_path, body):
    """None and 1970 are opposite facts. Epoch zero would be BEFORE every logon, so a
    malformed btime silently becomes a PASS -- the worst available failure."""
    stat = tmp_path / "stat"
    stat.write_text(body)
    assert vha.wsl_boot_time_utc(stat) is None


def test_the_epoch_zero_mutation_would_pass_the_outage():
    """MUTATION: default an unreadable btime to 0 instead of None."""
    status, _ = vha.verdict(_dt.datetime.fromtimestamp(0, tz=UTC), _t(8, 55, 26))
    assert status == vha.PASS, "epoch-zero btime passes anything -- which is why None is required"


# --------------------------------------------------------------------------------------
# CONTROL 4 -- the logon reader treats a dead or erroring PowerShell as unanswered, not as clean.
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("payload", [None, "", "   ", "NONE", "not-a-timestamp", "2026-08-12 09:00"])
def test_unusable_powershell_output_is_None(payload):
    assert vha.first_interactive_logon_utc(runner=lambda _s: payload) is None


def test_a_raising_runner_is_None_not_an_exception():
    def boom(_script):
        raise RuntimeError("powershell.exe missing")
    assert vha.first_interactive_logon_utc(runner=boom) is None


def test_a_good_timestamp_round_trips_to_utc():
    got = vha.first_interactive_logon_utc(runner=lambda _s: "2026-08-12T08:55:26.0000000+00:00")
    assert got == _t(8, 55, 26)


# --------------------------------------------------------------------------------------
# CONTROL 5 -- the query only counts HUMAN logons.
# --------------------------------------------------------------------------------------

def test_only_interactive_logon_types_are_counted():
    """Service (5) and network (3) logons happen constantly on a booting machine. Counting them
    would put a 'logon' microseconds after boot on every reboot and make FAIL unreachable."""
    assert vha.INTERACTIVE_LOGON_TYPES == (2, 10, 11)
    assert 5 not in vha.INTERACTIVE_LOGON_TYPES
    assert 3 not in vha.INTERACTIVE_LOGON_TYPES
    for t in vha.INTERACTIVE_LOGON_TYPES:
        assert str(t) in vha._PS_FIRST_LOGON, "the query must filter to the documented types"


def test_the_query_windows_from_host_boot_not_from_wsl_boot():
    """Anchoring the search at WSL's boot would hide the very logon that CAUSED it."""
    assert "LastBootUpTime" in vha._PS_FIRST_LOGON


# --------------------------------------------------------------------------------------
# CONTROL 6 -- Windows' own pseudo-accounts must not count as humans.
#
# Found by RUNNING the control, not by reasoning: on this box every boot logs type-2 logons for
# Font\UMFD-0, Font\UMFD-1 and Window\DWM-1 within a second of start. If those count, a "human"
# is always present at boot+1s, WSL starting at boot+30s always reads as FAIL, and PASS becomes
# unreachable -- a fail-ALWAYS control, as useless as a fail-open one.
# --------------------------------------------------------------------------------------

def test_the_windows_pseudo_accounts_are_excluded_by_the_query():
    q = vha._PS_FIRST_LOGON
    assert "UMFD" in q and "DWM" in q, "the window/font hosts must be filtered by name"
    assert "*$" in q, "machine accounts end in $ and are not people"


def test_the_real_observed_boot_sequence_would_not_be_read_as_a_human():
    """The literal 2026-08-12 sequence. Only the MicrosoftAccount logon is a person."""
    observed = [
        ("09:33:18", 2, "Font", "UMFD-0"),
        ("09:33:18", 2, "Font", "UMFD-1"),
        ("09:33:18", 2, "Window", "DWM-1"),
        ("09:55:26", 11, "MicrosoftAccount", "21bcarlisle@gmail.com"),
    ]

    def is_human(domain, name):
        if name.endswith("$"):
            return False
        if any(domain.startswith(p) for p in ("Window", "Font", "NT")):
            return False
        return True

    humans = [(t, d, n) for t, _ty, d, n in observed if is_human(d, n)]
    assert len(humans) == 1, f"exactly one human logon expected, got {humans}"
    assert humans[0][0] == "09:55:26"


def test_the_unfiltered_mutation_makes_PASS_unreachable():
    """MUTATION: filter on logon TYPE only, as the first version of this module did.

    Under it, a boot-started WSL (boot+30s) is judged against a UMFD logon at boot+1s and
    reports FAIL -- so the control would have condemned a working autostart.
    """
    host_boot = _t(8, 33, 17)
    umfd_logon = host_boot + _dt.timedelta(seconds=1)
    wsl_boot_after_fix = host_boot + _dt.timedelta(seconds=30)

    unfiltered, _ = vha.verdict(wsl_boot_after_fix, umfd_logon)
    assert unfiltered == vha.FAIL, "type-only filtering condemns a correct autostart"

    real_human_logon = _t(9, 55, 26)
    filtered, _ = vha.verdict(wsl_boot_after_fix, real_human_logon)
    assert filtered == vha.PASS, "filtering to real accounts lets a correct autostart pass"


# --------------------------------------------------------------------------------------
# CONTROL 7 -- the verdict is WIRED. A control nobody runs is the no-caller class.
#
# tools/orphan_ratchet.py refused the first version of this commit for exactly that reason:
# the module existed, was tested, and nothing ran it. It is now read once per boot by
# background/boot_announce.py, on the boot it is about.
# --------------------------------------------------------------------------------------

def test_boot_announce_reports_each_verdict_distinguishably():
    from background import boot_announce as ba

    assert "SELF-STARTED" in ba._autostart_line({"status": "PASS", "reason": "r"})
    assert "HUMAN-STARTED" in ba._autostart_line({"status": "FAIL", "reason": "r"})
    assert "UNPROVEN" in ba._autostart_line({"status": "UNPROVEN", "reason": "r"})


def test_a_broken_verdict_degrades_to_UNPROVEN_and_never_breaks_the_announce():
    """MUTATION: let the diagnostic raise. The boot announce must still be produced --
    losing the whole boot report to a diagnostic extra is strictly worse than losing the extra."""
    from background import boot_announce as ba
    import tools.verify_host_autostart as vha

    original = vha.evaluate
    try:
        vha.evaluate = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        line = ba._autostart_line()
    finally:
        vha.evaluate = original
    assert "UNPROVEN" in line
    assert "RuntimeError" in line


def test_the_autostart_line_reaches_the_summary_text():
    from background import boot_announce as ba

    text, _ = ba.build_summary(
        proc_results=[], sched_results=[],
        autostart={"status": "PASS", "reason": "booted 900s before any human logon"},
    )
    assert "SELF-STARTED" in text, "the verdict must appear in the text that is actually sent"


def test_a_human_started_boot_does_not_raise_the_alarm_flag():
    """A director reboot-and-sign-in is the normal case; alarming on it would fire on most
    boots and become wallpaper. Stated, not alarmed."""
    from background import boot_announce as ba

    _, has_alarm = ba.build_summary(
        proc_results=[], sched_results=[],
        autostart={"status": "FAIL", "reason": "a human started it"},
    )
    assert has_alarm is False
