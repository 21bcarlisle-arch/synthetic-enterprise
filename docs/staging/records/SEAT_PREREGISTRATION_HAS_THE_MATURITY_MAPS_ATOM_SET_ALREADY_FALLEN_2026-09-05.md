# [SEAT PRE-REGISTRATION] Has the maturity map's atom set already fallen, and would a low-water rung have wedged honest work?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `census-register-low-water-third-question`
**Filed** 2026-09-05, **before any of the measurements in §3 have been run.** Every number in §3 is
a prediction with no answer visible to the writer.

Predecessors, both landed today: `dc5fcbbc8` (`removed_dispositions()` on the alarm census) and
`6f4e6b1f4` (`background/register_low_water.py`, the shared mechanism, wired at
`background/finding_classes.py`).

---

## 1. What is established by reading, and is NOT in question

`6f4e6b1f4` measured all four sibling registers the direction named and left exactly one piece
unbuilt, naming it in its own commit message and in the finding:

> `docs/design/maturity_map.yaml`: **HOLED for a leaf.** 314 atoms, 175 named by nothing in
> `depends_on`/`couples_with`/`blocked_on`; deleting one returned 0 violations from all five facet
> checks. Measured and written up, **NOT wired**: the map is a bare list with nowhere to hang a
> retirement reason, and choosing that home is the work.

So the *measurement* is not in question here and is not repeated. Two things are.

**(a) A live contradiction in the record.** `background/register_low_water.py`'s own docstring says
of `docs/design/maturity_map.yaml`: "**Wired here.**" Nothing wires it — `grep -rn
register_low_water` returns `finding_classes.py` and the test file only. The module makes a
checkable claim about itself that is false. That is not a prediction; it is read directly, and it
is repaired by this turn either way (by wiring it, or by correcting the sentence).

**(b) The map is TWO files.** `maturity_map.yaml` + `maturity_map_closed.yaml`, split 2026-08-26;
`tools/maturity_map_store.MAP_PARTS_REL` is the pair, and `refile()` MOVES atoms from the live half
to the closed half. So the register whose low-water mark matters is the union of both halves —
measuring the live half alone would read every honest refile as a deletion. `level_promotion_gate`
already knows this (`_whole_map`, which concatenates both parts at a revision) and says so in its
own docstring.

## 2. Why the answer is not already known

The third question — *can the register shrink?* — has been asked of the map as a hypothetical
(delete a row, see nothing fire). It has **not** been asked of the map's own history. A gate that
refuses a removal is only shippable if honest work does not routinely remove atoms; and if the set
HAS already fallen, the rows that went are evidence nobody can now recover.

## 3. PREDICTIONS — written before any of these are run

**P1 — the whole-map atom-id set has shrunk in at least one landed commit.** Confidence: moderate-
high. Point prediction: **between 3 and 15** commits touching a map part show a net shrink of the
union key set. Reasoning: the director's 2026-08-24 instruction was explicitly *"delete what
shouldn't exist"*, so at least one deliberate pruning pass should be visible.

**P2 — measured over the LIVE half alone, the 2026-08-26 split shows as a shrink of >200 atoms;
measured over the UNION it shows as zero.** Confidence: high. This is the invariant `_whole_map`
exists to preserve, and if it does not hold the split itself lost atoms.

**P3 — `refile()` preserves the union key set exactly.** Confidence: high, from reading `_cut_blocks`
/ `_append_blocks`. Recorded because it is the single legitimate operation most likely to trip a
naive rung, and "high confidence from reading" is how the last two defects here got through.

**P4 — at least one atom id that existed in the map at some past commit is in NEITHER half at HEAD,
with nothing anywhere saying why.** Confidence: moderate. Point prediction: the count is **greater
than zero and of order tens**. If it is zero, the map's protection-by-accident held in practice and
the rung is prophylactic; if it is large, the register has already fallen and the rung is late.

**P5 — the honest home for a retirement reason is a THIRD sibling file, not a section inside either
half.** Confidence: high, but recorded as a prediction because it is a design call I could be wrong
about: both halves are top-level YAML *lists* that are concatenated and line-scanned for `- id:`,
so a `_retired` mapping inside one of them breaks `map_text()`'s concatenation contract. If a
mapping CAN live in a half without breaking a reader, P5 is refuted and the simpler home wins.

**P6 — wiring the rung at `level_promotion_gate.main()` costs no new git reads.** Confidence: high:
that gate already computes `_whole_map(":")` and `_whole_map("HEAD:")` for the level comparison, and
already returns 0 early when no map part is staged. Recorded because "it's free" is the claim most
likely to be wrong once the fail-closed branches are written.

## 4. What would refute the direction rather than the predictions

If §3 P1 comes back large — say every second map commit drops an atom — then a refusing gate is the
wrong mechanism, because it would wedge ordinary work several times a week, and the right answer is
a report, not a refusal. That outcome is recorded here as a stopping condition, not as a failure.
