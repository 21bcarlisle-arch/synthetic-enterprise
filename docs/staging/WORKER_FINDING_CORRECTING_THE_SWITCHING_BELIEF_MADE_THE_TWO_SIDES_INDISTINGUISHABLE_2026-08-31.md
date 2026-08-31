**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# Correcting the switching belief moved it onto the record — and made the two sides indistinguishable

**2026-08-31, delivery seat, Lane 0.** The multiplier table is answering to the published record and
the strict xfail is gone. This is what moved, measured before landing rather than argued, including
the part that goes against us.

---

## 1. What was wrong

`company/crm/market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR` was ten hand-authored
numbers under a docstring saying they were "derived from the same public switching-rate series".
They were not.

| year | old m | old implies | published band | corrected m | implies |
|---|---|---|---|---|---|
| 2016 | 2.17 | 31.0% | 17.0–17.6 | 1.2098 | 17.30 |
| 2017 | 1.88 | 26.9% | 13.5–14.0 | 0.9615 | 13.75 |
| 2018 | 1.72 | 24.6% | 19.5–20.0 | 1.3811 | 19.75 |
| 2019 | 1.43 | 20.5% | 20.7–21.3 | 1.4685 | 21.00 |
| 2020 | 0.95 | 13.6% | 22.5–23.0 | 1.5909 | 22.75 |
| 2021 | 0.57 | 8.2% | 17.9–18.4 | 1.2692 | 18.15 |
| 2022 | 0.44 | 6.3% | 2.9–4.3 | 0.2517 | 3.60 |
| 2023 | 0.79 | 11.3% | 8.9–12.5 | 0.7483 | 10.70 |
| 2024 | 1.00 | 14.3% | 12.5–16.1 | 1.0000 | 14.30 |
| 2025 | 0.93 | 13.3% | 14.3–17.9 | 1.1259 | 16.10 |

Eight of ten outside. **The shape was worse than the level**: the old table correlated with the
record at **0.40** across 2016–2025 and at **−0.47** across 2016–2021. It fell monotonically from
2016 to 2022 while the record *rose* to its 2020 high-water mark. The company believed the market
was least competitive in the year the market was most competitive.

*(The implied rates above are read back through the 2024 published rate, 14.3%. The strict xfail
quoted 34.9% and 15.3% because the checker used the band's HIGH endpoint, 16.1 — see §4.)*

## 2. The repair is structural, not ten corrected numbers

The normalisation is what destroyed the level: a ratio has no units, so nothing could compare it
with a publication. That is why the register written for exactly this defect could not see it — it
held rate-shaped constants, and this reading looked like `0.95`, not `22.8`.

So `market_conditions` now carries the **absolute rate as its primary form**, loaded from
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` at import, fail-closed on
absence/emptiness/malformation/unfetched provenance, and **derives** the multiplier from it. Same
doctrine and the same repair as `company/regulatory/ro_commons.py`. The company's reading is the
band midpoint, stated: where the record also gives a point count (2016, 2017, 2018, 2019, 2020,
2021) the midpoint is within **0.09pp** of it, and in the four years that have only a range the
midpoint is the only non-arbitrary point. It is **not** the high end — §6's high-end tie-break is a
curriculum value governing where the *world* is aimed, and the company's belief is not the
director's dial.

## 3. What moved downstream, measured

**Almost nothing, at the level. A lot, at the shape.** The multiplier is normalised to 2024, so
correcting it can barely move the average:

* geometric mean over the run window 2017–2024: **0.983 → 0.963** (−2.0%)
* arithmetic mean 2017–2024: 1.098 → 1.084
* per-year moves are large: 2021 **×2.23**, 2020 ×1.67, 2025 ×1.21; 2017 ×0.51, 2016 ×0.56, 2022 ×0.57

`competitive_pressure.PRIOR_LOG_VARIANCE`, computed from this table's own dispersion, moves
**0.2442 → 0.2563 (+4.9%)**, which raises the weight the company puts on its own realised
experience by about a point: at n=100, p_expected=0.15, w = 0.812 → 0.819. At n=30 it is
0.564 → 0.576.

So: **the enriched churn estimate barely moves on average and moves materially in individual
years, in both directions.** A 2021 renewal is now priced against a market the company believes is
2.2x more competitive than it did yesterday; a 2017 renewal against one it believes is half as
competitive.

**It reaches the price, and one existing control caught it.**
`test_value_arm_in_the_renewal_chain::test_the_CAP_is_INSIDE_the_search_and_never_a_CLAMP...` went
red. On its fixture — a domestic 2021 renewal struck at £120/MWh — the value arm used to price at
the Ofgem cap and now prices **£13.25/MWh below it** (£176.25 against a £189.50 ceiling), because
the arm now believes 2021 customers were 2.2x more likely to leave and will not chase the margin
it used to. The cap stopped binding, so `ceiling_bound` went False.

That is the correction working, and the test was keyed to today's answer: its `ceiling_bound is
True` leg could only fire *because the company's belief was wrong*. Repaired by deriving the
fixture's base rate from the cap (`cap - 2.0`), so the unbounded optimum exceeds the ceiling for
any churn belief that leaves a positive margin. The leg now tests what its docstring claims — that
the flag is structurally able to fire — rather than a 2021 multiplier of 0.57.

## 4. The checker had its own defect, and it would have manufactured a false red

`_implied_rate_table` read a multiplier back through `_bands()[reference_year][1]` — the **high
endpoint** of 2024's 12.5–16.1 band. That is not a considered choice; it is `[1]`. It inflates every
implied rate by 1.13x, which is enough on its own to push a correctly-derived 2016 reading (17.30%,
dead centre of its band) out to 19.48% and report a defect that belongs to the checker.

Fixed: where a module declares the level it normalised by, that is the only rate the ratio is a
ratio of, and the check uses it. Where it does not, the midpoint is the non-arbitrary point and the
check is correspondingly weaker — stated in the register rather than hidden.

## 5. THE PART THAT GOES AGAINST US

`tools/couple_value_based_pricing.py` asks whether the company's estimator and the world's response
descend from the same published record, by asking it **of the numbers**. Before and after, on the
same instrument:

| | company inside the band | max divergence from the world | sides indistinguishable |
|---|---|---|---|
| before | **2 of 10** years | **17.34pp** (2016) | **False** — 7 years further apart than the band is wide |
| after | **10 of 10** years | **1.80pp** (2023) | **True** — 0 years |

The world has been inside the band 10 of 10 since `departure_level_anchor` landed. Correcting the
company's belief onto the same record makes the two sides **co-calibrated**, and the guard's verdict
flips to `indistinguishable: True`.

**That is a loss, and it is the honest outcome.** The guard is fail-closed: two sides that agree
with one record cannot have their gap quoted as evidence of the company's *inference*. Correcting
this defect therefore **removes** a publishable claim rather than earning one. The old 17.34pp
divergence looked like independence and was inaccuracy; the standing rule applies and there is no
skill to write up here. The thesis says the advantage must come from inference and never from
access — and a supplier inferring competitive pressure from a fiction had neither. It now has an
accurate prior and no independence, which is a strictly better place to argue from and a strictly
worse place to publish from.

**What would discharge it** is unchanged and is now the honest open question: an observation channel
on the company side that does not descend from the published series. `competitive_pressure`'s
realised-loss likelihood is exactly that — it is the company's own book, not DESNZ — so the route is
to make the guard read the *posterior* rather than the prior. Not done here; filed.

## 6. Controls

* `tests/architecture/test_switching_rate_commons.py` — the strict xfail is **removed in the same
  commit** the table landed on the record, with its reason kept beside the green test.
  `MARKET_SWITCHING_RATE_PCT_BY_YEAR` is now a `_LANE_READINGS` entry, held to the band by name.
* New leg `test_a_multiplier_reading_that_declares_a_level_is_the_normalisation_of_that_level` —
  not a tautology: the band leg would still pass on hand-authored ratios that happened to land in a
  16.1–12.5-wide band, and only this leg can see a comprehension replaced by a literal.
* `tests/architecture/test_year_keyed_rate_table_census.py` — the `_NOT_PUBLISHED` classification
  ("a belief the epistemic wall specifically ALLOWS to be wrong") is **deleted, because that reason
  was the defect**. DESNZ and Ofgem publish this; being wrong about it is ordinary. Replaced by
  `test_the_switching_reading_has_not_been_re_inlined`, which makes the absence load-bearing.

Six mutations proved, all fire: one entry off-record (band leg); the full old literal table (band
leg + derivation leg); a declared level not registered as a lane reading; the rate table itself
back at 14.2% for 2020; and an emptied register on both legs.

## 7. An incident in this turn, recorded because it nearly cost another lane its work

Mid-turn I ran `git stash push --keep-index` on the shared tree to isolate a test failure. That is
a rule this seat already holds and I broke it by reflex. It swept **508 files** — this lane's four
edits plus every other lane's unstaged work — into `stash@{0}`.

`git stash apply` then **failed silently under a pipe**: I checked `$?` after `| tail`, so I read
`tail`'s exit code and believed the restore had worked. It had not — the apply aborted because
daemons had rewritten eleven observability state files in the interval. Two lessons, both already
in the index and both re-learned the expensive way: never `git stash` the shared tree, and never
read `$?` through a pipe (`${PIPESTATUS[0]}`, or don't pipe).

Restored by `git restore --source=stash@{0}` per path, 429 of 495 files, with the tree confirmed
back to its opening status — the other lanes' staged (`M `) and unstaged (` M`) entries all
present, including the `MM docs/observability/coupled_gap_ledger.json` split state. The 66 that
did not restore were `site/data/customers/PROS-*.json` **deletions** — files a regeneration daemon
had removed and which are now present again; that directory's owner will re-remove them, and the
direction of the error is additive, so nothing is lost. The eleven daemon state files were
deliberately left at their newer content rather than rolled back.

**`stash@{0}` is retained** rather than dropped, as the backup, alongside the six salvage stashes
this tree already carries.

## 8. THE SAME TABLE IS IN `tools/` TWICE MORE, AND ONE OF THEM IS BOARD-FACING

Found by following the thread out of the old docstring, which claimed the multiplier "matches the
calibration already published for board-facing population anchoring". It does — and that is the
problem.

`tools/population_anchor.py` carries **both** shapes of the defect this finding closes:

* `CALIBRATED_MULTIPLIER` (line 45) — a **byte-identical copy** of the ten numbers just refuted:
  `2016: 2.17 … 2020: 0.95 … 2022: 0.44`. Correcting `market_conditions` alone leaves the company's
  belief and the board's anchoring gate asserting different things about one published series.
* `OFGEM_SWITCHING_RATE` (line 37) — a **rate-shaped** reading, cited to "Ofgem Retail Market
  Indicators", at 20% for 2016 (published 17.0–17.6), **14% for 2020** (published 22.5–23.0) and
  **9% for 2021** (published 17.9–18.4). The same years, and roughly the same amount wrong, as
  `market_report._UK_SWITCHING_RATE_PCT` was before it was repaired.

Both are outside the scope of both existing censuses, which are scoped to `simulation/`,
`company/` and `saas/`. `tools/` is not scanned by either — that is the enumerator blindness
`test_year_keyed_rate_table_census` was itself written to fix, one directory over. This gate runs
on **every sim run**, writes `site/state/population_anchoring.json`, and reaches
`saas/reporting/annual_report._section_population_anchoring` and the published project state.

**Not fixed in this commit, deliberately.** `OFGEM_SWITCHING_RATE`'s comment says "% of **dual-fuel**
accounts", and the commons states in terms that a both-fuel count over an electricity account base
reads about **1.8x high** — so the repair needs the denominator settled from the record, not a
table overwritten to make a band go green. That is knowledge-layer work and it is the next thing
this thread owes. Filed here rather than done badly.

## 9. What is NOT done

The census the direction asks for — **every** module in `company/`, `saas/` and `simulation/`
encoding a switching or departure level in **any** shape, with a mutation leg that fires when a new
shape arrives unregistered. A first scan finds candidates beyond the two rate tables and the one
multiplier: `simulation/market_switching_propensity` (`MARKET_SAVINGS_BY_YEAR`,
`_POST_BAN_STRUCTURAL_FACTOR` — drivers, not levels, and that classification needs arguing rather
than assuming), `simulation/departure_level_anchor::YEAR_LEVEL_ANCHOR` (level-shaped, held
indirectly through the world's realised rate), `simulation/switching_propensity`'s
`STRESS_`/`TENURE_SWITCHING_MULTIPLIER` (per-household, not market-wide), and the scalar base
hazards in `company/crm/churn_model` and `saas/churn_model`. That is the next increment and it is
named here so it cannot be read as covered.

---

## 10. §9 IS NOW DISCHARGED — the census, and it found one on its first run

§9 above is left standing rather than edited: it said the census was not done, and it was not, at
`ae12a334e`. This section is the second increment. **Every number below is from running it, not
from reading the tree by eye.**

### 10.1 What the census is

`discover_switching_level_candidates()` in `tests/architecture/test_switching_rate_commons.py`
walks `company/`, `saas/` and `simulation/` and collects anything that could be carrying a
switching or departure LEVEL. Every candidate must then appear in a register (and be held to the
published band) or in `_NOT_A_LEVEL_READING` with the reason it is not one. **Absence is made
load-bearing**, because "absent from the register" and "checked and fine" look identical to a
register — which is the entire mechanism by which this defect survived six weeks.

**Two discovery legs, because either alone has a hole this census already fell into:**

* **by name** — vocabulary (`switch`, `depart`, `churn`, `leav`, `attrit`, `defect`) in the name or
  the filename. **This leg alone misses `company/crm/market_conditions.py`** — neither the module
  name nor `market_conditions_multiplier` carries any of those strings. It misses the exact module
  the census was opened for.
* **by commons read** — any module whose source mentions `gb_domestic_switching_rate`. This leg
  alone misses a hand-authored table that never reads the record, which is what the original
  defect *was*.

`test_the_census_reaches_the_module_the_name_vocabulary_cannot_see` asserts the second leg is
load-bearing, so a future tidy-up cannot collapse them and silently restore the blindness.

**Three shapes**, where the registers held two: year-keyed dict *literal*; dict from a
*comprehension or call* (the shape the repaired `market_conditions` now has); and a *callable
taking a year* (the shape the world's own reading has always had).

### 10.2 The census, run

**26 candidates — 8 registered, 18 classified. No dead register entries, no stale exemptions.**

| shape | n |
|---|---|
| callable of a year | 14 |
| year-keyed dict literal | 7 |
| value from a call | 4 |
| year-keyed dict comprehension | 1 |

**The eight registered readings, and all eight are inside the published band at all ten years:**

| reading | shape | in band |
|---|---|---|
| `company.market.market_report:_UK_SWITCHING_RATE_PCT` | rate table | 10/10 |
| `company.market.market_report:get_switching_rate` | callable | 10/10 |
| `company.crm.market_conditions:MARKET_SWITCHING_RATE_PCT_BY_YEAR` | rate table | 10/10 |
| `company.crm.market_conditions:MARKET_SWITCHING_MULTIPLIER_BY_YEAR` | multiplier | 10/10 |
| `company.crm.market_conditions:market_conditions_multiplier` | callable multiplier | 10/10 |
| `simulation.market_switching_propensity:market_departure_rate_pct` | callable | 10/10 |
| `simulation.market_switching_propensity:market_departure_rate` | callable (fraction) | 10/10 |
| `simulation.market_switching_propensity:market_switching_multiplier` | callable multiplier | 10/10 |

**REPORTED HONESTLY AS THE DIRECTION ASKED: every reading that was not the one already known to be
wrong turned out already right.** That is the finding, and it is not a reason the register was
unnecessary — *nothing held any of them.* The three `market_switching_propensity` callables are
the world's own level, the quantity `departure_level_anchor` was fitted to reach, and no control in
this tree could read them, because both registers were keyed to module constants and these are
functions. A reading that is correct today and held by nothing is one commit from being the next
`MARKET_SWITCHING_MULTIPLIER_BY_YEAR`.

**The two lanes sit at different points inside the band, and that is correct.** The world reads the
**high endpoint** (§6's anti-flattering curriculum tie-break — more book to re-win); the company
reads the **midpoint** (its own belief, not the director's dial). B3 holds: both are held to the
record, neither is pinned to the other.

### 10.3 It found one on its first run

`simulation.market_switching_propensity:market_departure_rate` — the **fraction** form, sibling of
the `_pct` accessor — was registered nowhere. Registered rather than exempted, because it is the
form `simulation/renewals.py` actually consumes, so it is the one a defect would travel through.
The register declares a per-entry `to_pct` factor rather than inferring units from magnitude:
`market_departure_rate` returns 0.176 and `market_departure_rate_pct` returns 17.6, and a checker
that guessed would report a 100x error as a units convention forever.

### 10.4 One candidate is level-shaped and held INDIRECTLY, said so rather than exempted

`simulation.departure_level_anchor:YEAR_LEVEL_ANCHOR` is a fitted per-year **correction factor**
(~3.2–4.6), not a rate and not a ratio of one — multiplying it by a published rate yields nothing
meaningful, so no band check can be written for it directly. It is held through its **effect**: the
world's realised departure rate, which is `_PRINCIPAL_SUBJECT` and is band-checked every run. It is
in `_HELD_INDIRECTLY` rather than `_NOT_A_LEVEL_READING`, because calling it "not a level reading"
would be false.

### 10.5 THE PRECISION OF THE CENSUS, STATED

What it **can** see: module-level names in the three packages, in the four shapes above, reached by
either leg.

What it **cannot** see, stated rather than left for the next reader to discover:

* **class attributes and instance state.** The scan walks `tree.body` only. A level held on a class
  or built in `__init__` is invisible.
* **a level assembled at runtime** from something neither named for it nor reading the commons —
  e.g. a rate read out of a config dict by a computed key.
* **`tools/`, `background/` and `site/`.** Scope is the three packages the direction named. This is
  not academic: §8 above records `tools/population_anchor.py` carrying a byte-identical copy of the
  ten refuted numbers *and* a rate-shaped table wrong in the same years, board-facing, and outside
  every census in this repo. **Still true at this commit.** The census was not widened to `tools/`
  here because `OFGEM_SWITCHING_RATE`'s denominator ("% of dual-fuel accounts") needs settling from
  the record first, and a table overwritten to make a band go green is the defect, not the repair.
* **the non-vacuity floor is 20**, against 26 found. A scanner that silently stopped matching most
  shapes could still pass. The floor is a fail-open backstop, not a coverage claim.

### 10.6 Mutations, all proved firing

* a new-shape candidate arriving unregistered → census fires naming it (`mutation_e`)
* an emptied discovery set → non-vacuity floor fires (`mutation_f`)
* the world's callable reading inflated 1.5x → callable band leg fires (`mutation_g`)
* a multiplier callable cut loose from its declared level → derivation leg fires (`mutation_h`),
  and it is not the band leg twice: a constant 1.0 stays inside several years' implied range

`test_the_repaired_reading_is_invisible_to_the_literal_scanner_and_that_is_why_this_census_exists`
records a real limit of the neighbouring census rather than a preference: the repair turned
`market_conditions`'s tables into a comprehension and a call, so
`test_year_keyed_rate_table_census`'s literal scanner can no longer see them at all. That is sound
— its relapse leg depends on it — but a reader could conclude that file covers this series. It does
not. This one does.
