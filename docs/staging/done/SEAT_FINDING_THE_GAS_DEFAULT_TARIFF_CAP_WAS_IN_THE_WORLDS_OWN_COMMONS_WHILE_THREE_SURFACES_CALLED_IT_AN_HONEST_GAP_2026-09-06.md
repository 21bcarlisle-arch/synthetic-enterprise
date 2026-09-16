**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The gas default-tariff cap was in the world's own commons while three surfaces called it an honest gap

**Found and fixed:** 2026-09-06, delivery seat, claim
`the-decision-instrument-is-electricity-only-on-a-book-that-is-half-gas`. Drawn as lane-0 direction:
*"Fit the renewal arm to gas: establish from the published record what a gas renewal decision is and
how it differs (there is no gas default-tariff cap in `simulation/svt_rates`, which is also why the
ceiling's `svt_rate_gbp_per_mwh` stops at 146 of 164 households)."*

The direction's parenthesis is true of `simulation/svt_rates`. It is false of the tree, and the
direction inherited the claim from the code rather than from the record.

---

## The defect

Three surfaces stated, as an established fact and in the language of an honest gap, that no published
gas equivalent to the electricity default-tariff cap existed:

| where | what it said |
|---|---|
| `simulation/svt_rates.py` docstring | *"UK domestic SVT ... **electricity** unit rates"* — the module has only ever had one fuel |
| `simulation/run_phase2b.py`, account-state writer | *"**ELECTRICITY ONLY, and that is the honest shape rather than a gap**: `svt_rates` publishes the electricity default-tariff cap and there is no gas equivalent in it"* |
| `tools/r1_inference_ceiling.py`, `OBSERVABLE_FIELD_SCOPE` | *"the published default-tariff cap on the day — electricity only, **because `simulation/svt_rates` publishes no gas equivalent**"* — and this one is **published**, in `docs/observability/r1_inference_ceiling.json`, as the field's own reason for 146-of-164 |

The Ofgem cap has always covered both fuels — the instrument is the **Domestic Gas and Electricity
(Tariff Cap) Act 2018**, and the fuels are in its title. The world's own regulation commons,
`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`, has carried the
**gas leg per published window since W3_1b**, at exactly the granularity of the electricity leg — 21
windows, `{"from": "2019-01-01", "to": "2019-03-31", "elec": 165.2, "gas": 37.3}` — and
`simulation/price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh_inc_vat("gas", d)` has been the
world's reader for it the whole time. `docs/market_research/svt_rates_active_passive_2016_2025.md` §1
carries the pre-cap years too, at the same M confidence as the electricity rows already in the module.

**Nothing pointed the reader at either.** This is the shape of the £55 acquisition cost exactly: a
sourced figure and a declared gap about the same subject, both in the tree, neither aware of the
other — CLAUDE.md, *"the answer is usually already here"*.

## What it cost, measured

On `docs/reports/run_output_latest.json`:

| | count |
|---|---|
| `account_state_log` rows | 2,098 |
| of those, gas | 449 |
| gas rows carrying `svt_rate_gbp_per_mwh` | **0 of 449** |
| households with the field in no term at all | **105** |
| of those 105, gas-only | **105 of 105** |

Not one of the missing households was missing for any reason but this. In the R1 ceiling's own
164-household book that is the 18 gas-only accounts, and `svt_rate_gbp_per_mwh` is one of the **six
fields in `whole_book_pair_rung`** — so a coverage figure the instrument published as *the field's
own truth* was a missing read, on the rung that gates R3 and R4.

**This is the second time on this instrument that a refusal read as a fact about the book.** The
first was the leg-as-household count fixed earlier today
(`SEAT_FINDING_THE_R1_CEILING_COUNTED_A_HOUSEHOLDS_GAS_LEG_AS_A_SECOND_HOUSEHOLD...`). Both defects
are the gas leg, and neither was visible from the rung that reported the number.

## The repair

**The post-cap series is READ, never restated.** `simulation/svt_rates.get_svt_gas_rate_gbp_per_mwh`
delegates 2019-onward to the commons, so the published cap keeps one home; only 2016–2018 is a table
here, because before January 2019 there was no cap to read and the rate was supplier discretion —
which is exactly the basis the module's own 2016–2018 electricity rows are carried on. The three
pre-cap values are the **midpoints of the published ranges** in the market-research table, the same
treatment `_SVT_ELEC_PENCE_PER_KWH` already applies to its own pre-cap rows.

`run_phase2b` dispatches per fuel. The warning the old comment carried is honoured rather than
dropped: writing the *electricity* cap against a gas leg would be a spread between two commodities.
Writing the *gas* cap against a gas leg is the quantity the field was always meant to be.

Printed at real inputs before shipping, against the source table (p/kWh):

| | 2016 | 2017 | 2018 | 2019-01 | 2020-10 | 2022-04 | 2024-04 | 2025-10 |
|---|---|---|---|---|---|---|---|---|
| gas, this module | 4.00 | 2.80 | 3.75 | 3.73 | 3.00 | 7.37 | 6.04 | 6.29 |
| source §1 | ~3.8–4.2 | ~2.1–3.5 | ~3.5–4.0 | 3.73 | 3.00 | 7.37 | 6.04 | 6.29 |

Where the EPG was in force the commons returns `min(ofgem, epg)` — Oct 2022 gas reads 10.32p, not
the source table's headline 14.76p. That is the rate that actually bound, and it is the commons'
rule rather than a choice made here.

**What the wiring delivers**, computed by applying the new dispatch to the 2,098 real rows:

| | before | after |
|---|---|---|
| rows carrying `svt_rate_gbp_per_mwh` | 1,649 | **2,098 (all)** |
| households carrying it (log-wide) | 146 | **251 (all)** |
| rows carrying a `rate_vs_svt_pct` spread | 1,649 | **2,098** |

The 449 new gas spreads have median **−10.7%** (range −58.9% to +303.6%): the book's gas fixed rates
sit about a tenth below the cap, which is the direction and magnitude a real supplier's fixed gas
book sits at against the default tariff.

## The controls, and the poison round that proved they can fire

`tests/simulation/test_svt_rates.py`, four new controls each naming its own defect. Each mutation
applied in place and reverted; baseline 29 green before and after:

| mutation | red |
|---|---|
| gas accessor forwards to the electricity accessor | **3** — `..._is_NOT_the_electricity_series`, `..._IS_the_commons`, `..._PUBLISHED_band` |
| pre-cap branch deleted (gas answerable only from 2019) | **3** — `..._answerable_for_EVERY_year_of_the_record`, `..._PUBLISHED_band` |
| 2017 midpoint moved to 4.00p, off its published band | **1** — `..._PUBLISHED_band` |
| post-cap series restated as a local table | **3** — `..._has_no_SECOND_home_in_this_module`, `..._IS_the_commons` |

The first mutation is the reachability floor: a gas accessor that merely forwards to electricity
passes every other test in the block.

## What is NOT in this commit

**The third surface — `tools/r1_inference_ceiling.py`'s `OBSERVABLE_FIELD_SCOPE` — is corrected in
the shared working tree but is NOT in this commit.** Another lane holds that file with 21 uncommitted
hunks (the R1 magnitude work), and the single hunk carrying my ten lines carries fifty of theirs with
it: `isolate_hunks --keep` cannot separate them, and landing into a file another lane holds dirty
wedges the shared tree's fast-forward. The correction sits in the working tree and will land under
whoever lands that file. **Until it does, the published `r1_inference_ceiling.json` keeps stating
`"because simulation/svt_rates publishes no gas equivalent"` as the field's reason while the world
underneath it writes the value** — so the next run reads full coverage against a stale explanation.
That is the one loose end here and it is named rather than left for a reader to find.

## What is NOT fixed, and is a separate finding

**`rate_vs_svt_pct` divides an ex-VAT unit rate by an inc-VAT cap**, on both fuels. Every rate this
codebase settles is ex-VAT; the published cap is inc-VAT at the domestic 5% rate, which
`price_cap_enforcement` states in as many words and offers an `_ex_vat` accessor for. The spread
therefore carries a **−4.76% bias**. That bias is pre-existing on the electricity leg and this change
does not introduce it — gas is deliberately written on the **same** basis so the field stays one
quantity rather than becoming two. Filed rather than fixed here because correcting it moves a
published electricity figure and needs its own before/after.

**The renewal arm is still electricity-only.** `UPLIFTABLE_COMMODITY = "electricity"` in
`company/crm/customer_profitability.py` still refuses 346 of the world's 1,953 offered renewals as
`not_the_arms_commodity`. This finding is the **precondition the direction named** — the published
gas cap the arm's ceiling would run under now exists and is readable — not the arm itself. The gain
in *independent* decisions must still be measured rather than assumed from the 346, because 87 of
the book's 164 accounts are dual-fuel.

## Why nothing could see it

A comment that says *"and that is the honest shape rather than a gap"* is the most expensive kind of
wrong in this repository, because it closes the question. Two of the three surfaces above were
written by sessions doing the right thing — naming a limit instead of inventing a number — and the
limit they named was of the module in front of them, never of the record. The published-evidence
rule has a direction: **check the commons before writing down that the commons is silent.**

---

## Addendum, 2026-09-06 (scheduled tick, lane-0 claim `r1-ceiling-needs-coverage-not-correction`)

The above sat uncommitted in the shared tree. This is the landing, plus the two things the tree's
copy was still missing.

**The dispatch is now reachable.** It was an inline conditional inside `_main`'s term loop, where
the only route to it is a decade-long run — so the branch that had been silently wrong for the whole
book had no control on it and could not get one. It is now
`simulation/run_phase2b._account_state_svt_rate(commodity, term_start)`, module level, called from
the same place. `svt_rates` declines to publish a `get_svt_rate(fuel, date)` of its own, deliberately
and in writing, so the dispatch belongs to the record that needs it and is named for that record.

**The portfolio-position leg travels with it and had the same shape.** `mean_recent_margin_rate` and
`portfolio_premium_pct` reached 149 of 164 households because `dynamic_pricing_log` wrote them only
where the premium cleared `1e-6` and moved a rate — a continuously-held reading recorded as an
event, the same accounting accident as `company_eac_kwh`. `company/pricing/renewal_rate_chain.py::
portfolio_position` is the one implementation both writers now read.

**New control: `tests/simulation/test_account_state_record.py`**, in the world's own test tree rather
than the instrument's, because these are properties of the record and not of the thing that reads it.
Six mutations, each applied in place and reverted; baseline 8 green before and after:

| mutation | verdict |
|---|---|
| gas leg answered `None` (the original defect) | **KILLED** (2) |
| gas leg answered the ELECTRICITY cap (the warned-against fix) | **KILLED** (2) |
| unknown fuel falls back to electricity | **KILLED** (5) |
| `account_state_log.append` moved under `if term_index >= 1` | **KILLED** (1) |
| `_position` read gated by a ternary | **KILLED** (1) — *survived the first draft* |
| `_position` read moved under an `if` | **KILLED** (1) |

The fifth is the one worth keeping. The first draft asserted that an assignment to `_position` was a
statement of the loop's own body, which `x = None if gate else f(...)` satisfies while reinstating
the gate inside the expression. The control now asserts the assigned VALUE is a bare call. Had the
poison round not been run, that leg would have read as proving the property and proved only that a
line existed — and a gated `_position` is worse than an absent one, because it would carry the
PREVIOUS iteration's reading, taken on a different customer's book.

Printed at real inputs before shipping, £/MWh inc-VAT at 1 June each year:

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| elec | 140.0 | 140.0 | 152.5 | 185.6 | 178.1 | 189.5 | 283.4 | 301.0 | 245.0 | 270.3 |
| gas | 40.0 | 28.0 | 37.5 | 41.4 | 35.0 | 33.4 | 73.7 | 103.2 | 60.4 | 69.9 |
| ratio | 0.286 | 0.200 | 0.246 | 0.223 | 0.197 | 0.176 | 0.260 | 0.343 | 0.247 | 0.259 |

2015 is `None` on both fuels; an unnamed fuel is `None`. The ratio never approaches 0.5, which is
where the ordering control sits, so it is keyed to the two series being told apart and not to a
value.

**A correction to the entry above, in the ratchet.** The tree's uncommitted `RUFF_BASELINE` said
`I001: 1318` and claimed the whole `-1` was this commit's. It was not: measured in a `git archive
HEAD` extract overlaid with exactly this commit's files, clean HEAD censuses 1319 and this commit
1317 — **two** of its own, `test_svt_rates.py` and `svt_rates.py` one each. The shared tree reads
1316, and that third `-1` is another lane's uncommitted fix. Freezing the dirty tree's number would
have banked it and redded the live-tree control the moment that lane landed alone — which is the
error the replaced entry's own comment warned against, committed by the entry itself.

**Still not in this commit, unchanged from above:** `tools/r1_inference_ceiling.py`. The shared
tree's copy predates HEAD's stability rung and a pathspec land would delete `verdict_across_runs`,
`_reduce_runs`, `recent_run_outputs` and ten of HEAD's controls — see
`SEAT_FINDING_THREE_SHARED_TREE_FILES_CARRY_A_REWRITE_FROM_BEFORE_THE_STABILITY_RUNG...`. So the
world now writes the value while the instrument's published reason still says gas has no equivalent.
That is a read-side lag of one landing, and it is named here rather than left to be found.
