**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `generated-tree-declarations-are-exactly-two-segments-so-a-deeper-or-shallower-generated-tree-cannot-be-expressed`)

# A generated-tree declaration is a path prefix of any depth now — and the pair shape was not merely inexpressive, it was emitting a path that is not a file while the real artefact reached neither oracle

**Filed 2026-09-15, delivery seat.** Prereg:
`docs/staging/records/PREREG_WHAT_THE_DEPTH_TWO_SHAPE_OF_A_GENERATED_TREE_DECLARATION_EXCLUDES_2026-09-15.md`,
written before any directory was counted and before `generated_artefacts()` was asked what it
returns.

Two consecutive findings named the same structural limit and acted on neither:

> A generated tree that is one segment deep, or three, cannot be expressed at all.
> `GENERATED_TREES` members are exactly `(parent, child)`. `docs/observability/scale_probe_10k` is
> already reached only because its parent is declared. This is a real structural limit, named here
> rather than discovered by the next census.

That is how a named gap becomes furniture. It is acted on here, and **the sentence above is itself
half wrong** — the correction is §3 and it is the reason this turn was worth more than a type
change.

---

## 1. The two questions, separated, because running them together is why neither moved

**(A) EXPRESSIVENESS** — *can* a tree of another depth be declared? A property of the type.
**(B) POPULATION** — is there a tree of another depth that *wants* declaring? The census answers it.

The earlier findings treated "generalise the tuple" and "record the limit with its count" as
alternatives. They are not: the count is evidence about **members**, the tuple is about the
**type**. A is worth doing at population zero provided it cannot move the gate; B is what decides
whether anything is added.

## 2. The census — depth 1 and depth 3, which the 2026-09-15 census computed and never published

12,853 tracked files; 169 write-reached paths. Instrument: `_write_reached_paths()`, the
tree-agnostic write-site scan — `generated_artefacts()` cannot answer a question about which trees
are undeclared, because it is keyed to `GENERATED_TREES` and would be evidence about itself.

**Depth 1 — every top-level directory holding a write-reached file:**

| directory | tracked | reached | density |
|---|---|---|---|
| `site` | 466 | 48 | 0.103 |
| `sim` | 64 | 4 | 0.062 |
| `docs` | 9,363 | 76 | 0.008 |
| `background` | 213 | 1 | 0.005 |
| `tests` | 1,720 | 1 | 0.001 |

**Q1 HELD.** Five directories hold a write-reached file and none is a plausible generated tree —
the densest is `site` at 0.103, and each is overwhelmingly authored source. **Nothing wants a
depth-1 declaration**, and §5 turns that into the floor rather than leaving it as a happy fact.

**Depth 3 — every directory holding a write-reached file:**

| directory | tracked | reached | density | under a declared prefix? |
|---|---|---|---|---|
| `docs/staging/reference` | 7 | 1 | 0.143 | no |
| `docs/domain_artefact_library/regulatory` | 12 | 1 | 0.083 | no |
| `site/data/customers` | 252 | 1 | 0.004 | **yes** |

Depth 4 and 5: **zero** directories with any write-reached file.

**Q2 point FALSIFIED, band held.** I predicted 0 undeclared depth-3 directories, accepting 0–3, and
there are 2. Both are single-file hits in trees whose other 6 and 11 files are hand-written prose
(`docs/staging/reference` is the staging reference shelf; `docs/domain_artefact_library/regulatory`
is the published-law commons). Neither is a generated tree and neither is declared. The point
prediction was wrong and the decision it fed was not.

**Q3 HELD on the count and FALSIFIED on the instance, and the instance is the finding.** I predicted
≥1 depth-3 directory under a declared prefix and named `docs/observability/scale_probe_10k` as the
minimum. The count is 1 — and it is `site/data/customers`. **`scale_probe_10k` does not appear at
all**, which is what sent me to §3.

**The one-sidedness is inherited and is stated rather than buried.** This census can show that a
directory is written; it cannot show one is authored, because the scan leaves 364 destinations
unresolved against the 169 it resolves. Q1 and Q2 are upper bounds on what the instrument can see,
not claims about the tree. A depth-3 generated tree whose producer builds its path through a
cross-module helper, two frames, a rebound parameter, or a `/` join on a name would score 0 here.

## 3. The correction: "reached only because its parent is declared" is true of the GATE and false of the ORACLE

Both earlier findings said `docs/observability/scale_probe_10k` was already reached via its parent,
which reads as *there is nothing here to fix*. Asked of the live tree:

| path | tree-keyed oracle | write-keyed oracle | reconciler UNION | `offends()` | on disk |
|---|---|---|---|---|---|
| `docs/observability/scale_probe_10k/report.json` | **no** | **no** | **no** | yes | **yes** |
| `docs/observability/scale_probe_10k/prediction_register.json` | **no** | **no** | **no** | yes | **yes** |
| `docs/observability/report.json` | **yes** | no | **yes** | yes | **no** |

`offends()` decides by prefix, so the GATE reached them. `origin_reconcile._split_generated` reads
exact **membership**, and by that reckoning both real artefacts were somebody's WORK — so the
reconciler was leading with how to **land** them, on AO12's output. Meanwhile a path that is not a
file sat in the generated set claiming to be one.

The mechanism, and it is worse than inexpressiveness. The match is a **membership test** over one
assignment's string constants and the emitted path is **hard-joined from the declared pair**:

```python
if a in parts and b in parts:
    found.update(f"{a}/{b}/{s}" for s in parts if s.endswith(ARTEFACT_SUFFIXES))
```

`simulation/premise_population.py:1189` writes
`... / "docs" / "observability" / "scale_probe_10k" / "report.json"`. `docs` and `observability`
both matched; `scale_probe_10k` carries no artefact suffix and was silently dropped from the join;
the oracle emitted `docs/observability/report.json`. **A grep for the concept name would have found
`scale_probe_10k` in the producer and concluded it was covered.** It was not covered; it was
mis-spelled into a neighbour that does not exist.

## 4. The repair, and the measurements that gated it

*(This section was headed "What landed" and `tools/landed_manifest_check` refused the commit for
it, correctly. A `what landed` heading makes every backticked path in its body a claim that the
path is in the tree — and this section names `docs/observability/report.json` precisely because it
is NOT a file. The heading was wrong, not the control: what follows is a measurement narrative, not
a manifest of landed paths. Recorded rather than quietly retitled, because the refusal is a better
description of this document's subject than the heading was.)*

`GENERATED_TREES` is now `tuple[tuple[str, ...], ...]` — a path prefix of any depth — and the two
derived views (`_tree_prefixes()`, `_WHOLE_PATH_PREFIXES`) are rebuilt from it at whatever depth.
The match requires **every** declared segment, so a deeper member is strictly harder to satisfy than
the shallower one containing it and can never fire where its parent does not.

`("docs", "observability", "scale_probe_10k")` is declared beside its parent, not instead of it.

**Q6 HELD, measured in isolation before the member was added.** The type change alone, with the same
six trees spelled as length-2 tuples, moves `generated_artefacts()` by **0** members, `violations()`
by **0**, `gate_violations()` by **0**. That was the stopping rule: a generalisation that moves the
gate is a widening wearing one's clothes and would have needed the freeze re-measured in the same
commit. It did not move.

**Q7 HELD.** The depth-3 member adds **0** gate violations. `offends()` is decided by the subsuming
prefix `docs/observability` and everything under the deeper prefix was already refused by it — the
memory-file shape, in the direction that makes a *narrower* prefix free. This is exactly why
`("docs", "status")` needed its freeze re-measured and this one does not, and §5's second control
makes that distinction checkable instead of remembered.

**Q8 HELD.** 0 frozen entries go stale. AO12's two remain live on the depth-2 prefix.

**Q4 HELD, on the instance I named in advance.** `docs/observability/report.json` is in the oracle
and is not a file. **Q5**: 55 of 222 members are not on disk — above my 3–12 band, but the count is
not the one I was measuring, because most are gitignored state files that legitimately do not exist
in a fresh worktree. The fabrication class needs its own instrument and §6 is it.

**The member pays 1 of 2, and the honest number is here rather than rounded up.**
`report.json` joins the union; `prediction_register.json` does **not**, because no assignment
anywhere names it beside those segments — `tools/scale_probe_10k.py` binds
`ARTEFACT_DIR = PROJECT / "docs" / "observability" / "scale_probe_10k"` with no artefact suffix in
scope, and then joins the filename in a separate expression the membership test cannot see. Union
259 → 260.

## 5. The controls, and the mutation each one names

`tests/tools/test_a_generated_tree_declaration_may_be_any_depth.py`, four legs, every one reddened
by running the mutation in its own docstring rather than by asserting it would:

| leg | mutation that reddens it | verified |
|---|---|---|
| a declaration may not be one segment deep | append `("site",)` | red |
| a nested declaration is subsumed at the gate | nest under an **undeclared** parent | red |
| the depth-3 member is load-bearing | drop it | red |
| both derived views read the declared set | pin either back to `f"{a}/{b}"` | red |

**The floor is the load-bearing leg and it is not a style rule.** Widening a membership test
downward is the one direction this change is dangerous in. Two segments need two independent
constants to coincide in one assignment; one segment needs a coincidence that happens constantly —
every assignment mentioning `"site"` beside any `.json` name would emit `site/<that name>` into a
set whose consumer's remedy is REVERT. The census says nothing wants depth 1, so the floor costs
nothing today, and it is asserted rather than trusted to the comment beside it.

**The fourth leg caught a live defect within the minute it was written.**
`test_a_generated_tree_may_hold_an_authored_document.py:109` had re-derived the prefixes itself as
`tuple(f"{a}/{b}/" for a, b in fs.GENERATED_TREES)` — a second implementation of one rule, which
raised `ValueError: too many values to unpack` the moment a member became three segments. It now
reads `fs._WHOLE_PATH_PREFIXES`, the subject's own answer, and the keying claim in its docstring is
unchanged. **That is the whole reason the leg exists**: a half-done generalisation does not raise on
a 2-tuple, so without it the tree would have stayed green while one view honoured the deeper member
and the other did not — a carve-out honoured by one of two unioned oracles, which is no carve-out.

40 tests across the four controls on this module: green. `gate_violations()`: empty, 11 frozen.

## 6. What is still out, with counts rather than names

- **The hard-join fabrication is a SEPARATE defect and is filed separately**, deliberately not
  folded into this repair, because a reader seeing one fixed must not conclude the other was. Seven
  assignment sites flatten a deeper destination or emit a cross-product of two declared trees in one
  assignment (`tools/mirror_github_pages.py:22` matches both `site/data` and `site/state` and emits
  every artefact name under both). Declaring the depth-3 member fixes the *missing* half for
  `scale_probe_10k` and leaves the *fabricated* half standing: `docs/observability/report.json` is
  still emitted. See
  `SEAT_FINDING_THE_TREE_KEYED_ORACLE_HARD_JOINS_A_PATH_FROM_THE_DECLARED_PAIR_SO_A_DEEPER_DESTINATION_IS_EMITTED_AS_A_FILE_THAT_DOES_NOT_EXIST_2026-09-15.md`.
- **`prediction_register.json` is still in neither oracle** — §4. The declaration was necessary and
  is not sufficient; the remaining blindness is the separate-expression join, which is the
  fabrication finding's subject too.
- **A depth-1 generated tree, if one ever exists, needs a different mechanism than this membership
  test** — not a shorter tuple. The floor says so in its own refusal message.
