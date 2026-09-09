**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The page's departure headline is a mean over shoppers judged against a band over everybody

**Measured:** 2026-09-09, delivery seat, while working the Lane 0 switching-band item. **Class:**
`figures_on_a_superseded_clock`. Result document:
`SEAT_RESULT_THE_CORRECTED_RECORD_MAKES_THE_WORLD_LOOK_WORSE_AND_THE_PAGE_WAS_COMPARING_SHOPPERS_TO_EVERYBODY_2026-09-09.md`.

## The one-sentence finding

`site/data/value_arms.json`'s `departure_level` publishes `world_realised_rate_pct` — the world's mean
expected departure at a **renewal decision**, which post-C1b is the households who took a fixed deal
and so demonstrably shop — and judges it against a published band stated over **all domestic
electricity accounts**, while the same module exposes the comparable whole-book reading and calls it
so in its own docstring.

## Why this is BLOCKING and not a tidy

The two quantities do not merely differ in precision; they give different verdicts and different
headlines on a live public page:

| | renewal-decision reading (published) | whole-book reading (comparable) |
|---|---|---|
| mean level | 28.08% | 15.96% |
| vs the refuted band | 1.63x, **0 of 7 inside** | **6 of 8 inside** |
| vs DESNZ QEP 2.7.1 | **1.80x** | **1.14x** |

The page's own statement reads *"Customers leave this world faster than they left the real one, so
every retention, churn and lifetime-value figure below reads LOW by roughly that factor."* On the
comparable quantity that factor is 1.14, not 1.63 — so the discount the page instructs a reader to
apply to every money figure on it is **overstated by about 40%**, in the direction that makes the
company's own results look conservatively stated. It is a published instruction to misread a page.

## The evidence is the producer's own prose

`tools/measure_departure_level.world_book_rate_pct` — the function NOT called by the page:

> *"THIS IS THE COLUMN THE PUBLISHED BAND WAS ALWAYS ABOUT... `world_realised_rate_pct` above is a
> mean over renewal DECISIONS: post-C1b that is the selected subset of households who took a fixed
> deal, i.e. the ones who demonstrably shop, and a mean over shoppers is not the book's departure
> level."*

The instrument's own CLI prints the same warning above the whole-book table and the page never read
it. **Nothing was hidden and nothing was wrong in the module** — the defect is entirely in which of
two correctly-named functions the publisher called, which is why no control caught it: every control
over `departure_level` checks that the page agrees with `world_realised_rate_pct`, and it does.

## What was fixed in this landing and what deliberately was not

**FIXED.** The `denominator` field declared the account denominator and described the renewal
column; it is corrected in place, beside the number it describes, and the comparable whole-book
reading is published alongside with its own verdict. A reader now has both, named.

**NOT FIXED: which one is the headline.** Re-siting `world_pct` moves a published figure from 1.63x
to 1.14x and changes the page's central instruction to its reader. That is a headline move and it
needs a preregistration written before the number is known — not a swap made in the same pass that
discovered it, by a seat that already knows which direction it goes. It also changes the subject of
`tests/architecture/test_switching_rate_commons.py`'s band control, and
`world_book_rate_pct`'s docstring states the reason that must not happen in the repairing commit:
*"moving a control's subject inside the commit that repairs what it measures is how a moved number
becomes unattributable."*

## What is next

1. **Preregister, then re-site.** Write what the page's verdict, its year-by-year in/out counts and
   its stated discount factor will be after the swap, then make it, then check. The numbers are in
   the result document and must be re-derived rather than copied, or the preregistration is a
   transcription.
2. **Ask whether the renewal reading should stay on the page at all.** It is a real quantity about a
   real population — how readily a shopper leaves — and it may be the more interesting one for a
   company whose whole thesis is finding movable customers. If it stays, it needs its own band over
   its own population, which nothing in the commons currently provides. That is a knowledge gap and
   it is filed as one, not guessed at.
3. **Sweep for the same shape.** Every other place in the tree that divides a count by a population
   and compares it to a published rate should be asked which population each side counts. This is the
   fourth instance of this class this fortnight and a census beats a hand pass.
