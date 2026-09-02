"""Tree divergence — how much uncommitted work is squatting in the shared tree, and whose.

THE RULING (director, DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09): the publish gate's
subject became a clean checkout of HEAD, so a lane's uncommitted work can no longer halt
publishing. That removes the punishment; this module supplies the accountability that replaces
it. Verbatim: *"squatting gets named daily, never punished via the public site."*

WHY IT IS NEEDED. Once the gate stops reading the working tree, uncommitted work becomes free —
and unmeasured. On 2026-08-09 KNIFE2 left 19 source files in the tree, committed nowhere on any
ref, while its atom was certified L2; the machine only noticed because those files reddened the
gate. Under the new gate nothing would have noticed at all. So the cost has to be MEASURED and
NAMED instead of enforced.

WHAT IT MEASURES (report-only, always):
  * COUNT   — source files diverging from HEAD. Generated artefacts are excluded, because the
              publish path rewrites ~180 of them every cycle and a measure that counts those
              reads as noise no matter how carefully anyone looks at it.
  * AGE     — how long the oldest divergence has sat, from file mtime.
  * BY LANE — attributed through `maturity_map.yaml`'s `file_scope`, where the map declares one.

TWO HONEST LIMITS, stated because a measure that hides its own error bars invites false
confidence:
  1. ATTRIBUTION IS PARTIAL. Many atoms carry `file_scope: []`, so a diverging file often maps to
     no atom at all. Those are reported as `unattributed:<top-dir>` rather than guessed at. The
     number of unattributed files is itself published — if it dominates, the measure is weak and
     says so.
  2. AGE IS MTIME, AND MTIME LIES UNDER MERGE. A merge rewrites every file it touches, so all 19
     KNIFE2 files shared one mtime (15:31:46Z) that was hours younger than the work. Age is
     therefore a FLOOR on how long something has squatted, never the true age. Treated as a
     signal, not a clock.

NEVER PUNISHES. Nothing here returns a value the publish path can block on. `--check` exits
non-zero for a human/cron caller, but the publish path only ever calls `write_artifact()`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from tools import maturity_map_store as map_store

PROJECT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_PATH = PROJECT_DIR / "docs" / "observability" / "tree_divergence.json"
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

# Paths the machine REWRITES every publish cycle. Divergence here is the pipeline breathing, not
# a lane squatting, and counting it would bury the signal (~180 of 236 changed paths on the day
# this was written).
GENERATED_PREFIXES = (
    "docs/observability/",
    "docs/reports/",
    "docs/market_data/",
    "docs/snapshots/",
    "docs/shadow/",
    "docs/state/",
    "site/",
    "node_modules/",
)

# Runtime state, excluded by CONVENTION rather than by list: in this repo a dotfile is machine
# state (`.tree.lock`, `.maintenance_reminder_sent.json`, `.publish_gate_state.json`,
# `.dispatcher_seen.json`), while source never starts with a dot. Both of the first two took the
# "oldest divergence" slot on this module's first runs -- i.e. the measure was reporting its own
# machinery, and `.tree.lock` is literally the lock the publish path holds while being measured.
# A directory dotted at some level (`.claude/hooks/foo.py`) is NOT caught, which is correct: that
# is real source.
def _is_runtime_state(rel: str) -> bool:
    return rel.rsplit("/", 1)[-1].startswith(".")

# Thresholds. Chosen against the measured KNIFE2 episode (19 files, >1h) so that episode would
# have paged; deliberately not tighter, because a daily naming that fires every day names nothing.
FILE_COUNT_THRESHOLD = 15
AGE_HOURS_THRESHOLD = 4.0


# THE ONE MIXED PREFIX (2026-08-26, found while closing the 436-file walk). Every other entry in
# GENERATED_PREFIXES is owned end-to-end by one writer -- `docs/reports/` by the report generator,
# `site/` by the publisher, `docs/state/` by the run. `docs/observability/` is not: it is the
# machine's log directory AND the place agents write findings, audits, walks, retros and director
# reports. Excluding it wholesale therefore hid AUTHORED PROSE, and did:
# `docs/observability/DIRECTOR_REPORT_2026-08-20.md` -- a written report to the director -- sat
# UNTRACKED for six days while this measure, running every publish cycle, could not see it. The
# walk that closed the 436 lives in that same directory and was invisible for the same reason.
#
# The narrowing is UNTRACKED + `.md` + not `*-log.md`, and each clause earns its place:
#   * untracked -- the machine's own documents under this prefix are all TRACKED and rewritten in
#     place (`daily-self-note.md`, `autonomous-turn-output.md`); a brand-new `.md` here was
#     authored, not generated. This is also what keeps the daily churn out.
#   * `.md`      -- the JSON/JSONL ledgers under this prefix are machine state, no exceptions.
#   * not `*-log.md` -- the append-only logs (`supervisor-log.md`, `delivery-seat-log.md`) are
#     machine-written and several are untracked by design.
# The residual carve-out is named and both directions are tested, so it can FAIL (R15): an
# authored document fires, a log does not.
OBSERVABILITY_PREFIX = "docs/observability/"


def _is_authored_document(rel: str, untracked: bool) -> bool:
    """An untracked, non-log Markdown document under the one mixed prefix is authored prose."""
    if not untracked or not rel.startswith(OBSERVABILITY_PREFIX):
        return False
    name = rel.rsplit("/", 1)[-1]
    if name.startswith(".") or not name.endswith(".md"):
        return False
    return not name.endswith("-log.md")


def _is_generated(rel: str, untracked: bool = False) -> bool:
    if _is_authored_document(rel, untracked):
        return False
    return rel.startswith(GENERATED_PREFIXES) or _is_runtime_state(rel)


#: THE BASE THIS MODULE MEASURES AGAINST, and why reading it is not optional.
#:
#: `git status` answers against local `HEAD`. On 2026-09-01 local `HEAD` stood 15 commits ahead
#: of `origin/main` and 20 behind it, and 9 of the files counted here as squatting were
#: byte-identical to `origin/main` -- landed, pushed work that the local base cannot see.
#: `background/autonomous_runner.py` was one: it paged four reds through two consecutive
#: operational-layer signals while being exactly what is on the trunk, and two of those four
#: tests do not even exist at local HEAD. A direction was issued to "land or park" another such
#: file, and the tick that drew it spent its turn proving the premise false.
#:
#: So "diverges from HEAD" is TWO different findings wearing one number, and they have opposite
#: repairs: one is a lane's unfinished work, the other is a stale base. This module already
#: refuses to report a count when `git status` cannot answer; a count that cannot separate those
#: two is unavailable in the same way, and is refused the same way.
REMOTE_BASE = "origin/main"


def _base_state(project_dir: Path | None = None) -> tuple[dict | None, str]:
    """How far local `HEAD` is from `origin/main`. Three answers, and the third is the refusal.

      * `({"behind": n, "ahead": n}, "")` — the trunk is there and was read.
      * `({"no_remote_base": True}, "")` — there is NO `origin/main` in this repo. Not a failure:
        a checkout with no remote (the publish gate archives HEAD into exactly one) has no trunk
        to be stale against, so the count is measured against the only base there is. It is
        published as this rather than as `behind: 0` so no reader can mistake "nothing to be
        behind" for "up to date with the trunk".
      * `(None, reason)` — the ref EXISTS and git still could not answer. That one is a refusal.

    Keeping the second case out of the refusal is the difference between a control and a nuisance:
    scoped any wider it reds every consumer in every archive checkout, which is a control failing
    against a passer-by rather than against its own defect.
    """
    root = project_dir or PROJECT_DIR
    try:
        present = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", "refs/remotes/{}".format(REMOTE_BASE)],
            cwd=str(root), capture_output=True, text=True, timeout=60)
        if present.returncode != 0:
            return {"no_remote_base": True}, ""
        out = subprocess.run(
            ["git", "rev-list", "--count", "--left-right", "{}...HEAD".format(REMOTE_BASE)],
            cwd=str(root), capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001 -- TimeoutExpired/OSError are "git could not answer"
        return None, "{}: {}".format(type(exc).__name__, exc)
    if out.returncode != 0:
        return None, "{} exists but cannot be read (git rev-list rc={}: {})".format(
            REMOTE_BASE, out.returncode,
            (out.stderr or "").strip().splitlines()[0] if out.stderr else "no stderr")
    parts = out.stdout.split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return None, "git rev-list {}...HEAD returned unreadable output {!r}".format(
            REMOTE_BASE, out.stdout.strip()[:80])
    return {"behind": int(parts[0]), "ahead": int(parts[1])}, ""


def paths_already_on_origin(project_dir: Path | None,
                            paths: list[str]) -> list[str] | None:
    """Of `paths`, those whose WORKING-TREE bytes are identical to `origin/main`'s.

    These are not squatting and naming them as such is the defect. They are work that reached the
    trunk while this checkout's `HEAD` stayed behind it.

    HASHED, NOT DIFFED, and the difference is load-bearing: `git diff origin/main -- <path>`
    ignores an UNTRACKED path entirely, so a file that is tracked upstream and untracked here --
    the commonest shape of this artefact -- would come back "no difference" and be counted as
    already-landed without anything having compared it. Hashing the working file against the
    upstream blob compares the only two things that matter, and cannot answer for a path it did
    not read. Returns None when git could not answer, so the caller can refuse rather than guess.
    """
    root = project_dir or PROJECT_DIR
    if not paths:
        return []
    existing = [p for p in paths if (root / p).is_file()]
    if not existing:
        return []
    try:
        tree = subprocess.run(["git", "ls-tree", "-r", REMOTE_BASE],
                              cwd=str(root), capture_output=True, text=True, timeout=120)
        hashed = subprocess.run(["git", "hash-object", "--", *existing],
                                cwd=str(root), capture_output=True, text=True, timeout=120)
    except Exception:  # noqa: BLE001 -- an unanswerable git is a refusal, handled by the caller
        return None
    if tree.returncode != 0 or hashed.returncode != 0:
        return None
    upstream: dict[str, str] = {}
    for line in tree.stdout.splitlines():
        meta, _, rel = line.partition("\t")
        bits = meta.split()
        if rel and len(bits) >= 3 and bits[1] == "blob":
            upstream[rel.strip().strip('"')] = bits[2]
    local = hashed.stdout.split()
    if len(local) != len(existing):
        return None
    return sorted(p for p, sha in zip(existing, local) if upstream.get(p) == sha)


#: How far back each suspect path's OWN history is searched for the working-tree bytes. A path that
#: reaches this without a match is reported UNPROVEN, never SAFE -- see `armed_revert_paths`. 25 is
#: a DIAL: it bounds the search, never whether the search happens. Both hazards this was written for
#: (the VAT pair, the level-anchor block) sat ONE commit back, and the artefact publishes the depth
#: so a reader gets the bound the search actually earns rather than assuming "everything".
#:
#: SET AT 500 FROM A MEASUREMENT, NOT A GUESS, AND RAISED FROM 25 (2026-09-02). At 25 the first real
#: run reported two files UNPROVEN -- `saas/reporting/annual_report.py` and
#: `tests/background/test_supervisor.py`. Searching their FULL history (219 and 51 commits) cleared
#: both as novel work, so the cap was producing false conservatism, not catching anything. The walk
#: is affordable at this depth precisely because the blob-existence filter runs FIRST: only 2 of 283
#: diverging files were ever walked. Raising it makes the check MORE complete, not quieter -- the
#: UNPROVEN class stays, and still fails closed for a path whose history outruns even this.
ARMED_REVERT_SEARCH_DEPTH = 500


def _batch_check(root: Path, queries: list[str]) -> dict[str, str] | None:
    """`git cat-file --batch-check` over `queries`. Maps query -> object id, omitting misses.

    Returns None when git could not answer, so every caller refuses rather than guessing.
    """
    if not queries:
        return {}
    try:
        proc = subprocess.run(["git", "cat-file", "--batch-check"],
                              cwd=str(root), input="\n".join(queries) + "\n",
                              capture_output=True, text=True, timeout=120)
    except Exception:  # noqa: BLE001 -- an unanswerable git is a refusal, handled by the caller
        return None
    if proc.returncode != 0:
        return None
    out: dict[str, str] = {}
    for query, line in zip(queries, proc.stdout.splitlines()):
        bits = line.split()
        if len(bits) >= 3 and bits[1] == "blob":
            out[query] = bits[0]
    return out


def armed_revert_paths(project_dir: Path | None,
                       paths: list[str]) -> tuple[list[dict] | None, list[str]]:
    """Of `paths`, those whose working-tree bytes are an OLDER COMMITTED VERSION of that same path.

    THIS IS THE POPULATION SPLIT, AND IT IS THE POINT. `changed_paths` counts one number across two
    populations whose remedies are opposite. A file holding NOVEL bytes is work in progress and the
    remedy is to LAND it. A file holding bytes this path already had at an ANCESTOR commit is an
    ARMED SILENT REVERT and the remedy is to RESTORE it to HEAD: the next *correct* pathspec commit
    that happens to include it undoes whatever HEAD holds, with no diff a reviewer would read as a
    revert. That is how the canonical VAT repair (`2bf3ad0aa`) came within one `git add` of being
    undone while the divergence alarm counted it as 1 of 272 and said "this blocks nothing".

    THE CHEAP FILTER IS EXACT ABOUT WHAT IT EXCLUDES, WHICH IS WHY IT IS SAFE. Novel bytes have no
    blob in the object store (`git hash-object` without `-w` writes nothing), so a blob that does
    NOT exist cannot be a previously-committed version and is dropped with certainty. Existence is
    necessary but NOT sufficient -- the same bytes may live at another path -- so every survivor is
    then confirmed against that path's OWN history. Filter for speed, confirm for truth.

    Returns `(armed, unproven)`. `armed` is a list of `{path, commit, subject}`. `unproven` names
    suspects whose history hit `ARMED_REVERT_SEARCH_DEPTH` without a match: NOT a clean bill, and
    published as its own field so the bound is on the surface rather than in a footnote.

    Returns `(None, [])` when git could not answer. `None` is deliberately not falsy-equivalent to
    `[]`: a new field that failed open to "nothing is armed" would reinstate, one field over, the
    exact defect `changed_paths` was repaired for in
    WORKER_FINDING_TREE_DIVERGENCE_FAILS_OPEN_TO_A_CLEAN_TREE.
    """
    root = project_dir or PROJECT_DIR
    existing = [p for p in (paths or []) if (root / p).is_file()]
    if not existing:
        return [], []
    try:
        head = subprocess.run(["git", "ls-tree", "-r", "HEAD"],
                              cwd=str(root), capture_output=True, text=True, timeout=120)
        hashed = subprocess.run(["git", "hash-object", "--", *existing],
                                cwd=str(root), capture_output=True, text=True, timeout=120)
    except Exception:  # noqa: BLE001 -- an unanswerable git is a refusal, handled by the caller
        return None, []
    if head.returncode != 0 or hashed.returncode != 0:
        return None, []
    head_blobs: dict[str, str] = {}
    for line in head.stdout.splitlines():
        meta, _, rel = line.partition("\t")
        bits = meta.split()
        if rel and len(bits) >= 3 and bits[1] == "blob":
            head_blobs[rel.strip().strip('"')] = bits[2]
    local = hashed.stdout.split()
    if len(local) != len(existing):
        return None, []

    # UNTRACKED CANNOT BE ARMED: with no entry at HEAD there is no version to revert TO. And a path
    # already equal to HEAD is not diverged at all.
    candidates = [(p, sha) for p, sha in zip(existing, local)
                  if p in head_blobs and head_blobs[p] != sha]
    if not candidates:
        return [], []

    present = _batch_check(root, [sha for _, sha in candidates])
    if present is None:
        return None, []
    suspects = [(p, sha) for p, sha in candidates if sha in present]

    armed: list[dict] = []
    unproven: list[str] = []
    for path, sha in suspects:
        try:
            hist = subprocess.run(
                ["git", "log", "--format=%H", "-n", str(ARMED_REVERT_SEARCH_DEPTH), "--", path],
                cwd=str(root), capture_output=True, text=True, timeout=120)
        except Exception:  # noqa: BLE001
            return None, []
        if hist.returncode != 0:
            return None, []
        commits = hist.stdout.split()
        at_commit = _batch_check(root, ["{}:{}".format(c, path) for c in commits])
        if at_commit is None:
            return None, []
        hit = next((c for c in commits if at_commit.get("{}:{}".format(c, path)) == sha), None)
        if hit is None:
            if len(commits) >= ARMED_REVERT_SEARCH_DEPTH:
                unproven.append(path)
            continue
        try:
            subj = subprocess.run(["git", "log", "--format=%s", "-1", hit],
                                  cwd=str(root), capture_output=True, text=True, timeout=60)
            subject = subj.stdout.strip() if subj.returncode == 0 else ""
        except Exception:  # noqa: BLE001
            subject = ""
        armed.append({"path": path, "commit": hit[:9], "subject": subject[:80]})
    return sorted(armed, key=lambda r: r["path"]), sorted(unproven)


def changed_paths(project_dir: Path | None = None) -> list[str] | None:
    """Repo-relative paths differing from HEAD (tracked modifications AND untracked files),
    generated artefacts excluded. Untracked counts: KNIFE2's new seam module was untracked, and
    an untracked file is the most invisible squat of all.

    RETURNS None WHEN GIT COULD NOT ANSWER -- never `[]`. This used to return the empty list on a
    non-zero `git status`, which every downstream reader then rendered as a genuinely clean tree:
    `measure()` reported `total_files: 0`, `breaches()` returned `[]`, and the daily naming said
    nothing. The artefact at HEAD proved it fired that way (`tree_divergence.json` at measured_at
    1786333430 recorded 0 files; the same tree measured 346 by hand six minutes later). Since this
    module is the whole accountability half of DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09,
    that silence made the ruling's cost side inert -- R15's third killer pattern exactly: an
    unavailable check is a FAILED check, not a pass.
    `None` is deliberately not falsy-equivalent to `[]` for a caller that checks `is None`, and
    the callers below all do. See WORKER_FINDING_TREE_DIVERGENCE_FAILS_OPEN_TO_A_CLEAN_TREE."""
    return _changed_paths_or_reason(project_dir)[0]


def _changed_paths_or_reason(project_dir: Path | None = None) -> tuple[list[str] | None, str]:
    """`changed_paths` plus WHY it could not answer. The reason travels with the failure rather
    than being re-derived downstream: a breach sentence that says only "unavailable" sends the
    reader back to re-run the thing that just failed."""
    root = project_dir or PROJECT_DIR
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                             cwd=str(root), capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001 -- TimeoutExpired/OSError are "git could not answer"
        return None, "{}: {}".format(type(exc).__name__, exc)  # timeout is reachable here
    if out.returncode != 0:
        return None, "git status rc={} ({})".format(
            out.returncode, (out.stderr or "").strip().splitlines()[0] if out.stderr else "no stderr")
    paths = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        untracked = line[:2] == "??"
        rel = line[3:].strip()
        if " -> " in rel:            # rename: take the destination
            rel = rel.split(" -> ", 1)[1]
        rel = rel.strip('"')
        if not _is_generated(rel, untracked):
            paths.append(rel)
    return sorted(set(paths)), ""


def _file_scope_index(map_path: Path | None = None) -> dict[str, str]:
    """path -> lane, from the map's declared `file_scope`. Best-effort and cheap: a line scan
    rather than a YAML load, because this runs every publish cycle and the map is ~400KB."""
    p = map_path or MAP_PATH
    index: dict[str, str] = {}
    try:
        text = map_store.map_text(p)
    except (OSError, map_store.MapStoreError):
        return index
    lane = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("lane:"):
            lane = s.split(":", 1)[1].strip()
        elif s.startswith("file_scope:") and lane:
            inner = s.split(":", 1)[1].strip().lstrip("[").rstrip("]")
            for item in inner.split(","):
                item = item.strip().strip("'\"")
                if item:
                    index[item] = lane
    return index


def lane_for(rel: str, index: dict[str, str]) -> str:
    """The lane that declared this path, or an explicit `unattributed:` label. Never guesses."""
    if rel in index:
        return index[rel]
    return "unattributed:" + (rel.split("/", 1)[0] if "/" in rel else rel)


def measure(project_dir: Path | None = None, now: float | None = None,
            map_path: Path | None = None) -> dict:
    """The whole measure. PURE-ish: reads git + mtimes, writes nothing."""
    root = project_dir or PROJECT_DIR
    now = time.time() if now is None else now
    index = _file_scope_index(map_path)
    by_lane: dict[str, dict] = {}
    oldest_age = 0.0
    oldest_path = None
    paths, why = _changed_paths_or_reason(root)
    base, base_why = _base_state(root)
    if paths is not None and base is None:
        # THE SAME REFUSAL, FOR THE SAME REASON. `git status` answered, but its answer is
        # against a base whose distance from the trunk is unknown, so "uncommitted" cannot be
        # told from "stale". An unavailable check is a FAILED check, not a clean tree, and it
        # is not a clean tree here either.
        paths, why = None, "cannot read the base this count is measured against -- {}".format(
            base_why or "reason unrecorded")
    if paths is None:
        # THE COUNTS ARE OMITTED, NOT ZEROED. A reader that has never heard of `unavailable`
        # gets a loud KeyError; it can no longer receive a quiet 0 and publish a clean bill of
        # health for a tree it never managed to look at. That asymmetry is the whole repair.
        return {
            "measured_at": now,
            "unavailable": True,
            "unavailable_reason": why,
            "thresholds": {"files": FILE_COUNT_THRESHOLD, "age_hours": AGE_HOURS_THRESHOLD},
        }
    for rel in paths:
        try:
            age = max(0.0, now - (root / rel).stat().st_mtime)
        except OSError:
            age = 0.0
        lane = lane_for(rel, index)
        row = by_lane.setdefault(lane, {"count": 0, "oldest_age_hours": 0.0, "oldest_path": None})
        row["count"] += 1
        if age > row["oldest_age_hours"] * 3600:
            row["oldest_age_hours"] = round(age / 3600, 2)
            row["oldest_path"] = rel
        if age > oldest_age:
            oldest_age, oldest_path = age, rel
    attributed = sum(v["count"] for k, v in by_lane.items() if not k.startswith("unattributed:"))
    landed = paths_already_on_origin(root, paths)
    armed, armed_unproven = armed_revert_paths(root, paths)
    return {
        "measured_at": now,
        "base": base,
        # THE POPULATION SPLIT. `total_files` counts work-in-progress and armed silent reverts
        # together, and their remedies are opposite (land it / restore it). `None` means git could
        # not answer and is NOT the same as "none armed" -- `breaches` names it as a failed check.
        "armed_reverts": None if armed is None else len(armed),
        "armed_revert_paths": None if armed is None else armed[:20],
        "armed_revert_unproven": armed_unproven,
        "armed_revert_search_depth": ARMED_REVERT_SEARCH_DEPTH,
        # Of `total_files`, the ones that are NOT squatting: identical to the trunk, invisible
        # here only because HEAD is behind it. `None` means git could not answer, which is why
        # the count is published beside the base rather than subtracted out of sight of it.
        "already_on_origin": None if landed is None else len(landed),
        "already_on_origin_paths": None if landed is None else landed[:20],
        "total_files": len(paths),
        "attributed_files": attributed,
        "unattributed_files": len(paths) - attributed,
        "oldest_age_hours": round(oldest_age / 3600, 2),
        "oldest_path": oldest_path,
        "by_lane": dict(sorted(by_lane.items(), key=lambda kv: -kv[1]["count"])),
        "thresholds": {"files": FILE_COUNT_THRESHOLD, "age_hours": AGE_HOURS_THRESHOLD},
    }


def breaches(m: dict) -> list[str]:
    """Threshold breaches, as sentences. PURE (mutation-testable). Empty == nothing to name.

    AN UNMEASURABLE TREE IS ITS OWN BREACH, and it is checked FIRST -- the daily naming has to
    keep firing when the measure fails, saying the true thing, or the ruling's accountability
    half goes quiet exactly when something is wrong with the machine."""
    out = []
    if m.get("unavailable"):
        return ["tree divergence could not be measured ({}); this is a FAILED check, "
                "not a clean tree".format(m.get("unavailable_reason") or "reason unrecorded")]
    if m["total_files"] > FILE_COUNT_THRESHOLD:
        out.append(
            "{} source files diverge from HEAD (threshold {})".format(
                m["total_files"], FILE_COUNT_THRESHOLD))
    # NAMED WHENEVER THE BASE IS STALE, not only when the count breaches. The count can sit
    # under the threshold while every file in it is already on the trunk, and that reader is
    # the one who goes and "finishes" a decision somebody already took.
    base = m.get("base") or {}
    if base.get("behind"):
        landed = m.get("already_on_origin")
        out.append(
            "HEAD is {} commit(s) behind {} (and {} ahead), so this count is measured against a "
            "stale base: {} of the {} are byte-identical to the trunk and are not uncommitted "
            "work".format(base["behind"], REMOTE_BASE, base.get("ahead"),
                          "an unknown number" if landed is None else landed,
                          m["total_files"]))
    if m["oldest_age_hours"] > AGE_HOURS_THRESHOLD:
        out.append(
            "the oldest has sat {}h (threshold {}h): {}".format(
                m["oldest_age_hours"], AGE_HOURS_THRESHOLD, m["oldest_path"]))
    # ARMED REVERTS HAVE NO THRESHOLD AND THAT IS DELIBERATE. The other two lines here are volume
    # measures with a dial, because divergence is normal and only its scale is a problem. This one
    # is a class, not a quantity: ONE file holding an ancestor version is one `git add` away from
    # silently undoing whatever HEAD holds, and 1 is not a smaller version of 272 -- it is a
    # different population. A threshold here would hide exactly the case this exists to catch.
    armed = m.get("armed_reverts")
    if armed is None:
        out.append(
            "whether any diverging file is an ARMED SILENT REVERT could not be measured; "
            "this is a FAILED check, not a clean tree")
    elif armed:
        named = ", ".join(
            "{} (would revert to {} {})".format(r["path"], r["commit"], r["subject"])
            for r in (m.get("armed_revert_paths") or [])[:3])
        out.append(
            "{} of the {} diverging file(s) hold an OLDER COMMITTED VERSION and are armed to "
            "silently revert HEAD on the next pathspec commit that includes them -- restore to "
            "HEAD, do not land: {}".format(armed, m["total_files"], named))
    unproven = m.get("armed_revert_unproven") or []
    if unproven:
        out.append(
            "{} file(s) could not be cleared of being an armed revert within {} commits of their "
            "own history and are UNPROVEN, not safe: {}".format(
                len(unproven), m.get("armed_revert_search_depth"), ", ".join(unproven[:3])))
    return out


#: How many multiples past a threshold stop a breach being routine. Set at 5x rather than
#: tuned: the breach this was written for stood at 29x the file line and 39x the age line,
#: so any value in this region separates it from the ordinary two-or-three-files-over that
#: the digest exists to absorb. It is a DIAL -- moving it changes what gets hoisted, never
#: whether the breach is measured or whether it blocks anything (it blocks nothing).
ESCALATION_MULTIPLE = 5.0


def severity(m: dict) -> dict:
    """HOW FAR over the line, not merely whether. PURE, so it can be mutation-tested.

    THE CONTROL FIRED CORRECTLY EVERY DAY AND COULD NOT BE HEARD (2026-08-26). This module
    is report-only by deliberate design and that design is right -- the publish gate's
    subject is a clean HEAD checkout precisely so a lane's uncommitted work cannot halt
    publishing. But report-only had come to mean "one line in a batched digest", and
    `process_run_complete._publish_tree_divergence` routes to that digest on CATEGORY alone.
    So 436 files at 29x the file threshold, with the oldest at 158h against a 4h line, read
    exactly like three files two hours over. It was named daily for six days and absorbed
    every time.

    A control that fires and cannot be heard is the same family as a control that cannot
    fire, and it fails the same way: the reader learns nothing from the alarm's presence.
    The repair is not a louder alarm for everything -- that re-teaches the same lesson one
    volume up -- it is to make MAGNITUDE part of the routing decision, so the ordinary case
    stays batched and the extraordinary one arrives as itself.

    Returns the worst multiple on each axis and whether either is past
    `ESCALATION_MULTIPLE`. An UNMEASURABLE tree is severe: it is the one state where the
    reader most needs to hear something, and it is the state a fail-open would swallow.
    """
    if m.get("unavailable"):
        return {"severe": True, "file_multiple": None, "age_multiple": None,
                "worst_multiple": None,
                "reason": "the tree could not be measured, which is a FAILED check"}
    file_mult = m["total_files"] / FILE_COUNT_THRESHOLD if FILE_COUNT_THRESHOLD else 0.0
    age_mult = m["oldest_age_hours"] / AGE_HOURS_THRESHOLD if AGE_HOURS_THRESHOLD else 0.0
    worst = max(file_mult, age_mult)
    severe = worst >= ESCALATION_MULTIPLE
    return {
        "severe": severe,
        "file_multiple": round(file_mult, 1),
        "age_multiple": round(age_mult, 1),
        "worst_multiple": round(worst, 1),
        "reason": (
            "{}x the file line ({} vs {}) and {}x the age line ({}h vs {}h)".format(
                round(file_mult, 1), m["total_files"], FILE_COUNT_THRESHOLD,
                round(age_mult, 1), m["oldest_age_hours"], AGE_HOURS_THRESHOLD)
            if severe else "within {}x of both lines".format(ESCALATION_MULTIPLE)
        ),
    }


def top_squatters(m: dict, n: int = 3) -> str:
    if m.get("unavailable"):   # called in the same log line as the counts; must not raise into
        return "unknown (measure unavailable)"   # the publish path this module observes
    rows = [(k, v) for k, v in m["by_lane"].items()][:n]
    return "; ".join("{} ({} files, oldest {}h)".format(k, v["count"], v["oldest_age_hours"])
                     for k, v in rows) or "none"


def divergence_state(m: dict) -> str:
    """The IDENTITY of a squat, for the notification contract's transition check.

    A STATE THAT MOVES EVERY CYCLE IS A TRANSITION CHECK THAT CANNOT SUPPRESS ANYTHING (2026-09-01,
    director: *"the channel under-reports you… divergence and publishing alarms filled the mirror.
    I've read that as a stall twice today when you were working normally."*).

    `top_squatters(m)` was being passed as `state`, and it carries `oldest_age_hours` — a clock. So
    one unchanging condition (the same file, ageing 92.6h → 110.4h across the day) presented as a
    NEW state on every publish cycle: **27 pages, 42% of everything the director received that day,
    all of them the same squat.** Transition-only (G-N1/R5) was fully engaged and had nothing to
    compare, because no two firings were ever equal.

    Worse, and this is the part that mattered: `alarm_repetition`'s escalation — the mechanism that
    turns a repeating alarm into a DRAWN WORK ITEM and then stops re-telling him — counts REPEATS of
    an unchanged state. A state that never repeats never escalates. The one condition that most
    deserved to become work was the one condition structurally unable to.

    The author's intent was already right and is stated in the caller: *"keying state on the lane
    table rather than the raw counts means the generated-file churn that moves the total every cycle
    does not re-page; a lane appearing, growing or leaving does."* The implementation then used a
    function containing both a clock and the counts.

    SO THE STATE IS THE LANE SET AND NOTHING ELSE. A lane starting or finishing a squat is a real
    change and pages. A standing squat ageing or wobbling by a few files is the same condition, is
    named DAILY by `re_escalate_after`, and becomes a work item after three repeats. Every number
    stays in the MESSAGE, where the reader wants it; none of it is in the identity.
    """
    if m.get("unavailable"):
        return "unavailable"
    return "lanes:" + ",".join(sorted(m.get("by_lane", {})))


def write_artifact(m: dict, path: Path | None = None) -> Path:
    """Publish the measure. Called from the publish path; must never raise into it."""
    p = path or ARTIFACT_PATH
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:  # noqa: BLE001 -- an observer that can raise into the publish path it
        pass           # observes is itself a defect; the artefact is never load-bearing.
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Measure uncommitted divergence from HEAD, by lane.")
    ap.add_argument("--json", action="store_true", help="print the artefact")
    ap.add_argument("--check", action="store_true", help="exit 1 on a threshold breach")
    ap.add_argument("--write", action="store_true", help="write the artefact")
    args = ap.parse_args(argv)

    m = measure()
    if args.write:
        write_artifact(m)
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
    elif m.get("unavailable"):
        print("tree divergence: UNAVAILABLE — " + (m.get("unavailable_reason") or "unrecorded"))
    else:
        base = m.get("base") or {}
        print("tree divergence: {} source file(s) vs HEAD, oldest {}h ({} attributed, "
              "{} unattributed) — HEAD is {} behind / {} ahead of {}, {} of the {} already on "
              "the trunk".format(m["total_files"], m["oldest_age_hours"],
                                 m["attributed_files"], m["unattributed_files"],
                                 base.get("behind"), base.get("ahead"), REMOTE_BASE,
                                 m.get("already_on_origin"), m["total_files"]))
        print("  top: " + top_squatters(m))
    for b in breaches(m):
        print("  BREACH: " + b)
    return 1 if (args.check and breaches(m)) else 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/tree_divergence.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("tree_divergence")
    raise SystemExit(main())
