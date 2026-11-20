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

## Count and pre-registration (delivery seat, 2026-11-19, before reading the biller)

**The count.** On the 6af7fd0bfd ledger (53,605 bills), there are 87 bill periods in which an E7 fix
(a term carrying a Day/Night pair) ends and an SVT term begins. 84 are BOUNDED: 58 with one register
and 26 with two. **3 are DISAGREED**, and all 3 have two registers. So it is not every E7-to-SVT roll.
It is not every two-register roll either: 26 of the 29 sit inside the range.

**What the data alone shows.** PROS-2021-0313, Sep 2022, prints two rate lines. Line 1 is the fix's
1-day stub: 6.6 kWh at 18.48p, which is inside 10.03..21.35. Line 2 is the SVT from 2 Sep: 531.7 kWh
at **28.618p**, all-in £152.16. The term record gives that SVT a flat 25.4557p and NO Day/Night pair
(`tou_unit_rates: null`). October's SVT term, which is the same product on the same meter, does
carry a pair (60.08 / 28.24 against a flat of 46.70).

**Pre-registered prediction.** The excess is carried by the ENERGY line, on the SVT rate line. The
biller charges the SVT stub per register at an E7 Day/Night pair. That pair's average, weighted by
this customer's 76% day share, is above the flat rate, because the flat rate is the pair averaged at
a standard split. The network-and-policy line is NOT double-counted. The defect is in the term record
the ledger exports, not in the bill: a stub SVT term that no full bill settles as time-of-use gets no
pair. So the validator's ceiling (max of the flat rates) is too low. Fix the export so that the term
carries its pair, and keep the bill. **Refuted if** the biller prices the SVT stub at the flat rate
plus a separate adder, or if the levy line is charged twice.

## The cause, read (delivery seat, 2026-11-19)

**The prediction held, and another lane had already fixed the cause.** c6695cd8db (18 Nov 12:45,
after this ledger was written at 10:10) found what I pre-registered. The SVT stub term is no bill's
`term_of_bill`, so `_tou_terms` gave it no pair. Its record went out with `tou_unit_rates: null`,
and the bound's ceiling was the flat rate. The biller settled the stub on Day/Night: its rate line
is flagged `time_of_use`, and PROS-2021-0313 was charged 28.618p, which is the pair weighted by a 76%
day share. The bill is right and the exported term record was wrong. That commit measured the book
moving from 3 DISAGREED to 0, with 29 stub terms gaining a pair. **The red clears when the next
publish regenerates the ledger. Nothing is left to fix on the crossing.**

## The cap row is a class: 996 bills, not 1

On this ledger, `default_tariff_rate_within_cap` reads AGREED 26,553 and DISAGREED 996. All 996 are
on multi-register meters, across every cap window from 2019 to 2025, and every one is over by less
than 0.5p. **PROS-2021-0313 is not a pro-rating artefact.** Its SVT term (2 Sep to 30 Sep 2022) sits
wholly inside one window. It is also not a charge above the published level. Two readings of a
level that is not published are disagreeing:

- **The company** takes the published single-rate headline, 283.4 £/MWh inc VAT (26.990p ex-VAT),
  and scales it by the cap model's multi-register / single-rate ratio (25.41 / 26.942 = 0.9431):
  **25.4557p**.
- **The validator** takes the model's 15-region median multi-register level directly: **25.41p**.
  That median's own single-rate twin (26.942p) is 0.18% UNDER the published headline (26.990p).

The validator's single-rate check uses the published headline, so its two checks are on different
bases. The multi-register column "has NOT been checked against a published Economy 7 cap series"
(`slc_28ad_multi_register_cap_test.md`). The law is per region, and neither figure is that
customer's regional level.

**Fix (validator; the bill is kept).** Put the multi-register ceiling on the single-rate check's
basis: the published headline × the model's multi/single ratio for the same period. The windows and
the multi-register periods share every boundary (checked).

**Pre-registered before re-measuring.** The 996 move to AGREED. Whether any AGREED bill moves to
DISAGREED depends on whether the headline is under the median single-rate in any period, which I
have not looked at. If it is, those periods' ceilings fall, and I predict 0 bills cross because the
company's rate is built on the headline.

**Measured after the fix, on the same ledger.** `default_tariff_rate_within_cap` reads AGREED
27,549 and DISAGREED 0. That is all 996 moved, and none moved the other way. The headline IS under
the model's single-rate median in 6 periods (Apr–Dec 2024 and Jul–Dec 2025, by up to 0.47%), so
those ceilings fell. No bill crossed, because the company's rate is built on the headline. The
prediction held.

**What this costs the check, stated.** The validator's multi-register ceiling is now computed the
way the company computes its own. A company that struck a multi-register SVT at the single-rate
headline still disagrees, because the ratio is below 1 in every period (test). A company that read
the WRONG ratio from the same artefact would not. The ratio has one source, the cap model, and no
second one is published. The open knowledge gap is a published Economy 7 cap series, which the
commons artefact already names as uncorroborated. This lane does not close it.

**Status.** The crossing cause was named and fixed in c6695cd8db, and its red clears at the next
publish. The cap row is fixed in the validator and the bill is kept. Nothing here is left open, so
this finding can move to `done/` once the next publish shows both readers green.

## Done (2026-11-20, the commit that moves this file)

**Not an overcharge. The validator's ceiling was wrong, and that was fixed in c6695cd8db (18 Nov 12:45),
two hours after the 6af7fd0bf publish this red was read from.** The bill charged the SVT stub its
own Day/Night pair. The ledger's term record for that stub carried only the SVT's flat rate
(`tou_unit_rates: null`), so the ceiling sat under the Day rate. On PROS-2016-0253 Sep 2017 the SVT
pair is 18.9888 / 8.9247p, and the ceiling becomes £189.55 against the £164.63 charged.

**Measured 2026-11-20 in a clean worktree at b3c18d1846, with the ledger rebuilt by
`python3 -m tools.generate_billing_ledger` (53,605 invoices) and nothing published:**
- `test_the_validator_checks_the_printed_rate_against_the_contracted_tariff.py`: 10 passed.
  Against the ledger in git (still 6af7fd0bf's) the same file has 1 failed and 9 passed, with the
  same 3 bills.
- The three stubs now carry their pairs: 0253 18.9888/8.9247, 0286 19.9689/9.3854, 0313
  32.7447/15.39. All three bills are BOUNDED. For example, 0313 is £153.38 inside £54.02..176.26.
- **The second claim clears too.** For PROS-2021-0313 Sep 2022, `default_tariff_rate_within_cap` is
  AGREED at 25.4557p under the multi-register cap model. Book-wide it is 27,549 AGREED, 0 DISAGREED.
- **The denominator this finding asked for, from the old ledger:** 115 bills with two terms mixed a
  term carrying a ToU pair with one that did not (65 fix→SVT, 22 SVT→SVT, 28 SVT→fix). Only 3 broke
  the loose ceiling. The rest were BOUNDED against a ceiling too low to bind.

The post-publish reader store turns green at the next publish that rebuilds the ledger. Nothing in
this commit touches code.
