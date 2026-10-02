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
