# What the per-method bad-debt figure counts, and what the world produces by method

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `resi-payment-outcome-depends-on-how-the-household-pays` (Lane 0). Follows
`SEAT_FINDING_A_STOPPED_DD_NOW_REACHES_THE_MONEY_SIDE_AND_PUBLISHED_BAD_DEBT_DOES_NOT_MOVE_2026-10-03.md`.

## 1. What the figure counts (traced before anything was run)

`knowledge_map.md` row *Bad debt rates by payment method* says "DD ~1% of bills, standard credit ~6%"
and "bad debt should be 6x higher". Traced to its source:

- `docs/market_research/company_debt_management.md` §5 gives 1%/6% with no source but "(Ofgem
  allowance basis)".
- `docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md` found the primary it
  stands on: **Ofgem, Consultation Appendix 2: Debt-related costs, Dec 2024, Table 2.1 (cap 13a)**.
  DD £25 = **1.4%**, standard credit £121 = **6.5%**, prepayment £10 = **0.6%**. That note already says
  the clean 1%/6% and "6x" are approximate; the primary ratio is about **4.6x**.

So the figure is:

- **A share of revenue, not of bills or of customers.** It is £ of debt-related cost per customer at
  benchmark consumption, over that method's own cap level.
- **A cost allowance, not a loss rate.** Its numerator is bad-debt charge plus the cost of
  collecting it. It is not a write-off rate and not an arrears-incidence rate.
- **Population by method.** It is the average over the customers who pay that way. It includes both
  **selection** (who chooses or is left on standard credit) and **channel** (whether the same
  household would pay worse off DD). It does not separate them. Standard credit also contains the
  households a supplier has already taken off a failing DD. That is the fallen-out-of-DD stock
  Centrica Note 17 provisions at 44.7% under "pay on receipt".

**Nothing we hold publishes the selection/channel split.** No source says how much worse a given
household pays when it moves from DD to standard credit. So the first question for the world is not
"what multiplier does method apply". It is "does the world's book reproduce the population ratio by
method, and if not, which of its mechanisms is missing?"

## 2. How method reaches the world's outcome today (read from the code)

- `household_segments.payment_channel_for_customer` draws channel from
  `Random(f"paychannel_{household}_electricity")`. That stream is independent of the household's
  income-stress trajectory. **There is no selection by stress.**
- `arrears_engine.payment_outcome` uses one `_DD_FAILURE_PROB`/`_ON_TIME_PROB` by stress tier for
  every resi method. **There is no channel effect.** That includes `prepayment`, which can "fail" a
  bill here although a prepayment meter is paid before use.
- The only coupling is fuel poverty. It is drawn at 8.8% for DD, 18.5% for standard credit and 22.3%
  for prepayment, and it scales the failure probability by 1.3. The expected failure multiplier is
  1.026 for DD and 1.056 for standard credit, a ratio of about **1.03**.

## 3. Pre-registration (written before the measurement below)

Measurement: `docs/reports/run_output_latest.json` (13:00, seed 42), `_resolve_bills` over the
issued bills, grouped by the household's DRAWN channel (`payment_method`) and also by PAYING method.
Write-offs from `balance_settlement`, as a share of billed £ per group.

1. **Failed-bill rate, standard credit over DD, by drawn channel: between 0.8 and 1.3.** The
   mechanism gives about 1.03. The band is wide because the standard-credit group is small.
2. **Write-off £ per billed £, standard credit over DD, by drawn channel: between 0.5 and 2.0.** It
   is nowhere near 4.6. If it is above 3, then something I have not read couples method to loss, and
   §2 is wrong.
3. **By PAYING method, standard credit reads higher than by drawn channel.** PB8 L2 moves the
   stopped, stressed households (18% failure on their later bills) onto standard credit. This is
   the one selection mechanism the world has, and it is the supplier's own, not the household's.
4. **Prepayment fails bills at about the DD rate.** That should be zero by construction.

## 4. Results

`/tmp/permethod_probe.py`, one process, at `3b5dbfdc4` (origin/main at draw time). Resi bills with
a positive charge, 175 supply points, write-offs from `balance_settlement`:

| group | supply pts | bills | failed | billed £ | write-off £ | **write-off / billed** |
|---|---|---|---|---|---|---|
| drawn DD | 129 | 6,124 | 6.45% | 516,341 | 15,534 | 3.01% |
| drawn standard credit | 26 | 953 | 7.24% | 67,307 | 785 | 1.17% |
| drawn prepayment | 20 | 907 | 4.63% | 93,954 | 1,605 | 1.71% |
| **paying DD** | 129 | 5,334 | 4.78% | 427,586 | 4,280 | **1.00%** |
| **paying standard credit** | 48 | 1,743 | 11.99% | 156,062 | 12,039 | **7.71%** |
| paying prepayment | 20 | 907 | 4.63% | 93,954 | 1,605 | 1.71% |

| | predicted | measured |
|---|---|---|
| 1. failed rate, SC/DD, drawn | 0.8 to 1.3 | **HELD, 1.12** |
| 2. write-off share, SC/DD, drawn | 0.5 to 2.0 | **REFUTED low, 0.39.** It is the same direction as my reasoning (no coupling), but outside the band. 26 supply points; a few large DD leavers dominate the DD £. I cannot yet say whether it is noise or a mechanism, and one seed cannot say |
| 3. paying SC above drawn SC | higher | **HELD, and much larger than I expected: 7.71% against 1.00%, 7.7x** |
| 4. prepayment fails at about the DD rate | about DD | **HELD, 4.63%.** 907 prepayment bills "fail" and £1,605 is written off on a meter that is paid before use |

## 5. What this means, and the decision

**The item's premise is half right.** For a given household in a given year, the outcome draw is the
same whichever way it pays. That is true. But the population statistic the source publishes is
*by the method customers pay*, and **the world already reproduces it by that method: DD 1.00%,
standard credit 7.71% (source 1.4% and 6.5%, ratio 4.6x; the world gives 7.7x).** It gets there
entirely by selection, and the selection is the supplier's own: PB8 (`dd7bbce0f` and before) stops a
failing DD and moves a stressed household to pay on receipt. That is how a real standard-credit book
fills up. Centrica Note 17's "pay on receipt" bucket is that same fallen-out-of-DD stock.

**Decision: `payment_outcome` does not get a method multiplier.** The sourced figure already
contains selection. The world now has a selection mechanism, and that mechanism alone overshoots
the sourced ratio. A channel multiplier calibrated to "about 6x" on top would count the same effect
twice. Its size would also be a number picked to fill a slot, because nothing we hold separates
channel from selection. The gap stays a named gap (knowledge map row, updated in this commit). It is
not a constant.

**The caveats are what stop this being a calibration claim.** The numerators differ: Ofgem's figure
is bad debt **plus collection cost**, and ours is write-off only. So the world's 7.7x does not show
the world is "too high". It shows the shape is present and the order of magnitude is right. This is
one seed, with 48 paying-SC supply points.

## 6. What this changes downstream (interconnection)

1. **The company cannot see the ratio, because the seam reports the DRAWN channel.**
   `SimInterface.get_payment_method` still answers with the household's trait, not the
   paying method after a stop. So `company/pricing/default_belief.py` learns per-method cells over
   the drawn split (here SC/DD write-off 0.39x), not the 7.7x a real supplier would see in its own
   mandate records. A real supplier knows it cancelled a DD. This was already item 1 of the PB8 L2
   finding's "not done", and it is now the item that lets the company see the per-method shape that
   the world produces. Handed off as `the-seam-reports-the-paying-method-after-a-supplier-dd-stop`.

   **Correction, 2026-10-03 (the hand-off's own seat).** Two parts of this item were wrong. First,
   the seam half was already on origin when the hand-off was drawn, as `065ac54eb`
   (`get_payment_method(..., as_of=)`, read by the renewal price). Second, `default_belief` does not
   learn per-method CELLS: the belief is keyed on arrears state only, by the 2026-09-23 ruling.
   Method reaches it in one place, which published provision row a charge is read on. So "the
   company learns 0.39x where it should see 7.7x" overstated the case. The real defect is narrower.
   `run_phase2b._book_method_of` asked the seam once per account with no date, so a stopped DD's
   debt stayed on the DD live row, and the `method|*` rows of `tabulate` showed the drawn split.
   Fixed: the register is now asked `(account, date)`. Each provision is read on the method held on
   its own date, and the year's covariate is the method at its start.
   Control: `test_a_dd_the_supplier_stopped_is_provisioned_on_the_pay_on_receipt_row_from_its_notice_on`.
   Mutation: reading the year-end provision on the start-of-year method reds it.
   **Not measured:** how far this moves the own-book rate on a run. I cannot yet say. The
   own-book policy is a switch that is off by default, so the default run does not move.
2. **A prepayment bill can fail.** `payment_outcome` puts prepayment on the resi credit draw. A
   prepayment customer is not sent a bill to pay; it vends. 907 bills, £1,605 written off. This is an
   absurdity of class, not of calibration. Handed off as
   `a-prepayment-meter-bill-cannot-fail-like-a-credit-bill`.
3. The knowledge-map row's "Key gap" asked whether any sim customers are on standard credit, and if
   so whether bad debt is 6x higher. **Both are answered**, and the row now says so.
