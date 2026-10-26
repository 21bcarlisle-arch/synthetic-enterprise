"""A page the publisher rendered this cycle is declared its own to the stale-copy guard (2026-10-26).

The defect: the third Monday attempt at run 4ae8da9b0f was refused `predates_landing` on 19 site
pages. Each page's last landing had changed a run-stamped line ("Published with the run of 19 Oct
2026", the explore cast drawn from that run), and the fresh render, carrying that landing's wording,
says 26 Oct. A run-stamped line never survives the next run's render, so rule 1 refused the publish.

MUTATIONS: flip `>=` to `<` in `_pages_rendered_this_cycle`, and both partition assertions go red.
Drop the `retire["drops"] = ...` line in `_land_publish_commit`, and the wiring assertion goes red.
"""
import os

from background import process_run_complete as prc


def _page(root, name, mtime):
    path = root / "pages" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<p>run</p>\n")
    os.utime(path, (mtime, mtime))
    return "pages/" + name


def test_only_pages_this_cycle_rewrote_are_declared_and_an_older_copy_is_still_judged(tmp_path):
    started = 1_000_000.0
    fresh = _page(tmp_path, "fresh.html", started + 5)
    older = _page(tmp_path, "older.html", started - 5)
    feed = _page(tmp_path, "feed.json", started + 5)

    declared = prc._pages_rendered_this_cycle([fresh, older, feed, "pages/gone.html"], tmp_path,
                                              started=started)

    # BOTH PARTITIONS, in one control: an exemption that declares everything passes a test that
    # only asks for the fresh page, and one that declares nothing passes a test that only asks for
    # the older one.
    assert fresh in declared and older not in declared, declared
    assert feed not in declared, "`.json` is clock_judge's, and this exemption is for pages only"


def test_the_declared_pages_reach_the_landing_as_drops(tmp_path, monkeypatch):
    from tools import surgical_land

    rel = _page(tmp_path, "fresh.html", 2_000_000.0)
    seen = {}

    def fake_land(root, paths, message, attempts=None, on_lost=None, **kw):
        seen.update(kw)
        return "f" * 40

    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "_PROCESS_STARTED_WALL", 1_000_000.0)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_wait_for_a_quiet_tree", lambda *a, **k: {"waited_seconds": 0})
    monkeypatch.setattr(prc, "_advance_to_origin_or_say_why",
                        lambda *a, **k: {"advanced": True, "reason": "ff"})
    monkeypatch.setattr(surgical_land, "land", fake_land)

    out = prc._land_publish_commit([str(tmp_path / rel)], "msg", "abc1234")

    assert out["sha"] == "f" * 40, out
    assert rel in seen.get("drops", frozenset()), seen
