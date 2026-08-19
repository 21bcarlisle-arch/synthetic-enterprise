"""Tests for `tools/lab_query.py` — atom `G13_projection_consumers`.

The lab half of the proof-of-caller. Four properties, each proven BOTH WAYS per R15:

  1. every named question RUNS and its declared columns match its SQL
                                     → `test_every_named_question_answers`
  2. the joins are CORRECT, not merely plausible
                                     → `test_blocked_deps_uses_the_json_join_not_a_substring`
                                       mutant: the `LIKE` a reader would reach for first,
                                       shown returning a wrong row on a prefix id
  3. READ-ONLY, enforced twice       → `test_a_write_is_refused_by_the_statement_check`
                                       and `test_a_write_is_refused_by_the_driver_too`
                                     mutant: `test_r15_the_read_only_check_fires_...`
  4. FAIL-CLOSED, never an empty answer
                                     → `test_an_unreadable_source_fails_closed_not_empty`
                                       mutant: `test_r15_the_fail_closed_control_...`

Property 2 is the one worth the words. `depends_on` is a JSON array in a TEXT column, so the
obvious `depends_on LIKE '%X%'` reads as correct and is wrong for any atom id that is a
prefix of another — a defect that shows up as a plausible extra row, never as an error. The
test builds exactly that pair and asserts the two approaches DISAGREE.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.tools.test_build_projections import (  # noqa: E402
    _atoms_fixture,
    _commit_all,
    _gaps_fixture,
    _git,
    _probe_fixture,
    _runs_fixture,
    _write,
)
from tools import build_projections as bp  # noqa: E402
from tools import lab_query as lq  # noqa: E402


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "test")
    _write(root, "docs/design/maturity_map.yaml", _atoms_fixture())
    _write(root, "docs/observability/run_history.json", _runs_fixture())
    _write(root, "docs/observability/coupled_gap_ledger.json", _gaps_fixture())
    _write(root, bp.SCALE_PROBE_RELPATH, _probe_fixture())
    _commit_all(root, "fixtures")
    return root


# ------------------------------------------------- 1. every question answers


def test_every_named_question_answers(repo: Path):
    """Each question runs against a real store, and its declared column list matches the
    width of what its SQL actually returns. A column list that has drifted from the SQL
    mislabels every row it prints, silently."""
    for q in lq.QUESTIONS:
        answer = lq.ask(q.name, repo=repo)
        assert answer["question"] == q.question
        for row in answer["rows"]:
            assert len(row) == len(q.columns), f"{q.name}: {len(row)} values, {len(q.columns)} labels"


def test_the_answer_carries_the_commit_it_is_true_of(repo: Path):
    """R14: a figure without its clock is a defect. The lab's clock is the sha."""
    answer = lq.ask("wip", repo=repo)
    assert answer["store"]["head_sha"] == _git(repo, "rev-parse", "HEAD").strip()


def test_a_named_commit_is_a_different_question_honestly_labelled(repo: Path):
    """`--rev` is not a staleness bypass: the answer moves AND the stamp moves with it."""
    first = _git(repo, "rev-parse", "HEAD").strip()
    atoms = _atoms_fixture() + [dict(_atoms_fixture()[0], id="Z3_third", loop_stage="idle")]
    _write(repo, "docs/design/maturity_map.yaml", atoms)
    _commit_all(repo, "add an atom")

    now = lq.ask("wip", repo=repo)
    then = lq.ask("wip", repo=repo, rev=first)
    assert then["store"]["head_sha"] == first
    assert sum(r[1] for r in then["rows"]) < sum(r[1] for r in now["rows"])


# ------------------------------------------------- 2. the joins are correct


def test_blocked_deps_uses_the_json_join_not_a_substring(repo: Path):
    """MUTATION: the `LIKE` a reader would reach for first, on a prefix-id pair.

    `Z1_first` is a prefix of `Z1_first_extended`. An atom depending only on the LONGER id
    matches a substring search for the SHORTER one, so the naive query invents a dependency
    that does not exist. json_each does not.
    """
    atoms = [
        dict(_atoms_fixture()[0], id="Z1_first", level_current=1, loop_stage="harden",
             depends_on=[]),
        dict(_atoms_fixture()[0], id="Z1_first_extended", level_current=0, loop_stage="harden",
             depends_on=[]),
        dict(_atoms_fixture()[0], id="Z9_consumer", loop_stage="build",
             depends_on=["Z1_first_extended"]),
    ]
    _write(repo, "docs/design/maturity_map.yaml", atoms)
    _commit_all(repo, "prefix pair")

    correct = {(r[0], r[2]) for r in lq.ask("blocked-deps", repo=repo)["rows"]}
    assert correct == {("Z9_consumer", "Z1_first_extended")}

    naive_sql = (
        "SELECT a.id, d.id FROM atoms a JOIN atoms d "
        "ON a.depends_on LIKE '%' || d.id || '%' "
        "WHERE a.loop_stage = 'build' AND d.level_current < 2"
    )
    naive, _ = lq.run_sql(naive_sql, repo=repo)
    assert ("Z9_consumer", "Z1_first") in {tuple(r) for r in naive}, (
        "the fixture no longer exercises the prefix defect, so this control proves nothing"
    )
    assert {tuple(r) for r in naive} != correct


def test_shortfall_only_counts_atoms_that_are_actually_short(repo: Path):
    """A lane whose atoms are all at target must not appear at all — a zero row and an
    absent row read the same on a leaderboard, and only one of them is true."""
    atoms = [dict(_atoms_fixture()[0], id="Z1_done", lane="L_done",
                  level_current=2, level_target=2)]
    _write(repo, "docs/design/maturity_map.yaml", atoms)
    _commit_all(repo, "nothing short")
    assert lq.ask("shortfall", repo=repo)["rows"] == []


# ------------------------------------------------- 3. read-only, twice


@pytest.mark.parametrize("sql", [
    "INSERT INTO atoms VALUES ('x')",
    "UPDATE atoms SET lane = 'x'",
    "DELETE FROM atoms",
    "DROP TABLE atoms",
    "ATTACH DATABASE '/tmp/x.sqlite' AS x",
    "PRAGMA journal_mode = WAL",
    "SELECT 1; DROP TABLE atoms",
    "  \n SELECT 1 ;DELETE FROM atoms",
])
def test_a_write_is_refused_by_the_statement_check(sql: str):
    with pytest.raises(lq.NotReadOnly):
        lq.assert_read_only(sql)


@pytest.mark.parametrize("sql", [
    "SELECT 1",
    "select lane from atoms",
    "WITH x AS (SELECT 1) SELECT * FROM x",
    "SELECT 1;",
])
def test_a_genuine_read_is_allowed(sql: str):
    lq.assert_read_only(sql)


def test_a_write_is_refused_by_the_driver_too(repo: Path):
    """The statement check is the first lock, not the only one. Even a statement that got
    past it reaches a connection SQLite itself opened read-only."""
    lq.ask("wip", repo=repo)                       # build the store
    store = repo / bp.STORE_RELPATH
    conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("DELETE FROM atoms")
    finally:
        conn.close()


def test_r15_the_read_only_check_fires_on_its_own_named_defect():
    """MUTATION: the check reduced to a keyword blocklist, the shape that always looks
    sufficient and never is. `SELECT 1; DROP TABLE atoms` starts with SELECT and contains
    no blocked leading word, so a blocklist waves it through and the real check does not."""
    chained = "SELECT 1; DROP TABLE atoms"

    def _blocklist(sql: str) -> bool:
        first = sql.strip().split(None, 1)[0].upper()
        return first not in {"INSERT", "UPDATE", "DELETE", "DROP", "ATTACH", "PRAGMA"}

    assert _blocklist(chained), "the mutant must accept the chained statement"
    with pytest.raises(lq.NotReadOnly):
        lq.assert_read_only(chained)


# ------------------------------------------------- 4. fail-closed, never empty


def test_an_unreadable_source_fails_closed_not_empty(repo: Path):
    """An UNKNOWN source must raise, never come back as zero rows. Zero rows and "we could
    not read it" are the same pixel downstream, and only one of them is honest."""
    lq.ask("wip", repo=repo)
    (repo / "docs" / "observability" / "coupled_gap_ledger.json").write_text("{not json")
    _commit_all(repo, "break a source")

    with pytest.raises(bp.SourceUnreadable):
        lq.ask("gap", repo=repo)


def test_r15_the_fail_closed_control_fires_when_the_status_is_not_checked(repo: Path):
    """MUTATION: `run_sql` without its `status != ok` guard.

    The store is left untouched by a failed-closed build, so a lab that skips the check
    answers happily off the PREVIOUS build and reports nothing wrong. That is the stale
    answer this atom exists to prevent, and it is invisible without the guard.
    """
    lq.ask("gap", repo=repo)
    (repo / "docs" / "observability" / "coupled_gap_ledger.json").write_text("{not json")
    _commit_all(repo, "break a source")

    report = bp.build(repo=repo)
    assert report["status"] == "failed_closed"

    store = repo / bp.STORE_RELPATH
    conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        stale = list(conn.execute("SELECT COUNT(*) FROM coupled_gaps"))[0][0]
    finally:
        conn.close()
    assert stale > 0, "the mutant must be able to answer off the previous build"


def test_there_is_no_flag_that_skips_the_rebuild():
    """G12's own doctrine: a bypass door is the whole defect wearing a flag. If one is ever
    added, this reds — which is the point of asserting an ABSENCE."""
    parser_text = Path(lq.__file__).read_text()
    for door in ("--no-rebuild", "--stale", "--allow-stale", "--cached", "--allow-unknown"):
        assert f'"{door}"' not in parser_text, f"a rebuild bypass was added: {door}"


# ------------------------------------------------- the CLI


def test_the_cli_lists_and_answers(capsys, repo: Path, monkeypatch):
    monkeypatch.setattr(lq, "PROJECT", repo)
    assert lq.main(["--list"]) == 0
    listed = capsys.readouterr().out
    for q in lq.QUESTIONS:
        assert q.name in listed

    assert lq.main(["wip", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "wip" and payload["store"]["head_sha"]

    assert lq.main(["--sql", "DELETE FROM atoms"]) == 2
    assert "REFUSED" in capsys.readouterr().err

    assert lq.main(["no-such-question"]) == 2
