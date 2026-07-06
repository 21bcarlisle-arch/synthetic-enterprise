#!/usr/bin/env python3
"""WEBSITE_AS_SHOWCASE.md tab 4 (CUSTOMER PORTAL -- MICRO MEETS MACRO): the
case-study recommender. Auto-curates a handful of interesting customers
purely by ranking real per-household signals the sim/company layers already
compute -- nobody is hand-picked by account id.

- Most eventful journey: highest timeline + reaction-chain entry count.
- Largest company-vs-SIM churn divergence: biggest churn_estimate_error_pct
  from a real renewal (customer_sample.json churn_accuracy_by_renewal).
- Retention save, then churned anyway: a retention_decision fired in the
  reaction chain before the eventual churn.
- Heaviest arrears cascade: most WRITTEN_OFF outcomes in the reaction chain.
- Notable life event: a life_event timeline entry with a real measured
  before/after effect.

Each slot links straight into that household Customer 360 timeline via the
existing deep-link params (site/customers/index.html, Phase RM). Must run
after generate_customer_data, generate_customer_reaction_chain, and
generate_customer_sample (needs their output on disk).

Output: site/data/case_studies.json, read by the Customer Portal landing page.
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"
SAMPLE_PATH = PROJECT / "site" / "data" / "customer_sample.json"
OUT_PATH = PROJECT / "site" / "data" / "case_studies.json"


def _households():
    idx = json.loads((CUSTOMERS_DIR / "_index.json").read_text())
    by_base = dict()
    for cid in idx:
        obj = json.loads((CUSTOMERS_DIR / (cid + ".json")).read_text())
        base = obj.get("base_account_id", cid)
        is_elec = obj.get("commodity") != "gas"
        if base not in by_base or is_elec:
            by_base[base] = (cid, obj)
    return by_base


def _max_divergence(sample_customers, cid):
    entry = sample_customers.get(cid) or dict()
    entries = entry.get("churn_accuracy_by_renewal") or []
    if not entries:
        return None
    return max(entries, key=lambda e: abs(e.get("churn_estimate_error_pct", 0)))


def _writeoffs(reaction_chain):
    return [e for e in reaction_chain if e.get("outcome") == "WRITTEN_OFF"]


def _retention_then_churn(timeline, reaction_chain):
    churned = next((e for e in timeline if e.get("type") == "churned"), None)
    if not churned:
        return False
    return any(
        e.get("event_type") == "retention_decision" and e["date"] < churned["date"]
        for e in reaction_chain
    )


def _life_events(timeline):
    return [e for e in timeline if e.get("type") == "life_event"]


def _score_households(by_base, sample_customers):
    scored = []
    for base, pair in sorted(by_base.items()):
        cid, obj = pair
        timeline = obj.get("timeline", [])
        reaction_chain = obj.get("reaction_chain", [])
        life_events = [e for e in _life_events(timeline) if e.get("effect")]
        row = dict(
            base=base, cid=cid, obj=obj,
            event_density=len(timeline) + len(reaction_chain),
            divergence=_max_divergence(sample_customers, cid),
            writeoffs=_writeoffs(reaction_chain),
            retention_then_churn=_retention_then_churn(timeline, reaction_chain),
            life_events=life_events,
        )
        scored.append(row)
    return scored


def _pick(scored, used, key, filt=None):
    pool = [c for c in scored if c["base"] not in used and (filt is None or filt(c))]
    if not pool:
        return None
    best = max(pool, key=key)
    used.add(best["base"])
    return best


def _fmt_pct(v):
    return str(round(abs(v) * 100)) + "%"


def build(by_base, sample_customers):
    scored = _score_households(by_base, sample_customers)
    used = set()
    cases = []

    c = _pick(scored, used, lambda c: c["event_density"])
    if c:
        headline = str(c["event_density"]) + " timeline + reaction-chain entries on record"
        cases.append(dict(category="Most eventful journey", headline=headline, c=c, year=None))

    c = _pick(
        scored, used, lambda c: abs(c["divergence"]["churn_estimate_error_pct"]),
        filt=lambda c: c["divergence"] is not None,
    )
    if c:
        d = c["divergence"]
        headline = (
            _fmt_pct(d["churn_estimate_error_pct"]) + " error at the " + d["term_start"][:4]
            + " renewal (sim " + _fmt_pct(d["sim_churn_probability"])
            + " vs company " + _fmt_pct(d["company_churn_estimate"]) + ")"
        )
        cases.append(dict(
            category="Largest company-vs-SIM churn divergence", headline=headline,
            c=c, year=int(d["term_start"][:4]),
        ))

    c = _pick(scored, used, lambda c: c["event_density"], filt=lambda c: c["retention_then_churn"])
    if c:
        churned = next(e for e in c["obj"]["timeline"] if e.get("type") == "churned")
        headline = "The company offered retention and won, then lost the account regardless"
        cases.append(dict(
            category="Retention save, then churned anyway", headline=headline,
            c=c, year=int(churned["date"][:4]),
        ))

    c = _pick(scored, used, lambda c: len(c["writeoffs"]), filt=lambda c: c["writeoffs"])
    if c:
        wo = c["writeoffs"][0]
        headline = str(len(c["writeoffs"])) + " debt write-off event(s) in the arrears cascade"
        cases.append(dict(
            category="Heaviest arrears cascade", headline=headline,
            c=c, year=int(wo["date"][:4]),
        ))

    c = _pick(scored, used, lambda c: len(c["life_events"]), filt=lambda c: c["life_events"])
    if c:
        le = c["life_events"][-1]
        headline = str(le.get("detail", "Life event")) + " (" + le["date"][:4] + ") -- " + le["effect"]
        cases.append(dict(
            category="Notable life event", headline=headline,
            c=c, year=int(le["date"][:4]),
        ))

    out = []
    for case in cases:
        c = case["c"]
        obj = c["obj"]
        link = dict(acc=c["cid"], tab="timeline")
        if case["year"]:
            link["year"] = case["year"]
        out.append(dict(
            category=case["category"],
            headline=case["headline"],
            account_id=c["cid"],
            base_account_id=c["base"],
            segment=obj.get("segment"),
            commodity=obj.get("commodity"),
            link=link,
        ))
    return out


def generate(run_json_path=None):
    if not SAMPLE_PATH.exists() or not (CUSTOMERS_DIR / "_index.json").exists():
        print("Skipped: customer_sample.json or customers index missing")
        return 0
    sample = json.loads(SAMPLE_PATH.read_text())
    sample_customers = sample.get("customers", {})
    by_base = _households()
    cases = build(by_base, sample_customers)
    meta = dict(
        generated_at=sample.get("meta", {}).get("generated_at"),
        git_commit=sample.get("meta", {}).get("git_commit"),
        household_count=len(by_base),
        note=(
            "Auto-curated from real per-household timeline/reaction-chain/"
            "churn-accuracy data (WEBSITE_AS_SHOWCASE.md tab 4) -- no "
            "household is hand-picked."
        ),
    )
    out = dict(meta=meta, cases=cases)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print("Generated " + str(OUT_PATH) + " (" + str(len(cases)) + " cases)")
    return len(cases)


if __name__ == "__main__":
    generate()
