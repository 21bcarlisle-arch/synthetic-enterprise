# DISCOVER — D27: what set each scenario constant's VALUE, and what the choice cost

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: idle`)
**Stage:** DISCOVER only. **No BUILD code was written** — the atom is epoch-parked and BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Nothing here is landed in `tools/couple_w2_11_d5.py`.
**Date:** 2026-08-14 (worker tick, DISCOVER/FRAME lane)
**Takes:** `docs/design/D27_BELIEF_WINDOW_RESHAPE_FRAME.md` §7 third bullet — *"`DD_FAILURE_WINDOW_DAYS`
is not the only constant chosen to remove a confounder, and the census of such choices still does not
exist"* — which is also Hour #9's third lead, in the finding that minted this atom.

---

## 1. The gap this census fills, stated against the census that already exists

`SCENARIO_CONSTANT_CENSUS` (built by D30, `tools/couple_w2_11_d5.py:5712`) is a good control and it
answers a different question. Its two measured fields are `bounds_resolution` and `sets_edges`, both
established by **perturbing the age-span predictor one day and seeing which edge moves**. That is a
census of each constant's **mechanical ROLE in the book**.

What no field records is **why the value is the value** — and that is the whole of D27's complaint one
level up. D27 is not "400 was the wrong number"; it is *"a design note stood in for a measurement."*
A constant whose role is censused and whose **choice** is not is precisely the shape that produced
this atom, so the census's subject has to be the choice, not the role.

Two consequences fall out immediately, both checkable off the source:

* the census's `why` strings describe role (e.g. `DD_FAILURE_WINDOW_DAYS`: *"NOT A BAND CONSTANT — it
  is the ORIGIN the band is measured from"*), never provenance; and
* `sets_edges` is measured against the **predictor**, so a constant that is inert on the band's edges
  and still **moves a published figure** is censused as inert. Exactly one constant has been checked
  for that third property — `DD_FAILURE_WINDOW_DAYS`, by D27's own FRAME — and §3 below shows the
  second one moves a headline by up to a third.

## 2. The census: what set each value (observed off the source, R9)

Subject: the eight constants `scenario_constants()` derives from `build_scenario`'s AST — the same
subject `SCENARIO_CONSTANT_CENSUS` fails closed on, so this census cannot silently cover fewer.

| constant | value | stated reason **at the definition site** | provenance class |
|---|---|---|---|
| `BILLING_CYCLE_SPREAD_DAYS` | `= PERIOD_SPACING_DAYS` | 27 lines of it: a resolution fix, *"the cycle length itself — the only non-arbitrary choice available"*, fixed before any post-reshape figure was read | **derived + argued** |
| `PAYMENT_TERMS_DAYS` | 14 | *"matches account_ledger/arrears_engine's own default"* — and it does (`arrears_engine.py:100,186,408,796`) | **organ-derived, by hand** |
| `AS_OF_BUFFER_DAYS` | 30 | *"comfortably past payment_terms + the ARUDD lag window"* | **confounder-removal** |
| `DD_FAILURE_WINDOW_DAYS` | 400 | *"Generous on purpose: isolates the CHANNEL blind spot … rather than letting the belief's own recency-decay window confound the reading"* | **confounder-removal** |
| `N_PERIODS` | 3 | — none | **unstated** |
| `PERIOD_SPACING_DAYS` | 21 | — none | **unstated** |
| `FIRST_DUE_DATE` | 2024-01-15 | — none | **unstated** |
| `BILL_AMOUNT_GBP` | 120.0 | — none | **unstated** |

The only text covering the last four is the section header: *"frozen, illustrative harness
scaffolding (R13-style; not a baseline-world fidelity claim, not director curriculum)"*. That is a
statement about what the constants are **not** — correctly, and it is why R13 is not engaged here —
and it is not a reason for any particular value.

**The census's own headline, and it is not the class the lead asked for.** The confounder-removal
class has two members, as the lead guessed. But the largest class is **unstated (4 of 8)**, and it
contains `N_PERIODS` and `PERIOD_SPACING_DAYS` — *the two constants that set the band's upper edge,
the two `D30_the_belief_band_is_this_books_length` exists to change.* D30 is currently positioned to
move a number that has never had a stated reason, which makes "what does the new value buy" a
question with no baseline to answer it against. That is a handoff, in writing, and it is the reverse
of the direction this lead was looking.

**`PAYMENT_TERMS_DAYS` carries D27's own criterion-1 exposure.** The FRAME requires the window be
`inspect`-derived from `PaymentObservationConsumer`'s default rather than hand-typed, because a
hand-copy silently re-opens the gap if the organ moves. `PAYMENT_TERMS_DAYS = 14` is a hand-copy of
`arrears_engine`'s default — correct today (verified above), unpinned tomorrow. Same defect, one
field over; recorded here rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE).

## 3. The second confounder-removal constant, measured (2026-08-14, n=300, seeds 7/11/23)

Method: shipped `build_scenario`/`score_triad`, `AS_OF_BUFFER_DAYS` monkeypatched in a scratch script
(§5), nothing committed to the harness.

`as_of = last_due + AS_OF_BUFFER_DAYS` (`couple_w2_11_d5.py:546-548`), so the buffer is measured
**past the due date**. Against that, take the stated reason apart:

* **`payment_terms`** — `issue = due - PAYMENT_TERMS_DAYS` (line 488). The terms are behind the due
  date *by construction*, so they are cleared at buffer **0**. The stated reason's first term does no
  work at all.
* **the ARUDD lag window** — `ARUDD_NOTIFICATION_LAG_DAYS = 2` working days (`simulation/bacs_rails.py:50`);
  the module records measured DD lags on this population of `{0, 1, 2}` days. Cleared by **~2–4**.
* the requirement the comment does **not** name: the company's reconciliation detector fires at
  `due + DEFAULT_RECONCILIATION_GRACE_DAYS`, and that constant is **5**
  (`company/billing/payment_observation_consumer.py:260`). Cleared by **~6**.

So every requirement the constant's own comment cites, plus the binding one it omits, is discharged
at a buffer of about **6**. The shipped value is **30**. What the other 24 days buy was never stated
and, until now, never measured:

| buffer | `n_truly_overdue` (7/11/23) | `ageing` gap (7/11/23) |
|---|---|---|
| **30 (shipped)** | 102 / 96 / 113 | **0.1129626 / 0.1915354 / 0.1193996** |
| 18 | 85 / 75 / 96 | 0.0907229 / 0.1790152 / 0.1110670 |
| 10 | 73 / 67 / 78 | 0.0838178 / 0.1732444 / 0.1033851 |
| 6 | 64 / 57 / 69 | 0.0789263 / 0.1682440 / 0.0805192 |

Three readings, and the first is the one that matters:

1. **The operative reason is arrears MATURITY, and it is not the stated one.** Between buffer 6 and
   buffer 30 the truly-overdue population grows 64→102 (seed 7): a short buffer scores the company
   against a book whose arrears have not finished forming, which is a genuine confounder — you would
   be measuring the harness's clock rather than the company's dating. **The 30 is defensible; its
   stated justification is not the reason it is defensible.** A reader auditing the constant against
   its comment would conclude ~6 was sufficient and be wrong for a reason the comment never gave.
2. **It is not inert on a published figure.** The `ageing` headline moves 0.1130→0.0789 (seed 7),
   0.1915→0.1682 (11), 0.1194→0.0805 (23) — **30%, 12% and 33%** of the shipped figure. The census
   records this constant as an edge-setter (true, D29's) and nothing records that a third of a
   published headline rides on the choice.
3. **The choice is monotone across the whole range tried**, on all three seeds and in the same
   direction, so this is a systematic property of the buffer and not seed noise.

**R12, explicitly:** no recommendation to change the value is made or implied, here or in the exit
criteria below. 6 is not proposed and 30 is not defended by its output. The finding is that the
choice is unmeasured, and the remedy is a recorded, measured reason — not a different number.
**R13:** harness scaffolding (when the harness reads the book), not a baseline-world fidelity claim
and not curriculum, exactly as the section header says.

## 4. What a BUILD would land, and the mutation that proves each control can fail (R15)

Not built here (epoch-gated). Owned by **D29** for the buffer and **D30** for the two unstated edge
constants; D27 owns the census shape itself and hands these over.

1. **Every censused constant declares a `value_provenance`** from a closed vocabulary
   (`derived`/`organ_default`/`confounder_removal`/`unstated`), and `unstated` is a legal, *visible*
   answer rather than an absent field — the four above must appear as unstated, not disappear.
   *Mutation:* drop the field from one entry → `check_scenario_constant_census` must raise, fail-closed
   on the keyset the way `_check_census_is_complete` already does for the subject.
2. **A `confounder_removal` entry owes a measured cost.** It must carry the published figure(s) its
   value moves and by how much, measured by re-scoring, not declared. *Mutation:* freeze the measured
   delta → must fire. *Second mutation:* make the constant genuinely inert → the entry must be
   refused as mis-classed, so the control discriminates in both directions.
3. **`organ_default` is derived, not hand-typed** — `inspect.signature`, the same rule the FRAME's
   criterion 1 sets for the window. *Mutation:* move the organ's default and leave the harness's copy
   → must fire. This covers `PAYMENT_TERMS_DAYS` today and the window when D27 builds.
4. **The "moves a published figure" leg is measured separately from `sets_edges`.** A constant inert
   on the age-span predictor and live on a headline (which is what `DD_FAILURE_WINDOW_DAYS` is, and
   what the buffer turns out also to be for `ageing`) must be recorded as both. *Mutation:* route the
   check through the predictor only → the belief window must stop being flagged, i.e. the control
   reverts to today's blindness and the mutation is visible.

## 5. Reproducing the measurement

From the repo root with `PYTHONPATH=.`; monkeypatches a module constant, writes nothing:

```python
from tools import couple_w2_11_d5 as C
BASE = C.AS_OF_BUFFER_DAYS
def run(buffer_days, seed, n=300):
    C.AS_OF_BUFFER_DAYS = buffer_days
    try:
        recs, cons, book, as_of = C.build_scenario(n, seed=seed)
        return C.score_triad(recs, cons, as_of)["ageing"]
    finally:
        C.AS_OF_BUFFER_DAYS = BASE
# buffers 30 / 18 / 10 / 6, seeds 7 / 11 / 23; read `.gap` and
# `.components["n_truly_overdue"]`.
```

## 6. What this DISCOVER does not settle

* **Whether `N_PERIODS = 3` and `PERIOD_SPACING_DAYS = 21` have reasons that were simply never
  written down.** The census records that none is stated; it does not claim none exists. D30 must
  state one before it changes either — that is the point of recording it now rather than after.
* **The scoring side.** `scenario_constants()` derives its subject from `build_scenario`, so a
  confounder-removal choice made in a *scoring* constant is outside the census's subject by
  construction. `RESOLUTION_SEEDS = (7, 11, 23)` and `AGEING_RESOLUTION_TARGET_DAYS = 1` are the two
  visible candidates and neither was examined here.
* **Whether 30 is the right buffer.** Deliberately not asked (R12, §3).
