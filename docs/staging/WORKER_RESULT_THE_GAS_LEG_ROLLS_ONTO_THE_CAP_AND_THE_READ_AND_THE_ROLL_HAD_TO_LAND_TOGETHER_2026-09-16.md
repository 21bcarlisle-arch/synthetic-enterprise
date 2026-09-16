**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the gas tariff_type read becomes the C1b roll now that the 18 can leave"

# The gas leg rolls onto the cap, and the read and the roll had to land in one commit

**2026-09-16, scheduled tick, worker seat.** Repair 2 of the 2026-09-16 tariff-type determination,
landed. Repair 1 (`9fd8ca3c3`, a departure route for a gas-only billing account) was confirmed an
ancestor of `origin/main` before anything was built, so the premise held and was not spent.

---

## The premise check turned up something first: the tree was five commits behind origin

`git rev-list --count HEAD..origin/main` was **5**, and `simulation/run_phase2b.py` in the shared
working tree was repair 1's *predecessor*. Editing that copy would have landed a commit whose
message says "repair 2" and whose diff reverts repair 1 — the atomic-revert shape. The stale
working-tree copy of `simulation/customer_events.py` (another lane's, still uncommitted) also
**lacks `departure_decision_leg` entirely**, so the shared tree could not import
`run_phase2b` at origin's content at all.

`background.origin_reconcile` refused to advance, correctly, naming that one path. The fork was
closed with `surgical_land --merge origin/main` (`fa4790b32`), which computes the merged tree by
plumbing and never opens the shared index, and all the work below was then built and measured in
an isolated extract of that tree rather than in the shared worktree.

## What was built

Four things, and the first two are one change that cannot be split:

| what | where |
|---|---|
| `resolved_tariff_type`'s commodity split **deleted** — both fuels now `record.get("tariff_type") or "fixed"` | `simulation/run_phase2b.py` |
| the **C1b roll on the gas leg** — at each non-first resi fixed boundary, `rolls_active_renewal` decides shop-or-roll and a passive answer emits cap-period segments to the household's next anniversary | `_build_gas_renewal_schedule` |
| `build_svt_schedule` **fuel-parameterised**, `fuel` required and keyword-only with no default | `simulation/svt_product.py` |
| `get_svt_gas_rate_charged_to_household_gbp_per_mwh` — the gas twin the module's own docstring had briefed as "two lines over `binding_cap_unit_rate_gbp_per_mwh_inc_vat`" and deferred for want of a caller | `simulation/svt_rates.py` |

**Why one commit.** `or "fixed"` alone IS the blanket-fixed that
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused on 2026-08-28 — every gas leg on a
fixed deal for its whole tenure against a published domestic fixed share of roughly a third. It is
only an *opening term* because the roll decides every boundary after it. Landing the line first
and the roll later would have put the refused shape into the world for however long the gap was,
under a commit message saying the determination had been honoured.

**No new rule and no new constant.** Same `rolls_active_renewal`, same seed grammar
(`{household}_{rows emitted so far}`), same anchored 35% population rate with the same
per-household engagement archetype, same `FTC_WITHDRAWAL_WINDOW` forcing. What repair 2 had to
build was the fuel, not the decision.

## The numbers, printed at real inputs before the formula shipped

The gas twin against the cap leg, £/MWh inc-VAT, at every published cap-period start — identical
outside the Energy Price Guarantee and split inside it, with `cap = charged + receipt` closing on
every row:

| date | gas cap | gas charged | HMT receipt |
|---|---|---|---|
| 2016-01-01 | 40.0 | 40.0 | 0.0 |
| 2022-07-01 | 73.7 | 73.7 | 0.0 |
| **2022-10-01** | 147.6 | **103.2** | 44.4 |
| **2023-01-01** | 170.8 | **103.2** | 67.6 |
| **2023-04-01** | 126.1 | **103.2** | 22.9 |
| 2023-07-01 | 75.1 | 75.1 | 0.0 |
| 2025-04-01 | 69.9 | 69.9 | 0.0 |

103.2 is the published 10.32p/kWh gas EPG against a 17.08p cap — the figure
`simulation/svt_rates.py`'s own docstring had been quoting as the reason the twin was owed.

A 24-household synthetic cohort driven through the repaired builder over 2016–2025, sampled on
1 July each year — the **generated** fixed share, not an input:

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed share | 1.00 | 0.42 | 0.50 | 0.42 | 0.25 | 0.29 | 0.00 | 0.00 | 0.33 | 0.38 |

2016 is the burn-in every account opens fixed into and must not be fitted; 2022–23 is the FTC
withdrawal window doing what it does on electricity. 2024–25 at a third is the neighbourhood the
determination's published anchor names. **This is a check on the output and is not asserted
anywhere** — a control pinning a year's share would be keyed to today's answer.

## One defect the work found in itself

`build_svt_schedule` calls `generate_forward_price` unguarded, while the gas builder's fixed path
has always answered "the NBP series ran out" with `break`. A gas SVT stint past the end of the
feed would therefore have raised out of the whole run where a fixed term ends the schedule
quietly. Caught by a control written with `REPORT_END = "2025-12-31"` before the world's own
`REPORT_END` (2025-06-07, derived from where the series stops) was read. The C1b branch now
answers with the same `break`: *"the price history ends here" is one fact about the world and it
cannot have two answers depending on which product the household happens to be on.*

## Controls

`tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` — nine, each
naming its own defect, each mutation-proven against a COPY of the world file with the **observed**
result recorded rather than the intended one. Two of the five mutations refuted my prediction and
both are written up in the file's docstring:

* deleting the C1b block reds **6**, not the 3 predicted — and three of those six fail for lack of
  a SUBJECT (with no `svt` term anywhere, the rate control and the replay control have nothing to
  look at) rather than on the property they assert. Weaker evidence, recorded as such.
* reverting `resolved_tariff_type` to the pre-repair split reds **1**, not 2. The whole-book label
  control stayed GREEN because the four founder gas legs (`C1g`..`C4g`) carry no `tariff_type`
  **key at all**, so the defeated spelling reaches its default on them, they roll, and `svt` is
  still in the book. A control over a union cannot see a defect that spares four accounts — which
  is why the opening-term leg is asserted per leg.

`test_the_two_commodities_are_read_differently_and_that_is_the_finding` is **deleted**. Its own
docstring set that contract: *"when the gas fidelity determination lands and the difference goes
away, that control goes red and is deleted with the finding it records, rather than silently
passing on a world that got better."* It went red on the repair and
`test_the_two_commodities_are_now_read_the_same_way_on_purpose` stands in its place, with a third
leg — a record that NAMES its product keeps it — so the read cannot decay into a constant.

93 of 94 green across the eight SVT/renewal/tariff suites.

## Two reds this landing did not cause, and what happened to each

**`test_svt_product.py::test_an_account_on_the_svt_product_can_leave_it` was red at HEAD** on
`len(ELEC_CUSTOMERS) >= 140` against a roster of 136. Proven pre-existing in a clean `git archive
HEAD` extract with no edits applied, so it is not this landing's — but a red commit is
structurally impossible here, so it was refusing every lane, and leaving it was not an option.
Measured rather than argued: 9 founder + 46 drawn + 81 won today against 9 + 51 + 90 on
2026-08-30. **Nothing was deleted** — the two that moved are both GENERATED, so the floor was a
count over today's answer, which is the failure its own comment warned against. Re-keyed to the
property (is there any resi household the C1b roll can reach?) rather than lowered, and
mutation-proven. Full reasoning, including the second defect — the floor's stated justification
was false of the assertion it sat under, which never reads the roster — in
`docs/staging/WORKER_FINDING_THE_SVT_POPULATION_FLOOR_IS_RED_AT_HEAD_BECAUSE_THE_ELECTRICITY_ROSTER_LOST_FOURTEEN_LEGS_2026-09-16.md`.

**Four in `test_run_phase2b.py` WERE this landing's**, found by the gate and not by me — a lesson
recorded as one. Their gas fixtures carry no `customer_id`, which this builder never read until
today; the C1b roll reads it through `household_of`. The builder now REFUSES such a record by
name rather than skipping the roll, because skipping it would give that leg a fixed tenure and no
surface would say why. `test_gas_schedule_notice_date_is_42_days_before_term_start` needed more
than a fixture: it looped over every row asserting a 42-day notice, and a cap-period segment
correctly has none. It is not narrowed to fixed terms — a narrowing added for a false positive can
only hide, and it would hide a fixed term losing its notice. Both partitions are asserted and both
are asserted NON-EMPTY.

## What this does NOT claim

**The 158 are not admitted yet.** That needs a run: the world must be re-run and
`run_value_cycle_ab`'s funnel regenerated before anything can be said about the value arm's
population. Nothing on any published surface has moved.

**The net sign is still not predicted, and that is deliberate.** Repair 2 done honestly moves a
large share of the 90 resi gas legs onto SVT, which SHRINKS the priced population, while the 158
enlarge it. Two effects in opposite directions; a verdict claimed now would be a prediction filed
after its answer was available to me and before it was measured.

## A named simplification, stated because it is real

`household_of` strips the gas-leg suffix, so a dual-fuel household's two legs reach their FIRST
boundary with the same household key and the same row count and roll the **same answer** — right,
because a household that shops, shops. Once either leg emits a different number of rows (an SVT
stint emits one row per cap period, a fixed year emits one), the counts diverge and the two legs
decorrelate. That is not defended as fidelity. It is the cost of mirroring electricity's grammar
exactly rather than minting a second one, and it is strictly closer to the truth than what it
replaces, which was gas never rolling at all. Keying the seed on the boundary DATE instead would
correlate the legs for a whole tenure and is the obvious repair — it moves the electricity world,
so it is a determination and not a tidy-up.

## What is owed next

1. Re-run the world and regenerate the value-arm funnel; report the 158 admitted, the SVT-route
   gas departures (0 at HEAD, because the branch had no gas subject), and the sign nobody has
   predicted.
2. `tools/svt_generated_share_check.py` on the repaired book, both fuels. The electricity finding
   (`SEAT_FINDING_THE_WORLDS_FIXED_DEAL_SHARE_IS_OUTSIDE_THE_PUBLISHED_BAND_IN_EVERY_YEAR_2026-09-04.md`,
   LATENT) now has a gas leg to be measured against the same band.
3. The seed-decorrelation determination above, if it is ever worth the electricity move.
