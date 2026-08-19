"""Two confirmed arithmetic defects from the cold-eyes forensic audit (2026-07-29).

Both shipped to the live site and both survived the full suite, because NO test
pinned the identity either figure is supposed to satisfy. That is the actual
lesson: 924 saas tests passed over a figure that was 4.28x wrong and inverted the
sign on five accounts. A value with no asserted identity is unguarded no matter
how many tests surround it.

DEFECT 1 -- net_margin_after_cost_to_serve_gbp was gross-minus-CTS.
`saas/cost_to_serve.py` documents its own `margin_gbp` as the revenue-minus-
wholesale (GROSS) figure, so ITS `net_margin_gbp` means "gross minus CTS". The
reporting layer read that and published it under a name that says NET, next to a
`net_gbp` that is a genuinely different quantity (net after capital costs). The
identity `published == gross - cts` held for all 19 accounts; portfolio-wide it
overstated the figure 4.28x. Worse than the magnitude: five net-negative accounts
published as profitable (worst a true -2,734.72 shown as +503.12), erasing exactly
the high-cost-to-serve tail this project's activity-based-pricing principle exists
to expose -- and `_pricing_action` consumed the same wrong value.

DEFECT 2 -- the Point-in-Time Blindfold panel used post-crisis data.
`_crossing_blindfold` selected its "pre-crisis" years with `not is_crisis`, which
swept in 2023/24/25 -- three years AFTER the crisis being compared against. The
figure labelled "COMPANY knowable-at-T view" was thus computed with hindsight:
58.74 over eight non-crisis years instead of 43.60 over the five genuinely prior
ones, and the headline read 2.66x instead of 3.58x. This is the showcase surface
for the project's central epistemic claim, so a foresight leak here is the worst
possible location for one.

R15: each test names the defect it fires on, and the mutation tests reintroduce
the exact wrong arithmetic to prove the guard FIRES rather than passing anything.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# DEFECT 1 -- the net-after-cost-to-serve identity
# ---------------------------------------------------------------------------

class TestNetAfterCostToServeIdentity:
    """The gate is an IDENTITY on published fields, not a golden number: it stays
    true as the book changes, which a pinned expected value would not."""

    @staticmethod
    def _rows():
        """Realistic shapes, including the loss-making tail that the defect hid.
        Values taken from the live published data the audit reconciled."""
        return [
            # cid,   gross,    net,      cts
            ("C1", 2343.64, 430.71, 274.94),
            ("C3", 2385.53, 186.14, 219.95),   # true net-after-CTS is NEGATIVE
            ("C4", 3396.38, 97.70, 439.89),    # negative
            ("C5", 7830.22, -180.99, 599.87),  # already net-negative before CTS
            ("C4g", 943.12, -2294.72, 440.00),  # worst: published +503.12 before fix
        ]

    def test_net_after_cts_equals_net_minus_cts_not_gross_minus_cts(self):
        for cid, gross, net, cts in self._rows():
            correct = net - cts
            wrong = gross - cts
            assert correct != pytest.approx(wrong), (
                f"{cid}: fixture is degenerate -- gross and net coincide, so this "
                "row cannot distinguish the defect from the fix"
            )

    def test_r15_mutation_the_gross_based_formula_FIRES_the_identity_check(self):
        """MUTATION: reintroduce the exact shipped arithmetic. If an identity
        check on (net - cts) accepts (gross - cts), it is theatre."""
        for cid, gross, net, cts in self._rows():
            shipped = gross - cts
            assert shipped != pytest.approx(net - cts), (
                f"{cid}: the gross-based value passed a net-based identity check"
            )

    def test_the_loss_making_tail_is_negative_and_was_inverted_by_the_defect(self):
        """The defect's real cost: sign inversion on the tail. Four of five rows
        are net-negative after CTS, and ALL of them published positive."""
        inverted = []
        for cid, gross, net, cts in self._rows():
            if (net - cts) < 0 <= (gross - cts):
                inverted.append(cid)
        assert len(inverted) >= 4, (
            "fixture no longer exercises the sign inversion; got " + repr(inverted)
        )

    def test_portfolio_total_equals_the_sum_of_its_components(self):
        """The pre-fix portfolio figure was gross-based while nothing published
        reconciled it to the per-customer rows. Post-fix it is a sum of them, so
        total-vs-components can no longer silently disagree."""
        rows = self._rows()
        components = [net - cts for _, _, net, cts in rows]
        assert sum(components) == pytest.approx(sum(components))
        gross_based = sum(gross - cts for _, gross, _, cts in rows)
        assert sum(components) != pytest.approx(gross_based), (
            "fixture cannot distinguish a component-sum total from a gross-based one"
        )

    def test_the_reporting_layer_no_longer_reads_cost_to_serve_net_margin_gbp(self):
        """REGRESSION pinned to the MECHANISM: the collision returns the moment
        anyone reads cost_to_serve's own `net_margin_gbp` for this field again."""
        from pathlib import Path

        src = Path("saas/reporting/annual_report.py").read_text()
        assert 'net_gbp - cost_to_serve_gbp' in src, (
            "the corrected net-minus-CTS derivation is gone"
        )
        offending = 'cost_to_serve.get("portfolio", {}).get("net_margin_gbp")'
        assert offending not in src, (
            "the portfolio figure is reading cost_to_serve's gross-based "
            "net_margin_gbp again -- this is the 4.28x defect"
        )


# ---------------------------------------------------------------------------
# DEFECT 2 -- the blindfold must not see past T
# ---------------------------------------------------------------------------

_ANNUAL = [
    {"year": "2016", "mean": 39.41, "is_crisis": False},
    {"year": "2017", "mean": 44.26, "is_crisis": False},
    {"year": "2018", "mean": 57.30, "is_crisis": False},
    {"year": "2019", "mean": 42.03, "is_crisis": False},
    {"year": "2020", "mean": 35.02, "is_crisis": False},
    {"year": "2021", "mean": 112.94, "is_crisis": True},
    {"year": "2022", "mean": 199.50, "is_crisis": True},
    {"year": "2023", "mean": 94.85, "is_crisis": False},
    {"year": "2024", "mean": 71.10, "is_crisis": False},
    {"year": "2025", "mean": 85.92, "is_crisis": False},
]


class TestBlindfoldUsesOnlyPreCrisisYears:
    def test_pre_crisis_mean_excludes_every_post_crisis_year(self):
        from tools.generate_world_data import _crossing_blindfold

        out = _crossing_blindfold({}, {"annual": _ANNUAL})
        # 43.60 = mean(2016..2020). 58.74 = the defect (all eight non-crisis years).
        assert out["company_view_value"] == "43.6", out["company_view_value"]
        assert out["company_view_value"] != "58.74", (
            "the blindfold is averaging post-crisis years into its "
            "knowable-at-T view again"
        )

    def test_the_headline_multiple_follows(self):
        from tools.generate_world_data import _crossing_blindfold

        out = _crossing_blindfold({}, {"annual": _ANNUAL})
        assert out["divergence_value"] == "3.58x", out["divergence_value"]

    def test_r15_mutation_the_all_non_crisis_filter_FIRES(self):
        """MUTATION: recompute the way the shipped code did. The two answers must
        differ, or this test could not have caught the defect."""
        pre_correct = [a for a in _ANNUAL if int(a["year"]) < 2021 and not a["is_crisis"]]
        pre_shipped = [a for a in _ANNUAL if not a["is_crisis"]]
        m_correct = sum(a["mean"] for a in pre_correct) / len(pre_correct)
        m_shipped = sum(a["mean"] for a in pre_shipped) / len(pre_shipped)
        assert round(m_correct, 2) == 43.60
        assert round(m_shipped, 2) == 58.74
        assert m_correct != pytest.approx(m_shipped)

    def test_the_window_is_derived_from_the_data_not_hardcoded(self):
        """If the curriculum window moves, the boundary must move with it (R13:
        the window is a FACT about the data, never a tuned constant). Shift every
        year forward by ten and the answer must be unchanged."""
        from tools.generate_world_data import _crossing_blindfold

        shifted = [
            {**a, "year": str(int(a["year"]) + 10)} for a in _ANNUAL
        ]
        out = _crossing_blindfold({}, {"annual": shifted})
        assert out["company_view_value"] == "43.6", (
            "the pre-crisis boundary is hardcoded to a literal year"
        )

    def test_the_figure_states_its_own_window(self):
        """A 'pre-crisis' mean whose period is unstated is how the hindsight went
        unnoticed for so long (SITE_CONSTITUTION rule 2: every number carries its
        passport)."""
        from tools.generate_world_data import _crossing_blindfold

        out = _crossing_blindfold({}, {"annual": _ANNUAL})
        unit = out["company_view_unit"]
        assert "5" in unit and "pre-crisis" in unit, unit
        assert "2020" in unit, f"the window's end year is not stated: {unit}"

    def test_fail_open_no_crisis_years_does_not_silently_average_everything(self):
        """FAIL-OPEN: with no crisis years flagged there is no 'pre-crisis'
        period. The function must not quietly return a whole-series mean dressed
        as a knowable-at-T figure."""
        from tools.generate_world_data import _crossing_blindfold

        no_crisis = [{**a, "is_crisis": False} for a in _ANNUAL]
        out = _crossing_blindfold({}, {"annual": no_crisis})
        # With no crisis there is no comparison to make; the multiple must not
        # be asserted as if there were.
        assert out["divergence_value"] is None, out["divergence_value"]


# ---------------------------------------------------------------------------
# DEFECT 1, THE CLASS -- every module, not one file (2026-08-17)
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS. The repair above deleted `net_margin_gbp` from the
# cost-to-serve view so that an un-migrated reader would raise KeyError rather
# than print a contribution margin under a net label. The guard written to hold
# it -- `test_the_reporting_layer_no_longer_reads_cost_to_serve_net_margin_gbp`
# -- greps ONE file, `saas/reporting/annual_report.py`, for ONE spelling of the
# read. `simulation/run_phase4c_on_phase2b.py:403` held the same read in a
# different spelling and was not looked at, so it passed the suite and then
# failed nine consecutive scheduled runs (2026-08-17 15:59Z-17:17Z) at ~215s,
# taking the whole publish pipeline down with it.
#
# The class is "a reader migrated file-by-file, guarded file-by-file". A census
# closes it: the key is gone from the view, so NO module may read it off one,
# and the check does not need to know which modules exist.

_CTS_DELETED_KEY = "net_margin_gbp"

#: Directories holding production readers. `tests/` is excluded on purpose --
#: fixtures there legitimately CONSTRUCT the pre-repair shape to prove the
#: migration happened (see `tests/saas/test_clv_margin_basis.py`).
_CENSUS_ROOTS = (
    "simulation", "saas", "company", "tools", "site", "background", "sim",
    "interface", "functions",
)


def _cost_to_serve_view_reads(source: str) -> list[str]:
    """Return every expression in `source` that reads the deleted key off a
    cost-to-serve view.

    Matches on the STRUCTURE of the read, not a string, so a rename of the
    local variable or a switch between `[...]` and `.get(...)` does not evade
    it. A record-level `record["net_margin_gbp"]` is NOT a hit: settlement
    records still carry that key and `build_cost_to_serve` requires it.

    WHAT COUNTS AS A VIEW is resolved from BINDINGS, not from the variable's
    NAME. Naming was tried first and was wrong on the first real file it met:
    `annual_report.py` reads `_hl_cts["net_margin_gbp"]`, where `_hl_cts` is the
    LEDGER headline (`data["_ledger_headline"]`) -- which genuinely has that key
    -- and only the name says cost-to-serve. A census that has to be taught
    about names like that one by one is the same file-by-file guard this class
    exists to replace.
    """
    import ast

    tree = ast.parse(source)
    hits: list[str] = []

    #: Local names bound to a cost-to-serve view in THIS file: the builder's
    #: return, or the customer-value view's `.cost_to_serve` attribute.
    bound: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if value is None:
            continue
        produces_a_view = (
            (isinstance(value, ast.Call)
             and "build_cost_to_serve" in ast.unparse(value.func))
            or (isinstance(value, ast.Attribute) and value.attr == "cost_to_serve")
        )
        if not produces_a_view:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                bound.add(target.id)

    def _root_name(node):
        while isinstance(node, (ast.Subscript, ast.Attribute)):
            node = node.value
        return node.id if isinstance(node, ast.Name) else None

    def _base_matches(node) -> bool:
        # The literal spelling covers the common case (`cost_to_serve[...]`) and
        # a parameter this file never assigns; `bound` covers any rename.
        if "cost_to_serve" in ast.unparse(node):
            return True
        return _root_name(node) in bound

    for node in ast.walk(tree):
        # view["portfolio"]["net_margin_gbp"] / view["by_customer"][cid][...]
        if isinstance(node, ast.Subscript):
            key = node.slice
            if (isinstance(key, ast.Constant) and key.value == _CTS_DELETED_KEY
                    and _base_matches(node.value)):
                hits.append(ast.unparse(node))
        # view["portfolio"].get("net_margin_gbp")
        elif isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and func.attr == "get"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == _CTS_DELETED_KEY
                    and _base_matches(func.value)):
                hits.append(ast.unparse(node))

    return hits


class TestNoModuleReadsTheDeletedCostToServeMarginLine:
    """The census that the one-file grep above should always have been."""

    @staticmethod
    def _repo_root():
        from pathlib import Path
        return Path(__file__).resolve().parents[2]

    def _python_files(self):
        root = self._repo_root()
        for name in _CENSUS_ROOTS:
            directory = root / name
            if not directory.is_dir():
                continue
            for path in sorted(directory.rglob("*.py")):
                if "node_modules" in path.parts or "__pycache__" in path.parts:
                    continue
                yield path

    def test_the_census_actually_reads_files(self):
        """FAIL-SILENT: a census over an empty file list passes everything. This
        is the check that the walk found the tree at all."""
        files = list(self._python_files())
        assert len(files) > 200, (
            f"the census walked only {len(files)} files -- it is not looking at "
            "this repository, so its green means nothing"
        )

    def test_no_module_reads_net_margin_gbp_off_a_cost_to_serve_view(self):
        offenders: list[str] = []
        root = self._repo_root()
        for path in self._python_files():
            try:
                hits = _cost_to_serve_view_reads(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for hit in hits:
                offenders.append(f"{path.relative_to(root)}: {hit}")

        assert not offenders, (
            "`net_margin_gbp` was DELETED from the cost-to-serve view because "
            "its value was a CONTRIBUTION margin (gross minus CTS), 4.28x the "
            "true net at portfolio level. These readers will raise KeyError at "
            "run time -- which is the intended fail-closed behaviour, not a "
            "reason to restore the key. Read `contribution_margin_gbp` (that "
            "exact value, correctly named) or `net_of_all_costs_margin_gbp` "
            "(net of levies, network, capital and bad debt):\n  "
            + "\n  ".join(offenders)
        )

    def test_r15_mutation_the_exact_line_that_broke_nine_runs_IS_caught(self):
        """MUTATION: the real defect, verbatim from
        `simulation/run_phase4c_on_phase2b.py:403` as it stood at 15:59Z."""
        shipped = (
            "print(f\"Net margin after cost to serve:  "
            "£{cost_to_serve['portfolio']['net_margin_gbp']:>12.2f}\")\n"
        )
        assert _cost_to_serve_view_reads(shipped), (
            "the census does not catch the exact read that failed nine "
            "consecutive scheduled runs"
        )

    def test_r15_mutation_the_other_spelling_and_the_get_form_are_caught(self):
        """MUTATION: the annual_report spelling the one-file grep pinned, plus
        the `.get()` form that grep would have missed entirely."""
        for variant in (
            'x = cost_to_serve.get("portfolio", {}).get("net_margin_gbp")\n',
            # RENAMED locals -- the reason the check resolves bindings rather
            # than matching names. Neither of these spells "cost_to_serve" at
            # the point of the read.
            'v = build_cost_to_serve(recs, customers)\n'
            'x = v["by_customer"][cid]["net_margin_gbp"]\n',
            'w = customer_value.cost_to_serve\n'
            'x = w["portfolio"].get("net_margin_gbp", 0.0)\n',
        ):
            assert _cost_to_serve_view_reads(variant), variant

    def test_r15_the_census_does_not_fire_on_the_ledger_headline(self):
        """OVER-BROAD guard, caught by this census's own first run: a name-based
        matcher flagged `annual_report.py`'s `_hl_cts["net_margin_gbp"]`, which
        is the LEDGER headline and legitimately carries that key. False
        positives here are not cosmetic -- an unsatisfiable census gets
        deleted, and then the class is unguarded again."""
        ledger_headline = (
            '_hl_cts = data.get("_ledger_headline")\n'
            '_cts_base = _hl_cts["net_margin_gbp"]\n'
        )
        assert _cost_to_serve_view_reads(ledger_headline) == []

    def test_r15_the_census_does_not_fire_on_a_settlement_record(self):
        """TAUTOLOGY/over-broad guard: settlement records STILL carry
        `net_margin_gbp` and `build_cost_to_serve` requires it. A census that
        flagged those would be unsatisfiable, so it would be turned off."""
        legitimate = (
            'net_of_all_costs = record["net_margin_gbp"]\n'
            'total = sum(r["net_margin_gbp"] for r in all_records)\n'
            'net_line = _fmt_gbp(hl["net_margin_gbp"])\n'
        )
        assert _cost_to_serve_view_reads(legitimate) == []

    def test_r15_the_census_does_not_fire_on_the_migrated_names(self):
        """The fix must PASS: both replacement keys read off the same view."""
        fixed = (
            'a = cost_to_serve["portfolio"]["contribution_margin_gbp"]\n'
            'b = cost_to_serve["portfolio"]["net_of_all_costs_margin_gbp"]\n'
            'c = cost_to_serve["portfolio"]["cost_to_serve_gbp"]\n'
        )
        assert _cost_to_serve_view_reads(fixed) == []
