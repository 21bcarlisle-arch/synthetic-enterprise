#!/usr/bin/env python3
"""WEBSITE_AS_SHOWCASE.md tab 4 (CUSTOMER PORTAL -- MICRO MEETS MACRO): the
case-study recommender. Auto-curates a handful of interesting customers
purely by ranking real per-household signals the sim/company layers already
compute -- nobody is hand-picked by account id.

- Most eventful journey: highest timeline + reaction-chain entry count.
- Largest company-vs-SIM churn divergence: biggest PERCENTAGE-POINT gap
  between the company's estimate and the probability the sim actually rolled,
  at a real renewal (customer_sample.json churn_accuracy_by_renewal). NOT
  churn_estimate_error_pct -- see the unit doctrine below.
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

UNIT DOCTRINE -- A LEVEL, A RATIO AND A DIFFERENCE ARE THREE QUANTITIES
(cold-eyes 2026-08-12, coldwalk:site2_coo_2841_percent_error_arithmetic_doubt).
Every headline here is a public claim on poesys.net, and this module used ONE
formatter (_fmt_pct) for a probability LEVEL, for a RATIO of two probabilities
and for a DIFFERENCE of two probabilities -- emitting the same bare "N%" for
all three and leaving the surrounding English to say which was meant. In both
places the English mattered it was wrong, in OPPOSITE directions: a ratio was
published as "2841% error" (innumerate framing of a 91.8-point gap), and a
91.8/12.2-point difference was published as "fell 12%" (which reads as a
relative fall, and the relative fall was 19%). So the formatters are now split
by the KIND of quantity and each carries its own unit in the string:

  _fmt_level(v)  -> "3.2%"                  a probability or score LEVEL
  _fmt_points(v) -> "91.8 percentage points" a DIFFERENCE between two levels

There is deliberately no bare-percentage formatter left to reach for, and no
relative error is published at all. Levels print to one decimal so that a
reader can reproduce the stated gap from the two levels printed beside it --
the original defect was checkable only against unrounded inputs the reader was
never shown. Guarded as a CLASS over the produced output, not per instance, by
tests/tools/test_case_study_recommender.py:
  test_no_headline_expresses_a_change_or_gap_as_a_bare_percentage
  test_the_divergence_headline_gap_is_reproducible_from_its_own_two_levels
  test_the_module_exposes_no_shared_bare_percentage_formatter
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


def _gap_points(entry):
    """The company-vs-SIM churn divergence in PERCENTAGE POINTS, or None if
    either level is missing (churn_estimate_error_pct is documented nullable in
    simulation/run_phase2b.py, and abs(None) is a crash, not a ranking).

    This is the quantity the "largest divergence" slot claims to rank by, and
    it is not the quantity it used to rank by. Ranking on the RATIO
    churn_estimate_error_pct = (company - sim)/sim divides by the sim
    probability, so it prefers whichever renewal had the SMALLEST denominator
    -- confident-when-nothing-happened -- over the largest actual divergence.
    Measured on the live book at the time of the fix: 6 of 13 households'
    within-household pick moved (C1, C2, C4, C7, C8, C9), C9's worst by ratio
    being a 5.0-point gap when its true worst was 12.2. The published winner
    (C_IC1, 91.8 points) happened to be the same household under both keys, so
    the public headline was right by luck rather than by construction; the
    deep-linked ?year= a reader lands on was not.
    """
    if not entry:
        return None
    sim = entry.get("sim_churn_probability")
    company = entry.get("company_churn_estimate")
    if sim is None or company is None:
        return None
    return abs(float(company) - float(sim)) * 100.0


def _max_divergence(sample_customers, cid):
    entry = sample_customers.get(cid) or dict()
    entries = [
        e for e in (entry.get("churn_accuracy_by_renewal") or [])
        if _gap_points(e) is not None
    ]
    if not entries:
        return None
    return max(entries, key=_gap_points)


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


def _silent_middle_drop(sample_customers, cid):
    """Phase RU (FEEDBACK_AND_REPUTATION.md): a household whose SIM-true
    satisfaction fell across the run but who never once responded to a
    solicited CSAT/NPS survey -- the company's measurement instrument has
    zero visibility into this decline. Requires at least one dispatched
    survey (so "never responded" is a real non-response, not a customer
    with no survey history at all)."""
    entries = (sample_customers.get(cid) or {}).get("feedback_survey_history") or []
    if len(entries) < 2:
        return None
    if any(e.get("csat_responded") or e.get("nps_responded") for e in entries):
        return None
    first_sat = entries[0].get("true_satisfaction")
    last_sat = entries[-1].get("true_satisfaction")
    if first_sat is None or last_sat is None or last_sat >= first_sat:
        return None
    return {"first": entries[0], "last": entries[-1], "drop": first_sat - last_sat}


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
            silent_middle=_silent_middle_drop(sample_customers, cid),
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


def _fmt_level(v):
    """A probability or score LEVEL, e.g. 0.0323 -> "3.2%". One decimal, not
    zero: the old formatter rounded 3.23% to "3%", so the gap it printed beside
    it was reproducible only from inputs the reader was never shown."""
    return "{:.1f}%".format(abs(float(v)) * 100.0)


def _fmt_points(v):
    """A DIFFERENCE between two levels, already in points, e.g. 91.77 ->
    "91.8 percentage points". The unit is inside the string so the figure
    cannot be read as a relative change -- see the module's unit doctrine."""
    return "{:.1f} percentage points".format(abs(float(v)))


def build(by_base, sample_customers):
    scored = _score_households(by_base, sample_customers)
    used = set()
    cases = []

    c = _pick(scored, used, lambda c: c["event_density"])
    if c:
        headline = str(c["event_density"]) + " timeline + reaction-chain entries on record"
        cases.append(dict(category="Most eventful journey", headline=headline, c=c, year=None))

    c = _pick(
        scored, used, lambda c: _gap_points(c["divergence"]),
        filt=lambda c: _gap_points(c["divergence"]) is not None,
    )
    if c:
        d = c["divergence"]
        headline = (
            _fmt_points(_gap_points(d)) + " apart at the " + d["term_start"][:4]
            + " renewal (sim " + _fmt_level(d["sim_churn_probability"])
            + " vs company " + _fmt_level(d["company_churn_estimate"]) + ")"
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

    c = _pick(
        scored, used, lambda c: c["silent_middle"]["drop"],
        filt=lambda c: c["silent_middle"] is not None,
    )
    if c:
        sm = c["silent_middle"]
        # sm["drop"] is first - last, a DIFFERENCE of two 0-1 satisfaction
        # scores. Published as "fell 12%" it read as a 12% relative fall; the
        # relative fall was 19%. Both levels are printed so the points figure
        # is reproducible from the headline's own numbers.
        headline = (
            "True satisfaction fell " + _fmt_points(sm["drop"] * 100.0) + " ("
            + _fmt_level(sm["first"]["true_satisfaction"]) + " in "
            + sm["first"]["term_start"][:4] + " to "
            + _fmt_level(sm["last"]["true_satisfaction"]) + " in "
            + sm["last"]["term_start"][:4]
            + ") but never once answered a survey -- invisible to the company's "
            "measurement instrument"
        )
        cases.append(dict(
            category="Silent-middle churn risk", headline=headline,
            c=c, year=int(sm["last"]["term_start"][:4]),
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
