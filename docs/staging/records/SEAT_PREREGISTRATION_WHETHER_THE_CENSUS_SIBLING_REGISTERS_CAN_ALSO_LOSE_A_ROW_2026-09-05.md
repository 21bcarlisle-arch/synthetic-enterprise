# [SEAT PRE-REGISTRATION] Can the census's sibling registers lose a row the same way, and where is deleting the row the cure for a refusal?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `census-register-low-water-third-question`
**Filed** 2026-09-05, **before any of the deletion measurements below have been run.** Every number
in §3 is a prediction with no answer visible to the writer.

Related: `dc5fcbbc8` (`removed_dispositions()`, the third rung on the alarm census),
`background/self_clearing_alarm_census.py`,
`tests/background/test_the_register_can_lose_a_row_and_take_the_alarm_with_it.py`.

---

## 1. What is established by reading, and is NOT in question

`removed_dispositions()` landed 2026-09-05 on the alarm census. Its argument, verbatim from its own
docstring: `eroded_dispositions()` iterates `sorted(disp)`, **so its subject set IS the register**,
and its non-tautology argument rests on the register being a HIGH-WATER mark that nothing kept from
falling. Measured on the live tree before it was built: delete a row and its hit together, and all
five then-existing rungs returned clean.

The second-order shape, which is the part that generalises: `eroded_dispositions()` **REFUSES** a
row whose carrier the census can no longer resolve. Deleting that row clears the refusal. A red
clearable by deleting the evidence is a fail-open with an extra step.

The generalisable defect is therefore a property of a *shape*, not of that module: **any control
written as `for key in register` has the register as its subject set.** The census now has all
three rungs (hit-without-row, row-without-hit, row-that-left). Its siblings have at most two.

Four registers in this tree have at least one control iterating them:

| Register | Iterating control | Register is |
|---|---|---|
| `docs/design/canon_claims.yaml` | `tools/canon_drift_check.py` — `evaluate()` per claim, `run()` over `load_register()` | a YAML file, versioned |
| `docs/design/maturity_map.yaml` | many, via `tools/maturity_map_store` | a YAML file, versioned |
| `background/finding_classes.py` `CLASSES` | `check()` — `for finding_class in CLASSES` | a Python literal, versioned |
| `tools/domain_constant_origins.py` | `without_origin()`, `duplicates()` over `scan()` | **DERIVED from source**, not a stored register |

The fourth is listed in the direction but is not obviously the same shape and §3 says so as a
prediction, not as a finding.

## 2. The question

For each register: **if a row is deleted from it, does every existing control return clean?** And
the sharper second question: **is there a row on which some control currently REFUSES, such that
deleting that row is the cure for the refusal?**

## 3. Predictions, made before running anything

Recorded so the measurement can refute them. Confidence in words, not invented percentages.

**P1 — `canon_claims.yaml`: HOLE, high confidence.** `run()` iterates `load_register()`; nothing
compares the register against a baseline. Deleting a claim whose verdict is a drift verdict removes
the drift from the report and `main()` exits 0. I expect no count assertion and no HEAD comparison
anywhere. This is the closest structural twin to the census and I expect it to be the one that
matters.

**P2 — `canon_claims.yaml` second question: YES.** `DRIFT_VERDICTS` includes `UNBOUND` (the anchor
sentence has gone from the page). That is *precisely* the census's path-gone refusal: the register
row refuses because its subject can no longer be resolved, and deleting the row cures the refusal.
If P2 holds, this register has the identical second-order defect and not merely a missing rung.

**P3 — `maturity_map.yaml`: PARTIAL.** I expect deleting an atom that another atom names in
`depends_on` or `couples_with` to red on a dangling-reference check, which would be an accidental
low-water guard. I expect deleting a LEAF atom — nothing pointing at it — to return clean. If both
hold, the map is protected only by the accident of being referenced, which is not a control.

**P4 — `CLASSES`: UNCERTAIN, leaning clean.** Deleting a class leaves its class document in the
staging root. I do not know whether that document then reads as an unclassed finding, as a TWO
ROOMS collision, or as nothing at all. I genuinely cannot predict this one and am recording that
rather than picking a side.

**P5 — `domain_constant_origins.py`: NOT THE SAME SHAPE.** Its subject set is derived from a scan
of the source, so "deleting a row" means deleting the constant, i.e. deleting the carrier itself.
That is an honest change, not an erasure of the record that a carrier existed. I predict this
candidate is correctly excluded and that saying so is the finding, not building a rung for it.

## 4. What would refute the whole direction

If every register above already has a baseline-vs-HEAD comparison, or if the deletions all red for
reasons that are genuine controls rather than accidents, the direction is spent and this turn should
say so rather than building. That outcome is filed the same way as any other.

## 5. What done means for the turn that follows

Not "four rungs". A rung per register, hand-rolled, is the shape CLAUDE.md names as regressing every
repair the helper holds. Done means: **one shared low-water mechanism, mutation-proved, wired at the
sites the measurement shows are actually holed, with the wiring proved at each site** — because a
control that calls the shared helper survives mutation of the caller, so the helper being proved is
not the site being proved.
