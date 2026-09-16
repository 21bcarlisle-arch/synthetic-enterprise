**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-published-inversion-must-carry-its-attribution-on-the-page-not-only-in-the-tree) · **Class:** figures_on_a_superseded_clock

# RESULT — the inversion now carries its attribution on the page, and the strata carry no interval of their own

`run_value_cycle_ab.pair_strata` was landed, tested and mutation-proven at `8d3fe6836`, and
`grep -rn pair_strata tools/generate_value_arms_data.py site/capabilities/index.html` returned
nothing: the identity existed and no reader could see it. It is wired. The live
`site/data/value_arms.json` carries the split under `method_skill.fixed_horizon.pair_strata`, and
the door renders it in `fixedHorizonBlock` immediately after the estimand's own verdict.

## What a reader now meets, beside the 0.4210

| stratum | pairs the estimator could compare | rank |
|---|---|---|
| within settled — leg 2's own population | 7,606 | **0.5130** |
| **the tie mass** — both rows scored 0.0 | **0** (666 pairs of decisions) | *no comparable pair* |
| cross — each departure against each survivor | 4,588 | **0.2686** |

and the producer's own composed sentence: *37 of 161 scored decisions (23%) sit tied at 0.0 … the
tie mass supplies NONE of the 12,194 comparable pairs and cannot move the figure. The departure is
carried by the 4,588 cross pairs … in 73% of departure-against-survivor pairs the arm had given the
DEPARTURE the higher margin. Had the cross stratum carried no information the estimand would read
**0.5081** rather than 0.4210. THE INVERSION IS NOT A TIE-HANDLING ARTEFACT: it is the arm ranking
its own departures above the customers it kept.*

No re-run was needed and none was done. The split is an identity over four counts the two legs
already publish, so the page calls the producer's own function over the artefact of `2026-09-09
01:24:34Z` and says so on the surface: **"Attributed by this page, by calling the run producer's own
`pair_strata` over the two legs this artefact already carries."** A run that carries the block in
its own artefact is passed through instead, and `computed_by` is what tells the two apart.

## What is STILL unattributed, which is the half that is easy to lose

1. **`pair_strata` rules out the tie mass and does not rule out the arm — it names it.** What it
   rules out is one *structural* cause: the estimator excludes every pair tied on the outcome, so
   all 666 within-zero pairs contribute nothing and cannot move a weighted mean of the other two.
   That is answered by construction and *measured* by two identities (the estimand's comparable
   pairs must exceed leg 2's by exactly `z × s`, and its outcome ties by exactly `C(z, 2)`), which
   is why the block refuses rather than publishing an attribution whose precondition is false.
2. **The cross stratum's direction is attributed; its precision is not.** Its 4,588 pairs are
   determined by only **37** rows' signals, over a wider account set than leg 2's. That is leverage
   and clustering — it does not move which stratum carries the departure, and it does mean the
   interval beside the estimand is **narrower than this sample really earns**. Until this landed
   that sentence lived only in the producer's docstring; it is now on the page, composed from the
   counts, as the strata's own "no interval of their own" clause.
3. **Why the departures were priced up is not touched here.** The split says *where* the departure
   lives, not *why* the arm ranked a customer it went on to lose above one it kept. That is the next
   question and it is not a statistic — it is the pricing rule.

## The control, and what it fires on

`site/test_the_baseline_comparison_reaches_the_reader.py::
test_an_out_of_null_estimand_reaches_the_reader_with_WHICH_PAIRS_carry_its_departure` is keyed to the
PROPERTY — *a reader shown an estimand outside its own null is also shown which stratum carries the
departure* — and not to 0.4210, 0.2686 or the word "cross", which is the defect `81127c854` repaired
one quantity along. Every figure it asserts is read from what the two producers composed on its own
fixture, so the day the arm stops pricing its departures up, the control holds and the page's
sentence changes underneath it. Both sides are driven: a feed with the split and a feed without it,
which must render a named refusal rather than silence under an unattributed figure.

Three mutations, three kills, each by the control that should own it:

| mutation | what went red |
|---|---|
| the door stops calling `pairStrataBlock` | the new control **and** `test_NO_cut_ANYWHERE…` ("no decomposition term reached the reader") |
| the amber emphasis applied whenever the stratum exists | the new control's styling leg — the emphasis has to be the cross stratum's own number |
| the producer publishes the strata with no statement of the bound they lack | both — a decomposition term may not reach a reader bare |

## One thing this changed about an existing control, stated because it is a widening

`test_NO_cut_ANYWHERE_in_the_feed_renders_its_number_without_its_OWN_interval` walks the feed for
every block carrying a `concordance` and splits them into **measured** (carries the n it was
computed on) and **hypothetical** (carries the n it would need), failing on anything else. A
stratum is neither: it is a concordance over PAIRS with no sample of its own to permute. So a third
class is named — decomposition — and it carries an obligation rather than an excuse: a term that
reaches the reader must reach them with the sentence saying it has no interval of its own and
naming the figure whose bound it decomposes. A stratum rendered bare and silent fails there exactly
as a leg would, which the third mutation above proves.

`the_two_cuts_the_item_asked_for` is deliberately not carried into the feed: its two rows ARE the
bridge table above it, same concordances and same intervals, and republishing them would give one
figure two homes on one page.

**Suite:** `site/test_the_baseline_comparison_reaches_the_reader.py` — 120 passed, 1 skipped.
