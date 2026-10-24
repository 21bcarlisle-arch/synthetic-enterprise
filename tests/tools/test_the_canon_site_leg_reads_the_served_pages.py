"""The canon-against-site leg of `tools/canon_drift_check.py` (director's front-door steer,
2026-10-22, Checks: "no superseded line presented as current on any served page, and quoted canon
lines verbatim").

Each test names the defect it exists to catch. The first is the partition control: over the real
tree the leg must have pages AND quotes to read, and must be matching at least one quote on a page,
or every "holds" below is a leg that looked at nothing.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import canon_drift_check as C

REPO = Path(__file__).resolve().parents[2]
M1 = ("We are creating enterprise value by automating ways to find individual customers we can "
      "create value for, and sharing in that value — by saving them money, time and carbon, "
      "through personalised modelling, tariffs and advice.")


def _tree(tmp_path: Path, page: str, canon: str = f'**M1.** "{M1}" *(28 Aug)*\n') -> Path:
    (tmp_path / "site").mkdir()
    (tmp_path / "site" / "index.html").write_text(page, encoding="utf-8")
    (tmp_path / "docs" / "design").mkdir(parents=True)
    (tmp_path / C.CANON_DOC).write_text(canon, encoding="utf-8")
    return tmp_path


def test_the_real_site_holds_and_the_leg_is_reading_something():
    site = C.site_drift(REPO)
    assert site["pages"] > 10 and site["quotes"] > 10
    front = C.visible_text((REPO / "site" / "index.html").read_text(encoding="utf-8"))
    assert M1 in C.canon_quotes((REPO / C.CANON_DOC).read_text(encoding="utf-8"))
    assert M1 in front, "the front door must carry M1 verbatim (canon M11, decision 14)"
    assert site["superseded"] == [], site["superseded"]
    assert site["misquoted"] == [], site["misquoted"]
    # The 24 Oct steer: the picture carried the retired mission for weeks because this leg read only
    # HTML. The diagram must be among the pages read, and its M1 must be the canon's words.
    diagram = REPO / "site" / "assets" / "model-on-a-page.svg"
    assert diagram in C.served_pages(REPO)
    assert M1 in C.visible_text(diagram.read_text(encoding="utf-8"))


def test_the_diagrams_withdrawn_lines_are_caught_in_an_svg(tmp_path):
    """The lines the picture carried until 24 Oct, as SVG text nodes split across elements."""
    root = _tree(tmp_path, "<p>x</p>")
    (root / "site" / "d.svg").write_text(
        '<svg><text>Mission: cut carbon through personalisation — measured in '
        '<tspan>£ per tonne</tspan></text><text>£/tCO₂e on the front page — the headline</text>'
        '<text>— EV is fitness, mortality is selection.</text></svg>', encoding="utf-8")
    rows = C.site_drift(root)["superseded"]
    assert sorted(r["phrase"] for r in rows) == [
        "cut carbon through personalisation", "ev is fitness", "tco₂e on the front page"]
    assert {r["page"] for r in rows} == {"site/d.svg"}


def test_a_superseded_framing_presented_as_current_is_caught(tmp_path):
    root = _tree(tmp_path, "<h1>An energy company built to find the cheapest tonne of carbon</h1>")
    rows = C.site_drift(root)["superseded"]
    assert [r["phrase"] for r in rows] == ["cheapest tonne"]


def test_the_same_framing_in_a_comment_a_script_or_a_marked_history_is_not(tmp_path):
    """Item 1's sweep: the withdrawn headline survives only in an HTML comment explaining it."""
    root = _tree(tmp_path, (
        "<!-- the cheapest tonne framing was withdrawn -->"
        "<script>// cheapest tonne</script>"
        "<p data-canon-history>In July the headline read <q>the cheapest tonne</q>.</p>"
        "<p>Saved and could-save CO2.</p>"))
    assert C.site_drift(root)["superseded"] == []


def test_a_paraphrased_canon_quote_is_caught(tmp_path):
    drifted = M1.replace("money, time and carbon", "money and carbon")
    root = _tree(tmp_path, f"<p>&ldquo;{drifted}&rdquo;</p>")
    rows = C.site_drift(root)["misquoted"]
    assert len(rows) == 1 and rows[0]["canon"] == M1


def test_a_verbatim_quote_across_line_wraps_and_entities_holds(tmp_path):
    wrapped = M1.replace("—", "&mdash;").replace(" value ", "\n    value ")
    root = _tree(tmp_path, f"<p><strong>The mission:</strong> &ldquo;{wrapped}&rdquo;</p>")
    assert C.site_drift(root)["misquoted"] == []


def test_an_unreadable_or_empty_canon_fails_closed(tmp_path):
    root = _tree(tmp_path, "<p>x</p>", canon="no quotes here at all\n")
    with pytest.raises(C.ProbeError):
        C.site_drift(root)


def test_main_exits_1_when_a_served_page_drifts(tmp_path, monkeypatch):
    root = _tree(tmp_path, "<p>grown toward go-live</p>")
    monkeypatch.setattr(C, "run", lambda r, reg: ([], {"removed": [], "drift": []}))
    assert C.main(["--root", str(root), "--register", str(root / "r.yaml")]) == 1
