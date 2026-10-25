"""Capabilities writes its grid and go-live table into the HTML at publish (tools/capabilities_page_figures.py).

Director, 23 Oct 2026 07:18: "Make more appropriate for energy or tech person who is not familiar
with the detail"; the steer's item 3.1 asks for the grid "rendered static". The defects these name:
a branch of the column renderer never taken; a state or count on the page that the feed does not
carry; a writer that half-writes a page missing a marker; a publish step that stops calling it;
and the page's script drawing over the static blocks from a second renderer.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools import capabilities_page_figures as cpf
from tools.python_code_text import searchable

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "site" / "capabilities" / "index.html"
FEED = ROOT / "site" / "data" / "capabilities_door.json"


def _entry(name, status, checks=None, evidence=None):
    return {"name": name, "what": "does " + name, "status": status, "checks": checks,
            "evidence": evidence}


def test_every_branch_of_the_column_is_taken_and_counts_come_from_the_entries():
    """One control over the partition: a Live entry partly covered and linked, a Live entry fully
    covered, a Live entry with no checks, a Building and a Planned one. Each row is one line (a
    `<summary>`) with its evidence badge; the paragraph is one tap down. MUTATIONS: dropping the
    partial-coverage clause, the no-test badge, the evidence link, the Next heading, the summary
    wrapper, or counting a state by a literal -- each reds an assert below."""
    side = {"entries": [
        _entry("A<b>", "Live", {"checks": 5, "covered": 1, "of": 2}, "../knowledge/x/"),
        _entry("B", "Live", {"checks": 3, "covered": 2, "of": 2}),
        _entry("C", "Live"),
        _entry("D", "Building"),
        _entry("E", "Planned"),
    ]}
    out = cpf.render_side(side)
    assert "5 functions: 3 live &middot; 1 building &middot; 1 planned" in out
    assert "Now &middot; 3" in out and "Next &middot; 2" in out
    assert out.count("<summary") == 5 and out.count("</details>") == 5
    assert "5 tests · 1 of 2 parts tested" in out and ">3 tests<" in out
    assert "The tests cover 1 of the 2 pieces" in out and out.count("The tests cover") == 1
    assert out.count("no test cited") == 3
    assert out.count("see the record") == 1
    assert "A&lt;b&gt;" in out and "A<b>" not in out
    assert out.index(">D<") > out.index("Next") and out.index(">C<") < out.index("Next")
    # The badge is in the one line; the paragraph is not.
    first = out.split("<details")[1]
    assert "5 tests" in first.split("</summary>")[0] and "does A" in first.split("</summary>")[1]


def test_an_empty_side_says_zero_and_draws_no_heading():
    out = cpf.render_side({"entries": []})
    assert out.startswith('<p class="side-count">0 functions') and "col-h" not in out


def test_the_go_live_rows_carry_the_spec_reading_and_both_pills():
    feed = {"go_live": {"access_tally": {"OPEN": 2, "GATED": 1},
                        "seams": [{"area": "Meters", "counterparty": "DCC", "access": "GATED",
                                   "gate": "SEC accession", "spec": {"what": "DUIS read"},
                                   "status": "Planned"},
                                  {"area": "Prices", "counterparty": "Elexon", "access": "OPEN",
                                   "gate": "None", "spec": None, "status": "Live"}]}}
    blocks = cpf.render_blocks(feed)
    assert blocks["GOLIVE"].count("<tr>") == 2
    assert "spec-read" in blocks["GOLIVE"] and "spec-unread" in blocks["GOLIVE"]
    assert "pill-gated" in blocks["GOLIVE"] and "pill-live" in blocks["GOLIVE"]
    # A class the tally lacks is printed as 0, never skipped.
    assert [p.split("</div>")[0] for p in blocks["ACCESS"].split('fig-v">')[1:]] == ["2", "0", "1"]


def test_a_page_missing_a_marker_is_refused_and_left_alone(tmp_path):
    page = tmp_path / "index.html"
    partial = "".join("{}\nSTALE\n{}\n".format(cpf.START.format(n), cpf.END.format(n))
                      for n in cpf.BLOCKS[:-1])
    page.write_text(partial, encoding="utf-8")
    assert not cpf.write_capabilities_figures(page, FEED)
    assert page.read_text(encoding="utf-8") == partial


def test_every_block_is_written_and_nothing_stale_survives(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<p>top</p>\n" + "".join(
        "{}\nSTALE\n{}\n<p>between</p>\n".format(cpf.START.format(n), cpf.END.format(n))
        for n in cpf.BLOCKS), encoding="utf-8")
    assert cpf.write_capabilities_figures(page, FEED)
    out = page.read_text(encoding="utf-8")
    assert "STALE" not in out and out.count("<p>between</p>") == len(cpf.BLOCKS)
    assert "<p>top</p>" in out


def test_the_served_page_shows_what_the_committed_feed_says():
    """KEYED TO THE FEED, NOT TO TODAY'S ANSWER. No state or count is pinned here: the page's four
    blocks must be exactly what the committed feed renders to, so a state edited by hand on the
    page, or a feed published without its page, reds. The publisher commits both in one commit."""
    page = PAGE.read_text(encoding="utf-8")
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    for name, inner in cpf.render_blocks(feed).items():
        assert page.count(cpf.START.format(name)) == 1, name
        assert cpf.block(page, name) == inner, (
            "the {} block on the Capabilities page is not what site/data/capabilities_door.json "
            "renders to; run python3 -m tools.capabilities_page_figures".format(name))


def test_the_page_script_no_longer_draws_the_static_blocks():
    page = (ROOT / "site" / "capabilities" / "index.html").read_text(encoding="utf-8")
    scripts = "".join(part.split("</script>")[0] for part in page.split("<script>")[1:])
    for eid in ("world", "supplier", "access", "golive", "use-cases", "uc-tally"):
        assert 'getElementById("{}")'.format(eid) not in scripts, eid
    assert 'getElementById("stamp").innerHTML' not in scripts, "the stamp is written at publish"


def _fixed(*items):
    return {"fixed_this_week": {"window_days": 7, "as_of": "24 Oct 2026", "items": list(items)}}


def test_the_fixed_strip_takes_every_branch():
    """The dated strip under In brief (director, 24 Oct). One control over the partition: a fix the
    published run carries, one it does not yet, one with no run to ask, an empty window, and a feed
    from before the record existed. MUTATION: render every fix as "in the published figures" -> the
    second assert reds; drop the empty-window sentence -> the fourth reds."""
    one = {"commit": "a" * 40, "what": "Bills <fixed>", "date": "Sat 24 Oct"}
    out = cpf.render_fixed(_fixed(dict(one, in_published_run=True),
                                  dict(one, in_published_run=False),
                                  dict(one, in_published_run=None)))
    assert out.count("<li>") == 3 and "Bills &lt;fixed&gt;" in out
    assert out.count("in the published figures") == 1
    assert out.count("reaches the figures at the next published run") == 1
    assert "Nothing recorded" in cpf.render_fixed(_fixed())
    assert cpf.render_fixed({}) == ""


def test_the_register_is_collapsed_with_its_three_counts_outside():
    """24 Oct: the register goes "below the fold as one collapsed section ... Keep its three headline
    counts visible". MUTATION: move the tally inside the details, or open it by default -> reds."""
    page = (ROOT / "site" / "capabilities" / "index.html").read_text(encoding="utf-8")
    opens = page.index('<details class="more register" id="use-cases">')
    assert page.index('id="uc-tally"') < opens
    assert "open" not in page[opens:page.index(">", opens)].replace('id="use-cases"', "")
    assert cpf.block(page, "USECASES").startswith("<summary>What this world is for: ")


def test_the_stamp_is_in_the_footer():
    page = (ROOT / "site" / "capabilities" / "index.html").read_text(encoding="utf-8")
    foot = page[page.index("<footer>"):page.index("</footer>")]
    assert cpf.START.format("STAMP") in foot and 'id="stamp"' in cpf.block(page, "STAMP")


def test_the_publish_step_calls_the_writer_after_the_feed_is_published():
    code = searchable((ROOT / "background" / "process_run_complete.py").read_text(encoding="utf-8"))
    publish, write = code.find("publish_clean()"), code.find("write_capabilities_figures(")
    assert 0 < publish < write
