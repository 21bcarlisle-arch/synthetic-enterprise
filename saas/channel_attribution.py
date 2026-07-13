"""C12_channel_attribution_analytics -- the company's NAIVE channel-attribution
analytics (company-side, INSIDE the epistemic wall).

WHAT THIS IS
------------
A real UK supplier that offers a direct-debit (DD) discount, or wants to justify
pushing customers onto DD, builds a "business case": it looks at its own billing
records, sees that DD customers fall into arrears LESS than non-DD customers, and
attributes that whole difference TO the DD channel. This module is that analytics
-- and it is DELIBERATELY capable of being WRONG.

It computes, from OBSERVABLES ONLY (which channel a customer is on, and whether
they fell into arrears -- exactly what a billing system records):

    delta_naive = (arrears rate among non-DD) - (arrears rate among DD)

and CREDITS THE WHOLE OF IT to the DD channel (``attributed_to_dd``). That is the
naive causal reading a real supplier makes. It is an OVER-estimate, because the DD
cohort is pre-selected clean: more financially organised customers self-select
into DD AND independently carry lower arrears risk (a back-door confound). Most of
``delta_naive`` is therefore SELECTION, not treatment -- but this module cannot see
that, and does NOT try to. The harness (A6 attribution_gap) measures how far wrong
it is against the hidden causal answer key (``delta_true``).

THE WALL (CLAUDE.md Architectural Laws -- the company cannot see inside the SIM)
-------------------------------------------------------------------------------
This is COMPANY-side code. It imports NOTHING from ``simulation.*`` / ``sim.*``
(``python3 -m tools.epistemic_verifier`` enforces it). It never reads a customer's
hidden ``organisation`` latent, income decile, ``dd_selection_prob``, or the
counterfactual arrears probabilities -- those are the answer key. It reads ONLY the
two observables (``payment_channel``, ``had_arrears``). From those two alone the
selection and the treatment are NOT separable, which is exactly why a real supplier
falls into this trap and why this module is STRUCTURALLY capable of the error.

NO SECRET DE-CONFOUNDING (R12/R13 anti-goal-seek)
-------------------------------------------------
The headline ``delta_naive`` is the naive figure and nothing subtracts a selection
correction from it. There is a DISCOVERY HOOK (``confound_flag`` / ``confound_note``)
-- an honest analyst's CAVEAT that the effect MIGHT be a selection artefact -- but it
is a qualitative flag ONLY; it does not, and must not, adjust ``delta_naive`` toward
the causal truth. The whole point of the atom is that the naive method IS wrong by
the confound amount, and the gap is whatever it is.

DETERMINISM / PURITY (C-S2): every function here is pure -- same observations in ->
identical result out, no hidden state, no clock, no RNG. Safe to replay.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

# The company's own label for the direct-debit channel. Anything that is NOT this
# exact value is folded into "non-DD" (standard credit + prepayment) -- the binary
# the company's own DD-discount business case is framed on. The company does not
# need to know how the world spells the other channels; every non-DD channel is
# "the cohort without the DD discount" for this analysis.
DIRECT_DEBIT = "direct_debit"


@dataclass(frozen=True)
class ChannelObservation:
    """One customer's OBSERVABLE billing record, as a real supplier holds it.

    These two fields are ALL the company gets. There is deliberately NOWHERE here
    to put the hidden organisation latent / income decile / counterfactual -- the
    dataclass itself is the wall: you cannot pass what you cannot see.
    """
    payment_channel: str
    had_arrears: bool

    @property
    def on_dd(self) -> bool:
        return self.payment_channel == DIRECT_DEBIT


@dataclass(frozen=True)
class ChannelAttributionResult:
    """The naive DD business case, plus its honest caveat.

    ``delta_naive`` / ``attributed_to_dd`` are the SAME number: the observed
    arrears-rate difference, credited wholesale to the DD channel. ``confound_flag``
    / ``confound_note`` are the discovery hook -- a caveat, never a correction.
    """
    delta_naive: float            # (non-DD arrears rate) - (DD arrears rate)
    attributed_to_dd: float       # == delta_naive: the naive method credits it all to DD
    arrears_rate_dd: float
    arrears_rate_non_dd: float
    n_dd: int
    n_non_dd: int
    dd_share: float
    confound_flag: bool           # discovery hook: MIGHT this be a selection artefact?
    confound_note: str
    components: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# The naive analytics
# ---------------------------------------------------------------------------

def _confound_caveat(delta_naive: float, dd_share: float,
                     n_dd: int, n_non_dd: int) -> tuple[bool, str]:
    """The DISCOVERY HOOK. A qualitative caveat that ``delta_naive`` MIGHT be
    (partly) a selection artefact rather than a pure channel effect. It NEVER
    changes ``delta_naive`` -- it only raises the analyst's hand.

    Fires whenever the naive method has actually credited the DD channel with a
    benefit (delta_naive > 0) off an observational cohort comparison, because that
    is precisely the situation where unobserved self-selection into DD can inflate
    the measured effect. This is an honest supplier analyst's note ("we cannot
    rule out that DD customers were already lower-risk"), not a de-confounding
    step -- the company still has no way to separate selection from treatment from
    observables alone.
    """
    if n_dd == 0 or n_non_dd == 0:
        return (False, "only one channel present -- no channel comparison possible")
    if delta_naive > 0:
        return (
            True,
            "CAVEAT (not corrected): delta_naive credits the WHOLE observed arrears "
            "difference to the DD channel, but the DD cohort may be pre-selected "
            "lower-risk (customers self-selecting into direct debit by unobserved "
            "traits). From these observables alone selection and treatment are not "
            "separable, so delta_naive is an UPPER bound on the true channel effect.",
        )
    return (False, "delta_naive <= 0: DD shows no observed arrears advantage to over-credit")


def analyse_observations(
    observations: Iterable[ChannelObservation],
) -> ChannelAttributionResult:
    """Compute the naive DD business case from per-customer OBSERVABLES.

    delta_naive = (arrears rate among non-DD) - (arrears rate among DD), credited
    wholesale to the DD channel. Reads only ``payment_channel`` + ``had_arrears``.
    """
    n_dd = n_non_dd = arrears_dd = arrears_non_dd = 0
    for obs in observations:
        if obs.on_dd:
            n_dd += 1
            arrears_dd += 1 if obs.had_arrears else 0
        else:
            n_non_dd += 1
            arrears_non_dd += 1 if obs.had_arrears else 0
    return _build_result(n_dd, n_non_dd, arrears_dd, arrears_non_dd)


def analyse_ingredients(ingredients: Mapping) -> ChannelAttributionResult:
    """Compute the naive DD business case from the aggregate OBSERVABLE ingredients
    (the ``naive_ingredients`` shape a real billing extract would hand you):

        {"n_dd", "n_non_dd", "arrears_dd", "arrears_non_dd", ...}

    Reads only those observable counts -- no hidden field is present to read.
    """
    return _build_result(
        int(ingredients["n_dd"]),
        int(ingredients["n_non_dd"]),
        int(ingredients["arrears_dd"]),
        int(ingredients["arrears_non_dd"]),
    )


def _build_result(n_dd: int, n_non_dd: int,
                  arrears_dd: int, arrears_non_dd: int) -> ChannelAttributionResult:
    rate_dd = (arrears_dd / n_dd) if n_dd else 0.0
    rate_non_dd = (arrears_non_dd / n_non_dd) if n_non_dd else 0.0
    delta_naive = rate_non_dd - rate_dd            # credited wholesale to DD
    total = n_dd + n_non_dd
    dd_share = (n_dd / total) if total else 0.0
    flag, note = _confound_caveat(delta_naive, dd_share, n_dd, n_non_dd)
    return ChannelAttributionResult(
        delta_naive=delta_naive,
        attributed_to_dd=delta_naive,              # the naive method's causal claim
        arrears_rate_dd=rate_dd,
        arrears_rate_non_dd=rate_non_dd,
        n_dd=n_dd,
        n_non_dd=n_non_dd,
        dd_share=dd_share,
        confound_flag=flag,
        confound_note=note,
        components={
            "arrears_dd": arrears_dd,
            "arrears_non_dd": arrears_non_dd,
            "rate_dd": round(rate_dd, 6),
            "rate_non_dd": round(rate_non_dd, 6),
        },
    )


def make_observations(
    records: Sequence[Mapping],
    channel_key: str = "payment_channel",
    arrears_key: str = "had_arrears",
) -> list[ChannelObservation]:
    """Adapt a sequence of raw observable dicts (channel + arrears flag) into
    ``ChannelObservation`` records. A convenience for callers holding billing rows;
    it copies ONLY the two observable fields, so nothing hidden can ride along."""
    return [
        ChannelObservation(
            payment_channel=str(r[channel_key]),
            had_arrears=bool(r[arrears_key]),
        )
        for r in records
    ]
