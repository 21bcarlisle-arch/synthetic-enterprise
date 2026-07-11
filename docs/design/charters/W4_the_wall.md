# W4 — The Wall: lane charter

**Dial reached 3 (SPIKE_WEEKEND charter flood, 2026-07-11)** — charter earned per the map's own
rule ("a lane earns its charter when its dial reaches 3+"). This is a DISCOVER+FRAME artefact:
research and framing only. Neither atom in this lane has an active build in flight this pass —
see "Lane roadmap" below for the honest status of each.

## Mission

The SIM/company boundary (`company/interfaces/sim_interface.py`) is not just an internal code
seam — it is this project's own future go-live seam. Architectural Law #2 (the company cannot
see inside the SIM) is already enforced as a *rule*; W4's job is to make the boundary structurally
trustworthy in two different senses at once: (1) that what crosses it is *shaped* like a real
industry integration would be (typed, versioned messages, not ad-hoc dicts) so that going live one
day means swapping sim adapters for real endpoints behind unchanged interfaces, not a rewrite; and
(2) that the boundary is *actually watched* for the right *kind* of violation — data flowing the
wrong direction in time, not just the wrong module doing a literal `import`. This lane's own
`real_world_twin` fields name both: "a real go-live integration seam between a trading system and
a retail billing system" (W4_1) and "a Chinese-wall audit that checks for information leakage, not
just org-chart separation" (W4_2) (`docs/design/maturity_map.yaml`).

## Shared architecture note — this lane sits downstream of W1/D2's spine, and beside interface-steward's mandate

W4 does not own the SIM/company seam's *content* — `interface-steward`
(`.claude/agents/interface-steward.md`) is "the only role permitted to touch both sides of the
seam, and only at the seam itself." W4 owns two orthogonal concerns *about* that seam: its wire
*shape* (W4_1) and the *detection* of violations across it (W4_2). W4_2 in particular is a direct
consequence of the W1 lane's reveal-over-time work (`docs/design/charters/W1_market_weather.md`)
— the incident that opened W4_2 (`docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`)
is the same failure class W1's `PointInTimeView`/`BitemporalEventLog` foundation exists to make
structurally impossible, and this charter's own gate-closure record explicitly says so: "a
structural point-in-time access layer would make many classes of this bug structurally impossible
rather than needing to be statically detected after the fact... the two proposals are
complementary, not competing" (`docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md`).

## Sub-capability tree

- **W4 (this lane, `W4_the_wall`)** — the go-live seam as a whole: shape + policing.
- **W4_1_typed_adapters** — typed, versioned-message SIM/company boundary adapters, forward-
  preference only (CLAUDE.md's "Typed-flow seam preference," 2026-07-08: new crossings from Phase
  2/4 onward should prefer this shape; already-shipped Phase 3 code is not reworked for it).
- **W4_2_verifier_timing_extension** — extending `tools/epistemic_verifier.py`'s detection beyond
  literal `simulation.*` import matching to data-flow/timing violations (the shape of bug the
  hedge-volatility incident actually was).
- Related but out of this lane's scope: `W1_reveal_over_time` (the structural point-in-time
  access layer W4_2's own gate names as the *permanent* fix, sitting in lane W1, not here) and
  `credit_bureau_port.py` (the pre-existing Protocol-shaped port W4_1's sketch cites as an early
  example of the target shape).

## What L2/L3/L4 mean in this lane's terms

**W4_1 — typed adapters (level 2/3, dial 3, idle):**
- L1 (superseded): every SIM/company crossing is a direct Python function call or plain dict —
  correct under the epistemic *rule* (observables only), but not shaped like a real protocol.
- L2 (current): the target shape has a proven, live reference implementation —
  `tools/market_data_port.py::MarketDataPort`, a `runtime_checkable` Protocol whose every method
  takes an explicit `as_of: Optional[date]` parameter — plus a catalogued, current audit of every
  other candidate crossing (`docs/design/WALLED_INTERFACES_SKETCH.md`'s 6-row table: meter reads,
  smart-meter comms, contact-centre messages, credit-bureau checks, funnel-stage transitions,
  market/forward price reads), each classified already-typed vs plain-call against the live code,
  not a stale sketch.
- L3 (target): one real reference-flow conversion lands end to end (the sketch's own candidate:
  meter reads, "smallest conversion delta") — a versioned-message adapter with a schema-version
  field, existing call sites updated to construct/consume the message instead of a raw dict.
- L4 (not targeted by this atom's `level_target`, future): the pattern generalises to the
  remaining candidate flows one at a time, each independently testable/revertable, and the
  informal `sim_interface.py` observable-only contract is either retired into the typed-message
  layer or explicitly kept as the rule the typed layer rides on top of.

**W4_2 — verifier timing extension (level 1/3, dial 3, idle, GATE CLOSED — see roadmap):**
- L1 (current, and — per this atom's own corrected history — the *honest* current level):
  `tools/epistemic_verifier.py` is 202 lines of literal import-statement regex matching
  (`FORBIDDEN_SOURCES = [r"^from sim\.", ...]`); zero data-flow/timing detection exists anywhere
  in the tool or the repository. This atom's own maturity-map entry originally overstated this to
  level 2 with `expert_hour: passed` — corrected down 2026-07-10 after a self-audit found the
  claim false (see roadmap and simplifications register below).
- L2 (target, per this atom's `level_target: 3`, NOW DECLINED — see roadmap): a real, tested,
  automated data-flow/timing detector inside the verifier itself, catching the hedge-volatility
  bug's shape (a company/saas function receiving a full, un-bounded historical dataset with no
  as-of truncation) without false-positiving on the codebase's many legitimate large-dataset call
  sites.
- L3/L4 (not reached, and now not the planned path): broader data-flow coverage beyond the one
  known bug shape; superseded by the closed gate's actual resolution (below), which routes the
  practical burden through two *other* mechanisms instead of building this into the verifier.

## Named best-practice references

**On typed/versioned message contracts at system boundaries (W4_1):**
- **Protocol Buffers / gRPC schema evolution** (https://protobuf.dev/programming-guides/proto3/#updating,
  https://grpc.io/docs/guides/) — the standard real-world pattern for a versioned message contract
  at a service boundary: fields are added/deprecated under explicit compatibility rules, never
  silently reshaped, which is exactly the discipline `docs/design/WALLED_INTERFACES_SKETCH.md`'s
  target shape (`MeterReadMessage {..., schema_version}`) is reaching for.
- **The Anti-Corruption Layer pattern**, Eric Evans, *Domain-Driven Design: Tackling Complexity in
  the Heart of Software* (Addison-Wesley, 2003), Ch. 14 — a translation layer that isolates one
  model (here: the SIM's internal world) from another (the company's decision-making model) so
  neither is corrupted by the other's assumptions; directly names the shape `sim_interface.py` +
  a typed adapter layer are jointly trying to be, not an invented analogy.
- **Consumer-driven contract testing**, e.g. Pact (https://docs.pact.io/) — the practice of the
  consumer (here: company/) codifying the exact shape of message it expects from the provider
  (here: sim/), tested independently of either side's implementation; the natural verification
  companion to W4_1's typed-adapter programme once a reference flow exists to test against (not
  yet built — registered as a gap, not a claim).

**On static detection of data-flow/timing violations (W4_2):**
- **Taint analysis / information-flow control**, the general static-analysis technique of tracking
  whether data from a "tainted" source (here: a future-dated or unbounded historical record) can
  reach a "sensitive sink" (here: a company-layer decision function) without passing through a
  sanitizer (here: an as-of bound) — the correct general name for the class of check Option A of
  the closed gate sketches, and the honest reason it was assessed as non-trivial: general
  data-flow analysis of arbitrary Python is a much larger undertaking than the literal
  import-regex the verifier does today.
- **Semgrep's dataflow/taint-mode rules** (https://semgrep.dev/docs/writing-rules/data-flow/data-flow-overview)
  — a real, existing open-source implementation of exactly this technique (source/sink/sanitizer
  rule shape) against Python and other languages; the concrete tool-shape reference if Option A of
  the closed gate is ever revisited, rather than a from-scratch analyzer.
- **QuantConnect/LEAN's "look-ahead bias" framing and Zipline's event-driven data delivery**
  (already cited in `docs/design/charters/W1_market_weather.md`) — the same underlying
  problem (data from the wrong point in time reaching a decision) from the quant-finance side;
  W4_2 is the *detection* half of the same problem W1 solves *structurally*.

## Lane roadmap

1. **W4_1 — idle, rank block LIFTED 2026-07-11, no longer awaiting external decision:**
   `PRIORITIES.md` (lines ~883-904) originally carried a standing instruction — "Awaiting director
   rank — do not start the first reference-flow conversion without it" — but the director resolved
   this directly 2026-07-11 ("assess versus the goals and progress of the project and use your
   judgement"): the block is lifted, and the reference-flow conversion (L3 above, meter reads) may
   now be picked up whenever the dial-weighted maturity-map self-refill draw next surfaces
   `W4_1_typed_adapters` — no special manual rank needed, same as any other atom. Not started this
   pass; this charter is FRAME-stage registration, not a claim of build progress.
2. **W4_2 — idle, gate CLOSED 2026-07-10, decision made: do NOT build detection into the
   verifier.** `docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` records the
   director's actual ruling: *"Verifier gate: B/C confirmed — register + doc-fix, no build; the
   PreToolUse hook (adoption sprint) is the near-term detector, the as-of snapshot object the
   permanent fix. Close the gate."* Two other real mechanisms now carry this burden instead:
   (a) near-term — `.claude/hooks/block_point_in_time_read.py`, a PreToolUse hook targeting the
   exact known-dangerous call shape; (b) permanent — W1's `PointInTimeView`/`BitemporalEventLog`
   (`docs/design/charters/W1_market_weather.md`), which makes the bug class structurally
   impossible rather than needing to be caught after the fact. `tools/epistemic_verifier.py`
   itself is not modified as a result of this atom, and per this charter's own understanding,
   should not be treated as "still pending a decision" — the decision is made and closed.
   **Note for `maturity_map.yaml`'s own bookkeeping (not changed by this charter, per this DISCOVER
   +FRAME document's scope):** the atom's `simplifications` text and `PRIORITIES.md`'s
   maturity-queue-status entry (line ~575) both still describe this gate as "still-open" — that
   text predates the 2026-07-10 21:51 close and is stale; this charter registers the correction
   for whoever next touches that atom's bookkeeping, without editing it here.
3. **Both atoms:** no further action is planned by this charter itself — it is the DISCOVER+FRAME
   deliverable the map's charter rule requires at dial 3, not a build commitment. The lane's next
   real move for either atom is whatever the dial-weighted self-refill draw surfaces next.

## Simplifications register

- W4_1's reference-flow conversion (meter reads → `MeterReadMessage`) has not been built — the
  sketch, the audit, and this charter are the lane's real output so far, not the adapter itself.
  `docs/design/WALLED_INTERFACES_SKETCH.md` is explicit that this is "not a data-model rewrite,
  not a scale change, not a new epistemic rule" — a transport-shape change to already-correct
  data, deliberately scoped small.
- W4_1's `MarketDataPort` reference implementation is real and already at target shape (typed
  Protocol + explicit `as_of` on every method) but is the *only* crossing at that shape today —
  the other five candidate flows in the sketch's table remain plain calls/dicts, an honest,
  unclosed gap, not an oversight.
- W4_2's own history is itself a registered lesson: this atom's level/`expert_hour` fields were
  wrong for a period (claimed level 2/passed with zero actual detection code), caught by a
  self-audit, corrected to level 1, and resolved by the closed gate to *not* build the missing
  capability into the verifier at all — the gap this atom names (no automated data-flow/timing
  detection in `tools/epistemic_verifier.py`) is real, permanent (by director decision, not
  oversight), and covered instead by the two mechanisms named in the roadmap above, not by this
  tool.
- No consumer-driven contract test (Pact-shaped or otherwise) exists yet for any SIM/company
  crossing — named above as the natural verification companion to W4_1's programme, not built.
- This charter itself makes no code change and does not touch `maturity_map.yaml`, per its own
  DISCOVER+FRAME scope — the staleness noted in the roadmap (PRIORITIES.md/maturity_map.yaml
  text describing W4_2's gate as still-open) is flagged, not fixed, here.
