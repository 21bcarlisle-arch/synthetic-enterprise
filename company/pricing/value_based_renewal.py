"""Price one renewal on what THAT customer is worth, and keep the flat rule beside it as the control.

REUSE: company/pricing/value_based_renewal.py
CLASS: CUSTOM
INDEX: searched "renewal", "price", "margin", "clv", "lifetime", "churn", "retention", "offer",
       "cost to serve", "decision". Six organs came back and every one of them is CALLED here
       rather than rebuilt, because the whole point of this module is that the company already
       knows enough to decide and does not:
         - `company/crm/enriched_churn_estimate.enriched_churn_estimate` — P(leave) given a
           CANDIDATE new rate, from company observables only. This is the load-bearing one and
           it is already GRADED against the world's truth (`churn_estimate_error_pct`).
         - `saas/clv_model.expected_lifetime_periods` + `_annuity_factor` + `DISCOUNT_RATE_ANNUAL`
           — the horizon and the discounting the book is already valued on. A second opinion
           about how long a customer lasts would be a second CLV.
         - `saas/cost_to_serve.build_cost_to_serve` — what this account costs to serve, per year.
         - `saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH` — the flat rule, imported as the
           CONTROL rather than copied, so the control cannot drift from what the company
           actually does today.
         - `company/pricing/renewal_desk.strike_fixed_unit_rate` is deliberately NOT called: this
           module decides a MARGIN, and the rate chain stays exactly where it is.
       Nothing here computes a churn probability, a lifetime or a cost.

WHY THIS EXISTS
---------------
Director, 2026-08-25, stating the thesis: *"a supplier that makes commercial and operational
decisions customer-by-customer on lifetime value — using only what it can actually know ...
Measured against that, what exists today is rules, not decisions: a dunning ladder, a churn
estimate, a price. Nothing yet chooses per customer on what that customer is worth."*

Read off HEAD, that is exactly right, and the renewal price is the sharpest instance:

    saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH = 2.00

Two pounds a megawatt-hour, for every customer on the book, whoever they are. The one hook that
could have varied it — `price_fixed_tariff(..., profitability_uplift_per_mwh=...)` — has NO
CALLER anywhere in the tree, so even the parameter that exists is dead.

Meanwhile the company holds two honest per-customer beliefs and acts on neither. It estimates
P(leave) per account at a candidate rate and SCORES that estimate against what the world
actually did. It computes cost-to-serve per account. Both are then reported and dropped.

THE DECISION
------------
Ask the company's own churn model what each candidate margin would do to this customer's chance
of staying, and take the one with the highest expected discounted contribution:

    EV(m) = P(stay | m) x (m x eac_mwh + fixed_revenue - expected_cost(m)) x annuity(lifetime, r)

A COARSE GRID BRACKETS IT AND A REFINEMENT DECIDES IT (2026-08-25), because for four months a
grid alone did both jobs and could only ever return one of its own sixteen numbers. Over the
real book that produced 107 accounts on exactly 130.00 and 83 on exactly 100.00 -- a record of
"per-customer decisions" in which two rungs carried 72% of the customers. See
`MARGIN_RESOLUTION_GBP_PER_MWH`.

A cheap-to-serve customer who is unlikely to leave is worth keeping keenly. One who is leaving
anyway and expensive to serve should not be bought back at a loss. Neither sentence is
expressible in a flat £2.

THE ADVANTAGE IS INFERENCE, NEVER ACCESS, and that is a property of the arithmetic rather than a
promise. Every term above is the company's own belief from its own records: the rate it charged,
the rate it is about to offer, tenure from its own contracts, consumption from its own meters,
payment behaviour from its own ledger, cost from its own cost model. The world's true churn
probability exists — `sim_churn_probability` rides on the churn event — and this module cannot
name it, cannot reach it, and a test refuses any import that would let it.

So this arm beats flat EXACTLY to the degree `enriched_churn_estimate` predicts better than
chance, and not at all otherwise. If that model is noise, the grid search maximises noise and
the arm loses. That is the intended failure mode, it is not guarded against, and
`test_a_BLIND_churn_model_gives_the_value_arm_NO_advantage` pins it.

THE CONTROL, AND WHY IT IS FREE
-------------------------------
The director: *"there has to be a baseline to beat. Average behaviour is the control — the same
book run by a supplier applying flat rules with no per-customer view. Without that comparison,
'it performed well' means nothing."*

Today's company IS that control, exactly — flat £2.00, no per-customer view — so the baseline
does not have to be invented, only FROZEN before it is replaced. `decide_margin(arm=FLAT_RULES)`
returns what HEAD does today and imports the constant rather than restating it, so the control
cannot quietly drift toward the arm it is supposed to judge.

WHAT THIS MODULE DOES NOT CLAIM, said here because the claim would be easy to make and wrong.
It does not show that pricing on value earns more. It cannot: the objective is built from the
company's own beliefs, so scoring the arms on EXPECTED value would let the value arm win by
construction — it maximises the very number it would be judged on, which is R15's tautology
pattern with money in it. The only honest comparison is REALISED: the same book, the same world,
run once per arm, scored on what actually happened. That needs two runs and it is the next step,
not this one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from company.crm.churn_model import CHURN_SEGMENTS, RESI_SEGMENT, SME_SEGMENT
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.regulatory.pricing_permissions import check_class_margin
from saas.clv_model import DISCOUNT_RATE_ANNUAL, _annuity_factor
from saas.payment_behaviour import DEFAULT_CREDIT_RISK, bad_debt_provision_gbp
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH

#: The two arms. `FLAT_RULES` is what the company does today and is the CONTROL; `VALUE_BASED`
#: is the arm under test. Named rather than a boolean so a decision record says which supplier
#: made it, and so a third arm can be added without every call site growing a second flag.
FLAT_RULES = "flat_rules"
VALUE_BASED = "value_based"

#: THE LEVEL-WITHOUT-SELECTION ARM (2026-08-27, director-directed). Applies ONE uplift to every
#: renewal it prices -- the same renewals `value_based` prices, through the same guards and under
#: the same lawful ceiling -- so the two arms differ by the CHOOSING and by nothing else.
#:
#: It exists because the value arm's £7,066 advantage came with `discrimination_auc` 0.4653, which
#: cannot be attributed to inference. (RESTATED 2026-08-30: this said "below a coin flip". It is
#: not below one -- on that run's 16 retentions and 9 departures the exact null runs 0.264..0.736,
#: making 0.4653 two-sided p 0.80, INDISTINGUISHABLE from a coin flip. The conclusion is unchanged
#: and better founded: an advantage cannot be attributed to a ranking the run could not show
#: exists.) What the arm demonstrably did was price
#: high (median £44.50/MWh against the flat rule's £2.00). Without this arm there is no way to
#: separate "chose well" from "charged more", and the A/B's own `bound_attribution.reading`
#: already says a delta it cannot attribute "is a statement that this run did not test it".
#:
#: NOT `FLAT_RULES` AT A DIFFERENT CONSTANT. `flat_rules` applies NO uplift at all -- its £2.00
#: lives in the base rate of every contract -- so raising that constant raises the price for every
#: customer on every contract, not for the renewals the arm priced. A whole-book price rise and a
#: renewal-time price rise are different experiments; the first was tried on 2026-08-27, returned
#: a 9.4x artefact, and was withdrawn.
FLAT_AT_LEVEL = "flat_at_level"

ARMS = (FLAT_RULES, VALUE_BASED, FLAT_AT_LEVEL)

#: The margins the value arm may choose between, £/MWh. Deliberately BRACKETING the flat rule
#: rather than starting at it: an arm that can only price ABOVE the control would beat it on
#: revenue-per-retained-customer by construction and lose customers to pay for it, and one that
#: can only price BELOW would be a discount programme wearing a decision's clothes.
#:
#: THE FIRST GRID WAS 0.50..8.00 AND IT WAS DECIDING NOTHING. Measured on the first probe, every
#: customer shape came back at exactly 8.00 -- the ceiling -- because over that range the
#: company's churn model barely moves: £2 to £8 on a 3,100 kWh account is £18.60 a year on a
#: ~£1,700 bill, about one percent, and the DESNZ-calibrated switching curve correctly shrugs at
#: one percent. The "decision" was my own constant, read back.
#:
#: Widened until the model actually turns over, which it does. Re-measured 2026-08-25 on the same
#: account (3,100 kWh, on £120/MWh over a £118 base, four years' tenure, £80/yr to serve, £98.55
#: of standing charge, six periods, renewing in 2025) — the earlier table here was taken before
#: the churn model's captive floor was removed and before the supplier-specific/market-wide split
#: reached the decision, and both moved it:
#:
#:      margin   offered   P(leave)        EV
#:        2.00     120.0     0.127     65.79
#:       20.00     138.0     0.241    238.11
#:       66.25     184.2     0.538    427.18     <- turn-over, and where the arm lands
#:      130.00     248.0     0.911    157.47
#:      200.00     318.0     0.979     56.47
#:
#: That is a finding about the company and not about this grid, and it is stated rather than
#: tuned away: ON ITS OWN MODEL, the flat £2 is an order of magnitude below the value-maximising
#: margin, and the only thing that stops a value-maximising supplier charging it is the
#: competitive/lawful ceiling the renewal desk already applies. `max_offered_rate_gbp_per_mwh`
#: is where that comes in, and `ceiling_bound` is how a reader is told it bound.
#:
#: THE TOP OF THIS GRID IS STILL A POLICY AND NOT A DERIVATION. One account of the 263 (a 954
#: kWh meter) wants more than £200/MWh and gets £200 — reported `endpoint_side="ceiling"`, and
#: left there deliberately: extending the grid so that one account reads as an "optimum" would
#: publish a £250/MWh domestic commodity margin as a decision. Whether a supplier's grid should
#: reach that far is a pricing policy, which is the director's, and it is one account.
CANDIDATE_MARGINS_GBP_PER_MWH: tuple[float, ...] = (
    0.50, 1.00, 2.00, 3.00, 5.00, 8.00, 12.00, 20.00, 30.00, 45.00,
    60.00, 80.00, 100.00, 130.00, 160.00, 200.00,
)

#: THE GRID BRACKETS. THIS DECIDES. £/MWh, and the reason it exists is a measurement.
#:
#: On 2026-08-25 the arm was run over the real book and 107 of 263 accounts came back at exactly
#: 130.00 GBP/MWh, 83 more at exactly 100.00 — two of this module's own constants, carrying 72%
#: of the book between them. That reads as "the bound decided", and it is worse than that: the
#: bound was not even binding. Re-scored on a 0.25 lattice the same 263 accounts have 180
#: DISTINCT optima, every one of them strictly interior to the region the churn model supports,
#: and the modal margin covers 5 accounts rather than 107. The optima were always per-customer;
#: the grid was rounding them onto four rungs whose gaps (100 -> 130 -> 160) are thirty pounds
#: wide, in a region where the whole spread of the book's answers is a hundred.
#:
#: A COARSE GRID IS NOT A CONSERVATIVE CHOICE, it is a silent one. It cannot make the arm's
#: answer wrong by more than its own spacing, which is exactly the amount that decides whether a
#: reader sees a decision or a constant. `tests/company/pricing/test_value_based_renewal.py::
#: test_forgetting_the_STANDING_CHARGE_makes_the_arm_OVER_PRICE` had already worked around this
#: by hand — it passes its own £1 grid, with a comment saying a grid whose gaps are wider than
#: the effect measures the grid. That was true of every caller, not just that test.
#:
#: 0.25 GBP/MWh is about 80p a year on a 3.1 MWh domestic account: below anything a renewal
#: quote would meaningfully distinguish, so refining further would report precision the decision
#: does not have.
MARGIN_RESOLUTION_GBP_PER_MWH: float = 0.25

#: Sub-intervals per refinement pass. Nine points, re-bracket on the winner, halve-ish and
#: repeat: each pass narrows the bracket by 4x, so any bracket this grid can produce reaches
#: 0.25 in at most eight passes and ~70 churn evaluations. Bounded on purpose — the null-control
#: test hands this module a grid running to £5,000/MWh, and a flat scan of that at 0.25 would be
#: twenty thousand evaluations per customer.
_REFINEMENT_SAMPLES: int = 8
_REFINEMENT_MAX_PASSES: int = 12

def max_supported_rate_increase_pct() -> float:
    """The largest single-step price rise this company's churn model has any evidence for,
    DERIVED from the published domestic cap rather than chosen.

    WHY A DECISION NEEDS THIS AND A REPORT DOES NOT. `company/crm/churn_model.py` caps churn at
    `MAX_CHURN_PROBABILITY = 0.95` and saturates toward it: measured, a customer facing +100%
    leaves with p=0.86, +200% with p=0.946, +400% with p=0.950. So five percent of the book is
    modelled as staying WHATEVER they are charged — harmless in a number that is reported, and
    fatal in one that is maximised, because expected value then rises without bound in the
    price. Run unbounded against the real book, this arm priced all 263 accounts between £60 and
    £200/MWh against a flat £2 — thirty to a hundred times, enough to double a domestic bill —
    and reported no losses, because on the model there are none. The maximiser was not wrong; it
    found a floor of unconditionally captive customers and did exactly what that implies.

    THE FIX IS NOT TO CHANGE THE MODEL. That cap is a calibrated company belief and moving it so
    this arm behaves is precisely the goal-seeking R12 forbids. The fix is that a DECISION may
    not rest on an extrapolation its belief cannot support.

    THE BOUND IS SOURCED, NOT PICKED. `estimate_churn_probability` is calibrated on GB domestic
    switching behaviour, and the largest single-step domestic price move ever published is the
    Ofgem cap's own — +83.1% on 1 Oct 2022, from `PUBLISHED_CAP_WINDOWS`, the same commons
    artefact both lanes read. Domestic customers have never been observed responding to a bigger
    one-step rise than the market itself has ever made, so the company may not price on a
    prediction beyond it. Derived from the schedule rather than written down, so a re-ingest
    moves it and a reader can decompose it.

    READ THROUGH THE COMPANY'S OWN CAP MODULE, and the first draft got this wrong: it imported
    `simulation.price_cap_enforcement` — the WORLD's reading of the same schedule — and this
    module's own wall test refused it, correctly and immediately. The regulatory TEXT is a shared
    commons, but each lane's READING of it is independently owned, which is the whole point of
    `company/pricing/ofgem_price_cap.py` existing separately at all. A supplier bounds its own
    pricing by its own reading of the law; borrowing the world's would be the company checking
    its homework against the answer sheet.

    THE BOUND IS DOMESTIC AND IT IS APPLIED TO EVERY SEGMENT. Stated here because it was not
    (2026-08-27). Every sentence above justifies this number from DOMESTIC evidence -- GB
    domestic switching behaviour, the Ofgem domestic cap's own largest step -- and
    `decide_margin` applies it to whatever it is given, SME and I&C included. Neither is on the
    domestic cap, and `churn_model` branches to a different curve for them entirely
    (`IC_BASE_CHURN_RATE` 0.20 against 0.10, `IC_RATE_SENSITIVITY` 1.5 against 0.8, and no
    bill-stress term at all). A bound whose whole defence is "domestic customers have never been
    observed responding to a bigger one-step rise" defends nothing about a business account.

    IT IS LEFT APPLIED ANYWAY, deliberately, and the reason is the measurement. The served book
    is 417 resi and **2 SME** -- 0.5%, and no I&C at all while the director's suspension stands.
    The alternatives are worse at that size: refusing non-domestic accounts would raise
    `MarginDecisionUnavailable` on every SME renewal and take two real accounts out of the arm to
    fix a category error affecting two real accounts; and inventing a non-domestic frontier with
    no published series behind it would be the picked number this function exists not to be
    (there IS no non-domestic Ofgem cap -- the 2022 non-domestic intervention was a subsidy, not
    a cap, so the commons artefact simply does not carry the step this derivation needs).

    SO IT IS A TRIPWIRE, NOT A SILENCE. `tests/company/pricing/test_the_support_bound_is_domestic.py`
    fails the moment the non-domestic share of the priceable book grows past a threshold, with
    the instruction to derive a non-domestic bound rather than to raise the threshold. An
    accepted limitation that nothing measures is how a 0.5% exposure becomes a 20% one silently.
    """
    from company.pricing.ofgem_price_cap import _CAP_WINDOWS

    steps = []
    previous = None
    for window in _CAP_WINDOWS:
        level = window.get("elec")
        if previous and level:
            steps.append(100.0 * (level - previous) / previous)
        previous = level or previous
    if not steps:
        raise MarginDecisionUnavailable(
            "the published cap schedule carries no step to derive a support bound from, so "
            "there is no defensible range for this decision -- not an unbounded one"
        )
    return max(steps)


#: Payment-behaviour scores that mean this household is in difficulty. Taken from the company's
#: OWN ledger, which is where a real supplier sees it.
DISTRESS_SCORES = (BehaviourScore.POOR, BehaviourScore.CRITICAL)

#: Bill shocks that count as distress on their own, for an account with no behaviour score yet.
#: Two rather than one: a single shock is a cold winter.
DISTRESS_BILL_SHOCKS = 2

#: A customer with no usable lifetime estimate is priced at ONE period rather than at the book's
#: average. Borrowing the average would let a brand-new account inherit a long lifetime it has
#: given no evidence for, which is the direction that flatters the value arm — it would justify
#: keener pricing on exactly the accounts the company knows least about.
FALLBACK_LIFETIME_PERIODS = 1.0


class MarginDecisionUnavailable(Exception):
    """The decision could not be made. Never a silent fall back to the flat rule.

    A value arm that quietly returns the control's answer whenever an input is missing would
    report itself as "no different from flat" on every account it could not price, which is
    indistinguishable from an arm that ran and found nothing to gain (R15 fail-silent).
    """


@dataclass(frozen=True)
class MarginDecision:
    """One customer's margin, and enough of the reasoning to refute it."""

    customer_id: str
    arm: str
    margin_gbp_per_mwh: float
    #: The company's OWN expected discounted contribution at the chosen margin. A belief, and
    #: labelled as one: it is never evidence that the decision was right.
    expected_value_gbp: float
    p_retain: float
    expected_periods: float
    cost_to_serve_gbp_per_year: float
    eac_mwh: float
    #: Every candidate and its score, so a reader can see the shape of the trade-off rather than
    #: take the argmax on trust. Cheap: sixteen rows.
    considered: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    #: TRUE when the choice sits at an END of the searchable interval. An argmax at an endpoint is
    #: not an optimum, it is a constant of this module read back, and the first version of this
    #: grid returned one for every customer shape probed. Reported so nobody has to notice.
    endpoint_bound: bool = False
    #: WHICH end, because they are opposite statements about the customer and the verdict that
    #: reads this used to call both of them "chose the highest margin available". `"ceiling"`
    #: means the arm wanted to charge more than it was allowed to. `"floor"` means it wanted to
    #: charge LESS than the lowest margin on offer — measured, that is a 190 kWh/year account
    #: whose standing charge is the entire relationship, and whose profit-maximising COMMODITY
    #: margin is negative. Both are the bound deciding; only one of them is the arm straining
    #: upward, and a reader told the wrong one draws the opposite conclusion.
    endpoint_side: str | None = None
    #: How many candidates the ceiling and support bounds took off the grid before the search saw
    #: it. A COUNT AND NOT A VERDICT: `ceiling_bound`/`extrapolation_bound` say whether removing
    #: them changed the answer, which on the real book they mostly did not — 165 accounts had
    #: candidates trimmed and none of them would have chosen a trimmed one.
    candidates_removed: int = 0
    #: The cost terms behind `expected_value_gbp`, itemised, and which of them this company has
    #: no figure for. A total that is missing collections cost or standing-charge revenue is a
    #: different number from one that is not, and only this field can tell them apart.
    costs: "ExpectedAnnualCosts | None" = None
    #: WHY the value arm declined to charge what it wanted to. `None` when it did not decline.
    #: This is the one place the arm is deliberately NOT a maximiser, and it says so out loud.
    withheld_reason: str | None = None
    #: TRUE when the support bound actually DECIDED — the margin this customer's own curve peaks
    #: at lies beyond anything the churn model has evidence for, so the arm was stopped short of
    #: its own answer. Until 2026-08-25 this meant merely that candidates had been REMOVED, which
    #: on the real book was true for 165 of 263 accounts and binding for none of them: the peak
    #: sat far below the frontier and the trimmed candidates were ones the arm was never going to
    #: choose. A flag that fires when nothing happened is read as a cause, and it was.
    extrapolation_bound: bool = False
    #: TRUE when the lawful/competitive ceiling actually DECIDED, same sense as above. A
    #: value-maximising supplier is still a supplier that obeys the cap, and when the cap is what
    #: chose the price the reader should be told that rather than shown a "decision".
    ceiling_bound: bool = False
    #: THE RUNG. `margin_gbp_per_mwh` is what this customer is actually offered; when the ladder
    #: multiplier is not 1.0 that is a fraction (or a multiple) of what the arm's own search chose,
    #: and this field carries the search's unscaled answer so the two are never confused. `None`
    #: on an ordinary decision, where they are the same number.
    unscaled_margin_gbp_per_mwh: float | None = None
    #: The multiplier applied to the arm's own uplift over the flat rule. 1.0 is the arm as it
    #: stands; 0.0 is the flat rule exactly.
    ladder_multiplier: float = 1.0
    #: TRUE when the RUNG (not the search) had to be cut back to the lawful ceiling. Only a rung
    #: above 1.0 can trip this, and reading a slope without it would read a saturation the world
    #: never saw: the price stopped rising because the cap held it, not because the customer did.
    ladder_ceiling_clamped: bool = False
    #: TRUE when the rung's offered rate sits beyond `max_supported_rate_increase_pct()` — the
    #: frontier of what this company's churn model has evidence for. The rung is still PRICED and
    #: still scored, because the whole point of a ladder is to make the world answer at prices the
    #: company cannot honestly predict; but the believed side of that rung is an extrapolation and
    #: any slope read across it must say how many decisions were in this state.
    ladder_above_support_bound: bool = False
    #: The rate this account is observed to be on today — the denominator of the company's own
    #: `rate_increase_pct`, and the reference its belief keys on. Carried out of the decision
    #: rather than re-derived by a reader, because the world keys on a LEVEL against the published
    #: SVT and the two references disagree in both directions (the 2026-08-27 section's Finding 4).
    current_rate_gbp_per_mwh: float | None = None
    #: The rate actually offered: `base_rate + margin`. The numerator of both references.
    offered_rate_gbp_per_mwh: float | None = None

    @property
    def rate_increase_pct(self) -> float | None:
        """THE COMPANY'S REFERENCE, as a percentage: a delta against this customer's OWN prior
        rate. This is the quantity `churn_model.estimate_churn_probability` keys on, and it is
        structurally incapable of containing the published SVT level the WORLD keys on. Published
        beside the world's `rate_vs_svt_pct` wherever a decision is reported, because Finding 4 of
        the 2026-08-27 section took an inversion in a four-row bucket table to detect and would
        have been one column."""
        if not self.current_rate_gbp_per_mwh or self.offered_rate_gbp_per_mwh is None:
            return None
        return 100.0 * (
            self.offered_rate_gbp_per_mwh - self.current_rate_gbp_per_mwh
        ) / self.current_rate_gbp_per_mwh

    @property
    def differs_from_flat(self) -> bool:
        return abs(self.margin_gbp_per_mwh - TARGET_MARGIN_GBP_PER_MWH) > 1e-9


@dataclass(frozen=True)
class ExpectedAnnualCosts:
    """What serving this customer for a year is expected to cost, term by term.

    ITEMISED RATHER THAN SUMMED, because the terms have completely different provenance and a
    single number hides which of them is a measurement and which is a guess. `unsourced` names
    the ones this company has no figure for, so a reader can see the hole instead of inferring
    a zero.
    """

    cost_to_serve_gbp: float
    bad_debt_gbp: float
    collections_gbp: float
    carrying_gbp: float
    #: Revenue this customer pays that is NOT the commodity margin -- the standing charge, and
    #: anything else billed per day rather than per MWh. See `expected_value_gbp` for why leaving
    #: it out changes the LEVEL of the answer and not the CHOICE.
    fixed_revenue_gbp: float = 0.0
    unsourced: tuple[str, ...] = ()

    @property
    def total_gbp(self) -> float:
        return self.cost_to_serve_gbp + self.bad_debt_gbp + self.collections_gbp + self.carrying_gbp


def expected_annual_costs(
    *,
    cost_to_serve_gbp_per_year: float,
    annual_revenue_gbp: float,
    credit_risk: str = DEFAULT_CREDIT_RISK,
    payment_delay_days: float | None = None,
    cost_of_capital_annual: float = DISCOUNT_RATE_ANNUAL,
    collections_gbp_per_year: float | None = None,
    fixed_revenue_gbp_per_year: float | None = None,
) -> ExpectedAnnualCosts:
    """Expected cost of serving one customer for a year, INCLUDING the cost of them not paying.

    Director, 2026-08-25: *"pricing follows expected cost -- and default risk, collections cost
    and bad debt are part of that cost. Put them inside the EV arithmetic and let the answer
    emerge rather than imposing a floor."*

    BAD DEBT IS TAKEN ON THE WHOLE BILL, NOT ON THE MARGIN, and that is the entire economics of
    a risky customer. A default on a 1,700 GBP annual bill costs the supplier the wholesale,
    network and policy cost it has already paid -- not the six pounds of margin it hoped to make.
    Charging the margin for the loss would make default look like a rounding error and would let
    the arm price a bad payer as though they were merely unprofitable.

    THE RATE IS THE COMPANY'S OWN AND IT IS NOT ABOVE SUSPICION. `saas.payment_behaviour.
    bad_debt_provision_gbp` applies a per-segment default probability (0.5% low to 8%
    vulnerable). Its own module says it is "not yet wired into saas/cost_to_serve.py", and
    `saas/cost_to_serve.py` records that Phase QD measured the FLAT bad-debt rate as overstating
    true bad debt by about 30x. That measurement was of the flat rate, not of this per-segment
    table, and the table has never been re-measured against the emergent arrears model. It is
    used as the company's belief and the caveat travels with it; it is NOT adjusted here, because
    tuning a belief so a pricing arm behaves is the inversion this project exists to avoid.

    CARRYING COST IS REAL MONEY AND IS USUALLY FORGOTTEN. A customer who pays 45 days after
    period-end against one who pays in 5 has borrowed the bill from the supplier for forty extra
    days. At the CLV model's own discount rate that is a genuine cost of the relationship, and it
    is one of the two places (with collections) where a slow payer differs from a defaulter.

    COLLECTIONS COST IS UNSOURCED IN THIS TREE. No per-contact or per-dunning-step cost exists
    anywhere under `company/` or `saas/` -- searched. Rather than invent one, the term is present
    in the arithmetic, defaults to zero, and is NAMED in `unsourced` so that a total which is
    missing it says so. A silent zero here would understate the cost of exactly the customers
    this decision is about.
    """
    revenue = max(0.0, float(annual_revenue_gbp))
    bad_debt = bad_debt_provision_gbp(credit_risk, revenue)

    unsourced: list[str] = []
    if collections_gbp_per_year is None:
        unsourced.append(
            "collections cost: no per-contact or per-dunning-step figure exists in this tree, so "
            "the cost of chasing a late payer is counted as zero and this total is a FLOOR"
        )
        collections = 0.0
    else:
        collections = float(collections_gbp_per_year)

    if payment_delay_days is None:
        unsourced.append("payment timing: no expected delay supplied, so no carrying cost is counted")
        carrying = 0.0
    else:
        carrying = revenue * (float(payment_delay_days) / 365.0) * float(cost_of_capital_annual)

    if fixed_revenue_gbp_per_year is None:
        unsourced.append(
            "fixed revenue: no standing-charge contribution supplied, so every figure derived "
            "from this is a MARGIN-ONLY contribution. A domestic electricity standing charge is "
            "0.27 GBP/day in this tree -- about 99 GBP a year -- so an EV computed without it "
            "understates by roughly that much and MUST NOT be read as saying a customer is "
            "value-negative"
        )

    return ExpectedAnnualCosts(
        cost_to_serve_gbp=float(cost_to_serve_gbp_per_year),
        bad_debt_gbp=bad_debt,
        collections_gbp=collections,
        carrying_gbp=carrying,
        fixed_revenue_gbp=float(fixed_revenue_gbp_per_year or 0.0),
        unsourced=tuple(unsourced),
    )


def expected_value_gbp(
    *,
    margin_gbp_per_mwh: float,
    eac_mwh: float,
    cost_to_serve_gbp_per_year: float,
    p_retain: float,
    expected_periods: float,
    discount_rate: float = DISCOUNT_RATE_ANNUAL,
    fixed_revenue_gbp_per_year: float = 0.0,
) -> float:
    """Expected discounted contribution from one customer at one candidate margin.

    FIXED REVENUE IS PART OF THE SUM AND LEAVING IT OUT NEARLY PUBLISHED A FALSE CLAIM. The
    first version compared the commodity margin against the WHOLE cost of serving, and every
    customer came out value-negative -- 2.00 GBP/MWh on 3.1 MWh is 6.20 GBP a year against 66 to
    98 GBP of cost. That reads as "this company loses money on every domestic customer", and it
    is an artefact: a domestic electricity standing charge is 0.27 GBP/day, about 99 GBP a year,
    which the customer really pays and the sum really omitted.

    AND IT DOES NOT CANCEL, WHICH IS THE INTERESTING PART. My first correction claimed the
    standing charge merely raised the level, because both arms bill it -- and the test refused
    that: with it the value-maximising margin FELL from 80.00 to 60.00 GBP/MWh. The reason is
    that fixed revenue is only earned from a customer who STAYS, so it sits inside the retention
    term. Making retention more valuable makes losing the customer more expensive, and the
    optimiser responds by charging LESS to keep them.

    So omitting it did two things, not one: it understated the level, and it made the arm
    OVER-PRICE. A supplier that forgets its standing charge charges more for its commodity than
    the economics support.

    COST TO SERVE IS SUBTRACTED INSIDE THE RETAINED BRANCH, not outside it, and the difference
    is the whole economics of a bad customer: a supplier does not pay to serve an account that
    left. Outside, a loss-making customer would look equally bad at every margin and the model
    would price them as though nothing could be done; inside, raising the margin until they
    leave is a legitimate outcome and the arithmetic can say so.

    Discounting is the CLV model's own (`DISCOUNT_RATE_ANNUAL`, `_annuity_factor`), because a
    second opinion about the time value of a customer would be a second CLV — and this repo has
    already paid for having three of a thing that should be one.
    """
    annual_contribution = (
        margin_gbp_per_mwh * eac_mwh + fixed_revenue_gbp_per_year - cost_to_serve_gbp_per_year
    )
    return p_retain * annual_contribution * _annuity_factor(expected_periods, discount_rate)


def _refine(
    score,
    lo: float,
    hi: float,
    resolution: float = MARGIN_RESOLUTION_GBP_PER_MWH,
) -> tuple[float, dict[float, tuple[float, float, "ExpectedAnnualCosts"]]]:
    """Find the best margin INSIDE `[lo, hi]` to `resolution`, and return everything it scored.

    THE COARSE GRID FINDS THE SHAPE; THIS FINDS THE NUMBER. The grid is what establishes that
    this customer's expected value turns over at all and roughly where — that is a global claim
    and it needs points spread across the whole feasible range. Where the peak actually sits is a
    local question, and answering it by adding rungs to the global grid would cost every customer
    the same evaluations whether or not their peak is anywhere near them.

    RE-BRACKETING, NOT GOLDEN SECTION, and the difference is an assumption I am not entitled to.
    Golden-section search converges faster and is only valid on a unimodal function; expected
    value here is `P(stay | m) x contribution(m)`, and `P(stay)` comes from a piecewise model with
    a saturation elbow in it, composed with a market multiplier in survival space. It is unimodal
    on every account measured and I have no proof it is unimodal on every account there could be.
    Sampling the whole bracket each pass and re-bracketing on the winner degrades gracefully if it
    is not: the worst case is a local peak, which is what a coarse grid would have returned
    anyway, rather than a confidently-converged wrong answer.

    TIES GO TO THE LOWER MARGIN, at this resolution as at the grid's — see the call site.
    """
    scanned: dict[float, tuple[float, float, ExpectedAnnualCosts]] = {}

    def at(margin: float) -> tuple[float, float, ExpectedAnnualCosts]:
        key = round(margin, 6)
        if key not in scanned:
            scanned[key] = score(key)
        return scanned[key]

    lo, hi = min(lo, hi), max(lo, hi)
    floor, ceiling = lo, hi
    best = lo
    passes = 0
    while hi - lo > resolution and passes < _REFINEMENT_MAX_PASSES:
        step = (hi - lo) / _REFINEMENT_SAMPLES
        points = [lo + i * step for i in range(_REFINEMENT_SAMPLES + 1)]
        best = max(points, key=lambda m: (round(at(m)[1], 6), -m))
        lo, hi = max(lo, best - step), min(hi, best + step)
        passes += 1
    if hi - lo <= resolution:
        best = max((lo, hi), key=lambda m: (round(at(m)[1], 6), -m))

    # SNAPPED TO THE LATTICE, because a renewal margin of 66.328125 GBP/MWh claims a precision the
    # decision does not have. Clamped to the ORIGINAL bracket and not the converged one -- the
    # first draft clamped to the converged bracket, whose ends are wherever the search stopped,
    # and handed back 66.328125 unchanged: a snap that can be undone by its own guard is not a
    # snap. What the guard is actually for is the outer bound, so that is what it holds to.
    snapped = round(round(best / resolution) * resolution, 6)
    snapped = min(max(snapped, round(floor, 6)), round(ceiling, 6))
    at(snapped)
    return snapped, scanned


def decide_margin(
    *,
    customer_id: str,
    arm: str,
    current_rate_gbp_per_mwh: float,
    base_rate_gbp_per_mwh: float,
    eac_kwh: float,
    tenure_years: float,
    cost_to_serve_gbp_per_year: float,
    expected_periods: float | None = None,
    segment: str = "resi",
    fuel: str = "electricity",
    bill_shock_count: int = 0,
    behaviour_score: BehaviourScore | None = None,
    satisfaction_score: float | None = None,
    renewal_year: int | None = None,
    candidates: tuple[float, ...] = CANDIDATE_MARGINS_GBP_PER_MWH,
    max_offered_rate_gbp_per_mwh: float | None = None,
    annual_revenue_gbp: float | None = None,
    credit_risk: str = DEFAULT_CREDIT_RISK,
    payment_delay_days: float | None = None,
    collections_gbp_per_year: float | None = None,
    fixed_revenue_gbp_per_year: float | None = None,
    is_deemed_contract: bool = False,
    book_general_margin_gbp_per_mwh: float | None = None,
    ladder_multiplier: float = 1.0,
    flat_level_gbp_per_mwh: float | None = None,
) -> MarginDecision:
    """The offered margin for ONE customer, under ONE arm.

    `base_rate_gbp_per_mwh` is the rate BEFORE margin — wholesale + capital + policy + network,
    exactly what `renewal_desk.strike_fixed_unit_rate` already computes. This module adds the
    margin and nothing else; the rate chain is untouched and stays the single place a rate is
    built.

    EVERY ARGUMENT IS A COMPANY OBSERVABLE. There is deliberately no parameter through which a
    caller could hand in the world's churn probability, the world's population draw, or anything
    else the supplier could not look up in its own records — the same shape `growth_desk`'s
    docstring holds for the acquisition gate.
    """
    if arm not in ARMS:
        raise MarginDecisionUnavailable(f"{arm!r} is not an arm; expected one of {ARMS}")
    if eac_kwh is None or float(eac_kwh) <= 0.0:
        raise MarginDecisionUnavailable(
            f"{customer_id} has no annual consumption on record, so there is no volume to earn a "
            "margin on and no decision to make -- not a flat-rule default"
        )
    eac_mwh = float(eac_kwh) / 1000.0
    periods = FALLBACK_LIFETIME_PERIODS if not expected_periods else float(expected_periods)

    # THE BILL MOVES WITH THE OFFER, AND SO DOES THE COST OF NOT BEING PAID. Until 2026-08-25
    # expected cost was computed ONCE, off the bill this customer is on today, and held fixed
    # across every candidate -- so the arm scored a 50% price rise as carrying exactly the default
    # risk of the old price. Bad debt is a fraction of the bill and carrying cost is the bill
    # borrowed for the payment delay; both are bigger on a bigger bill. Holding them still makes
    # every extra pound of margin look like a clean pound, which is a subsidy from the arithmetic
    # to the maximiser, and it is largest exactly where the arm wants to be.
    #
    # The LEVEL comes from the company's own billed record and the CHANGE from its own arithmetic:
    # `observed bill + (candidate margin - the margin they are on) x volume`. At the current offer
    # it reproduces the billed figure exactly, so nothing about today's number is re-derived.
    #
    # Measured, it moves the chosen margin by -0.17 GBP/MWh on the mean account of the real book,
    # and it is here because it is right rather than because it is large: the default rates in
    # `saas.payment_behaviour` run 0.5% to 8%, so this is a small correction to a big number, and
    # a bigger one for exactly the customers the decision is about.
    current_margin = float(current_rate_gbp_per_mwh) - float(base_rate_gbp_per_mwh)
    observed_revenue = (current_rate_gbp_per_mwh * eac_mwh
                        if annual_revenue_gbp is None else float(annual_revenue_gbp))

    def _score(margin: float) -> tuple[float, float, ExpectedAnnualCosts]:
        costs = expected_annual_costs(
            cost_to_serve_gbp_per_year=cost_to_serve_gbp_per_year,
            annual_revenue_gbp=observed_revenue + (margin - current_margin) * eac_mwh,
            credit_risk=credit_risk,
            payment_delay_days=payment_delay_days,
            collections_gbp_per_year=collections_gbp_per_year,
            fixed_revenue_gbp_per_year=fixed_revenue_gbp_per_year,
        )
        offered = base_rate_gbp_per_mwh + margin
        p_leave = enriched_churn_estimate(
            current_rate_gbp_per_mwh, offered, tenure_years, float(eac_kwh),
            bill_shock_count=bill_shock_count,
            behaviour_score=behaviour_score,
            satisfaction_score=satisfaction_score,
            fuel=fuel,
            segment=segment,
            renewal_year=renewal_year,
        )
        p_stay = max(0.0, 1.0 - float(p_leave))
        return p_stay, expected_value_gbp(
            margin_gbp_per_mwh=margin, eac_mwh=eac_mwh,
            cost_to_serve_gbp_per_year=costs.total_gbp,
            p_retain=p_stay, expected_periods=periods,
            fixed_revenue_gbp_per_year=costs.fixed_revenue_gbp,
        ), costs

    if arm == FLAT_RULES:
        # THE CONTROL DOES NOT SEARCH. It prices the constant and then reports what that choice
        # was worth, so the two arms are scored by the same function and any difference between
        # them is the DECISION and never the scorer.
        p_stay, value, costs = _score(TARGET_MARGIN_GBP_PER_MWH)
        return MarginDecision(
            customer_id=customer_id, arm=FLAT_RULES,
            margin_gbp_per_mwh=TARGET_MARGIN_GBP_PER_MWH,
            expected_value_gbp=value, p_retain=p_stay, expected_periods=periods,
            cost_to_serve_gbp_per_year=costs.total_gbp, eac_mwh=eac_mwh, costs=costs,
            considered=((TARGET_MARGIN_GBP_PER_MWH, value),),
            current_rate_gbp_per_mwh=float(current_rate_gbp_per_mwh),
            offered_rate_gbp_per_mwh=(
                float(base_rate_gbp_per_mwh) + TARGET_MARGIN_GBP_PER_MWH),
        )

    if arm == FLAT_AT_LEVEL:
        # THE LEVEL WITHOUT THE SELECTION. One margin for every renewal this arm prices, scored
        # by the same `_score` as the other two so any difference is the DECISION and never the
        # scorer.
        if flat_level_gbp_per_mwh is None:
            raise MarginDecisionUnavailable(
                f"{customer_id}: the flat-at-level arm was selected with no level set. A level of "
                "zero would silently reproduce the flat rule and be reported as a level "
                "comparison, so this refuses rather than defaults."
            )
        level = float(flat_level_gbp_per_mwh)
        # CLAMPED, UNLIKE `FLAT_RULES`, AND THAT IS THE POINT. This arm exists to be compared
        # against the value arm, which searches only lawful candidates -- so an unclamped level
        # would let it price where the value arm may not and reproduce exactly the confound that
        # made the 2026-08-27 whole-book attempt return a 9.4x artefact.
        #
        # AND THE CLAMP MUST SAY SO. The first full-decade run reported `distinct_margins: 4` for
        # an arm that applies ONE level, alongside `endpoint_at_ceiling: 0` -- and both were true
        # of the same run. `arm_decision_shape` reads `endpoint_side`, which the value arm's
        # SEARCH sets and this branch did not, so the clamp fired silently and the shape reported
        # a purely flat, unclamped arm. That is R15's FAIL-SILENT pattern exactly: a field that
        # reads zero because nobody writes it, not because the thing did not happen. Clamping is
        # the only mechanism that can vary a single constant, so those four values WERE the cap
        # binding, and the report denied it.
        #
        # `"ceiling"` is the exact word for this and not a borrowed one -- see the field's own
        # docstring: it "means the arm wanted to charge more than it was allowed to", which is
        # what `min(level, headroom)` does when it bites.
        clamped = False
        if max_offered_rate_gbp_per_mwh is not None:
            headroom = float(max_offered_rate_gbp_per_mwh) - float(base_rate_gbp_per_mwh)
            if headroom < level:
                level = headroom
                clamped = True
        p_stay, value, costs = _score(level)
        return MarginDecision(
            customer_id=customer_id, arm=FLAT_AT_LEVEL,
            margin_gbp_per_mwh=level,
            endpoint_bound=clamped,
            endpoint_side="ceiling" if clamped else None,
            expected_value_gbp=value, p_retain=p_stay, expected_periods=periods,
            cost_to_serve_gbp_per_year=costs.total_gbp, eac_mwh=eac_mwh, costs=costs,
            considered=((level, value),),
            current_rate_gbp_per_mwh=float(current_rate_gbp_per_mwh),
            offered_rate_gbp_per_mwh=float(base_rate_gbp_per_mwh) + level,
        )

    if not candidates:
        raise MarginDecisionUnavailable(
            f"{customer_id}: the value arm was given no candidate margins, so its 'choice' would "
            "be an empty search reported as a decision"
        )
    # THE CEILING IS APPLIED BEFORE THE SEARCH, not after it. Scoring a candidate the company
    # may not lawfully offer and then clamping the winner would report an expected value nobody
    # can earn, and would make the arm look better than the supplier it describes.
    lawful = tuple(
        m for m in candidates
        if max_offered_rate_gbp_per_mwh is None
        or base_rate_gbp_per_mwh + m <= max_offered_rate_gbp_per_mwh + 1e-9
    )

    # AND THE MODEL'S OWN EVIDENCE BOUNDS IT TOO. See `max_supported_rate_increase_pct`: the
    # churn cap at 0.95 leaves a floor of customers who never leave, so an unbounded maximiser
    # prices to infinity, and on the real book it very nearly did.
    support_pct = max_supported_rate_increase_pct()
    ceiling_from_support = current_rate_gbp_per_mwh * (1.0 + support_pct / 100.0)
    allowed = tuple(m for m in lawful if base_rate_gbp_per_mwh + m <= ceiling_from_support + 1e-9)
    if not allowed:
        raise MarginDecisionUnavailable(
            f"{customer_id}: no candidate margin survives both the ceiling "
            f"({max_offered_rate_gbp_per_mwh} GBP/MWh) and the model's support bound "
            f"({ceiling_from_support:.1f} GBP/MWh, {support_pct:.1f}% above the current rate) at "
            f"a base rate of {base_rate_gbp_per_mwh}. That is a real answer -- there is no offer "
            "here this company can both lawfully make and honestly predict -- and not a default."
        )
    scored = {margin: _score(margin) for margin in allowed}
    # TIES GO TO THE LOWER MARGIN, and it is not a rounding convention. On a flat stretch of the
    # switching curve several margins score identically; taking the highest would make the arm
    # prefer charging more for no expected gain, which is the shape a reader would rightly call
    # an excuse rather than a decision.
    def _rank(margin: float) -> tuple[float, float]:
        return (-round(scored[margin][1], 6), margin)

    bracket_at = min(allowed, key=_rank)
    # BRACKET WITH THE NEIGHBOURS, then find the peak between them. The grid says which stretch of
    # the curve this customer's optimum is on; `_refine` says where on it. When the grid's winner
    # is at an end there is only one neighbour, so the bracket is one-sided and the refinement can
    # confirm the end rather than invent an interior point that is not there.
    _at = allowed.index(bracket_at)
    lo = allowed[max(0, _at - 1)]
    hi = allowed[min(len(allowed) - 1, _at + 1)]
    refined_best, refined = _refine(_score, lo, hi)
    scored.update(refined)
    # The refinement may never be WORSE than the grid point that bracketed it. It cannot be, on a
    # bracket it sampled -- but the snap to the 0.25 lattice is a move the search did not choose,
    # so the comparison is made rather than assumed.
    best_margin = min((bracket_at, refined_best), key=_rank)
    best_p, best_value, best_costs = scored[best_margin]

    # DID THE BOUND ACTUALLY DECIDE? Answered by asking what the arm would have chosen with the
    # bound lifted, because there is no other way to answer it: a candidate can be removed from
    # the grid without being anywhere near the peak, and on the real book that is the usual case.
    # The shadow score is a DIAGNOSTIC and never an offer -- it is not added to `considered`, no
    # caller can act on it, and an unlawful candidate is still never scored as a price this
    # company would make.
    unbounded_best = min(candidates, key=lambda m: (-round(_score(m)[1], 6), m))
    ceiling_bound = (max_offered_rate_gbp_per_mwh is not None
                     and base_rate_gbp_per_mwh + unbounded_best > max_offered_rate_gbp_per_mwh + 1e-9)
    extrapolation_bound = base_rate_gbp_per_mwh + unbounded_best > ceiling_from_support + 1e-9

    # THE FLOOR IS GONE, AND READING THE LICENCE IS WHY.
    #
    # Until 2026-08-25 this arm refused to price a household in payment difficulty above the flat
    # rule, on the reasoning that charging a struggling customer more is the harm side of
    # `A7_harm_cost_weights_ratio`. The director asked me to check that against the rules rather
    # than assume it, and the rules do not say it:
    #
    #   SLC 27.8 requires the supplier to ascertain ability to pay and use it "when CALCULATING
    #   INSTALMENTS". It is a debt-repayment duty. It does not govern the unit rate.
    #
    # What the licence does constrain is recorded in `docs/domain_artefact_library/regulatory/
    # pricing_differentiation_permissions.md` with the text quoted, and read by
    # `company/regulatory/pricing_permissions.py`. Two of those bite here:
    #
    #   SLC 7.3/7.4 -- a DEEMED-contract class margin significantly above the book's general
    #   margin is unduly onerous. Comparative, so it does not forbid a wide margin, only a
    #   singled-out one, and it reaches a negotiated contract not at all.
    #   SLC 27.8A(a)(ii) -- incentives must attach to "successful customer outcomes not the value
    #   of repayment rates". That is why this module offers nothing that sets a repayment amount.
    #
    # AND THE ARITHMETIC NOW CARRIES WHAT THE FLOOR WAS STANDING IN FOR. A risky customer's
    # expected cost includes their expected default: on a 1,700 GBP bill the spread from low to
    # vulnerable is 66 to 212 GBP a year, about 47 GBP/MWh at domestic volumes. The flat 2.00 was
    # never neutral -- it was a large cross-subsidy from reliable payers to unreliable ones,
    # invisible because nobody had put the cost in the sum.
    verdict = check_class_margin(
        class_margin_gbp_per_mwh=best_margin,
        book_general_margin_gbp_per_mwh=book_general_margin_gbp_per_mwh,
        is_deemed_contract=is_deemed_contract,
    )
    withheld = None
    if not verdict.permitted:
        withheld = "{}: {}".format(verdict.condition, verdict.reason)
        best_margin = min(best_margin, TARGET_MARGIN_GBP_PER_MWH)
        best_p, best_value, best_costs = _score(best_margin)

    at_floor = withheld is None and best_margin <= allowed[0] + 1e-9
    at_ceiling = withheld is None and best_margin >= allowed[-1] - 1e-9

    # ── THE LADDER RUNG ────────────────────────────────────────────────────────────────────────
    #
    # THE RUNG IS SCORED AT THE PRICE IT DELIVERS, and that is the entire reason this sits inside
    # `decide_margin` rather than in the chain that calls it. Scaling the uplift after the decision
    # would leave `p_retain` describing a rate the customer is never offered -- which is precisely
    # the defect the 2026-08-26 ceiling repair closed ("the two sides of that comparison were
    # different prices"), and a price ladder whose believed leg is measured at a different price
    # from its realised leg measures nothing at all.
    #
    # THE PARAMETERISATION IS THE UPLIFT OVER THE FLAT RULE, not the margin. `flat + k x (chosen -
    # flat)` makes k=0 the flat rule EXACTLY, so rung zero is a null control the harness can check
    # against the flat-rules arm rather than a nearby price it has to argue about.
    unscaled_margin = best_margin
    ladder_clamped = False
    above_support = False
    if abs(ladder_multiplier - 1.0) > 1e-12:
        rung = TARGET_MARGIN_GBP_PER_MWH + ladder_multiplier * (
            best_margin - TARGET_MARGIN_GBP_PER_MWH)
        # THE LAWFUL CEILING STILL BINDS. It is a wall and not a dial: a rung above the cap is a
        # price this supplier may not charge, chain writer 4 would claw it back downstream, and the
        # belief would once again be at a rate nobody was offered. Clamped HERE so the scored
        # price and the delivered price stay the same number, and flagged so a reader can see a
        # flat top of the ladder for what it is.
        if max_offered_rate_gbp_per_mwh is not None:
            lawful_rung = float(max_offered_rate_gbp_per_mwh) - float(base_rate_gbp_per_mwh)
            if rung > lawful_rung + 1e-9:
                rung, ladder_clamped = lawful_rung, True
        # THE SUPPORT BOUND DOES NOT CLAMP THE RUNG, and the asymmetry is deliberate. That bound
        # is the frontier of the company's own EVIDENCE, not of the law -- it exists to stop the
        # arm CHOOSING a price it cannot predict. A ladder does not choose: it asks the world to
        # answer at a price the experimenter set, which is the only way to find out whether the
        # company's extrapolation beyond its own frontier is any good. So the rung is priced and
        # the state is reported, per decision and counted per rung.
        above_support = base_rate_gbp_per_mwh + rung > ceiling_from_support + 1e-9
        best_margin = rung
        best_p, best_value, best_costs = _score(best_margin)

    return MarginDecision(
        customer_id=customer_id, arm=VALUE_BASED, margin_gbp_per_mwh=best_margin,
        expected_value_gbp=best_value, p_retain=best_p, expected_periods=periods,
        cost_to_serve_gbp_per_year=best_costs.total_gbp, eac_mwh=eac_mwh, costs=best_costs,
        considered=tuple(sorted((m, v) for m, (_p, v, _c) in scored.items())),
        endpoint_bound=at_floor or at_ceiling,
        endpoint_side=("ceiling" if at_ceiling else "floor" if at_floor else None),
        candidates_removed=len(candidates) - len(allowed),
        ceiling_bound=ceiling_bound,
        extrapolation_bound=extrapolation_bound,
        withheld_reason=withheld,
        unscaled_margin_gbp_per_mwh=unscaled_margin,
        ladder_multiplier=float(ladder_multiplier),
        ladder_ceiling_clamped=ladder_clamped,
        ladder_above_support_bound=above_support,
        current_rate_gbp_per_mwh=float(current_rate_gbp_per_mwh),
        offered_rate_gbp_per_mwh=float(base_rate_gbp_per_mwh) + best_margin,
    )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE CHAIN ADAPTER — what a renewal desk can actually call
# ═══════════════════════════════════════════════════════════════════════════════════════════
#
# `decide_margin` above takes twenty keyword arguments and every one is a company observable,
# which is the property that makes it honest and also the reason it had no caller but a harness
# tool: `company/pricing/renewal_rate_chain.decide_renewal_rate` -- the ONE door through which
# every rate-moving supplier decision fires -- holds an account id, a term start and the
# supplier's own settled book, and not one of tenure, EAC, cost-to-serve or the rate this
# customer is on today. `tools/couple_value_based_pricing.py` assembles those from a FINISHED
# run's output, which a renewal cannot do because the run has not finished.
#
# So this layer derives them, from the same two things `customer_profitability.
# renewal_unit_rate_uplift` already derives its answer from: the account id and the supplier's
# settled records, bounded to what had settled before the term was struck. The seam does not
# grow, and the derivation sits behind the wall where a real supplier's would be.
#
# THE ELIGIBILITY RULE IS IMPORTED, NOT RESTATED. `company/crm/customer_profitability.py`
# already owns the vocabulary for "a renewal a per-MWh writer may move" -- electricity, a fixed
# or pass-through product, a locked rate to adjust, not the acquisition term. A second copy here
# would let two writers in the SAME chain silently disagree about which renewals they apply to,
# which is the mirror error of duplication the AO2 amendment names.

from company.crm.customer_profitability import (  # noqa: E402
    MIN_TERM_INDEX_FOR_UPLIFT,
    UPLIFTABLE_COMMODITY,
    UPLIFTABLE_TARIFF_TYPES,
)
from saas.cost_to_serve import cost_to_serve_for_period  # noqa: E402
from saas.non_commodity import standing_charge_rate  # noqa: E402

#: The rolling window every derivation below reads. IT IS THE SAME WINDOW
#: `run_phase2b._company_eac_estimate` uses for the churn estimate's EAC -- half-open
#: `[term_start - 1y, term_start)` -- and that is load-bearing rather than tidy. This arm's
#: objective is `p_retain(m) x (m x eac_mwh + ...)`, and the `p_retain` it multiplies by is
#: estimated against an EAC from that window. Two different sizes for one customer inside one
#: product would make the arm's own objective internally inconsistent and nothing would say so.
OBSERVATION_WINDOW_YEARS = 1

# ── THE FUNNEL'S STAGE NAMES ──────────────────────────────────────────────────────────────────
# One machine-readable key per guard below, published beside the prose reason rather than instead
# of it. The prose says WHY to a human; the key is what a funnel can COUNT, and the two are set at
# the same statement so they cannot drift apart.
#
# WHY THIS EXISTS (2026-08-28). `decision_shape.priced` reported 25 decisions on a book of 210
# billing accounts and nothing in the artefact could say where the other renewals went -- the
# guards below return a 0.0 uplift and the chain logs NOTHING for a renewal the arm was not
# eligible for, so "the world never offered this renewal", "the arm was not allowed to price it"
# and "the arm priced it flat" were one indistinguishable absence. That is R15's fail-silent shape
# applied to a POPULATION rather than to a verdict.
STAGE_CONTROL_ARM = "control_arm_no_writer"
STAGE_NO_LOCKED_RATE = "no_locked_rate"
STAGE_ACQUISITION_TERM = "acquisition_term"
STAGE_NOT_THE_ARMS_COMMODITY = "not_the_arms_commodity"
STAGE_PRODUCT_NOT_UPLIFTABLE = "product_not_upliftable"
STAGE_NO_OBSERVED_HISTORY = "no_observed_history"
STAGE_DECLINED = "declined"
STAGE_PRICED = "priced"

#: Every terminal state of one renewal passing this adapter, in the order the guards fire. A
#: funnel that reports a stage outside this tuple, or omits one of them, is reporting a shape
#: this module does not have.
FUNNEL_STAGES: tuple[str, ...] = (
    STAGE_CONTROL_ARM,
    STAGE_NO_LOCKED_RATE,
    STAGE_ACQUISITION_TERM,
    STAGE_NOT_THE_ARMS_COMMODITY,
    STAGE_PRODUCT_NOT_UPLIFTABLE,
    STAGE_NO_OBSERVED_HISTORY,
    STAGE_DECLINED,
    STAGE_PRICED,
)


@dataclass(frozen=True)
class MarginArmUplift:
    """What the value arm moved this renewal by, and enough to refute it.

    `uplift_gbp_per_mwh` is a DELTA AGAINST THE FLAT RULE, never a margin: the rate handed to the
    chain already carries `TARGET_MARGIN_GBP_PER_MWH`, so adding the chosen margin outright would
    charge the flat rule twice. It is SIGNED, because the arm prices some accounts BELOW the flat
    rule -- measured, 5 of 263 -- and a writer that could only add would turn a per-customer
    decision back into a surcharge.
    """

    uplift_gbp_per_mwh: float
    #: The full decision, or `None` when the arm did not run.
    decision: MarginDecision | None = None
    #: TRUE when the arm RAN and found no offer it could both lawfully make and honestly
    #: predict. That is a DECISION and belongs in the log; not-eligible is not. A single
    #: `not_run_reason` string cannot be branched on without parsing prose, and a reader that
    #: has to parse prose to tell a decision from an omission will eventually get it wrong.
    declined: bool = False
    #: WHY it did not run. Carried rather than inferred from a 0.0, because an arm that ran and
    #: chose the flat margin and an arm that never ran are the same number and opposite facts --
    #: R15's fail-silent pattern, and the one this adapter is most exposed to.
    not_run_reason: str | None = None
    #: WHICH GUARD, as a countable key rather than a sentence. `not_run_reason` interpolates the
    #: offending value into its prose ("tariff type None has no locked margin to move"), so a
    #: funnel grouping on it would report one bucket per distinct tariff type and could never
    #: report a stage total. One of `FUNNEL_STAGES`, and set at the same statement as the prose.
    #: `None` only on the priced path, where `stage` reads it off `decision is not None`.
    not_run_stage: str | None = None



def segments_for(segment: str | None, is_domestic: bool) -> tuple[str, str]:
    """(churn_segment, cost_segment) for one account -- two vocabularies, mapped, not shared.

    TWO VOCABULARIES, MAPPED, NOT SHARED (2026-08-26, WORKER_FINDING_THE_VALUE_ARMS_WHOLE_
    LOSS_IS_ONE_INDUSTRIAL_ACCOUNT_PRICED_AS_A_HOUSEHOLD). This read
    `segment = "resi" if is_domestic else "SME"` and used the result for BOTH the churn model
    and the cost tables, on the stated reasoning that `cost_to_serve_for_period` accepts
    exactly two segments so one vocabulary beats two that can disagree. That is right about
    costs and wrong about churn: `company/crm/churn_model.estimate_churn_probability` branches
    THREE ways, and its I&C arm exists precisely to switch bill-size-driven churn OFF
    (`IC_BILL_STRESS_SENSITIVITY = 0.0` -- "I&C: rate-driven churn, not bill-size-driven").
    Collapsing to two made that branch UNREACHABLE from the only production caller.

    Measured cost, on C_IC3 (3,936,105 kWh/yr): on the SME path the bill-stress term is
    `0.25 x max(0, annual_bill/3000 - 1)` against a bill in the hundreds of thousands, so
    P(leave) SATURATES AT 1.0000 for every candidate margin -- including margins BELOW what
    the company already charges. With `p_retain = 0` flat across the grid there is nothing to
    maximise and the search falls to the floor, GBP 0.50/MWh under the control's GBP 2.00. On
    3.94 GWh that giveaway compounded to -GBP 94,314 of realised margin, which was 99.5% of the
    value arm's entire measured loss. On the I&C path the same account reads 0.0288 at the
    floor and rises properly to 0.8094 at GBP 46. At DOMESTIC volume the resi path also gives
    0.0288 -- the curve is correct for households and saturates at industrial scale.

    `segment` is optional and falls back to the old mapping, so every existing caller keeps its
    behaviour and only a caller that KNOWS the segment changes anything. It is not a wall
    crossing: a supplier knows which of its own customers are industrial -- they are
    half-hourly settled on bespoke contracts -- exactly as it already knows `is_domestic`.
    """
    churn_segment = (
        segment if segment in CHURN_SEGMENTS
        else (RESI_SEGMENT if is_domestic else SME_SEGMENT))
    # The COST vocabulary, derived from the churn one rather than the other way round,
    # because the cost tables are the side with fewer categories and mapping down is
    # lossless where mapping up would have to invent.
    cost_segment = RESI_SEGMENT if churn_segment == RESI_SEGMENT else SME_SEGMENT
    return churn_segment, cost_segment


def renewal_margin_uplift(
    *,
    account_id: str,
    commodity: str,
    tariff_type: str | None,
    term_index: int,
    term_start: str,
    locked_unit_rate: float | None,
    settled_records: list[dict],
    is_domestic: bool,
    arm: str,
    max_offered_rate_gbp_per_mwh: float | None = None,
    segment: str | None = None,
    ladder_multiplier: float = 1.0,
    flat_level_gbp_per_mwh: float | None = None,
) -> MarginArmUplift:
    """The £/MWh this renewal moves by, under ONE arm, from the supplier's own settled book.

    Returns a ZERO uplift for `FLAT_RULES` before computing anything, so a run on the control arm
    is byte-identical to a run with this writer absent. That is what makes the A/B a comparison
    of one variable rather than of two code paths, and it is asserted rather than assumed by
    `test_the_control_arm_is_byte_identical_to_no_writer_at_all`.

    POINT-IN-TIME: every derivation filters `settlement_date < term_start` before reading
    anything, the same bound `estimate_prior_term_net_margin` applies one writer along.

    `is_domestic` rather than a segment string: the door already carries that boolean and
    `cost_to_serve_for_period` accepts exactly two segments, so mapping here keeps ONE vocabulary
    for one fact instead of two that can disagree.

    `max_offered_rate_gbp_per_mwh` IS THE CEILING THE SEARCH RUNS UNDER, and passing it is the
    2026-08-26 half of the same finding. `decide_margin` says in its own body that "THE CEILING IS
    APPLIED BEFORE THE SEARCH, not after it. Scoring a candidate the company may not lawfully offer
    and then clamping the winner would report an expected value nobody can earn, and would make the
    arm look better than the supplier it describes." This adapter passed no ceiling at all, so on
    the ONE path a live run uses, the cap arrived afterwards as chain writer 4 -- exactly the
    forbidden order, on 27 of the 66 renewals the first ten-year A/B priced.

    Two things followed and both are R15 shapes rather than approximations. `ceiling_bound` is
    computed as `max_offered_rate_gbp_per_mwh is not None and ...`, so on this path it was
    STRUCTURALLY False: the flag that exists to tell a reader the cap decided the price could not
    fire on the only caller where the cap ever decided one (fail-silent). And `believed_p_retain`
    /`believed_expected_value_gbp` -- the beliefs the A/B's belief-vs-truth column scores -- were
    the arm's beliefs at a rate the customer was never charged, while the world churned them at the
    capped one. The two sides of that comparison were different prices.

    `None` remains legitimate and means what it says: no ceiling binds this renewal. A non-domestic
    or non-capped product genuinely has none, and the caller that knows which is the chain.
    """
    if arm == FLAT_RULES:
        return MarginArmUplift(0.0, not_run_stage=STAGE_CONTROL_ARM)
    # `FLAT_AT_LEVEL` deliberately does NOT return here. It must pass through every guard below --
    # locked rate, term index, commodity, tariff type, observed state -- so it prices EXACTLY the
    # renewals the value arm prices. An arm that priced a different population would compare the
    # level against the selection AND against the book, which is the confound this arm exists to
    # remove.
    if arm not in ARMS:
        raise MarginDecisionUnavailable(f"{arm!r} is not an arm; expected one of {ARMS}")
    if locked_unit_rate is None:
        return MarginArmUplift(
            0.0, not_run_reason="no locked rate to move", not_run_stage=STAGE_NO_LOCKED_RATE)
    if term_index < MIN_TERM_INDEX_FOR_UPLIFT:
        return MarginArmUplift(
            0.0, not_run_reason="acquisition term: nothing observed yet",
            not_run_stage=STAGE_ACQUISITION_TERM)
    if commodity != UPLIFTABLE_COMMODITY:
        return MarginArmUplift(
            0.0, not_run_reason=f"commodity {commodity!r} is not priced by this arm",
            not_run_stage=STAGE_NOT_THE_ARMS_COMMODITY)
    if tariff_type not in UPLIFTABLE_TARIFF_TYPES:
        return MarginArmUplift(
            0.0, not_run_reason=f"tariff type {tariff_type!r} has no locked margin to move",
            not_run_stage=STAGE_PRODUCT_NOT_UPLIFTABLE)

    # Two vocabularies, mapped rather than shared -- see `segments_for`.
    churn_segment, cost_segment = segments_for(segment, is_domestic)
    observed = observed_account_state(account_id, term_start, settled_records, cost_segment)
    if observed is None:
        return MarginArmUplift(
            0.0, not_run_reason="nothing settled for this account inside the observation window",
            not_run_stage=STAGE_NO_OBSERVED_HISTORY)

    try:
        decision = decide_margin(
            customer_id=account_id,
            # THE ARM AS GIVEN, not a constant. This read `arm=VALUE_BASED` while the only other
            # arm returned above, so the hardcoding was invisible; a third arm makes it a defect
            # that would have silently priced `flat_at_level` renewals with the value arm.
            arm=arm,
            current_rate_gbp_per_mwh=observed["current_rate_gbp_per_mwh"],
            # The rate BEFORE margin. The strike already added the flat rule, so subtracting it
            # is what makes `base + chosen` the arm's own answer rather than the flat rule plus
            # it.
            base_rate_gbp_per_mwh=float(locked_unit_rate) - TARGET_MARGIN_GBP_PER_MWH,
            eac_kwh=observed["eac_kwh"],
            tenure_years=observed["tenure_years"],
            cost_to_serve_gbp_per_year=observed["cost_to_serve_gbp_per_year"],
            # THE CHURN vocabulary, not the cost one -- see the mapping above.
            segment=churn_segment,
            renewal_year=int(term_start[:4]),
            # EVERYTHING THIS ACCOUNT'S OWN RECORDS ALREADY SAID, and until 2026-08-26 none of it
            # was passed. `decide_margin` takes twenty company observables; this adapter handed it
            # six and let the rest default, so the arm the ten-year A/B scored was not the arm
            # `tools/couple_value_based_pricing.py` probes -- that tool passes the standing charge,
            # the billed revenue and the lifetime, and its 263-account probe came back 6/263
            # endpoint-bound where the chain's came back 36/66. Same module, same book, different
            # information. The defaults are not neutral: an absent standing charge makes the arm
            # OVER-PRICE (`expected_value_gbp`'s docstring measures it at 80.00 -> 60.00 GBP/MWh,
            # because fixed revenue is only earned from a customer who stays, so forgetting it
            # makes losing them look cheap).
            annual_revenue_gbp=observed["annual_revenue_gbp"],
            fixed_revenue_gbp_per_year=observed["fixed_revenue_gbp_per_year"],
            expected_periods=observed["expected_periods"],
            max_offered_rate_gbp_per_mwh=max_offered_rate_gbp_per_mwh,
            # THE RUNG, and it goes into the DECISION rather than onto its answer -- see the
            # ladder block in `decide_margin`. Default 1.0 leaves every existing caller alone.
            ladder_multiplier=ladder_multiplier,
            flat_level_gbp_per_mwh=flat_level_gbp_per_mwh,
        )
    except MarginDecisionUnavailable as exc:
        # "NO OFFER" IS AN ANSWER, AND A LIVE PRICING CHAIN MUST BE ABLE TO HEAR IT (2026-08-26).
        #
        # `decide_margin` raises when no candidate margin survives BOTH the price cap and the
        # churn model's support bound, and its own message insists that is "a real answer -- there
        # is no offer here this company can both lawfully make and honestly predict -- and not a
        # default." Correct as a REPORT. Fatal as a WRITER: the first ten-year A/B died at
        # `C_IC3`, 2021, base rate GBP 251.45, where +83.1% of the current rate leaves no lawful
        # margin at all -- the 2016-2018 window never reached a rate high enough to produce one,
        # which is exactly what a short window hides.
        #
        # So the arm DECLINES this renewal and the chain leaves the struck rate alone. That is
        # the same outcome as the flat rule, which is the honest fallback: a supplier that cannot
        # form a defensible view charges what it already charges. The distinction that must NOT
        # be lost is between "declined, here is why" and "agreed with the control", so the reason
        # is carried in full rather than collapsed to a 0.0 -- R15's fail-silent pattern, in the
        # one place on this path where the arm has the most to say.
        return MarginArmUplift(
            0.0, not_run_reason="no lawful, predictable offer: {}".format(exc), declined=True,
            not_run_stage=STAGE_DECLINED)
    return MarginArmUplift(
        uplift_gbp_per_mwh=decision.margin_gbp_per_mwh - TARGET_MARGIN_GBP_PER_MWH,
        decision=decision,
    )


def observed_account_state(
    account_id: str, term_start: str, settled_records: list[dict], segment: str,
) -> dict | None:
    """Tenure, EAC, the rate this account is actually on, and cost-to-serve — all observed.

    Returns `None` where the account has nothing settled inside the window before this term. That
    is a STATE and not an error: an account with no observed history is one this arm has no basis
    to price, and the caller adds 0.0 rather than the arm guessing at it.

    THE STANDING CHARGE IS SPLIT OUT OF THE RATE, AND UNTIL 2026-08-26 IT WAS NOT (this is the
    mechanism behind `WORKER_FINDING_VALUE_ARM_CHOOSES_A_BOUND_NOT_A_CUSTOMER`). A settled record's
    `revenue_gbp` INCLUDES the per-period standing charge -- `simulation/hedged_settlement.py`
    adds `sc_per_period` into it explicitly -- so `revenue / volume` is an ALL-IN GBP/MWh. The
    number it was being compared against is not: `base_rate_gbp_per_mwh + margin`, the offer
    handed to the churn model, is a commodity unit rate with no standing charge in it at all.

    The gap between those two is the standing charge expressed per MWh, and on a small domestic
    account it is enormous: GBP 0.27/day is about GBP 99 a year, which over 1,779 kWh is GBP
    55/MWh. So the arm was asking its churn model how a customer feels about moving from an all-in
    GBP 176/MWh to a commodity GBP 130/MWh, and the model correctly answered "that is a price
    CUT". Fifty-five pounds a megawatt-hour of phantom headroom, spent before the belief registered
    any rise at all -- and the support bound is `current_rate x 1.831`, so the inflated rate
    inflated the frontier by the same proportion on the way past.

    Netting it off makes the comparison like-for-like. `annual_revenue_gbp` still carries the WHOLE
    bill, because bad debt is taken on what the customer owes rather than on the commodity leg of
    it, and `fixed_revenue_gbp_per_year` carries the standing charge into the EV where
    `expected_value_gbp`'s own docstring says it belongs.

    Policy and network costs are deliberately NOT netted off: on a pass-through tariff the customer
    really is billed them per MWh, and the struck rate this is compared against carries them too
    (`renewal_desk.strike_fixed_unit_rate` builds wholesale + capital + policy + network). Only the
    standing charge is billed on a basis the offered rate has no term for.
    """
    from datetime import date as _date

    start = _date.fromisoformat(term_start)
    window_open = start.replace(year=start.year - OBSERVATION_WINDOW_YEARS).isoformat()

    prior = [
        r for r in settled_records
        if r.get("customer_id") == account_id
        and r.get("commodity", UPLIFTABLE_COMMODITY) == UPLIFTABLE_COMMODITY
        and r.get("settlement_date", "") < term_start
    ]
    if not prior:
        return None
    window = [r for r in prior if r.get("settlement_date", "") >= window_open]
    if not window:
        return None

    kwh = sum(float(r.get("consumption_kwh") or 0.0) for r in window)
    revenue = sum(float(r.get("revenue_gbp") or 0.0) for r in window)
    if kwh <= 0.0:
        return None

    fixed_revenue = _observed_standing_charge_gbp(window, segment)
    tenure_years = max(0.0, (start - _date.fromisoformat(
        min(r.get("settlement_date", term_start) for r in prior))).days / 365.25)

    return {
        "eac_kwh": kwh,
        # THE REALISED COMMODITY RATE, not a quoted one: what the supplier actually billed over
        # the window per MWh, with the standing charge taken back out so it is the same KIND of
        # number as the offer it will be compared against. A stored headline rate stops describing
        # the account the moment a discount, a cap clamp or a part-term moves it, and all three
        # happen here.
        "current_rate_gbp_per_mwh": max(0.0, revenue - fixed_revenue) / (kwh / 1000.0),
        # THE WHOLE BILL, because that is what a defaulting customer fails to pay.
        "annual_revenue_gbp": revenue,
        "fixed_revenue_gbp_per_year": fixed_revenue,
        "tenure_years": tenure_years,
        # HOW LONG THIS ACCOUNT IS EXPECTED TO LAST, from its own observed tenure. Until
        # 2026-08-26 this adapter passed nothing, so every renewal in a live run was priced at
        # `FALLBACK_LIFETIME_PERIODS` -- the deliberately pessimistic one-period value written for
        # an account that has given NO evidence -- including accounts with years of settled
        # history in the very records this function was handed. It is a uniform scalar on EV so it
        # never moved the CHOICE; it made every published `believed_expected_value_gbp` on the
        # chain path the value of one period of a relationship the company had already observed
        # for four years. Capped at the CLV model's own horizon, as `couple_value_based_pricing`
        # caps it, so a long-tenured account cannot buy an unbounded lifetime from its own past.
        "expected_periods": min(MAX_EXPECTED_PERIODS, max(1.0, tenure_years)),
        "cost_to_serve_gbp_per_year": sum(
            cost_to_serve_for_period(
                segment, float(r.get("revenue_gbp") or 0.0), UPLIFTABLE_COMMODITY,
                periods=int(r.get("settlement_periods_folded", 1) or 1))
            for r in window),
    }


#: The longest lifetime this arm will price on, in renewal periods. Not a belief of its own: it is
#: the horizon `tools/couple_value_based_pricing.py` already applies to the same decision, named
#: once here rather than restated at a second call site where the two could drift apart.
MAX_EXPECTED_PERIODS: float = 6.0


def _observed_standing_charge_gbp(window: list[dict], segment: str) -> float:
    """What this account was billed in STANDING CHARGE over the window, from its own records.

    THE RECORD IS AUTHORITATIVE AND THE TARIFF TABLE IS THE FALLBACK, which is the same order
    `saas/bill_generator.py` reads them in and the order `saas/non_commodity.standing_charge_rate`
    asks to be read in ("FALLBACK ONLY. The authoritative standing charge for a real bill is the
    year-calibrated value on each settlement record"). A settlement generator that stamps
    `standing_charge_gbp` on every period is describing what this customer actually paid; the flat
    per-day rate is what the company would charge an account it has no record for.

    THE FALLBACK COUNTS DAYS AND NOT RECORDS. There are 48 settlement periods in a day and the
    standing charge is per DAY, so summing a per-day rate over records would overstate it 48-fold.
    Distinct settlement dates is the observable that means "days this account was supplied".
    """
    stamped = sum(float(r.get("standing_charge_gbp") or 0.0) for r in window)
    if stamped > 0.0:
        return stamped
    days = len({r.get("settlement_date") for r in window if r.get("settlement_date")})
    return days * standing_charge_rate(UPLIFTABLE_COMMODITY, segment)
