"""Does every path a staged document claims LANDED actually exist in a tree?

THE CLASS THIS CLOSES, and it is the third instance in three days.
`WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14`
opened `status: INSTANCE FIXED (the supplier half landed)` and closed with a "what landed
this tick" manifest naming `tools/simplifications_store.py`. None of it was in any tree:

    $ git log -S "def atom_name" -- tools/simplifications_store.py   <- no output, ever
    $ git status --porcelain -- tools/simplifications_store.py
    M  tools/simplifications_store.py                                <- index, not a tree

The publish gate went on logging the identical red for another 30 cycles while a reader who
believed the manifest diagnosed elsewhere (229 -> 244 consecutive failures). A false LANDED
is worse than no finding, because it redirects the next reader away from the live cause --
the same asymmetry CLAUDE.md names for prose-only rules ("illusion of control"). The first
two instances of this mechanism were both closed with PROSE. R3 says a second false
completion claim on one mechanism means build the control; this is the third.

WHY THE SIBLING CONTROL DOES NOT COVER IT. `tools/symbol_landing_check.py` resolves changed
first-party REFERENCES against the resulting tree, and it would have caught the ORIGINAL
omission (a consumer committed without its supplier). It cannot catch this one, because here
nothing was committed at all -- there was no changed reference to resolve. The missing
control is narrower and much cheaper: read the document's own claim.

WHAT IT CHECKS. For each path P a changed staging document claims LANDED:

  1. ABSENT   -- P is not in the tree this commit creates. Claimed landed, never landed.
  2. STAGED   -- P's blob in the REAL index differs from P's blob in the tree this commit
                 creates. There is content for P sitting in the index that this commit is
                 not carrying, so a reader cannot tell which version the claim is about.
                 This is the clause the 2026-08-14 instance trips, and the ONLY one it
                 trips: `tools/simplifications_store.py` existed at the parent commit
                 (blob 4ec6f9bf), so path-existence alone is blind to it.

THE THREE KILLER PATTERNS (R15), each answered rather than asserted:

  * TAUTOLOGY -- every read is git plumbing against a TREE (`ls-tree`, `cat-file`) or the
    index (`ls-files -s`). `git status` is never consulted and the working tree is never
    read, including for the document text itself, which is fetched with `cat-file blob`
    from the tree under judgement. Asking the working tree would ask the desk that was
    already green ([[feedback_a_cut_recorded_as_executed_may_never_have_been_committed]]).
  * FAIL-OPEN -- a document that ASSERTS a landing but from which no path can be parsed is
    counted and NAMED in the report as `unchecked`, never silently skipped. Otherwise the
    control's real population is "documents that happen to use the heading I grepped for",
    which is a population chosen by the parser rather than by the subject.
  * FAIL-SILENT -- it has an automated caller in `tools/pre_commit_test_gate.py`, which is
    the moment a claim becomes load-bearing for the next reader (a staging-only commit is
    exactly the commit that archives a finding to `done/`). A control invoked only by
    someone typing it is the class already filed as CLASS_NO_CALLER_AND_NEVER_RUNS.
    **A control built to catch "the record outran the code" cannot be invoked by the
    record. It has to be invoked by the thing that makes the code real -- the commit.**

SCOPE, and it is deliberately the narrow one. The population is staging documents THIS
COMMIT CHANGES, not every document in the rooms. Two reasons, one principled and one
measured. Principled: the moment the claim becomes load-bearing is the moment it is written
or archived, which is this commit. Measured: paths move, and archived documents cite paths
that have since been renamed (66 dead evidence paths across 80 atoms were counted on
2026-08-13), so a whole-rooms scope would red on hundreds of historical documents for a
reason that is not their author's and not this control's subject. Billing a committer for
that is how a gate gets turned off.

TWO HONEST LIMITS, stated because a control that hides its error bars invites false
confidence:
  1. It checks that the PATH is in a tree, never that the path's CONTENT says what the
     document meant. A manifest naming a file that landed with the wrong body still passes
     here; that is `symbol_landing_check`'s subject, not this one.
  2. Clause 2 reds when a claimed-landed path also has content staged that this commit
     excludes -- including the rare case where the claim was about an EARLIER landing and
     the staged content is an unrelated later edit. That is deliberate rather than
     overlooked: at that moment the document's reader genuinely cannot tell which version
     landed, which is the ambiguity the class is about. The message says how to clear it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

STAGING_PREFIX = "docs/staging/"

# A document ASSERTS a landing. Kept deliberately broader than the path parser: a claim we
# can see but cannot parse must reach the `unchecked` list rather than fall out of the
# population, which is the FAIL-OPEN pattern this control is required to answer.
_CLAIM_PATTERNS = (
    re.compile(r"\bwhat landed\b", re.I),
    re.compile(r"\blanded this tick\b", re.I),
    re.compile(r"\blanded with\b", re.I),
    re.compile(r"\bINSTANCE (?:FIXED|LANDED)\b"),
    re.compile(r"\bINSTANCES LANDED\b"),
    re.compile(r"^\*\*status:\*\*.*\bLANDED\b", re.I | re.M),
    re.compile(r"\bis now at HEAD\b", re.I),
)

# The section whose body IS the manifest. Anything from this heading to the next heading of
# any level is manifest text.
_MANIFEST_HEADING = re.compile(r"^#{1,6}\s+.*\b(what landed|landed this tick)\b.*$", re.I)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")

# WHERE A DOCUMENT MAKES ITS OWN CLAIM, and this scope was NARROWED after the control
# refused the very report announcing it. A first pass read any body line containing
# "landed", which cannot tell a claim from a CITATION of someone else's: a report whose
# subject is "commit X falsely claimed `path/y.py` landed" got billed for X's defect, and a
# control that punishes the document reporting a defect is a control that stops findings
# being written. The authoritative claim surface is therefore structural, not lexical:
#   * the HEADER BLOCK (everything before the first `##` section), which is where
#     `**status:** ... LANDED` lives, and
#   * the body of a "what landed" section.
# Prose elsewhere is discussion, and discussion is where honest quotation happens.
_SECTION_HEADING = re.compile(r"^##\s")

# A BACKTICKED TOKEN IS NOT A PATH. This repo has already paid for the opposite assumption:
# a discharge line that read every backtick as a path turned test node ids and prose into
# phantom files. Require a directory separator, a known source extension, and no node-id /
# glob / URL shrapnel.
_SOURCE_SUFFIXES = (
    ".py", ".md", ".yaml", ".yml", ".json", ".jsonl", ".js", ".ts", ".tsx",
    ".html", ".css", ".sh", ".toml", ".cfg", ".ini", ".txt", ".sql",
)
_BACKTICKED = re.compile(r"`([^`\n]+)`")


def _git(args: list[str], root: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True, check=False,
        env=env if env is not None else os.environ.copy(),
    )


def _real_index_env(root: Path) -> dict:
    """An env pinned to the REAL index, never the commit-in-progress temporary one.

    `git commit -- <pathspec>` hands the hook a TEMPORARY index in `GIT_INDEX_FILE`
    containing HEAD plus only that pathspec. Clause 2's whole subject is what is staged and
    NOT being carried, so reading that temporary index would compare the resulting tree
    against itself -- a tautology that can never red. Resolve `--git-path index` and pin it.
    """
    env = os.environ.copy()
    where = _git(["rev-parse", "--git-path", "index"], root, env=env)
    if where.returncode != 0:
        raise RuntimeError(
            f"git rev-parse --git-path index rc={where.returncode}: {where.stderr.strip()[-200:]}"
        )
    idx = where.stdout.strip()
    src = Path(idx) if os.path.isabs(idx) else (root / idx)
    env["GIT_INDEX_FILE"] = str(src)
    return env


def is_path_like(token: str) -> bool:
    """Would a reader take this backticked token for a REPO path?

    NOT MERELY "a path" -- a path IN THIS REPOSITORY, and the distinction wedged a
    419-file backlog for six days (2026-08-26).

    Two staging documents mention an absolute scratch path in backticks:
    `/tmp/claude-1000/.../scratchpad/land.sh` in `DIRECTOR_CONSOLE_2026-08-20.md` and a
    sibling in a 2026-08-25 finding. Both are honest prose -- they describe a wrapper
    script that really did exist outside the tree. This function called them repo paths,
    the caller ran `git ls-tree <tree> -- /tmp/...`, git answered rc=128 "Invalid path", and
    the checker RAISED. So it refused every commit that touched `docs/staging`, which is
    every commit that would have cleared the archive backlog -- and the refusal named a
    crash rather than a claim, because a checker that cannot read its input is not
    reporting a false LANDED.

    Fail-closed is right for "this path is missing from the tree". It is NOT right for
    "this token was never about the tree". An absolute path, or one that climbs out of the
    repository, is prose about somewhere else and cannot be a landing claim about here.
    """
    t = token.strip().rstrip(".,;:)").strip()
    if not t or "/" not in t or " " in t:
        return False
    if "::" in t or "*" in t or "://" in t or t.startswith("-"):
        return False
    # OUTSIDE THE REPOSITORY IS NOT A CLAIM ABOUT THE REPOSITORY. Absolute paths, home-dir
    # paths, and anything climbing out through `..` are prose about elsewhere. `git ls-tree`
    # rejects them at the plumbing level, so treating them as claims turns a document's
    # honest mention of a scratch file into a commit refusal.
    if t.startswith(("/", "~")) or t.split("/")[0] == "..":
        return False
    return t.endswith(_SOURCE_SUFFIXES)


def manifest_paths(text: str) -> list[str]:
    """Every repo path the document claims LANDED, in first-seen order.

    Two sources, both the document's own: the body of a "what landed" section, and any
    single line that makes a landing claim inline.
    """
    lines = text.splitlines()
    regions: list[str] = []

    # A HEADER BLOCK ONLY EXISTS IF THE DOCUMENT HAS SECTIONS (2026-08-26). The design above
    # says the authoritative claim surface is "the HEADER BLOCK (everything before the first
    # `##` section), which is where `**status:** ... LANDED` lives" -- a handful of lines.
    # In a document with NO `##` heading at all that rule silently swallows the whole file,
    # so every backticked path anywhere in it becomes a landing claim.
    #
    # `docs/staging/DIRECTOR_CONSOLE_2026-08-26.md` is exactly that: no `##` headings, and a
    # quoted session summary in its body. The line the control billed it for reads
    # "`tests/simulation/test_policy_cost_coverage.py` remains uncommitted" -- the OPPOSITE
    # of a landing claim, quoted from a handover. It refused the archive commit for six days
    # on a sentence saying the file had NOT landed.
    #
    # This is the same shape as the narrowing recorded above ("a control that punishes the
    # document reporting a defect is a control that stops findings being written"), one step
    # further out: that pass fixed the BODY rule and left the header rule able to become the
    # body. A document with no sections has no header block, and by this design's own words
    # "prose elsewhere is discussion, and discussion is where honest quotation happens".
    has_sections = any(_SECTION_HEADING.match(line) for line in lines)

    in_header = has_sections
    in_manifest = False
    for line in lines:
        if _SECTION_HEADING.match(line):
            in_header = False
        if _MANIFEST_HEADING.match(line):
            in_manifest = True
            continue
        if in_manifest and _ANY_HEADING.match(line):
            in_manifest = False
        if in_header or in_manifest:
            regions.append(line)

    seen: list[str] = []
    for line in regions:
        for token in _BACKTICKED.findall(line):
            cand = token.strip().rstrip(".,;:)").strip()
            if is_path_like(token) and cand not in seen:
                seen.append(cand)
    return seen


def asserts_landing(text: str) -> bool:
    return any(p.search(text) for p in _CLAIM_PATTERNS)


def _tree_blob(tree: str, path: str, root: Path, env: dict) -> str | None:
    out = _git(["ls-tree", "-z", tree, "--", path], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(
            f"git ls-tree {tree[:9]} -- {path} rc={out.returncode}: {out.stderr.strip()[-200:]}"
        )
    rec = out.stdout.strip("\x00").strip()
    if not rec:
        return None
    # "<mode> <type> <sha>\t<path>"
    try:
        return rec.split("\t", 1)[0].split()[2]
    except IndexError:  # pragma: no cover -- malformed plumbing output is a FAILED check
        raise RuntimeError(f"unparseable ls-tree record for {path}: {rec!r}") from None


def _index_blob(path: str, root: Path, env: dict) -> str | None:
    out = _git(["ls-files", "-s", "-z", "--", path], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(
            f"git ls-files -s -- {path} rc={out.returncode}: {out.stderr.strip()[-200:]}"
        )
    rec = out.stdout.strip("\x00").strip()
    if not rec:
        return None
    try:
        return rec.split("\t", 1)[0].split()[1]
    except IndexError:  # pragma: no cover
        raise RuntimeError(f"unparseable ls-files record for {path}: {rec!r}") from None


def changed_staging_documents(tree: str, since_tree: str, root: Path, env: dict) -> list[str]:
    out = _git(["diff", "--name-only", "-z", since_tree, tree], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(
            f"git diff --name-only {since_tree}..{tree[:9]} rc={out.returncode}: "
            f"{out.stderr.strip()[-200:]}"
        )
    names = [n for n in out.stdout.split("\x00") if n]
    return sorted(n for n in names if n.startswith(STAGING_PREFIX) and n.endswith(".md"))


def _document_text(tree: str, path: str, root: Path, env: dict) -> str | None:
    """The document AS THIS COMMIT WOULD PUBLISH IT. Never the working tree (tautology)."""
    out = _git(["cat-file", "blob", f"{tree}:{path}"], root, env=env)
    if out.returncode != 0:
        return None
    return out.stdout


def run_at_tree(
    tree: str,
    since_tree: str = "HEAD^{tree}",
    root: Path | str = PROJECT_DIR,
) -> tuple[list[str], dict]:
    """Check every landing claim this commit's staging documents make. Returns (findings, report)."""
    root = Path(root)
    env = _real_index_env(root)

    docs = changed_staging_documents(tree, since_tree, root, env)
    findings: list[str] = []
    unchecked: list[str] = []
    claims = 0
    paths_checked = 0

    for doc in docs:
        text = _document_text(tree, doc, root, env)
        if text is None:
            # Deleted by this commit (an archive move shows as delete+add): nothing to judge
            # on the delete side; the add side is a separate entry in `docs`.
            continue
        if not asserts_landing(text):
            continue
        claims += 1
        paths = manifest_paths(text)
        if not paths:
            unchecked.append(doc)
            continue
        for p in paths:
            paths_checked += 1
            in_tree = _tree_blob(tree, p, root, env)
            if in_tree is None:
                findings.append(
                    f"{doc}: claims `{p}` LANDED, but it is ABSENT from the tree this "
                    f"commit creates. Land the path in this commit, or drop the claim."
                )
                continue
            staged = _index_blob(p, root, env)
            at_head = _tree_blob("HEAD^{tree}", p, root, env)
            # RED ONLY IF SOMETHING IS ACTUALLY STAGED AND EXCLUDED. `index != tree` alone is
            # not that, and the control refused the very commit announcing it: `git commit --
            # <pathspec>` builds the resulting tree from the WORKING TREE, so an edited-but-
            # not-`git add`ed path legitimately reads index(==HEAD) != tree(new content).
            # That is the commit LANDING the claim, which is the honest case. The 2026-08-14
            # defect is the mirror image and is still caught exactly: there the index held the
            # new content (!= HEAD) and the tree held the old, so the claim was about content
            # no tree carried. Discriminate on `staged != at_head` -- is there content in the
            # index that is not at HEAD and not in this commit.
            if staged is not None and staged != in_tree and staged != at_head:
                findings.append(
                    f"{doc}: claims `{p}` LANDED, but content for it is sitting in the "
                    f"INDEX ({staged[:9]}) that this commit is not carrying "
                    f"(tree has {in_tree[:9]}). A reader cannot tell which version landed. "
                    f"Add the path to this commit's pathspec, or drop the claim."
                )

    report = {
        "tree": tree,
        "since_tree": since_tree,
        "staging_documents_changed": len(docs),
        "documents_claiming_a_landing": claims,
        "paths_checked": paths_checked,
        "unchecked_documents": unchecked,
        "findings": len(findings),
    }
    return findings, report


def _resolve_tree(ref: str, root: Path, env: dict) -> str:
    out = _git(["rev-parse", f"{ref}^{{tree}}"], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(f"cannot resolve {ref} to a tree: {out.stderr.strip()[-200:]}")
    return out.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--at-tree", help="the tree to judge (default: HEAD's tree)")
    ap.add_argument("--since-tree", default=None,
                    help="the tree to diff against for the population (default: HEAD^)")
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = ap.parse_args(argv)

    root = PROJECT_DIR
    env = _real_index_env(root)
    tree = args.at_tree or _resolve_tree("HEAD", root, env)
    since = args.since_tree or _resolve_tree("HEAD^", root, env)

    findings, report = run_at_tree(tree, since_tree=since, root=root)
    if args.json:
        print(json.dumps({**report, "finding_lines": findings}, indent=2))
    else:
        print(f"landed-manifest check @ {tree[:9]} (since {since[:9]})")
        print(f"  staging documents changed : {report['staging_documents_changed']}")
        print(f"  claiming a landing        : {report['documents_claiming_a_landing']}")
        print(f"  paths checked             : {report['paths_checked']}")
        if report["unchecked_documents"]:
            print(f"  UNCHECKED (claim seen, no path parsed): "
                  f"{len(report['unchecked_documents'])}")
            for d in report["unchecked_documents"]:
                print(f"    ? {d}")
        for f in findings:
            print(f"  - {f}")
        print("  OK" if not findings else f"  {len(findings)} FINDING(S)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
