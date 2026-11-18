**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# An Economy 7 fix that rolls to SVT mid-period is charged more than every kWh at its highest rate (2026-11-18)

**Where it came from.** This is the one post-publish reader red on publish 6af7fd0bf
(`docs/observability/.post_publish_reader_reds.json`):
`tests/tools/test_the_validator_checks_the_printed_rate_against_the_contracted_tariff.py::test_the_published_book_charges_its_contracted_tariff`.
I re-ran it on this box at 2026-11-18 and got the same red. 3 bills disagree.

**What is measured.** Each disagreeing bill is the period in which an E7 fixed term (Day and Night
rates) ends and a single-rate SVT begins. The bill does not print the band split, so the validator
can only give a range: every kWh at the lowest rate up to every kWh at the highest. Each bill is
charged ABOVE that ceiling. "Charged" means energy + network and policy + EPG, which is what
`tools/bill_validation_comparison.py` sets against the contracted rate.

| account | period | validator range £ | charged £ | energy line £ | network and policy line £ |
|---|---|---|---|---|---|
| PROS-2016-0253 | 2017-09 (fix to 2017-09-08) | 61.28..147.35 | 164.63 | 110.73 | 53.90 |
| PROS-2017-0286 | 2018-09 (fix to 2018-09-14) | 34.66..80.46 | 81.23 | 53.76 | 27.47 |
| PROS-2021-0313 | 2022-09 (fix to 2022-09-02) | 54.02..137.03 | 153.38 | 114.08 | 39.30 |

On these three bills, the energy, standing charge, VAT and total lines each agree with the bill's
own printed rate. So the bill is arithmetically consistent with itself; the open question is
whether it is consistent with the tariff the customer was sold.

**Second, separate claim on the same bill.** For PROS-2021-0313, `default_tariff_rate_within_cap`
DISAGREES. The SVT term rate is 25.4557 p/kWh against a published level of 25.41 p/kWh, ex-VAT.

**Not established.**

- Whether the excess comes from the network-and-policy line being added on top of an energy line
  that already carries it on the SVT stub, or from something else. I have not read the biller's
  term-crossing path.
- Whether the validator's ceiling is itself right for a crossing period.
- How many crossing periods in the book do NOT disagree. Without that I cannot say whether every
  E7-to-SVT roll is affected or only some.

The first thing to measure: count every E7-to-SVT crossing period in the ledger and grade each one
as AGREED, BOUNDED or DISAGREED. That gives the denominator before anyone names a cause.

**Why LATENT and not BLOCKING.** 3 bills in the book fail. The overcharge is a few pounds to £17
per bill, on a population the validator can see.
