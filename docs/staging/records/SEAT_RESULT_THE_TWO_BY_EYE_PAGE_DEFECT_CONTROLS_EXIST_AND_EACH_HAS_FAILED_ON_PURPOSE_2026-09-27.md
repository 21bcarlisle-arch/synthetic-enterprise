**Severity:** RECORD · **Lane:** H_harness · result, graded against `SEAT_PREREG_THE_TWO_BY_EYE_PAGE_DEFECT_CONTROLS_2026-09-27.md`

# Result: both by-eye page defects now have deterministic controls, each seen to fail

DIRECTION item `the-two-by-eye-page-defects-get-deterministic-controls`. No model was used.

## What landed

1. **Nav orphan, page level.** `site/ia_register.py` gains `PAGE_ORPHAN_DEBT`, `unrouted_pages()`
   and `page_orphan_violations()`, folded into `register_violations()`. Every published `*.html`
   that nothing reachable from the front door links to must be recorded with its reason;
   shrink-only both ways. `site/brand/exemplar.html` and `site/brand/proof.html` are CAUGHT and recorded as
   deliberate debt, each naming what clears it (move out of the published tree, with
   `tests/tools/test_brand_compliance.py` repointed). `tools/site_reachability.py` now DERIVES its
   exclusions from that dict — its own hand-typed list and a `snapshots/` prefix whose reason
   named `/now/` (deleted 2026-08-20) are gone.
2. **Chart stamp vintage.** `site/test_a_chart_stamp_is_never_older_than_its_page.py` drives every
   published door with its own JavaScript over the index bytes and fails when any chart's
   rendered `as of` month is older than the page's rendered `Data:` month.

## Predictions graded

- **P1 CONFIRMED.** Exactly 4 unrouted published pages: `site/404.html`, both brand files, the June
  snapshot.
- **P2 CONFIRMED.** Population is one door (`/knowledge/electricity-wholesale/`), 4 stamps
  `2025-06-07` under `Data: 2025-06`, 0 disagreements.
- **P3 CONFIRMED, with one correction.** Every named mutation reds. Mutating the production code
  too: removing the fold into `register_violations` reds 4 tests; hiding the brand files from the
  walk reds 4; making the page date unreadable reds 4. **One mutant survived at first**: comparing
  the chart's month against the page's YEAR passed every test, because every fixture differed by
  a year. That was a missing test, not an equivalence — a chart one month behind is inside the
  rule — and `test_MUTATION_a_chart_one_month_behind_its_page_fires` now kills it.

## Not predicted

- The first draft treated every `chart-src` caption as a stamp and went red on
  `/knowledge/weather-cells/`, whose caption is a legend ("Solid: one shared partition…") that
  claims no vintage. The subject is now captions that say `as of`; one that says `as of` with no
  readable date still fails closed.

## Limit, stated

The door keys to the page's own vocabulary (`.stamp` "Data:", `.chart-src` "as of"). A chart
captioned in other words is outside the subject; the population floor stops that from silently
becoming nothing, but a SECOND page with new vocabulary would not be graded until it is added.
