**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `does-minting-arrivals-widen-the-scored-decision-population`

# PRE-REGISTRATION — does minting default-tariff arrivals WIDEN or NARROW the scored decision population?

**Filed 2026-09-19 ~16:55 BST, delivery seat, before either leg was launched and with neither leg
artefact on disk.** Checkable: the two outputs are
`docs/observability/arrival_decision_population_off_20260919.json` and
`..._on_20260919.json`, and at the moment this file was written `ls` returned *no such file* for
both. The predictions below were fixed before any figure from either leg existed.

Settles **P2**, pre-registered in §5 of
`SEAT_RESULT_THE_WORLD_NOW_MINTS_DEFAULT_TARIFF_ARRIVALS_..._2026-09-19.md` and **landed in git at
`7bff15179`** — a pre-registration nothing in this turn can backdate. **This file predicts the
opposite direction to P2, and says why below.**

---

## 1. The question, and the two numbers that answer it

The arrival producer (C6, `simulation/arrival_route.py`) mints **35 `svt` of 226** on the live
roster where every record carried `None` before. The question the producer's own write-up declined
to answer is what that does to the population of **priced, scored renewal decisions** — the
denominator of the rank (selection) leg, whose replication unit was argued to be the roster
precisely because a seed re-draw adds no decisions.

**The before state is already on disk** (`value_cycle_ab_s1_three_arm_20260918.json`, value arm):

| quantity | value |
|---|---:|
| `renewals_the_world_offered` | 2,824 |
| `product_not_upliftable` (all `'svt'`) | 2,490 |
| `acquisition_term` | 227 |
| `priced` / `declined` | 104 / 3 |
| `decisions_that_existed` | **107** |
| scored decisions (`belief_vs_outcome`) | **104** — 60 retained, 44 left |
| `discrimination_auc` | 0.5566287878787879 |
| own-roster null sd (tie-corrected / untied) | 0.05755173 / 0.05757077 |
| distance from 0.5 | **0.98 null sd — does not clear** |

## 2. P3a — the DIRECTION, and it is against P2

**P2 said `decisions_that_existed` will be ABOVE 107.** Its warrant was the arrival EXIT: 19 of 31
SVT-origin electricity accounts reach a non-SVT term, first at term index 4 against a
`MIN_TERM_INDEX_FOR_UPLIFT` of 1, so households that could not be priced now can be.

**Reading the two mechanisms together gives the opposite sign, and P2 only counted one of them.**
Before this producer, a drawn record carried `tariff_type` present-and-`None`, and
`run_phase2b.resolved_tariff_type` resolves that to `"fixed"` for the OPENING term (`or "fixed"`,
2026-08-30) — so an arrival was on a *priceable* product from term index 1 and left it only when
its own engagement roll (C1b) put it on SVT. After this producer, 35 of 226 open ON SVT and stay
there until that same roll exits them: **first exit at term index 4, and 12 of the 31 never exit at
all.** SVT terms are refused at `product_not_upliftable`. So the producer takes terms OUT of the
priceable population at the FRONT of every arrival's tenure and hands some of them back later.

**P3a: `decisions_that_existed` on the arrivals-on leg will be BELOW 107.** Point prediction **95**;
80% band **85–107**. The fall will appear as a rise in `product_not_upliftable` at `'svt'` (before:
2,490) and in no other stage; `no_observed_history` stays at 0.

*What would make P3a wrong, and P2 right:* the exits returning more priceable terms than the
pre-exit SVT terms remove — arithmetically possible if arrivals sit in long tenures whose post-exit
fixed terms outnumber their first four. **If the count rises, P2 is confirmed and this reading of
the mechanism is wrong; that is recorded here beside the prediction, not revised after.**

## 3. P3b — the NULL WIDTH, which is arithmetic once the counts are known

The Mann-Whitney null for an AUC is a closed form in the two outcome counts and nothing else:
`sd = sqrt((n1 + n2 + 1) / (12 n1 n2))` (`generate_value_arms_data._auc_null_sd`), tie-corrected off
its own roster by `_auc_from_a_roster`. At 60/44 that is 0.057571 untied and a 95% half-width of
**0.11284**. Scaling at the observed 57.7% retained share:

| scored decisions | n1 / n2 | null sd |
|---:|---:|---:|
| 95 | 55 / 40 | 0.060302 |
| **104 (today)** | **60 / 44** | **0.057571** |
| 120 | 69 / 51 | 0.053529 |
| 160 | 92 / 68 | 0.046310 |
| 416 | 240 / 176 | 0.028682 |

**P3b: the null sd moves by less than 15% in either direction, and the rank leg does not get
materially cheaper.** Under P3a it gets *wider* (~+4.7% at 95 decisions). Halving the half-width
needs ~4× the decisions — about **416** — and no roster repair of this size delivers that: the
producer touches 35 accounts of 226.

**P3c: the AUC on the arrivals-on leg is still inside 2 null sd of 0.5** — i.e. it still does not
clear its own null. The AUC is *re-measured* on the new leg, never carried across from 0.5566: a
different population is a different figure.

## 4. P3d — the patch must be OBSERVED TO FIRE, or there is no measurement

The one-variable design is two value-arm passes at one HEAD, one seed, one roster, differing in
exactly one symbol: `simulation.population_draw._draw_tariff_type` rebound to return `None` — which
is *exactly* the pre-commit world, because `tariff_type` is a dataclass field defaulting to `None`
(`population_draw.py:257`) that the pre-commit `_draw_one` never passed. It is patched **before
`run_phase2b` is imported**, because that module binds `CUSTOMERS = live_population()` at import;
one world per process for that reason.

**P3d: the off leg has ZERO roster records at `tariff_type == 'svt'` and the on leg has 35.** A
rebind that reaches no call site produces two byte-identical worlds, a difference of exactly zero,
and the most flattering possible headline — so the counter is asserted per leg and a leg that fails
it is VOID, not a result. (The floor runner's own lesson, `noise_floor`'s patch-fires counter.)

## 5. What this measurement costs, and what it is NOT

Two value-arm passes — **not** a seed family. The hard constraint on the drawn item is honoured: no
twelve-seed floor run, which is ~17 hours of the only box. Launched via
`background.launch_long_job` so it outlives this bounded tick, with the elapsed cost reported in the
result.

**The decision count is a count of OPPORTUNITIES TO BE GRADED, and is not evidence about the
selection leg's sign.** No sentence in the result will let it travel as one. Any AUC quoted is
graded against its OWN roster's null, off that leg's own `scored_decisions` — never another
family's ruler.

---

# THE RESULT, FILED BESIDE THE PREDICTION — 2026-09-19 ~19:20 BST

*Both legs are on disk and folded. Every figure below comes from
`tools.arrival_decision_population --fold`, re-run in this turn and **byte-identical** to the
`docs/observability/arrival_decision_population.json` landed at `db00d334c` (compared field by
field, ignoring timestamps). Nothing here is a hand calculation.*

## 6. The scoreboard: one refuted, three confirmed

| # | predicted | observed | verdict |
|---|---|---:|---|
| **P3a** | `decisions_that_existed` **below** 107; point **95**, 80% band 85–107 | **114** | **REFUTED** — wrong in DIRECTION and outside the band |
| **P3b** | null sd moves <15% either way; rank leg not materially cheaper; ~416 decisions to halve | ratio **0.9897** (1.0% narrower); **414** | **CONFIRMED** |
| **P3c** | on-leg AUC still inside 2 null sd of 0.5 | **0.564** null sd | **CONFIRMED** — still does not clear |
| **P3d** | off leg 0 `svt` roster records, on leg 35 | **0 / 35** | **CONFIRMED** — the patch fired; the leg is a result, not VOID |

**P2 — the earlier prediction this file was written to contradict — is CONFIRMED, and P3a, the one
written four hours later at `768895de2`, is the one that was wrong.** Both stay in the record.

## 7. The explicit sentence the drawn item asked for

**The rank leg got THE SAME, not cheaper.** In the module's own words
(`did_the_rank_leg_get_cheaper`): *"the same, within 5%: the arrivals-on null is 99.0% of the
arrivals-off null, so this route does not move the rank leg's cost."* The 95% half-width goes
**0.11280 → 0.11164**. Halving it needs **414** scored decisions against today's 107 — and this
producer bought **+3** scored decisions by minting 35 SVT arrivals on a 226-record roster. **This
route is closed as a way to buy rank-leg power.** The item pre-priced that answer as worth the same
hour as a positive one; it is, and it means the ask to the director is the route that remains.

## 8. Why P3a was wrong, kept rather than revised

P3a's *mechanism* was visible and real: `product_not_upliftable` rose **2,490 → 2,602**, every one
`'svt'`, exactly as predicted, and `no_observed_history` held at 0 and `acquisition_term` at 227 —
so the increment is new arrivals reaching the funnel and not the term-index mechanism, the read P1
and P2 both required before anyone attributed it.

**What P3a did not count is that the denominator was not fixed.** `renewals_the_world_offered` rose
**2,824 → 2,943**, because an account on a default tariff is offered a term boundary more often than
one on a fixed deal. The arithmetic closes exactly: **+119 boundaries = +112 refused at
`product_not_upliftable` + 7 priced.** I reasoned about the composition of a fixed denominator and
the denominator moved. That is the error, it is named, and the prediction above is left standing.

## 9. The two legs were produced at DIFFERENT commits, and the divergence is INERT BY PATHS

The drawn item asked for this check explicitly and it had not been answered.

| leg | `producing_commit` | resolved |
|---|---|---|
| OFF | `768895de2` | 16:39:05Z |
| ON | `f8a54c985` | 17:03:54Z |

**They differ**, and `768895de2` is a strict ancestor of `f8a54c985` — the ON leg bound its modules
two commits later. The item warned that the one-variable attribution "expires if the ON leg is re-run
at a later tree", so this is not cosmetic.

**It is inert, and by path disjointness rather than by argument.** The complete diff
`768895de2..f8a54c985` is three paths — `docs/staging/SEAT_RESULT_THE_VALUE_ARMS_POINTER_RUNG_...md`,
`tests/tools/test_the_value_arms_pages_undriven_pointers.py`, and `tools/generate_value_arms_data.py`
— a staging document, a test, and the value-arms *page* producer. `tools/arrival_decision_population.py`
imports none of them; it reads only `argparse`, `json`, `math`, `subprocess`, `sys`, `time` and
`pathlib`, plus the simulation modules it binds at process start. **No path the arrival producer can
read moved between the two legs, so the +7 remains attributable to the one rebound symbol
(`_draw_tariff_type`) and to nothing else.**

## 10. What may NOT travel from this

* **The decision count is a count of opportunities to be graded.** It is not evidence the selection
  leg improved, and no sentence above says it is.
* **The AUC fell, 0.5566 → 0.5321, and that is NOT a finding about the producer.** It is a different
  population, measured once, with no error bar on the difference between two AUCs. What is sayable —
  each graded against its own roster's null via `_auc_from_a_roster`, never another family's ruler —
  is that **neither leg clears, and the ON leg is further from clearing** (0.564 null sd against
  0.984).
* **+7 priced becomes +3 scored** because four of the seven new priced decisions are unscored: the
  world rolled no lifecycle event at that `(account, term_start)`. That is the funnel's own
  `unmatched_meaning`, not an inference.
