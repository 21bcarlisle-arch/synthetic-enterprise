"""Internal work-order text must never reach the director channel (2026-08-13).

The message that forced this, verbatim from the ops mirror at 16:20:44Z, carried the tick's raw
doorbell -- the whole drawn-work list -- to the director's phone.
"""
from __future__ import annotations

import pytest

from background import doorbell_redaction as dr

# The real doorbell, trimmed to five names from the 114 that were sent.
REAL_DOORBELL = (
    "unprocessed staging -- ADVISOR_PROPOSAL_SEAT_CUTOVER_AND_DR_2026-08-07.md, "
    "ADVISOR_RETRO_FAILURE_MODES_AND_BIRTH_CERTIFICATE_LAW_2026-08-05.md, "
    "CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md, CLASS_MEASUREMENTS_THAT_MOVED_2026-08-11.md, "
    "WORKER_FINDING_A_SATURATION_EDGE_WAS_THE_GRIDS_OWN_END_2026-08-13.md"
)
REAL_MESSAGE = (
    f"Supervisor: granting turns for ~60min for the same work ({REAL_DOORBELL}) with no state "
    "change -- something below the tmux layer may be swallowing turns."
)

REAL_ENUMERATION = (
    "AUTHORIZED-SET enumeration [build=Y site=Y discover_frame=Y open_campaign=. planner=Y] -> "
    "MUST-DRAW: build,site,discover_frame,planner | OPEN MINTS (1): "
    "PLANNER_MINTED_ssp_negative_lift_cells_2026-07-24.md -> the merit-order reconstruction landed"
)


def test_the_message_the_director_received_is_collapsed():
    out = dr.redact(REAL_MESSAGE)
    assert "2 more (see docs/staging/)" in out
    assert "CLASS_MEASUREMENTS_THAT_MOVED_2026-08-11.md" not in out
    # The ALARM survives intact -- only the listing is trimmed. Deleting the alert to punish its
    # formatting would be the worse defect.
    assert "granting turns for ~60min" in out
    assert "swallowing turns" in out


def test_the_tick_enumeration_never_goes_out():
    """Pure machine state: the draw's own working. It says nothing a person can act on."""
    out = dr.redact(f"Tick verdict: drew. {REAL_ENUMERATION}")
    assert "AUTHORIZED-SET" not in out
    assert "MUST-DRAW" not in out
    assert "OPEN MINTS" not in out
    assert "Tick verdict: drew." in out
    assert "redacted" in out


def test_a_short_list_of_names_is_LEFT_ALONE():
    """MUTATION both ways. 'Which documents' is often the whole diagnostic -- the dead-man's
    switch naming two blocked mints is exactly the message he wants. This bounds volume; it is
    not a ban on filenames."""
    msg = "[ACT] blocked mints: PLANNER_MINTED_a_2026-07-24.md, PLANNER_MINTED_b_2026-07-29.md"
    assert dr.redact(msg) == msg
    assert not dr.was_redacted(msg, dr.redact(msg))


def test_ordinary_alarms_pass_through_untouched():
    for msg in (
        "[PUBLISHING DOWN] The published figures have not reached origin for 18.0h.",
        "[SIM] Run FAILED after 121s - KeyError: 'epc_rating' (full tail in sim-runner-log.md)",
        "New staged instruction: WORKER_FINDING_A_SATURATION_EDGE_2026-08-13.md - pending review",
        "",
    ):
        assert dr.redact(msg) == msg, f"redactor touched an innocent message: {msg!r}"


def test_redaction_is_idempotent():
    """The guard sits on a path a message can reach more than once. A redactor that re-collapsed
    its own summary would eat the alarm one pass at a time."""
    once = dr.redact(REAL_MESSAGE)
    assert dr.redact(once) == once
    assert dr.redact(dr.redact(REAL_ENUMERATION)) == dr.redact(REAL_ENUMERATION)


@pytest.mark.real_ntfy
def test_the_guard_is_wired_into_the_one_channel_he_reads(monkeypatch):
    """R11, no orphan transitions: a redactor nothing calls is a module, not a control.

    MUTATION: remove the `redact(...)` call from `send_ntfy` and this fails.
    """
    from background import ntfy_utils

    posted = {}

    def fake_run(cmd, **kwargs):
        posted["message"] = cmd[cmd.index("-d") + 1]
        return type("R", (), {"stdout": '{"id": "abc"}\n200', "returncode": 0, "stderr": ""})()

    monkeypatch.setattr(ntfy_utils.subprocess, "run", fake_run)
    monkeypatch.setattr(ntfy_utils, "record_delivery_outcome", lambda *a, **k: None)
    monkeypatch.setattr("background.ntfy_mirror.append_mirror_entry", lambda *a, **k: None)
    monkeypatch.setattr("background.director_input_log.append_entry", lambda *a, **k: None)

    ntfy_utils.send_ntfy(REAL_MESSAGE, _allow_real_send=True)

    assert "CLASS_MEASUREMENTS_THAT_MOVED_2026-08-11.md" not in posted["message"], (
        "the raw drawn-work list reached the send -- the guard is not on the channel"
    )
    assert "2 more (see docs/staging/)" in posted["message"]


@pytest.mark.real_ntfy
def test_the_full_text_stays_recoverable_in_the_mirror(monkeypatch):
    """G-N4's rule applied to redaction: volume is cut by ROUTING, never by dropping. The list is
    removed from his PHONE and from nowhere else."""
    from background import ntfy_utils

    mirrored = []
    monkeypatch.setattr(ntfy_utils.subprocess, "run",
                        lambda cmd, **k: type("R", (), {"stdout": '{"id":"x"}\n200',
                                                        "returncode": 0, "stderr": ""})())
    monkeypatch.setattr(ntfy_utils, "record_delivery_outcome", lambda *a, **k: None)
    monkeypatch.setattr("background.ntfy_mirror.append_mirror_entry",
                        lambda direction, msg, **k: mirrored.append((direction, msg)))
    monkeypatch.setattr("background.director_input_log.append_entry", lambda *a, **k: None)

    ntfy_utils.send_ntfy(REAL_MESSAGE, _allow_real_send=True)

    redacted_entries = [m for d, m in mirrored if d == "out-redacted"]
    assert redacted_entries, "a redaction left no trace -- the channel edits in silence"
    assert "CLASS_MEASUREMENTS_THAT_MOVED_2026-08-11.md" in redacted_entries[0]


def test_a_sender_can_summarise_rather_than_lean_on_the_guard():
    """The guard is the backstop; a sender should not need it. `summarise_work_order` is what
    `supervisor._check_stuck_escalation` passes instead of the raw doorbell."""
    assert dr.summarise_work_order(REAL_DOORBELL) == "unprocessed staging, 5 item(s)"
    assert dr.summarise_work_order("publish gate wedge") == "publish gate wedge"
    assert dr.summarise_work_order("") == "work"


def test_the_summary_survives_the_guard_untouched():
    """The two halves compose: a message built from the summary has nothing left to redact, so
    the courtesy path and the wall agree rather than each trimming the other's output."""
    msg = (f"Supervisor: granting turns for ~60min for the same work "
           f"({dr.summarise_work_order(REAL_DOORBELL)}) with no state change.")
    assert dr.redact(msg) == msg
