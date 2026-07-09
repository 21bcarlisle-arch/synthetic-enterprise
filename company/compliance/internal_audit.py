"""Internal audit -- Phase 6 of DOMAIN_SENSE_AND_COMPLIANCE.md.

"Institutionalise the local-Qwen skeptic inside the company": an
independent sampling agent that reads real rendered bill artefacts and asks
a local Qwen model, prompted as a grumpy UK energy auditor, to flag
absurdities a human reviewer would catch but an automated invariant might
not have been written for yet (method rule 0c's own motivating case: a
real SME account rendering as "Household" with residential-implausible
consumption -- no automated invariant existed for "does the label match
the segment" until that incident).

Risk-based sampling (director's principle 3: depth/frequency follows risk
tier): resi bills are sampled preferentially, since Phase 1's Tier-1
obligations (billing accuracy, VAT-by-segment) concentrate there.

Same fail-safe contract as background/discovery_agent.py's `_call_qwen()`
(a separate copy, not imported, so this module has no dependency on the
discovery daemon): a failed/unavailable Ollama call returns "" and this
module treats that as clean (no finding) rather than fabricating one --
an audit sampler that can't reach its own model must fail silent, not
false-positive.
"""
from __future__ import annotations

import json
import random
import re
import subprocess
from typing import Callable, Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"


def call_qwen(prompt: str, max_tokens: int = 200) -> str:
    """Call local Qwen via Ollama. Returns empty string on any failure.

    `"think": false` is the Ollama API's own switch for qwen3's reasoning
    mode -- found live (2026-07-09) that the `/no_think` prompt-suffix
    convention (as used by background/discovery_agent.py's _call_qwen())
    does NOT reliably suppress it on this server: a real call came back
    with an empty "response" and all the model's output sitting in a
    separate "thinking" field, having exhausted num_predict before ever
    reaching an answer. The explicit API parameter is the actual fix."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", OLLAMA_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "model": OLLAMA_MODEL,
                 "prompt": prompt,
                 "stream": False,
                 "think": False,
                 "options": {"num_predict": max_tokens, "temperature": 0.1},
             })],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("response", "").strip()
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return ""


def build_audit_prompt(bill: dict) -> str:
    return f"""You are a grumpy, skeptical UK energy industry auditor reviewing one customer bill for absurdities an automated check might miss.

Customer segment: {bill.get('segment')}
Commodity: {bill.get('commodity')}
Billing period: {bill.get('period_start')} to {bill.get('period_end')}
Consumption: {bill.get('total_consumption_kwh')} kWh
Commodity charge: GBP {bill.get('commodity_amount_gbp', 0):.2f}
Non-commodity charge: GBP {bill.get('non_commodity_amount_gbp', 0):.2f}
Standing charge: GBP {bill.get('standing_charge_gbp', 0):.2f}
VAT: GBP {bill.get('vat_gbp', 0):.2f}
Total: GBP {bill.get('total_amount_gbp', 0):.2f}

Does anything here look absurd or wrong for a real UK {bill.get('segment')} energy customer -- e.g. consumption implausible for the stated segment, VAT rate inconsistent with segment, charges that don't add up? Respond with EXACTLY this format (no extra text):
VERDICT: clean|flagged
NOTE: <one sentence>
/no_think"""


def parse_audit_response(response: str) -> dict:
    verdict = "clean"
    note = "Qwen assessment unavailable"
    if response:
        verdict_match = re.search(r"VERDICT:\s*(clean|flagged)", response, re.IGNORECASE)
        note_match = re.search(r"NOTE:\s*(.+)", response)
        if verdict_match:
            verdict = verdict_match.group(1).lower()
        if note_match:
            note = note_match.group(1).strip()
    return {"verdict": verdict, "note": note}


def sample_bills_risk_based(bills: list, n: int, rng: random.Random) -> list:
    """resi bills get 3x the sampling weight of I&C/SME -- Tier-1
    obligations (billing accuracy, VAT-by-segment) concentrate on resi."""
    if not bills or n <= 0:
        return []
    weights = [3 if b.get("segment") == "resi" else 1 for b in bills]
    return rng.choices(bills, weights=weights, k=min(n, len(bills)))


def run_internal_audit(
    bills: list, n_samples: int = 5, seed: Optional[int] = None,
    call_qwen_fn: Callable[[str], str] = call_qwen,
) -> list[dict]:
    """Sample `n_samples` bills risk-based, ask Qwen to audit each, return
    only FLAGGED findings -- a clean verdict is the expected, silent case,
    matching every other check in this programme (Phase 3/5's checks also
    only ever report failures, not a running list of passes)."""
    rng = random.Random(seed)
    sampled = sample_bills_risk_based(bills, n_samples, rng)
    findings = []
    for bill in sampled:
        response = call_qwen_fn(build_audit_prompt(bill))
        result = parse_audit_response(response)
        if result["verdict"] == "flagged":
            findings.append({
                "customer_id": bill.get("customer_id"),
                "period_end": bill.get("period_end"),
                "note": result["note"],
            })
    return findings
