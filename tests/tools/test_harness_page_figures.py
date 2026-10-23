"""How it's built writes its scale and its week into the HTML at publish (tools/harness_page_figures.py).

Director, 23 Oct 2026 07:18: "Make more appropriate for energy or tech person who is not familiar
with the detail". The defects these name: a highlight list that leaks the seat's orientation
entries or a run-on list of findings; a plain-English line its writer supplied being ignored; a
gate count typed by hand rather than read from the hooks; a figure with no store printed anyway.
"""
from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

from tools import harness_page_figures as hpf
from tools.python_code_text import searchable

ROOT = Path(__file__).resolve().parents[2]

_LOG = """# log

## 2026-10-22 — orientation: Sideways for the thesis

## 2026-10-22 — The code galaxy gets its own tab; detail after the semicolon

## 2026-10-21 — Founder households: a run-on title that lists one finding after another and goes on past any line a newcomer reads

## 2026-10-21 — An entry whose title is internal; the writer gave a plain line

**In plain English:** The supplier now bills dual-fuel homes on one account.

## 2026-10-20 — The code galaxy, a second entry on the same subject

## 2026-10-10 — Out of the window
"""


def _tree(tmp_path, log=_LOG):
    (tmp_path / "docs" / "status").mkdir(parents=True)
    (tmp_path / "docs" / "status" / "SEAT_STRETCH_LOG.md").write_text(log, encoding="utf-8")
    return tmp_path


def test_every_branch_of_the_highlight_filter_is_taken_and_each_does_its_job(tmp_path):
    """One control over the whole partition: something is shown, and every excluding branch
    excluded something. MUTATIONS: dropping the orientation skip shows "Orientation"; dropping
    the plain-line read shows the internal title; dropping the length bound shows "Founder
    households"; dropping the subject de-dup shows the galaxy twice; dropping the window shows
    "Out of the window" -- each reds the matching assert below."""
    got = hpf.week_highlights(_tree(tmp_path), today=date(2026, 10, 23))
    lines = [t for _, t in got]
    assert lines == ["The code galaxy gets its own tab",
                     "The supplier now bills dual-fuel homes on one account."], lines
    joined = " ".join(lines)
    for excluded in ("Orientation", "Founder households", "internal", "Out of the window",
                     "second entry"):
        assert excluded not in joined, excluded


def test_no_work_entry_in_the_window_says_so_rather_than_an_empty_list(tmp_path):
    root = _tree(tmp_path, "## 2026-09-01 — Long ago\n")
    assert hpf.week_highlights(root, today=date(2026, 10, 23)) == []
    assert hpf.week_highlights(tmp_path / "absent", today=date(2026, 10, 23)) is None


def _commit_all(tree):
    subprocess.run(["git", "init", "-q", str(tree)], check=True)
    subprocess.run(["git", "-C", str(tree), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tree), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "--allow-empty", "-m", "x"], check=True)


def test_the_gate_count_is_read_from_the_hook_files_as_committed(tmp_path):
    hooks = tmp_path / "tools" / "git-hooks"
    hooks.mkdir(parents=True)
    (hooks / "pre-commit").write_text(
        "python3 -m tools.live_hook_drift || true\npython3 tools/a.py || exit 1\n"
        "python3 -m b --gate || exit 1\npython3 -m c || {\n# python3 d.py || exit 1\n")
    (hooks / "commit-msg").write_text("python3 tools/e.py \"$1\" || exit 1\n"
                                      "python3 -m tools.hook_gate_mark --stamp \"$1\"\n")
    _commit_all(tmp_path)
    assert hpf.count_hook_gates(tmp_path) == {"pre-commit": 3, "commit-msg": 1}
    assert hpf.count_hook_gates(tmp_path / "absent") is None


def test_the_real_hooks_count_is_the_number_of_refusing_lines_not_a_literal():
    """Keyed to the property: the count equals what the hook files hold today, whatever it is."""
    got = hpf.count_hook_gates(ROOT)
    for name in ("pre-commit", "commit-msg"):
        text = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:tools/git-hooks/" + name],
                              capture_output=True, text=True, check=True).stdout
        assert got[name] == text.count("|| exit 1") + text.count("|| {") - sum(
            1 for ln in text.splitlines() if ln.lstrip().startswith("#") and "|| exit 1" in ln)


def test_a_figure_with_no_store_is_named_as_not_measured_and_never_printed():
    figures, _, missing = hpf.scale_figures(ROOT, {})
    assert any("first time" in m and "not measured yet" in m for m in missing)
    assert not any("first time" in lab for _, lab, _ in figures)
    # No control register in the feed: that figure is left out with its reason, not zeroed.
    assert any("control register could not be read" in m for m in missing)


def test_both_blocks_are_written_into_a_page_carrying_the_markers(tmp_path):
    page = tmp_path / "site" / "harness" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text("<p>top</p>\n{}\nSTALE\n{}\n<p>mid</p>\n{}\nSTALE\n{}\n".format(
        hpf.SCALE_START, hpf.SCALE_END, hpf.WEEK_START, hpf.WEEK_END), encoding="utf-8")
    # The page's root is three levels up, and git there is the real repository's when tmp is
    # not one, so make it a repository with one commit.
    _commit_all(tmp_path)
    assert hpf.write_harness_figures(page, tmp_path / "no_proof.json")
    out = page.read_text(encoding="utf-8")
    assert "STALE" not in out and "<p>top</p>" in out and "<p>mid</p>" in out
    assert "test files" in out and "Commits per week" in out
    assert "no highlight is shown" in out  # no stretch log in this tree: said, not blank


def test_a_page_without_the_markers_is_refused_and_left_alone(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<p>no markers</p>", encoding="utf-8")
    assert not hpf.write_harness_figures(page, tmp_path / "proof.json")
    assert page.read_text(encoding="utf-8") == "<p>no markers</p>"


def test_the_served_page_carries_both_marker_pairs():
    page = (ROOT / "site" / "harness" / "index.html").read_text(encoding="utf-8")
    for marker in (hpf.SCALE_START, hpf.SCALE_END, hpf.WEEK_START, hpf.WEEK_END):
        assert page.count(marker) == 1, marker


def test_the_publish_step_calls_the_writer():
    code = searchable((ROOT / "tools" / "generate_dashboard_data.py").read_text(encoding="utf-8"))
    assert "write_harness_figures(" in code
