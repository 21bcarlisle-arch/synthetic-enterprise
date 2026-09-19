**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "SVT internal conversion needs a ceiling, not a better floor"

# Result: the banner that cannot give a share gives a bound, and the ceiling is the side that can refuse

**Delivery seat, 2026-09-19, claim `svt-internal-conversion-needs-a-ceiling-not-a-better-floor`.**
Pre-registration filed before the workbook was opened and before the world was measured:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_RECORD_SETS_A_CEILING_ON_J_SVT_AND_WHETHER_THE_BANNER_RULED_OUT_FOR_PHI_IS_ADMISSIBLE_ONE_SIDED_2026-09-19.md`.
**All six predictions landed as written, including the two about a source I had not read.**

---

## 1. The answer in four lines

1. **The record DOES set a ceiling, it needs less than the floor did, and it is now published.**
   `J_svt ≤ I / s`, from the same identity at `φ = 1`. `φ ≤ 1` is the definition of a share, not an
   assumption about one — where the floor needed `J_svt ≥ 0` to drop its term.
2. **The binding ceiling is 0.2659 and the world sits at 0.70 of it.** Against a floor the world
   cleared by 4.14×. The band `[0.0449, 0.2659]` is two-sided for the first time and the top of it
   is where the next move in the SVT-side decision would be refused.
3. **The tariff-type banner, which `gb_domestic_switcher_split_cim_2022_2025.md` §3 rules out for φ
   and §6.3 names as the reach that does not work, is admissible one-sidedly here** — because the
   contamination that destroys it for a share runs the *safe* way for an upper bound. It tightens
   the ceiling to 0.2389 and it is deliberately NOT the published bar.
4. **The world clears both, and that verdict is the STRONG one.** Four individual years sit above
   the ceiling and **none of them is a breach**, for a reason stated in §4 and carried in the
   reading's own output.

## 2. The duplicate-claim note was the self-collision, checked before building

The draw reported this id already held under this very id in `.seat_work_in_hand.json`. That is the
shape the 2026-09-19 decision's §2 recorded once already and it was not a rival then either. Checked
before a line was written: `git worktree list` (this is the only live seat worktree at 215424f2c),
no `.seat_work_in_hand.json` reachable from here at all, and the single `ps` match for
`surgical_land|published_route_split|fit_year_level` is **this session's own prompt text**, which is
the known `pgrep` false positive. It was this claim, held by this draw. No disposition taken.

## 3. What was built, and it is all on the check side

| | |
|---|---|
| `published_route_split.svt_internal_conversion_ceiling()` | the bound, per wave and binding, with the tighter banner variant reported beside it and never in place of it |
| `SwitcherSplitObservation.internal_weighted_reporting_fixed` / `_variable` | Table 109's two tariff-type columns, both held, neither derived from the other |
| `.the_banner_partitions_the_internal_switchers` | the fact the banner ceiling rests on, CHECKED rather than assumed |
| `fit_year_level_anchor._internal_return_vs_the_published_ceiling` | the join to the captured world, wired as `against_the_ceiling_for_this_route` and printed by `--internal-return` |
| `tests/tools/test_the_worlds_internal_route_is_judged_against_a_ceiling_and_not_only_a_floor.py` | 13 legs, 14 mutations, every one caught by the leg written for it |

**Nothing in `simulation/`, `company/` or `saas/` moves.** No world-side constant, no second home for
the rate gap, no import across either wall. `SVT_INTERNAL_CONVERSION_RATE` is still `None` with its
gap named — two bounds are not a point estimate, and with a floor and a ceiling in hand a midpoint
starts to look like one, which is why a leg exists to stop exactly that.

## 4. The inversion, which is the part that was easy to get wrong

Every conservative choice in the floor runs the other way in the ceiling, and copying rather than
inverting any one of them publishes a bar tighter than the record supports:

| | floor pushes DOWN | ceiling pushes UP |
|---|---|---|
| default share `s` | LARGEST in the window | **SMALLEST** |
| across waves | MINIMUM | **MAXIMUM** |
| six-month rate read as annual | a valid annual floor, so **clearing is the weak verdict** | **NOT a valid annual ceiling**, so the bar is harsher than the record supports and **clearing is the STRONG verdict** |

The third line is the one that matters to a reader. The world exceeds the un-annualised ceiling in
2018, 2021, 2023 and 2025 — and **that is not a refutation of anything.** A year can carry up to
twice a half-year's conversions; bounding that above needs the repeat-switching assumption this
module has now declined to make three times. Inventing one to strengthen my own reading is the
single move that would make this worthless, and the same sentence appears in the floor's landing
because it was the same temptation running the other way.

Had `min` been copied from the floor instead of inverted to `max`, the binding ceiling would be
0.1380 — **below the world's own 0.1859** — and this turn would have published a breach the record
does not make. That mutation is `test_the_binding_ceiling_is_the_loosest_wave_and_not_the_tightest`.

## 5. The banner, and why a contaminated variable can bound what it cannot describe

§3 of the research note rules Table 109 out because *"tariff type is recorded after the switch, so a
household that switched onto a fix is counted in the fixed column whichever route it came from"*.
That is fatal for φ, which needs the column to mean the tariff held *before*.

**It is the safe direction for a ceiling.** A `J_svt` event *is* a move onto a fix, so the household
is on a fixed tariff when asked, so every `J_svt` event is in the Fixed column. Dropping the Variable
column can only discard non-conversions. And the price is exact rather than rhetorical: **the two
ceilings differ by precisely the Variable column's internal switchers.** If every one of those were a
conversion whose mover mis-reported, 0.2389 would be wrong and 0.2659 would still be right. That is
why the assumption-free figure is the bar.

One fact had to be checked rather than assumed, because dropping a column is only safe if the pair
is exhaustive: **the two columns partition the internal switchers exactly in all six waves.**

**And I got the supporting claim wrong first, which is worth keeping.** I wrote — in the module, the
research note and this document — that the columns' *bases* fail to partition the total base "by
0.5–2.5% in every wave", inferred from W6's unweighted 2127 + 1316 against 3458 and never computed
for the others. Checked before landing: the bases partition **exactly** in W1–W5, and W6 alone is
15 unweighted respondents (0.46%) short. None of those 15 reported an internal switch, which is why
the switchers still partition at W6. The correction does not move the ceiling — the property the
ceiling rests on is exhaustiveness over *switchers*, which held throughout — but the sentence was a
range asserted from one wave's arithmetic, which is the thing this project keeps paying for.

**A tension found and recorded rather than resolved:** the banner's base puts 61.9% of W6
respondents on a fixed tariff while `published_tariff_mix` puts the 2025 GB fixed share at 30–36%.
Self-report and the market statistic disagree by nearly two-fold. It does not touch this ceiling —
the argument needs only where a conversion *lands* — but it would sink any use of these columns as a
population share, and it is written into the research note so the next session meets it before
building on it rather than after.

## 6. Every prediction, against what happened

| # | predicted, before the measurement | measured |
|---|---|---|
| P1 | world clears the ceiling at 0.69–0.71× | **0.6990** ✓ |
| P2 | at least one YEAR breaches | **four**: 2018, 2021, 2023, 2025 ✓ |
| P3 | the flattering direction inverts; `below` is the strong verdict | holds, and is stated in the reading's own output ✓ |
| P4 | the banner is one-sidedly admissible and gives a tighter ceiling | **0.2389 < 0.2659** ✓ |
| P5 | Table 109's W6 cells within ±0.02 of `I_fixed = 0.247`, `I_var = 0.045`; ceiling within ±0.02 of 0.237 | **0.2469, 0.0459, 0.23892** — all within 0.001 ✓ |
| P6 | the banner changes no verdict | changes none ✓ |

P5 was the one worth filing: it was a reconstruction from two *ranges* quoted in an in-repo note plus
Table 56's bases, predicting cells in a 27MB workbook nobody here had opened. It also went further
than predicted — Table 109 carries the tariff-type banner for **all six waves**, not the one wave the
reconstruction could reach, so the banner ceiling is a six-wave figure rather than a W6 one.

**Nothing was refuted.** That is worth naming rather than enjoying: six-for-six means the
pre-registration was not ambitious enough, and the one genuinely open prediction was P2, where I
recorded being least sure. Its answer — four years, not one — is the only number here that surprised
me.

## 7. The control, and that it can fail

13 legs, **keyed to the property and not to today's answer**. A leg pinned to "clears" would go red
the moment the world's SVT-side decision is made more aggressive, which is the one change this bound
exists to catch.

14 mutations run, **every one caught by the leg written for it** — checked without `-x`, because a
mutation caught by a neighbouring leg is the flattering reading:

| mutation | leg |
|---|---|
| `s_max` instead of `s_min` | `..._divides_by_the_smallest_default_share_and_not_the_largest` |
| `min` instead of `max` across waves | `..._is_the_loosest_wave_and_not_the_tightest` |
| banner figure becomes the bar | `..._never_becomes_the_binding_bar` |
| partition flag hardcoded `True` | `..._must_be_shown_to_partition_the_internal_switchers` |
| point estimate set to the ceiling | `..._is_a_bound_and_never_becomes_the_point_estimate` |
| `<=` → `<` at the bound | `..._the_boundary_is_not_strict` |
| verdict frozen `True` | `test_both_verdicts_are_reachable` |
| fail open on a `None` ceiling | `..._is_refused_and_never_passed` |
| uniformity flag frozen | `..._is_derived_and_not_declared` |
| direction statement copied from the floor's | `..._it_is_the_floors_inverted` |
| `None` per-year rate read as `0.0` | `..._is_scored_as_neither` |
| band membership frozen `True` | `..._reachable_in_all_three_directions` |
| whole-book denominator | `test_both_verdicts_are_reachable` |
| ceiling scaled below its floor | `..._is_never_below_the_floor_it_pairs_with` |

The last is the only leg that would survive a rewrite of both bounds: floor and ceiling describe the
same quantity, so the band must be non-empty at every wave. A ceiling under its floor is a derivation
error that **no verdict leg would notice**, because both verdicts would still compute.

## 8. What is still owed, and it is unchanged

**The point estimate.** `SVT_INTERNAL_CONVERSION_RATE` is `None` and now has a band rather than a
floor. What closes it is what closed nothing this turn: **one published domestic instrument that cuts
the internal-switching row by the tariff the respondent was on BEFORE the move.** Table 109 is not
it and cannot be made into it — §5 is a bound extracted from a contaminated variable, not the
variable decontaminated.

**The band is wide — 5.9× from floor to ceiling — and the world is inside it.** So the borrow of the
35% fixed-expiry anchor for the SVT-side decision is *not refuted*, and it was not refutable in
either direction before today. It is refutable in one direction now, and the direction that matters:
a fixed-expiry anchor borrowed for a default-tariff household errs HIGH, and high is the side that
now has a bar.

**Annualisation would make the ceiling bite properly and nothing licenses it.** A six-month ceiling
read annually is the flattering-to-the-world direction; the true annual ceiling is up to twice as
high, and which it is depends on repeat switching within a year. That is the one further published
fact that would turn this bound from live into firing.

## 9. Reversal

Two `tools/` modules, one new test file, one regenerated report artefact, two research-note sections,
two knowledge-map cells, two staging documents. Deleting `svt_internal_conversion_ceiling`,
`_internal_return_vs_the_published_ceiling` and its call restores the previous reading exactly; the
artefact regenerates with `python3 -m tools.fit_year_level_anchor --internal-return`. The two new
dataclass fields default to `None`, so removing the six literals leaves every existing caller intact
and the banner ceiling reporting `None` rather than crashing.
