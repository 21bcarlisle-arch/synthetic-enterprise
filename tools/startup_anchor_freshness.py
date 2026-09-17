"""The startup surface must carry its own COMPUTED age, so it can be stale but never silently so.

REUSE: tools/startup_anchor_freshness.py
CLASS: CUSTOM
INDEX: searched "freshness", "stale", "anchor", "startup", "last updated". The near rows are
       `tools/assert_deployed_bytes_are_served.py` (asserts the EDGE serves the commit just
       deployed -- a transport check, and it passes here) and `tools/publish_surface_gate.py`
       (gates whether a publish's FIGURES are right). Neither asks the question this one asks:
       whether a document's own claim about its age agrees with its age. That question has no
       existing home, and the incident below is what happens without one.

WHY THIS EXISTS -- and the answer was neither of the two candidates
------------------------------------------------------------------
Director console, 2026-09-05: another session's startup read PROJECT_OVERVIEW.md, LATEST.md and
ASSUMPTIONS.md from the published Pages URLs "and found them dated 3-10 August", against an origin
whose LATEST.md had been written at 07:06Z that morning. Two hypotheses were offered: the anchor is
stale at the edge, or the files have moved since the site rebuild.

Measured, both are false:

  * THE EDGE IS FRESH. All three fetch byte-identical to `origin/main` (md5, 2026-09-05), with
    `age: 0` and a `last-modified` of that morning.
  * NOTHING MOVED. Same paths, served correctly. The director's own check missed them only because
    the repo paths are `docs/PROJECT_OVERVIEW.md` and `docs/market_research/ASSUMPTIONS.md`, not
    the repo-root paths.

What the session actually read was each document's OWN self-declared date sentence -- and two of
the three are hand-typed, so nothing computes them and nothing can notice when they rot:

  * `PROJECT_OVERVIEW.md` says "Last updated: 2026-08-09". Its last commit is 2026-08-17. The
    sentence is wrong about its own document by 8 days, and its "23,826 tests collected" was 2,905
    behind CLAUDE.md on the day it was read. THIS IS THE DEFECT: not old, but lying about being old.
  * `ASSUMPTIONS.md` says "Last seeded: 2026-08-10" and genuinely last changed 2026-08-10. Old, and
    honest about it. That is not a defect and this module does not treat it as one.
  * `LATEST.md` says "2026-09-05T07:06:34Z" and is machine-stamped. Correct.

THE AGGRAVATING FACT, and the reason "silently" is the right word. The one automatic freshness
signal a reader can check -- HTTP `last-modified` -- is USELESS HERE AND WORSE THAN ABSENT. The
GitHub Pages mirror uploads the whole `docs/` tree as a single artefact, so a `docs/status/`
publish restamps every file in the mirror. A reader fetching a 19-day-old PROJECT_OVERVIEW.md is
told `last-modified: today`. The transport actively asserts freshness the content does not have.

WHAT IS REFUSED, AND WHAT DELIBERATELY IS NOT
---------------------------------------------
REFUSED: a declared date that DISAGREES with the document's real age (`LIES`). That is a property,
not today's answer -- it stays green when the document is updated and stays green when it rots for
a year with an honest line, and it is always satisfiable by editing one sentence.

NOT REFUSED: age itself. An anchor that is genuinely old and says so is working as intended, and a
control keyed to age would go red for a reason nobody could act on and would be turned off -- the
"headroom control that reds because it became unsatisfiable" shape. Age is REPORTED instead, into
`docs/status/STARTUP_ANCHORS.md`, which ships by the same push as LATEST.md (the route already
proven to reach the edge fresh) and which the anchor block itself now points at. So an undated or
stale anchor is still stale -- it just cannot be stale WITHOUT THE READER BEING TOLD, which is the
whole of the director's instruction.

FAIL-CLOSED. Git unavailable, the anchor block unparseable, or fewer than `MIN_ANCHORS` anchors
recovered all REFUSE. The floor is what stops the cheapest possible silencing of a register-driven
control: deleting the rows. An empty anchor set is a broken check, never a clean pass.

THE SECOND HALF, added 2026-09-16 (H47): THE DATE WAS GATED AND THE FIGURES WERE NOT
-----------------------------------------------------------------------------------
Everything above grades one word of the startup header -- its DATE. The same sentence states four
QUANTITIES, and in the incident that produced this module three of them were wrong by 3.7x, 15x and
2,905 tests while the date was wrong by 8 days. A header can therefore be perfectly fresh by the
check above and still tell a session it is orienting on a project a fifteenth of this one's size:
freshness is not agreement, and nothing here asked whether the figures were COMPUTED at all.

What is graded is not "is the figure today's number" -- that control would red on every commit and
be turned off within a day. It is: **does each stated figure lie inside the range its own named
source actually took, over the window the date sentence is already allowed to be wrong by?** A
figure computed from the source when the header was written is inside that band by construction; a
figure typed from memory is not. It is a property, not today's answer -- it stays green as the repo
grows, it reds in EITHER direction (a figure too high and a figure too low are both outside the
band), and it is always satisfiable by recomputing one sentence.

The sources are the ones the header itself names, not a second opinion: the commits figure is
`git rev-list --count`; the lines and modules figures are the `*.py` blobs in the index; the tests
figure is what CLAUDE.md's Build line carries, which is what the incident measured the header
against ("2,905 behind CLAUDE.md on the day it was read") and what the live site is generated from.

AND THE TESTS FIGURE ALONE NEEDED A SECOND SOURCE (Expert Hour EH-3, 2026-09-17). Three of those
four sources are git, which nobody can type into. The Build line is another HAND-TYPED number, so
the band it gives is degenerate -- low == high == stated -- and the leg was clearable by typing:
update both documents in one commit and the check agrees with you. It was not a hypothetical. On
the day this paragraph was written both documents said 26,731, the Build line had not moved in 20
days and 1,440 commits, a real collection returned 36,835, this check said AGREES, and the live
site published the typed number. `_collectible_test_functions` is the independent bound, and it
costs nothing this function was not already paying. It floors the figure and does NOT cap it --
`@parametrize` expansion is unbounded, so only a real collection could -- and the published table
says so in the reader's own words rather than letting one AGREES look like another.
"""
from __future__ import annotations

import ast
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:  # run as a script by the publish path, not as `-m`
    sys.path.insert(0, str(PROJECT))

OVERVIEW = PROJECT / "docs" / "PROJECT_OVERVIEW.md"
OUT = PROJECT / "docs" / "status" / "STARTUP_ANCHORS.md"

#: GitHub Pages serves the repo's `docs/` directory as the site root.
PAGES_ROOT = "https://21bcarlisle-arch.github.io/synthetic-enterprise/"
DOCS_ROOT = "docs"

#: rel path -> the sentence the anchor block uses to say what it is for. Filled by `anchor_paths`.
_LABELS: dict[str, str] = {}

#: Below this many parsed anchors the check is not measuring the startup surface, so it refuses.
#: Four is the count the anchor block has carried since it was written; a fifth added later raises
#: nothing, a deletion below four refuses. Keyed to "the block still describes a surface", not to
#: which four are in it today.
MIN_ANCHORS = 4

#: How far a document's own date sentence may sit from its real last-change date before the
#: sentence counts as a claim rather than a rounding. Three days absorbs a doc edited over a
#: weekend and stamped on the Friday; the incident's own gap was 8 days.
DECLARED_DATE_TOLERANCE_DAYS = 3

#: Purely descriptive: the age at which the published table calls an anchor OLD for the reader.
#: Nothing refuses on it -- see the module docstring.
REPORTED_STALE_AFTER_DAYS = 14

_ANCHOR_LINE_RE = re.compile(
    r"^\s*-\s+(?P<label>[^:]+?):\s*(?P<url>" + re.escape(PAGES_ROOT) + r"\S+)\s*$", re.M)
#: A document's own claim about when it was last touched. Deliberately narrow: only the leading
#: lines are read, because a date deep in an append-log is a fact ABOUT the log, not about the file.
_DECLARED_RE = re.compile(
    r"(?:last\s+updated|last\s+seeded|generated)\s*:?\s*"
    r"(\d{4}-\d{2}-\d{2})", re.I)
_DECLARED_HEAD_LINES = 10

#: Each quantity the startup header states -> the source the header itself says it comes from.
#: Named here so a refusal can tell the reader what to recompute, and so no figure can be checked
#: against a source the sentence never claimed.
FIGURE_SOURCES = {
    "commits": "`git rev-list --count`",
    "tests": "CLAUDE.md's Build line, floored by the test functions in the git index",
    "lines": "newlines across every `*.py` in the git index",
    "modules": "the count of `*.py` in the git index",
}

#: Which tracked paths pytest will collect from. There is no `testpaths`, `norecursedirs`,
#: `collect_ignore` or `python_files` anywhere in this repository (measured 2026-09-17, across
#: every `conftest.py`, `pyproject.toml`, `pytest.ini`, `setup.cfg` and `tox.ini` at HEAD), so
#: collection is pytest's default and these two spellings are exactly what it walks into.
def _is_test_file(rel: str) -> bool:
    """pytest's default `python_files`, over a PATH -- `test_*.py` and `*_test.py`.

    Spelled with `str` methods rather than a regex on purpose. This prefilter sits in the same
    function that holds Python source in a local, and `substring_source_scan_census` reads a regex
    there as a substring scan OF that source -- which is the very thing
    `_collectible_test_functions` exists to avoid doing. The source itself goes through the AST;
    this only ever looks at a name.
    """
    name = rel.rpartition("/")[2]
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def _collectible_test_functions(source: bytes) -> int:
    """How many test items pytest will collect from this file, read as CODE and not as text.

    A collected item is never fewer than one per test function -- skipped and xfailed functions
    are still COLLECTED, and `@parametrize` only ever multiplies -- so this is a floor a truthful
    collection count cannot sit below. See `figure_verdicts` for what it is a floor FOR.

    THE FIRST DRAFT WAS A REGEX OVER THE RAW BYTES AND THE GATE WAS RIGHT TO REFUSE IT
    (`tests/architecture/test_a_control_reads_python_as_code.py`, 2026-09-17). It over-counted by
    25 against the real tree, because `def test_x():` inside a STRING LITERAL is not a test -- this
    repository's own control fixtures write exactly that text into temporary files. A floor that
    counts prose can rise above the truth it is bounding and red an honest figure, which is the
    one failure this direction must not have. `python_code_text.searchable()` was tried, as the
    control's message suggests, and removed only ONE of the 25: it blanks comments and bare string
    expressions, and these literals are call arguments. It also cost 5.7s against the AST's 1.4s.
    So the sanctioned reading here is the AST, and it is both the correct one and the cheap one.

    Matched to what pytest ACTUALLY collects rather than to every `def test_`: module-level
    functions, plus methods of `Test`-prefixed classes. A method of a class pytest ignores, or a
    function nested inside another function, is not collected and would inflate the floor.

    Unparseable source counts ZERO rather than refusing. That is the safe direction for a bound:
    under-counting keeps it a floor, and a file that will not parse fails collection loudly
    anyway.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return 0
    total = 0
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total += node.name.startswith("test_")
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            total += sum(m.name.startswith("test_") for m in node.body
                         if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
    return total
#: Matched on the NUMBER AND ITS NOUN, so rewording the sentence around a figure keeps passing and
#: deleting the figure refuses. Each pattern is anchored on the words the header uses to say what
#: the quantity IS -- never on its current value.
#:
#: THE TRAILING `+` IS PART OF THE FIGURE, not a reason to stop seeing one (Expert Hour, 2026-09-17,
#: found by replaying the incident that produced this module through it). The header that cost a
#: session its bearings said "2,500+ commits ... 360+ Python modules", and a pattern ending the
#: number at `[\d,]+` read those as NO FIGURE STATED -- so the replay refused, but by the
#: unstated-figure leg, and the OVERSTATES/UNDERSTATES machinery that is the whole substance here
#: was never reached by the only real instance of the defect. The hedge is exactly how a person
#: types a number they know is going stale; it is where this class LIVES. `~` and `over` already
#: matched because they sit to the LEFT of the digits. Grading the bare number is right: "9,000+
#: commits" against a true 9,385 is an honest claim, and "2,500+" against 9,385 is not one the `+`
#: can rescue.
_FIGURE_RES = {
    "commits": re.compile(r"([\d,]+)\+?\s+commits\b", re.I),
    "tests": re.compile(r"([\d,]+)\+?\s+tests\s+collected\b", re.I),
    "lines": re.compile(r"([\d,]+)\+?\s+lines\b", re.I),
    "modules": re.compile(r"([\d,]+)\+?\s+tracked\s+Python\s+modules\b", re.I),
}


#: Directories the GitHub Pages workflow's `paths-ignore` excludes, plus the retired shadow mirror.
#: A path under these is not published, so a reader cannot be sent to it.
_UNPUBLISHED = ("docs/observability/", "docs/staging/", "docs/market_data/", "docs/state/",
                "docs/snapshots/", "docs/design/", "docs/instructions/", "docs/claude/",
                "docs/domain_artefact_library/", "docs/review_gates/", "docs/shadow/")
#: Extensions a person opens and reads. A JSON feed is machinery output, not an orientation surface.
_READER_SUFFIXES = (".md", ".txt", ".yaml", ".yml", ".jsonl")

#: Surfaces `discover_maintained_surfaces` structurally CANNOT see, each with the reason. Its scan
#: reads module-level constants built in ONE expression from a "docs" segment; a path assembled in
#: two steps is invisible to it. Named rather than papered over, and
#: `test_the_named_exemptions_are_still_undiscoverable` reds if one becomes discoverable, so an
#: exemption cannot outlive its reason.
UNDISCOVERABLE = {
    # background/direction.py: DIRECTION_DIR = PROJECT_DIR / "docs" / "direction"
    #                          DIRECTION_PATH = DIRECTION_DIR / "DIRECTION.yaml"
    "docs/direction/DIRECTION.yaml": "background/direction.py builds it in two steps",
    "docs/direction/decisions.jsonl": "background/direction.py builds it in two steps",
}


def discover_maintained_surfaces(root: Path | None = None) -> dict[str, set[str]]:
    """Published reader surfaces that MACHINERY declares a path to -> the modules declaring them.

    THE CLASS THIS EXISTS TO CLOSE (director, 2026-09-06): "every operating change we make is
    invisible to a fresh session until it trips over it." The anchor block was a hand-kept list
    naming what the project IS -- PROJECT_OVERVIEW, LATEST, ASSUMPTIONS, all of which predate the
    delivery seat, DIRECTION.yaml, the class registers and the stretch log. Measured the same day:
    two of the five named surfaces had ZERO commits in fourteen days, while the five most actively
    maintained reasoning surfaces were named nowhere. A week of daily prose was written, rendered
    and published, and nobody outside the machine found it.

    Frequency is the wrong discriminator and was tried first: it ranks the retired `docs/shadow/`
    mirror pages above `knowledge_map.md`, and it would never have caught the stretch log, which
    was two commits old on the day it was missed. The structural signal is that a TOOL DECLARES A
    PATH TO IT -- a surface the machine maintains is one a reader can be sent to, however new.
    """
    import ast as _ast
    import re as _re

    root = root or PROJECT
    found: dict[str, set[str]] = {}
    for tree in ("tools", "background"):
        for f in sorted((root / tree).glob("*.py")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
                parsed = _ast.parse(text)
            except (OSError, SyntaxError):
                continue
            # THE PREFILTER IS WHY THIS COSTS A SECOND AND NOT FORTY (2026-09-17).
            # `ast.get_source_segment` re-splits the WHOLE file into lines on every call, so
            # calling it once per `Assign` made this O(assigns x file size): 42.2s over
            # tools/ + background/ to return EIGHT surfaces, paid by every commit that stages
            # an anchor. Measured, not reasoned: 18,947 calls become 450, and 218 of the 445
            # modules are never segmented at all.
            #
            # WHERE THAT NUMBER CAME FROM: `tools/time_the_commit_hook_chain.py`, which times
            # the pre-commit chain step by step. Until it existed the chain had ONE number per
            # commit, so this step's 42s was invisible inside a 333s total and every argument
            # about what to cut was an argument about what LOOKED expensive.
            #
            # IT IS EXACT, NOT AN APPROXIMATION, and that is the only reason it is allowed to
            # be here -- a speed-up that narrows a control is the class this repo keeps paying
            # for. The regex below needs the literal `"docs"` INSIDE the node's own source
            # segment; that segment lies wholly within lines `lineno..end_lineno`, so a node
            # spanning no line that contains `"docs"` cannot match. The line set is a SUPERSET
            # of the matching nodes (a `"docs"` sitting before `col_offset` on the opening line
            # keeps the node in, and `get_source_segment` then returns the true segment and the
            # regex simply declines it), so every surface the unfiltered walk found is still
            # found. `test_the_prefilter_finds_exactly_what_the_unfiltered_walk_finds` is the
            # control, and it compares the two implementations over the real tree.
            if '"docs"' not in text:
                continue
            docs_lines = {i + 1 for i, line in enumerate(text.splitlines())
                          if '"docs"' in line}
            for node in _ast.walk(parsed):
                if not isinstance(node, _ast.Assign):
                    continue
                if not any(ln in docs_lines
                           for ln in range(node.lineno,
                                           (node.end_lineno or node.lineno) + 1)):
                    continue
                src = _ast.get_source_segment(text, node) or ""
                m = _re.search(r'"docs"\s*/\s*(.+)', src, _re.S)
                if not m:
                    continue
                segs = _re.findall(r'"([^"]+)"', m.group(1))
                if not segs:
                    continue
                rel = "docs/" + "/".join(segs)
                if rel.startswith(_UNPUBLISHED) or not rel.endswith(_READER_SUFFIXES):
                    continue
                found.setdefault(rel, set()).add(f"{tree}/{f.name}")
    return found


def unnamed_surfaces(root: Path | None = None) -> dict[str, set[str]]:
    """Machine-maintained published surfaces the anchor block does not send a reader to."""
    try:
        named = set(anchor_paths())
    except AnchorRefusal:
        return {}
    return {k: v for k, v in discover_maintained_surfaces(root).items() if k not in named}


class AnchorRefusal(RuntimeError):
    """The check could not be performed. Never raised for a merely stale anchor."""


def _git(*args: str) -> str:
    done = subprocess.run(("git", *args), cwd=str(PROJECT),
                          capture_output=True, text=True, timeout=60)
    if done.returncode != 0:
        raise AnchorRefusal(f"git {' '.join(args)} failed: {done.stderr.strip()[:200]}")
    return done.stdout.strip()


def anchor_paths(overview_text: str | None = None) -> list[str]:
    """Repo paths for the anchors the startup surface DECLARES, read from the block that declares
    them rather than from a list this module also authors.

    Deriving the subject from the document keeps the two from drifting, which is the defect this
    whole module is about. `MIN_ANCHORS` is what stops the derivation degrading into "no anchors,
    nothing to check" when the block is edited or the file is unreadable.
    """
    if overview_text is None:
        try:
            overview_text = OVERVIEW.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AnchorRefusal(f"cannot read the anchor block at {OVERVIEW}: {exc}") from exc

    paths = []
    for m in _ANCHOR_LINE_RE.finditer(overview_text):
        url = m.group("url")
        rest = url[len(PAGES_ROOT):].split("#", 1)[0].split("?", 1)[0]
        if rest and not rest.endswith("/"):
            rel = f"{DOCS_ROOT}/{rest}"
            paths.append(rel)
            # The label is the sentence beside the link. Taken from the SAME line the path came
            # from, so the table cannot describe one anchor and age another, and so "what this is
            # for" is never a second list to maintain.
            _LABELS[rel] = m.group("label").strip()
    # Order-preserving dedup: the block lists PROJECT_OVERVIEW.md as "this document".
    seen, ordered = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    if len(ordered) < MIN_ANCHORS:
        raise AnchorRefusal(
            f"only {len(ordered)} startup anchors parsed from {OVERVIEW.name} (floor is "
            f"{MIN_ANCHORS}). An empty or shrunken anchor set is a broken check, not a clean one -- "
            "a control that iterates a register is silenced by deleting the rows."
        )
    return ordered


def true_last_change(path: str, today: dt.date | None = None) -> dt.date | None:
    """When this anchor's CONTENT last changed, answered against the tree a commit would create.

    Git history for a path that is not being touched; TODAY for one that is, because a file with
    uncommitted or staged changes is a file whose content is changing now.

    THE ASYMMETRY THIS EXISTS TO AVOID, found by running the first draft against the very edit that
    was fixing the defect: `declared_date` reads the WORKING TREE and this read only HEAD, so from
    the moment anyone corrected a date sentence until they committed it, the two sides described
    different trees and the check refused -- on every commit, for every lane, for the whole window,
    and most loudly at the person doing the repair. The same shape appears twice in this project's
    own record: a measurement whose subject is another process's uncommitted copy, and a staged
    repair invisible to a gate whose subject is HEAD. Both sides must read one tree.

    mtime is deliberately not used: it would answer for a `touch`, and every fresh clone would
    disagree with every other. `None` means the path is in neither HEAD nor the working tree.
    """
    today = today or dt.date.today()
    # STAGED, not merely dirty -- the subject is the tree THIS COMMIT creates, and another lane's
    # open working-tree edit is not part of it.
    #
    # The first draft used `git status --porcelain`, which counts unstaged edits too, and it was
    # wrong the first time it met the real tree: a concurrent lane was mid-append to
    # ASSUMPTIONS.md, so this reported the file as changing today, called its honest
    # "Last seeded: 2026-08-10" a lie, and refused -- pointing at a file that lane held dirty and
    # that could not be corrected without carrying their uncommitted work into someone else's
    # commit. Scoping to the index gives the property that actually belongs here: the lane whose
    # commit makes a document's date wrong is the lane asked to fix it, and no other.
    if _git("diff", "--cached", "--name-only", "HEAD", "--", path):
        return today
    out = _git("log", "-1", "--format=%cI", "HEAD", "--", path)
    if not out:
        # Distinguish "absent at this revision" from "git could not answer" -- `git log` returns
        # empty for both, and treating an unanswerable query as a missing file would fabricate a
        # MISSING refusal out of a transient git failure.
        if _git("ls-tree", "--name-only", "HEAD", "--", path):
            raise AnchorRefusal(
                f"{path} is in HEAD but git could not date it -- the check cannot be performed")
        return None
    return dt.datetime.fromisoformat(out).date()


def _declared_from_text(text: str) -> dt.date | None:
    head = "\n".join(text.splitlines()[:_DECLARED_HEAD_LINES])
    m = _DECLARED_RE.search(head)
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def declared_date(path: str) -> dt.date | None:
    """What the document CLAIMS about its own age, or None if it makes no claim."""
    try:
        text = (PROJECT / path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return _declared_from_text(text)


def stated_figures(overview_text: str | None = None) -> dict[str, int]:
    """The quantities the startup header STATES, read from the header that states them.

    Read from the same narrow head-of-document window as `declared_date`, and for the same reason:
    a figure deep in the body is a fact about a section, not the sentence a session orients on.

    FAIL-CLOSED on a missing figure, which is the cheapest possible silencing of this half of the
    check -- delete the number and there is nothing left to disagree with. A reworded header that
    still states the quantity keeps passing (only the number and its noun are matched); a header
    that drops one refuses and names which.
    """
    if overview_text is None:
        try:
            overview_text = OVERVIEW.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AnchorRefusal(f"cannot read the startup header at {OVERVIEW}: {exc}") from exc
    head = "\n".join(overview_text.splitlines()[:_DECLARED_HEAD_LINES])

    found: dict[str, int] = {}
    for key, pattern in _FIGURE_RES.items():
        m = pattern.search(head)
        if m:
            found[key] = int(m.group(1).replace(",", ""))
    missing = [k for k in _FIGURE_RES if k not in found]
    if missing:
        raise AnchorRefusal(
            f"the startup header states no {', '.join(missing)} figure. The header's quantities are "
            "what a session orients on; a figure that is not stated cannot be checked against the "
            f"source it comes from ({', '.join(FIGURE_SOURCES[k] for k in missing)}), and an "
            "unstated figure is a broken check rather than a clean one."
        )
    return found


def _tests_figure(claude_md: str) -> int | None:
    """The full-suite collection count CLAUDE.md's Build line carries.

    The Build line specifically, not the first "tests collected" in the file: this project's own
    phase-close prose quotes partial, scoped counts in the same words, and a first-match scan
    landing on one of those is a defect `generate_dashboard_data` has already paid for twice.
    """
    m = re.search(r"\*\*Build:\*\*\s*([\d,]+)\s+tests collected", claude_md)
    return int(m.group(1).replace(",", "")) if m else None


def _figures_at(rev: str) -> dict[str, int]:
    """Every stated figure, computed from its named source at one revision.

    `tests_floor` is not a stated figure and gets no row of its own. It is the INDEPENDENT bound
    the `tests` figure had none of -- see `figure_verdicts`. It costs nothing: this function
    already streams every `*.py` blob at `rev` to count newlines, so the test functions are counted
    in the same pass rather than by a second read of the tree.
    """
    names = _git("ls-tree", "-r", "--name-only", rev).splitlines()
    modules = [n for n in names if n.endswith(".py")]
    lines = 0
    test_funcs = 0
    if modules:
        spec = "".join(f"{rev}:{n}\n" for n in modules).encode()
        done = subprocess.run(("git", "cat-file", "--batch"), cwd=str(PROJECT),
                              input=spec, capture_output=True, timeout=300)
        if done.returncode != 0:
            raise AnchorRefusal("git cat-file could not read the index's modules at "
                                f"{rev[:12]} -- the figure check cannot be performed")
        blob, i, k = done.stdout, 0, 0
        while i < len(blob):
            j = blob.index(b"\n", i)
            size = int(blob[i:j].split()[2])
            body = blob[j + 1:j + 1 + size]
            lines += body.count(b"\n")
            if _is_test_file(modules[k]):
                test_funcs += _collectible_test_functions(body)
            i = j + 1 + size + 1
            k += 1
    out = {
        "commits": int(_git("rev-list", "--count", rev)),
        "modules": len(modules),
        "lines": lines,
        "tests_floor": test_funcs,
    }
    # None, not a refusal: CLAUDE.md's Build line only exists since the 2026-08-28 rewrite, so a
    # window reaching further back has NO SOURCE for the test figure rather than a wrong one.
    # Refusing there would wedge on a document that is merely old and honest -- the exact shape the
    # age half of this module deliberately does not refuse on -- and the route an author could
    # abuse it by (back-dating the header past the source) is already closed by the LIES check,
    # which ties the declared date to the document's real last change.
    out["tests"] = _tests_figure(_git("show", f"{rev}:CLAUDE.md"))
    return out


def _figures_in_working_tree() -> dict[str, int]:
    """The same figures for the tree on disk, for a header being written TODAY.

    The band's upper end has to reach the tree the author is looking at, or a header written and
    committed in the same hour would be graded against a repository that no longer exists. This is
    the same "both sides must read one tree" lesson `true_last_change` records.
    """
    modules = [n for n in _git("ls-files", "--", "*.py").splitlines() if n]
    lines = 0
    test_funcs = 0
    for rel in modules:
        try:
            body = (PROJECT / rel).read_bytes()
        except OSError:
            continue  # deleted-but-tracked: the committed copy already sets the other bound
        lines += body.count(b"\n")
        if _is_test_file(rel):
            test_funcs += _collectible_test_functions(body)
    tests = _tests_figure((PROJECT / "CLAUDE.md").read_text(encoding="utf-8", errors="replace"))
    return {
        "commits": int(_git("rev-list", "--count", "HEAD")),
        "modules": len(modules),
        "lines": lines,
        "tests_floor": test_funcs,
        "tests": tests if tests is not None else 0,
    }


def _band_and_ends(declared: dt.date) -> tuple[dict[str, tuple], dict[str, tuple[bool, bool]]]:
    """The band, AND whether each figure's source was readable at each end of the window.

    Both come off ONE pass of the two expensive revision reads. The ends are what tells the two
    causes of a `(None, None)` band apart, and until this existed they were indistinguishable --
    see `figure_verdicts` for why that mattered.
    """
    low_rev = _git("rev-list", "-1",
                   f"--before={declared - dt.timedelta(days=DECLARED_DATE_TOLERANCE_DAYS)} 00:00:00",
                   "HEAD")
    if not low_rev:
        # A declared date older than the repository itself: the floor is the first commit there was.
        low_rev = _git("rev-list", "--max-parents=0", "HEAD").splitlines()[-1]
    high_rev = _git("rev-list", "-1",
                    "--before="
                    f"{declared + dt.timedelta(days=DECLARED_DATE_TOLERANCE_DAYS + 1)} 00:00:00",
                    "HEAD")
    head = _git("rev-parse", "HEAD")
    low, high = _figures_at(low_rev), _figures_at(high_rev or head)
    if not high_rev or high_rev == head:
        live = _figures_in_working_tree()
        high = {k: v if (v is None or live[k] is None) else max(v, live[k])
                for k, v in high.items()}
    band = {k: (None, None) if (low[k] is None or high[k] is None)
            else (min(low[k], high[k]), max(low[k], high[k])) for k in low}
    ends = {k: (low[k] is not None, high[k] is not None) for k in low}
    return band, ends


def figure_band(declared: dt.date) -> dict[str, tuple[int, int]]:
    """For each stated figure, the range its named source took across the declared date's window.

    The window is `DECLARED_DATE_TOLERANCE_DAYS` either side of the declared date -- the same slack
    the date sentence itself is already granted above, rather than a second tolerance minted here.
    Tying the two means the header may be written one day and land the next without this going red,
    and it cannot be widened without widening the date check that every publish already runs.
    """
    return _band_and_ends(declared)[0]


def figure_verdicts(overview_text: str | None = None) -> list[dict]:
    """One row per stated figure: what the header says, what its source could have said, verdict."""
    stated = stated_figures(overview_text)
    if overview_text is None:
        overview_text = OVERVIEW.read_text(encoding="utf-8", errors="replace")
    declared = _declared_from_text(overview_text)
    if declared is None:
        raise AnchorRefusal(
            "the startup header states figures but no date, so there is no window to compute them "
            "over. A quantity with no as-of is unfalsifiable.")
    band, ends = _band_and_ends(declared)
    rows = []
    for key in sorted(stated):
        low, high = band[key]
        value = stated[key]
        floor = band["tests_floor"][0] if key == "tests" else None
        if floor is not None and value < floor:
            # EH-3, THE LEG THAT WAS GRADED AGAINST A COPY OF ITSELF (Expert Hour, 2026-09-17).
            # Three of the four figures come from git, which nobody can type into. `tests` came
            # from CLAUDE.md's Build line -- another hand-typed number -- so the band was
            # DEGENERATE (low == high == stated) and the leg was clearable by typing: an author
            # who invents a count and updates both documents in one commit was agreed with.
            #
            # It was not hypothetical. Measured the day this was written: both documents said
            # 26,731, the Build line had not moved since the spelling was introduced 20 days and
            # 1,440 commits earlier, a real collection of a clean HEAD extract returned 36,835,
            # and this check said AGREES while the live site published the typed number.
            #
            # The floor is what git can answer on its own: a collected item is never fewer than
            # one per test function, class-nested/skipped/xfailed functions are all still
            # collected, and `@parametrize` only multiplies. So a stated collection count BELOW
            # the test functions the index carries is not a matter of tolerance -- no truthful
            # collection can sit there. Taken at the LOW end of the window, so a figure computed
            # honestly anywhere inside it clears the bound rather than racing the suite's growth.
            #
            # Checked BEFORE the band, and before `low is None`: the whole point is that this
            # bound does not depend on the typed source being present, readable, or right.
            verdict = "BELOW_THE_INDEX_FLOOR"
        elif low is None:
            # TWO CAUSES, ONE BAND, AND ONLY ONE OF THEM IS HONEST (Expert Hour, 2026-09-17). A
            # source that did not exist yet cannot grade the figure and saying so is the result.
            # A source that WAS readable at the start of the window and is not readable at the end
            # did not go missing by the passage of time -- something stopped it being readable, and
            # `UNGRADED` there is the escape hatch the reviewer named: reword one line in the
            # document the source lives in and this leg switches itself off with a green gate and a
            # published table that says the figure merely could not be checked.
            #
            # That route is REAL and not hypothetical here: the test figure's source is matched on a
            # literal `**Build:**`, the pre-2026-08-28 spelling `Build:` returns None, and a prior
            # audit has already deleted that line once. The module's own note closes the BACK-DATING
            # route to `UNGRADED` and points at the LIES check to do it -- but the LIES check grades
            # the date of the header's own document and can see nothing about a source living in
            # another one. Keyed to the property (the source was there and then was not), never to
            # the date the source happened to appear.
            verdict = "SOURCE_GONE" if ends[key] == (True, False) else "UNGRADED"
        elif value < low:
            verdict = "UNDERSTATES"
        elif value > high:
            verdict = "OVERSTATES"
        else:
            verdict = "AGREES"
        rows.append({"figure": key, "source": FIGURE_SOURCES[key], "stated": value,
                     "band_low": low, "band_high": high, "floor": floor, "verdict": verdict})
    return rows


def figure_refusals(rows: list[dict]) -> list[dict]:
    """A stated figure its own source never carried, in either direction.

    `UNGRADED` is deliberately not a refusal and is deliberately not silence either: it is printed
    on the published surface, because "we cannot tell" is a result a reader is owed.

    `SOURCE_GONE` IS a refusal, and it is the same figure in the same `(None, None)` band: the
    difference is that nobody chose for the source not to exist in 2026-08, and somebody did choose
    to stop it being readable today. An unearned "we cannot tell" is how this check gets turned off.

    `BELOW_THE_INDEX_FLOOR` is a refusal on evidence the typed source cannot reach -- see
    `figure_verdicts`. It is the only leg here that survives the Build line being wrong, absent or
    deleted, which is exactly why it exists.
    """
    return [r for r in rows if r["verdict"] in ("OVERSTATES", "UNDERSTATES", "SOURCE_GONE",
                                                "BELOW_THE_INDEX_FLOOR")]


def assess(today: dt.date | None = None) -> list[dict]:
    """One row per declared anchor. Raises AnchorRefusal if the check cannot be performed."""
    today = today or dt.date.today()
    rows = []
    for path in anchor_paths():
        true = true_last_change(path, today)
        claimed = declared_date(path)
        age = (today - true).days if true else None
        drift = abs((claimed - true).days) if (claimed and true) else None

        if true is None:
            verdict = "MISSING"
        elif drift is not None and drift > DECLARED_DATE_TOLERANCE_DAYS:
            verdict = "LIES"
        elif claimed is None:
            verdict = "UNDATED"
        elif age is not None and age > REPORTED_STALE_AFTER_DAYS:
            verdict = "OLD"
        else:
            verdict = "FRESH"

        rows.append({
            "path": path, "true_last_change": true.isoformat() if true else None,
            "declared": claimed.isoformat() if claimed else None,
            "age_days": age, "declared_drift_days": drift, "verdict": verdict,
        })
    return rows


def refusals(rows: list[dict]) -> list[dict]:
    """Only a document that MISSTATES its own age, or is not in HEAD at all.

    A merely old anchor is not here on purpose: it is reported, not refused. See the docstring.
    """
    return [r for r in rows if r["verdict"] in ("LIES", "MISSING")]


def render(rows: list[dict], today: dt.date | None = None,
           figure_rows: list[dict] | None = None) -> str:
    today = today or dt.date.today()
    out = [
        "# Startup anchors -- computed freshness",
        "",
        f"Generated: {today.isoformat()} by `tools/startup_anchor_freshness.py`.",
        "",
        "Every age below is computed from this repository's history at HEAD. **Do not use the HTTP",
        "`last-modified` header of any of these URLs to judge freshness**: the GitHub Pages mirror",
        "uploads the whole `docs/` tree as one artefact, so any publish restamps every file in it,",
        "and a document untouched for a month is served with today's date.",
        "",
        "**If you are orienting, read this table first.** It is the whole set of surfaces the",
        "machine keeps current, and what each one is for. Anything not here is either static or",
        "not maintained -- so it tells you what the project IS, not what it is currently doing.",
        "",
        "| Anchor | What it is for | Last really changed | Age (days) | Verdict |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        out.append("| `{}` | {} | {} | {} | {} |".format(
            r["path"], _LABELS.get(r["path"], "—"),
            r["true_last_change"] or "not in HEAD",
            "?" if r["age_days"] is None else r["age_days"],
            r["verdict"]))
    out += [
        "",
        "`FRESH` recent · `OLD` genuinely old and honest about it (not a defect) · `UNDATED` states",
        f"no date of its own, so this table is the only age a reader gets · `LIES` its own date is "
        f"more than {DECLARED_DATE_TOLERANCE_DAYS} days from its real one · `MISSING` not in HEAD.",
        "",
    ]
    out += _render_figures(figure_rows)
    return "\n".join(out)


def _render_figures(rows: list[dict] | None) -> list[str]:
    """The header's own quantities, against what their sources could have said. On the surface and
    not in a footnote: a reader orienting on the header is entitled to the same reading the gate
    gets, including when the check could not be performed at all."""
    out = ["## The header's stated figures", ""]
    if rows is None:
        out += ["**Could not be computed on this run.** The figures below the title are therefore "
                "unchecked -- treat them as hand-typed.", ""]
        return out
    out += [
        "The sentence under the title states four quantities. Each is graded against the range its",
        f"own named source took over the {DECLARED_DATE_TOLERANCE_DAYS} days either side of the",
        "date that sentence declares -- so a figure computed when the header was written agrees, and",
        "one typed from memory does not.",
        "",
        "| Figure | Stated | Its source could have said | Verdict |",
        "|---|---|---|---|",
    ]
    for r in rows:
        if r["verdict"] == "BELOW_THE_INDEX_FLOOR":
            band = (f"**at least {r['floor']:,}** -- the test functions the git index carries, "
                    "which no collection can be smaller than")
        elif r["band_low"] is not None:
            band = f"{r['band_low']:,} – {r['band_high']:,}"
        elif r["verdict"] == "SOURCE_GONE":
            band = "**its source was readable at the start of this window and is not now**"
        else:
            band = "no source existed over this window"
        out.append("| {} | {:,} | {} ({}) | {} |".format(
            r["figure"], r["stated"], band, r["source"], r["verdict"]))
    out += ["", "`AGREES` inside the band · `OVERSTATES` / `UNDERSTATES` a number its own source "
            "never carried in that window · `UNGRADED` the source did not exist that far back, so "
            "this figure is unchecked and the reader is told so rather than reassured · "
            "`SOURCE_GONE` the source existed and stopped being readable inside this window, which "
            "is a refusal rather than an unchecked figure -- nobody chooses for a source not to "
            "have existed yet, and somebody chose this · `BELOW_THE_INDEX_FLOOR` the figure is "
            "smaller than the number of test functions the repository actually contains, which no "
            "collection can be.",
            "",
            "**These four verdicts are not all worth the same, and the reader is owed that.** "
            "`commits`, `lines` and `modules` are graded against git, which nobody can type into. "
            "`tests` is graded against another hand-typed line -- CLAUDE.md's Build stamp -- so "
            "its band is only as independent as that line is, and it is floored, but not capped, "
            "by the index. An `AGREES` on `tests` therefore rules out a count that is too small "
            "and does not rule out one that is too large: a figure inflated in both documents at "
            "once would still read as agreeing. That gap is named rather than papered over.",
            ""]
    return out


def staged_anchors(paths: list[str]) -> set[str]:
    """Which declared anchors THIS COMMIT changes."""
    out = _git("diff", "--cached", "--name-only", "HEAD", "--", *paths)
    return {line for line in out.splitlines() if line}


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    write = "--check" not in argv and "--gate" not in argv
    # `--overview PATH` grades the figures stated by ANOTHER copy of the header against this
    # repository's real sources. That is how the check is mutation-proved by hand -- type a wrong
    # number into a copy and watch it refuse -- and it is why the figure half takes text rather
    # than only reading `OVERVIEW` off disk.
    overview_text = None
    if "--overview" in argv:
        overview_text = Path(argv[argv.index("--overview") + 1]).read_text(
            encoding="utf-8", errors="replace")
        write = False
    try:
        rows = assess()
        # `--gate` (the pre-commit hook) judges ONLY anchors this commit touches. Refusing an
        # unrelated lane's commit because some other document's date sentence is wrong would wedge
        # the whole tree on a defect that lane did not cause and cannot fix without carrying
        # someone else's uncommitted work -- and "the red that refused your land was already at
        # HEAD" is a trap this project has paid for before. The publish path (no flag) still
        # reports every anchor, so nothing goes unseen; only the REFUSAL is scoped to the author.
        gated = "--gate" in argv
        if gated:
            touched = staged_anchors([r["path"] for r in rows])
            if not touched:
                return 0
            rows = [r for r in rows if r["path"] in touched]
        # Scoped exactly like the date refusal above, and for the same reason: the lane whose
        # commit makes the header's figures wrong is the lane asked to recompute them, and no
        # other. Unscoped, one rotted sentence would wedge every lane in the tree.
        overview_rel = str(OVERVIEW.relative_to(PROJECT))
        figure_rows = (figure_verdicts(overview_text)
                       if (not gated or overview_rel in touched or overview_text) else [])
    except AnchorRefusal as exc:
        # FAILS CLOSED. Unlike the next-step gate (one missed trailer is recoverable), an
        # unmeasurable startup surface is the exact condition being guarded against.
        print(f"[startup-anchors] REFUSED, check could not run: {exc}", file=sys.stderr)
        return 1

    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(render(rows, figure_rows=figure_rows), encoding="utf-8")
        print(f"[startup-anchors] wrote {OUT.relative_to(PROJECT)} ({len(rows)} anchors)")

    missing = unnamed_surfaces()
    if missing:
        for rel, mods in sorted(missing.items()):
            print(f"[startup-anchors] REFUSED: {rel} is a published surface the machine maintains "
                  f"({', '.join(sorted(mods))}) and the anchor block sends no reader to it.\n"
                  "An operating change nobody is told about is invisible to every fresh session "
                  "until it trips over it. Add it to PROJECT_OVERVIEW.md's anchor block with a "
                  "sentence saying what it is for.", file=sys.stderr)
        return 1

    bad_figures = figure_refusals(figure_rows)
    for r in bad_figures:
        if r["verdict"] == "SOURCE_GONE":
            print(f"[startup-anchors] REFUSED: the startup header's {r['figure']} figure says "
                  f"{r['stated']:,} and can no longer be graded: {r['source']} was readable at the "
                  "start of the window its own date declares and is not readable at the end. That "
                  "is a source that was taken away, not one that never existed, and leaving it as "
                  "an unchecked figure is how this check gets switched off. Restore the source, or "
                  "point this figure at the one that replaced it.", file=sys.stderr)
            continue
        if r["verdict"] == "BELOW_THE_INDEX_FLOOR":
            print(f"[startup-anchors] REFUSED: the startup header says {r['stated']:,} tests "
                  f"collected, and this repository's git index carries {r['floor']:,} test "
                  "functions. A collection is never smaller than one item per test function, so "
                  "that figure is not merely stale -- no run of this suite could have produced it. "
                  "Both this sentence and CLAUDE.md's Build line are hand-typed and agree with "
                  "each other, which is why nothing else here catches it. Recompute it: "
                  "`python3 -m pytest --collect-only -q | tail -1`, then correct BOTH.",
                  file=sys.stderr)
            continue
        print(f"[startup-anchors] REFUSED: the startup header {r['verdict'].lower()} "
              f"{r['figure']} -- it says {r['stated']:,}, and {r['source']} was never outside "
              f"{r['band_low']:,}–{r['band_high']:,} in the window its own date declares. A "
              "session's first number is this sentence; recompute the figure from that source, or "
              "correct the date it is as-of.", file=sys.stderr)

    bad = refusals(rows)
    for r in bad:
        if r["verdict"] == "LIES":
            print(f"[startup-anchors] REFUSED: {r['path']} says it was last updated "
                  f"{r['declared']} but really changed {r['true_last_change']} "
                  f"({r['declared_drift_days']} days out). A reader orienting on this document is "
                  f"told an age it does not have. Correct the date sentence.", file=sys.stderr)
        else:
            print(f"[startup-anchors] REFUSED: {r['path']} is declared as a startup anchor but is "
                  f"not in HEAD.", file=sys.stderr)
    return 1 if (bad or bad_figures) else 0


if __name__ == "__main__":
    raise SystemExit(main())
