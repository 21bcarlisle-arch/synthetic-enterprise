# WORKER FINDING — the basis line published a relation that is false for three of fourteen pairs

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/test_gap_normalisation_declaration.py::test_an_entry_that_declares_no_kind_cannot_be_written`, `site/proof/test_coupled_gaps_panel.py::test_an_undeclared_entry_says_so_instead_of_implying_the_old_relation`, `background/gap_metric.py` — the misread field is repaired at both ends and both falsifiers are landed at HEAD: an undeclared entry can no longer be constructed, and the door states its own basis per kind rather than implying the divisor relation for all of them (41 green in the two named files, re-run 2026-08-14).

**Atom:** H27_payment_belief_gap (Expert Hour #28) · **Mechanism minted:** D44 · **Date:** 2026-08-13
**Drawn as:** H27 level 2→3, loop_stage=harden

*Header form corrected 2026-08-14 (OPS13 tick): the original `SEVERITY: FINDING` is out of the
OPS9 vocabulary, so it parsed UNCLASSIFIED and, per OPS11, an unreadable severity cannot show any
lane clear — this one document held every level-raise in lane `H_harness`. The severity below states
what the Hour FOUND (a public door field carrying two meanings, BLOCKING by construction); the
discharge above states what it LEFT. Neither claim is new; only the form is.*

---

## What was drawn and what was owed

Hour #27's close named five leads. Lead (a) was the narrowest and the only one about a
number a reader of the **public Proof door** actually sees:

> `raw 0.000` on the public basis line while the gap reads 0.118 — either the raw gap
> really is ~0 and the basis line is telling the reader something surprising, or it is the
> render of a quantity that is not being carried, and nobody has asked.

Nobody had asked. This Hour asked.

## The finding — `gap = raw_gap / g0` is not true of every published pair, and the door says it is

`background/gap_metric.py`'s module docstring has stated one relation between the three
fields it publishes since atom A6:

```
    gap(w, c) = raw_gap(w, c) / g0(w)
```

and enumerated **exactly one** exempt family — ageing, deliberately un-normalised, with a
named reason constant beside it. **That enumeration was incomplete.**

Measured on the live ledger the door serves (`docs/observability/coupled_gap_ledger.json`,
14 published pairs), `observed-with-evidence`:

| pair | published gap | raw_gap | g0 | raw/g0 | relation holds |
|---|---|---|---|---|---|
| 11 others | — | — | — | — | **yes** |
| `W2_11` ↔ `D5` | 0.0834 | **0.000** | 0.5 | 0.000 | **no** |
| `W2_5` ↔ `C7` | 0.0329 | 0.0081 | 0.5 | 0.0163 | **no** |
| `W2_8` ↔ `C10` | 0.1993 | 0.3613 | 0.5 | **0.7226** | **no** |

All three failures are the same unenumerated family: `detection_measures` (atom D11, landed
2026-08-09), the **balanced** successor to the recall-only detection gap. There,
`gap = mean(missed_failure_rate, false_flag_rate)` — already a score — `g0 = 0.5` is the
**no-skill score on that same scale**, not a divisor, and `raw_gap` is **one of the two
averaged directions**. Both the metric name (`"detection"`) and the field names are shared
with the recall family that *does* divide, so nothing on the entry distinguishes them.

**What the reader was handed.** The door renders `baseline g0 <g0> · raw <raw>` on one line
for every pair, so both readings of the same field reached the same surface:

* **W2_11 ↔ D5** — `raw 0.000` beside a live headline. The miss direction really is zero:
  the company missed **no** true payment failure. The **entire** headline is the other
  direction — 242 of 1,451 truly-succeeded invoices flagged (`false_flag_rate` 0.1668), the
  wrongful-dunning exposure. `raw 0.000` beside a nonzero score reads as *"the company's own
  error is nil, the score is an artefact of the normalisation"* — the exact opposite of
  what happened, on the one dimension whose real-world cost is dunning a customer who paid.
* **W2_8 ↔ C10** — `raw 0.361` against a published 0.199. A reader applying the module's own
  stated relation gets 0.723, **3.6× the headline**, in the other direction.

Nothing anywhere asserted the relation on any population. It had never been measured.

## Why declaration and not inference (D40's negative answer, applied to a field)

A kind *inferred* from whether `gap == raw/g0` holds would classify every entry correctly by
construction and could never fire on the case it exists for — the fail-**open** direction of
this same mistake. So the kind is **declared at the construction site and checked against the
arithmetic there**, and the population control grades the **ledger on disk**, not the code
that writes it, because an entry nothing re-measures is still being served.

## What landed (atom D44)

1. **`GapResult.normalisation`** — one of `divisor` / `reference` / `none`, with **no usable
   default**: an undeclared kind **raises**. A new family that forgets to declare cannot be
   constructed, which is the only reason `detection_measures` was able to join the ledger.
2. **The declaration is falsifiable at construction** (`__post_init__`), per kind:
   `divisor` ⇒ `gap == raw_gap/g0` to 1e-9; `reference` ⇒ `raw_gap_is` must **name a published
   component** carrying the same number (prose alone would be unfalsifiable — the state this
   check exists to leave), `g0 ≠ 0`, and a live headline may not outlive an undefined
   direction; `none` ⇒ `g0 == 0.0` and `raw_gap` **is** the headline.
3. **`reference` and `none` must state WHY** there is no divisor. An unexplained exemption is
   how the first one sat unnoticed for four days.
4. **Every construction site declares** — six in `gap_metric.py`, plus the H27 latency measure
   and `couple_cohort`. The two `reference` sites are exactly the two balanced successors
   (D11 detection, D19 belief); the D19 one is not in the live ledger today and was **one
   re-measure away** from publishing the same defect.
5. **`audit_ledger_normalisation`** — the population control. Grades every ledger entry
   against the relation it declares. **Fail-closed both ways**: an undeclared entry is a
   finding, never a pass, and an undeclared entry whose numbers *additionally* break the
   stated relation is a **separate, harder** finding (`undeclared_and_relation_false`) —
   unable-to-check and already-told-something-false are not the same defect. It never raises
   on a malformed entry (a checker that dies on its own population is fail-**silent**).
6. **The door says which relation it is publishing.** `basisText()` renders per kind:
   `reference` → "no-skill SCORE 0.500 — a reference point, NOT a divisor · missed_failure_rate
   0.000 — one of two averaged directions"; `none` → "un-normalised — no no-skill divisor";
   undeclared → the numbers **plus** "basis UNDECLARED — this entry does not record whether g0
   divides the headline". Every live entry predates D44, so **that is what the door renders
   today**, and it is true.

## R15 — the mutations

Twenty write-side tests, each a defect that could be written today, not a restatement of the
declaration: an undeclared entry (**the defect that shipped**); a declared `divisor` whose
arithmetic is false; a `reference` with no reason; with no `raw_gap_is`; naming a component
that does not exist; naming one that carries a different number; with `g0 = 0`; a live
headline beside an undefined direction; a `none` with a non-zero `g0`; a `none` whose raw is
not the headline; an unknown kind word. Audit-side: undeclared reported, misleading separated
from merely-unreadable, each declared kind's own lie fired, a malformed entry not fatal, and
the writer's and auditor's vocabularies proven to be the same object.

**Not always-red**: a fully-declared ledger audits empty; the real scorers construct clean;
the `divisor` render carries no caveat at all, so the caveat keeps meaning something.

Six render-side tests execute the page's own JavaScript against the four kinds and assert the
rendered pixel — including **the old defect stated as a control**: a `reference` row must not
render `raw 0.000` without saying it is one of two directions.

## R12 — no published number moved

No scorer was touched and no gap, epsilon, band or floor changed. What changed is what the
basis line *says about* the numbers it was already rendering. The one published **string**
that moved is that line, deliberately, and the `why_inert` declaration of
`div.gap-row[0]/div.gap-basis[0]` was updated to match (the surface stays inert — Hour #27's
two-book classification is unaffected).

## The level, and why it stays 2 for the twenty-eighth Hour

The 2→3 is drawable, unblocked, and **not taken here**. L3 is the claim that this harness
measures what it says it measures. This Hour did not change any measurement — but it did
establish that a **published field on the public door has been carrying two different
meanings under one name**, on three of fourteen pairs, on the dimension whose cost is
dunning a customer who paid. Hour #4's two-consecutive-clean-Hours criterion is at zero.

## Queued, not fixed (SELF_INTERRUPT_DISCIPLINE)

* **`components["normalisation"]` already carries three different meanings** across families
  (the ageing no-normaliser reason, the misapplication "majority-class prevalence", the
  latency reason) and now sits beside a top-level `normalisation` that is the kind word. Two
  namespaces, one name, rendered in the same row. Not renamed here — four cells' tests read it.
* **The live ledger's 14 entries are all undeclared** and will stay so until runs re-measure
  with the declaring writers. The audit reports them; nothing re-measures them on a schedule.
* **`D37`–`D44` exist only in this register's prose and in no map cell** — a **seventh** Hour
  running for that lead.
* Hour #27's leads (b) the bar's unstated clamp and (c) the other six pairs' rows, plus
  D35's scoped build and Hour #21's vacuous-in-isolation sibling control, remain untaken.

---

**Evidence:** `background/gap_metric.py` (declaration + `__post_init__` + `audit_ledger_normalisation`) ·
`tests/test_gap_normalisation_declaration.py` (20 tests) ·
`site/proof/index.html::basisText` · `site/proof/test_coupled_gaps_panel.py` (6 render tests) ·
`tools/generate_proof_data.py` (passthrough) · `tools/couple_w2_11_d5.py`, `tools/couple_cohort.py` (declaring sites)
