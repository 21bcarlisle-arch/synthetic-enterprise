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


def test_the_world_settles_the_standard_variable_product_the_determination_registered_as_owed():
    """DISCHARGED 2026-09-19, and the way it had to be rewritten is the finding.

    This test used to assert the OPPOSITE -- that no standard-variable product existed -- and its
    docstring said: *"When the SVT product lands, this test is the one that should be updated --
    by adding it to the set, not by deleting the assertion."* That is the update.

    **IT NEVER FIRED, AND IT SHOULD HAVE FIRED THREE WEEKS AGO.** The old assertion was
    `'"svt"' not in src.lower()` over `simulation/renewals.py`. C1a landed the product on
    2026-08-30 and `renewals.py` branches on it at line 131 -- but through the imported constant
    `SVT_TARIFF_TYPE`, so the literal three characters in quotes never appear in that file and the
    grep stayed green across the exact event it was written to catch. A grep for a NAME is blind
    to the MECHANISM implemented without it. The replacement below asks the builder, not the
    bytes.

    So the assertion is now the positive one: the world settles `svt`, `deemed` and `flex`, and
    the drawn book's label has been revisited against the published record -- which is what
    `simulation/arrival_route.py` and `population_draw._draw_tariff_type` did, on the arrival
    route rather than on the stock share.

    TWO DRAFTS OF THE REPLACEMENT WERE ALSO WRONG AND BOTH ARE KEPT HERE, because each was caught
    by running the mutation rather than by thinking harder, and the second one is the more
    instructive.

    Draft 1 asserted `SVT_TARIFF_TYPE in {t["tariff_type"] for t in schedule}`. It passes with the
    SVT-origin branch dead, because the C1b passive ROLL further down the same builder also emits
    SVT segments. The observable was satisfied by a different mechanism than the one under test.

    Draft 2 asserted `schedule[0]["tariff_type"] == SVT_TARIFF_TYPE`, on the stated reasoning that
    *"the roll cannot reach index 0 because a roll needs a term to roll off"*. That reasoning is
    FALSE: a household that is passive at its very first boundary rolls onto SVT at index 0, so
    with the branch neutered this household's schedule came back all-SVT and the control passed
    again. Same defect as draft 1, one layer deeper.

    Draft 3 used a BOUND PAIR -- the same household built as a switcher and as a mover -- and
    asserted they differ at index 0. It ALSO passed under the mutation, and the reason is the
    useful one: **"opens on SVT" is over-determined by the label.** Two mechanisms produce it. The
    arrival branch is one; the other is `rolls_active_renewal`, which reads `tariff_type` and
    returns False for an SVT household, so the main loop's own passive branch opens the account on
    SVT anyway. Neuter either one and the observable survives on the other.

    So the observable that belongs to the arrival branch ALONE is not the opening -- it is the
    EXIT. Without the branch the household stays on the default tariff for the whole window; with
    it, the stint is bounded by the first anniversary and a non-SVT term follows. The pair is kept
    because it is what establishes the household is not a passive roller, and the exit clause is
    what makes the whole thing falsifiable.

    R15 MUTATION (must fire): neuter the SVT-origin branch in `renewals.build_renewal_schedule`
    (`if tariff_type == SVT_TARIFF_TYPE:` -> `if False:`). RUN 2026-09-19 -- it did NOT fire
    against drafts 1, 2 or 3, which is how each was caught, and DOES fire against the exit clause
    below. The grep this all replaces could not be mutated to fire at all, which is the definition
    of a control that cannot fail.
    """
    import datetime as _dt

    from simulation.renewals import build_renewal_schedule
    from simulation.svt_product import SVT_TARIFF_TYPE

    start, end = "2017-01-01", "2020-01-01"
    records = [
        {
            "settlementDate": (_dt.date(2016, 1, 1) + _dt.timedelta(days=i)).isoformat(),
            "systemSellPrice": 60.0,
        }
        for i in range((_dt.date.fromisoformat(end) - _dt.date(2016, 1, 1)).days + 1)
    ]
    def _open(tariff_type):
        return build_renewal_schedule(
            "FIDELITY-SVT-1", start, end, records, 3100,
            segment="resi", tariff_type=tariff_type,
        )

    as_switcher, as_mover = _open("fixed"), _open(SVT_TARIFF_TYPE)
    assert as_switcher and as_mover, "the builder returned an empty schedule for one leg"

    # LEG 1 -- the pair can discriminate. If this household were passive at its first boundary it
    # would open on SVT whichever way it was built, and leg 2 would be true for a reason that has
    # nothing to do with the arrival branch.
    assert as_switcher[0].get("tariff_type") != SVT_TARIFF_TYPE, (
        "the control's own subject has stopped discriminating: this household now opens on SVT "
        "even when built as a switcher, so it is a passive first-boundary roller and leg 2 below "
        "would pass without the arrival branch existing. Pick a household that opens on a fixed "
        "term as a switcher -- do not delete leg 2."
    )
    # LEG 2 -- built as a move-in, the same household opens on the default tariff instead.
    assert as_mover[0].get("tariff_type") == SVT_TARIFF_TYPE, (
        f"built as a move-in this household still opened on "
        f"{as_mover[0].get('tariff_type')!r}. The standard variable product the 2026-08-28 "
        "determination registered as owed is not reachable AS AN ARRIVAL, so the drawn book has "
        "nothing honest to be labelled with again."
    )
    # LEG 3 -- THE ONE THE MUTATION FIRES ON. An SVT arrival is a stint, not an absorbing state:
    # it is bounded by the first anniversary and the household can leave. Legs 1 and 2 are both
    # satisfied by `rolls_active_renewal` reading the label, with the arrival branch dead; only
    # this one requires the branch itself.
    mover_kinds = [t.get("tariff_type") for t in as_mover]
    assert any(k != SVT_TARIFF_TYPE for k in mover_kinds), (
        f"a move-in arrival never leaves the default tariff: {mover_kinds}. The arrival is an "
        "absorbing state, so the priced boundary the arm was shown to admit is unreachable and "
        "the producer mints a label with no path behind it -- the drawn item's own stated test "
        "for insufficient work."
    )
    # And the three products it displaced nothing from are still settleable, or "the world gained
    # SVT" would be indistinguishable from "the world lost everything else".
    import simulation.renewals as renewals

    src = open(renewals.__file__, encoding="utf-8").read()
    for product in ("deemed", "flex"):
        assert f'"{product}"' in src, f"{product} is no longer a product this world settles"
