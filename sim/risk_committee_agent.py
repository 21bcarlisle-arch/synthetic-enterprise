"""Risk committee LLM agent — the Context Handshake decision layer.

This module is the LLM side of the Context Handshake. It is invoked only when
sim/risk_committee.py's RiskCommitteeMonitor.update() returns True (a threshold
breach). It reads the context summary written by the monitor, reasons about the
right hedge_fraction adjustment for the flagged customer(s), writes its decision
back to the simulation state, and logs its reasoning.

Architecture contract (the Context Handshake):
  1. The Python engine detects a threshold breach (risk_committee.py)
  2. The engine writes the context summary to docs/context-handshake-latest.md
  3. THIS module reads the summary and takes a decision (see RETIRED below)
  4. The decision (new hedge_fraction per customer) is returned to the engine
  5. The engine updates its simulation state and continues the inner loop
  6. THIS module logs the reasoning in docs/observability/risk-committee-log.md
  7. No further LLM activity until the next threshold breach

The LLM agent:
  - Never decreases hedge_fraction (it acts only when risk is elevated)
  - Adjusts exactly one lever per wake-up (hedge_fraction for the flagged customer(s))
  - Makes a minimum adjustment of +0.10 and a maximum of +0.30 per wake-up
  - Justifies its decision in plain English
  - Returns to sleep immediately after adjusting

Routing — local Ollama, not the frontier (decision reversed 2026-06-12):
  Earlier versions of this module called the Anthropic frontier API directly
  and were marked "frontier model only — MUST NOT be delegated to a local
  model", on the basis that this is the one place a live LLM agent makes a
  real-time decision affecting the simulation's financial state. In practice
  this left the Context Handshake permanently unable to fire: this
  environment has no ANTHROPIC_API_KEY, so every wake-up would fail with an
  auth error (see PHASE_2b_SUMMARY.md open questions).

  Rich's call: the simulation is synthetic — there is no portfolio, customer,
  or money at stake outside the simulation's own bookkeeping, so there is no
  justification for an autonomous frontier API call (with its associated cost
  and external dependency) during a simulation run. The risk committee agent
  is therefore routed through local Ollama like every other subagent in this
  project, via the same Ollama HTTP API used by tools/delegate_ollama.py. The
  validation logic below (no decrease, +0.10..+0.30 clamp) is the actual
  safety boundary regardless of which model proposes the adjustment, so this
  change does not weaken the guardrails on what the agent can do — only on
  which model is allowed to propose it.

RETIRED 2026-09-27: the live (non-fast) branch. Its local model, qwen3:14b, was evicted
2026-08-10, so from then a breach in a non-fast run died on a refused socket. `_call_local`
now refuses with that reason and opens nothing. Every production launch sets SIM_FAST_MODE=1
(background/process_run_complete.py), which takes `_call_mock` and never reaches it. A live
committee again is a director decision about which model, not a restart.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

HANDSHAKE_FILE = "docs/context-handshake-latest.md"

# Import deterministic rule engine — used by default; LLM reserved for crisis escalations
from sim.risk_committee_rules import decide as _rule_engine_decide
COMMITTEE_LOG_FILE = "docs/observability/risk-committee-log.md"

LIVE_COMMITTEE_RETIRED = (
    "the live risk committee is retired: its local model (qwen3:14b) was evicted 2026-08-10 "
    "and nothing replaced it. Run with SIM_FAST_MODE=1 for the deterministic committee."
)


def _read_handshake_context() -> str:
    return Path(HANDSHAKE_FILE).read_text()


#: The environment variable that decides WHICH COMMITTEE RUNS, named once because two modules now
#: ask the question: `invoke()` below branches on it, and `tools/run_annual_report` publishes the
#: answer into every run output's identity header. Two copies of the predicate would be two facts,
#: and the one in the header would be a claim about a branch it never watched being taken.
FAST_MODE_ENV = "SIM_FAST_MODE"


def fast_mode_enabled() -> bool:
    """Whether this process runs the deterministic mock committee instead of the local LLM.

    EXACTLY `== "1"`, NEVER TRUTHINESS, and the difference is not pedantic: `SIM_FAST_MODE=0` and
    `SIM_FAST_MODE=false` are both non-empty strings and neither one takes the mock branch below.
    A stamp built on `bool(os.environ.get(...))` would publish "this run used the mock committee"
    for a run that spent its whole length in Ollama — a plausible sentence about the wrong run,
    which is exactly the class of defect the run identity header exists to close.

    READ IN THE RUNNING PROCESS, and that is the honest reading rather than a convenient one.
    `tools/run_annual_report.main()` sets the variable from `--fast`, but `tournament_runner`,
    `measure_publish_gate_subject_cost` and every hand-launched arm run set it in the child's
    ENVIRONMENT and pass no flag at all. A stamp keyed to `args.fast` would read False for all of
    them while this function — the one the committee actually obeys — reads True.
    """
    return os.environ.get(FAST_MODE_ENV) == "1"


def _call_mock(current_hedge_fractions: dict[str, float]) -> dict:
    """Fast-mode deterministic committee (no LLM). Increases every customer's
    hedge fraction by the minimum +0.10, capped at 1.0. Used when
    SIM_FAST_MODE=1 is set — gives realistic committee behaviour (always
    cautious, always increases) without any GPU time. Results are clearly
    labelled in the log so fast-mode runs are distinguishable."""
    adjustments = [
        {
            "customer_id": cid,
            "old_hedge_fraction": hf,
            "new_hedge_fraction": round(min(1.0, hf + 0.10), 2),
        }
        for cid, hf in current_hedge_fractions.items()
        if hf < 1.0
    ]
    return {
        "reasoning": "[FAST-MODE] Deterministic minimum-increase policy — no LLM call.",
        "adjustments": adjustments,
    }


def _call_local(context: str) -> dict:
    """Refuses, naming why. See RETIRED in the module docstring."""
    raise RuntimeError(LIVE_COMMITTEE_RETIRED)


def _log_decision(settlement_date: str, settlement_period: int, context: str, decision: dict) -> None:
    """Append one wake-up entry to the risk committee log."""
    log_path = Path(COMMITTEE_LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    adjustments_text = "\n".join(
        f"  - {a['customer_id']}: {a['old_hedge_fraction']:.2f} → {a['new_hedge_fraction']:.2f}"
        for a in decision.get("adjustments", [])
    )

    entry = f"""
---

## Risk Committee Wake-Up — {settlement_date} period {settlement_period} (logged {timestamp})

**Context summary:**
{context.strip()}

**Agent reasoning:**
{decision.get('reasoning', '(no reasoning provided)')}

**Adjustments made:**
{adjustments_text if adjustments_text else '  (none)'}
"""
    with open(log_path, "a") as f:
        f.write(entry)


def invoke(settlement_date: str, settlement_period: int, current_hedge_fractions: dict[str, float]) -> dict[str, float]:
    """Invoke the risk committee agent. Returns a dict of {customer_id: new_hedge_fraction}
    for any customers whose hedge_fraction was adjusted. Customers not in the returned
    dict retain their current fraction unchanged.

    current_hedge_fractions: {customer_id: current_hedge_fraction} for all customers
      in scope — used to validate the agent's adjustments (enforce min +0.10, max +0.30,
      no decrease, clamp to [0.0, 1.0]).
    """
    context = _read_handshake_context()
    if fast_mode_enabled():
        decision = _call_mock(current_hedge_fractions)
    else:
        decision = _call_local(context)

    validated_adjustments = {}
    for adj in decision.get("adjustments", []):
        cid = adj["customer_id"]
        new_hf = float(adj["new_hedge_fraction"])
        current_hf = current_hedge_fractions.get(cid, 0.0)

        # Enforce constraints: no decrease, min +0.10, max +0.30, clamp to [0, 1]
        if new_hf < current_hf:
            new_hf = current_hf  # agent tried to decrease — silently hold
        elif new_hf < current_hf + 0.10:
            new_hf = current_hf + 0.10  # enforce minimum adjustment
        elif new_hf > current_hf + 0.30:
            new_hf = current_hf + 0.30  # enforce maximum adjustment
        new_hf = min(1.0, max(0.0, round(new_hf, 2)))

        if new_hf != current_hf:
            validated_adjustments[cid] = new_hf

    _log_decision(settlement_date, settlement_period, context, decision)
    return validated_adjustments
