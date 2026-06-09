"""Risk committee LLM agent — the Context Handshake decision layer.

This module is the LLM side of the Context Handshake. It is invoked only when
sim/risk_committee.py's RiskCommitteeMonitor.update() returns True (a threshold
breach). It reads the context summary written by the monitor, reasons about the
right hedge_fraction adjustment for the flagged customer(s), writes its decision
back to the simulation state, and logs its reasoning.

Architecture contract (the Context Handshake):
  1. The Python engine detects a threshold breach (risk_committee.py)
  2. The engine writes the context summary to docs/context-handshake-latest.md
  3. THIS module reads the summary, calls the frontier LLM, and extracts a decision
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

Frontier model only — this module MUST NOT be delegated to a local model. The
risk committee agent is the first place in this project where a live LLM agent
makes a real-time decision that affects the simulation's financial state.
"""

import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

HANDSHAKE_FILE = "docs/context-handshake-latest.md"
COMMITTEE_LOG_FILE = "docs/observability/risk-committee-log.md"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
COMMITTEE_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are the risk committee agent for a simulated UK energy supplier.
You have been woken by a threshold breach in the portfolio's risk monitoring system.
Your job is to read the context summary, reason about the appropriate hedge_fraction
adjustment for the flagged customer(s), and output a structured decision.

Rules:
- You may ONLY increase hedge_fraction, never decrease it
- Minimum adjustment: +0.10 per customer per wake-up
- Maximum adjustment: +0.30 per customer per wake-up
- You adjust exactly one lever: hedge_fraction. Nothing else.
- You must justify your reasoning in plain English (2-4 sentences)
- After your decision, you return to sleep — no further action until the next breach

Output format (JSON, no markdown fences):
{
  "reasoning": "2-4 sentences explaining your decision",
  "adjustments": [
    {"customer_id": "CX", "old_hedge_fraction": 0.00, "new_hedge_fraction": 0.20},
    ...
  ]
}
"""


def _read_handshake_context() -> str:
    return Path(HANDSHAKE_FILE).read_text()


def _call_frontier(context: str) -> dict:
    """Call the frontier model with the handshake context. Returns the parsed
    decision dict. Raises on API error or unparseable response.
    """
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    payload = json.dumps({
        "model": COMMITTEE_MODEL,
        "max_tokens": 512,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": context}],
    }).encode()

    request = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read())

    raw_text = result["content"][0]["text"]

    # Strip any accidental markdown fences before parsing
    cleaned = re.sub(r"^```[a-z]*\n?", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```$", "", cleaned.strip())
    return json.loads(cleaned)


def _log_decision(settlement_date: str, settlement_period: int, context: str, decision: dict) -> None:
    """Append one wake-up entry to the risk committee log."""
    log_path = Path(COMMITTEE_LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
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
    decision = _call_frontier(context)

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
