"""The declared money boundary -- one quantization point for printed money.

**Why this module exists.** `docs/design/MONEY_REPRESENTATION_EVIDENCE.md`
(DISCOVER, 2026-07-28) censused money representation across `saas/`+`company/`
and found: zero `Decimal` usage, money is `float` everywhere it is computed,
and `round(x, 2)` appears ~1,006 times applied independently at whichever call
site a developer happened to remember. That is the "undeclared -- worst of the
three" state: not float-by-choice, not Decimal, just ad hoc.

Its measured consequence, reproduced against the live published customer-facing
artefact `docs/state/billing_ledger.json` (the GitHub-Pages mirror of
`site/state/billing_ledger.json`) before this module existed: **534 of 1,603
printed invoices (33.3%) had line items that did not sum, to the penny, to the
total printed on the same invoice** (worst single-bill divergence 2p; e.g.
94.50 + 34.15 + 8.36 + 6.85 = 143.86 printed against a total of 143.88). The
material finding is the DEFECT RATE, not the magnitude -- a third of bills said
"the maths doesn't add up" on their face.

**The recommendation this implements** (that DISCOVER's §4 [ACT]): a declared
boundary-conversion policy, NOT a full float->Decimal core migration. Money
stays `float` in the computation core; every point where money becomes a
PRINTED figure goes through here. That closes the observed defect without the
schema/JSON/front-end blast radius of a core migration (§3 of the same doc).
The full-migration question stays separately open and is NOT answered here.

**The mechanism, and why it is this one.** The printed total is DERIVED from
the printed line items rather than rounded independently from the raw total.
By construction the parts then sum to the whole, and no line item is fudged to
absorb a residual -- every printed line is exactly the quantization of its own
raw value. This is the same class fix already applied to the metered reads in
`tools/generate_billing_ledger.py` (the displayed usage is derived from the
displayed reads, 2026-07-11, ADVISOR_STEER_BILL_ARITHMETIC.md Defect 1), now
applied to money. A customer re-adding the column always gets the total.

**Rounding convention: ROUND_HALF_UP, computed in Decimal.** Python's builtin
`round()` does banker's rounding on the binary float, so `round(2.675, 2)` is
`2.67` -- a customer who works the arithmetic by hand gets 2.68 and concludes
the bill is wrong. UK consumer billing rounds half away from zero. Quantizing
via `Decimal(str(x))` reads the DECIMAL value a human sees rather than its
binary approximation, so the printed figure matches hand arithmetic.

**The rate boundary (2026-08-03, `D_printed_figure_rederivation`).** Footing
closed "the column adds up". It did not close "each line can be re-derived",
which is the same customer test one level down and was false on 86% of
RENDERED usage lines: a bill saying `317.9 kWh x 11.90p = GBP 37.82` is
arithmetic that does not hold, whatever the underlying figures were. So a
printed RATE goes through here too (`display_rate_p_per_kwh`,
`display_rate_gbp_per_day`), at a declared display precision chosen so the
line reproduces exactly as printed. See `minimal_display_rate` for why the
rate is fitted to the amount rather than the amount derived from a fixed-
precision rate -- the short version is that these rates are DERIVED, so the
money is the primary figure and must not move to tidy the printout.

R15: every public function fails CLOSED. A value that cannot be read, or is not
finite, raises rather than being silently coerced to 0.0 -- an unquantizable
figure is a failed quantization, never a pass. `foot_components_to_total`
additionally refuses a reconciliation whose residual exceeds what independent
penny-rounding could possibly produce, because that means a component is
MISSING from the printed set (the F6 defect class -- see its docstring), not
that rounding drifted.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import isfinite
from typing import Mapping

__all__ = [
    "MoneyBoundaryError",
    "PENNY",
    "MAX_PENNY_ROUNDING_GBP",
    "RATE_DISPLAY_MIN_DP",
    "RATE_DISPLAY_MAX_DP",
    "quantize_gbp",
    "foot_components_to_total",
    "minimal_display_rate",
    "display_rate_p_per_kwh",
    "display_rate_gbp_per_day",
]

PENNY = Decimal("0.01")

#: Display precision floor for a printed RATE, in decimal places of its own
#: unit. Two is the real-bill convention (a UK bill prints "24.50p/kWh", not
#: "24.5p/kWh"), so a rate is never printed coarser than this even when a
#: coarser one would happen to reconcile.
RATE_DISPLAY_MIN_DP = 2

#: Display precision ceiling for a printed rate. Beyond this a figure stops
#: being readable on a bill, so a line needing more precision than this is
#: treated as NOT expressible as quantity x rate at all (see
#: `minimal_display_rate`) rather than printed at a precision nobody can use.
RATE_DISPLAY_MAX_DP = 6

#: The most a single independent 2dp rounding can move a figure. A component
#: rounded to the penny differs from its raw value by at most half a penny.
MAX_PENNY_ROUNDING_GBP = 0.005

#: Float-comparison slack for the residual bound below. Two orders of magnitude
#: below a penny -- large enough to absorb IEEE-754 representation noise in the
#: bound arithmetic, far too small to admit a real missing component.
_RESIDUAL_EPSILON_GBP = 1e-9


class MoneyBoundaryError(ValueError):
    """A figure could not be carried across the money boundary.

    Raised rather than returned so a bad money value can never be printed. The
    caller's correct response is to HOLD the bill to the exception queue (see
    `company.billing.pre_bill_validation`), never to fall back to the
    unreconciled figure -- that fallback would be the fail-open R15 names.
    """


def quantize_gbp(value, *, field: str = "amount") -> float:
    """Quantize one GBP figure to the penny, ROUND_HALF_UP, as a float.

    `field` names the figure in any raised error so a failure is diagnosable
    from the message alone (R5: alerts carry the diagnostic payload).

    Fails CLOSED: a None, a non-numeric, or a non-finite (NaN/Inf) value raises
    `MoneyBoundaryError`. There is deliberately no "treat missing as zero" path
    here -- callers that legitimately have an absent optional line (a catch-up
    adjustment on a non-catch-up bill) omit the key rather than passing None,
    so an unexpected None stays a real failure instead of silently printing
    £0.00 where a real charge belonged.
    """
    if isinstance(value, bool) or value is None:
        # bool is an int subclass; a True/False in a money field is a type
        # error that would otherwise quantize happily to 1.00/0.00.
        raise MoneyBoundaryError(
            f"{field}: expected a GBP number, got {value!r}"
        )
    try:
        as_float = float(value)
    except (TypeError, ValueError) as exc:
        raise MoneyBoundaryError(
            f"{field}: expected a GBP number, got {value!r}"
        ) from exc
    if not isfinite(as_float):
        raise MoneyBoundaryError(
            f"{field}: non-finite GBP value {as_float!r} cannot be quantized"
        )
    try:
        quantized = Decimal(str(as_float)).quantize(PENNY, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:  # pragma: no cover - defensive
        raise MoneyBoundaryError(
            f"{field}: {as_float!r} cannot be quantized to the penny"
        ) from exc
    return float(quantized)


def foot_components_to_total(
    components: Mapping[str, float],
    declared_total,
    *,
    label: str = "bill",
) -> tuple[dict[str, float], float]:
    """Quantize a bill's components and derive the printed total from them.

    Returns `(printed_components, printed_total)` where every value is a
    penny-exact float and `sum(printed_components.values()) == printed_total`
    exactly, as printed. That equality is what makes the invoice add up on its
    face; it is achieved by DERIVING the total, not by adjusting a line item.

    `declared_total` is the computation core's own unrounded total for the same
    bill. It is not printed -- it is the independent cross-check. The derived
    total is compared against it, and a divergence larger than independent
    penny-rounding could produce raises `MoneyBoundaryError`.

    **The residual bound, and what it is really guarding.** With `n`
    components, `sum(quantized components)` can differ from `sum(raw
    components)` by at most `n x 0.005`, and `quantize(declared_total)` can
    differ from the raw total by at most a further `0.005`. So anything inside
    `(n + 1) x 0.005` is ordinary rounding. Anything OUTSIDE it means the
    declared total contains money that is not in the printed component set --
    i.e. a line item the invoice does not show. That is precisely the F6 defect
    class (`company.compliance.domain_invariants.BILL_FOOTS`: the first F6
    build omitted `catchup_adjustment_gbp` from its footing set and wrongly
    held 147 legitimate catch-up bills). Here the same omission fails LOUDLY at
    the point of printing instead of silently printing a total nobody can
    reconcile. The bound is tight enough to catch a missing line (any real
    component is pounds, not pence) and loose enough that ordinary rounding can
    never trip it -- a false positive here would hold a legitimate bill.

    Empty `components` with a non-zero declared total raises: a bill whose
    total rests on no printed line at all is the £999,999-on-£88-of-line-items
    absurdity BILL_FOOTS was written for, and returning 0.00 would be the
    fail-open reading.
    """
    printed: dict[str, float] = {}
    for key, raw in components.items():
        printed[key] = quantize_gbp(raw, field=f"{label}.{key}")

    # Sum in Decimal: adding penny-exact floats in binary can land at
    # 143.86000000000001, which would then not compare equal to the printed
    # total a consumer recomputes. Summing the Decimals keeps the identity
    # sum(printed) == printed_total exact in the decimal domain.
    total_dec = sum(
        (Decimal(str(v)) for v in printed.values()), Decimal("0")
    ).quantize(PENNY, rounding=ROUND_HALF_UP)
    printed_total = float(total_dec)

    checked_total = quantize_gbp(declared_total, field=f"{label}.declared_total")
    residual = abs(printed_total - checked_total)
    max_residual = (len(printed) + 1) * MAX_PENNY_ROUNDING_GBP + _RESIDUAL_EPSILON_GBP
    if residual > max_residual:
        raise MoneyBoundaryError(
            f"{label}: printed line items sum to {printed_total:.2f} but the declared "
            f"total is {checked_total:.2f} (residual {residual:.2f} > {max_residual:.3f} "
            f"admissible for {len(printed)} independently rounded components) -- a "
            f"component is missing from the printed set, not a rounding difference. "
            f"Printed set: {sorted(printed)}"
        )
    return printed, printed_total


def minimal_display_rate(
    quantity,
    amount_gbp,
    *,
    scale: float,
    field: str = "rate",
    min_dp: int = RATE_DISPLAY_MIN_DP,
    max_dp: int = RATE_DISPLAY_MAX_DP,
):
    """The coarsest printable rate that still reproduces the printed amount.

    Returns `(rate, dp)` -- the rate quantized to `dp` decimal places -- or
    `None` when no precision in `[min_dp, max_dp]` reproduces the amount.

    `quantity` and `amount_gbp` must be the PRINTED figures, not the core's
    full-precision ones: the identity this establishes is the one a customer
    checks with the numbers in front of them. `scale` converts rate units into
    pounds (0.01 for a p/kWh rate, 1.0 for a GBP/day rate), so the reproduced
    identity is `quantize_gbp(quantity * rate * scale) == amount_gbp`.

    **Why the rate is fitted to the amount and not the other way round.** The
    alternative -- declare a fixed rate precision and DERIVE the printed amount
    from it -- was measured on the real book and rejected: it changes the
    charge on 86% of bills (median ~7p, up to GBP 7.86 on a GBP 17,215
    industrial line) purely to tidy the printout. Changing what a customer is
    charged so the bill's arithmetic looks right is the wrong way round. It is
    only tempting because a unit rate LOOKS contractual; here it is not. These
    rates are DERIVED (`commodity_amount / consumption`, `standing_charge /
    days`) from a half-hourly settled charge that no single unit rate
    generated, so the amount is the primary figure and the rate is a
    presentation of it. A contractual tariff rate would invert this, and this
    function would be the wrong tool for that line.

    **Why a range of precisions rather than one declared constant.** The
    precision a line needs is a function of its magnitude: the same 2dp rate
    that reproduces a 50 kWh line to the penny is out by GBP 7.86 on a 157,128
    kWh one, because the rounding error is `quantity x delta`. Measured across
    the real book, the required precision spans 1 to 6 decimal places. A single
    declared constant is therefore either too coarse for industrial lines or
    absurd on domestic ones; the floor keeps domestic bills looking like bills
    and the search buys exactness where the magnitude demands it.

    Fails CLOSED. A non-finite or unreadable quantity or amount raises
    `MoneyBoundaryError` rather than returning None, because those are broken
    inputs rather than an inexpressible line -- non-finite is checked FIRST,
    since every comparison below is NaN-blind and would otherwise report a
    tidy "not expressible" for a corrupt figure. A zero quantity returns None:
    no rate divides into it, and printing one would invent an arithmetic.
    """
    if isinstance(quantity, bool) or quantity is None:
        raise MoneyBoundaryError(f"{field}: expected a quantity, got {quantity!r}")
    try:
        qty = float(quantity)
    except (TypeError, ValueError) as exc:
        raise MoneyBoundaryError(
            f"{field}: expected a quantity, got {quantity!r}"
        ) from exc
    if not isfinite(qty):
        raise MoneyBoundaryError(
            f"{field}: non-finite quantity {qty!r} cannot carry a printed rate"
        )
    # quantize_gbp does the non-finite/unreadable check for the amount, and
    # raises with the field name if it fails.
    amount = quantize_gbp(amount_gbp, field=f"{field}.amount")
    if qty == 0:
        return None

    qty_dec = Decimal(str(qty))
    scale_dec = Decimal(str(scale))
    amount_dec = Decimal(str(amount))
    for dp in range(min_dp, max_dp + 1):
        exponent = Decimal(1).scaleb(-dp)
        rate = (amount_dec / (qty_dec * scale_dec)).quantize(
            exponent, rounding=ROUND_HALF_UP
        )
        reproduced = (qty_dec * rate * scale_dec).quantize(
            PENNY, rounding=ROUND_HALF_UP
        )
        if reproduced == amount_dec:
            return float(rate), dp
    return None


def display_rate_p_per_kwh(consumption_kwh, commodity_amount_gbp, *, field="unit_rate"):
    """The printed p/kWh rate for a usage line, or None if none reproduces it.

    Thin, named wrapper over `minimal_display_rate` at pence scale -- the
    caller should not be restating `scale=0.01` at each site, which is exactly
    the ad hoc repetition this module exists to end.
    """
    return minimal_display_rate(
        consumption_kwh, commodity_amount_gbp, scale=0.01, field=field
    )


def display_rate_gbp_per_day(days_in_period, standing_charge_gbp, *, field="standing_rate"):
    """The printed GBP/day standing rate, or None if none reproduces the line.

    Also the fix for printed binary-float residue: the daily rate was
    previously passed to the bill raw from `standing_charge / days`, printing
    figures like 0.23983870967741938 into a customer-facing artefact. A rate
    that comes out of here is quantized by construction.
    """
    return minimal_display_rate(
        days_in_period, standing_charge_gbp, scale=1.0, field=field
    )
