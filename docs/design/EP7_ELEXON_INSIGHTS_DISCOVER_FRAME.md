# EP7 — Elexon Insights and IRIS, for real: DISCOVER + FRAME

**Atom:** `EP7_adapter_elexon_insights` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-14 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0. The deliverable of this atom is an adapter — code — so a document cannot move it.
Same call as `EP10_adapter_uk_link_xoserve` (held, 2026-08-13) and `EP12_css_rec_switching`; opposite call to
`EP19_counterparty_qualification_paths`, where the register *was* the deliverable.

Every claim below is **observed** against the tree at this tick unless labelled *inferred* (R9).

---

## 0. What the atom says it is, and what it turns out to be

The atom is filed as *"Adapter for the Elexon Insights Solution … REST for the full BMRS catalogue …
plus IRIS real-time push and the Data Archive. Access class OPEN NOW, zero accession cost."*

Its own `origin_note` already flags the shape: *"CLAUDE.md already records that the legacy Elexon
wrappers are partly stale after the Insights migration — so this adapter has an existing implementation
to reconcile against, not a greenfield."*

That is right, and it understates the position. **The Insights migration is not partly done, it is done
on the fetch side.** Four `sim/` modules already speak Insights REST v1, and one of them has been
running daily against the live platform for fourteen months. What is missing is not a client. It is:

1. a **typed crossing** for the prices the world publishes to the company (§3), and
2. any representation at all of the thing that actually makes Elexon interesting to a supplier — that a
   settlement figure is **revised for months after delivery** (§4).

The atom's title points at the part that is built. Its value is in the two parts that are not.

---

## 1. DISCOVER — every fetch already goes to the Insights Solution

`https://data.elexon.co.uk/bmrs/api/v1` is the `BASE_URL` in four modules. Endpoints, and non-test
importers (a file that actually `import`s the module, excluding `tests/`):

| module | endpoint(s) on Insights v1 | non-test importers |
|---|---|---|
| `sim/system_prices_history.py` | `/balancing/settlement/system-prices/{date}` | **16** — every `run_phase*`, `company/interfaces/sim_interface.py`, both prefetch/refresh jobs |
| `sim/generation_demand_history.py` | `/demand/outturn`, `/generation/actual/per-type/wind-and-solar` | 4 |
| `sim/market_index_history.py` | `/balancing/pricing/market-index` | 1 |
| `sim/system_prices.py` | `/balancing/settlement/system-prices/{date}` | **0** |

`sim/system_prices.py` (45 lines) duplicates `system_prices_history.py`'s endpoint constant and base URL
and is reachable only from its own test and the epistemic-wall ratchet's file walk. It is an instance of
the live `no_caller_and_never_runs` class, recorded here rather than deleted on sight
(SELF-INTERRUPT DISCIPLINE: queue, don't fix).

**Four of the catalogue's datasets are consumed. The atom names four more** — imbalance volumes,
disaggregated pricing stacks, dynamic BMU data, and the Data Archive — plus IRIS push. None of those
appear anywhere in the tree (`grep -i iris` over `*.py` returns nothing outside docs). That is the
breadth half of the atom, and it is genuinely unbuilt. It is also the *cheap* half: same host, same
no-key access class, same `requests.Session`. A builder will spend their time on §3–§4, not here.

---

## 2. The live rolling cache is real, complete, and frozen at D+1

`background/refresh_elexon_ssp_rolling.py` runs from `process_run_complete.py` and extends the frozen
historical decade past its `2025-06-07` boundary. Observed at this tick:

* `sim/cache/elexon_ssp_live_rolling.json` — **20,736 records, 2025-06-08 … 2026-08-13**.
  432 days × 48 settlement periods = 20,736 exactly: no gaps, fourteen months of real settlement prices
  fetched from the live platform.
* `tools/live_market.py` merges it with the frozen cache **for the live decision path only**.

So the "integrate now, real data" tier of the advisor's build order is not a proposal here. It is in
production and it works.

What it does **not** do is re-ask. `refresh()` sets `start_date = last_covered + 1 day`, so its window is
strictly forward of everything already on disk. The merge two dozen lines later —

```python
# Merge: drop any existing rows for the dates we just re-fetched (D+1 corrections win),
refetched_dates = {r["settlementDate"] for r in fresh}
merged = [r for r in existing if r.get("settlementDate") not in refetched_dates] + fresh
```

— can therefore never drop anything: `refetched_dates` and the existing dates are disjoint by
construction. **Falsified, not read** (an injected fetcher, a scratch cache, the real `refresh()`): after
`2025-06-08` is covered, no later call ever produces a window containing it. The "D+1 corrections win"
line is unreachable. Every one of the 20,736 records is the value Elexon served on the day after
delivery, and nothing in the pipeline can ever replace it.

Staged as `WORKER_FINDING_THE_ROLLING_ELEXON_CACHE_CAN_NEVER_REFETCH_2026-08-14.md` (LATENT · `W4_the_wall`).

---

## 3. The market feed is the one wall crossing that is not on the envelope

`interface/contracts/wall_envelope.py` is this project's typed, versioned wall message. Three seams are
built on it — `conversation_seam.py`, `flex_observable_seam.py`, `payment_observable_seam.py` — with 8
non-test importers between them.

The market-price crossing is not one of them. `company/interfaces/market_feed_publication.py` says so in
its own docstring, and names this atom:

> Typing the payload as a versioned message (the typed-flow seam preference, and what an Epoch-3 Elexon
> adapter would need) is owed to `EP7_adapter_elexon_insights`, which is level 0 / idle at the time of
> this cut.

What crosses today is `{"published_at": <wall clock>, "prices": [{"fuel", "period", "price_gbp_per_mwh"}]}`,
written with `open(path, "w")` — the whole file replaced on every run, holding a rolling 24-hour window.

**The envelope already has the semantics this atom needs**, which is the finding that matters for
sequencing. `WallResponse` carries `schema_version`, `observed_at` (when the answer became known) and
`valid_time` (what period it is about), and its docstring states the rule verbatim:

> a restatement (e.g. **a superseding settlement run**) is always a NEW `WallResponse` with a later
> `observed_at` for the same `valid_time`, never an edit to a stored response object.

A price feed that is overwritten in place is exactly the edit that sentence forbids. **The first EP7
crossing-side move is a reuse, not a design** — put the market feed on the existing envelope. No new
protocol, no adapters-for-future-adapters (SIMPLICITY GUARD), and the bitemporal shape the revision work
in §4 needs arrives with it.

---

## 4. The gap worth measuring: the company has never seen a price change its mind

This repo already models settlement revision, twice, on both sides of the wall, with a test asserting
the two constant sets never drift:

* `simulation/settlement_timetable.py` (world) and `company/regulatory/settlement_reconciliation.py`
  (company belief) — R1 ~1 month, R2 ~3, R3 ~5, RF ~28 months after delivery, resolving 60/25/12/3% of
  the adjustment.
* `company/market/bsc_settlement_run_register.py`, `simulation/settlement_run_series.py`,
  `company/market/settlement_reconciler.py` — **zero non-test importers each.** The
  remedy-exists-unwired shape again; nothing in a run constructs any of them.
* `company/interfaces/internal_seams.py` even carries the run type (`'SF','R1','R2','R3','RF'`) so
  billing knows how firm a position is.

Against that, `refresh_elexon_ssp_rolling.py`'s window comment reads:

```python
end_date = today - dt.timedelta(days=1)  # settlement data is final at D+1
```

**Those two statements about the same world cannot both be true**, and the one attached to the code that
touches the real platform is the one asserting finality. The atom's own `name:` field disagrees with it
too: *"Indicative settlement prices land ~15 min after each settlement period with a D+1 refresh;
Settlement messages give early warnings on calculation accuracy."* An indicative price with a refresh and
an accuracy warning is not a final price.

That is the coupled-triad gap EP7 owns, stated in the triad's own terms:

* **SIM adds depth** — the world publishes an indicative figure, then supersedes it. It already knows how
  (`settlement_timetable`), and the envelope already knows how to carry it (§3).
* **COMPANY discovers and copes** — it prices, hedges and reconciles against a figure that will move,
  and is *allowed to be wrong*. Today it cannot be wrong, because it is handed one number that never
  changes.
* **HARNESS measures the gap** — belief-at-D+1 vs figure-at-RF, per settlement period. That number does
  not exist anywhere today.

*Inferred, and the reason for §5:* whether the SSP series specifically moves between D+1 and the later
runs — as opposed to the consumption volumes the 60/25/12/3 shares are calibrated to — is a fact about
Elexon that cannot be checked from this sandbox (no network in autonomous runs). It should be measured,
not assumed in either direction.

---

## 5. The cheapest EP7 experiment costs one extra HTTP GET, and is not epoch-gated

Re-fetch a settlement date the rolling cache already holds — say `2025-06-08`, now fourteen months and
three settlement runs old — and diff it against the stored record.

* **If it differs:** the world has a revision the company has never observed, §4's gap is real and
  quantified on the first attempt, and the fix to §2 is a re-fetch window rather than a forward-only one.
* **If it is identical:** the "final at D+1" comment is vindicated against the price series, the
  unreachable merge line can be deleted honestly rather than repaired, and §4 narrows to volumes.

Either outcome is a fact the project does not currently have, it costs one request against a key-free
public endpoint already on the egress allowlist, and **it is a measurement rather than an integration** —
so it does not need the epoch gate to open. It belongs in the background pipeline where the network is,
alongside the refresh job whose own docstring explains why (`WHY IT IS SAFE TO DEPLOY UNVERIFIED`).

This document does not ask for EP7 to be unblocked. §5 is drawable inside the block; §3–§4 are what a
builder should find on the day it is not.

---

## 6. Sequencing, if EP7 is ever pulled forward

1. **Measure the revision** (§5) — one GET, no gate, settles what the rest is worth.
2. **Put the market feed on `WallEnvelope`** (§3) — reuse, already named as owed by the seam it crosses.
3. **Carry the run label and both clocks** across it, so a superseding figure is a new response rather
   than an overwrite, and the D+1-vs-RF gap becomes reportable per coupled pair.
4. **Wire the settlement-run registers** that already exist (§4) — the twelfth module problem: a builder
   reading only the atom title will write a new one on top of three that nothing calls.
5. **Then** widen the catalogue — imbalance volumes, pricing stacks, dynamic BMU, IRIS push (§1). Last,
   because it is the easiest and buys the least.

IRIS in particular should not be pulled forward for its own sake: a real-time push channel is only worth
building once something downstream reacts to a price arriving *late* or *revised*, which is step 3.

---

## 7. What this pass changed

* This document.
* `docs/design/simplifications/EP7_adapter_elexon_insights.yaml` — the atom's own single `evidence`
  pointer repaired (it named `docs/staging/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`,
  which no longer exists; the file is at `docs/design/refs/`), and this document added as its second
  evidence pointer. Instance of the live
  `WORKER_FINDING_EIGHTY_ATOMS_CITE_EVIDENCE_AT_A_PATH_THAT_MOVED_2026-08-13` class.
  No `map_notes` key was added for the pass: the atom's map block declares `notes_rehomed: [name,
  origin_note]`, and `tests/design/test_atom_notes_store.py` requires that declaration to name exactly
  the fields the store file holds, in both directions. Recording the pass as a third note would have
  needed a map edit on a file other lanes are writing, to say something this document already says.
  Same shape as EP10's record.
* One finding staged, not fixed:
  `WORKER_FINDING_THE_ROLLING_ELEXON_CACHE_CAN_NEVER_REFETCH_2026-08-14.md` (LATENT · `W4_the_wall`).

No level moved. Nothing under `company/`, `simulation/`, `sim/` or `saas/` was touched.
