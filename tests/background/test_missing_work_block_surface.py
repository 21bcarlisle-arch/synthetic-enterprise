"""§4 missing 'WORK THIS CREATES' block SURFACE -- R15 both-ways proof
(DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27, deliverable 4).

Item 2 (landed) built the §4 PARSER (`work_this_creates_deliverables`) and the missing-block DETECTOR
(`ruling_steer_missing_work_block`), both R15-proven. The detector was wired NOWHERE (an un-surfaced
detector is a fail-silent control), so a block-less ruling would be detected and then silently dropped.
`supervisor.surface_missing_work_block_defects()` wires it to a real consumer: it returns the defective
ruling names and `run_cycle` LOGS them.

WHAT CHANGED 2026-08-03 (rip-out 102c29790 + THE_STANDARD, which governs the conflict). The surface used
to open a durable [ACTION NEEDED] register item + fire an NTFY -- a "waiting on Rich" queue entry for
something that is NOT one of the four reserved real-world classes. `action_needed.register_item` now
REFUSES exactly that class, which made the register/NTFY path dead code and left these tests asserting a
withdrawn contract (they were the whole of the 4-hour operational-signal RED on 2026-08-03). The
machine's answer to a block-less doc is now the one THE_STANDARD prescribes: ABSORB it -- the tick draws
the staged doc and mints the work from its body -- and say what it did, never page and wait.

These tests prove the surface BOTH ways under the current contract:
  * MUST DETECT: a staged ruling with NO block -> returned by the surface (so run_cycle logs it).
  * MUST NEVER PAGE: the same defect produces NO register item and NO NTFY. This is the fail-open teeth
    -- re-wiring a director page onto this non-reserved defect class turns this test RED.
  * MUST STAY SILENT: a ruling WITH a block, and a non-ruling doc, produce nothing at all (no false
    detection -- feedback_control_false_positive_jams_pipeline).
  * RECONCILE: a legacy pre-guard item clears once its ruling gains a block or leaves the root, so a
    withdrawn convention's items leave the director window (R11 no-orphan-transition).
  * R15 INDEPENDENCE: neutralising the detector (`ruling_steer_missing_work_block` -> []) with a
    block-less ruling still on disk makes the defect go UNDETECTED -> the surface returns nothing: the
    fail-open direction is catchable, and the surface provably depends on the real detector, not a
    constant.
"""
import pytest

from background import action_needed
from background import supervisor

pytestmark = pytest.mark.operational  # validates harness machinery, never a business surface


_RULING_WITH_BLOCK = (
    "# [DIRECTOR-RULING] -- some ruling\n\nbody prose\n\n"
    "## WORK THIS CREATES\n\n1. First deliverable.\n2. Second deliverable.\n"
)
_RULING_NO_BLOCK = "# [DIRECTOR-RULING] -- names work only in prose\n\ndo the merit-order thing please.\n"


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Isolated staging dir + action_needed register, and a capturing NTFY sink."""
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(supervisor, "STAGING_DIR", staging)
    register = tmp_path / "action_needed_register.json"
    sent: list[str] = []

    def _send(msg, **kwargs):
        sent.append(msg)
        return "ntfy-id-1"                     # truthy id => a CONFIRMED send (advances the clock)

    return staging, register, sent, _send


def _seed_legacy_item(register, ruling_name):
    """Write a pre-guard §4 item straight into the register file, bypassing register_item (which now
    refuses this whole class). Reproduces what a live register carried before 2026-08-03, so the
    reconcile path is tested against real legacy state rather than state the code can still create."""
    reg = action_needed.load_register(register)
    reg[supervisor._MISSING_BLOCK_ITEM_PREFIX + ruling_name] = {
        "item_id": supervisor._MISSING_BLOCK_ITEM_PREFIX + ruling_name,
        "what": f"Staged ruling/steer '{ruling_name}' carries NO 'WORK THIS CREATES' block (§4 defect).",
        "how": "legacy", "why": "legacy",
        "first_asked_at": "2026-08-01T00:00:00+00:00",
        "last_pinged_at": "2026-08-01T00:00:00+00:00",
        "last_sent_at": None, "resolved": False,
    }
    action_needed.save_register(reg, register)
    assert len(action_needed.open_items(register)) == 1      # the legacy item really is open


def test_blockless_ruling_detected_but_never_pages(env):
    """MUST DETECT + MUST NEVER PAGE. The defect is surfaced through the RETURN VALUE (run_cycle logs
    it), and produces no director-queue item and no NTFY -- a missing block is a defect in the doc, not
    one of the four reserved real-world classes, so it is absorbed and never queued against a human."""
    staging, register, sent, send = env
    (staging / "DIRECTOR_RULING_NOBLOCK_2026-07-27.md").write_text(_RULING_NO_BLOCK)

    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == ["DIRECTOR_RULING_NOBLOCK_2026-07-27.md"]

    assert action_needed.open_items(register) == []          # no "waiting on Rich" entry
    assert sent == []                                        # and no page

    # stable across cycles: still detected, still never paged (no drift into a queue on repeat ticks)
    again = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert again == ["DIRECTOR_RULING_NOBLOCK_2026-07-27.md"]
    assert action_needed.open_items(register) == []
    assert sent == []


def test_the_register_itself_refuses_this_defect_class(env):
    """The guard this contract rests on, asserted directly rather than assumed: the §4 ask really is
    outside the four reserved classes, so `register_item` REFUSES it. If that guard were ever loosened,
    the surface's no-page design would be resting on nothing -- this test says so out loud."""
    _, register, _, _ = env
    with pytest.raises(action_needed.NotReservedForDirector):
        action_needed.register_item(
            "ruling_missing_work_block:DIRECTOR_RULING_X_2026-07-27.md",
            what="Staged ruling/steer 'DIRECTOR_RULING_X_2026-07-27.md' carries NO "
                 "'WORK THIS CREATES' block (§4 defect).",
            how="Close the ruling with a 'WORK THIS CREATES' block.",
            why="§4 DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27.",
            path=register,
        )


def test_ruling_with_block_stays_silent(env):
    """Legitimate-edge: a well-formed ruling (has a block) and a non-ruling doc never false-fire."""
    staging, register, sent, send = env
    (staging / "DIRECTOR_RULING_OK_2026-07-27.md").write_text(_RULING_WITH_BLOCK)
    (staging / "ordinary_note.md").write_text("just an ordinary staged note, no tag")

    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == []
    assert action_needed.open_items(register) == []
    assert sent == []


def test_adding_the_block_reconciles_a_legacy_item_closed(env):
    """R11 no-orphan: a LEGACY pre-guard item (the register no longer creates these) clears once its
    ruling gains a block -- a withdrawn convention's items must be able to LEAVE the director window,
    not linger forever unresolvable."""
    staging, register, sent, send = env
    doc = staging / "DIRECTOR_RULING_FIXME_2026-07-27.md"
    doc.write_text(_RULING_NO_BLOCK)
    _seed_legacy_item(register, doc.name)

    # still block-less -> the legacy item is NOT cleared (clearing it would be a false "fixed")
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert len(action_needed.open_items(register)) == 1

    doc.write_text(_RULING_WITH_BLOCK)          # author closes it with a block
    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == []
    assert action_needed.open_items(register) == []   # reconciled closed -- window is clean
    assert sent == []


def test_archiving_the_ruling_reconciles_a_legacy_item_closed(env):
    """A block-less ruling PARKED to in_progress/ (consumed) is no longer a root defect -> its legacy
    item clears. The reconcile keys on the OBSERVABLE root state, not on how the doc left the root."""
    staging, register, sent, send = env
    doc = staging / "DIRECTOR_RULING_PARKME_2026-07-27.md"
    doc.write_text(_RULING_NO_BLOCK)
    _seed_legacy_item(register, doc.name)

    (staging / "in_progress").mkdir()
    doc.rename(staging / "in_progress" / doc.name)   # parked/consumed
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert action_needed.open_items(register) == []
    assert sent == []


def test_R15_neutralised_detector_leaves_the_defect_undetected(env, monkeypatch):
    """R15 INDEPENDENCE (the fail-open direction, catchable): the surface depends on the REAL detector,
    not a constant. With a block-less ruling still on disk, neutralising the detector (mutation:
    `ruling_steer_missing_work_block` -> []) makes the defect go UNDETECTED -> the surface returns
    nothing. The honest test (first block) asserts the defect IS returned -> it goes RED under this
    mutation, which is exactly the teeth R15 requires: a control that could not fail here would be
    worse than none."""
    staging, register, sent, send = env
    (staging / "DIRECTOR_RULING_HIDDEN_2026-07-27.md").write_text(_RULING_NO_BLOCK)

    # honest detector: the defect is found
    assert supervisor.ruling_steer_missing_work_block(staging) == ["DIRECTOR_RULING_HIDDEN_2026-07-27.md"]

    # mutate the detector to a no-op (fail-open) -> the surface must now find nothing
    monkeypatch.setattr(supervisor, "ruling_steer_missing_work_block", lambda *a, **k: [])
    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == []
    assert action_needed.open_items(register) == []
    assert sent == []
