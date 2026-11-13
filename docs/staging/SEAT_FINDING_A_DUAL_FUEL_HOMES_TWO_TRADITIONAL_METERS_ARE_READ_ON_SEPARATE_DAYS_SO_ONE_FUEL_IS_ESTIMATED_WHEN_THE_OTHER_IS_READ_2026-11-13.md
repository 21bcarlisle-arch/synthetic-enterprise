**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# A dual-fuel home's two traditional meters are read separately, so one fuel is estimated when the other is read (N30, 2026-11-13)

**Found by** the twelfth cold read, objection O23, from a billing-systems test analyst's lens
(`records/SEAT_READING_THE_TWELFTH_COLD_READ_ON_THE_6FE7827AB2_BOOK_2026-11-13.md`). On the estimate-trap slot the
reader quoted "gas · 29 Aug 2018 · 209 kWh ACTUAL READ" beside "electricity · 29 Aug 2018 · 87 kWh ESTIMATED". Their
point: "a visit or customer read usually takes both meters."

## What it is

On a dual-fuel home with two traditional meters, a bill period where one fuel has an actual read almost never has an
actual read on the other fuel.

## How big it is

Measured over every page file of the 6fe7827ab2 book rebuilt at origin 1d86d8e71f, with
`/var/tmp/twelfth-read/scripts/fuelpair.py`. A pair is one bill period billed on both legs.

| meters | pairs | both read | one read, one estimated | one-only as a share of pairs with any read | households |
|---|---:|---:|---:|---:|---:|
| traditional, traditional | 16,271 | 679 | 5,364 | **89%** | 359 |
| smart, smart | 3,290 | 2,803 | 384 | 12% | 71 |

89% is what independent draws give. At an actual-read rate near 20% a month per fuel, the share with both read, given
that either is, is p²/(2p − p²) ≈ 11%, and the book shows 11% (679 of 6,043).

## Why it is wrong

On a traditional meter an actual read comes from one of two sources:
- a meter reader's visit, which reads every meter at the premises;
- a customer's own submission, which suppliers ask for on both fuels together.

So the two fuels' actual reads should mostly fall on the same day. Smart meters can fail on one fuel only, because gas
communications drop out more than electricity (DESNZ: 9.1% against 4.7%). Their 12% is therefore not shown wrong here.

**GAP.** No published source gives the share of traditional dual-fuel reads taken together. That share is a
practitioner fact. The knowledge page (K8) should state it as a belief with a range before the build, not as a number.

## The cause (read after filing)

- `simulation/meter_reads.py:523` seeds the read draw with `meterread_{customer_id}_{period_end}`. The gas leg's id
  carries a `g` suffix, so the two fuels draw independently.
- `is_hard_to_read(customer_id)` (line 225) is keyed per leg too, so a premise can be hard to read on one fuel only.
- The smart-mode draw (line 244) is already keyed on `household_of(customer_id)`. The household coupling was made there
  and not for the read itself.

## Serious by the rule

It changes money. Which fuel is estimated decides what each bill charges and when a catch-up lands. The size of that
effect is not measured, and under `serious_class_rule` unproven counts as serious.

## What done means

The world's read event for a traditional dual-fuel premise is drawn once per premise visit, and both legs read on it.
A blind row (`checkable: true`) grades the one-only share on traditional pairs. Its ceiling comes from the knowledge
page's range, and it is graded on a book built after the fix.

**Reverse.** Delete this file.

## Status, 2026-11-13 (the build)

- Knowledge (K8): `docs/market_research/unbilled_energy_and_revenue_assurance.md` K2, "a traditional dual home's two
  meters are read on one occasion". The GAP is carried as register row `q6_dual_fuel_read_together_share`, 0.8 in
  0.6–0.95.
- World: `simulation/meter_reads.read_occasion_id`. A gas leg draws its read on its household's occasion at that share.
  Each fuel's read rate is unchanged and electricity reads are byte-identical. On 480,000 drawn pairs the one-only
  share is 0.886 → 0.286, as predicted on the page before it was measured.
- Blind row: `INV_DUAL_FUEL_TRADITIONAL_READS_TAKEN_TOGETHER`, `checkable: true`, with a ceiling of 0.5 (the low edge)
  and a floor of 0.09 (the high edge).
- **Open:** grading that row on a book built after this commit. The 6fe7827ab2 book would breach it at 0.89. This
  file closes when a post-fix book grades CLEAN.
