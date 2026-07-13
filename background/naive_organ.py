"""NAIVE_ORGAN — the deliberately-amnesiac question/falsify organ
(2026-07-13, THE_NAIVE_ORGAN.md + the 2026-07-13 DIRECTOR AMENDMENT,
commit 0685dd26). Full buildable design: docs/design/NAIVE_ORGAN_DESIGN.md.

The STRUCTURAL INVERSE of background/director_twin.py. The twin isolates a
fresh Claude process so it can ONLY see the director's CANON (max fidelity to a
principal). The organ isolates a fresh Claude process so it can ONLY see the
*raw observable state* and the *bare claim* — deliberately denied the codebase,
CLAUDE.md, the map's prose rationales, the history, and every accumulated
"that's just how it is here." Same process mechanism (`claude -p
--model claude-opus-4-8 --tools=`, scratch cwd, no permission bypass); the
prompt payload is opposite. The amnesia is enforced at the process boundary,
not asked for in prose.

DIRECTOR AMENDMENT folded in (see design §8):
  ONE organ (no separate devil's advocate).
  TWO modes:  interrogate (question a claim) / falsify (break a plan/claim).
  THREE targets: (1) the SYSTEM's own claims/state (the 7 triggers);
                 (2) an ADVISOR-staged doc, FALSIFY'd BEFORE the agent acts;
                 (3) the DIRECTOR's falsifiable factual/strategic CLAIMS.
  THE LINE (non-negotiable): questions CLAIMS and PLANS from anyone, but NEVER
  PURPOSE — values / the fitness function are the director's and not falsifiable
  (same wall as canon Law B / R13). Enforced by is_purpose_claim() BEFORE any
  Opus call: a purpose claim is declined, not asked.

ANTI-CAPTURE (Law-B-shaped, same as the twin): the rubrics and thresholds are
fixed SOURCE CONSTANTS; the invocation payload NEVER includes prior
questions/answers or any hit/miss feedback; the organ never learns the house
norms (a naive agent that accumulates context stops being naive). Its hit-rate
is a diagnostic for US, never a training signal for IT.

Output = QUESTIONS / falsification-attempts, never fixes. The answer-writer
REJECTS an empty-evidence answer (mechanism, not exhortation): "no, that was
true because X" (X fetchable) closes a question; "that's just how it is" does
not.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ── observable-state sources (the organ's ENTIRE world; see design §1) ──
MATURITY_MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
RUN_HISTORY_PATH = PROJECT_DIR / "docs" / "observability" / "run_history.json"
RUN_INSIGHTS_PATH = PROJECT_DIR / "docs" / "observability" / "run_insights.json"
AGENT_STATUS_PATH = PROJECT_DIR / "docs" / "observability" / "agent_status.json"
LATEST_PATH = PROJECT_DIR / "docs" / "status" / "LATEST.md"
IDLE_COUNTER_PATH = PROJECT_DIR / "docs" / "observability" / ".supervisor_idle_turn_count.json"

# ── output ──
ORGAN_LOG_PATH = PROJECT_DIR / "docs" / "observability" / "naive_organ_log.jsonl"

CLAUDE_BIN = Path("/home/rich/.nvm/versions/node/v24.16.0/bin/claude")
# OPUS-tier, non-negotiable (MODEL_SELECTION_POLICY: a good naive question is
# JUDGMENT, the same class as the twin — a cheap model asks a bland question and
# the organ is worthless). The DETECTORS are free Python; only the
# question-formulation spends Opus.
ORGAN_MODEL = "claude-opus-4-8"

InvokeFn = Callable[[str], str]

# ── modes + targets (director amendment) ──
MODE_INTERROGATE = "interrogate"
MODE_FALSIFY = "falsify"
TARGET_SYSTEM = "system"
TARGET_ADVISOR = "advisor"
TARGET_DIRECTOR = "director"

# ── thresholds: FIXED SOURCE CONSTANTS, never tuned by outcomes (anti-capture) ──
FLAT_METRIC_EPSILON_GBP = 1.0     # T1/T5: max-min < ε over the window == "flat"
FLAT_METRIC_WINDOW_K = 3          # T1: number of trailing runs
IDLE_TURN_THRESHOLD = 5           # T1: idle turns while atoms remain below target
SUSTAINED_BUCKET_FRACTION = 0.60  # T5: one work-category dominates
SUSTAINED_WINDOW_M = 20           # T5: trailing commits classified
FIXCLASS_MIN_COUNT = 3            # T7: same fix-class applied >= N times
FIXCLASS_WINDOW_W = 40            # T7: trailing commits fingerprinted
STALE_ANSWER_HOURS = 24           # a question open beyond this is re-surfaced

# ── THE GOAL: a single fixed sentence, passed as a literal constant, NOT read
# from CLAUDE.md (the amnesia depends on this — see design §2.1). ──
GOAL_CONST = (
    "The business's north star: maximise the simulated UK energy supplier's "
    "enterprise value under survival constraints (it must never enter "
    "administration)."
)

# ── THE RUBRICS: fixed constants, one per mode. Never conditioned on prior
# answers or on which questions were 'unhelpful' (Law-B no-learn). ──
_RUBRIC_HEADER = (
    "You are a NAIVE OUTSIDER. You have never seen this system's code, its "
    "documentation, its history, or its reasoning. Everything you know is in "
    "this prompt. Do NOT assume the claim below is true; do NOT assume it is "
    "false. You have no tools and cannot read anything — reason only over the "
    "text given.\n"
)
RUBRIC_INTERROGATE = (
    _RUBRIC_HEADER
    + "MODE: INTERROGATE. Ask the SINGLE sharpest question a smart outsider "
    "would ask about the contradiction / flatness / claim below, given only the "
    "goal and the observable state. Output ONLY the question (one or two "
    "sentences), never a fix, never an answer, never advice."
)
RUBRIC_FALSIFY = (
    _RUBRIC_HEADER
    + "MODE: FALSIFY. Try to BREAK the plan/claim below. List the load-bearing "
    "assumptions it depends on, and the concrete conditions under which it would "
    "FAIL or be false. Output ONLY falsification attempts / the assumptions that "
    "must hold — never a fix, never an endorsement, never advice on how to "
    "proceed."
)


def rubric_for_mode(mode: str) -> str:
    if mode == MODE_FALSIFY:
        return RUBRIC_FALSIFY
    return RUBRIC_INTERROGATE


# ── THE LINE: never question PURPOSE (values / fitness function). A code gate,
# run BEFORE any Opus call — enforced, not exhorted. ──
_PURPOSE_TOKENS = [
    "fitness function", "values decision", "what the company is for",
    "what the company should be for", "what we are for", "north star",
    "the mission", "company's purpose", "the purpose of the company",
    "should the company optimise", "should the company optimize",
    "should the business optimise", "should the business optimize",
    "what should the company value", "the epoch-4 fitness",
    "what the company should value", "what matters most to the company",
]


def is_purpose_claim(text: str) -> bool:
    """True if the claim is about PURPOSE/values/the fitness function — which
    the organ NEVER questions (THE LINE; same wall as canon Law B / R13). The
    organ may ASK 'is the map exhausted?' but never 'should this company
    optimise for EV?' — the latter is the director's alone."""
    low = (text or "").lower()
    return any(tok in low for tok in _PURPOSE_TOKENS)


# ── the isolation mechanism (inverse of director_twin._default_invoke) ──
def _default_invoke(prompt: str) -> str:
    """Port of director_twin._default_invoke's process defences VERBATIM — only
    the prompt payload differs (the twin embeds the whole canon; the organ
    embeds only goal + raw state + the bare claim + rubric). Three defences,
    each a PROCESS-level guarantee proven by the twin's real failed-write test:
      1. no --dangerously-skip-permissions -> default-deny; non-interactive
         -p mode cannot satisfy a permission prompt, so any tool call fails
         closed.
      2. --tools= (single argv token) -> every tool disabled at the CLI level.
      3. cwd = scratch tempdir OUTSIDE the repo -> even a determined attempt to
         read CLAUDE.md/docs/ finds no repo at its cwd.
    The amnesia is thus structural: the ONLY context the process can have is the
    prompt string built here from four explicit args."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="naive_organ_scratch_") as scratch_dir:
        result = subprocess.run(
            [str(CLAUDE_BIN), "-p", "--model", ORGAN_MODEL, "--tools=", prompt],
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


# ── the payload: a PURE function of four strings (design §2.2 / PA-3) ──
def build_prompt(goal: str, evidence_pack: str, claim: str, rubric: str) -> str:
    """The organ's ENTIRE world = these four arguments. Nothing sourced from
    disk. A future edit that 'helpfully' pastes CLAUDE.md in here would silently
    kill the amnesia — PA-3 (test_naive_organ.py) guards against exactly that by
    asserting this function is closed over its arguments."""
    return (
        f"GOAL (the only context you are given about what this system is for):\n"
        f"{goal}\n\n"
        f"OBSERVABLE STATE (raw numbers/rows, chosen by a mechanical detector):\n"
        f"{evidence_pack}\n\n"
        f"THE CLAIM / PLAN UNDER EXAMINATION:\n"
        f"{claim}\n\n"
        f"{rubric}\n"
    )


# ── Trigger dataclass ──
@dataclass(frozen=True)
class Trigger:
    trigger_id: str
    mode: str
    claim_text: str
    evidence_refs: tuple[str, ...]
    observed_value: dict
    fire_reason: str
    target: str = TARGET_SYSTEM

    def evidence_pack(self) -> str:
        return json.dumps(self.observed_value, sort_keys=True, indent=1)


# ── open-atom predicate (independent recomputation; matches supervisor.py's
# _maturity_map_draw_concurrent open-atom predicate, computed here from the raw
# YAML so a bug in the draw cannot silence the organ — design T2) ──
def open_atoms(atoms: list) -> list[dict]:
    out = []
    for a in atoms or []:
        if not isinstance(a, dict):
            continue
        lc, lt = a.get("level_current"), a.get("level_target")
        if lc is None or lt is None:
            continue
        if lc < lt:
            out.append(a)
    return out


def _normalise_claim(text: str) -> str:
    """Strip run-hashes/numbers/dates for fingerprinting (T7 + debounce). Same
    normaliser shape for both, so a reworded-but-identical claim does not
    re-fire (design BQ-4)."""
    low = (text or "").lower()
    low = re.sub(r"\b[0-9a-f]{7,40}\b", "", low)      # git hashes
    low = re.sub(r"\d{4}-\d{2}-\d{2}t?[\d:.+z]*", "", low)  # iso dates
    low = re.sub(r"[\d,]+", "", low)                  # numbers
    low = re.sub(r"\s+", " ", low).strip()
    return low


# ── State loader: reads the observable surfaces. Detectors take an explicit
# state dict so they are trivially testable (feed a dict, no disk). ──
def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_state(*, gitlog_window: str = "3 days ago") -> dict:
    """Assemble the organ's observable world from disk + git. Test code builds
    the dict directly and never calls this."""
    runhist = _load_json(RUN_HISTORY_PATH, [])
    insights = _load_json(RUN_INSIGHTS_PATH, {})
    agent_status = _load_json(AGENT_STATUS_PATH, {})
    idle_state = _load_json(IDLE_COUNTER_PATH, {})
    try:
        import yaml
        atoms = yaml.safe_load(MATURITY_MAP_PATH.read_text(encoding="utf-8"))
    except Exception:
        atoms = []
    claims_text = ""
    try:
        claims_text = LATEST_PATH.read_text(encoding="utf-8")
    except Exception:
        pass
    gitlog_subjects: list[str] = []
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate", f"--since={gitlog_window}"],
            cwd=PROJECT_DIR, capture_output=True, text=True, timeout=30,
        )
        gitlog_subjects = [ln.split(" ", 1)[1] for ln in r.stdout.splitlines() if " " in ln]
    except Exception:
        pass
    return {
        "runhist": runhist if isinstance(runhist, list) else [],
        "insights": insights if isinstance(insights, dict) else {},
        "agent_status": agent_status if isinstance(agent_status, dict) else {},
        "atoms": atoms if isinstance(atoms, list) else [],
        "claims_text": claims_text,
        "gitlog_subjects": gitlog_subjects,
        "idle_count": (idle_state or {}).get("count", 0) if isinstance(idle_state, dict) else 0,
    }


# ── helpers over state ──
def _net_margins(runhist: list, k: int) -> list[float]:
    vals = []
    for entry in (runhist or [])[-k:]:
        v = entry.get("net_margin_gbp")
        if v is None:
            hm = entry.get("headline_metrics", {})
            v = (hm.get("financial", {}) or {}).get("net_margin_gbp")
        if v is not None:
            vals.append(float(v))
    return vals


def _statuses_all_healthy(agent_status: dict) -> bool:
    agents = (agent_status or {}).get("agents", [])
    if not agents:
        return False
    for a in agents:
        if a.get("anomaly") not in (None, "", "null"):
            return False
        if a.get("status") not in ("idle", "ok", "running"):
            return False
    return True


# ── the seven detectors (design §1). Each: pure fn state -> list[Trigger]. ──
_TERMINAL_TOKENS = [
    "exhausted", "nothing to do", "nothing left", "no candidates",
    "no drawable", "no drawable atoms", "complete", "all done",
    "map exhausted", "nothing to draw",
]
_INHERENCE_TOKENS = [
    "physics", "inherent", "inherently", "unavoidable", "by design",
    "cannot be parallelised", "cannot be parallelized", "must be narrow",
    "one at a time", "can't be", "impossible to", "no way to",
]
_FIRST_PRINCIPLES_TOKENS = [
    "from first principles", "must be", "the only way", "necessarily",
    "there is no", "the fundamental",
]
_FAST_FIELD_NOUNS = [
    "claude code", "worktree", "subagent", "model", "opus", "sonnet",
    "haiku", "mcp", "hook", "context window", "agent sdk", "token", "api",
]
_CITATION_TOKENS = [
    "per docs", "published", "release notes", "changelog",
    "verified against", "https://", "checked",
]
_FIXCLASS_REGEXES = [
    (r"idle[- ]?(?:hole|turn|variant)", "idle_variant"),
    (r"\[?action needed\]?", "action_needed"),
    (r"escalat", "escalation"),
    (r"false (?:completion|claim)", "false_completion"),
    (r"stale (?:process|code|site)", "stale_artifact"),
    (r"two[- ]?strike|\br3\b", "two_strike"),
    (r"refill|draw", "refill_draw"),
]
_BUCKET_KEYWORDS = {
    "harness": ["background/", "supervisor", "daemon", "digest", "ntfy",
                "idle", "watchdog", "harness"],
    "company": ["company/", "saas/", "billing", "pricing", "churn"],
    "site": ["site/", "docs/shadow", "dashboard"],
    "sim": ["sim/", "simulation/"],
}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.\n]", text or "") if s.strip()]


def detect_t1(state: dict) -> list[Trigger]:
    """Flat metric while the system reports healthy (real catch: 3h idle turns,
    flat net=£1,505,286, status 'healthy')."""
    runhist = state.get("runhist", [])
    vals = _net_margins(runhist, FLAT_METRIC_WINDOW_K)
    idle_count = state.get("idle_count", 0)
    open_ct = len(open_atoms(state.get("atoms", [])))
    fires = []
    flat = len(vals) >= FLAT_METRIC_WINDOW_K and (max(vals) - min(vals)) < FLAT_METRIC_EPSILON_GBP
    if flat and _statuses_all_healthy(state.get("agent_status", {})):
        fires.append(Trigger(
            trigger_id="T1_flat_metric_healthy",
            mode=MODE_INTERROGATE,
            claim_text="Every status reads healthy/nominal.",
            evidence_refs=("run_history.json", "agent_status.json"),
            observed_value={"net_margins_last_k": vals, "epsilon": FLAT_METRIC_EPSILON_GBP,
                            "all_statuses_healthy": True},
            fire_reason=f"net margin flat across last {len(vals)} runs while all statuses healthy",
        ))
    if idle_count > IDLE_TURN_THRESHOLD and open_ct > 0:
        fires.append(Trigger(
            trigger_id="T1_idle_turns_with_open_atoms",
            mode=MODE_INTERROGATE,
            claim_text=f"The supervisor has taken {idle_count} idle turns.",
            evidence_refs=(".supervisor_idle_turn_count.json", "maturity_map.yaml"),
            observed_value={"idle_count": idle_count, "open_atoms": open_ct},
            fire_reason=f"{idle_count} idle turns while {open_ct} atoms remain below target",
        ))
    return fires


def detect_t2(state: dict) -> list[Trigger]:
    """Terminal-state claim — MUST independently check raw data (real catch:
    'map exhausted' with 31 open atoms)."""
    claims = state.get("claims_text", "")
    low = claims.lower()
    hit = next((t for t in _TERMINAL_TOKENS if t in low), None)
    if hit is None:
        return []
    opens = open_atoms(state.get("atoms", []))
    if len(opens) == 0:
        return []
    return [Trigger(
        trigger_id="T2_terminal_state",
        mode=MODE_INTERROGATE,
        claim_text=f"A live claim asserts '{hit}'.",
        evidence_refs=("maturity_map.yaml",),
        observed_value={
            "terminal_token": hit,
            "open_atoms": len(opens),
            "open_ids": [a.get("id") for a in opens][:40],
        },
        fire_reason=f"terminal claim '{hit}' while {len(opens)} atoms are below target",
    )]


def detect_t3(state: dict) -> list[Trigger]:
    """Inherence claim — fact, or unchecked assumption? (real catch: 'build must
    be narrow' — worktrees existed all along)."""
    fires = []
    surface = state.get("claims_text", "") + "\n" + "\n".join(state.get("gitlog_subjects", []))
    for sent in _sentences(surface):
        low = sent.lower()
        tok = next((t for t in _INHERENCE_TOKENS if t in low), None)
        if tok:
            fires.append(Trigger(
                trigger_id="T3_inherence",
                mode=MODE_INTERROGATE,
                claim_text=sent,
                evidence_refs=("LATEST.md/gitlog",),
                observed_value={"inherence_token": tok, "sentence": sent},
                fire_reason=f"inherence token '{tok}' asserted as fact",
            ))
    return _dedupe_by_claim(fires)


def detect_t4(state: dict) -> list[Trigger]:
    """First-principles claim about a fast-moving external field, unchecked
    (real catch: six weeks blind to worktrees)."""
    fires = []
    entries = list(state.get("gitlog_subjects", [])) + _sentences(state.get("claims_text", ""))
    for entry in entries:
        low = entry.lower()
        has_fp = any(t in low for t in _FIRST_PRINCIPLES_TOKENS)
        has_field = any(n in low for n in _FAST_FIELD_NOUNS)
        has_citation = any(c in low for c in _CITATION_TOKENS)
        if has_fp and has_field and not has_citation:
            fires.append(Trigger(
                trigger_id="T4_unchecked_first_principles",
                mode=MODE_INTERROGATE,
                claim_text=entry,
                evidence_refs=("gitlog/LATEST.md",),
                observed_value={"entry": entry, "cited_external_check": False},
                fire_reason="first-principles claim about a fast field with no cited external check",
            ))
    return _dedupe_by_claim(fires)


def detect_t5(state: dict) -> list[Trigger]:
    """Sustained work in one category while the goal metric is flat (the
    treadmill; real catch: harness-grooming vs company backlog)."""
    subjects = state.get("gitlog_subjects", [])[:SUSTAINED_WINDOW_M]
    if not subjects:
        return []
    counts = {b: 0 for b in _BUCKET_KEYWORDS}
    classified = 0
    for s in subjects:
        low = s.lower()
        for bucket, kws in _BUCKET_KEYWORDS.items():
            if any(kw in low for kw in kws):
                counts[bucket] += 1
                classified += 1
                break
    if classified == 0:
        return []
    top_bucket = max(counts, key=counts.get)
    frac = counts[top_bucket] / len(subjects)
    vals = _net_margins(state.get("runhist", []), FLAT_METRIC_WINDOW_K)
    flat = len(vals) >= 2 and (max(vals) - min(vals)) < FLAT_METRIC_EPSILON_GBP
    if frac >= SUSTAINED_BUCKET_FRACTION and flat:
        return [Trigger(
            trigger_id="T5_sustained_work_flat_goal",
            mode=MODE_INTERROGATE,
            claim_text=f"{counts[top_bucket]} of the last {len(subjects)} commits are '{top_bucket}' work.",
            evidence_refs=("gitlog", "run_history.json"),
            observed_value={"bucket": top_bucket, "bucket_count": counts[top_bucket],
                            "window": len(subjects), "fraction": round(frac, 2),
                            "goal_metric_flat": True},
            fire_reason=f"{top_bucket} work is {frac:.0%} of commits while the goal metric is flat",
        )]
    return []


# T6 claim-extraction table: regex over the claims surface -> recompute over
# the data surface, fire on mismatch. This table IS the trigger; adding a row is
# the supported way to widen it (design §T6).
def _t6_rows(state: dict) -> list[tuple]:
    atoms = state.get("atoms", [])
    open_ct = len(open_atoms(atoms))
    runhist = state.get("runhist", [])
    latest_net = _net_margins(runhist, 1)
    latest_net_val = round(latest_net[0]) if latest_net else None
    return [
        (r"(\d[\d,]*)\s+atoms?\s+below\s+target", lambda m: int(m.group(1).replace(",", "")), open_ct, "atoms_below_target"),
        (r"no drawable atoms|nothing to draw", lambda m: 0, open_ct, "drawable_atoms_zero"),
        (r"net(?:\s+margin)?[^\d]{0,8}£?([\d,]+)", lambda m: int(m.group(1).replace(",", "")), latest_net_val, "net_margin"),
    ]


def detect_t6(state: dict) -> list[Trigger]:
    """Claim-vs-data contradiction on any observable surface (real catch: 'no
    drawable atoms' vs 30 idle atoms — the tautology)."""
    fires = []
    claims = state.get("claims_text", "")
    for pattern, extract, computed, name in _t6_rows(state):
        if computed is None:
            continue
        m = re.search(pattern, claims, re.IGNORECASE)
        if not m:
            continue
        try:
            claimed = extract(m)
        except Exception:
            continue
        mismatch = (abs(claimed - computed) > 1) if name == "net_margin" else (claimed != computed)
        if mismatch:
            fires.append(Trigger(
                trigger_id=f"T6_claim_vs_data_{name}",
                mode=MODE_INTERROGATE,
                claim_text=m.group(0),
                evidence_refs=("LATEST.md", "maturity_map.yaml/run_history.json"),
                observed_value={"claimed": claimed, "computed": computed, "field": name},
                fire_reason=f"{name}: claim says {claimed}, raw data says {computed}",
            ))
    return fires


def detect_t7(state: dict) -> list[Trigger]:
    """Same class of fix applied N times — is the class defined correctly?
    (real catch: 5 [ACTION NEEDED] patches / '9th idle variant')."""
    subjects = state.get("gitlog_subjects", [])[:FIXCLASS_WINDOW_W]
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for s in subjects:
        low = s.lower()
        for pattern, cls in _FIXCLASS_REGEXES:
            if re.search(pattern, low):
                counts[cls] = counts.get(cls, 0) + 1
                examples.setdefault(cls, []).append(s)
    fires = []
    for cls, n in counts.items():
        if n >= FIXCLASS_MIN_COUNT:
            fires.append(Trigger(
                trigger_id=f"T7_repeated_fix_class_{cls}",
                mode=MODE_INTERROGATE,
                claim_text=f"The '{cls}' fix-class has been applied {n} times.",
                evidence_refs=("gitlog",),
                observed_value={"fix_class": cls, "count": n, "examples": examples[cls][:5]},
                fire_reason=f"fix-class '{cls}' applied {n} times (>= {FIXCLASS_MIN_COUNT})",
            ))
    return fires


ALL_DETECTORS = [detect_t1, detect_t2, detect_t3, detect_t4, detect_t5, detect_t6, detect_t7]


def _dedupe_by_claim(triggers: list[Trigger]) -> list[Trigger]:
    seen = set()
    out = []
    for t in triggers:
        key = (t.trigger_id, _normalise_claim(t.claim_text))
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def run_detectors(state: dict) -> list[Trigger]:
    """Run all seven detectors over the observable state; return every fired
    trigger. The detectors decide WHEN to ask; the amnesiac Opus process decides
    WHAT to ask (design §1)."""
    fired: list[Trigger] = []
    for det in ALL_DETECTORS:
        try:
            fired.extend(det(state))
        except Exception:
            continue
    return fired


# ── debounce: a (trigger_id, normalised-claim) already OPEN is not re-asked ──
def _open_fingerprints(log_path: Path) -> set:
    out = set()
    for e in _read_jsonl(log_path):
        if e.get("verdict") == "open":
            out.add((e.get("trigger_id"), _normalise_claim(
                (e.get("fired_on", {}) or {}).get("claim", ""))))
    return out


# ── ask_organ: build the closed prompt, call the isolated Opus process, write
# the log record. THE LINE gate runs BEFORE any invocation. ──
def ask_organ(trigger: Trigger, *, invoke_fn: InvokeFn | None = None,
              log_path: Path | None = None) -> dict | None:
    log_path = log_path or ORGAN_LOG_PATH

    # THE LINE — never question PURPOSE. A code gate, before any Opus spend.
    if is_purpose_claim(trigger.claim_text):
        entry = {
            "entry_id": datetime.now(timezone.utc).isoformat(),
            "trigger_id": trigger.trigger_id,
            "mode": trigger.mode,
            "target": trigger.target,
            "fired_on": {"claim": trigger.claim_text,
                         "evidence_refs": list(trigger.evidence_refs),
                         "observed_value": trigger.observed_value},
            "question": None,
            "model": ORGAN_MODEL,
            "asked_at": None,
            "answer": None,
            "answered_at": None,
            "answer_evidence": None,
            "verdict": "declined_purpose",
            "declined_reason": "THE LINE: purpose/values/fitness is the "
                               "director's and is not falsifiable (Law B / R13).",
        }
        _append_jsonl(log_path, entry)
        return entry

    # debounce: do not re-ask an already-open (trigger, claim)
    fp = (trigger.trigger_id, _normalise_claim(trigger.claim_text))
    if fp in _open_fingerprints(log_path):
        return None

    prompt = build_prompt(
        GOAL_CONST, trigger.evidence_pack(), trigger.claim_text,
        rubric_for_mode(trigger.mode),
    )
    invoke = invoke_fn or _default_invoke
    asked_at = datetime.now(timezone.utc).isoformat()
    question = invoke(prompt)

    entry = {
        "entry_id": asked_at,
        "trigger_id": trigger.trigger_id,
        "mode": trigger.mode,
        "target": trigger.target,
        "fired_on": {"claim": trigger.claim_text,
                     "evidence_refs": list(trigger.evidence_refs),
                     "observed_value": trigger.observed_value,
                     "fire_reason": trigger.fire_reason},
        "question": question,
        "model": ORGAN_MODEL,
        "asked_at": asked_at,
        "answer": None,
        "answered_at": None,
        "answer_evidence": None,
        "verdict": "open",
    }
    _append_jsonl(log_path, entry)
    return entry


def run_system_organ(state: dict, *, invoke_fn: InvokeFn | None = None,
                     log_path: Path | None = None,
                     max_new: int | None = None) -> list[dict]:
    """TARGET 1 — the SYSTEM. Run detectors, ask the organ once per fired
    trigger (with debounce). Returns the records written.

    `max_new` caps the number of NEW records produced in one pass (bounds Opus
    latency on the live publish path; any un-asked triggers surface next cycle).
    None = no cap (the test/analysis default)."""
    written = []
    for trig in run_detectors(state):
        if max_new is not None and len(written) >= max_new:
            break
        rec = ask_organ(trig, invoke_fn=invoke_fn, log_path=log_path)
        if rec is not None:
            written.append(rec)
    return written


# ── TARGET 2 — the ADVISOR. FALSIFY an advisor-staged doc BEFORE the agent acts
# on it. The agent may cite the result to push back on the advisor (director
# amendment). ──
def falsify_advisor_doc(doc_ref: str, doc_text: str, *,
                        invoke_fn: InvokeFn | None = None,
                        log_path: Path | None = None) -> dict | None:
    """Run a FALSIFY pass on an advisor-staged doc. The advisor is the
    least-protected seat (writes plans AND reviews outcomes, no evaluator of its
    own), so its plans get broken BEFORE action, not after. Output = the
    assumptions that must hold + conditions under which the plan fails — the
    agent may cite this to push back, and should."""
    trig = Trigger(
        trigger_id="ADVISOR_DOC_FALSIFY",
        mode=MODE_FALSIFY,
        claim_text=doc_text,
        evidence_refs=(doc_ref,),
        observed_value={"doc_ref": doc_ref, "chars": len(doc_text or "")},
        fire_reason=f"advisor-staged doc {doc_ref} falsified before the agent acts on it",
        target=TARGET_ADVISOR,
    )
    return ask_organ(trig, invoke_fn=invoke_fn, log_path=log_path)


# ── TARGET 3 — the DIRECTOR. INTERROGATE a falsifiable factual/strategic claim.
# THE LINE still applies (ask_organ declines a purpose claim). ──
def interrogate_claim(claim_text: str, *, source: str = TARGET_DIRECTOR,
                      evidence_refs: tuple = (), observed_value: dict | None = None,
                      invoke_fn: InvokeFn | None = None,
                      log_path: Path | None = None) -> dict | None:
    """INTERROGATE a factual/strategic claim from the director (or any source).
    Questions the claim's TRUTH, never its purpose — ask_organ's THE LINE gate
    declines a values/fitness claim before any Opus call."""
    trig = Trigger(
        trigger_id=f"CLAIM_INTERROGATE_{source}",
        mode=MODE_INTERROGATE,
        claim_text=claim_text,
        evidence_refs=tuple(evidence_refs),
        observed_value=observed_value or {},
        fire_reason=f"{source} factual/strategic claim interrogated",
        target=source,
    )
    return ask_organ(trig, invoke_fn=invoke_fn, log_path=log_path)


# ── the answer / verdict API ──
class EmptyEvidenceRejected(ValueError):
    """The answer-writer REJECTS an empty-evidence answer — the discipline is a
    mechanism, not an exhortation (MAKE_IT_STICK). 'no, that was true because X'
    (X a fetchable ref) closes a question; 'that's just how it is' does not."""


def answer_question(entry_id: str, answer: str, evidence_refs,
                    *, log_path: Path | None = None) -> dict:
    """Answer an open organ question. REJECTS an empty-evidence answer by
    raising EmptyEvidenceRejected — the shape enforces 'answer WITH EVIDENCE'
    structurally."""
    log_path = log_path or ORGAN_LOG_PATH
    refs = [r for r in (evidence_refs or []) if str(r).strip()]
    if not refs or not (answer or "").strip():
        raise EmptyEvidenceRejected(
            "an organ question is closed only by an answer WITH fetchable "
            "evidence refs — 'that's just how it is' is rejected."
        )
    entries = _read_jsonl(log_path)
    found = None
    for e in entries:
        if e.get("entry_id") == entry_id:
            found = e
            break
    if found is None:
        raise KeyError(f"no organ question with entry_id {entry_id}")
    found["answer"] = answer
    found["answer_evidence"] = refs
    found["answered_at"] = datetime.now(timezone.utc).isoformat()
    found["verdict"] = "answered_with_evidence"
    _rewrite_log(log_path, entries)
    return found


def mark_verdict(entry_id: str, verdict: str, *, log_path: Path | None = None) -> dict:
    """Mark a HIT (question surfaced a real problem) or MISS (claim legitimately
    true). Diagnostic for US — NEVER fed back to tune the detectors/rubric."""
    if verdict not in ("hit", "miss", "withdrawn"):
        raise ValueError(f"verdict must be hit|miss|withdrawn, got {verdict!r}")
    log_path = log_path or ORGAN_LOG_PATH
    entries = _read_jsonl(log_path)
    for e in entries:
        if e.get("entry_id") == entry_id:
            e["verdict"] = verdict
            _rewrite_log(log_path, entries)
            return e
    raise KeyError(f"no organ question with entry_id {entry_id}")


def _rewrite_log(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, sort_keys=True) + "\n")


def open_questions(*, log_path: Path | None = None) -> list[dict]:
    log_path = log_path or ORGAN_LOG_PATH
    return [e for e in _read_jsonl(log_path) if e.get("verdict") == "open"]


def stale_questions(*, hours: int = STALE_ANSWER_HOURS, log_path: Path | None = None) -> list[dict]:
    """Open questions past the staleness bound — a SELF-finding, so per
    SELF_INTERRUPT_DISCIPLINE it QUEUEs (surfaced in the digest), it does not
    interrupt unless it also trips the one-way-door / genuinely-blocked test."""
    cutoff = time.time() - hours * 3600
    out = []
    for e in open_questions(log_path=log_path):
        try:
            ts = datetime.fromisoformat(e["asked_at"]).timestamp()
        except Exception:
            continue
        if ts < cutoff:
            out.append(e)
    return out


def hit_rate(*, log_path: Path | None = None) -> dict:
    """Diagnostic for US (judge whether the organ earns its Opus spend) — read
    at digest/epoch boundaries, NEVER fed back to tune anything (anti-capture)."""
    entries = _read_jsonl(log_path or ORGAN_LOG_PATH)
    hits = sum(1 for e in entries if e.get("verdict") == "hit")
    misses = sum(1 for e in entries if e.get("verdict") == "miss")
    return {
        "hits": hits,
        "misses": misses,
        "hit_rate": (hits / (hits + misses)) if (hits + misses) else None,
        "open": sum(1 for e in entries if e.get("verdict") == "open"),
        "declined_purpose": sum(1 for e in entries if e.get("verdict") == "declined_purpose"),
    }


# ── THE LIVE HOOK (L2): the organ is called from the observability/publish cycle
# (background/process_run_complete.py::run_naive_organ_step). This is what makes
# the organ FIRE ON REAL CONDITIONS instead of staying dormant. It loads the real
# observable world, runs the 7 SYSTEM detectors, and asks the amnesiac Opus
# process once per NEW fired contradiction (debounced). Output = QUESTIONS to the
# log + the digest section below, NEVER actions (safe by construction —
# SELF_INTERRUPT_DISCIPLINE QUEUE). ──
def run_organ_cycle(*, invoke_fn: InvokeFn | None = None,
                    log_path: Path | None = None,
                    max_new: int | None = 3,
                    gitlog_window: str = "3 days ago") -> list[dict]:
    """Assemble the observable world from disk (load_state), run the SYSTEM
    organ, and return the records written this cycle. `max_new` bounds Opus
    latency on the publish path (default 3; un-asked triggers surface next
    cycle, still debounced). This is the single entry point the live pipeline
    calls — tests inject `invoke_fn`/`log_path` so no real Opus is spawned."""
    state = load_state(gitlog_window=gitlog_window)
    return run_system_organ(state, invoke_fn=invoke_fn, log_path=log_path,
                            max_new=max_new)


def render_digest_section(*, log_path: Path | None = None,
                          hours: int = STALE_ANSWER_HOURS) -> str:
    """The DIGEST sink (design §3.2 sink 1). Render the 'NAIVE ORGAN asks:'
    section from the OPEN questions in the log; '' when none are open. An open
    question past the staleness bound is marked [unanswered >Nh] (the
    action_needed daily-reping shape) — a SELF-finding that QUEUEs, never
    interrupts (SELF_INTERRUPT_DISCIPLINE)."""
    log_path = log_path or ORGAN_LOG_PATH
    opens = open_questions(log_path=log_path)
    if not opens:
        return ""
    stale_ids = {e.get("entry_id") for e in stale_questions(hours=hours, log_path=log_path)}
    lines = ["**NAIVE ORGAN asks:** — open questions; answer WITH EVIDENCE "
             "(`answer_question`) or mark a miss. Never actions."]
    for e in opens:
        q = (e.get("question") or "").strip().replace("\n", " ")
        tid = e.get("trigger_id", "?")
        stale = " [unanswered >{}h]".format(hours) if e.get("entry_id") in stale_ids else ""
        lines.append("- ({}){} {}".format(tid, stale, q))
    return "\n".join(lines)


# ── TARGET 2 entry point, made callable (not dormant). Read an advisor-staged
# doc from disk and FALSIFY it BEFORE the agent acts. Invoked by the agent per
# the staging protocol, or from the CLI:
#   python3 -m background.naive_organ falsify docs/staging/SOME_DOC.md
def falsify_staged_doc(doc_path, *, invoke_fn: InvokeFn | None = None,
                       log_path: Path | None = None) -> dict | None:
    """Run a FALSIFY pass on an advisor-staged doc read from disk. Returns the
    log record (assumptions that must hold + conditions under which the plan
    fails) — the agent may cite it to push back on the advisor, and should."""
    p = Path(doc_path)
    text = p.read_text(encoding="utf-8")
    return falsify_advisor_doc(str(p), text, invoke_fn=invoke_fn, log_path=log_path)


def _main(argv: list[str]) -> int:
    """CLI so the organ is real and callable from a shell, not only importable.
      python3 -m background.naive_organ cycle            # run the SYSTEM organ now
      python3 -m background.naive_organ falsify <path>   # FALSIFY a staged doc
    """
    if len(argv) >= 2 and argv[1] == "cycle":
        written = run_organ_cycle()
        print("naive organ cycle: {} new question(s) asked".format(len(written)))
        section = render_digest_section()
        if section:
            print("\n" + section)
        return 0
    if len(argv) >= 3 and argv[1] == "falsify":
        rec = falsify_staged_doc(argv[2])
        print(json.dumps(rec, indent=1, sort_keys=True) if rec else "no record (debounced or empty)")
        return 0
    print("usage: python3 -m background.naive_organ [cycle | falsify <doc_path>]")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(_main(sys.argv))
