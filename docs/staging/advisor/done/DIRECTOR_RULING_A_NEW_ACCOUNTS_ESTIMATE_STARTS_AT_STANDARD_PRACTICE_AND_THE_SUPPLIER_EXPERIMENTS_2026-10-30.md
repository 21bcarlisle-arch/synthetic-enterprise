**Severity:** BLOCKING · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] A new account's billing estimate starts at today's standard practice, and improving it is the supplier's experiment, not the director's decision (2026-10-30)

**Type:** RULING, through the advisor channel. These are the director's words from chat on Fri 30 Oct. He was answering the open row `a-practitioner-question-k4-published-sources-exhausted`, which asks whether a new account's billing estimate follows the data collector's EAC or the supplier's own reads, and what SPAR is.

- 07:26 GMT: "I think we should start with what ever is standard practice. The billing estimate should be based on the consumption used in the quote shouldn't it? However if the customer got this wrong it will create payment changes and problems and may also create a gap between billing and settlement. Let's start with what happens today. But the idea should be that the supplier figures out ways to improve this."
- 07:26 GMT: "It might quick or validate the quote assumption for example? This might vary by channel? It might account for a new tennant versus the history. It might be transparent about an early review."
- 07:26 GMT: "The pint is that the supplier should start simple and then look to improve customer outcomes both the ability to acquire with a clean quote and good customer satisfaction for new customers and also avoiding bill show etc. So I don't think this should be decided by me. It should be exactly trlhe sort of thing the supplier should experiment with in its runs to try and improve"

## The ruling

1. **Close the row as *returned to the seat*.** The method is a supplier choice, and it is not for the director to make. Do not raise it again as a question.
2. **Baseline: today's standard practice, kept simple.**
   - The billing estimate and the first direct debit come from **the consumption used in the quote**. That figure is the customer's declared use where the channel takes one. Otherwise it is the industry figure available at quote: the registry or DC EAC for electricity, the AQ for gas.
   - Settlement runs separately on the DC's EAC, with the BSC blend and the smoothing parameter carried as a named assumption.
   - The **gap between billing and settlement** is reported as a measured quantity. It is not hidden.
   - Write the K-page entry for this baseline. Mark it as the director's stated understanding of standard practice, and record any primary source you find that refines it.
3. **The world must hold the truth the quote can get wrong.**
   - A declared or quoted figure is a draw with an error distribution against the home's true use. The error depends on channel, on a new tenant compared with an established occupier, and on whether the occupier has history at the address.
   - Without this, there is nothing for the supplier to learn.
4. **Improvement is an experiment in the runs.** Pre-register each variant and grade it against the baseline. Candidate levers, from the director:
   - validate or correct the quote assumption early, from the first actual read, smart data, or a quick check at sign-up;
   - treat channels differently, for example comparison site, direct or broker;
   - treat a new tenant differently from a household with history at the address;
   - an **early review that the customer can see**, at a stated date such as the first read or month three;

   and any other lever the seat proposes.
5. **Outcomes to grade.** Grade each variant on all of these, not only on estimate accuracy:
   - acquisition with a clean quote (conversion, and objections or cancellations in cooling-off);
   - new-customer satisfaction and complaints in the first months;
   - **bill shock** (large catch-up bills or DD step-changes in year one);
   - payment changes and arrears in year one;
   - the billing-to-settlement gap.
6. **The invariant must not encode a method.** Redraw `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` so that it checks the estimate against **the supplier's declared estimation policy for that account**, plus the duty-level rules (SLC 27.15, the read duty, back-billing). It should not check against one method chosen in advance.
   - Re-grade the 179 E1 exceptions under the redrawn row. Those that are policy-consistent are not breaches. The remainder are real defects.
   - This should release the correctness stretch's exit leg that the row was holding open.

## Where this sits

- The baseline and the redrawn invariant belong to the correctness stretch.
- The experiment belongs to the advice and customer-outcomes roadmap. File it there as a named candidate. It is drawn after the correctness exit test is met, unless it is needed to close it.

## Done (2026-10-30, the worker)

1. **Row closed as returned to the seat.** `a-practitioner-question-k4-published-sources-exhausted` is answered in `docs/direction/DIRECTION.yaml`. Its commitment is `new-account-first-months-experiment`, due 2026-12-15.
2. **Baseline written** as the director's stated understanding of standard practice, in §10 of `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md`. No primary source refining it was found. E1's registry branch already is this baseline for the registry half. The declared-use rung is the world gap already named in `annual_consumption_estimate.CUSTOMER_DECLARED`. **Owed, not done:** the billing-to-settlement gap is not yet measured on any book, and §10 carries this as a GAP.
3. **The world's quote error** (item 3) and **the experiment** (items 4–5, with its five outcomes) are filed as `new-account-first-months-experiment` in `docs/direction/priority_order.yaml` `customer_outcomes_candidates`. It is drawn after the correctness exit test.
4. **The row is redrawn** (item 6). `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` grades against the row's `declared_policy`: a quote rung (one annual figure, within 5% of the meter's median) until the reads span 182 days from the supply start, then the reads band. Duty rules stay on `INV_READ_DUTY_ANNUAL` and `INV_BACK_BILLING_12M`. **Re-grade:** 179 of 24,904 became 0 of 30,793 on both the 209c3350ab and 3dc5a92948 books. All 179 are policy-consistent, none remains a defect, and the exception is retired. Both rungs are mutation-proven in the runner's test.
