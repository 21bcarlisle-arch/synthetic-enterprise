**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `value_cycle_ab`
· **Class:** `figures_on_a_superseded_clock`

# Every control asked whether the figure was right; none asked whether its world still existed

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Pre-registration and grading: `SEAT_PREREGISTRATION_WHETHER_THE_WORLD_THE_ARMS_RAN_IN_STILL_EXISTS_2026-09-03.md`.*

---

## 1. What was published, and what was true

`/capabilities/` published, as the company's standing beat over a flat-rule baseline:

> Running the same book through the per-customer decision engine earned **£12,071 MORE** than flat
> rules, clearing the **±£2,291** this figure moves across 3 seed re-draws.

That figure comes from `value_cycle_ab_s1_three_arm.json` (**2026-08-31T03:47:57Z**), bounded by
`value_cycle_ab_s1_noise_floor.json` (**2026-08-31T07:05:53Z**) and read against
`value_cycle_ab_floor_decomposition.json` (**2026-08-30**).

`simulation/departure_level_anchor.py` — the term that sets how readily a household leaves, and
therefore how much book there is to lose and re-win — was re-fitted **twice** afterwards, at
`a621edb15` (09-02 07:11) and `712ae5323` (09-03 07:47), plus a third pass at `ace28fa44`.

**On the arms' own capture population, changing nothing but the anchor block**
(`docs/reports/c4_whole_book_departure_factors.json` + its SVT sibling — the capture taken under the
block the arms ran under), whole-book expected departure moves:

| year | band % | under the arms' anchor | under the live anchor | move |
|---|---|---|---|---|
| 2017 | 13.5–14.0 | 10.764 | 14.128 | **+3.365pp** |
| 2018 | 19.5–20.0 | 20.268 | 19.150 | −1.118pp |
| 2019 | 20.7–21.3 | 17.510 | 23.735 | **+6.225pp** |
| 2020 | 22.5–23.0 | 20.945 | 24.531 | **+3.586pp** |
| 2021 | 17.9–18.4 | 14.541 | 19.071 | **+4.530pp** |
| 2022 | 2.9–4.3 | 2.536 | 2.536 | +0.000pp |
| 2023 | 8.9–12.5 | 12.599 | 12.445 | −0.154pp |
| 2024 | 12.5–16.1 | 13.765 | 16.389 | **+2.624pp** |

**+19.06pp summed across 2017–2024**; mean absolute **2.70pp/yr**; **+6.23pp** at 2019. Every
published band is **0.5–3.6pp wide**, so the world moved by several bands' worth on the one quantity
the whole comparison sits on.

**The world got HARDER to hold, not easier.** The Lane 0 direction that drew this work states the
opposite — *"the world got easier to hold … so there is less book to re-win"* — and so did the
direction before it. Both read the premise off the **renewal-route** table, which is 7-of-7 out and
high; the whole book is the comparable quantity. This is now the second consecutive direction to
carry it, and the anchor block's own docstring already said so in writing:
*"AND THE NET MOVE IS UPWARD … this pass makes the book HARDER to hold, not easier."*

## 2. Why nothing noticed, and this is the part that generalises

The page has controls for a great deal, and every one of them is about whether a figure is
**internally** right:

- `clock_audit` — is every figure's clock declared and consistent?
- `_producing_commit` — which commit built this run?
- `_staleness_caveat` — is the error bar older than the point estimate it bounds?
- `_decomposition_is_the_same_book` — was the remedy measured on this page's book?
- `_seed_spreads` — does the derived spread reconcile with the published one?

Every one passed. **None of them can express "the world this was measured in is not the world."**

`_staleness_caveat` is the near miss and it is instructive: it compares the floor's `generated_at`
against the three-arm's. Both are 2026-08-31 and the floor is the later one, so it correctly returned
`None` — the two artefacts *are* consistent with each other. **A comparison between two artefacts can
say which of them is older and can never say whether either is current.** That is a different
question and nothing was asking it.

`_producing_commit` looks like it should catch this and cannot. A commit hash moves for a docstring,
a test, another lane's page — so an artefact whose hash differs from HEAD is the **ordinary** case.
A signal that fires on everything is a signal that fires on nothing.

**And the page was already displaying the contradiction.** `_world_departure_level()` measures the
departure level **at publish time**, from the live capture (`c6_second_pass_departure_factors.json`),
and publishes it as the bound on the arms' figures. So `/capabilities/` was rendering a departure
level from **one** world directly beside an advantage measured in **another**, presented as one
reading, with a control on each half and none across the pair.

## 3. The repair

**A world stamp, and a leg that reads it.** Not a date and not a commit — a digest of the departure
level itself.

- `simulation.departure_level_anchor.world_level_identity()` — digests `year_level_anchor` across
  every year inside the published record, **fitted and declared alike**. A re-fit changes it; a
  docstring does not.
- `tools/run_value_cycle_ab.py` stamps `world_identity` onto every artefact it writes, **resolved at
  import** for the same reason `PRODUCING_COMMIT` is: the run takes hours and the tree moves under
  it, so a digest taken at assembly names a world the figures were not measured in.
- `decompose_floor` **refuses** legs that do not share one world, and refuses legs that cannot name
  theirs. A variance measured over one departure level is not a component of a variance measured
  over another; their ratio is not a reconciliation. This is `c30b98048`'s defect made unreachable
  rather than re-described.
- `tools/generate_value_arms_data._world_provenance` fails closed, and
  `_world_clause` puts the verdict **ahead of the figure** in the headline — because a reader who
  meets £12,071 first has already taken it as current.

**Absence refuses.** Every artefact on disk today predates the stamp, so the page now leads with
*"READ THIS AS HISTORY, NOT AS TODAY"* and names the run dates. That is the correct verdict, not a
bug in the leg: those runs genuinely cannot say which world they ran in.

**The old figures are kept.** Superseded-with-provenance is the correction; deletion is not. The
£12,071 is still stated, under its caveat, with its date.

## 4. Mutation-proved

Eight mutations, each run and reverted (`python3 -B` throughout — a stale `.pyc` reports SURVIVED):

| mutation | test that reds |
|---|---|
| unstamped branch returns `superseded: False` instead of `None` | `test_a_run_that_cannot_name_its_world_is_an_absence_not_a_clean_bill` |
| drop the unstamped branch; compare digests only | same, + the live-world test |
| `_world_clause` returns its sentence unconditionally | `test_a_run_in_the_live_world_gets_no_history_clause` |
| `_world_clause` returns `""` unconditionally | `test_a_superseded_world_reaches_the_headline_and_not_only_the_payload` |
| move a fitted anchor 0.5; change a DECLARED year's value | `test_the_world_digest_tracks_the_departure_level_and_not_the_commit` |
| drop `decompose_floor`'s unstamped refusal | `test_legs_that_cannot_name_their_world_are_refused` |
| default a missing digest to a shared sentinel | same |
| drop the two-world refusal | `test_legs_from_two_worlds_do_not_partition_one_call_stream` |

**Two defects were caught by the controls rather than by review**, and both are recorded because
they are the reason the reachable-PASS rung is worth writing:

1. **The PASS branch crashed.** `_world_provenance`'s `reason` had `.format(...)` applied *outside*
   the conditional, so the live-world branch — the only state in which this page is a claim about
   today — raised `NoneType has no attribute format`. A control exercised only by its own failure
   branch looks green forever. `test_a_run_in_the_live_world_gets_no_history_clause` found it.
2. **An existing control had quietly become a tautology.**
   `test_a_divergent_published_run_is_reported_as_a_divergence` asserted
   `headline.startswith("The comparison below is against")` on the positive rung and
   `not ...startswith(...)` on the negative one. Adding a clause *before* that one reddened the
   positive rung — and made the **negative** rung pass trivially, on any headline with a prefix,
   including one that went on to make the lapsed claim three clauses later. **The rung that went red
   was the honest one; the rung that stayed green was the one that had lost its teeth.** Both were
   moved to presence-not-position together, and the repaired negative rung was mutation-proved
   (forcing the clause unconditional reds it; under the old `startswith` form it would not have).

## 5. What is NOT closed

**The re-run is in flight and is not part of this commit.** `value_cycle_ab_s1_three_arm_20260903.json`
is being produced now, to a **new dated path** so nothing existing is overwritten. Until it and both
floor legs land, from one world, and that world is the live one:

- the page correctly says these figures are history;
- `P-C1`, `P-C2` and `P-C3` in the pre-registration are **ungraded and must not be read as
  discharged**;
- the claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists` is **not** finished.

**The floor legs are the larger half of the remaining work**, and they must be run in the same world
as the headline arm or the comparison reproduces exactly the defect `c30b98048` was filed for. Same
world on both sides, or it is not a comparison.
