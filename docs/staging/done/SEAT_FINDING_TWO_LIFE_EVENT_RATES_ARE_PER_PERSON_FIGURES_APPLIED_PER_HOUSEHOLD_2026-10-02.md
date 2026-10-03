**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# Two life-event rates are per-person figures applied per household

**2026-10-02.** Surfaced while drafting the who-lives-where knowledge page, then checked in the code.

`simulation/life_events.py`:

- **New baby** (line ~180): *"UK birth rate ~10.7/1,000 population ≈ 1.1% per resi household/year"*,
  `_NEW_BABY_ANNUAL_PROB = 0.011`. 10.7 per 1,000 is a rate **per person**. It is applied **per
  household**. At the census mean of about 2.36 people per household, the per-household rate the same
  statistic implies is nearer 2.5%, so the world draws about half the births it should. That is a
  reading of one published statistic, not a sourced per-household rate, and it is not used here as one.
- **Job loss** (line ~173): *"UK annual unemployment entry rate ~2.2% of working-age employed"*,
  `_JOB_LOSS_ANNUAL_PROB = 0.022`. A rate **per employed person** is applied **per household**. The
  right per-household quantity depends on how many employed people live there: zero for a retired
  household, often more than one in a working one. It is a different quantity, and not only a
  different number.

**Why it matters.** Both events move `income_stress`, which feeds payment and arrears behaviour, so the
world under-draws the economic shocks the supplier's collections and vulnerability handling exist to
meet. This is a WORLD fidelity change, to be decided blind to company results.

**What is owed (knowledge first, not a computed constant):** a sourced per-household rate for each, or
an event drawn per person over the household's own composition (the people layer already carries
headcount, children and employment cuts through `dwelling_records.composition_cuts_for`). The
conversion above is a pointer, not the replacement value.

## Resolution, 2026-10-03

**Remedy (the second option: no new number).** `simulation/life_events.py` now draws each event per
person over the home's own composition, read from the same `dwelling_records` draws the demand
model uses (`people_count_for_area`, `composition_cuts_for`). A birth uses the crude rate per
person (10.7/1,000, the cited figure; it had been rounded to 0.011). A job loss uses 2.2% per
employed person. The constants now carry their unit in their names:
`_NEW_BABY_ANNUAL_PROB_PER_PERSON`, `_JOB_LOSS_ANNUAL_PROB_PER_EMPLOYED_PERSON`.

**Live book (164 residential homes, 2.36 people each, 70% with someone employed), 2016-2025:**

| | before | after |
|---|---|---|
| new_baby per household-year | 0.85% (14 events) | 1.83% (30 events) |
| job_loss per household-year | 1.83% (30 events) | 1.34% (22 events) |

**Job loss is a named lower bound, not a fix of the level.** The record carries whether anyone in
the home works, not how many people do. So a working home counts one earner and a workless home
counts none. Ungated per-household probability: 2.20% before; 1.54% at one earner; 2.90% if every
adult in a working home worked. Retired and workless homes no longer lose jobs, which is the fidelity
gain. Multi-earner homes are under-drawn, so on this book the world now draws *fewer* job-loss
shocks than the published rate implies. The figure that closes this is the employed adults per
working household, from the ONS "working and workless households" release. It is not in the
knowledge layer yet, and no multiplier stands in for it.

**A latent defect this made live, closed in the same change.** With births doubled, the W2_5
emission/reconstruction defect (queued 2026-07-24/07-27) went live at PROS-2020-0102. The generator
gated new_baby on stress in processing order, but consumers replay by date.
`_dated_in_gate_order` now dates each year's demographic events in gate order, with substream draws
unchanged. The two strict-xfail invariants pass and are plain controls now.

**Controls.** `tests/simulation/test_a_per_person_life_event_rate_is_drawn_per_person.py`. Each
mutation was applied and reverted, and each went red: a birth rate applied per home; a job-loss
rate applied to a workless home; a composition not read from the world's record. The gate-order
no-op mutation reds three tests in `tests/simulation/test_phase_b_life_events.py`.
