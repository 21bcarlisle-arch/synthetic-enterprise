"""The front door's proof strip is written from the run at publish (director steer, 22 Oct 2026).

Each test names the defect it exists to catch. The published page's own copy is checked in
`site/test_home_door.py::test_the_front_door_carries_its_figures_without_javascript`.
"""
from tools import generate_dashboard_data as g

PAGE = ("<html><body>\n" + g.PROOF_STRIP_START + "\nstale bytes\n" + g.PROOF_STRIP_END
        + "\n<p>after</p></body></html>")
SIM = {"total_records": 96, "period_from": "2016-01-01", "period_to": "2016-01-02",
       "crisis_years": ["2021", "2022"]}


def _run(active):
    return {"years": {"2016": {}, "2017": {"active_customer_ids": active}}}


def _dashboard(lifetime):
    return {"meta": {"generated_at": "2026-10-19T08:46:30Z", "source_file": "run_output_abc.json"},
            "financial": {"annual": [{"year": 2016}, {"year": 2017}]},
            "customers": {"lifetime": lifetime}}


LIFETIME = {"C1": {"segment": "resi"}, "C1g": {"segment": "resi"}, "C2": {"segment": "resi"},
            "C3": {"segment": "resi"}, "S1": {"segment": "SME"}}


def test_the_household_figure_moves_with_the_run_and_counts_a_dual_home_once():
    """Defect: a typed or account-counted figure. Two runs differing only in the final-year book
    must render different counts, and C1 + C1g is one household, not two."""
    figures, _ = g.proof_strip_figures(_run(["C1", "C1g", "C2", "S1"]), _dashboard(LIFETIME), SIM)
    assert ("2", "households on the book in 2017, the run's last year") == figures[2][:2]
    figures, _ = g.proof_strip_figures(_run(["C1", "C1g", "C2", "C3"]), _dashboard(LIFETIME), SIM)
    assert figures[2][0] == "3"


def test_every_source_present_shows_all_three_and_every_source_absent_names_each():
    """The partition, both legs: a renderer that always reports "missing" passes any test of the
    missing leg alone, and one that never does passes any test of the full leg alone."""
    full, missing = g.proof_strip_figures(_run(["C1"]), _dashboard(LIFETIME), SIM)
    assert len(full) == 3 and missing == []
    empty, missing = g.proof_strip_figures({}, _dashboard({}) | {"financial": {}}, {})
    assert empty == [] and len(missing) == 3


def test_the_rewrite_replaces_only_the_bytes_between_the_markers(tmp_path):
    page = tmp_path / "index.html"
    page.write_text(PAGE)
    assert g.write_front_door_proof_strip(_run(["C1"]), _dashboard(LIFETIME), page,
                                          tmp_path / "absent_sim_data.json")
    out = page.read_text()
    assert "stale bytes" not in out and out.endswith("<p>after</p></body></html>")
    assert out.count(g.PROOF_STRIP_START) == 1 and out.count(g.PROOF_STRIP_END) == 1
    # the unreadable source is said on the page, not filled in
    assert "half-hourly period count" in out and "(run abc;" in out
    # the front door's only clock (director, 22 Oct 2026): the run's date and the cadence
    assert "Figures from the run of 19 Oct 2026 &middot; published every Monday" in out


def test_a_page_without_the_markers_is_left_alone(tmp_path):
    """Defect: a front door whose markers were edited away gets the strip appended somewhere, or
    a redirected test output rewrites a page. Neither may write."""
    page = tmp_path / "index.html"
    page.write_text("<html>no markers</html>")
    assert not g.write_front_door_proof_strip(_run(["C1"]), _dashboard(LIFETIME), page,
                                              tmp_path / "sim.json")
    assert page.read_text() == "<html>no markers</html>"
    assert not g.write_front_door_proof_strip(_run(["C1"]), _dashboard(LIFETIME),
                                              tmp_path / "none.html", tmp_path / "sim.json")


def test_a_last_year_the_record_ends_inside_is_not_called_a_calendar_year():
    """Defect: "10 calendar years" over a price record that ends 7 Jun 2025 (cold reader,
    2026-10-22). Both legs: a record ending 31 Dec keeps the plain label."""
    part = dict(SIM, period_to="2017-06-07")
    figures, _ = g.proof_strip_figures(_run(["C1"]), _dashboard(LIFETIME), part)
    assert figures[1][1] == "2 years, lived in order; 2017 runs to 7 Jun 2017"
    whole = dict(SIM, period_to="2017-12-31")
    figures, _ = g.proof_strip_figures(_run(["C1"]), _dashboard(LIFETIME), whole)
    assert figures[1][1] == "2 calendar years, lived in order"


# ── THE BUILD STRIP: what has been built, counted from git at publish (director, 22 Oct 14:57) ──
def _repo(tmp_path, files):
    import subprocess
    root = tmp_path / "repo"
    for rel in files:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("a\nb\n")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"}
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "one"],
                ["commit", "-q", "--allow-empty", "-m", "two"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True, env=env)
    return root


def test_the_build_figures_are_counted_from_the_repository_and_name_what_they_count(tmp_path):
    """Defect: a typed or stale build figure. Two repositories that differ by one file must
    render different counts, and a test file is counted inside the Python files, not beside."""
    base = ["a.py", "tests/test_a.py", "site/knowledge/x/index.html", "site/knowledge/index.html",
            "docs/market_research/n.md"]
    figures, missing = g.build_scale_figures(_repo(tmp_path, base))
    assert missing == []
    assert [f[0] for f in figures] == ["2", "2", "1"], figures
    assert figures[1][2].startswith("1 of them test files; 4 lines in all; counted from git at ")
    assert "built from 1 sourced research notes" in figures[2][2]
    more, _ = g.build_scale_figures(_repo(tmp_path / "b", base + ["b.py"]))
    assert more[1][0] == "3"


def test_a_build_strip_with_no_readable_git_names_each_gap_and_shows_no_number(tmp_path):
    """The other leg of the partition: no repository means no figure, and the strip says why."""
    figures, missing = g.build_scale_figures(tmp_path / "not-a-repo")
    assert figures == [] and len(missing) == 2
    page = tmp_path / "site" / "index.html"
    page.parent.mkdir()
    page.write_text("x\n" + g.BUILD_STRIP_START + "\nstale\n" + g.BUILD_STRIP_END + "\ny")
    assert g.write_front_door_build_strip(page)
    out = page.read_text()
    assert "stale" not in out and "could not be read: the commit count" in out
