#!/usr/bin/env python3
"""Generate site/data/method.json -- the Method section's data source.

NAV_STORY_PLATFORM_METHOD.md item 6 (The Way): the harness itself framed as
a transferable, licensable method -- operating model, the R1-R6 rules with
the real incidents that forged them, a live view of the staging loop
actually working, and the retrospective library. Per the same discipline as
tools/generate_platform_data.py: the staging-loop and retro-library sections
are computed fresh from the filesystem at generation time; only the rule
descriptions and incident summaries are static prose.
"""
import json
from datetime import datetime, timezone
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
SCORECARD_PATH = PROJECT / "site" / "state" / "track_record_scorecard.json"
STAGING_DIR = PROJECT / "docs" / "staging"
STAGING_DONE_DIR = STAGING_DIR / "done"
STAGING_DRAFTS_DIR = STAGING_DIR / "drafts"
RETRO_DIR = PROJECT / "docs" / "retrospectives"
OUT_PATH = PROJECT / "site" / "data" / "method.json"

RECENT_DONE_LIMIT = 12


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


OPERATING_MODEL = dict(
    roles=[
        dict(name="Rich (MD / board)", description="Stages direction in docs/staging/; reviews outcomes. Does not write code. Staging a document IS the approval signal for pre-approved (Tier 2) queue items."),
        dict(name="Claude Code (orchestrator)", description="Designs, delegates, reviews, and manages the build. Classifies every proposal into a tier before acting on it."),
        dict(name="qwen3:14b / Ollama (local GPU)", description="Mechanical code generation and execution. Frontier (Claude) tokens are reserved for reasoning, not typing code."),
        dict(name="Risk committee (local Ollama only)", description="Makes simulated business decisions inside the sim/company boundary. No frontier API spend in simulation runs -- keeps the epistemic wall and the cost model both honest."),
    ],
    tiers=[
        dict(tier="Tier 1", name="One-way doors", description="Architecture changes expensive to reverse, epistemic-wall changes, safety-control modifications, anything external-facing or spending-related. Hard block: explicit in-conversation approval required, no timeout, never proceeds on silence."),
        dict(tier="Tier 2", name="Pre-approved queue", description="Items already named in PRIORITIES.md, or an actioned staged instruction. Proceeds immediately on reaching the front of the queue -- staging/priorities approval already happened, so there is no separate opt-out window."),
        dict(tier="Tier 3", name="Novel self-generated proposals", description="Anything not already in PRIORITIES.md and not staged. Keeps a 4-hour opt-out window so the human principal's veto carries real information value instead of being a rubber stamp."),
    ],
)


RULES = [
    dict(
        id="R1", name="Consumer-verified completion",
        description="An artifact with an external consumer is done only when that consumer's fetch confirms it -- quote the fetched evidence, not the producer's own view of it.",
        incident="Forged by a cluster of false \'fixed\' claims (2026-06-30 to 07-04): PROJECT_STATE.txt read stale to the advisor's fetch while it was fresh in the local working copy at the very same commit -- the producer and the consumer were looking at genuinely different things, and self-certification from the producer side could not have caught it.",
    ),
    dict(
        id="R2", name="Long-running processes",
        description="A code fix is deployed only once the running process has been restarted with it. Committed does not mean running.",
        incident="Forged by the same verification week: the session watchdog was claimed fixed twice while the tmux pane it managed still showed a bare shell, because the fix had landed in the script but the already-running process was never restarted with the new code.",
    ),
    dict(
        id="R3", name="Two-strike redesign",
        description="A second false completion claim on the same component means eliminate or redesign the mechanism, not patch it again.",
        incident="Forged when the watchdog's tmux send-keys relaunch failed three distinct ways in succession (a launch-timing race, an nvm PATH issue, and an apostrophe silently swallowing every following line via PS2 continuation). The fix that actually worked was eliminating send-keys entirely -- launching claude directly as the pane's own command -- not a third patch on top of the second.",
    ),
    dict(
        id="R4", name="Diagnosis discipline",
        description="Before fixing a stuck problem, name the nearest working analogue and state the diff; if none exists, build the smallest closed-loop test first.",
        incident="Forged by every real breakthrough that week coming from a contrast pair rather than a first-principles theory: LATEST.md fresh vs. PROJECT_STATE.txt stale at the same commit through the same pipeline, and an interactive shell vs. a login shell for PATH resolution.",
    ),
    dict(
        id="R5", name="Alerting",
        description="Notifications fire on state transitions only, carry the diagnostic payload, and never repeat an unchanged status.",
        incident="Forged by the watchdog's own launch-failure alert: an early version just said \'launch failed\', which told the human nothing he could act on. The fix carries the last N captured pane lines in the NTFY itself, because an alert that doesn't change what the human knows shouldn't exist.",
    ),
    dict(
        id="R6", name="Board/report sections are never the primary work of a phase",
        description="Reporting is a byproduct of building capability, not the capability itself. A new dashboard/report/Observatory section alone never counts as a phase.",
        incident="Forged when an instruction to close four real priorities (P1-P4) was satisfied, in name only, by writing four board report sections instead of building the capability each priority actually named -- labels got honoured, substance got swapped.",
    ),
]

METHOD_FRAMING = (
    "This is not just how one energy-supplier simulation got built -- it is a working answer to "
    "how do you grow a company with an autonomous agent and not lose control of it. The tiered "
    "approval model, the staging bridge, verify-by-fetch, the two-strike redesign rule, and the "
    "retro practice below are all domain-agnostic: none of them mention electricity, gas, or "
    "customers. The only energy-specific layer is the SIM/company epistemic wall itself. Everything "
    "in this section is the transferable, licensable part of the product."
)


def _staging_pending():
    if not STAGING_DIR.is_dir():
        return []
    items = []
    for p in sorted(STAGING_DIR.glob("*.md")):
        try:
            stat = p.stat()
        except OSError:
            continue
        items.append(dict(
            filename=p.name,
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            size_bytes=stat.st_size,
        ))
    return items


def _staging_done_recent(limit=RECENT_DONE_LIMIT):
    if not STAGING_DONE_DIR.is_dir():
        return [], 0
    entries = []
    for p in STAGING_DONE_DIR.glob("*.md"):
        try:
            stat = p.stat()
        except OSError:
            continue
        entries.append((stat.st_mtime, p.name, stat.st_size))
    entries.sort(key=lambda t: -t[0])
    total = len(entries)
    recent = [
        dict(
            filename=name,
            modified_at=datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            size_bytes=size,
        )
        for mtime, name, size in entries[:limit]
    ]
    return recent, total


def _staging_drafts_count():
    if not STAGING_DRAFTS_DIR.is_dir():
        return 0
    return len(list(STAGING_DRAFTS_DIR.glob("*.md")))


def _retro_library():
    if not RETRO_DIR.is_dir():
        return []
    entries = []
    for p in sorted(RETRO_DIR.glob("*.md")):
        try:
            stat = p.stat()
        except OSError:
            continue
        name = p.stem
        date = name[:10] if len(name) >= 10 and name[4] == "-" and name[7] == "-" else None
        title = name[11:].replace("-", " ").title() if date else name.replace("-", " ").title()
        lines = p.read_text(errors="replace").splitlines()
        heading = next((l.lstrip("# ").strip() for l in lines if l.startswith("#")), title)
        entries.append(dict(
            filename=p.name, date=date, title=heading, size_bytes=stat.st_size,
            path="https://21bcarlisle-arch.github.io/synthetic-enterprise/retrospectives/" + p.name,
        ))
    return entries


def _track_record():
    """S1 Option B (docs/staging/S1_SHADOW_LIVE_TRACK_RECORD_DESIGN.md), Decision 2:
    the predicted-vs-realised scorecard is public from day one, misses included --
    folded onto the Method page verbatim rather than summarised, so a zero-graded
    early state reads as honest, not hidden."""
    try:
        return json.loads(SCORECARD_PATH.read_text())
    except Exception:
        return None


def generate():
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    recent_done, done_total = _staging_done_recent()
    pending = _staging_pending()

    data = dict(
        generated_at=_get(dashboard, "meta", "generated_at"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        phase=_get(dashboard, "build", "current_phase"),
        test_count=_get(dashboard, "build", "test_count"),
        operating_model=OPERATING_MODEL,
        rules=RULES,
        method_framing=METHOD_FRAMING,
        staging_loop=dict(
            pending_count=len(pending),
            pending=pending,
            done_total=done_total,
            recent_done=recent_done,
            drafts_count=_staging_drafts_count(),
        ),
        retro_library=_retro_library(),
        track_record=_track_record(),
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return True


if __name__ == "__main__":
    generate()
