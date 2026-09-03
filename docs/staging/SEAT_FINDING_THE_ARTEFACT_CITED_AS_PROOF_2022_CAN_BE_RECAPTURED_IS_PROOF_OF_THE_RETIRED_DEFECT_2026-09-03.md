**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — the artefact cited as proof that 2022's renewal population can be re-captured is proof of the defect C1b retired, and a Lane 0 direction was drawn on the inference

**Found 2026-09-03, delivery seat, Lane 0, isolated worktree `/var/tmp/se-seat-executor`, on the
drawn item `2022-needs-a-renewal-population`.** The finding is what the item's own premise turned
out to be when it was checked, before any capture was run.

---

## 1. The claim, and what it cited

`simulation/departure_level_anchor.UNFITTED_YEARS[2022]` read, until this commit:

> *"`c3_shown_price_departure_factors.json` carries 53 renewal rows in 2022 under the retired
> ten-year block, so a re-capture CAN close this one."*

The drawn direction repeats it verbatim: *"c3_shown_price_departure_factors.json carries 53 2022
renewal rows under the retired block, so those rolls DO exist under some configuration."*

**The row count is right. The inference is false, and it is false in the direction that costs a
ten-minute run and ends in a wrong conclusion.**

## 2. What those 53 rows are

Measured on the committed artefact:

```
c3 rows by year: 2016:3 2017:57 2018:51 2019:49 2020:50 2021:49 2022:53 2023:53 2024:59 2025:35
c3 2022 rows: 53      passive_churn_cap: Counter({0.1: 53})
```

**All 53 carry `passive_churn_cap = 0.1`.** That is `renewal_engagement.PASSIVE_CHURN_CAP`, set by
`passive_churn_cap_for(active_renewal=False)`. Every one of those rows is a **forced-passive roll
that the pre-C1b world settled as a fixed term anyway** — which is, verbatim from `renewals.py`'s
own C1b note, the defect C1b was landed to remove:

> *"the world both knew who had rolled onto the standard variable tariff and settled them as
> though nobody had."*

So the artefact cited as evidence that the 2022 renewal population is recoverable is evidence of
the retired defect. "Re-capture" as a repair means re-introducing it. Driven: removing the passive
divert from `build_renewal_schedule` — i.e. restoring the pre-C1b world — is exactly what makes
those rows come back, and it reds six controls in `tests/simulation/test_svt_assignment.py`.

## 3. The absence is STRUCTURAL, and nothing in the tree said so in code

Two committed facts compose:

* `rolls_active_renewal` returns `False` for every crisis-year term start **regardless of the
  household's engagement probability** (`CRISIS_PASSIVE_YEARS = {"2022"}`);
* `build_renewal_schedule` diverts **every** passive roll to `build_svt_schedule` and `continue`s
  past the renewal machinery.

Therefore **no fixed term can START in a crisis year, at any seed, for any household**, so no
renewal roll can fire and no capture of the live world can carry a 2022 renewal decision.

Each half was already held. **Their composition was not**, which is the claim a reader of the
anchor actually needs — and the register above it therefore carried a false locator with every leg
green. Now held directly by
`tests/simulation/test_svt_assignment.py::test_no_household_can_reach_a_renewal_decision_in_a_crisis_year`.

## 4. Why every existing control was green through it

`test_switching_rate_commons.py` corroborates `UNFITTED_YEARS` causes on two axes and neither
touches this one:

| leg | what it checks | 2022's clause it covers |
|---|---|---|
| `..._every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` | the renewal DECISION COUNT is genuinely zero | cause (i)'s *count* |
| `..._every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs` | a stated SVT floor re-drives under the live hazard | cause (ii)'s *floor* |
| — nothing — | **what the rows in a capture the cause NAMES actually are** | cause (i)'s *inference* |

**A cause could cite any file in the tree for any property and nothing would open it.** This is the
same mixed-subject OR that let half of this entry be false for two days on 2026-09-02
(`SEAT_FINDING_THE_2022_CAUSE_DECLARED_NOT_CAPTURE_SCOPED_IS_THE_ONE_THAT_MOVED`) — a control over
a multi-clause claim that corroborates some clauses reports the OR, and the uncovered clause is
where the rot goes. **This is the third time on this one register entry.** The generalisation worth
keeping is not "check c3" but: *a refusal that CITES an artefact has made a checkable claim about
that artefact, and the citation is a disclosure exactly like a stated figure.*

Closed by `..._a_capture_a_refusal_cites_for_its_rows_is_read_for_what_those_rows_actually_are`,
keyed to the grammar rather than to 2022 or to 53, with an empty-subject floor.

## 5. What actually closes 2022, which is a change to the WORLD and not to the capture

Stated so the next lane does not re-derive it. In 2022 the **whole book is on SVT** — 51 accounts,
197 SVT segment decisions, **zero** renewal decisions (measured on `c6_second_pass`). And
`run_phase2b` builds every SVT segment's risks as:

```python
_svt_risks = build_departure_risks(
    bill_shock_base=0.0, price_response=0.0, dissatisfaction_response=0.0,
    action_propensity=_svt_propensity,
    level_anchor=year_level_anchor(int(term_start_str[:4])),   # <-- reaches nothing
    svt_inertia=_svt_hazard,
)
```

Those three zeroed responses are **the only hazards `level_anchor` multiplies** —
`build_departure_risks` deliberately keeps the anchor off the `CAUSE_SVT_INERTIA` line, and says
why. So `level_anchor=` is passed on that call and cannot reach a single term in it. In a year
where the whole book is on SVT, that means **the year has no calibration lever of any kind**, which
is what `NO_LEVEL_CORRECTION = 1.0` is actually recording.

`run_phase2b`'s own note already concedes the modelling half: *"an SVT account's departures are
understated by whatever those three would have added."* In 2022 an SVT household's cap went
£1,277 → £1,971 → £3,549 (Oct 2021 / Apr 2022 / Oct 2022, from
`svt_rates_active_passive_2016_2025.md` §1) and the world assigns it a bill shock of exactly zero.
**That is the largest bill shock in the record, on the whole book, priced at nothing.**

The whole-book reading today is 2.50% against a published 2.9–4.3% — out LOW by 0.40pp, which is
the direction an understated hazard predicts.

**THIS IS NOT A 2022 REPAIR AND MUST NOT BE SCOPED AS ONE.** An SVT segment carries no bill-shock,
price or service hazard in *every* year, so fixing it moves all ten and requires the full
`capture → fit → capture` loop against `YEAR_LEVEL_ANCHOR`'s seven fitted years. Scoping it to 2022
to close a band would be a carve-out fitted to today's answer. Handed off as its own item.

## 6. What was NOT done, and why

No re-capture was run and no anchor was re-fitted. The drawn item's stated route — re-capture to
recover 53 rows — is refuted above, and the route that does work is a baseline change whose
convergence loop is larger than one turn. Landing the refutation first is what stops the next lane
spending the run.

`tests/architecture/test_switching_rate_commons.py::test_the_whole_book_departure_level_is_inside_the_published_band`
**stays xfail(strict=True)** and its reason is unchanged in substance: 2021 is out HIGH by 0.13pp
(inside the draw at 51 accounts; a further capture-fit pass may close it) and 2022 is out LOW by
0.40pp. What changed is that the 2022 half now names a repair that exists.

## 7. Mutations (all `python3 -B`, observed rather than intended)

| mutation | result |
|---|---|
| drop the `CRISIS_PASSIVE_YEARS` branch from `rolls_active_renewal` | **1 red**, the composition leg, on its VERDICT, naming `C3@2022-12-30 C1@2022-12-30 SYN-2016-003@2022-12-30` |
| remove the passive divert entirely (the pre-C1b world) | **6 reds**, the composition leg among them |
| make the divert unconditional on every year | **2 reds, and the composition leg is NOT one** — an EQUIVALENCE, stated: the first term is always fixed so its floor survives. It does not hold the divert's scope; its two siblings do |
| `ALL 53` → `ALL 54` in the cause | **1 red**, on the count |
| `passive_churn_cap = 0.1` → `0.2` | **1 red**, on the cap |
| repoint the citation at `c5_refitted_departure_factors.json` (no 2022 rows) | **1 red**, on the zero-row leg — the case where a re-capture claim is checked against nothing |
| delete the claim from the cause | **1 red**, on the empty-subject floor |

The first draft of the composition leg asked its floor for an *SVT stint* beginning in the crisis
year, which is the verdict's own fact from the other side: under mutation 1 the floor emptied and
fired FIRST, turning a substantive red into a procedural one — this repository's catalogued *scope
guard before the verdict*. The floor now counts boundaries of either product.

## 8. One incidental, recorded because it silently disarms a whole file

`tests/simulation/test_svt_assignment.py`'s `price_records` fixture skips on
`get_cached_prices(...)` returning nothing, and `sim/cache/` is `.gitignore`d. **In a fresh isolated
worktree only `elexon_ssp_live_rolling.json` is present, so 7 of that file's 10 controls skip and
report as a pass.** Symlinking the shared tree's `sim/cache/*.json` in restores them. Not repaired
here — it is a fixture-isolation question that belongs with whoever owns the worktree stem — but a
lane that mutation-proves in a worktree and sees "3 passed, 7 skipped" should know the 7 are not
telling it anything.
