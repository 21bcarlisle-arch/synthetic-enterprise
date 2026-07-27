"""The single HARDEN-commit classifier (WORK_DEFINITION §1, 2026-07-27). One source of truth for
'is this commit a HARDEN re-verify?', consumed by deadmans_switch (liveness clock) and
daily_self_note (substantive count + product/machinery split). R15 independence: the verdict is
derived from the ACTUAL subject string, never a constant."""
from __future__ import annotations

from background.harden_commit import is_harden_commit


def test_bracket_form_is_harden():
    """The `[HARDEN <atom>]` form -- the one that touches real code/tests and previously counted
    as forward work. These are the shipped subjects from `git log` 2026-07-27."""
    assert is_harden_commit("[HARDEN D5_account_hierarchy_payments] Rule-0 dial-yield (dial=4): ...")
    assert is_harden_commit("[HARDEN C13_weather_normalisation] Rule-0 dial-yield: re-verify 24 exit tests")
    assert is_harden_commit("[HARDEN] re-verify")  # atom-less bracket form


def test_chore_harden_form_is_harden():
    """The `chore(harden...)` cooldown-stamp / no-source re-verify form."""
    assert is_harden_commit("chore(harden): re-verify B1_margin_bridge after sibling scope-change")
    assert is_harden_commit("chore(harden-cooldown): stamp ARCH1_internal_seams pass")


def test_leading_whitespace_tolerated():
    assert is_harden_commit("  [HARDEN X] pass")


def test_real_work_is_not_harden():
    """No over-match: genuine forward-work subjects, and near-miss prefixes, are NOT HARDEN."""
    assert not is_harden_commit("[build] real forward progress landed here")
    assert not is_harden_commit("Wave-1 integration: bank F7->L2")
    assert not is_harden_commit("[DIRECTOR-RULING][mint-consume] WORK_DEFINITION §4")
    assert not is_harden_commit("Auto-process run complete: report + LATEST.md + site/")
    assert not is_harden_commit("chore(liveness): publish heartbeat")  # a different chore, not harden
    assert not is_harden_commit("feat: hardening pass notes")  # substring 'harden' mid-subject != marker
    assert not is_harden_commit("")
