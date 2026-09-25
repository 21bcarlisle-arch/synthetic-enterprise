"""R15 proof for AO2, the write-time reuse gate (`tools/write_time_gate.py`).

Two things have to be true for this gate to be worth having, and each is tested here rather than
asserted:

  1. **Every guard FIRES on its own named defect.** Proven by SOURCE MUTATION -- `test_mutations`
     below breaks one guard at a time in a copy of the real module and requires the matching
     assertion to go green-when-it-should-be-red. A guard that no mutation can break is decoration
     (and this project has found tautologies living INSIDE its own R15 tests before, which is why
     the mutations edit the source rather than a fixture).
  2. **The gate never compels the reuse DECISION** -- the director's wall. `test_the_wall_holds`
     commits a record that says "I found an existing module and wrote a new one anyway" and
     requires it to PASS. If that ever fails, the gate has become the mirror defect it exists to
     avoid, and no amount of the rest passing makes up for it.

Plus a VACUITY guard: the fail-open shape here is a gate whose detector never fires, so the whole
suite passes while no commit is ever actually checked. `test_detection_is_not_vacuous` fails if the
fixtures stop producing owed records.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import write_time_gate as g  # noqa: E402

SOURCE = ROOT / "tools" / "write_time_gate.py"

NEW_MODULE = "company/billing/late_payment_charge.py"


def rows(*specs: tuple[str, str]) -> list[dict]:
    """Index-shaped rows: (module, search text). Matches what capability_index.build_rows emits,
    since `find` is reused verbatim and must be fed the shape it really consumes."""
    return [{"module": m, "path": m.replace(".", "/") + ".py", "callers": [],
             "search_blob": blob.lower(), "status": "wired"} for m, blob in specs]


def record(**fields: str) -> str:
    """A commit message carrying one REUSE block for NEW_MODULE, with `fields` as its lines."""
    body = "".join(f"{k.upper()}: {v}\n" for k, v in fields.items())
    return f"AO-something: add the charge calculator\n\nREUSE: {NEW_MODULE}\n{body}"


GOOD = dict(CLASS="CUSTOM", INDEX='searched "late payment", "charge" -- nearest is '
                                  "company.billing.dunning, which schedules but never prices")


# ── what owes a record ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("path,owed", [
    ("company/billing/late_payment_charge.py", True),
    ("tools/some_new_tool.py", True),
    ("sim/weather/new_source.py", True),
    ("tests/tools/test_new_tool.py", False),          # a test is evidence, not a capability
    ("company/billing/test_helper.py", False),
    ("company/billing/__init__.py", False),           # packaging
    ("docs/design/NEW.md", False),
    ("site/pages/new.js", False),
    ("scratch/experiment.py", False),                 # outside the declared code roots
])
def test_owes_a_record(path: str, owed: bool) -> None:
    assert (g.owes_a_record([path]) == [path]) is owed


def test_modified_files_owe_nothing() -> None:
    """Only ADDED paths reach the gate -- an edit to an existing module is not a new capability.
    (Enforced by --diff-filter=A at the git seam; this pins the intent alongside it.)"""
    assert g.owes_a_record([]) == []


# ── parsing ─────────────────────────────────────────────────────────────────────────────────
def test_parse_handles_wrapped_lines_and_multiple_blocks() -> None:
    msg = ("header\n\n"
           "REUSE: a/b.py\nCLASS: CUSTOM\nINDEX: searched \"one\"\n    and it wrapped onto here\n"
           "REUSE: c/d.py\nclass: SUBSYSTEM\nEVALUATED: beancount\nREJECTED: no GB settlement\n")
    parsed = g.parse_records(msg)
    assert set(parsed) == {"a/b.py", "c/d.py"}
    assert parsed["a/b.py"]["INDEX"].endswith("and it wrapped onto here")
    assert parsed["c/d.py"]["CLASS"] == "SUBSYSTEM"        # field heads are case-insensitive
    assert parsed["c/d.py"]["REJECTED"] == "no GB settlement"


def test_index_terms_and_nothing_claim() -> None:
    assert g.index_terms({"INDEX": 'searched "late payment", "dunning"'}) == ["late payment",
                                                                             "dunning"]
    assert g.claims_nothing_exists({"INDEX": 'searched "x" -- no existing row covers this'})
    assert not g.claims_nothing_exists({"INDEX": 'searched "x" -- nearest company.billing.dunning'})


# ── the guards, each on its own defect ──────────────────────────────────────────────────────
def _findings(message: str, index_rows: list[dict] | None = None) -> str:
    r = g.evaluate([NEW_MODULE], message, index_rows or [])
    return " ".join(r["findings"])


def test_g1_missing_record_refuses() -> None:
    r = g.evaluate([NEW_MODULE], "AO-something: add the charge calculator\n", [])
    assert r["status"] == "REJECT" and "G1" in r["findings"][0]
    assert "--explain" in r["findings"][0]      # the refusal carries its own remedy


def test_g2_absent_or_unknown_class_refuses() -> None:
    assert "G2" in _findings(record(INDEX=GOOD["INDEX"]))
    assert "G2" in _findings(record(CLASS="WHATEVER", INDEX=GOOD["INDEX"]))


def test_g3_catalogue_without_library_refuses() -> None:
    """The director's named evidence class: a catalogue part hand-rolled while a library exists."""
    assert "G3" in _findings(record(CLASS="CATALOGUE", INDEX=GOOD["INDEX"]))
    assert "G3" not in _findings(record(CLASS="CATALOGUE", INDEX=GOOD["INDEX"],
                                        LIBRARY="holidays (pinned) -- thin wrapper"))


def test_g4_subsystem_without_build_vs_buy_refuses() -> None:
    """Silence is a gap: BOTH halves of the note are owed, and each is missed on its own."""
    both = _findings(record(CLASS="SUBSYSTEM", INDEX=GOOD["INDEX"]))
    assert "G4" in both and "EVALUATED" in both and "REJECTED" in both
    only_evaluated = _findings(record(CLASS="SUBSYSTEM", INDEX=GOOD["INDEX"],
                                      EVALUATED="beancount"))
    assert "G4" in only_evaluated and "REJECTED" in only_evaluated
    complete = _findings(record(CLASS="SUBSYSTEM", INDEX=GOOD["INDEX"], EVALUATED="beancount",
                                REJECTED="assumes a file-backed journal"))
    assert "G4" not in complete


def test_g5_index_line_without_quoted_terms_refuses() -> None:
    assert "G5" in _findings(record(CLASS="CUSTOM", INDEX="I had a look and there was nothing"))
    assert "G5" in _findings(record(CLASS="CUSTOM"))


def test_g6_contradicted_by_the_live_index() -> None:
    """The one guard with an INDEPENDENT source: the record claims emptiness, the index answers."""
    msg = record(CLASS="CUSTOM", INDEX='searched "late payment" -- no existing row covers this')
    idx = rows(("company.billing.dunning", "late payment chasing and dunning ladder"))
    out = _findings(msg, idx)
    assert "G6" in out and "company.billing.dunning" in out
    assert g.evaluate([NEW_MODULE], msg, [])["status"] == "OK"   # empty index -> no contradiction


def test_g6_does_not_fire_when_the_record_is_honest() -> None:
    """Found something, wrote fresh anyway, said so -- the gate has no opinion about that."""
    msg = record(CLASS="CUSTOM",
                 INDEX='searched "late payment" -- nearest company.billing.dunning, which '
                       "schedules chasing but never prices a charge")
    idx = rows(("company.billing.dunning", "late payment chasing and dunning ladder"))
    assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "OK"


# ── G6 is about DISCLOSURE, not phrasing (2026-08-09 finding, part 2) ───────────────────────
# Two honest records were really refused for a bare quantifier: one naming three neighbours and
# saying "each considered, none extended", one naming its three matches and saying "nothing else
# composes this". Both are the MOST informative form of the record. The wall to keep while fixing
# it: G6 is the only guard with an INDEPENDENT source (R15), so it must still fire on a record
# that discloses nothing -- `test_g6_contradicted_by_the_live_index` above is that direction, and
# the mutation table below re-proves it after every edit.

def test_g6_accepts_a_record_that_names_its_matches_then_says_none_extended() -> None:
    """Instance 1: neighbours named by dotted module, a nothing-word about the REMAINDER."""
    msg = record(CLASS="CUSTOM",
                 INDEX='searched "late payment", "arrears" -- company.billing.dunning and '
                       "company.billing.arrears_ageing both looked, each considered, none "
                       "extended: neither prices a charge")
    idx = rows(("company.billing.dunning", "late payment chasing and dunning ladder"),
               ("company.billing.arrears_ageing", "arrears ageing buckets"))
    assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "OK"


def test_g6_accepts_a_record_naming_matches_by_bare_module_name() -> None:
    """Instance 2's shape: the matches named, then 'nothing else composes this'."""
    msg = record(CLASS="CUSTOM",
                 INDEX='searched "late payment", "charge" -- the only rows returned are dunning '
                       "and arrears_ageing themselves; nothing else in the index composes "
                       "a per-account late charge")
    idx = rows(("company.billing.dunning", "late payment chasing"),
               ("company.billing.arrears_ageing", "arrears ageing charge buckets"))
    assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "OK"


def test_g6_still_fires_when_only_the_searched_term_resembles_the_match() -> None:
    """The false-negative this fix could have bought: searching "dunning" is not disclosing
    `company.billing.dunning`. The quoted terms are subtracted before looking for names."""
    msg = record(CLASS="CUSTOM", INDEX='searched "dunning" -- no existing row covers this')
    idx = rows(("company.billing.dunning", "late payment chasing and dunning ladder"))
    out = g.evaluate([NEW_MODULE], msg, idx)
    assert out["status"] == "REJECT" and "G6" in " ".join(out["findings"])


def test_g6_does_not_count_the_records_own_subject_as_a_contradiction() -> None:
    """A row for the module being added is the file in the commit, not prior art. This is what
    really refused the three composition roots: they were on disk, so the index returned them."""
    msg = record(CLASS="CUSTOM",
                 INDEX='searched "late payment charge" -- no other row covers this')
    idx = rows((NEW_MODULE[:-3].replace("/", "."), "late payment charge calculator"))
    assert idx[0]["path"] == NEW_MODULE, "fixture must model the subject's OWN row"
    assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "OK"
    # ...and a sibling row that is NOT the subject still contradicts
    idx.append(rows(("company.billing.dunning", "late payment charge chasing"))[0])
    assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "REJECT"


def test_names_a_match_is_not_satisfied_by_a_short_or_glued_token() -> None:
    """Unit-level guard on the naming test itself: no 3-letter tails, no substring hits."""
    assert not g.names_a_match({"INDEX": "vat handling elsewhere"}, ["company.tax.vat"])
    assert not g.names_a_match({"INDEX": "see redunningx notes"}, ["company.billing.dunning"])
    assert g.names_a_match({"INDEX": "nearest is dunning, which chases"},
                           ["company.billing.dunning"])


def test_the_wall_holds() -> None:
    """THE WALL (director): the gate compels the look and the record, NEVER the reuse decision.

    Same new module, same index showing a near-neighbour, two records -- one saying 'extended it',
    one saying 'wrote a new one'. Both must pass. If this test ever fails, the gate has started
    deciding, and forced reuse that couples two purposes is as much a defect as duplication."""
    idx = rows(("company.billing.dunning", "late payment chasing and dunning ladder"))
    reused = record(CLASS="CUSTOM", INDEX='searched "late payment" -- extending '
                                          "company.billing.dunning rather than adding a module")
    wrote_fresh = record(CLASS="CUSTOM", INDEX='searched "late payment" -- company.billing.dunning '
                                               "exists; kept separate, chasing and pricing are "
                                               "different purposes")
    for msg in (reused, wrote_fresh):
        assert g.evaluate([NEW_MODULE], msg, idx)["status"] == "OK"


def test_clean_record_passes() -> None:
    assert g.evaluate([NEW_MODULE], record(**GOOD), [])["status"] == "OK"


# ── vacuity: the fail-open shape that would make all of the above theatre ────────────────────
def test_detection_is_not_vacuous() -> None:
    """A gate whose detector never fires passes every test while checking nothing. This fails if
    the fixtures stop being seen as owed, or if a clean commit stops being distinguishable from
    an unchecked one."""
    assert g.evaluate([NEW_MODULE], record(**GOOD), [])["owed"] == [NEW_MODULE]
    assert g.evaluate(["docs/design/X.md"], "no record here", [])["owed"] == []
    assert g.evaluate([NEW_MODULE], "no record here", [])["status"] == "REJECT"


def test_a_commit_with_no_new_module_is_never_touched() -> None:
    """Only ADDED paths reach evaluate() (--diff-filter=A), so a commit that adds a report and
    edits ten modules arrives here as a list with no new capability in it, and pays nothing."""
    r = g.evaluate(["docs/status/LATEST.md", "docs/observability/run_history.json"], "", [])
    assert r == {"status": "OK", "findings": [], "owed": []}


# ── mode file: fail-closed in every unreadable direction ────────────────────────────────────
def test_mode_defaults_to_gate_when_absent(tmp_path: Path) -> None:
    assert g.read_mode(tmp_path / "nope.mode") == "gate"


def test_mode_warn_is_honoured(tmp_path: Path) -> None:
    p = tmp_path / "m.mode"
    p.write_text("warn\n")
    assert g.read_mode(p) == "warn"


def test_unknown_mode_word_raises_rather_than_passing(tmp_path: Path) -> None:
    p = tmp_path / "m.mode"
    p.write_text("off\n")
    with pytest.raises(ValueError):
        g.read_mode(p)


def test_refuse_blocks_in_gate_and_reports_in_warn(capsys: pytest.CaptureFixture) -> None:
    assert g._refuse(["x: G1 nothing"], "gate") == 1
    gate_text = capsys.readouterr().err
    assert g._refuse(["x: G1 nothing"], "warn") == 0
    warn_text = capsys.readouterr().err
    assert "G1 nothing" in gate_text and "G1 nothing" in warn_text   # warn is not quieter


def test_the_live_mode_file_is_gate_or_absent() -> None:
    """§5 rules this the immediate behaviour change, so it must not land de-fanged."""
    assert g.read_mode() == "gate"


# ── fail-closed at the seams ────────────────────────────────────────────────────────────────
def test_unreadable_message_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "staged_additions", lambda: [NEW_MODULE])
    assert g.main([str(tmp_path / "absent-message")]) == 1


def test_unavailable_index_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An unavailable check is a FAILED check -- G6 cannot be evaluated, so nothing clears."""
    msg = tmp_path / "msg"
    msg.write_text(record(**GOOD))
    monkeypatch.setattr(g, "staged_additions", lambda: [NEW_MODULE])
    monkeypatch.setattr(g, "build_rows", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no")))
    assert g.main([str(msg)]) == 1


def test_git_failure_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "staged_additions",
                        lambda: (_ for _ in ()).throw(RuntimeError("git exploded")))
    assert g.main(["irrelevant"]) == 1


def test_ordinary_commit_pays_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """No new module -> exit 0 without reading the message, the mode or the index at all."""
    monkeypatch.setattr(g, "staged_additions", lambda: ["docs/status/LATEST.md"])
    monkeypatch.setattr(g, "build_rows", lambda *a, **k: pytest.fail("index must not be built"))
    assert g.main(["/nonexistent/message"]) == 0


def test_explain_prints_a_usable_block() -> None:
    out = g.explain("company/billing/late_payment_charge.py")
    assert out.startswith("REUSE: company/billing/late_payment_charge.py")
    assert "CLASS:" in out and "INDEX:" in out and "searched" in out


# ── a MERGE adds nothing its other parent already has ───────────────────────────────────────
#
# The defect: `staged_additions` asked `git diff --cached --diff-filter=A`, which compares the index
# to `HEAD`, and for a merge `HEAD` is only the FIRST parent. Every module arriving from the second
# parent therefore read as this commit's own authorship and the merge was refused for lacking a
# record about somebody else's work. Measured 2026-09-25 on the live shared tree: merging
# `origin/main` into a checkout 3 behind it was refused with "tools/live_hook_drift.py: G1 no REUSE
# record". Because `core.hooksPath` is that checkout's own working copy and a diverged checkout can
# only advance by merging, that one refusal held the live gate chain at a version the trunk had moved
# past.


def _diverged_repo_mid_merge(tmp_path: Path, extra: dict[str, str] | None = None) -> Path:
    """A real repo, really diverged, with a real `git merge` in progress. Returns its root.

    NOT A STUB OF ONE. What is under test is whether `MERGE_HEAD` and the other parent's tree are
    read at the moment `commit-msg` runs, and a fake that hands the function two lists would prove
    the fake. `--no-commit` is what leaves `MERGE_HEAD` on disk, which is exactly the state git is in
    when it invokes `commit-msg`.
    """
    import subprocess as sp
    root = tmp_path / "repo"
    root.mkdir()

    def git(*args: str) -> None:
        r = sp.run(["git", *args], cwd=str(root), capture_output=True, text=True)
        assert r.returncode == 0, "git {}: {}".format(" ".join(args), r.stderr)

    def write(rel: str, text: str) -> None:
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("config", "commit.gpgsign", "false")
    write("tools/base.py", "x = 0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "side")
    write("tools/arrives_from_the_other_parent.py", "y = 1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "side adds a module, and records it there")
    git("checkout", "-q", "main")
    write("tools/ours.py", "z = 2\n")
    git("add", "-A")
    git("commit", "-q", "-m", "ours, so the branches diverge")
    # The merge itself. `--no-commit` stops at precisely the state `commit-msg` is invoked in.
    r = sp.run(["git", "merge", "--no-commit", "--no-ff", "side"], cwd=str(root),
               capture_output=True, text=True)
    assert (root / ".git" / "MERGE_HEAD").exists(), (
        "the fixture did not reach a merge state, so nothing below is about a merge: {}{}".format(
            r.stdout, r.stderr))
    for rel, text in (extra or {}).items():
        write(rel, text)
        sp.run(["git", "add", "--", rel], cwd=str(root), capture_output=True, text=True)
    return root


def test_a_merge_owes_no_record_for_the_other_parents_module_but_still_owes_one_for_its_own(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE DEFECT: a module arriving from the second parent was read as this commit's authorship.

    ONE CONTROL OVER THE WHOLE PARTITION, not a leg per branch. Both shapes are present in the SAME
    merge -- one path the other parent carries, one path no parent has ever seen -- so a repair that
    collapsed them into one state (exempt everything, or exempt nothing) cannot pass. A test that
    only asserted the exemption would go green on `return []`, which is the fail-open that matters
    here: it would switch the gate off for every merge commit, and merges are how the trunk arrives.
    """
    root = _diverged_repo_mid_merge(tmp_path, {"tools/authored_in_the_merge.py": "w = 3\n"})
    monkeypatch.setattr(g, "ROOT", root)

    added = g.staged_additions()
    owed = g.owes_a_record(added)

    assert owed == ["tools/authored_in_the_merge.py"], (
        "the merge owes a record for exactly the module NO parent carries. Got {} from additions "
        "{}".format(owed, added))
    assert "tools/arrives_from_the_other_parent.py" not in added, (
        "the second parent's own module is still being read as this commit's authorship -- which is "
        "the defect, and it refuses the merge for lacking a record about another commit's work")


def test_outside_a_merge_nothing_is_subtracted(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """The ordinary commit is untouched, and this is the arm the repair could most easily break.

    `merging_parents` returning something on a NON-merge would subtract HEAD's whole tree from the
    additions -- and HEAD's tree contains every file that already exists, so the gate would go quiet
    on exactly the commits it exists for. Asserted against a real repo with no `MERGE_HEAD`.
    """
    import subprocess as sp
    root = _diverged_repo_mid_merge(tmp_path)
    sp.run(["git", "merge", "--abort"], cwd=str(root), capture_output=True, text=True)
    (root / "tools" / "brand_new.py").write_text("q = 4\n", encoding="utf-8")
    sp.run(["git", "add", "-A"], cwd=str(root), capture_output=True, text=True)
    monkeypatch.setattr(g, "ROOT", root)

    assert g.merging_parents() == [], "no merge is in progress, so there is no other parent"
    assert g.owes_a_record(g.staged_additions()) == ["tools/brand_new.py"]


def test_an_unreadable_parent_keeps_the_strict_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    """`paths_at` returning `None` must subtract NOTHING -- the safe wrong answer, not the open one.

    An empty set from a parent would mean "that parent carries no files" and is a different claim
    from "git would not answer". Conflating them puts a fail-open behind one broken subprocess: the
    gate would exempt every path of any merge whose parent could not be read.
    """
    assert g.staged_additions(added_fn=lambda: ["tools/a.py"], parents_fn=lambda: ["deadbeef"],
                              paths_fn=lambda _c: None) == ["tools/a.py"], (
        "an unreadable parent must leave the additions exactly as a non-merge leaves them")
    assert g.paths_at("not-a-commit-that-exists") is None, (
        "a ref git cannot resolve must be None and never an empty set")


# Fixed inputs for the three merge-parent probes. NOT read from the live index: `git_additions`
# against this worktree returns whatever happens to be staged right now, which is routinely nothing,
# and a probe comparing [] to [] passes on every mutant there is.
_ADDED = ["tools/arrives_from_the_other_parent.py", "tools/authored_in_the_merge.py"]
_PARENT_CARRIES = {"tools/arrives_from_the_other_parent.py", "tools/base.py"}


def _probe_subtraction(m) -> bool:
    """The other parent's path is dropped and the merge's own is kept."""
    return m.staged_additions(added_fn=lambda: list(_ADDED),
                              parents_fn=lambda: ["side"],
                              paths_fn=lambda _c: set(_PARENT_CARRIES),
                              ) == ["tools/authored_in_the_merge.py"]


def _probe_non_merge(m) -> bool:
    """With no merge in progress the additions come back untouched."""
    return m.staged_additions(added_fn=lambda: list(_ADDED),
                              parents_fn=lambda: [],
                              paths_fn=lambda _c: set(_PARENT_CARRIES)) == _ADDED


def _probe_unreadable(m) -> bool:
    """An unreadable parent subtracts nothing -- the safe wrong answer, never the open one."""
    return m.staged_additions(added_fn=lambda: list(_ADDED),
                              parents_fn=lambda: ["x"],
                              paths_fn=lambda _c: None) == _ADDED


# ── R15: every guard broken at source, one at a time ────────────────────────────────────────
MUTATIONS = [
    # (name, old source fragment, replacement, probe -> must be TRUE on the real module and
    #  FALSE on the mutant; i.e. the guard stops firing when its own logic is broken)
    ("G1 missing-record",
     'findings.append(\n                f"{path}: G1',
     'pass  # noqa\n            _ = (\n                f"{path}: G1',
     lambda m: m.evaluate([NEW_MODULE], "no record", [])["status"] == "REJECT"),
    ("G2 class validity",
     "if cls not in PART_CLASSES:",
     "if False:",
     lambda m: "G2" in " ".join(m.evaluate([NEW_MODULE], record(INDEX=GOOD["INDEX"]),
                                           [])["findings"])),
    ("G3 catalogue needs a library",
     'if cls == "CATALOGUE" and not record.get("LIBRARY", "").strip():',
     'if False and cls == "CATALOGUE":',
     lambda m: "G3" in " ".join(m.evaluate([NEW_MODULE],
                                           record(CLASS="CATALOGUE", INDEX=GOOD["INDEX"]),
                                           [])["findings"])),
    ("G4 subsystem build-vs-buy",
     'missing = [f for f in ("EVALUATED", "REJECTED") if not record.get(f, "").strip()]',
     "missing = []",
     lambda m: "G4" in " ".join(m.evaluate([NEW_MODULE],
                                           record(CLASS="SUBSYSTEM", INDEX=GOOD["INDEX"]),
                                           [])["findings"])),
    ("G5 index terms recorded",
     "if not index_terms(record):",
     "if False:",
     lambda m: "G5" in " ".join(m.evaluate([NEW_MODULE],
                                           record(CLASS="CUSTOM", INDEX="had a look, nothing"),
                                           [])["findings"])),
    ("G6 index contradiction",
     "if not claims_nothing_exists(record):\n        return []",
     "if True:\n        return []",
     lambda m: "G6" in " ".join(m.evaluate(
         [NEW_MODULE],
         record(CLASS="CUSTOM", INDEX='searched "late payment" -- no existing row covers this'),
         rows(("company.billing.dunning", "late payment chasing")))["findings"])),
    ("detector sees new modules at all",
     'if not p.startswith(CODE_ROOTS):\n            continue',
     "if True:\n            continue",
     lambda m: m.evaluate([NEW_MODULE], "no record", [])["status"] == "REJECT"),
    ("the merge-parent subtraction",
     "    return [p for p in added if p not in already]",
     "    return added",
     # TRUE on the real module: the other parent's module is exempt. FALSE on the mutant, which
     # goes back to reading it as this commit's authorship.
     _probe_subtraction),
    ("the exemption is not blanket",
     "    if not parents:\n        return added",
     "    if not parents:\n        return []",
     # TRUE on the real module: a non-merge keeps its additions. The mutant silences the gate on
     # every ordinary commit, which is the fail-open the exemption could most easily become.
     _probe_non_merge),
    ("unreadable parent stays strict",
     "            return added\n        already |= carried",
     "            return []\n        already |= carried",
     _probe_unreadable),
    ("the module-vs-test distinction",
     'if p.startswith("tests/") or "/tests/" in p or Path(p).name.startswith("test_"):',
     "if False:",
     # inside a code root, so the roots clause cannot mask this -- only the test clause excludes it
     lambda m: m.evaluate(["tools/test_helper.py"], "no record", [])["owed"] == []),
]


def _load_mutant(tmp_path: Path, old: str, new: str, tag: str):
    src = SOURCE.read_text(encoding="utf-8")
    assert old in src, f"mutation target vanished from the source: {tag}"
    path = tmp_path / f"mutant_{tag}.py"
    path.write_text(src.replace(old, new, 1), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"wtg_mutant_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name,old,new,probe", MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_mutations(tmp_path: Path, name: str, old: str, new: str, probe) -> None:
    """Each guard, broken alone in a copy of the real source, must stop detecting its own defect.

    The probe passes on the REAL module (the guard works) and must FAIL on the mutant (the guard
    was load-bearing, not decorative). A probe that passes both ways is a test pinning nothing."""
    assert probe(g), f"{name}: probe does not hold on the real module -- the test is wrong"
    mutant = _load_mutant(tmp_path, old, new, name.split()[0].lower())
    assert not probe(mutant), (
        f"{name}: the guard was broken at source and NOTHING went red -- this guard cannot fail, "
        f"which R15 rules worse than having no guard at all")
