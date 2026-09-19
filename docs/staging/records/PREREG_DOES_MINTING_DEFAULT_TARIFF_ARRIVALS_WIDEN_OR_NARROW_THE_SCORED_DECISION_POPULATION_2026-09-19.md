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
