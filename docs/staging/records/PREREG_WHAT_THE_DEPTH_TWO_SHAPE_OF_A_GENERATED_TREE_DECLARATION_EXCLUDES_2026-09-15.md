# PREREG — what does the DEPTH-TWO shape of a generated-tree declaration actually exclude?

**Written 2026-09-15 by the delivery seat, BEFORE any directory was counted and before
`generated_artefacts()` was asked what it returns.** Lane 0, claim
`generated-tree-declarations-are-exactly-two-segments-so-a-deeper-or-shallower-generated-tree-cannot-be-expressed`.

`GENERATED_TREES` in `tools/file_scope_generated_paths.py` is a tuple of `(parent, child)` pairs.
Two consecutive findings have now named the consequence as a structural limit and neither acted on
it:

- `SEAT_FINDING_A_FOURTH_GENERATED_TREE_EXISTS_AND_THE_CARVE_OUT_ONLY_COVERED_ONE_OF_TWO_ORACLES_2026-09-15.md`
  §9: *"A generated tree that is one segment deep, or three, cannot be expressed at all …
  `docs/observability/scale_probe_10k` is already reached only because its parent is declared. This
  is a real structural limit, named here rather than discovered by the next census."*
- `SEAT_FINDING_A_PREFIX_REFUSAL_HAD_NO_PER_PATH_HATCH_..._2026-09-15.md`, same limit, restated.

The 2026-09-15 census measured density for every directory at every depth but its finding
**published only the two-segment rows**. Depth 1 and depth 3 were computed and never reported, so
the count the limit needs has never been written down.

---

## 1. The two questions, and they are not the same question

This turn separates them deliberately, because the earlier findings ran them together and that is
why neither could be acted on.

**(A) EXPRESSIVENESS — can a tree of another depth be DECLARED?** A structural property of the
type. Nothing about today's tree can make a 1- or 3-segment prefix expressible.

**(B) POPULATION — is there a tree of another depth that WANTS declaring?** An empirical question,
answered by the census.

A is worth fixing even if B is zero, *provided the fix cannot move the gate*, because the cost of
the limit is paid by the next census rather than this one. B is what decides whether anything gets
added. Conflating them is how "record the limit as deliberate with its count" and "generalise the
tuple" got treated as alternatives: they are not — the count is the evidence for whether to add a
MEMBER, and the generalisation is about the TYPE.

## 2. The instrument

Same as the 2026-09-15 census and for the same reason: `_write_reached_paths()`, the tree-agnostic
write-site scan. `generated_artefacts()` cannot answer a question about which trees are undeclared,
because it is keyed to `GENERATED_TREES` and is therefore evidence about itself.

**And I inherit that census's own correction**: density is a ONE-SIDED instrument. High density is
informative; low density is not evidence of authorship, because the scan's recall is poor by
construction (364 unresolved destinations against 169 resolved). So density NOMINATES and never
justifies — any candidate is then verified file by file on provenance.

## 3. What I am measuring

Over every directory `D` in the repo at every depth, `tracked(D)` / `reached(D)` / `density(D)` as
before, but this time **partitioned by segment count** and reported for depths 1 and 3+, which the
previous finding computed and dropped.

And one thing the previous census did not ask at all, about the mechanism rather than the
population: **what `generated_artefacts()` returns for a destination built DEEPER than the declared
pair.** The segment match is

```python
for a, b in GENERATED_TREES:
    if a in parts and b in parts:
        found.update(f"{a}/{b}/{s}" for s in parts if s.endswith(ARTEFACT_SUFFIXES))
```

`parts` is every string constant in the assignment, membership-tested, and the emitted path is
**hard-joined from the declared pair**. So for `PROJECT / "docs" / "observability" /
"scale_probe_10k" / "report.json"` the test passes on `docs` and `observability`, and the path it
emits is `docs/observability/report.json` — which is not where the module writes. That is a
prediction about the code, stated here before it was run, and it is the reason this frame is about
more than declaring a new member.

## 4. The predictions

Each marked HELD or FALSIFIED in the result, beside the answer, whichever way it falls.

| # | Prediction |
|---|---|
| Q1 | Depth-1 (top-level) directories that are undeclared candidates — any write-reached file, `tracked ≥ 3`: several will have write-reached files, but **0** will be a plausible generated TREE, because every top-level directory here (`docs`, `site`, `sim`, `tools`, `background`, `tests`) is overwhelmingly authored. Depth 1 is excluded by the shape and **nothing wants it**. |
| Q2 | Depth-3+ directories with any write-reached file, NOT under a declared prefix: **0**, accepting 0–3. Generated output in this tree is flat; the one nested generated directory I know of (`docs/observability/scale_probe_10k`) is under a declared prefix already. |
| Q3 | Depth-3+ directories with write-reached files that ARE under a declared prefix: **≥ 1** (`scale_probe_10k` at minimum), accepting 1–8. These are the ones "reached by accident of nesting" — the drawn item's phrase — and they are the population the expressiveness question is really about. |
| Q4 | `generated_artefacts()` today returns **at least one path that does not exist on disk**, produced by the §3 hard join flattening a deeper destination. I name `docs/observability/report.json` and `docs/observability/prediction_register.json` in advance as the two most likely. |
| Q5 | Total members of `generated_artefacts()` that do not exist on disk, from ANY cause: **3–12**. (Separate from Q4 because a fabricated path can also come from an artefact-suffixed string that was never a destination at all.) |
| Q6 | Generalising `GENERATED_TREES` to an arbitrary-length segment tuple **without changing what is covered** (the same six trees, spelled as 2-tuples that happen to have length 2) moves `gate_violations()` by exactly **0** entries and `generated_artefacts()` by exactly **0** members. If either moves, the generalisation is not coverage-preserving and I have mis-modelled the mechanism. |
| Q7 | The number of live `gate_violations()` entries created by declaring `("docs", "observability", "scale_probe_10k")` as an explicit member, on top of the six: **0**, because `offends()` is decided by the SUBSUMING prefix `docs/observability` and every path under the deeper prefix is already under it. This is the memory-file shape *"widening can't move a gate whose membership test is subsumed"* and it should hold here in the other direction — a NARROWER prefix adds nothing the wider one did not already refuse. |
| Q8 | `FROZEN` entries going stale from the generalisation: **0**. `AO12_scale_probe_10k`'s two frozen entries are `docs/observability/scale_probe_10k/report.json` and `.../prediction_register.json`; both stay live because the depth-2 prefix still refuses them. |

## 5. What I do with each answer

- **Q6 FALSIFIED** — stop and do not land the type change. A generalisation that moves the gate is
  not a generalisation, it is a widening wearing one's clothes, and it needs the freeze re-measured
  in the same commit (the rule that `("docs", "status")` was landed under).
- **Q6 HELD, Q2 = 0, Q3 ≥ 1** — the type change lands on its own, with the census as the record of
  why no new MEMBER accompanies it. The limit stops being furniture because the shape can express
  the thing; the population says nothing needs expressing yet. That is the expected outcome and it
  is deliberately the *smaller* of the two deliverables.
- **Q2 ≥ 1** — the candidate is verified file by file on provenance, exactly as `docs/status` was,
  and only then declared. Density nominates; it does not justify.
- **Q4 HELD** — the fabrication is real and is a SEPARATE defect from the expressiveness limit. It
  is filed as its own finding with the count, and fixed in this turn only if the fix is provably
  gate-neutral. It is not folded silently into the type change: they have different causes and a
  reader who sees one repair must not conclude the other was made.
- **Q4 FALSIFIED** — recorded as a correction beside the §3 reasoning, because I stated the
  mechanism as fact and would have been wrong about code I had just read.

## 6. What this cannot establish

The census inherits the write-site scan's recall ceiling and therefore cannot show that a directory
is authored — only that one is written. A depth-3 tree whose producer builds its path through any
of the four unresolved shapes (cross-module helper, two frames, a rebound parameter, a `/` join on
a name) is invisible to this and would score 0. **Q1 and Q2 are therefore upper-bounded claims
about what the instrument can see, not claims about the tree**, and the finding must say so in
those words rather than reporting a bare zero.
