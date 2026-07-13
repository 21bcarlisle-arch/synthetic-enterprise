# GO-LIVE SEAM AND INTERNAL SEAMS DESIGN — ARCH1 (Epoch 3)

**Status:** DISCOVER/FRAME (Lane-3, doc-only). **NO code changed by this doc; no tests run.** Epoch-3 BUILD stays gated until Epoch-2's exit test passes — everything below is thinking, which is never gated (EPOCH_GATING_AND_ATOM_AUTHORSHIP.md).
**Atom:** `ARCH1_internal_seams` (Epoch 3, `docs/design/maturity_map.yaml`), level_target 2.
**Source requirements:** `docs/staging/done/WORKTREE_ISOLATION_AND_SEAMS.md` Half 2 (director-decided QUEUE); the sim/company epistemic wall (`company/interfaces/sim_interface.py`, `tools/epistemic_verifier.py`); CLAUDE.md scale constraints C-S1..C-S5, typed-flow-seam preference, portability constraints.
**Author:** discovery fork, 2026-07-13.
**What was out of scope, and why** (G3 Finding-2 discipline): this doc does NOT design the Epoch-4 fitness function, does NOT touch the sim-side of any wall crossing, and does NOT specify the go-live *deployment/network* topology (containers, brokers, real endpoints) — CLAUDE.md bars horizontal-scale infrastructure in current epochs; this is a *logic-boundary* design that a later infra epoch slots real transports behind.

---

## Framing: one doctrine, applied twice

The director's framing (WORKTREE_ISOLATION_AND_SEAMS.md Half 2): **the architecture work and the velocity work are the same work.** This doc treats the go-live seam and the internal seams as **the same mechanism at two radii**:

- The **outer wall** (sim ↔ company) already exists and is enforced by hooks + tests, not a network: `company/interfaces/` is the *only* sanctioned crossing, and `tools/epistemic_verifier.py` fails any `company/**` or `saas/**` file that imports sim internals directly. The wall IS the future go-live seam — at go-live you swap the sim-side adapter for a real endpoint behind an unchanged company-side interface.
- The **inner walls** (billing ↔ pricing ↔ settlement ↔ collections) do not exist yet. ARCH1 builds them with the *identical* enforcement pattern — typed interface + verifier check + hooks — so two agents editing two domains can never collide *in meaning*, and so the monolith stays modular by enforced discipline rather than by splitting into microservices.

The load-bearing claim, recorded: a typed seam is simultaneously (a) the go-live boundary, (b) the concurrent-build-safety boundary, and (c) the modularity-discipline mechanism. Build it once; it pays three bills.

---

## Part 1 — The go-live seam as a real SLA boundary

### 1.1 What the wall must carry to become a real endpoint boundary

Today the wall is a synchronous in-process Python call (`SimInterface.get_forward_price(...)` returns a `float` immediately). A real endpoint boundary differs in five ways that must be *representable in the contract now* (cheap today, brutal to retrofit — CLAUDE.md scale-readiness rationale), even though the transport stays in-process until a later infra epoch:

| Property | In-process today | Real endpoint at go-live | C-S constraint |
|---|---|---|---|
| **Typing** | positional args, `dict[str, Any]` returns | versioned typed message envelope, schema-checked both sides | typed-flow-seam preference |
| **Time** | request→response in one call, same step | request and response are **separate events in time** | **C-S3** |
| **Arrival** | one call, complete, ordered | events arrive one-at-a-time, late, out of order | **C-S1** |
| **Repeat** | called once | may be delivered twice; must be harmless; replay reproduces state | **C-S2** |
| **Failure** | exception propagates | explicit timeout / error / partial-result semantics as first-class message outcomes | C-S3 |

**The design decision (and it is the hardest one in Part 1):** do we make the *current* in-process seam synchronous-looking (keep `float` returns) and only *describe* async, or do we make the contract async-shaped now and resolve synchronously under the hood? **Resolution: async-shaped contract, synchronous resolver adapter under it, from day one.** Rationale: C-S3 says request/response are separate events "never same-step-resolution", and A3_approval_interface already found its own "schema cannot represent pending latency" defect — CLAUDE.md states explicitly these are *the same law, build one mechanism*. If we keep the synchronous `float` shape now, every call site bakes in the assumption that the answer is available instantly, and retrofitting latency later means touching every call site — the exact retrofit the scale addendum exists to prevent. So the *contract type* is async (a request yields a correlation id; a response arrives as a later event carrying that id), and the current transport is a trivial in-process resolver that happens to answer immediately. Call sites are written against the async contract; the wall can later become a real latency-bearing endpoint with zero call-site change.

### 1.2 The typed message envelope (shared shape for every crossing)

Every crossing — outer wall and inner seam alike — carries the same envelope; only the payload type differs. Sketch (a `@dataclass(frozen=True)`, mirroring `BitemporalRecord`'s frozen+copy-on-read discipline):

```
WallRequest[P]:
  correlation_id: str        # idempotency key + response-matching key (C-S2)
  request_type: str          # e.g. "forward_price.v1"
  schema_version: int        # explicit version; both sides assert compatibility
  as_of: datetime            # point-in-time decision clock (blindfold, R11/R14)
  emitted_at: datetime       # transaction_time — when the request was raised
  payload: P                 # typed request body

WallResponse[R]:
  correlation_id: str        # matches the request (C-S1 out-of-order tolerant)
  status: OK | TIMEOUT | ERROR | NOT_KNOWABLE_YET
  schema_version: int
  observed_at: datetime      # transaction_time of the answer
  valid_time: date | None    # what period the answer is ABOUT (bitemporal)
  payload: R | None          # None unless status == OK
  error: ErrorDetail | None
```

Key points:
- **`correlation_id` is the idempotency key (C-S2).** A resolver that has already answered a correlation id returns the *same* response, never recomputes with fresh state — this is what makes "delivered twice is harmless" true by construction. Replaying a recorded request log reproduces identical responses.
- **`NOT_KNOWABLE_YET` is a first-class status, not an exception.** This is the honest answer the bitemporal log already gives (`as_known_at()` returns `None`, "not a KeyError, not a silent 0") lifted into the wire contract. A real supplier's meter-read endpoint returns "no read yet", not zero.
- **`valid_time` vs `observed_at` are separate** — the bitemporal split (`company/interfaces/bitemporal_event_log.py`) is already the right model; the envelope just surfaces both axes so a restatement (a later settlement run) is a new response with a later `observed_at` for the same `valid_time`, never a mutation.

### 1.3 The four key crossings — typed contract shapes

Each is a `runtime_checkable Protocol` (the existing port pattern: `tools/market_data_port.py`, `meter_read_port.py`, `contact_centre_port.py`, `acquisition_funnel_port.py` — "future adapters slot in with zero company-layer changes"). Each Protocol is re-expressed in the async envelope of §1.2. The four are chosen because they are the crossings that become *real external endpoints* at go-live:

1. **Market data** (`forward_price`, `spot`, `curve`) — request `{fuel, delivery_date, as_of, term_months}` → response `{price_gbp_per_mwh, valid_time}`. Already the most mature crossing (`MarketDataPort`, `LiveSimInterface.get_forward_price` reads only public Elexon/NBP data). Go-live swap: sim price cache → real market-data vendor feed. **Blindfold-critical:** `as_of` on the request is load-bearing; the endpoint must never answer with data whose `observed_at > as_of`.
2. **Meter reads / settlement consumption** — request `{mpan, period, as_of}` → response `{consumption_kwh, settlement_run, valid_time}` with `status=NOT_KNOWABLE_YET` before the first Elexon run. This crossing is *inherently bitemporal* (Initial→II→SF restatements) — its response carries `settlement_run` and a `superseded_by_run` hint exactly like `BitemporalRecord`. Currently a stub (`get_settlement_data` returns zeros/`_stub:True`); go-live swap: sim consumption → real DNO/Elexon settlement feed.
3. **Settlement / imbalance** (company owes/owed at the BSC) — request `{settlement_date, bsc_party, as_of}` → response `{imbalance_volume_mwh, imbalance_price, cashflow_gbp, run}`. Backed by `company/market/settlement_reconciler.py`, `bsc_settlement_run_register.py`. Go-live swap: sim settlement engine → Elexon BSCCo settlement reports.
4. **Payments / collections banking** — request `{account_id, amount, mandate_ref, as_of}` → response `{payment_status, cleared_at, failure_reason}`. Async by nature (a Direct Debit clears days after submission — a textbook C-S3 request/response-separated-in-time case). Backed by `company/billing/dd_mandate_register.py`, `collections.py`. Go-live swap: sim payment resolver → real BACS/Open-Banking rail.

**Error/timeout semantics (uniform across all four):** `TIMEOUT` and `ERROR` are response *statuses*, and the company-side contract specifies the *obligation on receipt* — e.g. a market-data `TIMEOUT` means "fall back to last-known `as_known_at` price and flag stale", never "assume zero". This obligation lives on the *company* side of the seam (its own reading of a degraded feed), preserving the regulation-commons/independent-implementation doctrine: the endpoint reports the failure; the company decides what to do about it, and can decide *wrongly* (a real supplier mishandling a feed outage stays structurally possible).

---

## Part 2 — Internal seams (ARCH1)

### 2.1 Which module boundaries become seams

Four domains, drawn to match the director's naming and the real coupling observed in-repo (`grep` of cross-package imports, 2026-07-13):

- **PRICING** — `company/pricing/**` (tariff_engine, renewal_pricing_engine, ofgem_price_cap, cost_to_serve, price_elasticity…). *Produces:* rate cards / unit rates. *Must not:* reach into billing invoice internals or collections ledgers.
- **BILLING** — `company/billing/**` (invoice, consumption, annual_statement, contract, back_billing…). *Produces:* bills/invoices from a rate card + consumption. *Consumes:* pricing rate cards, settlement consumption. Today `from company.billing.invoice import ...` is the single most common cross-module import (5 hits) — invoice is already a de-facto hub; a seam formalises that.
- **SETTLEMENT** — `company/market/settlement_reconciler.py`, `bsc_settlement_run_register.py`, `company/regulatory/settlement_reconciliation.py`. *Produces:* settled volumes/imbalance cashflows (bitemporal, restated). *Consumes:* meter/consumption events.
- **COLLECTIONS** — `company/billing/collections.py`, `company/finance/debt_collection.py`, breathing_space/capacity_to_pay/dd_* registers. *Produces:* dunning actions, payment-arrangement state. *Consumes:* billing (what's owed), payments (what cleared).

**The natural dependency DAG** (data flows one way; this is what the seam makes explicit and enforceable):

```
  meter reads ─▶ SETTLEMENT ─▶ BILLING ◀─ PRICING
                                  │
                                  ▼
                             COLLECTIONS ─▶ payments
```

Each arrow becomes a **typed seam contract** (a Protocol + message type in `company/interfaces/`), not a direct import. A domain may only reach a peer through its seam interface; peer *internals* (`company/billing/invoice.py`'s functions, DB schema, `DEFAULT_DB_PATH`) become private to the domain.

### 2.2 What each contract carries

Each contract is expressed in the §1.2 envelope so the inner seams and the outer wall are *literally the same shape* (one mechanism, two radii):

- **PRICING → BILLING** — `RateCard.v1`: `{tariff_id, unit_rate_gbp_per_mwh, standing_charge_gbp_per_day, price_cap_ref, effective_from, effective_to}`. Carries `effective_from/to` because law is time-indexed (`domain_invariants.py`) and a bill must apply the rate card valid *at the consumption date*, not "now".
- **SETTLEMENT → BILLING** — `SettledConsumption.v1`: `{mpan, period, consumption_kwh, settlement_run, valid_time, observed_at, superseded_by_run}`. Bitemporal by construction — a restated settlement is a new message, and billing must be able to re-bill on restatement (back-billing) without mutating the prior bill.
- **BILLING → COLLECTIONS** — `AmountDue.v1`: `{account_id, invoice_id, amount_gbp, due_date, basis}` — **`basis` (settled/billed/banked) is mandatory (R14: no financial figure without its clock).** The seam contract *encodes R14 structurally* — a message lacking `basis` fails schema validation, which is stronger than the current `_check_basis_labels_present` page-gate.
- **COLLECTIONS → PAYMENTS (wall)** — `PaymentInstruction.v1` (see §1.3 #4).

### 2.3 How enforcement works — the epistemic-verifier pattern, pointed inward

The outer wall is enforced by `tools/epistemic_verifier.py`: a git-diff scan that FAILs any `company/**`/`saas/**` file importing forbidden sources, with `company/interfaces/` as the sole EXEMPT crossing. ARCH1 adds an **internal-seam verifier** built on the identical skeleton (`_get_diff_files` → `_scan_file` regex → PASS/FAIL report), so it plugs into the same phase-close and pre-commit hook slot the epistemic verifier already occupies.

Enforcement rules (all mechanised — MAKE_IT_STICK: "convert policy to mechanism, or accept it will evaporate"):

1. **Cross-domain-import ban.** A file in `company/pricing/**` may not `import company.billing.*` (and the other cross pairs) *except* the domain's public seam module. Concretely: each domain gets a declared **public surface** (e.g. `company/billing/__init__.py` re-exports only the seam contract types); a cross-domain import of anything *below* that surface is a violation. This is the direct analogue of "`company/interfaces/` is the only sanctioned crossing." Implemented as a regex/AST scan of the diff — same shape as `_scan_file`, new `FORBIDDEN_CROSS_DOMAIN` table keyed by (importer-domain, imported-domain).
2. **Seam-message schema-version check.** Any change to a `*.v1` contract dataclass without bumping `schema_version` (or adding a `.v2`) fails — both sides must agree on version (belt-and-braces for the concurrent-build case where two forks touch a shared contract).
3. **R14 basis-label structural gate** — a financial-payload contract type lacking a `basis` field fails at definition time (a test over the contract registry), not just at page render.
4. **Path-scoped rule reminders** — mirror `.claude/rules/epistemic-wall-company.md`: add per-domain `.claude/rules/seam-*.md` that fire when editing `company/billing/**` etc., reminding "you are inside the BILLING domain; reach peers only through their seam."

**Enforcement is hooks + tests, not a network** — exactly the wall's proven model. No message bus, no RPC, no serialization at runtime in the current epoch (SIMPLICITY GUARD: "no repository-pattern-over-a-JSON-file cathedrals"). The envelope is a frozen dataclass passed in-process; the *discipline* is what the verifier enforces. The transport can later become real without changing the contract or the call sites.

### 2.4 Why this is BOTH go-live architecture AND concurrent-build safety

Worktrees (H10) solve file-system collisions: two agents in two trees never overwrite each other's bytes. They do **not** solve logical collision — two agents both reaching into `hedged_settlement.py`, or one editing `billing` while another edits `pricing` *assuming billing's old signature*, collide **in meaning at the merge** (WORKTREE_ISOLATION_AND_SEAMS.md Half 2). A typed seam removes that class:

- If PRICING and BILLING communicate *only* through `RateCard.v1`, an agent building PRICING and an agent building BILLING share exactly one artefact — the contract — and it is versioned. Neither can silently change what the other depends on; a contract change is a visible, schema-versioned, verifier-gated event, not a hidden signature drift. **Two agents cannot collide in meaning if the seam is typed** — this is the whole velocity argument, and it is why ARCH1 caps throughput *now*, not "later": until the seams exist, `file_scope`-disjoint is the *only* safe concurrency, and domains that share meaning aren't truly disjoint even in separate files.
- The same typed contract is the go-live boundary: at go-live, SETTLEMENT's real feed swaps in behind `SettledConsumption.v1` with zero change to BILLING — identical to how the outer wall will swap the sim adapter for a real endpoint. One artefact, three payoffs (§Framing).

---

## Part 3 — Sequencing

### 3.1 DISCOVER/FRAME-able NOW (this epoch, doc-only, no gate)

- This doc (the contract shapes, the domain DAG, the enforcement design). ✔ (landed here)
- **Coupling audit** (extend §2.1): a full read-only map of every current cross-domain import among billing/pricing/settlement/collections, so the BUILD step knows exactly which call sites move to a seam. Partially done here (grep); a complete inventory is DISCOVER work and un-gated.
- **Contract-registry FRAME:** the exact field lists and `schema_version` policy for the four inner contracts + four wall contracts — refine against `domain_invariants.py`'s `effective_from/to` and R14 basis vocabulary.
- **Verifier FRAME:** design the `FORBIDDEN_CROSS_DOMAIN` table and the per-domain public-surface declaration format (doc-only; the code is BUILD).

### 3.2 Needs Epoch-2's exit test first (BUILD-gated)

- Writing ANY of `company/interfaces/*_seam.py`, the internal-seam verifier code, the `.claude/rules/seam-*.md`, or refactoring domain call sites onto seams. All are BUILD; all wait for the epoch gate. (This doc writes none of it.)
- Rationale for the gate order: the async-envelope decision (§1.1) shares a mechanism with A3_approval_interface and the C-S3 wall contracts — those should settle (or co-build) so ARCH1 doesn't build a second, divergent envelope. Two-way-door filter: don't build the seam envelope on top of an unresolved async-contract question.

### 3.3 Ordered BUILD task list (for when Epoch-3 opens)

1. **Define the envelope** — `WallRequest/WallResponse` frozen dataclasses in `company/interfaces/` (async-shaped, §1.2), with the in-process synchronous resolver adapter. Idempotency by `correlation_id`. Tests: deliver-twice-is-harmless, replay-reproduces-state (C-S2), out-of-order tolerated (C-S1).
2. **Formalise the outer-wall crossings** onto the envelope — re-express the four §1.3 Protocols (market data, meter reads, settlement, payments) in `WallRequest/Response`. Keep existing `LiveSimInterface`/port adapters working behind them (remediation-on-touch, not a speculative rewrite of shipped Phase-3 code).
3. **Declare domain public surfaces** — pin each domain's seam-only export set (billing/pricing/settlement/collections `__init__` or an explicit `*_seam.py`).
4. **Define the four inner contracts** — `RateCard.v1`, `SettledConsumption.v1`, `AmountDue.v1`, `PaymentInstruction.v1` (§2.2), each in the envelope, `basis` mandatory where financial (R14).
5. **Build the internal-seam verifier** — clone `epistemic_verifier.py` skeleton; `FORBIDDEN_CROSS_DOMAIN` table; schema-version-bump check; R14 basis structural gate. Wire into the phase-close hook slot beside the epistemic verifier.
6. **Add path-scoped `.claude/rules/seam-*.md`** per domain.
7. **Refactor the highest-traffic real seam first** — PRICING→BILLING via `RateCard.v1` (invoice is already the de-facto hub; biggest safety win, proves the pattern on real coupling). Then SETTLEMENT→BILLING, BILLING→COLLECTIONS, COLLECTIONS→PAYMENTS.
8. **Prove the velocity claim** — two forks build two *meaning-adjacent* domains concurrently in worktrees (H10) with only the versioned contract shared; show no merge-time meaning collision. This is ARCH1's DoD and the concrete link to H10.

### 3.4 Open questions (for Epoch-3 open)

1. **Biggest open question — async contract vs. current synchronous call sites.** §1.1 resolves the *contract type* to async, but the migration cost is real: every existing `get_forward_price()`-style call site currently expects an immediate return. Do we (a) migrate call sites onto the async contract incrementally (remediation-on-touch, slow but safe), or (b) provide a thin synchronous convenience wrapper over the async resolver so shipped code keeps compiling while new code goes async? Leaning (b) — it honours the scale addendum's SIMPLICITY GUARD and the "don't retrofit shipped code speculatively" rule — but it risks the wrapper becoming the path of least resistance and the async shape never actually exercised. **Decide by measuring:** if after one epoch no crossing exercises real latency, the async shape bought nothing measurable and should be reconsidered (the CLAUDE.md "revert a tier assignment if the premium buys nothing" discipline, applied to architecture).
2. **Domain boundary of `finance`/`risk`/`trading`.** Part 2 draws four domains (billing/pricing/settlement/collections) per the director's naming. But `company/finance/**` (double_entry, company_pl) and `company/trading/**` (forward_book, hedge_decision) also cross-couple. Are they additional seamed domains, or do they sit *above* the four as consumers? FRAME before BUILD; do not over-seam (SIMPLICITY GUARD).
3. **Where does the seam contract registry live** so both the verifier and both sides can import it without creating a new cross-domain dependency? Candidate: `company/interfaces/seam_contracts.py` (already the EXEMPT, sanctioned location) — verify it does not itself become a god-module.
4. **Interaction with H10 merge model** — the internal-seam verifier must run in the *scoped* per-worktree suite (so a fork catches its own violation before merge), not only at integration. Confirm the scoped-test mapping (H10 design §A) routes seam-verifier runs to the touching worktree.

---

## Appendix — grounding evidence (direct repo read, 2026-07-13)

- Outer wall enforcement: `tools/epistemic_verifier.py` — git-diff scan, `EXEMPT_PATHS` includes `company/interfaces/`, FORBIDDEN_SOURCES regex on `sim`/`simulation` imports, PASS/FAIL report. The internal verifier reuses this exact skeleton.
- Seam location: `company/interfaces/{sim_interface,bitemporal_event_log,point_in_time_view}.py`. `bitemporal_event_log.py` supplies the append-only/valid_time/transaction_time/`as_known_at`→None model the envelope lifts to the wire.
- Port pattern: `tools/{market_data,meter_read,contact_centre,acquisition_funnel}_port.py` — `@runtime_checkable Protocol`, adapter-slots-in-with-zero-company-change. The four §1.3 crossings extend these.
- Real coupling: cross-package import grep shows `company.billing.invoice` as the dominant hub (5 hits), plus pricing/risk/finance cross-imports — the concrete call sites §3.3 step 7 refactors first.
- Domain modules confirmed present: pricing (`tariff_engine`…), billing (`invoice`, `collections.py`…), settlement (`market/settlement_reconciler.py`, `regulatory/settlement_reconciliation.py`), collections (`billing/collections.py`, `finance/debt_collection.py`).
