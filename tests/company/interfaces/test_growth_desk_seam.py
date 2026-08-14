"""KNIFE pass 3, `A_composition_lift` step 27 (register §3v) — the control.

Subject: the two doors that took the acquire-or-retain economics and the
monthly overhead accrual off `simulation/run_phase2b.py` —
`company/interfaces/growth_desk.py` and `company/interfaces/fixed_overhead.py`.

EVERY EXPECTED VALUE IN THE `Behaviour` CLASS WAS COMPUTED AGAINST
`saas.growth_mandate` / `saas.ledger` BEFORE THE CUT LANDED and transcribed here
as a LITERAL. They are pre-cut evidence, not a re-record of the post-cut tree,
which is the tautology this project keeps catching: a pin regenerated from the
thing it pins can never fail. Nothing in this file derives an expectation by
calling the module it is checking.

The three things that could rot silently, and the class that fires on each:

  * `Behaviour`   — an arithmetic or shape change behind the door.
  * `TheDoorIsADoor` — the per-market tables leaking back onto the seam surface,
    which is the failure that would leave the wall ratchet GREEN (the import
    still terminates on the exempt seam package) while the world could once
    again read the supplier's cost table straight through the door.
  * `TheWorldNoLongerHoldsIt` — the crossing coming back, in either the direct
    form (`simulation/` importing `saas.growth_mandate` / `saas.ledger` again)
    or the subtler one where the overhead AMOUNT reappears on the world side.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from company.interfaces.fixed_overhead import book_monthly_overhead
from company.interfaces.growth_desk import (
    AcquisitionDecision,
    book_acquisition_gate,
    book_acquisition_spend,
    book_retention_cost,
    decide_acquisition,
    growth_mandate_label,
    mandate_permits_replacement,
    replacement_cost_avoided_gbp,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
RUN_PHASE2B = REPO_ROOT / "simulation" / "run_phase2b.py"


class TestBehaviour:
    """Pre-cut answers, transcribed as literals. See the module docstring."""

    def test_the_standing_mandate_label_is_unchanged(self):
        assert growth_mandate_label() == "flat"

    def test_a_flat_mandate_permits_replacement(self):
        assert mandate_permits_replacement() is True

    @pytest.mark.parametrize(
        "segment,expected_budget",
        [("resi", 150.0), ("SME", 400.0), ("micro", 150.0)],
    )
    def test_the_budget_per_segment_including_the_unknown_default(
        self, segment, expected_budget
    ):
        decision = decide_acquisition(
            segment=segment,
            commodity="gas",
            company_fwd_gbp_per_mwh=40.0,
            term_start="2018-04-01",
        )
        assert decision.budget_gbp == expected_budget

    def test_the_gate_fires_only_for_resi_electricity_under_a_binding_cap(self):
        # 2022-10: cap 305 GBP/MWh, so a 400 forward is above it and the
        # supplier declines. Pinned including the reason STRING, because the
        # reason is what reaches the ledger row and a silent reword there is
        # invisible to a boolean-only assertion.
        blocked = decide_acquisition(
            segment="resi",
            commodity="electricity",
            company_fwd_gbp_per_mwh=400.0,
            term_start="2022-10-01",
        )
        assert blocked.attempt is False
        assert blocked.gate_reason == "cap_constrained (cap=305 < fwd=400 GBP/MWh)"

        blocked_2023 = decide_acquisition(
            segment="resi",
            commodity="electricity",
            company_fwd_gbp_per_mwh=400.0,
            term_start="2023-01-01",
        )
        assert blocked_2023.attempt is False
        assert blocked_2023.gate_reason == "cap_constrained (cap=265 < fwd=400 GBP/MWh)"

    @pytest.mark.parametrize(
        "segment,commodity,fwd,term_start",
        [
            # A cheap forward under the same binding cap year — the cap is not
            # the thing that decides, the COMPARISON is.
            ("resi", "electricity", 40.0, "2022-10-01"),
            # Gas is never gated, at any forward.
            ("resi", "gas", 400.0, "2022-10-01"),
            # Non-resi is never gated, at any forward.
            ("SME", "electricity", 400.0, "2022-10-01"),
            ("SME", "gas", 400.0, "2023-01-01"),
            # 2016 predates the domestic cap: no cap, so no gate, even at 400.
            ("resi", "electricity", 400.0, "2016-01-01"),
            # 2018-04 likewise sits before the cap bites at this forward.
            ("resi", "electricity", 400.0, "2018-04-01"),
        ],
    )
    def test_every_other_cell_of_the_grid_proceeds_ungated(
        self, segment, commodity, fwd, term_start
    ):
        decision = decide_acquisition(
            segment=segment,
            commodity=commodity,
            company_fwd_gbp_per_mwh=fwd,
            term_start=term_start,
        )
        assert decision.attempt is True
        assert decision.gate_reason is None

    def test_the_retention_guard_credit_is_the_segments_replacement_cost(self):
        assert replacement_cost_avoided_gbp(segment="resi", counted_in_guard=True) == 150.0
        assert replacement_cost_avoided_gbp(segment="SME", counted_in_guard=True) == 400.0
        assert replacement_cost_avoided_gbp(segment="micro", counted_in_guard=True) == 150.0

    def test_the_frozen_naive_policy_zeroes_that_credit_rather_than_scaling_it(self):
        # The whole effect of `policy.include_acq_cost_saved_in_guard=False`.
        # A guard that merely halved the credit would pass a "less than" check.
        assert replacement_cost_avoided_gbp(segment="SME", counted_in_guard=False) == 0.0
        assert replacement_cost_avoided_gbp(segment="resi", counted_in_guard=False) == 0.0

    def test_the_acquisition_spend_row_is_unchanged_including_its_sign(self):
        assert book_acquisition_spend(
            billing_account="BA-1",
            event_date="2022-04-01",
            amount_gbp=150.0,
            won=True,
            segment="resi",
        ) == {
            "transaction_id": "707a60b4-2769-5dca-b1e9-7fba1abb136b",
            "event_type": "acquisition_spend_event",
            "timestamp": "2022-04-01",
            "billing_account": "BA-1",
            "segment": "resi",
            "amount_gbp": -150.0,
            "acquisition_won": True,
        }

    def test_a_lost_attempt_still_books_the_spend(self):
        # Cash out whether or not it won — the pin that would catch a "only
        # charge for wins" change, which would flatter CAC without touching a
        # single test that only ever exercises the winning path.
        row = book_acquisition_spend(
            billing_account="BA-1",
            event_date="2022-04-01",
            amount_gbp=400.0,
            won=False,
            segment="SME",
        )
        assert row["amount_gbp"] == -400.0
        assert row["acquisition_won"] is False

    def test_the_gate_row_is_zero_amount_and_carries_no_transaction_id(self):
        # The absence of `transaction_id` is PINNED, not overlooked: the spend
        # and retention rows both carry one and this row has never had one.
        # Moving it inside the door is exactly when that asymmetry would get
        # "tidied up" by accident.
        assert book_acquisition_gate(
            billing_account="BA-9",
            event_date="2022-10-01",
            segment="resi",
            gate_reason="cap_constrained (cap=305 < fwd=400 GBP/MWh)",
        ) == {
            "event_type": "acquisition_gate_event",
            "timestamp": "2022-10-01",
            "billing_account": "BA-9",
            "segment": "resi",
            "amount_gbp": 0.0,
            "acquisition_won": False,
            "gate_reason": "cap_constrained (cap=305 < fwd=400 GBP/MWh)",
        }

    def test_the_retention_row_carries_the_belief_that_justified_the_spend(self):
        assert book_retention_cost(
            billing_account="BA-2",
            event_date="2021-07-15",
            cost_gbp=23.4567,
            company_churn_estimate=0.42,
        ) == {
            "transaction_id": "47ecd077-4934-5bbf-9076-0714ec4f93f6",
            "event_type": "retention_cost_event",
            "timestamp": "2021-07-15",
            "billing_account": "BA-2",
            "company_churn_estimate": 0.42,
            "amount_gbp": -23.4567,
        }

    def test_the_overhead_row_is_unchanged_and_the_amount_comes_from_inside(self):
        # `book_monthly_overhead` takes a month and nothing else. The -50.0 is
        # the supplier's own figure, asserted here as a literal precisely
        # because the world can no longer supply or read it.
        assert book_monthly_overhead("2020-03") == {
            "transaction_id": "2f3fdc2b-8207-5e70-b0a8-e0a08d6c4a75",
            "event_type": "fixed_cost_event",
            "timestamp": "2020-03-01",
            "month": "2020-03",
            "amount_gbp": -50.0,
        }

    def test_the_overhead_row_is_stamped_to_the_first_of_its_month(self):
        assert book_monthly_overhead("2019-12")["timestamp"] == "2019-12-01"


class TestTheDoorIsADoor:
    """The failure that leaves the wall ratchet green — see the module docstring."""

    @pytest.mark.parametrize(
        "module_name,forbidden",
        [
            (
                "company.interfaces.growth_desk",
                ("COST_PER_ACQUISITION", "FIXED_COST_MONTHLY", "MANDATE",
                 "ACQUISITION_WIN_RATE", "should_attempt_acquisition",
                 "make_acquisition_spend_event", "make_retention_cost_event",
                 "make_fixed_cost_event"),
            ),
            (
                "company.interfaces.fixed_overhead",
                ("FIXED_COST_MONTHLY", "make_fixed_cost_event"),
            ),
        ],
    )
    def test_no_table_or_desk_entry_point_is_reachable_through_the_door(
        self, module_name, forbidden
    ):
        import importlib

        module = importlib.import_module(module_name)
        leaked = [name for name in forbidden if hasattr(module, name)]
        assert leaked == [], (
            f"{module_name} re-exports {leaked} — a caller can reach the "
            "supplier's own table or desk entry point THROUGH the seam, and the "
            "epistemic ratchet stays green because the import still terminates "
            "on the exempt seam package. Import inside the function body."
        )

    @pytest.mark.parametrize(
        "relpath",
        ["company/interfaces/growth_desk.py", "company/interfaces/fixed_overhead.py"],
    )
    def test_the_saas_imports_are_made_inside_function_bodies(self, relpath):
        tree = ast.parse((REPO_ROOT / relpath).read_text())
        module_level = [
            node
            for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and any(
                (alias.name if isinstance(node, ast.Import) else (node.module or ""))
                .startswith(("saas", "company.pricing", "company.billing"))
                for alias in node.names
            )
        ]
        assert module_level == [], (
            f"{relpath} imports the desk at module scope; that is what puts its "
            "names in the door's namespace."
        )

    def test_the_decision_carries_no_route_back_to_the_table(self):
        decision = decide_acquisition(
            segment="resi",
            commodity="gas",
            company_fwd_gbp_per_mwh=40.0,
            term_start="2018-04-01",
        )
        assert isinstance(decision, AcquisitionDecision)
        # A decided number for ONE segment, never the decision table.
        assert set(vars(decision)) == {"attempt", "gate_reason", "budget_gbp"}
        assert not any(isinstance(value, dict) for value in vars(decision).values())


class TestTheWorldNoLongerHoldsIt:
    """The crossing coming back, in either of its two forms."""

    def test_run_phase2b_imports_neither_saas_module(self):
        source = RUN_PHASE2B.read_text()
        tree = ast.parse(source)
        offenders = sorted(
            {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                and (node.module or "").startswith(("saas.growth_mandate", "saas.ledger"))
            }
        )
        assert offenders == [], (
            f"simulation/run_phase2b.py imports {offenders} again — the crossing "
            "this cut removed is back. Go through company.interfaces.growth_desk "
            "or company.interfaces.fixed_overhead."
        )

    @pytest.mark.parametrize(
        "identifier,what",
        [
            ("FIXED_COST_MONTHLY", "the supplier's monthly overhead figure"),
            ("COST_PER_ACQUISITION", "the supplier's per-segment replacement cost table"),
        ],
    )
    def test_the_suppliers_own_cost_constants_are_unreadable_under_simulation(
        self, identifier, what
    ):
        # The SUBTLER return: not an import, but the figure itself copied onto
        # the world side, where the world could then spend it early, twice, or
        # at a number of its own choosing.
        #
        # DELIBERATELY AST-BASED AND NOT A SUBSTRING SEARCH. A substring search
        # ran first and reported `simulation/acquisition_funnel.py`, which is a
        # DOCSTRING recording design B6's own earlier cut of exactly this name —
        # prose about a crossing that no longer exists. Counting that as a
        # reachable read would make this control fire on the register's own
        # history, and the natural way to green it would be to delete the
        # explanation. The subject is a NAME the interpreter would resolve.
        offenders = []
        for path in (REPO_ROOT / "simulation").rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == identifier:
                    offenders.append(path.relative_to(REPO_ROOT).as_posix())
                    break
                if isinstance(node, ast.Attribute) and node.attr == identifier:
                    offenders.append(path.relative_to(REPO_ROOT).as_posix())
                    break
                if isinstance(node, (ast.Import, ast.ImportFrom)) and any(
                    alias.name == identifier or alias.asname == identifier
                    for alias in node.names
                ):
                    offenders.append(path.relative_to(REPO_ROOT).as_posix())
                    break
        assert sorted(set(offenders)) == [], f"{what} is readable in {sorted(set(offenders))}"
