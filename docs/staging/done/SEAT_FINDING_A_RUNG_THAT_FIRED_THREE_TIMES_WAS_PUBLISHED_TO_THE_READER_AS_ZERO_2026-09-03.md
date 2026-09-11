**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# A rung that fired three times was published to the reader as zero

*Delivery seat, 2026-09-03, lane-0. Grades
`SEAT_PREREGISTRATION_WHETHER_A_WALKED_RUNG_THAT_FIRED_IS_PUBLISHED_AS_ZERO_2026-09-03.md`
(R1–R5), filed before the repaired split was computed. Discharges §7 item 3 of
`SEAT_FINDING_THE_OPENING_DD_ESTIMATE_WORKS_AND_NOTHING_PUBLISHED_CAN_SEE_IT_2026-09-03.md`.
Evidence: `tools/dd_opening_arms.py`, `site/capabilities/index.html`, feed
`site/data/dd_opening_arms.json`.*

---

## 1. What was on the page

`site/capabilities/index.html` rendered, to any reader who opened it:

> Ofgem's published typical values — **0** accounts

The truth is that three accounts used it. `C7`, `C8` and `C9` carry no `eac_kwh`, so
`estimate_annual_consumption` resolves all three through `TDCV_TYPICAL` — SLC 27.15's published
fallback doing exactly the job it is in the precedence to do. All three were acquired in 2016, and
all three then lost their opening amount to a **second, independent refusal**: this company holds
no published GB rate before the price cap began in January 2019, so there is nothing to annualise
against.

`tools/dd_opening_arms.py:351` built the split by iterating `est_open` — the accounts that came out
with an **amount**. A rung that fired and then lost its accounts downstream contributed nothing.

**This is the same defect `28865ab63` fixed six hours earlier, on the rung it did not cover.** That
commit abolished a rendered `our own meter reads 0` on exactly this ground — *a rendered zero is a
MEASUREMENT: it says the supplier looked and found none* — and mechanised it for the two rungs in
`NOT_REACHABLE_AT_OPENING`. The third rung is the one that **can** be reached, so it kept a count,
and the count it kept was of a different quantity.

## 2. The name was the whole defect

The internal key was honestly named — `basis_split_of_estimated_accounts`. `publish_view` renamed it
to `basis_split` and handed it to `basis_precedence_view`, whose own docstring calls it the split of
**the precedence**. Nobody wrote a wrong number. A correct count of survivors was published under a
name that promised a count of resolutions, and the page rendered it as the latter.

CLAUDE.md: *"Before measuring a thing, say what it is."* Two events, separated by a refusal:

| | what it counts |
|---|---|
| `n_resolved` | the estimate CAME FROM this rung |
| `n_with_opening_amount` | ...and the household got a direct debit out of it |

They are now separate keys, computed separately rather than one derived from the other by
subtraction, and never summed.

## 3. The repaired numbers

| rung | resolved | got an opening payment |
|---|---|---|
| the industry EAC/AQ handed over at registration | **254** | 142 |
| Ofgem's published typical values | **3** | 0 |

What the reader now meets:

> Walked: the industry EAC/AQ handed over at registration — 254 accounts, of which 142 got an
> opening payment (the rest had no published rate to annualise against); Ofgem's published typical
> values — 3 accounts, of which 0 got an opening payment (the rest had no published rate to
> annualise against).

The 82 refusals were never a mystery — they were already published with their cause. What was
missing is that the refusal lands *after* the precedence has done its job, so reading the split as
the precedence's own scoreboard attributed a rate gap to a consumption source.

## 4. The predictions, graded

* **R1 CONFIRMED.** `tdcv_typical` resolved 3, amount 0. The two counts separate for exactly this
  rung.
* **R2 CONFIRMED.** `registry_eac` resolved **254**, against the 142 published. `N_asked` is 257,
  so `254 + 3` accounts for the whole population and `successor_supply_points()` adds no supply
  point the live population does not already carry.
* **R3 CONFIRMED.** `unavailable` is absent from the split — no account resolves to it.
* **R4 CONFIRMED.** No run-output key moved. `keys_moved` is still exactly
  `annual_dd_review`, `dd_balance_book`, `dd_level_collection_book`; `keys_unmoved_count` still 101;
  refusals still 82/82/0; the paired result still 80 of 96 at −£201.93. The organ was not touched
  and the diff proves it.
* **R5 CONFIRMED, and this is the part worth keeping.** The pre-repair feed was driven through the
  real door: **the whole site suite stayed green on it.** The existing control's walked-rung leg was
  `assert str(row["n_accounts"]) in rendered`, and `"0"` satisfies a substring check against almost
  any page carrying a money figure. The control could not fail on the defect it was written for.

## 5. The controls, each mutation run and reverted

* `tests/tools/test_dd_opening_arms.py::test_a_rung_that_fired_is_never_published_as_a_zero` —
  mutation: `basis_precedence_view` reads `with_amount_split` for `n_resolved` (i.e. the single
  split it used to take). **Reds** `assert 0 == 3`; the other ten controls in the file stay green.
* `site/test_the_opening_direct_debit_comparison_reaches_the_reader.py::test_a_rung_the_estimate_used_never_reaches_the_reader_as_a_zero`
  — mutation: the page renders `n_with_opening_amount` as the rung's count. **Reds.**
* The door control is driven off a **synthetic** feed, not the live one. Keyed to today's numbers it
  would go green the day the population stops containing an EAC-less account — which is when the
  page becomes honest, not when it breaks. It also carries a sole-witness rung that loses nobody, so
  it cannot be satisfied by always printing the caveat.
* `basis_precedence_view`'s second argument is positional and required. A default would let an old
  caller publish one count under both names and the page would read exactly as before, with nothing
  red.

## 6. What this leaves

**`tdcv_typical` is now a walked rung with zero payments, and that is a true statement about a real
population, not a hidden one.** It stays honest without further work: the day the company holds a
dated tariff book reaching before 2019, those three accounts get a direct debit and the second
column moves on its own.

**The generalisable shape, for the catalogue.** A count published under a name that describes a
larger population is indistinguishable from a measurement of that larger population, and a substring
control over a rendered `0` cannot tell them apart. Where a figure passes through two independent
refusals, publish the count at each stage or the reader attributes the second refusal to the first.
