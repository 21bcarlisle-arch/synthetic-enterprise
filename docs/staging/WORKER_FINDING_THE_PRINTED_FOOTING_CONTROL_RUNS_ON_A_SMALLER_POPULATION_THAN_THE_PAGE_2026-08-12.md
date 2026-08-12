# WORKER FINDING — the printed-footing control runs on a smaller population than the page

**Found:** 2026-08-12, worker tick, while building D36_bill_render_footing_and_pence.
**Class:** R15 WRONG POPULATION (the control is real, fires correctly, and never meets the defect).
**Rank requested:** backlog — a penny per bill on 30 of 1682 bills, no publish-path wedge, no
figure on a public surface known to be affected. It is filed because the SHAPE is the expensive
part, not the pennies.

## Observed, with evidence

`PRINTED_BILL_FOOTS_EXACTLY` (`company/compliance/domain_invariants.py`,
`check_printed_bill_foots_exactly`) is a zero-tolerance control: a rendered invoice's printed line
items must sum EXACTLY to its printed total. It is enforced against
`site/state/billing_ledger.json`.

    site/state/billing_ledger.json   18 accounts   1557 invoices   0 not footing
    site/data/customers/*.json       21 accounts   1682 invoices  30 not footing

The page a reader actually opens — `site/customers/index.html` — renders the SECOND file, per
account. The three accounts in the difference are the re-acquired accounts `C1_2`, `C2_2`, `C5_2`,
and 30 of their invoice records are a penny out:

    C2_2  17 invoices
    C5_2  13 invoices
    C1_2   0 invoices

    C2_2-INV248:  19.36 + 0.27 + 3.81 + 1.17 = 24.61,  declared total 24.62
    C5_2-INV733: components sum to 936.88,             declared total 936.87

(observed-with-evidence: both numbers read directly from `site/data/customers/*.json` and
`site/state/billing_ledger.json` on the working tree at f8225fb23, summed in `Decimal`, not float.)

The residual is one penny in both directions, which is the signature of components and total being
rounded independently from full-precision floats — the exact defect
`PRINTED_BILL_FOOTS_EXACTLY` was written for, and which it eliminated from the ledger population
(0/1557). It survives in the population the control does not read.

## Why the control could never have caught this

Nothing here is a bug in the checker. The checker's subject is the ledger artefact; the page's
subject is a different artefact produced for a wider account set. Neither side is wrong on its own
terms, and the gap is invisible from either: the ledger is perfectly clean, and the page has no
control at all. This is the wrong-population shape from the R15 catalogue — the population under
test excludes exactly the sub-population where the defect lives — and it is worth more than the
30 pennies because the same split (a control reading `site/state/`, a surface reading
`site/data/`) exists elsewhere in the publish path.

## What D36 did about it (and deliberately did not)

D36 is render-layer only by the ruling's own terms, so this was queued rather than fixed on sight
(SELF-INTERRUPT DISCIPLINE). Its footing test is split so neither half hides the other:

* `test_the_renderer_introduces_no_residual_of_its_own` — WHOLE 1682-bill population, zero
  tolerance: the gap between the printed column and the printed total is EXACTLY the gap already
  in the record. The render layer provably adds nothing, including on these 30.
* `test_the_printed_column_adds_up_on_every_bill_whose_record_foots` — the customer's own test,
  exact, on every record that can pass it, with a floor at 90% of the population so this exemption
  cannot quietly grow into a hole.

So the 30 are *visible and bounded* in the test suite, not suppressed.

## The fix this is asking for (recommendation, not a question)

Two candidates, and the recommendation is the second:

1. **Extend `PRINTED_BILL_FOOTS_EXACTLY`'s enforcement to `site/data/customers/*.json`.** Cheap,
   and it would turn the 30 red immediately — but it makes the control's population a list of
   paths someone has to remember to extend again next time.
2. **Fix it at the generator and give the control a population RULE rather than a path.**
   `tools/generate_invoice_data.py` writes the per-customer files; the same penny-quantisation
   discipline `tools/generate_billing_ledger.py` already applies (quantise the components, derive
   the total from the quantised components — never round both independently) belongs there. Then
   state the control's subject as "every artefact on the publish path that carries printed invoice
   line items", enumerated from the publish manifest rather than hard-coded, so a third invoice
   artefact cannot appear outside it. R10: the class fails automatically, not the instance.

Recommended: (2), sized S–M, no epistemic-wall implications (both artefacts are already
company-side published outputs). Suggested atom: `D_printed_footing_population` in
`D_billing_metering`, coupling with `D_money_boundary_reconciliation`.

## R15 obligation on whatever fix lands

A mutation that re-introduces independent rounding in the generator must kill a NAMED test, and
the test must run on the WIDER population — proving it on the ledger population only would
reproduce this finding exactly.
