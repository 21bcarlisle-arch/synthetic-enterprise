"""§4 missing 'WORK THIS CREATES' block SURFACE -- R15 both-ways proof
(DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27, deliverable 4).

Item 2 (landed) built the §4 PARSER (`work_this_creates_deliverables`) and the missing-block DETECTOR
(`ruling_steer_missing_work_block`), both R15-proven. But §4 is binding *on the advisor*: "A ruling
arriving without one is a defect in the ruling -- say so and request it; do not silently absorb it."
The detector was wired NOWHERE (an un-surfaced detector is a fail-silent control), so a block-less
ruling would be detected and then silently dropped -- the exact silent absorption §4 forbids.

`supervisor.surface_missing_work_block_defects()` wires the detector to a real consumer: a durable
[ACTION NEEDED]-class register item (the director window / daily note reads OPEN items) + a
transition-only NTFY (R5). These tests prove it BOTH ways:
  * MUST FIRE: a staged ruling with NO block -> an open register item naming the ruling + the ask, and
    a single NTFY on the transition (fire-once, not per-cycle).
  * MUST STAY SILENT: a ruling WITH a block, and a non-ruling doc, produce no item and no NTFY (no
    false page -- feedback_control_false_positive_jams_pipeline).
  * RECONCILE: adding the block (or archiving the doc) clears the item (a fixed defect leaves the
    window -- R11 no-orphan-transition).
  * R15 INDEPENDENCE: neutralising the detector (`ruling_steer_missing_work_block` -> []) with a
    block-less ruling still on disk makes the defect go UNDETECTED -> the surface produces nothing:
    the fail-open direction is catchable, and the surface provably depends on the real detector, not a
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


def test_blockless_ruling_surfaces_item_and_fires_once(env):
    staging, register, sent, send = env
    (staging / "DIRECTOR_RULING_NOBLOCK_2026-07-27.md").write_text(_RULING_NO_BLOCK)

    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == ["DIRECTOR_RULING_NOBLOCK_2026-07-27.md"]

    # a durable OPEN register item naming the ruling + the ask
    items = action_needed.open_items(register)
    assert len(items) == 1
    item = items[0]
    assert "DIRECTOR_RULING_NOBLOCK_2026-07-27.md" in item["what"]
    assert "WORK THIS CREATES" in item["how"]
    assert "do not silently absorb" in item["why"]

    # a single NTFY on the TRANSITION, naming the ruling and stating the ask
    assert len(sent) == 1
    assert "DIRECTOR_RULING_NOBLOCK_2026-07-27.md" in sent[0]
    assert "WORK THIS CREATES" in sent[0]

    # fire-once: a second cycle with the SAME unfixed defect does NOT re-fire (R5 transition-only)
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert len(sent) == 1                      # still one send -- not re-paged every cycle
    assert len(action_needed.open_items(register)) == 1   # still exactly one open item


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


def test_adding_the_block_reconciles_the_item_closed(env):
    """R15 / no-orphan: a block-less ruling surfaces an item; add the block -> the item CLEARS so a
    FIXED defect leaves the director window (a release whose effect is nothing is a defect -- R11)."""
    staging, register, sent, send = env
    doc = staging / "DIRECTOR_RULING_FIXME_2026-07-27.md"
    doc.write_text(_RULING_NO_BLOCK)
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert len(action_needed.open_items(register)) == 1

    doc.write_text(_RULING_WITH_BLOCK)          # author closes it with a block
    got = supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert got == []
    assert action_needed.open_items(register) == []   # reconciled closed -- window is clean


def test_archiving_the_ruling_reconciles_the_item_closed(env):
    """A block-less ruling PARKED to in_progress/ (consumed) is no longer a root defect -> its item
    clears. The reconcile keys on the OBSERVABLE root state, not on how the doc left the root."""
    staging, register, sent, send = env
    doc = staging / "DIRECTOR_RULING_PARKME_2026-07-27.md"
    doc.write_text(_RULING_NO_BLOCK)
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert len(action_needed.open_items(register)) == 1

    (staging / "in_progress").mkdir()
    doc.rename(staging / "in_progress" / doc.name)   # parked/consumed
    supervisor.surface_missing_work_block_defects(
        staging_dir=staging, register_path=register, send_ntfy_fn=send)
    assert action_needed.open_items(register) == []


def test_R15_neutralised_detector_leaves_the_defect_undetected(env, monkeypatch):
    """R15 INDEPENDENCE (the fail-open direction, catchable): the surface depends on the REAL detector,
    not a constant. With a block-less ruling still on disk, neutralising the detector (mutation:
    `ruling_steer_missing_work_block` -> []) makes the defect go UNDETECTED -> the surface produces no
    item. The honest test (first block) asserts the item IS produced -> it goes RED under this mutation,
    which is exactly the teeth R15 requires: a control that could not fail here would be worse than none."""
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
