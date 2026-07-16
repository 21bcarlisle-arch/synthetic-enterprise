#!/usr/bin/env python3
"""Activity-based cost + utilisation -- is the machine spending resources on
PRODUCT, or on ITSELF? (atom G11_activity_cost_utilisation,
docs/staging/done/ACTIVITY_COST_AND_UTILISATION.md).

This is a REPORTING layer, not new instrumentation. It attributes two resources
-- SEPARATELY -- to a PRODUCTIVE/WASTE activity taxonomy, from data that ALREADY
EXISTS in this repo:

  * ELAPSED TIME  (the UTILISATION denominator) -- from git commit timestamps:
    the bounded gap before each commit is the work-time that produced it. Gaps
    longer than IDLE_GAP_CAP_SECONDS are treated as WASTE/idle, never billed to
    the commit that eventually landed (so an overnight pause is not counted as
    hours of "product" work). The clock is git commit time (%ct).

  * TOKENS       (the COST denominator) -- parsed from
    docs/observability/token-log.md (one "Frontier tokens:" line per session
    entry). Token data is coarse and sparse (~one entry per multi-phase
    session); entries that do not parse are reported as `unattributed`, NEVER
    fabricated as zero.

Time and cost are tracked separately ON PURPOSE: they diverge, and the
DIVERGENCE is the signal (e.g. lots of wall-clock spent on self-repair while
few tokens went there, or vice-versa).

Taxonomy (the 7 buckets from the staged design):
  PRODUCTIVE/product              -- building/running the actual product
  PRODUCTIVE/discovery            -- discovery/framing/research/retro (investment)
  WASTE/self-repair               -- the machine fixing its own plumbing
  WASTE/idle                      -- elapsed time with no work landing
  WASTE/hit-limit                 -- usage-limit interruptions
  WASTE/rework                    -- reverts, re-draws, redoing landed work
  WASTE/idle-waiting-on-director  -- blocked on a director decision

================================ GUARDRAIL ================================
UTILISATION IS A DIAGNOSTIC, NEVER A TARGET (same law as G5 sizing / R12
anti-goal-seek). 40% productive-and-correct beats 90% busy-and-wrong. NOTHING
here may be computed in a way that could be tuned to make the number look good,
and no figure here is ever a completion gate or a thing to hit -- the moment it
becomes a target it manufactures the deadline pressure that produces false
self-certified levels, AND it corrupts the very actuals it reports. This
guardrail is carried on the rendered surface and in the emitted JSON, not just
this docstring.
==========================================================================

FAIL-HONEST (R15 fail-open discipline): missing or unparseable data degrades to
a visible "unattributed" / "insufficient_data" status, never a fabricated zero.
An unclassifiable commit is counted under `unattributed`, surfaced, and excluded
from the numerator/denominator of every rate -- it is not silently dropped into
"productive".

Read-only. Git subprocess reads + file reads only; no repo mutation, no edit to
maturity_map.yaml.

CLI:
    python3 -m tools.activity_cost            # human-readable summary
    python3 -m tools.activity_cost --json      # full report as JSON
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROJECT = Path(__file__).resolve().parent.parent
TOKEN_LOG = PROJECT / "docs" / "observability" / "token-log.md"
ACTION_NEEDED = PROJECT / "docs" / "observability" / "action_needed_register.json"

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------
PRODUCT = "PRODUCTIVE/product"
DISCOVERY = "PRODUCTIVE/discovery"
SELF_REPAIR = "WASTE/self-repair"
IDLE = "WASTE/idle"
HIT_LIMIT = "WASTE/hit-limit"
REWORK = "WASTE/rework"
IDLE_DIRECTOR = "WASTE/idle-waiting-on-director"
UNATTRIBUTED = "unattributed"

PRODUCTIVE_CLASSES = (PRODUCT, DISCOVERY)
WASTE_CLASSES = (SELF_REPAIR, IDLE, HIT_LIMIT, REWORK, IDLE_DIRECTOR)
# "problems" the machine had to deal with, for value-per-problem (excludes plain
# idle, which is absence-of-work, not a problem the machine created/fixed).
PROBLEM_CLASSES = (SELF_REPAIR, HIT_LIMIT, REWORK)
ALL_CLASSES = PRODUCTIVE_CLASSES + WASTE_CLASSES

# Any inter-commit gap longer than this is WASTE/idle, not work-time billed to
# the commit that landed. 30 min: comfortably above this repo's real p90
# commit-to-commit gap (~15 min, measured), below an overnight pause. A DIAL:
# the cap trades "idle undercount" (too high) against "product overcount" (too
# low); documented, never tuned to move a headline number.
IDLE_GAP_CAP_SECONDS = 30 * 60

GUARDRAIL = (
    "DIAGNOSTIC, NEVER A TARGET (R12 / G5 law). 40% productive-and-correct "
    "beats 90% busy-and-wrong. No figure here is a completion gate or a thing "
    "to hit -- tuning the machine to make utilisation look good corrupts the "
    "very actuals it reports."
)

FRAMING = (
    "Is the machine spending its resources on PRODUCT or on ITSELF? This "
    "attributes elapsed TIME (the utilisation denominator, from git commit "
    "timestamps) and TOKENS (the cost denominator, from the token log) -- "
    "SEPARATELY, because they diverge and the divergence is signal -- to a "
    "productive/waste activity taxonomy built entirely from data this repo "
    "already keeps. A reporting layer, not new instrumentation."
)

# ---------------------------------------------------------------------------
# Path domains -- which part of the machine a commit touched. Used to settle the
# genuinely ambiguous case (a "Fix" commit is self-repair IFF it repaired the
# plumbing; a fix to the product is product work).
# ---------------------------------------------------------------------------
INFRA_PREFIXES = (
    "background/", "tools/", ".claude/", "docs/observability/",
    "session_watchdog", "autonomous_runner",
)
PRODUCT_PREFIXES = (
    "company/", "sim/", "saas/", "simulation/", "interface/", "site/", "data/",
)
DISCOVERY_PREFIXES = (
    "docs/design/", "docs/staging/", "docs/market_research/", "docs/claude/",
    "docs/domain_artefact_library/", "docs/retrospectives/", "docs/curriculum/",
)

# The transition arrow "-> L3" -- a landed level bump is product output.
_ARROW_RE = re.compile(r"->\s*L\d+")

# Subject-keyword signals, checked in the documented order in classify_commit().
# Word-ish boundaries where a substring would false-match (rework/revert etc.).
_REWORK_RE = re.compile(
    r"\b(rework|revert|re-draw|redraw|re-do|redo|false completion|"
    r"two-strike|back ?out|backed out|undo)\b",
    re.IGNORECASE,
)
# HIT-LIMIT is an ACTUAL usage-limit INTERRUPTION (the machine stopped because it
# ran out), NOT a commit that merely BUILDS/FIXES usage-limit handling (that is
# self-repair). Tightened to interruption-markers only, after a real-commit audit
# found "tighten usage-limit detection", "usage-limit auto-resume", "Cloudflare
# quota" (a deploy-contention plumbing issue) all mis-billed as hit-limit WASTE.
_HIT_LIMIT_RE = re.compile(
    r"\b(usage[- ]limit reached|hit (?:the )?(?:usage|rate)[- ]?limit|"
    r"out of tokens|rate[- ]?limited|quota exceeded|"
    r"paused[:,]? usage[- ]limit|5-?hour (?:window|cap) (?:hit|reached))\b",
    re.IGNORECASE,
)
# DIRECTOR-BLOCK requires BOTH the word "director" AND a block/escalation cue --
# a real-commit audit found the bare "escalat"/"one-way door" catch mislabelling
# product features ("Ombudsman escalation" in complaint management) and plumbing
# fixes ("fix escalation gap in the twin") as idle-waiting-on-director. The honest
# source for the idle-on-director METRIC is the escalation register (director_idle),
# not commit subjects; this subject rule is deliberately narrow. Dual-lookahead:
# both a director mention and a block cue must appear somewhere in the subject.
_DIRECTOR_RE = re.compile(
    r"(?=.*\bdirector\b)"
    r"(?=.*\b(?:await\w*|blocked|waiting|escalat\w*|one[- ]way door|idle[- ]?waiting)\b)",
    re.IGNORECASE | re.DOTALL,
)
_FIX_RE = re.compile(
    r"\b(fix|hotfix|housekeeping|unblock|unstick|stale|leak|repair|patch|"
    r"restart|wedge|jam|flake|flaky|regression|broke|broken)\b",
    re.IGNORECASE,
)
_DISCOVERY_RE = re.compile(
    r"\b(discover|frame|framing|register|registered|retro|retrospective|"
    r"research|charter|red[- ]team|survey|proposal|scope|decompose|meta-finding)\b",
    re.IGNORECASE,
)
_PRODUCT_RE = re.compile(
    r"\b(build|migrate|wire|wave|fold|merge|auto-process|run complete|"
    r"harden|hardening|deploy|publish|generate|render|dashboard)\b",
    re.IGNORECASE,
)


@dataclass
class Commit:
    sha: str
    timestamp: int  # unix epoch seconds, git commit time (%ct)
    subject: str
    files: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Git history walk (read-only)
# ---------------------------------------------------------------------------
def git_log_commits(repo_root: Path = PROJECT, limit: Optional[int] = None) -> list[Commit]:
    """Walk `git log` (whole history unless `limit`), capturing per-commit
    subject + changed file list. One `git log --name-only` read; no mutation."""
    fmt = "__C__%x1f%H%x1f%ct%x1f%s"
    cmd = ["git", "log", "--name-only", f"--pretty=format:{fmt}"]
    if limit:
        cmd.insert(2, f"-{int(limit)}")
    try:
        out = subprocess.run(
            cmd, cwd=repo_root, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    commits: list[Commit] = []
    cur: Optional[Commit] = None
    for line in out.splitlines():
        if line.startswith("__C__"):
            parts = line.split("\x1f")
            # parts = ["__C__", sha, ct, subject]
            if len(parts) >= 4:
                cur = Commit(sha=parts[1], timestamp=int(parts[2]), subject=parts[3])
                commits.append(cur)
        elif line.strip() and cur is not None:
            cur.files.append(line.strip())
    return commits


def _domain(files: list) -> str:
    """Which domain a commit's changed files predominantly touch:
    'infra' | 'product' | 'discovery' | 'mixed_or_unknown'. Plurality by file
    count; ties / no-match -> 'mixed_or_unknown' (honest, not forced)."""
    counts = {"infra": 0, "product": 0, "discovery": 0}
    for f in files:
        if f.startswith(PRODUCT_PREFIXES):
            counts["product"] += 1
        elif f.startswith(INFRA_PREFIXES):
            counts["infra"] += 1
        elif f.startswith(DISCOVERY_PREFIXES):
            counts["discovery"] += 1
    top = max(counts.values())
    if top == 0:
        return "mixed_or_unknown"
    leaders = [k for k, v in counts.items() if v == top]
    return leaders[0] if len(leaders) == 1 else "mixed_or_unknown"


def _is_staging_directive(files: list) -> bool:
    """A commit whose changed files are ALL under docs/staging/ is a directive/
    policy/registration being STAGED (incl. [ADVISOR-STAGED]). Its subject quotes
    the policy TEXT -- full of words like 'escalation', 'revert', 'two-strike',
    'quota', 'one-way door' -- which is ABOUT those activities, not the machine
    DOING them. Staging/framing a directive is discovery INVESTMENT, so it must be
    settled by the file location, never by keyword-matching the quoted policy."""
    return bool(files) and all(f.startswith("docs/staging/") for f in files)


def classify_commit(commit: Commit) -> tuple[str, str]:
    """Classify one commit into (taxonomy_class, rule_name). Pure -- no git.

    Ordered ruleset (first match wins); each branch names its rule so the
    classification is auditable, and anything unmatched degrades to
    `unattributed` (fail-honest) rather than being forced into productive:

      0. all files under docs/staging/ -> PRODUCTIVE/discovery (staging a directive
           is framing investment; its subject QUOTES policy prose that must not be
           keyword-classified as the waste activity it merely describes)
      1. rework keywords            -> WASTE/rework
      2. hit-limit INTERRUPTION     -> WASTE/hit-limit  (interruption, not building
                                                         limit-handling -> that's a fix)
      3. a landed level bump (-> L) -> PRODUCTIVE/product   (output shipped)
      4. fix-class subject:
           product-domain files     -> PRODUCTIVE/product   (fixed the product)
           else                     -> WASTE/self-repair    (fixed the plumbing)
      5. director-block (director word + block cue) -> WASTE/idle-waiting-on-director
           (checked AFTER fix so a plumbing FIX that merely mentions the director
            is self-repair, not a block; the honest metric source is the register)
      6. discovery keywords         -> PRODUCTIVE/discovery
      7. product keywords           -> PRODUCTIVE/product
      8. else fall back to file domain:
           product                  -> PRODUCTIVE/product
           discovery                -> PRODUCTIVE/discovery
           infra                    -> WASTE/self-repair
           mixed/unknown            -> unattributed
    """
    s = commit.subject
    if _is_staging_directive(commit.files):
        return DISCOVERY, "staging_directive"
    if _REWORK_RE.search(s):
        return REWORK, "rework_keyword"
    if _HIT_LIMIT_RE.search(s):
        return HIT_LIMIT, "hit_limit_keyword"
    if _ARROW_RE.search(s):
        return PRODUCT, "level_transition"
    if _FIX_RE.search(s):
        dom = _domain(commit.files)
        if dom == "product":
            return PRODUCT, "fix_of_product"
        return SELF_REPAIR, "fix_of_plumbing"
    if _DIRECTOR_RE.search(s):
        return IDLE_DIRECTOR, "director_block_keyword"
    if _DISCOVERY_RE.search(s):
        return DISCOVERY, "discovery_keyword"
    if _PRODUCT_RE.search(s):
        return PRODUCT, "product_keyword"
    dom = _domain(commit.files)
    if dom == "product":
        return PRODUCT, "product_file_domain"
    if dom == "discovery":
        return DISCOVERY, "discovery_file_domain"
    if dom == "infra":
        return SELF_REPAIR, "infra_file_domain"
    return UNATTRIBUTED, "no_signal"


# ---------------------------------------------------------------------------
# Time attribution (the UTILISATION denominator)
# ---------------------------------------------------------------------------
def attribute_time(commits: list[Commit]) -> dict:
    """Attribute bounded inter-commit elapsed time to each commit's class.

    Commits are walked oldest->newest. The gap before a commit is billed to
    that commit's class, CAPPED at IDLE_GAP_CAP_SECONDS; any excess is billed to
    WASTE/idle (an overnight pause is idle, not product work). The very first
    commit has no prior anchor and contributes no time (we never guess a start).

    Returns per-class seconds + the totals needed by the metrics. FAIL-HONEST:
    an empty history yields status 'insufficient_data', not a table of zeros."""
    ordered = sorted(commits, key=lambda c: c.timestamp)
    if len(ordered) < 2:
        return {"status": "insufficient_data", "n_commits": len(ordered), "by_class_seconds": {}}

    by_class: dict[str, float] = defaultdict(float)
    for prev, cur in zip(ordered, ordered[1:]):
        gap = cur.timestamp - prev.timestamp
        if gap <= 0:
            continue  # same-second / backdated commit -- no negative/zero time
        cls, _ = classify_commit(cur)
        work = min(gap, IDLE_GAP_CAP_SECONDS)
        idle_excess = gap - work
        if cls == UNATTRIBUTED:
            by_class[UNATTRIBUTED] += work
        else:
            by_class[cls] += work
        if idle_excess > 0:
            by_class[IDLE] += idle_excess

    attributed = sum(v for k, v in by_class.items() if k != UNATTRIBUTED)
    productive = sum(by_class.get(c, 0.0) for c in PRODUCTIVE_CLASSES)
    return {
        "status": "ok",
        "n_commits": len(ordered),
        "idle_gap_cap_seconds": IDLE_GAP_CAP_SECONDS,
        "by_class_seconds": {c: round(by_class.get(c, 0.0), 1) for c in ALL_CLASSES},
        "unattributed_seconds": round(by_class.get(UNATTRIBUTED, 0.0), 1),
        "attributed_seconds": round(attributed, 1),
        "productive_seconds": round(productive, 1),
        "productive_pct": round(100.0 * productive / attributed, 1) if attributed else None,
    }


def classify_commits(commits: list[Commit]) -> dict:
    """Per-class commit COUNTS + rule tallies (the count basis for rework-rate
    and value-per-problem). Separate from time so a caller can see both."""
    by_class: dict[str, int] = defaultdict(int)
    by_rule: dict[str, int] = defaultdict(int)
    for c in commits:
        cls, rule = classify_commit(c)
        by_class[cls] += 1
        by_rule[rule] += 1
    return {
        "n_commits": len(commits),
        "by_class_counts": {c: by_class.get(c, 0) for c in ALL_CLASSES},
        "unattributed_count": by_class.get(UNATTRIBUTED, 0),
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])),
    }


# ---------------------------------------------------------------------------
# Token attribution (the COST denominator)
# ---------------------------------------------------------------------------
_ENTRY_HEADING_RE = re.compile(r"^##\s+(.*)$")
_TOKENS_RE = re.compile(r"\*\*Frontier tokens:\*\*\s*~?([0-9][0-9,]*)")


def parse_token_log(path: Path = TOKEN_LOG) -> list[dict]:
    """Parse token-log.md into [{heading, tokens}] session entries. Each entry
    is a `## ...` heading followed (somewhere before the next heading) by a
    `**Frontier tokens:** <n>` line. An entry whose token figure will not parse
    is skipped from the token numerator but COUNTED as unparsed by the caller --
    never invented as zero."""
    if not path.is_file():
        return []
    entries: list[dict] = []
    cur_heading: Optional[str] = None
    cur_tokens: Optional[int] = None
    have_tokens = False

    def _flush():
        nonlocal cur_heading, cur_tokens, have_tokens
        if cur_heading is not None:
            entries.append({"heading": cur_heading, "tokens": cur_tokens})
        cur_heading, cur_tokens, have_tokens = None, None, False

    for line in path.read_text().splitlines():
        h = _ENTRY_HEADING_RE.match(line)
        if h:
            _flush()
            cur_heading = h.group(1).strip()
            continue
        if cur_heading is not None and not have_tokens:
            m = _TOKENS_RE.search(line)
            if m:
                try:
                    cur_tokens = int(m.group(1).replace(",", ""))
                except ValueError:
                    cur_tokens = None
                have_tokens = True
    _flush()
    # Drop the "How to log" / template preamble headings that never carry a
    # tokens line AND are not session entries (heuristic: keep only headings
    # that look like a dated session -- start with a 4-digit year).
    return [e for e in entries if re.match(r"^\d{4}", e["heading"])]


def classify_token_entry(heading: str) -> tuple[str, str]:
    """Classify a token-log session entry by its heading text into the taxonomy.
    Coarse by nature (a session heading spans several phases) -- so a heading
    with no clear signal is `unattributed`, not guessed. Same ordered
    keyword-signal idea as commits, minus the file-domain refinement (headings
    have no file list)."""
    if _REWORK_RE.search(heading):
        return REWORK, "rework_keyword"
    if _HIT_LIMIT_RE.search(heading):
        return HIT_LIMIT, "hit_limit_keyword"
    if _DIRECTOR_RE.search(heading):
        return IDLE_DIRECTOR, "director_block_keyword"
    if _FIX_RE.search(heading):
        return SELF_REPAIR, "fix_keyword"
    if _DISCOVERY_RE.search(heading):
        return DISCOVERY, "discovery_keyword"
    # Most session headings describe phase/coverage/feature work -> product.
    if _PRODUCT_RE.search(heading) or re.search(
        r"\b(phase|coverage|settlement|model|portfolio|customer|billing|report|"
        r"intelligence|depth|sprint|section)\b",
        heading,
        re.IGNORECASE,
    ):
        return PRODUCT, "product_keyword"
    return UNATTRIBUTED, "no_signal"


def attribute_tokens(entries: list[dict]) -> dict:
    """Attribute each session entry's frontier tokens to its class. Entries with
    an unparsed token figure are counted (`n_unparsed`) but excluded from the
    numerator; classes with no tokens read honestly as 0 while the overall
    `unattributed_tokens` (real tokens we could not confidently place) is
    surfaced separately. FAIL-HONEST: no parseable token data at all ->
    status 'insufficient_data'."""
    by_class: dict[str, int] = defaultdict(int)
    n_parsed = 0
    n_unparsed = 0
    for e in entries:
        tok = e.get("tokens")
        if tok is None:
            n_unparsed += 1
            continue
        n_parsed += 1
        cls, _ = classify_token_entry(e["heading"])
        by_class[cls] += tok

    total = sum(by_class.values())
    if n_parsed == 0:
        return {
            "status": "insufficient_data",
            "n_entries": len(entries),
            "n_parsed": 0,
            "n_unparsed": n_unparsed,
            "by_class_tokens": {},
        }
    attributed = sum(by_class.get(c, 0) for c in ALL_CLASSES)
    productive = sum(by_class.get(c, 0) for c in PRODUCTIVE_CLASSES)
    return {
        "status": "ok",
        "n_entries": len(entries),
        "n_parsed": n_parsed,
        "n_unparsed": n_unparsed,
        "total_tokens": total,
        "by_class_tokens": {c: by_class.get(c, 0) for c in ALL_CLASSES},
        "unattributed_tokens": by_class.get(UNATTRIBUTED, 0),
        "attributed_tokens": attributed,
        "productive_tokens": productive,
        "productive_pct": round(100.0 * productive / attributed, 1) if attributed else None,
    }


# ---------------------------------------------------------------------------
# Idle-waiting-on-director (from the real escalation register)
# ---------------------------------------------------------------------------
def director_idle(path: Path = ACTION_NEEDED, now: Optional[int] = None) -> dict:
    """OPEN (`resolved: false`) director-gated items from the real
    action_needed_register.json -- the honest, direct signal for
    idle-waiting-on-director (a generic git-time idle gap cannot tell a
    director-block apart from a coffee break; this register can). Reports the
    open count + oldest-open age. FAIL-HONEST: a missing/unreadable register is
    status 'no_register', never a silent zero."""
    if not path.is_file():
        return {"status": "no_register", "open_count": None, "items": []}
    try:
        reg = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {"status": "unreadable", "open_count": None, "items": []}
    if not isinstance(reg, dict):
        return {"status": "unreadable", "open_count": None, "items": []}

    now = now if now is not None else int(datetime.now(timezone.utc).timestamp())
    open_items = []
    for key, item in reg.items():
        if not isinstance(item, dict) or item.get("resolved") is True:
            continue
        first = item.get("first_asked_at")
        age_h = None
        if isinstance(first, str):
            try:
                ts = datetime.fromisoformat(first)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                age_h = round((now - ts.timestamp()) / 3600.0, 1)
            except ValueError:
                age_h = None
        open_items.append({
            "item_id": item.get("item_id", key),
            "what": item.get("what", ""),
            "first_asked_at": first,
            "age_hours": age_h,
        })
    open_items.sort(key=lambda i: -(i["age_hours"] or 0))
    ages = [i["age_hours"] for i in open_items if i["age_hours"] is not None]
    return {
        "status": "ok",
        "open_count": len(open_items),
        "oldest_open_hours": max(ages) if ages else None,
        "items": open_items,
    }


# ---------------------------------------------------------------------------
# The five headline metrics
# ---------------------------------------------------------------------------
def self_maintenance_trend(commits: list[Commit], windows=(30, 14, 7)) -> dict:
    """Cost-of-self-maintenance made TRENDABLE: WASTE/self-repair share of
    attributed WORK-time within each trailing window (git commit clock). The
    design requires this be trendable DOWN (or the harness is a treadmill) --
    so it is reported per window, newest windows last, never as one static
    number. DIAGNOSTIC only."""
    ordered = sorted(commits, key=lambda c: c.timestamp)
    if len(ordered) < 2:
        return {"status": "insufficient_data", "windows": []}
    now = ordered[-1].timestamp
    out = []
    for days in sorted(windows, reverse=True):
        cutoff = now - days * 86400
        window_commits = [c for c in ordered if c.timestamp >= cutoff]
        t = attribute_time(window_commits)
        if t.get("status") != "ok" or not t["attributed_seconds"]:
            out.append({"window_days": days, "status": "insufficient_data"})
            continue
        sr = t["by_class_seconds"].get(SELF_REPAIR, 0.0)
        out.append({
            "window_days": days,
            "status": "ok",
            "self_repair_pct_of_time": round(100.0 * sr / t["attributed_seconds"], 1),
            "self_repair_hours": round(sr / 3600.0, 1),
            "attributed_hours": round(t["attributed_seconds"] / 3600.0, 1),
        })
    return {"status": "ok", "windows": out}


def compute_metrics(time_attr: dict, count_attr: dict, token_attr: dict,
                    director: dict, trend: dict) -> dict:
    """The five headline metrics, each fail-honest. Every one is a DIAGNOSTIC
    (see GUARDRAIL) -- none is a target or a gate."""
    # 1. productive-% -- BOTH denominators, and their divergence (the signal).
    t_pct = time_attr.get("productive_pct")
    c_pct = token_attr.get("productive_pct")
    divergence = round(t_pct - c_pct, 1) if (t_pct is not None and c_pct is not None) else None
    productive_pct = {
        "time_pct": t_pct,
        "cost_pct": c_pct,
        "time_minus_cost_divergence_pp": divergence,
        "note": ("time = utilisation denominator (git clock); cost = token "
                 "denominator (token log). They are tracked separately because "
                 "they diverge -- the divergence is the signal, not an error."),
    }

    # 2. cost-of-self-maintenance -- share now + the trend (must be able to fall).
    sr_time = time_attr.get("by_class_seconds", {}).get(SELF_REPAIR)
    attributed = time_attr.get("attributed_seconds") or 0
    self_maint = {
        "self_repair_pct_of_time": (
            round(100.0 * sr_time / attributed, 1) if (sr_time is not None and attributed) else None
        ),
        "self_repair_pct_of_tokens": (
            round(100.0 * token_attr["by_class_tokens"].get(SELF_REPAIR, 0)
                  / token_attr["attributed_tokens"], 1)
            if token_attr.get("status") == "ok" and token_attr.get("attributed_tokens") else None
        ),
        "trend": trend,
        "note": "Must be trendable DOWN over windows, or the harness is a treadmill.",
    }

    # 3. rework-rate -- rework commits / classified (non-unattributed) commits.
    counts = count_attr.get("by_class_counts", {})
    classified = sum(counts.get(c, 0) for c in ALL_CLASSES)
    rework_rate = {
        "rework_commits": counts.get(REWORK, 0),
        "classified_commits": classified,
        "rework_pct": round(100.0 * counts.get(REWORK, 0) / classified, 2) if classified else None,
    }

    # 4. value-per-problem -- productive commits per problem commit (self-repair,
    #    rework, hit-limit). How much product you get per problem you deal with.
    productive_commits = sum(counts.get(c, 0) for c in PRODUCTIVE_CLASSES)
    problem_commits = sum(counts.get(c, 0) for c in PROBLEM_CLASSES)
    value_per_problem = {
        "productive_commits": productive_commits,
        "problem_commits": problem_commits,
        "ratio": round(productive_commits / problem_commits, 2) if problem_commits else None,
        "note": ("productive commits per PROBLEM commit (self-repair + rework + "
                 "hit-limit). No problems in-window -> ratio null, not infinity."),
    }

    # 5. idle-on-director -- straight from the escalation register.
    idle_on_director = {
        "status": director.get("status"),
        "open_count": director.get("open_count"),
        "oldest_open_hours": director.get("oldest_open_hours"),
    }

    return {
        "productive_pct": productive_pct,
        "cost_of_self_maintenance": self_maint,
        "rework_rate": rework_rate,
        "value_per_problem": value_per_problem,
        "idle_on_director": idle_on_director,
    }


# ---------------------------------------------------------------------------
# Top-level report
# ---------------------------------------------------------------------------
def build_report(repo_root: Path = PROJECT, *, token_log: Path = TOKEN_LOG,
                 action_needed: Path = ACTION_NEEDED) -> dict:
    commits = git_log_commits(repo_root)
    time_attr = attribute_time(commits)
    count_attr = classify_commits(commits)
    token_entries = parse_token_log(token_log)
    token_attr = attribute_tokens(token_entries)
    director = director_idle(action_needed)
    trend = self_maintenance_trend(commits)
    metrics = compute_metrics(time_attr, count_attr, token_attr, director, trend)

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_from": (
            "git log (commit subjects + changed files) + "
            "docs/observability/token-log.md + action_needed_register.json"
        ),
        "framing": FRAMING,
        "guardrail": GUARDRAIL,
        "time_attribution": time_attr,
        "commit_classification": count_attr,
        "token_attribution": token_attr,
        "director_idle": director,
        "metrics": metrics,
        "taxonomy": list(ALL_CLASSES),
    }


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the full report as JSON")
    args = parser.parse_args(argv)

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    m = report["metrics"]
    print("Activity-based cost + utilisation (G11) -- DIAGNOSTIC, never a target")
    print(f"  {report['guardrail']}")
    ta = report["time_attribution"]
    print(f"  commits classified: {report['commit_classification']['n_commits']}, "
          f"time status: {ta.get('status')}")
    pp = m["productive_pct"]
    print(f"  productive-% : time={pp['time_pct']}  cost={pp['cost_pct']}  "
          f"divergence={pp['time_minus_cost_divergence_pp']}pp")
    sm = m["cost_of_self_maintenance"]
    print(f"  self-maintenance: {sm['self_repair_pct_of_time']}% of time "
          f"(tokens {sm['self_repair_pct_of_tokens']}%)")
    for w in sm["trend"].get("windows", []):
        if w.get("status") == "ok":
            print(f"    last {w['window_days']}d: {w['self_repair_pct_of_time']}% self-repair")
    print(f"  rework-rate: {m['rework_rate']['rework_pct']}% "
          f"({m['rework_rate']['rework_commits']} commits)")
    print(f"  value-per-problem: {m['value_per_problem']['ratio']} "
          f"(productive/problem commits)")
    idl = m["idle_on_director"]
    print(f"  idle-on-director: {idl['open_count']} open, "
          f"oldest {idl['oldest_open_hours']}h")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
