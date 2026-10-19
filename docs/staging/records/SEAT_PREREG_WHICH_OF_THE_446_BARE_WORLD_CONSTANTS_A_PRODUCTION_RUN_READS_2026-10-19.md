**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery
**Class:** `unanchored_world_constant` (primary)

# Pre-registration: which of the 446 bare world constants does a production run actually read?

**Claim:** `anchor-the-446-bare-world-constants-in-impact-order`
**Written BEFORE the measurement below was run.**

## The question

`7cb23588e` registered 446 bare world constants (`docs/design/world_constant_anchor_register.txt`).
The director's 19 Oct 16:28 reading: anchor them in impact order, not alphabetically. A constant
cannot move a published figure unless the run that publishes reads it. So the first cut of
"impact" is reach: is the line that reads the constant executed in a production run?

## What "reads" means, said before it is measured

A READING SITE is a `Load` of the constant's name: inside its own module, through a
`from M import NAME [as A]` in another module, or as `m.NAME` where `m` is bound to the module.
A module-level assignment computed FROM the constant makes its targets carry the constant
(followed to a fixpoint), so `DERIVED = NAME * k` is reached when `DERIVED` is read. A default
argument counts when the function's body runs. A class-body read is recorded as its own kind and
not resolved further.

REACHED means at least one reading site inside a function body executed, recorded by
`sys.monitoring` LINE events in one process (`SE_FORK_WORKERS=1`, so no forked worker escapes the
monitor), under `SIM_FAST_MODE=1`, which every production launch sets. Import-time execution of a
module-level line does not count: it says the module was imported, not that a draw used the value.

## The instrument's known blind spots

`getattr(module, "NAME")` with a string, `globals()[...]`, and a value copied into a dataclass
field default then read as an attribute are not resolved. Each makes a reached constant read as
unreached, never the reverse — the ranking errs towards calling a constant dead, so a constant in
the unreached tier still needs one grep before it is dismissed.

## Predictions (short window, `report_end=2017-06-30`, the default book)

- **P1.** Reached: between 120 and 220 of 446 (point 170).
- **P2.** `sim/`: at most 20 of its 64 reached — much of `sim/` is market reconstruction the run
  reads from a cache, not live.
- **P3.** At least 60 of 446 have no function-body reading site anywhere in the tree (dead on
  arrival, or read only by tests).
- **P4.** `simulation/population_draw.py::DEFAULT_BAND_WEIGHTS` is reached.
- **P5.** A full-window run (to the data's end) reaches fewer than 15% more constants than the
  short window. If it is more, crisis-only branches matter and the short window is not a usable
  proxy for ranking.

## What it decides

The reached tier is the anchoring queue; within it, the second cut is a one-at-a-time sensitivity
on the published figures for the top entries. The unreached tier is not anchored first — its
constants move nothing the company or the site can see, and each one is a candidate for deletion,
which is cheaper than a citation.

## Addendum, written after the short-window reach and BEFORE the sensitivity screen

Reach, short window (graded in the finding): 239 reached, so P1 is refuted just above its band.

**The screen.** One arm per MODULE, scaling every reached bare constant in it by 1.1 (a share stays
at or below 1; a container summing to one moves mass onto its first entry, because scaling every
weight of a normalised distribution is a no-op). Same short window and default book; baseline run
twice. Read: relative change in `total_gross`, `total_bad_debt`, the settled records' summed
numeric fields, and the churned-account count. Blind spot, named now: same-direction scaling of a
whole module can cancel, so a module that moves nothing is "did not move under this push", not
"no impact"; a module that moves is then split one constant at a time.

- **P6.** The two baseline arms agree in every figure to the last digit (the run is seeded).
- **P7.** At most half the module groups move `total_gross` by more than 0.1%.
- **P8.** `premise_trace` and `fabric_physics` are among the three groups that move `total_gross` most.
- **P9.** `feedback_survey` and `sim_satisfaction` move no money figure by more than 0.1% inside
  eighteen months.
