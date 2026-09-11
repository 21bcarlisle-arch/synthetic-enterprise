**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The switching band's own publisher disagrees with it in eight of ten years

**Measured:** 2026-09-07, delivery seat, from the publisher's own release rather than from any
in-repo derivation. **Class:** `figures_on_a_superseded_clock`. Opened by
`SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md`,
which left `gb_domestic_switching_rate` at `cannot_tell`.

## Class registration

Belongs to `figures_on_a_superseded_clock`. Declared rather than left to the title patterns,
because this title names the DISAGREEMENT and the patterns key on the clock — so the backstop
would have routed it nowhere, which is how a family stops growing silently.

## The one-sentence finding

The DESNZ release the artefact's own `provenance_legend` names as the only route to `primary`
**exists, was fetched, and publishes both the numerator and the denominator on one table** — and
its figures fall **outside `gb_domestic_switching_rate`'s band in eight of the ten years**,
including every year from 2020 on. The `cannot_tell` settles as **superseded**. The drawn work was
a stamping exercise; what it found is a refutation.

## The publisher, and what it publishes

**DESNZ Quarterly Energy Prices table 2.7.1, "Transfer statistics in the domestic gas and
electricity markets, Great Britain"**, published on the statistical data set page
`https://www.gov.uk/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics`.
Edition read: **publication date 30/06/2026, data period "New data for January to March 2026",
next update 29/09/2026** — the workbook states all three on its own Cover Sheet, so the edition
token is in the artefact, not only in the page metadata. gov.uk `public_updated_at` agrees:
`2026-06-30T09:30:10+01:00`. Asset `table_271__2_.xlsx`, 119,879 bytes, sha256
`6cd4dee481faf8f71068fa1ca7f86ef9cf049e546336d93c54d35368740c75b4`. Source line on every sheet:
**Ofgem** — which is what the artefact's `published_by` already said the series was.

**THE URL THE ARTEFACT CITED IS DEAD.** `https://www.gov.uk/government/collections/domestic-energy-switching-statistics`
returns **HTTP 404**, both as a page and through the content API. A citation can rot without anyone
touching the value or the citation — the second instance of that shape this week, after the RO
artefact's rolling supplier page.

**AND THERE IS NO "RELEASE FOR EACH YEAR" TO STAMP.** The drawn item asked for the DESNZ release
for each of the ten years. DESNZ does not publish one per year: it publishes **one rolling table**,
revised quarterly, whose Annual sheet carries every year from 2003. So every row's edition is the
same edition, and the legend's `primary` definition — *"the publisher's own release for THIS
year"* — names a thing that does not exist for this publisher. That definition is unreachable by
construction, which is a legend level nothing can ever occupy.

## The numbers, and they are not close

Electricity transfers and total electricity customers are **both columns of the same table**, on the
same basis (Note 4: meter points, not individuals; Note 5: non-domestic filtered out since April
2016; NI excluded). The annual customer figure is the mean of that year's four quarters — 2025's
30,249k is the mean of 29,818 / 30,361 / 30,406 / 30,410 — which is the right denominator
convention for a whole-year rate.

| year | artefact band % | DESNZ transfers (m) | DESNZ customers (m) | published rate % | verdict |
|---|---|---|---|---|---|
| 2016 | 17.0–17.6 | 4.420 | 27.947 | **15.82** | OUTSIDE (below) |
| 2017 | 13.5–14.0 | 5.118 | 28.129 | **18.19** | OUTSIDE (above) |
| 2018 | 19.5–20.0 | 5.402 | 28.336 | **19.06** | OUTSIDE (below) |
| 2019 | 20.7–21.3 | 5.946 | 28.556 | 20.82 | inside |
| 2020 | 22.5–23.0 | 5.811 | 28.749 | **20.21** | OUTSIDE (below) |
| 2021 | 17.9–18.4 | 4.502 | 28.916 | **15.57** | OUTSIDE (below) |
| 2022 | 2.9–4.3 | 0.893 | 29.224 | 3.06 | inside |
| 2023 | 8.9–12.5 | 1.867 | 29.487 | **6.33** | OUTSIDE (below) |
| 2024 | 12.5–16.1 | 2.681 | 29.695 | **9.03** | OUTSIDE (below) |
| 2025 | 14.3–17.9 | 3.146 | 30.249 | **10.40** | OUTSIDE (below) |

**THE VERDICT DOES NOT TURN ON THE DENOMINATOR, AND THAT WAS CHECKED BEFORE IT WAS CLAIMED.** Run
the same numerators against the artefact's own flat 28.0m instead of the publisher's per-year
count and it is still **8 of 10 outside, the same 8 years** (2016 15.79, 2017 18.28, 2018 19.29,
2020 20.75, 2021 16.08, 2023 6.67, 2024 9.57, 2025 11.24). The disagreement is in the numerator
series, not in the divisor.

**NOR ON THE FUEL SCOPE.** The obvious rescue — that the band was silently on both fuels — fails
harder: electricity+gas is **8 of 10 outside** as well (2016 27.79, 2017 32.93, 2018 35.00, 2019
37.71, 2020 35.30, 2021 26.23, 2022 4.99, 2025 18.58), and the two readings are inside on
*different* years (electricity 2019 and 2022; both-fuels 2023 and 2024). No reading of this table
is inside the band more than twice. The band is not a mislabelled fuel scope; it is a different
series.

**The 2017 row is inverted, not merely off.** The artefact holds 3.84m and calls it "market
consolidation" — a fall. The publisher has 5.118m, a **rise of 16% on 2016**. Every narrative note
in the artefact that leans on the 2016→2017 shape is describing a movement that did not happen.

**Two smaller errors found on the way.** (1) `series_source` cites *"DESNZ Quarterly Energy Prices
Table 2.1"*; 2.1 is a prices table and the switching table is **2.7.1**. (2)
`denominator_count_note` claims domestic electricity accounts "sat between 27.5m and 28.3m across
2016-2025". The publisher has them at 27.947m rising to **30.249m** — 2025 is 1.9m outside the
stated band, and the note's claim that a flat 28.0m moves any year by less than 0.4pp is false at
the recent end (2025: 11.24% flat against 10.40% published, 0.84pp).

## What is fixed in this commit, and what deliberately is not

**FIXED.** The artefact can now be asked its own question honestly. `source_check` names the live
publication and the dead one, carries the edition token the workbook states on its face, and
records `found: "superseded"` naming this document — so the ACTIONED leg of
`tools/commons_source_supersession.py` holds it open. `how_to_recheck` now names the exact fetch
(content API `public_updated_at`, then the Annual sheet), not a re-derivation. The false
denominator claim is corrected in place, beside the number it describes.

**NOT FIXED: the band itself, and this is a judgement, not an omission.** Re-siting `rates` onto
the publisher is the repair, and it is not a one-turn edit:

* `simulation/departure_level_anchor.py`'s `YEAR_LEVEL_ANCHOR` is fitted to each band's **HIGH
  endpoint** — the mission brief's anti-flattering tie-break — so the world sits *on the ceiling in
  all ten years* with **0.00pp of room above**. The new figures are 3.5–7.1pp **below** the old
  high endpoint in 2023–2025.
* That reds the containment controls in `tests/architecture/test_switching_rate_commons.py`
  (`test_the_worlds_realised_departure_rate_is_inside_the_published_band`,
  `test_the_whole_book_departure_level_is_inside_the_published_band`,
  `test_every_lane_reading_of_the_switching_rate_is_inside_the_published_band`, and the
  multiplier/callable/unit-derived family), and that suite's own instruction when they fire is
  **re-capture and re-fit — never widen the band**. A re-capture is
  `tools/capture_departure_factors.py` plus `tools/fit_year_level_anchor.py`, not a bounded tick.
* Landing the band alone would therefore put a whole-tree red at HEAD and wedge every lane. **The
  band change and the re-fit are one atom and must land together.**

This is the same disposition the CCL and RO supersessions were given on 2026-09-07, and for the
same stated reason: the detector's job is to make the move enumerable, and a repair with its own
blast radius gets its own pass rather than being smuggled into the commit that found it.

## Where this pass was wrong before it started

**No preregistration was filed, and the drawn premise was mis-shaped.** The item predicted a
provenance upgrade — fetch ten editions, stamp them, move `secondary` → `primary`, band unchanged.
Three of its four assumptions were wrong: there are not ten editions, the values move, and the
move is large enough to break the world's calibration. Recorded here rather than quietly
re-scoped, because the interesting thing is that **a provenance defect and a value defect looked
identical from outside**: the artefact said its citation was weak, and the citation being weak was
why nobody had noticed the values were wrong. `secondary` was doing the work of an alibi.

## What is next

1. **One atom, not two:** re-site `rates` onto DESNZ QEP 2.7.1 (transfers and customers from the
   same table, per-year denominator), re-capture and re-fit `YEAR_LEVEL_ANCHOR`, and move the ten
   rows to `primary` — with the legend's `primary` definition first repaired to name a reachable
   property (*read from a named QEP 2.7.1 edition's Annual row for that year*) instead of a
   per-year release that this publisher does not issue.
2. **Re-ask the band's meaning at the same time.** With a rounded-to-the-nearest-thousand count
   over a published denominator, `band_meaning`'s rounding allowance gives a band ~0.004pp wide.
   A band that tight is honest about *this series* and silent about series disagreement — which is
   the whole content of this finding. Decide what the band is a band *of* before re-deriving it;
   do not let the width fall out of the arithmetic.
3. **Retire the in-repo series as the artefact's source.** `docs/market_research/churn_price_elasticity.md`
   section 1 is refuted as a reading of DESNZ switching statistics. Its downstream elasticity work
   is a separate question and is not touched here.
4. **The ElectraLink `unreconciled_cross_check` is now askable and still unresolved.** Its 3.21m
   changes of supplier in 2024 sits between DESNZ electricity (2.681m) and both fuels (4.773m), and
   its stated 6.34m peak in 2019 is nearest electricity (5.946m) but 6.7% above it. Neither fuel
   reading closes it, so the block stays — but it can now be stated against a publisher rather than
   against a derivation.
