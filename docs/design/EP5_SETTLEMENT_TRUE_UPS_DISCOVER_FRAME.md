# EP5_settlement_true_ups — DISCOVER + FRAME (2026-08-17)

**Atom:** `EP5_settlement_true_ups` (lane `E_finance_treasury`, stream `wholesale_to_price`,
epoch 2, L0→L3, `loop_stage: idle`, `dial_inherited: 3`, `provenance: director_ruling`)
**Couples with:** `W3_2_settlement_timetable` (lane `W3_industry_systems`, **L2/L2, idle**)
**Draw:** LANE 3, DISCOVER/FRAME only. **No BUILD code** — epoch gating
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Level **HELD at 0**.
**Prior work this builds on:** `EP2_VARIANCE_LEARNING_LOOP_DISCOVER_FRAME.md` (2026-08-13) §6,
which found this dependency "dark end to end" from the EP2 side. This pass re-verifies that at
today's HEAD, and finds the larger thing §6 could not see from where it stood.

---

## 0. The headline

EP2's §6 said the late-truth chain is dark. It is — re-verified below, unchanged. But the
finding that matters for EP5 is not that the timetable is unwired. It is that **this repo
contains three different UK settlement timetables, none of which cites a source, and they
disagree by up to eleven months on when a correction arrives.**

| Artefact | SF | R1 | R2 | R3 | RF |
|---|---|---|---|---|---|
| `simulation/settlement_timetable.py` — the **WORLD**, W3_2 at L2 | *(none; run is `initial`)* | **1 mo** | **3 mo** | **5 mo** | **28 mo** |
| `company/market/bsc_settlement_run_register.py` — the **COMPANY** | 0 mo | **5 mo** | **14 mo** | **26 mo** | **28 mo** |
| `THE_VALUE_CYCLE_FRAMING.md` C2 — the **DIRECTOR'S FRAMING**, and this atom's own `name:` | named | named | — | — | **"at 14 months"** |

Read those rows as a triangle rather than a table. The world emits its first reconciliation at
**1 month**; the company's own register expects it at **5**. The framing that authorised this
atom says the sequence ends at **14 months**; both implementations say **28**. The company's
`R2 = 14 mo` is the only place the framing's "14 months" appears at all, under a different run
name.

This is not the regulation-commons doctrine working. The doctrine says the company is *allowed*
to misread the law, because a real supplier can and gets fined for it — but that only produces a
meaningful gap when the **world's** copy is anchored to the real BSC and the **company's** is a
belief that can be shown wrong against it. Here neither copy is anchored to anything: the world
module's own comments say "~1 month", "~28 months" with no citation, and the company register's
say "T + 5 months (first smart/actual reads)" with no citation. Two unsourced numbers disagreeing
is not a measurable belief-vs-truth gap; it is **two guesses, and the harness cannot tell you
which one is wrong** (`feedback_agreeing_sources_may_share_lineage` in reverse — these do not even
agree, and neither has provenance).

**So EP5's first owed artefact is not code. It is a sourced timetable** — one external citation,
one authority, from which the world's physics is calibrated and against which the company's
register becomes a falsifiable belief. Everything else in this atom is downstream of that, and
building the ledger's coping mechanism first would bake whichever guess happened to be nearest.

---

## 1. Caller census (non-test importers, at HEAD `95cc1be06`)

| Module | Non-test importers | State |
|---|---|---|
| `simulation/settlement_timetable.py` | `settlement_run_series.py` only | **DARK** — world side |
| `simulation/settlement_run_series.py` | `settlement_timetable.py` only (mutual) | **DARK** — the pair imports only itself |
| `company/market/bsc_settlement_run_register.py` | `bsc_settlement_dispute_register.py`, `regulatory/network_code_modification_register.py`, `tools/generate_world_data.py` | **REGISTER-ONLY** — no run path |
| `company/market/settlement_reconciler.py` | `bsc_settlement_dispute_register.py` | **REGISTER-ONLY** |
| `company/finance/period_reconciliation.py` | **zero** | **DEAD** |
| `company/finance/revenue_accruals.py` | **zero** | **DEAD** — and it is the unbilled-income module this atom is named for |
| `company/interfaces/bitemporal_event_log.py` | 8, incl. `billing/account_ledger.py`, `interfaces/point_in_time_view.py`, `governance/decision_rights.py` | **LIVE** |

Two corrections to the prior pass, both of which I got wrong first and checked:

* EP2 §6 said `settlement_timetable.py` has "no importer in `simulation/`". A `grep -l` today
  returns `simulation/population_draw.py` — which is a **mention in a comment**
  (`population_draw.py:24`: *"NOT imported, exactly as `simulation/settlement_timetable.py`
  duplicates its…"*), not an import. §6's claim stands; my first census of it did not.
  (`feedback_count_the_consumers_before_replacing_the_one_table`: grep each importer for a CALL.)
* The company-side modules are not "dead" in the same sense as the world pair. They are reachable
  from other registers and from `tools/generate_world_data.py`, so they render into published
  world data. They are dead only on the **run path** — nothing in `run_phase2b` ever asks them
  what a settlement run said.

`SimInterface.get_settlement_data` is still stubbed to zeros in `LiveSimInterface` as well as
`StubSimInterface` (`sim_interface.py:324-331`, `_stub: True`), unchanged since EP2's pass.

---

## 2. The bitemporal foundation is real, and it is queried on one axis

This is the good news, and it is better than EP2 §6 implied. `BitemporalEventLog` is a genuine
two-axis log — `valid_time` (what the fact is about) and `transaction_time` (when it became
knowable) — append-only, with a `superseded_by_run` field already carrying values like `"SF"`,
and its docstring was written **for exactly this atom's problem**: *"a half-hour's
consumption/price goes through multiple Elexon settlement runs … that can RESTATE an earlier
figure."* `as_known_at()` / `history_as_known_at()` exist and have live callers in
`point_in_time_view`, `renewal_desk` and `decision_rights`.

**But `company/billing/account_ledger.py` — the ledger EP5 must restate — carries
`transaction_time` on every `LedgerEvent` and never queries it.** Its `as_of` parameter filters
on `valid_time` alone (`account_ledger.py:288`: `if as_of is not None and e.valid_time > as_of:
continue`); the only occurrence of `transaction_time` outside the field declaration is a
pass-through copy at line 602. So the ledger can answer *"what is true about March"* and cannot
answer *"what did we believe about March, in March"* — which is precisely the question a
restatement makes interesting, and precisely the question the log one layer down was built to
answer.

That is EP5's cheapest real move and its first falsifiable one: **`balance(as_of=…,
known_at=…)`, with the second axis honoured.** No new architecture, no new seam — the field is
already on the event, the semantics are already written down in the sibling module, and the
SIMPLICITY GUARD reading below says use them rather than build a third thing.

---

## 3. The published `settled` clock is a label, not a run

R14 is the acceptance surface this atom's own record names, so I checked what the clock currently
means on the live surface rather than in the code.

`site/data/dashboard.json` carries exactly **two** basis entries, and both read `clock:
"settled"` — `net_margin_gbp` ("Settlement-derived (total_net_gbp)…") and
`enterprise_value_gbp`. There is **no `billed` clock and no `banked` clock published anywhere**,
so C2's three clocks are, on the front door today, one clock.

And that one clock is named after the one that does not exist. Nothing in the run path imports
either settlement module (§1), so **no R1/R2/R3/RF has ever restated a published figure**;
`total_net_gbp` is the run's own single-pass arithmetic. The label is not false about its
lineage — the note honestly says `total_net_gbp` — but "settled" is the industry word for
*post-reconciliation*, and this figure has never met a reconciliation run.

Filed as a candidate finding rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE — the supply
is infinite; this is EP5's own subject matter and belongs in EP5's build, not in a drive-by
relabel). The disposition question for the build is a real fork, and it is **not** mine to close
here:

* **(a)** relabel today's figure to the clock it is actually on (`billed`, or a new
  `single_pass`), leaving `settled` unpublished until a run produces one; or
* **(b)** leave the label and let EP5's first restatement make it true.

(a) is honest sooner and makes the front door move twice; (b) risks the label being wrong for as
long as EP5 is parked, which is currently indefinite. **Recommendation: (a)**, because a wrong
clock is exactly the defect R14 exists to prevent and "it will become true later" is the
reasoning R14 was written against — but it touches a published surface, so it is written down
here for the build to take rather than taken now under a DISCOVER draw.

---

## 4. FRAME — the walls this atom is built inside

**R13 is the sharpest one here, and it cuts a way the atom's name hides.** The *timetable* — when
runs land, what share each resolves — is BASELINE-WORLD fidelity: it changes only for
fidelity-to-reality reasons, decided blind to company P&L. The *company's register* is company
belief and may be wrong. The danger is that both files are edited by the same agent in the same
session, so "the company's R1 belief" and "the world's R1 truth" can be silently converged into
one number for the convenience of a green reconciliation. **The wall is that the world's
timetable moves only with a citation, never because a restatement came out ugly.**

**R14 binds every output.** Every figure this atom restates carries its clock, and a restatement
must **supersede**, never overwrite: the log is append-only by construction, and the ledger's
reader must be able to reproduce the superseded number. A restatement that silently replaces a
published figure is the atom's own named defect.

**C-S1 (event-arrival tolerance) binds at birth, not at scale.** True-ups arrive singly, late,
and out of order by nature — R2 for March can land after R1 for April. Any logic assuming batch
completeness is wrong on day one, not wrong later. The existing log's `record_id`-ordered
`as_known_at` is the right primitive; a "wait until the run is complete" accumulator is not.

**R12: the restatement is a diagnostic.** The size of a true-up is not a target and shrinking it
is not the objective. If cohort margin restates by a lot, that is a finding about estimation, not
a cue to tune the estimate toward the settled figure.

**Coupled triad (the gap is the score).** SIM depth = W3_2's run series, which exists at L2 and
is dark. COMPANY = the ledger restating on arrival + unbilled income carried as judgement.
HARNESS = the gap between what the company believed the period was worth at close and what the
runs eventually said. Note the binding rule cuts here: **W3_2 is at L2 with `level_target: 2`, so
it is at its own target while never having been tested against a company that copes with it.**
Its saturation is a saturation of the world's half only.

**The epistemic wall.** The company may read its own settlement statements — that is an
observable, a real supplier gets them. It may not read `settlement_timetable`'s internals (the
share constants, `true_final_value`, the variance parameters). The seam is
`get_settlement_data`, and today it returns zeros; making it return *statements arriving on a
timetable* is the crossing this atom needs, and it is a typed-flow seam by the standing
preference, not a direct call.

---

## 5. SIMPLICITY GUARD reading

The simplest construct that discharges this atom is **not** a settlement subsystem. It is:

1. one **sourced** timetable (§0), which is a document plus a constant;
2. the **second axis honoured** in `account_ledger.balance()` (§2) — the field already exists;
3. the world pair **wired into the run** rather than reimplemented — `settlement_run_series.py`
   already emits the R1→RF revision sequence into a `BitemporalEventLog`, which is exactly the
   shape the ledger needs to consume;
4. `revenue_accruals.py` **given its first caller** rather than a second accrual module written
   next to it. It already models `RecognitionBasis.BILLED` vs `ACCRUED`, which is C2's
   billed-vs-unbilled distinction, and it has zero non-test callers today.

Three of those four are wiring. The guard's own words: *the wall already provides the seam, no
adapters-for-future-adapters.* The thing to resist is a fifth settlement enum: this repo already
has `RunName` (world), `SettlementRunType` (company) and `superseded_by_run` (the log) for one
concept, which is how the third timetable got written in the first place.

---

## 6. Falsifiable exit criteria (proposed; not a gate, no level moved)

Each is written so it can go RED, per R15 — a criterion that cannot fail is not a criterion.

1. **Provenance.** The world's timetable constants trace to one named external authority, and a
   test fails if a constant changes without the citation changing. *Mutation: edit `R1_MONTHS`
   alone → red.*
2. **The two copies are measurably different beliefs.** A test asserts the company register's
   expected arrival months and the world's actual emission months are read from **different**
   sources, and reports the gap as a number. *Mutation: point the company register at the world's
   constants → the independence test goes red, not the gap.*
3. **The ledger answers the second axis.** `balance(as_of=D, known_at=D)` for a period later
   restated returns the **pre-restatement** figure, and `known_at=now` returns the restated one.
   *Mutation: drop the `known_at` filter → red on the first case.*
4. **Restatement supersedes, never overwrites.** After a true-up, the superseded figure is still
   reproducible from the log, and the published figure carries the run that produced it.
   *Mutation: mutate in place → red.*
5. **Out-of-order arrival.** R2-for-March landing after R1-for-April leaves both cohorts correct.
   *Mutation: sort by arrival instead of `(valid_time, record_id)` → red.*
6. **Unbilled income is carried and disclosed.** Period close publishes accrued-not-billed with
   its own clock, and the R14 basis gate fails if it is published without one.
7. **The coupled gap is reported.** Per-cohort belief-at-close vs settled-at-RF is a published
   number per digest, with its residual, never suppressed (R12).

---

## 7. Six open questions this pass could not close

1. **Which timetable is real?** Resolvable only against Elexon/BSC published material (BSC
   Section U / the published settlement calendar), and MHHS compresses it — so the answer is
   date-indexed, and `domain_invariants`' `effective_from`/`effective_to` shape applies. **This
   is the DISCOVER task that should precede any EP5 build,** and it is a `discovery-agent` job
   (read published sources, write `docs/market_research/`), not a build job.
2. **Does the atom's own name need correcting?** It asserts "RF at 14 months" from C2. If the
   sourced answer is 28, the atom's `name:` and the framing doc both carry a wrong number, and
   R13 says the world moves to the citation — but the framing is the **director's**, so the
   correction is proposed to him, not applied to his document.
3. **Is `W3_2` really done at L2?** Its `level_target: 2` is met, but the coupled-triad rule says
   no world atom reaches L3 until a company has been tested against it. Is L2 the intended
   terminus, or a target set before the coupling rule existed?
4. **What is the company's estimate before the run lands?** Restatement is only interesting
   against a prior belief. `revenue_accruals` models the accrual but nothing computes the
   *estimated* settled cost per cohort at close — EP2's sub-atom 1 ("persist the expected margin
   at the pricing decision") is the same missing artefact seen from the other side. Possible
   shared build, possible duplication; worth one look before either lane starts.
5. **Which clock does the front door publish in the interim?** §3's (a)/(b) fork.
6. **Does back-billing law bind here?** C2 names "catch-up rebills within back-billing law" in the
   same breath as the settled clock. A settlement true-up that restates a *cost* is unconstrained;
   one that produces a customer *rebill* meets the 12-month back-billing rule. Whether EP5 owns
   that boundary or hands it to the billing lane is unresolved.

---

## 8. Disposition

**Level HELD at 0.** `loop_stage: idle`, BUILD-gated per the draw; no code under
`company/ sim/ simulation/ saas/ tools/ background/` touched by this pass. No level move, so
nothing is owed to `gate_authorizations.jsonl` (R16).

**Nothing fixed on sight.** §3's clock label and the three-timetable disagreement are EP5's own
subject matter and are queued as this document, not patched (SELF_INTERRUPT_DISCIPLINE).

**Evidence line** added to the atom's own record, `docs/design/simplifications/
EP5_settlement_true_ups.yaml`. `docs/design/maturity_map.yaml` is unchanged and clean — the atom's
fields are all still correct, and the map is not where a DISCOVER artefact belongs.
