#!/usr/bin/env python3
"""Model evaluation: gemma4:12b vs qwen3:14b on three tasks.

Tasks:
  1. Dispatcher message classification (10 messages, compare accuracy)
  2. Discovery agent assumption reasoning (5 UK energy benchmark questions)
  3. Risk committee decision quality (same portfolio state, compare reasoning)
"""

import json
import time
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"
MODELS = ["qwen3:14b", "gemma4:12b"]
PROJECT_DIR = Path(__file__).resolve().parent.parent


def _call(model: str, system: str, user: str, max_tokens: int = 200, think: bool = False) -> tuple[str, float]:
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "think": think,
        "options": {"num_predict": max_tokens, "temperature": 0.0},
    }).encode()
    t0 = time.monotonic()
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:  # 5min to allow model swap
        result = json.loads(resp.read())
    elapsed = time.monotonic() - t0
    return result["message"]["content"].strip(), elapsed


# ─── TASK 1: DISPATCHER CLASSIFICATION ──────────────────────────────────────

DISPATCHER_SYSTEM = """You are a message classifier for an energy simulation operator (Rich) communicating with an autonomous AI agent (Claude Code). Classify this inbound message from Rich.

Rules:
- URGENT: Rich is asking why something is wrong or why the agent is idle; or has spotted a correctness problem; or has explicitly flagged urgency.
- NORMAL: a real instruction, request, or design steer that needs action but is not an emergency.
- FYI: informational only, no action required.

Respond with EXACTLY one word: urgent, normal, or fyi"""

DISPATCHER_CASES = [
    # (message, expected)
    ("Start Phase 13a when you get a chance", "normal"),
    ("ok, looks good", "fyi"),
    ("The net margin is showing a positive number but I think basis risk should make it negative — investigate", "urgent"),
    ("Review what regular processes are spending tokens — make sure we're not over-using frontier", "normal"),
    ("I'll be back in 2 hours", "fyi"),
    ("why is the treasury declining even in 2016 when markets were calm?", "urgent"),
    ("Pull gemma4:12b and evaluate against qwen3:14b on 3 tasks", "normal"),
    ("nice work on Phase 12b", "fyi"),
    ("The sim runner log shows it failed twice — what's wrong?", "urgent"),
    ("When you have capacity, review the hedging mandate and consider raising the floor", "normal"),
]

def task1_dispatcher(model: str) -> dict:
    results = []
    for msg, expected in DISPATCHER_CASES:
        raw, t = _call(model, DISPATCHER_SYSTEM, f'Message: "{msg}"\n\nRespond with EXACTLY one word: urgent, normal, or fyi', max_tokens=10)
        got = raw.lower().strip().split()[0] if raw.strip() else "?"
        correct = expected in got
        results.append({"message": msg[:50], "expected": expected, "got": got, "correct": correct, "latency_s": round(t, 1)})
        print(f"  [{model}] '{msg[:40]}...' → {got} ({'✓' if correct else '✗'} expected {expected})")
    score = sum(1 for r in results if r["correct"])
    return {"score": score, "total": len(results), "results": results}


# ─── TASK 2: DISCOVERY AGENT — ASSUMPTION REASONING ─────────────────────────

DISCOVERY_SYSTEM = """You are auditing a UK retail energy supplier simulation (2016-2025).
Assess whether this simulation assumption is realistic for a small UK retail energy supplier.

Respond with EXACTLY this format (no extra text):
VERDICT: ok|warning|critical
NOTE: <one sentence explaining your verdict>

Use 'critical' only if the SIM value is clearly outside industry range and materially distorts outputs.
Use 'warning' if the value is at the edge of plausible range or the source is dated.
Use 'ok' if the value is realistic."""

DISCOVERY_CASES = [
    {
        "assumption": "Residential electricity EAC",
        "sim_value": "15,000 kWh/year",
        "benchmark": "3,100 kWh/year (Ofgem 2023)",
        "expected_verdict": "critical",
        "note": "SIM uses 15,000 kWh/yr — ~5x the Ofgem residential average of 3,100 kWh/yr",
    },
    {
        "assumption": "Non-commodity cost (network + levies)",
        "sim_value": "£50/MWh",
        "benchmark": "£45-£60/MWh (Ofgem 2022)",
        "expected_verdict": "ok",
        "note": "Within plausible range for 2016-2025 blended NCC",
    },
    {
        "assumption": "Churn base rate",
        "sim_value": "10% per annum",
        "benchmark": "15-20% p.a. (Ofgem switching data 2018-2022)",
        "expected_verdict": "warning",
        "note": "10% is below the Ofgem-observed switching rate but not wildly implausible for a stable cohort",
    },
    {
        "assumption": "Bad debt rate",
        "sim_value": "2% of revenue",
        "benchmark": "1-3% (industry range, pre-crisis)",
        "expected_verdict": "ok",
        "note": "2% is within industry range",
    },
    {
        "assumption": "Customer acquisition cost",
        "sim_value": "£50 per customer",
        "benchmark": "£50-£150 (industry estimates, 2018-2022)",
        "expected_verdict": "ok",
        "note": "At the low end but plausible for digital-first acquisition",
    },
]

def task2_discovery(model: str) -> dict:
    results = []
    for case in DISCOVERY_CASES:
        prompt = f"""Assumption: {case['assumption']}
Current SIM value: {case['sim_value']}
Industry benchmark: {case['benchmark']}"""
        raw, t = _call(model, DISCOVERY_SYSTEM, prompt, max_tokens=100)
        import re
        verdict_match = re.search(r"VERDICT:\s*(ok|warning|critical)", raw, re.IGNORECASE)
        got = verdict_match.group(1).lower() if verdict_match else "?"
        correct = got == case["expected_verdict"]
        results.append({
            "assumption": case["assumption"],
            "expected": case["expected_verdict"],
            "got": got,
            "correct": correct,
            "latency_s": round(t, 1),
            "raw": raw[:200],
        })
        print(f"  [{model}] {case['assumption']} → {got} ({'✓' if correct else '✗'} expected {case['expected_verdict']})")
    score = sum(1 for r in results if r["correct"])
    return {"score": score, "total": len(results), "results": results}


# ─── TASK 3: RISK COMMITTEE DECISION QUALITY ────────────────────────────────

RISK_SYSTEM = """You are the risk committee agent for a simulated UK energy supplier.
You have been woken by a threshold breach in the portfolio's risk monitoring system.
Your job is to read the context summary, reason about the appropriate hedge_fraction
adjustment for the flagged customer(s), and output a structured decision.

Rules:
- You may ONLY increase hedge_fraction, never decrease it
- Minimum adjustment: +0.10 per customer per wake-up
- Maximum adjustment: +0.30 per customer per wake-up
- You adjust exactly one lever: hedge_fraction. Nothing else.
- You must justify your reasoning in plain English (2-4 sentences)

Output format (JSON, no markdown fences):
{
  "reasoning": "2-4 sentences explaining your decision",
  "adjustments": [
    {"customer_id": "CX", "old_hedge_fraction": 0.00, "new_hedge_fraction": 0.20}
  ]
}"""

RISK_CONTEXT = """## Risk Committee Wake-Up — 2022-09-01 period 4
Trigger: treasury drawdown 22.1% from 12-month peak £24832.15 | VaR_current £2341.18 exceeds VaR_stressed £812.44 × 2.5 (ratio 2.88)
Treasury balance: £19348.05 (12-month peak: £24832.15, drawdown: 22.1%)
Portfolio gross margin YTD: £-721.34 | Net margin YTD: £-758.22
Capital costs YTD: £36.88
VaR_current: £2341.18 | VaR_stressed: £812.44 | Ratio: 2.88
Per-customer hedge_fraction: C1=0.85 C2=0.85 C3=0.85 C4=0.95 C5=0.85 C6=0.95 C7=0.95 C8=0.95 C9=1.00
Per-customer collateral: C1: collateral=£55.20 coc=£0.46/mo C2: collateral=£158.30 coc=£1.32/mo C3: collateral=£24.10 coc=£0.20/mo C4: collateral=£198.75 coc=£1.66/mo C5: collateral=£489.20 coc=£4.08/mo C6: collateral=£712.40 coc=£5.94/mo C7: collateral=£428.90 coc=£3.57/mo C8: collateral=£187.30 coc=£1.56/mo C9: collateral=£0.00 coc=£0.00/mo
Rolling 12m SSP: σ_recent = 1.821 | Forward price: £312.44/MWh
Regime: post-2021 (σ_stressed = 0.80) — energy crisis
Recommendation requested: adjust hedge_fraction for C1, C2, C3, C5
Constraint: minimum adjustment +0.10, maximum single adjustment +0.30 | never decrease hedge_fraction"""

def _validate_adjustments(raw: str, context_hfs: dict) -> dict:
    """Parse and validate risk committee response."""
    import json as _json
    import re
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    cleaned = re.sub(r"```[a-z]*\n?", "", cleaned).strip()
    try:
        decision = _json.loads(cleaned)
        adjustments = decision.get("adjustments", [])
        valid = True
        issues = []
        for adj in adjustments:
            cid = adj.get("customer_id", "?")
            old_hf = context_hfs.get(cid, 0.85)
            new_hf = float(adj.get("new_hedge_fraction", 0))
            if new_hf < old_hf:
                issues.append(f"{cid}: decreased hedge_fraction (violation)")
                valid = False
            delta = new_hf - old_hf
            if delta < 0.09:
                issues.append(f"{cid}: delta {delta:.2f} < 0.10 (too small)")
                valid = False
            if delta > 0.31:
                issues.append(f"{cid}: delta {delta:.2f} > 0.30 (too large)")
                valid = False
        return {"valid": valid, "issues": issues, "adjustments": adjustments, "reasoning": decision.get("reasoning", "")[:300]}
    except Exception as e:
        return {"valid": False, "issues": [f"JSON parse error: {e}"], "adjustments": [], "reasoning": ""}

def task3_risk_committee(model: str) -> dict:
    context_hfs = {"C1": 0.85, "C2": 0.85, "C3": 0.85, "C4": 0.95, "C5": 0.85, "C6": 0.95, "C7": 0.95, "C8": 0.95, "C9": 1.00}
    raw, t = _call(model, RISK_SYSTEM, RISK_CONTEXT, max_tokens=512, think=False)
    result = _validate_adjustments(raw, context_hfs)
    result["latency_s"] = round(t, 1)
    result["raw"] = raw[:500]
    adj_str = ", ".join(f"{a['customer_id']}→{a.get('new_hedge_fraction', '?')}" for a in result["adjustments"])
    print(f"  [{model}] {'✓ VALID' if result['valid'] else '✗ INVALID'} ({t:.1f}s) | adjustments: {adj_str or 'none parsed'}")
    if result["issues"]:
        for issue in result["issues"]:
            print(f"    ISSUE: {issue}")
    print(f"    Reasoning: {result['reasoning'][:200]}")
    return result


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("MODEL EVALUATION: gemma4:12b vs qwen3:14b")
    print("=" * 70)

    summary = {}

    for model in MODELS:
        print(f"\n{'─'*70}")
        print(f"MODEL: {model}")
        print(f"{'─'*70}")

        print("\n[Task 1] Dispatcher classification (10 messages)")
        t1 = task1_dispatcher(model)
        print(f"  Score: {t1['score']}/{t1['total']}")

        print("\n[Task 2] Discovery agent assumption reasoning (5 questions)")
        t2 = task2_discovery(model)
        print(f"  Score: {t2['score']}/{t2['total']}")

        print("\n[Task 3] Risk committee decision quality")
        t3 = task3_risk_committee(model)
        print(f"  Valid: {t3['valid']}")

        summary[model] = {
            "dispatcher": f"{t1['score']}/{t1['total']}",
            "dispatcher_latencies": [r["latency_s"] for r in t1["results"]],
            "discovery": f"{t2['score']}/{t2['total']}",
            "discovery_latencies": [r["latency_s"] for r in t2["results"]],
            "risk_committee_valid": t3["valid"],
            "risk_committee_latency_s": t3["latency_s"],
            "risk_committee_issues": t3["issues"],
        }

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for model, s in summary.items():
        avg_d = round(sum(s["dispatcher_latencies"]) / len(s["dispatcher_latencies"]), 1)
        avg_r = round(sum(s["discovery_latencies"]) / len(s["discovery_latencies"]), 1)
        print(f"\n{model}:")
        print(f"  Task 1 (dispatcher): {s['dispatcher']} (avg {avg_d}s/call)")
        print(f"  Task 2 (discovery):  {s['discovery']} (avg {avg_r}s/call)")
        print(f"  Task 3 (risk):       {'PASS' if s['risk_committee_valid'] else 'FAIL'} ({s['risk_committee_latency_s']}s)")


if __name__ == "__main__":
    main()
