**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The catch-up VAT rows are in the 16 Nov book, but the book is not published (2026-11-16)

*Delivery seat executor, drawn on `catchup-vat-rows-on-the-16-nov-page`.*

## Premise, re-measured at draw

- f0bca8e35 is on origin, as the draw said. The **published** page file is still the 11 Nov book
  (`publish_provenance.json` last_verified 6fe7827ab2). The 16 Nov book (git=8a300fa561) is paused
  since 04:26Z on four domain-invariant breaches (INV_OVERDUE_WITHIN_BALANCE 4,
  INV_OVERDUE_WITHIN_PAGE_BALANCE 7, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 2,
  INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5). Origin's C5-INV113 carries no
  `catchup_lines_by_rate`, `catchup_corrects_invoices` or `catchup_vat_gbp`.
- The shared tree's dirty `site/data/customers/C5.json` (written 08:26Z) is that unpublished export.
  It is not this seat's to land: publishing it would put an unverified figure on the site.

## What the 16 Nov book carries (measured, not published)

C5-INV113 in the 16 Nov export: `catchup_lines_by_rate` = 20% −157.51/−31.50 and 5% +112.49/+5.62,
`catchup_corrects_invoices` = [C5-INV112], `catchup_vat_gbp` −25.88. All three match the predicted values exactly.
Rendered through `site/explore/_bill_render_harness.mjs` against `site/explore/index.html`:

    + Catch-up adjustment (… VAT at 20% (-£31.50); corrects C5-INV112) | -£157.51
    + Catch-up adjustment (… VAT at 5% (£5.62); corrects C5-INV112)    | £112.49
    + VAT | £5.86 on this month + -£25.88 on the catch-up = -£20.02
    = Total | £52.19

So the method works end to end on a real book. What cannot be claimed is "done on the rendered
page": no published page file carries these fields yet.

## What landed

Before this change, the door test **overwrote** the record's fields with the pinned ones, so a book that
carried wrong lines would still pass. Now it asserts that any field the book carries equals the
pinned value, and injects the value only where the field is absent. A mutation (a book carrying a single 20% line of
−45.02) reds `…one_row_per_vat_rate…`. All six tests pass against the 11 Nov file and the 16 Nov
export. The one-rate test injects hypothetical lines and is marked `hypothetical=True`, so it stays
green when the real lines are published.

## What remains

Once a verified publish carries C5-INV113's lines, delete the injection, so the test reads only the
committed page file. That depends on the publish pause, not on this work.
