#!/usr/bin/env python3
"""An atom that CLAIMS A LEVEL must name a file_scope that exists.

THE DEFECT THIS EXISTS TO CATCH, found 2026-08-24 while truing the harness lane. Thirteen
atoms in `docs/design/maturity_map.yaml` sat at `level_current > 0` while naming file_scope
paths that had been deleted -- eleven of them by one commit, 03dd8c49e ("The five tabs are the
site now"), which removed eleven pages on a director ruling. `E2_revenue_reconciliation` was
the worst: L3 claimed, and every one of its three named paths gone. A level is a claim about
evidence; if the evidence has been deleted, the map is asserting something no longer checkable
and nothing anywhere said so.

03dd8c49e's own message names the class it was fixing on the OTHER side of the same boundary:
"a generator that outlives its page is how a deleted surface returns", and 87 controls carrying
literal page lists were rewritten to derive from the built site. Nothing looked at the MAP. An
atom that outlives its files is the same defect wearing governance clothes -- and it is worse,
because the map is what the draw reads to decide what to work on.

WHY THE RULE IS `level_current > 0` AND NOT "every atom". A `level_current: 0`, `loop_stage:
idle` proposal naming `sim/competitor_field.py` is CORRECT: that is an unbuilt atom declaring
the files it would create, and 17 such atoms exist today. Refusing those would make the map
unable to describe future work, which is most of what a maturity map is for. What cannot be
right is a CLAIM resting on absence. So the rule keys on the claim, not on the path.

TWO KINDS OF NOTHING, and the live tree taught the second one on this control's first real run.
Against the working directory it was clean; inside the pre-commit extract -- built from git
objects, not from disk -- it refused `PB2_opening_book_won_not_assigned` at L3 for
`docs/design/PB2_INVERSION_BUILD.md`, a completed build record sitting on disk and never
committed while its own sibling `PB2_JOIN_KEY_BUILD.md` was in git. That is worse than a
deletion, not a false positive: an L3 claim whose evidence dies with one working tree. So
DELETED and NOT IN GIT are reported apart, with different instructions, and both refuse.

WHAT IT DOES NOT CHECK, said plainly so nobody reads it as stronger than it is: that the files
still SUPPORT the level. A path can exist and be empty, or exist and have had the relevant code
cut out of it. This control answers "is the evidence still there at all", which is the cheap
half, and it is the half that was silently false thirteen times.

NO FROZEN BASELINE, deliberately. The thirteen were fixed in the commit that armed this, so the
control starts from zero and has nothing to erode. A ratchet with a starting allowance is a
control that has already conceded the argument once.

Run standalone:  python3 -m tools.scope_evidence_ratchet
Exit 0 = clean, 1 = a claimed level rests on a path that does not exist.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from tools import maturity_map_store as map_store

ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = ROOT / "docs" / "design" / "maturity_map.yaml"


def parse_atoms(text: str) -> list[dict]:
    """The map's atom records, read with the real YAML parser.

    A HAND-ROLLED TEXT PARSER WAS THE FIRST DRAFT HERE AND IT WAS WRONG, which is worth
    recording because the reasoning sounded good: this runs inside a pre-commit hook, and a
    third-party import is one more way for a gate to fail for a reason that is not about the
    commit. `site/moap_coherence.py` reads the map that way for exactly that reason.

    Two things killed it. First, PyYAML is not an extra risk here at all -- both
    `tools/level_promotion_gate.py` and `tools/orphan_ratchet.py` already import it and both
    already run in this hook, so the dependency was being taken anyway and I had argued myself
    out of it on a premise I had not checked. Second, and worse, the text parser was measurably
    WRONG on the map as it stands: cross-checked against yaml it disagreed on four records --
    `level_current: 1   # <comment>` defeated the scalar match, and an inline list WRAPPED
    ACROSS LINES (`file_scope: [a, b,` / newline / `  c, d]`) yielded an EMPTY scope. Empty
    scope means "nothing to check", so three atoms would have been silently exempt from the
    control -- R15's fail-silent pattern, built into the control on its first day.

    `test_the_parser_agrees_with_yaml_on_every_atom` keeps the two honest against each other.
    """
    parsed = yaml.safe_load(text)
    if not isinstance(parsed, list):
        raise ValueError("the maturity map did not parse as a list of atoms")
    out = []
    for a in parsed:
        if not isinstance(a, dict) or not a.get("id"):
            continue
        scope = a.get("file_scope") or []
        out.append({
            "id": a["id"],
            "level_current": a.get("level_current"),
            "file_scope": [str(s) for s in scope] if isinstance(scope, list) else [],
        })
    return out


#: The two ways a claimed level can rest on nothing, and they need different sentences.
DELETED = "deleted"
UNCOMMITTED = "uncommitted"


def _tracked_paths(root: Path) -> frozenset[str] | None:
    """Everything git has. `None` if git could not be asked -- the caller then falls back to
    the filesystem alone rather than inventing a verdict about the repository."""
    try:
        r = subprocess.run(["git", "ls-files"], cwd=str(root),
                           capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 -- probe unavailable, not a finding about the map
        return None
    if r.returncode != 0:
        return None
    return frozenset(ln.strip() for ln in r.stdout.splitlines() if ln.strip())


def _in_git(rel: str, tracked: frozenset[str]) -> bool:
    if rel in tracked:
        return True
    prefix = rel if rel.endswith("/") else rel + "/"
    return any(t.startswith(prefix) for t in tracked)


def violations(text: str, root: Path = ROOT,
               tracked: frozenset[str] | None = None) -> list[tuple[str, int, str, str]]:
    """(atom_id, level_current, path, kind), one row per path that is not real evidence.

    TWO KINDS, and the distinction was not in the first draft -- the live tree taught it. Run
    against the working directory this control was clean; run inside the pre-commit extract,
    which is built from git objects, it refused `PB2_opening_book_won_not_assigned` at L3 for
    `docs/design/PB2_INVERSION_BUILD.md`. The file was right there on disk. It had never been
    committed.

    That is a WORSE defect than a deleted path, not a false positive: an L3 claim whose build
    record exists only in one working tree dies with that tree, and this repo already tracks
    the class (`uncommitted_and_orphaned_work`). But "missing" is the wrong word for it and
    would send a reader looking for a deletion that never happened, so the two are reported
    apart. Both refuse.

    `tracked` is injectable so a test can drive both kinds without a git repo; when it is None
    the tree is asked, and if git cannot be asked at all the check degrades to existence-only
    rather than asserting anything about the repository it could not read.
    """
    if tracked is None:
        tracked = _tracked_paths(root)
    out = []
    for a in parse_atoms(text):
        level = a["level_current"]
        if not isinstance(level, int) or level <= 0:
            continue
        for rel in a["file_scope"]:
            on_disk = (root / rel).exists()
            if not on_disk:
                out.append((a["id"], level, rel, DELETED))
            elif tracked is not None and not _in_git(rel, tracked):
                out.append((a["id"], level, rel, UNCOMMITTED))
    return out


def main(argv: list[str] | None = None) -> int:
    try:
        text = map_store.map_text(MAP_PATH)
        parse_atoms(text)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        # FAIL-CLOSED. An unreadable map is an unavailable check, and R15 names an unavailable
        # check a FAILED one -- passing here would let a commit that broke the map slip past
        # the one control that reads it.
        sys.stderr.write(
            "[scope-evidence] ❌ the maturity map could not be read or parsed ({}), so this "
            "control could not run. An unavailable check is a failed check.\n".format(exc))
        return 1

    bad = violations(text)
    if not bad:
        return 0

    sys.stderr.write(
        "\n[scope-evidence] ❌ COMMIT REFUSED -- {} atom(s) CLAIM A LEVEL on evidence that is "
        "not in the tree this commit would create. A level is a claim about evidence; a path "
        "that was deleted, or never committed, is not evidence.\n\n".format(
            len({b[0] for b in bad})))
    last = None
    for atom, level, rel, kind in bad:
        if atom != last:
            sys.stderr.write("  {} (level_current {})\n".format(atom, level))
            last = atom
        sys.stderr.write("      {:<12} {}\n".format(
            "DELETED:" if kind == DELETED else "NOT IN GIT:", rel))
    if any(k == DELETED for *_, k in bad):
        sys.stderr.write(
            "\n  DELETED -- fix by RE-POINTING the scope at wherever the work now lives, or by\n"
            "  correcting the level down with the evidence that stopped reproducing\n"
            "  (background.gate_authorization.record_level_correction_self_certified).\n"
            "  Removing the path with nothing put in its place is only right when the atom's OWN\n"
            "  work deleted the file -- say so in the commit if it is.\n")
    if any(k == UNCOMMITTED for *_, k in bad):
        sys.stderr.write(
            "\n  NOT IN GIT -- the file is on disk and has never been committed, so this level\n"
            "  rests on evidence that dies with one working tree. Land it. This is the\n"
            "  `uncommitted_and_orphaned_work` class, caught at the point where it makes a\n"
            "  published claim false rather than at the point somebody notices the file.\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
