**Severity:** LATENT · **Lane:** B_commercial (world side: `simulation/`) · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon (upstream world fidelity)
**Evidence:** `docs/staging/records/SEAT_PREREG_WHAT_THE_WORLD_DOES_AT_A_FIXED_TERM_END_AND_AT_AN_SVT_ANNIVERSARY_2026-10-01.md` (landed `acc9abc37` before the reading); `/var/tmp/se-ptm-out/analyse.py` over `/var/tmp/se-pb4-shock-out/run.log` (md5 `63452795f4a10c0b0e1634c0776a1255`)

# The passive term end needs no departure roll, and the SVT anniversary adds a second exit route

**2026-10-01, delivery seat, claim `a-passive-fixed-term-end-is-a-decision-point-in-the-world`.**
This answers `WORKER_FINDING_THE_WORLD_ROLLS_NO_DEPARTURE_AT_A_PASSIVE_FIXED_TERM_END_THOUGH_THE_LICENCE_MAKES_IT_A_DECISION_POINT_2026-10-01.md`
(moved to `done/` with this commit).

## Answer

1. **The item's premise does not hold.** Passive means the household did nothing at its term end,
   and nobody leaves by doing nothing. In the world, an exit at a term end is an outcome of the
   active branch. The licence makes the **term end** a decision point. That is P(active) ×
   P(exit | active), and it is not a second exit owed to the passive branch. Adding a passive roll
   would count one exit route twice. **No roll was added.**
2. **The "65% of term ends" was mostly not term ends.** 64.8% of `rolls_active_renewal` draws fall
   at the anniversary of a household already on SVT. In law that is not a decision point.
3. **The SVT anniversary duplicates the C1b hazard, in the direction that is harder on the
   company.** Measured, not changed.

## The numbers: one world, `aed6bf966`, world code byte-identical to HEAD, electricity leg, resi

| Boundary | n | active | passive | exit |
|---|---|---|---|---|
| Closes a fixed term, outside the FTC window | 144 | 29 (20.1%) | 95 (66.0%) | **20 (13.9%)** |
| Closes a fixed term, inside the window | 13 | 0 | 13 | 0 |
| SVT anniversary, outside the window | 219 | 28 (12.8%) | 176 (80.4%) | 15 (6.8%) |
| SVT anniversary, inside the window | 70 | 0 | 70 | 0 |

14 boundaries were unclassifiable because the run ended inside the next term. 3 of the 38
`[CHURN]` lines fall off an electricity anniversary and are not counted. Among the 49 households
that acted at a fixed end, 41% left. In the trial it was 6 of 19, or 32%.

**Before / after exit count at term ends, on this world:** 20 of 157 fixed ends before, and 20 of
157 after. The world was not changed, because the pre-registered rule said not to change it: the
exit rate at fixed ends outside the window (13.9%) is at or above the published 6% floor (Ofgem
2019 End of Fixed Term trial, external switching in six weeks, on a 17-year-tenure book selected
for high roll-over).

**What this does NOT establish.** That 13.9% is the right size. A small supplier's switched-in book
has no published term-end rate, and `FIRST_RENEWAL_DEPARTURE_PRIOR` stays `None`. The world's
figure comes from the 35% active anchor, which is a structural inference, times the churn physics.
All this shows is that it is not under the only published floor.

## Predictions against results

| | Predicted | Got | |
|---|---|---|---|
| P1 | SVT anniversaries ≥30% of draws | 64.8% | held |
| P2 | Fixed-end passive share outside the window, 55–75% | 66.0% | held |
| P3 | Fixed-end exit outside the window, 8–18% | 13.9% | held |
| P4 | Anniversary-route exits ≥25% of `[CHURN-SVT]` | 15 / 52 = 29% | held |

## The duplication, measured (item's second question)

On 360.2 SVT account-years:

- The C1b inertia route gave 52 exits, **0.144/yr**.
- The anniversary route (an active re-draw, then the renewal churn roll against the last *fixed*
  rate, because `prev_elec_unit_rates` is not updated on SVT) gave 15 exits, **0.042/yr**.

C1b's bands, `SVT_INERTIA_ANNUAL_RECENT` 0.20 and `_LONG_STAYER` 0.10, are all-cause rates of
leaving the default tariff (`departure_risks.py`, from `svt_rates_active_passive_2016_2025.md` §4).
So the anniversary route's exits come **on top of** a rate that already counts them. SVT exits run
about 29% above what C1b's own band sets. **This errs against the company**, the opposite of the
item's premise, and it adds noise to every noise-floor test.

The 28 active re-draws that re-fix with the same supplier are a separate question. Internal
conversion off SVT is real (`published_route_split.svt_internal_conversion_floor`), but its date
follows the household's acquisition anniversary, which the record does not give an evergreen
customer.

## Correction to the pre-registration, beside it

The pre-registration promised "a control that a genuine fixed end CAN produce an exit". Both legs
already exist. `tests/simulation/test_renewal_engagement.py` pins the draw over 400 seeds, and they
contain both outcomes. `roll_lifecycle_event`'s churn is driven across many files. This run's 20
exits are the end-to-end witness. A third control would only guard the existing ones. What was
missing was the reason a later lane must not add the passive roll, and that is now at the branch
in `simulation/renewals.py`.

## Next, for the world lane (a baseline decision, blind to company results)

**Remove the anniversary route's departure roll for a household coming off SVT, or move its
re-draw onto the cap calendar.** Either way, C1b then carries all SVT exits, as its band says. This
changes the world's churn, so it waits until the PB4 bill-shock swap has its own run on origin, and
it never shares a run with it.
