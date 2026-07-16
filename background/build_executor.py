#!/usr/bin/env python3
"""Autonomous build-executor — SAFE-DARK foundation (H17 / H10_autonomous_build_executor).

Scope of THIS module (Appendix-C steps 1-3, AUTONOMOUS_EXECUTOR_SPEC.md):
  1. Skeleton lifecycle primitives (dispatch_turn / reap_turn / log / _heartbeat),
     lifted from the retired autonomous_runner.py's REUSABLE primitives (Appendix A.1
     #1/#3/#6/#7/#9/#10/#11/#12) and inheriting NONE of its governance anti-patterns.
  2. THE RETURN-GATE: write_landed(sha) — success is WRITE-LANDED (a commit SHA
     genuinely on origin), never submit-consumed. Reuses the two pure git predicates
     from .claude/hooks/block_unevidenced_claim.py so the independence rule is one
     mechanism, not two copies.
  3. run_once(): draw (background.supervisor._self_refill_draw) -> dispatch ONE
     headless turn -> gate its return -> record the outcome. One turn, no loop.

SAFETY — this module is DARK. It has NO activation surface of its own:
  * It is NOT wired into background/start_worker.sh (no launcher entry).
  * It reads NO enable-flag and creates none.
  * dispatch_turn's binary is PARAMETERISED (bin_path, default the real CLAUDE_BIN)
    purely so tests inject a STUB. Nothing in this module ever runs a real
    `claude -p` turn; that is a later, director-present, attended step (Appendix C.6
    step 6) and activation of any unattended loop is director-console-only (C.5).
  * There is no `while True` / daemon / main() loop here. run_once does exactly one
    gated cycle and returns.

Governance anti-patterns explicitly NOT inherited (Appendix A.2): no pane-scrape
liveness, no non-durable respawner, no free-text-prompt / rc-only success, no
self-directing scope. The tripwire governor, launcher wiring, and activation
(steps 4-9) are OUT OF SCOPE for this module.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

PROJECT_DIR = Path(__file__).resolve().parent.parent

# --- Primitive #3: absolute CLAUDE_BIN path + existence guard ----------------
# Full path since nvm isn't active in a subprocess env (real operational lesson).
CLAUDE_BIN = Path("/home/rich/.nvm/versions/node/v24.16.0/bin/claude")

# --- Model routing (DIRECTOR_ANSWERS_C7 #5): the executor IS the main loop, so
# its TURN model is OPUS -- the standing Monday decision (judgment failures were
# main-session failures). Per-atom routing INSIDE a turn still follows CLAUDE.md
# (build=Opus, swarm=Sonnet, supervisor micro=Haiku) -- that is the turn's own
# choice. AUTONOMOUS_TURN_MODEL (Haiku) is retained ONLY for the deferred
# tournament-life micro-turns (Epoch-4), never for a build-executor draw turn.
MAIN_LOOP_MODEL = "claude-opus-4-8"
AUTONOMOUS_TURN_MODEL = "claude-haiku-4-5-20251001"  # tournament lives only (deferred)

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "build-executor-log.md"
TURN_OUTPUT_DIR = PROJECT_DIR / "docs" / "observability" / "build-executor-turns"

AGENT_NAME = "build-executor"
_AGENT_ROLE = (
    "Governed headless-turn executor: consumes the Rule-0 self-refill draw and "
    "lands one gated unit of build work per cycle (SAFE-DARK foundation)."
)
_AGENT_PRODUCES = "write-landed build turns (origin-verified commit SHAs)"

# Reap wait bound (seconds). A real drawn turn can run for minutes; this is a
# generous cap so a hung child cannot wedge a manual --once cycle forever.
REAP_TIMEOUT_SECONDS = 30 * 60

# Landed-evidence poll cadence (seconds). The verdict is gated on LANDED evidence,
# not process exit, so reap_turn polls the turn's output for its schema-forced
# return; this bounds how often it looks. Cheap when no return has appeared yet
# (no claimed_sha -> no git fetch), so a tight cadence costs nothing while the
# child is still thinking.
REAP_POLL_INTERVAL_SECONDS = 5

# A candidate git SHA: 7..40 hex chars, whole token (mirrors the hook's contract).
_SHA_RE = re.compile(r"\A[0-9a-f]{7,40}\Z", re.IGNORECASE)


# --- Reuse the hook's two pure git predicates (independence, one mechanism) ---
def _load_hook_predicates() -> tuple[Callable[[], Optional[str]], Callable[[str, str], bool]]:
    """Import _resolve_origin_ref / _sha_on_origin from the block-unevidenced-claim
    hook by file path (it lives under .claude/hooks, not an importable package).

    This is deliberate REUSE, not a copy: the write-landed gate and the outbound
    claim gate must share one definition of "on origin" so they cannot drift.
    """
    hook_path = PROJECT_DIR / ".claude" / "hooks" / "block_unevidenced_claim.py"
    spec = importlib.util.spec_from_file_location("_block_unevidenced_claim", hook_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load hook predicates from {hook_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._resolve_origin_ref, module._sha_on_origin


_resolve_origin_ref, _sha_on_origin = _load_hook_predicates()


# =============================================================================
# Primitive #9: append-only, UTC-stamped log
# =============================================================================
def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry, flush=True)


# =============================================================================
# Primitive #10: agent_status heartbeat (the Director-door consumes this file)
# =============================================================================
def _heartbeat(state: str, last_action: str, *, anomaly: str | None = None) -> None:
    """Surface the executor's live state on agent_status.json.

    Invisibility (not autonomy) is what retired the predecessor (Appendix A.2 #3),
    so every meaningful transition heartbeats. Failure to update the status file
    must never crash a cycle -> swallow-and-log.
    """
    try:
        from background.agent_status import update_agent_status

        update_agent_status(
            AGENT_NAME,
            status=state,
            last_action=last_action,
            anomaly=anomaly,
            role=_AGENT_ROLE,
            produces=_AGENT_PRODUCES,
        )
    except Exception as exc:  # pragma: no cover - defensive
        log(f"heartbeat failed ({state}): {exc}")


# =============================================================================
# Result / handle dataclasses
# =============================================================================
@dataclass
class TurnHandle:
    """A dispatched (in-flight) headless turn."""

    proc: Any
    out_path: Path
    prompt: str
    model: str


@dataclass
class RawTurnResult:
    """Reaped turn: exit-code capture (#6) + structured infra classification (#7).

    The VERDICT fields (landed / claimed_sha / structured_return / surfaced_via) are
    gated on LANDED EVIDENCE, surfaced the moment work lands on origin, NEVER on the
    child's exit -- so a child that lands its work and then hangs cannot block a true
    result. `surfaced_via` records which termination signal settled the verdict:
    'landed' (work on origin, child may still have been running), 'exit' (process
    exited), or 'timeout' (killed at the reap bound)."""

    rc: int
    out_path: Path
    infra_failure: bool = False
    timed_out: bool = False
    landed: bool = False
    claimed_sha: str | None = None
    structured_return: dict | None = None
    surfaced_via: str = ""


@dataclass
class LandedEvidence:
    """What the gate reads off the turn's captured output, INDEPENDENT of process
    exit: the schema-forced structured return and whether its claimed_commit_sha is
    genuinely on origin. This -- not `rc` -- is the verdict."""

    landed: bool = False
    claimed_sha: str | None = None
    structured_return: dict | None = None


@dataclass
class ExecutorCycleResult:
    """Outcome of one run_once cycle. status in {success, failed, escalated, idle, error, skipped}."""

    status: str
    atom_reason: str | None = None
    claimed_sha: str | None = None
    landed: bool = False
    rc: int | None = None
    infra_failure: bool = False
    detail: str = ""
    structured_return: dict | None = field(default=None)


# =============================================================================
# Primitive #1 (+#3, #11): headless `claude -p` dispatch with env hygiene
# =============================================================================
def _child_env() -> dict:
    """Per-launch env hygiene (primitive #11): go direct (no token-proxy SPOF)
    and force DISABLE_AUTOUPDATER rather than trusting tmux inheritance."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_BASE_URL", None)
    env["DISABLE_AUTOUPDATER"] = "1"
    return env


def dispatch_turn(
    prompt: str,
    *,
    model: str | None = None,
    out_path: Path | None = None,
    bin_path: Path | None = None,
    popen: Callable[..., Any] = subprocess.Popen,
) -> TurnHandle | None:
    """Launch ONE headless, non-interactive `claude -p` turn (primitive #1).

    Output is redirected to a file (never a TTY); the executor NEVER types into
    an interactive pane. `bin_path` and `popen` are PARAMETERISED (defaults: the
    real CLAUDE_BIN / subprocess.Popen) solely so tests inject a stub binary or a
    fake Popen — this module never dispatches against the real binary itself.

    Returns None (logged) if the binary is missing — primitive #3's existence guard.
    """
    model = model or AUTONOMOUS_TURN_MODEL
    bin_path = Path(bin_path) if bin_path is not None else CLAUDE_BIN

    if not bin_path.exists():
        log(f"claude binary not found at {bin_path} — cannot dispatch turn")
        return None

    if out_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        TURN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = TURN_OUTPUT_DIR / f"turn_{ts}.out"
    else:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # Redirect stdout+stderr to the capture file (append-safe).
    outfile = open(out_path, "a")
    try:
        proc = popen(
            [
                str(bin_path),
                "-p",
                "--model",
                model,
                "--dangerously-skip-permissions",
                prompt,
            ],
            cwd=str(PROJECT_DIR),
            stdout=outfile,
            stderr=outfile,
            text=True,
            env=_child_env(),
        )
    except Exception:
        outfile.close()
        raise

    log(f"dispatched headless turn (model={model}, out={out_path.name})")
    return TurnHandle(proc=proc, out_path=out_path, prompt=prompt, model=model)


# =============================================================================
# Primitive #6 (+#7): reap the turn, capture rc, classify infra failure
# =============================================================================
# Structured connectivity classifier (primitive #7, re-implemented off a real
# signal, NOT the old fragile rsplit("---\n",1)[-1] substring grep of a log tail).
# These are the markers a `claude -p` process emits on a genuine transport failure.
_INFRA_MARKERS = (
    "ConnectionRefused",
    "ConnectionError",
    "Unable to connect",
    "ENOTFOUND",
    "ECONNREFUSED",
    "ETIMEDOUT",
    "getaddrinfo",
)


def _classify_infra_failure(rc: int, out_path: Path) -> bool:
    """True iff a non-zero exit looks like an infra/connectivity failure (so the
    budget window is not charged for API downtime). Structured: only consulted on
    rc != 0, and matched against a bounded set of transport markers."""
    if rc == 0:
        return False
    try:
        tail = out_path.read_text(encoding="utf-8", errors="replace")[-4000:]
    except OSError:
        return False
    return any(marker in tail for marker in _INFRA_MARKERS)


def _landed_evidence(out_path: Path, *, fetch: bool = True) -> LandedEvidence:
    """Read the turn's LANDED evidence from its captured output -- the ONLY thing the
    verdict is gated on. Parses the schema-forced return; if it carries a
    claimed_commit_sha, fetches origin (so the tracking ref reflects a just-pushed
    turn) then evaluates write_landed.

    Cheap while the turn is still thinking: no claimed_sha in the output yet -> no
    fetch, no git at all -- so this is safe to call on a tight poll from reap_turn.
    """
    ret = _parse_structured_return(out_path)
    claimed = (ret or {}).get("claimed_commit_sha") or None
    if not claimed:
        return LandedEvidence(landed=False, claimed_sha=None, structured_return=ret)
    if fetch:
        _git_fetch()
    return LandedEvidence(landed=write_landed(claimed), claimed_sha=claimed, structured_return=ret)


def _reap_surplus_child(proc: Any) -> int:
    """The turn's work has already LANDED, so the child is now surplus. Reap it
    WITHOUT blocking on a hang: already-exited -> take its rc; still-running (the
    hung-but-landed case the whole design exists for) -> kill it and move on. The
    verdict is already true; a slow/hung teardown must never delay it."""
    try:
        rc = proc.poll()
    except Exception:  # pragma: no cover - defensive
        rc = None
    if rc is not None:
        return rc
    try:
        proc.kill()
    except Exception:  # pragma: no cover - defensive
        pass
    try:
        return proc.wait(timeout=30)
    except Exception:  # pragma: no cover - defensive
        return 0  # landed already; the teardown rc is immaterial to the verdict


def reap_turn(
    handle: TurnHandle,
    *,
    timeout: int = REAP_TIMEOUT_SECONDS,
    poll_interval: float = REAP_POLL_INTERVAL_SECONDS,
    fetch: bool = True,
    probe: Callable[[], LandedEvidence] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> RawTurnResult:
    """Surface the turn's VERDICT on LANDED EVIDENCE, not on process exit.

    THE CONTRACT (mutation-tested, test_reap_surfaces_verdict_on_landing_not_exit):
    the moment the turn's work is landed on origin -- its schema-forced return names
    a claimed_commit_sha genuinely reachable on the origin ref -- the verdict surfaces
    IMMEDIATELY. A child that lands its work and then HANGS can never block a true
    result; a child that DIES without landing surfaces a FAILED verdict just as
    promptly. Process exit is one termination signal among {landed | exit | timeout},
    never THE gate. This corrects the prior design, which blocked on proc.wait(timeout)
    first and so let a hung-but-successful child wedge the cycle for the full 30 min.

    `probe`/`sleep`/`monotonic` are injectable so the mutation test drives a
    hung-but-landed child deterministically, with no wall-clock waits.
    """
    proc = handle.proc
    probe = probe or (lambda: _landed_evidence(handle.out_path, fetch=fetch))

    deadline = monotonic() + timeout
    ev = LandedEvidence()
    rc: int | None = None
    timed_out = False
    surfaced_via = ""

    while True:
        ev = probe()
        if ev.landed:
            # Work is on origin -> the verdict is TRUE now, regardless of whether the
            # child has exited. Reap the surplus child without blocking on a hang.
            surfaced_via = "landed"
            rc = _reap_surplus_child(proc)
            break

        if proc.poll() is not None:
            # Exited without landed evidence in hand. Take one final read (the return
            # may have been flushed at exit), then settle the verdict.
            surfaced_via = "exit"
            rc = proc.returncode if proc.returncode is not None else -1
            ev = probe()
            break

        if monotonic() >= deadline:
            surfaced_via = "timeout"
            timed_out = True
            try:
                proc.kill()
            except Exception:  # pragma: no cover - defensive
                pass
            try:
                rc = proc.wait(timeout=30)
            except Exception:  # pragma: no cover - defensive
                rc = -1
            log(f"turn timed out after {timeout}s — killed (out={handle.out_path.name})")
            break

        sleep(poll_interval)

    if rc is None:  # pragma: no cover - defensive
        rc = -1
    # Infra classification only matters on the FAIL path -- a landed turn is a success
    # however its child exited or was reaped.
    infra = False if ev.landed else _classify_infra_failure(rc, handle.out_path)
    log(
        f"reaped turn (surfaced_via={surfaced_via}, landed={ev.landed}, rc={rc}, "
        f"infra_failure={infra}, timed_out={timed_out})"
    )
    return RawTurnResult(
        rc=rc,
        out_path=handle.out_path,
        infra_failure=infra,
        timed_out=timed_out,
        landed=ev.landed,
        claimed_sha=ev.claimed_sha,
        structured_return=ev.structured_return,
        surfaced_via=surfaced_via,
    )


# =============================================================================
# STEP 2 — THE RETURN-GATE: write-landed, not submit-consumed (R15, mutation-tested)
# =============================================================================
def write_landed(sha: str | None) -> bool:
    """The success predicate. TRUE iff `sha` is a valid commit SHA genuinely
    reachable on the origin tracking ref (i.e. was actually pushed).

    This is the non-negotiable floor from AUTONOMOUS_EXECUTOR_SPEC.md §C.2/§Verification
    standard: a turn "succeeds" only when its work LANDED on origin, never because a
    turn was submitted or exited 0. The agent cannot satisfy this by touching a file
    — only by doing the work and publishing it (that is the independence).

    Fail-closed everywhere (R15 killer patterns): no/blank/malformed SHA -> False
    (FAIL-OPEN killer); origin tracking ref unresolvable / git unavailable -> False
    (FAIL-SILENT killer — an unavailable check is a FAILED check); a valid SHA that is
    NOT an ancestor of origin -> False (submit-not-landed, the named defect).

    Note: this predicate does NOT fetch — call _git_fetch() first (run_once does) so
    the tracking ref reflects a just-pushed turn. Kept fetch-free so the predicate is
    a pure, network-optional function of git's local view of origin (mutation-testable
    against a throwaway repo with no network).
    """
    if not sha:
        return False
    sha = sha.strip()
    if not _SHA_RE.match(sha):
        return False
    origin_ref = _resolve_origin_ref()
    if origin_ref is None:
        # Check UNAVAILABLE -> fail closed (never a pass).
        return False
    return _sha_on_origin(sha, origin_ref)


def _git_fetch() -> bool:
    """Update the origin tracking ref so write_landed sees a just-pushed turn.
    Best-effort: a fetch failure leaves the local view stale, which write_landed
    then treats as not-landed (fail-closed) — never a false pass."""
    try:
        proc = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"git fetch origin failed: {exc}")
        return False
    if proc.returncode != 0:
        log(f"git fetch origin non-zero rc={proc.returncode}: {proc.stderr.strip()[:200]}")
        return False
    return True


# =============================================================================
# STEP 3 — run_once: draw -> dispatch ONE -> gate the return -> record
# =============================================================================
# The schema-forced structured return the turn must emit (replaces A.2 #7's free
# text). We parse the LAST JSON object carrying claimed_commit_sha from the output.
_RETURN_KEYS = ("atom_id", "action", "claimed_commit_sha", "level_before", "level_after", "gate_status", "door_reason")


def _parse_structured_return(out_path: Path) -> dict | None:
    """Extract the turn's machine-checkable JSON return from its captured output.

    Scans for JSON objects and returns the LAST one that contains a
    'claimed_commit_sha' key. Absence of such a return is itself a FAILED turn
    (no evidence) — the caller treats a None here as unverifiable.
    """
    try:
        text = out_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    found: dict | None = None
    # Non-greedy brace scan; robust enough for a stub and for a turn that prints a
    # single JSON object. We prefer the last object carrying the SHA key.
    for match in re.finditer(r"\{[^{}]*\}", text, re.DOTALL):
        chunk = match.group(0)
        if "claimed_commit_sha" not in chunk:
            continue
        try:
            obj = json.loads(chunk)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict) and "claimed_commit_sha" in obj:
            found = obj
    return found


def _build_prompt(draw_reason: str) -> str:
    """Assemble the turn prompt: the governed draw reason as scope + a hard demand
    for the schema-forced structured return. (Not exercised against a real bin in
    this module; shaped here so the L1 attended --once step reuses it verbatim.)"""
    keys = ", ".join(_RETURN_KEYS)
    return (
        "You are a GOVERNED headless build-executor turn (H17). You run inside the repo, "
        "so CLAUDE.md's laws are IN FORCE -- follow them exactly. Your scope is EXACTLY "
        "the drawn work below; do not free-choose other work.\n\n"
        "DRAWN WORK (Rule-0 draw -- R7: this is a DOORBELL. Verify against real disk/git "
        f"state and act on that, never on this text alone):\n{draw_reason}\n\n"
        "GOVERNANCE WALLS you inherit, non-negotiable:\n"
        "- ONE-WAY DOORS -> the DIRECTOR. Escalate (gate_status='escalate') ONLY for a "
        "GENUINE, PROVABLY-IRREVERSIBLE one-way door (real money; legal/contractual/"
        "real-world commitments; unretractable public claims; irrecoverable data loss; "
        "security/secrets/safety-control changes; values/curriculum decisions e.g. opening "
        "a new epoch; a real customer or market; platform administration). A REVERSIBLE "
        "REVIEW-GATE IS NEVER A ONE-WAY DOOR: if the only question is 'is this good enough?' "
        "and a wrong answer demotes freely (e.g. a visible-surface / Expert-Hour sign-off), "
        "you DO NOT escalate -- cold-eyes decides it and you proceed (DELEGATE, P-4 narrowed). "
        "When you DO escalate, set door_reason to ONE self-contained sentence naming the "
        "SPECIFIC irreversible action + its door-class + the options (so the director can "
        "answer from his phone in one word); it is verified INDEPENDENTLY against the "
        "one_way_door predicate -- a door_reason the predicate does not confirm is downgraded "
        "and NOT sent to the director. Never decide a one-way door yourself; never escalate a "
        "reversible one.\n"
        "- TWIN for the reversible rest (e.g. BUILD-open within the open epoch); never "
        "self-authorize past a wall.\n"
        "- GATE-VERIFIED PUSH: run the blast-radius tests for your touched files AND the "
        "epistemic verifier; commit+push (via background.tree_lock) ONLY if both pass. "
        "Never push red.\n"
        "- ATOMIC LEVEL-WRITE (F1): you are a fork -- do NOT edit "
        "docs/design/maturity_map.yaml. Record the level you reached by writing a structured "
        "inbox at docs/design/atom_status/<atom-id>.yaml IN THE SAME COMMIT as your code "
        "(fields: `id`, `level_current`, optional `append_evidence`/`append_simplification`; "
        "schema in that dir's README). The loop folds it into the map via merge_atom_status "
        "as part of landing -- so the committed code and the reported level can never "
        "disagree. Do NOT free-text the level and leave the map to a separate judgment step.\n"
        "- NO pane/NTFY writes on your own initiative (the pane is the director's console).\n\n"
        "When finished, PUSH your work to origin, then end your final message with a single "
        "JSON object on its own line carrying these keys: "
        f"{{{keys}}}. 'claimed_commit_sha' MUST be the full SHA of a commit you actually "
        "pushed to origin; a turn that landed nothing reports an empty claimed_commit_sha "
        "with gate_status='failed' (or 'escalate' for a one-way door). Success is verified "
        "INDEPENDENTLY against origin -- an unpushed or fabricated SHA fails the gate."
    )


def run_once(
    *,
    draw_fn: Callable[[], str | None] | None = None,
    bin_path: Path | None = None,
    popen: Callable[..., Any] = subprocess.Popen,
    fetch: bool = True,
    out_path: Path | None = None,
    model: str | None = None,
    poll_interval: float = REAP_POLL_INTERVAL_SECONDS,
) -> ExecutorCycleResult:
    """ONE gated cycle: draw -> dispatch ONE headless turn -> gate the return -> record.

    Wrapped in try/except-that-only-logs (primitive #12) so one bad cycle cannot
    propagate. There is NO loop here — exactly one turn is dispatched and reaped.

    `draw_fn` defaults to background.supervisor._self_refill_draw (imported lazily so
    tests can inject a draw without pulling supervisor). `bin_path`/`popen` are
    injected by tests with a STUB; this function never dispatches against the real
    CLAUDE_BIN.
    """
    try:
        if draw_fn is None:
            from background.supervisor import _self_refill_draw as draw_fn  # type: ignore

        reason = draw_fn()
        if reason is None:
            # Genuine WALL — no at-target atom. Idle this cycle; do NOT invent work.
            _heartbeat("idle", "No draw available (wall) — idling this cycle")
            log("run_once: draw returned None (wall) — idling, no turn dispatched")
            return ExecutorCycleResult(status="idle", detail="draw wall")

        # A build-executor draw turn IS a main-loop turn -> Opus (answer #5).
        turn_model = model or MAIN_LOOP_MODEL
        _heartbeat("working", f"Dispatching {turn_model} turn for draw: {reason[:80]}")
        prompt = _build_prompt(reason)
        handle = dispatch_turn(
            prompt, model=turn_model, out_path=out_path, bin_path=bin_path, popen=popen
        )
        if handle is None:
            _heartbeat("error", "claude binary missing — cannot dispatch")
            return ExecutorCycleResult(status="error", atom_reason=reason, detail="binary missing")

        # Reap on LANDED EVIDENCE (not process exit): the verdict, claimed SHA and
        # structured return all come back off the RawTurnResult. reap_turn has already
        # fetched + evaluated write_landed, surfacing the moment work landed on origin.
        raw = reap_turn(handle, fetch=fetch, poll_interval=poll_interval)
        ret = raw.structured_return
        claimed_sha = raw.claimed_sha
        landed = raw.landed

        if landed:
            _heartbeat("idle", f"Turn LANDED (sha={claimed_sha[:12]}) for: {reason[:60]}")
            log(f"run_once SUCCESS: write-landed sha={claimed_sha} rc={raw.rc}")
            return ExecutorCycleResult(
                status="success",
                atom_reason=reason,
                claimed_sha=claimed_sha,
                landed=True,
                rc=raw.rc,
                infra_failure=raw.infra_failure,
                structured_return=ret,
                detail="write-landed on origin",
            )

        # WALL — the turn refused a one-way door (gate_status='escalate'). This is NOT
        # a failure: it is a governance boundary only the director may cross. Surface a
        # distinct 'escalated' status so the loop STOPS and alerts, never silently
        # retries a wall (C.4: a one-way door is never answered by the executor).
        if (ret or {}).get("gate_status") == "escalate":
            # PREDICATE-GATED ESCALATION (DIRECTOR_ANSWER_DELEGATE_AND_PREDICATE_FIX,
            # 2026-07-16): the turn self-reporting 'escalate' is NOT trusted. It fires a
            # director alert IFF the INDEPENDENT one_way_door predicate confirms a genuine
            # door on the turn's stated door_reason. A reversible review-gate the turn
            # mislabelled (SITE1 "director Expert Hour", "is it good enough") is DOWNGRADED
            # to a benign no-progress draw -- no director alert, loop proceeds. Fail-safe:
            # an escalation with NOTHING to classify still surfaces (never silently drop a
            # possibly-genuine door). This is the whole fix for the live mis-escalation.
            from background.one_way_door import classify_action
            door_reason = ((ret or {}).get("door_reason") or (ret or {}).get("action") or "").strip()
            verdict = classify_action(door_reason) if door_reason else None
            if door_reason and not verdict.is_one_way_door:
                log("run_once escalation DOWNGRADED (one_way_door predicate says reversible "
                    "review-gate, NOT a door; proceeding, no director alert): "
                    f"door_reason={door_reason[:160]!r}")
                _heartbeat("idle", f"Downgraded mis-escalation (reversible) for: {reason[:50]}")
                return ExecutorCycleResult(
                    status="idle",
                    atom_reason=reason,
                    claimed_sha=None,
                    landed=False,
                    rc=raw.rc,
                    infra_failure=raw.infra_failure,
                    structured_return=ret,
                    detail="escalation downgraded — reversible review-gate, not a one-way door",
                )
            cat = verdict.category.value if (verdict and verdict.category) else "unclassified"
            _heartbeat(
                "blocked",
                f"Turn ESCALATED a one-way door ({cat}) for: {reason[:50]}",
                anomaly="one-way-door escalation — director decision required",
            )
            log(f"run_once ESCALATED: genuine one-way door ({cat}) confirmed by predicate: "
                f"{door_reason or reason}")
            return ExecutorCycleResult(
                status="escalated",
                atom_reason=door_reason or reason,  # self-contained door_reason drives the NTFY
                claimed_sha=None,
                landed=False,
                rc=raw.rc,
                infra_failure=raw.infra_failure,
                structured_return=ret,
                detail=f"one-way-door escalation ({cat}) — director decision required",
            )

        # FAIL PATH — never rc-trusted. Turn recorded FAILED; atom NOT counted advanced.
        why = (
            "no claimed_commit_sha in structured return"
            if not claimed_sha
            else f"claimed_commit_sha {claimed_sha[:12]} NOT on origin (submit-not-landed)"
        )
        _heartbeat(
            "idle" if raw.infra_failure else "error",
            f"Turn FAILED gate ({why})",
            anomaly=None if raw.infra_failure else f"unlanded turn: {why}",
        )
        log(f"run_once FAILED gate: {why} (rc={raw.rc}, infra_failure={raw.infra_failure})")
        return ExecutorCycleResult(
            status="failed",
            atom_reason=reason,
            claimed_sha=claimed_sha,
            landed=False,
            rc=raw.rc,
            infra_failure=raw.infra_failure,
            structured_return=ret,
            detail=why,
        )
    except Exception as exc:  # primitive #12: one bad cycle can't kill the caller
        log(f"run_once error: {exc}")
        _heartbeat("error", f"run_once raised: {exc}", anomaly=str(exc))
        return ExecutorCycleResult(status="error", detail=str(exc))


# No main(), no daemon loop, no launcher entry, no enable-flag: this module is DARK.
# Activation (an unattended loop) is a director-console-only safety step (Appendix C.5).
