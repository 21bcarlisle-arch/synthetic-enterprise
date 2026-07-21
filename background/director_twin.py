"""DIRECTOR_TWIN — the pretend principal (2026-07-12, DIRECTOR_TWIN.md, capstone
of the autonomy work). Two callers exist per the doc; THIS module is the
builder-facing twin only (answers the agent's own questions in seconds) —
NOT the company-facing approver already registered in
company/governance/decision_rights.py (that one plays the human approver
inside the SIMULATED company's governance, where latency is physics; do not
conflate the two, per the doc's own explicit warning).

Cold-eyes discipline: the twin is a genuinely separate context (a fresh
`claude -p` subprocess, no shared conversation history with the caller) whose
ENTIRE brief is `docs/design/DIRECTOR_CANON.md` plus the one question and
context pack it's given -- it never sees the builder's internal case for
what it wants the answer to be.

Law B (non-negotiable): the twin's policy is director-authored curriculum.
It must NOT learn from outcomes -- there is no feedback loop from "the agent
proceeded and it worked out" back into the canon. The ONLY way the canon
changes is `overturn()`, which requires a human-supplied reason and bumps
the canon's version -- never a silent drift.

One-way doors are never answered by the twin -- `ask_twin()` runs the same
`background/one_way_door.py` predicate the agent itself uses, BEFORE ever
consulting the canon or spending a `claude -p` call, and routes to the real
director instead.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from background import gate_authorization
from background.one_way_door import classify_action

PROJECT_DIR = Path(__file__).resolve().parent.parent
CANON_PATH = PROJECT_DIR / "docs" / "design" / "DIRECTOR_CANON.md"
TWIN_LOG_PATH = PROJECT_DIR / "docs" / "observability" / "director_twin_log.jsonl"
OVERTURNS_LOG_PATH = PROJECT_DIR / "docs" / "observability" / "director_twin_overturns.jsonl"

CLAUDE_BIN = Path("/home/rich/.nvm/versions/node/v24.16.0/bin/claude")
# OPUS-tier, MANDATORY, non-negotiable (2026-07-12, MODEL_SELECTION_POLICY.md,
# director-raised): "its entire value is fidelity to the principal's
# judgement. A cheaper model that approximates the director BADLY is worse
# than no twin: it answers confidently, as him, wrongly, and the error only
# surfaces at overturn." Judgment work, not execution volume -- the
# opposite tier from BUILD/HARDEN work.
TWIN_MODEL = "claude-opus-4-8"

InvokeFn = Callable[[str], str]


@dataclass(frozen=True)
class TwinAnswer:
    entry_id: str
    question: str
    routed_to_director: bool
    answer: str | None
    reason: str
    latency_seconds: float
    confidence: str | None = None  # high|medium|low, parsed from the twin's own answer (director spec, 2026-07-13)
    defers_to_director: bool = False  # the twin's ANSWER itself reserves this decision to the director (e.g. R13 curriculum / canon §5), a director-reservation axis DISTINCT from the one-way-door classifier's routed_to_director. Parsed from a 'DEFERS_TO_DIRECTOR: yes|no' line. (2026-07-13 root-cause fix: a twin-answered curriculum reservation was silently not escalated to the director.)


def _default_invoke(prompt: str) -> str:
    """2026-07-12 SELF-CAUGHT INCIDENT, fixed same session: the first version
    of this function ran with `--dangerously-skip-permissions` and `cwd=
    PROJECT_DIR` -- a live test call spawned a fully unrestricted, fresh
    Claude Code session sharing this exact repo/working tree. That session
    inherited CLAUDE.md's own "poll docs/staging and action unread files"
    instruction, found this session's own uncommitted work sitting in the
    working tree, judged it complete, and committed + PUSHED to origin
    autonomously -- a real single-writer-to-main violation, entirely as an
    unintended side effect of what was meant to be a narrow "ask a question,
    read back the text" call. The twin needs ZERO tool access: the entire
    canon is embedded in the prompt text already (see `ask_twin()`), so it
    only ever needs to reason over text and print an answer. Fixed with
    defense in depth: no `--dangerously-skip-permissions` (default-deny
    permission mode, and non-interactive `-p` mode cannot satisfy a
    permission prompt so any tool call attempt fails closed); `--tools ""`
    explicitly disables every tool at the CLI level, structurally, not by
    convention; `cwd` set to a scratch temp directory outside this repo
    entirely, so even a determined attempt to read CLAUDE.md's own
    staging-poll instruction finds no `docs/staging/` there to act on."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="director_twin_scratch_") as scratch_dir:
        result = subprocess.run(
            # "--tools=" as ONE argv token (not "--tools", "" as two) -- verified
            # directly: the two-token form is misparsed by the CLI ("Input must
            # be provided either through stdin or as a prompt argument"), the
            # single "--tools=" token disables tool execution correctly (verified
            # against a real file-write attempt: the model prints a plausible
            # "I created it" narrative but no file is actually written).
            [str(CLAUDE_BIN), "-p", "--model", TWIN_MODEL, "--tools=", prompt],
            cwd=scratch_dir,
            capture_output=True,
            text=True,
            timeout=180,
        )
    return result.stdout.strip()


def _append_jsonl(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def current_canon_version() -> int:
    text = CANON_PATH.read_text(encoding="utf-8")
    m = re.search(r"\*\*Version:\s*(\d+)\.\*\*", text)
    return int(m.group(1)) if m else 1


def ask_twin(
    question: str,
    context_pack: str = "",
    *,
    uncertain: bool = False,
    invoke_fn: InvokeFn | None = None,
) -> TwinAnswer:
    """THE builder-facing call site. Returns in seconds for ordinary
    questions; routes to the real director (never answers) for anything
    matching the one-way-door predicate."""
    entry_id = datetime.now(timezone.utc).isoformat()
    verdict = classify_action(question, uncertain=uncertain)

    if verdict.is_one_way_door:
        _append_jsonl(TWIN_LOG_PATH, {
            "entry_id": entry_id,
            "question": question,
            "routed_to_director": True,
            "reason": verdict.reason,
            "category": verdict.category.value if verdict.category else None,
            "canon_version": current_canon_version(),
        })
        return TwinAnswer(
            entry_id=entry_id, question=question, routed_to_director=True,
            answer=None, reason=verdict.reason, latency_seconds=0.0,
        )

    canon = CANON_PATH.read_text(encoding="utf-8")
    prompt = (
        f"{canon}\n\n---\n"
        "QUESTION FROM THE BUILDER (you have never seen its conversation, context, or "
        "rationale for what it wants to hear -- only this question and the context pack "
        "below; per Law B, this canon is your entire world):\n"
        f"{question}\n\nCONTEXT PACK:\n{context_pack or '(none supplied)'}\n\n"
        "Answer directly and concisely (a few sentences), citing which canon section "
        "supports your answer. Then TWO final lines, each exactly in the given form:\n"
        "'DEFERS_TO_DIRECTOR: yes' if your answer reserves this decision to the director — "
        "i.e. it is HIS to author/decide per canon (a curriculum/difficulty change per R13, a "
        "values decision, a one-way door, or anything the canon marks director-reserved) and the "
        "builder must NOT proceed unilaterally; otherwise 'DEFERS_TO_DIRECTOR: no' (the builder "
        "may proceed on your answer).\n"
        "'CONFIDENCE: high' (or medium/low) — your confidence that this answer is what the "
        "director's canon actually requires (2026-07-13 director spec: confidence is logged)."
    )
    invoke = invoke_fn or _default_invoke
    start = time.time()
    answer_text = invoke(prompt)
    latency = time.time() - start

    m = re.search(r"CONFIDENCE:\s*(high|medium|low)", answer_text or "", re.IGNORECASE)
    confidence = m.group(1).lower() if m else None

    dm = re.search(r"DEFERS_TO_DIRECTOR:\s*(yes|no)", answer_text or "", re.IGNORECASE)
    # Fail SAFE: if the twin didn't emit a parseable line, treat as deferring
    # (better a spurious escalation than a silently-swallowed director-reservation
    # -- the exact failure this fix exists to prevent).
    defers_to_director = (dm.group(1).lower() == "yes") if dm else True

    _append_jsonl(TWIN_LOG_PATH, {
        "entry_id": entry_id,
        "question": question,
        "context_pack": context_pack,
        "routed_to_director": False,
        "defers_to_director": defers_to_director,
        "answer": answer_text,
        "confidence": confidence,
        "latency_seconds": round(latency, 3),
        "canon_version": current_canon_version(),
    })
    return TwinAnswer(
        entry_id=entry_id, question=question, routed_to_director=False,
        answer=answer_text, reason="answered from canon", latency_seconds=latency,
        confidence=confidence, defers_to_director=defers_to_director,
    )


def route_blocking_decision(
    item_id: str,
    question: str,
    how: str,
    context_pack: str = "",
    *,
    uncertain: bool = False,
    invoke_fn: InvokeFn | None = None,
) -> TwinAnswer:
    """THE builder's single call for any blocking / awaiting-director state
    (2026-07-13, director in-console authorization, canon v2 §3a: "wire it as
    a HOOK, not a habit ... you should never sit waiting on me again except at
    a genuine one-way door"). Routes the decision through the standing-approver
    seat:

    - `ask_twin()` classifies via the one-way-door predicate. For a GENUINE
      one-way door it returns `routed_to_director=True` (Law B: the twin NEVER
      answers these) — this function then registers a durable `[ACTION NEEDED]`
      for the REAL director (dedicated NTFY + daily re-ping) and the builder
      waits.
    - Otherwise the twin answers from canon in seconds; the builder proceeds
      on `ans.answer`. Every question + answer + confidence is already logged
      by `ask_twin()` (`director_twin_log.jsonl`); the director reviews and may
      `overturn()` (amends the canon, versioned).

    A decision is director-reserved on EITHER of two independent axes, and this
    function escalates on BOTH (2026-07-13 root-cause fix, director-reported: a
    twin-answered R13 CURRICULUM reservation for W2_2_population_draw was logged
    but never surfaced, because escalation was gated only on axis 1):
      1. `routed_to_director` — the one-way-door CLASSIFIER flagged the QUESTION
         (Law B: the twin never answers these).
      2. `defers_to_director` — the twin's own canon-based ANSWER reserves the
         decision to the director (curriculum/values/anything canon marks his),
         which the keyword classifier cannot catch. Fails safe: an unparseable
         signal is treated as deferring.
    In EITHER case a durable `[ACTION NEEDED]` is registered (dedicated NTFY +
    daily re-ping) and the caller must WAIT — `needs_director(ans)` says so.

    This is a voice, not a hand: it never performs the approved action, it only
    returns the approver's answer for the builder to act on."""
    from background import action_needed
    ans = ask_twin(question, context_pack, uncertain=uncertain, invoke_fn=invoke_fn)
    if ans.routed_to_director or ans.defers_to_director:
        if ans.routed_to_director:
            why = f"Genuine one-way door — the twin may never answer it (Law B). {ans.reason}"
        else:
            why = (
                "The twin's own canon-based answer reserves this decision to the director "
                f"(director-authored per canon, not agent-buildable). Twin's answer: {ans.answer}"
            )
        action_needed.register_item(item_id, question, how, why)
        try:
            from background.notify import notify
            # CLASS FIX (2026-07-18): register_item() above never advances the
            # send-clock -- only a CONFIRMED successful send (a truthy id) does,
            # via mark_sent(). A failed send here leaves the item due, so the next
            # route_blocking_decision/deadman sweep retries instead of the item
            # silently looking "already open" for a day.
            sent_id = notify(action_needed.format_action_needed(item_id, question, how, why), kind="real_alarm")
            if sent_id:
                action_needed.mark_sent(item_id)
        except Exception:
            pass
    return ans


def needs_director(ans: "TwinAnswer") -> bool:
    """True if the builder must WAIT for the real director rather than proceed
    on the twin's answer — the single predicate covering both director-reservation
    axes (one-way-door classifier OR the twin's own canon-based deferral)."""
    return ans.routed_to_director or ans.defers_to_director


def overturn(entry_id: str, corrected_answer: str, reason: str) -> int:
    """The director reverses a twin answer. This is not just a log entry --
    it AMENDS THE CANON (Law B's only permitted mechanism of change),
    versioned, with the reason recorded. Returns the new canon version."""
    old_version = current_canon_version()
    new_version = old_version + 1

    canon_text = CANON_PATH.read_text(encoding="utf-8")
    canon_text = re.sub(
        r"\*\*Version:\s*\d+\.\*\*",
        f"**Version: {new_version}.**",
        canon_text,
        count=1,
    )
    today = datetime.now(timezone.utc).date().isoformat()
    changelog_line = f"- v{new_version} ({today}): overturn on entry {entry_id} -- {reason}\n"
    canon_text = canon_text.rstrip("\n") + "\n" + changelog_line
    CANON_PATH.write_text(canon_text, encoding="utf-8")

    _append_jsonl(OVERTURNS_LOG_PATH, {
        "entry_id": entry_id,
        "corrected_answer": corrected_answer,
        "reason": reason,
        "overturned_at": datetime.now(timezone.utc).isoformat(),
        "old_canon_version": old_version,
        "new_canon_version": new_version,
    })
    return new_version


DIRECTOR_RESERVED_LEVEL = 3  # L3+ is the director's "this is real" ruling; the twin never ratifies it.


@dataclass(frozen=True)
class LevelRatificationDecision:
    atom_id: str
    level: int
    approved: bool
    routed_to_director: bool = False  # L3+ refused, or a one-way-door / canon deferral -> the director rules
    reason: str = ""
    twin_answer: str | None = None
    recorded: bool = False            # whether a director_twin LEVEL_UP_TWIN ledger entry was written


def ratify_routine_level(atom_id: str, level: int, evidence: str, *,
                         invoke_fn: InvokeFn | None = None,
                         record: bool = True) -> LevelRatificationDecision:
    """Standing-approver path for ROUTINE L1/L2 level ratifications, so routine levels stop queuing
    on the director (director console 2026-07-21: "run its live L1/L2 proof on the next eligible
    promotion ... L3 stays mine, R15 refusal test included").

    Two INDEPENDENT L3 refusal layers (defense in depth, R15):
      1. HERE — L3+ is refused before the twin is even consulted (returns routed_to_director).
      2. background.gate_authorization.is_valid_twin_level_up — a director_twin entry at L3+ is an
         INVALID authorization, so even if this guard were removed a twin L3 entry could not clear
         the LEVEL gate. record_twin_level_up also raises on L3+.

    For L1/L2 the twin adjudicates from canon; it also DEFERS (routes to the director) on any
    director-reserved dimension (values / R13 curriculum / one-way door). On an APPROVE verdict the
    ORCHESTRATOR records a director_twin ratification — the twin process itself stays a voice, not a
    hand (it answers via ask_twin's --tools= sandbox; THIS function writes the ledger on its answer).
    Fail-safe: an unparseable / non-APPROVE verdict is a REFUSAL — the twin never auto-approves on
    ambiguity."""
    if not isinstance(level, int) or level < 1:
        raise ValueError("level must be an integer >= 1")
    # Refusal layer 1: L3+ is director-reserved. The twin is not even asked.
    if level >= DIRECTOR_RESERVED_LEVEL:
        return LevelRatificationDecision(
            atom_id=atom_id, level=level, approved=False, routed_to_director=True,
            reason=(f"L{level} is director-reserved: the twin ratifies routine L1-"
                    f"L{gate_authorization.TWIN_LEVEL_CAP} only; L3+ is the director's "
                    "'this is real' ruling (canon)."))
    question = (
        f"ROUTINE LEVEL RATIFICATION request. Atom: {atom_id}. Requested level_current move to "
        f"L{level}. Evidence offered:\n{evidence}\n\n"
        "You are the standing approver for ROUTINE L1/L2 level moves ONLY. APPROVE iff BOTH hold: "
        "(a) the objective maturity bar for the requested level is met by the evidence (L1 = built in "
        "some real form; L2 = mechanically real AND its belief-vs-truth gap measured / its invariant "
        "mutation-tested), AND (b) the move carries NO director-reserved dimension -- no values "
        "decision, no curriculum/difficulty change (R13), no one-way door, nothing the canon marks "
        "his. If any director-reserved dimension is present, DEFER; if the evidence does not clearly "
        "meet the bar, REFUSE. End your answer with one extra line exactly in this form:\n"
        "'RATIFY_VERDICT: APPROVE' or 'RATIFY_VERDICT: REFUSE'.")
    ans = ask_twin(question, invoke_fn=invoke_fn)
    # A one-way-door route or a canon deferral means the director rules, not the twin.
    if ans.routed_to_director or ans.defers_to_director:
        return LevelRatificationDecision(
            atom_id=atom_id, level=level, approved=False, routed_to_director=True,
            reason=f"Twin routes to director (reserved dimension): {ans.reason or ans.answer}",
            twin_answer=ans.answer)
    vm = re.search(r"RATIFY_VERDICT:\s*(APPROVE|REFUSE)", ans.answer or "", re.IGNORECASE)
    approved = bool(vm) and vm.group(1).upper() == "APPROVE"  # fail-safe: ambiguous => refuse
    recorded = False
    if approved and record:
        gate_authorization.record_twin_level_up(
            atom_id, level,
            provenance=(f"DIRECTOR_TWIN routine L{level} ratification (standing approver per director "
                        f"console 2026-07-21; canon v{current_canon_version()}). Twin verdict: {ans.answer}"))
        recorded = True
    return LevelRatificationDecision(
        atom_id=atom_id, level=level, approved=approved, routed_to_director=False,
        reason=("twin approved from canon" if approved else "twin refused: routine bar not met"),
        twin_answer=ans.answer, recorded=recorded)


def fidelity_metric() -> dict:
    """Twin-vs-principal divergence: what fraction of twin answers the
    director overturns. High fidelity -> the director reviews less;
    rising divergence -> scrutiny rises (wired to the scrutiny dial as a
    follow-up, not built here -- this function is the number itself)."""
    twin_entries = _read_jsonl(TWIN_LOG_PATH)
    answered = [e for e in twin_entries if not e.get("routed_to_director")]
    routed = [e for e in twin_entries if e.get("routed_to_director")]
    overturns = _read_jsonl(OVERTURNS_LOG_PATH)
    overturned_ids = {o["entry_id"] for o in overturns}
    overturned_count = sum(1 for e in answered if e["entry_id"] in overturned_ids)

    return {
        "answered": len(answered),
        "routed_to_director": len(routed),
        "overturned": overturned_count,
        "overturn_rate": (overturned_count / len(answered)) if answered else None,
        "canon_version": current_canon_version(),
    }
