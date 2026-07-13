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
discovery daemon): a failed/unavailable Ollama call returns "".

FAIL-SILENT FIX (2026-07-13, CONTROLS_THAT_CANNOT_FAIL.md, F6 class):
this module PREVIOUSLY treated an unreachable model as "clean" (verdict
defaulted to clean, no finding) so that on every autonomous run where
Ollama happened to be down the audit passed by NOT RUNNING -- the exact
FAIL-SILENT killer pattern the controls-that-cannot-fail doctrine names.
An unavailable check is a FAILED check. The verdict now has a THIRD state,
"unavailable", distinct from both "clean" and "flagged": it never
fabricates a finding against a specific bill (that would false-positive a
correct bill), but it DOES alarm -- run_internal_audit / run_phase_close_
audit surface a `kind="checker_unavailable"` finding when the model could
not be reached, so a caller (background/sanity_daemon.py) sees a non-empty
findings list and reports the outage instead of logging "0 flagged".
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


CHECKER_UNAVAILABLE = "unavailable"


def parse_audit_response(response: str) -> dict:
    """Parse the model's verdict. THREE states, not two:
      - "flagged"      -- the model reached a verdict and flagged the artefact.
      - "clean"        -- the model reached a verdict and passed the artefact.
      - "unavailable"  -- the model returned nothing usable (empty response =
                          Ollama down/timed out, OR a response with no parseable
                          VERDICT line = unusable output). This is NOT clean: an
                          unavailable check is a FAILED check (F6 fail-silent
                          fix, CONTROLS_THAT_CANNOT_FAIL.md). The caller alarms
                          on it rather than passing.
    """
    if not response:
        return {"verdict": CHECKER_UNAVAILABLE, "note": "Qwen assessment unavailable (empty response -- model unreachable)"}
    verdict_match = re.search(r"VERDICT:\s*(clean|flagged)", response, re.IGNORECASE)
    note_match = re.search(r"NOTE:\s*(.+)", response)
    if not verdict_match:
        return {
            "verdict": CHECKER_UNAVAILABLE,
            "note": "Qwen response carried no parseable VERDICT line -- treating as unavailable, not clean",
        }
    verdict = verdict_match.group(1).lower()
    note = note_match.group(1).strip() if note_match else "Qwen assessment unavailable"
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
    unavailable = 0
    for bill in sampled:
        response = call_qwen_fn(build_audit_prompt(bill))
        result = parse_audit_response(response)
        if result["verdict"] == "flagged":
            findings.append({
                "customer_id": bill.get("customer_id"),
                "period_end": bill.get("period_end"),
                "note": result["note"],
            })
        elif result["verdict"] == CHECKER_UNAVAILABLE:
            unavailable += 1
    # F6 FAIL-SILENT FIX: an unavailable checker ALARMS, it does not pass
    # silently. If the model could not be reached for any sampled bill, emit a
    # single checker_unavailable finding so a non-empty findings list forces the
    # caller to report the outage (CONTROLS_THAT_CANNOT_FAIL.md). Prepended so it
    # is never lost behind real flags. Shape-compatible with the flagged findings
    # (customer_id/period_end/note) so sanity_daemon's formatting is unaffected.
    if unavailable and sampled:
        findings.insert(0, {
            "kind": "checker_unavailable",
            "customer_id": None,
            "period_end": None,
            "note": (
                f"Internal audit checker (Qwen/Ollama) unavailable for "
                f"{unavailable}/{len(sampled)} sampled bills -- the audit did NOT "
                f"run; treat as a FAILED check, not clean"
            ),
        })
    return findings


# --- Phase 7: Qwen skeptic phase-close pass (generalises the bill-specific
# audit above to ANY rendered artefact -- a portal page's text, a report
# section, a dashboard block -- for the phase-close checklist ritual named
# in DOMAIN_SENSE_AND_COMPLIANCE.md, rather than a second bespoke prompt/
# parsing mechanism) ---

def build_artefact_audit_prompt(artefact_name: str, artefact_text: str) -> str:
    # Truncated -- num_predict-sized context is for the verdict, not for
    # re-reading an arbitrarily long rendered page back in full.
    excerpt = artefact_text[:2000]
    return f"""You are a grumpy, skeptical UK energy industry auditor reviewing a rendered artefact ({artefact_name}) from a UK energy supplier's systems for absurdities an automated check might miss.

Artefact content:
{excerpt}

Does anything here look absurd, inconsistent, or wrong for a real UK energy supplier -- e.g. numbers that don't add up, labels that contradict the data, implausible values? Respond with EXACTLY this format (no extra text):
VERDICT: clean|flagged
NOTE: <one sentence>
/no_think"""


def audit_artefact(
    artefact_name: str, artefact_text: str,
    call_qwen_fn: Callable[[str], str] = call_qwen,
) -> dict:
    """One artefact, one verdict -- the phase-close pass calls this once per
    randomly sampled artefact and collects only the flagged ones, same
    silent-on-clean discipline as run_internal_audit()."""
    response = call_qwen_fn(build_artefact_audit_prompt(artefact_name, artefact_text))
    result = parse_audit_response(response)
    return {"artefact_name": artefact_name, "verdict": result["verdict"], "note": result["note"]}


def run_phase_close_audit(
    artefacts: dict[str, str], n_samples: int = 3, seed: Optional[int] = None,
    call_qwen_fn: Callable[[str], str] = call_qwen,
) -> list[dict]:
    """`artefacts` maps a name (e.g. "site/customers/index.html#C1-bill") to
    its rendered text content. Randomly samples n_samples of them and
    returns only the flagged verdicts -- the phase-close checklist step
    named in DOMAIN_SENSE_AND_COMPLIANCE.md ("Qwen skeptic pass at phase
    close: grumpy-UK-energy-auditor prompt reads randomly sampled rendered
    artefacts; flags absurdities")."""
    rng = random.Random(seed)
    names = list(artefacts.keys())
    sampled_names = rng.sample(names, k=min(n_samples, len(names))) if names else []
    findings = []
    unavailable = 0
    for name in sampled_names:
        result = audit_artefact(name, artefacts[name], call_qwen_fn=call_qwen_fn)
        if result["verdict"] == "flagged":
            findings.append(result)
        elif result["verdict"] == CHECKER_UNAVAILABLE:
            unavailable += 1
    # F6 FAIL-SILENT FIX (same contract as run_internal_audit): alarm on an
    # unreachable checker rather than reporting a clean phase-close pass.
    if unavailable and sampled_names:
        findings.insert(0, {
            "kind": "checker_unavailable",
            "artefact_name": None,
            "verdict": CHECKER_UNAVAILABLE,
            "note": (
                f"Phase-close audit checker (Qwen/Ollama) unavailable for "
                f"{unavailable}/{len(sampled_names)} sampled artefacts -- the audit "
                f"did NOT run; treat as a FAILED check, not clean"
            ),
        })
    return findings
