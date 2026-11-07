"""A repeating-alarm filing reaches the orienting seat BY NAME, not as one LATENT among many.

The defect: `alarm_repetition` files at LATENT and `findings_now()` names only BLOCKING and
UNCLASSIFIED documents, so the 7 Nov fork-open alarm was globbed off the shared tree by the 18:48
orientation and handed to it as a count. Its being untracked was not the gap (the seat reads the
filesystem); the brief not naming it was.
"""
from __future__ import annotations

from background import delivery_seat as seat

FORK = "WORKER_FINDING_REPEATING_ALARM_FORK_OPEN_STREAK_2026-11-07.md"


def _file(root, name, *dates):
    lines = "\n".join(f"- **{d}** — still live: the fork is open" for d in dates)
    (root / name).write_text(
        "**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`\n\n"
        f"# The shared tree's fork with origin is open\n\n## Still live\n\n{lines}\n",
        encoding="utf-8")


def test_a_LATENT_alarm_is_NAMED_in_the_prompt_the_seat_reads(tmp_path):
    """MUTATION (must fire): drop `_render_live_alarms(...)` from `_prompt`'s assembly, or drop
    the `live_alarms` key from the brief -- the name then appears nowhere above the JSON."""
    _file(tmp_path, FORK, "2026-10-23", "2026-11-07")
    _file(tmp_path, "WORKER_FINDING_REPEATING_ALARM_OLDER_2026-10-01.md", "2026-10-01")
    (tmp_path / "done").mkdir()
    _file(tmp_path / "done", "WORKER_FINDING_REPEATING_ALARM_ARCHIVED_2026-09-01.md", "2026-09-01")

    block = seat.live_alarms(tmp_path)
    assert block["available"] is True
    names = [r["name"] for r in block["alarms"]]
    # Newest observation first, and an archived one is not live.
    assert names == [FORK, "WORKER_FINDING_REPEATING_ALARM_OLDER_2026-10-01.md"]
    assert block["alarms"][0]["last"] == "2026-11-07"

    prompt = seat._prompt({"live_alarms": block})
    above_the_json = prompt.split("THE STRETCH, assembled from git")[0]
    assert FORK in above_the_json


def test_an_unreadable_alarm_room_SAYS_it_was_not_read_rather_than_none_is_live():
    """Silence must not read as 'no alarm firing'. MUTATION (must fire): render an unavailable
    block as the empty-room sentence."""
    text = seat._render_live_alarms({"available": False, "why": "OSError('x')"})
    assert "COULD NOT BE READ" in text and "OSError" in text
    assert "NO REPEATING ALARM" not in text
