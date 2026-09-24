# A reference page is scoped out of the one freshness check that is not about its figures

*Filed 2026-09-24 by the delivery seat, from the frozen-feed repair in `site/assets/freshness-banner.js`.*

**Class:** `measurements_that_mirror` — a scope rule written for one subject applied to a second
subject it was never reasoned about.

**Lane:** `H_harness` — where the publish-gate and site-surface findings are filed; there is no
separate site lane.

**Severity:** RECORDED. The live site's figure-bearing pages are covered; this is about the
reference pages beside them.

---

## The finding

`site/assets/freshness-banner.js` now carries a fourth publish sentence, `feedNotArrivingSentence`,
which is the only one that survives the publisher going dark: it measures the feed's `ts_iso`
against the reader's own clock, so a frozen feed cannot suppress it.

It is scoped exactly like the other three — silent when the including page declares
`data-figures="none"`. That scope comes from the 2026-08-24 ruling, recorded in
`site/test_freshness_banner_publish_state.py::test_a_reference_page_carries_no_publishing_status_at_all`:
publishing status on a page carrying no simulation figure is noise that undermines the honest
banners elsewhere.

**The ruling was made about three sentences that are all claims about FIGURES.** "These figures are
21.7h old" is genuinely vacuous on a page with no figures. But "nothing has reached this site for 23
days" is not a claim about figures at all — it is a claim about the channel, and it is exactly as
true, and exactly as useful, on a reference page as anywhere else. A reader looking at a
three-week-old copy of a reference page is looking at a three-week-old page.

So the new sentence inherited a scope whose reasoning does not reach it.

## What was done and why it was not settled

The repair keeps the existing scope. Reversing it is a judgement about what a reference page is
*for* — and the ruling is recorded while this reading of it is one session's — so the code holds the
narrow scope and names the disagreement in a comment beside it rather than quietly widening a rule
the director set.

## The prediction, written before it is tested

If the scope is widened, the sentence fires on reference pages **only** when the site is genuinely
dark past its own cadence — which, on a healthy publisher, is never. The noise the 2026-08-24 ruling
was protecting against does not arrive, because unlike the other three sentences this one has no
healthy-state text at all: it renders `""` or an outage.

That is the falsifiable part. If widening it produces any sentence on a reference page while the
publisher is healthy, this finding is wrong and the existing scope is right for a reason nobody
wrote down.

## How to settle it

One question for the director, costing one line: *should a reference page tell its reader the site
has stopped publishing?* Failing that, widen it, watch one healthy publish cycle, and check no
reference page gained a sentence.

## Reversal

Two lines in `render()` in `site/assets/freshness-banner.js` — the `noFigures` term in the
`notArriving` assignment and in `publishIsDown`. The control that pins the current scope is
`test_a_reference_page_carries_no_publishing_status_at_all`.
