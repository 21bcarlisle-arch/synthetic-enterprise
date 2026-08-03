"""Stall-class register — the ONE enumeration of what counts as a STALL-class
event, plus the detectors this atom (HX2_stall_set_coverage_verdict) adds for the
four events the director named that had none.

PURPOSE (stated first, per DON'T ACCRETE / OPERATIONAL_LAYER_DESIGN)
    The ratified harness exit criterion (DIRECTOR_RULING_HARNESS_EXIT_CRITERION_
    RATIFIED_2026-07-27) is "three consecutive product-content advances across a span
    in which the STALL-class intervention count is ZERO". That criterion is only as
    good as the SET of things called a stall. The proposal it ratified listed five
    classes and asserted "each has an existing detector"; the director returned four
    events that actually happened and asked whether they were covered. Three of them
    were not, and two of the proposal's own five classes had no detector either.

    This module is the single place that set lives, so HX1 (the counter) cannot
    silently miss a class, and so the answer to "what resets the counter?" is one
    readable list rather than an inference over five daemons.

GUARANTEES (what this gives, honestly scoped)
    G1 ONE ENUMERATION. `STALL_CLASSES` is the whole set. A class with no detector is
       listed with `detector=None` and reported as UNCOVERED — never omitted. An
       omitted class is invisible; an uncovered class is a named hole (FAIL-SILENT).
    G2 NAMED DETECTORS MUST RESOLVE. `resolve_detectors()` raises if a class names a
       detector that no longer imports. A renamed/deleted detector therefore fails
       loudly instead of degrading to "no stalls detected" (FAIL-SILENT).
    G3 NO NEW STATE. Every detector here is a pure function of PRIMARY STATE — git
       history and the publish-gate state file `process_run_complete` already writes.
       Nothing here writes a register, a flag or a counter. This is the coherence
       requirement of the ruling §4 (LAW C: computed from primary state, never from
       the tick's own enumeration) and it also means there is no new real-disk flag
       to leak into unpinned test loaders.
    G4 UNAVAILABLE IS NOT CLEAN. Every detector returns an `unavailable=True` event
       when its input cannot be read (git unreadable, origin unreachable, malformed
       state). An unavailable check is a FAILED check (R15), never a quiet pass.
    G5 CONSERVATIVE DIRECTION. Where this module is uncertain it counts a stall
       rather than not. A false stall only DELAYS harness investment (the counter is
       a gate on one decision, R12); a false clean span would grant it unearned.
       Nothing here gates publishing, so a false positive cannot wedge the pipeline.

WHY THESE THREE DETECTORS AND NOT MORE
    E2 (publish-gate wedge >1h) already had a detector at exactly the director's
    threshold — `supervisor._publish_gate_wedge_active`, MIN_AGE 3600s. It is ADAPTED
    here, not rebuilt. E1/E3/E4 had none and are built here. Full verdicts with
    evidence: `docs/design/HX2_STALL_SET_COVERAGE_VERDICT.md`.

R12: nothing computed here is a fidelity, maturity or product-quality measure. It
gates one decision — may harness investment resume — and must not appear in any
quality claim.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ── Dials (informative thresholds, never targets — R12) ──────────────────────────
# The director named ">30 min" for an origin freeze. 30 min is also exactly
# process_run_complete.PUSH_THROTTLE_SECONDS, so a freeze reaching this bar means at
# least one whole push cycle produced no advance — the phantom-push signature.
ORIGIN_FREEZE_THRESHOLD_SECONDS = 30 * 60

# How long after a director/advisor input meaningful work must resume for that input
# to be read as the thing that RESTARTED the work (rather than a coincidence).
RESCUE_ATTRIBUTION_WINDOW_SECONDS = 60 * 60


class StallRegistryError(RuntimeError):
    """A class in STALL_CLASSES names a detector that does not resolve. G2: this is a
    LOUD failure, never a degradation to 'no stalls found'."""


@dataclass(frozen=True)
class StallEvent:
    """One stall-class occurrence. `unavailable` marks a check that could not run —
    G4: the caller must treat it as NOT-CLEAN, never as absence of a stall."""

    class_id: str
    at: float | None
    detail: str
    channel: str = "n/a"
    unavailable: bool = False


@dataclass(frozen=True)
class StallClass:
    """One member of the stall set.

    detector: "module:attribute" of the thing that detects it, or None when nothing
        detects it. None is a NAMED HOLE, deliberately visible (G1).
    evidence_kind: "span" — recomputable over any historical window from primary
        state; "point" — only observable at the moment it holds, so HX1 must SAMPLE
        it each tick and cannot reconstruct it after the fact.
    """

    id: str
    summary: str
    detector: str | None
    evidence_kind: str
    origin: str
    verdict: str
    notes: str = ""


# ── THE SET ─────────────────────────────────────────────────────────────────────
# Ordering: the five from HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27 §2 first, then
# the four the director returned (some of which subsume a proposal class — said so
# in `notes` rather than duplicated).
STALL_CLASSES: tuple[StallClass, ...] = (
    StallClass(
        id="supervisor_idle_turn_with_atoms",
        summary="A supervisor cycle where find_work() returned nothing while atoms remained.",
        detector="background.supervisor:_load_idle_turn_count",
        evidence_kind="point",
        origin="proposal_2026-07-27",
        verdict="already_detected",
        notes=(
            "Counter is ALL-TIME and monotone (supervisor._record_idle_turn); a span count is "
            "value_at_end - value_at_start, so HX1 must snapshot it at span open. A legitimate "
            "drained-and-gated rest is deliberately NOT counted (supervisor.run_cycle)."
        ),
    ),
    StallClass(
        id="map_exhausted_while_work_exists",
        summary="The self-refill draw found NO candidate at all — a genuine cannot-draw.",
        detector="background.supervisor:check_map_exhausted_escalation",
        evidence_kind="point",
        origin="proposal_2026-07-27",
        verdict="already_detected",
        notes="Transition-only NTFY + .supervisor_map_exhausted_state.json; no span history.",
    ),
    StallClass(
        id="director_hand_types_next_atom",
        summary="The director had to name the next piece of work himself.",
        detector="background.stall_class_register:detect_progress_gap_stalls",
        evidence_kind="span",
        origin="proposal_2026-07-27",
        verdict="detector_added",
        notes=(
            "The proposal asserted this had an existing detector. It did not — grep for RESCUE "
            "across background/ and tools/ returns no code. Covered here as the attributed half "
            "of the progress-gap detector: a director/advisor input that lands INSIDE a "
            "meaningful-progress gap and is followed by resumption is, by construction, the "
            "director naming the next move."
        ),
    ),
    StallClass(
        id="harden_while_content_unminted",
        summary="A HARDEN re-verify drawn while named product content sat un-minted.",
        detector=None,
        evidence_kind="point",
        origin="proposal_2026-07-27",
        verdict="uncovered",
        notes=(
            "UNCOVERED (G1 named hole). supervisor.py has a SUPPRESSOR for the adjacent case "
            "(_unconsumed_director_ruling_or_steer gates the RULE-0 HARDEN tier) but suppression "
            "leaves no event record, so a span cannot be audited for it. Closing this is HX1 "
            "scope, not HX2's — HX2's duty is that it is not silently missing."
        ),
    ),
    StallClass(
        id="act_later_ruled_reversible",
        summary="An [ACT] escalation the director later ruled was reversible all along.",
        detector=None,
        evidence_kind="span",
        origin="proposal_2026-07-27",
        verdict="uncovered",
        notes=(
            "UNCOVERED (G1 named hole). action_needed.resolve_item stores the director's answer "
            "text but never a reversibility verdict, so 'later ruled reversible' is not machine-"
            "readable. Would need a verdict field at resolve time; not built here."
        ),
    ),
    StallClass(
        id="meaningful_progress_gap",
        summary=(
            "A gap between MEANINGFUL commits longer than the project's own stall threshold "
            "with no director/advisor input inside it — the machine went quiet and came back."
        ),
        detector="background.stall_class_register:detect_progress_gap_stalls",
        evidence_kind="span",
        origin="HX2_E1",
        verdict="detector_added",
        notes=(
            "This is the E1 (emergency console rescue) fallback. A console turn leaves NO trace "
            "in THIS repository: director_input_log.py writes its channel-tagged record to the "
            "PRIVATE ops repo, so a third party with repository access — the ruling's own "
            "acceptance test — cannot see it. The gap it ended is visible in git, and by "
            "construction a rescue implies a gap. Over-inclusive by design (G5): a self-recovered "
            "gap also lands here, and under R17 that IS a stall."
        ),
    ),
    StallClass(
        id="stall_ended_by_director_or_advisor_input",
        summary=(
            "A meaningful-progress gap terminated by a director/advisor input — the machine "
            "had to be doorbelled awake."
        ),
        detector="background.stall_class_register:detect_progress_gap_stalls",
        evidence_kind="span",
        origin="HX2_E1_E4",
        verdict="detector_added",
        notes=(
            "The stall/decision split the ruling praises, mechanised: an input arriving while "
            "meaningful work is flowing is a DECISION and produces NO event; the same input "
            "arriving inside a silence and followed by resumption is a RESCUE. `channel` "
            "distinguishes E4 (advisor_bridge) from an NTFY steer (ntfy)."
        ),
    ),
    StallClass(
        id="publish_gate_wedged_over_an_hour",
        summary="The publish gate has been failing for more than an hour, blocking all publishing.",
        detector="background.stall_class_register:detect_publish_gate_wedge",
        evidence_kind="point",
        origin="HX2_E2",
        verdict="already_detected",
        notes=(
            "ALREADY DETECTED — this entry ADAPTS supervisor._publish_gate_wedge_active "
            "(PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS == 3600, i.e. exactly the director's '>1h') "
            "into a StallEvent. No new predicate. Point-kind: .publish_gate_state.json is "
            "overwritten in place and is not committed, so past wedges are not reconstructible "
            "— HX1 must sample this each tick."
        ),
    ),
    StallClass(
        id="origin_frozen_over_thirty_minutes",
        summary="Local commits have not reached origin for over thirty minutes.",
        detector="background.stall_class_register:detect_origin_freeze",
        evidence_kind="point",
        origin="HX2_E3",
        verdict="detector_added",
        notes=(
            "process_run_complete._push_reached_origin verifies ONE push attempt against "
            "ls-remote ground truth and alarms on a phantom, but nothing measured how long "
            "origin had been frozen — the 3.5h freeze was a sequence of individually-handled "
            "attempts. This measures the standing condition."
        ),
    ),
)


def stall_class(class_id: str) -> StallClass:
    for c in STALL_CLASSES:
        if c.id == class_id:
            return c
    raise KeyError(class_id)


# ── G2: named detectors must resolve ────────────────────────────────────────────
def resolve_detectors() -> dict[str, object]:
    """Import every NAMED detector. Raises StallRegistryError on the first that does
    not resolve — a renamed or deleted detector must fail LOUDLY, not degrade into a
    silently smaller stall set (R15 FAIL-SILENT). Classes with detector=None are not
    errors; they are reported by `uncovered_class_ids()`."""
    import importlib

    out: dict[str, object] = {}
    for cls in STALL_CLASSES:
        if cls.detector is None:
            continue
        if ":" not in cls.detector:
            raise StallRegistryError(
                f"{cls.id}: detector {cls.detector!r} is not 'module:attribute'"
            )
        mod_name, attr = cls.detector.split(":", 1)
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001 - any import failure is the same defect
            raise StallRegistryError(
                f"{cls.id}: detector module {mod_name!r} does not import ({type(exc).__name__}: "
                f"{exc}). A stall class whose detector vanished would otherwise read as "
                f"'no stalls of this class' -- the FAIL-SILENT pattern R15 forbids."
            ) from exc
        if not hasattr(mod, attr):
            raise StallRegistryError(
                f"{cls.id}: detector {mod_name}:{attr} no longer exists. Re-point or de-list the "
                f"class explicitly -- never leave the counter reading a class that cannot fire."
            )
        out[cls.id] = getattr(mod, attr)
    return out


def uncovered_class_ids() -> list[str]:
    """Classes in the set with NO detector. Non-empty means the stall count cannot be
    proven zero from machinery alone (G1)."""
    return [c.id for c in STALL_CLASSES if c.detector is None]


# ── primary-state readers ───────────────────────────────────────────────────────
def _run_git(*args: str) -> tuple[int, str]:
    """(rc, stdout). rc != 0 means UNREADABLE, which callers turn into an
    `unavailable` event — never into an empty (clean) result."""
    try:
        r = subprocess.run(
            ["git", *args], cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=30
        )
        return r.returncode, r.stdout
    except Exception:  # noqa: BLE001 - git missing/hung is the same "unreadable"
        return 1, ""


def _finite(value) -> bool:
    """R15 NaN-blindness guard: reject non-finite BEFORE any comparison."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return False
    return f == f and f not in (float("inf"), float("-inf"))


def meaningful_commits(since: float, until: float, *, runner=None) -> list[tuple[float, str]] | None:
    """Ascending (epoch, subject) of MEANINGFUL commits in [since, until], or None if
    git is unreadable.

    "Meaningful" reuses `deadmans_switch._is_non_progress_commit` rather than
    re-deriving it — one definition of forward progress for the deadman clock, the
    daily note and this register, so they cannot drift apart. A missing classifier
    RAISES (fail-closed): silently treating every commit as progress would make every
    span look stall-free.

    ONE addition the deadman does not need: a commit that merely STAGES a director or
    advisor document is INPUT, not the machine's output, so it is excluded here. This
    is not cosmetic — it was found by running this detector against the real 42h
    deadlock of 2026-07-25/27, where the advisor's own staging commit (`c0647456b`,
    "[DIRECTOR-RULING][ADVISOR-STAGED] EIGHTH CLASS ...") counted as the machine
    resuming work and so hid the very rescue it was. Counting a doorbell as progress
    makes a doorbelled stall undetectable by construction."""
    from background.deadmans_switch import _is_non_progress_commit

    run = runner or _run_git
    rc, out = run("log", f"--since=@{int(since)}", f"--until=@{int(until)}", "--format=%ct%x00%s")
    if rc != 0:
        return None
    rows: list[tuple[float, str]] = []
    for line in out.splitlines():
        if "\x00" not in line:
            continue
        ct_str, subject = line.split("\x00", 1)
        if not _finite(ct_str):
            continue
        if _is_non_progress_commit(subject):
            continue
        if _BRIDGE_SUBJECT_RE.search(subject):
            continue
        rows.append((float(ct_str), subject))
    rows.sort(key=lambda r: r[0])
    return rows


_FROM_RICH_RE = re.compile(r"from_rich_(\d{8})_(\d{6})(?:_[0-9a-f]+)?\.md$")
_BRIDGE_DOC_RE = re.compile(r"/(?:DIRECTOR|ADVISOR)_[A-Z0-9_]+\.md$")
_BRIDGE_SUBJECT_RE = re.compile(r"\[(?:DIRECTOR-[A-Z]+|ADVISOR-STAGED)\]")


@dataclass(frozen=True)
class DirectorInput:
    at: float
    channel: str  # "ntfy" | "advisor_bridge"
    ref: str
    unattributed_time: bool = False


def director_inputs(since: float, until: float, *, runner=None) -> list[DirectorInput] | None:
    """Director/advisor inputs that ARRIVED in [since, until], from git alone, or None
    if git is unreadable.

    Two primary-state signatures, both third-party checkable with no machine access:
      * a `from_rich_*.md` file ADDED anywhere under docs/staging/ — the NTFY channel.
        Its ARRIVAL time is parsed from the filename (UTC, written by
        ntfy_responder), which is exact; the commit that swept it in may be much
        later, so filename time is preferred and commit time is only a fallback.
      * a DIRECTOR_*/ADVISOR_*.md staging doc added, or a commit subject carrying a
        [DIRECTOR-*]/[ADVISOR-STAGED] tag — the advisor bridge.

    NOT a signature: a console turn. `director_input_log.py` tags console turns
    `window`, but writes to the PRIVATE ops repo, so it is invisible to this repo's
    primary state. That hole is why `meaningful_progress_gap` exists as E1's fallback.
    """
    run = runner or _run_git
    # Widen the git window: a from_rich file that ARRIVED inside the span may have been
    # committed well after it, so filtering commits to the span would drop it.
    rc, out = run(
        "log",
        f"--since=@{int(since) - 7 * 24 * 3600}",
        f"--until=@{int(until) + 7 * 24 * 3600}",
        "--diff-filter=A",
        "--name-only",
        "--format=%x01%ct%x00%s",
    )
    if rc != 0:
        return None
    events: list[DirectorInput] = []
    commit_ts: float | None = None
    subject = ""
    for raw in out.splitlines():
        if raw.startswith("\x01"):
            body = raw[1:]
            commit_ts, subject = (None, "")
            if "\x00" in body:
                ct_str, subject = body.split("\x00", 1)
                commit_ts = float(ct_str) if _finite(ct_str) else None
            if commit_ts is not None and _BRIDGE_SUBJECT_RE.search(subject):
                events.append(DirectorInput(commit_ts, "advisor_bridge", subject[:120]))
            continue
        path = raw.strip()
        if not path or not path.startswith("docs/staging/"):
            continue
        m = _FROM_RICH_RE.search(path)
        if m:
            at = _parse_from_rich_stamp(m.group(1), m.group(2))
            events.append(
                DirectorInput(
                    at if at is not None else (commit_ts or 0.0),
                    "ntfy",
                    path,
                    unattributed_time=at is None,
                )
            )
            continue
        if _BRIDGE_DOC_RE.search("/" + path):
            if commit_ts is not None:
                events.append(DirectorInput(commit_ts, "advisor_bridge", path))
    inside = [e for e in events if since <= e.at <= until]
    inside.sort(key=lambda e: e.at)
    return inside


def _parse_from_rich_stamp(day: str, clock: str) -> float | None:
    from datetime import datetime, timezone

    try:
        return datetime.strptime(day + clock, "%Y%m%d%H%M%S").replace(
            tzinfo=timezone.utc
        ).timestamp()
    except ValueError:
        return None


# ── E1 / E4 / "director hand-types the next atom" ───────────────────────────────
def _progress_gap_threshold() -> float:
    """The project's OWN stall threshold, imported rather than restated so the two
    cannot drift (deadmans_switch fires [STALL] at exactly this age)."""
    from background.deadmans_switch import SILENT_STALL_THRESHOLD_SECONDS

    return float(SILENT_STALL_THRESHOLD_SECONDS)


def detect_progress_gap_stalls(
    since: float,
    until: float,
    *,
    gap_seconds: float | None = None,
    attribution_window: float = RESCUE_ATTRIBUTION_WINDOW_SECONDS,
    runner=None,
) -> list[StallEvent]:
    """Span-wise stall detection from git alone.

    A GAP is an interval between two consecutive MEANINGFUL commits longer than the
    project's stall threshold. For each gap, if a director/advisor input landed INSIDE
    it and meaningful work resumed within `attribution_window` of that input, the gap
    is a RESCUE (`stall_ended_by_director_or_advisor_input`, carrying the channel);
    otherwise it is an unattributed `meaningful_progress_gap`.

    This is the stall/decision split, mechanised: an input that arrives while
    meaningful commits are flowing produces NO event at all, because there is no gap
    to attribute it to. Only an input that arrives into silence, and is followed by
    work, is counted. That is exactly the ruling's "director DECISION-class touches
    unrestricted".

    FAIL-CLOSED: git unreadable -> a single `unavailable` event, never [].
    LIMITATION (stated, not hidden): a gap during a PROVEN legitimate rest (R17
    rest-with-proof) is not distinguishable here, because rest-proof is written to a
    point-in-time file that is not committed. Such a gap is counted. Conservative by
    G5; the attributed half is unaffected because a proven rest produces no director
    input."""
    threshold = _progress_gap_threshold() if gap_seconds is None else float(gap_seconds)
    commits = meaningful_commits(since, until, runner=runner)
    if commits is None:
        return [
            StallEvent(
                "meaningful_progress_gap",
                None,
                "git history unreadable -- an unavailable check is a FAILED check (R15), so this "
                "span is NOT provably stall-free.",
                unavailable=True,
            )
        ]
    inputs = director_inputs(since, until, runner=runner)
    inputs_unavailable = inputs is None
    inputs = inputs or []

    events: list[StallEvent] = []
    for (start_ts, _s1), (end_ts, end_subject) in zip(commits, commits[1:]):
        if end_ts - start_ts < threshold:
            continue
        gap_min = int((end_ts - start_ts) // 60)
        rescuer = None
        for inp in inputs:
            if start_ts < inp.at < end_ts and (end_ts - inp.at) <= attribution_window:
                rescuer = inp
                break
        if rescuer is not None:
            events.append(
                StallEvent(
                    "stall_ended_by_director_or_advisor_input",
                    end_ts,
                    f"{gap_min} min without a meaningful commit, ended {int((end_ts - rescuer.at) // 60)} "
                    f"min after {rescuer.channel} input {rescuer.ref[:100]!r}; resumed with "
                    f"{end_subject[:80]!r}",
                    channel=rescuer.channel,
                )
            )
        else:
            events.append(
                StallEvent(
                    "meaningful_progress_gap",
                    end_ts,
                    f"{gap_min} min without a meaningful commit, no director/advisor input inside "
                    f"the gap (a console rescue leaves no trace in this repo); resumed with "
                    f"{end_subject[:80]!r}",
                )
            )
    if inputs_unavailable:
        events.append(
            StallEvent(
                "stall_ended_by_director_or_advisor_input",
                None,
                "director/advisor input history unreadable -- attribution could not run, so any "
                "gap above may in fact be a rescue (R15: unavailable == FAILED).",
                unavailable=True,
            )
        )
    return events


# ── E2 (adapter over the existing detector) ─────────────────────────────────────
def detect_publish_gate_wedge(
    now: float | None = None,
    *,
    state_path: Path | None = None,
    last_tested_path: Path | None = None,
    head: str | None = None,
) -> StallEvent | None:
    """ADAPTER, not a new predicate. `supervisor._publish_gate_wedge_active` already
    fires at exactly the director's ">1h" bar (PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS ==
    3600) with an independent .last_tested_hash cross-check. This wraps its verdict as
    a StallEvent so the register speaks one vocabulary.

    Deliberately inherits the supervisor's fail-safe: an absent/malformed state file
    yields no wedge. That is right THERE (a phantom RUNG-1 draw would displace real
    work) and it is right here too — the wedge alarm is not the only stall detector,
    and the publish-gate class is `point`-kind precisely because its state is not
    durable."""
    from background import supervisor

    msg = supervisor._publish_gate_wedge_active(
        now=now, head=head, state_path=state_path, last_tested_path=last_tested_path
    )
    if not msg:
        return None
    return StallEvent("publish_gate_wedged_over_an_hour", now, msg[:400])


# ── E3 ──────────────────────────────────────────────────────────────────────────
def _ls_remote_head(runner=None) -> str | None:
    run = runner or _run_git
    rc, out = run("ls-remote", "origin", "refs/heads/main")
    if rc != 0 or not out.split():
        return None
    return out.split()[0]


def detect_origin_freeze(
    now: float,
    *,
    threshold_seconds: float = ORIGIN_FREEZE_THRESHOLD_SECONDS,
    runner=None,
    remote_head_fn=None,
) -> StallEvent | None:
    """Is origin FROZEN — local commits unpushed for longer than the threshold?

    `process_run_complete._push_reached_origin` already makes a single push attempt
    honest (rc=0 is not enough; ls-remote must show origin at local HEAD). What it
    cannot see is DURATION: the 3.5h freeze of 2026-07-24 was a run of individually
    "handled" attempts while 15 real commits stacked up locally. This measures the
    standing condition instead of the attempt.

    Ground truth, not the tracking ref: the remote head comes from `git ls-remote`,
    exactly as the push verifier does. The local remote-tracking ref is the very thing
    that goes stale in this failure, so reading it would be the TAUTOLOGY pattern —
    checking the phantom against the phantom.

    FAIL-CLOSED (R15): origin unreachable -> `unavailable` event, not "no freeze". No
    network in an autonomous run is a check that did not run, and an unavailable check
    is a FAILED check.

    Cannot jam the pipeline: this returns a verdict and writes nothing. Its only
    consumer is the exit-criterion counter, so a false positive delays a harness
    decision — it never blocks a publish."""
    run = runner or _run_git
    if not _finite(now):
        return StallEvent(
            "origin_frozen_over_thirty_minutes", None, "non-finite clock supplied", unavailable=True
        )
    rc, out = run("rev-parse", "HEAD")
    local_head = out.strip() if rc == 0 else ""
    if not local_head:
        return StallEvent(
            "origin_frozen_over_thirty_minutes",
            None,
            "local HEAD unreadable -- freeze state unknown (R15: unavailable == FAILED)",
            unavailable=True,
        )
    remote_head = (remote_head_fn or (lambda: _ls_remote_head(runner=run)))()
    if not remote_head:
        return StallEvent(
            "origin_frozen_over_thirty_minutes",
            None,
            "origin head unreadable (ls-remote failed/offline) -- the machine cannot know whether "
            "its pushes are landing, which is precisely the phantom-push blind spot (R15: "
            "unavailable == FAILED)",
            unavailable=True,
        )
    if remote_head == local_head:
        return None
    rc, out = run("log", f"{remote_head}..HEAD", "--format=%ct")
    if rc != 0:
        return StallEvent(
            "origin_frozen_over_thirty_minutes",
            None,
            f"cannot compare origin {remote_head[:9]} with local HEAD {local_head[:9]} -- the "
            "remote commit is not present locally, so unpushed age is unknown (R15: unavailable "
            "== FAILED)",
            unavailable=True,
        )
    stamps = [float(t) for t in out.split() if _finite(t)]
    if not stamps:
        return None  # nothing unpushed: origin is ahead or equal by another path
    oldest = min(stamps)
    age = now - oldest
    if age < float(threshold_seconds):
        return None
    return StallEvent(
        "origin_frozen_over_thirty_minutes",
        oldest,
        f"{len(stamps)} local commit(s) have not reached origin; the oldest has been unpushed for "
        f"~{int(age // 60)} min (origin {remote_head[:9]}, HEAD {local_head[:9]}). Publishing may "
        f"look healthy locally while the advisor bridge is blind.",
    )


# ── coverage surface (the live consumer) ────────────────────────────────────────
@dataclass(frozen=True)
class Coverage:
    total: int
    covered: int
    uncovered: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def complete(self) -> bool:
        return self.error is None and not self.uncovered


def coverage() -> Coverage:
    """Registry self-check: does every enumerated class resolve to a live detector?
    Used by the daily self-note so the named holes are visible every morning rather
    than discovered when HX1 quietly counts zero."""
    try:
        resolved = resolve_detectors()
    except StallRegistryError as exc:
        return Coverage(len(STALL_CLASSES), 0, uncovered_class_ids(), error=str(exc)[:300])
    return Coverage(len(STALL_CLASSES), len(resolved), uncovered_class_ids())


def coverage_line() -> str:
    """One markdown line for the daily self-note. RED whenever the set is not fully
    covered — the honest reading is 'the stall count cannot yet be proven zero',
    which is exactly what HX1 needs to know before it trusts its own counter."""
    cov = coverage()
    if cov.error:
        return (
            f"🔴 **Stall-set coverage: BROKEN** — {cov.error} "
            f"(a named detector no longer resolves; the exit-criterion counter must not be trusted)"
        )
    if cov.uncovered:
        return (
            f"🟠 Stall-set coverage: {cov.covered}/{cov.total} classes have a live detector — "
            f"UNCOVERED: {', '.join(cov.uncovered)}. A zero stall count is therefore *not proof* of "
            f"a clean span (docs/design/HX2_STALL_SET_COVERAGE_VERDICT.md)."
        )
    return f"🟢 Stall-set coverage: all {cov.total} classes have a live detector."
