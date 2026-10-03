"""Compare pricing RULES decision by decision: same customer, same moment, two rules.

REUSE: tools/decision_probe.py
CLASS: CUSTOM
INDEX: searched "decision probe", "counterfactual", "per decision" -- no existing row covers this.
       `tools/run_value_cycle_ab.py` is the book-level A/B this complements, not replaces: it
       runs each rule as its own arm, so the arms' books diverge the moment one keeps a customer
       the other loses, and by year ten they compare different populations.
       `company/analytics/counterfactual_retention.py` scores retention OFFERS, not price rules.

WHY (director, 2026-10-03). "The arms start with the same customers, but once one arm loses a
customer the other keeps, they hold different books." On the 2025 seeds, split survival paths
carried mean -4,753 and sd 3,677 per seed of the selection residual: the coin on whole remaining
lives, not decision quality. PROS-2016-0098 is that shape exactly.

WHAT THIS DOES. One engine run on the CONTROL path is the reference book. At every renewal the
probe:
  1. asks each rule what it would offer THIS customer NOW, from the same company observables (the
     pricing door is called again under the value arm's policy; the chain only appends to its own
     result object, so the reference run is unchanged);
  2. asks the WORLD its true P(stay) at each offer, re-asking `roll_lifecycle_event` with only
     the new rate changed, so the roll, the market, the household and its history are held fixed.
The row says what each rule would have earned on that customer at that moment, in expectation, with
no coin. Scoring is offline and microseconds per decision, so any number of rules can be compared
on one run.

THE HARNESS MAY READ THE WORLD'S TRUTH; THE COMPANY NEVER SEES IT. Both bindings are wrapped on
`simulation.run_phase2b`, the runner's own names, from here, so `simulation/` gains no import of
`company/` and the company decides exactly as it does in a live run.

WHAT IT DOES NOT YET COUNT, said so it is not read as counted: bad debt (a household's true
non-payment scales with the bill and is not in these rows), and continuation value (a customer kept
renews again). The first is a column to add. The second is the honest limit of a one-term,
per-decision score, and it is the price of holding the book fixed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
from pathlib import Path

RULES = ("flat", "value", "value_blind")
#: The value arm with the company's payment history taken away -- arrears state, unpaid bills and
#: payment method stripped from the door, exactly what it saw before e0370bf94. Scored against
#: "value" on the same decision, it is the payment-history fix measured rule against rule.
PAYMENT_HISTORY_ARGS = ("arrears_state", "receivable", "payment_method")
#: The flat-at-level margins each decision is also priced at, GBP/MWh. The book-level A/B holds its
#: third arm at the value arm's own MEDIAN margin, which is only known after the value arm has
#: chosen; recording a grid lets `score` take the level the value rule actually produced, after
#: the run, without a second pass. A 5 GBP step keeps the chosen level within 2.5 of the median.
LEVEL_GRID = tuple(range(5, 155, 5))

#: The reference run's own renewal outcomes from the last `probe()`, as (customer, date, outcome):
#: what the control proves equals a plain run's, i.e. that probing moved nothing.
LAST_REFERENCE_EVENTS: list = []


def _annual_mwh(records, customer_id: str, commodity: str, term_start: str) -> float | None:
    start = (dt.date.fromisoformat(term_start[:10]) - dt.timedelta(days=365)).isoformat()
    kwh = [r.get("consumption_kwh") for r in records
           if isinstance(r, dict) and r.get("customer_id") == customer_id
           and r.get("commodity", commodity) == commodity
           and start <= str(r.get("settlement_date", ""))[:10] < term_start[:10]
           and isinstance(r.get("consumption_kwh"), (int, float))]
    return sum(kwh) / 1000.0 if kwh else None


def probe(report_end: str | None = None, roll_seed: int | None = None) -> list[dict]:
    """Run the control path once and return one row per probed renewal.

    `roll_seed` re-draws every account's renewal dice (`churn_roll_for_renewal`) at that seed, as
    the A/B's churn-roll noise floor does: the same book and world, a different reference PATH. It
    never touches a rule's offer or the world's P(stay); it changes which renewals happen.
    """
    import random
    from dataclasses import replace

    import simulation.customer_events as events
    import simulation.run_phase2b as runner
    from company.policy.decision_policy import CURRENT_POLICY, VALUE_ARM_POLICY, policy_scope
    from company.pricing.value_based_renewal import FLAT_AT_LEVEL
    from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

    offers: dict[tuple, dict] = {}
    rows: list[dict] = []
    real_price, real_roll = runner.decide_renewal_rate, runner.roll_lifecycle_event

    def priced(**kw):
        result = real_price(**kw)
        if kw.get("term_index", 0) >= 1 and kw.get("struck_unit_rate_gbp_per_mwh"):
            with policy_scope(VALUE_ARM_POLICY):
                value = real_price(**kw)
                blind = real_price(**{k: v for k, v in kw.items()
                                      if k not in PAYMENT_HISTORY_ARGS})
            levels = {}
            for level in LEVEL_GRID:
                with policy_scope(replace(CURRENT_POLICY, name="level_arm",
                                          renewal_margin_arm=FLAT_AT_LEVEL,
                                          renewal_margin_flat_level_gbp_per_mwh=float(level))):
                    levels[level] = real_price(**kw).unit_rate_gbp_per_mwh
            offers[(kw["customer_id"], kw["term_start"][:10], kw["commodity"])] = {
                "billing_account": kw["billing_account"],
                "base_gbp_per_mwh": float(kw["struck_unit_rate_gbp_per_mwh"])
                - TARGET_MARGIN_GBP_PER_MWH,
                "offer": {"flat": result.unit_rate_gbp_per_mwh,
                          "value": value.unit_rate_gbp_per_mwh,
                          "value_blind": blind.unit_rate_gbp_per_mwh},
                "levels": levels,
                # WHAT THE COMPANY BELIEVED about this customer staying, at its own offer: the
                # value arm's churn belief, set beside the world's truth so the belief error is
                # measured per decision. None where the arm declined or did not price.
                "believed_p_retain": next((e.get("believed_p_retain")
                                           for e in reversed(value.value_arm_entries)
                                           if e.get("believed_p_retain") is not None), None),
            }
        return result

    def rolled(cid, term_start_str, commodity, records, customers, **kw):
        event = real_roll(cid, term_start_str, commodity, records, customers, **kw)
        held = offers.pop((cid, term_start_str[:10], commodity), None)
        if held is None:
            return event
        p = {}
        for rule in RULES:
            asked = {**kw, "new_rate_gbp_per_mwh": held["offer"][rule], "retention_modifier": None}
            p[rule] = real_roll(cid, term_start_str, commodity, records, customers,
                                **asked)["effective_retention_probability"]
        level_p = {}
        for level, offer in held["levels"].items():
            asked = {**kw, "new_rate_gbp_per_mwh": offer, "retention_modifier": None}
            level_p[level] = real_roll(cid, term_start_str, commodity, records, customers,
                                       **asked)["effective_retention_probability"]
        rows.append({
            "customer_id": cid, "billing_account": held["billing_account"],
            "term_start": term_start_str[:10], "commodity": commodity,
            "annual_mwh": _annual_mwh(records, cid, commodity, term_start_str),
            "base_gbp_per_mwh": round(held["base_gbp_per_mwh"], 4),
            "offer_gbp_per_mwh": {k: round(v, 4) for k, v in held["offer"].items()},
            "true_p_retain": p,
            "believed_p_retain_value": held["believed_p_retain"],
            "level_grid": {str(lv): {"offer": round(o, 4), "p": level_p[lv]}
                           for lv, o in held["levels"].items()},
        })
        return event

    runner.decide_renewal_rate, runner.roll_lifecycle_event = priced, rolled
    real_dice = events.churn_roll_for_renewal
    if roll_seed is not None:
        events.churn_roll_for_renewal = lambda account, term_start: random.Random(
            f"probe_roll:{roll_seed}:{account}:{term_start}").random()
    try:
        with policy_scope(CURRENT_POLICY):
            # THROUGH PHASE 4C, because that is where the world's EMERGENT bad debt is booked. The
            # settlement pass's own `bad_debt_gbp` is a flat placeholder (1-6% by segment) and
            # read alone it showed every household as an ordinary payer.
            from simulation.run_phase4c_on_phase2b import main as run_phase4c
            phase2b = run_phase4c(report_end=report_end, policy=CURRENT_POLICY)["phase2b"]
    finally:
        runner.decide_renewal_rate, runner.roll_lifecycle_event = real_price, real_roll
        events.churn_roll_for_renewal = real_dice
    LAST_REFERENCE_EVENTS[:] = sorted(
        (e["customer_id"], e["event_date"], e["event_type"])
        for e in phase2b.get("customer_events") or [] if isinstance(e, dict))
    # THE WORLD'S OWN VERDICT ON EACH HOUSEHOLD'S PAYING, from the reference run: what the arrears
    # engine wrote off or provisioned for it, over the revenue it was billed. A truth the company
    # never sees; the harness may.
    revenue: dict[str, float] = {}
    for rec in phase2b.get("all_records") or []:
        if isinstance(rec, dict) and rec.get("customer_id"):
            revenue[rec["customer_id"]] = revenue.get(rec["customer_id"], 0.0) + float(
                rec.get("revenue_gbp") or 0.0)
    billed: dict[str, tuple[float, float]] = {}
    for cid, lines in (phase2b.get("arrears_lines_by_customer") or {}).items():
        lost = (float(lines["write_off_at_close_gbp"]) + float(lines["write_off_statute_barred_gbp"])
                + float(lines["stayer_provision_gbp"]) - float(lines["unbooked_bad_debt_gbp"])
                - (float(lines["dca_recovery_gbp"]) - float(lines["unbooked_recovery_gbp"])))
        billed[cid] = (max(0.0, lost), revenue.get(cid, 0.0))
    later: dict[tuple, int] = {}
    for r in rows:
        later[(r["customer_id"], r["commodity"])] = later.get((r["customer_id"], r["commodity"]), 0) + 1
    seen: dict[tuple, int] = {}
    for r in rows:
        bd, rev = billed.get(r["customer_id"], (0.0, 0.0))
        r["true_bad_debt_share"] = round(bd / rev, 5) if rev > 0 else None
        k = (r["customer_id"], r["commodity"])
        seen[k] = seen.get(k, 0) + 1
        # How many MORE renewals this customer had on the reference path: a stand-in for what
        # keeping them is worth beyond this term. An estimate, scored as a range, never alone.
        r["reference_renewals_after"] = later[k] - seen[k]
    return rows


def expected_term_margin_gbp(row: dict, rule: str, bad_debt: bool = True,
                             continuation: bool = False) -> float | None:
    """What `rule` would have earned on this customer, in expectation, from this decision.

    Stay: the term's margin over the shared base x annual volume, less the household's TRUE
    bad-debt share of the bill it is charged (a higher price is a bigger unpaid bill). With
    `continuation`, keeping them is also worth their remaining reference-path renewals at the flat
    rule's margin, the same for both rules, so the only thing a rule moves is the chance of
    keeping it. Leave: nothing. No coin is rolled; the world's P(stay) weights both branches.
    """
    vol = row.get("annual_mwh")
    if not vol:
        return None
    offer = row["offer_gbp_per_mwh"][rule]
    stay = (offer - row["base_gbp_per_mwh"]) * vol
    if bad_debt and row.get("true_bad_debt_share") is not None:
        stay -= row["true_bad_debt_share"] * offer * vol
    if continuation:
        flat_margin = (row["offer_gbp_per_mwh"]["flat"] - row["base_gbp_per_mwh"]) * vol
        stay += row.get("reference_renewals_after", 0) * flat_margin
    return row["true_p_retain"][rule] * stay


def value_median_margin(rows: list[dict]) -> float | None:
    """The value rule's median chosen margin over the decisions it priced: the level the book-level
    A/B holds its third arm at, taken from THIS book."""
    m = [r["offer_gbp_per_mwh"]["value"] - r["base_gbp_per_mwh"] for r in rows
         if r["offer_gbp_per_mwh"]["value"] != r["offer_gbp_per_mwh"]["flat"]]
    return statistics.median(m) if m else None


def with_level(rows: list[dict], level: float) -> list[dict]:
    """Rows with a `level` rule added at the grid point nearest `level`."""
    out = []
    for r in rows:
        grid = r.get("level_grid") or {}
        if not grid:
            continue
        key = min(grid, key=lambda k: abs(float(k) - level))
        out.append({**r,
                    "offer_gbp_per_mwh": {**r["offer_gbp_per_mwh"], "level": grid[key]["offer"]},
                    "true_p_retain": {**r["true_p_retain"], "level": grid[key]["p"]}})
    return out


def score(rows: list[dict], a: str = "value", b: str = "flat", resamples: int = 2000,
          seed: int = 7, **terms) -> dict:
    """Per-decision difference a - b, summed, with a bootstrap over ACCOUNTS (an account's
    renewals are resampled together, so one customer's decisions are never treated as
    independent of each other)."""
    import random
    by_account: dict[str, float] = {}
    n = 0
    for r in rows:
        ea, eb = expected_term_margin_gbp(r, a, **terms), expected_term_margin_gbp(r, b, **terms)
        if ea is None or eb is None:
            continue
        by_account[r["billing_account"]] = by_account.get(r["billing_account"], 0.0) + ea - eb
        n += 1
    accounts = list(by_account.values())
    total = sum(accounts)
    rng = random.Random(seed)
    boots = [sum(rng.choice(accounts) for _ in accounts) for _ in range(resamples)] if accounts else []
    sd = statistics.stdev(boots) if len(boots) > 1 else None
    return {"decisions": n, "accounts": len(accounts), "total_gbp": round(total, 2),
            "bootstrap_sd_gbp": round(sd, 2) if sd else None,
            "snr": round(abs(total) / sd, 2) if sd else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--end-year")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--world", default=None,
                    help="the SPINE_1 world a run past the record lives through, e.g. neso_central")
    ap.add_argument("--roll-seed", type=int, default=None,
                    help="re-draw every renewal's dice at this seed (same book, different path)")
    args = ap.parse_args(argv)
    report_end = f"{args.end_year}-12-31" if args.end_year else None
    if args.world:
        # PAST THE RECORD, inside one named world, as the A/B does with --world: every rule and
        # every re-asked roll reads the same forward prices and analogue-year weather.
        from simulation.run_scenario import forward_world
        if not report_end:
            print("REFUSED: --world names a forward world; give --end-year past 2025.")
            return 2
        with forward_world(args.world, report_end):
            rows = probe(report_end, roll_seed=args.roll_seed)
    else:
        rows = probe(report_end, roll_seed=args.roll_seed)
    level = value_median_margin(rows)
    levelled = with_level(rows, level) if level is not None else []
    result = {"rows": rows, "value_median_margin_gbp_per_mwh": level,
              "score_value_vs_flat": {
                  "margin_only": score(rows, bad_debt=False),
                  "with_bad_debt": score(rows),
                  "with_bad_debt_and_continuation": score(rows, continuation=True)},
              "score_payment_history": {
                  "with_bad_debt": score(rows, a="value", b="value_blind"),
                  "with_bad_debt_and_continuation": score(rows, a="value", b="value_blind",
                                                          continuation=True)},
              "score_value_vs_level": {
                  "margin_only": score(levelled, b="level", bad_debt=False),
                  "with_bad_debt": score(levelled, b="level"),
                  "with_bad_debt_and_continuation": score(levelled, b="level", continuation=True)},
              }
    args.out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("value_median_margin_gbp_per_mwh",
                                              "score_value_vs_flat", "score_value_vs_level",
                                              "score_payment_history")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
