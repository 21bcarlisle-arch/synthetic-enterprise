**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 2 · **Atom:** unminted

*RECORDED, not BLOCKING: the leg with an unambiguous direction was repaired in the same turn
(the ceiling now runs on the production draw, R15 mutation-proven), so nothing is left refusing
work. Two sibling guards are STATED and unrepaired at the bottom, deliberately: both have a
blast radius this tick has no measurement for, and guessing at either is how the third broke.*

# The pass ceiling was live on the idle draw nothing calls, and absent from the one that hands out the work

**Found:** 2026-09-06, delivery seat, on being woken by a LANE 3 doorbell that drew
`EP17_varied_population_draw` for a **seventh** DISCOVER/FRAME pass. Found by checking the
draw before doing it, not by the work failing.

---

## The measurement

`python3 -m tools.discovery_pass_ceiling`, live tree, at the moment the doorbell fired:

```
  since passes  moves  stage    level  atom
      6      6      0  idle       0/3  EP17_varied_population_draw
      5      5      0  idle       0/3  EP16_anchored_generators

EP17_varied_population_draw [idle] -- promote to build, or close it --
  investigating again is no longer an available answer
```

The atom the doorbell handed me for investigation is the atom the ceiling names as one that
may no longer be investigated. `EP16_anchored_generators`, the other saturated idle row, was
equally drawable.

## The cause — two doors, and the guard is on the one with no production caller

`tools/discovery_pass_ceiling.py` shipped 2026-08-19 against the director's ruling: *"make it
impossible for the system to run indefinitely on work that cannot change its own state."*

| draw function | applies the ceiling | called by |
|---|---|---|
| `supervisor._idle_discover_frame_draw` | **yes** (`saturated_ids()`, fail-closed, ~40 lines of rationale) | nothing in the doorbell path |
| `supervisor._idle_discover_frame_draw_concurrent` | **no** | `_self_refill_draw()` (line ~5437) — the LANE 3 doorbell |

`_self_refill_draw` composes the message a worker tick is woken with. It calls the concurrent
twin. Until this turn that twin filtered on `_is_externally_blocked`, `_is_frame_saturated` and
staleness, and never on the ceiling — so the lane the ruling was written to make finite stayed
infinite on the only path that matters.

The 2026-08-19 repair's own follow-up is the reason this hid.
`tests/background/test_harden_rung_pass_ceiling.py`'s docstring records that the ceiling
*"reached exactly ONE consumer, `supervisor._idle_discover_frame_draw`"* and treats that as the
idle tier being covered. It was the wrong one, and the extension work that followed went
sideways into `build`/`harden` (`core_draw_exclusions`) rather than checking whether the idle
consumer named was the live one. **The census of consumers was taken by name, not by caller.**

## The repair

`background/supervisor.py::_idle_discover_frame_draw_concurrent` now applies
`saturated_ids()` after the H23 frame-saturation skip and before the stall ordering — the same
position and the same fail-closed direction as its singular twin. An unreadable ceiling returns
`[]` rather than reopening the lane; BUILD, SITE and HARDEN are untouched.

Live cost, measured rather than assumed: **2 of ~80 idle candidates** leave the draw, so the
fix cannot starve the tier.

**R15, three controls in `tests/background/test_harden_rung_pass_ceiling.py`, each proven able
to fail.** Baseline 16/16 green through the identical command first.

| control | mutation | result |
|---|---|---|
| `..._a_saturated_IDLE_atom_is_excluded_from_the_CONCURRENT_discovery_draw` | `over_ceiling = set()` | **RED** |
| `..._no_atom_over_the_idle_ceiling_survives_the_live_concurrent_draw` | same | **RED**, and it named `EP17_varied_population_draw` off the real map |
| `..._an_UNREADABLE_ceiling_closes_the_concurrent_draw_rather_than_reopening_it` | `return []` → fall through | **RED** |
| `..._an_UNSATURATED_idle_atom_still_reaches_the_concurrent_draw` | (poison round) | GREEN under both — the leg that stops "excluded" meaning "the draw is empty" |

---

## The two siblings, stated and NOT repaired

Three independent guards should each have refused this draw. All three were inert on EP17, for
three different reasons, and only one had a repair whose direction was unambiguous.

**1. `_is_externally_blocked` reads a field nobody writes.** EP17's `block_reason` says, in
words: *"no further DISCOVER pass is authorised … until then a pass here is the livelock, not
the work."* The draw filter commented `# never draw director-blocked atoms` reads
`blocked_on`. Census of the live map:

```
  atoms: 336   blocked_on rows: 0   block_reason rows: 22   both: 0
```

**The filter is inert across the entire map** — it cannot fire, because the field it reads is
empty on every row. `tools/abolished_block_classes.py` already recorded this exact class fix
for a different consumer (*"WRONG FIELD. It read `blocked_on` only"*) and defines
`LIVE_CLAIM_FIELDS = ("blocked_on", "block_reason")`; the supervisor's filter was never brought
to it. This is the VAT shape CLAUDE.md names — one rule, several implementations, fixed in one.

Not repaired here because `background/blocked_atom_visibility.py` carries a recorded decision
that *"`block_reason` is prose stating the gate and is NOT what parks the atom"*, and reading it
as blocking would remove 22 rows from every draw. Reversing a recorded decision needs the
measurement of what those 22 rows are, which this tick does not have.

**2. `_is_frame_saturated` is keyed to the evidence list, not to disk.**
`docs/design/frame/EP17_VARIED_POPULATION_DRAW_FRAME.md` exists and is the output of six
passes. The guard resolves the atom's `evidence` (correctly, through the `_atom_evidence`
rehome seam — that part works), and EP17's evidence names three source documents and **not the
FRAME doc its own passes wrote**. So a six-times-framed atom reads un-framed.

The proxy is "did somebody list the FRAME doc", and the property is "does the FRAME doc exist".
Not repaired here because keying it to disk instead would change the verdict on every framed
atom in the map at once, and this control's whole documented philosophy is fail-toward-offering
precisely because starving a genuine atom is its expensive direction.

---

## What this says about EP17 and EP16

Neither is drawable for discovery any more, which is the ceiling working. Their next honest
answer is *promote to build, or close* — and for both, promotion is an epoch-4 curriculum act
that R13 reserves to the director. That is a decision to put to him, not a pass to take. It is
**not** actioned here and no level moved; this finding records that the two rows now surface as
decisions rather than as work.

`EP3_pricing_engine_late_truth`, the other atom on the same doorbell, is at 2 passes and is not
saturated — its draw was legitimate and is unaffected by any of this.
