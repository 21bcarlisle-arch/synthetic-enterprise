"""Write HEAD's bytes over a RIVAL working copy HEAD strictly supersedes -- preserving it first.

THE GAP THIS FILLS, and it is a gap a rule left rather than a defect anyone wrote.
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES_2026-09-08`:
`tools/stale_copy_refusal.py` names eight working copies that would revert a landing, and its
refusal text sends each of them to `tools/isolate_hunks.py --keep N` + `surgical_land --content`.
For two of the eight that remedy has **no legal application**, and `isolate_hunks` is right to
refuse it: they supply *zero* names HEAD does not have, so every hunk in them is either the same
code reworded or a strictly weaker version of what landed. Select a hunk and you land a revert.
Select none and the tool refuses -- *"landing HEAD's own bytes back over itself is an empty change
wearing a commit's clothes"*. Both branches correct; no third one.

The repair such a copy needs is **replace these bytes with HEAD's**, and nothing in the repo did it:
`surgical_land --content` never writes the working tree (deliberately -- that is what makes it safe
for a two-lane file), and `git checkout <path>` / `git stash` are forbidden by `CLAUDE.md` *for
exactly this class's sake*, because they discard the holder's work. The prohibition is right in
general. On a copy where the holder's work is provably nil it forbade the only move that helps, and
a rule that leaves no legal move evaporates -- the same argument that produced `surgical_land`.

WHAT STOPS THIS BEING `git checkout` WITH A NICER NAME. Three things, and they are conjunctive.

  1. THE COPY MUST SUPPLY NO NAME HEAD LACKS. Computed, never asserted: `stale_copy_refusal.symbols`
     over both blobs, and a single name on the copy's side is a REFUSAL that names it and sends the
     caller to `isolate_hunks`. This is the whole of the Kind-A/Kind-B split, made a precondition.
  2. HEAD MUST ACTUALLY SUPERSEDE IT. `stale_copy_refusal.judge` must have a complaint about this
     copy. Keyed to the PROPERTY (this copy would revert a landing), not to a path anyone listed:
     without it the tool reverts any edit you point it at, which IS `git checkout`.
  3. THE BYTES MUST BE RECOVERABLE BEFORE THEY ARE DESTROYED, and the recovery route is VERIFIED
     rather than claimed -- see `preserve`. The idiom is the repo's own (`e8f3a2618 preserved
     shared-tree worktree state before ff to origin/main`, and the twenty-odd `refs/preserved/*`
     refs that hand-made version left behind); what is new is that it runs before the write, on the
     exact bytes about to go, with the `git log --all -S` lookup RUN and not merely printed.

NOT A HOOK BYPASS, said here because the shape looks like one. `CLAUDE.md`'s wall is about commits
that enter the project's history without facing the gates -- `--no-verify`, hand-built
`commit-tree` merges onto a branch. The commit this writes is on **no branch**, has HEAD as its
parent, is never merged, never pushed and never fast-forwarded to; it exists so that
`git log --all -S` has something to find. It changes no tree any lane works from. A landing still
goes through `tools/surgical_land.py` and always did.

DEFAULT IS SURVEY. `--write` is required to touch a byte, because the discarded lines are printed
first and a reader who has not seen them cannot judge the one thing this tool cannot: whether a
reworded error string was worth keeping. Symbol-set granularity is blind to a value-level edit, so
the line-level losses go on the surface rather than in a footnote.

    python3 -m tools.refresh_to_head --root /home/rich/synthetic-enterprise tools/foo.py
    python3 -m tools.refresh_to_head --root ... --write --slug kind-a-repair tools/foo.py

Exit 0 = every named path is at HEAD or was refreshed; 1 = at least one refusal.
"""
from __future__ import annotations

import argparse
import difflib
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# REUSED rather than re-cut: the whole judgement half of this tool is `stale_copy_refusal`'s. Its
# `symbols()` is the reader that returns `None` -- not an empty set -- for a suffix it cannot read,
# which is what lets refusal 1 fail closed instead of waving an unreadable file through; its
# `judge()` is refusal 2 entire. Re-deriving either would be a second opinion about what a stale
# copy is, and two answers to that question is the defect this class already banked.
from tools.stale_copy_refusal import READABLE, Unparseable, blob_at, judge, symbols

ROOT = Path(__file__).resolve().parent.parent

PRESERVED_PREFIX = "refs/preserved/refresh-to-head/"

#: The verdicts. Only REFRESHABLE may be written; everything else is a refusal or a no-op, and each
#: says which because a refusal that does not name its reason is how you never discover it was wrong.
REFRESHABLE = "refreshable"
AT_HEAD = "already_at_head"
NO_BASE = "refused_no_base"
NO_READER = "refused_no_reader"
UNPARSEABLE = "refused_unparseable"
SUPPLIES_NEW = "refused_supplies_names_head_lacks"
NOT_SUPERSEDED = "refused_head_does_not_supersede_it"
STAGED = "refused_holder_has_it_staged"


class RefreshError(RuntimeError):
    """The move could not be completed. FAIL-CLOSED: nothing is written after this is raised."""


def _git(root: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full = dict(os.environ, **(env or {}))
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                          check=False, env=full)


def _git_ok(root: Path, *args: str, env: dict | None = None) -> str:
    out = _git(root, *args, env=env)
    if out.returncode != 0:
        raise RefreshError("git {} rc={}: {}".format(
            " ".join(args[:2]), out.returncode, out.stderr.strip()[-300:]))
    return out.stdout


def _blob_bytes(root: Path, tree: str, path: str) -> bytes:
    """HEAD's bytes, read as BYTES and never as text. The working copy is about to be replaced by
    these exactly; a text round-trip would normalise line endings and land a diff nobody chose."""
    out = subprocess.run(["git", "show", "{}:{}".format(tree, path)], cwd=str(root),
                         capture_output=True, check=False)
    if out.returncode != 0:
        raise RefreshError("{} is not in HEAD at {}".format(path, root))
    return out.stdout


def _trivial(line: str) -> bool:
    s = line.strip()
    return len(s) < 12 or s.startswith(("#", "//", "*"))


@dataclass(frozen=True)
class Verdict:
    path: str
    state: str
    reason: str
    gains: tuple[str, ...] = ()       # names the copy supplies that HEAD does not
    discarded: tuple[str, ...] = ()   # lines the copy has that HEAD does not

    @property
    def refused(self) -> bool:
        return self.state not in (REFRESHABLE, AT_HEAD)

    def render(self) -> str:
        body = "  {}  [{}]\n      {}\n".format(self.path, self.state, self.reason)
        for name in self.gains[:8]:
            body += "        + {}\n".format(name[:110])
        if len(self.gains) > 8:
            body += "        (+{} more name(s))\n".format(len(self.gains) - 8)
        if self.state == REFRESHABLE:
            body += "      LINES THAT WILL BE DISCARDED ({}), recoverable from the preserved " \
                    "commit:\n".format(len(self.discarded))
            for line in self.discarded[:10]:
                body += "        - {}\n".format(line[:110])
            if len(self.discarded) > 10:
                body += "        (+{} more line(s))\n".format(len(self.discarded) - 10)
        return body


def _discarded_lines(head_text: str, work_text: str) -> tuple[str, ...]:
    """Every line the working copy has and HEAD does not, in file order.

    This is what the caller is being asked to sign off, and it is LINE granularity on purpose: the
    symbol-set test that licenses the refresh is blind to a reworded error string or a changed
    constant, so the thing it cannot see is printed rather than inferred to be absent."""
    diff = difflib.unified_diff(head_text.splitlines(), work_text.splitlines(), n=0, lineterm="")
    return tuple(ln[1:].strip() for ln in diff
                 if ln.startswith("+") and not ln.startswith("+++") and ln[1:].strip())


def _staged_paths(root: Path) -> frozenset[str]:
    out = _git(root, "diff", "--cached", "--name-only")
    return frozenset(p.strip() for p in out.stdout.splitlines() if p.strip())


def judge_copy(root: Path, path: str, staged: frozenset[str] | None = None) -> Verdict:
    """The whole precondition for one path. Reads; writes nothing, ever."""
    staged = _staged_paths(root) if staged is None else staged
    if Path(path).suffix not in READABLE:
        return Verdict(path, NO_READER,
                       "this control has no reader for {} files, so it CANNOT establish that the "
                       "copy has nothing to lose. An unavailable check is a failed check.".format(
                           Path(path).suffix or "extension-less"))
    head_text = blob_at(root, "HEAD", path)
    if head_text is None:
        return Verdict(path, NO_BASE,
                       "HEAD has no such path, so there is nothing for HEAD to supersede it with.")
    try:
        work_text = (root / path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return Verdict(path, NO_BASE, "the working copy could not be read: {}".format(exc))
    if work_text == head_text:
        return Verdict(path, AT_HEAD, "identical to HEAD -- nothing to refresh.")
    if path in staged:
        return Verdict(path, STAGED,
                       "the holder has this path STAGED. A commit from that index makes the tree "
                       "from the INDEX copy, not the working one, so refreshing the working copy "
                       "would leave the revert armed while looking repaired.")
    try:
        head_names, work_names = symbols(head_text, path), symbols(work_text, path)
    except Unparseable as exc:
        return Verdict(path, UNPARSEABLE,
                       "{} -- an unparseable blob is a finding, never a skip.".format(exc))
    if head_names is None or work_names is None:
        return Verdict(path, NO_READER,
                       "no symbol reader for this path, so 'supplies nothing HEAD lacks' is "
                       "unestablished and the refresh is not licensed.")
    gains = tuple(sorted(work_names - head_names))
    if gains:
        return Verdict(path, SUPPLIES_NEW,
                       "this copy SUPPLIES {} name(s) HEAD does not have, so it is not a copy HEAD "
                       "supersedes -- it is holder work. Use `python3 -m tools.isolate_hunks "
                       "--survey {}` and land those hunks over HEAD.".format(len(gains), path),
                       gains=gains)
    loss = judge(root, path, head_text, work_text)
    if loss is None:
        return Verdict(path, NOT_SUPERSEDED,
                       "the stale-copy control has NO complaint about this copy: it does not "
                       "predate the last landing here and it deletes no name. Refreshing it would "
                       "discard an ordinary edit, which is `git checkout <path>` with a nicer name "
                       "-- and that is forbidden here for this exact reason.")
    return Verdict(path, REFRESHABLE,
                   "rival copy: supplies no name HEAD lacks, and the stale-copy control refuses it "
                   "[{}]. HEAD strictly supersedes it.".format(loss.rule),
                   discarded=_discarded_lines(head_text, work_text))


# ------------------------------------------------------------------------------ preservation


def preserve(root: Path, paths: list[str], slug: str, message: str) -> tuple[str, str]:
    """Commit the CURRENT bytes of `paths` onto `refs/preserved/refresh-to-head/<slug>`.

    Returns (ref, commit sha). Raises rather than returning a failure, because every caller's next
    act is the destructive one and a preservation that merely reported trouble would be read past.

    THE TREE IS HEAD'S, WITH THESE PATHS SWAPPED IN, built through a THROWAWAY INDEX
    (`GIT_INDEX_FILE`) so the holder's real index is not touched -- their staged work is not this
    tool's to move. The parent is HEAD, which makes the commit's own diff exactly the bytes being
    destroyed: that is what `git log --all -S <a line of it>` searches, so the recovery route the
    caller is told about is the one the commit actually supports.
    """
    if not paths:
        raise RefreshError("nothing to preserve")
    with tempfile.TemporaryDirectory() as tmp:
        env = {"GIT_INDEX_FILE": str(Path(tmp) / "index")}
        _git_ok(root, "read-tree", "HEAD", env=env)
        for path in paths:
            entry = _git_ok(root, "ls-tree", "HEAD", "--", path).split()
            if not entry:
                raise RefreshError("{} is not in HEAD; refusing to preserve".format(path))
            mode = entry[0]
            blob = _git_ok(root, "hash-object", "-w", "--", str(root / path)).strip()
            _git_ok(root, "update-index", "--add", "--cacheinfo",
                    "{},{},{}".format(mode, blob, path), env=env)
        tree = _git_ok(root, "write-tree", env=env).strip()
    head = _git_ok(root, "rev-parse", "HEAD").strip()
    commit = _git_ok(root, "commit-tree", tree, "-p", head, "-m", message).strip()
    ref = PRESERVED_PREFIX + slug
    _git_ok(root, "update-ref", ref, commit)
    return ref, commit


def verify_recoverable(root: Path, commit: str, path: str, work_bytes: bytes,
                       probe: str | None) -> str:
    """Prove the bytes come back BEFORE they are destroyed. Returns the recovery command to print.

    Two legs, and the second is the one that matters. The first is identity -- the blob under the
    preserved commit hashes to what is on disk right now. The second RUNS the `git log --all -S`
    lookup this tool advertises: a preserved commit that the advertised search cannot find is a
    preservation in name only, and the difference is invisible until someone needs it.
    """
    stored = subprocess.run(["git", "show", "{}:{}".format(commit, path)], cwd=str(root),
                            capture_output=True, check=False)
    if stored.returncode != 0 or stored.stdout != work_bytes:
        raise RefreshError(
            "PRESERVATION FAILED for {}: the blob under {} is not the bytes on disk. Nothing has "
            "been written.".format(path, commit[:9]))
    if probe is None:
        # A copy that differs from HEAD only by DELETIONS has no line of its own to search for.
        # Say so rather than printing a `-S` command that would find nothing.
        return "git show {}:{}   # (this copy has no line HEAD lacks, so -S has no probe)".format(
            commit[:9], path)
    found = _git(root, "log", "--all", "--max-count=1", "--format=%H", "-S", probe, "--", path)
    if commit not in found.stdout:
        raise RefreshError(
            "PRESERVATION FAILED for {}: `git log --all -S` does not find {} -- the advertised "
            "recovery route does not reach it. Nothing has been written.".format(path, commit[:9]))
    return "git log --all -S {!r} -- {}".format(probe, path)


def _probe(verdict: Verdict) -> str | None:
    candidates = [ln for ln in verdict.discarded if not _trivial(ln)]
    return max(candidates, key=len) if candidates else None


# ------------------------------------------------------------------------------------ the move


def refresh(root: Path, paths: list[str], slug: str | None, write: bool) -> tuple[int, str]:
    """Survey, and when `write` is set and EVERY named path is refreshable, do it."""
    staged = _staged_paths(root)
    verdicts = [judge_copy(root, path, staged) for path in paths]
    report = "".join(v.render() for v in verdicts)
    refusals = [v for v in verdicts if v.refused]
    doable = [v for v in verdicts if v.state == REFRESHABLE]

    if refusals:
        return 1, ("\n[refresh-to-head] ❌ {} of {} path(s) REFUSED -- nothing written.\n\n{}".format(
            len(refusals), len(verdicts), report))
    if not write:
        return 0, ("\n[refresh-to-head] {} path(s) refreshable, {} already at HEAD. SURVEY ONLY -- "
                   "re-run with --write --slug NAME to perform it.\n\n{}".format(
                       len(doable), len(verdicts) - len(doable), report))
    if not doable:
        return 0, "\n[refresh-to-head] every named path is already at HEAD -- nothing to do.\n"
    if not slug:
        return 1, ("\n[refresh-to-head] ❌ --write needs --slug NAME. The preservation ref is how "
                   "anyone finds these bytes again by name; an unnamed one is findable only by "
                   "someone who already knows what to search for.\n")

    targets = [v.path for v in doable]
    current = {p: (root / p).read_bytes() for p in targets}
    ref, commit = preserve(root, targets, slug, (
        "preserved rival working copies before refresh-to-head: {}\n\n"
        "These copies supplied no name HEAD lacks and the stale-copy control refused each of "
        "them, so HEAD strictly supersedes them and tools/refresh_to_head.py wrote HEAD's bytes "
        "over them. This commit is on no branch and is merged nowhere; it exists so the bytes "
        "are findable.".format(", ".join(targets))))

    routes = []
    for verdict in doable:
        routes.append((verdict.path,
                       verify_recoverable(root, commit, verdict.path,
                                          current[verdict.path], _probe(verdict))))
    for path in targets:
        (root / path).write_bytes(_blob_bytes(root, "HEAD", path))

    lines = "".join("  {}\n      recover with: {}\n".format(p, cmd) for p, cmd in routes)
    return 0, ("\n[refresh-to-head] ✅ refreshed {} path(s) to HEAD at {}.\n"
               "  preserved as {} ({})\n{}\n{}".format(
                   len(targets), root, ref, commit[:9], lines, report))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="repo-relative path(s) to refresh")
    ap.add_argument("--root", default=str(ROOT), help="the repository holding the rival copies")
    ap.add_argument("--write", action="store_true", help="perform it (default is survey only)")
    ap.add_argument("--slug", help="names the refs/preserved/refresh-to-head/<slug> ref")
    args = ap.parse_args(argv)
    try:
        rc, text = refresh(Path(args.root), args.paths, args.slug, args.write)
    except RefreshError as exc:
        print("\n[refresh-to-head] ❌ {}".format(exc))
        return 1
    print(text)
    return rc


if __name__ == "__main__":  # pragma: no cover -- entry point
    raise SystemExit(main())
