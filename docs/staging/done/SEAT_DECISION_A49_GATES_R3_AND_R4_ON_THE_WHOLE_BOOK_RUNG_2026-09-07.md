**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# A49 gates R3 and R4 on the whole-book rung, decided on populations and not on which rung had a number

**Decided:** 2026-09-07, delivery seat, claim `a49-decides-which-rung-gates-r3-and-r4`.
**Landed in** `tools/r1_inference_ceiling.py` (`A49_GATING_RUNG`, `the_a49_gate`),
`tools/generate_delivery_page.py`, `site/harness/index.html`, and A49's own `map_notes`.
**Held by** four mutation-proven controls in `tests/tools/test_r1_inference_ceiling.py` and one in
`site/test_harness_delivery_record.py`.

**This continues
`SEAT_FINDING_R1S_ONLY_UNBIASED_MAGNITUDE_WAS_MEASURED_AND_REACHED_NO_SURFACE_2026-09-07.md`**,
which put both rungs on `/harness/` and handed on exactly this: *"A49's gating decision is still not
made. Both rungs are on the surface so it can be made in view; choosing whichever rung has a number
is the outcome-driven selection the scope mechanism exists to prevent."* That is the decision made
here. No new measurement was taken and none was needed — the choice is between two questions, and
both of their answers were already on the page.

---

## The decision

**A49 gates R3 and R4 on `whole_book_pair_rung`, and reads its de-biased three-way magnitude
(`magnitude_three_way_split.estimate`) — never its selected maximum.**

## The two candidates, and what each one counts

Before dividing anything, what each rung's population *is*:

| | all-candidate pair rung | whole-book pair rung |
|---|---|---|
| search | all 45 pairs over 10 observables | the same search over the 6 `account_state` observables |
| winner | `perceived_bill_saving_gbp` × `mean_recent_margin_rate` | `rate_vs_svt_pct` × `mean_recent_margin_rate` |
| **population** | **69** — the accounts that reached a priced renewal | **164** — the whole book |
| de-biased magnitude | **REFUSED** (5.00 households/cell, needs 8) | **+0.2513** vs floor +0.1628, p=0.01 |
| selected-maximum verdict | does not clear | does not clear, p=0.4726 |

The populations are the whole argument. The all-candidate rung's is not 69 *yet*; it is 69
**by construction as long as a `decision_only` field can win**, because that rung's population is
set by whichever pair wins and the winner reaches through a field that exists only where a renewal
window opened. Coverage arrived on 2026-09-06 — four observables went from 69 households to 164
when `account_state_log` landed — and that rung refused before and refuses after.

## The reason, which is prior to both readings

**R3 (the score, PS/tCO2e) and R4 (products beyond price — advice, tariff fit, efficiency, solar,
heat pumps, time-shifting) are delivered to every account on supply.** A bound over the accounts
that happened to renew does not bound them. It is the ratio defect in its usual clothes: two honest
figures whose denominators are different populations, and the one being used to gate a book-wide
programme counts the renewing subset.

The whole-book rung asks the same question restricted to what the company holds for **every**
account, so its population *is* the programme's. That is a **narrower claim, not a better one** —
and the rung it displaces answers a real question, *what can be recovered about a household at its
renewal window*, which is **R2's** population. It stays on the page beside the gate rather than
being deleted, because a rung reported alone is a rung chosen.

## Why this is not the outcome-driven selection

On this book only one rung carries an unbiased magnitude, so "the rung with a number" and "the rung
over the programme's population" pick the same one *here*. Those two rules are indistinguishable by
any evidence on today's artefact, which is exactly why the decision had to be recorded rather than
read off.

Three things separate them, and all three are mechanical:

1. **`A49_GATING_RUNG` is a module constant** in `tools/r1_inference_ceiling.py`, declared beside
   `OBSERVABLE_FIELD_SCOPE` and above every run. `the_a49_gate` selects by that key. Nothing in it
   looks at a magnitude before choosing.
2. **`test_the_gate_does_not_follow_whichever_rung_has_a_number` inverts the readings** — the
   whole-book rung refusing, the all-candidate rung answering — and asserts the gate does not move,
   publishes `None`, and carries the refusal. It is the only control that can tell the two rules
   apart, and it fires on the tempting wrong implementation.
3. **The counterfactual is stated and is the same decision.** Were the readings the other way up,
   A49's answer would be *"we cannot tell what R3 and R4 could be worth"* — a result, published as
   such, neither retiring nor licensing anything.

**What would move the gate is a change of SCOPE, never a change of reading:** a `decision_only`
field honestly reclassified to `account_state` (which collapses the two rungs onto one population),
or R3/R4 redefined as renewal-window programmes. That falsifier is rendered on `/harness/` beside
the decision, because a decision published without one cannot be overturned by evidence.

Explicitly **not** done: `perceived_bill_saving_gbp` was not reclassified. Moving a field's declared
scope because it is the one blocking a figure is the same defect wearing the fix's clothes.

## What the gate says today, both readings

    magnitude (de-biased, three-way)  +0.2513  vs noise floor +0.1628   p = 0.01    n = 164
    selected-maximum verdict          +0.1963  vs p95 bound  +0.3103    p = 0.4726  DOES NOT CLEAR

Both travel together, always, because they point opposite ways and are different statistics against
different nulls — removing the selection is what buys the power. The magnitude published alone would
convert *"a magnitude over this population"* into *"a bound"*, which this rung has not earned.

**The consequence is two-sided and the page says both halves:**

- **R3 and R4 are NOT retired by R1.** There is household variation recoverable from what the
  company holds on every account on supply. The gate is open.
- **They are NOT licensed either.** R1 bounds **inference**. It says nothing about what a carbon
  score or an advice product is worth. A49's remaining work is unchanged and is what it was minted
  for: a ceiling instrument per side, each stating whether it is a true **CEILING** (perfect
  knowledge of the quantity a real method approximates, so a negative retires the candidate) or a
  handicapped **FLOOR** (bounds from below, so a negative retires nothing). Conflating those is the
  error EP13's tenth pass made and its eleventh corrected.

## A49's `map_notes` are corrected, beside the claim

The note asserted *"what closes this is COVERAGE (the pair fields populated on every household), not
a re-run"* and, later, *"What closes it is unchanged and is COVERAGE."* Refuted by the instrument's
own artefact. The original sentence is **left where it was written** with the correction beside it,
because a wrong prediction kept next to the result is the only evidence the experiment was designed
before its answer was known. The row's `level_current` is untouched: a level move is recorded, never
authorised.

## Controls, and that they can fail

Baseline green first (34 passed / 24 passed), each mutation poisoned separately, the target asserted
present before patching, and both source files restored byte-identical afterwards.

| mutation | killed by |
|---|---|
| the gate falls back to whichever rung carries an estimate | `test_the_gate_does_not_follow_whichever_rung_has_a_number` |
| `consequence` becomes an unconditional literal | `test_the_gates_CONSEQUENCE_is_derived_from_the_reading_on_every_branch` |
| `A49_GATING_RUNG` points at the all-candidate rung | `test_the_gating_rung_is_declared_where_a_reading_cannot_reach_it` |
| `whole_book_fields` admits a `decision_only` field | same |
| the page drops the gate block | `test_WHICH_RUNG_THE_PROGRAMME_IS_GATED_ON_reaches_the_reader` |
| the page emits it unconditionally, so an absent gate reads as a decided one | same, leg 3 |
| the page renders the reading without the reason | same, leg 1 |
| the page drops the falsifier | same, leg 1 |
| the page drops the losing rung | same, leg 1 |
| the refusal branch invents the other rung's figure | same, leg 2 |

`test_the_gate_on_the_REAL_artefact_reads_the_rung_it_names` is keyed to the property and never to
today's answer: it asserts the gate's figures **are** the gating rung's figures, whichever way they
fall. Pinning `+0.2513` would go red the day the book grows and green the day the lift returns a
stale constant.

## Loose ends, named rather than left to be found

- **`site/data/delivery.json` in this tree predates the gate** and regenerates on the publish lane.
  This is why the instrument-side control reads the artefact directly and the render control builds
  its own gate object rather than depending on the feed's state.
- **The committed artefact has no `the_a49_gate` key yet** — it was written before this landed. The
  instrument writes it on its next run; until then the page gets it because
  `generate_delivery_page` calls the same function on the artefact it reads. One implementation,
  two routes, deliberately: a second implementation on the publishing side is the VAT-rule shape.
- **Whether a whole-book analogue of `perceived_bill_saving_gbp` honestly exists** is still open,
  carried forward unchanged. It must be settled on the field's own merits.
- **`max(0.0, unit_rate - old_elec_rate)`** at `run_phase2b.py:2149` makes the perceived *saving*
  positive when the new rate is *higher*. Still unfixed, still not investigated here; carried
  forward from the previous turn so it does not fall off the record.
