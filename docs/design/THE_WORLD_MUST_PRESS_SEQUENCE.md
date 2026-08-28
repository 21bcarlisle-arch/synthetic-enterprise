# The delivery seat's sequencing of P1–P10, with the invalidation relationship stated

**Source:** `docs/staging/DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md`, WORK THIS
CREATES item 2 — *"P1–P10 minted into their lanes and epochs, sequenced by the delivery seat
with the invalidation relationship stated."* The guidance is explicit that the inventory is
**not** a priority order and that sequencing is this seat's. This is that sequence and the
reasoning behind it.

**Date:** 2026-08-28. **Author:** delivery seat. **Decided, not proposed** — recorded here so
the director reviews a decision rather than answers a question.

---

## The finding that changed the shape of the answer

The obvious reading of "mint P1–P10 as atoms" is that these are ten new pieces of work. **They
are not. Most of them were already on the map, parked.**

| Problem | Atom | Where it was |
|---|---|---|
| P1 no competitor | `B10_competitor_switching_response` | **idle, `depends_on: []`** — nothing blocked it |
| P2 variation with no channel | `B8_discovered_price_sensitivity_holdout` | idle |
| P3 heterogeneity in the wrong place | `B8_discovered_price_sensitivity_holdout` | idle |
| P4 engagement ≠ elasticity | — | **not on the map** → minted `PB4_engagement_separated_from_elasticity` |
| P5 £ or % | — | **not on the map** → minted `PB5_pounds_or_percent_resolved` |
| P6 lookup tables | — | **not on the map** → minted `C29_decisions_stop_being_lookup_tables` |
| P7 no cash mechanism | `B6_collateral_cash_death_loop`, `B7_customer_state_layer_moves_and_shocks`, `SPINE_1`/`SPINE_3` | idle, **blocked on an abolished act** |
| P8 no knowledge→atom chain | — | **not on the map** → minted `H45_the_queue_is_chained_to_the_map` |
| P9 book depth | — | **not on the map** → minted `A46_book_depth_is_a_curriculum_question` |
| P10 operational floor | `OPS6`, `OPS7`, `OPS8`, `H40`, `H41` | build |

So four of the ten needed no new atom at all, and one of those four — **P1, the most
consequential problem in the guidance — has been sitting at `loop_stage: idle` with an empty
dependency list.** Nothing was stopping it. It was invisible because nothing connects a named
problem to the atom that would fix it, which is the director's own P8. The inventory did not
mostly reveal missing work; it revealed a missing index.

### And P7 was parked on machinery that was abolished twenty-five days ago

`B6_collateral_cash_death_loop` — the atom that builds the whole of P7 and answers C3 — carried
this `block_reason`:

> *"BUILD is EPOCH-gated: opens only on a director/twin BUILD-open of an E/treasury front. No
> agent BUILD or level move until then (R16, no self-bump)."*

Every act named there was abolished on 2026-07-29 and swept on 2026-08-03. Its dependency
`SPINE_3` carried the same sentence, and so did `SPINE_1` behind that. Three atoms deep, all
parked on a permission regime that no longer exists.

**`tools/abolished_block_classes.py` exists precisely to catch this and reported zero
violations**, for two reasons that are one failure at two addresses:

1. **Wrong field.** It read `blocked_on` only. B6's `blocked_on` is `null`; the whole sentence
   lives in `block_reason` — which is exactly as much a claim about NOW, because it is the
   sentence a reader uses to decide not to draw.
2. **Wrong spelling.** It matched the *symbol* (`director_build_open`, `build_open`). A
   `block_reason` is written in *prose*. `BUILD-open` is a hyphen, not an underscore.

Fixed as a class (R10), not as three edits: `ABOLISHED_ACT_PROSE` + `LIVE_CLAIM_FIELDS`. It now
finds eight stale claims across both halves of the map, all repaired, and the repair notes moved
to a new `block_reason_history` field — because leaving the history in `block_reason` made the
guard fire on its own repair note, which is P10's "the divergence alarm counts its own output"
in miniature.

---

## The sequence, and why

The binding constraint is the guidance's own cul-de-sac: **P1 invalidates measurements taken
before it.** Anything calibrated against a market that cannot respond needs recalibrating once
it can. Everything below follows from taking that seriously rather than nodding at it.

### Wave 0 — the machine. Invalidated by nothing.

**`H45_the_queue_is_chained_to_the_map` (P8) · `A45_the_canon_is_a_standing_subject` · P10's
existing atoms.**

P8 first, and not because it is easy. The guidance calls it the velocity multiplier — *"fixing
it makes everything else cheaper"* — and this document is the evidence: the single most
consequential atom in the inventory was unblocked and invisible for weeks. Nothing about the
world changes P8's answer, so there is no reason to wait and every reason not to.

Part of it landed the same day: `background/staging_rooms.py`, the room taxonomy, the draw
order, and the chain header. `docs/staging/` went from 49 files in one folder to 15 in a ranked
queue, with reference and archive in their own rooms. What remains is the other three joints —
knowledge pages that name their atoms, discovery that cannot outrun what an atom can build, and
epoch attachment.

### Wave 1 — P1. The invalidator, and therefore first, not last.

**`B10_competitor_switching_response`** — moved `idle` → `build`.

The temptation is to sequence P1 late because it is the biggest. That is exactly backwards. Every
week it is not built is another week of measurements that will have to be retaken. The guidance
says it plainly and the seat's own published baseline is the example: flat rules £153,245 against
per-customer £157,913 is **a valid comparison between two internal policies and is not evidence
about a supplier's performance**, because it was taken against an opponent that cannot move.

### Wave 2 — P7. The other half of "the world presses", and structurally independent of P1.

**`SPINE_1_scenario_world_state`** — moved `idle` → `build`; `SPINE_3` → `B6` behind it.

Collateral calls and arrears timing do not need a competitor. Of C3's three mechanisms, only
*competition* is blocked by P1; **hedging** and **debt** are cash-and-timing problems the world
can impose today. The 2021–22 record is already in the world, which is exactly when real
suppliers failed. SPINE_1 goes to build under decomposition: the world-selection **mechanism**
is the agent's and is buildable now; only the named worlds and their probabilities are R13
curriculum and stay the director's.

### Wave 3 — P2, P3, P4, P5. The household. Built so P1 changes their answers, not their structure.

**`PB4_engagement_separated_from_elasticity`**, **`PB5_pounds_or_percent_resolved`** (both
minted, both `build`), **`B8_discovered_price_sensitivity_holdout`** (P2/P3).

These are safe to build before P1 lands **provided nothing is calibrated against the current
world**, which is the guidance's own condition. They change *what a household is*, not *what
number comes out*: two gates instead of one weight (P4); a decision scale that agrees on both
sides of the wall (P5); genuine within-household variance rather than a subgroup mean shift
(P3); and a channel that carries it (P2).

**Where the tension bites, said now rather than discovered later:** P3's target spread cannot be
chosen against the current world. The seat has already measured that price sensitivity is
*structurally unlearnable* on this book and that the published between-group spread is only
**1.26×**. Whether that is too little variance or the right amount of variance with no way to
observe it is a question only a world that presses can answer. So P3 builds the *mechanism* for
within-household variance and leaves its magnitude as a declared parameter, to be set after P1.

### Wave 4 — P6. Deliberately idle.

**`C29_decisions_stop_being_lookup_tables`** — minted `idle`, `depends_on: [B10, W2_engagement…,
W2_pounds…]`.

This is the one place the seat is deliberately *not* building the director's stated problem yet,
so the reasoning is on the record. A richer decision surface against a world that cannot react
produces a better-instrumented null. Measured, not assumed: the surface the A/B actually has is
**nine accounts wide**, and the choosing is worth **−£175 against an error bar 25× the
estimate**. DISCOVER and FRAME on it are drawable now; BUILD waits for something to exploit.

### Returned, not decided — P9.

**`A46_book_depth_is_a_curriculum_question`** — `build`, `blocked_on: null`.

Book depth moves the P&L, so R13 makes it the director's: the agent controls both sides of that
wall, and difficulty changes must be named, versioned, director-authored artefacts. **But the atom is a BUILD and is not
blocked**, which is the distinction worth being careful about: the DECISION is his, and the
PRICED MENU he needs in order to take it is the seat's and is drawable now. Parking the atom on
his answer would make the very thing he is waiting for unbuildable — which is how a real
reserved-class item and a permission ceremony end up looking identical. What the seat owes him
is: how many renewals each option buys, what each costs in wall-clock against the 30-minute
publish cadence that binds `SETTLEMENT_CUSTOMER_YEAR_BUDGET`, and which comparisons stay bounded
until it lands.

---

## The one-line sequence

> **P8 and the canon check now** (nothing invalidates them and everything is cheaper after) →
> **P1 next** (it invalidates what follows, so it must not follow) → **P7 in parallel** (cash and
> timing need no competitor) → **P2–P5 structurally, magnitudes deferred** → **P6 when there is
> something to exploit** → **P9 is the director's, priced and handed over.**

## What this costs if it is wrong

The order's one real risk is Wave 3 running ahead of Wave 1 and being tuned against the flat
world after all — the cul-de-sac, entered by accident. The guard against it is stated in each
atom rather than exhorted here: P3's magnitude is a declared parameter, P4's engagement gate
takes the comparison offer as an argument, and P5 establishes a scale rather than a value. If a
Wave 3 atom finds itself needing a number that only a responsive world can supply, that is the
signal to stop and let Wave 1 land first — and saying so in advance is cheaper than finding it
in a recalibration.
