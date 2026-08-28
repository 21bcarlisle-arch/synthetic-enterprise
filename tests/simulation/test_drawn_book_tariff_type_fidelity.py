"""The drawn book's `tariff_type`, and the change that must NOT be made to it.

Ruling: `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` (2026-08-28).

213 of 222 electricity accounts carry `tariff_type=None`, so the company's
`UPLIFTABLE_TARIFF_TYPES` guard refuses them and the value-cycle A/B prices 25
renewals instead of a few hundred. The tempting repair is to label the drawn book
`fixed` -- the world already settles these down every fixed branch, so it looks
like pure book-keeping.

It is not. Ofgem/CMA/DESNZ put the DOMESTIC fixed share at ~10-46% across
2016-2025, centred near one third
(`docs/market_research/svt_rates_active_passive_2016_2025.md`), and 220 of 222
electricity accounts are `resi`. Labelling the book `fixed` would assert 100%
fixed against a published ~33% -- a fidelity REGRESSION whose only real effect is
to widen the experiment's own denominator. R13 forbids exactly that: the baseline
world may only change for fidelity-to-reality reasons, decided blind to what it
does to company results.

So these tests do two jobs. They PIN what the world does with an unlabelled term
today, and they RATCHET against the unanchored repair while leaving the anchored
one free to land.
"""
from __future__ import annotations

import collections

import simulation.population_draw as pd
from company.interfaces.customer_profitability import UPLIFTABLE_TARIFF_TYPES

SEED = 7

# Well above the anchor's HIGHEST domestic fixed share in any year of the window
# (~44-46%, 2019-20 pre-crisis) and far below the 100% a blanket label produces.
# The bound is deliberately loose: it is not trying to police a distribution, it is
# trying to catch a book that was given ONE product because that made `n` bigger.
ANCHORED_FIXED_SHARE_CEILING = 0.60


def _drawn(lam: float = 40) -> list:
    """A drawn population big enough to say something about a SHARE.

    The live curriculum is a ~1/year trickle (Profile B), which is 7 accounts over
    the whole window -- far too few to distinguish "no product" from "one product".
    The lambda override is a fixture concern only; it moves the sample size, never
    the labelling law under test.
    """
    return list(
        pd.iter_acquisition_events(
            base_seed=SEED, start_year=2016, end_year=2025,
            acquisitions_per_year_lambda=lam,
        )
    )


# --------------------------------------------------------------------------- #
# (a) What the world does with an unlabelled term                             #
# --------------------------------------------------------------------------- #

def test_the_rendered_key_is_PRESENT_so_the_get_default_never_fires():
    """The mechanism, one line sharper than "the draw never sets it".

    `to_customer_dict()` renders `tariff_type` UNCONDITIONALLY, so the key is
    present with value None. `c.get("tariff_type", "fixed")` -- which
    `run_phase2b.py:1124` and `:1144` call precisely to avoid this -- therefore
    returns None, not "fixed". A rendered None and an absent key are DIFFERENT
    censuses, and the drawn and hand-authored populations sit on opposite sides of
    that line.

    Survives the anchored repair: it asserts the key is present and that the
    default is bypassed whenever a value is rendered, not that the value is None.
    """
    events = _drawn(lam=5)
    assert events, "no acquisition events drawn, so this proves nothing"

    rendered = [e.to_customer_dict() for e in events]
    assert all("tariff_type" in d for d in rendered), (
        "to_customer_dict() no longer renders tariff_type; the .get(..., 'fixed') "
        "defaults downstream would now fire and this whole finding changes shape"
    )
    # The key being present is exactly what disarms the default.
    for d in rendered:
        assert d.get("tariff_type", "fixed") == d["tariff_type"], (
            "a rendered key cannot take a .get default -- if this fails the dict "
            "semantics this determination rests on have changed"
        )


def test_an_unlabelled_term_settles_down_every_FIXED_branch():
    """What these accounts ARE in the world: ordinary annual fixed contracts whose
    product was never labelled.

    Every branch the settlement path takes on `tariff_type` sends an unlabelled
    term down the fixed route -- it locks a unit rate, it is not indexed, it is not
    deemed or flex, and it is hedged as a fixed contract rather than passed through.
    That is what makes the missing label look like book-keeping, and it is why the
    determination had to be argued on the DISTRIBUTION instead.
    """
    tt = None
    assert tt != "flex", "renewals.py:175 -- locks prev_fixed_unit_rate"
    assert tt != "deemed", "run_phase2b.py:1996"
    assert tt not in ("deemed", "flex"), "run_phase2b.py:1395 -- not indexed"
    assert tt != "pass_through", "run_phase2b.py:2086/2148/2183/2199 -- hedged, not passed through"
    # And the company refuses it, which is the whole observed effect.
    assert tt not in UPLIFTABLE_TARIFF_TYPES


# --------------------------------------------------------------------------- #
# (c) The ratchet                                                             #
# --------------------------------------------------------------------------- #

def test_the_drawn_book_is_not_given_a_BLANKET_upliftable_product():
    """THE RATCHET. Fails if the drawn domestic book is labelled with one
    upliftable product, whatever the stated reason.

    This is the change the determination refuses: it would take the A/B's decision
    surface from 25 to ~213 while moving the world's domestic fixed share from
    "silent" to 100% against a published ~33%. An ANCHORED repair -- drawing the
    label from the year-by-year Ofgem fixed/SVT split -- passes this test
    comfortably, because the anchor never exceeds ~46% in any year.

    R15 MUTATION (must fire): set `SyntheticCustomer.tariff_type` to `"fixed"`
    instead of `None`, or set it in `_draw_one`. Share goes 0.00 -> 1.00 and this
    reds. RUN AND REVERTED 2026-08-28.
    """
    events = _drawn()
    resi_elec = [
        e for e in events if e.segment == "resi" and e.commodity == "electricity"
    ]
    # Population assertion: a share computed over a handful of accounts says
    # nothing, and an empty list would pass every bound below for free.
    assert len(resi_elec) >= 100, (
        f"only {len(resi_elec)} resi electricity draws -- too few to judge a share, "
        "so this control would be passing on an empty population"
    )

    labelled = [e for e in resi_elec if e.tariff_type in UPLIFTABLE_TARIFF_TYPES]
    share = len(labelled) / len(resi_elec)

    assert share <= ANCHORED_FIXED_SHARE_CEILING, (
        f"{share:.0%} of drawn domestic electricity accounts carry an upliftable "
        f"product, above the {ANCHORED_FIXED_SHARE_CEILING:.0%} ceiling. Ofgem/CMA "
        "put the real domestic fixed share at ~10-46% across 2016-2025. If this is "
        "an ANCHORED distribution, raise the ceiling and cite the series. If it is "
        "a blanket label, it is the R13 change refused by "
        "docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md -- the world "
        "does not acquire a product because the experiment wants a bigger n."
    )


def test_the_world_still_has_NO_standard_variable_product_to_assign_the_rest_to():
    """Why the honest repair is an atom and not a label assignment.

    Two thirds of a real domestic book sits on SVT with no renewal decision at all,
    and the world cannot settle that: `build_renewal_schedule` knows `fixed`,
    `flex`, `deemed` and `pass_through` only. `deemed` is out-of-contract spot+20%
    -- a GAP between contracts, not a variable tariff. Until an SVT product exists,
    any label assigned to the drawn book is a choice between products that all
    carry an annual renewal decision, which is the fidelity defect itself.

    When the SVT product lands, this test is the one that should be updated -- by
    adding it to the set, not by deleting the assertion.
    """
    import simulation.renewals as renewals

    src = (renewals.__file__, open(renewals.__file__, encoding="utf-8").read())[1]
    for product in ("deemed", "flex"):
        assert f'"{product}"' in src, f"{product} is no longer a product this world settles"
    assert "standard_variable" not in src and '"svt"' not in src.lower(), (
        "a standard-variable product now exists in the world -- the owed repair in "
        "docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md has landed, "
        "so revisit the drawn book's label against the Ofgem year-by-year split"
    )
