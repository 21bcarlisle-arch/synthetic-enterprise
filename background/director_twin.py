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
        "supports your answer."
    )
    invoke = invoke_fn or _default_invoke
    start = time.time()
    answer_text = invoke(prompt)
    latency = time.time() - start

    _append_jsonl(TWIN_LOG_PATH, {
        "entry_id": entry_id,
        "question": question,
        "context_pack": context_pack,
        "routed_to_director": False,
        "answer": answer_text,
        "latency_seconds": round(latency, 3),
        "canon_version": current_canon_version(),
    })
    return TwinAnswer(
        entry_id=entry_id, question=question, routed_to_director=False,
        answer=answer_text, reason="answered from canon", latency_seconds=latency,
    )


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
