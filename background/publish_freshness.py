"""HOW LONG SINCE THE FIGURES MOVED — the one number that tells a frozen site from a live one.

DIRECTOR, 2026-08-13: *"content hasn't moved in ~17 hours while heartbeats keep landing — the
liveness signal is masking a content freeze ... alive-but-unchanged and alive-and-publishing must
not look the same to me or to the site."*

THE DEFECT THIS NAMES
---------------------
`site/data/tick_heartbeat.json` answers "is the tick running?" and answered it correctly for
eighteen hours: `verdict: drew` every sixty seconds, published to origin every thirty minutes by
`_refresh_published_liveness_on_skip`. Every daemon was healthy. Nothing was red. And the site
served 2026-08-12 figures the whole time, because every content commit was dying on the
pre-commit hook deadline.

Fault #1 (2026-07-25) correctly DECOUPLED the liveness signal from content-change, so a healthy
machine with unchanged output could still prove it was alive. What it did not do -- and what this
module adds -- is give that signal anything to say about CONTENT. A heartbeat that reports only
its own pulse is not a false statement; it is a true statement about the wrong subject, and a
true statement about the wrong subject is how eighteen hours pass unnoticed.

So the liveness surface now carries the statement of how stale everything else is. That is the
same shape as `publish_provenance.py` -- "publishes the one thing that must never freeze: the
statement of how frozen everything else is" -- applied to the surface that never stopped
publishing rather than to the one that did.

TWO CLOCKS, AND THEY ARE ALLOWED TO DISAGREE
--------------------------------------------
  published_age_seconds  since the PUBLISH PATH last got content to origin. Stamped by
                         `record_published()`, which is reachable from exactly one place: after
                         `_push_reached_origin` returned True on a content commit. Ground-truth-
                         gated the same way the push throttle is -- a phantom "up to date" never
                         advances it.
  committed_age_seconds  since content was last COMMITTED at all, asked of git rather than of our
                         own bookkeeping -- by ANY writer, not only the publisher.

They are deliberately not one field. Equal-and-small is healthy. Equal-and-large is a real
content freeze. `committed` small while `published` large is the case measured on 2026-08-13:
the publish path had not landed for 21.7 hours, and `site/data/dashboard.json` still reached
origin twice in that window -- once at 02:12 and once at 18:55 -- because an unrelated worker
commit happened to sweep the regenerated file along with it. Content moving by luck is not a
publishing pipeline, and a single blended number would have read those two accidents as health.

FAIL-SILENT IS THE FAILURE MODE HERE (R15), so an unavailable answer is None and NEVER 0. A
freshness module that reports "0 seconds since publish" when it cannot find its own state file
would manufacture exactly the false all-clear it exists to end. Every caller must treat None as
UNKNOWN and never as fresh -- `is_publishing_down` does, by returning False only on a positive
measurement and escalating an unknown to its own named state.

REUSE: background/publish_freshness.py
CLASS: CUSTOM
INDEX: searched "freshness", "staleness", "publish age". `publish_provenance.py` is the closest
       and is a different subject: it records whether the newest run was VERIFIED (gate green)
       and what the visitor is being shown, and it is written BEFORE the commit so it travels
       with it. It therefore said "Verified 2026-08-13T16:34:33Z" over content from the previous
       day -- correctly, by its own contract, because the gate WAS green; the commit is what
       died. This module asks the question that stayed unasked: did the bytes reach origin.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".last_content_publish.json"

#: The paths whose movement IS a content publish. Deliberately a short list of the surfaces a
#: visitor actually reads, not the full commit pathspec: adding every generated file would make
#: the age advance on any regeneration, and the question is whether the FIGURES moved.
CONTENT_PATHS = (
    "site/data/dashboard.json",
    "docs/status/LATEST.md",
    "docs/reports/ANNUAL_REPORT.md",
)

#: How stale a published content surface may get before it is a fault rather than a quiet spell.
#: The sim runs every ~6 minutes and the push throttle is 30, so a healthy at-rest cycle
#: republishes well inside this. Set at 3h: comfortably above any legitimate quiet spell
#: (including a long red-gate pause, which has its OWN banner and is not this alarm's subject),
#: and far below the eighteen hours it took a director to notice by eye.
STALE_AFTER_SECONDS = 3 * 60 * 60


def record_published(now: float | None = None) -> None:
    """Stamp a VERIFIED content publish. The only writer.

    Reachable from exactly one call site -- `git_commit_push`, immediately after
    `_push_reached_origin` confirmed via ls-remote that origin advanced to this HEAD. Never call
    it from a path that has not checked that: a stamp written on an unverified push would make
    this module agree with the very bookkeeping it exists to be independent of.
    """
    ts = time.time() if now is None else float(now)
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"ts": ts}))
    except OSError:
        pass  # never take a successful publish down over its own bookkeeping


def last_published_ts() -> float | None:
    """When content last reached origin, or None if never recorded / unreadable (= UNKNOWN)."""
    try:
        return float(json.loads(STATE_FILE.read_text())["ts"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def last_committed_ts(*, _run=None) -> float | None:
    """When content was last COMMITTED locally, asked of git. None if git cannot answer.

    Independent of this module's own state file on purpose -- it is the cross-check that catches
    a publish committing locally and never reaching origin, which is a different fault with a
    different fix and used to be invisible from the outside.
    """
    run = _run or subprocess.run
    try:
        r = run(["git", "log", "-1", "--format=%ct", "--"] + list(CONTENT_PATHS),
                cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=15)
    except Exception:  # noqa: BLE001 -- an unavailable check is UNKNOWN, never fresh
        return None
    if getattr(r, "returncode", 1) != 0:
        return None
    out = (r.stdout or "").strip().splitlines()
    try:
        return float(out[0]) if out else None
    except ValueError:
        return None


def _age(ts: float | None, now: float) -> float | None:
    return None if ts is None else max(0.0, now - ts)


def snapshot(now: float | None = None, *, _run=None) -> dict:
    """The publish-freshness block the heartbeat carries and the site renders.

    `state` is the reader's whole answer, so no consumer has to re-derive the comparison and
    two consumers cannot reach different verdicts from the same numbers:
        publishing   content reached origin within STALE_AFTER_SECONDS
        stale        it did not -- the freeze this exists to surface
        unpublished  no verified publish has EVER been recorded (a fresh install, or a state
                     file that was lost) -- reported as its own state rather than folded into
                     `stale`, because "we have no record" and "we have a record and it is old"
                     are answered differently
        unknown      the age could not be measured at all -- explicitly NOT `publishing`
    """
    now = time.time() if now is None else float(now)
    pub_ts, com_ts = last_published_ts(), last_committed_ts(_run=_run)
    pub_age, com_age = _age(pub_ts, now), _age(com_ts, now)

    if pub_age is None:
        state = "unpublished" if not STATE_FILE.exists() else "unknown"
    elif pub_age <= STALE_AFTER_SECONDS:
        state = "publishing"
    else:
        state = "stale"

    return {
        "state": state,
        "published_age_seconds": None if pub_age is None else round(pub_age, 1),
        "committed_age_seconds": None if com_age is None else round(com_age, 1),
        "stale_after_seconds": STALE_AFTER_SECONDS,
        # The disagreement, named rather than left for a reader to spot: content is being
        # COMMITTED while the publish path is not landing it. Its own fault and its own fix --
        # either the push is not reaching origin, or (2026-08-13) the publisher's commit is dying
        # and the figures only travel when another writer happens to sweep them along.
        "committed_but_unpublished": bool(
            pub_age is not None and com_age is not None and pub_age - com_age > STALE_AFTER_SECONDS
        ),
    }


def is_publishing_down(snap: dict | None = None) -> bool:
    """Is content publishing FAILING right now?

    True only on a positive measurement of staleness. An `unknown` age is not silently treated as
    healthy -- it is not this predicate's subject, and the caller pages on it separately -- but it
    is likewise never reported as down, because a missing measurement is not evidence of a fault.
    """
    snap = snapshot() if snap is None else snap
    return snap.get("state") in ("stale", "unpublished")


def describe(snap: dict | None = None) -> str:
    """One human line for a page, a banner or a log. Never says "fresh" without a number."""
    snap = snapshot() if snap is None else snap
    state, age = snap.get("state"), snap.get("published_age_seconds")
    if state == "unpublished":
        return "content publishing: NO verified publish on record"
    if state == "unknown":
        return "content publishing: age UNKNOWN (freshness could not be measured)"
    hours = (age or 0) / 3600.0
    if state == "stale":
        extra = " (content is still being committed -- the PUBLISH PATH is what stopped)" \
            if snap.get("committed_but_unpublished") else ""
        return f"content publishing: DOWN -- last published {hours:.1f}h ago{extra}"
    return f"content publishing: live -- last reached origin {hours:.1f}h ago"
