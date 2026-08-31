#!/usr/bin/env python3
"""Grade the company's renewal churn belief against the world's outcome, over EVERY renewal.

REUSE: tools/grade_renewal_churn_belief.py
CLASS: CUSTOM
INDEX: searched "belief", "calibration", "AUC", "discrimination", "churn", "grade", "bucket",
       "outcome". `tools/run_value_cycle_ab.py::belief_vs_outcome` is the nearest organ and is
       NOT extended: its subject is the VALUE ARM's own logged `believed_p_retain`, it reads
       `value["phase2b"]["value_arm_log"]`, and it therefore cannot run at all on a control run
       (`renewal_margin_arm="flat_rules"`) because the arm priced nothing. This module's subject
       is the belief that exists whether or not any arm runs -- `saas.churn_model.build_churn_risk`,
       logged per renewal by `simulation.customer_events.roll_lifecycle_event` as
       `churn_probability` -- and its population is EVERY renewal the world rolled, which on the
       control book is 478 against the arm's 25. The tie convention (a tie counts a half) and the
       bucket edges (`min(int(p * 5), 4) / 5`) are copied from `belief_vs_outcome` DELIBERATELY so
       the two artefacts' numbers are read on the same scale; folding one into the other is a
       remediation-on-touch for whichever is edited next, not a change to make while the A/B's
       published figures are the live citation. `tools/run_price_ladder.py` was read and is not
       this: it moves PRICE and measures a slope across rungs, needing a decade run per rung; this
       reads one finished run and moves nothing.

WHY THIS EXISTS
---------------
Four separately published numbers all rest on one belief, and every one of them was measured on a
population small enough to be an artefact:

  * the A/B's `discrimination_auc` 0.4653 -- 25 priced renewals, 9 of them departures. BOUNDED
    2026-08-30: the exact null on 16-vs-9 runs 0.264..0.736, so that figure is two-sided p 0.80 --
    the population was small enough to be an artefact and now says so on the page. The same
    estimator on the 2026-08-29 run scored 0.13 on 20 decisions, which IS outside its null, and
    five of the ten accounts behind it were driven out by the arm's own price rise.
  * its bucket table's INVERSION at believed p_retain 0.346/0.557/0.616 -- n=11, n=4, n=4
  * the ladder's level error, believed 33% against a realised 5.5%
  * the arm's calibration error -0.0774

None of the four is a measurement of the belief itself. They are measurements of the belief AS
FILTERED THROUGH the arm's decision to price -- and the arm priced 25 of 478 renewals. The world
rolled a churn decision at every one of the other 453 too, and logged both the belief and the
outcome each time. This grades the belief on all of them.

WHAT IS BEING GRADED, EXACTLY
-----------------------------
`roll_lifecycle_event` calls `build_churn_risk(records_so_far, customers, through_period=<the
month being priced>)` and stamps the result on the event as `churn_probability`. `records_so_far`
stops before the term being priced BY CONSTRUCTION at the call site in
`simulation/run_phase2b.py`, so the belief is Point-in-Time safe without this module having to
re-derive it. That the logged number really is that function's output is CHECKED and not assumed:
`build_churn_risk` can only return `BASE_ANNUAL_CHURN_PROBABILITY + k * CHURN_UPLIFT_PER_BILL_SHOCK`
for an integer k, so every graded belief must land on that lattice, and the recovered k IS the
bill-shock count -- which is what makes the mechanism testable from the same pairs.

THE INDEPENDENCE QUESTION, ANSWERED BEFORE A READER RAISES IT (R15 TAUTOLOGY)
-----------------------------------------------------------------------------
The world's roll is NOT independent of this belief. `roll_lifecycle_event` seeds
`effective_p_retain` from the same `build_churn_risk` number and then multiplies it through the
passive cap, the market-year switching multiplier, the price-position multiplier, income stress
and satisfaction. So a grade of belief against OUTCOME here is not "a forecast against an
unrelated tally" the way `belief_vs_outcome` is for the arm's log; it is a measurement of whether
the world's own adjustment chain preserves the ordering and the level of the base rate it starts
from. That is a weaker claim and it is the honest one, so it is published as
`independence.reading` in the artefact rather than left for a reader to discover.

Two things follow, and both are computed here:

  * the ORACLE CEILING. The world's own fully-adjusted `realized_churn_probability` is graded by
    the identical statistic. It is the best any belief could do on this population, so it converts
    "AUC 0.56 is low" from an assertion into a comparison. Without it, a low AUC is equally
    consistent with 37 departures being unrankable noise.
  * the ATTENUATION. Because the world publishes its true post-adjustment probability per renewal,
    the belief can be graded against a PROBABILITY and not only against a binary outcome. 478
    probability pairs carry far more signal than 37 departures, and the slope between them says
    directly how much of the belief's assumed dose-response the world actually delivers.

R12: every figure here is a DIAGNOSTIC. Nothing in this module writes to `BASE_ANNUAL_CHURN_
PROBABILITY`, `CHURN_UPLIFT_PER_BILL_SHOCK` or any cap, and the AUC is never a thing to move.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from saas.churn_model import (
    BASE_ANNUAL_CHURN_PROBABILITY,
    CHURN_UPLIFT_PER_BILL_SHOCK,
    MAX_BILL_SHOCK_CHURN_PROBABILITY,
)

DEFAULT_RUN_OUTPUT = Path("docs/reports/run_output_latest.json")
DEFAULT_ARTEFACT = Path("docs/observability/renewal_churn_belief_grade.json")

#: The lattice tolerance. The logged belief is rounded to 4dp by `roll_lifecycle_event`, so a
#: value on the lattice can sit up to 5e-5 off it; anything further away did not come out of
#: `churn_probability()` and the bill-shock count behind it is not recoverable.
LATTICE_TOLERANCE = 1e-4


def recover_bill_shock_count(believed_churn: float) -> int | None:
    """Invert `saas.churn_model.churn_probability` to the bill-shock count behind a belief.

    Returns None when the value is not on the model's lattice, or when it sits at the cap (where
    the inversion is many-to-one and the count is genuinely unrecoverable). None is a REFUSAL and
    is counted in the artefact -- never silently treated as zero, which would move every
    off-lattice belief into the model's own base-rate bucket and make the mechanism table read as
    if it had a population it does not have.
    """
    if believed_churn >= MAX_BILL_SHOCK_CHURN_PROBABILITY - LATTICE_TOLERANCE:
        return None
    steps = (believed_churn - BASE_ANNUAL_CHURN_PROBABILITY) / CHURN_UPLIFT_PER_BILL_SHOCK
    nearest = round(steps)
    if nearest < 0 or abs(steps - nearest) > LATTICE_TOLERANCE / CHURN_UPLIFT_PER_BILL_SHOCK:
        return None
    return int(nearest)


def rank_auc(scores_positive: list[float], scores_negative: list[float]) -> float | None:
    """Mann-Whitney AUC with ties counting a half. None when either class is empty.

    None rather than 0.5 on an empty class, because 0.5 is the value a real measurement takes when
    a belief carries no information, and a statistic that cannot be computed must not be
    indistinguishable from one that was computed and came out uninformative (R15 FAIL-OPEN).
    """
    if not scores_positive or not scores_negative:
        return None
    wins = sum(
        (p > n) + 0.5 * (p == n)
        for p in scores_positive
        for n in scores_negative
    )
    return wins / (len(scores_positive) * len(scores_negative))


def _bucket_table(rows: list[dict], belief_key: str) -> list[dict]:
    """Believed-p_retain quintiles, with the ACCOUNT count behind each one.

    The account count is the field that decides whether a bucket is a finding or a coincidence: 11
    renewals from 3 accounts is 3 households and a renewal schedule, not 11 independent draws.
    """
    buckets: dict[float, dict] = collections.defaultdict(
        lambda: {"n": 0, "retained": 0, "believed": 0.0, "accounts": set()}
    )
    for row in rows:
        p_retain = 1.0 - row[belief_key]
        edge = min(int(p_retain * 5), 4) / 5.0
        bucket = buckets[edge]
        bucket["n"] += 1
        bucket["retained"] += int(row["retained"])
        bucket["believed"] += p_retain
        bucket["accounts"].add(row["account"])
    return [
        {
            "believed_p_retain_from": edge,
            "believed_p_retain_to": round(edge + 0.2, 1),
            "n": b["n"],
            "accounts": len(b["accounts"]),
            "mean_believed_p_retain": b["believed"] / b["n"],
            "realised_retention_rate": b["retained"] / b["n"],
            "left": b["n"] - b["retained"],
        }
        for edge, b in sorted(buckets.items())
    ]


def grade_belief(rows: list[dict], belief_key: str, label: str) -> dict:
    """Calibration, discrimination and the bucket table for one believed churn probability."""
    if not rows:
        raise ValueError("grade_belief: empty population")
    believed_churn = [row[belief_key] for row in rows]
    stayed = [1.0 - row[belief_key] for row in rows if row["retained"]]
    left = [1.0 - row[belief_key] for row in rows if not row["retained"]]
    mean_believed_churn = sum(believed_churn) / len(believed_churn)
    realised_churn_rate = sum(1 for row in rows if not row["retained"]) / len(rows)
    auc = rank_auc(stayed, left)
    distinct = len(set(believed_churn))
    return {
        "belief": label,
        "n": len(rows),
        "accounts": len({row["account"] for row in rows}),
        "mean_believed_churn": mean_believed_churn,
        "realised_churn_rate": realised_churn_rate,
        # Signed the same way as the A/B's: believed retention minus realised retention, so a
        # POSITIVE calibration error means the company expects to keep more of the book than it
        # keeps, and a NEGATIVE one means it over-expects churn.
        "calibration_error": (1.0 - mean_believed_churn) - (1.0 - realised_churn_rate),
        "level_ratio_believed_over_realised": (
            mean_believed_churn / realised_churn_rate if realised_churn_rate else None
        ),
        "discrimination_auc": auc,
        "auc_population": {"retained": len(stayed), "left": len(left)},
        "auc_unavailable_reason": (
            None if auc is not None
            else "one outcome class is empty on this population, so no rank statistic exists"
        ),
        "distinct_believed_values": distinct,
        "belief_is_constant": distinct == 1,
        "by_believed_bucket": _bucket_table(rows, belief_key),
    }


def bill_shock_response(rows: list[dict]) -> dict:
    """THE MECHANISM, tested directly from the same pairs.

    `build_churn_risk` is `BASE + k * UPLIFT`, so the belief is a pure function of k, the count of
    bill shocks in the twelve months before the renewal. Every row therefore carries the model's
    own dose (k), its assumed response (UPLIFT per shock), the world's TRUE post-adjustment
    probability at that dose, and the realised outcome. The candidate the direction names -- that
    bill shock predicts the OPPOSITE of what the model assumes on this book -- is a claim about
    the SIGN of that response and is answered here rather than inferred from a bucket table.
    """
    graded = [row for row in rows if row["bill_shock_count"] is not None]
    if not graded:
        return {"available": False, "reason": "no belief on this run was on the model's lattice"}
    by_k: dict[int, list[dict]] = collections.defaultdict(list)
    for row in graded:
        by_k[row["bill_shock_count"]].append(row)

    table = []
    for k in sorted(by_k):
        group = by_k[k]
        # THE WORLD'S TRUE PROBABILITY IS AVERAGED OVER THE ROWS THAT HAVE ONE, never over the
        # whole group with a missing value read as zero -- that is the FAIL-OPEN shape, and it
        # would drag the attenuation factor toward infinity exactly when the field went missing.
        with_truth = [row for row in group if row["has_world_true"]]
        table.append({
            "bill_shock_count": k,
            "n": len(group),
            "accounts": len({row["account"] for row in group}),
            "believed_churn": group[0]["believed_churn"],
            "world_true_n": len(with_truth),
            "world_true_churn_probability_mean": (
                sum(row["world_true_churn"] for row in with_truth) / len(with_truth)
                if with_truth else None
            ),
            "realised_churn_rate": sum(1 for row in group if not row["retained"]) / len(group),
        })

    lowest, highest = table[0], table[-1]
    span_k = highest["bill_shock_count"] - lowest["bill_shock_count"]
    believed_slope = CHURN_UPLIFT_PER_BILL_SHOCK
    endpoints_have_truth = (
        lowest["world_true_churn_probability_mean"] is not None
        and highest["world_true_churn_probability_mean"] is not None
    )
    world_slope = (
        (highest["world_true_churn_probability_mean"] - lowest["world_true_churn_probability_mean"])
        / span_k if span_k and endpoints_have_truth else None
    )
    realised_slope = (
        (highest["realised_churn_rate"] - lowest["realised_churn_rate"]) / span_k
        if span_k else None
    )
    return {
        "available": True,
        "graded": len(graded),
        "by_bill_shock_count": table,
        "believed_uplift_per_shock": believed_slope,
        "world_true_uplift_per_shock_endpoints": world_slope,
        "realised_uplift_per_shock_endpoints": realised_slope,
        # The endpoint slope is reported beside the whole table on purpose: with 13 doses and a
        # population that is 66% concentrated in two of them, an endpoint slope is a summary of
        # the two ends and NOT a fit. The per-dose rows are the evidence; this is the headline.
        "sign_agrees_with_model": (
            None if world_slope is None else bool(world_slope > 0) == bool(believed_slope > 0)
        ),
        "attenuation_factor": (
            believed_slope / world_slope if world_slope not in (None, 0) else None
        ),
        "reading": (
            "`sign_agrees_with_model` false would mean bill shock predicts the OPPOSITE of what "
            "`build_churn_risk` assumes -- the candidate mechanism for an inversion. True with an "
            "`attenuation_factor` well above 1 means the model has the direction right and the "
            "DOSE wrong by that factor. R12: this is a diagnostic; no constant is moved from here."
        ),
    }


def build_rows(events: list[dict]) -> tuple[list[dict], dict]:
    """Pair each rolled renewal's belief with the world's outcome. Returns (rows, provenance)."""
    rows, skipped = [], collections.Counter()
    off_lattice_sample = []
    for event in events:
        if not isinstance(event, dict):
            skipped["not_a_dict"] += 1
            continue
        outcome = event.get("event_type")
        believed = event.get("churn_probability")
        if outcome not in ("renewed", "churned"):
            skipped["no_lifecycle_outcome"] += 1
            continue
        if not isinstance(believed, (int, float)) or isinstance(believed, bool):
            skipped["no_logged_belief"] += 1
            continue
        k = recover_bill_shock_count(float(believed))
        if k is None:
            off_lattice_sample.append({
                "account": event.get("customer_id"),
                "event_date": event.get("event_date"),
                "churn_probability": believed,
            })
        company_estimate = event.get("company_churn_estimate")
        rows.append({
            "account": event.get("customer_id"),
            "event_date": event.get("event_date"),
            "believed_churn": float(believed),
            "bill_shock_count": k,
            "company_estimate_churn": (
                float(company_estimate)
                if isinstance(company_estimate, (int, float))
                and not isinstance(company_estimate, bool) else None
            ),
            "world_true_churn": float(event.get("realized_churn_probability") or 0.0),
            "has_world_true": isinstance(event.get("realized_churn_probability"), (int, float)),
            "retained": outcome == "renewed",
        })
    provenance = {
        "graded_renewals": len(rows),
        "skipped": dict(skipped),
        "on_lattice": sum(1 for row in rows if row["bill_shock_count"] is not None),
        "on_lattice_share": (
            sum(1 for row in rows if row["bill_shock_count"] is not None) / len(rows)
            if rows else None
        ),
        "off_lattice_sample": off_lattice_sample[:10],
        "reading": (
            "`on_lattice_share` below 1.0 means some logged belief did not come out of "
            "`saas.churn_model.churn_probability(k)`, so the bill-shock count behind it is not "
            "recoverable and the mechanism table below describes only the recoverable part. It "
            "is published rather than assumed because the mechanism claim depends on it."
        ),
    }
    return rows, provenance


def grade_run(payload: dict, source: str | None = None) -> dict:
    """The whole instrument, over one finished run's `customer_events`."""
    events = payload.get("customer_events")
    if not isinstance(events, list) or not events:
        raise ValueError(
            "run output publishes no `customer_events` -- there is no renewal to grade. "
            "This refuses rather than reporting an empty grade: a belief graded over zero "
            "renewals must not read the same as a belief that ranked nothing."
        )
    rows, provenance = build_rows(events)
    if not rows:
        raise ValueError(
            f"no renewal in this run carries both a logged belief and a lifecycle outcome "
            f"({dict(provenance['skipped'])})"
        )

    with_truth = [row for row in rows if row["has_world_true"]]
    oracle = (
        rank_auc(
            [-row["world_true_churn"] for row in with_truth if row["retained"]],
            [-row["world_true_churn"] for row in with_truth if not row["retained"]],
        )
        if with_truth else None
    )

    company_rows = [row for row in rows if row["company_estimate_churn"] is not None]

    dates = sorted(row["event_date"] for row in rows if row["event_date"])
    return {
        "schema_version": 1,
        "source_run_output": source,
        "book": {
            "renewals_the_world_rolled": len(rows),
            "billing_accounts": len({row["account"] for row in rows}),
            "first_renewal": dates[0] if dates else None,
            "last_renewal": dates[-1] if dates else None,
            "churned": sum(1 for row in rows if not row["retained"]),
            "retained": sum(1 for row in rows if row["retained"]),
        },
        "belief_provenance": provenance,
        "bill_shock_model": grade_belief(
            rows, "believed_churn", "saas.churn_model.build_churn_risk (BASE + k x UPLIFT)"),
        "company_estimate": (
            grade_belief(
                company_rows, "company_estimate_churn",
                "company churn estimate logged as `company_churn_estimate`")
            if company_rows else
            {"available": False, "reason": "no renewal carries a company churn estimate"}
        ),
        "oracle_ceiling": {
            "discrimination_auc": oracle,
            "n": len(with_truth),
            "meaning": (
                "the world's OWN fully-adjusted `realized_churn_probability`, graded by the "
                "identical statistic. It is the ceiling: no belief can rank this population "
                "better than the probability the dice were actually rolled against. A graded "
                "belief near 0.5 is only a failure of the belief if this number is well above "
                "0.5 -- otherwise the population itself is unrankable and the low AUC says "
                "nothing about the model (R15: a control that cannot fail is worse than none)."
            ),
        },
        "mechanism": bill_shock_response(rows),
        "independence": {
            "belief_and_outcome_share_a_source": True,
            "reading": (
                "`simulation.customer_events.roll_lifecycle_event` SEEDS the world's "
                "`effective_p_retain` from this same `build_churn_risk` number and then "
                "multiplies it through the passive cap, the market-year switching multiplier, "
                "the price-position multiplier, income stress and satisfaction. So this is not a "
                "forecast graded against an unrelated tally: it measures whether the world's own "
                "adjustment chain preserves the ordering and the level of the base rate it "
                "starts from. The company-side `company_churn_estimate` is graded beside it and "
                "does NOT feed the roll, which is the independent leg."
            ),
        },
        "r12_note": (
            "Every figure here is a diagnostic. No constant in `saas/churn_model.py` is read as "
            "a target and none is written from this module."
        ),
    }


def render_markdown(grade: dict) -> str:
    book = grade["book"]
    lines = [
        f"Book: {book['renewals_the_world_rolled']} renewals the world rolled, "
        f"{book['billing_accounts']} billing accounts, "
        f"{book['first_renewal']}..{book['last_renewal']}, "
        f"{book['churned']} churned / {book['retained']} retained",
        "",
    ]
    for key in ("bill_shock_model", "company_estimate"):
        block = grade[key]
        if not block.get("n"):
            lines.append(f"{key}: {block.get('reason')}")
            continue
        auc = block["discrimination_auc"]
        lines += [
            f"### {block['belief']}",
            f"n={block['n']} accounts={block['accounts']} "
            f"AUC={auc if auc is None else round(auc, 4)} "
            f"(oracle ceiling {round(grade['oracle_ceiling']['discrimination_auc'], 4)})",
            f"mean believed churn {block['mean_believed_churn']:.4f} vs realised "
            f"{block['realised_churn_rate']:.4f} "
            f"(x{block['level_ratio_believed_over_realised']:.2f})",
            "",
            "| believed p_retain | n | accounts | mean believed | realised retention | left |",
            "|---|---|---|---|---|---|",
        ]
        for bucket in block["by_believed_bucket"]:
            lines.append(
                f"| {bucket['believed_p_retain_from']:.1f}-{bucket['believed_p_retain_to']:.1f} "
                f"| {bucket['n']} | {bucket['accounts']} "
                f"| {bucket['mean_believed_p_retain']:.3f} "
                f"| {bucket['realised_retention_rate']:.3f} | {bucket['left']} |"
            )
        lines.append("")
    mech = grade["mechanism"]
    if mech.get("available"):
        lines += [
            "### Mechanism: the dose the model assumes against the one the world delivers",
            "",
            "| bill shocks | n | accounts | believed churn | world true p_churn | realised |",
            "|---|---|---|---|---|---|",
        ]
        for row in mech["by_bill_shock_count"]:
            world_true = row["world_true_churn_probability_mean"]
            lines.append(
                f"| {row['bill_shock_count']} | {row['n']} | {row['accounts']} "
                f"| {row['believed_churn']:.3f} "
                f"| {'n/a' if world_true is None else format(world_true, '.4f')} "
                f"| {row['realised_churn_rate']:.3f} |"
            )
        lines += [
            "",
            f"believed uplift/shock {mech['believed_uplift_per_shock']:.4f} vs world true "
            f"{mech['world_true_uplift_per_shock_endpoints']:.4f} "
            f"(attenuation x{mech['attenuation_factor']:.2f}), "
            f"sign agrees with the model: {mech['sign_agrees_with_model']}",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-output", type=Path, default=DEFAULT_RUN_OUTPUT,
                        help="finished run JSON carrying `customer_events`")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTEFACT,
                        help="where to write the graded artefact")
    parser.add_argument("--markdown", action="store_true", help="print the tables as markdown")
    args = parser.parse_args(argv)

    payload = json.loads(args.run_output.read_text())
    grade = grade_run(payload, source=str(args.run_output))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(grade, indent=2) + "\n")
    if args.markdown:
        print(render_markdown(grade))
    else:
        print(f"wrote {args.out} — {grade['book']['renewals_the_world_rolled']} renewals, "
              f"AUC {grade['bill_shock_model']['discrimination_auc']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
