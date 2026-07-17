"""OPS1 sub-step 6 — the ONE notification contract (§2.3): typed + transition-only.

R15/MAKE_IT_STICK: the contract's two properties are mutation-tested (a transition control that
re-pages an unchanged status, or a test fixture that can page, is the disease), and a grep-guard
enforces that NEW code pages via notify() — with a SHRINKING allowlist as the migration checklist.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

from background import notify as N

BG = Path(__file__).resolve().parents[2] / "background"


@pytest.fixture
def sent(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")
    captured = []
    # notify() calls ntfy_utils.send_ntfy via the module -> patch it there.
    monkeypatch.setattr(
        N.ntfy_utils, "send_ntfy",
        lambda msg, headers=None, _allow_real_send=False: (captured.append((msg, headers)) or "id123"),
    )
    return captured


# ── G-N2: typed by source ──────────────────────────────────────────────────────────────────
def test_untyped_notify_is_forbidden(sent):
    with pytest.raises(ValueError):
        N.notify("x", kind="not-a-kind")


def test_real_alarm_sends_with_structural_tag(sent):
    assert N.notify("boom", kind="real_alarm") == "id123"
    assert len(sent) == 1
    _msg, headers = sent[0]
    assert headers["Tags"] == "rotating_light"          # type is structural, the director sees it


def test_test_fixture_can_never_page(sent):
    assert N.notify("synthetic", kind="test_fixture") == "test_fixture:not-sent"
    assert sent == []                                    # structurally not sent (independent of pytest)


# ── G-N1 / R5: transition-only ───────────────────────────────────────────────────────────────
def test_transition_only_suppresses_an_unchanged_status(sent):
    first = N.notify("stale!", kind="real_alarm", transition_key="loop", state="LOOP_BROKEN")
    again = N.notify("stale!", kind="real_alarm", transition_key="loop", state="LOOP_BROKEN")
    assert first == "id123"
    assert again == "suppressed:unchanged:loop"          # THE mutation: unchanged never re-pages
    assert len(sent) == 1


def test_transition_sends_on_a_state_change(sent):
    N.notify("s", kind="real_alarm", transition_key="loop", state="OK")
    N.notify("s", kind="real_alarm", transition_key="loop", state="LOOP_BROKEN")   # changed -> sends
    assert len(sent) == 2


def test_clear_transition_rearms(sent):
    N.notify("s", kind="real_alarm", transition_key="loop", state="LOOP_BROKEN")
    N.clear_transition("loop")
    again = N.notify("s", kind="real_alarm", transition_key="loop", state="LOOP_BROKEN")
    assert again == "id123"                              # re-armed after a resolved alarm
    assert len(sent) == 2


def test_no_transition_key_always_sends(sent):
    N.notify("a", kind="director_echo")
    N.notify("a", kind="director_echo")                  # no key -> not deduped
    assert len(sent) == 2


# ── re_escalate_after: transition-only PLUS re-alert while still stuck (the deadman pattern) ──
def test_re_escalate_suppresses_an_unchanged_state_within_the_window(sent):
    N.notify("stuck", kind="real_alarm", transition_key="k", state="STUCK", re_escalate_after=3600)
    N.notify("stuck", kind="real_alarm", transition_key="k", state="STUCK", re_escalate_after=3600)
    assert len(sent) == 1                                # unchanged + within window -> suppressed


def test_re_escalate_resends_an_unchanged_state_after_the_window(sent):
    import json
    N.notify("stuck", kind="real_alarm", transition_key="k", state="STUCK", re_escalate_after=3600)
    # age the stored timestamp past the window
    store = json.loads(N.TRANSITIONS_FILE.read_text())
    store["k"]["ts"] = time.time() - 3601
    N.TRANSITIONS_FILE.write_text(json.dumps(store))
    N.notify("stuck", kind="real_alarm", transition_key="k", state="STUCK", re_escalate_after=3600)
    assert len(sent) == 2                                # window elapsed -> re-escalated


def test_a_changed_state_sends_immediately_even_within_the_window(sent):
    N.notify("s", kind="real_alarm", transition_key="k", state="BLOCKED", re_escalate_after=3600)
    N.notify("s", kind="real_alarm", transition_key="k", state="CLEARED", re_escalate_after=3600)
    assert len(sent) == 2                                # a real state change is never suppressed


# ── MAKE_IT_STICK: the single-path grep-guard (shrinking allowlist = migration checklist) ────
# New code must page via notify(). These are the GRANDFATHERED direct send_ntfy callers, tracked
# as a checklist that can only SHRINK as they collapse onto the contract (§2.3). notify.py (the
# contract) and ntfy_utils.py (the primitive) are the two that legitimately touch send_ntfy.
_ALLOWED_DIRECT_SENDERS = {
    "notify.py", "ntfy_utils.py",
    # ntfy_mirror.py: NOT a real caller — its `send_ntfy(` is in a comment; it is the mirror
    # target that send_ntfy() calls, so it stays here (the regex matches the comment) but is never
    # migrated.
    "ntfy_mirror.py",
    # migration debt — remaining direct callers to route through notify() (2; was 17 — cohorts 1-5
    # migrated 13, incl. the deadman via the notify() re_escalate_after extension). The last 2:
    #  - supervisor: SAFETY-CRITICAL turn-granting daemon; careful transition-preserving migration.
    #  - process_run_complete: pipeline-critical publish path (3 sites); careful.
    "process_run_complete.py", "supervisor.py",
}


def _direct_senders() -> set[str]:
    return {py.name for py in BG.glob("*.py") if re.search(r"\bsend_ntfy\s*\(", py.read_text())}


def test_no_new_direct_send_ntfy_caller_outside_the_contract():
    offenders = _direct_senders() - _ALLOWED_DIRECT_SENDERS
    assert not offenders, (
        "NEW direct send_ntfy caller(s) -- route through background.notify.notify(): "
        + ", ".join(sorted(offenders))
    )


def test_allowlist_has_no_stale_entries():
    """Keeps the migration checklist honest: a file that no longer calls send_ntfy is removed
    from the allowlist (so the list can only shrink toward {notify, ntfy_utils})."""
    stale = _ALLOWED_DIRECT_SENDERS - _direct_senders()
    assert not stale, f"allowlist entries no longer call send_ntfy (remove them): {sorted(stale)}"
