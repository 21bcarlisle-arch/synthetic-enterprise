"""Steer item 6's measure counts a search's result only if it came before the turn's first edit,
and counts it as answerable by the map only if the search named a register term.

Defects this names: counting searches after the edit (a turn's verification would read as
orientation the map saves), and counting every search as answerable (the saving would read as the
whole search spend, whatever the register covers). Mutation recorded: deleting `and not edited` in knowledge_plan.token_saving
reds the first assertion; replacing the term test with `True` reds the second.
"""
import json
from pathlib import Path

from tools import knowledge_plan as the_map_saving
from tools import the_map

ROOT = Path(__file__).resolve().parents[2]


def _session(path: Path, calls: list[tuple[str, dict, str]]) -> None:
    rows = []
    for i, (name, inp, result) in enumerate(calls):
        rows.append({"message": {"content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": inp}]}})
        rows.append({"message": {"content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": result}]}})
    path.write_text("\n".join(json.dumps(r) for r in rows))


def test_only_pre_edit_searches_count_and_only_register_terms_are_answerable(tmp_path):
    term = the_map._terms(the_map.load_register(ROOT)["concepts"][0])[0]
    _session(tmp_path / "s.jsonl", [
        ("Grep", {"pattern": term}, "a" * 100),
        ("Grep", {"pattern": "zzqx_nothing_registered"}, "b" * 40),
        ("Edit", {"file_path": "x"}, "ok"),
        ("Grep", {"pattern": term}, "c" * 1000),
    ])
    got = the_map_saving.token_saving(transcripts=tmp_path, root=ROOT, file_chars=30)
    assert got["search_chars_median"] == 140
    assert got["answerable_chars_mean"] == 100
    assert got["saving_chars_per_turn"] == 70
