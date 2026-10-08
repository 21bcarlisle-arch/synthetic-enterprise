"""Acquisition selects on each prospect's own responsiveness (director, 2026-10-08).

The ruling, in `docs/design/curriculum/acquisition_selects_on_own_responsiveness.json`: option 1
on (the funnel's price stage reads the prospect's own latent elasticity, and prospects reach a quote
weighted by their own active-renewal probability); option 2 run both ways (the sensitivity LEVEL
drawn independently of engagement, or by rank on it); no new number; the latent value never crosses
into company/ or saas/.

Every control below names the defect it exists to catch.
"""
from __future__ import annotations

import ast
import datetime as dt
import functools
import json
import statistics as st
from pathlib import Path

import pytest

import simulation.population_draw as pd
from simulation import net_new_acquisition as nna
from simulation.acquisition_funnel import (
    QUOTE_TO_APPLICATION,
    _bernoulli,
    _quote_to_application_rate,
)
from simulation.household_segments import (
    active_renewal_probability_for_customer,
    engagement_propensity_for_customer,
)
from simulation.market_switching_propensity import PRICE_SENSITIVITY_WEIGHT

PROJECT = Path(__file__).resolve().parents[2]
SEED = 20260724
HORIZON = dt.date(2026, 1, 1)

#: A synthetic prospect population, outside the campaign's 2016-2025 window so no run mints it.
_IDS = tuple(f"{nna.PROSPECT_ID_PREFIX}-2099-{i:05d}" for i in range(12000))


def _arm(monkeypatch, arm: str) -> None:
    monkeypatch.setattr(pd, "sensitivity_level_draw", lambda path=None: arm)


# ---------------------------------------------------------------------------
# (a) Option 1 selects on the prospect's own sensitivity -- and the switch-off does not.
# ---------------------------------------------------------------------------

def _applicants_over_market(d: float, own: bool) -> float:
    elasticity = {i: pd._latent_price_elasticity(i, SEED) for i in _IDS}
    market = st.mean(elasticity.values())
    applied = [i for i in _IDS if _bernoulli(
        f"prospect_{i}", "application",
        _quote_to_application_rate("resi", d, elasticity[i] if own else None))]
    assert len(applied) > 500, "the funnel stopped letting prospects through -- nothing to compare"
    return st.mean(elasticity[i] for i in applied) / market


def test_a_the_funnel_wins_MORE_sensitive_prospects_when_on_and_the_market_mix_when_off():
    """DEFECT: a price stage that answers with one population response, so a prospect won by a
    discount carries the market's elasticity mix -- the world hides selection at entry.

    ONE CONTROL OVER THE PARTITION: the on-branch must select (ratio well above 1 when we are
    cheaper, well below when dearer) AND the off-branch must not, beyond sampling noise (12,000
    prospects, lognormal sigma ~0.54: the standard error of the applicants' mean is ~0.02). A switch
    that did nothing passes the off leg; a switch that always selected passes the on leg.
    """
    on_cheap = _applicants_over_market(-0.10, own=True)
    on_dear = _applicants_over_market(+0.10, own=True)
    off_cheap = _applicants_over_market(-0.10, own=False)
    off_dear = _applicants_over_market(+0.10, own=False)

    assert on_cheap > 1.08, f"cheaper than the market won the market mix ({on_cheap:.3f})"
    assert on_dear < 0.92, f"dearer than the market still won the market mix ({on_dear:.3f})"
    assert abs(off_cheap - 1.0) < 0.06 and abs(off_dear - 1.0) < 0.06, (
        f"with the switch off the applicants' sensitivity moved ({off_cheap:.3f}, "
        f"{off_dear:.3f}) -- the population response is supposed to be blind to it")


def test_a_at_PARITY_the_own_elasticity_changes_nothing_and_that_is_arithmetic_not_a_bug():
    """DEFECT this pins: reading the result at the shipped price as 'option 1 did nothing'. The
    elasticity scales the DIFFERENTIAL; at 0.0 there is nothing to scale. Selection on S at parity
    can only come through entry and an E<->S link (arm linked)."""
    for w in (0.3, 1.0, 2.5):
        assert _quote_to_application_rate("resi", 0.0, w) == QUOTE_TO_APPLICATION["resi"]


def test_MUTATION_a_a_price_stage_that_ignores_the_prospects_own_elasticity_selects_nothing(
        monkeypatch):
    """R15 for the partition control above: the pre-ruling price stage, applied to the imported
    module. If the on-branch still selected under it, the selection came from somewhere else."""
    from simulation import acquisition_funnel as af

    real = af._quote_to_application_rate
    monkeypatch.setattr(
        af, "_quote_to_application_rate",
        lambda segment, d=0.0, price_sensitivity=None: real(segment, d, None))
    elasticity = {i: pd._latent_price_elasticity(i, SEED) for i in _IDS}
    market = st.mean(elasticity.values())
    applied = [i for i in _IDS if _bernoulli(
        f"prospect_{i}", "application",
        af._quote_to_application_rate("resi", -0.10, elasticity[i]))]
    assert abs(st.mean(elasticity[i] for i in applied) / market - 1.0) < 0.06


class _Spy:
    """A funnel that records what the campaign handed it and wins every quote."""

    def __init__(self):
        self.calls = []

    def __call__(self, segment, seed, term_start, credit_bureau, total_amount_gbp, **kw):
        self.calls.append((seed, kw))

        class _R:
            won = True
            total_cost_gbp = total_amount_gbp
            stage_reached = "cooling_off"
        return _R()


def _campaign(select: bool | None, funnel, quotes: int = 60):
    kw = dict(
        years=[2018], base_seed=SEED, opening_net_assets_gbp=2_000_000.0,
        accounts_held_at_start=14, horizon_end=HORIZON, credit_bureau=None,
        cost_per_quote_gbp={"resi": 20.0, "SME": 50.0}, run_funnel=funnel,
        quote_budget_fn=lambda net_assets_gbp, accounts_held, quotes_issued_to_date=0,
        wins_to_date=0: {"quotes": quotes, "binding": "capital", "headroom_gbp": net_assets_gbp},
        customer_year_budget=100_000.0,
    )
    if select is not None:
        kw["select_on_own_responsiveness"] = select
    return nna.plan_growth_campaign(**kw)


@functools.lru_cache(maxsize=None)
def _spied(select):
    spy = _Spy()
    outcome = _campaign(select, spy)
    return spy, outcome


def test_a_the_campaign_hands_EACH_prospect_its_own_elasticity_and_reaches_the_shoppers():
    """DEFECT: the switch is read but the campaign never passes the prospect's weight to the
    funnel, or never re-orders who is quoted -- option 1 present in the file and absent in the run.

    Both halves, both branches: on, every quote carries `price_elasticity_for_prospect` of that
    prospect, and the quoted prospects' mean active-renewal probability is above the pool's; off,
    no quote carries a weight and the quoted set is the first `quotes` by position."""
    spy_on, on = _spied(True)
    spy_off, off = _spied(False)

    for seed, kw in spy_on.calls:
        pid = seed.removeprefix("prospect_")
        assert kw.get("price_sensitivity") == nna.price_elasticity_for_prospect(pid, SEED)
    assert spy_on.calls, "the on-branch quoted nobody"
    assert all("price_sensitivity" not in kw for _s, kw in spy_off.calls)

    pool = [f"{nna.PROSPECT_ID_PREFIX}-2018-{i:04d}" for i in range(1, nna.PROSPECTS_PER_YEAR + 1)]
    quoted_on = [r["prospect_id"] for r in on["spend"]]
    quoted_off = [r["prospect_id"] for r in off["spend"]]
    order = nna.engagement_weighted_entry_order(pool, SEED)
    assert len(quoted_on) == len(quoted_off) == 60, "the switch changed HOW MANY were quoted"
    assert set(quoted_on) == {pool[i] for i in order[:60]}, \
        "the switch-on campaign did not quote the first prospects in the engagement-weighted order"
    assert quoted_on == sorted(quoted_on), "quoted prospects must still be resolved in date order"
    assert quoted_off == pool[:60], "the switch-off campaign stopped quoting by position"
    assert set(quoted_on) != set(quoted_off), "the two branches quoted the same homes"


def _first_k_engagement_over_pool(k: int = 2000) -> float:
    order = nna.engagement_weighted_entry_order(_IDS, SEED)[:k]
    weights = [active_renewal_probability_for_customer(i) for i in _IDS]
    return st.mean(weights[i] for i in order) / st.mean(weights)


def test_a_the_entry_order_reaches_the_households_that_shop():
    """DEFECT: an entry order that is not weighted by the chance of shopping. The first 2,000 of
    12,000 must carry clearly more engagement than the pool (size-biased mean / mean is ~1.19 for
    this population; sampling error at k=2,000 is ~0.01)."""
    assert _first_k_engagement_over_pool() > 1.1


def test_MUTATION_a_a_uniform_entry_order_reaches_no_more_shoppers_than_the_pool(monkeypatch):
    """R15 for the control above: replace the engagement weight with a constant. The order is then
    a uniform shuffle and its first 2,000 carry the pool's engagement."""
    import simulation.household_segments as hs

    real = hs.active_renewal_probability_for_customer
    monkeypatch.setattr(hs, "active_renewal_probability_for_customer", lambda cid, **_: 0.35)
    order = nna.engagement_weighted_entry_order(_IDS, SEED)[:2000]
    monkeypatch.undo()
    weights = [real(i) for i in _IDS]
    assert st.mean(weights[i] for i in order) / st.mean(weights) < 1.05


def test_a_the_prospect_accessor_refuses_anything_that_is_not_a_prospect():
    """DEFECT: an unguarded ground-truth lookup that answers for any string (R1's 87 of 264)."""
    assert nna.price_elasticity_for_prospect(_IDS[0], SEED) > 0.0
    for bad in ("C1", "NOT_A_REAL_ID", _IDS[0] + "g"):
        with pytest.raises(ValueError, match="refuses"):
            nna.price_elasticity_for_prospect(bad, SEED)


# ---------------------------------------------------------------------------
# (b) Switch off is today's world.
# ---------------------------------------------------------------------------

def test_b_switch_off_is_the_pre_ruling_campaign_exactly():
    """DEFECT: a revert that does not revert -- `activated: false` must give the campaign the
    pre-ruling call, so the run is byte-identical (measured on a whole 40-founder run in the
    build report; this is the campaign-level leg a test can afford)."""
    spy_default, default = _spied(None)
    spy_off, off = _spied(False)
    assert spy_default.calls == spy_off.calls
    assert default["spend"] == off["spend"]
    assert [(p.customer_id, d) for p, d in default["winners"]] == \
        [(p.customer_id, d) for p, d in off["winners"]]


def test_b_arm_independent_is_the_pre_ruling_level_draw_byte_for_byte(monkeypatch):
    """DEFECT: the independent arm quietly re-drawing levels, which would move every founder's
    churn and make 'switch off' a different world."""
    _arm(monkeypatch, "independent")
    c = pd._load_cohort_curriculum()
    marginals = c["price_sensitivity_marginals"]["value"]
    for cid in _IDS[:2000]:
        before = pd._weighted_choice(pd._cohort_substream(cid, SEED, "price_sensitivity"), marginals)
        assert pd._draw_curriculum_axis(cid, SEED, "price_sensitivity", c) == before


def test_b_the_shipped_curriculum_reads_on_and_independent_and_refuses_a_bad_value(tmp_path):
    """DEFECT: a curriculum file whose value is not what the run reads, or a typo read as off."""
    shipped = json.loads(pd.ACQUISITION_RESPONSIVENESS_PATH.read_text())
    assert pd.acquisition_selects_on_own_responsiveness() is shipped["activated"]["value"] is True
    assert pd.sensitivity_level_draw() == shipped["sensitivity_level_draw"]["value"] == "independent"
    for field, bad in (("activated", "yes"), ("sensitivity_level_draw", "halfway")):
        broken = json.loads(json.dumps(shipped))
        broken[field]["value"] = bad
        path = tmp_path / f"{field}.json"
        path.write_text(json.dumps(broken))
        with pytest.raises(ValueError):
            pd.acquisition_selects_on_own_responsiveness(path)


# ---------------------------------------------------------------------------
# (c) Arm linked keeps the 2% R^2 and the 1.26x spread, and is ranked on engagement.
# ---------------------------------------------------------------------------

def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2.0
        i = j + 1
    return out


def _arm_statistics(monkeypatch, arm: str) -> dict:
    _arm(monkeypatch, arm)
    c = pd._load_cohort_curriculum()
    levels = [pd._draw_curriculum_axis(i, SEED, "price_sensitivity", c) for i in _IDS]
    weights = [pd._latent_price_elasticity(i, SEED) for i in _IDS]
    shares = {k: levels.count(k) / len(levels) for k in PRICE_SENSITIVITY_WEIGHT}
    means = {k: st.mean(w for w, lv in zip(weights, levels) if lv == k) for k in shares}
    grand = st.mean(weights)
    between = sum(shares[k] * (means[k] - grand) ** 2 for k in shares)
    level_weight = [PRICE_SENSITIVITY_WEIGHT[lv] for lv in levels]
    engagement = [engagement_propensity_for_customer(i) for i in _IDS]
    return {
        "shares": shares, "r2": between / st.pvariance(weights),
        "spread": means["high"] / means["low"],
        "rho": st.correlation(_ranks(level_weight), _ranks(engagement)),
    }


@pytest.mark.parametrize("arm", pd.SENSITIVITY_LEVEL_DRAWS)
def test_c_both_arms_keep_the_marginals_the_2pct_R2_and_the_1_26x_spread(monkeypatch, arm):
    """DEFECT: the linked arm buying its coupling by moving how many households are elastic, or
    how much the segment explains -- the two numbers the ruling holds fixed.

    Tolerances are sampling error at n=12,000: shares +-0.015, R^2 +-0.006 around
    PRICE_ELASTICITY_SEGMENT_R2, segment-mean spread +-0.04 around 44/35."""
    s = _arm_statistics(monkeypatch, arm)
    marginals = pd._load_cohort_curriculum()["price_sensitivity_marginals"]["value"]
    for level, share in marginals.items():
        assert s["shares"][level] == pytest.approx(share, abs=0.015), (arm, level, s["shares"])
    assert s["r2"] == pytest.approx(pd.PRICE_ELASTICITY_SEGMENT_R2, abs=0.006), (arm, s["r2"])
    assert s["spread"] == pytest.approx(44 / 35, abs=0.04), (arm, s["spread"])


def test_c_linked_is_ranked_on_engagement_and_independent_is_not(monkeypatch):
    """DEFECT: an arm switch that changes nothing (both arms crossed) or changes the wrong thing
    (coupled the wrong way round). One control over the partition."""
    linked = _arm_statistics(monkeypatch, "linked")["rho"]
    independent = _arm_statistics(monkeypatch, "independent")["rho"]
    assert linked > 0.9, f"linked level is not ranked on engagement (rho={linked:.3f})"
    assert abs(independent) < 0.03, f"independent level is coupled to engagement ({independent:.3f})"


def test_MUTATION_c_a_linked_arm_walked_the_wrong_way_couples_negatively(monkeypatch):
    """R15 for the control above: walk the levels in ASCENDING weight (most engaged = least
    sensitive). The marginals still hold, so only the rank control can see it."""
    import simulation.market_switching_propensity as msp

    monkeypatch.setattr(msp, "PRICE_SENSITIVITY_WEIGHT",
                        {k: -v for k, v in PRICE_SENSITIVITY_WEIGHT.items()})
    _arm(monkeypatch, "linked")
    c = pd._load_cohort_curriculum()
    levels = [pd._draw_curriculum_axis(i, SEED, "price_sensitivity", c) for i in _IDS[:3000]]
    monkeypatch.undo()
    rho = st.correlation(_ranks([PRICE_SENSITIVITY_WEIGHT[lv] for lv in levels]),
                         _ranks([engagement_propensity_for_customer(i) for i in _IDS[:3000]]))
    assert rho < -0.9


# ---------------------------------------------------------------------------
# (d) The latent sensitivity never crosses the wall.
# ---------------------------------------------------------------------------

#: Every accessor that returns a household's or prospect's latent price sensitivity, its level, or
#: the switches that decide how it was drawn.
LATENT_SENSITIVITY_NAMES = frozenset({
    "price_elasticity_for_customer",
    "price_elasticity_for_prospect",
    "_latent_price_elasticity",
    "price_sensitivity_for_customer",
    "_level_by_engagement_rank",
    "engagement_weighted_entry_order",
    "sensitivity_level_draw",
    "acquisition_selects_on_own_responsiveness",
})


def _offenders(paths) -> list[str]:
    found = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            name = (node.attr if isinstance(node, ast.Attribute)
                    else node.id if isinstance(node, ast.Name)
                    else node.name if isinstance(node, ast.alias)
                    else None)
            if name in LATENT_SENSITIVITY_NAMES:
                found.append(f"{path}:{getattr(node, 'lineno', '?')} -> {name}")
    return found


def _company_and_saas_sources() -> list[Path]:
    return sorted(p for root in ("company", "saas") for p in (PROJECT / root).rglob("*.py")
                  if "__pycache__" not in p.parts)


def test_d_no_company_or_saas_module_can_name_the_latent_sensitivity():
    """DEFECT: the company reading a prospect's or customer's true elasticity instead of
    inferring it -- every targeting result would then measure the label, not the method."""
    sources = _company_and_saas_sources()
    assert len(sources) > 50, f"only {len(sources)} modules scanned -- the scan lost its subject"
    offenders = _offenders(sources)
    assert not offenders, "the latent price sensitivity reached the company:\n" + "\n".join(offenders)


def test_MUTATION_d_the_scan_sees_an_import_and_a_call(tmp_path):
    """R15 for the wall control: a module that imports the accessor, and one that calls it as an
    attribute, must both be caught -- or the control above is green on an empty net."""
    a = tmp_path / "a.py"
    a.write_text("from simulation.net_new_acquisition import price_elasticity_for_prospect\n")
    b = tmp_path / "b.py"
    b.write_text("import simulation.population_draw as p\nx = p._latent_price_elasticity('C1', 1)\n")
    assert len(_offenders([a])) == 1 and len(_offenders([b])) == 1


def test_d_nothing_the_campaign_returns_carries_the_weight():
    """DEFECT: the weight riding out on a spend row or a funnel result, where the run's books and
    the seam's typed message would hand it to the company without anyone importing anything."""
    _spy, on = _spied(True)
    for row in on["spend"]:
        assert not any("sensitiv" in k or "elastic" in k for k in row), row
    from simulation.acquisition_funnel import AcquisitionFunnelResult

    assert not any("sensitiv" in f or "elastic" in f
                   for f in AcquisitionFunnelResult.__dataclass_fields__)


def test_b_a_campaign_resolved_under_one_arm_is_never_handed_back_under_another(monkeypatch):
    """DEFECT: the per-process campaign memo keyed without the switches, so a test or tool that
    flips the arm mid-process silently reads the other arm's winners."""
    import simulation.live_population as lp

    keys = set()
    for on in (True, False):
        for arm in pd.SENSITIVITY_LEVEL_DRAWS:
            monkeypatch.setattr(pd, "acquisition_selects_on_own_responsiveness",
                                lambda path=None, _on=on: _on)
            _arm(monkeypatch, arm)
            keys.add(lp._campaign_key(SEED))
    assert len(keys) == 4
