"""Home move win-rate model — Phase 4b-4 (customer value layer).

`saas/churn_model.py` (4b-2) estimates the probability that an account
*doesn't* renew at each annual renewal point — i.e. the occupant moves out
("churns"). That event isn't the end of the story for the property: a new
occupant moves in, and the property's supply contract either stays with us
(a "win") or goes to a competitor (a "loss"). This module estimates that
win probability, and combines it with `churn_model`'s churn probability to
produce an *effective retention probability* per renewal point — the
likelihood the property remains on supply with us, whether through a normal
renewal or through winning the post-move-in occupant.

Two factors drive the win probability, both seed estimates (see
"Open Questions" in `docs/observability/PHASE_4b_SUMMARY.md`):

  1. Segment baseline — UK "deemed contract" inertia means many residential
     movers simply continue with whatever supplier already serves the
     property, giving resi properties a relatively high baseline win rate.
     SME premises are more often re-tendered by a facilities agent at
     move-in, giving a lower baseline.
  2. Price competitiveness, scaled by EPC rating — Key Domain Insight
     (CLAUDE.md): customer reaction to bills is non-rational and driven by
     absolute £ impact, not %. A poorly-insulated (low EPC) property has
     higher absolute consumption, so the same percentage price gap versus
     the market translates into a larger £ difference — making new
     occupants of low-EPC properties more price-sensitive at the point of
     moving in, and more likely to shop around rather than accept the
     incumbent.

This module is pure: it takes the plain-dict output of
`churn_model.build_churn_risk()` plus the CUSTOMERS roster (for segment and
epc_rating) and returns a plain dict. No imports from `sim/`.
"""

# The one import this module has, and it is a saas sibling, not `sim/`: a DRAWN
# customer carries `consumption_band` instead of `epc_rating`, and the derivation
# from that observable belongs beside the other property derivations rather than
# duplicated here (two copies of a derivation drift, and the drifting copy is
# always the one nobody is looking at). `property_model` is a leaf module.
from saas.property_model import _epc_rating_of

# Baseline win probability when our price is exactly at the market average
# (price_differential_pct == 0), by segment.
BASE_WIN_PROBABILITY = {
    "resi": 0.55,
    "SME": 0.35,
}

# Percentage-point reduction in win probability per 1 percentage point that
# our price sits above the market average (price_differential_pct == 0.01),
# scaled by the property's EPC rating. A negative price_differential_pct
# (we're cheaper than market) increases the win probability by the same
# scaling.
PRICE_SENSITIVITY_BY_EPC = {
    "A": 0.5,
    "B": 0.5,
    "C": 1.0,
    "D": 1.5,
    "E": 2.0,
    "F": 2.5,
    "G": 3.0,
}

MIN_WIN_PROBABILITY = 0.05
MAX_WIN_PROBABILITY = 0.95


# ===========================================================================
# W2_12 — acquisition-VALUE physics (2026-07-29).
#
# Until now this module produced a win *probability* and stopped there. A
# probability with no value attached cannot answer the question the director
# actually asked of this atom — that a tenancy change is "simultaneously the
# prime acquisition moment for high-value low-churn customers". Winning a
# 0.6-probability occupant worth £90 and winning one worth £900 were the same
# number. `home_move_acquisition_value()` closes that: the win outcome now
# carries the CLV of the occupant landed, which is what `saas/enterprise_value.py`
# discounts into the book's value.
#
# The "low-churn" half is DERIVED, not asserted
# ---------------------------------------------
# An occupant who lands via a home move and accepts our deemed contract has,
# by revealed preference, declined to shop at the single most natural shopping
# moment there is. That places them in the default-tariff population, and Ofgem
# publishes how sticky that population is.
#
# Ofgem Retail Market Indicators, "default tariffs" panel, as of October 2025
# (domestic non-prepayment electricity): 45.1% of customers are on an actively-
# chosen tariff; 54.9% are on a default tariff, of which 34.6pp have held it
# under 3 years and 20.3pp for 3 years or more.
#
#   share of the default-tariff cohort holding 3+ years = 20.3 / 54.9 = 0.370
#   implied annual retention                            = 0.370 ** (1/3) = 0.718
#   implied annual churn hazard                         = 1 - 0.718      = 0.282
#
# That 0.282 is the landed occupant's churn hazard: lower than a whole-book
# hazard, which blends in the 45.1% actively-chosen cohort that shops by
# definition. Nothing here is a tuned coefficient — the two constants below are
# arithmetic on one published Ofgem table.
#
# ⚠ This is the COMPANY'S BELIEF, and it is allowed to be wrong. A real supplier
# reads Ofgem's published aggregates and reasons exactly this way; it cannot see
# the true engagement archetype of the household that just moved in. The
# belief-vs-truth gap against the world's own occupant behaviour is the coupled
# triad's score for this atom, not a defect to be tuned away.
#
# ⚠ Named gap: the inference "accepted a deemed contract at move-in ⇒ drawn from
# the default-tariff population" is a REASONABLE reading, not a published
# finding. Ofgem publishes the default-tariff stock split; it does not publish
# the tenure distribution of home-movers specifically. The conservative cap in
# `landed_occupant_churn_probability()` exists because of that gap.
# ===========================================================================

OFGEM_RMI_DEFAULT_TARIFF_SHARE = 0.549          # published, Oct-2025 panel
OFGEM_RMI_DEFAULT_HELD_3YR_PLUS_SHARE = 0.203   # published, Oct-2025 panel

# Arithmetic on the two published figures above — see the derivation comment.
DEFAULT_TARIFF_3YR_HOLD_RATE = (
    OFGEM_RMI_DEFAULT_HELD_3YR_PLUS_SHARE / OFGEM_RMI_DEFAULT_TARIFF_SHARE
)
DEFAULT_TARIFF_ANNUAL_CHURN_HAZARD = 1.0 - DEFAULT_TARIFF_3YR_HOLD_RATE ** (1.0 / 3.0)

# Matches saas/clv_model.py::DISCOUNT_RATE_ANNUAL — the same book, the same rate.
DISCOUNT_RATE_ANNUAL = 0.10


def landed_occupant_churn_probability(book_churn_probability: float) -> float:
    """Annual churn probability we should expect of an occupant we landed at a
    home move, given the book-wide `book_churn_probability`.

    Returns the published default-tariff hazard (~0.282), but never MORE than
    the book's own hazard. That cap is deliberate and conservative: the
    derivation supports "a deemed-landing occupant is stickier than the book",
    and it would be an over-claim to let this function make an already-sticky
    book look churnier just because the published aggregate happens to sit
    higher than it. Where the book is already stickier than the published
    default-tariff cohort, we claim no home-move bonus at all.

    Raises ValueError on a churn probability outside [0, 1].
    """
    if not 0.0 <= book_churn_probability <= 1.0:
        raise ValueError(
            "book_churn_probability must be in [0, 1], got " + repr(book_churn_probability)
        )
    return min(book_churn_probability, DEFAULT_TARIFF_ANNUAL_CHURN_HAZARD)


def occupant_clv_gbp(
    annual_net_margin_gbp: float,
    churn_probability: float,
    discount_rate: float = DISCOUNT_RATE_ANNUAL,
) -> float:
    """Discounted lifetime value of an occupant under geometric retention.

    Margin `annual_net_margin_gbp` is received at the end of each year the
    occupant is still with us; they survive each year with probability
    `r = 1 - churn_probability`. Summing the geometric series gives the closed
    form used here:

        CLV = Σ(k≥1) m·r^(k-1)/(1+d)^k = m / (1 + d - r)

    Same economics as `clv_model.build_clv()`'s annuity — that path projects an
    expected lifetime through the shifted-beta-geometric model first, which is
    right for an existing account with renewal history. A just-landed occupant
    has no history to fit, so the closed form is used directly rather than
    fabricating renewal points for them.

    A churn probability of 0 with a zero discount rate would be an infinite
    lifetime; that combination raises ValueError rather than returning inf.
    """
    if not 0.0 <= churn_probability <= 1.0:
        raise ValueError("churn_probability must be in [0, 1], got " + repr(churn_probability))
    denominator = 1.0 + discount_rate - (1.0 - churn_probability)
    if denominator <= 0.0:
        raise ValueError(
            "undiscounted immortal customer: churn_probability="
            + repr(churn_probability) + ", discount_rate=" + repr(discount_rate)
        )
    return annual_net_margin_gbp / denominator


def home_move_acquisition_value(
    win_probability: float,
    annual_net_margin_gbp: float,
    book_churn_probability: float,
    discount_rate: float = DISCOUNT_RATE_ANNUAL,
) -> dict:
    """The value — not just the odds — of the acquisition moment at a home move.

    Returns:
      landed_occupant_churn_probability — what we expect of a deemed-landing
          occupant (published default-tariff hazard, capped at the book's).
      occupant_clv_gbp — that occupant's discounted lifetime value if won.
      expected_acquisition_value_gbp — `win_probability × occupant_clv_gbp`,
          the value of standing at this moment before knowing the outcome.
      value_at_risk_gbp — `(1 - win_probability) × occupant_clv_gbp`, the value
          that walks to a competitor if we lose. The pair is what makes a home
          move worth spending retention money on; the win probability alone
          never could.
      low_churn_uplift_gbp — how much of the CLV exists ONLY because the landed
          occupant is stickier than the book. This is the director's
          "high-value low-churn" claim, isolated and measurable rather than
          asserted; it is zero when the book is already stickier.

    Raises ValueError on a win probability outside [0, 1].
    """
    if not 0.0 <= win_probability <= 1.0:
        raise ValueError("win_probability must be in [0, 1], got " + repr(win_probability))

    landed_churn = landed_occupant_churn_probability(book_churn_probability)
    clv = occupant_clv_gbp(annual_net_margin_gbp, landed_churn, discount_rate)
    book_clv = occupant_clv_gbp(annual_net_margin_gbp, book_churn_probability, discount_rate)

    return {
        "win_probability": win_probability,
        "landed_occupant_churn_probability": landed_churn,
        "occupant_clv_gbp": clv,
        "expected_acquisition_value_gbp": win_probability * clv,
        "value_at_risk_gbp": (1.0 - win_probability) * clv,
        "low_churn_uplift_gbp": clv - book_clv,
    }


def build_home_move_acquisition_values(
    home_move_win_rates: dict,
    annual_net_margin_by_account: dict,
    discount_rate: float = DISCOUNT_RATE_ANNUAL,
) -> dict:
    """Attach acquisition VALUE to every renewal point in
    `build_home_move_win_rates()`'s output.

    `annual_net_margin_by_account` maps billing-account id to that account's
    average annual net margin (the same figure `clv_model.build_clv()` derives
    from `cost_to_serve`). Accounts absent from it are skipped rather than
    valued at zero — a missing margin is unknown, not nil, and silently
    booking it as nil would understate the book (an R15 fail-open shape).

    Returns `{account_id: [{renewal_period, ...acquisition value fields}]}` plus
    nothing else; the portfolio roll-up is the caller's (see
    `saas/enterprise_value.py`).
    """
    values: dict[str, list[dict]] = {}
    for account_id, renewals in home_move_win_rates.items():
        if account_id not in annual_net_margin_by_account:
            continue
        margin = annual_net_margin_by_account[account_id]
        values[account_id] = [
            {
                "renewal_period": renewal["renewal_period"],
                **home_move_acquisition_value(
                    renewal["win_probability"],
                    margin,
                    renewal["churn_probability"],
                    discount_rate,
                ),
            }
            for renewal in renewals
        ]
    return values


def home_move_win_probability(segment: str, epc_rating: str, price_differential_pct: float) -> float:
    """Return the probability that we win/retain a property's supply
    contract when its occupant moves out and a new occupant moves in.

    segment: "resi" or "SME" — looked up in BASE_WIN_PROBABILITY, defaulting
        to the "resi" baseline for any other value.
    epc_rating: "A" through "G" — looked up in PRICE_SENSITIVITY_BY_EPC,
        defaulting to a sensitivity of 1.0 for any other value.
    price_differential_pct: our price relative to the market average, as a
        fraction (e.g. 0.05 == we are 5% above market average; -0.05 == 5%
        below). Positive values reduce the win probability, negative values
        increase it.

    Result is clamped to [MIN_WIN_PROBABILITY, MAX_WIN_PROBABILITY].
    """
    base = BASE_WIN_PROBABILITY.get(segment, BASE_WIN_PROBABILITY["resi"])
    sensitivity = PRICE_SENSITIVITY_BY_EPC.get(epc_rating, 1.0)
    win_probability = base - price_differential_pct * sensitivity
    return max(MIN_WIN_PROBABILITY, min(MAX_WIN_PROBABILITY, win_probability))


def build_home_move_win_rates(churn_risk: dict, customers: list[dict], price_differential_pct: float) -> dict:
    """For every renewal point in `churn_risk` (see
    `churn_model.build_churn_risk()`), add the home-move win probability and
    an effective retention probability.

    Returns a dict keyed by billing-account id (same keys as `churn_risk`),
    each value a list of:
      {renewal_period, churn_probability, win_probability, effective_retention_probability}

    `win_probability` is constant across an account's renewal points (it
    depends only on that property's segment and EPC rating, plus the
    portfolio-wide `price_differential_pct`), but is repeated per renewal
    point for convenience.

    `effective_retention_probability` is the probability the property
    remains on supply with us at this renewal point, whether through a
    normal renewal (probability `1 - churn_probability`) or by winning the
    post-move-in occupant after a churn (probability
    `churn_probability * win_probability`):

      effective_retention_probability
          = (1 - churn_probability) + churn_probability * win_probability

    Accounts with no renewal points (`churn_risk[account] == []`) map to an
    empty list.

    Raises KeyError if a billing account in `churn_risk` has no matching
    entry in `customers` (looked up by `customer_id`).
    """
    profile_by_account = {c["customer_id"]: c for c in customers}

    win_rates: dict[str, list[dict]] = {}
    for account_id, renewals in churn_risk.items():
        profile = profile_by_account[account_id]
        # A DRAWN (SYN-*) customer carries `consumption_band`, not the static
        # roster's `epc_rating` (generator_draw_wiring activation, 2026-08-13).
        # Read it through the shared accessor rather than off the dict, so this
        # site and `property_model.build_properties()` cannot disagree about the
        # same customer's EPC. Unguarded, this was the KeyError that killed the
        # whole 10-year run the moment the population draw was activated.
        win_probability = home_move_win_probability(
            profile["segment"], _epc_rating_of(profile), price_differential_pct
        )

        account_win_rates = []
        for renewal in renewals:
            churn_probability = renewal["churn_probability"]
            account_win_rates.append({
                "renewal_period": renewal["renewal_period"],
                "churn_probability": churn_probability,
                "win_probability": win_probability,
                "effective_retention_probability": (
                    (1 - churn_probability) + churn_probability * win_probability
                ),
            })

        win_rates[account_id] = account_win_rates

    return win_rates
