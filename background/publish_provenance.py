"""BEHIND, NEVER FROZEN, NEVER SILENT — the published provenance/staleness banner.

DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10, properties 1 and 3, sequenced to the front by
DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10.

Verbatim: *"If even the scoped gate is red, the site keeps serving the last verified snapshot
under a dated banner ('verification paused since T; showing run R'). A visitor can always tell
WHAT they are seeing and HOW current it is. Freshness claims are provenance claims; fake-fresh
(re-stamping stale runs) remains the cardinal sin."*

THE DEFECT THIS NAMES
---------------------
When the gate reds, the publisher returns before `git_commit_push`, so the live site keeps
serving the last pushed snapshot. That half was always right — last-known-good is the correct
thing to serve. What was missing is that the site said NOTHING about it. The published stamp
read 2026-08-09T12:41:51Z for 25 hours, and from outside, a site frozen because verification
is paused is indistinguishable from a site frozen because the machine is dead, or from a site
that is simply current. Silence is the defect, not the staleness.

So this module publishes the one thing that must never freeze: the statement of how frozen
everything else is.

TWO STATES, AND WHAT MAY MOVE IN EACH
-------------------------------------
  VERIFIED — a publish completed with the scoped gate green. `last_verified` and `showing_run`
             advance to that run. `paused_since` clears.
  PAUSED   — the scoped gate is red. `last_verified` and `showing_run` MUST NOT MOVE (they
             describe a run that is still the newest verified one, and it is still what the
             visitor is looking at). `paused_since` is stamped ONCE, at the transition.

THE CARDINAL SIN, MECHANISED (R15)
----------------------------------
"Fake-fresh" is not prevented here by intent or by convention — it is prevented by the two
recorders having disjoint write sets, and by tests that mutate each one and assert the other's
fields are byte-identical (`tests/background/test_publish_provenance.py`):

  * `record_verified()` is the ONLY writer of `last_verified` / `showing_run`, and it is
    reachable only from a completed publish. No caller can advance freshness without one.
  * `record_paused()` cannot touch either. Called a hundred times, the served run's stamp does
    not move by a byte — which is the property the four-times-republished figure violated.
  * `paused_since` is stamped at the TRANSITION only. Re-stamping it every cycle would be the
    same sin wearing the opposite coat: a banner reading "paused since 30 seconds ago" for 25
    hours is a fresh-looking lie about staleness. A test asserts it survives repeated calls.

WHY IT IS ITS OWN FILE, AND ITS OWN PUSH
----------------------------------------
`site/data/publish_provenance.json` is deliberately NOT a key inside `dashboard.json`. The
banner has to reach origin on exactly the cycles the dashboard MUST NOT — the whole point is
that the numbers stay put while the statement about them updates. Sharing a file would make
publishing the banner mean publishing the unverified numbers with it. The publisher therefore
commits this path alone on a red cycle (see
`process_run_complete._publish_provenance_banner`), the same narrow-pathspec shape as the
liveness heartbeat refresh.

REUSE: background/publish_provenance.py
CLASS: CUSTOM
INDEX: searched "provenance", "freshness", "staleness banner" -- 22 rows mention provenance
       and none covers this. `tools.map_assertion_provenance` (AO11) is the closest name and
       a different subject entirely: when a MATURITY-MAP CELL was asserted, internal, never
       rendered to a visitor. The published-surface half is `site/data/dashboard.json`'s
       `meta` block, which records when a snapshot was GENERATED and has no concept of
       whether it was VERIFIED or of a pause -- and it is precisely the file this one must
       not share, because the banner has to publish on the cycles the dashboard must not.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROVENANCE_FILE = PROJECT_DIR / "site" / "data" / "publish_provenance.json"

SCHEMA_VERSION = 1
STATE_VERIFIED = "verified"
STATE_PAUSED = "paused"

# Bounded: the banner is a page, not a directory listing (same reasoning as
# PUBLISH_GATE_MAX_CITED_FINDINGS).
MAX_ANNOTATED_REDS = 8


def _now_iso(now=None) -> str:
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _blank() -> dict:
    return {
        "schema": SCHEMA_VERSION,
        "verification_state": STATE_PAUSED,
        "showing_run": None,
        "last_verified": None,
        "paused_since": None,
        "annotation": {"open_findings": 0, "nonblocking_reds": [], "checked_at": None},
        "written_at": None,
    }


def read(path: Path = None) -> dict:
    """Current provenance. A missing or corrupt file reads as PAUSED with nothing verified.

    FAIL-CLOSED on purpose: the honest reading of "I cannot tell you what was verified" is
    "nothing is verified", never "everything is fine". A corrupt file that read as VERIFIED
    would publish a fresh-looking banner over an unknown state — the cardinal sin by accident.
    """
    path = path or PROVENANCE_FILE
    try:
        loaded = json.loads(path.read_text())
    except (OSError, ValueError):
        return _blank()
    if not isinstance(loaded, dict):
        return _blank()
    base = _blank()
    base.update(loaded)
    return base


def _write(state: dict, path: Path = None, now=None) -> dict:
    path = path or PROVENANCE_FILE
    state["schema"] = SCHEMA_VERSION
    state["written_at"] = _now_iso(now)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    return state


def record_verified(*, run_id, git_commit, generated_at=None, path: Path = None, now=None) -> dict:
    """A publish completed with the scoped gate GREEN. The ONLY freshness advance there is."""
    state = read(path)
    stamp = {
        "run_id": run_id,
        "git_commit": git_commit,
        "generated_at": generated_at or _now_iso(now),
        "verified_at": _now_iso(now),
    }
    state["verification_state"] = STATE_VERIFIED
    state["showing_run"] = stamp
    state["last_verified"] = stamp
    state["paused_since"] = None
    return _write(state, path, now)


def record_paused(*, reason=None, path: Path = None, now=None) -> dict:
    """The scoped gate is RED. Stamps the pause once; moves no freshness field, ever.

    Returns the written state. `paused_since` is preserved across repeated calls — see the
    module docstring on why re-stamping it is the same sin in the opposite direction.
    """
    state = read(path)
    state["verification_state"] = STATE_PAUSED
    if not state.get("paused_since"):
        state["paused_since"] = _now_iso(now)
    if reason:
        state["paused_reason"] = str(reason)[:400]
    # showing_run / last_verified deliberately untouched: what the visitor is looking at has
    # not changed, and saying it has would be the fake-fresh sin.
    return _write(state, path, now)


def record_annotation(*, open_findings=None, nonblocking_reds=None, path: Path = None,
                      now=None) -> dict:
    """The honest repo-health line: "published with N open findings — see health".

    Separate from the two state recorders because it is a different KIND of claim: those say
    how current the numbers are, this says what is known to be wrong elsewhere while they are
    published. It never touches `verification_state` — an annotation must not be able to
    pause or unpause the site, or a noisy finding count would become an outage.
    """
    state = read(path)
    annotation = dict(state.get("annotation") or {})
    if open_findings is not None:
        annotation["open_findings"] = int(open_findings)
    if nonblocking_reds is not None:
        reds = [str(r) for r in nonblocking_reds]
        annotation["nonblocking_reds"] = reds[:MAX_ANNOTATED_REDS]
        annotation["nonblocking_reds_total"] = len(reds)
    annotation["checked_at"] = _now_iso(now)
    state["annotation"] = annotation
    return _write(state, path, now)


def banner_line(state=None, now=None) -> str:
    """The sentence a visitor reads. Rendered client-side too (site/assets/freshness-banner.js);
    this is the same sentence in Python so the publisher can log exactly what the site says and
    a test can assert the two agree rather than drifting apart."""
    state = read() if state is None else state
    showing = state.get("showing_run") or {}
    run = showing.get("run_id") or "unknown"
    if state.get("verification_state") == STATE_VERIFIED:
        return "Verified {} · showing run {}".format(
            showing.get("verified_at") or "unknown", run)
    since = state.get("paused_since") or "unknown"
    return "Verification paused since {} · showing run {} (last verified {})".format(
        since, run, (state.get("last_verified") or {}).get("verified_at") or "never")
