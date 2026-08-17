# EP6 — protocol typing of the wall: DISCOVER (exit-criterion framing)

**Atom:** `EP6_wall_protocol_typing` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-17 scheduled tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom
is epoch-3 BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13); EPOCH_GATING_AND_
ATOM_AUTHORSHIP Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level: HELD at 0.** No map level move made or recommended by this pass.
**Measured at:** HEAD `31791a01d` (2026-08-17 18:49:49+0100). Live artefact
`docs/reports/run_output_latest.json` (mtime 2026-08-17 18:58, 4,154,361 bytes), parsed in full.
`tools.epistemic_wall.live_crossings()` / `live_indirect_crossings()` and
`python3 -m tools.wall_crossing_dispositions` run directly, nothing mocked. No network. Every claim is
**observed-with-evidence** unless labelled **inferred** (R9).

## 0. This is NOT the first DISCOVER pass on this atom — read before trusting a number here

Two prior passes already did the heavy measurement and their output is authoritative for the numbers they
took: `docs/design/simplifications/EP6_wall_protocol_typing.yaml` (2026-08-13 entry, "FINDING 1" — names
the two-family confusion in this atom's own `name:` field) and
`docs/design/EP6_WALL_CONFORMANCE_CENSUS_DISCOVER.md` (2026-08-15, two passes — the six-channel census).
This document does **not** re-run that census from scratch. It (a) re-verifies the highest-leverage claims
at today's HEAD, (b) reports what changed, and (c) writes the three sections the dispatcher for this draw
asked for that the prior passes did not produce in this form: a **falsifiable indistinguishability test**,
an explicit **SIMPLICITY GUARD reading**, and **named open questions**. Duplicating the census walk would
have cost a second full read of a 4MB artefact and every seam module for no new information — the census
is already exhaustive per-channel and states its own method.

## 1. Re-verification: two numbers moved since 2026-08-15, neither destroys the census's conclusions

**Channel A (direct import edge) is now 5, not 6.** The 2026-08-15 census table listed six rows including
`simulation.run_phase4c_on_phase2b → company.billing.dd_review_runner`. KNIFE3 pass 3 step 32
(`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`, same day as this draw, commit series
ending at `31791a01d`) cut that edge with a new door, `company/interfaces/dd_review.py`. Re-run at HEAD:

```
live_crossings()          -> 5 rows (was 6; dd_review_runner gone)
live_indirect_crossings() -> 2 rows (unchanged)
python3 -m tools.wall_crossing_dispositions
  -> "7 live crossings (5 direct, 2 indirect); 91 ruled (cut 84, owed 7, grandfathered 0)"
```

This matches KNIFE3's own step-32 record exactly (91 ruled, cut 84, owed 7) — the two registers agree.
**This is the expected decay pattern for a census against a tree under active, unrelated construction**
(memory note: a class doc must be re-rendered before its numbers are relied on) — not a defect in either
prior pass, both of which were correct when measured.

**Channel F's denominator moved: 93 top-level keys today, not 92.** Not chased further — identifying the
new key and reclassifying it is a rerun of §6/§7 of the conformance census, out of scope for this pass, and
the census itself already states 91-of-92 was "the width of the channel, not a crossing count" — one more
key does not change that framing.

**Everything else in the 2026-08-15 census (channels B, C, D, E, and the ground-truth-named-field count
on F) was spot-checked, not fully re-walked, and held:** channel D's three log types (`meter_read_log` 1,600
rows, `contact_centre_log` 392, `acquisition_funnel_log` 4) still carry zero `schema_version` and zero
`correlation_id` keys in today's artefact; `_cache_meta` is still absent from the published file. Channel C's
module set (`interface/contracts/{wall_envelope,payment_observable_seam,conversation_seam,
flex_observable_seam}.py`) is unchanged on disk since 2026-08-15.

## 2. Which crossings are already typed, and by which of two unrelated patterns

The atom's own `name:` field points at the wrong ancestor (2026-08-13 finding, still true): it says
`W4_1_typed_adapters` "built the adapter PATTERN" that EP6 would build a protocol layer on top of. Two
**disjoint** patterns exist on disk, and only one has the property this atom is named for:

| Pattern | Where | Crossings using it | Has request/response separated in time? |
|---|---|---|---|
| **Envelope** (`WallRequest[P]`/`WallResponse[R]`, `interface/contracts/`) | `interface/contracts/{payment,conversation,flex}_observable_seam.py`, built under atom **W4_4**, not W4_1 | payment, conversation, flex (3) | **Yes, by construction** — `correlation_id` is the only link, `as_of`/`emitted_at`/`observed_at`/`valid_time` are kept apart, `schema_version: int` has no default, `__post_init__` refuses a malformed pairing |
| **Same-step typed port** (`runtime_checkable Protocol` + frozen dataclass, `tools/*_port.py`) | `market_data_port`, `credit_bureau_port`, `meter_read_port`, `acquisition_funnel_port`, `contact_centre_port`, built under atom **W4_1** (SATURATED) | market data, credit check, meter reads, acquisition funnel, contact centre (5) | **No** — every Protocol method returns the answer in the same call frame; `schema_version` exists on the dataclass but, per §1, is never populated on the wire |
| **Direct import** | `simulation.run_phase2b`/`simulation.customer_events` → 5 `company`/`saas` modules (channel A), + 2 via `background.live_payment_triad` (channel B) | policy decisions, cost-to-serve-adjacent reads, churn model, home-move win rate (7) | No — no adapter at all, this is KNIFE3's subject, not EP6's |
| **Structural (duck-typed) Protocol** | `company/billing/monthly_bill_assembly.py`'s own Protocol, satisfied by the world's `MeterReadEvent` with no import either way | at least 1 confirmed, no full count taken by either prior pass | Partially — swappable by construction, but **no field exists to carry a version**, so it cannot represent a shape change at all, sync or async |
| **Published report** | `run_output_latest.json`, 93 top-level keys, read by 11 `company`/`saas` modules | not a "crossing" in the request/response sense — a batch report | No, and per §5 below it should not try to be |

**So "which crossings already have a typed adapter (W4_1) and which are direct calls" has a three-way, not
two-way, answer.** W4_1's adapters (Family/pattern 2) are typed **values**, not typed **messages with
async separation** — they satisfy "swap the implementation behind an unchanged interface" (the go-live
promise) but not "a mock counterparty and a real one are indistinguishable" under the specific stress the
origin note names (C-S1/C-S2/C-S3: late, duplicated, or asynchronous delivery). Pattern 1 (the envelope)
is the one that actually has the property EP6 is named for, and it was built by a different atom, for a
narrower set of crossings, without EP6 ever being opened.

## 3. What "request/response separated in time" would have to mean per shape found

Read against real UK-market physics per crossing, not assumed:

- **Flex, payment, conversation (envelope, already built):** genuinely asynchronous in the real world a
  real supplier would face — a BOA is issued in-day and its Elexon settlement line lands days later; a
  Bacs payment can return via ARUDD days after presentment; a customer conversation and its downstream
  effect on churn belief are not resolved in the same tick. The envelope's separation is **real**, not
  cosmetic, and this is exactly the C-S3 property the origin note calls "the thing most likely to be
  quietly dropped."
- **Meter reads, credit checks, market data, acquisition-funnel stages, contact-centre events (5 same-step
  ports):** mixed. Market data (`MarketDataPort`) is legitimately near-synchronous in the real world too —
  a live price feed answers "now" and the `as_of` parameter already carries the point-in-time discipline
  that matters here; forcing it into a WallRequest/WallResponse pair would add an idle correlation_id with
  nothing asynchronous behind it. Meter reads and credit checks are the opposite: a real D0010 actual read
  can arrive days after the estimated read it supersedes (the module's own docstring already models an
  `"estimated"` vs `"actual"` status for exactly this reason), and a real bureau check has a network RTT a
  synchronous Python return cannot represent honestly. **The asynchrony these two need is real; the port
  shape they currently have cannot express it** (see §4, indistinguishability test, channel D fails there).
- **Direct-import crossings (channel A/B, 7 remaining):** this is KNIFE3's subject — whether the crossing
  should exist at all — not EP6's. Typing an edge that a different, actively-running programme may cut
  next week is wasted protocol design; see §5.
- **Structural Protocol (channel E):** cosmetic today (in-process, same tick, no version negotiation
  needed because the shape has never changed) but would become real the moment either side's field set
  diverges — and there is currently no seam artefact that would even notice a divergence, because nothing
  is versioned.
- **Published report (channel F):** not a request/response relationship at all — a report is produced,
  once, from state that already exists. Forcing "separation in time" onto it is a category error; see §5.

## 4. The indistinguishability test, stated as a falsifiable exit criterion

The atom's own words: "a mock counterparty and a real one are indistinguishable to the company." Read
literally, that is a property of the **company-side code**, not of the message shape alone — it must hold
even under the failure modes a real endpoint has and an in-process mock does not. Stated per channel,
because §2's census shows there is no single mechanism to test:

> **For a crossing to pass, swapping its SIM-side adapter for a different implementation that answers the
> same envelope contract — including one that sometimes returns `TIMEOUT`, `NOT_KNOWABLE_YET`, or a
> duplicate response for the same `correlation_id` — must require ZERO changes to company-side code, and
> the company-side code must not contain a branch, `isinstance` check, or import that could only succeed
> against one specific adapter.**

Applied:

- **Channel C (envelope) — PASSES, mechanically checkable today.** `tests/architecture/
  test_epistemic_wall_ratchet.py` already proves company code imports no SIM internals for these three
  seams; `WallResponse.__post_init__` proves a malformed pairing cannot be constructed by any adapter,
  real or mock; and the async wiring at `simulation/conversation_response.py::respond_over_wall` already
  demonstrates same-step resolution is refused by construction. **The one un-tested half of this
  criterion**: no test in the repo actually swaps the flex/payment/conversation SIM adapters for a
  double that returns `TIMEOUT`/`NOT_KNOWABLE_YET`/a duplicate and asserts the company side degrades
  correctly rather than crashing — R15 would call an envelope that has never been forced through its own
  non-OK statuses an unproven control on this specific property.
- **Channel D (same-step ports) — FAILS today, by construction, not by omission.** A `Protocol` method
  signature `get_meter_reads(...) -> list[MeterReadMessage]` has no representable way to say "not
  available yet" other than blocking or raising — there is no `TIMEOUT`/`NOT_KNOWABLE_YET` return path at
  all. A real D0010 feed or bureau API that answers late or out of order cannot be swapped in behind this
  Protocol without either (a) the company blocking synchronously on a real network call inside what today
  is a same-tick simulation loop, or (b) the Protocol changing shape — both of which are visible,
  behaviour-changing swaps, the opposite of indistinguishable.
- **Channel A/B (direct import) — FAILS trivially.** There is no adapter to swap; going live means editing
  an import statement in `simulation/run_phase2b.py` itself. This is definitionally distinguishable and is
  KNIFE3's problem to remove, not EP6's to type.
- **Channel E (structural) — PASSES for a frozen shape, FAILS under evolution.** Any object with the right
  attribute names satisfies the Protocol, mock or real, so today's swap is invisible. But there is no
  version field anywhere in the pattern, so a real counterparty that adds/renames a field would either
  silently satisfy the Protocol with wrong data or silently fail to satisfy it with no diagnostic — the
  test degrades from "indistinguishable" to "untestable" the moment the two sides' shapes diverge, which
  is the scenario going-live is supposed to survive.
- **Channel F (report) — the test does not apply, and forcing it to would be wrong.** The published
  artefact is read by the harness specifically **because** it carries both the company's belief and the
  SIM's ground truth in the same row (e.g. `customer_events`' `company_churn_estimate` beside
  `realized_churn_probability`, per the 2026-08-15 second pass) — that is the coupled-triad measurement
  instrument, and a real counterparty must never see it. "Indistinguishable to the company" is the wrong
  goal for a wire whose entire value is that the *harness* can distinguish the two sides.

## 5. The SIMPLICITY GUARD reading

CLAUDE.md's standing lens: no adapters-for-future-adapters, no protocol cathedral — build only what a real
next touch needs. Applied to the six channels found:

- **Do not rebuild the envelope.** Channel C already has the exact property EP6 exists to establish, proven
  on three real crossings. EP6 opening with "design a typed message protocol" would either reinvent
  `wall_envelope.py` under a new name (pure waste) or produce a second, competing envelope shape (a
  worse outcome than one gap, per the "two knobs that only appear as a difference are one knob" class).
  **EP6's honest first move is conformance — migrate more crossings onto the existing envelope — not
  design.** Both prior DISCOVER passes reached this conclusion independently; this pass concurs after
  re-verification and adds the falsifiable form in §4.
- **Do not envelope channel F.** Wrapping 93 report keys in `WallRequest`/`WallResponse` is the cathedral
  the origin note explicitly forbids ("no protocol cathedral") applied to a subject — a batch report — that
  was never a counterparty relationship. The defensible target there is provenance (which keys are
  world-origin), not messages.
- **Do not envelope channel E yet.** It is the cheapest possible pattern (zero seam code) and it is working
  for every crossing that currently uses it. The SIMPLICITY GUARD says leave it structural until a real
  shape divergence forces a version, not pre-emptively wrap it because §4 shows it fails under evolution —
  building for a failure mode that has not occurred yet is exactly "adapters for future adapters."
- **Do not scope channel A/B into EP6 at all while KNIFE3 is live.** KNIFE3 is actively cutting these edges
  (91 ruled, 7 owed at this HEAD) under a different design vocabulary (`A_composition_lift`, doors, module
  moves) whose goal is removing the crossing, not typing it. An EP6 that spent BUILD effort putting a
  protocol around an edge KNIFE3 is about to delete would be waste in the other direction — protocol
  machinery around something that should not exist. The two atoms' scopes are adjacent, not overlapping,
  and nothing in either atom's record currently says so in one place; this sentence is that place.
- **Channel D is the one place the guard does NOT counsel restraint**, because §4 shows it is not a
  hypothetical gap — it is the one channel EP7 (Elexon), EP8 (DCC/DUIS), EP9 (n3rgy metering), and the
  W5_1 banking-rails item all *name in their own real-world analogues* as genuinely asynchronous (a DCC
  Service Request/Response pair, a Bacs ARUDD return days later). Building a protocol layer there is not
  cathedral-building; it is building the one thing nine dependent atoms actually need before they can be
  built honestly.

## 6. Open questions before BUILD, each named with what would resolve it

1. **Is channel D's async gap (§4) actually load-bearing for EP7-EP15, or can those nine atoms be built
   against same-step ports with the asynchrony added later per-adapter?** Resolved by: reading each of
   EP7/EP8/EP9/EP11's own `name:`/`origin_note` fields against whether their real-world analogue's
   asynchrony is structural to the fidelity claim (e.g. "the webhook arrived four days later" — the
   2026-08-13 finding's own phrase) or incidental. Not resolved here — this pass names the question, the
   2026-08-13 finding raised it but did not check it atom-by-atom.
2. **Should EP6's deliverable be (a) a per-channel conformance census with a shrink-only allowlist (the
   2026-08-15 second pass's recommendation), (b) migrating the 5 channel-D ports onto the envelope, or
   (c) both, staged?** Resolved by: a director/curriculum ruling when Epoch 3 opens (R13 — this is the
   agent's proposal to make, not its call to make unilaterally); this pass's own view, stated as a
   recommendation per NEVER_ASK_WITHOUT_RECOMMENDING: (b) is the higher-leverage BUILD move because it is
   the one gap §4 shows is real and load-bearing for nine dependent atoms, with (a) as the accompanying
   control so the migration cannot silently regress.
3. **What should happen to the 7 channel-A/B edges KNIFE3 still owns while EP6 is parked?** Resolved by:
   nothing EP6-side — re-read `tools.wall_crossing_dispositions`'s live count at BUILD time and exclude
   any edge still `owed` there from EP6's scope, per §5. This is a standing exclusion rule, not a one-time
   check, since the count moves under KNIFE3's own active work (it moved during this very draw).
4. **Is the "two wires wearing one name" split for channel F (counterparty wire vs. harness wire, proposed
   by the 2026-08-15 second pass) ratified anywhere, or still a DISCOVER hypothesis?** Checked this pass:
   grepping the whole tree for "counterparty wire" / "harness wire" returns zero hits outside that one
   document. **Still an unratified hypothesis** — no FRAME or BUILD step has acted on it. Resolved by: a
   future FRAME pass either adopting it into a design doc or replacing it; it should not be assumed settled
   by the next reader just because it reads as a conclusion.
5. **Channel D's `to_log_entry(include_schema_version=False)` default (§1) — is silently omitting the
   version field from every production write acceptable indefinitely, or must it flip before the first
   schema bump?** Resolved by: whoever builds the first v2.0 message shape in this family — at that point
   the fail-open default (§1's `entry.get("schema_version", SCHEMA_VERSION)`, already flagged by the
   2026-08-13 finding) silently relabels every historical v1.0 row as v2.0, which is the concrete trigger
   condition, not a hypothetical one worth fixing pre-emptively per §5's guard.
6. **What is the new 93rd top-level published key (§1), and does it change channel F's count of seven
   ground-truth-named fields?** Not resolved here — flagged so the next channel-F pass diffs the two
   artefacts rather than assuming the count is unchanged.

## 7. Record

Level held at 0 (no move made or recommended). This document plus one `simplifications` entry recorded via
`tools.simplifications_store.append_for_atom` (the store's own writer, not a hand edit) are the whole output
of this pass. No new WORKER_FINDING filed (SELF_INTERRUPT_DISCIPLINE): §1's two drift observations are
re-measurements of already-tracked numbers, not new defects; §4-§6 are framing/synthesis, not findings
against a control.
