#!/usr/bin/env python3
"""SP3 -- the size + clone ratchet ENGINE: a monotonic ceiling on module size and cross-file
structural duplication, so structural debt drains as a side-effect of ordinary work.

Serves `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28` s3 (required shape) +
s7 (anti-Goodhart, binding) + s8 (warn-then-gate rollout), designed in
`docs/design/SIZE_AND_CLONE_RATCHET_DISCOVER.md`. This module is the pure measurement + rule
engine; `tools/size_ratchet_gate.py` is the CLI/pre-commit skin and `tools/size_ratchet_override.py`
is the logged-override helper.

WHY THIS EXISTS AS A TRIPWIRE AND NOT A SCORE (ruling s7, binding on every line below)
--------------------------------------------------------------------------------------
File size and clone count are REPORTED FACTS and hard pass/fail tripwires -- never scores to
minimise, never inputs to any reward or selection mechanism. There is no lower bound and there
never should be one: the gate asks "did this commit make it worse?", never "is this number small
enough?". A ceiling lowered by deleting tests, by splitting one long file into two short ones with
no reduction in real duplication, or by obfuscating a cloned body to dodge the fingerprint is the
fidelity bug this exists to catch -- not a way to pass it.

THE DETECTOR IS BORROWED, NOT REBUILT (the finding that shaped this build)
--------------------------------------------------------------------------
The DISCOVER doc's s2.1 recorded "no existing clone-census tool found in-repo -- the BUILD half
therefore needs to BUILD the census tool". That was true on 2026-07-28 and is FALSE now:
`background/shared_primitive_census.py` (SP5, landed 2026-08-03) ships a parameterised AST
clone detector, and its own docstring records the reconciliation it owed SP3. Writing a second
AST clone detector here -- inside the atom whose entire purpose is to stop duplication -- would
have been the 92nd-register pattern committed by its own remedy. So this module IMPORTS SP5's
detector. `tests/tools/test_size_ratchet_gate.py::test_sp3_does_not_ship_a_rival_clone_detector`
pins that: it fails if this file ever grows its own fingerprinting.

THE CEILING IS MEASURED AT GO-LIVE, NOT COPIED FROM THE RULING (and why 223 was refused)
-----------------------------------------------------------------------------------------
The DISCOVER's s2.3 said to freeze the ceiling at the ruling's 223 directly. Its own s8 named the
condition for trusting that number: "re-derive 223 with its chosen convention and confirm it still
lands at (or very near) 223 before trusting the frozen ceiling." Measured at build time, it does
not, under either available convention -- SP5's detector reads 283 over SP3's scope, and a
body-only fingerprint reads 209. The tree also moved hard since the census (789 -> 818 files,
+24k lines in six days). Freezing 223 against a tree measuring 283 would hand the ratchet 60
instances of silent headroom on day one, which is a fail-open by construction; freezing 283 against
a tree measuring 283 is what a ratchet IS. So the ceiling is frozen from the detector that actually
runs, over the declared scope, at the moment of freezing -- and the ruling's 223 is carried
alongside in the artefact as `historical_reference_ceiling` so the delta stays visible and is never
silently laundered into "we were always at 283". See `docs/design/SIZE_AND_CLONE_RATCHET_DISCOVER.md`
s2.3 for the superseded design and the correction note appended to it.

MEASURED AGAINST THE INDEX, NEVER THE WORKING TREE
---------------------------------------------------
This repo has three concurrent writers and a permanently dirty working tree (CLAUDE.md, "Concurrent
writers on this one working tree"). A ratchet that measured the worktree would red on a co-writer's
uncommitted work -- a control false-positive jamming the pipeline, a failure class this project has
already paid for. Every rule below reads the INDEX (what this commit will actually contain) and
compares against HEAD. `--report` mode may read the worktree, and says so.

FAIL-CLOSED (R15, the mint's explicit guard)
---------------------------------------------
A missing or unparseable baseline, an unparseable source file in scope, or an empty scope scan is a
FAILED check, never a passed one -- an unavailable check is a failed check. There is no
`--skip-ratchet` flag: the only way past a violation is a named, logged override
(`tools/size_ratchet_override.py`), which is scoped to one file at one line count and expires the
moment the file grows again.
"""
from __future__ import annotations

import ast
import json
import subprocess
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

PROJECT_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = PROJECT_DIR / "docs" / "observability" / "size_ratchet_baseline.json"
WARN_LOG_PATH = PROJECT_DIR / "docs" / "observability" / "size_ratchet_warnings.jsonl"

# The seven source roots that make up the built system, plus `functions/` for forward-compat so a
# first file dropped there is baselined from its first commit rather than silently exempt.
# DELIBERATELY WIDER THAN SP5's `SCAN_ROOTS` (which omits `tools/` and `interface/` -- 110 files it
# never sees). The ruling's own census scope was "all 788 source modules", which this reproduces and
# SP5 does not; the divergence is registered as a finding on SP5 rather than fixed here on sight.
SCOPE_ROOTS = ("background", "company", "functions", "interface", "saas", "sim", "simulation", "tools")

# Caps apply to NEW files/functions only. Existing oversized files are grandfathered by rule 1
# ("no larger than its own current count") and are never retroactively broken -- 43 files already
# exceed 600 lines and the ratchet is not a remediation sprint.
NEW_FILE_LINE_CAP = 600
NEW_FUNCTION_LINE_CAP = 60

_EXCLUDED_PARTS = ("__pycache__", "node_modules", ".claude", "tests")

RULE_FILE_EXCEEDS_BASELINE = "file_exceeds_baseline"
RULE_TOUCHED_FILE_GREW = "touched_file_grew"
RULE_NEW_FILE_OVER_CAP = "new_file_over_cap"
RULE_NEW_FUNCTION_OVER_CAP = "new_function_over_cap"
RULE_CLONE_CEILING = "clone_ceiling_exceeded"
RULE_UNAVAILABLE = "check_unavailable"


class RatchetUnavailable(RuntimeError):
    """The check could not be performed. Callers MUST treat this as a failure, never a pass."""


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    ceiling: int
    actual: int
    detail: str = ""

    @property
    def delta(self) -> int:
        return self.actual - self.ceiling

    def line(self) -> str:
        return (
            f"[{self.rule}] {self.path}: {self.actual} > {self.ceiling} (+{self.delta})"
            + (f" -- {self.detail}" if self.detail else "")
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "path": self.path,
            "ceiling": self.ceiling,
            "actual": self.actual,
            "delta": self.delta,
            "detail": self.detail,
        }


@dataclass
class Census:
    """A whole-tree measurement at one revision."""

    lines: dict[str, int] = field(default_factory=dict)
    clone_count: int = 0
    clone_set_count: int = 0
    files_scanned: int = 0


# ------------------------------------------------------------------ git plumbing (index / HEAD)
def _git(*args: str, project_dir: Path = PROJECT_DIR) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(project_dir), capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise RatchetUnavailable(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def in_scope(rel_path: str) -> bool:
    """A path this ratchet governs: a .py file under a scope root, excluding caches, vendored
    trees, worktrees and tests. Tests are out of scope deliberately -- test growth is governed by
    the test gate, and counting it would penalise every migration whose guard test is SUPPOSED to
    grow (the ruling's own exclusion)."""
    if not rel_path.endswith(".py"):
        return False
    parts = Path(rel_path).parts
    if not parts or parts[0] not in SCOPE_ROOTS:
        return False
    if any(part in _EXCLUDED_PARTS for part in parts):
        return False
    return not Path(rel_path).name.startswith("test_")


def _blob_shas(rev: str | None, project_dir: Path = PROJECT_DIR) -> dict[str, str]:
    """Map rel_path -> blob sha for every in-scope file at `rev`. `rev=None` means THE INDEX."""
    out: dict[str, str] = {}
    if rev is None:
        raw = _git("ls-files", "-s", "--", *SCOPE_ROOTS, project_dir=project_dir)
        for line in raw.splitlines():
            meta, _, path = line.partition("\t")
            bits = meta.split()
            if len(bits) < 3 or bits[2] != "0":  # skip unmerged stages
                continue
            if in_scope(path):
                out[path] = bits[1]
        return out
    raw = _git("ls-tree", "-r", rev, "--", *SCOPE_ROOTS, project_dir=project_dir)
    for line in raw.splitlines():
        meta, _, path = line.partition("\t")
        bits = meta.split()
        if len(bits) < 3 or bits[1] != "blob":
            continue
        if in_scope(path):
            out[path] = bits[2]
    return out


def _read_blobs(shas: Iterable[str], project_dir: Path = PROJECT_DIR) -> dict[str, str]:
    """Stream blob contents through ONE `git cat-file --batch` process (819 separate `git show`
    calls would make this gate cost more than the test gate it follows)."""
    sha_list = list(dict.fromkeys(shas))
    if not sha_list:
        return {}
    proc = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=str(project_dir),
        input=("\n".join(sha_list) + "\n").encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RatchetUnavailable(f"git cat-file --batch failed: {proc.stderr.decode(errors='replace')}")
    out: dict[str, str] = {}
    buf = proc.stdout
    pos = 0
    for sha in sha_list:
        nl = buf.find(b"\n", pos)
        if nl == -1:
            raise RatchetUnavailable("git cat-file --batch returned a truncated stream")
        header = buf[pos:nl].decode(errors="replace").split()
        if len(header) < 3:
            raise RatchetUnavailable(f"git cat-file --batch could not read object {sha}")
        size = int(header[2])
        out[sha] = buf[nl + 1 : nl + 1 + size].decode("utf-8", errors="replace")
        pos = nl + 1 + size + 1  # trailing newline after the payload
    return out


def line_count(text: str) -> int:
    return len(text.splitlines())


# ------------------------------------------------------------------------------- the census
def census_at(rev: str | None, project_dir: Path = PROJECT_DIR) -> Census:
    """Measure line counts + the clone census at `rev` (None = the index).

    FAIL-CLOSED: an unparseable in-scope file or an empty scan raises, and every caller treats a
    raise as a violation. A census that silently skipped what it could not read would report a
    falling clone count precisely when the tree became unreadable.
    """
    shas = _blob_shas(rev, project_dir=project_dir)
    if not shas:
        raise RatchetUnavailable(
            f"scope scan at rev={rev or 'INDEX'} found 0 files under {SCOPE_ROOTS} -- "
            "an empty scan is a failed check, not a clean tree"
        )
    contents = _read_blobs(shas.values(), project_dir=project_dir)
    lines = {path: line_count(contents[sha]) for path, sha in shas.items()}

    # The clone detector reads from disk, so materialise this revision into a temp tree and point
    # SP5's own detector at it. Reusing the detector is the point; re-implementing it against
    # strings would fork the very duplication this gate measures.
    clone_count, clone_set_count = _clone_census_of(shas, contents)
    return Census(
        lines=lines,
        clone_count=clone_count,
        clone_set_count=clone_set_count,
        files_scanned=len(shas),
    )


def _clone_census_of(shas: dict[str, str], contents: dict[str, str]) -> tuple[int, int]:
    """Run SP5's AST clone detector over the given revision's content. Imported, never rebuilt --
    see the module docstring. A single detector means SP3's ceiling and SP5's register can never
    drift into two incompatible definitions of the same word."""
    from background import shared_primitive_census as spc  # noqa: PLC0415 (import cost is real)

    with tempfile.TemporaryDirectory(prefix="size_ratchet_") as tmp:
        root = Path(tmp)
        files: list[Path] = []
        for rel, sha in sorted(shas.items()):
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(contents[sha], encoding="utf-8")
            files.append(dest)
        # Suppress SyntaxWarning only (e.g. an invalid escape sequence in a real source file):
        # it is a property of the code being MEASURED, not of this gate, and printing it on every
        # commit would train the reader to ignore this gate's output. A genuine SyntaxERROR still
        # raises through `unparseable` above -- warnings are muted, failures never are.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            result = spc._clone_census(files, project_dir=root)
    if result["unparseable"]:
        raise RatchetUnavailable(
            "clone census could not parse "
            f"{len(result['unparseable'])} in-scope file(s): {result['unparseable'][:3]} -- "
            "an unparseable census is a failed check, never a passed one"
        )
    return int(result["clone_count"]), int(result["clone_set_count"])


# -------------------------------------------------------------------------- function inventory
def function_spans(text: str) -> dict[str, int]:
    """Qualified function name -> line span, for the new-function cap. Qualified by dotted path so
    a RENAME reads as a new function (intentional: the ratchet must notice a rename rather than
    carry an old baseline entry forward under a new name)."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        raise RatchetUnavailable(f"unparseable source: {exc}") from exc

    spans: dict[str, int] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            name = getattr(child, "name", None)
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                end = getattr(child, "end_lineno", child.lineno) or child.lineno
                spans[qual] = end - child.lineno + 1
                walk(child, f"{qual}.")
            elif isinstance(child, ast.ClassDef) and name:
                walk(child, f"{prefix}{child.name}.")
    walk(tree, "")
    return spans


# ------------------------------------------------------------------------------ baseline I/O
def load_baseline(path: Path = BASELINE_PATH) -> dict[str, Any]:
    """FAIL-CLOSED: a missing or unparseable baseline raises. A ratchet that passed when its own
    ceiling was unreadable would be the fail-open the mint names explicitly."""
    if not path.exists():
        raise RatchetUnavailable(
            f"baseline artefact missing at {path} -- run `tools/size_ratchet_gate.py --freeze`. "
            "A missing baseline is a failed check, never a passed one"
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RatchetUnavailable(f"baseline artefact unreadable at {path}: {exc}") from exc
    for key in ("files", "clone_ceiling", "rollout_state", "scope_roots"):
        if key not in data:
            raise RatchetUnavailable(f"baseline artefact at {path} is missing required key '{key}'")
    if data["rollout_state"] not in ("warn", "gate"):
        raise RatchetUnavailable(
            f"baseline rollout_state must be 'warn' or 'gate', got {data['rollout_state']!r}"
        )
    return data


# ---------------------------------------------------------------------------------- the rules
def evaluate(
    baseline: dict[str, Any],
    index: Census,
    head_lines: dict[str, int],
    touched: set[str],
    index_texts: dict[str, str] | None = None,
    head_texts: dict[str, str] | None = None,
    renames: dict[str, str] | None = None,
) -> list[Finding]:
    """Apply the four ruling-decided rules to a measured index. Pure: no I/O, no git, no exit
    codes -- so the same detection logic runs identically under both rollout states (R15 test 7).

    `renames` maps a staged path to the path the SAME content had at HEAD (git's own -M detection,
    resolved by the caller so this stays pure). Rules 2b and 3 both read prior state BY PATH, so
    without the map a `git mv` is invisible to them in OPPOSITE directions: 2b presents every
    function in the moved file as brand new (too strict -- see
    `docs/staging/done/WORKER_FINDING_A_PURE_RENAME_READS_AS_A_NEW_OVERSIZED_FUNCTION_2026-08-10.md`)
    and 3 waves its growth through (too lax -- see
    `docs/staging/done/WORKER_FINDING_RULE_3_HAS_THE_SAME_RENAME_BLINDNESS_2026-08-10.md`).
    """
    findings: list[Finding] = []
    base_files: dict[str, int] = baseline["files"]
    rename_map: dict[str, str] = renames or {}

    for path, count in sorted(index.lines.items()):
        # Rule 1 (s3.1): no file already in the baseline may exceed its own frozen count.
        if path in base_files and count > base_files[path]:
            findings.append(
                Finding(RULE_FILE_EXCEEDS_BASELINE, path, base_files[path], count,
                        "frozen baseline for this file")
            )
        # Rule 2 (s3.2): a NEW file (no baseline entry) is capped. Existing oversized files are
        # grandfathered by rule 1 and never retroactively broken by this cap.
        elif path not in base_files and count > NEW_FILE_LINE_CAP:
            findings.append(
                Finding(RULE_NEW_FILE_OVER_CAP, path, NEW_FILE_LINE_CAP, count,
                        "new file -- split it, or log an override")
            )
        # Rule 3 (s3.3): a file this commit TOUCHES comes out no larger than it went in. Stricter
        # than rule 1 and the reason the ratchet DRAINS debt instead of merely freezing it: the 91
        # registers shrink when someone touches one for an unrelated reason, never by a sprint.
        # A file that arrived via `git mv` has no entry under its NEW path, so its prior count is
        # resolved through the rename map -- otherwise the drain rule is switched off for exactly
        # the commits that move code around, and a rename-plus-growth is invisible to it.
        prior = path if path in head_lines else rename_map.get(path, path)
        if path in touched and prior in head_lines and count > head_lines[prior]:
            findings.append(
                Finding(RULE_TOUCHED_FILE_GREW, path, head_lines[prior], count,
                        "touched by this commit -- must come out no larger than it went in")
            )

    # Rule 2b (s3.2): a NEW function in a touched file is capped.
    if index_texts is not None:
        findings.extend(
            _new_function_findings(touched, index_texts, head_texts or {}, renames or {})
        )

    # Rule 4 (s3.4): the clone ceiling. NEVER a target of zero -- there is no lower-bound check
    # here and there must never be one (ruling s7).
    ceiling = int(baseline["clone_ceiling"])
    if index.clone_count > ceiling:
        findings.append(
            Finding(RULE_CLONE_CEILING, "<tree>", ceiling, index.clone_count,
                    f"{index.clone_set_count} cross-file clone-sets; extract a shared primitive "
                    "rather than obfuscating the duplicate")
        )
    return findings


def _new_function_findings(
    touched: set[str], index_texts: dict[str, str], head_texts: dict[str, str],
    renames: dict[str, str] | None = None,
) -> list[Finding]:
    out: list[Finding] = []
    renames = renames or {}
    for path in sorted(touched):
        if path not in index_texts:
            continue
        new_spans = function_spans(index_texts[path])
        # A renamed file's prior state lives under its OLD path. Resolve through the rename map
        # first, so a pure `git mv` carries its functions across instead of minting them anew.
        prior = path if path in head_texts else renames.get(path, path)
        old = set(function_spans(head_texts[prior])) if prior in head_texts else set()
        for qual, span in sorted(new_spans.items()):
            if qual not in old and span > NEW_FUNCTION_LINE_CAP:
                out.append(
                    Finding(RULE_NEW_FUNCTION_OVER_CAP, f"{path}::{qual}",
                            NEW_FUNCTION_LINE_CAP, span, "new function -- decompose it")
                )
    return out
