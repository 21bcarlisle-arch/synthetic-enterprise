# [WORKER FINDING] The count assertion was standing in front of a 7-of-7 out-of-band verdict, and the anchor's 2022 entry is held by nothing at all

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `the-only-control-holding-the-level-anchor-is-red-and-reports-a-constant-pass`
**Found:** 2026-09-01, by the autonomous worker, on Lane 0 delivery direction to repair the emptied subject in `tests/architecture/test_switching_rate_commons.py`.
**Born archived:** new instance of an existing class, per the rule that a new finding in a live class is filed archived rather than staged.

## Class registration

Belongs to `controls_that_cannot_fail` (27 instances). Same lane (`H_harness`), so it consolidates
rather than being refused out of lane.

---

## What the direction asked, and what was actually there

The direction was precise and its premise was **half right**. It said two legs were red at clean
HEAD because a subject had emptied from eight years to seven, that the repair was to key the leg to
the property rather than to the count, and that establishing *why* the subject emptied came first.
All of that is correct and all of it is done.

But it also predicted that keying to the property would turn both legs green. **It does not.** One
of the two legs is still red, and the reason is the finding.

## 1. Why the subject emptied — it stopped being PRODUCED, and permanently

Three candidates were named: a year stopped being produced, stopped being read, or stopped being
classified. It is the first, and the mechanism is exact:

- `simulation/renewal_engagement.py:62` — `CRISIS_PASSIVE_YEARS = frozenset({"2022"})`. Every 2022
  renewal is forced passive, because GB suppliers withdrew fixed tariffs when wholesale costs
  exceeded the cap. This is correct fidelity, not a bug.
- C1b then routes every passive roll to `build_svt_schedule`, so it is settled as an **SVT segment
  decision** and never emits a renewal row.
- Therefore the renewal capture carries **zero** 2022 decisions, while carrying 16–23 in every
  other year. It is an interior hole, not truncation at the capture's rim.

**The forcing alone was never sufficient, and this correction matters for anyone re-deriving it.**
`b46318106`'s predecessor capture carried **54** decisions in 2022 under the same
`CRISIS_PASSIVE_YEARS`. The forcing became subject-emptying only when C1b re-routed forced-passive
renewals off the renewal table. A reader who blames the crisis constant alone will look for a
regression in it and find nothing wrong.

This is **permanent while both hold**. It is not a gap a re-capture fills.

## 2. The bigger finding: the count assertion was masking a universal failure

`test_the_worlds_realised_departure_rate_is_inside_the_published_band` opened with
`assert len(world) >= 8`. That fired on every run, so **the band loop underneath it never
executed**. Bypassing the count assertion at clean HEAD and running the loop it guards:

| year | world realised % | published band % | verdict |
|---|---|---|---|
| 2017 | 15.12 | 13.5–14.0 | **OUT** −1.10pp |
| 2018 | 25.77 | 19.5–20.0 | **OUT** −5.80pp |
| 2019 | 28.10 | 20.7–21.3 | **OUT** −6.80pp |
| 2020 | 38.89 | 22.5–23.0 | **OUT** −15.90pp |
| 2021 | 23.40 | 17.9–18.4 | **OUT** −5.00pp |
| 2023 | 2.81 | 8.9–12.5 | **OUT** −6.10pp |
| 2024 | 22.34 | 12.5–16.1 | **OUT** −6.20pp |

**7 of 7 readable years are out of band.** The scope assertion was not merely reporting a smaller
PASS — it was failing *earlier in the same function* than the verdict that mattered, so the file's
red said "the subject shrank" for as long as the real answer was "the world is nowhere near its
published band on this route". A reader triaging that red would fix the count, watch it go green,
and never see the table above.

### 2a. And it is ONE COMMIT that both broke the verdict and installed the mask

Running the identical code against the capture this control was **discharged** against —
`b46318106^`, 465 rows:

| capture | years read | out of band |
|---|---|---|
| `b46318106^` (465 rows) | 8 | **0** — every year exactly on its band's HIGH endpoint, the anchor's own fit |
| committed HEAD (148 rows) | 7 | **7** |

`b46318106` — *"the capture the published departure figures were already produced from lands, so the
tool and the page stop disagreeing at HEAD"* — swapped a capture on which this control was green for
one on which it fails in every year. **The same swap emptied 2022**, because C1b routes the crisis
year's forced-passive rolls to the SVT table. So the commit that broke the verdict installed, in the
same change, the assertion that hid the break.

This is not world drift and it is not a stale reading of a moving target: it is a **population
swap**. `YEAR_LEVEL_ANCHOR` was fitted against the 465-row population and is now read against a
148-row one over 68 accounts. The anchor is stale against the capture it is paired with — exactly
what the leg's own failure message has been saying to nobody.

**This is a new sub-shape for `controls_that_cannot_fail` and it is worth naming:** a scope guard
placed *before* the verdict in the same test converts a substantive failure into a procedural one.
Both are red, so nothing looks wrong; the catalogue's existing entries are about controls that
report a false PASS, and this one reports a **true red for the wrong reason**, which is harder to
catch because the test is already failing and nobody looks twice at a red that is already known.

## 3. The `_HELD_INDIRECTLY` claim is false for 2022, and structurally so

The register classified `YEAR_LEVEL_ANCHOR` as *"held through its EFFECT — the world's realised
departure rate, which is `_PRINCIPAL_SUBJECT` above and is band-checked every run."*

For nine entries that is true. For `YEAR_LEVEL_ANCHOR[2022] = 1.524110` it is false, and not by
accident:

- the anchor scales the three household hazards and **deliberately not `svt_inertia`**
  (`simulation/departure_risks.py:324`, which says so in its own comment);
- 2022's departures are entirely SVT drift, because nothing reaches a renewal roll;
- so the anchor multiplies nothing that year.

Corroborated independently by the seat on 2026-08-31
(`SEAT_FINDING_THE_DEPARTURE_LEVEL_UNIONED_ONTO_ACCOUNT_YEARS_AND_2022_HAS_NO_LEVER`): sweeping the
2022 anchor from 0 to 10³ moves the book's 2022 level **by not one basis point** — floor equals
ceiling equals 12.09%. The entry is **unidentified**, not badly fitted.

**The honest answer the direction asked for is: the indirection never held 2022.** That is the one
year the anchor module's own docstring records a fallback silently running at 1.98x, and it is
precisely the year no control could see. The register now says so. Naming a gap is not closing it —
nothing in this file holds that entry, and the repair is rung-2 mechanism work (`svt_inertia_hazard`
is a function of `years_on_svt` and `segment_days` and of nothing about the market, so the crisis
year reads like any other), not a control change.

## 4. `nan` was reaching the published surface

2022 entered every aggregate as `nan`. The instrument's headline printed
`mean world E[depart] : nan%` and `nanx short of the record`. One unread year did not reduce the
summary's coverage — it **destroyed** the summary, in the shape of a number. Now 22.35%, over a
stated 7 years, with the refused year named above it.

## 5. What the shared tree was holding — a separate, live hazard

The drawn pathspec was `tests/architecture/test_switching_rate_commons.py`. **Committing that file
from the working tree would have deleted three controls landed at HEAD** in `58c496f64`:

- `test_the_register_names_the_route_its_principal_subject_can_see`
- `test_the_whole_book_departure_level_is_inside_the_published_band`
- `test_the_whole_book_reading_refuses_with_a_named_cause_and_never_the_renewal_one`

Another lane had branched from `60c51b622` (the parent commit for that path) and staged 181 lines;
its index entry never saw the three controls land. This is the second of the two blocking findings
the doorbell carried, confirmed concretely — and it is the catalogued shape *"a drawn pathspec can
be the careless pathspec it warns about"*.

Resolved by **reconstruction, not reversion**: a 3-way `git merge-file` (base `60c51b622`, ours
`HEAD`, theirs working tree) merged clean with rc=0 and no conflicts, giving 30 tests = HEAD's 27
plus the other lane's 3. Both lanes' work is preserved and the silent revert is disarmed.

**And the union went red in a way neither lane could see alone.** One lane widened `_SCOPE` to
`tools/`; the other added `tools.fit_year_level_anchor:_MARKET_PARAMETER_NAMES`. Neither lane's own
test run could fail on it. That is exactly the interconnection check CLAUDE.md reserves for the
seat, arriving as a test failure instead of a question. Classified under `_NOT_A_LEVEL_READING`
(strings naming a signature, no year key, no value to band-check).

## 6. What landed

- `realised_rate_coverage()` — readings and refusals as a **partition** of the comparison window,
  adopted from the working tree, its cause note corrected to name the C1b mediation.
- Both legs re-keyed to the property: *every banded comparison year is read, or refused by name
  with a cause the artefact corroborates*. Never to a count.
- A standalone control for the coverage property, so it can be green and mutation-proven while the
  band verdict is red for a real reason.
- `_HELD_INDIRECTLY` corrected.
- The refusal on the surface: the row says `REFUSED / NO READING` instead of `nan`, the reason is
  printed, and the summary states which years it averaged.

**Mutation-proven, `python3 -B`, three mutations each killing a named test:**

| mutation | killed |
|---|---|
| drop an unreadable year from both returns (the old fail-silent shape) | `test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` |
| refuse a year that HAS 18 decisions (a fabricated excuse) | same, via the independent capture reader |
| keep the refusal out of the printed output | `test_the_instrument_prints_the_distance_to_both_band_edges_and_not_only_the_verdict` |
| make `inside_band` return True (simulates the re-fit landing) | `test_the_worlds_realised_departure_rate_is_inside_the_published_band` XPASSes → **FAILED**, proving the strict marker is a live control and not a silencer |

The second is the one that matters: `realised_rate_coverage` both decides a year is unreadable and
writes the reason, so the leg reads the count through a **second reader** off the capture. Without
that, the producer could retire any inconvenient year by naming it refused.

## 7. What is owed next

1. **Re-fit `YEAR_LEVEL_ANCHOR` against the committed 148-row capture.** That is what discharges
   the re-instated strict xfail, and the marker will break loudly the day it lands rather than
   going quietly green. Not by widening the band and not by re-keying the leg to today's readings.
   **A fit adopted while its only accountability control is red is a number with nothing behind
   it** — and note the direction of the risk here: the *old* capture's eight years all sat exactly
   on their band's high endpoint, which is what a fit aimed at an endpoint looks like. A re-fit
   that reproduces that pattern has calibrated to the target, not measured against it.

   **The marker is held STRICT rather than the test left failing** because a red test wedges every
   commit touching this file, and the gate refuses red commits by construction (director P0,
   2026-07-17). A permanently-red control taxes every lane and gets routed around; a strict xfail
   carrying its full reason stays visible, stays attributable, and cannot be discharged silently.
   This is the same idiom the file used for this same test before 2026-08-30, and the one
   `test_the_whole_book_departure_level_is_inside_the_published_band` uses today.
2. **2022 stays out of any re-fit.** It is unidentified; a fitted value for it would be a free
   parameter setting the quantity it was meant to measure.
3. **The other lane's 181 lines are still uncommitted** in the shared tree. This commit preserves
   them but does not land them — that is theirs to land.
