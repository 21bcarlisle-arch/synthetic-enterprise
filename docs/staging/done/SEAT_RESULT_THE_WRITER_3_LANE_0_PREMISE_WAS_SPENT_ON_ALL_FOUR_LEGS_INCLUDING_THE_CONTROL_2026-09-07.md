**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `writer-3-prices-no-gas-renewal-and-the-fix-is-one-line`) · **Class:** uncommitted_and_orphaned_work

# RESULT — the writer-3 Lane 0 premise was spent on all four legs, including the control

The Lane 0 draw of 2026-09-07 asked for the `_billing_account_id` repair at
`company/crm/customer_profitability.py:156`, the one-variable A/B pair after it, and the
pre-registered prediction graded beside it. **Every leg had already landed.** The doorbell's own
premise check flagged this — it cited `40fe58f85` as already an ancestor of `origin/main` — and the
re-measurement below confirms it and extends it to three things the doorbell did not check.

Measured at HEAD `38e22f470`. Nothing was rebuilt; this is a re-measurement, not a redo.

## The four legs

| leg | state | evidence |
|---|---|---|
| the id repair | **LANDED** | `28ba48dd4`, `company/crm/customer_profitability.py:240` reads `_billing_account_id(r.get("customer_id") or "") == cid` |
| the A/B pair | **RUN** | `SEAT_RESULT_WRITER_3_NOW_FIRES_51_TIMES_AND_EVERY_POUND_OF_IT_IS_TRANSFER_2026-09-07.md` — 0 → 51 firings (5 elec / 46 gas) against an unmoved 1,878 decomposed renewals |
| the prediction | **GRADED** | same doc §"Grading the prediction, beside the claim" — confirmed on four legs of five, with the wrong leg kept beside the result rather than revised |
| the class control | **LANDED** | `tests/company/pricing/test_value_arm_in_the_renewal_chain.py:712`, over the same `_WORLD_LEG_ID` map the finding asked for |

The fourth row is the one worth recording, because the finding that opened this
(`SEAT_FINDING_THE_SAME_ID_MISMATCH_IS_LIVE_AT_WRITER_3...`, §"The control that would have caught
it") explicitly said writer 3 had **no** equivalent of the value arm's control and that *"the fix
should bring one"*. It did. Re-run here rather than read:

```
$ pytest tests/company/pricing/test_value_arm_in_the_renewal_chain.py -k reach_its_own_book \
         tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py -q
1 passed, 31 deselected
```

The control also carries its own vacuity leg — `len({_WORLD_LEG_ID[c]("C1") …}) > 1`, refusing to
pass on a book where every commodity is filed under the billing account itself — which is the leg
that stops it becoming a control that cannot fail once the ids happen to agree.

## The named residue was also closed

The result doc's "What is next" listed three items. Two are done and the third is not what it said:

1. **`profitability_uplift_log` never reaches the saved payload.** **CLOSED** —
   `saas/reporting/annual_report.py:1228` carries it through the reduction at HEAD, with
   `tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`
   as the control. That test's own docstring records that the AST census written for it found
   **three** dropped logs where one was being chased — the write-the-guard-first shape paying out.
2. **`NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` has no sourced origin.** **CLOSED as far as it can
   be** — it now carries a ~40-line origin block that separates what the published record settles
   (the PERMISSION, off the consolidated supply licence: SLC 27.2A, 7.4, 0.3) from what it does not
   (the MAGNITUDE, marked `UNSOURCED`), and labels itself a COMPANY BELIEF rather than a bare 5.0.
   That is the honest-`None`-with-a-named-reason treatment, applied to a number that had to keep a
   value because 51 live repricings depend on it.
3. **"Settle the definition" — two writers, one question, two populations, two thresholds.** OPEN,
   and it is a pricing-policy question for the director, already filed as
   `SEAT_FINDING_THE_NET_NEGATIVE_SURCHARGE_IS_FLAT_IN_POUNDS_AND_SO_VARIES_5_7X_IN_WHAT_IT_CHARGES_2026-09-07.md`.
   Not seat work, and not this draw's.

## What I did instead

Released the claim and took the Lane 3 draw in the same tick — EP8's Q4, the last open question
behind that atom. See `docs/design/EP8_ESTIMATION_CUT_DISCOVER_2026-09-07.md` and the finding it
filed out.

## The thing worth keeping

**The doorbell's premise check fired correctly and was still not sufficient.** It checks whether
cited commit ids are ancestors — which caught the arm's fix — but the draw's *own* deliverables
(the line, the A/B, the grading, the control) had each landed under commits the item never cited, so
nothing in the check could see them. The cheap general move is the one this tick used: before doing
drawn work, `grep` for the deliverable's own spelling at HEAD. Four greps, no run, and it separates
"the premise is spent" from "the work is done" — which are different claims, and only the second one
was true here.
