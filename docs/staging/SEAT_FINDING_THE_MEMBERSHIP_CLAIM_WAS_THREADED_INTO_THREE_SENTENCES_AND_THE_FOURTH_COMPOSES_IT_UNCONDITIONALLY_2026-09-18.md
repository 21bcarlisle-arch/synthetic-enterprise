**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The membership claim was threaded into three sentences and the fourth composes it unconditionally

**Filed:** 2026-09-18 · **Claim id:** `republish-the-arms-decomposition-over-one-priced-book`
**Subject:** `tools/generate_value_arms_data.py::_one_member_clause`
**Established against:** `5167f1281` (the commit that threaded the other three)

---

## The finding in one line

`5167f1281` made the membership claim conditional on `membership_refused_because` in
`_leg_over_its_own_family`'s two structural sentences and in `_selection_leg_reading`'s rendered
reading. **`_one_member_clause` was not threaded** and still composes
*"The single run every other figure on this page is drawn from is one member of those {n}"*
unconditionally, from a leg that now carries the answer in
`single_run.is_one_of_the_draws_above`.

## It is LATENT and not live, and the reason is worth writing down

The clause is reached only from `_selection_sentence`, which reaches it only when
`_spread_for(spreads, ...)` returns a family — which requires `_seed_spreads` to have cleared its
staleness leg — and on that branch `_seed_spreads` sets `membership_refused_because` to `None`. So
today the argument that would refuse membership cannot be non-`None` at this call site, and the
published feed contains **zero** occurrences of `is one member of` (measured on
`site/data/value_arms.json` regenerated at `5167f1281` over the 09-18 book).

**This is an equivalence today, not a missing test — established rather than assumed**, and it is
the flattering reading, so it is recorded here rather than left to a reader. The reachable-only-by-
construction witness is a `spreads` dict with the key absent, which is what a test has to build.

## Why it is still owed

The equivalence holds only while `membership_refused_because` has exactly ONE source. The
parameter's whole point is that membership can be refused for reasons other than the stamp — the
stamp is a proxy `_staleness_caveat`'s own docstring calls *"wrong in both directions"*, and the
floor carries no book identity. The first time a second refusal reason is added, or the first time
`_seed_spreads` admits a pair on a book rule rather than a date, this sentence republishes the
claim the other three withdrew — on the page's prose, under the headline, where a reader meets it.

Three sentences saying one thing and a fourth saying its opposite is the shape this page has now
paid for twice in one day: the fourth sentence in `_selection_leg_reading` was itself found only
because a mutation on the third did not fire.

## The remedy

Compose from the leg, which already carries the answer — no new parameter, so there is nothing for
a call site to forget to pass:

```python
    single = leg.get("single_run") or {}
    if single.get("is_one_of_the_draws_above") is True:
        ...the existing member wording...
    return (" The single run every other figure on this page is drawn from came out at {run}"
            "{flip}, and it is NOT one of those {n}: {why}")
```

...with its witness constructed (a `spreads` block with the key absent), because the live artefact
cannot reach the branch — which is the same lesson `_floor_without_a_book` records.

## Why this was not fixed in the same turn

`tools/generate_value_arms_data.py` was under live in-place edit by the lane that landed
`5167f1281`, and the defect is unreachable on today's feed. Landing a contested-path change for a
branch nothing can enter buys a collision and no honesty. The deliverable this turn — the
promotion and republish over one priced book — touches neither file.
