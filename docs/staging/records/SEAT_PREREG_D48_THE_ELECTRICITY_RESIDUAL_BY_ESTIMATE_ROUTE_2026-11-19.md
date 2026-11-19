# D48: the electricity unbilled residual, split by estimate route, read age and tenure

Filed 2026-11-19 by the delivery lane `electricity-unbilled-residual-is-traced-to-the-company-estimator`.
The book is `run_output_6af7fd0bfd_20261118T070221Z.json`. It was only read, and no book was built.
The runner is `tools/couple_w2_36_d48.py` (f79826ffc). Its `account_errors` was re-run unchanged and
the split below was taken from the same accounts. The reconstruction checks to 0.0 kWh on all 722
electricity accounts.

## What the number is, said first

The electricity gap of 0.407 [0.268, 0.538] is the company's mean |belief − truth| per account,
divided by the same mean for a no-skill supplier. Belief is the company's own true-up. Truth is billed
less used. On every run an actual read closes, the true-up matches the world exactly. So the whole
residual sits on estimated bills that no actual read ever closed. That means runs closed on an
estimated final bill (78% of |residual|) and runs still open when the book ends at 2025-06 (22%).

**Correction beside the drawn item.** The item said "mean |billed-used| 455 kWh against 50-400".
455.3 kWh is the pooled **no-skill** MAE, not the company's error. The company's pooled MAE is
131.9 kWh. For electricity alone it is 77.0 kWh per account, over 722 accounts, and 407 of them
carry a residual above 0.01 kWh.

## The split (electricity, residual bills only: 2,044 bills on 408 accounts)

**Read type.** This book has no customer reads. Prepayment bills are never estimated, and an
actual-read bill trues up exactly. So read type holds nothing to split: 100% of the residual sits
on `billing_basis == "estimated"`.

**Estimate route.** This is the route `company/billing/monthly_bill_assembly.py` takes for the
bill, at about line 1143. The harness re-derived it from the account's own actual-read dates:

| route | bills | Σ\|bill err\| share | billed / true | accounts | share of Σ\|account residual\| |
|---|---|---|---|---|---|
| own reads span ≥ 182 d: annualised advance (`annualised_advance_kwh`) | 1,345 | 0.47 | 0.989 | 307 | 0.37 |
| own reads span < 182 d: **registry EAC** (`opening_estimate_kwh`) | 421 | 0.44 | **1.148** | 71 | **0.57** |
| no actual read yet: registry EAC, or TDCV MEDIUM | 278 | 0.08 | 1.005 | 30 | 0.06 |

**Months since last actual read** (Σ\|bill err\| share): 1–2 months 0.37, 3–6 months 0.38,
7–12 months 0.15, 13+ months 0.02, never read 0.08. The error does not grow with read age. It is
not the stale-read shape.

**Tenure at the bill:** 0–5 months 0.12 (billed/true 1.10), **6–11 months 0.35 (1.15)**, 12–35 months
0.24 (0.99), 36+ months 0.29 (0.99). The over-billing sits in the first year, where the 182-day hold
falls.

**Profile class:** PC1 0.47 (billed/true 1.02), PC2 0.33 (0.92, under-billed), PC3 0.20 (1.85).
**Meter:** traditional 0.99. **Segment:** the SME share is 0.20 of bills and 0.29 of accounts, on 2
accounts.

**Concentration.** The top 5% of accounts hold 79% of Σ\|residual\|, and the top 10% hold 89%.
**One account, C6 (SME, PC3), holds 28%:** 31,996 kWh billed against 16,284 used over eight
estimated months, 2016-05 to 2017-03. Its registry EAC is 45,000 kWh. Its own two reads, April and
July 2016 (a 92-day span), imply about 22,000. The company held those reads and set them aside,
because the span was under 182 days. Without C6 the electricity gap is 0.341.

## The estimator, named

The estimated electricity read is set in `company/billing/monthly_bill_assembly.py` (the
`estimated` branch, `shaped = ...`). It takes three routes:

1. **`unread_month_estimate.annualised_advance_kwh`.** This is the EAC-from-an-advance: the
   company's own register reads over a span nearest a year, within 182–731 days, divided by the
   profile weight. It is used once the reads span 182 days, because `annualised_advance_estimate` is
   on by default (ruling of 23 Oct).
2. **`unread_month_estimate.opening_estimate_kwh`**, through `_registration_annual_kwh`. This is the
   registry EAC handed over on registration (`customer_data["eac_kwh"]`), else Ofgem's TDCV MEDIUM,
   spread on `MONTHLY_SHARE_OF_ANNUAL_USE["electricity"]`. It is used before the first read **and
   whenever the company's own reads span less than `MIN_ADVANCE_DAYS` = 182**.
3. PC2 meters go per register, by the same routes.

The 182-day hold has **no source**. That is the code's own comment, corrected 2026-10-29. The
knowledge page's §8 (`docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md`)
establishes BSC Annex S-2 §4.3.7. Under it, every advance moves the settlement EAC by the weight
`min(1, FYC·SPAR)`, with no hold. **SPAR's value is a GAP:** it is Market Domain Data, behind a login.

## Which side

**The company's estimator, on one route.** Route 2-after-reads holds 57% of the account residual
and over-bills by 15%. The world's electricity shape is not the suspect here. On the route that
uses the published profile with the company's own year-long advance (route 1), billed/true is 0.989.
By calendar month the signed error has no consistent winter-against-summer sign. N17 (a flat year-on-year electricity
world) would show as route 1 drifting, and route 1 does not drift. One caveat: whether C6's
45,000 kWh registry EAC is a fair stand-in for the real industry figure is a question about the
world's registration draw, and this split cannot settle it.

## Pre-registered single-variable change (NOT built)

**Change.** In `monthly_bill_assembly`, replace the 182-day hold with the BSC blend. On each actual
read, `EAC ← w·(advance/FYC) + (1−w)·EAC`, where `w = min(1, FYC·SPAR)`, starting from the registry
EAC. Bill the estimate as `EAC × profile_weight(period)`. Nothing else changes: route 1, PC2 and gas
stay as they are.

**Predicted electricity gap on this book**, against 0.407 today. The no-skill denominator is held
fixed, and only PC1/PC3 bills on the hold route move. Computed now, before any build:

| SPAR | 0 (control) | 0.5 | 1 | 2 | 3 | ∞ (latest advance only) |
|---|---|---|---|---|---|---|
| gap | 0.402 | 0.379 | 0.356 | 0.315 | 0.289 | 0.317 |
| C6 \|residual\| kWh | 15,712 | 13,218 | 10,841 | 6,437 | 2,502 | 3,453 |

The SPAR 0 control reproduces C6 exactly. It reproduces the total to within 749 kWh (1.3%): those
are accounts whose opening figure was TDCV, not a registry EAC. **The prediction is a gap in
[0.28, 0.38] at any SPAR in [0.5, 3].** A rerun outside that band refutes this account of the
residual. PC2 is left out, because the harness cannot re-run its per-register estimate faithfully
from the book. Its 8 hold-route accounts carry 7,504 kWh, and the PC1 total-shape stand-in made
them worse (0/8 improved). So PC2 is a separate question.

**Why it is not built.** One cause does hold most of the residual: the hold route, at 57%. But the
change is a blend whose weight is SPAR, and SPAR is an established GAP. Picking it would be the
invented constant the rule forbids. Half of the route's share is also one account. The next step is
knowledge, not code. Either establish SPAR, or establish what a supplier's billing estimate does in
its first months. The latter is §5/§7's GAP: whether billing follows the settlement EAC at all.
Once either is established, this table is the pre-registration that build answers to.

## Method, for the rerun

Run `account_errors(book)` from the runner. For each electricity account, take the bills after its
last non-estimated bill: those are the residual run. Then, per bill:

- **err** = `total_consumption_kwh − meter_read_log.true_consumption_kwh`, for the same `period_end`.
- **route** = no actual read yet, else actual-read span (first to last `period_end`) < 182 d, else
  ≥ 182 d.

The account sums equal the runner's `truth − belief` to 0.0 kWh. For the counterfactual, the
advances are each actual read's `true_consumption_kwh` summed since the previous read. That is the
register advance the company itself holds, so nothing beyond the wall is read to form the estimate.

## Outcome of the knowledge step (2026-11-19, later): NOT built, and the band is not graded

SPAR is still a GAP. Every public Elexon document that names it gives no value. The URS, the
Logical Data Design, the Technical Spec, the System Management Guide, P40 and the MDD page were all
read. The only number found (1.100, 1997) is a sample report layout. The value sits in MDD Online
or the D0269/D0270 flows under licence, which is a G5 wall. Billing practice is partly established:
OVO bills an unread month from the D0019 EAC, which blends with no hold. So the hold is now
contradicted on both sides, and it stays only because every replacement needs SPAR. That also
changes where the build belongs. A real supplier is handed the EAC on the D0019, so SPAR is the
world data collector's parameter, not a company constant. The [0.28, 0.38] band above still stands
as the prediction that build answers to. It also needs the E1 breach count at each SPAR alongside
it, because SPAR → ∞ re-opens those breaches. Record:
`docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §5, §7, §8.

## Graded 2026-11-19: the blend is built at both ends of SPAR [0.5, 3], and is read on 67d454905c

*Filed by the delivery lane `d48-the-electricity-blend-is-built-across-spar-0-5-to-3`. Nothing
above this line was edited.*

**What is built.** The blend is `unread_month_estimate.bsc_blended_eac_kwh`. Its §4.3.7 step is
`blend_advances_into_eac`, which the harness now calls too, so the grade below is graded on the
built formula. It is billed by `monthly_bill_assembly` on the hold route, for PC1/PC3 electricity
only. It sits behind `DecisionPolicy.bill_estimate_blends_the_eac_at_spar`, which is `None` (the
hold) on every standing policy. SPAR is `SPAR_WEIGHT_RATE_STATED_RANGE = (0.5, 3.0)`. A value
outside the range is refused, and the refusal names its reason. Knowledge first:
`how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §8, "Design choice, 2026-11-19".

**The grade.** Read-only, by `python3 -m tools.d48_spar_blend_counterfactual --ends`, on
`run_output_67d454905c_20261119T184502Z.json`. Before that, the full sweep was re-run on
6af7fd0bfd through the refactored harness. It reproduces the E1 record's table exactly, to the
breach and flag counts at SPAR 0, 0.5, 1, 2, 3 and ∞.

| book | SPAR | elec gap | Σ\|residual\| kWh | no-skill kWh | C6 \|res\| kWh | E1 breaches / runs | E1 flags | breach set, flag set = control |
|---|---|---|---|---|---|---|---|---|
| 6af7fd0bfd | 0 (hold) | 0.407 | 55,561 | 136,384 | 15,712 | 8 / 4,428 | 27 | — |
| 6af7fd0bfd | 0.5 | 0.379 | 51,742 | 136,384 | 13,218 | 8 | 27 | yes, yes |
| 6af7fd0bfd | 3 | 0.289 | 39,425 | 136,384 | 2,502 | 8 | 27 | yes, yes |
| **67d454905c** | 0 (hold) | **0.388** | 56,295 | 144,994 | 15,712 | 10 / 4,455 | 35 | — |
| **67d454905c** | **0.5** | **0.361** | 52,372 | 144,994 | 13,218 | **10** | **35** | **yes, yes** |
| **67d454905c** | **3** | **0.276** | 40,047 | 144,994 | 2,502 | **10** | **35** | **yes, yes** |

At both ends, 3,182 hold-route bills were re-billed and 11 zero advances were skipped.

**Against the pre-registered band [0.28, 0.38].**
- **SPAR 0.5: inside** (0.361).
- **SPAR 3: outside, by 0.004 below the floor** (0.276). Read literally, the band is refuted at
  the high end, and that stands as written.
- **What moved is the denominator, not the blend.** Between the two books the electricity
  no-skill denominator rose 6.3% (136,384 → 144,994 kWh) and the residual rose 1.3%. The blend
  removes almost the same kWh on both: 16,136 on 6af7fd0bfd and 16,248 on 67d454905c, at SPAR 3.
  As a share of the hold's gap that is −29.0% and −28.9%. So the band was drawn on one book's
  denominator and read on another's. The account of the residual (the hold route carries it, and
  the blend removes the same share) is not what failed. A band for the next book should be
  stated relative to its own SPAR-0 control.

**E1, against SEAT_PREREG_D48_E1_BREACHES_AT_EACH_SPAR's column.** On this book the guard holds at
both ends. The breach set and the flag set are identical to the hold's: 10 breaches and 35 flags.
Three of the 10 breaches sit on accounts the blend moves (SYN-2016-215 twice, PROS-2019-0302). All
three are also in the control, so none is new. This is a replication by the harness. It is not
the graded invariant for 67d454905c.

**Published as a range:** with the blend, the electricity gap on 67d454905c is **0.276–0.361**,
against 0.388 under the hold. E1 is unchanged at every SPAR in the range. No point value of SPAR
is stated anywhere.

**Next, not done here.** The switch stays off. Turning it on in the published policy is its own
step, taken after the 0.12 pair has read. A fresh run with the switch set at each end is what
grades the build end to end: route 1, the catch-up and the DD path, which this harness does not
move.
