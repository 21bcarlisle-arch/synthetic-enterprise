"""A page that stamps itself "as of <date>" must not outlive the thing that stamps it.

THE DEFECT, MEASURED 2026-09-20 (docs/staging/SEAT_FINDING_THE_PAGES_ROOT_SERVES_A_RETIRED_
MIRROR_AND_PATHS_IGNORE_IS_NOT_A_PUBLISH_FILTER_2026-09-20.md)
---------------------------------------------------------------------------------------------
`docs/shadow/` -- five pages, uploaded to the public GitHub Pages root by a workflow whose
upload step is `path: docs`, the whole tree. Its generator was retired from the publish cycle on
2026-08-20 by the director's five-tab ruling (03dd8c49e). The pages stayed. For a month the root
served a full internal P&L -- net margin GBP1,529,289, treasury, enterprise value, a ten-row
year table, and ten Run History rows reading blank/blank/GBP0 -- each carrying
`Generated: 2026-08-20T06:59:11Z | Run a5bfec712...`.

Nothing could move those figures, and that is the precise harm. A page with no stamp that goes
stale is merely old. A page that ASSERTS a date and cannot be rewritten is a frozen claim: it
keeps saying "this was true on 2026-08-20" to every reader, forever, in the present tense of a
live site. The repair (d066d3534, the same day) that made the renderer emit the real
git_hash/generated_at/net_margin was correct AND inert, because the renderer is not called --
which is the shape in one line.

WHY THE TREE COULD NOT SEE IT
-----------------------------
Two roots serve this project: Cloudflare from `site/` and GitHub Pages from `docs/`. For a month
only `site/` was ever checked, and two prior findings concluded "no wrong figure is on the live
site" on the strength of looking at one of them. `tools/startup_anchor_freshness._UNPUBLISHED`
had `docs/shadow/` on a list of paths "a reader cannot be sent to", read off the workflow's
`paths-ignore` -- which is a TRIGGER filter, not a publish filter.

WHAT THIS IS KEYED TO, AND WHAT IT IS DELIBERATELY NOT
------------------------------------------------------
NOT "docs/shadow/ does not exist". That is today's answer. It goes green the moment the
directory is deleted and stays green while the identical defect lands under another name
tomorrow -- the control-pinned-to-the-current-state shape this project has paid for repeatedly.

The PROPERTY: a stamped page served from the Pages root must have a module that can still write
it. Both halves are derived, never remembered -- the root from the workflow's own `path:` value,
the writers by asking the source tree which paths it names. An unstamped page (a hand-written
static page, a template) is out of scope on purpose: it makes no claim about when it was true,
so it cannot be frozen against one, and widening to "every HTML needs a writer" would refuse
three legitimate hand-authored pages and be switched off inside a week.

NON-VACUITY IS THE WHOLE RISK, AND IT IS MEASURED NOT ASSUMED
-------------------------------------------------------------
After the repair the live stamped population under `docs/` is ZERO. Leg 1 alone is therefore
the textbook FAIL-OPEN that R15 names first: an empty evidence set read as no complaint, green
forever, including on the day the defect returns with a producer that stops writing. So
`frozen_pages()` is a pure function over an injected root and an injected source set, and
`test_the_predicate_fires_on_a_stamped_orphan_and_spares_the_rest` drives it over a fixture
holding all three populations at once -- a stamped orphan, a stamped page whose writer exists,
and an unstamped orphan. It asserts the partition in ONE control rather than a leg per branch:
the orphan is returned AND the other two are not. A predicate that refuses everything fails it,
which is the mutation a per-branch version would pass.

FAIL-CLOSED. A missing or unparseable workflow, an absent Pages root, an empty HTML population
and an empty source population all RAISE. The subject set is derived by subtraction, so a `docs/`
that failed to check out would otherwise read as a clean site rather than a broken check.

WHAT THIS CANNOT SEE, STATED RATHER THAN GLOSSED
-------------------------------------------------
"A module declares this path" is a NECESSARY condition for a live writer, not a sufficient one.
A path-shaped string in a list that never writes anything -- a classification keyword, a
divergence exemption, a gate's root tuple -- reads here as a writer and would clear a frozen
page. That is a real hole and it is why the landing this control shipped with also removed the
three such entries that still named `docs/shadow/` (`background/tree_divergence.GENERATED_
PREFIXES`, `background/naive_organ._BUCKET_KEYWORDS`, `tools/publish_surface_gate.PUBLISH_
SURFACE_ROOTS`): with any one of them left, this control passes over the exact defect it was
written for. Named here so the next reader knows the check is one-sided, rather than finding out
by trusting it.

Both narrowings below were forced by re-running the REAL mutation, not by the fixture -- the
fixture was green through two drafts that the live tree refuted. Printing the numbers at real
inputs before shipping the formula, which is the rule, and it earned its keep twice in one hour.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "github-pages.yml"

#: A machine freshness stamp: the page is asserting when it was true. Both shapes the site's
#: renderers emit -- an ISO `Generated:` line and a `Run <sha>` provenance line -- because a
#: renderer that drops one still asserts a vintage with the other.
_STAMP = re.compile(r"Generated:\s*\d{4}-\d{2}-\d{2}T|\bRun\s+[0-9a-f]{40}\b")

#: The action whose `path:` IS the published root. Matched exactly against `uses` minus its ref.
_UPLOAD_ACTION = "actions/upload-pages-artifact"

#: Where a module may declare a path it writes. Both roots, because the publish cycle lives in
#: `background/` and the generators it calls live in `tools/`.
_SOURCE_ROOTS = ("tools", "background")


def pages_root(workflow: Path = WORKFLOW) -> str:
    """The directory the Pages workflow uploads, read from the workflow itself.

    Derived rather than hardcoded so that narrowing the upload (the open question in the
    finding above) moves this control's subject with it, instead of leaving it pointed at a
    root nobody publishes any more.

    PARSED AS YAML, NOT REGEXED. The first draft matched `upload-pages-artifact.*?path:\\s*(\\S+)`
    over the file text, which `tests/architecture/test_a_control_reads_python_as_code.py`
    correctly objected to on the same grounds even though the subject here is YAML rather than
    Python: a control reading structured source as text is one reformat away from silently
    finding nothing. A comment mentioning `path:`, a re-ordered `with:` block or a quoted value
    all break the regex, and the failure mode is this control losing its subject and passing.
    The structure answers the question exactly and cannot drift.
    """
    if not workflow.is_file():
        raise AssertionError(
            "the GitHub Pages workflow is missing at {} -- this control cannot say what is "
            "served and must not pass by default".format(workflow)
        )
    try:
        spec = yaml.safe_load(workflow.read_text()) or {}
    except yaml.YAMLError as exc:
        raise AssertionError(
            "{} does not parse as YAML ({}) -- the subject of this control is not "
            "derivable".format(workflow, exc)
        ) from exc

    for job in (spec.get("jobs") or {}).values():
        for step in (job or {}).get("steps") or []:
            uses = (step or {}).get("uses") or ""
            # The action NAME, matched exactly -- `owner/action@ref` split on its own separators
            # rather than sniffed for a substring. A membership test would also match a step
            # merely named after the action, and the census that guards this class is right to
            # treat "search tainted text for a token" as the hazard whatever the file format.
            if uses.split("@")[0] == _UPLOAD_ACTION:
                path = ((step.get("with") or {}).get("path") or "").strip()
                if path:
                    return path.rstrip("/")
    raise AssertionError(
        "no upload-pages-artifact step with a `path:` in {} -- the workflow's shape changed and "
        "this control can no longer say what is served".format(workflow)
    )


def declared_paths(source: str, label: str = "<source>") -> set[str]:
    """Every path this module's CODE declares -- comments and docstrings excluded.

    A COMMENT IS NOT A WRITER, and this control's first draft failed exactly there: its plain
    substring search over the file text counted the tombstone comments left by the very repair
    that deleted the mirror ("`docs/shadow/` was here too until 2026-09-20"). The retired
    surface was therefore cleared by the prose recording its retirement -- a tautology, and one
    that would have shipped green. Caught by re-running the real mutation rather than trusting
    the fixture, which is the only reason it is not in the tree.

    Two forms are read, because both are in live use here and a scan that reads only the first
    is how `docs/direction/` became invisible to
    `startup_anchor_freshness.discover_maintained_surfaces` (its `UNDISCOVERABLE` block records
    the same lesson):

      * the slash literal      -- `"docs/state/customer_sample.json"`
      * the segment-wise build -- `PROJECT / "docs" / "state"`
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise AssertionError(
            "{} does not parse ({}) -- skipping it would quietly shrink the writer set and "
            "turn live pages into orphans".format(label, exc)
        ) from exc

    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))

    out = set()

    def _strs(node):
        """The ordered string constants of a `/` chain, or None if it is not one."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return [node.value]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left, right = _strs(node.left), _strs(node.right)
            if right is None:
                return None
            return (left or []) + right
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and id(node) not in docstrings and _path_shaped(node.value):
            out.add(node.value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            chain = _strs(node)
            if chain:
                out.add("/".join(chain))
    return out


def _path_shaped(text: str) -> bool:
    """A path literal, not prose that happens to contain one.

    THE SECOND THING THE REAL MUTATION CAUGHT. Before this, every string constant counted, so
    `process_run_complete`'s log line -- "Mirrored {} file(s) to docs/shadow + docs/state for
    GitHub Pages" -- cleared the whole frozen mirror. A sentence ABOUT a path is not a writer of
    it, and the sentence in question was itself stale prose describing a copy that had not
    happened for a month.
    """
    return bool(text) and not re.search(r"\s", text)


def _names_path(declared: set[str], rel_dir: str) -> bool:
    """Does any declared path string name `rel_dir`?"""
    return any(rel_dir in d for d in declared)


def frozen_pages(root: Path, sources: dict[str, str]) -> list[str]:
    """Stamped HTML pages under `root` that no source in `sources` declares a path to.

    `sources` maps a label to that file's text, injected so the predicate can be driven over a
    fixture. Returns page paths relative to `root.parent`, sorted, so a failure names the URL
    the reader would actually be served.
    """
    if not root.is_dir():
        raise AssertionError(
            "the Pages root {} does not exist -- a control whose subject vanished must refuse, "
            "not report a clean site".format(root)
        )
    if not sources:
        raise AssertionError(
            "no source files were supplied -- with an empty writer set EVERY page looks "
            "orphaned, or with the subtraction the other way none do. Refusing either reading."
        )

    pages = sorted(root.rglob("*.html"))
    if not pages:
        raise AssertionError(
            "no HTML pages found under {} -- a moved or unchecked-out Pages root must not read "
            "as 'nothing frozen'".format(root)
        )

    declared = set()
    for label, text in sources.items():
        declared |= declared_paths(text, label)

    frozen = []
    for page in pages:
        if not _STAMP.search(page.read_text(errors="replace")):
            continue
        rel = page.relative_to(root.parent)
        # The page itself, its directory, and every ancestor STRICTLY BELOW the root: a mirror
        # step names the TREE it writes (`docs/shadow`), never each leaf inside it.
        #
        # THE ROOT ITSELF IS EXCLUDED, and the fixture caught this as a fail-open before the
        # control shipped: with `docs` in the candidate set, ANY source mentioning `docs/`
        # anywhere cleared every page under the root at once, and the predicate returned `[]`
        # for a tree whose orphan was sitting right there. A guard that clears everything
        # passes every leg written to confirm it refuses correctly.
        root_rel = str(root.relative_to(root.parent))
        candidates = [str(rel)] + [
            str(p) for p in rel.parents if str(p) not in (".", root_rel)
        ]
        if not any(_names_path(declared, c) for c in candidates):
            frozen.append(str(rel))
    return sorted(frozen)


def _repo_sources() -> dict[str, str]:
    out = {}
    for sub in _SOURCE_ROOTS:
        for py in (ROOT / sub).rglob("*.py"):
            out[str(py.relative_to(ROOT))] = py.read_text(errors="replace")
    return out


def test_no_stamped_page_at_the_pages_root_has_lost_its_writer():
    """THE PROPERTY, against the real tree."""
    sources = _repo_sources()
    assert len(sources) > 100, (
        "only {} source files found under {} -- the writer population collapsed, so this "
        "control cannot judge anything".format(len(sources), _SOURCE_ROOTS)
    )

    frozen = frozen_pages(ROOT / pages_root(), sources)

    assert frozen == [], (
        "These pages are served from the GitHub Pages root and stamp themselves with a date, "
        "but nothing in tools/ or background/ still names a path to them -- so the stamp can "
        "never move again and the figures under it are a frozen claim: {}. Either restore a "
        "writer or delete the pages; leaving them is the docs/shadow/ defect of 2026-09-20."
        .format(frozen)
    )


def test_the_predicate_fires_on_a_stamped_orphan_and_spares_the_rest(tmp_path):
    """THE WHOLE PARTITION IN ONE CONTROL -- this is what stops leg 1 being vacuous.

    The live stamped population is zero, so without this the predicate could return `[]`
    unconditionally, or refuse every page, and leg 1 would be green either way. All three
    populations are present here at once and the single assertion pins the discrimination:
    only the stamped orphan comes back.
    """
    root = tmp_path / "docs"
    (root / "ghost").mkdir(parents=True)
    (root / "kept").mkdir()
    (root / "static").mkdir()

    # 1. stamped, no writer -> the defect
    (root / "ghost" / "index.html").write_text(
        "<p>Net Margin &pound;1,529,289</p><p>Generated: 2026-08-20T06:59:11Z</p>")
    # 2. stamped, writer exists -> fine, and it is what proves the check is not refusing all
    (root / "kept" / "index.html").write_text("<p>Generated: 2026-09-20T01:00:00Z</p>")
    # 3. unstamped, no writer -> a hand-written static page, correctly out of scope
    (root / "static" / "index.html").write_text("<p>About this project</p>")

    sources = {"tools/generate_kept.py": 'OUT = PROJECT / "docs" / "kept" / "index.html"'}

    assert frozen_pages(root, sources) == ["docs/ghost/index.html"]


def test_prose_naming_a_path_is_not_a_writer_of_it(tmp_path):
    """A sentence mentioning the directory must not clear the pages inside it.

    THE MUTATION THAT SHIPPED GREEN TWICE. `process_run_complete` logged "Mirrored {} file(s)
    to docs/shadow + docs/state for GitHub Pages" -- a log line describing a copy that had not
    run for a month -- and that string alone cleared the entire frozen mirror from the first
    draft of this control. A comment does the same thing and is worse, because the comment that
    clears a retired surface is usually the tombstone recording its retirement: the control
    would be silenced by the prose announcing the very defect it watches for.
    """
    root = tmp_path / "docs"
    (root / "ghost").mkdir(parents=True)
    (root / "ghost" / "index.html").write_text("Generated: 2026-08-20T06:59:11Z")

    log_line = 'log("Mirrored files to docs/ghost + docs/state for GitHub Pages")'
    comment = '# docs/ghost/ was retired on 2026-08-20 and its generator switched off\nx = 1\n'
    docstring = '"""The mirror used to write docs/ghost/index.html and no longer does."""\n'

    for label, source in (("log", log_line), ("comment", comment), ("docstring", docstring)):
        assert frozen_pages(root, {label: source}) == ["docs/ghost/index.html"], (
            "{} silenced the control".format(label))


def test_the_segmentwise_path_form_counts_as_a_writer(tmp_path):
    """`PROJECT / "docs" / "kept"` is a declaration, and a scan that only reads the slash
    literal would call its page an orphan. Named because the mirror step this control was born
    from writes its destination exactly that way."""
    root = tmp_path / "docs"
    (root / "kept").mkdir(parents=True)
    (root / "kept" / "index.html").write_text("Generated: 2026-09-20T01:00:00Z")

    assert frozen_pages(root, {"a.py": 'DEST = PROJECT / "docs" / "kept"'}) == []
    assert frozen_pages(root, {"a.py": "x = 1"}) == ["docs/kept/index.html"]


@pytest.mark.parametrize("broken", ["no_root", "no_sources", "no_pages"])
def test_every_degenerate_input_refuses_rather_than_passing(tmp_path, broken):
    """An unavailable check is a FAILED check. Each of these would otherwise be the cheapest
    possible silencing: point the control at nothing and collect a green."""
    root = tmp_path / "docs"
    sources = {"a.py": "x = 1"}
    if broken == "no_root":
        pass  # never created
    else:
        root.mkdir(parents=True)
        if broken == "no_pages":
            (root / "notes.md").write_text("not a page")
        else:
            (root / "p.html").write_text("Generated: 2026-09-20T01:00:00Z")
            sources = {}

    with pytest.raises(AssertionError):
        frozen_pages(root, sources)


def test_a_missing_or_reshaped_workflow_refuses(tmp_path):
    """The subject is derived from the workflow, so an unreadable workflow means the control
    does not know what is served -- which is a refusal, never a default to `docs`."""
    with pytest.raises(AssertionError):
        pages_root(tmp_path / "absent.yml")

    reshaped = tmp_path / "w.yml"
    reshaped.write_text("jobs:\n  deploy:\n    steps:\n      - uses: actions/checkout@v5\n")
    with pytest.raises(AssertionError):
        pages_root(reshaped)

    unparseable = tmp_path / "bad.yml"
    unparseable.write_text("jobs: [unclosed\n")
    with pytest.raises(AssertionError):
        pages_root(unparseable)

    assert pages_root() == "docs"


def test_the_root_is_read_from_the_structure_not_the_text(tmp_path):
    """A reformat that a regex would lose must still answer, and a comment must not answer.

    The subject is derived, so losing it is the quiet failure: a control pointed at nothing
    reports a clean site. Both shapes below break a text match and neither changes what the
    workflow actually uploads.
    """
    quoted = tmp_path / "quoted.yml"
    quoted.write_text(
        "jobs:\n  deploy:\n    steps:\n      - name: Upload\n"
        "        uses: actions/upload-pages-artifact@v5\n"
        "        with:\n          retention-days: 1\n          path: 'public/'\n"
    )
    assert pages_root(quoted) == "public"

    commented = tmp_path / "commented.yml"
    commented.write_text(
        "jobs:\n  deploy:\n    steps:\n"
        "      # upload-pages-artifact used to run here with path: docs\n"
        "      - uses: actions/checkout@v5\n"
    )
    with pytest.raises(AssertionError):
        pages_root(commented)
