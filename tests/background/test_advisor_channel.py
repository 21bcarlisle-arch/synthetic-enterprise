"""The advisor channel draws an attributed file first and refuses an unattributed one with its reason.

Director, 15 Oct (DIRECTOR_STEER_ADVISOR_CHANNEL_NO_PASTE_2026-10-15.md): "Test that an advisor file
is drawn first, and that one without a valid attribution is refused with its reason."
"""
from pathlib import Path

import pytest

from background import advisor_channel as ac

HEADER = ("**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · "
          "**Atom:** `unminted`\n\n# A steer\n\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ac.ADVISOR_DIR_REL).mkdir(parents=True)
    return tmp_path


def _write(repo: Path, name: str, body: str) -> None:
    (repo / ac.ADVISOR_DIR_REL / name).write_text(HEADER + body, encoding="utf-8")


def test_the_partition_holds_a_drawn_and_a_refused_file_at_once(repo):
    """Control over the whole partition: both verdicts are reachable in one folder, so a rule that
    refused everything (or drew everything) fails here, not silently."""
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a separate channel"\n')
    _write(repo, "B_delegated.md", "Acting on the director's standing delegation of 15 Oct.\n")
    _write(repo, "C_bare.md", "The director would want C34 first.\n")
    verdicts = {i.path.name: i for i in ac.scan(repo)}
    assert verdicts["A_quoted.md"].attribution == "quoted"
    assert verdicts["B_delegated.md"].attribution == "delegation"
    assert not verdicts["C_bare.md"].drawable
    assert "no attribution" in verdicts["C_bare.md"].refusal


def test_a_file_without_the_staging_header_is_refused_with_that_reason(repo):
    (repo / ac.ADVISOR_DIR_REL / "X.md").write_text(
        '- 09:49 BST: "Is there a way to create a channel"\n', encoding="utf-8")
    (item,) = ac.scan(repo)
    assert item.refusal.startswith("no staging header")


def test_the_rung_names_the_drawn_file_and_the_refusal_and_draws_nothing_when_empty(repo):
    assert ac.rung_zero_text(repo, acknowledge=False) is None
    _write(repo, "A_quoted.md", '- 14:00 BST: "I can\'t paste, that\'s the whole issue!"\n')
    _write(repo, "C_bare.md", "Do C34 first.\n")
    text = ac.rung_zero_text(repo, acknowledge=False)
    assert text.startswith("ADVISOR CHANNEL (RUNG ZERO")
    first_line, refusal_line = text.splitlines()
    assert "A_quoted.md" in first_line and "C_bare.md" not in first_line
    assert "REFUSED" in refusal_line and "C_bare.md" in refusal_line and "no attribution" in refusal_line


def test_done_files_are_not_drawn_again(repo):
    done = repo / ac.ADVISOR_DIR_REL / ac.DONE_SUBDIR
    done.mkdir()
    (done / "A_quoted.md").write_text(HEADER + '- 09:49 BST: "an old actioned steer here"\n')
    assert ac.scan(repo) == []


def test_the_ack_is_sent_once_per_file_by_the_mechanism(repo, monkeypatch):
    sent = []
    monkeypatch.setattr("background.notify.notify",
                        lambda message, **kw: sent.append((message, kw["transition_key"])))
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a channel"\n')
    ac.rung_zero_text(repo)
    assert len(sent) == 1
    assert "A_quoted.md" in sent[0][0] and sent[0][1].endswith("A_quoted.md")


@pytest.fixture
def one_steer_in_the_channel(repo, monkeypatch):
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a separate channel"\n')
    monkeypatch.setattr(ac, "REPO_ROOT", repo)
    monkeypatch.setattr(ac, "_acknowledge", lambda item: None)
    return repo


def test_every_lane_reads_the_advisor_file_ahead_of_its_drawn_work(one_steer_in_the_channel,
                                                                   monkeypatch):
    """Drawn first, by each of the three lanes' own prompt builders: worker tick, executor, seat."""
    from background import delivery_lane, delivery_seat, seat_executor, worker_tick

    tick = worker_tick.compose_prompt("LANE 0 DELIVERY -- some drawn work")
    assert -1 < tick.find("ADVISOR CHANNEL (RUNG ZERO") < tick.find("LANE 0 DELIVERY")

    monkeypatch.setattr(delivery_lane, "doorbell", lambda item: "EXECUTOR ITEM")
    executor = seat_executor.build_prompt({})
    assert -1 < executor.find("ADVISOR CHANNEL (RUNG ZERO") < executor.find("EXECUTOR ITEM")

    seat = delivery_seat._prompt({})
    assert -1 < seat.find("ADVISOR CHANNEL (RUNG ZERO") < seat.find("THE LAST STRETCH OF COMMITS")


def test_an_empty_channel_adds_nothing_to_a_lanes_prompt(repo, monkeypatch):
    from background import worker_tick

    monkeypatch.setattr(ac, "REPO_ROOT", repo)
    assert "ADVISOR CHANNEL" not in worker_tick.compose_prompt("work")
