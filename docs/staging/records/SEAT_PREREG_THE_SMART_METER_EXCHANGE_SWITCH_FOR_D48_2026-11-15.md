**Severity:** RECORDED · **Lane:** 0 delivery · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Direction item:** `d48-meter-exchange-flip-is-preregistered`

# Pre-registration: turning `meter_reads.SMART_METER_EXCHANGE` on, for D48's L3

Written 2026-11-15, at origin `aac80452a6`. Nothing has been launched. No code changes. The switch
(`simulation/meter_reads.py:441`, `SMART_METER_EXCHANGE = False`) stays off in this item. Every range
below was written before any run with the switch on.

## What the switch does

With it on, `SimulatedReadFeed._record_exchange` gives each premise traditional at acquisition an
exchange date, drawn from `life_events.smart_meter_installed_event` (its own substream, keyed per
premise, both legs of a dual-fuel home in one visit) at the DESNZ conditional hazard: 8.2% (2017),
rising to 19.0% (2024), and 0 in 2025, where the stock series is held flat at 68.9%. From that date,
`meter_in_force` reads the account as smart. Knowledge: `unbilled_energy_and_revenue_assurance.md`
§4e.

## Measured first: the last published book, switch off

Book: `docs/reports/run_output_latest.json`, producing commit `dc53f3311e` (stamped at 2026-11-14
08:07Z). Read through the measure D48 already publishes (`company/billing/billing_accuracy.py`):
53,595 bills and 53,595 world reads.

**Accounts.** 722 electricity and 584 gas. **No account changes meter type in its life:** 579/462
are traditional throughout and 143/122 are smart throughout. That is the switch's absence, measured.

**Reads by kind (world read log, the meter in force):**

| meter | actual | estimated |
|---|---:|---:|
| traditional | 9,308 | 36,147 |
| smart | 7,388 | 752 |

**Bills by basis (the meter the supplier holds):**

| fuel | meter | estimated | actual | prepayment |
|---|---|---:|---:|---:|
| electricity | traditional | 17,744 | 4,495 | 3,012 |
| electricity | smart | 270 | 3,628 | 631 |
| gas | traditional | 14,102 | 3,710 | 2,392 |
| gas | smart | 422 | 2,697 | 492 |

**Traditional share of accounts billed in the year** was 0.85 in 2016, 0.84 in 2020 and 0.77 in 2025
on electricity. Gas is the same to within 0.01. The national stock, 1 − p(Y), was 0.89, 0.60 and 0.31.
**The estimated share of billed kWh within each meter type is flat across the decade:** traditional
0.69–0.74 on electricity and 0.67–0.72 on gas; smart 0.02–0.06 on electricity and 0.08–0.16 on gas.
Over the decade the blend is **0.62** on electricity (5.49 of 8.84 GWh) and **0.61** on gas (11.97 of 19.71 GWh).

**Billed against used (D48's K2 true-ups; absolute error is under-charge plus over-charge, over billed kWh):**

| fuel | meter | accounts | true-ups | abs error / billed | barred true-ups | 12+ run accounts |
|---|---|---:|---:|---:|---:|---:|
| electricity | traditional | 579 | 3,525 | 6.56% | 28 | 183 |
| electricity | smart | 143 | 131 | 0.34% | 0 | 3 |
| gas | traditional | 462 | 2,863 | 7.11% | 27 | 139 |
| gas | smart | 122 | 143 | 1.33% | 0 | 6 |

Book-wide, that is 5.6% on electricity and 6.2% on gas.

**Catch-up bills (`catchup_applied`, absolute £ adjustment):** on electricity, traditional 3,521 with a median of
£3.20, a p90 of £64.87 and **29 at £500 or more**; smart 131 with a median of £1.64 and none at £500 or more.
On gas, traditional 2,862 with a median of £9.64, a p90 of £40.20 and none at £500 or more; smart 143 and none.

**Back-billing (SLC 21BA).** On pay-on-bill, the cap was applied 25 times on electricity and 26 times
on gas, all of them traditional, for £240.03 and £186.08 written off. The barred energy was 1,477 and
3,726 kWh. On the DD money line, 236 of 829 accounts that met a recovery action were barred, for
£19,315.76 (share 0.285, CI 0.255–0.316). At the 2025-06 snapshot, the accounts with no read bill in
12 months were 10 of 203 on electricity and 5 of 165 on gas.

## A precondition the switch does not meet: the supplier never learns of the exchange

`monthly_bill_assembly.py:853` calls `read_feed.meter_type_for(customer_data)` **once per account**,
and `:1304` stamps that type on every bill. With the switch on, the world reads the meter in force
(`meter_in_force`, `meter_reads.py:924/943/958`), but the bill, the raw export, the read-duty
register and `K2_by_year_and_meter_type` all still say `traditional` for an exchanged meter. §4e
itself says that an exchange is "a fact the supplier holds about its own supply point": the supplier
fitted the meter. If the run is graded as built, the split meant to tell the reading from the book's
meters would put every exchanged smart meter into the traditional cell. That cell's estimated share
would fall, and the fall would be read as better reading of dumb meters. **This is the definition
failure CLAUDE.md names, so it is fixed before the run, not after.**

**Launch precondition (P0), a sim-side build in its own commit before the flip.** From the exchange
date onward, the bill's `meter_type` is the meter in force. The control is that a test account exchanged
mid-life prints `traditional` before its exchange date and `smart` after it, and that switch off is
byte-identical. Until P0 lands, the readout keys meter type on the read log's `meter_type` (the meter in
force), never on the bill's.

## The arms

- **`off`**: the policy and world at the launch commit, with the switch as it stands.
- **`on`**: the same commit, book and seed, with `SimulatedReadFeed(smart_meter_exchange=True)`.
  There is no run-level override today: the constructor argument exists, but nothing on the run path
  passes it. The launch commit adds one (an env/CLI flag that reaches the constructor) and prints the
  flag in the run identity. The one variable is the switch. The launch is
  checked by diffing `run_identity_fields` between the two books.
- One primary pair on the default book and seed. **This item does not flip the default.** The default
  flips only if the readout below lands inside its ranges, or a refutation is explained, in the same
  commit as D48's unpark.

## Readout and predicted ranges (on − off unless stated)

| # | quantity | off (measured) | predicted on |
|---|---|---:|---:|
| R1 | traditional share of accounts in force, electricity, 2020 / 2024 | 0.84 / 0.79 | 0.52–0.68 / 0.26–0.42 |
| R2 | estimated share of billed kWh, decade, electricity / gas | 0.62 / 0.61 | 0.38–0.52 / 0.40–0.54 |
| R3 | estimated share **within** meter type (in force), every year | trad 0.67–0.74, smart 0.02–0.16 | each cell moves by no more than ±0.05 from off |
| R4 | billed-against-used abs error / billed kWh, electricity / gas | 5.6% / 6.2% | 3.0–4.6% / 3.4–5.2% |
| R5 | catch-up bills, electricity / gas | 3,652 / 3,005 | 2,100–3,300 / 1,700–2,800 |
| R6 | electricity catch-ups of £500 or more | 29 | 10–32 |
| R7 | pay-on-bill 21BA caps applied, electricity / gas | 25 / 26 | 6–22 / 6–22 |
| R8 | DD money line: accounts barred / £ barred | 236 / £19,316 | 130–236 / £8k–£19.3k |
| R9 | snapshot share with no read bill in 12 months, electricity / gas | 10/203 / 5/165 | 1–7 / 0–4 of the snapshot accounts |

**How the ranges were made.** R1 is 1 − p(Y), scaled by the book's 0.95 offset at 2016 (0.85 against
0.89). R2 is the off cell rates (traditional about 0.72, smart 0.045 on electricity and 0.12 on gas), reweighted by kWh
and year at R1's mix. A 0–1 year lag gives 0.43–0.47 on electricity and 0.45–0.49 on gas, and the range is widened
by the reweighting's error. R4 is the off per-meter error rates at the same mix. R5 and R6 fall less
than in proportion, because the exchange's first smart read ENDS any open estimated run. So
2017–24 should show a catch-up on the exchange month for every premise exchanged mid-run, and that
is the mechanism R6's upper end allows for. R3 is the control: the switch changes which meters are
traditional, not how a traditional meter is read. **If R3 moves by more than 0.05 in any year, the
switch has changed something besides the mix, and nothing else in this table is graded until that is
explained.**

**Refutation lines.** (a) R1 at 2024 above 0.45 means the exchange did not reach the book, a wiring
fault, and the run is void. (b) R2 falling by less than 5 points on either fuel refutes the D48 finding
that the flat estimated share is the book's meters and not its reading
(`WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_*`). (c) R5, R7 or R8 rising, or R6 above 32. Fewer traditional
meters cannot raise traditional-only harms, so a rise is a defect in the exchange path.

**The one I am least sure of: R8.** The DD bar depends on how the debit drifts against the bills, and
I have not traced how the exchange-month catch-up enters the DD review. The sign is the prediction;
the size is not.

## What the world-digest move makes unattributable

The switch moves the world digest: every read, and so every bill, catch-up, balance and payment
downstream of an exchanged premise. A comparison across the flip is not a one-variable result.
**Any result whose two arms, or whose result and baseline, straddle the flip cannot be attributed.**
By name:

1. **churn_roll's grade.** Its fourth of six pairs is running on the current digest.
2. **Candidate A** (pre-registered at `b060dd719`), compared against churn_roll's flat twin.
3. **B11 M7**: the six fresh `value_arm` books, seeds 61113–61118 (`7036dcbd54`), graded against
   the value arms' existing results.
4. **The retention-netting pair** (`460c37044`, `4e89cefeb`), whose comparison is the 22 Oct pair and
   the vintage-belief grade.
5. Also: the correctness stretch's cold-read grades, W1's level-DD measure
   (`SEAT_FINDING_W1S_LEVEL_DD_MEASURE_READS_6_OF_20_*`), D48's own off numbers above, and any DD
   review-arm pair.

## Sequence

**churn_roll's grade → candidate A → B11 M7 → the retention-netting pair → P0 → this flip pair →
a second blind D48 Expert Hour (`done/SEAT_BRIEF_D48_EXPERT_HOUR_*`) → D48's L3.**

The flip pair launches when the retention-netting pair has finished running and P0 is on origin. It does not wait for the
netting pair's grade, because the grade reads a finished book. If W2's BLOCKING crisis-bad-debt finding is still open
at launch time, it is read first: the switch is a W2 world change. The order is recorded on D48's
simplification record and its map park in the same commit as this file.
