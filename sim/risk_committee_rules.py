"""Deterministic rule engine for routine risk committee decisions.

Replaces the Ollama call for within-mandate hedge fraction adjustments.
The LLM is reserved for crisis regimes (sigma > threshold) and edge cases.

Rules (applied in order):
  1. If sigma_recent > CRISIS_SIGMA_THRESHOLD: escalate to LLM
  2. If all triggered customers at hf=1.0: escalate to LLM (nothing to do)
  3. Otherwise: increase triggered customers by step based on VaR breach severity
     - ratio >= 3.0: +0.25  (severe breach)
     - ratio >= 2.5: +0.20  (moderate breach)
     - treasury-only or mild: +0.15

This covers ~95% of committee wake-ups, saving ~15s Ollama call each time.
"""
import re

CRISIS_SIGMA_THRESHOLD = 1.5  # post-crisis regime detection threshold


def parse_handshake(context: str) -> dict:
    """Extract key numeric fields from the structured handshake context text."""
    result: dict = {
        "hedge_fractions": {},
        "var_ratio": 0.0,
        "sigma_recent": 0.0,
        "triggered_customers": [],
    }

    # Per-customer hedge_fraction: "Per-customer hedge_fraction: C1=0.91 C2=0.91 ..."
    hf_match = re.search(r"Per-customer hedge_fraction: (.+)", context)
    if hf_match:
        for item in hf_match.group(1).strip().split():
            if "=" in item:
                cid, hf = item.split("=", 1)
                try:
                    result["hedge_fractions"][cid.strip()] = float(hf.strip())
                except ValueError:
                    pass

    # VaR ratio: "Ratio: 2.57"
    ratio_match = re.search(r"Ratio: ([0-9.]+)", context)
    if ratio_match:
        result["var_ratio"] = float(ratio_match.group(1))

    # sigma_recent from line like: "Rolling 12m SSP: sigma_recent = 1.316"
    # Handles both Unicode sigma (u03c3) and ASCII fallback
    sigma_match = re.search(r"\u03c3_recent\s*=\s*([0-9.]+)", context)
    if not sigma_match:
        sigma_match = re.search(r"_recent = ([0-9.]+)", context)
    if sigma_match:
        result["sigma_recent"] = float(sigma_match.group(1))

    # Triggered customers: "Recommendation requested: adjust hedge_fraction for C1, C5, C7"
    triggered_match = re.search(
        r"Recommendation requested: adjust hedge_fraction for (.+)", context
    )
    if triggered_match:
        result["triggered_customers"] = [
            c.strip() for c in triggered_match.group(1).split(",") if c.strip()
        ]

    return result


def should_escalate(parsed: dict) -> bool:
    """Return True if the decision is non-routine and requires LLM reasoning."""
    if parsed["sigma_recent"] > CRISIS_SIGMA_THRESHOLD:
        return True
    triggered = parsed["triggered_customers"]
    if triggered and all(
        parsed["hedge_fractions"].get(cid, 0.0) >= 1.0 for cid in triggered
    ):
        return True
    return False


def _adjustment_step(var_ratio: float) -> float:
    """Return the hedge fraction step for the given VaR breach ratio."""
    if var_ratio >= 3.0:
        return 0.25
    if var_ratio >= 2.5:
        return 0.20
    return 0.15


def apply_rules(
    parsed: dict,
    current_hf: dict[str, float],
) -> dict[str, float]:
    """Apply deterministic adjustments. Returns {customer_id: new_hf} for changed customers."""
    triggered = parsed["triggered_customers"]
    if not triggered:
        return {}
    step = _adjustment_step(parsed["var_ratio"])
    adjustments: dict[str, float] = {}
    for cid in triggered:
        hf = current_hf.get(cid, parsed["hedge_fractions"].get(cid, 0.0))
        if hf < 1.0:
            new_hf = min(1.0, round(hf + step, 2))
            if new_hf > hf:
                adjustments[cid] = new_hf
    return adjustments


def decide(
    context: str,
    current_hf: dict[str, float],
) -> tuple[bool, dict[str, float]]:
    """Evaluate context and produce a deterministic committee decision.

    Returns (escalate_to_llm, adjustments).
    If escalate_to_llm is True, caller should invoke the LLM instead.
    """
    parsed = parse_handshake(context)
    if should_escalate(parsed):
        return True, {}
    return False, apply_rules(parsed, current_hf)
