# WORKER REPORT — D24: the organ's overdue clock is signed (L0 → L2)

**2026-08-10, worker tick.** Atom `D24_the_latency_floor_is_the_organs_clamped_overdue`,
lane `D_billing_metering`, drawn at `loop_stage: build`, closed at L2.

## What was wrong, and it was not the harness's

`company/billing/arrears_engine.age_open_items` published
`days_overdue = max(0, (as_of - due).days)`. A floor at zero is not a smaller reading —
it is a COLLAPSE. "Issued today, due in a fortnight" and "due today" were one number, so
nothing downstream could tell them apart. Two consequences, both **reproduced on the
shipped code before anything was changed**:

1. `collections_snapshot` selected the dunning path's trigger-0 step from the moment a
   bill was **issued**. A residential account whose only invoice went out that morning
   read `dunning_action='reminder'` — the company chasing a customer for a bill it had
   given them 14 days to pay.
2. The same zero also stood for *nothing at all* (`max(…, default=0)`), so an account
   with **no open items** read `dunning_action='reminder'` too.

One class: zero doing duty as "nothing", "not yet due" and "due today".

The third consequence is the one the atom was minted for. `expected_collection_misses`
compares this number against its reconciliation grace, so every counterfactual company
with a grace of zero or less fired on the issue date: a -5d detector and a -20d detector,
a fortnight apart in fact, published ONE latency (-14.0) and ONE detection gap (0.500000).
D23 declared that as this organ's debt rather than its own grid's, and was right to.

## The fix, and what it does not touch

The clock is signed: `(as_of - due).days`, negative before due, 0 on the due date.
`age_balance` likewise. **R12 — no published figure moved**: the shipped baseline is
5.0 / 0.014505 exactly as before, because a positive grace and a bucket scheme whose
lowest band is "current" read a negative day exactly as they read zero. What changed is
that the organ can now be *asked* about the days before the due date and answer.

The floor that remains is the company's own and is not this organ's to lift: nothing
exists to reconcile before the invoice is issued.

## R15, both ways (11 new mutation tests)

* `assert_overdue_clock_resolves_before_due` is a **DIFFERENCE against elapsed calendar
  time**, never a re-derivation of `due = issue + terms` — a harness copy of the organ's
  arithmetic is R15's tautology pattern. So it fires on the shipped clamp *and* on an
  unfloored weekly-quantised clock, is fail-closed on a probe that returns nothing, and
  **refuses to run** on a domain with no pre-due sample points (a vacuous claim is not a
  pass).
* `assert_dunning_requires_an_item` fires on the zero sentinel, on a disputed-only
  account and on a not-yet-due item, with a vacuity guard that an INERT selector fails.
* Both are wired into `collections_snapshot`, so a re-clamp **raises at read time**.
* **R10, the class not the instance**: `assert_age_buckets_partition` now probes from
  -400 days. The clamp was the only thing keeping negative days out of the bucket
  function; lifting it without widening the probe would have moved an untested domain
  into production.

## The harness side re-derived — because D23's own control fired by name

The moment the organ landed, `check_organ_query_grid_resolution` failed exactly as
designed: a declared collapse whose two companies now read differently is a debt
outliving its debt. Re-measured (n=300, seeds 7/11/23): -5d reads 0.0 / 0.025597 and -20d
reads -14.0 / 0.500000.

**What is left is not a debt, and the register now says which of three kinds each residual
is** — because a register with only a debt shape has two bad options here: name an atom
for a residual no atom can close, or delete the entry and lose the declaration that
catches the repair being undone.

* `-20d/-30d` collapse because nothing exists to reconcile before the invoice is issued —
  a bound on the **company's knowledge**, witnessed by `n_recon_dated_at_issue_floor`
  saturating for both and being zero at the baseline.
* `-15d/-20d` collapse only in the SET reading, because a saturated set has nowhere to go
  — a bound on the **reading's shape**, witnessed by the sibling DATE reading separating
  the same pair. `+1d` likewise.

Neither claim is takeable on trust: a knowledge-bound whose readings are **not at** the
floor is refused as a debt in disguise; a shape-bound the sibling is **equally blind to**
is refused as a dead instrument.

**New `distinct_pairs`** — two companies that must NOT read alike — is the direction
`collapsed_pairs` structurally cannot check: a collapse rule fires when a residual is
FIXED, never when a fix is UNDONE. Its mutation test re-clamps the **real** organ
(`mock.patch` over the shipped `age_open_items`), not a simulation of it.

## Evidence

* 2,608 green across every suite touching the arrears organ, the payment-observation
  consumer, the W2_11↔D5 pair and the live triad.
* 298 green in `tests/tools/test_couple_w2_11_d5.py` + `tests/tools/test_d7_ageing_measures.py`.
* 2,146 green in `tests/company/billing/`.
* Level move recorded: `docs/observability/gate_authorizations.jsonl`
  (`LEVEL_UP_SELF_CERTIFIED`, level 2, with the evidence above).
* Build note: `docs/design/simplifications/D24_the_latency_floor_is_the_organs_clamped_overdue.yaml`.

## Left open, declared rather than discovered later

`current_dunning_step`'s trigger-0 step now fires **on** the due date rather than before
it. Whether a real supplier's first reminder should sit on the due date or a few days
after it is a dunning-path question (the path data, not the clock), untouched here
because nothing in the D24 measurement bears on it.
