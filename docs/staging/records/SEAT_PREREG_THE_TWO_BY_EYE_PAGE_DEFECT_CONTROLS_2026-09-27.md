**Severity:** RECORD · **Lane:** H_harness · pre-registration, filed before either control was run

# Pre-registration: the two by-eye page-defect controls (nav orphan, chart stamp vintage)

Filed 2026-09-27 for DIRECTION item `the-two-by-eye-page-defects-get-deterministic-controls`,
before the widened register or the new door had been executed once.

## What already existed, read before building

- `site/ia_register.py` grades AREAS: the root plus each top-level directory carrying an
  `index.html`. `brand/exemplar.html` is not an area, so the register could never see it.
- `tools/site_reachability.py` grades every `*.html` from the front door, but excuses the brand
  pages, `404.html` and `snapshots/` through its OWN hand-typed `STRUCTURAL_EXCLUSIONS` and a
  `snapshots/` prefix — a second list of "allowed orphans" outside the register, whose snapshot
  reason still names `/now/`, a door deleted on 2026-08-20.
- `tests/tools/test_site_freshness_stamps.py` compares FEED stamps, and only the header against
  the NEWEST datum (`max`), so one stale chart beside a current one is invisible to it, and it
  never reads what the page renders.

## Design

1. **Page-level orphan register.** `ia_register.PAGE_ORPHAN_DEBT`: every published `*.html` with
   no route in from the front door (whose nav is the register's render) must be an entry with a
   reason; shrink-only in both directions (an entry that is now routed, or names no file, is a
   violation). Folded into `register_violations()`, so `test_the_register_is_green_at_head`
   carries it. `site_reachability.STRUCTURAL_EXCLUSIONS` becomes DERIVED from it — one list.
2. **Chart-stamp door** `site/test_a_chart_stamp_is_never_older_than_its_page.py`: every published
   door is driven by its own JavaScript over the published (index) bytes; the rendered page data
   date (`Data: <date>` in a `.stamp` badge) and every chart caption date (`as of <date>` in a
   `.chart-src`) are read from the RENDERED HTML; any chart stamp whose month is older than the
   page's data month fails. A page rendering chart captions but no page date, or a caption with
   no date, fails closed.

## Predictions

- **P1** the widened register finds exactly 4 unrouted published pages at HEAD: `404.html`,
  `brand/exemplar.html`, `brand/proof.html`, `snapshots/DASHBOARD_20260623_120151.html`. With the
  debt recorded it is green.
- **P2** the door's population today is exactly ONE page (`/knowledge/electricity-wholesale/`),
  with 4 chart stamps (`2025-06-07`) under a page date of `2025-06`, and 0 disagreements.
- **P3** each control reds on its mutation: deleting one debt entry; backdating one chart's
  `as_of` by a year in the published feed. And the door does NOT red on a chart stamp in the same
  month as the page (day-level difference) — the anti-always-red arm.
