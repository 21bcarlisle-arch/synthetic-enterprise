"""Phase 4c applied to the full Phase 2b portfolio — end-to-end run.

Phase 4c-4 through 4c-6 (`saas/bill_generator.py`, `saas/payment_behaviour.py`,
`saas/contact_model.py`) were built and tested against small hand-written
settlement fixtures. This script is the follow-up flagged in
`docs/observability/PHASE_4c_SUMMARY.md`'s Open Questions: it runs the full
Phase 2b simulation once, groups its `all_records` settlement output into
monthly bills per customer (chronological, carrying `previous_bill_total_gbp`
for the bill-shock clarity penalty), then feeds those bills through 4c-5
(payment behaviour) and 4c-6 (contact/complaints) to produce portfolio-level
billing-experience figures for the real 10-account portfolio (6 electricity +
4 gas).

4c-2 (weather-driven demand shapes) and 4c-3 (weather->price sensitivity) are
NOT included here — both modify `simulation/settlement.py`'s inputs
(consumption shape, forward price) rather than consuming its output, so
wiring them in is a separate, larger re-run of `simulation/run_phase2b.py`
itself, not a downstream pass over its existing records. Flagged as a further
follow-up.

Delegation note: hand-written (orchestration-adjacent, per protocol).

Phase 5b: this script is also the single entry point for the combined
2b+4b+4c run output that the annual report is built from. Rather than
have `run_phase4b_on_phase2b.py` call `run_phase2b()` a second time (a
separate, non-deterministic ~100-minute run with different committee
decisions), `main()` here runs Phase 2b once and feeds the same
`all_records`/`CUSTOMERS` through the 4b customer-value builders
(`cost_to_serve`, `churn_model`, `home_move_win_rate`, `enterprise_value`)
as well as the 4c billing-experience builders.

KNIFE pass 1 (2026-08-09): this module is a pure LIBRARY — it has no CLI and
no `__main__` block. `main()` runs the pipeline and returns its output dict;
persisting the reduced report data and writing the run markers is the job of
`tools/run_phase4c_pipeline.py` (CLI: `python3 -m tools.run_phase4c_pipeline
--save-json`), which sits above both layers. The lazy
`saas.reporting.annual_report` import that used to live at the bottom of this
file existed only to work around the import cycle that pass removed.

SCOPE OF THAT CUT, stated precisely because the honest boundary matters: pass 1
removed the ONE `saas.reporting` edge, which is the edge that closed the
reporting import CYCLE. This module still imports 14 company-side packages
directly (`saas.bill_generator`, `saas.customers`, `company.billing.*`, …) —
they are class-(b) crossings in `LEGACY_SIM_READS_COMPANY` and remain the
densest such source in the codebase. Paying those down is KNIFE passes 2 and 3,
not this one. Do NOT read "pure library" as "wall-clean": it is cycle-free and
composition-free, nothing more.
"""

import saas.payment_behaviour as payment_behaviour_module
from simulation.dd_collection_book import build_dd_collection_book
from simulation.dd_balance_book import build_dd_balance_book
from simulation.dd_level_collection_book import build_dd_level_collection_book
from company.billing.dd_review_runner import run_annual_reviews
from company.billing.pre_bill_validation import validate_bills
from company.interfaces.bill_assembly import assemble_monthly_bills
from saas.churn_model import build_churn_risk
from saas.contact_model import build_contact_model
from saas.cost_to_serve import build_cost_to_serve, build_cost_to_serve_ledger_events
from company.interfaces.supply_book import (
    acquired_supply_points,
    registered_supply_points,
    successor_supply_points,
)
from saas.enterprise_value import build_enterprise_value
from saas.home_move_win_rate import build_home_move_win_rates
from saas.ledger import build_ledger, derive_pnl, ledger_summary, make_cost_to_serve_event
from saas.payment_behaviour import build_payment_behaviour
from simulation.arrears_engine import (
    compute_emergent_bad_debt,
    apply_emergent_bad_debt,
    compute_debt_recovery,
    apply_debt_recovery,
)
from simulation.contact_centre import generate_contact_centre_log
from simulation.credit_refund_events import generate_credit_refund_log
from simulation.meter_reads import (
    SimulatedReadFeed,
    generate_meter_read_log,
    meter_type_for_customer,
)
from simulation.run_phase2b import main as run_phase2b
from tools.contact_centre_port import ContactCentreMessage
from tools.meter_read_port import MeterReadMessage

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
ACQUIRED_CUSTOMERS = acquired_supply_points()
CUSTOMERS = registered_supply_points()
SUCCESSOR_CUSTOMERS = successor_supply_points()

PRICE_DIFFERENTIAL_PCT = 0.0  # matches run_phase4b_on_phase2b.py


def _get_all_customers() -> list[dict]:
    """Live customer list including Phase 8a acquired customers.

    Must be a function (not a module-level constant) because ACQUIRED_CUSTOMERS
    is populated by run_phase2b.main() after import time.
    """
    return CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS

# `RUN_OUTPUT_LATEST_PATH` / `RUN_OUTPUT_VERSIONED_DIR` moved to
# `tools/run_annual_report.py` with `save_run_output_json()` — where a run's
# REPORT data is persisted is a reporting concern, not the run module's.


def build_monthly_bills(all_records: list[dict], churned_ids: set[str] | None = None) -> list[dict]:
    """Run the SUPPLIER's monthly billing over this run's settled records.

    The assembly itself moved to the company layer in KNIFE pass 3
    (`A_composition_lift` step 11, 2026-08-10) — see
    `company/billing/monthly_bill_assembly.py` for why, and
    `company/interfaces/bill_assembly.py` for the door it comes through. What is
    left here is the world's half: hand over the settled records and the read
    feed, take back the bills.

    Kept as a named function at this path on purpose. It is the world's own call
    site, it is what `saas/ledger.py` and this module's `main()` document, and
    the wrapper is what lets the read feed be supplied world-side without every
    caller learning about it. Behaviour is unchanged: `SimulatedReadFeed` calls
    the same read functions with the same arguments the inlined code did.
    """
    return assemble_monthly_bills(
        all_records, SimulatedReadFeed(), churned_ids=churned_ids
    )


def _serialize_dd_collection_book(book) -> dict:
    """JSON-safe form of a DirectDebitBook for the run-output surface
    (2026-07-12, W5_1_banking_payment_rails L2->L3: this atom's decisive
    remaining gap was 'zero live pipeline callers anywhere' -- this wiring
    plus this serialisation close that gap). Every mandate and collection
    attempt, not just the aggregate summary, so a per-customer business
    surface (e.g. Customers tab) can render one real, evidenced instance."""
    import dataclasses

    return {
        "summary": book.dd_summary(),
        "mandates": [dataclasses.asdict(m) for m in book.all_mandates()],
        "attempts": [dataclasses.asdict(a) for a in book.all_attempts()],
    }


def main(report_end: str | None = None, policy=None):
    phase2b_result = run_phase2b(report_end=report_end, policy=policy)
    all_records = phase2b_result["all_records"]

    # D3 step 2 (Expert-Hour finding, 2026-07-12): computed here (moved
    # earlier than its pre-existing use below, for generate_credit_refund_log)
    # so a churning account's own last bill can force-resolve any pending
    # estimated run rather than leaving it unreconciled forever.
    churned_ids = set(phase2b_result.get("churned_billing_accounts", []))

    bills = build_monthly_bills(all_records, churned_ids)

    # W5_1_banking_payment_rails L2->L3 (2026-07-12): the rails-timed DD
    # collection book (mandate setup/collection/amendment, real AUDDIS/ARUDD/
    # ADDACS timing) had zero callers from any real run pipeline until now --
    # an Expert Hour review named this the decisive blocker to L3 ("cannot
    # live in time" without one). Purely additive and read-only against
    # everything computed so far: reads `bills` and `phase2b_result`'s own
    # `per_customer_behavioral`, uses its own independently-seeded RNG
    # instances, and does not mutate `all_records`/`bills` or any other
    # ground-truth structure. Same seed (42, the function's own default) as
    # compute_emergent_bad_debt() below, so its success/failure pattern
    # matches the real ground truth exactly (proven by
    # tests/simulation/test_dd_collection_book.py's TestOutcomeSequence
    # MatchesGroundTruth suite, including the amendment-firing path).
    dd_collection_book = build_dd_collection_book(
        bills, phase2b_result.get("per_customer_behavioral", {})
    )

    # DD4a (atom DD_seasonal_cashflow_physics): the annual DD review as a
    # first-class LIVE event -- dd_review.py held complete review logic but had
    # zero live callers. run_annual_reviews drives it over the portfolio at
    # each customer's 12-month anniversary. Purely additive and read-only,
    # exactly like build_dd_collection_book above: reads only the company's own
    # issued `bills` (company-observable), draws no RNG, mutates nothing, and
    # changes no existing financial figure. The `large_increase` events it
    # emits are the seam DD4b will route into the churn/resentment engine (the
    # registered next gated step -- deliberately not wired here, as that shifts
    # ground-truth churn and needs population-level verification).
    annual_dd_review = run_annual_reviews(bills)

    # DD2 (atom DD_seasonal_cashflow_physics): the per-customer level-DD seasonal
    # credit/debit balance carried tick-by-tick, and the portfolio HELD-CREDIT
    # LIABILITY it aggregates to (summer credit builds, winter draws it down; the
    # positive balance is money owed back -- the "cash-rich but insolvent" tell).
    # Purely additive and read-only, EXACTLY like build_dd_collection_book and
    # run_annual_reviews above: reads only the company's own issued `bills`
    # (company-observable), draws no RNG, mutates nothing, and changes no existing
    # financial figure. It emits the held-credit-liability figure DD3 will book
    # into the double-entry chart and DD-H will weigh against believed solvency
    # (both the registered next gated steps, deliberately not wired here).
    dd_balance_book = build_dd_balance_book(bills)

    # DD1 (atom DD_seasonal_cashflow_physics): the LEVEL (fixed) DD collection
    # made first-class -- the standing monthly amount actually SIZES a collection
    # record, landing on the customer's staggered payment day. Consumes DD2's
    # balance book (so the standing-DD chain is IDENTICAL by construction, no
    # drift), reads no other structure, draws no RNG, mutates nothing, and
    # changes no existing figure. This is the Fixed-DD counterpart to
    # build_dd_collection_book above (which is Variable DD: raw bill sizes it).
    dd_level_collection_book = build_dd_level_collection_book(dd_balance_book)

    # Phase 3 (CORE_FIDELITY_PHASES.md item 1): meter-read arrival/
    # estimation/failure events, one per bill -- company-observable data
    # layer only, does not alter settlement-based revenue recognition above.
    all_customers_for_meter_type = _get_all_customers()
    customer_meter_types = {
        c["customer_id"]: meter_type_for_customer(c) for c in all_customers_for_meter_type
    }
    # WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters): the
    # meter-read crossing now travels as versioned typed messages
    # (tools.meter_read_port.MeterReadMessage) rather than raw dicts. This is a
    # transport-shape change only -- `to_log_entry()` is a lossless identity on
    # the pre-conversion dict, so every downstream consumer of `meter_read_log`
    # is unaffected. Migrating those consumers to accept the message directly
    # is the follow-on "generalize the pattern" step, not done here.
    meter_read_messages = [
        MeterReadMessage.from_log_entry(entry)
        for entry in generate_meter_read_log(bills, customer_meter_types)
    ]
    meter_read_log = [message.to_log_entry() for message in meter_read_messages]

    # Phase 3 (CORE_FIDELITY_PHASES.md item 2): SLC 14 credit-refund
    # activation -- company/billing/credit_refund.py already had the real
    # SLA mechanic but no caller anywhere in simulation/. DD customers who
    # churn carrying a positive DD-smoothing credit balance now raise a real
    # refund event with an on-time/breach outcome. `churned_ids` computed
    # above, before build_monthly_bills.
    customer_segments = {
        c["customer_id"]: c.get("segment", "resi") for c in all_customers_for_meter_type
    }
    credit_refund_log = generate_credit_refund_log(bills, customer_segments, churned_ids)

    # Phase QD: replace the flat get_bad_debt_rate() formula baked into
    # all_records by run_phase2b's real-time settlement loop with the real,
    # emergent bad debt from the same payment/arrears model that drives the
    # per-customer billing ledger (tools.generate_billing_ledger) -- so the
    # board-reported bad_debt_gbp is an outcome of simulated payment
    # behaviour, not a calibrated assumption.
    emergent_bad_debt = compute_emergent_bad_debt(
        bills,
        phase2b_result.get("per_customer_behavioral", {}),
        churned_ids,
    )
    apply_emergent_bad_debt(all_records, emergent_bad_debt)

    # Phase [debt-branch, docs/design/PROCESS_MODEL.md Section 4]: real
    # post-write-off DCA recovery / debt-sale proceeds, applied as a
    # reduction to the bad debt just written off above -- same bills/
    # behavioral/churned inputs as compute_emergent_bad_debt() so the two
    # line up on the identical set of written-off cases.
    debt_recovery = compute_debt_recovery(
        bills,
        phase2b_result.get("per_customer_behavioral", {}),
        churned_ids,
    )
    apply_debt_recovery(all_records, debt_recovery)

    payment_behaviour = build_payment_behaviour(bills)
    contact_model = build_contact_model(bills)

    # Phase 3 (CORE_FIDELITY_PHASES.md item 4): contact-centre first-response
    # time, distinct from feedback_survey's complaint *resolution* timer --
    # reuses contact_model's already-computed per-bill contact_probability
    # as the trigger, adds the channel + first-response latency layer.
    # WALLED_INTERFACES reference-flow conversion (W4_1_typed_adapters, third
    # flow): the customer-contact crossing now travels as versioned typed
    # messages (tools.contact_centre_port.ContactCentreMessage) rather than raw
    # dicts. Transport-shape change only -- `to_log_entry()` is a lossless
    # identity on the pre-conversion dict, so the downstream consumer of
    # `contact_centre_log` (annual_report.py's SLC 25C SLA-breach check) is
    # unaffected. All fields are company-observable contact-centre operational
    # data; unlike meter reads / the acquisition funnel there is no SIM-internal
    # ground-truth field on this seam.
    contact_centre_messages = [
        ContactCentreMessage.from_log_entry(entry)
        for entry in generate_contact_centre_log(bills, contact_model)
    ]
    contact_centre_log = [message.to_log_entry() for message in contact_centre_messages]

    all_customers = _get_all_customers()
    cost_to_serve = build_cost_to_serve(all_records, all_customers)
    churn_risk = build_churn_risk(all_records, all_customers)
    home_move_win_rates = build_home_move_win_rates(churn_risk, all_customers, PRICE_DIFFERENTIAL_PCT)
    enterprise_value = build_enterprise_value(
        churn_risk, cost_to_serve, all_customers, PRICE_DIFFERENTIAL_PCT
    )

    avg_clarity = sum(b["clarity_score"] for b in bills) / len(bills)
    shocked = [b for b in bills if b["bill_shock_pct"] is not None]
    avg_bill_shock = sum(b["bill_shock_pct"] for b in shocked) / len(shocked) if shocked else 0.0
    total_bad_debt = sum(
        record["bad_debt_provision_gbp"]
        for records in payment_behaviour.values()
        for record in records
    )

    print("\n" + "=" * 60)
    print("=== Phase 4c billing experience layer (full portfolio) ===")
    print("=" * 60)

    print(f"\nBills generated:                 {len(bills)}")
    print(f"Average clarity score:            {avg_clarity:>12.3f}")
    print(f"Average bill shock (where shown): {avg_bill_shock:>12.1%}")
    print(f"Total bad debt provision:        £{total_bad_debt:>12.2f}")
    print(f"Avg complaint probability:        {contact_model['portfolio']['avg_complaint_probability']:>12.3f}")
    print(f"Service quality score:            {contact_model['portfolio']['service_quality_score']:>12.3f}")
    print(f"Enterprise value (4b):           £{enterprise_value['portfolio']['enterprise_value_gbp']:>12.2f} "
          f"across {enterprise_value['portfolio']['account_count']} billing accounts")
    print(f"Cost to serve (portfolio):       £{cost_to_serve['portfolio']['cost_to_serve_gbp']:>12.2f}")
    print(f"Net margin after cost to serve:  £{cost_to_serve['portfolio']['net_margin_gbp']:>12.2f}")

    print(f"\n{'Account':<8} {'Bills':>6} {'AvgClarity':>11} {'CreditRisk':>11} {'BadDebt£':>10}")
    for customer in CUSTOMERS:
        customer_id = customer["customer_id"]
        customer_bills = [b for b in bills if b["customer_id"] == customer_id]
        if not customer_bills:
            continue
        avg_customer_clarity = sum(b["clarity_score"] for b in customer_bills) / len(customer_bills)
        credit_risk = payment_behaviour[customer_id][0]["credit_risk"]
        bad_debt = sum(r["bad_debt_provision_gbp"] for r in payment_behaviour[customer_id])
        print(
            f"{customer_id:<8} {len(customer_bills):>6} {avg_customer_clarity:>11.3f} "
            f"{credit_risk:>11} {bad_debt:>10.2f}"
        )

    # Phase 8a: merge acquisition_spend and fixed_cost events into the ledger
    # CTS reconciliation fix (docs/staging/drafts/NEXT_PHASE.md option B):
    # also emit monthly cost_to_serve_event totals so ledger account 6100
    # ("Cost to Serve") stops always netting to £0 against the non-zero
    # figure `cost_to_serve` (above) already reports for pricing/CLV.
    cost_to_serve_ledger_events = build_cost_to_serve_ledger_events(all_records, all_customers)
    extra_events = (
        phase2b_result.get("acquisition_spend_events", [])
        + phase2b_result.get("fixed_cost_events", [])
        + [make_cost_to_serve_event(e["month"], e["amount_gbp"]) for e in cost_to_serve_ledger_events]
    )
    # BILL_TO_LEDGER_LINKAGE.md (2026-07-12): a HELD bill (pre_bill_
    # validation.py's Tier-1 gate) has NOT been issued to the customer --
    # recognising its revenue in the ledger P&L before that gate clears it
    # is a real accounting error (revenue recognition without an issued
    # bill), confirmed live: this run's own held_bill_count means
    # ledger_pnl.total_billed_gbp previously counted an un-issued bill's
    # total_amount_gbp as recognised revenue. Only ISSUED (validate_bills()-
    # passing) bills feed the ledger's revenue recognition; `bills` itself
    # (the full, unfiltered list, held ones included) is left untouched for
    # every other consumer (per-customer views, the exception queue tools/
    # generate_billing_ledger.py builds separately) -- this fix is scoped
    # to ledger revenue recognition specifically, not a wider bill-list change.
    issued_bills, _held_bills_excluded_from_ledger = validate_bills(bills)
    ledger_events = build_ledger(
        all_records, issued_bills, payment_behaviour_module,
        extra_events=extra_events or None,
    )
    ledger_pnl = derive_pnl(ledger_events)
    ledger_meta = ledger_summary(ledger_events)

    # BILL_TO_LEDGER_LINKAGE.md Tier-1 invariant: the ledger's recognised
    # billed revenue must reconcile to the penny with the bills that
    # actually fed it. A whole-run aggregate check, not a per-bill gate --
    # logged loudly rather than raising (this pipeline run already takes
    # ~100 minutes; a divergence here is a real defect worth a visible flag,
    # not a reason to discard a completed run), and surfaced on the report
    # itself so it lands on a business surface, not just a log line.
    from company.compliance.domain_invariants import check_billed_clock_reconciles
    billed_clock_reconciles = check_billed_clock_reconciles(
        ledger_pnl.get("total_billed_gbp", 0.0), issued_bills
    )
    if not billed_clock_reconciles:
        print(
            "WARNING: billed-clock invariant VIOLATED -- ledger_pnl.total_billed_gbp "
            "does not reconcile with the sum of issued bills. See "
            "BILLED_CLOCK_RECONCILES_WITH_ISSUED_BILLS "
            "(company/compliance/domain_invariants.py)."
        )
    ledger_meta["billed_clock_reconciles_with_issued_bills"] = billed_clock_reconciles

    return {
        "phase2b": phase2b_result,
        "bills": bills,
        "dd_collection_book": _serialize_dd_collection_book(dd_collection_book),
        "annual_dd_review": annual_dd_review.serialise(),
        "dd_balance_book": dd_balance_book.serialise(),
        "dd_level_collection_book": dd_level_collection_book.serialise(),
        "meter_read_log": meter_read_log,
        "credit_refund_log": credit_refund_log,
        "contact_centre_log": contact_centre_log,
        "payment_behaviour": payment_behaviour,
        "contact_model": contact_model,
        "cost_to_serve": cost_to_serve,
        "churn_risk": churn_risk,
        "home_move_win_rates": home_move_win_rates,
        "enterprise_value": enterprise_value,
        "price_differential_pct": PRICE_DIFFERENTIAL_PCT,
        "ledger_events": ledger_events,
        "ledger_pnl": ledger_pnl,
        "ledger_meta": ledger_meta,
        "won_successor_activations": phase2b_result.get("won_successor_activations", {}),
        # Phase 8a: growth mandate outputs
        "acquisition_spend_events": phase2b_result.get("acquisition_spend_events", []),
        "fixed_cost_events": phase2b_result.get("fixed_cost_events", []),
        "acquired_customers": phase2b_result.get("acquired_customers", []),
        "growth_mandate": phase2b_result.get("growth_mandate", "flat"),
    }


# `_git_commit_hash()`, `save_run_output_json()` and the `--save-json` CLI that
# used to live here moved to `tools/run_annual_report.py` and
# `tools/run_phase4c_pipeline.py` (KNIFE pass 1, 2026-08-09). Reducing this
# module's output through `saas.reporting.annual_report.extract_report_data`
# was the return edge that closed the reporting import cycle; a composition of
# the two layers belongs above both of them, not inside the run module. This
# module is now a pure library — `main()` runs the pipeline and returns its
# output dict.
