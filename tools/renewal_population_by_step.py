"""How many accounts survive each step of the renewal decision, year by year, in one run.

    python3 -m tools.renewal_population_by_step [run_output.json]

A run's retention log answers "how many offers", and the B8 holdout log answers "how many coin
flips". Neither says where the rest of the book went. This counts the four steps the run loop takes
at every term boundary on a household's decision leg, each from the log that step writes:

1. ``term_ended``: a fixed term ended and the next term started (`account_state_log`, the new
   row's ``term_index >= 1``, the previous row on that supply point ``fixed``). A term that follows
   an SVT segment is not a fixed term ending; it is counted on its own as ``after_svt``.
2. ``reached_decision``: the company estimated churn and the world rolled for departure
   (`customer_events`, the renewal event dated that term start). A fixed term rolls onto the
   default (`svt`) or an indexed tariff when the next row is one, and then there is no decision.
3. ``considered``: the company's own estimate was above `RETENTION_THRESHOLD`, so the guard looked
   at an offer (the same event's ``company_churn_estimate``).
4. ``offered``: an offer was made (`retention_log`).

The steps are counted INDEPENDENTLY from their own logs and then matched to the step before.
A row that has no match at the previous step goes to ``unmatched`` rather than being dropped. A
non-zero there means the logs disagree about the population, and that is a finding, not noise.

Context rows that bear on the reasons the population falls: ``live_accounts`` (decision-leg
accounts holding a term that starts in the year), ``rolled_to_default`` (fixed terms whose next
row is indexed), and ``no_offer_reasons`` (why a considered leaver got no offer, from
`no_offer_churn_log`). The published run carries no reason for a considered household that stayed
without an offer, so the 10-10 gate's refusals are visible among leavers only.

This reads world-side fields only to find the population (dates, tariff types, which events
exist), plus the company's own estimate. It reads no ground-truth probability.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

# The run loop's own constant. Imported rather than copied so the tool cannot drift from the gate.
from simulation.run_phase2b import RETENTION_THRESHOLD

STEPS = ("term_ended", "reached_decision", "considered", "offered")
# `run_phase2b._indexed_tariff`: no renewal decision follows a term of these types.
INDEXED_TARIFFS = frozenset({"deemed", "flex", "svt"})
DEFAULT_RUN = Path("docs/reports/run_output_latest.json")


def _decision_legs(account_state_log: list[dict]) -> dict[str, str]:
    """`customer_events.departure_decision_leg`: electricity where the account has an electricity
    leg, gas otherwise."""
    fuels: dict[str, set[str]] = defaultdict(set)
    for row in account_state_log:
        fuels[row["billing_account"]].add(row["commodity"])
    return {acct: ("electricity" if "electricity" in f else "gas") for acct, f in fuels.items()}


def population_by_step(run: dict) -> dict:
    """Per-year counts of distinct accounts at each step, by route, plus what no step could match."""
    states = run.get("account_state_log") or []
    legs = _decision_legs(states)
    account_of = {row["customer_id"]: row["billing_account"] for row in states}
    # A spliced default stint repeats its `term_index`, so a supply point's terms are ordered by
    # date, never keyed by index.
    by_point: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in states:
        if row["commodity"] == legs[row["billing_account"]]:
            by_point[(row["customer_id"], row["commodity"])].append(row)

    def per_year() -> dict[str, set]:
        return defaultdict(set)

    fixed = {s: per_year() for s in STEPS}
    default = {s: per_year() for s in STEPS[1:]}
    context = {k: per_year() for k in ("live_accounts", "fixed_to_default_with_no_decision")}
    unmatched = {"event_at_no_boundary": 0, "offer_at_no_considered_decision": 0}

    fixed_ended: dict[tuple[str, str], str] = {}  # (account, date) -> next term's tariff type
    on_default: set[tuple[str, str]] = set()  # a boundary inside or at the end of a default stint
    for terms in by_point.values():
        terms.sort(key=lambda r: (r["term_start"], r["term_end"]))
        for prev, row in zip([None, *terms], terms):
            acct, start = row["billing_account"], row["term_start"]
            context["live_accounts"][start[:4]].add(acct)
            if prev is not None and prev["tariff_type"] not in INDEXED_TARIFFS:
                fixed["term_ended"][start[:4]].add(acct)
                fixed_ended[(acct, start)] = row["tariff_type"]
            elif prev is not None:
                on_default.add((acct, start))

    decided: dict[tuple[str, str], str] = {}  # (account, date) -> route
    considered: set[tuple[str, str]] = set()
    for event in run.get("customer_events") or []:
        acct = account_of.get(event["customer_id"], event["customer_id"])
        if event.get("commodity", legs.get(acct)) != legs.get(acct):
            continue
        key = (acct, event["event_date"])
        # The route is the term the boundary ENDS, not the event's occasion label: a household
        # on the default that declines a fix at its anniversary is booked `declined_fix`, the
        # same label as one declining at the end of a fixed term.
        if key in fixed_ended:
            route = fixed
        elif key in on_default:
            route = default
        else:
            unmatched["event_at_no_boundary"] += 1
            continue
        decided[key] = "default" if route is default else "fixed"
        route["reached_decision"][key[1][:4]].add(acct)
        estimate = event.get("company_churn_estimate")
        if estimate is not None and estimate > RETENTION_THRESHOLD:
            considered.add(key)
            route["considered"][key[1][:4]].add(acct)

    for key, next_tariff in fixed_ended.items():
        if key not in decided and next_tariff in INDEXED_TARIFFS:
            context["fixed_to_default_with_no_decision"][key[1][:4]].add(key[0])

    for offer in run.get("retention_log") or []:
        key = (account_of.get(offer["customer_id"], offer["customer_id"]), offer["event_date"])
        if key not in considered:
            unmatched["offer_at_no_considered_decision"] += 1
            continue
        (default if decided[key] == "default" else fixed)["offered"][key[1][:4]].add(key[0])

    reasons: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in run.get("no_offer_churn_log") or []:
        reasons[row["event_date"][:4]][row.get("no_offer_reason") or "none"] += 1

    years = sorted({y for group in (fixed, default, context) for c in group.values() for y in c})
    return {
        "producing_commit": (run.get("producing_commit") or {}).get("commit"),
        "retention_threshold": RETENTION_THRESHOLD,
        "years": {
            y: {
                "fixed_term": {s: len(fixed[s].get(y, ())) for s in STEPS},
                "default_anniversary": {s: len(default[s].get(y, ())) for s in STEPS[1:]},
                **{k: len(context[k].get(y, ())) for k in context},
                "no_offer_leavers": dict(reasons.get(y, {})),
            }
            for y in years
        },
        "unmatched": unmatched,
    }


def render(result: dict) -> str:
    lines = [f"run {result['producing_commit']}, threshold {result['retention_threshold']}",
             "year  fixed term: ended > decided > considered > offered   "
             "default anniversary: decided > considered > offered   "
             "fixed-to-default with no decision   live accounts   no-offer leavers"]
    for y, row in result["years"].items():
        f, d = row["fixed_term"], row["default_anniversary"]
        lines.append(
            f"{y}  {' > '.join(f'{f[s]:>3}' for s in STEPS):<46}"
            f"{' > '.join(f'{d[s]:>3}' for s in STEPS[1:]):<52}"
            f"{row['fixed_to_default_with_no_decision']:>34}   {row['live_accounts']:>13}   "
            f"{row['no_offer_leavers']}")
    lines.append(f"unmatched: {result['unmatched']}")
    return "\n".join(lines)


def load_run(path: Path) -> dict:
    """The run's payload, parsed. Kept apart from the counting so the counter only ever holds a
    dict: `substring_source_scan_census` follows file text into a callee's parameters, and read
    every membership test below as a scan of source text."""
    return json.loads(path.read_text())


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    print(render(population_by_step(load_run(Path(args[0]) if args else DEFAULT_RUN))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
