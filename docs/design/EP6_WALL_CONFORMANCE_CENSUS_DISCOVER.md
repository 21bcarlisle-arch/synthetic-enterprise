# EP6 — the wall's conformance census: DISCOVER

**Atom:** `EP6_wall_protocol_typing` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-15 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** **HELD at 0.** The deliverable of this atom is a *protocol layer*; this document is a *measurement of
the tree the protocol layer would have to conform*. Same call as `EP10_adapter_uk_link_xoserve` and
`EP12_adapter_css_rec_switching` (both held at 0), opposite call to `EP19_counterparty_qualification_paths`
(moved 0→1, because a register was its own stated ceiling). EP6's ceiling is code.
**Measured at:** HEAD `6a33e9f0d`. Live published artefact `docs/reports/run_output_latest.json`
(mtime 2026-08-15 02:47:30, 4,156,355 bytes) parsed in full, not sampled. No network (autonomous runs have
none), so nothing here is new external research. Every claim is **observed** unless labelled **inferred** (R9).

**What this pass owed.** The 2026-08-13 DISCOVER pass on this atom
(`docs/design/simplifications/EP6_wall_protocol_typing.yaml`, findings 1 and 2) ended by naming its own
successor task and refusing to claim it had been done:

> "When EP6 opens, its first task is the census, not a design … The denominator is NOT claimed complete: this
> pass enumerated from the sketch table and the `WallResponse` importer set, not from an exhaustive walk.
> **Establishing that walk IS the census task.**"

This document is that walk. It does not open the atom and does not design anything.

---

## 0. The denominator problem, stated before any number

"Every live SIM/company crossing" has no single enumerable definition in this tree, and that — not the count —
is the finding. A crossing is *data or control passing between the world side and the business side*. The repo
has one enumerator for it, `tools/epistemic_wall.py`, and that enumerator's subject is **the import edge**: a
module under `WALL_DIRS = ('company', 'saas', 'sim', 'simulation')` naming a module on the other side. It is
sound and honest about that subject.

An import edge is one *mechanism*. It is not the *property*. So the census below is organised by mechanism,
each with its own exhaustive enumeration method stated, because a count without its method is not a census.

---

## 1. Channel A — the direct import edge. **6 live.** Walker-visible, fully ruled.

Method: `tools.epistemic_wall.live_crossings()`, run at HEAD.

| src | dst |
|---|---|
| `simulation.customer_events` | `company.crm.churn_model` |
| `simulation.customer_events` | `saas.churn_model` |
| `simulation.customer_events` | `saas.home_move_win_rate` |
| `simulation.run_phase2b` | `company.policy.decision_policy` |
| `simulation.run_phase2b` | `saas.property_model` |
| `simulation.run_phase4c_on_phase2b` | `company.billing.dd_review_runner` |

All six are `sim_reads_company` in direction (the orchestrator reaching into business code), each carries a
disposition in `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`, and
`tools/wall_crossing_dispositions.py` fails the commit if one does not. This channel is in good order: 91
examined, 6 surviving, every survivor ruled, and the ruling checked against HEAD rather than against the desk.

## 2. Channel B — the indirect import edge through a bridge. **2 live.** Walker-visible.

Method: `tools.epistemic_wall.live_indirect_crossings()`.

| src | dst | via |
|---|---|---|
| `simulation.run_phase2b` | `company.billing.account_ledger` | `background.live_payment_triad` |
| `simulation.run_phase2b` | `company.billing.payment_observation_consumer` | `background.live_payment_triad` |

## 3. Channel C — the envelope. **3 seams, 10 non-test modules.** Walker-INVISIBLE by construction.

Method: every non-test importer of `interface.contracts.*` at HEAD.

`interface/contracts/` holds four modules: `wall_envelope.py` (the `WallRequest[P]`/`WallResponse[R]`/
`WallStatus` generic pair) and three seams expressed in it — `payment_observable_seam.py`,
`conversation_seam.py`, `flex_observable_seam.py`.

| seam | world side | business side | harness/bridge |
|---|---|---|---|
| payment | `simulation/payment_seam_adapter.py` | `company/billing/payment_observation_consumer.py` | `background/live_payment_triad.py` (channel B) |
| conversation | `simulation/conversation_response.py` | `company/comms/conversation_generator.py`, `company/comms/susceptibility_estimator.py` | `background/conversation_gap_ledger.py` |
| flex | `sim/flex_dispatch.py` | `company/interfaces/sim_interface.py`, `company/market/flex_participation.py` | `background/flex_dispatch_triad.py` |

**This is the only channel that has the property EP6 exists to establish.** `schema_version: int` is required on
both request and response (no default — structurally impossible to omit); `correlation_id` is the sole link
between a request and its response and doubles as the idempotency key; `as_of` (decision clock) is kept apart
from `emitted_at` (transaction time); a malformed envelope is refused in `__post_init__` rather than at some
quieter later read.

`interface` is not under `WALL_DIRS`, so **none of these ten modules appears in channels A or B.** That is
deliberate — `tests/architecture/test_epistemic_wall_ratchet.py` asserts
`not _under_seam("interface.contracts.wall_envelope")` — and it means the walker cannot distinguish "this
crossing is envelope-borne" from "this crossing does not exist".

## 4. Channel D — the same-step typed port. **5 ports.** Walker-INVISIBLE.

Method: every `tools/*_port.py` and its non-test importers.

`market_data_port`, `credit_bureau_port`, `meter_read_port`, `acquisition_funnel_port`, `contact_centre_port`.
Each is a `runtime_checkable` Protocol whose method returns the answer **in the same call frame**. No request
object, no correlation id, no separation in time. Their message classes reach the business side directly:
`MeterReadMessage` → `company/billing/monthly_bill_assembly.py`; `CreditCheckResult` →
`company/trading/credit_limits.py`; `MarketDataPort` → `company/interfaces/point_in_time_view.py` and
`company/interfaces/bitemporal_event_log.py`.

Each message class carries a `schema_version` field and serialises it behind
`to_log_entry(include_schema_version: bool = False)`. **All three live call sites take the default**
(`simulation/run_phase4c_on_phase2b.py:237`, `:324`, `simulation/run_phase2b.py:1647`); the only three
`include_schema_version=True` occurrences in the repo are test assertions. Re-confirmed on today's artefact:
`meter_read_log` 1,600 rows, `contact_centre_log` 392 rows, `acquisition_funnel_log` 4 rows — **not one row
carries `schema_version`, and not one carries `correlation_id`.** Filed 2026-08-13 as
`docs/staging/WORKER_FINDING_THE_WALLS_CONFORMANCE_CONTROL_IS_IMPORT_SHAPED_2026-08-13.md` (LATENT, QUEUED);
this pass re-measures it on a newer artefact rather than re-filing it.

## 5. Channel E — the structurally-satisfied protocol. **At least 1.** Walker-INVISIBLE, and version-INCAPABLE.

Method: business-side `Protocol` declarations satisfied by a world object with no import in either direction.

`company/billing/monthly_bill_assembly.py` declares its own read-shaped Protocol and says so in as many words:
*"Structural on purpose: the world's own `MeterReadEvent` satisfies it as-is, so nothing had to change shape
for this cut. The company reads exactly these fields."* There is no import edge (invisible to A and B), no
envelope (not C), and no message object with a version field on it (not even D). **A structural crossing has
nowhere to put a schema version** — the whole point of the pattern is that neither side declares the other.

This channel is the one an adapter programme should worry about most, because it is the cheapest to add and
the only one with no possible place to hang a protocol property. It is also the pattern the KNIFE cuts
*produced*: converting an import edge into a structural read is how several of the 91 register rows were paid
down. **That is a real reduction in coupling and a real reduction in visibility at the same time**, and this
census is the first document to say both halves. No count is claimed for this channel — enumerating
business-side Protocols satisfied by world objects requires a walk this pass did not build, and one confirmed
instance is enough to establish the class.

## 6. Channel F — the published artefact. **91 of 92 top-level keys, 11 reader modules.** Walker-INVISIBLE.

Method: exhaustive over the artefact's own key set — for each of the 92 top-level keys of
`run_output_latest.json`, grep `company/` and `saas/` for a literal key access (`.get("k"`, `.get('k'`,
`["k"]`, `['k']`).

**91 of 92 keys are read by at least one company/saas module.**

| reader | keys read |
|---|---|
| `saas/reporting/annual_report.py` | 91 |
| `saas/reporting/css_statement.py` | 12 |
| `saas/reporting/segment_report.py` | 11 |
| `company/portal/app.py` | 4 |
| `company/compliance/crisis_bad_debt_validator.py` | 2 |
| `company/finance/bad_debt_reconciliation.py`, `company/finance/board_dashboard.py`, `saas/reporting/portfolio_composition.py`, `saas/reporting/margin_attribution.py`, `saas/reporting/payment_health.py`, `saas/reporting/shadow_retention.py` | 1 each |

Eight of those keys carry a field whose *name* asserts SIM ground truth — `bills`
(`true_consumption_kwh`, `true_commodity_amount_gbp`, `true_total_amount_gbp`), `meter_read_log`
(`true_consumption_kwh`), `demand_estimation_log` (`true_eac_kwh`), `feedback_survey_log`
(`true_satisfaction`), `churn_basis_risk` and `company_event_log` (`sim_churn_probability`),
`basis_risk_terms` (`sim_fwd_gbp_per_mwh`), and `churn_model_performance`. **`churn_model_performance` is a
false positive of the naming heuristic** — its `true_positives`/`true_negatives` are confusion-matrix cells,
not ground truth. Seven genuine.

That ground truth is in the published bytes is a **known, already-registered latent gap** from `W4_1`'s
2026-07-22 red-team (the accessor is enforced, the wire is not) — re-confirmed here, not filed as new. Two
observations that are this pass's own:

1. The business side is not merely a *reader* of those fields. `company/billing/monthly_bill_assembly.py`
   `_annotate_billing_basis` **writes them**: it takes `true_bill` as an argument and stamps
   `true_consumption_kwh` / `true_commodity_amount_gbp` / `true_total_amount_gbp` onto every estimated bill,
   deliberately and with a stated reason (the true-vs-billed pair is what makes catch-up rebilling
   measurable). Whatever the merits, a conformance control that only inspects *reads* would find nothing here.
2. **Nothing in the repo reads this wire.** Grepping `tests/` for an assertion over `true_*` in published
   output returns two files, and neither asserts it: `test_epistemic_wall_ratchet.py`'s only hit is a comment,
   and `test_household_identity_is_the_worlds.py` has none. There is no control on channel F at all.

---

## 7. What the census establishes, and what it explicitly does not

**Establishes (observed).** Six mechanisms carry data across this wall. The repo's one enumerator sees two of
them, covering **8 crossings**. The other four are invisible to every automated control in the tree, and the
widest of them is **91 keys wide with 11 reader modules**. The register itself does not claim otherwise —
`WALL_CROSSING_DISPOSITION_REGISTER.md` §5 says it decides nothing "about the Epoch-3 adapter programme". The
gap is disclosed, not hidden; it is simply unmeasured until now.

**Does NOT establish (and this is the trap in the 91).** *Key access is not provenance.* Many of those 92 keys
are the business side's **own output** round-tripping through the run harness — `management_accounts`,
`ledger_pnl`, `enterprise_value_gbp`, `_ledger_headline`. Reading those back is not a wall crossing at all. So
**91 is the width of the CHANNEL, not the count of SIM→company crossings**, and anyone who quotes it as the
latter will be wrong. Deriving the true subset requires per-key provenance — which module first wrote each key
into the run output — and that walk is the next measurement, not this one. The seven ground-truth-named keys
are a *lower bound* on the genuine subset, established by field naming rather than by tracing the writer.

**Also not established:** a total for channel E, for the reason given in §5.

---

## 8. FRAME — what this means for the atom's exit criterion

The 2026-08-13 pass recommended a conformance census with a shrink-only allowlist. The measurement above
**sharpens that recommendation in one specific way and weakens it in another**, and both belong on the record
before anyone builds to it.

**Sharpened.** The allowlist's unit cannot be "the crossing", because five of the six channels have no stable
identifier for one. Channels A and B have `(src, dst)` module pairs — that is exactly why the register works.
Channel C has a seam module. Channel D has a port class. Channel F has a **key**. Channel E has *nothing*. An
exit criterion of the form "every crossing is envelope-borne or grandfathered" is therefore **not directly
testable at HEAD today**, and an atom that adopted it would be adopting an unfalsifiable criterion — the
failure mode this project files under R15 and has now seen enough times to expect. The testable form is
**per-channel**: each channel gets its own enumerator and its own shrink-only list, and the exit criterion is
that every channel *has* an enumerator. Channel F's is the cheapest and is already written — it is §6's method,
seven lines of Python.

**Weakened.** "Migrate every crossing onto the envelope" is the wrong target for channel F. The published
artefact is a *report*, not a counterparty message; wrapping 92 report keys in `WallResponse` would be the
protocol cathedral this atom's own `origin_note` forbids by name ("no adapters-for-future-adapters, no protocol
cathedral"). The defensible target for F is **provenance, not envelopes**: know which keys originate world-side,
and prevent that set from growing silently. For D it is the opposite — those five ports *are* counterparty
stand-ins, they already own a version field, and putting it on the wire is the whole of their conformance.

**The one thing this atom should NOT do first is design.** Its highest-value first BUILD move, when the
director opens epoch 3, is the per-key provenance walk of §7 — because until the SIM-origin subset of the 92
is known, nobody can say whether channel F is a 7-key problem or a 60-key one, and the answer changes which
of the four remaining channels is worth building a protocol for at all.

---

## 9. Record

Level held at 0; no map level move, no `file_scope`, no BUILD code. This document plus its store entry in
`docs/design/simplifications/EP6_wall_protocol_typing.yaml` are the whole output of the pass. The queued
2026-08-13 finding stays queued — it is re-measured here, not discharged, and this pass files no new finding
because everything above is either a re-confirmation or a measurement of an already-registered class.
