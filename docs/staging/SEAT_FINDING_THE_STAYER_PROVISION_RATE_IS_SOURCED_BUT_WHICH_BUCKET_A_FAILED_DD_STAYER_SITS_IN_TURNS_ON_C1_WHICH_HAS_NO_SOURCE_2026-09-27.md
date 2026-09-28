**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Evidence:** `docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md`

# The stayer provision rate is sourced, but which bucket a failed-DD stayer sits in turns on C1, and C1 has no source

**2026-09-27.** This is the knowledge pass on C1 and C6 of
`SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md`, done before
anything is wired. The evidence note carries the sources. This file carries what they mean for the
design. **Leg 4b is not wired, and the reason is below.**

## C1: `_DD_FAILURE_PROB` (3 / 12 / 35%) is a GAP

- **Origin.** Minted without a source in Phase MW (`c1e3e5105`, 2026-07-02) as
  `simulation/payment_timing._DD_FAILURE_PROBABILITY`, with the comment *"per payment event"*.
  Copied verbatim into `tools/generate_billing_ledger.py` in Phase PP (`dc05cdea8`), and into
  `simulation/arrears_engine._DD_FAILURE_PROB` in Phase QD (`a1c7b4b50`). Neither commit cites
  anything.
- **So by its author's own word it is a per-presentation rate.** Nothing downstream treats it as
  one: there is no re-presentation, so every first-attempt failure is terminal.
- **What the published record has:**
  - no DD return rate for energy, and none economy-wide that could be fetched;
  - Bacs 2023 "Unpaid debits" (114.6m of 4.83bn DD items) sits in a payment-PURPOSE list, so it is
    not a return rate and is not used here;
  - no source segments DD failure by any "income stress" tier. That segmentation is ours alone.
- **What is missing:** a first-presentation ARUDD return rate for domestic energy DDs, and the cure
  rate on re-presentation (C2b).
- **What a practitioner would know:** a supplier's collections team tracks first-bounce and
  net-of-retry unpaid as two separate numbers, and scores propensity-to-pay continuously rather
  than in three tiers. Both numbers are proprietary. The director is the route to a "which of the
  two does 35% look like" judgement. No published search will find one.

## C6: the rates are SOURCED, for one supplier and two years

Centrica plc ARA 2025, Note 17, p.175 (checked against the PDF by the seat). This is UK residential
energy only, with Ireland excluded. **Rate = provision ÷ gross billed receivables at 31 Dec, by days
beyond invoice date.** It is a year-end stock ratio, not an annual charge.

| Bucket | <30d | 30–90d | >90d | all ages |
|---|---|---|---|---|
| Direct debit (live) | 0% / 0% | 1.4% / 0% | **7.4% / 4.4%** | 2.8% / 1.7% |
| Payment on receipt of bill (live) | 4.5% / 4.5% | 15.1% / 14.3% | **50.3% / 54.6%** | 44.7% / 47.6% |
| Final bills (closed) | 31.6% / 36.8% | 57.6% / 63.6% | 87.8% / 89.6% | 84.0% / 85.6% |

*2025 / 2024.*

Same page: *"Receivables are generally written off only once a period of time has elapsed since
the final bill."* That is independent support for the design's leg 3.

What is **not** sourced:

- any year before 2024;
- any supplier but one;
- an age band beyond ">90 days". The design's <12m / >12m split does not exist in this table, and
  Energy UK's Fig. 5 still has no definition (its footnote reads *"Energy UK's analysis."*).

`company_debt_management.md` §7's "indicative" matrix puts DD provision at 15–25% at 91–180 days.
Centrica's DD rate for ALL ages past 90 days is 4.4–7.4%. **The matrix is unsupported and is now
marked so.**

## Why leg 4b is not wired: the bucket is the constant, and C1 decides the bucket

Under the balance rule, a stayer's open failed bill is a live balance, mostly older than 90 days by
run end. The live rates for that age differ about **tenfold by bucket**: 4.4–7.4% (DD) against
50.3–54.6% (pay on receipt). Which bucket applies depends on what a sim "failure" is:

- **If 35% is net of re-presentation** (the DD failed and its retries failed too), British Gas
  *stops the DD after a second failure* (C2, sourced). The account is then a pay-on-receipt account
  carrying arrears. **Bucket: pay-on-receipt, ~50–55%.**
- **If 35% is per presentation** (its author's word), most such failures cure on re-presentation,
  and the survivors are a smaller balance whose bucket still depends on whether the retry failed.
  Neither the cure rate (C2b) nor the balance is known.

Wiring either bucket is choosing the answer. This is the picked number the item forbids, one level
up: a sourced rate applied through an unsourced mapping.

## What each bucket would do to the selection figure: arithmetic, not a run

This is filed BEFORE any wiring, as the prediction for whoever wires leg 4b.

From `/var/tmp/se-two-state-diff-rerun/account_diff.json`:

- the selection is value arm minus level arm;
- it reads **−£4,238.56** in the state where `PROS-2016-0098` stays;
- it reads **+£1,105.54** where it leaves (the level arm writes off £6,766.59 and recovers £1,416.85).

A stayer provision at rate *p* on that account's stayer-fate open balance *B* lowers the level arm
in the stay state by *p·B*. **The single-account term flips the stay-state sign when p·B > £4,238.56.**
If *B* equals the leaver-fate failed total, £6,766.59, that is **p > 62.6%**.

| Bucket | *p* | Stay-state selection, single-account term only |
|---|---|---|
| DD live >90d | 4.4–7.4% | −£3,941 to −£3,738: sign holds |
| pay-on-receipt live >90d | 50.3–54.6% | −£835 to −£544: sign holds, within ~£550–£850 of flipping |
| final bills >90d (closed, not a stayer's) | 87.8–89.6% | would flip; excluded by definition |

**Three caveats, each able to move this:**

1. *B* in the stay fate is not measured. The account is billed for longer there, so *B* is probably
   larger, which lowers the crossover *p*.
2. Leg 4b applies to every stayer in BOTH arms, and the arms' other open stayer balances are not
   split out. The £37,109.27 stayer total is one book, not a difference of two.
3. The rates are 2024–25. The account's debt is 2016-onward.

**I cannot yet say whether the published sign survives leg 4b.** Under the DD bucket it plainly
does. Under the pay-on-receipt bucket it is within one caveat of flipping.

## What moves this

1. **The director, as practitioner:** *"In our books, is a failed DD bill what is left after the
   retries, so the customer is off DD and on pay-on-receipt, or is it a first bounce?"*
   **Recommendation: treat it as net-of-retry**, because the sim has no cure. That makes the bucket
   pay-on-receipt >90d, 50.3% (2025, the conservative end), labelled "Centrica 2025, one supplier,
   applied to all years". Wire it one-variable against `6ba548633`. The sign is to be read with
   caveat 1 measured, not assumed.
2. **Measure *B*** (the stay-fate open balance of `PROS-2016-0098`) and the per-arm stayer open
   balances from the two-seed artefact. That turns the table above from a bracket into a figure
   without choosing anything.
3. **A second supplier's table.** Octopus's FY2025 accounts are a scanned image (no OCR here);
   E.ON UK and EDF Energy Customers Ltd filings are unread.

## How to reverse

Documents only. Nothing in `simulation/` changed.

## 2026-09-28: leg 4b is wired, with the bucket as a parameter and no default

`fcba478b7` adds:

- `LIVE_ARREARS_PROVISION_RATES`: both Centrica 2025 rows, cited;
- `stayer_provision_charges`: a 31-Dec stock on stayers' open failed-DD balances, net of
  credits, charged as its yearly change; leavers excluded; barred items released;
- `SIM_STAYER_FAILED_DD_BUCKET`: unset means off, and an unknown value is refused, naming C1.

Nothing picks a row. The bracket that says whether the choice matters is
`records/SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md`. The practitioner
question went to the director at 03:03Z (NTFY `N8U7crm2DRQP`), recommending net-of-retry. C1
itself stays a GAP.
