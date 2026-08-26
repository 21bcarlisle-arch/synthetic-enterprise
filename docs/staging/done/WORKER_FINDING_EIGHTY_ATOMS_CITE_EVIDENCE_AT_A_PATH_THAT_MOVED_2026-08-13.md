# [WORKER-FINDING] Eighty atoms cite their evidence at a path that moved, and the archive move is what moved it (2026-08-13)

**Severity:** LATENT · **Lane:** H_harness · **Status:** measured and reported, **not swept** — per
SELF_INTERRUPT_DISCIPLINE this is queued as a class, not fixed on sight. Found while drawing
`EP10_adapter_uk_link_xoserve` (LANE 3 DISCOVER), whose own two evidence pointers are two of the 66.

No published figure and no control's verdict reads these pointers today, which is why this is LATENT.
It is also why nothing has caught it: **nothing resolves them**, so nothing goes red when they rot.

## The measurement

`observed-with-evidence`. Over every `docs/design/simplifications/*.yaml`, taking each `map_records`
value that is a space-free path ending `.md/.py/.yaml/.json/.html` (the conservative subject — several
records hold whole prose paragraphs that merely end in a filename, and those are excluded):

```
space-free path refs:          648 distinct, across 264 atoms
DEAD (os.path.exists false):    66
atoms carrying >=1 dead path:   80
```

**80 of 264 atoms — 30% — cite at least one piece of evidence at a path that is not there.**

Of the 66 dead paths, **63 are MOVED, not gone** — the basename exists elsewhere in the tree:

| now lives in | count |
|---|---|
| `docs/staging/done/` | 46 |
| `docs/staging/in_progress/` | 8 |
| `docs/domain_artefact_library/scope_briefs/` | 7 |
| `docs/design/refs/` | 1 |
| `site/evidence/` | 1 |

The dominant cause is **ordinary archiving**: a record cites `docs/staging/X.md`, the staging protocol
later moves X to `docs/staging/done/`, and the atom's record still names the old path. Commit `314f16912`
("Drain the staging backlog: 98 root docs to 64") relocated a large batch in one go — EP10's own two,
`ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md` (now `docs/design/refs/`) and
`ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md` (now `docs/domain_artefact_library/scope_briefs/`), among them.
**Archiving a document silently breaks every atom record that cited it.**

Three are absent from the tree entirely, and each names something real that was deleted or never built:

* `background/fronts_reconciler.py` — cited by `H25_self_gov_detection_hardening`; deleted by the
  2026-08-03 permission rip-out, which `tests/background/test_gate_authorization.py::test_the_permission_surface_is_gone`
  requires to stay deleted. The atom record still points at it.
* `tools/generate_method_casebook_data.py` — cited by `G6_method_lens_audit`.
* `docs/design/H22_SCHEDULED_HOUSEKEEPING_FRAME.md` — cited by `H22_scheduled_housekeeping`.

## Why it matters, stated plainly

An atom's `map_records.evidence` is the answer to "what did this level rest on?". R16 makes the ledger
the record; the evidence list is how a later reader — or a cold-eyes pass, or a promotion audit —
reaches the artefact behind a claim. A pointer that resolves to nothing does not fail loudly; it returns
"file not found" to whoever bothers to look, and 30% of the map is in that state. This is adjacent to
the already-filed *a discharge line reads every backtick as a PATH* class: the project keeps writing
paths into records that nothing dereferences, so nothing keeps them true.

## What would discharge this — the class, not the instances (R10)

An instance sweep would be wrong twice over: it repairs 63 pointers and leaves the next archive move to
break the next 63. The class fix is a **control**, and the cheap honest version is:

1. A checker that resolves every space-free path-shaped `map_records` value and reports the dead ones,
   with the subject defined as it is above (prose paragraphs excluded, explicitly, so the population
   boundary is a decision and not an accident).
2. Wired where archiving happens — the staging-protocol move — so relocating a document is what
   surfaces the atoms citing it, at the moment it is relocatable rather than months later.
3. R15 both ways: it must go red on a synthetic dead pointer and stay green when a cited file is merely
   moved *and* the record updated with it. A version that passes on an empty evidence list is fail-open
   and is the shape to mutation-test against first.

Deliberately **not** proposed: making the checker fatal at commit time. 66 dead paths at HEAD means a
fatal control would wedge every lane on day one, and the wedge would be paid by whoever committed next
rather than by whoever archived. Report-and-ratchet is the shape that fits a 66-deep backlog.

Sizing, so the atom that picks this up knows what it is buying: the checker is ~40 lines, the repair of
the 63 movable pointers is mechanical (basename lookup resolved all 63 unambiguously in this pass), and
the 3 absent ones need a human decision each — delete the pointer, or name the successor.

**Discharged:** no.
