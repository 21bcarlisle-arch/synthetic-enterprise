# FINDING — the binding half of 2022's refusal was voided by a term that landed the day before

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`
**Filed:** 2026-09-02, delivery seat, Lane 0.
**Pre-registration:** `WORKER_PREREGISTRATION_WHETHER_2022S_DECLARED_CAUSE_SURVIVES_THE_MARKET_TERM_2026-09-02.md`,
filed before any measurement below was run, and graded clause by clause in §4.
**Class:** `controls_that_cannot_fail` — a two-cause refusal whose control corroborated one cause and
reported the OR.

---

## 1. The defect in one line

`simulation/departure_level_anchor.UNFITTED_YEARS[2022]` declared two independently binding causes
and named the second *"the reason that is NOT capture-scoped"* — the one a reader is told to trust
when the first is scoped away. **That one was already false when it was written.** Its number came
from a hazard the tree had replaced the previous day, and no control in the repository could see it.

| | declared at HEAD | live, same capture, today's hazard |
|---|---|---|
| 2022 SVT floor | **12.09%** | **2.34%** |
| against published ceiling | 4.30% | 4.30% |
| verdict | *"NO anchor ≥ 0 brings 2022 to the record"* | **reachable — the year is SHORT, not over** |

## 2. How it happened, and it is not carelessness

On 2026-09-01, `c628cb37d` gave `simulation.departure_risks.svt_inertia_hazard` a **required**
`market_switching_multiplier`, so the route carrying 61% of this world's departures stopped running
the flat 0.20/0.10 through both the 2020 switching peak and the 2022 collapse. That was the right
change and it was properly held. What it also did — invisibly — was move a number that a *refusal
in another module* had stated as a fact.

**The capture did not change. The capture is byte-identical.** The mechanism moved under a stored
figure. That is why every instinct to go and check the artefact would have returned "unchanged".

The next day, `docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md` restated 12.09% as
current, called it *"the one that binds"*, and built on it the **defence** of setting 2022 to
`NO_LEVEL_CORRECTION = 1.0`: *"the year runs ~2.8x above the record before the anchor touches it."*
At a floor of 2.34% the year runs **0.54x** — under the record. That defence is void and is corrected
beside its own text.

## 3. Why nothing caught it — the control shape, which is the transferable part

`test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` **does** corroborate
2022's refusal, and it is a good leg: it refuses to take the producer's word and counts renewal
decisions straight off the capture through a second reader. But the renewal decision count is
**cause (i)**. Cause (ii) is a different quantity on a different route, and no leg in that file read
it.

> **A control over a multi-cause claim reports the OR of its causes.** One corroborated cause holds
> the entry green while the other rots. This is the catalogued mixed-subject shape, arriving through
> a door nobody had marked: not a mixed *population*, a mixed *claim*.

Two further properties made it silent rather than merely uncaught:

* **The number was in prose, in a dict value, in a module no test parsed for figures.** A grep for
  `12.09` across the tree returns exactly one hit in code.
* **The two artefacts that state it disagree and nothing compared them.** The entry says 12.09%; the
  capture the band control actually reads records 12.83% under its own market-blind column. The
  declared figure was never reproducible from the capture the verdict is taken on, *before* the
  market term ever landed — it came from a different capture's denominator.

## 4. Predictions, graded beside their filed text — including the one I got wrong

| | filed | measured | verdict |
|---|---|---|---|
| **P1** floor below 4.30%, point 2.3%, band 1.8–3.0% | 2.3% | **2.34%** | **CONFIRMED** |
| **P2** the *"no anchor ≥ 0"* conclusion inverts | inverts | floor < target | **CONFIRMED** |
| **P3** 2022 renewal decisions in `c2` = 0; floor == ceiling | 0 | **0** | **CONFIRMED** |
| **P4** causes change RANK, not count: (i) binds, (ii) void | rank | as filed | **CONFIRMED** |
| **P5** declared value stays 1.0, defence rewritten | stays 1.0 | stays 1.0 | **CONFIRMED** |
| **P6** no existing leg fires; suite stays 57 passed / 2 xfailed | green | green | **CONFIRMED** |
| **P7** new leg RED at HEAD's text, green corrected; xfails unmoved | red | **red, 9.75pp** | **CONFIRMED** |

**P1 is a reproduction and I said so before running it.** `WORKER_FINDING_THE_SVT_ROUTE_CAN_NOW_SEE_
THE_MARKET_AND_THE_NEXT_GATE_IS_A_STALE_CAPTURE_2026-09-01.md` already reported 2.33% and 2.34% on
two different denominators. It was still worth running: that document is a day old, its own two
tables show the union denominator moving under it inside one day (2022: 55 → 52 accounts), and a
cited baseline from a different run than the comparison is a shape this project has paid for. It
reproduced at **2.34%** on a third population — 52 accounts here.

**What was NOT predicted and is recorded because it is a finding in its own right.** The declared
12.09% does not match the 12.83% the very capture the band control reads carries in its own
market-blind column. **The refusal's stated figure was never reproducible from the artefact the
verdict is taken on**, independently of the market term. My prereg framed this as one stale number;
it is a stale number *and* a cross-capture number. I did not predict the second and am not claiming
it as foreseen.

**Scope, stated because clause (i)'s is.** Everything above is measured on
`docs/reports/c2_departure_factors.json` + its `_svt_segment_decisions.json` sibling (148 renewal
rows, 1,221 SVT rows, 52 accounts in 2022). Every year's floor moved, not only 2022 — 2017 9.27 →
5.67, 2023 11.94 → 6.51, and 2020 *up* 9.65 → 10.06, it being the only year whose market factor
exceeds 1.

## 5. What landed

1. **`UNFITTED_YEARS[2022]` corrected beside its superseded text.** Cause (i) is named as the one
   that binds and as capture-scoped; cause (ii) is kept as a quotation, in the past tense, with what
   voided it and what survives of it (the anchor still does not reach `svt_inertia` — that clause was
   never the problem).
2. **`test_every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs`** — the
   missing leg. It recomputes each declared floor from the committed capture's own recorded inputs
   under the live `svt_inertia_hazard` rather than reading the capture's stored probability column,
   because a claim checked against the code that produced it can never go stale. Keyed to the
   property (*a stated figure reproduces*), not to 2.34. Fails closed on an empty subject.
   **Mutation-proven under `python3 -B`:** restoring HEAD's own `12.09%` fires it at 9.75pp.
3. **The design document's correction**, in two places: cause 2, and the self-flagged defence of
   `NO_LEVEL_CORRECTION` that rested on it.

## 6. What this does NOT do

**It does not put the world in band and does not discharge anything.** Both `xfail(strict)` band legs
remain xfailed, as pre-registered — correcting a refusal's stated cause changes what we *say*, not
where the world *is*. Anyone reading this as progress on the level should read §1 of the answered
document instead: neither table is band-verified until a re-capture runs, and the whole-book fit
currently **refuses every committed capture as stale** in those words (`1221 of 1221 SVT rows
reproduce under a MARKET-BLIND hazard`). That refusal is correct and is the next gate.

**A grammar convention is now load-bearing and is named here so it is not discovered by accident.**
A live floor claim is written *"SVT floor is X% against a published Y%"*; a superseded one is quoted
in the past tense. The leg matches only the present tense, so an entry can keep its own corrected
history without the history going red — which is the alternative that would have forced deletion of
the evidence.

## 7. Tree state at the time of writing

```
$ git rev-list --left-right --count HEAD...origin/main
0	0
```
Landed by pathspec on the shared tree; no `-A`, no `--no-verify`, no `git checkout <path>`, no
`git stash`.
