**Severity:** RECORDED · **Lane:** 0 delivery · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `retention-netting-arm-is-preregistered` · **Triage:** `retention-money-goes-to-debtors-priced-as-payers`

# Pre-registration: switching `retention_nets_bad_debt` on, re-armed on the vintage belief

Written 2026-11-14 at about 21:50Z, at origin `cec629ab6`. Nothing has been launched. No code changes.
The default of `DecisionPolicy.retention_nets_bad_debt` stays `False` in this item.

## Correction to the item's premise

The item says the switch "has been 'next week's' since 14 Oct" and is unmeasured. **That is wrong.**
The pair was pre-registered on 21 Oct
(`SEAT_PREREG_THE_RETENTION_GUARD_NETTING_ITS_OWN_BAD_DEBT_BELIEF_ON_THE_CONTRIBUTION_GUARD_2026-10-21.md`)
and graded on 22 Oct
(`WORKER_RESULT_THE_RETENTION_GUARD_NETTING_ITS_OWN_BAD_DEBT_BELIEF_ON_THE_CONTRIBUTION_GUARD_2026-10-22.md`),
both beside this file, at `1ac35d918`. It found 113 offers off and 108 net. Of the 6 offers the netting withdrew,
**none** was POOR or CRITICAL. `total_net` moved +£29. The verdict was that the field "stays off as a
debtor fix". The triage row's 14 Oct reason was never updated, so the next readers kept calling it
next week's. This record corrects the row, in the same commit.

**What is still open, and why a re-arm is worth one run.** Four days later, `7939895894` changed the belief
the netting reads (the own-book belief is read by vintage). Its graded result
(`SEAT_RESULT_THE_BAD_DEBT_BELIEF_READ_BY_VINTAGE_..._2026-10-22.md`) moves loss **out of** the clean
cell and **into** the arrears cells. In calls dated 2023 or later, `no_debt` went from 0.39% to 0.20%,
`in_arrears_steady` from 0.85% to 1.17%, and `worsening` from 5.3% to 6.6%. The 22 Oct pair ran on
the old reading. The only way netting can become a debtor fix is that shift, and the shift has never met
the guard. That is this arm's one question. If it does not move the debtor offers, the triage row
should change from `fix by netting` to `needs its own mechanism`, which the 22 Oct result already
recommended. A mechanism of that kind (an arrears-state rule on the guard) is a director decision under G9, so it goes in
`for_the_director` and is not built here.

## Measured first: the guard on the last book that carries bands

Only the 22 Oct `off` arm records a payment-score band for each guard verdict
(`/var/tmp/se-retnet/off.json`, 240 guard rows, 113 offers). The live book does not. Headroom is
(value protected − offer cost) over the term's billing, on rows the un-netted guard offered. The last
four columns count the rows that a flat charge at that share of billing would withdraw.

| band | guard rows | headroom p10 | headroom median | @1% | @2% | @3% | @5% |
|---|---:|---:|---:|---:|---:|---:|---:|
| EXCELLENT | 51 | 2.0% | 5.0% | 2 | 5 | 14 | 25 |
| GOOD | 117 | 1.5% | 4.1% | 5 | 18 | 35 | 68 |
| FAIR | 44 | 2.2% | 4.4% | 2 | 3 | 9 | 25 |
| POOR | 14 | 2.7% | 5.6% | 0 | 0 | 3 | 6 |
| CRITICAL | 14 | 1.6% | 4.6% | 1 | 1 | 3 | 8 |

Debtors (POOR and CRITICAL) carry **as much or more** headroom than payers do. So a book-wide charge
falls on payers first. A debtor offer is withdrawn only if the belief that reaches *that* renewal exceeds
about 5%. Under the vintage reading, only the `worsening` cell gets there, and only from 2023 (6.6%).
In the 22 Oct `net` arm the median belief was 1.2% for CRITICAL and 0.24% for POOR. 72 of the 240 rows
were still at the 2% prior, because 93 of the 113 offers fall in 2017–18, before cells resolve. The
payment band is not the arrears state the belief is keyed on, and nobody has cross-tabbed the two.
That gap is what the predictions are least sure of.

## The arms

- **`net`**: `dataclasses.replace(CURRENT_POLICY, retention_nets_bad_debt=True)`.
- **`off`, the flat twin**: `CURRENT_POLICY` at the same commit, on the same book and seed. The twin
  is the guard as it stands, pricing every debtor as a payer. The one variable is the field. Whatever
  else `CURRENT_POLICY` carries at launch rides on both arms, including `renewal_belief_by_ending_term`
  if candidate A's grade switched it on (see the sequencing below). The launch commit prints
  `dataclasses.asdict` of both policies, and the diff must be that one field.
- **Book and seeds.** The primary pair runs on the default book and default seed, as the 21 Oct
  pair did, so that 22 Oct's numbers are the comparison for the vintage reading. The replication pair
  runs on **seed 61113**, the first of B11 M7's six fresh 40-founder books. It is listed and authorised
  by `7036dcbd54`, and it runs through the same book switch M7's driver uses. Its job is to check the
  sign of P2 only. A 40-founder book holds tens of offers, which is too few for anything else.
- **Instrument.** `tools/_c29_retention_engagement_arm.py <off|net> <out.json>`. Before it can launch it
  needs two changes, and both go in the launch commit. (1) `observed_value` crashes on the
  contribution guard's `None` margin. That is why the 21 Oct run used an out-of-tree probe. Make
  `unweighted` `None` when `expected_margin` is `None`, and make `offered_unweighted` `False`. (2) Add to each guard row
  the probe's fields: `customer_id`, `event_date`, `margin`, `acq`, `billed`, `belief_rate` and
  the **company's arrears state for the leg** (`_company_arrears_state`, the key the belief reads). The
  arrears state is the cross-tab the 22 Oct grade lacked. The world's ground truth does not enter. The
  arms publish nothing (scratch gap ledger, as now).

## Readout (each arm, then net − off)

1. **Retention offers by payment-score band**, plus the same offers by the company's arrears state.
   Withdrawn and added offers are matched on `(customer_id, event_date)`. Any offer that appears only
   in `net` is path divergence, because netting can only lower value.
2. **Retained CLV net of bad debt, by band.** Ex ante, from the guard's own rows: Σ over offered renewals
   that stayed of (term contribution + replacement cost avoided − the company's own belief × billing −
   offer cost). Ex post, for the whole book: `total_net`, `total_bad_debt` and `renewal_departures`.
   Per account: the write-offs booked in the term after the renewal on each account whose offer was
   withdrawn. They are read from the run's `collections_journeys` output. I have not checked that
   output carries a write-off per account. If it does not, this leg is published as `None` with that
   reason, and P6 is graded ex ante only.
3. **The M3 vector beside it, for the households whose offer changed.**
   - *Money (cost)*: £ the households pay with the offer withdrawn. This is the withdrawn discount,
     and it is a transfer to the company, not value created (M2).
   - *Money (cash flow)*, *certainty* and *control*: 0 by construction. The offer is a unit-rate
     cut on a fix the household already takes, and it changes no payment date or method. This is a
     stated belief, and the readout checks it against the arm's payment-method changes.
   - *Time*: the change in departures, as a count of switches. **Household minutes per switch are a GAP**,
     because no sourced constant exists in `company/`, `saas/` or `docs/market_research/`. So the minutes are
     published as `None` with that reason, beside the count.
   - *Carbon*: the change in kWh supplied to the changed households. It is published in kWh because the
     arm carries no per-period carbon intensity for these accounts.
   - *Weighted utility*: `None`. The hidden-weight instrument waits on the K8 page due 23 Nov, and is
     not built.

## Predictions (primary pair, net − off), written before any run

| # | Quantity | Predicted | Refuted if |
|---|---|---|---|
| P1 | Offers withdrawn (matched) | **3–12**, point 6. Retention spend −£100 to −£700 | 0 withdrawn, or more than 20 |
| P2 | POOR + CRITICAL among the withdrawn guard verdicts | **0–4 of 28 debtor guard rows**, point 2. Debtor share of `net` offers within 3 points of `off` | **8 or more**: the vintage reading has made netting a debtor fix, and the triage row stays `fix` with the switch as its remedy |
| P3 | Belief at the guard, median by band | CRITICAL 1.2–3.0%; GOOD and EXCELLENT 0.1–0.5% after 2019. No row below 0 (`7939895894` floors it by construction) | Any negative row; or CRITICAL ≤ GOOD |
| P3b | Belief by the company's arrears state, from 2023 | `worsening` 5–8%, `in_arrears_steady` 0.8–1.6%, `no_debt` 0.1–0.4%, all within 0.5 points of the 22 Oct vintage table | Outside those bands. The guard is then reading a different belief from the one the vintage grade measured |
| P4 | Renewal departures; churned accounts | **0 to +2** each | +4 or more |
| P5 | `total_net`; `total_bad_debt` | `total_net` **−£300 to +£500**. \|Δ bad debt\| < £500 | \|Δ total_net\| > £3,000: path divergence dominates, and the pair is re-read before anything is concluded |
| P6 | Retained CLV net of bad debt, debtor bands, ex ante | **+£0 to +£80** | Above +£300 |
| P7 | M3 money, changed households | +£100 to +£700 paid, the same pounds as P1's spend. Cash flow, certainty and control 0 | Cash flow, certainty or control non-zero. Something besides the rate moved |
| R | Seed 61113 pair: sign only | Debtor withdrawals ≤ payer withdrawals | Debtor withdrawals > payer withdrawals |

Confidence is lowest on P2, because the band-to-arrears-state mapping is unmeasured. A held P2 is the
outcome that goes against the thesis, which is why it is the one predicted (F11).

## What each outcome decides

- **P2 refuted (8 or more debtor withdrawals) and P5 held**: propose switching the default on, through
  a raised concern with this result as its evidence. The 16 Nov book is frozen, so a switch lands after
  it, never into it.
- **P2 held**: the netting remains a correct valuation that does not stop the debtor transfer. The
  triage row moves its remedy to "an arrears-state rule on the retention guard". That rule goes to the
  director under G9 with a recommendation: refuse an offer on a leg in `worsening` arrears unless the
  netted value clears the cost. It is not built here. Whether the field is switched on as the correct
  valuation is decided on P5 alone, and only if `total_net` does not fall.

## Sequence: when it runs, and what it reads

It runs **after** three things, in this order. It does not compete with any of them for the box:

1. **The `churn_roll` grade** (continuation stamped not before 15 Nov 09:30). It reads that grade's
   **measured half-range on the choosing leg** (redesign §8) as the noise bar for P5. If that half-range
   is wider than £500 a book, P5's range widens to match before launch, and the change is recorded
   here, dated. It also reads `SEAT_FINDING_THE_CHURN_ROLL_NOISE_FLOOR_RE_DRAWS_THE_RENEWAL_BUT_NOT_THE_OFFER_ANSWERING_IT_2026-10-22.md`:
   if the graded family re-draws offers too, P1's matched count is read against that floor.
2. **Candidate A** (redesign §9, `/var/tmp/vta-driver`). It reads **A's verdict on A2**, whether the
   desk belief moved realised retention, and whether `renewal_belief_by_ending_term` is on by default
   at launch. The flag gates which renewals reach the guard, so it changes the 240-row denominator. It
   rides both arms equally and is recorded at launch, never mixed between them.
3. **B11 M7** (six `value_arm` members on 61113–61118, `SEAT_PREREG_B11_M7_HELD_BACK_GRADE_ON_SIX_FRESH_BOOKS_2026-11-14.md`).
   It reads **M7's driver and its 61113 member**: the book switch for the replication pair, and the
   member's graded and departer counts, which bound what R can show. This arm launches when M7's
   last member exits and frees the memory.

Launch: `background.launch_long_job` with `--asserted-live-by` naming this file. Peak ~7,000 MB per
arm (the 21 Oct job's declaration), each arm in its own process, serial. Two primary arms take about 4 h
each. The 61113 pair is smaller. The grade continuation is filed by the launch driver, as on 21 Oct.

## 14 Nov, about 22:10Z: the instrument is fixed, and the launch gate is unmet

**Instrument (this commit).** `tools/_c29_retention_engagement_arm.py` now does what §Instrument asks.
(1) A `None` value from the guard records a row with `unweighted` None and `offered_unweighted`
False instead of crashing. (2) Every guard row carries `margin`, `acq`, `billed`, `belief_rate`, and
the renewal's `customer_id` (supply point), `billing_account` (the `retention_log` key, so the readout
matches on `(billing_account, event_date)`) and `event_date`. It also carries `arrears_state`: the
company's answer from `LivePaymentTriad.arrears_state` for the leg, observed on the class, which is
the same door the guard's belief reads. One row per value: the run's second comparison of the same
value is not recorded twice, as in the 21 Oct probe. The output also carries `policy`
(`dataclasses.asdict`), `retention_log` and `total_bad_debt`. A 2017 smoke run of the `net` arm
checked the instrument; its result is below.

**Gate state, read at 22:10Z. None of the three has cleared:**
1. The `churn_roll` family is **not graded**. `/var/tmp/vtcr-out/` holds three member/control
   pairs (`11111_22222`, `33333_44444`, `55555_66666`), and `77777_88888` is running under
   `/var/tmp/vtcr-driver/driver.py`. So the half-range bar for P5 **cannot be read
   yet**, and P5 stays at −£300 to +£500 until it can.
2. Candidate A has **not launched**: `/var/tmp/vta-driver/` holds the driver but no output. At
   `a2ed86cf7`, `renewal_belief_by_ending_term` is **False** in `CURRENT_POLICY`. Re-read it at launch.
3. B11 M7 has **not launched**: there is no `/var/tmp/b11m7`, and its own record says it waits on 1 and 2.

So the pair launches after M7 exits, which is at least a day out. The launch is handed on, not
started here.

**Smoke run, `net` arm only, through 2017-12-31, at `a2ed86cf7`** (`/var/tmp/retnet1114/smoke_net.json`).
It produced 69 guard rows and 9 offers. Each offered row's `(billing_account, event_date)` matches
`retention_log` 9 of 9, and no row is missing its keys. The arrears cells are `no_debt` 60,
`worsening` 6 and `in_arrears_steady` 3. **The `None` branch did not fire in 2017** (0 rows), so fix (1)
is in the code but not yet exercised. The full arm will exercise it or show it is never reached.
**One reading that bears on P1, recorded before any pair runs and not used to revise it:** in this
single arm, 15 rows have `offered_unweighted` true and `offered` false, all in 2017, where the belief
is the 2% prior. That is already above P1's 3–12 for the whole book. It is not a matched withdrawal
count: it compares within one arm, with no `off` twin and no path divergence. P1 stands as written.
If the graded pair lands far above 12, the reason is visible here, before the run: at `a2ed86cf7` the
book's 2017 guard rows have thinner headroom than 22 Oct's did.

**Launch scripts drafted, not started:** `/var/tmp/retnet1114/run_both.sh` (off, then net, serial)
and `driver.sh <origin sha>`. The driver pins a locked worktree, goes through
`background.launch_long_job --asserted-live-by` this file, and files the grade continuation. The
seed-61113 replication pair is not in it: it needs M7's book switch, which does not exist yet.

## 14 Nov, 22:37Z: re-read, and the gate is still unmet

Nothing has changed since 22:10Z. `churn_roll`: the same three pairs are on disk, and `77777_88888`
is still running (pid 541133, under the driver at pid 2790906). The family is not graded, so P5
stays at −£300 to +£500. Candidate A: `/var/tmp/vta-driver/` still holds only the driver and grade
scripts, with no output and no process. B11 M7: `/var/tmp/b11m7` does not exist. The launch is
handed on again. One side note for whoever grades `churn_roll`: `/var/tmp/vtcr-out/run.log` is
already 335 MB, with one pair left to run.

## 14 Nov, 22:46Z: still unmet; the re-draw is now held on M7's output directory

Unchanged since 22:37Z. `churn_roll`: three pairs are on disk, and `77777_88888` is still running
(pid 541133, 59 min in, under the driver at pid 2790906). The three finished pairs landed at 15:54,
18:51 and 21:46, about 2 h 55 min apart. The family's own grade continuation is stamped not before
15 Nov 09:30. Candidate A: `/var/tmp/vta-driver/` still holds only `driver.py`, `grade.py` and
their diffs, with no output and no process. B11 M7: `/var/tmp/b11m7` does not exist. P5 stays at
−£300 to +£500.

**Why the hand-on changes form.** This item was drawn at 22:10Z, 22:37Z and 22:46Z, and each draw
could only say "unmet". The chain is serial: the `churn_roll` grade (not before 15 Nov 09:30), then
candidate A (§9: about 1.5 h for one draw, about 19 h for twelve), then M7's six members. The
re-offer is therefore held with the delivery lane's path embargo on `/var/tmp/b11m7`, not handed on
untimed. That directory can only appear after the first two gates have cleared (M7's own launch
condition). Its existence does not mean M7 has exited. The next draw still re-reads gate 3 and
launches only after M7's last member is done.
