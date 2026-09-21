# EP5_settlement_true_ups — DISCOVER pass 3 (2026-09-21)

**Atom:** `EP5_settlement_true_ups` (lane `E_finance_treasury`, epoch 2, L0→L3, `loop_stage: idle`,
`dial_inherited: 3`, `provenance: director_ruling`). **Couples with:** `W3_2_settlement_timetable`
(L2/L2, idle, saturated).
**Draw:** LANE 3, DISCOVER/FRAME only, **no BUILD code** (epoch gating, Rule 1). Level **HELD at 0**.
**Builds on:** `EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md` (2026-08-17) and
`..._PASS2_2026-08-18.md`. At HEAD `a4f2649cf`.

This pass does not re-narrate those two. It does one thing they could not: it asks **what has
landed since, and whether their conclusions still hold** — and it looks at the one live module on
this atom's subject that neither of them surveyed.

---

## 0. The headline

**EP5's own stated precondition is discharged.** Pass 1 §0 said *"EP5's first owed artefact is not
code. It is a sourced timetable … Everything else in this atom is downstream of that, and building
the ledger's coping mechanism first would bake whichever guess happened to be nearest."*

That artefact exists, the correction it forced has landed in every reader, and a control now holds
it. The three-timetables-disagreeing finding that was pass 1's headline **no longer describes the
tree**:

| Pass 1 §0 said | At HEAD today |
|---|---|
| Three timetables, none citing a source | **One**, `settlement_reconciliation.ELEXON_RUN_MONTHS`, citing a primary Elexon document |
| World R1/R2/R3/RF = 1/3/5/28 | **2/4/7/14**, corrected `703e4dbb7` (2026-08-29) |
| Company register = 0/5/14/26/28 | **Imports the shared map** (`bsc_settlement_run_register.py:46`), `56fa3bd7b` (2026-09-06) |
| Published Door-5 feed carried a fourth hand-typed copy | **Reads the shared map**; `tests/tools/test_the_published_settlement_timetable_is_the_sourced_one.py` re-derives the expectation from it every run |
| Shares 0.60/0.25/0.12/0.03, commented not cited | **0.3093/0.3093/0.2062/0.1752**, normalised from Elexon's own published NHH curve (30/60/80/97 cumulative) |

Pass 1's open questions **1** ("which timetable is real?") and **2** ("does the atom's own name need
correcting?") are closed, and closed the way pass 2 predicted: the director's framing and this
atom's own `name:` — *"RF at 14 months"* — were the artefacts that turned out **correct**, and the
correction was owed to the code.

**So the reason EP5 was held is gone.** What holds it now is a different thing, and it is below.

---

## 1. What actually blocks EP5, stated plainly

**The company's live month-end close is built on the premise that settlement finality precedes the
close. Under the now-sourced timetable it never does — and no month ever has.**

`company/finance/accounting_close.py::close_the_books` is reached by the real run pipeline through
`company/interfaces/accounting_close.py` (`simulation/run_phase4c_on_phase2b.py:65`,
`run_phase2b.py`, `live_population.py`). It is the **only live module on this atom's subject**.
Every module in pass 1's §1 caller census — `settlement_timetable`, `settlement_run_series`,
`bsc_settlement_run_register`, `settlement_reconciler`, `period_reconciliation`,
`revenue_accruals` — is dark on the run path. **`accounting_close.py` does not appear in that
census at all.** The survey looked where settlement is named and missed where settlement lands.

Its POINT-IN-TIME NOTE is explicit, and it deserves to be read as the careful argument it is:

> *"There is deliberately NO `as_of` bound here and its absence is not an oversight: a month-end
> close is an after-the-fact aggregation of records that have **ALREADY SETTLED**, not a decision
> taken at a point in time. Nothing computed below feeds a forward-looking choice … so there is no
> future for the company to see. The blindfold binds decisions … If a future caller ever routes a
> DECISION through this output, that caller needs the bound — this module does not."*

**That argument is sound about the blindfold and silent about finality.** It is right that no
forward-looking decision is routed through the close, so no foresight bug is created. But its
premise — *records that have already settled* — is true of this repo's data structure and false of
the industry it models. `close_the_books` takes `settled_records`, described as *"the world's
settled half-hourly records (what flowed). The whole run's worth, deliberately."* In the real BSC
those records do not exist at the close: SF at 1 month, R1 at 2, R2 at 4, R3 at 7, and RF — the
last scheduled run — at **14**. At the close for delivery month M the supplier has an estimate;
17% of the eventual correction (the RF share) is still 14 months away.

So the defect is not a missing restatement hook. It is that **the live close emits a final number
where the industry can only produce a provisional one**, and a figure that was never provisional
has nowhere for a true-up to land. That, not the timetable, is EP5's real subject.

The note's own escape clause is nearly the right one and misses by a category: it anticipates a
future caller needing a *decision* bound. EP5 is a future caller of a second kind — one that needs
the output to be **supersedable**. The owed change is therefore **not** an `as_of` parameter on
`close_the_books` (the note is right to refuse that), but a run-stamped position that a later run
can supersede without overwriting.

---

## 2. Claims re-verified at HEAD — what held, what moved

Pass 1's findings, each re-asked against real disk rather than carried forward. Two literals moved.

| Pass 1 claim | Verdict at `a4f2649cf` |
|---|---|
| `revenue_accruals.py` — zero non-test callers, *"and it is the unbilled-income module this atom is named for"* | **HOLDS.** Five test files, no production importer. Unchanged in the month since. |
| `period_reconciliation.py` — zero callers | **HOLDS.** Two test files only. Its `VarianceType` already enumerates `SETTLEMENT_DIFFERENCE` and `ACCRUAL_REVERSAL` — EP5's exact landing zone, with no caller. |
| `account_ledger.py` carries `transaction_time` and never queries it | **HOLDS.** The identifier appears at the field declaration (`:88`), one docstring line (`:23`) and one pass-through copy (`:602`). No `known_at`. `as_of` still filters `valid_time` alone. |
| `get_settlement_data` stubbed to zeros in `LiveSimInterface` as well as `StubSimInterface` | **HOLDS, and is pinned.** Zeros and `_stub: True` in `StubSimInterface` (`:316`), `LiveSimInterface` (`:508`) and `RecordedSimInterface` (delegates). `tests/company/pricing/test_live_sim_interface.py:66` **asserts `_stub is True`** — a control that holds the stub in place. |
| No company-side consumer of the world's revision series | **HOLDS.** `emit_settlement_timetable` / `build_settlement_revision_log` have **zero** importers in `company/`, `saas/`, `tools/` or `site/`. W3_2's own named L3 gap (2) is untouched 10 weeks on. |
| The published `settled` clock has never met a run: *"exactly **two** basis entries, both `clock: settled`"* | **CONCLUSION HOLDS; THE COUNT MOVED — it is now three.** `portfolio.basis` carries `net_margin_gbp`, `enterprise_value_gbp` and now **`treasury_end_gbp`**, all `clock: settled`. A third published figure has been put on the clock that has never met a settlement run, in the month since the finding was filed. There is still no `billed` and no `banked` clock: C2's three clocks remain one. |

The moved literal is the instructive one. Re-running the observation rather than trusting the
sentence is the whole of the cost, and the conclusion came back **stronger**, not stale.

---

## 3. Exit criterion 2 is superseded, and the reason matters

Pass 1 §6 proposed as falsifiable criterion 2:

> *"A test asserts the company register's expected arrival months and the world's actual emission
> months are read from **different** sources, and reports the gap as a number. Mutation: point the
> company register at the world's constants → the independence test goes red."*

**The company register has since been pointed at the shared constants — deliberately, correctly,
and to fix a real published defect.** `bsc_settlement_run_register.py` now imports
`ELEXON_RUN_MONTHS` rather than restating it, precisely because *"a copy is what made the
correction miss it"* for nineteen days while the wrong figure was served under Poesys's name. The
world's duplicate is pinned to the same values by `TestConstantsMatchSharedSource`.

Two correct decisions, a month apart in different lanes, that disagree at the seam — and the
disagreement resolves in the **landing's** favour, not the criterion's:

**A settlement run's timing is published law, not a belief.** A real supplier knows exactly when
R1 lands; it does not guess. Criterion 2 asked for an independence that fidelity forbids. The
commons is the right home for a published timetable, and single-sourcing it is the right shape.

**The falsifiable gap EP5 must publish is on the AMOUNT, not the timing** — what the company
believed a cohort was worth at close, against what the runs eventually said. That gap is real,
unmeasured, and already computable: `build_settlement_revision_log` derives it from the meter-read
model's own prior-reads estimate against the settled records, with final-value neutrality proven by
construction. Nothing reads it.

**One thing to carry into the build rather than settle here.** The drift guard pins the world's
*share* curve to the company module's copy as well as the months. The shares are Elexon's published
industry curve, so a supplier may legitimately know them — but they are also the world's resolution
physics, and a single table serving as both the world's truth and the company's belief is the exact
R13 hazard pass 1 §4 named in the abstract. It is **not** a live defect (the numbers are sourced and
the company-side model is an exposure estimate, not a peek at its own realised gap), and it is not
this pass's to change. It is the question the build must answer before it adds a reader: *which of
these constants is physics, and which is the company reading the published rulebook?*

---

## 4. What this pass changes about the SIMPLICITY GUARD reading

Pass 1 §5 listed four moves, three of them wiring. They survive, with one correction and one
addition, in dependency order:

1. ~~one **sourced** timetable~~ — **DONE.** `elexon_settlement_run_timetable_verified.md`, landed
   in every reader, controlled by a published-feed test.
2. **The close emits a provisional, run-stamped position** rather than a final one (§1). This is
   new and it is now first, because 3 and 4 have nowhere to land without it.
3. The **second axis honoured** in `account_ledger.balance(as_of=…, known_at=…)` — the field is
   already on the event, the semantics are already written in `bitemporal_event_log`.
4. The world pair **wired into the run** rather than reimplemented, and consumed through the seam —
   which means `get_settlement_data` must carry a run identity and its publication date, and the
   control that asserts `_stub is True` is the thing that must go red first.
5. `revenue_accruals.py` **given its first caller**, not a second accrual module beside it.

Still the guard's own words, and now with a fifth enum to resist as well as the fourth: `RunName`
(world), `SettlementRunType` (company), `superseded_by_run` (the log) and `ELEXON_RUN_MONTHS` (the
commons) are four names for one concept. The next pass adds a reader, not a vocabulary.

---

## 5. Open questions after this pass

Pass 1's six, updated. **1 and 2: CLOSED** (pass 2 + the landed corrections). **5** (which clock the
front door publishes meanwhile) is now more pressing, not less — a third figure joined the `settled`
clock this month while the label stayed untrue. Pass 1 recommended (a), relabel now; this pass
concurs and notes the cost of waiting is monotonically increasing. **3** (is W3_2 really done at
L2?) and **4** (what is the company's estimate before the run lands? — shared with EP2 sub-atom 1)
and **6** (back-billing boundary) stand unchanged.

New, from this pass:

7. **Does `close_the_books` restate, or does a restatement post as a fresh event against the prior
   period?** The append-only log argues for the second; the P&L's readers argue for the first. This
   is the build's first real fork and it decides everything downstream.
8. **Which of the settlement constants is physics and which is the published rulebook?** (§3.)

---

## 6. Disposition

**Level HELD at 0.** `loop_stage: idle`, BUILD-gated per the draw. No code under `company/`,
`saas/`, `simulation/`, `sim/`, `tools/` or `background/` touched by this pass. No level move, so
nothing is owed to `gate_authorizations.jsonl`.

**Nothing fixed on sight.** §2's third `settled`-clock entry and §1's close-emits-a-final-number are
EP5's own subject matter and are queued as this document, not patched
(SELF_INTERRUPT_DISCIPLINE). The `_stub is True` assertion is left standing: it is honest about
today and it is the right thing to make red when the seam opens.

Evidence line and simplification note appended to
`docs/design/simplifications/EP5_settlement_true_ups.yaml`; the map row gains only its
`simplifications_count`.
