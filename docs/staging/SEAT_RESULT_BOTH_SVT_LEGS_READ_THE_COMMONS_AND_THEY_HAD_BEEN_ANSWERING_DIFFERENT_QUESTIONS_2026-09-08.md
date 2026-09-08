**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census

# Both SVT legs read the commons, and the two fuels had been answering different questions

**2026-09-08. Lane 0 delivery.** Claim:
`the-electricity-svt-leg-reads-the-commons-and-the-epg-rows-move-alone`.

Pre-registration: `docs/staging/PREREG_WHAT_THE_ELECTRICITY_SVT_LEG_READING_THE_COMMONS_MOVES_2026-09-08.md`,
written before any measurement and left unedited. Predecessor:
`docs/staging/SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_IS_A_SECOND_HOME_2026-09-08.md`.

---

## The item asked for the wrong move first, and the tree already said why

The drawn direction was: set the three EPG rows (2022-10, 2023-01, 2023-04) to what the commons
returns as the **binding** instrument — 34.0p/kWh — as the one-variable version.

**The EPG lowered the household's bill and did not lower supplier revenue.** HM Treasury paid the
supplier the difference. This tree states the scheme in its own words, in
`company/regulatory/epg_reconciliation_register.py` lines 6–12, and **that register has no
production caller** — grepped: its only importer is its own test module. So the world has no HMT
receipt leg, and billing `simulation/svt_product.py` at 34.0p would have taken roughly half the unit
revenue out of Oct-2022–Jun-2023 and called it fidelity, in the three quarters that carry the most
weight in the whole 2016–2025 record.

The real defect was one level up. **`get_svt_elec_rate_gbp_per_mwh` was being read as three
different quantities** — the published cap (`competitor_reference`, in its own docstring), what the
supplier bills (`svt_product`), and what a switching household compares against (`customer_events`).
Outside those three quarters they are the same number, so nothing ever had to choose. Inside them
they differ by 33p/kWh. CLAUDE.md's shape exactly: *the cause split follows from the definition,
never the reverse.*

## What was found on the way, and it is worse than the item described

**The two fuels were answering different questions in exactly those three quarters.** The gas leg,
landed 2026-09-06, read `binding_cap_unit_rate_gbp_per_mwh_inc_vat` — the EPG-selected 103.2 — while
the electricity table carried the cap. One field, `svt_rate_gbp_per_mwh`, written into account state
by `run_phase2b` for both fuels, holding two different quantities, differing only where it matters,
and nothing in the tree able to notice. The module's own docstring says one basis for both fuels is
"the whole point"; it had the basis right and the *instrument* wrong.

**`simulation/svt_product.py` cited a control that has never existed.** Its duplicated
`CAP_PERIOD_START_MONTHS` carried the comment *"the duplication is one tuple and
`test_the_segment_starts_match_the_published_series` fails if the two ever disagree"*. That test is
in no file in this tree. The duplication was unguarded for as long as it stood, under prose saying
it was not.

**A control was pinned to a typo.** `test_svt_product.py` asserted the Jan-2023 peak equalled
`670.0` — a transcription of the 674.7 cap. Making the series honest turned it red. That is a
control going red because the code became *more* correct, which is the direction CLAUDE.md names as
backwards, and it is now keyed to the publication instead.

## What landed

Both legs delegate to the commons for the capped years; only 2016–2018 remain tables, because there
was no cap to read before 2019.

* `simulation/price_cap_enforcement.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat` — new: the Ofgem cap
  row alone, no EPG selection. Two named accessors rather than a flag, so a caller has to write down
  which quantity it wants. The carry-forward rule is factored into `_window_for` so the two readings
  cannot drift apart.
* `simulation/svt_rates` — the post-cap electricity table is **gone**, including the invented
  "moderate decline as renewables penetration rises" series that stood across 2026–2029 exactly
  where the commons publishes Ofgem's cap level model v1.31. Both accessors answer the cap. The EPG
  question is answered **in words, in the module**, which is item 2 of the predecessor's list.
* `simulation/svt_product` imports `CAP_PERIOD_START_MONTHS` instead of duplicating it. Deleting a
  duplication beats guarding it.
* `tests/simulation/test_the_elec_svt_leg_reads_the_commons.py` replaces
  `test_the_elec_svt_table_agrees_with_the_published_cap.py`, whose subject no longer exists. Seven
  controls; the load-bearing one **perturbs the commons and requires the accessor to follow**,
  because a value assertion cannot tell a delegation from a literal that agrees today — the exact
  survival the `vat_book` repair recorded this morning.

## The prediction, and it was confirmed

P1 said the accessor would move on eight named spans and on no others. Enumerated day by day across
2016-01-01..2029-12-31 against the HEAD implementation: **exactly the predicted spans moved, and
every span predicted unchanged was unchanged** — all of 2016–2019, 2020-04-01..2022-12-31, and
2024-04-01..2025-12-31.

| span | from | to |
|---|---|---|
| 2020-01-01..03-31 | 178.1 | 178.5 |
| 2023-01-01..03-31 | 670.0 | 674.7 |
| 2023-04-01..06-30 | 301.0 | **506.0** |
| 2023-07-01..09-30 | 301.0 | 301.1 |
| 2023-10-01..12-31 | 274.0 | 273.5 |
| 2024-01-01..03-31 | 274.0 | 286.2 |
| 2026 (4 windows) | 260.0/255.0/250.0/255.0 | 276.9/246.7/261.1/263.2 |
| 2027-01-01..2029-12-31 | 250.0 declining to 220.0 | 263.2 throughout |

Gas moves too, in the three EPG windows only: 103.2 → 147.6 / 170.8 / 126.1.

The published diagnostics stay coherent: `historical_discount_pct` and `anchor_rate_gbp_per_mwh`
move by exactly the SVT delta (the discount is savings/SVT, so it cancels), 2023 anchor 663.0 →
667.7, 2024 anchor 263.4 → 275.6.

## What is NOT established, said plainly

**The book was not measured.** A `--fast` full run at HEAD reached 2016-02-29 in four minutes; the
decade is ~4 hours and before/after is ~8. P2 — revenue rises, concentrated in Q2-2023; churn falls
slightly there; 2016–2019 bit-for-bit identical — **remains a prediction**, filed before the change,
and 2024/2025 moves were pre-registered as unattributable because eight rows moved at once.

**The household-charged gap is now larger and named rather than accidentally masked.** 2023-04 moved
from 30.10 to 50.60, away from the 34.0p a household actually paid. P3 registered this before the
measurement: 30.10 was the *Jul-2023* cap sitting in the Apr-2023 slot, and its nearness to 34.0 was
a coincidence, not a mitigation.

## What is next, in order

1. **The before/after book run**, 8 hours of compute, against the P2 predictions above. It is the
   only thing that can refute them.
2. **Wire the HMT receipt leg**, then add the household-charged accessor and re-point
   `customer_events._price_differential_vs_market` and the churn reference at it. Those two are one
   atom: either alone moves the crisis quarters in the wrong direction.
3. **`binding_cap_unit_rate_gbp_per_mwh_ex_vat` divides every row by 1.05**, and the commons
   artefact's own `basis` block says electricity is **zero-rated 2026-10-01..2027-03-31** and that
   *"a reader dividing any row here by 1.05 to recover an ex-VAT figure is wrong for that row"*. The
   settlement clamp reads that accessor. Found in passing, not repaired here, and it is a live
   ex-VAT error on a published row from 2026-10-01.
4. Items 3 and 4 of the predecessor's list — `company/pricing/ofgem_price_cap.py`'s basis, and the
   census's `by_year` token weakness — remain open and unchanged.
