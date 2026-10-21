**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `grade-the-read-instruction-arms-at-both-access-ends` (Lane 0 delivery)
**Knowledge:** read-access-and-theft-duties

# The read instruction performs SLC 21B.4 and, at no access, moves no money. Flip it on in the standing policy, but only in the same change that charges the visit

Graded 2026-10-21 from three run outputs at 8927e9345. The arms are `off`, `register` and
`ceiling`, from `tools/read_instruction_arms.py`. The grade sits under `## Graded` in
`docs/staging/records/WORKER_PREREG_THE_READ_INSTRUCTION_ON_A_PUBLISHED_RUN_AT_BOTH_ACCESS_ENDS_2026-10-18.md`.
Five of the seven predictions are confirmed.
- Prediction 1 is refuted by the book change, as the item expected.
- Prediction 4 is refuted high: the ratio is 0.944 against a predicted 0.40–0.65.

## What each count counts

- **Instruction:** a bill carrying `read_instruction_raised`, one for each visit the company asks
  for at the 11th estimate in a row. Counted per supply point and per fuel.
- **Duty row:** a `read_duty_register` row with `duty_applies`. It marks a credit supply point that
  has gone 12 months without a read, which is the licence breach.
- **Open closing undercharge new demand:** the instrument's money on closing accounts whose last
  run of estimates under-billed. It is counted at the last bill, and counts only demand the
  customer has not yet been asked for.

## What the run says

| | off | register (no access) | ceiling (every visit reads) |
|---|---|---|---|
| instructions | 0 | 582 | 582 |
| duty rows (12 months unread, credit) | 435 | 435 | **0** |
| open closing undercharge new demand | £4,344.29 | £4,344.29 | £4,101.50 |
| of which on runs that crossed the year | £341.67 | £341.67 | **£0** (no run crosses) |
| 21BA bar on crossed undercharge runs | £412.80 | £412.80 | **£0** |
| credit catch-up write-off on 12+ runs | £388.47 | £388.47 | **£0** |
| prepayment write-off on 12+ runs | £250.15 | £250.15 | £250.15 |

- **At no access, the only change is the record.** Every key of the run output is equal once the
  `read_instruction_*` keys and stamps are set aside. While
  `q6_read_visit_access_failure_rate` is null, this is the honest world. The company gains a dated
  record that it took the 21B.4 step on 582 occasions. It does not gain a penny.
- **At the read end, the duty is fully discharged.** No credit run reaches 12 months, so the duty
  rows go to 0 and so does the bar. The money moved is small:
  - £242.79 of undercharge is recovered inside the year.
  - £388.47 of write-off is avoided.
  - Both are transfers from customers to the company, not value created (M2).
- **The stock the instruction could reach is small on this book.** 92% of the open undercharge sits
  on runs that close before an 11th estimate. C7 drove the 17 Oct figures. It is now billed on
  actuals throughout (42/42 bills, leg (d), 80e30f67a). So the "C7 billed 23% of its true use"
  premise in the item is spent. The instruction did not fix it; the TDCV repair did.

## What the run does not charge

The run instructs 582 visits and charges for none of them. The knowledge page prices a visit, so
the zero is known to be wrong (K2):
- an appointment visit: **£17.50**
- an area round: **£3**

Both figures are from `docs/market_research/read_access_and_theft_duties.md` §2.1, meter operators
to DECC, 2015 costs.

Over the ten years, the bound is 582 × £3 = **£1,746** to 582 × £17.50 = **£10,185**. At the read
end, that is several times the £631 the visits move. Read the instruction as a compliance cost,
not a margin lever.

## Recommendation

**Yes: the standing policy should instruct reads.**
- SLC 21B.4 is a licence duty. Billing accuracy comes first in the director's order.
- Today the standing company has 435 register rows where the 12-month duty applies, and it acts on none of them.

**But the flip of `instruct_reads_in_billing_run` should be its own item, and it should land
together with the visit cost.**
- Charge each instruction at the area-round £3 as the central figure, with £17.50 as the stated
  upper bound. It goes in opex as a cost of compliance.
- Flipping without the cost publishes a duty performed for free. That is the invented zero K2
  forbids.
- Which visit type a supplier uses at the 11th estimate is the §2.6 GAP ("the chase before the
  year"). The cost choice should name that gap rather than hide it.

**Digests the flip moves.**
- **No world-identity part moves.** These four digests are equal across all three arms, because
  they digest world draws and the switch is company policy:
  - level `cdba75ebb9197b33`
  - homes `35f8efe8ff02f245`
  - demand `ccd2340d48f669cc`
  - payment methods `86560148d7db82b7`
- **Without the cost line,** the published run output gains only the `read_instruction_*` keys, and
  no value arm needs re-taking.
- **With the cost line,** opex and net margin move by £1.7k–£10.2k over ten years. Every value arm
  graded against a published run's margin must then be re-taken at the new commit. The flip item
  should list those arms, from `tests/tools/test_generate_value_arms_data.py`, before it lands.

## Not established

- Where the truth lies between the two ends. That turns on `q6_read_visit_access_failure_rate`,
  which is still a GAP and a question for a practitioner.
- Why the re-run raises 582 instructions where the decomposition counts 469.
- Why 113 no-access visits record outcome `actual` while the money is identical.
- `dd_book_reproduced` is false on this book. On 17 Oct it was true. The no-access bar figure
  rests on a DD book the instrument could not rebuild.
