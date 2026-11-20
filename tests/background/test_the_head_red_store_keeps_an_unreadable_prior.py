"""An unreadable HEAD-red observation store is moved aside, not overwritten.

The defect this names: `load_observed` read a corrupt store as empty, the next `save_observed`
wrote over it, and every `runs_red` age (the doorbell's "longest-standing red has stood N runs")
restarted at 1 with the evidence destroyed. That is the self-clearing shape the alarm census
enumerates; `.head_red_observed.json` is dispositioned `real` against this file.
"""
from __future__ import annotations

from background import head_red_register as reg


def _partition(tmp_path):
    absent = tmp_path / "absent.json"
    readable = tmp_path / "readable.json"
    readable.write_text('{"runs": [], "tests": {"t::a": {"runs_red": 7}}}')
    unreadable = tmp_path / "unreadable.json"
    unreadable.write_text('{"runs": [], "tests": {"t::a": {"runs_red": 7')
    return absent, readable, unreadable


def test_every_prior_shape_is_reachable_and_only_unreadable_is_stamped(tmp_path):
    absent, readable, unreadable = _partition(tmp_path)
    outs = {p.name: reg.load_observed(p) for p in (absent, readable, unreadable)}
    assert "prior_unreadable" not in outs["absent.json"]
    assert outs["readable.json"]["tests"]["t::a"]["runs_red"] == 7
    assert "prior_unreadable" not in outs["readable.json"]
    assert outs["unreadable.json"]["prior_unreadable"]["preserved_as"]


def test_the_unreadable_bytes_survive_the_save_that_follows(tmp_path):
    _, _, unreadable = _partition(tmp_path)
    original = unreadable.read_bytes()
    store = reg.load_observed(unreadable)
    reg.save_observed(store, unreadable)
    kept = tmp_path / store["prior_unreadable"]["preserved_as"]
    assert kept.read_bytes() == original
    assert reg.load_observed(unreadable)["prior_unreadable"] == store["prior_unreadable"]


def test_a_non_mapping_store_is_unreadable_not_absent(tmp_path):
    p = tmp_path / "list.json"
    p.write_text("[1, 2, 3]")
    assert reg.load_observed(p)["prior_unreadable"]["preserved_as"]


def test_the_register_says_its_ages_were_lost(tmp_path):
    _, _, unreadable = _partition(tmp_path)
    store = reg.record(["t::a"], head_sha="abc", passed=1, store=reg.load_observed(unreadable))
    text = reg.render(store, [])
    assert "The observation store was unreadable at" in text
    assert store["prior_unreadable"]["preserved_as"] in text
