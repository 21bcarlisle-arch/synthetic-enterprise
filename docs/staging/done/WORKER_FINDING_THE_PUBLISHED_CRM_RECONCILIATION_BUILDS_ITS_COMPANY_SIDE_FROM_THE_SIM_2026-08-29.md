**Severity:** LATENT · **Lane:** H_harness · **Atom:** `saas/reporting/annual_report.py` / `company/interfaces/sim_interface.py`

**Class:** `measurements_that_mirror` — the instrument reads its own subject back.

# The published "SIM vs company CRM" reconciliation builds its company side from the SIM, and the real CRM is empty in every production run

---

## What was asked

The competitive-pressure lane closed by moving one observable OUT from behind
`if sim_interface is not None` (`simulation/run_phase2b.py:1802-1815`), because that guard is
never satisfied on the production path and the ledger's numerator therefore never filled while
its denominator did. The drawn instruction was to sweep the pattern: **every other call site
behind that same guard, and whether its observable is silently absent in every `run_phase4c` run.**

This is that sweep. It found the expected absence, and one thing that was not expected.

## The sweep: five guarded call sites, all dead on the production path

`simulation/run_phase2b.py` has five surviving `if sim_interface is not None` guards:

| line | call | observable |
|---|---|---|
| 1777 | `notify_retention_attempt(...)` | offer made, outcome unknown at the time |
| 1821 | `notify_churn(...)` | an account left |
| 1853 | `notify_acquisition(..., channel="home-move-win")` | successor activated |
| 1953 | `notify_acquisition(..., channel="market-acquisition")` | fresh win |
| 1983 | `notify_retention_attempt(..., outcome="retained")` | offer made and held |

`main()` and `_main()` both declare `sim_interface=None` (`run_phase2b.py:886, 906`) and neither
resolves a fallback. So the question is entirely: who passes one?

**Every production entry point passes nothing.**

| caller | call | passes `sim_interface`? |
|---|---|---|
| `simulation/run_phase4c_on_phase2b.py:175` | `run_phase2b(report_end=report_end, policy=policy)` | **no** |
| `tools/run_phase4b_on_phase2b.py:37` | `run_phase2b()` | **no** |
| `tools/run_phase3a.py:46` | `run_phase2b()` | **no** |
| `simulation/run_scenario.py:356` | `_runner.main(report_end=..., sim_interface=sim_interface)` | forwards, but its own default is `None` (line 276) and no caller supplies one |

`run_phase4c_on_phase2b.main()` is the path behind `run_annual_report`, `run_price_ladder`,
`run_phase4c_pipeline`, `run_frozen_baseline` and `run_value_cycle_ab` — i.e. behind every
published figure. The only callers that pass an interface are four tests
(`test_run_phase2b.py:261`, `test_run_phase2b_event_log.py:16`, `test_value_chain_credit_feed_wiring.py:21`),
each with a `StubSimInterface`.

**Verdict, per class, not as an OR over the mixed set:** all five observables are absent in every
production run and present only in tests. `LiveSimInterface.notify_*` writes into
`self._event_log` (`company/interfaces/sim_interface.py:444, 486, 497, 507`) — a `CompanyEventLog`
that, on the production path, is constructed and never written to.

## The thing that was not expected

The obvious next question is what that starvation breaks downstream. The answer is *nothing* —
and that is the finding, not the reassurance it first reads as.

`saas/reporting/annual_report.py` publishes a section headed **"Company CRM — Event Log"**,
subtitled *"Dated artefacts of customer lifecycle events as seen by the company layer"*. It does
not read the company's event log. It reads `data["company_event_log"]`, which
`simulation/run_phase2b.py:2934` fills from `_build_company_event_log(...)` — a **SIM-side**
function (line 629) that projects the sim's own `customer_events_log`. The company layer never
touches it. A section titled as the company's record of what it saw is the world's record of what
happened, relabelled.

That would be a naming defect on its own. The reconciliation table below it makes it a mirror.

`annual_report.py:3566-3612` publishes:

> **SIM ground truth vs company CRM reconciliation (year-end snapshots)** — | Year-end | SIM churned (cumulative) | CRM active | Match |

and builds the "CRM" side by **replaying `cel` into a fresh `CompanyEventLog`** (line 3574-3591) —
the same list that is already the "SIM" side. Then:

```python
crm_churned        = {e["customer_id"] for e in cel if churn and date <= year_end}
sim_churned_by_year = {ba for ba in churned_ba if ∃ cel churn event for ba, date <= year_end}
match = "yes" if crm_churned == sim_churned_by_year else "mismatch"
```

`sim_churned_by_year` is `crm_churned ∩ churned_ba` **by construction**. The two sides are equal
iff `crm_churned ⊆ churned_ba`. And both are written in the same branch of the same loop:
`churned_billing_accounts.add(billing_account)` at `run_phase2b.py:1800`, and the `"churned"`
event that `_build_company_event_log` filters for, eight lines apart, unconditionally.

So the Match column is a one-sided containment check between two projections of one event stream.
It is structurally incapable of reading "mismatch" for the failure it exists to catch — an account
the world churned that the company's record missed — because that account is simply dropped from
both sides.

**Measured, not argued.** Running that block's exact logic against hand-built inputs:

| case | world churned | CRM holds | Match reads |
|---|---|---|---|
| A | A, B | A only — *the company missed a departure* | **yes** |
| B | A | A, B — company invented a departure | mismatch |
| C | A, B | **nothing at all** | **yes** |

Case C is the one that settles it: **a completely empty company CRM — precisely the state the dead
guard produces — reconciles as "yes" against a world that churned every account.** The control is
oriented to catch the direction that cannot happen (the CRM inventing churns, since it is built by
replaying the world's own list) and is blind in the direction that is actually true today.

**This is the R15 containment shape and the mirror shape in one control:** the
published claim "the company's CRM agrees with the world" is a claim the code cannot falsify, and
the CRM it names was never consulted.

The starved seam and the mirrored reconciliation are the same defect seen twice. The guard made
the real CRM empty; because the report reconstructs the CRM from the sim instead, the emptiness
never surfaced. Sixteen green tests and a published "Match: yes" column, over a ledger with
nothing in it.

## What is owed

1. **The report section must be renamed or rewired.** Either it is the world's event log and says
   so, or it reads `LiveSimInterface.event_log` and the seam gets plumbed. It cannot be titled as
   the company's and sourced from the world's.
2. **The reconciliation must be able to fail.** A containment check between two projections of one
   write is not a reconciliation. If the two sides cannot be made independent, the table should be
   deleted rather than published — a control that cannot fail is worse than no control, and this
   one carries a "Match" column into a public artefact.
3. **The five guards need the 1802 treatment or an honest refusal.** The pressure ledger's repair
   is the pattern: book the observable where every event passes, unconditionally, and let an
   *unarmed* consumer decline to update rather than read silence as absence. Whichever of the five
   observables has a real consumer should move out from behind the guard; the rest should be
   deleted, because an injected seam that only tests satisfy is a seam that documents an intention
   nobody implemented.
4. **A control keyed to the property**, not to today's answer: assert that the reconciliation's two
   sides do not share a writer. Pinned to the current "yes" it would go red exactly when the report
   became more honest.

## Prediction, filed before the repair

If item 3 is done for `notify_churn` — booking the CRM churn record where line 1800 already books
`churned_billing_accounts` — the Match column will still read "yes" for every year, because the
defect is item 2, not item 3. If it reads "mismatch" anywhere, my account of the containment
algebra above is wrong and this document is corrected beside itself, not over itself.

## Note on the drawn work this sweep came from

The two commits the instruction asked for were **already in HEAD** when this tick opened.
`c5641b12f` carries both `twelve_month_window_open` (`customer_events.py:46`, call site
`run_phase2b.py:773`) and the pressure hunks (`run_phase2b.py:31, 1812-1815`). The working tree
shows `run_phase2b.py` clean. The instruction's "done means `git show HEAD:simulation/run_phase2b.py`
contains `arm_loss_reporting`" is satisfied — by another lane, in one commit rather than two, so
the two-lane attribution the instruction wanted is not recoverable. Nothing was re-landed; only
this sweep, which was the half that had not been done.

---

## Repair, and the prediction graded beside itself (2026-08-29)

All four owed items landed in one commit. What was done:

1. **Renamed.** `## Company CRM — Event Log` → `## Customer Lifecycle Events — SIM Record`,
   on both surfaces (the populated section and the empty-run early return, which carried the
   old title too). The section now names `_build_company_event_log` as its source in its own
   body, and states on its face — not in a footnote — that there is no company record to
   reconcile against because `CompanyEventLog` has no production writer. Rewiring was rejected:
   the report reads a JSON artefact, and the only thing available to fill a `CompanyEventLog`
   with is the SIM's stream, so "rewiring" would have rebuilt the mirror one layer down.

2. **Deleted, not repaired.** The Match column, the "CRM active" column and the
   reconciliation heading are gone. What replaced them is a cumulative churn/acquisition
   count per year-end, labelled *one source, no cross-check*, with the note that accounts
   already on supply at run open emit no event and are in neither column — which the old
   "CRM active" figure silently omitted while being read as a book position.

3. **All five guards deleted, and the parameter with them.** No production entry point passed
   an interface, and none of the three observables had a consumer outside tests
   (`LiveSimInterface.event_log` and `StubSimInterface.*_notifications` are read only by
   `tests/company/interfaces/` and the four fixtures that injected the stub). None qualified
   for the 1802 treatment, because the pressure ledger's repair worked by booking an
   observable the COMPANY has — and an event stream the world hands over is not that. The
   `SimInterface.notify_*` methods stay: they are the company's API for recording what the
   company itself observed. What was wrong was the *world* calling them. `sim_interface` is
   also removed from `run_phase2b.main`/`_main` and `run_scenario.run_forward_scenario`,
   because an accepted-and-ignored parameter is fail-silent — a caller can pass one and get
   nothing booked.

4. **Control keyed to the property**, at `tests/saas/reporting/test_crm_section_cannot_mirror_itself.py`:
   no agreement verdict in the rendered section; `annual_report` does not *import*
   `company.crm.event_log` (parsed via AST, not grepped — the module's own prose names it while
   explaining why it doesn't use it, and a substring check would go red for the comment that
   records the repair); and `run_phase2b` gates no `notify_*` call behind any `is not None`
   test, keyed to the shape rather than to the parameter's name.

**Mutation proof — every leg red at HEAD (`29723c931`), measured, not argued.** Running the new
control's assertions against `git show HEAD:` versions:

| assertion | at HEAD |
|---|---|
| section publishes no agreement verdict | **red** — render contains `\| Match`, `reconciliation`, `crm active` |
| report does not import `company.crm.event_log` | **red** — imported at line 3574 |
| heading names the SIM as source | **red** — `## Company CRM — Event Log`, both surfaces |
| no `notify_*` behind an is-not-None guard | **red** — 5 sites: 1778, 1822, 1854, 1954, 1984 |

And the old renderer's own output on the fixture, which is the finding restated as data:

```
| 2020-12-31 | 1 accounts | 1 active | yes |
| 2021-12-31 | 2 accounts | 0 active | yes |
```

Two accounts churned, zero active, **Match: yes**.

### The prediction, graded

> *If item 3 is done for `notify_churn` … the Match column will still read "yes" for every
> year, because the defect is item 2, not item 3. If it reads "mismatch" anywhere, my account
> of the containment algebra above is wrong.*

**Not observable as stated, and confirmed by the route that was available.** Items 2 and 3
landed together, so the "3 without 2" world was never rendered — the prediction as written
cannot be graded by observation, and that is a defect in how it was framed, not a result. It
asked about a state the repair had no reason to pass through.

What *can* be graded is the algebra it rested on, and that is now pinned in code rather than
argued. `test_the_containment_check_could_not_fail` runs the deleted function verbatim:

- **Case C** (world churned A and B, CRM holds nothing — the state a plumbed-but-starved
  `notify_churn` would still have produced, since the guard was the only writer): `yes`.
- **Case A** (world churned A and B, CRM holds A — the company missed a departure): `yes`.
- **Case B** (CRM invented a churn): `mismatch` — the only direction it could see, and the one
  a replay of the world's list cannot produce.

So the claim underneath the prediction holds: the Match column could not have read "mismatch"
for a starved CRM under any completion of item 3. The lesson for next time is about the
prediction's *frame*, not its content — a prediction conditioned on a repair sequence nobody
would choose is unfalsifiable by construction. The one to have written was the case-C
assertion, which is what the control now holds.

### Coverage removed, and what replaced it

Four tests went with the seam: `test_sim_interface_churn_notifications_match_churned_accounts`,
`test_stub_churn_notifications_have_extended_fields`,
`test_stub_retention_notifications_count_matches_log`, `test_sim_interface_none_still_works`.
The first asserted a real property across a seam no production run plumbed, so
`test_every_churned_account_appears_in_the_event_log` now asserts the same property on the
projection that actually exists — **symmetric**, where the old one was a one-sided
`for cba in churned: assert cba in notified` that could not see an event log carrying a
departure the run never booked, plus a non-empty guard so a truncated window cannot pass it
vacuously. That check is named in the test as internal consistency between two SIM
projections, explicitly *not* a company-vs-world reconciliation — the distinction this whole
finding is about.
