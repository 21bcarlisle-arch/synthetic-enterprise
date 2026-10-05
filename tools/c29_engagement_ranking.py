"""C29: does the per-account engagement estimate rank households better than payment channel alone?

REUSE: tools/c29_engagement_ranking.py
CLASS: CUSTOM
INDEX: searched "engagement", "rank", "spearman". `tools/engagement_separation` supplies the
       household list and the way the world's engagement trait is read. Its shuffle null is for
       ONE correlation, and this grades a DIFFERENCE of two, so the null here shuffles the record.
       `tools/r1_inference_ceiling.newest_run_output` finds the run. The estimator is
       `company/crm/engagement_estimate`, and nothing here re-derives it.

THREE ARMS, ONE SCORE. Each is the Spearman correlation with the world's trait
(`household_segments.active_renewal_probability_for_customer`) of the estimate, minus the same
correlation for the channel's rate. That difference is the LIFT.

    book      the latest run's own record. The company's term history per electricity account,
              departures at a renewal from `customer_events`, and the channel from its own bills.
              Graded against a null that shuffles each account's outcomes among accounts on the
              same channel. That keeps every channel's rate and every account's anniversary count,
              and destroys only which household made which choices.
    world     every household on the live book, rolled at each anniversary by the world's own
              `renewal_engagement.rolls_active_renewal` with its own trait. The FTC withdrawal
              window's forced rolls are included. This is the planted arm, and it needs no run.
    null      the same rolls, at the household's CHANNEL rate rather than its own trait. Nothing
              per-account is left to find, so the lift must not be positive.

    python3 -m tools.c29_engagement_ranking            # the book arm, against the newest run
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from company.crm.engagement_estimate import (  # noqa: E402
    CHOSE,
    ROLLED,
    estimate_engagement,
    renewal_outcomes_from_terms,
)

#: Shuffles in the book arm's null, and its seed, fixed so the published band reproduces.
NULL_SHUFFLES = 200
NULL_SEED = 20261005
#: The world arm's first anniversary: the book's own acquisitions start on 2016-01-01, and a term
#: is `settlement.CONTRACT_LENGTH_DAYS` long.
FIRST_ACQUISITION = date(2016, 1, 1)


def _spearman(xs: list[float], ys: list[float]) -> float:
    from scipy.stats import spearmanr

    return float(spearmanr(xs, ys).statistic)


def lift(estimates: dict, truth: dict[str, float]) -> dict:
    ids = sorted(estimates)
    t = [truth[i] for i in ids]
    channel = _spearman([estimates[i].channel_rate for i in ids], t)
    own = _spearman([estimates[i].estimate for i in ids], t)
    return {"channel_rho": round(channel, 4), "estimate_rho": round(own, 4),
            "lift": round(own - channel, 4), "accounts": len(ids),
            "reached_no_anniversary": sum(1 for i in ids if not estimates[i].anniversaries)}


def _truth(ids) -> dict[str, float]:
    from simulation.household import household_of
    from simulation.household_segments import active_renewal_probability_for_customer

    return {i: active_renewal_probability_for_customer(household_of(i)) for i in ids}


def book_record(payload: dict) -> tuple[dict[str, list[str]], dict[str, str]]:
    """(outcomes, channel) per electricity account, read only from what the company recorded."""
    from simulation.settlement import CONTRACT_LENGTH_DAYS

    terms: dict[str, list[dict]] = defaultdict(list)
    for row in payload.get("account_state_log", []):
        if row.get("commodity") == "electricity":
            terms[row["customer_id"]].append(row)
    left_at_renewal = {r["customer_id"]: True for r in payload.get("customer_events", [])
                       if r.get("commodity") == "electricity" and r.get("event_type") == "churned"
                       and r.get("departure_occasion") == "renewal"}
    channel: dict[str, str] = {}
    for bill in payload.get("bills", []):
        if bill.get("commodity") == "electricity" and bill.get("payment_channel"):
            channel.setdefault(bill["customer_id"], bill["payment_channel"])
    accounts = sorted(set(terms) & set(channel))
    outcomes = {c: renewal_outcomes_from_terms(terms[c], contract_length_days=CONTRACT_LENGTH_DAYS,
                                               left_at_renewal=left_at_renewal.get(c, False))
                for c in accounts}
    return outcomes, {c: channel[c] for c in accounts}


def shuffled_within_channel(outcomes, channel, rnd: random.Random) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for acc in sorted(outcomes):
        groups[channel[acc]].append(acc)
    out: dict[str, list[str]] = {}
    for accs in groups.values():
        seqs = [outcomes[a] for a in accs]
        rnd.shuffle(seqs)
        out.update(zip(accs, seqs))
    return out


def measure_book(payload: dict) -> dict:
    outcomes, channel = book_record(payload)
    truth = _truth(outcomes)
    result = lift(estimate_engagement(outcomes, channel), truth)
    rnd = random.Random(NULL_SEED)
    draws = sorted(
        lift(estimate_engagement(shuffled_within_channel(outcomes, channel, rnd), channel),
             truth)["lift"]
        for _ in range(NULL_SHUFFLES))
    result["null_lift_low"] = draws[int(0.025 * NULL_SHUFFLES)]
    result["null_lift_high"] = draws[int(0.975 * NULL_SHUFFLES)]
    result["above_the_null"] = result["lift"] > result["null_lift_high"]
    return result


def world_rolls(anniversaries: int, *, at_channel_rate: bool) -> tuple[dict, dict, dict]:
    """(outcomes, channel, truth) for every household on the live book, rolled by the world.

    `at_channel_rate` replaces each household's own probability with the mean of its channel's.
    Each channel's level survives and the per-household signal does not, which makes this the null.
    """
    from simulation.household_segments import payment_channel_for_customer
    from simulation.renewal_engagement import rolls_active_renewal
    from simulation.settlement import CONTRACT_LENGTH_DAYS
    from tools.engagement_separation import households

    ids = households()
    truth = _truth(ids)
    channel = {h: payment_channel_for_customer(h).value for h in ids}
    probability = roll_probabilities(truth, channel, at_channel_rate=at_channel_rate)
    outcomes = {h: [
        CHOSE if rolls_active_renewal(
            (FIRST_ACQUISITION + timedelta(days=CONTRACT_LENGTH_DAYS * k)).isoformat(),
            f"c29_{h}_{k}", probability[h]) else ROLLED
        for k in range(1, anniversaries + 1)] for h in ids}
    return outcomes, channel, truth


def roll_probabilities(truth: dict[str, float], channel: dict[str, str], *,
                       at_channel_rate: bool) -> dict[str, float]:
    """The probability each household is rolled with: its own, or its channel's mean of them."""
    if not at_channel_rate:
        return dict(truth)
    by_channel: dict[str, list[float]] = defaultdict(list)
    for h, p in truth.items():
        by_channel[channel[h]].append(p)
    channel_mean = {c: sum(v) / len(v) for c, v in by_channel.items()}
    return {h: channel_mean[channel[h]] for h in truth}


def measure_world(anniversaries: int, *, at_channel_rate: bool) -> dict:
    outcomes, channel, truth = world_rolls(anniversaries, at_channel_rate=at_channel_rate)
    return lift(estimate_engagement(outcomes, channel), truth)


def main() -> int:
    from tools.r1_inference_ceiling import newest_run_output

    path = newest_run_output()
    out = {"run_output": path.name,
           "book": measure_book(json.loads(path.read_text(encoding="utf-8"))),
           "world_5": measure_world(5, at_channel_rate=False),
           "null_5": measure_world(5, at_channel_rate=True)}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
