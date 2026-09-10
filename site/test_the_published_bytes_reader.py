"""The PUBLISHED bytes of a site subject -- the index copy -- for every door test.

WHY THIS MODULE EXISTS. On 2026-09-10 `site/test_the_baseline_comparison_reaches_the_reader.py`
stopped taking the working-tree file as its subject, because both of the most serious defects
found in the published value-arms comparison during the first ten days of September were REPAIRED
IN THE WORKING TREE and stayed invisible to every control over them: each control read the same
file the repair was sitting in, and therefore reported the repaired state as the published one. A
door test whose subject is `SITE / "data" / x.json` cannot tell "the reader can see this" from
"someone in this tree has fixed it and not landed it", and those are the only two states it exists
to separate.

That fix covered ONE door. The relapse is one line long in every other door test in this
directory -- a constant like `FEED = SITE / "data" / "book_growth.json"` plus `FEED.read_text()`
-- and there were eight more files carrying exactly that shape. The mechanism lives here rather
than being copied into each of them, because a control duplicated nine times is a control that
will be repaired in one place and rot in eight; this project has paid for that shape before (one
VAT rule, five implementations, a July fix still live as a defect in August).

WHICH REF IS "PUBLISHED", AND WHY IT IS THE INDEX AND NOT `HEAD`. `tools/surgical_land.py` is the
only door work comes through, and its gate runs these suites in a clean extract whose `.git/HEAD`
is the PARENT commit (`_make_standalone_repo`) and whose index is the parent plus exactly the
paths being committed (`git add -A -- <paths>`, `_build_extract`). So inside the gate, `HEAD:<path>`
is the copy from BEFORE the commit: a control keyed to `HEAD` would go red on the very commit that
repairs the feed, and could only ever go green again by being landed past a gate that refuses it.
It would also pass every "does it refuse correctly" test written over it, because a guard that
refuses EVERYTHING refuses correctly.

The index answers the same question in both places: in a working tree it is HEAD unless something
has been staged, and inside the gate it is precisely the bytes this commit publishes. The residual
hole is stated rather than hidden -- a repair `git add`-ed and never committed reads as published
-- and it is one transient step wide, where the `HEAD` reading is unlandable.

The mechanism is proved BELOW, against scratch repos whose index and working tree deliberately
disagree, because on this project's own tree the two copies agree almost always and a control that
only ran here would pass whatever it happened to read.

WHY THE MECHANISM AND ITS PROOFS SHARE A FILE. `tools/capability_index.py` classifies a module as
evidence by its NAME -- `is_evidence_file` is `test_*` or `conftest.py` -- and the orphan ratchet
walks only the production graph. A `site/_published_bytes.py` whose only callers are nine test
files is therefore unreachable by construction: it can never acquire a caller the ratchet can see,
and the only ways to clear that refusal are to invent a production caller or to `--freeze` it as
"deliberately dormant". It is not dormant -- it executes on every `pytest site/` and inside every
gate run -- so freezing it would put a false statement on the record to clear a control, which is
the failure `tools/orphan_ratchet.py` names in its own comments. Living beside its proofs, under
the name the index already reserves for evidence, is the classification being correct rather than
a way around a gate.
"""

from __future__ import annotations

import ast
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import pytest

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent


def published_blob(rel: str, root: Path | None = None) -> str:
    """The PUBLISHED bytes of `rel` (repo-relative) -- the index copy -- never the file on disk.

    FAIL-CLOSED, AND IN THOSE WORDS. git being unable to answer is not "assume the file is fine":
    a path that has never been committed, a repo git cannot read, a timeout, all land here, and
    every one of them means the calling control has no subject. An unavailable check is a FAILED
    check, so this fails the test with the path and the git error in the message rather than
    falling back to the working tree, which is the one fallback that would restore the whole
    defect.

    `root` exists so the mechanism itself can be proved against a scratch repo whose index and
    working tree deliberately disagree. Production callers never pass it.
    """
    base = PROJECT if root is None else root
    try:
        shown = subprocess.run(
            ["git", "-C", str(base), "show", ":{}".format(rel)],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.fail(
            "git could not be run to read the published copy of {} ({}), so this control has no "
            "subject -- reported as a FAILURE and never skipped, and never read from the working "
            "tree instead".format(rel, exc))
    if shown.returncode != 0:
        pytest.fail(
            "{} is not in the index, so there is no published copy of it to check ({}). A repair "
            "that exists only in the working tree is exactly the state this control exists to "
            "call RED.".format(rel, (shown.stderr or "").strip()[-300:]))
    return shown.stdout


def published_json(rel: str, root: Path | None = None) -> dict:
    """`published_blob` parsed. Unreadable JSON is a FAILURE, never an empty (agreeing) dict."""
    text = published_blob(rel, root=root)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        pytest.fail("the published copy of {} is not readable JSON ({}), so the door a reader "
                    "boots cannot render from it".format(rel, exc))


#: rel -> (TemporaryDirectory holder, materialised path). Module-global rather than a fixture
#: because the door is materialised once and driven from ~150 tests across this directory, and
#: re-shelling `git show` per test is pure cost. The holder is kept alive here so the directory
#: is removed at interpreter exit rather than left behind in /tmp.
_MATERIALISED: dict[str, tuple] = {}


def published_file(rel: str) -> Path:
    """The published bytes of `rel`, on disk, because the render harness boots a FILE.

    Materialising is not a weakening of the subject: the bytes are the index's, read once, and
    nothing writes to this path. What it does mean is that the subject reaches the harness by a
    second mechanism, so callers assert the materialised bytes are byte-identical to what git
    returned (`published_file(rel).read_text() == published_blob(rel)`).

    The scratch file is deliberately NOT given the subject's own basename: `refuse_working_tree_
    reads` below refuses any `/`-built path whose segment quotes a subject basename, which is the
    exact shape of the relapse it exists to prevent, and naming the scratch copy after its
    subject would make every caller trip its own guard.
    """
    if rel not in _MATERIALISED:
        holder = tempfile.TemporaryDirectory(prefix="published-subject-")
        stem, _, ext = rel.rsplit("/", 1)[-1].rpartition(".")
        scratch = Path(holder.name) / "published_{}_copy.{}".format(stem.replace("-", "_"), ext)
        scratch.write_text(published_blob(rel), encoding="utf-8")
        _MATERIALISED[rel] = (holder, scratch)
    return _MATERIALISED[rel][1]


# ── the relapse guard ─────────────────────────────────────────────────────────────────────────


def working_tree_reads(source: str, basenames: Iterable[str]) -> tuple[list, list]:
    """Scan `source` for the two shapes that put a published subject back on the working tree.

    Returns `(paths BUILT to a subject, subjects READ off disk)` as `(line, basename)` pairs.

    The defect is one line long and looks completely ordinary -- `FEED = SITE / "data" /
    "value_arms.json"`, then `FEED.read_text()` -- which is why it survived for weeks in the file
    that first fixed it, and why the fix cannot be "remember not to". Two shapes are refused, and
    between them they cover both ways back in:

      (a) building a path to a subject with `/` at all, which is the constant these files used to
          carry;
      (b) reading a subject off disk with `read_text` / `read_bytes` / `open`, whether the
          basename is quoted at the call site (`open("site/data/x.json")`) or held in a name that
          was BOUND to a subject path earlier in the file (`FEED = ...` then `FEED.read_text()`).

    Shape (a) alone would pass a file that never builds the path with `/` -- `FEED =
    Path("site/data/value_arms.json")` is the same defect written differently -- and would say
    nothing about a constant that is built and then handed to `json.load`. Shape (b) alone would
    pass a path built and then given to a subprocess argument, which is how the render harness
    receives the door. Neither is redundant, and the one-line binding pass is what makes (b) see
    the shape that actually appears in these files.

    A repo-relative subject STRING is deliberately not a hit: `FEED_REL = "site/data/x.json"` is
    the correct spelling, and it differs from the defect exactly in that the basename is not its
    own quoted token. That discrimination is the reason the match is on `"<basename>"` rather
    than on the bare basename.
    """
    wanted = set(basenames)

    def names_a_subject(node) -> str | None:
        """The strict match: the basename is its own quoted token, as in `... / "x.json"`.

        Used for BUILDING a path and for binding a name to one, where the correct spelling --
        `FEED_REL = "site/data/x.json"` -- must NOT be a hit or the guard reds on every file that
        adopts it. The two differ exactly in whether the basename is quoted on its own.
        """
        segment = ast.get_source_segment(source, node) or ""
        return next((b for b in wanted
                     if '"{}"'.format(b) in segment or "'{}'".format(b) in segment), None)

    def mentions_a_subject(node) -> str | None:
        """The loose match: ANY string literal under `node` that ends in a subject's basename.

        Used only at a READ call site, where the distinction above stops mattering: passing
        `"site/data/x.json"` to `published_blob` is the fix, and passing the identical string to
        `open` is the defect. What is done with the path is the whole question, so the strict
        match would be fail-open here -- `open("site/data/x.json")` is exactly the spelling it
        was built to let through.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                hit = next((b for b in wanted if child.value.endswith(b)), None)
                if hit:
                    return hit
        return None

    tree = ast.parse(source)

    # Names BOUND to a subject path, so `FEED = SITE / "data" / x` + `FEED.read_text()` reads as
    # what it is. Flow-insensitive on purpose: a name that ever holds a subject path is treated
    # as holding one everywhere, which can only make this control stricter, never fail-open.
    bound: dict[str, str] = {}
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if not targets or node.value is None:
            continue
        hit = names_a_subject(node.value)
        if hit is None and not isinstance(node.value, ast.Constant):
            # A bare string constant is the CORRECT spelling and never binds a path; anything
            # else that mentions a subject -- `Path("site/data/x.json")`, a call, a subscript --
            # is a path object, and a path object is the thing that gets read off disk.
            hit = mentions_a_subject(node.value)
        if hit:
            for target in targets:
                if isinstance(target, ast.Name):
                    bound[target.id] = hit

    built, read = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            hit = names_a_subject(node)
            if hit:
                built.append((node.lineno, hit))
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in ("read_text", "read_bytes"):
                hit = mentions_a_subject(func.value)
                if hit is None and isinstance(func.value, ast.Name):
                    hit = bound.get(func.value.id)
            elif isinstance(func, ast.Name) and func.id == "open":
                hit = mentions_a_subject(node)
                if hit is None:
                    hit = next((bound[a.id] for a in node.args
                                if isinstance(a, ast.Name) and a.id in bound), None)
            else:
                hit = None
            if hit:
                read.append((node.lineno, hit))
    return built, read


def refuse_working_tree_reads(module_file: str, rels: Iterable[str]) -> None:
    """Assert the calling test module never takes a working-tree copy of its own subjects.

    Callers pass `__file__` and their own `*_REL` constants, so a sixth feed added to a door's
    render payload is covered the day it is added and not the day someone remembers this exists.

    NON-VACUITY IS CHECKED HERE, not left to each caller: "found nothing" and "cannot find
    anything" are the two readings of a silent scanner and only one of them is a pass, so the
    scanner is first run over the exact line these files used to carry and must catch it.
    """
    rels = list(rels)
    assert rels, ("refuse_working_tree_reads was given no subjects, so it would pass on a file "
                  "that reads every feed off disk -- an empty subject list is a FAILED check")
    basenames = {rel.rsplit("/", 1)[-1] for rel in rels}

    probe = 'SUBJECT = SITE / "data" / "{}"\nsource = SUBJECT.read_text()\n'.format(
        sorted(basenames)[0])
    caught_built, caught_read = working_tree_reads(probe, basenames)
    assert caught_built and caught_read, (
        "the scanner does not catch the two lines it exists to refuse ({!r}) -- built={}, "
        "read={} -- so its silence about {} means nothing".format(
            probe, caught_built, caught_read, module_file))

    source = Path(module_file).read_text(encoding="utf-8")
    built, read = working_tree_reads(source, basenames)
    assert not built, (
        "{} builds a filesystem path to a published subject at line(s) {}. Every control in that "
        "file would then grade whatever this tree is holding, which is how two live defects "
        "stayed invisible while being repaired. Read it with `published_blob`.".format(
            module_file, ", ".join("{} ({})".format(n, b) for n, b in built)))
    assert not read, (
        "{} reads a published subject off disk at line(s) {}; the published copy is the index "
        "copy, via `published_blob`.".format(
            module_file, ", ".join("{} ({})".format(n, b) for n, b in read)))


# ── the proofs ────────────────────────────────────────────────────────────────────────────
#
# The published-bytes reader is proved HERE, once, for every door test that rests on it.
#
# WHAT THE PROOFS BELOW ARE FOR. The reader above is the subject-picker underneath every
# `site/test_*_door.py` and `site/test_*_reaches_the_reader.py`: it decides whether "the published
# page" means the bytes a reader can fetch or the bytes this working tree happens to be holding.
# Every other control in this directory is downstream of that decision, so if the reader silently
# falls back to disk, ~450 render assertions go on passing while grading an unlanded repair. That
# is not hypothetical -- it is what happened to the value-arms comparison twice in ten days.
#
# WHY THE PROOFS ARE AGAINST SCRATCH REPOS AND NOT THIS TREE. On this project's own tree the index
# and the working tree agree almost always, so a control that only ran here would pass whatever the
# reader read -- including the working-tree file it exists to stop reading. The disagreement is
# therefore CONSTRUCTED: a scratch repo holding one string in its index and a different one on disk.
# `git init` and `git add` only -- no commit, so no repo's hooks are involved and nothing here can
# touch this project's history.
#
# R15 -- the mutations that bought these, each run and reverted, on 2026-09-10:
#   * `published_blob` falling back to `(base / rel).read_text()` when git fails ->
#     `test_the_reader_FAILS_when_there_is_no_published_copy` reds (DID NOT RAISE).
#   * `published_blob` reading `HEAD:{}` instead of `:{}` -> `test_the_reader_returns_the_INDEX_
#     copy_when_the_working_tree_disagrees` reds (no commit in the scratch repo, so a HEAD read
#     cannot answer at all) -- which is also the argument that the `HEAD` reading is unlandable
#     inside `surgical_land`'s gate extract, where HEAD is the PARENT commit.
#   * `working_tree_reads` returning `([], [])` unconditionally -> the non-vacuity leg inside
#     `refuse_working_tree_reads` reds, and so does `test_the_scanner_catches_both_halves_of_the_
#     relapse`. Both legs are needed: a scanner that finds nothing and a scanner that cannot find
#     anything are the same silence, and only one of them is a pass.
#   * dropping the `ast.BinOp` arm (path-building) from `working_tree_reads` -> the built-half
#     assertion reds and the read-half stays green, so neither arm is carried by the other.
#   * dropping the `ast.Call` arm (reading) -> the mirror.


FEED_REL = "site/data/value_arms.json"


def _scratch_repo(root: Path, rel: str, published: str, on_disk: str) -> None:
    """A repo whose index and working tree DELIBERATELY DISAGREE about `rel`.

    The index is the whole subject, so staging is all that is needed to construct the state.
    """
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True, timeout=60)
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(published, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "--", rel],
                   check=True, capture_output=True, timeout=60)
    target.write_text(on_disk, encoding="utf-8")


def test_the_reader_returns_the_INDEX_copy_when_the_working_tree_disagrees(tmp_path):
    """THE WHOLE POINT, proved where the two copies actually differ.

    Fires on: `published_blob` falling back to `rel.read_text()` on any path; on it reading
    `HEAD:` instead of `:` (there is no commit here, so a HEAD read cannot answer at all).
    """
    repo = tmp_path / "scratch"
    _scratch_repo(repo, FEED_REL, '{"available": true, "who": "published"}',
                  '{"available": true, "who": "repaired in the tree and never landed"}')

    # NON-VACUITY: the fixture must actually disagree, or the assertion below is satisfied by
    # two identical strings and says nothing.
    assert "never landed" in (repo / FEED_REL).read_text(encoding="utf-8")

    got = published_blob(FEED_REL, root=repo)
    assert '"who": "published"' in got, (
        "the reader returned something other than the index copy, so an unlanded repair is still "
        "what the door tests grade: {!r}".format(got[:200]))
    assert "never landed" not in got, (
        "the reader returned the WORKING-TREE copy. That is the entire defect this module exists "
        "to close: a repair sitting in the tree reads as the published page.")


def test_the_JSON_reader_parses_the_INDEX_copy_and_not_the_file_beside_it(tmp_path):
    """`published_json` is what ~40 render payloads are built from, so it gets its own leg.

    A door test asks for a dict, never a string, and an alias that quietly parsed the working-tree
    file would restore the defect for every one of those callers while `published_blob` stayed
    correct. Fires on `published_json` reading the path itself rather than delegating.
    """
    repo = tmp_path / "scratch"
    _scratch_repo(repo, FEED_REL, '{"who": "published"}', '{"who": "never landed"}')
    assert published_json(FEED_REL, root=repo) == {"who": "published"}


def test_the_reader_FAILS_when_there_is_no_published_copy_rather_than_reading_the_file(tmp_path):
    """FAIL-CLOSED, and the file being right there on disk is what makes it a real question.

    A `value_arms.json` that exists and has never been committed is not "fine" -- it is the
    defect at its most complete, because no reader has ever met it. The reader must say so, name
    the path, and never hand back the bytes lying next to it.

    Fires on: any `except` that returns the working-tree text; on returning `""` (an empty feed
    would skip or pass vacuously through most of a door test rather than failing).
    """
    repo = tmp_path / "scratch"
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True, timeout=60)
    target = repo / FEED_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('{"available": true, "who": "never committed"}', encoding="utf-8")

    with pytest.raises(pytest.fail.Exception) as refused:
        published_blob(FEED_REL, root=repo)
    said = str(refused.value)
    assert FEED_REL in said, "the refusal does not name the path it could not read: {}".format(said)
    assert "never committed" not in said, (
        "the refusal quotes the working-tree bytes, which means it read them")
    assert "index" in said.lower(), (
        "the refusal does not say WHY it refused, so the next reader cannot tell a missing "
        "publish from a broken checkout: {}".format(said))


def test_the_materialised_copy_is_the_published_copy(tmp_path):
    """The harness boots a FILE, so the bytes reach node by a second mechanism -- prove they match.

    Fires on the scratch copy being truncated, re-encoded, or written from the wrong source, and
    on `published_file` handing back the repo path itself.
    """
    on_disk = published_file(FEED_REL)
    assert on_disk.read_text(encoding="utf-8") == published_blob(FEED_REL)
    assert Path(FEED_REL).name not in on_disk.name, (
        "the materialised copy is named after its subject, which would make every caller's own "
        "relapse guard fire on the line that materialises it: {}".format(on_disk))
    assert json.loads(on_disk.read_text(encoding="utf-8")), "the materialised copy is empty"


def test_the_scanner_catches_both_halves_of_the_relapse():
    """The guard's teeth, over the exact two lines the eight door tests used to carry.

    Fires on either `ast` arm being dropped: the built list and the read list are asserted
    separately, so neither half can be carried by the other.
    """
    relapse = ('FEED = SITE / "data" / "value_arms.json"\n'
               'payload = json.loads(FEED.read_text(encoding="utf-8"))\n')
    built, read = working_tree_reads(relapse, {"value_arms.json"})
    assert [b for _, b in built] == ["value_arms.json"], (
        "the scanner does not see a path BUILT to a subject: {}".format(built))
    assert [b for _, b in read] == ["value_arms.json"], (
        "the scanner does not see a subject READ off disk: {}".format(read))

    # `open()` is the third door in, and a file that uses it evades an attribute-only scan.
    _, opened = working_tree_reads('h = open("site/data/value_arms.json")\n', {"value_arms.json"})
    assert opened, "the scanner is blind to the builtin `open`"

    # The same defect written WITHOUT `/`, which shape (a) cannot see at all.
    no_slash = ('FEED = Path("site/data/value_arms.json")\n'
                'payload = json.loads(FEED.read_text())\n')
    built_only, read_only = working_tree_reads(no_slash, {"value_arms.json"})
    assert not built_only, "no path is BUILT here, so flagging one would be a false positive"
    assert read_only, ("the scanner is blind to a subject bound with `Path(...)` and read through "
                       "the name, which is the same defect with the `/` taken out")

    # THE DISCRIMINATION THE WHOLE MATCH RESTS ON: the correct spelling must not be a hit, or the
    # guard reds on every file that adopts it and gets deleted within the day.
    correct = ('FEED_REL = "site/data/value_arms.json"\n'
               'payload = published_json(FEED_REL)\n')
    assert working_tree_reads(correct, {"value_arms.json"}) == ([], []), (
        "the guard flags the repo-relative subject string it exists to encourage")

    # A path that is NOT a subject must not be flagged, or the guard becomes unusable and gets
    # deleted -- the `_live_harness.mjs` constant every door test legitimately builds.
    clean, _ = working_tree_reads('H = SITE / "_live_harness.mjs"\n', {"value_arms.json"})
    assert not clean, "the scanner flags a path that is not one of its subjects: {}".format(clean)


def test_the_guard_REFUSES_a_module_that_reads_its_subject_off_disk(tmp_path):
    """`refuse_working_tree_reads` must FAIL on a relapsed file, not merely pass on clean ones.

    Every assertion in this directory that calls the guard is a "does it stay quiet" test, and a
    guard that stays quiet about everything passes all of them. This is the one leg that asks the
    opposite question.
    """
    relapsed = tmp_path / "test_pretend_door.py"
    relapsed.write_text('FEED = SITE / "data" / "value_arms.json"\n', encoding="utf-8")
    with pytest.raises(AssertionError) as refused:
        refuse_working_tree_reads(str(relapsed), (FEED_REL,))
    assert "value_arms.json" in str(refused.value)

    clean = tmp_path / "test_pretend_clean_door.py"
    clean.write_text('FEED_REL = "site/data/value_arms.json"\n'
                     'payload = published_json(FEED_REL)\n', encoding="utf-8")
    refuse_working_tree_reads(str(clean), (FEED_REL,))


def test_the_guard_REFUSES_an_empty_subject_list():
    """An empty subject list makes the guard vacuous, and vacuous is the failure mode it has.

    A caller that lifts the guard in but forgets to pass its `*_REL` constants would otherwise get
    a green test that reads every feed off disk. Fires on the `assert rels` leg being removed.
    """
    with pytest.raises(AssertionError) as refused:
        refuse_working_tree_reads(__file__, ())
    assert "no subjects" in str(refused.value)


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """The guard over the guard's own test file, so this one cannot drift either."""
    refuse_working_tree_reads(__file__, (FEED_REL,))
