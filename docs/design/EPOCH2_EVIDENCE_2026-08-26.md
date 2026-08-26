# EPOCH2 EVIDENCE — the ruled pass, re-run at the epoch boundary

**Ruled:** `docs/staging/done/EPOCH2_EVIDENCE_PASS.md` + `EPOCH2_INTENT_RIDER.md`.
**Original run:** `docs/design/EPOCH2_EVIDENCE.md`, 2026-07-09, against that day's tree.
**This run:** 2026-08-26, against `feaa30fed`, at the boundary — epoch 1 closed at 01:07 UTC when
`W4_2` landed (`12b972fb9`), and `tools/consolidation_rhythm.py --check` reports
`epochs closed: [1]`, coverage applicable, 0 unaccounted orphans, rc 0.

Desk work only. No fixes, no refactors made in this pass. Every claim is labelled
`observed-with-evidence` (file:line, or a command and its output) or `inferred` (chain stated),
per R9.

## Why it was re-run rather than cited

The July answers were measured on a 27-account book, a 2.5MB run output and a tree without a
bitemporal log, a population draw, a dwelling-record split or a per-customer pricing arm. Four of
those six now exist. A gate that reads a seven-week-old measurement is not a gate, and the
director's instruction — run the pass, and if it passes, start the value cycle — only means
anything if the pass describes the tree the value cycle would be built on.

## VERDICT

**Five of six questions pass. Q4 fails, and it fails harder than it did in July** — not because
anything regressed, but because the book grew 15x around a read path that did not move.

| | July 2026 | now | movement |
|---|---|---|---|
| Q1 pricing decision | evolution | **decision engine exists, unwired** | the subject of the value cycle |
| Q2 late-arriving truth | foundational rework | **PASS** | bitemporal log built and consumed |
| Q3 scale | partial rebuild | **PASS, with the named risk realised** | 9.2x blob growth, still linear |
| Q4 customer truth | foundational rework | **FAIL — worse** | portal sees 18 of 263 accounts |
| Q5 independent anchoring | evolution (accidental) | **PASS, now structural** | world/company records split |
| Q6 drawn population | partial rebuild | **PASS** | `draw_population()` built and wired |

**Ruling I am taking on the Q4 failure, rather than stopping at it.** Q4 does not gate the value
cycle and it must not be used to defer it. The value cycle's question is whether a per-customer
decision made from company observables beats a flat rule on *realised* outcomes, and that question
is answered inside a run, where `company/pricing/value_based_renewal.py` is already wall-clean by
its own test (it cannot name `sim_churn_probability` and an import test refuses the edge). What Q4
bounds is what may be CLAIMED from any surface the portal renders — and that is a publishing
constraint, not a build one. Recorded here so the choice is reviewable: the alternative was to hold
the epoch's headline work behind a portal read path, which would be holding at a dial.

---

## Q1. How are retail tariffs actually set today?

**observed-with-evidence.** The flat rule is unchanged and is still the only thing that prices:
`saas/tariff_pricing.py:30` — `TARGET_MARGIN_GBP_PER_MWH = 2.00`, added at
`saas/tariff_pricing.py:101` inside `price_fixed_tariff()`.

**observed-with-evidence.** The one per-customer lever inside that function is STILL DEAD, seven
weeks after the July pass named it dead. `grep -rn "profitability_uplift_per_mwh=" --include=*.py`
over the tree returns exactly two hits, both in
`tests/saas/test_tariff_pricing_characterization.py:48` (one of them the July worktree's copy).
No production call site passes it. `company/crm/customer_profitability.py:176`'s
`compute_profitability_uplift()` is still computed and logged
(`simulation/run_phase2b.py:1349`, `:2827`, rendered by
`saas/reporting/annual_report.py:2922`) and still never reaches a price.

**observed-with-evidence.** What HAS changed is that the decision engine now exists.
`company/pricing/value_based_renewal.py::decide_margin(arm=...)` chooses a margin per customer by
maximising expected discounted contribution against the company's own churn estimate, with
`FLAT_RULES` frozen beside it as the control by importing the constant rather than restating it.
Its only callers are `tools/couple_value_based_pricing.py:373-374` and its tests — it is **not
wired to `company/pricing/renewal_desk.py`**, deliberately and with the reason recorded.

**inferred.** Q1's July answer ("real cost-stack infrastructure, no governance on the margin
itself") is still the right description of the SHIPPED price. The difference is that the missing
half is now built and sitting beside the price rather than absent — which converts Q1 from a design
question into a wiring-and-evidence question, and that is exactly what the value cycle is.

## Q2. What is the event model, and could truth arrive late?

**observed-with-evidence.** `company/interfaces/bitemporal_event_log.py` exists and is consumed by
three production readers rather than one experiment:
`simulation/settlement_run_series.py:57,112,169` (the settlement run series is built ON a
`BitemporalEventLog`), `simulation/settlement_timetable.py:18-30` (SF→R1→R2→R3→RF reuses the same
log, and its docstring records why it is not a wall crossing), and
`company/billing/account_ledger.py:592` (`emit into a BitemporalEventLog` — "the shared seam").
`company/interfaces/point_in_time_view.py` is the as-of reader over it.

**inferred.** July's answer — "exactly one clock, computed once, with a cosmetic second clock on
the bill document" — no longer describes the tree. The settlement timetable is the real second
clock and it runs on the real 28-month calendar. This was July's most expensive finding
("foundational rework… an architectural change to the compute model itself") and it is the one that
has actually been paid for. **PASS.**

**What this pass does NOT assert:** that every downstream P&L/CLV consumer reads through the
as-of interface. That was not measured here and should not be inferred from the above.

## Q3. What do compute and storage actually scale with?

**observed-with-evidence.** Six consecutive full runs, `docs/observability/sim-runner-log.md`
(2026-08-25 23:04 through 2026-08-26 04:09): `elapsed_s` 700, 695, 717, 704, 743, 700 — call it
**~11.7 minutes**, against July's 477s. `size_kb: 23112` on every one of the six, against July's
2506 — **9.2x**, on a book that went from 27 accounts to 263 (`per_customer_lifetime` in
`docs/reports/run_output_latest.json` holds 263 keys; the file is 23,666,723 bytes on disk).

**inferred.** Both axes moved SUB-linearly against the book (9.7x accounts → 9.2x bytes, 1.47x
wall-clock), so nothing here is super-linear and the settlement core scales as July predicted it
would. **PASS on the mechanism.**

**The named risk is now realised rather than hypothetical, and that is worth stating separately.**
July wrote: *"the bigger risk is the JSON-blob-per-run storage model itself — at 100x customers the
~2.5MB run_output would become ~250MB, and this file is read wholesale by nearly every
`tools/generate_*.py` consumer."* It is 23MB today and still read wholesale. The prediction was
right, the threshold has not been crossed, and the consumption pattern has not changed. Not a
blocker for the value cycle; a standing item that gets worse on a schedule nobody reviews.

## Q4. Customer truth: read from the SIM, or discovered through interfaces? — **FAIL**

**observed-with-evidence.** `company/portal/app.py:52` still reads
`from saas.customers import CUSTOMERS`, and `company/portal/app.py:171` still builds
`_CUSTOMER_INDEX: dict[str, dict] = {c["customer_id"]: c for c in CUSTOMERS}` — **at module import
time**, from that list alone. Twenty-five call sites in that file resolve an account through
`_CUSTOMER_INDEX` (lines 114, 209, 220, 239, 263, 292, 307, 313, 339, 348, 376, 381, 403, 438, 491,
520, 538, 553, 564, 581, 625, 644, 657, 684, 703).

**observed-with-evidence.** The roster that index is built from holds **18 records**:

```
$ python3 -c "from saas.customers import CUSTOMERS, SUCCESSOR_CUSTOMERS, ACQUIRED_CUSTOMERS, DRAWN_CUSTOMERS; ..."
CUSTOMERS 18 SUCC 6 ACQ 0 DRAWN 0
```

The book the company actually runs is **263** (`per_customer_lifetime`, above). The other three
rosters are populated DURING a run, in the run's own process.

**observed-with-evidence.** A seam that would return all four already exists and the portal does
not use it: `company/interfaces/supply_book.py:78-90` imports `CUSTOMERS`, `SUCCESSOR_CUSTOMERS`,
`ACQUIRED_CUSTOMERS`, `DRAWN_CUSTOMERS`, `get_customer` and `_register_drawn_customers` and exposes
them as the registered book; `saas/customers.py:549` unions all four in `get_customer()`.

**inferred, and this is the part that is worse than July.** The July finding was about the KIND of
data the portal reads — physical property ground truth a real supplier would have to discover. That
is still true and unfixed. What is new is a consequence that can be counted: because the index is a
static snapshot of a literal taken at import, **the company's own customer-facing surface can
resolve 18 of its 263 accounts** — the other 245 receive `401 Account '<id>' not found` at
`/login` (`app.py:208-213`) and `404 Account not found` at `/account/{id}` (`app.py:220-221`),
both `observed-with-evidence` in the source rather than inferred from the count. And it cannot be
fixed by swapping the import alone, because acquired and drawn accounts live only in a run's
memory and there is no store for a separate process to read. That is the same structural gap Q4
named, arriving as an outage rather than as a purity argument.

**Not filed as a worker finding by this pass** — it belongs to Q4, it is recorded here with its
evidence, and the disposition is the epoch's, not this document's.

## Q5. Are customer generation and validation independently anchored? — **PASS, now structurally**

**observed-with-evidence.** The two sides are now separate modules on opposite sides of the wall:
the world's dwelling record is `simulation.dwelling_records.ASSET_PROFILE_BY_CUSTOMER`
(named at `saas/property_model.py:131`), and the company's guess is `saas/property_model.py`, whose
own docstring states the property that makes the independence structural rather than accidental:
*"**No imports from `sim/` or `simulation/`** — in particular it must NOT import the world's
dwelling record to check its own guess against, which would make the supplier right by
construction."* The company-side constants are labelled as approximations
(`saas/property_model.py:41-54`, `_SYN_MODAL_EPC_RATING = "D"`, "honest population default").

**inferred.** July's risk — *"the anchoring backlog item lands without this check, and the
generator silently starts sharing a source with its own validator"* — did not happen. The split
along the ownership line is what discharged it, and the gap between the company's inference and
the world's dwelling is now scored by the coupled triad rather than assumed away.

## Q6. Is the customer population fixed across runs, or drawn per run? — **PASS**

**observed-with-evidence.** `simulation/population_draw.py` exists, is world-side, and exposes
`draw_population(base_seed: int, **kwargs) -> List[SyntheticCustomer]` (line 572) with a named RNG
substream (`STREAM_NAME = "W2_2_population_draw"`, line 152) and its own anchor test reading the
real sources (line 28). The company receives the result through the seam
(`company/interfaces/supply_book.py:145` → `saas.customers._register_drawn_customers`), and the
report consumes `CUSTOMERS + SUCCESSOR_CUSTOMERS + DRAWN_CUSTOMERS` throughout
(`saas/reporting/annual_report.py:174-183`, `:388`, `:688`, activation noted in-file as
`generator_draw_wiring, 2026-08-13`).

**inferred.** July's blocking answer — *"there is no lever to pull"* — is discharged. The epoch-4
tournament precondition Q6 was gating now exists. What this pass did NOT verify is that two
different seeds produce two materially different books end-to-end; that is the exit test named in
THE_VALUE_CYCLE_FRAMING §M3 and it is not claimed here.

---

## What the pass says about starting the value cycle

The value cycle is the per-customer decision engine. Read against the six answers:

- Its decision function exists and is honest about what it cannot do (Q1).
- Its inputs are the company's own beliefs, and the world's truth is now genuinely separate
  from the company's guess about the same customer (Q5).
- The book it decides over is drawn rather than cast, so an answer is not a property of one
  hand-written roster (Q6).
- Truth can arrive late, so a decision can be judged against something it did not know (Q2).
- Two full runs cost ~23.4 minutes and ~46MB (Q3) — the A/B the arm's own docstring names as
  "the next step" is affordable today, which July's answer would not have supported.
- Nothing the value cycle needs passes through `company/portal/app.py` (Q4).

**So: proceed.** The one failure is real, is recorded, and constrains publication rather than
construction.
