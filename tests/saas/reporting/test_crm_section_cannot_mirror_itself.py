"""The lifecycle-events section may not reconcile a source against itself (2026-08-29).

DEFECT THIS FILE EXISTS TO CATCH. `annual_report._section_company_crm` published a table
headed "SIM ground truth vs company CRM reconciliation" with a Match column. It built the
"CRM" side by replaying `data["company_event_log"]` into a fresh `CompanyEventLog`, and the
"SIM" side as `crm_churned ∩ churned_billing_accounts`. Both sides were projections of one
write. The column could only read "mismatch" if the CRM had INVENTED a churn -- impossible
when the CRM is a replay of the world's own list -- so the failure it existed to catch, an
account the world churned that the company's record missed, dropped out of both sides and
read "yes". An entirely empty company CRM, which is what the production path actually
produced, reconciled as "yes" against a world that churned every account.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. A test pinned to the current "yes" would have
gone GREEN on the defect and RED the moment the report became honest -- exactly backwards,
and this project has done it before. The property asserted here is: **the section must not
publish an agreement verdict between two things that share a writer.** It stays green under
any future reconciliation whose company side has its own writer, and goes red if the mirror
comes back in any form.

`test_the_containment_check_could_not_fail` is the mutation proof: it runs the deleted
algorithm against the finding's case C and shows the verdict it produced. If that test ever
starts reading "mismatch", the containment algebra in
`docs/staging/done/WORKER_FINDING_THE_PUBLISHED_CRM_RECONCILIATION_BUILDS_ITS_COMPANY_SIDE_FROM_THE_SIM_2026-08-29.md`
is wrong and the finding is corrected beside itself.
"""
from __future__ import annotations

import ast
import inspect

from saas.reporting import annual_report
from saas.reporting.annual_report import _section_company_crm


def _run(n_years: int = 2) -> str:
    return _section_company_crm({
        "company_event_log": [
            {"event_type": "churn", "customer_id": "A", "event_date": "2020-03-01",
             "reason": "non-renewal", "sim_churn_probability": 0.4,
             "company_churn_estimate": 0.35},
            {"event_type": "acquisition", "customer_id": "B", "event_date": "2020-07-01",
             "channel": "market-acquisition", "predecessor_id": "A"},
            {"event_type": "churn", "customer_id": "B", "event_date": "2021-07-01",
             "reason": "non-renewal", "sim_churn_probability": None,
             "company_churn_estimate": None},
        ],
        "churned_billing_accounts": ["A", "B"],
        "years": {str(2020 + i): {} for i in range(n_years)},
    })


# ── The property: no agreement verdict over a shared writer ───────────────────

def test_the_section_publishes_no_agreement_verdict():
    """No Match/reconciliation claim, because both available sides share one writer."""
    rendered = _run().lower()
    for token in ("| match", "reconciliation", "reconciles", "crm active"):
        assert token not in rendered, (
            f"{token!r} is back in the lifecycle section. Both sides of anything it could "
            f"compare are written by run_phase2b in one loop; an agreement verdict over "
            f"them cannot read 'mismatch' for the failure it exists to catch."
        )


def test_the_report_does_not_rebuild_the_company_ledger_from_the_sim_stream():
    """The structural half: the report may not import the company's CRM at all.

    Replaying `company_event_log` into a `CompanyEventLog` is what manufactured the
    second 'independent' side. Asserting on the rendered text alone would miss a
    rebuild that fed some other published figure, so this reads the imports.

    Parsed, not grepped: the module's own prose names `company.crm.event_log` when
    explaining why it does not use it, and a substring check would fire on that --
    going red for the comment that records the repair.
    """
    tree = ast.parse(inspect.getsource(annual_report))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    assert "company.crm.event_log" not in imported, (
        "annual_report imports the company's CRM ledger. The only data it has to fill "
        "one with is the SIM's own event stream, so anything it computes from that "
        "ledger is a second projection of the same write wearing the company's name."
    )


def test_the_section_names_its_source_and_refuses_the_comparison_on_its_face():
    """Fail closed, on the surface -- not in a footnote."""
    rendered = _run()
    assert "## Customer Lifecycle Events — SIM Record" in rendered
    assert "_build_company_event_log" in rendered, "the section must name where it comes from"
    assert "no company record to reconcile against" in rendered, (
        "the absence of a company-side ledger is a result and belongs on the page"
    )


def test_the_empty_run_heading_matches_the_populated_one():
    """The early return is a second surface and used to carry the old title."""
    empty = _section_company_crm({"company_event_log": [], "years": {}})
    assert "## Customer Lifecycle Events — SIM Record" in empty
    assert "Company CRM" not in empty


def test_the_year_table_counts_only_what_the_stream_holds():
    """Cumulative counts, not a book position -- the opening book never emits an event."""
    rendered = _run(n_years=2)
    assert "| 2020-12-31 | 1 | 1 |" in rendered
    assert "| 2021-12-31 | 2 | 1 |" in rendered


# ── The mutation proof: the deleted control, run against case C ───────────────

def test_the_containment_check_could_not_fail():
    """The removed algorithm, verbatim, on an EMPTY CRM against a world that churned all.

    Mutating the inputs is the wrong knife here: the control was fail-open by
    CONSTRUCTION, so no perturbation of a live run reddens it. The mutation that
    exposes it is emptying one side -- and emptying the CRM is not a hypothetical,
    it is what every production run produced.
    """
    def deleted_match(cel, churned_ba, year_end):
        crm_churned = {
            e["customer_id"] for e in cel
            if e["event_type"] == "churn" and e["event_date"] <= year_end
        }
        sim_churned_by_year = {
            ba for ba in churned_ba
            if any(
                e["event_type"] == "churn" and e["customer_id"] == ba
                and e["event_date"] <= year_end
                for e in cel
            )
        }
        return "yes" if crm_churned == sim_churned_by_year else "mismatch"

    # Case C: the world churned A and B; the company's record holds nothing at all.
    assert deleted_match([], {"A", "B"}, "2020-12-31") == "yes"
    # Case A: the company missed a departure -- the exact failure it was published to catch.
    cel_a = [{"event_type": "churn", "customer_id": "A", "event_date": "2020-03-01"}]
    assert deleted_match(cel_a, {"A", "B"}, "2020-12-31") == "yes"
    # Case B: the only direction it could see, and the one a replay cannot produce.
    cel_b = cel_a + [{"event_type": "churn", "customer_id": "B", "event_date": "2020-04-01"}]
    assert deleted_match(cel_b, {"A"}, "2020-12-31") == "mismatch"


# ── The other half of the same defect: the seam that starved the CRM ──────────

def test_no_observable_is_booked_only_when_a_seam_no_caller_plumbs_is_present():
    """`run_phase2b` must not gate a company observable on an injected interface.

    The starved seam and the mirrored reconciliation were one defect seen twice: five
    `if sim_interface is not None` guards meant the company's ledger was empty on every
    production path, and because the report rebuilt the ledger from the world's stream
    the emptiness never surfaced. Deleting the mirror without deleting the guards would
    leave the starvation with nothing to reveal it.

    Keyed to the property (no conditional booking), not to the parameter's name: a
    replacement guard called anything else still trips the first assertion.
    """
    import simulation.run_phase2b as rp

    src = inspect.getsource(rp)
    tree = ast.parse(src)

    for fn in ("main", "_main"):
        params = inspect.signature(getattr(rp, fn)).parameters
        assert "sim_interface" not in params, (
            f"run_phase2b.{fn} accepts sim_interface again. No production entry point "
            f"passes one, so an accepted-and-ignored parameter is fail-silent: a caller "
            f"can pass an interface and get nothing booked into it."
        )

    # Any `notify_*` call reachable only under an `if <x> is not None` test is the shape
    # that produced the dead channel, whatever the guard variable is called.
    guarded = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (isinstance(test, ast.Compare)
                and len(test.ops) == 1 and isinstance(test.ops[0], ast.IsNot)
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value is None):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr.startswith("notify_")):
                guarded.append((inner.lineno, inner.func.attr))
    assert not guarded, (
        f"company observables booked only behind an is-not-None guard: {guarded}. "
        f"Book them where every event passes and let an unarmed consumer decline to "
        f"update, the way the competitive-pressure ledger does."
    )
