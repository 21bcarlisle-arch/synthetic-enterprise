"""How it's built writes its scale and its week into the HTML at publish (tools/harness_page_figures.py).

Director, 23 Oct 2026 07:18: "Make more appropriate for energy or tech person who is not familiar
with the detail". The defects these name: a highlight list that leaks the seat's orientation
entries or a run-on list of findings; a plain-English line its writer supplied being ignored; a
gate count typed by hand rather than read from the hooks; a figure with no store printed anyway.
"""
from __future__ import annotations

import json
import re
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
    # Proven able to fail is counted over the tests, so it stands without the July register,
    # and the register's figure is not borrowed when the feed lacks it.
    proven = [c for _, lab, c in figures if lab == "tests proven able to fail"]
    assert proven and "register" not in proven[0]
    kill = {"available": True, "controls_total": 35, "mutation_proven": 33,
            "last_verified": "2026-07-13"}
    figures, _, _ = hpf.scale_figures(ROOT, {"control_killlist": kill})
    # One live figure (director, 24 Oct item 6): the July register is not quoted beside it.
    assert not any("33 of 35" in c or "register" in c for _, _, c in figures)


def test_every_block_is_written_into_a_page_carrying_the_markers(tmp_path):
    page = tmp_path / "site" / "harness" / "index.html"
    page.parent.mkdir(parents=True)
    layers = "".join("<li>{}\nSTALE\n{}</li>\n".format(hpf.LAYER_START.format(n),
                                                       hpf.LAYER_END.format(n))
                     for n in hpf.LAYER_CODE)
    page.write_text("<p>top</p>\n{}{}\nSTALE\n{}\n<p>mid</p>\n{}\nSTALE\n{}\n".format(
        layers, hpf.SCALE_START, hpf.SCALE_END, hpf.WEEK_START, hpf.WEEK_END), encoding="utf-8")
    with page.open("a", encoding="utf-8") as f:
        for key in ("MEANING", "DOORS", "HUMAN", "CORRECTIONS", "ASKS", "LESSONS", "CHAINS"):
            f.write("{}\nSTALE\n{}\n".format(hpf.FOLLOW_START.format(key), hpf.FOLLOW_END.format(key)))
    # The page's root is three levels up, and git there is the real repository's when tmp is
    # not one, so make it a repository with one commit.
    _commit_all(tmp_path)
    assert hpf.write_harness_figures(page, tmp_path / "no_proof.json")
    out = page.read_text(encoding="utf-8")
    assert "STALE" not in out and "<p>top</p>" in out and "<p>mid</p>" in out
    assert "test files" in out and "Commits per week" in out
    assert "no highlight is shown" in out  # no stretch log in this tree: said, not blank
    assert out.count('<span class="ev">') == 8
    assert out.count('<ul class="fo">') == 2
    assert "could not be read at this publish" in out  # no canon, no direction file: said
    assert "ledger of director asks could not be built" in out  # no rulings file: said, not blank
    assert "no principle is shown" in out  # no canon: the lessons block says so, not blank
    assert "lessons could not be read" in out  # no bindings: the chains block says so, not blank


def test_a_page_without_the_markers_is_refused_and_left_alone(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<p>no markers</p>", encoding="utf-8")
    assert not hpf.write_harness_figures(page, tmp_path / "proof.json")
    assert page.read_text(encoding="utf-8") == "<p>no markers</p>"


def test_the_served_page_carries_every_marker_pair():
    page = (ROOT / "site" / "harness" / "index.html").read_text(encoding="utf-8")
    layers = [m.format(n) for n in hpf.LAYER_CODE for m in (hpf.LAYER_START, hpf.LAYER_END)]
    follow = [m.format(k) for k in ("MEANING", "DOORS", "HUMAN", "CORRECTIONS") for m in (hpf.FOLLOW_START, hpf.FOLLOW_END)]
    for marker in (hpf.SCALE_START, hpf.SCALE_END, hpf.WEEK_START, hpf.WEEK_END, *layers, *follow):
        assert page.count(marker) == 1, marker
    assert len(layers) == 16


def _jsonl_rows(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows) + "{torn\n", encoding="utf-8")


def test_every_layer_counts_its_own_store_inside_the_window_and_keeps_an_older_last(tmp_path):
    """One control over the eight boxes. Each store holds one row inside the thirty days and one
    from 2020: the count sees only the first, and a store whose only firing is old reports that
    day as its last. MUTATIONS: dropping the window counts 2 for the walls; reading the wrong
    outcome word counts the passes; dropping the MUTATION marker test counts 2 test files;
    keying the Director-doc read to the subject finds none; reading the raw text, not the code,
    for which module a test names credits layer 1 with a docstring -- each reds an assert below."""
    today = date.today().isoformat()
    obs = tmp_path / "obs"
    obs.mkdir()
    _jsonl_rows(obs / "lane_hook_denials.jsonl",
                [{"timestamp": today + "T01:00:00Z"}, {"timestamp": "2020-01-01T00:00:00Z"}])
    _jsonl_rows(obs / "commit_hook_duration.jsonl",
                [{"timestamp": today, "outcome": "refused"}, {"timestamp": today, "outcome": "pass"},
                 {"timestamp": today, "outcome": "pass"},
                 {"timestamp": "2020-01-01", "outcome": "refused"}])
    _jsonl_rows(obs / "publish_gate_duration.jsonl",
                [{"timestamp": today, "outcome": "pass"}, {"timestamp": "2020-02-03", "outcome": "fail"}])
    _jsonl_rows(obs / "blind_review_ledger.jsonl", [{"recorded_at": today}])
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_gate.py").write_text('"""MUTATION: drop it."""\nimport tools.world_claims\n')
    (tests / "test_plain.py").write_text('"""A mutation, lower case."""\nimport tools.world_claims\n')
    (tests / "test_says.py").write_text('"""MUTATION: names one_way_door in prose only."""\n')
    (tmp_path / "docs" / "market_research").mkdir(parents=True)
    (tmp_path / "docs" / "market_research" / "a.md").write_text("x")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", "fix a canon typo\n\nDirector-doc: correction -- x"],
                   check=True)
    got = {n: dict(rows) for n, rows in hpf.layer_evidence(tmp_path, obs).items()}
    assert sorted(got) == list(range(1, 9))
    fired = {n: next(v for k, v in rows.items() if k.endswith("30 days")) for n, rows in got.items()}
    assert fired[1].startswith("1 commits") and fired[2].startswith("1 sourced")
    assert fired[3].startswith("1 tool calls") and "last {}".format(hpf._day(today)) in fired[3]
    assert fired[4].startswith("1 of the publishing agent's 3 commit attempts")
    assert fired[5].startswith("2 of 3 test files") and "2 of them added" in fired[5]
    assert fired[6].startswith("1 blind reviews")
    assert fired[7].startswith("0 of 1 publish gate runs") and "last 3 Feb 2020" in fired[7]
    assert got[7]["Shown able to fail"].startswith("1 tests")
    assert "no test" in got[1]["Shown able to fail"]
    assert "Shown able to fail" not in got[5]  # the layer IS the count


def test_a_layer_whose_store_is_absent_says_not_measured_and_prints_no_number(tmp_path):
    _commit_all(tmp_path)
    got = hpf.layer_evidence(tmp_path, tmp_path / "no_such_dir")
    for n in (3, 4, 6, 7):
        text = got[n][0][1]
        assert text.startswith("not measured yet") and not re.search(r"\d", text), (n, text)


def test_the_publish_step_calls_the_writer():
    code = searchable((ROOT / "tools" / "generate_dashboard_data.py").read_text(encoding="utf-8"))
    assert "write_harness_figures(" in code


def _commit(root, path, day):
    f = root / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(path + day, encoding="utf-8")
    env = {"GIT_COMMITTER_DATE": day + "T12:00:00", "GIT_AUTHOR_DATE": day + "T12:00:00",
           "PATH": "/usr/bin:/bin"}
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit",
                    "-q", "-m", path], check=True, env=env)


def test_the_balance_counts_a_commit_as_product_only_when_it_changes_the_world_or_the_supplier(tmp_path):
    """One control over the partition: in one week a supplier commit, a world commit and a site
    commit, so the share must be strictly between nothing and everything (both branches taken),
    and exactly two thirds. A week entirely before the window is not counted, and the first week counted is a whole one, from its Monday. MUTATIONS: counting
    every commit as product gives 100%; matching `sim` without its slash counts `simple/` as the
    world; dropping the Monday alignment lets a partial first week in -- each reds an assert."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    _commit(tmp_path, "site/old.html", "2026-01-05")
    _commit(tmp_path, "site/tuesday.html", "2026-10-13")
    _commit(tmp_path, "company/billing/a.py", "2026-10-19")
    _commit(tmp_path, "simulation/b.py", "2026-10-20")
    _commit(tmp_path, "simple/c.py", "2026-10-21")
    weeks = hpf.product_share_by_week(tmp_path, weeks=2)
    assert weeks == [("2026-10-12", 0, 1), ("2026-10-19", 2, 3)], weeks
    p, n = weeks[1][1:]
    assert 0 < p < n


def test_the_follow_on_figures_name_an_absent_store_and_print_no_number_for_it(tmp_path):
    """The reviewers' ledger and the model-tier log live outside git; with neither present, their
    lines say not measured / not on this machine and carry no digit. The tier log's last entry,
    when it predates the window, is said as such rather than read as no sessions started.
    MUTATION: reading `recent` as zero sessions prints "0 sessions started" -- reds below."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    _commit(tmp_path, "company/a.py", date.today().isoformat())
    got = hpf.follow_on_figures(tmp_path, tmp_path / "no_such_dir")
    judges = dict(got["MEANING"])["Judging the judges"]
    assert judges.startswith("not measured yet") and not re.search(r"\d", judges)
    assert "not on this machine" in dict(got["DOORS"])["Effort and pace"]
    obs = tmp_path / "obs"
    obs.mkdir()
    _jsonl_rows(obs / "model_tier_log.jsonl",
                [{"ts": 1577880000.0, "outcome": "SPAWNED", "tier": "opus"}])
    pace = dict(hpf.follow_on_figures(tmp_path, obs)["DOORS"])["Effort and pace"]
    assert "last entry is 1 Jan 2020" in pace and "sessions started" not in pace


def test_every_stack_box_links_one_click_down_to_a_record_that_exists():
    """Each of the eight boxes carries one link down, to an anchor on this page or a page on the
    site, and every anchor it names exists. MUTATION: renaming `#checks` to `#check` reds."""
    page = (ROOT / "site" / "harness" / "index.html").read_text(encoding="utf-8")
    stack = page[page.index('<ol class="stack">'):page.index("</ol>", page.index('<ol class="stack">'))]
    hrefs = re.findall(r'<a class="down" href="([^"]+)"', stack)
    assert len(hrefs) == len(hpf.LAYER_CODE) == 8
    for href in hrefs:
        if href.startswith("#"):
            assert 'id="{}"'.format(href[1:]) in page, href
        else:
            assert (ROOT / "site" / "harness" / href / "index.html").resolve().exists(), href


_CANON = """# canon

**G5. Reserved actions: one list (ruled 12 Oct, decision 8).** It replaces the July seven:
- real money, never spent;
- destroying evidence.

Everything else: act, record how to reverse it, say what you did.

**G6. Next.**
"""


def test_the_human_section_quotes_g5_and_lists_what_waits_on_him_now(tmp_path):
    """Director, 24 Oct 07:28: the section gave the July seven and an 18 Sep "nothing waiting".

    One control over the partition: open rows are listed newest first, each with the first
    sentence of its recommendation; answered rows are not; with none open it says nothing waits;
    with no direction file it says it could not read one. MUTATIONS, run 24 Oct, all red: the
    status filter dropped (the answered row appears); the G5 pattern keyed to "G6" (the quote is
    replaced by the could-not-read line); the sort reversed (the order assert)."""
    (tmp_path / "docs" / "design").mkdir(parents=True)
    (tmp_path / "docs" / "direction").mkdir(parents=True)
    (tmp_path / "docs" / "design" / "DIRECTOR_CANON.md").write_text(_CANON, encoding="utf-8")
    rows = [
        {"id": "a", "raised": "2026-10-12", "status": "open", "what": "Old question. More.",
         "recommendation": "I recommend the old thing. Because."},
        {"id": "b", "raised": "2026-10-23", "status": "open", "what": "New question.",
         "recommendation": "I recommend the new thing. Because."},
        {"id": "c", "raised": "2026-10-20", "status": "answered", "what": "Done question.",
         "recommendation": "I recommend the answered thing."},
    ]
    import yaml
    direction = tmp_path / "docs" / "direction" / "DIRECTION.yaml"
    direction.write_text(yaml.safe_dump({"for_the_director": rows}), encoding="utf-8")
    _commit_all(tmp_path)
    out = hpf.reserved_and_waiting(tmp_path)
    assert "<li>real money, never spent;</li>" in out and "<li>destroying evidence.</li>" in out
    assert "act, record how to reverse it" in out
    assert "<b>2</b> questions wait on him" in out
    assert out.index("I recommend the new thing.") < out.index("I recommend the old thing.")
    assert "Because" not in out and "More." not in out
    assert "answered thing" not in out

    direction.write_text(yaml.safe_dump({"for_the_director": rows[2:]}), encoding="utf-8")
    _commit_all(tmp_path)
    assert "nothing is waiting on him" in hpf.reserved_and_waiting(tmp_path)


def test_the_served_page_presents_no_superseded_reserved_list():
    """The July seven was replaced by G5 on 12 Oct; the page must not present it as current."""
    page = (ROOT / "site" / "harness" / "index.html").read_text(encoding="utf-8")
    assert "Seven kinds of action" not in page
    assert "of those seven" not in page


def test_every_coupled_pair_has_a_plain_name_and_a_margin_renders_it():
    """Director, 24 Oct item 8: "W1_5_premise_demand_shape is 3.9% past the line" named nothing a
    reader knows. Every pair the record couples has a plain name, and the page's own margins
    renderer leads with it and keeps the id beside it. MUTATIONS, run 24 Oct, both red: a pair's
    entry deleted from PLAIN_PAIR_NAMES; the renderer reverted to `esc(m.world_atom)`."""
    import shutil

    import pytest

    from tools import generate_proof_data as gpd

    pairs = gpd._coupled_gaps(gpd._load_atoms()).get("pairs") or []
    assert pairs, "the coupled pairs could not be read"
    assert not [p["world_atom"] for p in pairs if not p.get("world_plain")]
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available to run the page's own script")
    harness = ROOT / "site" / "harness"
    proc = subprocess.run(
        [node, str(harness / "_render_harness.mjs"), str(harness / "index.html"), "renderGaps",
         "gap-note"],
        input=json.dumps({"coupled_gaps": {"available": True, "pair_count": 1, "measured": 1,
                                           "unmeasured": 0, "worse_than_blind_count": 1,
                                           "worse_than_blind_margins": [{
                                               "world_atom": "W1_5_premise_demand_shape",
                                               "world_plain": "how a home's demand moves",
                                               "percent_past_the_line": 3.9,
                                               "sample_size": None}]}}),
        capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
    out = json.loads(proc.stdout)["innerHTML"]
    assert "<b>how a home's demand moves</b>" in out or "<b>how a home&#39;s demand moves</b>" in out
    assert "<code>W1_5_premise_demand_shape</code>" in out


def test_corrections_come_from_the_log_newest_first_and_an_old_newest_says_so(tmp_path):
    """Director, 24 Oct item 3 and the rule against recurrence. One control: a dated line and an
    undated one (which takes its entry's date) are both read, newest first, and a duplicate is
    dropped; a log whose newest correction is over 30 days before the publish says so, and a
    fresh one does not. MUTATIONS, run 24 Oct, all red: the undated branch dropped; the sort
    reversed; the staleness bound removed (the fresh leg carries the note)."""
    log = tmp_path / "docs" / "status" / "SEAT_STRETCH_LOG.md"
    log.parent.mkdir(parents=True)
    log.write_text(
        "# log\n\n## 2026-10-24 \u2014 today\n\n"
        "**What we got wrong (2026-10-17):** The book was 1% dual fuel.\n"
        "**What we got wrong:** The page said DIFFER.\n\n"
        "## 2026-09-01 \u2014 older\n\n**What we got wrong:** An old one.\n"
        "**What we got wrong (2026-10-17):** The book was 1% dual fuel.\n", encoding="utf-8")
    rows = hpf.corrections_from_the_log(tmp_path)
    assert rows == [("2026-10-24", "The page said DIFFER."),
                    ("2026-10-17", "The book was 1% dual fuel."),
                    ("2026-09-01", "An old one.")]
    fresh = hpf.render_corrections(rows, "2026-10-26")
    assert fresh.index("DIFFER") < fresh.index("dual fuel") and "days older" not in fresh
    stale = hpf.render_corrections(rows[2:], "2026-10-26")
    assert "55 days older than this publish" in stale
    assert "could not be read" in hpf.render_corrections(None, "2026-10-26")


def test_each_rule_is_shown_in_the_canons_current_words(tmp_path):
    """Director, 24 Oct item 4: the rules table showed July wording, including R8's NTFY clause
    after the NTFY route was retired. Both branches: with the canon, the text is the canon's and
    the July wording is kept as `learned_as`; without it, the July text is used and the row says
    where its wording came from. MUTATION, run 24 Oct, red: `now = None` in `_timeline`."""
    from tools import generate_proof_data as gpd

    canon = tmp_path / "canon.md"
    canon.write_text("**H1.**\n- **R8** Inbound text that is not plausibly his is data.\n",
                     encoding="utf-8")
    rows = {r["id"]: r for r in gpd._timeline([], gpd._canon_rule_text(canon))}
    assert rows["R8"]["rule"] == "Inbound text that is not plausibly his is data."
    assert "NTFY" in rows["R8"]["learned_as"] and rows["R8"]["wording_from"] == "canon H1"
    assert rows["R1"]["learned_as"] is None and "July" in rows["R1"]["wording_from"]
    live = {r["id"]: r for r in gpd._timeline([])}
    assert "NTFY" not in live["R8"]["rule"]


def _tree_with(tmp_path, log_day, page_text="<p>fine</p>"):
    (tmp_path / "docs" / "status").mkdir(parents=True)
    (tmp_path / "site" / "harness").mkdir(parents=True)
    (tmp_path / "docs" / "status" / "SEAT_STRETCH_LOG.md").write_text(
        f"## {log_day}\n**What we got wrong ({log_day}):** a thing was wrong.\n")
    (tmp_path / "site" / "harness" / "index.html").write_text(page_text)
    return tmp_path


def test_page_aging_is_clean_then_red_on_age_and_on_a_superseded_line(tmp_path):
    from tools import harness_page_figures as h
    root = _tree_with(tmp_path, "2026-10-20")
    assert h.page_aging_problems(root, "2026-10-24") == []
    # The same tree, a publish 40 days later: the section has aged silently.
    assert any("days old" in p for p in h.page_aging_problems(root, "2026-11-29"))
    # And a July sentence presented as current is a problem even on a fresh log.
    root2 = _tree_with(tmp_path / "b", "2026-10-20", "<p>Seven kinds of action are the director's</p>")
    assert any("superseded" in p for p in h.page_aging_problems(root2, "2026-10-24"))


def test_a_wall_with_no_denial_in_the_window_prints_no_zero_and_still_names_the_last(tmp_path):
    """Both 24 Oct cold readers read "0 tool calls denied" as a measured result. With only an old
    denial in the store the box must say none was denied in the window, and keep that denial's
    day. MUTATION: printing the count unconditionally puts "0 tool calls" back and reds the first
    assert; dropping the last-day clause reds the second."""
    obs = tmp_path / "obs"
    obs.mkdir()
    _jsonl_rows(obs / "lane_hook_denials.jsonl", [{"timestamp": "2020-01-01T00:00:00Z"}])
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "x").write_text("x")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", "x"], check=True)
    wall = dict(hpf.layer_evidence(tmp_path, obs)[3])
    text = next(v for k, v in wall.items() if k.endswith("30 days"))
    assert not text[0].isdigit() and text.startswith("No tool call was denied")
    assert "1 Jan 2020" in text
